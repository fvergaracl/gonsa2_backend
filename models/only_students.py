import mysql.connector
from settings.config import Database, Config
from datetime import datetime

def get_all_challenges_student(student_nick):
	try:
		database_ = Database()
		config = database_.config
		cnx = mysql.connector.connect(**config)
		cursor = cnx.cursor()
		query = "SELECT all_c.id_number, all_c.title, all_c.photourl, all_c.summary, all_c.description, all_c.aim, all_c.created, all_c.last_edit, all_c.fk_category ,all_c.owner_fk_nick FROM all_challenges as all_c INNER JOIN class_challenges INNER JOIN class_list INNER JOIN classes WHERE class_challenges.FK_challenge_id_number = all_c.id_number AND class_list.id_number = class_challenges.FK_class_id_number AND classes.FK_class_id_number = class_list.id_number AND classes.FK_student_nick = %s;"
		data = (student_nick,)
		cursor.execute(query, data)
		r = []
		for (id_number, title, photourl, summary, description, aim, created, last_edit, fk_category, owner_fk_nick) in cursor:
			temp = [id_number, title, photourl, summary, description, aim, created, last_edit, fk_category, owner_fk_nick]
			r.append(temp)
		cursor.close()
		cnx.close()
		return r
	except Exception as e:
		print e

def get_status_challenge_by_id(nick_student,id_challenge_):
	try:
		database_ = Database()
		config = database_.config
		cnx = mysql.connector.connect(**config)
		cursor = cnx.cursor()
		query = "SELECT finalized, FK_student_nick FROM Challenge_last_activity WHERE FK_student_nick = %s AND FK_challenge_id_number = %s;"
		data = (nick_student,id_challenge_,)
		cursor.execute(query, data)
		r = []
		for (finalized, FK_student_nick) in cursor:
			if finalized == '1':
				return 'finalized'
			else:
				return 'init'
		cursor.close()
		cnx.close()
		return 'noinit'
	except Exception as e:
		print e

def get_all_challenges_student_finalized(student_nick):
	try:
		database_ = Database()
		config = database_.config
		cnx = mysql.connector.connect(**config)
		cursor = cnx.cursor()
		query = "SELECT all_c.id_number, all_c.title, all_c.photourl, all_c.summary, all_c.description, all_c.aim, all_c.created, all_c.last_edit, all_c.fk_category ,all_c.owner_fk_nick, cla.init_date, cla.end_date, cla.number_of_interaction, cla.last_response FROM all_challenges as all_c INNER JOIN class_challenges INNER JOIN Challenge_last_activity as cla INNER JOIN class_list INNER JOIN classes WHERE class_challenges.FK_challenge_id_number = all_c.id_number AND class_list.id_number = class_challenges.FK_class_id_number AND classes.FK_class_id_number = class_list.id_number AND classes.FK_student_nick = %s AND cla.FK_student_nick = classes.FK_student_nick and cla.FK_challenge_id_number = all_c.id_number and cla.finalized = '1' ORDER BY cla.number_of_interaction DESC; "
		data = (student_nick,)
		cursor.execute(query, data)
		r = []
		for (id_number, title, photourl, summary, description, aim, created, last_edit, fk_category, owner_fk_nick, init_date, end_date, number_of_interaction, last_response) in cursor:
			temp = [id_number, title, photourl, summary, description, aim, created, last_edit, fk_category, owner_fk_nick, init_date, end_date, number_of_interaction, last_response]
			r.append(temp)
		cursor.close()
		cnx.close()
		return r
	except Exception as e:
		print e
		print 'fina'

def get_all_challenges_student_no_finalized(student_nick):
	try:
		database_ = Database()
		config = database_.config
		cnx = mysql.connector.connect(**config)
		cursor = cnx.cursor()
		query = "SELECT all_c.id_number, all_c.title, all_c.photourl, all_c.summary, all_c.description, all_c.aim, all_c.created, all_c.last_edit, all_c.fk_category ,all_c.owner_fk_nick, cla.init_date, cla.number_of_interaction, cla.last_response FROM all_challenges as all_c INNER JOIN class_challenges INNER JOIN Challenge_last_activity as cla INNER JOIN class_list INNER JOIN classes WHERE class_challenges.FK_challenge_id_number = all_c.id_number AND class_list.id_number = class_challenges.FK_class_id_number AND classes.FK_class_id_number = class_list.id_number AND classes.FK_student_nick = %s AND cla.FK_student_nick = classes.FK_student_nick and cla.FK_challenge_id_number = all_c.id_number and cla.finalized = '0' ORDER BY cla.number_of_interaction DESC;"
		data = (student_nick,)
		cursor.execute(query, data)
		r = []
		for (id_number, title, photourl, summary, description, aim, created, last_edit, fk_category, owner_fk_nick, init_date, number_of_interaction, last_response) in cursor:
			temp = [id_number, title, photourl, summary, description, aim, created, last_edit, fk_category, owner_fk_nick, init_date, number_of_interaction, last_response]
			r.append(temp)
		cursor.close()
		cnx.close()
		return r
	except Exception as e:
		print e
		print ' no final'

