import mysql.connector
from settings.config import Database, Config
from datetime import datetime
from functions.general_functions import *

def new_class(school_, identificator_, class_, year_, _FK_owner_nick):
    try:
        c = Config()
        database_ = Database()
        config = database_.config
        cnx = mysql.connector.connect(**config)
        cursor = cnx.cursor()
        now = datetime.now()
        query = "INSERT INTO class_list(school, identificator, class, year, status, d_creation,FK_owner_nick) VALUES (%s, %s, %s,%s, %s, %s, %s);"
        data = (school_, identificator_, class_, year_,'active', now, str(_FK_owner_nick),)
        cursor.execute(query, data)
        cnx.commit()
        cnx.close()
        return True , 'The class has been successfully entered'
    except Exception as e:
        print e
        return False, 'Something went wrong'

def new_challenge_p(title_, summary_, description_, aims_, photo_, owner_ ,category_):
    try:
        c = Config()
        database_ = Database()
        config = database_.config
        cnx = mysql.connector.connect(**config)
        cursor = cnx.cursor()
        now = datetime.now()
        token_ = str(get_random_num(4)) + '-' + str(get_random_str(4))
        query = "INSERT INTO all_challenges(title,token_challenge, photourl, summary, description, aim, created, owner_fk_nick, fk_category) VALUES (%s, %s, %s, %s, %s,%s, %s, %s, %s);"
        data = (str(title_), str(token_), str(photo_), str(summary_), str(description_), str(aims_), now, str(owner_), str(category_),)
        cursor.execute(query, data)
        cnx.commit()
        cnx.close()
        return True 
    except Exception as e:
        print e
        return False

def get_id_challenge_by_token(token_):
    try:
        database_ = Database()
        config = database_.config
        cnx = mysql.connector.connect(**config)
        cursor = cnx.cursor()
        query = "SELECT id_number, token_challenge FROM all_challenges WHERE token_challenge = %s;"
        data = (token_,)
        cursor.execute(query, data)
        for (id_number, token_challenge) in cursor:
            return int(id_number)
        cursor.close()
        cnx.close()
        return 0
    except Exception as e:
        print e
        return 0

def new_permission(id_challenge_, nick_user):
    try:
        c = Config()
        database_ = Database()
        config = database_.config
        cnx = mysql.connector.connect(**config)
        cursor = cnx.cursor()
        now = datetime.now()
        query = "INSERT INTO evaluation_permissions(FK_all_challenges_id,FK_nick_evaluator) VALUES (%s, %s);"
        data = (id_challenge_, nick_user,)
        cursor.execute(query, data)
        cnx.commit()
        cnx.close()
    except Exception as e:
        print e

def new_challenge_p(title_, summary_, description_, aims_, photo_, owner_ ,category_):
    try:
        c = Config()
        database_ = Database()
        config = database_.config
        cnx = mysql.connector.connect(**config)
        cursor = cnx.cursor()
        now = datetime.now()
        token_ = str(get_random_num(4)) + '-' + str(get_random_str(4))
        query = "INSERT INTO all_challenges(title,token_challenge, photourl, summary, description, aim, created, owner_fk_nick, fk_category) VALUES (%s, %s, %s, %s, %s,%s, %s, %s, %s);"
        data = (str(title_), str(token_), str(photo_), str(summary_), str(description_), str(aims_), now, str(owner_), str(category_),)
        cursor.execute(query, data)
        cnx.commit()
        cnx.close()
        return True , token_
    except Exception as e:
        print e
        return False, token_

def get_all_classes_professor(_FK_owner_nick):
	try:
		database_ = Database()
		config = database_.config
		cnx = mysql.connector.connect(**config)
		cursor = cnx.cursor()
		query = "SELECT id_number, school, identificator, class AS class_, year, status FROM class_list WHERE FK_owner_nick = %s ORDER BY d_creation DESC;"
		data = (_FK_owner_nick,)
		cursor.execute(query, data)
		r = []
		for (id_number, school, identificator, class_, year, status) in cursor:
			temp = [id_number, school, identificator, class_, year, status]
			r.append(temp)
		cursor.close()
		cnx.close()
		return r
	except Exception as e:
		print e

