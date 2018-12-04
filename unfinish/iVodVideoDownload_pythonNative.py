# -*- coding: utf-8 -*-
import urllib2,sys,re,os,subprocess,threading
from PyQt4 QtGui import QtGui, QtCore
reload(sys)
sys.setdefaultencoding('utf8')
import binascii
import struct
import base64 
import math
import xml.etree.ElementTree
import xml.sax
from urlparse import urlparse, urlunparse
import string
import unicodedata
import Queue
import thread
import time
import urllib2
import decimal
import hashlib
from urllib2 import HTTPError
    

NumWorkerThreads = 1

class GetUrl(object):
    def __init__(self, url, fragnum):
        self.url = url
        self.fragNum = fragnum
        self.data = None
        self.errCount = 0

QueueUrl = Queue.PriorityQueue()
QueueUrlDone = Queue.PriorityQueue()

M6Item = None
def workerRun():
    global QueueUrl, QueueUrlDone, M6Item
    while not QueueUrl.empty() and M6Item.status == 'DOWNLOADING':
        item = QueueUrl.get()[1]
        fragUrl = item.url
        try:
            item.data = M6Item.getFile(fragUrl)
            QueueUrlDone.put((item.fragNum, item))
        except HTTPError, e:
            print( sys.exc_info())
            if item.errCount > 3:
                M6Item.status = 'STOPPED'
                # raise
            else:
                item.errCount += 1
                QueueUrl.put((item.fragNum, item))
        QueueUrl.task_done()
    # If we have exited the previous loop with error
    while not QueueUrl.empty():
        # print 'Ignore fragment', QueueUrl.get()[1].fragNum
        QueueUrl.get()

def worker():
    try:
        workerRun()
    except Exception, e:
        print( sys.exc_info())
        M6Item.status = 'STOPPED'
        thread.interrupt_main()

def workerqdRun():
    global QueueUrlDone, M6Item
    currentFrag = 1
    
    while currentFrag <= M6Item.nbFragments and M6Item.status == 'DOWNLOADING':
        
        item = QueueUrlDone.get()[1]
        outFile = open(M6Item.localfilename+"_Seg1-Frag"+ str(item.fragNum)  , "wb")
        if currentFrag == item.fragNum:
            #M6Item.verifyFragment(item.data)
            if not M6Item.decodeFragment(item.fragNum, item.data):
                raise Exception('decodeFrament')
            M6Item.videoFragment(item.fragNum, item.data, outFile)
            print( 'Fragment', currentFrag, 'OK')
            currentFrag += 1  
            requeue = False
        else:
            print( 'Requeue', item.fragNum)
            QueueUrlDone.put((item.fragNum, item))
            requeue = True
        QueueUrlDone.task_done()
        if requeue:
            time.sleep(1)
        outFile.close()
    # If we have exited the previous loop with error
    if currentFrag > M6Item.nbFragments:
        M6Item.status = 'COMPLETED'
    else:
        while not QueueUrlDone.empty():
            print( 'Ignore fragment', QueueUrlDone.get()[1].fragNum)

def workerqd():
    try:
        workerqdRun()
    except Exception, e:
        print( str(sys.exc_info()))
        M6Item.status = 'STOPPED'
        thread.interrupt_main()

validFilenameChars = "-_.() %s%s" % (string.ascii_letters, string.digits)

def removeDisallowedFilenameChars(filename):
    "Remove invalid filename characters" 
    filename = filename.decode('ASCII', 'ignore')
    cleanedFilename = unicodedata.normalize('NFKD', filename).encode('ASCII', 'ignore')
    cleanedFilename = cleanedFilename.replace(' ', '_')
    return ''.join(c for c in cleanedFilename if c in validFilenameChars)              

