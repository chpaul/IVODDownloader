#!/usr/bin/env python
# -*- coding: utf-8 -*-
# update database
import os, urllib, urllib2, json, cookielib, sys, random, time, datetime, subprocess
import io,os.path,unicodedata,shutil,sqlite3
from time import gmtime, strftime
reload(sys)
sys.setdefaultencoding('utf-8')
from PyQt4 import QtCore
class IVODDataBaseUpdate(object):
    currect_time =0
    dbLocation = ''
    MeetingDaylimit = 1
    base_url = 'http://ivod.ly.gov.tw/'
    committee_url = 'http://ivod.ly.gov.tw/Committee/CommsDate'
    committee ={
        '19':{'name': u'院會', 'code': 'YS'},
        '1':{'name': u'內政', 'code': 'IAD'},
        '17':{'name': u'外交及國防', 'code': 'FND'},
        '5':{'name': u'經濟', 'code': 'ECO'},
        '6':{'name': u'財政', 'code': 'FIN'},
        '8':{'name': u'教育及文化', 'code': 'EDU'},
        '9':{'name': u'交通', 'code': 'TRA'},
        '18':{'name': u'司法及法制', 'code': 'JUD'},
        '12':{'name': u'社會福利及衛生環境', 'code': 'SWE'},
        '13':{'name': u'程序', 'code': 'PRO'}}
        #'23':{'name': u'紀律', 'code': 'DIS'}}

    def __init__(self,argDBLocation, argMeetingDaylimit,argQTStatus):
        self.currect_time = 0
        self.dbLocation = argDBLocation
        self.MeetingDaylimit = argMeetingDaylimit
        self.qtStatus = argQTStatus

    #http://stackoverflow.com/questions/2677617/python-f-write-at-beginning-of-file

    @staticmethod
    def reset_cookie():
        #if time lagger then 15 min, will reset.
        if time.time() - IVODDataBaseUpdate.currect_time > 900:
            IVODDataBaseUpdate.currect_time = time.time()
            http_header = {'User-Agent': 'Mozilla/4.0 (compatible; MSIE 5.5; Windows NT)', 'Host': 'ivod.ly.gov.tw'}
            req = urllib2.Request('http://ivod.ly.gov.tw/', None, http_header)
            web = urllib2.urlopen(req)
            result = web.read()

    @staticmethod
    def get_committ_date_list(comt, start_date=None, end_date=None):
        http_header = {'Referer': 'http://ivod.ly.gov.tw/Committee',
            'Accept': '*/*',
            'User-Agent': 'Mozilla/4.0 (compatible; MSIE 5.5; Windows NT)',
            'Host': 'ivod.ly.gov.tw',
            'Connection': 'keep-alive',
            'X-Requested-With': 'XMLHttpRequest',
            'Pragma': 'no-cache'}
        req = urllib2.Request('http://ivod.ly.gov.tw/Committee/CommsDate', urllib.urlencode({'comtid': comt}), http_header)
        #try:
        if not start_date:
            start_date = '2011-01-01'
        if not end_date:
            end_date = datetime.datetime.now().strftime('%Y-%m-%d')
        web = urllib2.urlopen(req)
        if web.getcode() == 200:
            html = web.read()
            #print type(html)
            #print html
            html = html.decode('utf-8-sig')
            result = json.loads(html)
            date_list = []
            for i in result['mdate']:
                if end_date >= i['METDAT'] >= start_date:
                    date_list.append(i['METDAT'])
            return date_list
        else:
            return False

    @staticmethod
    def get_movie_by_date(comit, date, page=1):
        http_header = {'Referer': 'http://ivod.ly.gov.tw/Committee',
            'Accept': '*/*',
            'User-Agent': 'Mozilla/4.0 (compatible; MSIE 5.5; Windows NT)',
            'Host': 'ivod.ly.gov.tw',
            'Connection': 'keep-alive',
            'X-Requested-With': 'XMLHttpRequest',
            'Pragma': 'no-cache'}
        req = urllib2.Request('http://ivod.ly.gov.tw/Committee/MovieByDate', urllib.urlencode({'comtid': comit, 'date': date, 'page': page}), http_header)
        #try:
        web = urllib2.urlopen(req)
        if web.getcode() == 200:
            html_result = web.read()
            html_result = html_result.decode('utf-8-sig')
            #print html_result
            result = json.loads(html_result)
            return result
            #Find WZS_ID
        else:
            return False

    @staticmethod
    def get_movie_url(wzs_id, t, quality='w'):
        if t == 'whole':
            url_part = 'Full'
        elif t == 'clip':
            url_part = 'VOD'
        else:
            return False
        if quality == 'w':
            return 'http://ivod.ly.gov.tw/Play/%s/%s/1M' % (url_part, wzs_id)
        elif quality == 'n':
            return 'http://ivod.ly.gov.tw/Play/%s/%s/300K' % (url_part, wzs_id)
        else:
            return False

    @staticmethod
    def random_sleep():
        return
        time.sleep(random.randint(1,5))

    #更新資料庫
    def startUpdate(self):
        db_con = sqlite3.connect(str(self.dbLocation))
        Full_Result_By_MeetingDate ={}
        MeetingDaylimit =self.MeetingDaylimit
        #log 檔案
        logFile = open ('./ivod.log','a')

        logFile.write("----------------------------Start Time:"+strftime("%Y-%m-%d %H:%M:%S", time.localtime())+"-------------------------" +os.linesep)
        logFile.flush()

        IVODDataBaseUpdate.reset_cookie()
        for comit_id in self.committee.keys():
            IVODDataBaseUpdate.reset_cookie()
            self.qtStatus.append(u'開始掃描%s委員會可以抓取的影片...' % self.committee[comit_id]['name'])
            QtCore.QCoreApplication.processEvents()
            #print(u'開始掃描%s委員會可以抓取的影片...' % self.committee[comit_id]['name'])
            logFile.write("Check " + self.committee[comit_id]['name']   +os.linesep)
            logFile.flush()
            date_list = IVODDataBaseUpdate.get_committ_date_list(comit_id, None, None)
            date_list.sort(reverse=True)
            #for date in date_list:
            #    if(not Full_Result_By_MeetingDate.has_key(date)):
            #        Full_Result_By_MeetingDate[date] = {};
            #        List_MeetingDate.append(date)

            #for dateIdx in range(0,len(date_list)):#抓全部
            for dateIdx in range(0,int(MeetingDaylimit)):
                date = date_list[dateIdx]

                IVODDataBaseUpdate.reset_cookie()
                IVODDataBaseUpdate.random_sleep()
                movie_list = IVODDataBaseUpdate.get_movie_by_date(comit_id, date, 1)
                page_num = (int(movie_list['total']) / 5) + 1
                self.qtStatus.append(date)
                QtCore.QCoreApplication.processEvents()
                #print(date)
                for i in movie_list['full']:
                    cur = db_con.cursor()
                    cur.execute("Select * from iVOD_FullMeeting where MEREID=" + i['MEREID'])
                    IsRecordFound = cur.fetchone()
                    if IsRecordFound != None:
                        continue

                    iVOD_Full = i['CM_NAM'],int(i['DUTION']),i['ENCNAM'],bool(i['HFILEA']),bool(i['HFILEB']),bool(i['LFILEA']),bool(i['LFILEB']),int(i['MEETID']),int(i['MEREID']),i['METDEC'],bool(i['MFILEA']),bool(i['MFILEB']),i['RECNAM'],datetime.datetime.fromtimestamp(time.mktime( time.strptime(str(i['ST_TIM']),"%Y-%m-%d %H:%M"))),int(i['STAGE_'])
                    cur.execute("Insert into iVOD_FullMeeting(CM_NAM,DUTION,ENCNAM,HFILEA,HFILEB,LFILEA,LFILEB,MEETID,MEREID,METDEC,MFILEA,MFILEB,RECNAM,ST_TIM,STAGE_) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",(iVOD_Full))
                    logFile.write("\t- add full " + date + os.linesep)
                    logFile.flush()
                    IVODDataBaseUpdate.random_sleep()
                db_con.commit()
                #db_con = sqlite3.connect(IVODDataBaseUpdate.dbLocation)
                for num in xrange(1, (page_num + 1)):
                    if num != 1:
                        movie_list = IVODDataBaseUpdate.get_movie_by_date(comit_id, date, num)
                    for i in movie_list['result']:
                        cur = db_con.cursor()
                        cur.execute("Select * from iVOD_Lglt where WZS_ID=" + i['WZS_ID'])
                        IsRecordFound = cur.fetchone()
                        db_con.commit()
                        if IsRecordFound != None:
                            continue

                        iVOD_data= int(i['WZS_ID']),i['CH_NAM'],i['CLP_ST'],i['CLP_ET'],i['CM_NAM'],i['COMTST'],int(i['DUTION']),i['EN_NAM'],i['ENCNAM'],i['FILNAM'],bool(i['HFILEA']),bool(i['HFILEB']),bool(i['LFILEA']),bool(i['LFILEB']),i['LGLTIM'],int(i['MEETID']),i['METDEC'],bool(i['MFILEA']),bool(i['MFILEB']),i['MOVTIM'],i['PHOTO_'],bool(i['PUBLIC']),datetime.datetime.fromtimestamp(time.mktime( time.strptime(str(i['ST_TIM']),"%Y-%m-%d %H:%M"))),int(i['STAGE_']),i['SYS_ST'],i['SYS_ET']
                        cur.execute("Insert into iVOD_lglt(WZS_ID,CH_NAM,CLP_ST,CLP_ET,CM_NAM,COMTST,DUTION,EN_NAM,ENCNAM,FILNAM,HFILEA,HFILEB,LFILEA,LFILEB,LGLTIM,MEETID,METDEC,MFILEA,MFILEB,MOVTIM,PHOTO_,PUBLIC,ST_TIM,STAGE_,SYS_ST,SYS_ET) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",(iVOD_data))

                        #iVOD_dataList =iVOD_dataList,iVOD_data
                        logFile.write("\t-add personal "+ i['CH_NAM'] + " " + date + os.linesep)
                        logFile.flush()
                        IVODDataBaseUpdate.random_sleep()
                db_con.commit()
        logFile.write( "----------------------------End Time:"+strftime("%Y-%m-%d %H:%M:%S", time.localtime())+"-------------------------" +os.linesep)
        logFile.flush()
        logFile.close()
        self.qtStatus.append(u"更新完成")


    
#    
#req1 = urllib2.Request(uri)
#response = urllib2.urlopen(req1)
#cookie = response.headers.get('Set-Cookie')
#
## Use the cookie is subsequent requests
#req2 = urllib2.Request("http://ivod.ly.gov.tw/Legislator#lglt=2644&page=1")
#req2.add_header('cookie', cookie)
#response = urllib2.urlopen(req2)
#
#
#print (response.read())
