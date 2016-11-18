#-*- coding: utf-8 -*-
import sys
import setting
from db_client import *

from datetime import datetime, date, timedelta
import numpy as np
import json

def getIndex(s,sl):
    index = 0
    while s > sl[index] and index < len(sl) - 1:
        index += 1
    return float(index) / len(sl)


def get_risk_tag(max_drawdown):
    if max_drawdown >= 0.2:
        return "高风险"
    elif max_drawdown >= 0.15:
        return "中高风险"
    elif max_drawdown >= 0.1:
        return "中风险"
    elif max_drawdown < 0.1:
        return "中低风险"
        
def get_size_tag(value):
    if value >= 0.8:
        return "中小盘"
    else:
        return "大盘"


def get_value_tag(value):
    if value >= 0.7:
        return "价值"
    elif value < 0.3:
        return "成长"
    else:
        return "平衡"

        
def get_tags(factor_percentile, max_drawdown):
    result_tags = []
    if factor_percentile:
        data = json.loads(factor_percentile)
        percentile = data['percentile']
        result_tags.append(get_risk_tag(max_drawdown))
        result_tags.append(get_size_tag(percentile[1]))
        result_tags.append(get_value_tag(percentile[2]))
    return result_tags

def process():
    db_config = setting.DATABASES['fund_stat']
    conn,cr = create_db_connection(db_config['HOST'],db_config['DB'],db_config['PORT'],db_config['USER'],db_config['PASSWD'])

    today = date.today()
    sql = "select code, annaul_return, max_drawdown, factor_percentile from fund_overview"
    cr.execute(sql)

    code_annaul_dict = {}
    annual_list = []
    
    count = 0
    for rz in cr.fetchall():
        code = rz['code']
        print "code:" + code
        factor_percentile = rz['factor_percentile']
        annaul_return = rz['annaul_return']
        max_drawdown = rz['max_drawdown']
        tags = get_tags(factor_percentile, max_drawdown)
        if tags:
            sql = "update fund_overview set tags=%s where code = %s"
            cr.execute(sql, ((',').join(tags), code))

            count +=1
            if count % 500 == 0:
                conn.commit()
        sql = "select min(endDate) as start_dt from fund_nav where code = %s"
        cr.execute(sql, (code,))
        result = cr.fetchone()
        if result:
           start_dt = result['start_dt']
           days = (today - start_dt.date()).days
           if days > 365:
               annual_list.append(annaul_return) 
               code_annaul_dict[code] = annaul_return
    
    annual_list = sorted(annual_list)      
    count = 0
    for code in code_annaul_dict.keys():
        print "code:" + code
        annaul_return = code_annaul_dict[code]
        p1 = getIndex(annaul_return, annual_list)
        level = np.ceil(p1 * 5 + 0.001)
        if level > 5:
            level = 5 
        sql = "update fund_overview set level=%s where code = %s"
        cr.execute(sql, (level, code))
        count +=1
        if count % 500 == 0:
            conn.commit()

    conn.commit()
    db_close(conn, cr)

if __name__ == "__main__":
    process()
