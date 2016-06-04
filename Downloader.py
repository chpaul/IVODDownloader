#!/usr/bin/env python
# -*- coding: utf-8 -*-
# IVODDownloader entry point
import sys, ctypes, platform, os, urllib2
from PyQt4 import QtGui
if platform.system() !='Windows':
    os.chdir(os.path.dirname(__file__))
from IVODDownloader import IVODMain

reload(sys)
sys.setdefaultencoding('utf-8')

def main():
    #setup appid for Windows in order to display taskbas icon
    if platform.system() =='Windows':
        myappid = 'chpaul.ivoddownloader.python.1'  # arbitrary string
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)
    app = QtGui.QApplication(sys.argv)

    widget = IVODMain.IVODMain()

    # 找不到icon
    if not os.path.isfile('./icons/app.png'):
        QtGui.QMessageBox.information(widget, unicode('Icon遺失'), unicode('Icon遺失 從GitHub下載中'))
        f = urllib2.urlopen('https://raw.githubusercontent.com/chpaul/IVODDownloader/master/icons/app.png')
        if not os.path.isdir('./icons'):
            os.makedirs('./icons')
        with open('./icons/app.png', "wb") as local_file:
            local_file.write(f.read())
    widget.__init__()

    # 找不到資料庫
    if not (os.path.isfile('./db/IVOD_LY.sqlite')):
        QtGui.QMessageBox.information(widget, unicode('資料庫遺失'), unicode('自動產生空白資料庫 IVOD_LY.sqlite'))
        if not os.path.isdir('./db'):
            os.makedirs('./db')
        widget.createNewDatabase()

    # id AdobeHDS is missing download from github
    if not os.path.isfile('./bin/AdobeHDS.php'):
        QtGui.QMessageBox.information(widget, unicode('AdobeHDS遺失'), unicode('AdobeHDS.php遺失,從GitHub下載中'))
        f = urllib2.urlopen('https://raw.githubusercontent.com/chpaul/IVODDownloader/master/bin/AdobeHDS.php')
        if not os.path.isdir('./bin'):
            os.makedirs('./bin')
        with open('./bin/AdobeHDS.php', "wb") as local_file:
            local_file.write(f.read())

     # 找不到Setting file
    if not os.path.isfile('./config/setting.xml'):
        QtGui.QMessageBox.information(widget, unicode('setting.xml遺失'), unicode('setting.xml遺失,從GitHub下載中;請自行更改php路徑'))
        if platform.system() =='Windows':
            f = urllib2.urlopen('https://raw.githubusercontent.com/chpaul/IVODDownloader/master/config/windows_setting.xml')
        else:
            f = urllib2.urlopen('https://raw.githubusercontent.com/chpaul/IVODDownloader/master/config/unix_setting.xml')
        if not os.path.isdir('./config'):
                os.makedirs('./config')
        with open('./config/setting.xml', "wb") as local_file:
            local_file.write(f.read())

    widget.show()
    widget.SetupDateSearch()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()