class M6(object):
    def __init__(self, url, dest = '',  proxy=None ):            
        self.status = 'INIT'
        self.url = url
        self.proxy = proxy
        self.bitrate = 0
        self.duration = 0                        
        self.nbFragments = 0
        self.tagHeaderLen = 11        
        self.prevTagSize = 4
        urlp = urlparse(url)
        fn = os.path.basename(urlp.path)
        #self.localfilename = \
        #    os.path.join(dest, os.path.splitext(fn)[0]) + '.flv'
        self.localfilename = dest
        #self.localfilename = removeDisallowedFilenameChars(self.localfilename)
        self.urlbootstrap = ''
        self.bootstrapInfoId = ''
        self.baseUrl = urlunparse((urlp.scheme, urlp.netloc, 
                                   os.path.dirname(urlp.path), 
                                            '', '', ''))
        self.media ={}
        self.segStart =False    
        self.fragStart = False
        self.live = False
        self.manifest = self.getManifest(self.url)
        self.parseManifest()        
        # self.pm = urllib3.connection_from_url(self.urlbootstrap)
      
    def download(self):
        global QueueUrl, QueueUrlDone, M6Item
        M6Item = self
        self.status = 'DOWNLOADING'
        # self.outFile = open(self.localfilename, "wb")
        self.urlbootstrap = self.media['mediaEntry']['baseURL'] +"/" + self.media['url']
        
        for i in range(self.nbFragments):
            fragUrl = self.urlbootstrap + 'Seg1-Frag'+str(i + 1)
            QueueUrl.put((i + 1, GetUrl(fragUrl, i + 1)))

        t = threading.Thread(target=workerqd)
        # t.daemon = True
        t.start()

        for i in range(NumWorkerThreads):
            t = threading.Thread(target=worker)
            # t.daemon = True
            t.start()

        # QueueUrl.join()
        # QueueUrlDone.join()
        while self.status == 'DOWNLOADING':
            try:
                time.sleep(3)
            except (KeyboardInterrupt, Exception), e:
               print( sys.exc_info())
               self.status = 'STOPPED'
        # self.outFile.close()
        if self.status != 'STOPPED':
            self.status = 'COMPLETED'

    def getInfos(self):
        infos = {}
        infos['status']        = self.status
        infos['localfilename'] = self.localfilename
        infos['proxy']         = self.proxy
        infos['url']           = self.url
        infos['bitrate']       = self.bitrate
        infos['duration']      = self.duration
        infos['nbFragments']   = self.nbFragments
        infos['urlbootstrap']  = self.urlbootstrap
        infos['baseUrl']       = self.baseUrl
        #infos['drmId']         = self.drmAdditionalHeaderId
        return infos

    
    def getFile(self, url):
        txheaders = {'User-Agent':
                            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/35.0.1916.153 Safari/537.36',
                        'Keep-Alive' : '6000',
                        'Connection' : 'keep-alive'
                        }
        request = urllib2.Request(url, None, txheaders)
        response = urllib2.urlopen(request)
        return response.read()

    def getManifest(self, url):
        self.status = 'GETTING MANIFEST'              
        return xml.etree.ElementTree.fromstring(self.getFile(url))

    def parseManifest(self):
        self.status = 'PARSING MANIFEST'
        try:
            root = self.manifest
            self.baseUrl = self.url[0:self.url.rfind('/')]            
            streams = root.find("{http://ns.adobe.com/f4m/1.0}media")
            array ={}
            array['streamId'] = streams.attrib['streamId']
            array['bootstrapInfoId'] = streams.attrib['bootstrapInfoId']
            array['width'] = streams.attrib['width']
            array['height'] = streams.attrib['height']
            array['bitrate'] = streams.attrib['bitrate']
            array['url'] = streams.attrib['url']
            array['metadata'] = streams._children[0].text
            
            mediaEntry ={}
            mediaEntry['baseURL']= self.baseUrl
            mediaEntry['url'] = array['url']
            
            
            bootstrap = root.find("{http://ns.adobe.com/f4m/1.0}bootstrapInfo") 
            mediaEntry['bootstrapUrl']= bootstrap.text.decode('base64')
            mediaEntry['metadata'] = array['metadata'].decode('base64')
            array['mediaEntry'] = mediaEntry
            self.media = array
            self.flvHeader =  mediaEntry['metadata']
            #Parse initial bootstrap info
            (pos, boxType, boxSize) = self.readBoxHeader( mediaEntry['bootstrapUrl'])
            if boxType == 'abst':
                self.parseBootstrapBox(mediaEntry['bootstrapUrl'],8)
          
            
        except Exception, e:
            print("Not possible to parse the manifest")
            print( e)
            sys.exit(-1)
    def parseBootstrapBox(self, bootstrapInfo,pos):
        version = self.readByte(bootstrapInfo,pos)
        flag = self.readInt24(bootstrapInfo,pos+1)
        bootstapVersion = self.readInt32(bootstrapInfo,pos+4)
        byte = self.readByte(bootstrapInfo,pos+8)
        profile =( byte & 0xC0) >>6
        
        if ((byte & 0x20) >> 5):
            self.live     = true
            metadata = false       
        update = (byte & 0x10) >> 4
        if (not update):
            global segTable 
            global fragTable 
        timescale  =self.readInt32(bootstrapInfo,pos+9)
        currentMediaTime    = self.readInt64(bootstrapInfo, pos + 13)
        smpteTimeCodeOffset = self.readInt64(bootstrapInfo, pos + 21)
        
        pos += 29        
        (movieIdentifier,pos)  = self.readString(bootstrapInfo, pos)
        
        serverEntryCount = self.readByte(bootstrapInfo, pos)
        pos +=1
        serverEntryTable = {}
        for i in range(0,serverEntryCount):
              (serverEntryTable[i],pos) = self.readString(bootstrapInfo, pos)
        
        qualityEntryCount = self.readByte(bootstrapInfo, pos)
        pos +=1
        qualityEntryTable = {}
        for i in range(0,qualityEntryCount):
              (qualityEntryTable[i],pos) = self.readString(bootstrapInfo, pos)
        (drmData ,pos)         = self.readString(bootstrapInfo, pos)
        (metadata   ,pos)      = self.readString(bootstrapInfo, pos)        
        segRunTableCount = self.readByte(bootstrapInfo, pos)
        pos+=1
        
        for i in range(0,segRunTableCount):
            (pos, boxType, boxSize) = self.readBoxHeader( bootstrapInfo,pos)
            if(boxType =='asrt'):
                #segTable.append(self.parseAsrtBox(bootstrapInfo,pos))
                (self.parseAsrtBox(bootstrapInfo,pos))
            pos+=boxSize
        
        fragRunTableCount = self.readByte(bootstrapInfo, pos)
        pos+=1
        for i in range(0, fragRunTableCount):
            (pos, boxType, boxSize) =self.readBoxHeader(bootstrapInfo, pos)
            if boxType == "afrt":
                  #fragTable.append(self.parseAfrtBox(bootstrapInfo, pos))
                  (self.parseAfrtBox(bootstrapInfo, pos)) 
            pos +=boxSize
        self.parseSegandFragTable(segTable,fragTable)
        

    def parseAsrtBox(self, asrt, pos):
        global segTable
        segTable = []
        version           = self.readByte(asrt, pos)
        flags             = self.readInt24(asrt, pos + 1)
        qualityEntryCount = self.readByte(asrt, pos + 4)
        pos += 5
        qualitySegmentUrlModifiers= {}
        for i in range(0, qualityEntryCount):
              (qualitySegmentUrlModifiers[i],pos) = self.readString(asrt, pos)
        segCount = self.readInt32(asrt, pos)
        pos += 4; 
        
        for i in range (0,segCount):    
            segEntry ={}       
            firstSegment =self.readInt32(asrt, pos)
            #segEntry =& segTable[firstSegment]
            segEntry['firstSegment']        = firstSegment;
            segEntry['fragmentsPerSegment'] = self.readInt32(asrt, pos + 4)
            if (segEntry['fragmentsPerSegment'] & 0x80000000):
                segEntry['fragmentsPerSegment'] = 0
            pos += 8
            segTable.append(segEntry)
        return segTable
    def parseAfrtBox(self, afrt, pos):
        global fragTable        
        fragTable = []
        version           = self.readByte(afrt, pos)
        flags             = self.readInt24(afrt, pos + 1)
        timescale         = self.readInt32(afrt, pos + 4)
        qualityEntryCount = self.readByte(afrt, pos + 8)
        pos += 9;
        qualitySegmentUrlModifiers ={}
        for i in range(0,qualityEntryCount):
            (qualitySegmentUrlModifiers[i],pos) = self.readString(afrt, pos);
        fragEntries = self.readInt32(afrt, pos)
        pos += 4
        for i in range (0,fragEntries):
            fragEntry={}
            firstFragment = self.readInt32(afrt, pos)
            #fragEntry =& $fragTable[$firstFragment];
            fragEntry['firstFragment']          = firstFragment;
            fragEntry['firstFragmentTimestamp'] = self.readInt64(afrt, pos + 4)
            fragEntry['fragmentDuration']       = self.readInt32(afrt, pos + 12)
            fragEntry['discontinuityIndicator'] = "";
            pos += 16
            if fragEntry['fragmentDuration'] == 0:
                fragEntry['discontinuityIndicator'] = self.readByte(afrt, pos)
                pos+=1
            fragTable.append(fragEntry)
        return fragTable

    def parseSegandFragTable(self, segTable,fragTable):
        firstSegment  = segTable[0]
        lastSegment   = segTable[-1]
        firstFragment = fragTable[0]
        lastFragment  = fragTable[-1]
        
        #Check if live stream is still live
        if ((lastFragment['fragmentDuration'] == 0) and (lastFragment['discontinuityIndicator'] == 0)):            
            self.live = False
            fragTable =frgTable[0:-1]
            lastFragment = frgTable[-1]
        #Count total fragments by adding all entries in compactly coded segment table
        invalidFragCount = False
        prev             = segTable[0]
        self.nbFragments  = prev['fragmentsPerSegment']
        for segT in segTable:        
            self.nbFragments  += (segT['firstSegment'] - prev['firstSegment'] - 1) * prev['fragmentsPerSegment']
            self.nbFragments  += segT['fragmentsPerSegment'];
            prev = segT;
            
        if (not(self.nbFragments  & 0x80000000)):
            self.nbFragments  += firstFragment['firstFragment'] - 1;
        if (self.nbFragments  & 0x80000000):        
              self.nbFragments   = 0;
              invalidFragCount = True;
         
        if (self.nbFragments  < lastFragment['firstFragment']):
            self.nbFragments  = lastFragment['firstFragment']

        # Determine starting segment and fragment
        if (self.segStart == False):        
            if (self.live):
                self.segStart = lastSegment['firstSegment']
            else:
                self.segStart = firstSegment['firstSegment']
            if self.segStart < 1:
                self.segStart = 1
            
        if (self.fragStart == False):
            if (self.live and not invalidFragCount):
                self.fragStart = fragCount - 2;
            else:
                self.fragStart = firstFragment['firstFragment'] - 1;
            if (self.fragStart < 0):
                self.fragStart = 0
    

    def stop(self):
        self.status = 'STOPPED'
    
    def videoFragment(self, fragNum, data, fout):
        start = M6Item.videostart(fragNum, data)
        if fragNum == 1:
            self.videoBootstrap(fout)
        fout.write(data[start:])

    def videoBootstrap(self, fout):
        # Ajout de l'en-t?te FLV
        # fout.write(binascii.a2b_hex("464c560105000000090000000012"))
        # fout.write(binascii.a2b_hex("00018700000000000000")) 
        bootstrap = "464c560105000000090000000012"
        bootstrap += "%06X" % (len(self.flvHeader),)
        bootstrap += "%06X%08X" % (0, 0)
        fout.write(binascii.a2b_hex(bootstrap))
        # Ajout de l'header du fichier
        fout.write(self.flvHeader)
        fout.write(binascii.a2b_hex("00019209"))
        #flvHeader = binascii.unhexlify("464c5601050000000900000000")
        #flvHeaderLen = len(flvHeader)
                



    def videostart(self, fragNum, fragData):
        """
        Trouve le debut de la video dans un fragment
        """
        start = fragData.find("mdat") + 12
        # print "start ", start
        # For all fragment (except frag1)
        if (fragNum == 1):
            start += 0
        else:
            # Skip 2 FLV tags
            for dummy in range(2):
                tagLen, = struct.unpack_from(">L", fragData, start)  # Read 32 bits (big endian)
                # print 'tagLen = %X' % tagLen
                tagLen &= 0x00ffffff  # Take the last 24 bits
                # print 'tagLen2 = %X' % tagLen
                start += tagLen + self.tagHeaderLen + 4  # 11 = tag header len ; 4 = tag footer len
        return start           

    def readBoxHeader(self, data, pos=0):
        boxSize, = struct.unpack_from(">L", data, pos)  # Read 32 bits (big endian)struct.unpack_from(">L", data, pos)  # Read 32 bits (big endian)
        boxType = data[pos + 4 : pos + 8]
        if boxSize == 1:
            boxSize, = struct.unpack_from(">Q", data, pos + 8)  # Read 64 bits (big endian)
            boxSize -= 16
            pos += 16
        else:
            boxSize -= 8
            pos += 8
        if boxSize <= 0:
            boxSize = 0
        return (pos, boxType, boxSize)

    def verifyFragment(self, data):
        pos = 0
        fragLen = len(data)
        while pos < fragLen:
            pos, boxType, boxSize = self.readBoxHeader(data, pos)
            if boxType == 'mdat':
                slen = len(data[pos:])
                # print 'mdat %s' % (slen,)
                if boxSize and slen == boxSize:
                    return True
                else:
                    boxSize = fraglen - pos
            pos += boxSize
        return False

    def decodeFragment(self, fragNum, data):
        fragPos = 0
        fragLen = len(data)
        if not self.verifyFragment(data):
            print( "Skipping fragment number", fragNum)
            return False
        while fragPos < fragLen:
            fragPos, boxType, boxSize = self.readBoxHeader(data, fragPos)
            if boxType == 'mdat':
                fragLen = fragPos + boxSize
                break
            fragPos += boxSize
        while fragPos < fragLen:
            packetType = self.readByte(data, fragPos)
            packetSize = self.readInt24(data, fragPos + 1)
            packetTS = self.readInt24(data, fragPos + 4)
            packetTS |= self.readByte(data, fragPos + 7) << 24
            if packetTS & 0x80000000:
                packetTS &= 0x7FFFFFFF
            totalTagLen = self.tagHeaderLen + packetSize + self.prevTagSize
            # print 'decodeFragment', fragNum, packetType, packetSize, packetTS, totalTagLen
            # time.sleep(1)
            if packetType in (10, 11):
                print( "This stream is encrypted with Akamai DRM. Decryption of such streams isn't currently possible with this script.")
                return False
            if packetType in (40, 41):
                print( "This stream is encrypted with FlashAccess DRM. Decryption of such streams isn't currently possible with this script.")
                return False
            fragPos += totalTagLen
        return True
    def readByte(self, data, pos):
        return struct.unpack_from("B", data, pos)[0]
    #def readInt8(self, data, pos):
    #    return ord(struct.unpack_from("H", data, pos)[0])
    def readInt16(self, data, pos):
        return ord(struct.unpack_from(">L", "\0\0"+ data[pos:pos+2])[0])
    def readInt24(self, data, pos):
        return struct.unpack_from(">L", "\0"+data[pos:pos + 3], 0)[0]
    def readInt32(self, data, pos):
        return struct.unpack_from(">L", data[pos:pos + 4], 0)[0]
    def readInt64(self, data, pos):
        hi    = "%s" % self.readInt32(data, pos)
        lo    = "%s" % self.readInt32(data, pos + 4)
        int64 = decimal.Decimal(decimal.Decimal(hi)* decimal.Decimal("4294967296"))+decimal.Decimal(lo);
        return int64;
    def readString(self, data, pos):
        len = 0
        while(data[pos+len] !='\x00'):
            len +=1
        str = data[pos:len]
        len = pos + len +1
        return (str,len)
    

