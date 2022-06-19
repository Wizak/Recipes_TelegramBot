import os
basedir = os.path.abspath(os.path.dirname(__file__))

class Config(object):
    # SQLALCHEMY_DATABASE_URI = 'postgresql+psycopg2://{user}:{pw}@{url}/{db}'.format(
    #     user='postgres',
    #     pw='admin',
    #     url='localhost:5431',
    #     db='recipes_base'
    # )
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, 'app.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    API_TOKEN = '1911247240:AAG4a6xYAEdEL2ziGfixb0GIc8cvPBzVW3Y'
    PASSWORD = 'Bodya160720'