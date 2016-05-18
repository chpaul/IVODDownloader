﻿# -*- coding: utf-8 -*-
#主要Form 包含UI 
import sys,webbrowser,os
reload(sys)
sys.setdefaultencoding('utf8')
from PyQt4 import QtGui, QtCore
import iVodDataBaseUpdate, iVodDataBaseSearch,iVodVideoDownload_php
import sqlite3
class iVodMain(QtGui.QWidget):    
    def __init__(self, parent = None):
        super(iVodMain,self).__init__(parent)
        
        #List committee name
        lstCommitteeName = [unicode("院會"),unicode("內政委員會"),unicode("財政委員會"),unicode("司法及法制委員會"),unicode("外交及國防委員會"),unicode("教育及文化委員會"),unicode("社會福利及衛生環境委員會"),unicode("經濟委員會"),unicode("交通委員會"),unicode("程序委員會")]
        
        #Layout
        self.resize(800,400);
        self.setWindowTitle(unicode('iVod 下載器'))
        self.tabs = QtGui.QTabWidget()

        self.tabSearch = QtGui.QWidget()        
        self.tabDBUpdate = QtGui.QWidget()        
        self.tabDownload = QtGui.QWidget()    
        self.tabDownloadStatus = QtGui.QWidget()
        
        self.tabs.addTab(self.tabSearch,unicode("會議查詢"))        
        self.tabs.addTab(self.tabDownload,unicode("影片下載"))
        self.tabs.addTab(self.tabDownloadStatus,unicode("影片下載進度"))
        self.tabs.addTab(self.tabDBUpdate,unicode("資料庫更新"))       

     
        # 搜尋tab
        Searchlayout = QtGui.QVBoxLayout()        
        Searchlayout.setAlignment(QtCore.Qt.AlignTop)                       
        
        DateLayout = QtGui.QHBoxLayout()
        DateLayout.addWidget(QtGui.QLabel(unicode('開始時間:')),0,QtCore.Qt.AlignRight)
        self.cboStartTime = QtGui.QComboBox()
        DateLayout.addWidget(self.cboStartTime)
        DateLayout.addWidget(QtGui.QLabel(unicode('結束時間')),0,QtCore.Qt.AlignRight)
        self.cboEndTime = QtGui.QComboBox()
        DateLayout.addWidget(self.cboEndTime) 
        Searchlayout.addLayout(DateLayout,1)
        
        self.chkAllCommittee = QtGui.QCheckBox(unicode("全委員會"))
        self.chkAllCommittee.stateChanged.connect(self.chkAllCommittee_click)        
        Searchlayout.addWidget(self.chkAllCommittee,2,QtCore.Qt.AlignHCenter)
        
        #委員會控制項List
        self.lstCheckBoxs = [];        
        for CoName in lstCommitteeName:
            chkBox = QtGui.QCheckBox(CoName)
            self.lstCheckBoxs.append(chkBox)
           
        CommitteeGridLayout = QtGui.QGridLayout()
        CommitteeGridLayout.addWidget(self.lstCheckBoxs[0],2,0)
        #委員會checkbox控制項位置 
        for i in range(1,10):
            x = 0
            y = 0
            if( i %3 == 0):
                x = (i / 3)
                y = 3+1
            else:
                x = (i / 3)+1
                y = i % 3+1
            CommitteeGridLayout.addWidget(self.lstCheckBoxs[i],x,y);       
        

        Searchlayout.addLayout(CommitteeGridLayout)
        self.btnSearch = QtGui.QPushButton(unicode('搜尋'))        
        self.btnSearch.clicked.connect(self.btnSearch_click)
        Searchlayout.addWidget(self.btnSearch)
        self.tabSearch.setLayout(Searchlayout)

        #下載選擇tab        
        downloadlayout = QtGui.QVBoxLayout()
        downloadlayout.addWidget(QtGui.QLabel(unicode("委員發言片段(雙擊打開立院網頁)")))
        self.IndividualDataTable = QtGui.QTableWidget() 
        self.IndividualDataTable.setColumnCount(8)     
        self.IndividualDataTable.setHorizontalHeaderLabels([unicode("下載"),unicode("開會日期"),unicode("發言時間"), unicode("委員會"),unicode("會期"),unicode("發言人"),unicode("會議內容"),unicode("iVOD 連結")])       
        self.IndividualDataTable.verticalHeader().setDefaultSectionSize(36)
        self.IndividualDataTable.setColumnWidth(0,30)
        self.IndividualDataTable.setColumnWidth(1,70)
        self.IndividualDataTable.setColumnWidth(2,60)
        self.IndividualDataTable.setColumnWidth(3,80)
        self.IndividualDataTable.setColumnWidth(4,50)
        self.IndividualDataTable.setColumnWidth(5,50)
        self.IndividualDataTable.setColumnWidth(6,130)
        self.IndividualDataTable.setColumnWidth(7,235)
        downloadlayout.addWidget(self.IndividualDataTable)

        downloadlayout.addWidget(QtGui.QLabel(unicode("會議完整錄影(雙擊打開立院網頁)")))
        self.FullDataTable = QtGui.QTableWidget() 
        self.FullDataTable.setColumnCount(6)     
        self.FullDataTable.setHorizontalHeaderLabels([unicode("下載"),unicode("開會日期"), unicode("委員會"),unicode("會期"),unicode("會議內容"),unicode("iVOD 連結")])       
        self.FullDataTable.verticalHeader().setDefaultSectionSize(36)
        self.FullDataTable.setColumnWidth(0,30)
        self.FullDataTable.setColumnWidth(1,110)
        self.FullDataTable.setColumnWidth(2,80)
        self.FullDataTable.setColumnWidth(3,50)
        self.FullDataTable.setColumnWidth(4,220)
        self.FullDataTable.setColumnWidth(5,225)
        downloadlayout.addWidget(self.FullDataTable)

        downloadButtonLayout = QtGui.QHBoxLayout()
        
        btnDownload = QtGui.QPushButton("Download")
        btnDownload.clicked.connect(self.btnDownloand_click)
        downloadButtonLayout.addWidget(btnDownload)
        self.chkHD =QtGui.QCheckBox(unicode("下載高畫質 1M"))
        self.chkHD.setCheckState(True)
        downloadButtonLayout.addWidget(self.chkHD)
        downloadlayout.addLayout(downloadButtonLayout)
        self.tabDownload.setLayout(downloadlayout)

        #下載進度tab
        self.txtblkDownloadStatus = QtGui.QTextEdit()
        downloadStatusLayout = QtGui.QVBoxLayout()
        downloadStatusLayout.addWidget(self.txtblkDownloadStatus)
        self.tabDownloadStatus.setLayout(downloadStatusLayout)

        #資料庫更新tab      
        btnUpdateDB = QtGui.QPushButton('Update Database')
        #btnUpdateDB.setObjectName("btnUpdateDB")
        self.dbLocation = QtGui.QLineEdit()
        self.dbLocation.setObjectName("dbLocation")
        
        self.maxUpdateNumber = QtGui.QLineEdit()  
        self.maxUpdateNumber.setText('3')
        self.maxUpdateNumber.setObjectName("maxUpdateNumber")
        self.status = QtGui.QTextBrowser()
        DBlayout = QtGui.QGridLayout()
        DBlayout.addWidget(QtGui.QLabel('Database Location:'),0,0)
        DBlayout.addWidget(self.dbLocation,0,1,1,3)
        DBlayout.addWidget(QtGui.QLabel('Update number:'),1,0)
        DBlayout.addWidget(self.maxUpdateNumber,1,1,1,1)
        DBlayout.addWidget(btnUpdateDB,1,3)        
        DBlayout.addWidget(self.status,2,1,3,3)        
        
        btnUpdateDB.clicked.connect(self.btnUpdateDB_click)

        self.tabDBUpdate.setLayout(DBlayout)

        #TabControl
        mainLayout = QtGui.QVBoxLayout()
        mainLayout.addWidget(self.tabs)
        self.setLayout(mainLayout)
        

        #Fill data
        #指定資料庫位置
        if (os.path.isfile('./iVOD_LY.sqlite')):
            self.dbLocation.setText('./iVOD_LY.sqlite')
        else:
            self.dbLocation.setText('')
        self.SetupDateSearch()

    #讀取資料庫把搜尋的條件填入控制項
    def SetupDateSearch(self):
        
        db_con = sqlite3.connect('./iVOD_LY.sqlite')
        cur = db_con.cursor()                    
        cur.execute("Select Distinct ST_time from (SELECT DISTINCT substr(ST_TIM,1,10) as ST_time FROM iVOD_Lglt union SELECT DISTINCT substr(ST_TIM,1,10) as ST_time FROM iVOD_FullMeeting)order by ST_time DESC")
        MeetingTimeRecord = cur.fetchall()
        if len(MeetingTimeRecord) !=0 :
            for row in MeetingTimeRecord:
                self.cboStartTime.addItem(str(row[0]))
                self.cboEndTime.addItem(str(row[0]))
        else:
            self.btnSearch.setEnabled(False)
            QtGui.QMessageBox.information(self,unicode("錯誤"),unicode("資料庫為空!請先更新資料庫後重新啟動程式"))
        db_con.close()

    #全勾選控制項 Event
    def chkAllCommittee_click(self):    
        for chkBox in self.lstCheckBoxs:
            chkBox.setChecked(self.chkAllCommittee.checkState()) 

    #搜尋按鈕 Event
    def btnSearch_click(self):
       
        StartTime = str(self.cboStartTime.currentText()) + ' 00:00:00'
        EndTime = str(self.cboEndTime.currentText()) + ' 23:59:59'
        Committees = []
        for i in range(0,10):
            if self.lstCheckBoxs[i].isChecked():
                Committees.append(unicode(self.lstCheckBoxs[i].text()))

        DBSearch = iVodDataBaseSearch.iVodDataBaseSearch(StartTime,EndTime,Committees)        

        IndividualDataRoes = DBSearch.SearchIndividual()
        self.IndividualDataTable.cellDoubleClicked.connect(self.cellDataTable_DBclick)    
        for row in IndividualDataRoes:
            rowPosition = self.FullDataTable.rowCount()
            chkBoxItem = QtGui.QTableWidgetItem()
            chkBoxItem.setFlags(QtCore.Qt.ItemIsUserCheckable | QtCore.Qt.ItemIsEnabled)
            chkBoxItem.setCheckState(QtCore.Qt.Unchecked)  
            chkBoxItem.setTextAlignment(QtCore.Qt.AlignCenter)     
            self.IndividualDataTable.insertRow(rowPosition)
            self.IndividualDataTable.setItem(rowPosition,0,chkBoxItem)
            self.IndividualDataTable.setItem(rowPosition,1,QtGui.QTableWidgetItem(row[22].split(' ')[0]))
            self.IndividualDataTable.setItem(rowPosition,2,QtGui.QTableWidgetItem(row[14]))
            self.IndividualDataTable.setItem(rowPosition,3,QtGui.QTableWidgetItem(row[4]))
            self.IndividualDataTable.setItem(rowPosition,4,QtGui.QTableWidgetItem(unicode("第")+str(row[23])+unicode("屆 第")+str(row[6])+unicode("會期")))
            self.IndividualDataTable.setItem(rowPosition,5,QtGui.QTableWidgetItem(row[1]))
            self.IndividualDataTable.setItem(rowPosition,6,QtGui.QTableWidgetItem(row[16]))
            self.IndividualDataTable.setItem(rowPosition,7,QtGui.QTableWidgetItem("http://ivod.ly.gov.tw/Play/VOD/"+str(row[0])+"/300K"))
        FullDataRows = DBSearch.SearchFull()   
        self.FullDataTable.cellDoubleClicked.connect(self.cellDataTable_DBclick)
        for row in FullDataRows:
            rowPosition = self.FullDataTable.rowCount()
            chkBoxItem = QtGui.QTableWidgetItem()
            chkBoxItem.setFlags(QtCore.Qt.ItemIsUserCheckable | QtCore.Qt.ItemIsEnabled)
            chkBoxItem.setCheckState(QtCore.Qt.Unchecked)  
            chkBoxItem.setTextAlignment(QtCore.Qt.AlignCenter)     
            self.FullDataTable.insertRow(rowPosition)
            self.FullDataTable.setItem(rowPosition,0,chkBoxItem)
            self.FullDataTable.setItem(rowPosition,1,QtGui.QTableWidgetItem(row[13]))
            self.FullDataTable.setItem(rowPosition,2,QtGui.QTableWidgetItem(row[0]))
            self.FullDataTable.setItem(rowPosition,3,QtGui.QTableWidgetItem(unicode("第")+str(row[14])+unicode("屆 第")+str(row[1])+unicode("會期")))
            self.FullDataTable.setItem(rowPosition,4,QtGui.QTableWidgetItem(row[9]))
            self.FullDataTable.setItem(rowPosition,5,QtGui.QTableWidgetItem("http://ivod.ly.gov.tw/Play/Full/"+str(row[8])+"/300K"))            
        self.tabs.setCurrentIndex(1)       

    #下載按鈕 Event 呼叫iVodVideoDownload_php 進行下載
    def btnDownloand_click(self):
        selectID =[] # URL , FileName
        for row in xrange(self.IndividualDataTable.rowCount()):
            if QtGui.QTableWidgetItem(self.IndividualDataTable.item(row,0)).checkState() == QtCore.Qt.Checked:
                fileName = unicode(self.IndividualDataTable.item(row,5).text()) + "_" + unicode(self.IndividualDataTable.item(row,1).text()) +".flv"
                selectID.append([str(self.IndividualDataTable.item(row,7).text()),fileName])

        for row in xrange(self.FullDataTable.rowCount()):
            if QtGui.QTableWidgetItem(self.FullDataTable.item(row,0)).checkState() == QtCore.Qt.Checked:
                fileName = unicode(self.FullDataTable.item(row,2).text()) + "_" + unicode(self.FullDataTable.item(row,1).text()) +".flv"
                selectID.append([str(self.FullDataTable.item(row,5).text()),fileName])
        reply = QtGui.QMessageBox.question(self,unicode("下載清單"),"\n".join([row[1] for row in selectID]),QtGui.QMessageBox.Yes,QtGui.QMessageBox.No)
        if reply ==QtGui.QMessageBox.Yes:   
            folder = str(QtGui.QFileDialog.getExistingDirectory(self, "Select Directory"))
            self.tabs.setCurrentIndex(2)    
            downlaod = iVodVideoDownload_php.iVodVideoDownload(selectID,folder,self.chkHD.isChecked(),self.txtblkDownloadStatus)
            downlaod.downloadFile()

    #雙擊data table 直接開啟瀏覽器到iVod網站
    def cellDataTable_DBclick(self,row,column):        
        if (self.sender() == self.FullDataTable):
            URL = self.FullDataTable.item(row,5).text()        
        else:
            URL = self.IndividualDataTable.item(row,7).text()        
        webbrowser.open_new(URL)

    #更新資料庫按鈕 Event 呼叫 iVodDataBaseUpdate
    def btnUpdateDB_click(self):             
        DBUpdater = iVodDataBaseUpdate.iVodDataBaseUpdate(self.dbLocation.text(),self.maxUpdateNumber.text(), self.status)
        QtGui.QMessageBox.information(self,unicode('開始更新'),unicode('開始更新最新%s天資料' % str(self.maxUpdateNumber.text())))
        DBUpdater.startUpdate()
        QtGui.QMessageBox.information(self,unicode('更新完成'),unicode('OK'))

