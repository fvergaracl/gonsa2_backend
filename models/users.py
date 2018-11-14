import mysql.connector
from settings.config import Database

def login_user(user_, passw_):
    database_ = Database()
    config = database_.config
    cnx = mysql.connector.connect(**config)
    cursor = cnx.cursor()
    query = "SELECT nick FROM ymi_usuario WHERE nick = %s AND passw = %s "
    data = (user_, passw_)
    cursor.execute(query, data)
    for (nick) in cursor:
        r = True, nick
        return r
    cursor.close()
    cnx.close()
    r = False, ''
    return r
