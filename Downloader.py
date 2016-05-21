#!/usr/bin/env python
# -*- coding: utf-8 -*-
# iVodDownloader entry point
import sys, ctypes, platform, os, urllib2
from PyQt4 import QtGui
from iVodDownloader import iVodMain

reload(sys)
sys.setdefaultencoding('utf-8')

def main():
    #setup appid for Windows in order to display taskbas icon
    if platform.system() =='Windows':
        myappid = 'chpaul.ivoddownloader.python.1'  # arbitrary string
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)
    app = QtGui.QApplication(sys.argv)

    widget = iVodMain.iVodMain()

    # 找不到icon
    if not os.path.isfile('./icons/app.png'):
        QtGui.QMessageBox.information(widget, unicode('Icon遺失'), unicode('Icon遺失 從GitHub下載中'))
        f = urllib2.urlopen('https://raw.githubusercontent.com/chpaul/iVodDownloader/master/icons/app.png')
        with open(os.path.basename('./icons/app.png'), "wb") as local_file:
            local_file.write(f.read())
    widget.__init__()

    # 找不到資料庫
    if not (os.path.isfile('./db/iVOD_LY.sqlite')):
        QtGui.QMessageBox.information(widget, unicode('資料庫遺失'), unicode('自動產生空白資料庫 iVOD_LY.sqlite'))
        widget.createNewDatabase()

    # id AdobeHDS is missing download from github
    if not os.path.isfile('./bin/AdobeHDS.php'):
        QtGui.QMessageBox.information(widget, unicode('AdobeHDS遺失'), unicode('AdobeHDS.php遺失,從GitHub下載中'))
        f = urllib2.urlopen('https://raw.githubusercontent.com/chpaul/iVodDownloader/master/bin/AdobeHDS.php')
        with open(os.path.basename('./bin/AdobeHDS.php'), "wb") as local_file:
            local_file.write(f.read())

     # 找不到Setting file
    if not os.path.isfile('./setting.xml'):
        QtGui.QMessageBox.information(widget, unicode('Setting.xml遺失'), unicode('Setting.xml遺失,從GitHub下載中;請自行更改php路徑'))
        if platform.system() =='Windows':
            f = urllib2.urlopen('https://raw.githubusercontent.com/chpaul/iVodDownloader/master/config/windows_setting.xml')
        else
            f = urllib2.urlopen('https://raw.githubusercontent.com/chpaul/iVodDownloader/master/config/unix_setting.xml')
        with open(os.path.basename('./config/setting.xml'), "wb") as local_file:
            local_file.write(f.read())

    widget.show()
    widget.SetupDateSearch()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()