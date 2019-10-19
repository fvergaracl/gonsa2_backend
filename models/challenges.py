#!/usr/bin/env python
# -*- coding: utf-8 -*-
import mysql.connector
from datetime import datetime
from settings.config import Database, Config


def itwasintializedbyanystudent(idchallenge):
    database_ = Database()
    config = database_.config
    cnx = mysql.connector.connect(**config)
    cursor = cnx.cursor()
    query = "SELECT FK_challenge_id_number FROM Challenge_last_activity WHERE FK_challenge_id_number = %s"
    data = (idchallenge,)
    cursor.execute(query,data)
    for (FK_challenge_id_number) in cursor:
        return True
    cursor.close()
    cnx.close()
    return False

def get_all_challenges_p(nick):
    database_ = Database()
    config = database_.config
    cnx = mysql.connector.connect(**config)
    cursor = cnx.cursor()
    query = "SELECT id_number,token_challenge,title,photourl,summary,description,aim,created,last_edit,fk_category FROM all_challenges WHERE owner_fk_nick = %s"
    data = (nick,)
    cursor.execute(query,data)
    r = []
    for (id_number,token_challenge,title,photourl,summary,description,aim,created,last_edit,fk_category) in cursor:
        r.append([id_number,token_challenge,title,photourl,summary,description,aim,created,last_edit,fk_category])
    cursor.close()
    cnx.close()
    return r

def get_all_challenges_in_class(idclass_):
    try:
        database_ = Database()
        config = database_.config
        cnx = mysql.connector.connect(**config)
        cursor = cnx.cursor()
        query = "SELECT ac.id_number, ac.title , ac.photourl, ac.summary, ac.description, ac.aim, ac.created, ac.last_edit, ac.owner_fk_nick, ac.fk_category FROM class_challenges as cc INNER JOIN all_challenges as ac WHERE cc.FK_class_id_number = %s AND cc.FK_challenge_id_number = ac.id_number order by ac.created DESC"
        data = (idclass_,)
        cursor.execute(query, data)
        r = []
        for (id_number, title, photourl, summary, description, aim, created, last_edit,  owner_fk_nick, fk_category) in cursor:
            temp = [id_number, title, photourl, summary, description, aim, created, last_edit, owner_fk_nick, fk_category]
            r.append(temp)
        cursor.close()
        cnx.close()
        return r
    except Exception as e:
        print e

def get_challenge_by_id_p(nick, id_number):
    database_ = Database()
    config = database_.config
    cnx = mysql.connector.connect(**config)
    cursor = cnx.cursor()
    query = "SELECT id_number,token_challenge,title,photourl,summary,description,aim,created,last_edit,fk_category FROM all_challenges WHERE owner_fk_nick = %s AND id_number=%s"
    data = (nick, id_number,)
    cursor.execute(query,data)
    r = []
    for (id_number,token_challenge,title,photourl,summary,description,aim,created,last_edit,fk_category) in cursor:
        r.append([id_number,token_challenge,title,photourl,summary,description,aim,created,last_edit,fk_category])
        return True , r
    cursor.close()
    cnx.close()
    return False, r

def get_all_challenges_p_by_cat(nick, category):
    database_ = Database()
    config = database_.config
    cnx = mysql.connector.connect(**config)
    cursor = cnx.cursor()
    query = "SELECT id_number,token_challenge,title,photourl,summary,description,aim,created,last_edit,fk_category FROM all_challenges WHERE owner_fk_nick = %s AND fk_category = %s"
    data = (nick,category,)
    cursor.execute(query,data)
    r = []
    for (id_number,token_challenge,title,photourl,summary,description,aim,created,last_edit,fk_category) in cursor:
        r.append([id_number,token_challenge,title,photourl,summary,description,aim,created,last_edit,fk_category])
    cursor.close()
    cnx.close()
    return r

def challenge_is_initialized(id_challenge_, nick_student_):
    database_ = Database()
    config = database_.config
    cnx = mysql.connector.connect(**config)
    cursor = cnx.cursor()
    query = "SELECT finalized FROM Challenge_last_activity WHERE FK_challenge_id_number = %s AND FK_student_nick  = %s"
    data = (id_challenge_, nick_student_,)
    cursor.execute(query,data)
    for (finalized) in cursor:
        if int(finalized[0]) == 0:
            add_interaction(id_challenge_, nick_student_)
        return True , finalized
        # if finalized -> 0: NO | 1: YES
    cursor.close()
    cnx.close()
    challenge_init(id_challenge_, nick_student_)
    return False, (u'0',)


def challenge_init(id_challenge_, nick_student_):
    try:
        c = Config()
        database_ = Database()
        config = database_.config
        cnx = mysql.connector.connect(**config)
        cursor = cnx.cursor()
        now = datetime.now()
        query = "INSERT INTO Challenge_last_activity(FK_student_nick ,FK_challenge_id_number ,last_response, number_of_interaction, init_date, finalized) VALUES (%s, %s, %s, %s, %s,%s);"
        data = (nick_student_,id_challenge_, '', 1, now, 0)
        cursor.execute(query, data)
        cnx.commit()
        cnx.close()
        return True 
    except Exception as e:
        print e
        return False

