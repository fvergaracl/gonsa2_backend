#!/usr/bin/env python
# -*- coding: utf-8 -*-

from settings.config import Config, Database

from functions.Verifiers import verify_new_pass, verify_pass_conditions, validemail
from functions.general_functions import *
from functions.email_sender import *

from models.users import *
from models.only_administrador import *
from models.only_professor import *
from models.only_students import *
from models.categories import *
from models.challenges import *
from models.records import *

from flask import Flask, jsonify, request
import jwt
import datetime
import ast
import json
from functools import wraps
from flask_cors import CORS

UPLOAD_FOLDER = '/static/uploads'
ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'])
app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 1600 * 1024 * 1024

CORS(app)
c = Config()


def get_info_token():
    tokenTEMP = request.headers['Authorization']
    token = tokenTEMP.split(" ")
    data = jwt.decode(token[1], c.get_jwt_key())
    return data

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        try:
            tokenTEMP = request.headers['Authorization']
            token = tokenTEMP.split(" ")
            if not tokenTEMP:
                # token not found
                return jsonify({'message': 'Token not found', 'code': 404})
            try:
                # token valid
                data = jwt.decode(token[1], c.get_jwt_key())
            except Exception as e:
                # token not valid
                return jsonify({'message': 'Token not valid', 'code': 403})
            return f(*args, **kwargs)
        except KeyError:
            # token not found
            return jsonify({'message': 'Token not found', 'code': 404})
    return decorated

############################## TEST URIS #############################

@app.route('/', methods=['GET'])
def testing_root():
    return jsonify({'message': "It's works", 'code': 200})

@app.route('/islogged', methods=['GET'])
@token_required
def testing_logged():
    """
    Returns the data contained in the token, and thus validates that the token is valid
    """
    data = get_info_token()
    return jsonify({'message': "You're logged",'data':data , 'code': 200})

############################## END TEST URIS #############################


############################## GET USER INFORMATION #############################

@app.route('/userinformation', methods=['GET'])
@token_required
def userinformation():
    """
    Returns the data contained in the token, and thus validates that the token is valid
    """
    tokenTEMP = request.headers['Authorization']
    token = tokenTEMP.split(" ")
    data = jwt.decode(token[1], c.get_jwt_key())
    return jsonify({'User': data['User'], 'Rol':data['Rol'], 'code': 200})
############################## END USER INFORMATION #############################

############################## USER URIS #############################

@app.route('/login', methods=['POST'])
def login():
    """
    Receive a user (email or user) and a password
    Return: message with token (Only if the information entered is correct)
    """
    name_ = ''
    token = ''
    try:
        code = 400
        user_ = request.get_json()['user'].encode('utf-8').strip()
        pass_ = request.get_json()['pass'].encode('utf-8').strip()
        if user_ == '' or user_.strip() == '':
            message = 'You must enter an email or your user to enter the system'
            raise MyException("error")
        if pass_ == '' or pass_.strip() == '':
            message = 'You must enter your password to enter the system'
            raise MyException("error")
        all_ok = login_user(user_, pass_)
        if all_ok:
            code = 200
            message = 'Welcome'
            rol_ = get_rol_of_user(user_)
            name_ = user_
            insert_general_record('login', {}, name_)
            token = jwt.encode(
                {'User': name_, 'Rol': rol_, 'exp': datetime.datetime.utcnow() + c.get_jwt_time()},
                c.get_jwt_key())
        else:
            code = 400
            message = 'User or password, not valid'
            user_ = ''
    except MyException as e:
        return jsonify({'code': code,
                    'message': message,
                    'name': name_,
                    'token': token})
    except Exception as e:
        code = 500
        message = 'Something went wrong'
    return jsonify({'code': code,
                    'message': message,
                    'name': name_,
                    'token': token})

@app.route('/changepass', methods=['POST'])
@token_required
def changepass():
    """
    Receive the old password and twice new password
    Return: message with the result of this operation (Only if the information entered is correct)
    """
    user_ = get_info_token()['User']
    code = 400
    try:
        old_pass = request.get_json()['oldpass'].encode('utf-8').strip()
        new_pass1 = request.get_json()['newpass1'].encode('utf-8').strip()
        new_pass2 = request.get_json()['newpass2'].encode('utf-8').strip()
        if old_pass == '' or old_pass.strip() == '':
            message = 'You must enter your old password'
            raise MyException("error")
        if new_pass1 == '' or new_pass1.strip() == '' or new_pass2 == '' or new_pass2.strip() == '':
            message = 'You must enter your new password twice'
            raise MyException("error")
        all_ok, message = verify_new_pass(user_, old_pass, new_pass1,new_pass2)
        if all_ok:
            code = 200
            if updatepass(user_, new_pass1):
                ip = request.environ.get('HTTP_X_REAL_IP', request.remote_addr)
                #Platform name , username, ip, datetime, email contact
                now = datetime.datetime.now()
                email_ = get_email(user_)
                if email_ != '':
                    parameters = [c.get_platform_name(),user_, ip, now.strftime("%Y-%m-%d %H:%M"), c.get_email_contact(), c.get_email_contact()]
                    response_bool , response = email_to_send(parameters,'pass_changed','Your password has been changed', email_)
                    message = 'The password was successfully updated, and email was sent. (' + email_ + ')'
                else:
                    message = 'The password was successfully updated'
                insert_general_record('changepass', {
                    "user_": "updated"
                    }, user_)
            else:
                message = 'Could not update the password'
    except Exception as e:
        print e
        code = 500
        message = 'Something went wrong'

    
    return jsonify({'code': code,
                    'message': message})

