#-*- coding: utf-8 -*-
import sys
import setting
from db_client import *

import evaluate
import numpy as np

reload(sys)
sys.setdefaultencoding('utf-8')

def process():
    db_config = setting.DATABASES['fund_stat']
    conn,cr = create_db_connection(db_config['HOST'],db_config['DB'],db_config['PORT'],db_config['USER'],db_config['PASSWD'])

    fund_overview_code_set = set([])
    sql = "select code from fund_overview"
    cr.execute(sql)
    for rz in cr.fetchall():
        code = rz['code']
        fund_overview_code_set.add(code)


    sql = "select distinct code from fund_nav where code is not NULL"

    cr.execute(sql)
    count = 0
    for rz in cr.fetchall():
        code = rz['code']
        print "code:" + code
        print count 
        count += 1
        if count > 349:
            adjust_daily_return = []
            sql = "select ADJUST_NAV, secShortName from fund_nav where code = %s and ADJUST_NAV is not NULL"
            cr.execute(sql, (code, ))
            for rz2 in cr.fetchall():
                fund_name = rz2['secShortName']
                adjust_nav = rz2['ADJUST_NAV']
                adjust_daily_return.append(adjust_nav)
            if len(adjust_daily_return) > 30:
                print "len: %d" % (len(adjust_daily_return))
                return_df = np.array(adjust_daily_return)
                return_df[1:] = return_df[1:]*1.0 / return_df[:-1] -1
                return_df[:1] = 0
                acc_returns = evaluate.get_accum_returns(return_df)
                annual_rate = evaluate.get_annual_rate(acc_returns)
                max_drow_down = evaluate.get_max_draw_down(acc_returns)
                volatility = evaluate.get_volatility(return_df)
                sharp_ratio = evaluate.get_sharpe(annual_rate, volatility)
                
                print fund_name, acc_returns[-1], annual_rate, max_drow_down, volatility, sharp_ratio
                if code in fund_overview_code_set:
                    sql = "update fund_overview set acc_return = %s, annaul_return = %s,  max_drawdown = %s, volatility = %s, \
                           sharp_ratio = %s where code = %s "
                    cr.execute(sql, (acc_returns[-1], annual_rate, max_drow_down, volatility, sharp_ratio, code))
                else: 
                    sql = "insert into fund_overview (code, fund_name, acc_return, annaul_return, max_drawdown, volatility, sharp_ratio) \
    values (%s, %s, %s, %s, %s, %s, %s )"
                    cr.execute(sql, (code, fund_name, acc_returns[-1], annual_rate, max_drow_down, volatility, sharp_ratio ))
                if count % 1000 == 0:
                    conn.commit()
    conn.commit()
    db_close(conn,cr)

if __name__ == "__main__":
    process()
