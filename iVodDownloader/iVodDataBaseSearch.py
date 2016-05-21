#!/usr/bin/env python
# -*- coding: utf-8 -*-
# search database
import sys,os.path
reload(sys)
sys.setdefaultencoding('utf8')
import sqlite3

class iVodDataBaseSearch(object):
    StartTime =''
    EndTime =''
    Committees=[]

    def __init__(self,argStartTime,argEndTime,argCommittees):
        self.Committees = argCommittees
        self.StartTime = argStartTime
        self.EndTime = argEndTime
        

    def SearchFull(self):
        db_con = sqlite3.connect('./db/iVod_LY.sqlite')
        CommitteeString = "CM_NAM = \"" + "\" OR CM_NAM = \"".join(self.Committees)+"\""
        
        cur = db_con.cursor()
        cur.execute("SELECT * FROM iVOD_FullMeeting where ST_TIM Between \"" + self.StartTime + "\"  AND \"" + self.EndTime + "\" AND ("  +CommitteeString +") ORDER BY ST_TIM DESC ,CM_NAM ASC")
        return cur.fetchall()
    def SearchIndividual(self):
        db_con = sqlite3.connect('./db/iVod_LY.sqlite')
        CommitteeString = "CM_NAM = \"" + "\" OR CM_NAM = \"".join(self.Committees)+"\""
        
        cur = db_con.cursor()
        cur.execute("SELECT * FROM iVOD_Lglt where ST_TIM Between \"" + self.StartTime + "\"  AND \"" + self.EndTime + "\" AND ("  +CommitteeString +") ORDER BY ST_TIM DESC ,CM_NAM ASC")
        return cur.fetchall()