@app.route('/recoverpassbyemail', methods=['POST'])
def recoverpassbyemail():
    """
    Receive an user or email to define a new password
    Return: send an email with link to define a new password
    """
    code = 400
    try:
        email = request.get_json()['user_email'].encode('utf-8').strip()
        if email == '' or email.strip() == '' or email == None:
            message = 'You must enter an email or your user to recover your password.'
            raise MyException("error")
        resp_bool , user_email_ = user_email_exist(email)
        if not resp_bool:
            message ='The user or email entered, is not linked to any account.'
        else:
            have_valid_token, token = get_recovery_token(user_email_[0])
            if have_valid_token:
                message = 'You already have a request registered in our system, remember that this request is valid only for 4 hours. Please check your email'
            else:
                code = 200
                response, token = insert_token(user_email_[0])
                ip = request.environ.get('HTTP_X_REAL_IP', request.remote_addr)
                now = datetime.datetime.now()
                parameters = [c.get_platform_name(),user_email_[0], c.get_api_host()+'/recovery/'+ token, ip, now ] 
                response_bool , response = email_to_send(parameters,'password_recovery','Reset your password', user_email_[1])
                if response_bool:
                    message = 'It sent an email for restoring your password'
                else:
                    message = 'An error was generated in the server, the email could not be sent correctly. Please communicate with the administrator'
                username_ = get_nick_by_email(email.strip())
                insert_general_record('recoverpassbyemail', {
                    "message": message}, username_)
    except MyException as e:
        return jsonify({'code': code,
                    'message': message})
    except Exception as e:
        print e
        code = 500
        message = 'Something went wrong'
    
    return jsonify({'code': code,
                    'message': message})


@app.route('/newpassword/<token>' , methods=['POST'])
def newpassword_bytoken(token):
    """
    Receive a token by uri , with this method the user can change the password, however the user must request an email using the 'recoverpassbyemail' method
    Return: a message if the operation is successful or not
    """
    try:
        code = 400
        email = request.get_json()['email'].encode('utf-8').strip()
        pass1 = request.get_json()['pass1'].encode('utf-8').strip()
        pass2 = request.get_json()['pass2'].encode('utf-8').strip()
        if not (pass1 == pass2):
            message = 'Passwords entered do not match'
        elif email == '' or email.strip() == '' or email == None:
            message = 'You must enter an email.'
            raise MyException("error")
        elif pass1 == '' or pass1.strip() == '' or pass1 == None:
            message = 'You must enter a password.'
            raise MyException("error")
        else:
            all_ok, msg = verify_pass_conditions(pass1)
        if all_ok:
            resp_bool , user_email_ = user_email_exist(email)
            if resp_bool:
                token_bool, token = get_recovery_token(user_email_[0])
                if token_bool:
                    updatestatus_recovery_token(user_email_[0],token)
                    updatepass(user_email_[0],pass1)
                    ip = request.environ.get('HTTP_X_REAL_IP', request.remote_addr)
                    parameters = [c.get_platform_name(),user_email_[0], ip, now.strftime("%Y-%m-%d %H:%M"), c.get_email_contact(), c.get_email_contact()]
                    response_bool , response = email_to_send(parameters,'pass_changed','Your password has been changed', email_)
                    code = 200
                    message = 'The password was successfully updated'
                else:
                    code = 400
                    message = 'The provided email is not linked with the token'
                username_ = get_nick_by_email(email.strip())
                insert_general_record('newpassword/[token]',
                    {"message": message,
                    "token": token,
                    "code": code}, username_) 
            else:
                code = 400
                message = 'The provided email is not linked with the token'
            
        else:
            message = msg
    except MyException as e:
        return jsonify({'code': code,
                    'message': message})
    except Exception as e:
        print e
        code = 500
        message = 'Something went wrong'
    return jsonify({'code': code,
                    'message': message})
    
############################## END USER URIS #############################

############################## COMMON URIS #############################




@app.route('/getallcategories', methods=['GET'])
@token_required
def getallcategories_():
    """
    Returns all defined categories
    """
    data = get_info_token()
    user_ = data['User']
    rol_ = data['Rol']
    categories =[]
    code = 200
    if rol_ == 'Professor':
        try:
            categories = get_all_categories_profesor()
            code = 200
        except Exception as e:
            print e
            code = 500
    elif rol_ == 'Student':
        try:
            categories = get_all_categories_student(user_)
            code = 200
        except Exception as e:
            print e
            code = 500
    insert_general_record('getallcategories', 
        {'categories': categories,
        'code': code}
        ,user_)
    return jsonify({'categories': categories,  'code': code})

@app.route('/getclassbyid/<numid>', methods=['GET'])
@token_required
def getclasesbyid_(numid):
    """
    Returns all defined clases by id [number]
    """
    data = get_info_token()
    user_ = data['User']
    rol_ = data['Rol']
    data_response = ''
    if rol_ == 'Professor':
        try:
            bool_, data_response = getclassbyid_(data['User'],numid)
            if bool_:
                code = 200
            else:
                data_response = 'Forbidden'
                code = 403
        except Exception as e:
            print e
            data_response = 'Internal Error'
            code = 500
    elif rol_ == 'Student':
        try:
            bool_, data_response = getclassbyid_(data['User'],numid)
            if bool_:
                code = 200
            else:
                data_response = 'Forbidden'
                code = 403
        except Exception as e:
            print e
            code = 500
    insert_general_record('getclassbyid/[id]', 
        {'data': data_response,
        'code': code}
        ,user_)
    return jsonify({'data': data_response,  'code': code})

@app.route('/getallchallengesinclass/<idclass>', methods=['GET'])
@token_required
def getallchallengesinclass_(idclass):
    data = get_info_token()
    user_ = data['User']
    rol_ = data['Rol']
    data_response = []
    code = 400
    if rol_ == 'Professor':
        data_response = get_all_challenges_in_class(idclass)
    elif rol_ == 'Student':
        challenges_ = get_all_challenges_in_class(idclass)
        finalized_ = []
        initialized_ = []
        no_init = []
        for x in challenges_:
            response = get_status_challenge_by_id(user_, x[0] )
            if response == 'finalized':
                finalized_.append([x])
            elif response == 'init':
                initialized_.append([x])
            else:
                no_init.append([x])
        code = 200
        insert_general_record('getallchallengesinclass/[id]', 
        {'Finalized': len(finalized_), 
        'initialized': len(initialized_), 
        'no_init': len(no_init),  
        'code': code}
        ,user_)
        return jsonify({'Finalized': finalized_, 'initialized': initialized_, 'no_init': no_init,  'code': code})
    else:
        data_response = 'Forbidden'
        code = 503
    insert_general_record('getallchallengesinclass/[id]', 
        {'challenges': len(data_response),  'code': code}
        ,user_)
    return jsonify({'challenges': data_response,  'code': code})


