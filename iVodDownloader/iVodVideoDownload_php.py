#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import re
import os
import xml.etree.ElementTree
import subprocess as sp
import ssl
from PyQt5 import QtGui
from PyQt5 import QtCore
from PyQt5.QtWidgets import QMainWindow, QWidget, QApplication
from urllib.request import urlopen
from urllib.request import Request
from urllib.error import URLError
# 輸入參數
# argURLandFileNameList list[str,str] #  下載位置 和 檔名 List[URL,FileName]
# argSaveFolder : str # 下載目錄
# argHD : boolean # 是否下載高畫質
# argQTStatus : QTextBrowser # 顯示進度的控制項


class iVodVideoDownload(QMainWindow):
    def __init__(self, argURLandFileNameList, argSaveFolder, argHD, argQTStatus):
        #Clean up the temp
        for path, subdirs, files in os.walk("."):
            for name in files:
                if '-Frag' in name:
                    os.remove(os.path.join(path, name))
        e = xml.etree.ElementTree.parse('./config/setting.xml').getroot()
        self.phpExecutionPath = e.findall('phpLocation')[0].text
        if not self.hasPHP(self.phpExecutionPath):
            raise Exception("Can't find PHP; please install PHP and change location above")
        QWidget.__init__(self)
        self.SaveFolder = argSaveFolder
        self.QtStatus = argQTStatus
        self.Manifest = []
        self.header = {
            'User-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/35.0.1916.153 Safari/537.36'}
        for URLAndFileName in argURLandFileNameList:
            URL = URLAndFileName[0]
            FileName = os.path.join(argSaveFolder, URLAndFileName[1])
            if argHD:
                URL = str(URLAndFileName[0]).replace('300K', '1M')
            # 檢查URL然後抓資料
            if URL != '':
                html = urlopen(Request(URL, None, self.header), context=ssl.SSLContext(ssl.PROTOCOL_TLS)).read()
            # Find RealURL
            try:
            # readyPlayer('http://iVod.ly.gov.tw/public/scripts/','http://h264media01.ly.gov.tw:1935/vod/_definst_/mp4:1MClips/a7d6027a1ded6aa66237e895a7b354309c450e450740cf30da2b760e9327b2fda041cae092e76417.mp4/manifest.f4m');
                match_readyplayer = re.findall(r"readyPlayer\('.*\)", html.decode('utf-8'))
                manifest_url = re.findall(r",\'.*\)", match_readyplayer[0])[0][2:-2]
                #h264media01.ly.gov.tw:443  -> ivod-lyvod.cdn.hinet.net
                #manifest_url = manifest_url.replace('h264media01.ly.gov.tw:443','ivod-lyvod.cdn.hinet.net')
                #manifest_html = urllib2.urlopen(urllib2.Request(manifest_url, None, self.header), context=ssl.SSLContext(ssl.PROTOCOL_TLSv1)).read()
                manifest_html = urlopen(Request(manifest_url, None, self.header), context=ssl.SSLContext(ssl.PROTOCOL_TLS)).read()
            except URLError:
                #高畫質檔案找不到換回低畫質
                URL = str(URLAndFileName[0]).replace('1M', '300K')
                if URL != '':
                    html = urlopen(Request(URL, None, self.header), context=ssl.SSLContext(ssl.PROTOCOL_TLS)).read()
                match_readyplayer = re.findall(r"readyPlayer\('.*\)", html.decode('utf-8'))
                manifest_url = re.findall(r",\'.*\)", match_readyplayer[0])[0][2:-2]
                manifest_html = urlopen(Request(manifest_url, None, self.header), context=ssl.SSLContext(ssl.PROTOCOL_TLS)).read()
            duration_sec = re.findall(r'<duration>.*<', manifest_html.decode('utf-8'))[0][10:-2]
            duration_min = float(duration_sec) / 60.0
            tempFileName = os.path.join(argSaveFolder, "tmp.flv")
            self.Manifest.append([URL, manifest_url, FileName])
            self.process = QtCore.QProcess(self)
            self.process.readyReadStandardOutput.connect(self.dataReady)
            self.process.finished.connect(self.finish)

    def downloadFile(self):
        downloadfailed = []
        self.QtStatus.append('PHP Location:' + self.phpExecutionPath)
        logFile = open('./iVod.log', 'a', encoding="utf-8")
        logFile.write("----------------------------Download-------------------------" + os.linesep)
        for manifest in self.Manifest:
            tempFileName = os.path.join(self.SaveFolder, "tmp.flv")
            FileName = manifest[2]
            logFile.write('Name:' + FileName + os.linesep)
            logFile.write('URL:' + manifest[0] + os.linesep)
            logFile.write('Manifest URL:' + manifest[1] + os.linesep)
            logFile.flush()
            self.running = False

            self.QtStatus.append(('下載檔名:') + FileName)
            self.QtStatus.append(('原始URL:') + manifest[0])
            self.QtStatus.append(('Manifest URL:') + manifest[1])

            # call php
            self.callAdobeHDS(manifest[1], tempFileName)

            # 更新QT元件
            while self.running:
                QApplication.processEvents()

            # 如果有暫存檔案存在 下載失敗 刪除暫存檔
            if not os.path.isfile(tempFileName):
                downloadfailed.append(FileName)
                for s in os.listdir('./'):
                    if s.find('Seg1-Frag') != -1:
                        os.remove(s)
            # 轉換下載名稱 若有重複更改新下載名
            else:
                while os.path.isfile(FileName):
                    FileName = FileName[0:-4] + "_1.flv"
                os.rename(tempFileName, FileName)
                logFile.write(FileName + ' download finish' + os.linesep +os.linesep)

        if len(downloadfailed) != 0:
            for s in downloadfailed:
                self.QtStatus.append(s + u' 下載失敗')
                logFile.write(s + ' files failed' + os.linesep)
        logFile.write('----------------------------Download Finish------------------' + os.linesep)
        logFile.flush()
        logFile.close()

    def callAdobeHDS(self, manifestURL, tmpFileLocation):
        self.running = True
        self.process.start(self.phpExecutionPath,
                           ["./bin/AdobeHDS.php", "--quality", "high", "--useragent", self.header['User-agent'],
                            '--delete', '--outfile', tmpFileLocation, '--manifest',
                            manifestURL])  # , shell=True, stdout=subprocess.PIPE)

    def finish(self):
        self.running = False

    def dataReady(self):
        cursor = self.QtStatus.textCursor()
        cursor.movePosition(cursor.End)
        output = (bytearray(self.process.readAllStandardOutput())).decode('utf-8')

        cursor.insertText(output)
        # cursor.insertText(str(self.process.readAllStandardOutput()))
        self.QtStatus.ensureCursorVisible()

    def hasPHP(self, arg):
        try:
            sp.check_call([arg, '-v'])
            return True
        except:
            return False

# 測試區塊
# global mainForm
# def button_click():
#     status = mainForm.findChild(QTextBrowser,"Status");
#     listURL = [["https://iVod.ly.gov.tw/Play/VOD/76472/300K","test.flv"]]
#     download = iVodVideoDownload(listURL, "./",True,status)
#     download.downloadFile()
#
# def main():
#     app = QtGui.QApplication(sys.argv)
#     global mainForm
#     mainForm = QtGui.QWidget()
#     mainForm.resize(800,400)
#     layout = QtGui.QVBoxLayout()
#     edit = QtGui.QTextBrowser()
#     edit.setObjectName("Status")
#     edit.setWindowTitle("QTextEdit Standard Output Redirection")
#     layout.addWidget(edit)
#     button = QtGui.QPushButton()
#     button.clicked.connect(button_click)
#     layout.addWidget(button)
#     mainForm.setLayout(layout)
#     mainForm.show()
#     app.exec_()
#
#
# if __name__ == '__main__':
#     main()
