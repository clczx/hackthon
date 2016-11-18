from flask import Flask, render_template, request, jsonify, session, redirect, url_for
import marshal
import json
from datetime import datetime, date, timedelta
import numpy as np

import MySQLdb
from flask_mysqldb import MySQL

app = Flask(__name__)
app.config.update(
        MYSQL_HOST =  "10.100.143.244",
        MYSQL_DB   =  "fund_stat",
        MYSQL_USER  = "root",
        MYSQL_PASSWORD = ""
        )
mysql = MySQL(app)

ISOTIMEFORMAT='%Y-%m-%d'
app.secret_key = 'A0Zr98j/3yX R~XHH!jmN]LWX/,?RT'

@app.route('/', methods=['POST', 'GET'])
def index():
    username = None
    if 'username' in session:
	username = session["username"]
    return render_template('index.html', username=username)


@app.route('/fundselector', methods=['POST', 'GET'])
def fundselector():
    return render_template('fundselector.html')


@app.route('/fundinfo', methods=['POST', 'GET'])
def fundinfo():
    fundinfo = None
    funddata = None
    fundquery = None
    if request.method == "POST":
        fundquery = request.form["fundquery"]
    if request.method == "GET":
        fundquery = request.args.get("fund_code")
    if fundquery:
        print fundquery
        cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        sql = "select * from fund_overview where code='%s' or fund_name='%s' " % (fundquery, fundquery)
        cur.execute(sql)
        result = cur.fetchall()
        if len(result) != 0:
            fundinfo = result[0]
            if fundinfo["factor_percentile"]:
                funddata = json.loads(fundinfo["factor_percentile"])
    return render_template('fundinfo.html', fund=fundinfo, funddata=funddata)


@app.route('/fundstar', methods=['POST', 'GET'])
def fundstar():
    funddata = None
    cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    sql = "select * from user_fund_saving where user_id=1 and state=1"
    cur.execute(sql)
    funds = []
    entries = []
    for rz in cur.fetchall():
        funds.append(rz["fund_code"])
    for code in funds:
        sql = "select * from fund_overview where code=%s" % (code)
        cur.execute(sql)
        ret = cur.fetchall()[0]
        entries.append([ret["code"], ret["fund_name"], ret["tags"]])
    return render_template('fundstar.html', entries = entries)


@app.route('/api/suggest', methods=['POST', 'GET'])
def get_suggest():
    query = request.args.get('query', None)
    if query:
        print query
        cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)

        data = []
        sql = "select code, fund_name from fund_overview where code like '%s%%' or fund_name like '%s%%' order by annaul_return desc limit 10" % (query, query)
        cur.execute(sql)
        for rz in cur.fetchall():
            code = rz['code'] 
            fund_name = rz['fund_name']
            print code, fund_name
            if code.startswith(query):
                data.append(code)
            else:
                data.append(fund_name)

        result = {"status" : "Ok", 'result': data}
        return jsonify(**result)
    else:
        result = {"status" : "failed", 'result': "invalid query"}
        return jsonify(**result)


@app.route('/api/factor/market', methods=['GET'])
def get_factor_market():
    code = request.args.get('query', None)
    if code:
        today = date.today()
        one_years_ago = today - timedelta(days = 365)

        cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        sql = "select close_price, nav_date from hs300_info where nav_date >= %s and nav_date <= %s"
        cur.execute(sql, (one_years_ago, today))

        hs300_data_dict = {}
        date_list = []
        for rz in cur.fetchall():
            close_price = rz['close_price']
            nav_date = rz['nav_date']
            hs300_data_dict[nav_date] =  close_price        
            date_list.append(nav_date)

        fund_data_dict = {}
        sql = "select endDate, ADJUST_NAV, NAV from fund_nav where code=%s and ADJUST_NAV is not NULL \
            and endDate >= %s and endDate <=%s"
        cur.execute(sql, (code, one_years_ago, today))
        for rz in cur.fetchall():
            endDate = rz['endDate']
            adjust_nav = rz['ADJUST_NAV']
            fund_data_dict[endDate] = adjust_nav

        result_data = {"dt": [], "hs300":[], code :[]}
        if date_list and fund_data_dict:
            for dt in date_list:
                if dt in fund_data_dict:
                    result_data['dt'].append(dt.strftime(ISOTIMEFORMAT))
                    result_data['hs300'].append(hs300_data_dict[dt])
                    result_data[code].append(fund_data_dict[dt])
            result_data['hs300'] = np.round(get_acc_return(result_data['hs300']), 4).tolist()
            result_data[code] = np.round(get_acc_return(result_data[code]), 4).tolist()
#            print result_data['hs300']
#            print result_data[code]
#            print result_data['dt']
            result = {"status" : "Ok", "result" : result_data}
            return jsonify(**result)
        else:
            result = {"status" : "failed", "result": "invalid query result"}
            return jsonify(**result)
    else:
        result = {"status" : "failed", "result": "invalid query"}
        return jsonify(**result)


@app.route('/api/fund/saving', methods=['GET'])
def saving_user_fund():
    fund_code = request.args.get('fund_code', None)
    user_id = request.args.get('user_id', 1)
    if fund_code and user_id:

        cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        sql = "replace into user_fund_saving (user_id, fund_code, state) values(%s, %s, %s)"
        cur.execute(sql, (user_id, fund_code, 1))
        mysql.connection.commit()

        result = {"status" : "Ok"}
        return jsonify(**result)
    else:
        result = {"status" : "failed", "result": "invalid query"}
        return jsonify(**result)

@app.route('/api/fund/delete', methods=['GET'])
def delete_user_fund():
    fund_code = request.args.get('fund_code', None)
    user_id = request.args.get('user_id', 1)
    if fund_code and user_id:
        cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        sql = "update user_fund_saving set state=%s where user_id=%s and fund_code=%s"
        cur.execute(sql, (0, user_id, fund_code))
        mysql.connection.commit()

        result = {"status" : "Ok"}
        return jsonify(**result)
    else:
        result = {"status" : "failed", "result": "invalid query"}
        return jsonify(**result)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        session['username'] = request.form['username']
        return redirect(url_for('index'))
    return '''
        <form action="" method="post">
            <p><input type=text name=username>
            <p><input type=submit value=Login>
        </form>
    '''

@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('index'))

@app.route('/api/fund/selector', methods=['GET'])
def fund_selector():
    tags = request.args.get('tags', None)
    if tags:
        cur = mysql.connection.cursor()

        data = []
        sql = "select code, fund_name, acc_return, annaul_return, max_drawdown, volatility, sharp_ratio \
            from fund_overview where tags = '%s' order by annaul_return desc limit 10" % (tags)
        cur.execute(sql)
        for rz in cur.fetchall():
            data.append(rz)
        result = {"status" : "Ok", 'result': data}
        return jsonify(**result)

        result = {"status" : "Ok"}
        return jsonify(**result)
    else:
        result = {"status" : "failed", "result": "invalid query"}
        return jsonify(**result)



def get_acc_return(daily_nav):
    ret = []
    for i in range(len(daily_nav)):
        daily_ret = daily_nav[i] / daily_nav[0] - 1
        ret.append(daily_ret)
    return ret


if __name__ == "__main__":
    app.run(port=5000, debug=True)