@app.route('/getchallegebyid/<numid>', methods=['GET'])
@token_required
def getchallegebyid_(numid):
    """
    Returns all defined categories
    """
    data = get_info_token()
    user_ = data['User']
    rol_ = data['Rol']
    data_response = ''
    if rol_ == 'Professor':
        try:
            bool_, data_response = get_challenge_by_id_p(data['User'],numid)
            if bool_:
                code = 200
            else:
                data_response = 'Forbidden'
                code = 403
        except Exception as e:
            print e
            data_response = 'Internal Error'
            code = 500
    elif rol_ == 'Student':
        try:
            bool_, data_response = get_challenge_by_id_p(data['User'],numid)
            if bool_:
                code = 200
                response = get_status_challenge_by_id(user_, numid )
                return jsonify({'data': data_response, 'status': response, 'code': code})
            else:
                data_response = 'Forbidden'
                code = 403
        except Exception as e:
            print e
            code = 500
    insert_general_record('getchallegebyid/[id]', 
        {'data': data_response,
        'code': code}
        ,user_)
    return jsonify({'data': data_response,  'code': code})

############################## END COMMON URIS #############################

############################## CHALLENGES URIS #############################
@app.route('/getallchallenges_status', methods=['GET'])
@token_required
def getallchallenges_status_():
    data = get_info_token()
    user_ = data['User']
    rol_ = data['Rol']
    message = 'You are not allowed to access this page'
    code = 403
    finalized_challenge = []
    no_finalized_challenge = []
    no_init_challenge = []
    discard_id = []
    if rol_ == 'Student':
        all_challenges = get_all_challenges_student(user_)
        finalized_challenge = get_all_challenges_student_finalized(user_)
        for x in finalized_challenge:
            discard_id.append(x[0])
        no_finalized_challenge = get_all_challenges_student_no_finalized(user_)
        for x in no_finalized_challenge:
            discard_id.append(x[0])
        for x in all_challenges:
            if x[0] in discard_id:
                pass
            else:
                no_init_challenge.append(x)
        message = 'ok'
        code = 200
    insert_general_record('getallchallenges_status', 
        {"code": code}
        ,user_)
    return jsonify({'message': message,
        'finalized_challenge': finalized_challenge,
        'no_finalized_challenge': no_finalized_challenge,
        'no_init_challenge': no_init_challenge,
        'code': code})

@app.route('/getallchallenges', methods=['GET'])
@token_required
def getallchallenges_():
    """
    Returns all challenges of professor
    """
    data = get_info_token()
    user_ = data['User']
    rol_ = data['Rol']
    challenges =[]
    code = 500
    if rol_ == 'Professor':
        try:
            challenges = get_all_challenges_p(user_)
            code = 200
        except Exception as e:
            print e
            pass
    elif rol_ == 'Administrador':
        """
        Administrador - pendiente
        """
        try:
            challenges = get_all_challenges_p(user_)
            code = 200
        except Exception as e:
            print e
            pass
    elif rol_ == 'Student':
        challenges = get_all_challenges_student(user_)
        code = 200
    else:
        challenges = []
        code = 500
    insert_general_record('getallchallenges', 
        {"code": code}
        ,user_)
    return jsonify({'challenges': challenges,  'code': code})

@app.route('/getallchallenges/<category_>', methods=['GET'])
@token_required
def getallchallenges_by_cat(category_):
    """
    Returns all challenges of professor
    """
    data = get_info_token()
    user_ = data['User']
    rol_ = data['Rol']
    challenges =[]
    code = 500
    if rol_ == 'Professor':
        try:
            challenges = get_all_challenges_p_by_cat(user_,category_)
            code = 200
        except Exception as e:
            print e
            pass
    elif rol_ == 'Administrador':
        """
        Administrador - pendiente
        """
        try:
            challenges = get_all_challenges_p_by_cat(user_,category_)
            code = 200
        except Exception as e:
            print e
            pass
    else:
        challenges = get_all_challenges_student_by_cat(user_,category_)
        code = 200
    insert_general_record('getallchallenges/[category]', 
        {"code": code, "category": category_}
        ,user_)
    return jsonify({'challenges': challenges,  'code': code})

############################## END CHALLENGES URIS #############################

############################## ONLY PROFESSOR #############################
@app.route('/getallnickstudents', methods=['GET'])
@token_required
def getallnickstudents_():

    code = 200
    data = get_info_token()
    message = 'You are not allowed to access this page'
    code = 403
    if (data['Rol'] == 'Professor'):
        data_ = get_all_nicks_tudents()
        code = 200
        insert_general_record('getallnickstudents', 
        {"code": code}
        ,data['User'])
        return jsonify({'data': data_, 'code': code})
    else:
        insert_general_record('getallnickstudents', 
        {"code": code}
        ,data['User'])
        return jsonify({'message': message, 'code': code})

@app.route('/getallcountries', methods=['GET'])
@token_required
def get_all_countries_():
    data_ = get_all_countries()
    code = 200
    data = get_info_token()
    insert_general_record('getallcountries', 
        {"code": code,
        "contries": len(data_)}
        ,data['User'])
    return jsonify({'data': data_, 'code': code})

@app.route('/getstudentinclass/<id_class>', methods=['GET'])
@token_required
def getstudentinclass_(id_class):
    data = get_info_token()
    message = 'You are not allowed to access this page'
    code = 403
    users = []
    if (data['Rol'] == 'Professor'):
        users = get_all_students_in_class_by_id(id_class,data['User'])
        message = 'ok'
        code = 200
    insert_general_record('getstudentinclass/[id]', 
        {"code": code,
        "users": len(users)}
        ,data['User'])
    return jsonify({'message': message, 'users': users,'code': code})