def get_all_students_in_class_by_id(id_,_FK_owner_nick):
    try:
        database_ = Database()
        config = database_.config
        cnx = mysql.connector.connect(**config)
        cursor = cnx.cursor()
        query = "SELECT u.nick as nick , u.email as email, u.sex as sex, u.school as school, u.class as classs, u.fk_country as country FROM users as u INNER JOIN classes as c INNER JOIN class_list as cl WHERE c.FK_student_nick = u.nick AND c.FK_class_id_number = %s AND cl.id_number = c.FK_class_id_number AND cl.FK_owner_nick = %s;"
        data = (id_,_FK_owner_nick,)
        cursor.execute(query, data)
        r = []
        for (nick, email, sex, school, classs, country) in cursor:
            temp = [nick, email, sex, school, classs, country]
            r.append(temp)
        cursor.close()
        cnx.close()
        return r
    except Exception as e:
        print e

def it_s_my_class_professor(_FK_owner_nick, id_number_):
	try:
		database_ = Database()
		config = database_.config
		cnx = mysql.connector.connect(**config)
		cursor = cnx.cursor()
		query = "SELECT status FROM class_list WHERE FK_owner_nick = %s AND id_number = %s ORDER BY d_creation DESC;"
		data = (_FK_owner_nick,id_number_,)
		cursor.execute(query, data)
		for (status) in cursor:
			return True
		cursor.close()
		cnx.close()
		return False
	except Exception as e:
		print e
		return False

def add_student_to_class_professor(FK_class_id_number_, FK_student_nick_):
    try:
        c = Config()
        database_ = Database()
        config = database_.config
        cnx = mysql.connector.connect(**config)
        cursor = cnx.cursor()
        now = datetime.now()
        query = "INSERT INTO classes(FK_class_id_number, FK_student_nick) VALUES (%s, %s);"
        data = (FK_class_id_number_, FK_student_nick_,)
        cursor.execute(query, data)
        cnx.commit()
        cnx.close()
        # FALTA - enlazar estudiantes al desafio
        return True , 'The student has been successfully entered in the class'
    except Exception as e:
        if ('Duplicate entry' in str(e)) and ('for key' in str(e)):
        	return False, 'The student was previously registered in this class'
        else:
        	return False, 'Something went wrong'

def add_challenge_to_class_professor(FK_class_id_number_, FK_challenge_id_number_ ):
    try:
        c = Config()
        database_ = Database()
        config = database_.config
        cnx = mysql.connector.connect(**config)
        cursor = cnx.cursor()
        now = datetime.now()
        query = "INSERT INTO class_challenges(FK_class_id_number, FK_challenge_id_number ) VALUES (%s, %s);"
        data = (FK_class_id_number_, FK_challenge_id_number_,)
        cursor.execute(query, data)
        cnx.commit()
        cnx.close()
        # pendiente - enlazar estudiantes al desafio
        return True , 'The challenge has been successfully entered in the class'
    except Exception as e:
        if ('Duplicate entry' in str(e)) and ('for key' in str(e)):
        	return False, 'The challenge was previously registered in this class'
        else:
        	return False, 'Something went wrong'

def remove_student_to_class_professor(FK_class_id_number_, FK_student_nick_):
    try:
        c = Config()
        database_ = Database()
        config = database_.config
        cnx = mysql.connector.connect(**config)
        cursor = cnx.cursor()
        now = datetime.now()
        query = "DELETE FROM classes WHERE FK_class_id_number=%s AND FK_student_nick = %s;"
        data = (FK_class_id_number_, FK_student_nick_,)
        cursor.execute(query, data)
        row = cursor.rowcount
        cnx.commit()
        cnx.close()
        # pendiente - remover estudiantes al desafio
        if row >= 1:
        	return True , 'The student has been unlinked successfully of this class'
        else:
        	return True , 'No student was unlinked'
    except Exception as e:
    	return False, 'Something went wrong'	

def remove_challenge_to_class_professor(FK_class_id_number_, FK_challenge_id_number_):
    try:
        c = Config()
        database_ = Database()
        config = database_.config
        cnx = mysql.connector.connect(**config)
        cursor = cnx.cursor()
        now = datetime.now()
        query = "DELETE FROM class_challenges WHERE FK_class_id_number=%s AND FK_challenge_id_number = %s;"
        data = (FK_class_id_number_, FK_challenge_id_number_,)
        cursor.execute(query, data)
        row = cursor.rowcount
        cnx.commit()
        cnx.close()
        # pendiente - remover estudiantes al desafio
        if row >= 1:
        	return True , 'The challenge has been delete successfully of this class'
        else:
        	return True , 'No challenge was eliminated'
    except Exception as e:
    	return False, 'Something went wrong'