def get_all_challenges_student_by_cat(student_nick, category_):
	try:
		database_ = Database()
		config = database_.config
		cnx = mysql.connector.connect(**config)
		cursor = cnx.cursor()
		query = "SELECT all_c.id_number, all_c.title, all_c.photourl, all_c.summary, all_c.description, all_c.aim, all_c.created, all_c.last_edit, all_c.owner_fk_nick FROM all_challenges as all_c INNER JOIN class_challenges INNER JOIN class_list INNER JOIN classes WHERE class_challenges.FK_challenge_id_number = all_c.id_number AND class_list.id_number = class_challenges.FK_class_id_number AND classes.FK_student_nick = %s AND all_c.fk_category = %s;"
		data = (student_nick,category_,)
		cursor.execute(query, data)
		r = []
		for (id_number, title, photourl, summary, description, aim, created, last_edit, owner_fk_nick) in cursor:
			temp = [id_number, title, photourl, summary, description, aim, created, last_edit, owner_fk_nick]
			r.append(temp)
		cursor.close()
		cnx.close()
		return r
	except Exception as e:
		print e

def add_text_library(FK_student_nick , FK_challenge_id_number , title_text, url_text , date_added, state):
    try:
        c = Config()
        database_ = Database()
        config = database_.config
        cnx = mysql.connector.connect(**config)
        cursor = cnx.cursor()
        query = "INSERT INTO Student_personal_library(FK_student_nick , FK_challenge_id_number , title_text, url_text, date_added, state) VALUES (%s, %s, %s, %s, %s, %s);"
        data = (FK_student_nick , FK_challenge_id_number , title_text, url_text , date_added, state,)
        cursor.execute(query, data)
        cnx.commit()
        cnx.close()
        return True 
    except Exception as e:
        print e
        return False

def check_is_in_text_library(FK_student_nick , FK_challenge_id_number , title_text, url_text):
	try:
		database_ = Database()
		config = database_.config
		cnx = mysql.connector.connect(**config)
		cursor = cnx.cursor()
		query = "SELECT state FROM Student_personal_library WHERE FK_student_nick=%s AND FK_challenge_id_number=%s AND title_text=%s AND url_text=%s;"
		data = (FK_student_nick , FK_challenge_id_number , title_text, url_text,)
		cursor.execute(query, data)
		for (state) in cursor:
			return True
		cursor.close()
		cnx.close()
		return False
	except Exception as e:
		print e
		return False

def update_text_library(FK_student_nick , FK_challenge_id_number , title_text, url_text, state):
    try:
        c = Config()
        database_ = Database()
        config = database_.config
        cnx = mysql.connector.connect(**config)
        cursor = cnx.cursor()
        now = datetime.now()
        query = "UPDATE Student_personal_library SET  state=%s WHERE FK_student_nick=%s AND FK_challenge_id_number=%s AND title_text=%s AND url_text=%s;" 
        data = (state,FK_student_nick , FK_challenge_id_number , title_text, url_text,)
        cursor.execute(query, data)
        cnx.commit()
        cnx.close()
        return True 
    except Exception as e:
        print e
        return False

def getallmylibrary_by_challenge(FK_student_nick, FK_challenge_id_number):
	try:
		database_ = Database()
		config = database_.config
		cnx = mysql.connector.connect(**config)
		cursor = cnx.cursor()
		query = "SELECT title_text, url_text, date_added, state FROM Student_personal_library WHERE FK_student_nick=%s AND FK_challenge_id_number=%s;"
		data = (FK_student_nick , FK_challenge_id_number,)
		cursor.execute(query, data)
		r = []
		for (title_text, url_text, date_added, state) in cursor:
			r.append([title_text, url_text, date_added, state])
		cursor.close()
		cnx.close()
		return r
	except Exception as e:
		print e
		return []

