import tushare as ts
import sys
import os
import marshal
import numpy as np
import pandas as pd
from pandas.compat import StringIO
from sklearn.linear_model import LinearRegression as lr
import warnings
import MySQLdb

mysql = MySQLdb.connect(host='localhost', port=3306, user='root', passwd='', db='fund_stat')

ts.set_token('eaf6b3ffd2808fee8221dbbc2ab223c1ffa4e64c29ce508d7fcdaefd09c264ba')

fd = ts.Fund()

cnt = 0

for line in open("fundcode"):
    tc = line.strip()
    print cnt,"code:",tc
    cnt += 1
    #Get fund info
    f1 = fd.FundNav(ticker = tc, field = "secID,secShortName,endDate,NAV,ACCUM_NAV,ADJUST_NAV")
    if not f1.empty:
        pd.io.sql.to_sql(f1, "fund_nav", mysql, flavor='mysql', if_exists='append', index=False)

