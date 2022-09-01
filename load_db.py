import pymysql

db = pymysql.connect(
    user='root',
    passwd='1234',
    host='127.0.0.1',
    db='userdb',
    charset='utf8'
)

cursor = db.cursor()

def get_logininfo(userid, password):
    sql = "SELECT * FROM userinfo where user_id = %s AND password= %s"
    cursor.execute(sql, [userid, password])
    result = cursor.fetchall()
    return result

def get_userinfo(userid):
    sql = "SELECT * FROM history where user_id = %s"
    cursor.execute(sql, userid)
    result = cursor.fetchall()
    return result

def register(userid, password):
    sql = "INSERT INTO userinfo(user_id, password) VALUES (%s, %s)"
    cursor.execute(sql, [userid, password])
    result = cursor.fetchall()
    return result