import mysql.connector
from settings.config import Database, Config
from datetime import datetime
from functions.general_functions import *


def insert_general_record(action_, data_, fk_nick_):
    try:
        c = Config()
        database_ = Database()
        config = database_.config
        cnx = mysql.connector.connect(**config)
        cursor = cnx.cursor()
        now = datetime.now()
        query = "INSERT INTO records(action, data, dtime, fk_nick) VALUES (%s, %s, %s, %s);"
        data = (action_, str(data_), now, fk_nick_,)
        cursor.execute(query, data)
        cnx.commit()
        cnx.close()
    except Exception as e:
        print e