@app.route('/getstatusresponses/by_challenge/<id_challenge>', methods=['GET'])
@token_required
def getstatusresponses_by_cha_(id_challenge):
    data = get_info_token()
    message = 'You are not allowed to access this page'
    code = 403
    users = []
    rol_ = data['Rol']
    user_ = data['User']
    waiting_evaluation_challenge = []
    noinit_challenge = []
    in_challenges = []
    evaluated_challenge = []
    if (rol_ == 'Professor'):
        students = get_all_students_by_id_challenge(id_challenge)
        # without_init
        for x in students:
            print x[0]
            bool_, info = student_init_it(x[0],id_challenge)
            if not bool_:
                noinit_challenge.append(x[0])
            else:
                if info[7] == "0":
                    in_challenges.append(info)
                else:
                    #
                    id_last_challenge_activity = info[0]
                    bool_, marks_ = it_challenge_has_been_eva(info[0], user_)
                    if bool_:
                        evaluated_challenge.append([info[0],info[1],info[2],info[3],info[4],info[5],info[6],info[7], marks_])
                    else:
                        waiting_evaluation_challenge.append(info)
        message = 'ok'
        code = 200
    insert_general_record('getstatusresponses/by_challenge/[id]', 
        {'message': message,
        'waiting_marks': len(waiting_evaluation_challenge),
        'without_init': len(noinit_challenge),
        'users_in_challenge': len(in_challenges),
        'users_evaluated': len(evaluated_challenge),
        'code': code}
        ,user_)
    return jsonify({
        'message': message,
        'waiting_marks': waiting_evaluation_challenge,
        'without_init': noinit_challenge,
        'users_in_challenge': in_challenges,
        'users_evaluated': evaluated_challenge,
        'code': code})

@app.route('/evaluate_student', methods=['POST'])
@token_required
def evaluate_student_():
    try:
        data = get_info_token()
        message = 'You are not allowed to access this page'
        code = 403 
        id_response_ = request.get_json()['idresponse'].encode('utf-8').strip()
        marks_ = request.get_json()['marks'].encode('utf-8').strip()
        evaluator_ = data['User']
        if (data['Rol'] == 'Professor'):
            bool_finalized, challenge_id = challenge_last_activity_finalized(id_response_)
            if not bool_finalized:
                insert_general_record('evaluate_student', 
                {"id_response": id_response_,
                "marks": marks_,
                "message": "The student's challenge has not yet been finalized", "code": 400}
                ,evaluator_)
                return jsonify({"message": "The student's challenge has not yet been finalized", "code": 400})
            bool_permissions = have_permisssions_student_resp(challenge_id, evaluator_)
            if not bool_permissions:
                insert_general_record('evaluate_student', 
                {"id_response": id_response_,
                "marks": marks_,
                "message": "You don't have the permission enough to evaluate the student in this challenge", "code": 400}
                ,evaluator_)
                return jsonify({"message": "You don't have the permission enough to evaluate the student in this challenge", "code": 400})
            bool_has_been_evaluate, marks = it_challenge_has_been_eva(id_response_, evaluator_)
            if bool_has_been_evaluate:
                insert_general_record('evaluate_student', 
                {"id_response": id_response_,
                "marks": marks_,
                "message": "You have already evaluated this student in this challenge", "marks": marks , "code": 400}
                ,evaluator_)
                return jsonify({"message": "You have already evaluated this student in this challenge", "marks": marks , "code": 400})
            else:
                bool_all_ok = insert_new_mark_challenge_last_activity(id_response_, marks_, evaluator_)
                if bool_all_ok:
                    message = 'Marks entered into the system'
                    code = 200
                else:
                    message = 'Something went wrong'
                    code = 400
    except Exception as e:
        print e
        code = 500
        message = 'Internal Error'
    insert_general_record('evaluate_student', 
                {'message': message, 'code': code}
                ,evaluator_)
    return jsonify({'message': message, 'code': code})


@app.route('/createstudents', methods=['POST'])
@token_required
def createstudents_():
    try:
        data = get_info_token()
        message = 'You are not allowed to access this page'
        code = 403
        inals_students = []
        filter_invalid_email = []
        filter_used_email = []
        filter_used_user = []
        finals_students = []
        filter_invalid_email = []
        filter_invalid_country = []
        filter_used_email = []
        filter_used_user = []
        filter_error_info = []
        if (data['Rol'] == 'Professor'):
            students = request.get_json()['newstudents']
            if isinstance(students, list):
                code = 400
                message = 'Bad request'
                for x in range(0,len(students)):
                    nick_ = str(students[x]['nick'].encode('utf-8').strip()).lower()
                    email_ = str(students[x]['email'].encode('utf-8').strip()).lower()
                    sex_ = str(students[x]['sex'].encode('utf-8').strip()).lower()
                    school =  str(students[x]['school']).lower()
                    class_ =  str(students[x]['class']).lower()
                    birth_year_ =  str(students[x]['birth_year']).lower()
                    birth_month_ =  str(students[x]['birth_month']).lower()
                    birth_date_ =  str(students[x]['birth_date']).lower()
                    country_ =  str(students[x]['country'].encode('utf-8').strip()).lower()
                    if not validemail(email_):
                        filter_invalid_email.append(email_)
                    elif  user_exist_tocreate_user(nick_):
                        filter_used_user.append(nick_)
                    elif  email_exist_tocreate_user(email_):
                        filter_used_email.append(email_)
                    elif not country_exist_tocreate_user(country_):
                        filter_invalid_country.append(country_)
                    else:
                        bool_ , pass_ =create_user(nick_, email_, sex_, school, class_, birth_year_, birth_month_, birth_date_, country_)
                        if bool_: 
                            parameters = [c.get_platform_name(), c.get_platform_name(), c.get_web_url(), nick_ , pass_]
                            email_to_send(parameters,'new_account','Your new account is ready to use', email_)
                            finals_students.append([nick_,email_])
                            code = 200
                            message = 'ok'
                        else:
                            filter_error_info.append([nick_,email_])
                                        
            else:
                message = 'The data entered does not have the proper format'
                code = 400
    except Exception as e:
        code = 500
        message = 'Internal Error'
        print e
    insert_general_record('createstudents', 
        {'studentscreated': len(finals_students),
        'info_error': len(filter_error_info),
        'invalid_emails': len(filter_invalid_email),
        'invalid_country': len(filter_invalid_country),
        'used_emails': len(filter_used_email),
        'used_usernames': len(filter_used_user),
        'message': message,
        'code': code}
        ,data['User'])
    return jsonify(
            {'studentscreated': finals_students,
            'info_error':filter_error_info,
            'invalid_emails': filter_invalid_email,
            'invalid_country': filter_invalid_country,
            'used_emails': filter_used_email,
            'used_usernames': filter_used_user,
            'message': message,
            'code': code})
    


