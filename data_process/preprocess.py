#-*- coding: utf-8 -*-
from datetime import datetime, date, timedelta
import tushare as ts

import setting
from db_client import *

ts.set_token('eaf6b3ffd2808fee8221dbbc2ab223c1ffa4e64c29ce508d7fcdaefd09c264ba')

def preprocess():
    db_config = setting.DATABASES['fund_stat']
    conn,cr = create_db_connection(db_config['HOST'],db_config['DB'],db_config['PORT'],db_config['USER'],db_config['PASSWD'])
    
    fd = ts.Fund()

    cnt = 0
    for line in open("fundcode"):
        tc = line.strip()
        print cnt,"code:",tc
        cnt += 1

        f1 = fd.FundNav(ticker = tc, field = "secID,secShortName,endDate,NAV,ACCUM_NAV,ADJUST_NAV")
        if not f1.empty:
            secID = f1.ix[0, "secID"]
#            print secID

            sql = "update fund_nav set code= %s where secID=%s"
            cr.execute(sql, (tc, secID))
        if cnt % 50 == 0:
            print "commit"
            conn.commit()
#            for rz in cr.fetchall():
#                print rz
        
    conn.commit()
    db_close(conn,cr)


if __name__== "__main__":
    preprocess()