## manifest URL, Full Saved file name, WorkersThread
#def main(): 
#    global NumWorkerThreads
#    if len(sys.argv) > 3:
#        NumWorkerThreads = int(sys.argv[3])
#    else:
#        NumWorkerThreads = 7
#    st = time.time()
#    x = M6(sys.argv[1], sys.argv[2])        
#    infos = x.getInfos()
#    for item in infos.items():
#        print( item[0]+' : '+str(item[1]))
#    x.download()
#    print 'Download time:', time.time() - st

#if __name__ == "__main__":
#    main()


class iVodVideoDownload(QtCore.QProcess):
    def __init__(self, argURLandFileNameList, argSaveFolder, argHD,argQTStatus):     
        QtCore.QProcess.__init__(self)   
        self.SaveFolder = argSaveFolder
        self.QtStatus = argQTStatus
        self.Manifest = []
        header  ={'User-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/35.0.1916.153 Safari/537.36'}
        for URLAndFileName in argURLandFileNameList:
            URL = URLAndFileName[0]
            FileName = argSaveFolder + "\\" + URLAndFileName[1]
            if argHD:
                URL= str(URLAndFileName[0]).replace('300K','1M')
            #檢查URL然後抓資料
            if URL != '':                    
                html =urllib2.urlopen(urllib2.Request(URL,None,header)).read()
            #Find RealURL
            #readyPlayer('http://ivod.ly.gov.tw/public/scripts/','http://h264media01.ly.gov.tw:1935/vod/_definst_/mp4:1MClips/a7d6027a1ded6aa66237e895a7b354309c450e450740cf30da2b760e9327b2fda041cae092e76417.mp4/manifest.f4m');
            match_readyplayer = re.findall(r"readyPlayer\('.*\)",html)           
            
            manifest_url = re.findall(r',\'.*\)', match_readyplayer[0])[0][2:-2]
            manifest_html =urllib2.urlopen(urllib2.Request(manifest_url,None,header)).read()
            
            duration_sec = re.findall(r'<duration>.*<' ,manifest_html)[0][10:-2]
            duration_min = float(duration_sec)/ 60.0            
            tempFileName = argSaveFolder+"\\tmp.flv";
            self.Manifest.append([URL,manifest_url,FileName])

            #self.QtStatus.append('開始下載' + URLAndFileName[1])
            #run processs
            #self.downloadFile(manifest_url,tempFileName)
            #os.system('python ../bin/AdobeHDS.py -u ' +  manifest_url + "  " + tempFileName +" 2" )
            #while(os.path.isfile(FileName)):
            #    FileName = FileName[0:-4] + "_1.flv" 
            #os.rename(tempFileName,FileName)   
            #self.process.terminate()
            #self.process.waitForFinished()
    def downloadFile(self):
        #proc = subprocess.Popen(['python','AdobeHDS.py',  argFileManifest ,argTempFileLocation ,'7' ], stdout=subprocess.PIPE, stderr=subprocess.PIPE, stdin=subprocess.PIPE)            
        for manifest in self.Manifest:
            tempFileName = self.SaveFolder +"\\tmp.flv"
            FileName = manifest[2]
            
            xdownload = M6(manifest[1],tempFileName)  

            self.QtStatus.append(unicode('下載檔名:') + FileName)
            self.QtStatus.append(unicode('原始URL:') + manifest[0])
            self.QtStatus.append(unicode('Manifest URL:') + manifest[1])
            self.QtStatus.append(unicode('總共分段:') + str(xdownload.getInfos()['nbFragments']))

            
            xdownload.download()
            
            #while(os.path.isfile(FileName)):
            #    FileName = FileName[0:-4] + "_1.flv" 
            #os.rename(tempFileName,FileName)   
            

    #def readStdOutput(self):        
    #    self.QtStatus.append(QString(self.process.readAllStandardOutput()))