@app.route('/challenge/new', methods=['POST'])
@token_required
def new_challenge_professor():
    data = get_info_token()
    message = 'You are not allowed to access this page'
    code = 403
    title_ = ''
    summary_ = ''
    description_ = ''
    aims_ = ''
    photo_ = ''
    category_ = ''
    user_ = ''
    id_challenge_ = -1
    if (data['Rol'] == 'Professor'):
        try:
            title_ = str(request.get_json()['title'].encode('utf-8').strip())
            summary_ = str(request.get_json()['summary'].encode('utf-8').strip())
            description_ = str(request.get_json()['description'].encode('utf-8').strip())
            aims_ = str(request.get_json()['aims'].encode('utf-8').strip())
            exist_photo = False
            try:
                exist_photo = True
                photo_ = str(request.get_json()['photo'].encode('utf-8').strip())
            except Exception as e:
                print e
                photo_ = "data:image/png;base64,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"
            
            category_ = str(request.get_json()['category'].encode('utf-8').strip())
            user_ = data['User']
            _photo_ = convert_and_save_image(photo_, str(user_),'desafio')
            aims_ = eval(aims_)
            _aims = ''
            length_aims = len(aims_)
            c = 0
            for x in aims_:
                if c + 1 == length_aims:
                    _aims = _aims + str(x.encode('utf-8').strip()).split("'value': u'")[1].split("'}")[0]
                else:
                    _aims = _aims + str(x.encode('utf-8').strip()).split("'value': u'")[1].split("'}")[0] + ','
                c = c + 1
            code = 200
            bool_, _token_ = new_challenge_p(title_, summary_, description_, _aims, _photo_, user_ ,category_)
            if bool_:
                id_challenge_ =get_id_challenge_by_token(_token_)
                new_permission(id_challenge_, user_)
                message = 'The class was correctly entered'
            else:
                message = 'Something went wrong'
                code = 400
        except Exception as e:
            message = 'Internal error'
            code = 500
            if 'title' in e:
                message = 'You have not entered a title'
                code = 400
            elif 'summary' in e:
                message = 'You have not entered a summary'
                code = 400
            elif 'description' in e:
                message = 'You have not entered a description'
                code = 400
            elif 'aims' in e:
                message = 'You have not entered a aims'
                code = 400
            elif 'category' in e:
                message = 'You have not entered a category'
                code = 400
            print e
    insert_general_record('challenge/new', 
        {'data': message, 'code': code, 'idchallenge': id_challenge_}
        ,data['User'])      
    return jsonify({'data': message, 'code': code})

@app.route('/class/new', methods=['POST'])
@token_required
def new_class_professor():
    """
    Receive [school identificador class year]
    Return: message with token (Only if the information entered is correct)
    """
    data = get_info_token()
    message = 'You are not allowed to access this page'
    code = 403
    if (data['Rol'] == 'Professor'):
        try:
            code = 400
            school_ = str(request.get_json()['school'].encode('utf-8').strip())
            identificator_ = str(request.get_json()['identificator'].encode('utf-8').strip())
            class_ = str(request.get_json()['class'].encode('utf-8').strip())
            year_ = str(request.get_json()['year'].encode('utf-8').strip())
            FK_owner_nick = str(data['User'].encode('utf-8').strip())
            result_bool, result_text = new_class(school_, identificator_, class_, year_, FK_owner_nick)
            message = result_text
            if result_bool:
                code = 200
            else:
                code = 400
        except:
            message = 'Internal error'
            code = 500
    insert_general_record('class/new', 
        {'data': message, 'code': code}
        ,data['User'])      
    return jsonify({'data': message, 'code': code})

@app.route('/get_all_classes', methods=['GET'])
@token_required
def get_all_classes_p():
    """
    Method to get all data about the Professor's classes
    Return: [id,school,identificator,class, year, status]
    """
    data = get_info_token()
    message = 'You are not allowed to access this page'
    code = 403
    classes = []
    if (data['Rol'] == 'Professor'):
        classes = get_all_classes_professor(str(data['User'].encode('utf-8').strip()))
        message = 'Ok'
        code = 200
    insert_general_record('get_all_classes', 
        {'message': message, 'classes': len(classes),'code': code}
        ,data['User'])
    return jsonify({'message': message, 'classes': classes,'code': code})

@app.route('/class/add_student', methods=['POST'])
@token_required
def add_to_class_p():
    """
    Receive a user (student) to add a specific class
    Return: message with token (Only if the information entered is correct)
    """
    
    data = get_info_token()
    message = 'You are not allowed to access this page'
    code = 403
    student = "-"
    class_ = "-"
    if (data['Rol'] == 'Professor'):
        try:
            student = str(request.get_json()['student'].encode('utf-8').strip())
            class_ = str(request.get_json()['class'].encode('utf-8').strip())
            code = 400
            ismyclass_bool = it_s_my_class_professor(data['User'],class_)
            if ismyclass_bool:
                resp_bool, resp_text = add_student_to_class_professor(class_,student)
                message = resp_text
                if resp_bool:
                    code = 200
                else:
                    code = 400
            else:
                message = 'You are not allowed to do something in this class'
        except Exception as e:
            print e
            message = 'Internal error'
            code = 500
    insert_general_record('class/add_student', 
        {'data': message, 'code': code, 'student':student, 'class': class_}
        ,data['User'])
    return jsonify({'data': message, 'code': code})

