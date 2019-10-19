import datetime

class emailconfig():

    def __init__(self):
        ####### email settings ########
        self.emailuser = 'XXXXXXXXXXXXXXXXX'
        self.emailpass = 'XXXXXXXXXXXXXXXXX'
        self.emailserurl = 'smtp.gmail.com'
        self.emailserport = 465
  

    def get_user(self):
        return self.emailuser

    def get_pass(self):
        return self.emailpass

    def get_url(self):
        return self.emailserurl

    def get_port(self):
        return self.emailserport


class Database:

    config = None

    def __init__(self):
        # To connect BD
        self.user = 'XXXXXXXXXXXXXXXXX'
        self.password = 'XXXXXXXXXXXXXXXXX'
        self.host = 'localhost'
        self.database_name = 'XXXXXXXXXXXXXXXXX'

        # DB
        self.config = {'user': self.user,
                       'password': self.password,
                       'host': self.host,
                       'database': self.database_name}


class Config:

    def __init__(self):
        # JWT Settings
        self.api_jwt_key = 'XXXXXXXXXXXXXXXXX'
        self.api_jwt_time = datetime.timedelta(minutes=1800)

        # General Settings
        self.platform_name = 'GonSA2'

        self.api_host = 'http://tera.uach.cl'
        self.api_port = 8080
        self.api_debug = True

        self.web_url = 'http://tera.uach.cl'

        self.email_to_contact = 'Email@ejemplo.com'

        #How along the token to recovery password is valid
        self.token_recovery_time = 24*7 # hours

    def get_jwt_key(self):
        return self.api_jwt_key

    def get_jwt_time(self):
        return self.api_jwt_time

    def get_platform_name(self):
        return self.platform_name

    def get_api_host(self):
        return self.api_host

    def get_api_port(self):
        return self.api_port

    def get_api_debug(self):
        return self.api_debug

    def get_web_url(self):
        return self.web_url

    def get_email_contact(self):
        return self.email_to_contact

    def get_token_exp(self):
        return self.token_recovery_time