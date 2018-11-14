from settings.config import Config, Database

from models.users import login_user

from flask import Flask, jsonify, request
import jwt, datetime, ast, json
from functools import wraps
from flask_cors import CORS

app = Flask(__name__)
CORS(app)
c = Config()


def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        try:
            tokenTEMP = request.headers['Authorization']
            token = tokenTEMP.split(" ")
            if not tokenTEMP:
                # token not found
                return jsonify({'message': 'Tn', 'code': 404})
            try:
                # token valid
                data = jwt.decode(token[1], c.get_jwt_key())
            except Exception as e:
                # token not valid
                return jsonify({'message': 'Ti','code': 400})
            return f(*args, **kwargs)
        except KeyError:
            # token not found
            return jsonify({'message': 'Tn', 'code': 404})
    return decorated


@app.route('/', methods=['GET'])
def testing_root():
    return jsonify({'message': "It's works", 'code': 200})


@app.route('/login', methods=['POST'])
def login():
    name_ = ''
    token = ''
    try:
        user_ = str(request.get_json()['user'])
        pass_ = str(request.get_json()['pass'])
        allok, name_ = login_user(user_,pass_)
        if allok:
            code = 200
            message = 'Welcome'
            name_ = name_
            token = jwt.encode(
                {'User': name_, 'exp': datetime.datetime.utcnow() + c.get_jwt_time()},
                c.get_jwt_key())
        else:
            code = 400
            message = 'User or password, not valid'
            name_ = ''
    except Exception as e:
        code = 500
        message = 'Something went wrong'
    return jsonify({'code': code,
                    'message': message,
                    'name': name_,
                    'token': token})


if __name__ == '__main__':
    app.run(debug=c.get_api_debug(), host=c.get_api_host(), port=c.get_api_port())