@app.route('/class/remove_student', methods=['POST'])
@token_required
def remove_to_class_p():
    """
    Receive a user (student) to add a specific class
    Return: message with token (Only if the information entered is correct)
    """
    
    data = get_info_token()
    message = 'You are not allowed to access this page'
    code = 403
    student = "-"
    class_ = "-"
    if (data['Rol'] == 'Professor'):
        try:
            student = str(request.get_json()['student'].encode('utf-8').strip())
            class_ = str(request.get_json()['class'].encode('utf-8').strip())
            code = 400
            ismyclass_bool = it_s_my_class_professor(data['User'],class_)
            if ismyclass_bool:
                message = "it's my class"
                resp_bool, resp_text = remove_student_to_class_professor(class_,student)
                message = resp_text
                if resp_bool:
                    code = 200
                else:
                    code = 400
            else:
                message = 'You are not allowed to do something in this class'
        except Exception as e:
            print e
            message = 'Internal error'
            code = 500
    insert_general_record('class/remove_student', 
        {'data': message, 'code': code, 'student':student, 'class': class_}
        ,data['User'])
    return jsonify({'data': message, 'code': code})


@app.route('/class/add_challenge', methods=['POST'])
@token_required
def add_challenge_to_class_p_():
    """
    Receive a user (student) to add a specific class
    Return: message
    """
    
    data = get_info_token()
    message = 'You are not allowed to access this page'
    code = 403
    idchallenge_ = -1
    idclass_ = -1
    if (data['Rol'] == 'Professor'):
        try:
            idchallenge_ = str(request.get_json()['idchallenge'])
            idclass_ = str(request.get_json()['idclass'].encode('utf-8').strip())
            code = 400
            ismyclass_bool = it_s_my_class_professor(data['User'],idclass_)
            if ismyclass_bool:
                message = "it's my class"
                resp_bool, resp_text = add_challenge_to_class_professor(idclass_,idchallenge_)
                message = resp_text
                if resp_bool:
                    code = 200
                else:
                    code = 500
            else:
                message = 'You are not allowed to do something in this class'
        except Exception as e:
            print e
            message = 'Internal error'
            code = 500
    insert_general_record('class/add_challenge', 
        {'data': message, 'code': code, 'idchallenge':idchallenge_, 'idclass':idclass_}
        ,data['User'])
    return jsonify({'data': message, 'code': code})

@app.route('/class/remove_challenge', methods=['POST'])
@token_required
def remove_challenge_to_class_p_():
    """
    Receive a user (student) to remove in a specific class
    Return: message
    """
    
    data = get_info_token()
    message = 'You are not allowed to access this page'
    code = 403
    idchallenge_ = -1
    idclass_ = -1
    if (data['Rol'] == 'Professor'):
        try:
            idchallenge_ = str(request.get_json()['idchallenge'])
            idclass_ = str(request.get_json()['idclass'].encode('utf-8').strip())
            code = 400
            ismyclass_bool = it_s_my_class_professor(data['User'],idclass_)
            if ismyclass_bool:
                message = "it's my class"
                resp_bool, resp_text = remove_challenge_to_class_professor(idclass_,idchallenge_)
                message = resp_text
                if resp_bool:
                    code = 200
                else:
                    code = 500
            else:
                message = 'You are not allowed to do something in this class'
        except Exception as e:
            print e
            message = 'Internal error'
            code = 500
    insert_general_record('class/remove_challenge', 
        {'data': message, 'code': code, 'idchallenge': idchallenge_, 'idclass': idclass_}
        ,data['User'])
    return jsonify({'data': message, 'code': code})

@app.route('/class/edit_info', methods=['POST'])
@token_required
def edit_info_p():
    """
    Receive a class's data of a specific id number (INT) and info to edit
    Return: message
    """
    
    data = get_info_token()
    message = 'You are not allowed to access this page'
    code = 403
    id_class_ = -1
    if (data['Rol'] == 'Professor'):
        try:
            id_class_ = str(request.get_json()['id_number'].encode('utf-8').strip())
            school_ = str(request.get_json()['school'].encode('utf-8').strip())
            identificator_ = str(request.get_json()['identificator'].encode('utf-8').strip())
            class_ = str(request.get_json()['class'].encode('utf-8').strip())
            year_ = str(request.get_json()['year'].encode('utf-8').strip())
            code = 400
            resp_bool , resp_text = edit_class_info_professor(id_class_,school_,identificator_,class_,year_, data['User'])
            message = resp_text
            if resp_bool:
                code = 200
            else:
                code = 403
                message = 'You are not allowed to access this page'
        except Exception as e:
            print e
            message = 'Internal error'
            code = 500
    insert_general_record('class/edit_info', 
        {'data': message, 'code': code,  'idclass': id_class_}
        ,data['User'])
    return jsonify({'data': message, 'code': code})

@app.route('/class/edit_challenge', methods=['POST'])
@token_required
def edit_challenge_to_class_p_():

    """
    Receive a challenge's data of a specific id number (INT)
    Return: message
    """
    


    data = get_info_token()
    message = 'You are not allowed to access this page'
    code = 403
    idchallenge_ = -1
    if (data['Rol'] == 'Professor'):
        try:
            idchallenge_ = str(request.get_json()['idchallenge'])
            if (itwasintializedbyanystudent(idchallenge_)):
                return jsonify({'data': "The challenge cannot edit , because was init by one or more student ", 'code': 403})
            title_ = str(request.get_json()['title'].encode('utf-8').strip())
            #photourl_ = str(request.get_json()['photourl'])
            summary_ = str(request.get_json()['summary'].encode('utf-8').strip())
            description_ = str(request.get_json()['description'].encode('utf-8').strip())
            aim_ = str(request.get_json()['aim'].encode('utf-8').strip())
            fk_category = str(request.get_json()['category'].encode('utf-8').strip())
            code = 400
            resp_bool , resp_text = edit_challenge_professor(idchallenge_,title_,summary_,description_,aim_,fk_category, data['User'])
            #resp_bool , resp_text = edit_challenge_professor(idchallenge_,title_,photourl_,summary_,description_,aim_,fk_category, data['User'])
            message = resp_text
            if resp_bool:
                code = 200
            else:
                code = 500
        except Exception as e:
            print e
            message = 'Internal error'
            code = 500
    insert_general_record('class/edit_challenge', 
        {'data': message, 'code': code,  'idchallenge': idchallenge_}
        ,data['User'])
    return jsonify({'data': message, 'code': code})

############################## END ONLY PROFESSOR #############################

