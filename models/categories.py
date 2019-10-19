import mysql.connector
from settings.config import Database, Config

def get_all_categories_profesor():
    database_ = Database()
    config = database_.config
    cnx = mysql.connector.connect(**config)
    cursor = cnx.cursor()
    query = "SELECT category, description FROM categories WHERE 1 = 1"
    cursor.execute(query)
    r = []
    for (category, description) in cursor:
        r.append([category, description])
    cursor.close()
    cnx.close()
    return r


def get_all_categories_student(nick_student):
    database_ = Database()
    config = database_.config
    cnx = mysql.connector.connect(**config)
    cursor = cnx.cursor()
    query = "SELECT all_c.fk_category, categories.description FROM all_challenges as all_c INNER JOIN class_challenges INNER JOIN class_list INNER JOIN categories INNER JOIN classes WHERE class_challenges.FK_challenge_id_number = all_c.id_number AND class_list.id_number = class_challenges.FK_class_id_number AND categories.category= all_c.fk_category AND classes.FK_student_nick = %s;"
    data = (nick_student,)
    cursor.execute(query,data)
    r = []
    for (category, description) in cursor:
        noesta = True
        if len(r) !=0:
            for x in r:
                if x[0] == category:
                    noesta = False
            if noesta:
                r.append([category, description,1])
            else:
                for x in r:
                    if x[0] == category:
                        x[2] = x[2] + 1
        else:
            r.append([category, description,1])
    cursor.close()
    cnx.close()
    return r
