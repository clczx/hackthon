#-*- coding: utf8 -*-
import pandas as pd
from datetime import datetime, date, timedelta
import tushare as ts

import setting
from db_client import *
import sys

reload(sys)
sys.setdefaultencoding('utf8')
ts.set_token('eaf6b3ffd2808fee8221dbbc2ab223c1ffa4e64c29ce508d7fcdaefd09c264ba')


def get_hs300():
    st = ts.Market()

    hs300_df = st.MktIdxd(indexID='000300.ZICN', field=u"tradeDate,closeIndex")
    hs300_df.columns = ['nav_date', 'close_price']


    db_config = setting.DATABASES['fund_stat']
    conn,cr = create_db_connection(db_config['HOST'],db_config['DB'],db_config['PORT'],db_config['USER'],db_config['PASSWD'])
    pd.io.sql.to_sql(hs300_df, "hs300_info", conn, flavor='mysql', if_exists='append', index=False)
    
    db_close(conn,cr)
    

if __name__ == "__main__":
    get_hs300()