def edit_challenge_professor(id_number_challenge, title, summary, description, aim, category , FK_owner_nick):
    try:
        c = Config()
        database_ = Database()
        config = database_.config
        cnx = mysql.connector.connect(**config)
        cursor = cnx.cursor()
        now = datetime.now()
        query = "UPDATE all_challenges SET title =%s, summary =%s, description =%s, aim =%s, last_edit=%s, fk_category =%s WHERE id_number =%s AND owner_fk_nick =%s;"
        data = (title, summary, description, aim, now, category, id_number_challenge, FK_owner_nick,)
        cursor.execute(query, data)
        cnx.commit()
        row = cursor.rowcount
        cnx.close()
        # pendiente - remover estudiantes al desafio
        if row >= 1:
        	return True , 'The challenge has been edited successfully'
        else:
        	return True , 'No changes detected in the challenge'
    except Exception as e:
    	print e
    	return False, 'Something went wrong'


def edit_class_info_professor(id_class_, school_, identificator_, class_, year_, FK_owner_nick):
    try:
        c = Config()
        database_ = Database()
        config = database_.config
        cnx = mysql.connector.connect(**config)
        cursor = cnx.cursor()
        now = datetime.now()
        query = "UPDATE class_list SET school =%s, identificator =%s, class =%s, year =%s, d_last_modification =%s WHERE id_number =%s AND FK_owner_nick =%s;"
        data = (school_, identificator_, class_, year_, now, id_class_, FK_owner_nick,)
        cursor.execute(query, data)
        cnx.commit()
        row = cursor.rowcount
        cnx.close()
        if row >= 1:
            return True , 'The class information, has been edited successfully'
        else:
            return True , 'No changes detected in the class'
    except Exception as e:
        print e
        return False, 'Something went wrong'


def getclassbyid_(_FK_owner_nick, id_number_):
    try:
        database_ = Database()
        config = database_.config
        cnx = mysql.connector.connect(**config)
        cursor = cnx.cursor()
        query = "SELECT id_number, school, identificator, class as clss, year, d_creation, d_last_modification, FK_owner_nick FROM class_list WHERE FK_owner_nick = %s AND id_number = %s "
        data = (_FK_owner_nick,id_number_,)
        cursor.execute(query, data)
        for (id_number, school, identificator, clss, year, d_creation, d_last_modification, FK_owner_nick) in cursor:
            return True , [id_number, school, identificator, clss, year, d_creation, d_last_modification, FK_owner_nick]
        cursor.close()
        cnx.close()
        return False, []
    except Exception as e:
        print e
        return False, []


def user_exist_tocreate_user(nick_):
    try:
        database_ = Database()
        config = database_.config
        cnx = mysql.connector.connect(**config)
        cursor = cnx.cursor()
        query = "SELECT nick FROM users WHERE nick = %s "
        data = (nick_,)
        cursor.execute(query, data)
        for (nick) in cursor:
            return True
        cursor.close()
        cnx.close()
        return False
    except Exception as e:
        print e
        return True

def email_exist_tocreate_user(email_):
    try:
        database_ = Database()
        config = database_.config
        cnx = mysql.connector.connect(**config)
        cursor = cnx.cursor()
        query = "SELECT email FROM users WHERE email = %s "
        data = (email_,)
        cursor.execute(query, data)
        for (email) in cursor:
            return True
        cursor.close()
        cnx.close()
        return False
    except Exception as e:
        print e
        return True

def country_exist_tocreate_user(country_):
    try:
        database_ = Database()
        config = database_.config
        cnx = mysql.connector.connect(**config)
        cursor = cnx.cursor()
        query = "SELECT country FROM countries WHERE country = %s "
        data = (country_,)
        cursor.execute(query, data)
        for (country) in cursor:
            return True
        cursor.close()
        cnx.close()
        return False
    except Exception as e:
        print e
        return False

