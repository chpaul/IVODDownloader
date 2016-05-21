# iVodDownloader

http://ivod.ly.gov.tw/ video downloader using python (2.7 64bit) pyQT4 and php

Download iVod file from Legislative Yuan Taiwan

Modify php exection location in setting.xml and put it into the same folder


AdobeHDS.php comes from K-S-V 
https://github.com/K-S-V/Scripts/blob/master/AdobeHDS.php

台灣立法院iVod開會影片下載器

*  系統需求:python 2.7, pyqt 4, php 5.5 php需要安裝mcrypt module
*  執行檔測試平台: Microsoft Windows 7, Mac OS Yosemite
*  執行檔放置於dist的目錄下

#### 以下檔案若有遺失程式會自動從GitHub補齊或是自動產生
- [./bin/AdobeHDS.php](https://raw.githubusercontent.com/chpaul/iVodDownloader/5901b505e8981080b5f5ef33afd44d714aa9d8e1/bin/AdobeHDS.php) : 下載影音串流Module [原始檔案] (https://github.com/K-S-V/Scripts/blob/master/AdobeHDS.php)
- [./db/iVOD_LY.sqlite](https://github.com/chpaul/iVodDownloader/blob/5901b505e8981080b5f5ef33afd44d714aa9d8e1/db/iVOD_LY.sqlite) :立院開會資料庫,可以下載此歷史資料庫(09/12/2012~5/20/2016)或直接執行執行檔產生空白資料庫
- [./config/setting.xml](https://github.com/chpaul/iVodDownloader/tree/master/config) :設定本機php執行檔位置 分為 unix 及 windows 版本
- ./icons/ :圖示檔案

#### Windows 使用者
    php-mcrypt 安裝 [參考連結]()
     
1. 下載 [dist/windows/downloader.exe](https://github.com/chpaul/iVodDownloader/raw/master/dist/windows/Downloader.exe)
2. 下載附加檔案(optional)
3. 更改./config/setting.xml內php執行路徑
4. 執行 Downloader.exe

#### Mac使用者
 php-mcrypt 安裝  
>1. 安裝 [homebrew](http://brew.sh/)    
>   /usr/bin/ruby -e "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/master/install)"
>2. 安裝php mycrypt 套件   
> brew install homebrew/php/php55-mcrypt




1. 下載  [dist/mac/Downloader.zip](https://github.com/chpaul/iVodDownloader/raw/master/dist/mac/Downloader.zip)
2. 解壓縮
3. 更改/Downloader.app/Content/Resorce/config/setting.xml內的php執行路徑
4. 執行 Downloader.app