def Get_last_response_challenge(id_challenge_, nick_student_):
    database_ = Database()
    config = database_.config
    cnx = mysql.connector.connect(**config)
    cursor = cnx.cursor()
    query = "SELECT last_response FROM Challenge_last_activity WHERE FK_challenge_id_number = %s AND FK_student_nick  = %s"
    data = (id_challenge_, nick_student_,)
    cursor.execute(query,data)
    for (last_response) in cursor:
        return last_response
    cursor.close()
    cnx.close()
    return (u'-',)


def new_response(response_ ,id_challenge_, nick_student_):
    try:
        c = Config()
        database_ = Database()
        config = database_.config
        cnx = mysql.connector.connect(**config)
        cursor = cnx.cursor()
        now = datetime.now()
        query = "UPDATE Challenge_last_activity SET number_of_interaction = number_of_interaction + 1, last_response=%s WHERE  FK_challenge_id_number =%s AND FK_student_nick =%s AND finalized = 0"
        data = (response_,id_challenge_, nick_student_,)
        cursor.execute(query, data)
        cnx.commit()
        cnx.close()
        return True 
    except Exception as e:
        print e
        return False

def check_challenge_is_finished(id_challenge_, nick_student_):
    database_ = Database()
    config = database_.config
    cnx = mysql.connector.connect(**config)
    cursor = cnx.cursor()
    query = "SELECT finalized, end_date FROM Challenge_last_activity WHERE FK_challenge_id_number = %s AND FK_student_nick  = %s"
    data = (id_challenge_, nick_student_,)
    cursor.execute(query,data)
    for (finalized, end_date) in cursor:
        if int(finalized[0]) == 1:
            return True , end_date
        return False , '-'
        # if finalized -> 0: NO | 1: YES
    cursor.close()
    cnx.close()
    return False , '-'


def finish_challenge(id_challenge_, nick_student_, last_response, date_):
    try:
        c = Config()
        database_ = Database()
        config = database_.config
        cnx = mysql.connector.connect(**config)
        cursor = cnx.cursor()
        now = datetime.now()
        query = "UPDATE Challenge_last_activity SET last_response =%s, finalized = %s, end_date=%s WHERE FK_challenge_id_number =%s AND FK_student_nick =%s;"
        data = (last_response, '1', date_, id_challenge_, nick_student_,)
        cursor.execute(query, data)
        cnx.commit()
        row = cursor.rowcount
        cnx.close()
        if row >= 1:
            add_interaction(id_challenge_, nick_student_)
            return True , 'The challenge has been finished'
        else:
            return True , 'No changes detected in the challenge'
    except Exception as e:
        print e
        return False, 'Something went wrong'

def add_interaction(id_challenge_, nick_student_):
    try:
        c = Config()
        database_ = Database()
        config = database_.config
        cnx = mysql.connector.connect(**config)
        cursor = cnx.cursor()
        now = datetime.now()
        query = "UPDATE Challenge_last_activity SET  number_of_interaction = number_of_interaction + 1 WHERE FK_student_nick = %s AND FK_challenge_id_number=%s" 
        data = (nick_student_,id_challenge_,)
        cursor.execute(query, data)
        cnx.commit()
        cnx.close()
        return True 
    except Exception as e:
        print e
        return False


def log_student_queries(nick_student_, id_challenge_ , query_, now_):
    try:
        c = Config()
        database_ = Database()
        config = database_.config
        cnx = mysql.connector.connect(**config)
        cursor = cnx.cursor()
        query = "INSERT INTO Students_query(FK_student_nick ,FK_challenge_id_number ,query, date_executed ) VALUES (%s, %s, %s, %s);"
        data = (nick_student_, id_challenge_, query_, now_,)
        cursor.execute(query, data)
        cnx.commit()
        cnx.close()
        return True 
    except Exception as e:
        print e
        return False

def get_id_number_query(nick_student_, id_challenge_ , query_, now):
    database_ = Database()
    config = database_.config
    cnx = mysql.connector.connect(**config)
    cursor = cnx.cursor()
    query = "SELECT id_number FROM Students_query WHERE FK_student_nick=%s AND FK_challenge_id_number =%s AND query =%s AND date_executed =%s;"
    data = (nick_student_, id_challenge_ , query_, now,)
    cursor.execute(query,data)
    for (id_number) in cursor:
        return id_number
    cursor.close()
    cnx.close()
    return [0]

def insert_result_query(FK_id_number_student_query, position_, lang_, title_, snippet_, url_):
    try:
        c = Config()
        database_ = Database()
        config = database_.config
        cnx = mysql.connector.connect(**config)
        cursor = cnx.cursor()
        query = "INSERT INTO Students_queries_results(FK_student_query_id_number ,position , lang, title, snippet, url   ) VALUES (%s, %s, %s, %s, %s, %s);"
        data = (FK_id_number_student_query, position_, lang_, title_, snippet_, url_,)
        cursor.execute(query, data)
        cnx.commit()
        cnx.close()
        return True 
    except Exception as e:
        print e
        return False

def insert_related_search_query(FK_id_number_student_query, position_, query_text):
    try:
        c = Config()
        database_ = Database()
        config = database_.config
        cnx = mysql.connector.connect(**config)
        cursor = cnx.cursor()
        query = "INSERT INTO Students_related_search(FK_student_query_id_number ,position , textquery  ) VALUES (%s, %s, %s);"
        data = (FK_id_number_student_query, position_, query_text,)
        cursor.execute(query, data)
        cnx.commit()
        cnx.close()
        return True 
    except Exception as e:
        print e
        return False