def challenge_last_activity_finalized(id_response):
    try:
        database_ = Database()
        config = database_.config
        cnx = mysql.connector.connect(**config)
        cursor = cnx.cursor()
        query = "SELECT FK_challenge_id_number, number_of_interaction FROM Challenge_last_activity WHERE id_number = %s AND finalized = %s "
        data = (id_response, '1',)
        cursor.execute(query, data)
        for (FK_challenge_id_number, number_of_interaction) in cursor:
            return True , FK_challenge_id_number
        cursor.close()
        cnx.close()
        return False , 0
    except Exception as e:
        print e
        return False, 0

def have_permisssions_student_resp(id_challenge_ , FK_nick_evaluator):
    try:
        database_ = Database()
        config = database_.config
        cnx = mysql.connector.connect(**config)
        cursor = cnx.cursor()
        query = "SELECT FK_all_challenges_id FROM evaluation_permissions WHERE FK_all_challenges_id = %s AND FK_nick_evaluator = %s "
        data = (id_challenge_ , FK_nick_evaluator,)
        cursor.execute(query, data)
        for (FK_all_challenges_id) in cursor:
            return True 
        cursor.close()
        cnx.close()
        return False 
    except Exception as e:
        print e
        return False

def it_challenge_has_been_eva(id_last_activity , FK_nick_evaluator):
    try:
        database_ = Database()
        config = database_.config
        cnx = mysql.connector.connect(**config)
        cursor = cnx.cursor()
        query = "SELECT marks, FK_nick_evaluator FROM evaluation_marks WHERE FK_challenge_last_activity_id = %s AND FK_nick_evaluator = %s "
        data = (id_last_activity , FK_nick_evaluator,)
        cursor.execute(query, data)
        for (marks, FK_nick_evaluator) in cursor:
            return True , marks
        cursor.close()
        cnx.close()
        return False , -1
    except Exception as e:
        print e
        return False, -1

def insert_new_mark_challenge_last_activity(id_last_activity, marks, nick_evaluator):
    try:
        c = Config()
        database_ = Database()
        config = database_.config
        cnx = mysql.connector.connect(**config)
        cursor = cnx.cursor()
        now = datetime.now()
        query = "INSERT INTO evaluation_marks(FK_challenge_last_activity_id,marks,FK_nick_evaluator) VALUES (%s, %s, %s);"
        data = (id_last_activity, marks, nick_evaluator,)
        cursor.execute(query, data)
        cnx.commit()
        cnx.close()
        return True
    except Exception as e:
        return False
        print e

def get_all_students_by_id_challenge(id_challenge):
    try:
        database_ = Database()
        config = database_.config
        cnx = mysql.connector.connect(**config)
        cursor = cnx.cursor()
        query = "SELECT classes.FK_student_nick FROM class_challenges as cc INNER JOIN classes WHERE classes.FK_class_id_number = cc.FK_class_id_number AND cc.FK_challenge_id_number = %s "
        data = (id_challenge,)
        cursor.execute(query, data)
        r = []
        for (FK_student_nick) in cursor:
            r.append(FK_student_nick)
        cursor.close()
        cnx.close()
        return r
    except Exception as e:
        print e
        return []

def get_all_nicks_tudents():
    try:
        database_ = Database()
        config = database_.config
        cnx = mysql.connector.connect(**config)
        cursor = cnx.cursor()
        query = "SELECT nick, email FROM users WHERE fk_roluser = %s "
        data = ('Student',)
        cursor.execute(query, data)
        r = []
        for (nick, email) in cursor:
            r.append([nick])
        cursor.close()
        cnx.close()
        return r
    except Exception as e:
        print e
        return []

def student_init_it(student_nick,id_challenge):
    try:
        database_ = Database()
        config = database_.config
        cnx = mysql.connector.connect(**config)
        cursor = cnx.cursor()
        query = "SELECT id_number, FK_student_nick, FK_challenge_id_number, last_response, number_of_interaction, init_date, end_date, finalized FROM Challenge_last_activity WHERE FK_student_nick = %s AND FK_challenge_id_number = %s "
        data = (student_nick,id_challenge,)
        cursor.execute(query, data)
        for (id_number, FK_student_nick, FK_challenge_id_number, last_response, number_of_interaction, init_date, end_date, finalized) in cursor:
            return True , [id_number, FK_student_nick, FK_challenge_id_number, last_response, number_of_interaction, init_date, end_date, finalized]
        cursor.close()
        cnx.close()
        return False, []
    except Exception as e:
        print e
        return False, []