############################## ONLY STUDENT #############################
@app.route('/search_bing/<id_challenge>/<query>' , methods=['GET'])
@token_required
def search_by_bing(id_challenge,query):
    """
    Receive a query by uri , with this method the user can search information using de Bing's engine
    Return: the results with [Title,description,Url]
    """
    data = get_info_token()
    user_ = data['User']
    rol_ = data['Rol']
    if rol_ == 'Student':
        code = 500
        try:
            challenge = get_all_challenges_student(user_)
            challenge_allowed = False
            for x in challenge:
                if str(x[0]) == str(id_challenge):
                    challenge_allowed = True
            if not challenge_allowed:
                insert_general_record('search_bing/idchallenge/query', 
                    {'message': 'Challenge not allowed', 'code': 403 , 'query': query}
                    ,user_)
                return jsonify({'message': 'Challenge not allowed',  'code': 403})
            bool_, finalized = challenge_is_initialized(id_challenge,user_)
            #Finalized -> 0:No , 1:Yes
            if int(finalized[0]) == 1:
                insert_general_record('search_bing/idchallenge/query', 
                    {'message': 'The challenge is already finished', 'code': 403 , 'query': query}
                    ,user_)
                return jsonify({'message': 'The challenge is already finished',  'code': 403})
            code = 200
            #with open("/var/www/api_gonsa2/bingjson.json") as json_data:
            #    message = json.load(json_data)
            response = search_term_bing(query)
            response_json = json.dumps(response, )
            message = response
            date_request = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            log_student_queries(user_,id_challenge,query,date_request)
            log_id_number = int(get_id_number_query(user_,id_challenge,query,date_request)[0])
            array_results =  json.loads(response_json)['webPages']['value']
            position = 1
            for result in array_results:
                insert_result_query(log_id_number, position, result['language'], result['name'], result['snippet'], result['url'])
                position = position + 1
            try:
                array_related_searchs = []
                position = 1
                for related_search_text in array_related_searchs:
                    insert_related_search_query(log_id_number,position, related_search_text['text'])
                    position = position + 1
            except Exception as e:
                print e
                print '*'
            
            
        except Exception as e:
            print e
            message = str(e)
            code = 500
            if '400 ' in str(e):
                message = 'Query parameters is missing or not valid (Bing)'
                code = 400
            elif '401 ' in str(e):
                message = 'Unauthorized (Bing)'
                code = 401
            elif '403 ' in str(e):
                message = 'Forbidden (Bing)'
                code = 403
            elif '410 ' in str(e):
                message = 'Used HTTP instead of the HTTPS protocol (Bing)'
                code = 410
            elif '429 ' in str(e):
                message = 'Exceeded their queries per second quota (Bing)'
                code = 429
    else:
        message = 'Only students allowed'
        code = 403
    insert_general_record('search_bing/idchallenge/query', 
        {'message': message, 'code': code , 'query': query}
        ,user_)
    return jsonify({'message': message,  'code': code})

@app.route('/library/add', methods=['POST'])
@token_required
def library_add_resource_():
    """
    Receive a challenge's data of a specific id number (INT)
    Return: message
    """
    data = get_info_token()
    user_ = data['User']
    rol_ = data['Rol']
    message = 'You are not allowed to access this page'
    code = 500
    if (rol_ == 'Student'):
        try:
            idchallenge_ = str(request.get_json()['idchallenge'])
            text_ = str(request.get_json()['text'].encode('utf-8').strip())
            url = str(request.get_json()['url'].encode('utf-8').strip())
            # Check permission over challenge
            challenge = get_all_challenges_student(user_)
            challenge_allowed = False
            for x in challenge:
                if str(x[0]) == str(idchallenge_):
                    challenge_allowed = True
            if not challenge_allowed:
                insert_general_record('library/add', 
                    {'message': 'Challenge not allowed',  'code': 403}
                    ,user_)
                return jsonify({'message': 'Challenge not allowed',  'code': 403})
            # END Check permission over challenge
            # Check if exist a similar resource
            response = check_is_in_text_library(user_,idchallenge_, text_, url)
            if response:
                insert_general_record('library/add', 
                    {'message': 'The resource was previously registered',  'code': 400}
                    ,user_)
                return jsonify({'message': 'The resource was previously registered',  'code': 400})

            # END Check if exist a similar resource
            date_request = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            bool_ = add_text_library(user_,idchallenge_, text_, url, date_request, 0)
            if bool_:
                code = 200
                message = 'The resource has been successfully registered'
            else:
                code = 400
                message = 'Something went wrong'
        except Exception as e:
            print e
            code = 500
    else:
        message = 'Only students allowed'
        code = 403
    insert_general_record('library/add', 
        {'message': message,  'code': code}
        ,user_)
    return jsonify({'message': message,  'code': code})


@app.route('/library/accion', methods=['POST'])
@token_required
def library_remove_resource_():
    """
    Receive a challenge's data of a specific id number (INT)
    Return: message
    """
    data = get_info_token()
    user_ = data['User']
    rol_ = data['Rol']
    message = 'You are not allowed to access this page'
    code = 500
    action_ = '-'
    if (rol_ == 'Student'):
        try:
            idchallenge_ = str(request.get_json()['idchallenge'])
            text_ = str(request.get_json()['text'].encode('utf-8').strip())
            url = str(request.get_json()['url'].encode('utf-8').strip())
            action_ = str(request.get_json()['action'].encode('utf-8').strip())
            if 'block' == action_.lower():
                number_accion = 0
            elif 'hide' == action_.lower():
                number_accion = 1
            elif 'remove' == action_.lower():
                number_accion = 2
            else:
                insert_general_record('library/accion', 
                    {'message': 'Action not entered or not allowed',  'code': 400 , 'action': action_.lower()}
                    ,user_)
                return jsonify({'message': 'Action not entered or not allowed',  'code': 400})
            # Check permission over challenge
            challenge = get_all_challenges_student(user_)
            challenge_allowed = False
            for x in challenge:
                if str(x[0]) == str(idchallenge_):
                    challenge_allowed = True
            if not challenge_allowed:
                insert_general_record('library/accion', 
                    {'message': 'Challenge not allowed',  'code': 403 , 'action': action_.lower()}
                    ,user_)
                return jsonify({'message': 'Challenge not allowed',  'code': 403})
            # END Check permission over challenge
            # Check if exist a similar resource
            response = check_is_in_text_library(user_,idchallenge_, text_, url)
            if response:
                bool_ = update_text_library(user_,idchallenge_, text_, url, number_accion)
                if bool_:
                    code = 200
                    message = 'The resource has been successfully modified'
                    insert_general_record('library/accion', 
                    {'url': url, 'text': text_ , 'idchallenge': idchallenge_, 'code': 200 , 'action': action_.lower()},user_)
                    return jsonify({'message': message,  'code': code})
                else:
                    code = 400
                    message = 'Something went wrong'
        except Exception as e:
            print e
            code = 500
    else:
        message = 'Only students allowed'
        code = 403
    insert_general_record('library/accion', 
                    {'message': message,  'code': code , 'action': action_.lower()}
                    ,user_)
    return jsonify({'message': message,  'code': code})


