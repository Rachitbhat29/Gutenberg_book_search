import os

class Config(object):
    """ Parent configuration class """
    db_host = 'localhost'
    db_user = 'postgres'
    db_password = 'admin'
    db_port = 5432
    db_name = 'Book_Repo_Db'

    DEBUG = False
    TESTING = False
    Database_Url = os.getenv("Main_Database")
    SECRET_KEY = os.getenv("SECRET")


class DevelopmentConfig(Config):
    """ Configuration for development environment """
    DEBUG = True
    Database_Url = os.getenv("Main_Database")


class TestingConfig(Config):
    """ Configuratio(env) zonecc@trevor:/var/codezonecc/My Diary$n for the testing environment """
    TESTING = True
    DEBUG = True
    Database_Url = os.getenv("Test_Database")


# for heroku in case I decide to host the app but that's it
class ProductionConfig(Config):
    """ Configuration for the production environment """
    DEBUG = False
    TESTING = False
    Database_Url = os.getenv("DATABASE_URL")


app_config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig
}




