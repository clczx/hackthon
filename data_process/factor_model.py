#-*- coding: utf-8 -*-
import sys
import setting
from db_client import *

from datetime import datetime, date, timedelta
import numpy as np
from sklearn.linear_model import LinearRegression as lr
import json


def conv(adjust_nav_daily):
    ret = {}
    for i in xrange(len(adjust_nav_daily) - 1):
        (_, adjust_nav_pre) = adjust_nav_daily[i]
        (dt, adjust_nav) = adjust_nav_daily[i+1]
        ret[dt] = (adjust_nav - adjust_nav_pre) / adjust_nav_pre
    return ret


def factor_analysis(x, y):
    model = lr()
    model.fit(x,y)
    print "Alpha:", model.intercept_
    print "Betas:", model.coef_
    r2_score = model.score(x,y)
    print "R^2:", r2_score
    result_data = {"Betas" : model.coef_.tolist(), "R^2": r2_score, "period" : {}}
    for i in xrange(4):
        model.fit(x[len(x)/4*i:len(x)/4*(i+1)], y[len(x)/4*i:len(x)/4*(i+1)])
        print "Alpha:" + str(i) + ":", model.intercept_
        print "Betas:" + str(i) + ":", model.coef_
        period_r2_score = model.score(x,y)
        print "R^2:" + str(i) + ":", period_r2_score 
        result_data['period']['Q' + str(i+1)] = {'Betas' : model.coef_.tolist(), "R^2" : period_r2_score}
#    print result_data
    return result_data


def run(dt):
    db_config = setting.DATABASES['fund_stat']
    conn,cr = create_db_connection(db_config['HOST'],db_config['DB'],db_config['PORT'],db_config['USER'],db_config['PASSWD'])
    
    one_years_age = dt - timedelta(days = 600)
    sql = "select `date`,  market, smb, hml, mom from factor_daily where `date` >= %s and `date` <= %s order by `date` "
    print one_years_age, dt
    cr.execute(sql, (one_years_age, dt))
    factor_daily = {}
    date_list = []
    for rz in cr.fetchall():
        date = rz['date']
        market = rz['market']
        smb = rz['smb']
        hml = rz['hml']
        mom = rz['mom']
        date_list.append(date)
        factor_daily[date] = [market, smb, hml, mom]


    sql = "select code from fund_overview "
    cr.execute(sql)
    count = 0
    for rz in cr.fetchall():
        code = rz['code']
        print "code:" + code
        sql = "select endDate, ADJUST_NAV, NAV from fund_nav where code=%s and ADJUST_NAV is not NULL order by endDate"
        cr.execute(sql, (code,))
        adjust_nav_daily = []
        for rz2 in cr.fetchall():
            end_date = rz2['endDate'] 
            adjust_nav = rz2['ADJUST_NAV']
            adjust_nav_daily.append((end_date, adjust_nav))
        return_daily_list = conv(adjust_nav_daily)

        x = []
        y = []
        for dt in date_list:
            if dt in return_daily_list:
                x.append(factor_daily[dt])
                y.append(return_daily_list[dt])
        if len(x) > 200:
            result_data = factor_analysis(x, y)
            json_data =  json.dumps(result_data)
            sql = "update fund_overview set factor_info = %s where code = %s"
            cr.execute(sql, (json_data, code))
            count += 1
            if count % 500 == 0:
                conn.commit()

    conn.commit()
    db_close(conn, cr)


if __name__ == "__main__":
    dt = date.today()
    run(dt)

    