@app.route('/getallmylibrary/<id_challenge>', methods=['GET'])
@token_required
def getallmylibrary_(id_challenge):
    message = 'You are not allowed to access this page'
    code = 403
    data = get_info_token()
    user_ = data['User']
    rol_ = data['Rol']
    if (rol_ == 'Student'):
        message = getallmylibrary_by_challenge(user_,id_challenge)
        code = 200
    insert_general_record('getallmylibrary/[id]', 
                    {'message': message, 'code': code, 'idchallenge': id_challenge}
                    ,user_)
    return jsonify({'message': message, 'code': code})


@app.route('/finish_challenge', methods=['POST'])
@token_required
def close_challenge_():
    message = 'You are not allowed to access this page'
    code = 403
    data = get_info_token()
    user_ = data['User']
    rol_ = data['Rol']
    idchallenge_ = -1
    solution = '-'
    if (rol_ == 'Student'):
        try:
            idchallenge_ = str(request.get_json()['idchallenge'])
            solution = str(request.get_json()['solution'].encode('utf-8').strip())
            # Check permission over challenge
            challenge = get_all_challenges_student(user_)
            challenge_allowed = False
            for x in challenge:
                if str(x[0]) == str(idchallenge_):
                    challenge_allowed = True
            if not challenge_allowed:
                return jsonify({'message': 'Challenge not allowed',  'code': 400})
            # END Check permission over challenge
            # Check if the challenge is finished
            _bool , _sent_date = check_challenge_is_finished(idchallenge_, user_)
            if _bool:
                insert_general_record('finish_challenge', 
                    {'message': 'The final solution of the challenge has already been sent at ' + str(_sent_date),  'code': 403 , 'idchallenge':idchallenge_, 'response':solution}
                    ,user_)
                return jsonify({'message': 'The final solution of the challenge has already been sent at ' + str(_sent_date),  'code': 403})
            date_request = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            bool_ , message = finish_challenge(idchallenge_, user_, solution, date_request)
            if bool_:
                code = 200
            else:
                code = 400
            #
        except Exception as e:
            raise e
    insert_general_record('finish_challenge', 
        {'message': message, 'code': code , 'idchallenge':idchallenge_, 'response':solution}
        ,user_)
    return jsonify({'message': message, 'code': code})


@app.route('/new_response', methods=['POST'])
@token_required
def new_response_():
    message = 'You are not allowed to access this page'
    code = 403
    data = get_info_token()
    user_ = data['User']
    rol_ = data['Rol']
    idchallenge_ = -1
    solution = '-'
    last_response = '-'
    if (rol_ == 'Student'):
        try:
            idchallenge_ = str(request.get_json()['idchallenge'])
            solution = str(request.get_json()['solution'].encode('utf-8').strip())
            # Check permission over challenge
            challenge = get_all_challenges_student(user_)
            challenge_allowed = False
            for x in challenge:
                if str(x[0]) == str(idchallenge_):
                    challenge_allowed = True
            if not challenge_allowed:
                return jsonify({'message': 'Challenge not allowed',  'code': 400})
            # END Check permission over challenge
            # Check if the challenge is finished
            _bool , _sent_date = check_challenge_is_finished(idchallenge_, user_)
            if _bool:
                insert_general_record('new_response', 
                    {'message': 'The final solution of the challenge has already been sent at ' + str(_sent_date),  'code': 403 , 'idchallenge':idchallenge_, 'response':solution}
                    ,user_)
                return jsonify({'message': 'The final solution of the challenge has already been sent at ' + str(_sent_date),  'code': 403})
            last_response = str(Get_last_response_challenge(idchallenge_, user_)[0])
            bool_  = new_response(solution, idchallenge_, user_)
            if bool_:
                code = 200
                message = 'The response was entered successfully'
            else:
                code = 400
                message = 'Data entered with errors'
            #
        except Exception as e:
            raise e
    
    insert_general_record('new_response', 
        {'message': message, 'code': code , 'idchallenge':idchallenge_, 'prev_response':last_response , 'response':solution}
        ,user_)
    return jsonify({'message': message, 'code': code})

@app.route('/reg_event', methods=['POST'])
@token_required
def reg_event_():
    user_ = get_info_token()['User']
    try:
        data_ = str(request.get_json()['data'].encode('utf-8').strip())
        insert_general_record('event_registered', data_,user_)
        return jsonify({'message': 'ok', 'code': 200})
    except Exception as e:
        print 'eee'
        print e
        return jsonify({'message': 'Bad request', 'code': 401})
    

############################## END ONLY STUDENT #############################

############################## ONLY ADMINISTRADOR #############################
@app.route('/a_getallusers', methods=['GET'])
@token_required
def a_getallusers():
    data = get_info_token()
    message = 'You are not allowed to access this page'
    code = 403
    users = []
    if (data['Rol'] == 'Administrador'):
        users = a_get_all_users()
        message = 'Ok'
        code = 200
    insert_general_record('a_getallusers', 
        {'message': message, 'users': len(users),'code': code}
        ,data['User'])
    return jsonify({'message': message, 'users': users,'code': code})
############################## END ONLY ADMINISTRADOR #############################


if __name__ == '__main__':
    app.run(debug=c.get_api_debug(),
            host=c.get_api_host(), port=c.get_api_port())
