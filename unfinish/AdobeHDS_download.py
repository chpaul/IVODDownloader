#!/usr/bin/env python
# -*- coding:utf-8 -*-
# M6 version 0.1 par k3c
import binascii
import struct
import sys
import os
import base64 
import math
import xml.etree.ElementTree
import xml.sax
import re
from urlparse import urlparse, urlunparse
import string
import unicodedata
import Queue
import threading, thread
import time
try:
    import urllib3
    from urllib3.exceptions import HTTPError
    hasUrllib3 = True
except ImportError:
    import urllib2
    from urllib2 import HTTPError
    hasUrllib3 = False

NumWorkerThreads = None

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
            print sys.exc_info()
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
        print sys.exc_info()
        M6Item.status = 'STOPPED'
        thread.interrupt_main()

def workerqdRun():
    global QueueUrlDone, M6Item
    currentFrag = 1
    outFile = open(M6Item.localfilename, "wb")
    while currentFrag <= M6Item.nbFragments and M6Item.status == 'DOWNLOADING':
        item = QueueUrlDone.get()[1]
        if currentFrag == item.fragNum:
            # M6Item.verifyFragment(item.data)
            if not M6Item.decodeFragment(item.fragNum, item.data):
                raise Exception('decodeFrament')
            M6Item.videoFragment(item.fragNum, item.data, outFile)
            print 'Fragment', currentFrag, 'OK'
            currentFrag += 1  
            requeue = False
        else:
            print 'Requeue', item.fragNum
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
            print 'Ignore fragment', QueueUrlDone.get()[1].fragNum

def workerqd():
    try:
        workerqdRun()
    except Exception, e:
        print sys.exc_info()
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
    def __init__(self, url, dest = '', proxy=None):
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
        self.localfilename = \
            os.path.join(dest, os.path.splitext(fn)[0]) + '.flv'
        self.localfilename = removeDisallowedFilenameChars(self.localfilename)
        self.urlbootstrap = ''
        self.bootstrapInfoId = ''
        self.baseUrl = urlunparse((urlp.scheme, urlp.netloc, 
                                   os.path.dirname(urlp.path), 
                                            '', '', ''))
        if hasUrllib3:
            self.pm = urllib3.PoolManager(num_pools=100)
            # self.pm = urllib3.connection_from_url(self.baseUrl)
        self.manifest = self.getManifest(self.url)
        self.parseManifest()        
        # self.pm = urllib3.connection_from_url(self.urlbootstrap)
      
    def download(self):
        global QueueUrl, QueueUrlDone, M6Item
        M6Item = self
        self.status = 'DOWNLOADING'
        # self.outFile = open(self.localfilename, "wb")

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
                print sys.exc_info()
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

    if hasUrllib3:
        def getFile(self, url):
            headers = urllib3.make_headers(
                keep_alive=True,
                user_agent='Mozilla/5.0 (X11; Ubuntu; Linux i686; rv:17.0) Gecko/20100101 Firefox/17.0',
                accept_encoding=True)
            r = self.pm.request('GET', url, headers=headers)
            if r.status != 200:
                print 'Error downloading', r.status, url
                # sys.exit(1)
            return r.data
    else:
        def getFile(self, url):
            txheaders = {'User-Agent':
                             'Mozilla/5.0 (X11; Ubuntu; Linux i686; rv:17.0) Gecko/20100101 Firefox/17.0',
                         'Keep-Alive' : '600',
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
            # Duration
            self.duration = float(root.find("{http://ns.adobe.com/f4m/1.0}duration").text)
            # nombre de fragment
            self.nbFragments = int(math.ceil(self.duration/3))
            # streamid
            self.streamid = root.findall("{http://ns.adobe.com/f4m/1.0}media")[-1]
            # media
            self.media = None
            for media in root.findall('{http://ns.adobe.com/f4m/1.0}media'):
                if int(media.attrib['bitrate']) > self.bitrate:
                    self.media = media
                    self.bitrate = int(media.attrib['bitrate'])
                    self.bootstrapInfoId = media.attrib['bootstrapInfoId']
                    #self.drmAdditionalHeaderId = media.attrib['drmAdditionalHeaderId']
                    self.flvHeader = base64.b64decode(media.find("{http://ns.adobe.com/f4m/1.0}metadata").text)
            # Bootstrap URL
            self.urlbootstrap = self.media.attrib["url"]
            # urlbootstrap
            self.urlbootstrap = self.baseUrl + "/" + self.urlbootstrap
        except Exception, e:
            print("Not possible to parse the manifest")
            print e
            sys.exit(-1)

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
            print "Skipping fragment number", fragNum
            return false
        while fragPos < fragLen:
            fragPos, boxType, boxSize = self.readBoxHeader(data, fragPos)
            if boxType == 'mdat':
                fragLen = fragPos + boxSize
                break
            fragPos += boxSize
        while fragPos < fragLen:
            packetType = self.readInt8(data, fragPos)
            packetSize = self.readInt24(data, fragPos + 1)
            packetTS = self.readInt24(data, fragPos + 4)
            packetTS |= self.readInt8(data, fragPos + 7) << 24
            if packetTS & 0x80000000:
                packetTS &= 0x7FFFFFFF
            totalTagLen = self.tagHeaderLen + packetSize + self.prevTagSize
            # print 'decodeFragment', fragNum, packetType, packetSize, packetTS, totalTagLen
            # time.sleep(1)
            if packetType in (10, 11):
                print "This stream is encrypted with Akamai DRM. Decryption of such streams isn't currently possible with this script."
                return False
            if packetType in (40, 41):
                print "This stream is encrypted with FlashAccess DRM. Decryption of such streams isn't currently possible with this script."
                return False
            fragPos += totalTagLen
        return True

    def readInt8(self, data, pos):
        return ord(struct.unpack_from(">c", data, pos)[0])

    def readInt24(self, data, pos):
        return struct.unpack_from(">L", "\0" + data[pos:pos + 3], 0)[0]

def main():
    global NumWorkerThreads
    if len(sys.argv) > 2:
        NumWorkerThreads = int(sys.argv[2])
    else:
        NumWorkerThreads = 7
    st = time.time()
    manifast = 'http://h264media01.ly.gov.tw:1935/vod/_definst_/mp4:300KClips/a7d6027a1ded6aa6982806f154ed24239c450e450740cf30fe001e560f0d6da5e9562172e945f005.mp4/manifest.f4m'
    x = M6(manifast)
    infos = x.getInfos()
    for item in infos.items():
        print item[0]+' : '+str(item[1])
    x.download()
    print 'Download time:', time.time() - st

if __name__ == "__main__":
    main()
