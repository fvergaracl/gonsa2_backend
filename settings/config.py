import datetime


class Database:

    config = None

    def __init__(self):
        # To connect BD
        self.user = 'root'
        self.password = ''
        self.host = '127.0.0.1'
        self.database_name = 'chata'

        # DB
        self.config = {'user': self.user,
                       'password': self.password,
                       'host': self.host,
                       'database': self.database_name}


class Config:

    def __init__(self):
        # JWT Settings
        self.api_jwt_key = 'd95ms32_%'
        self.api_jwt_time = datetime.timedelta(minutes=1800)

        # General Settings
        self.platform_name = 'GonZa2'

        self.api_host = '127.0.0.1'
        self.api_port = 5000
        self.api_debug = True

        self.web_url = 'http://localhost'

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
