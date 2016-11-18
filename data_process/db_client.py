import MySQLdb

def create_db_connection(mysql_host,mysql_db,myssql_port,mysql_user,mysql_passwd):
    conn = MySQLdb.connect(host=mysql_host, port=myssql_port, user=mysql_user, db=mysql_db, passwd=mysql_passwd)
    cr = conn.cursor(MySQLdb.cursors.DictCursor)
    return conn, cr

def db_close(conn,cr):
    cr.close()
    conn.close()