global mainForm
def button_click():
    status = mainForm.findChild(QTextBrowser,"Status");
    listURL = [["https://ivod.ly.gov.tw/Play/VOD/88693/1M","test.flv"]]
    download = iVodVideoDownload(listURL, "d:/1985/",True,status)
    download.downloadFile()
    

def main():     
    #x = M6('http://h264media01.ly.gov.tw:1935/vod/_definst_/mp4:1MClips/93b47c7fc6d6e68bfaecdddf9cc0ad7ff5f26990720e1195111f9f57f751472c5d2e46a5ae096bd4.mp4/manifest.f4m','d:/1985/tmp.flv')
    app = QtGui.QApplication(sys.argv)
    global mainForm
    mainForm = QtGui.QWidget()
    mainForm.resize(800,400)
    layout = QtGui.QVBoxLayout()
    
    edit = QtGui.QTextBrowser()
    edit.setObjectName("Status")
    edit.setWindowTitle("QTextEdit Standard Output Redirection")
    layout.addWidget(edit)
    button = QtGui.QPushButton()
    button.clicked.connect(button_click);
    layout.addWidget(button)
    mainForm.setLayout(layout)
    mainForm.show()
    app.exec_()
    #download = iVodVideoDownload(listURL, "D:\\1985\\python\\python\\iVodDBUpdate",True,edit)    

if __name__ == '__main__':
    main()   