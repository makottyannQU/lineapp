from pathlib import Path
import datetime

#LINEbot
access_token='aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa'
secret_key='aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa'
img_url = 'https://aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa'

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

# department
department = {
    '工学部': ['機械航空工学科', '電気情報工学科', '物質化学工学科', '地球環境工学科', 'エネルギー科学科', '建築学科'],
    '理学部': ['物理学科', '化学科', '地球惑星科学科', '数学科', '生物学科'],
    '農学部': ['生物資源環境学科'],
    '文学部': ['人文学科'],
    '教育学部': ['教育学科'],
    '法学部': ['法学科'],
    '経済学部': ['経済・経営学科', '経済工学科'],
    '共創学部': ['共創学科'],
    '医学部': ['医学科', '生命科学科', '保健学科'],
    '薬学部': ['創薬科学科', '臨床薬学科'],
    '歯学部': ['歯学科'],
    '芸術工学部': ['環境設計学科', '工業設計学科', '画像設計学科', '音響設計学科', '芸術情報設計学科'],
    'その他': ['その他']
}

# grade
grade = {'1年': 1, '2年': 2, '3年': 3, '4年': 4, '修士1年': 5, '修士2年': 6, 'その他': 0}

# flask_setting
JSON_AS_ASCII = False
SQLALCHEMY_DATABASE_URI = db_uri
SQLALCHEMY_TRACK_MODIFICATIONS = True
SWAGGER_UI_DOC_EXPANSION = 'list'
RESTPLUS_VALIDATE = True
UPLOADED_CONTENT_DIR = Path("upload")
