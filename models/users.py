import mysql.connector
from settings.config import Database, Config
from functions.general_functions import encrypt_pass, random_salt, get_random
from datetime import datetime, timedelta

def get_email(user_):
    database_ = Database()
    config = database_.config
    cnx = mysql.connector.connect(**config)
    cursor = cnx.cursor()
    query = "SELECT email FROM users WHERE nick = %s"
    data = (user_,)
    cursor.execute(query, data)
    for (email) in cursor:
        r = str(email[0])
        return r
    cursor.close()
    cnx.close()
    return ''

def user_email_exist(user_):
    database_ = Database()
    config = database_.config
    cnx = mysql.connector.connect(**config)
    cursor = cnx.cursor()
    query = "SELECT nick, email FROM users WHERE nick = %s or email =%s"
    data = (user_,user_,)
    cursor.execute(query, data)
    r = ['','']
    for (nick, email) in cursor:
        r = [str(nick), str(email)]
        return [True, r]
    cursor.close()
    cnx.close()
    return [False, r]

def get_salt_of_user(user_):
    database_ = Database()
    config = database_.config
    cnx = mysql.connector.connect(**config)
    cursor = cnx.cursor()
    query = "SELECT salt FROM users WHERE nick = %s"
    data = (user_,)
    cursor.execute(query, data)
    for (salt) in cursor:
        r = str(salt[0])
        return r
    cursor.close()
    cnx.close()
    return r

def login_user(user_, passw_):
    database_ = Database()
    config = database_.config
    cnx = mysql.connector.connect(**config)
    cursor = cnx.cursor()
    salt = get_salt_of_user(user_)
    passw_salted = encrypt_pass(passw_,salt)
    query = "SELECT nick FROM users WHERE nick = %s AND password = %s "
    data = (user_, passw_salted)
    cursor.execute(query, data)
    for (nick) in cursor:
        r = True
        return r
    cursor.close()
    cnx.close()
    r = False
    return r

def get_nick_by_email(email):
    database_ = Database()
    config = database_.config
    cnx = mysql.connector.connect(**config)
    cursor = cnx.cursor()
    salt = get_salt_of_user(user_)
    passw_salted = encrypt_pass(passw_,salt)
    query = "SELECT nick, email FROM users WHERE email = %s "
    data = (user_, passw_salted)
    cursor.execute(query, data)
    for (nick, email) in cursor:
        return nick
    cursor.close()
    cnx.close()
    r = False
    return r

def updatepass(user_ , pass_):
    try:
        database_ = Database()
        config = database_.config
        cnx = mysql.connector.connect(**config)
        cursor = cnx.cursor()
        salt = random_salt()
        password = encrypt_pass(pass_, salt)
        semi_query = ("UPDATE users "
                      "SET password=%s , salt=%s "
                      "WHERE nick=%s")
        data = (str(password),str(salt), user_)
        cursor.execute(semi_query, data)
        cnx.commit()
        cnx.close()
        return True
    except Exception as e:
        print e
        return False

def get_rol_of_user(user_):
    database_ = Database()
    config = database_.config
    cnx = mysql.connector.connect(**config)
    cursor = cnx.cursor()
    query = "SELECT fk_roluser FROM users WHERE nick = %s;"
    data = (user_,)
    cursor.execute(query, data)
    for (rol_id) in cursor:
        return rol_id[0]
    cursor.close()
    cnx.close()
    return ''

def get_recovery_token(user_):
    token = ''
    c = Config()
    database_ = Database()
    config = database_.config
    cnx = mysql.connector.connect(**config)
    cursor = cnx.cursor()
    query = "SELECT token FROM recovery_pass_token WHERE used = 0 AND  expire >= NOW() AND fk_nick = %s;"
    data = (user_,)
    cursor.execute(query, data)
    for (token) in cursor:
        return True, token
    cursor.close()
    cnx.close()
    return False, token

def insert_token(user_):
    try:
        token = get_random(30)
        c = Config()
        database_ = Database()
        config = database_.config
        cnx = mysql.connector.connect(**config)
        cursor = cnx.cursor()
        exp = datetime.now() - timedelta(minutes=60*4)
        query = "INSERT INTO recovery_pass_token(token, fk_nick, expire, used) VALUES (%s, %s, DATE_ADD(NOW(), INTERVAL 4 HOUR), 0);"
        data = (str(token),user_,)
        cursor.execute(query, data)
        cnx.commit()
        cnx.close()
        return True , token
    except Exception as e:
        print e
        return False, ''
    

def updatestatus_recovery_token(user_,token_ ):
    try:
        database_ = Database()
        config = database_.config
        cnx = mysql.connector.connect(**config)
        cursor = cnx.cursor()
        semi_query = ("UPDATE recovery_pass_token "
                      "SET used=%i "
                      "WHERE fk_nick=%s AND token=%s;")
        data = (1, user_,token_)
        cursor.execute(semi_query, data)
        cnx.commit()
        cnx.close()
        return True
    except Exception as e:
        print e
        return False

def get_all_countries():
    database_ = Database()
    config = database_.config
    cnx = mysql.connector.connect(**config)
    cursor = cnx.cursor()
    query = "SELECT country, descr FROM countries WHERE 1= 1;"
    cursor.execute(query)
    r = []
    for (country, descr ) in cursor:
        r.append([str(country), str(descr)])
    cursor.close()
    cnx.close()
    return r


def create_user(nick_, email_, sex_, school, class_, birth_year_, birth_month_, birth_day_, country_):
    try:
        token = get_random(30)
        c = Config()
        database_ = Database()
        config = database_.config
        cnx = mysql.connector.connect(**config)
        cursor = cnx.cursor()
        pass_ = get_random(8)
        salt = random_salt()
        password = encrypt_pass(pass_, salt)
        query = "INSERT INTO users(nick, email, fk_roluser, password, salt, sex, school, class, birth_year, birth_month, birth_day, fk_country) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s);"
        data = (nick_, email_,'Student', password,salt, sex_, school, class_, birth_year_, birth_month_, birth_day_, country_,)
        cursor.execute(query, data)
        cnx.commit()
        cnx.close()
        return True , pass_
    except Exception as e:
        print e
        return False, ''
