#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# iVodDownloader entry point
import sys
import ctypes
import platform
import os
import os.path
from urllib.request import urlopen
from PyQt5.QtWidgets import QApplication, QMessageBox
from iVodDownloader import iVodMain
if platform.system() != 'Windows':
    os.chdir(os.path.dirname(__file__))


def main():
    # setup appid for Windows in order to display taskbar icon
    if platform.system() == 'Windows':
        myappid = 'chpaul.ivoddownloader.python.1'  # arbitrary string
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)
    app = QApplication(sys.argv)

    widget = iVodMain.iVodMain()

    # 找不到icon
    if not os.path.isfile('./icons/app.png'):
        QMessageBox.information(widget, 'Icon遺失', 'Icon遺失 從GitHub下載中')
        f = urlopen('https://raw.githubusercontent.com/chpaul/iVodDownloader/master/icons/app.png')
        if not os.path.isdir('./icons'):
            os.makedirs('./icons')
        with open('./icons/app.png', "wb") as local_file:
            local_file.write(f.read())
    widget.__init__()

    # 找不到資料庫
    if not (os.path.isfile('./db/iVod_LY.sqlite')):
        QMessageBox.information(widget, '資料庫遺失', '自動產生空白資料庫 iVod_LY.sqlite')
        if not os.path.isdir('./db'):
            os.makedirs('./db')
        widget.createNewDatabase()

    # if AdobeHDS is missing download from github
    if not os.path.isfile('./bin/AdobeHDS.php'):
        QMessageBox.information(widget, 'AdobeHDS遺失', 'AdobeHDS.php遺失,從GitHub下載中')
        f = urlopen('https://raw.githubusercontent.com/K-S-V/Scripts/master/AdobeHDS.php')
        if not os.path.isdir('./bin'):
            os.makedirs('./bin')
        with open('./bin/AdobeHDS.php', "wb") as local_file:
            local_file.write(f.read())

    # 找不到Setting file
    if not os.path.isfile('./config/setting.xml'):
        QMessageBox.information(widget, 'setting.xml遺失', 'setting.xml遺失,從GitHub下載中;請自行更改php路徑')
        if platform.system() == 'Windows':
            f = urlopen('https://raw.githubusercontent.com/chpaul/iVodDownloader/master/config/windows_setting.xml')
        else:
            f = urlopen('https://raw.githubusercontent.com/chpaul/iVodDownloader/master/config/unix_setting.xml')
        if not os.path.isdir('./config'):
                os.makedirs('./config')
        with open('./config/setting.xml', "wb") as local_file:
            local_file.write(f.read())

    widget.show()
    widget.SetupDateSearch()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
