import secrets

DEBUG = True

SQLALCHEMY_DATABASE_URI = 'sqlite:///storage.db'   #'postgresql://postgres:postgre123@localhost/question'      #'sqlite:///storage.db'

SQLALCHEMY_TRACK_MODIFICATIONS = True

SECRET_KEY = secrets.token_hex(16)        #'algo_secreto'