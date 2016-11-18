#-*- coding: utf-8 -*-
import tushare as ts
import sys
import os
import numpy as np
import pandas as pd
from pandas.compat import StringIO
import warnings


import setting
from db_client import *


ts.set_token('eaf6b3ffd2808fee8221dbbc2ab223c1ffa4e64c29ce508d7fcdaefd09c264ba')

def update_fund_nav():
    db_config = setting.DATABASES['fund_stat']
    conn,cr = create_db_connection(db_config['HOST'],db_config['DB'],db_config['PORT'],db_config['USER'],db_config['PASSWD'])
    
    fd = ts.Fund()

    cnt = 0


    for line in open("fundcode"):
        tc = line.strip()
        print cnt,"code:",tc
        cnt += 1
        #Get fund info
        f1 = fd.FundNav(ticker = tc, field = "secID,secShortName,endDate,NAV,ACCUM_NAV,ADJUST_NAV")
        if not f1.empty:
            f1['code'] = tc
            pd.io.sql.to_sql(f1, "fund_nav", conn, flavor='mysql', if_exists='append', index=False)

    conn.commit()
    db_close(conn,cr)

if __name__ == "__main__":
    update_fund_nav()

