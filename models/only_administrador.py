import mysql.connector
from settings.config import Database, Config

def a_get_all_users():
    database_ = Database()
    config = database_.config
    cnx = mysql.connector.connect(**config)
    cursor = cnx.cursor()
    query = "SELECT nick, email, sex, school, class as classs, fk_roluser, birth_year, birth_month, birth_day, fk_country FROM users WHERE 1 = 1;"
    cursor.execute(query,)
    r = []
    for (nick, email, sex, school, classs, fk_roluser, birth_year, birth_month, birth_day, fk_country) in cursor:
        temp = [nick, email, sex, school, classs, fk_roluser, birth_year, birth_month, birth_day, fk_country]
        r.append(temp)
    cursor.close()
    cnx.close()
    return r