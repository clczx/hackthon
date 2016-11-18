#-*- coding: utf-8 -*-
import sys
import setting
from db_client import *

from datetime import datetime, date, timedelta
import numpy as np
import json

R2_LOW_SCORE = 0.7

def getIndex(s,sl):
    index = 0
    while s > sl[index] and index < len(sl) - 1:
        index += 1
    return float(index) / len(sl)


def get_percentile(beta, beta_all_dict):
    p1 = getIndex(beta[0], beta_all_dict['market'])
    p2 = getIndex(beta[1], beta_all_dict['smb'])
    p3 = getIndex(beta[2], beta_all_dict['hml'])
    p4 = getIndex(beta[3], beta_all_dict['mom'])
    return [p1, p2, p3, p4]


def process_factor():
    db_config = setting.DATABASES['fund_stat']
    conn,cr = create_db_connection(db_config['HOST'],db_config['DB'],db_config['PORT'],db_config['USER'],db_config['PASSWD'])

    sql = "select code, factor_info from fund_overview where factor_info is not NULL "
    cr.execute(sql)

    beta_all_dict = {'market': [], 'smb': [] , 'hml': [], 'mom': []}
    beta_all_dict_q = {}
    beta_all_dict_q['Q1'] = {'market': [], 'smb': [] , 'hml': [], 'mom': []}
    beta_all_dict_q['Q2'] = {'market': [], 'smb': [] , 'hml': [], 'mom': []}
    beta_all_dict_q['Q3'] = {'market': [], 'smb': [] , 'hml': [], 'mom': []}
    beta_all_dict_q['Q4'] = {'market': [], 'smb': [] , 'hml': [], 'mom': []}
    fund_factor_dict = {}

    for rz in cr.fetchall():
        code = rz['code']
        factor_info = rz['factor_info']
        factor_info_data = json.loads(factor_info)

        fund_factor_dict[code] = factor_info_data
        if factor_info_data['R^2'] >= R2_LOW_SCORE:
            beta = factor_info_data['Betas']
            beta_all_dict['market'].append(beta[0])
            beta_all_dict['smb'].append(beta[1])
            beta_all_dict['hml'].append(beta[2])
            beta_all_dict['mom'].append(beta[3])
            period = factor_info_data['period']
            for q in period:
                beta = period[q]['Betas']
                beta_all_dict_q[q]['market'].append(beta[0])
                beta_all_dict_q[q]['smb'].append(beta[1])
                beta_all_dict_q[q]['hml'].append(beta[2])
                beta_all_dict_q[q]['mom'].append(beta[3])

    beta_all_dict['market'] = sorted(beta_all_dict['market'])
    beta_all_dict['smb'] = sorted(beta_all_dict['smb'])
    beta_all_dict['hml'] = sorted(beta_all_dict['hml'])
    beta_all_dict['mom'] = sorted(beta_all_dict['mom'])

    count = 0
    for code in fund_factor_dict.keys():
        print "code:" + code
        factor_info_data = fund_factor_dict[code]
        beta = factor_info_data['Betas']
        percentile = get_percentile(beta, beta_all_dict)
#        p1 = getIndex(beta[0], beta_all_dict['market'])
#        p2 = getIndex(beta[1], beta_all_dict['smb'])
#        p3 = getIndex(beta[2], beta_all_dict['hml'])
#        p4 = getIndex(beta[3], beta_all_dict['mom'])

        result_data = { "percentile" : percentile, "period": {}}
        period = factor_info_data['period']
        for q in period:
            beta = period[q]['Betas']
            percentile = get_percentile(beta, beta_all_dict)
            result_data["period"][q] = percentile
        json_data = json.dumps(result_data)
        sql = "update fund_overview set factor_percentile = %s where code = %s"
        cr.execute(sql, (json_data, code))
        count += 1
        if count % 500 == 0:
            conn.commit()
            
    conn.commit() 

    db_close(conn, cr)

if __name__ == "__main__":
    process_factor()


