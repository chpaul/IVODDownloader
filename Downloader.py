#!/usr/bin/env python
# -*- coding: utf-8 -*-
# iVodDownloader程式進入點
import sys, ctypes, platform, os, urllib2, iVodMain
from PyQt4.QtGui import *
reload(sys)
sys.setdefaultencoding('utf8')

def main():
    #setup appid for Windows in order to display taskbas icon
    if platform.system() =='Windows':
        myappid = 'chpaul.ivoddownloader.python.1'  # arbitrary string
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)
    app = QApplication(sys.argv)

    widget = iVodMain.iVodMain()

    # 找不到icon
    if not os.path.isfile('./app.png'):
        QMessageBox.information(widget, unicode('Icon遺失'), unicode('Icon遺失 從GitHub下載中'))
        f = urllib2.urlopen('https://raw.githubusercontent.com/chpaul/iVodDownloader/master/app.png')
        with open(os.path.basename('./app.png'), "wb") as local_file:
            local_file.write(f.read())
    widget.__init__()

    # 找不到資料庫
    if not (os.path.isfile('./iVOD_LY.sqlite')):
        QMessageBox.information(widget, unicode('資料庫遺失'), unicode('自動產生空白資料庫 iVod_LY.sqlite'))
        widget.createNewDatabase()

    # id AdobeHDS is missing download from github
    if not os.path.isfile('./AdobeHDS.php'):
        QMessageBox.information(widget, unicode('AdobeHDS遺失'), unicode('AdobeHDS.php遺失,從GitHub下載中'))
        f = urllib2.urlopen('https://raw.githubusercontent.com/chpaul/iVodDownloader/master/AdobeHDS.php')
        with open(os.path.basename('./AdobeHDS.php'), "wb") as local_file:
            local_file.write(f.read())

     # 找不到Setting file
    if not os.path.isfile('./setting.xml'):
        QMessageBox.information(widget, unicode('Setting.xml遺失'), unicode('Setting.xml遺失,從GitHub下載中;請自行更改php路徑'))
        f = urllib2.urlopen('https://raw.githubusercontent.com/chpaul/iVodDownloader/master/setting.xml')
        with open(os.path.basename('./Setting.xml'), "wb") as local_file:
            local_file.write(f.read())

    widget.show()
    widget.SetupDateSearch()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()