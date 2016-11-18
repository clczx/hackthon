from flask import Flask, render_template, request, jsonify
import marshal

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


@app.route('/', methods=['POST', 'GET'])
def index():
    return render_template('index.html')

@app.route('/fundinfo', methods=['POST', 'GET'])
def fundinfo():
    return render_template('fundinfo.html')

@app.route('/fundstar', methods=['POST', 'GET'])
def fundstar():
    return render_template('fundstar.html')

@app.route('/api/suggest', methods=['POST', 'GET'])
def get_suggest():
    query = request.args.get('query', None)
    if query:
        print query
        cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)

        data = []
        sql = "select code, fund_name from fund_overview where code like '%s%%' or fund_name like '%s%%' order by annaul_return desc limit 10" % (query, query)
        print sql
        cur.execute(sql)
        for rz in cur.fetchall():
            code = rz['code'] 
            fund_name = rz['fund_name']
            print code, fund_name
            if code.startswith(query):
                data.append(code)
            else:
                data.append(fund_name)

#        data = ['PHP', 'MySQL', 'SQL', 'PostgreSQL', 'HTML', 'CSS', 'HTML5', 'CSS3', 'JSON']
        result = {"status" : "Ok", 'result': data}
        return jsonify(**result)
    else:
        result = {"status" : "failed", 'result': "invalid query"}
        return jsonify(**result)

if __name__ == "__main__":
    app.run(port=5000, debug=True)
