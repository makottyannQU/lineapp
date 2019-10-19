from pathlib import Path
import datetime
import subprocess

#LINEbot
access_token='i+Km5q0lj1axuCaoIdc7lHa2iqYliBcNCIPmTwuZPuJnMl6c5jckrvWNTPtsPv8QDL2+vK8Xil19Qo0fkWb898ZfQxEI7NdofCRWhMINJAA4WXqzUzquzzdJF3BBh/ALpfeE0OZniVmI8nrDYNF+UgdB04t89/1O/w1cDnyilFU='
secret_key='77457a9d8b1f6dacc113dd67c6d0af90'
img_url = 'https://makottyann-app.herokuapp.com/'
coupon_uri = 'http://lin.ee/7uIGrdQ'
temp_message = '''このアカウントから個別に返信することはできません。
店主に御用の場合は下記LINEアカウント(まこっちゃん弁当店主)にご連絡ください。
https://line.me/ti/p/makottyann'''

testmode=0

# LINE notify
my_token='rL71jYoAcCK3pgRh4JmMzGVPdO8DDKd5y6gk13AVvYO'
notify_token=my_token

# richmenu
withcancel_richmenu_id = "richmenu-5c8e107773b7c18eb5e1a1fe1d5013f1"
withoutcancel_richmenu_id = "richmenu-c20594606512530e360928d2dff80155"
none_richmenu_id = "richmenu-341d1f26d1392d84f5657e1dd2091619"

#DB
if testmode==1:
    db_uri = 'postgres://uvacfxdfcurtmx:058c87a76cae4a258b542bfaa268acbc56146bc4b70d01595d7adc102ce0fe2c@ec2-174-129-18-42.compute-1.amazonaws.com:5432/d20r5q631d5qtv'
else:
    proc = subprocess.Popen('printenv DATABASE_URL', stdout=subprocess.PIPE, shell=True)
    db_uri = proc.stdout.read().decode('utf-8').strip()

# makottyann
operationtime = [[datetime.time(0, 0), 'pm'],
                 [datetime.time(11, 40), 'pm'],
                 [datetime.time(12, 30), 'pm'],
                 [datetime.time(21, 00), 'pm']]

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
