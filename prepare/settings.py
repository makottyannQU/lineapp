from pathlib import Path
import datetime

#LINEbot
access_token='aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa'
secret_key='aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa'

# richmenu
withcancel_richmenu_id = "richmenu-94696c816d15e60310442d3091f3d83e"
withoutcancel_richmenu_id = "richmenu-aeba8b140b55dbe3f9b99554e71bfc02"
none_richmenu_id = "richmenu-16e6e2e65f078bc7cb265ec3f67a90be"

#DB
db_info = {
    'user': 'aaaaaaaaaaaaaa',
    'password': 'aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa',
    'host': 'aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa',
    'database': 'aaaaaaaaaaaaaa',
    'charset': 'utf8mb4',
}
db_uri = 'postgres://{user}:{password}@{host}/{database}'.format(**db_info)  # for psql in heroku
# db_uri='mysql+pymysql://{user}:{password}@{host}/{database}?charset={charset}'.format(**db_info)

# makottyann
operationtime = [[datetime.time(7, 0), 'non'],
                 [datetime.time(11, 40), 'am'],
                 [datetime.time(13, 0), 'non'],
                 [datetime.time(21, 0), 'pm']]

# flask_setting
JSON_AS_ASCII = False
SQLALCHEMY_DATABASE_URI = db_uri
SQLALCHEMY_TRACK_MODIFICATIONS = True
SWAGGER_UI_DOC_EXPANSION = 'list'
RESTPLUS_VALIDATE = True
UPLOADED_CONTENT_DIR = Path("upload")
