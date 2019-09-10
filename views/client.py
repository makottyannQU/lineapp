# -*- coding: utf-8 -*-
from flask import request, abort,Blueprint,current_app
import pandas as pd
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import numpy as np
import datetime
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage, FollowEvent, UnfollowEvent, PostbackEvent
# import psycopg2  # for psql in heroku
import pymysql
import requests
import json
import ast

import settings
from models import *


with open('jsn.json') as f:
    jsn = json.load(f)

blueprint = Blueprint('client', __name__, url_prefix='/', static_folder='/views/static',
                      template_folder='/views/templates')

db_engine = create_engine(settings.db_uri, pool_pre_ping=True)

line_bot_api = LineBotApi(settings.access_token)
handler = WebhookHandler(settings.secret_key)

#  http postする時のヘッダー
headers = {
        'Content-Type': 'application/json',
        'Authorization': 'Bearer ' + settings.access_token
    }
# replyする時はここにjsonをpostする
reply_url = 'https://api.line.me/v2/bot/message/reply'

def operation():
    now=datetime.datetime.now().time()
    for time in settings.operationtime:
        if now<time[0]:
            return time[1]
    return 'non'

@blueprint.route("/callback", methods=['POST'])
def callback():
    # get X-Line-Signature header value
    signature = request.headers['X-Line-Signature']

    # get request body as text
    body = request.get_data(as_text=True)
    current_app.logger.info("Request body: " + body)

    # handle webhook body
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)

    return 'OK'


# @handler.add(FollowEvent)
# def handle_follow(event):
#     profile = line_bot_api.get_profile(event.source.user_id)
#
#     user = User(id=profile.user_id, name=profile.display_name)
#     db.session.add(user)
#     db.session.commit()
#     # print(profile.user_id, profile.display_name, profile.picture_url, profile.status_message)
#     app.logger.info(f'User add {profile.user_id}.')
#     data = jsn["Follow_message"]
#     # text = f'初めまして{profile.display_name}さん\nまこっちゃん弁当です'
#     line_bot_api.reply_message(
#         event.reply_token,
#         TextSendMessage(data["text"])
#     )
#
#
# @handler.add(UnfollowEvent)
# def handle_follow(event):
#     Session = sessionmaker(bind=db_engine)
#     s = Session()
#     s.query(User).filter(User.id == event.source.user_id).delete()  # statusを0にする
#     s.commit()
#     app.logger.info(f'User delete {event.source.user_id}.')


# @handler.add(MessageEvent, message=TextMessage)
# def message_text(event):
#     # 入力された文字列を格納
#     push_txt = event.message.text
#
#     token = event.reply_token
#     rtext = event.message.text
#
#     # メッセージによって分岐
#     if push_txt == '注文':
#         # 種類とサイズを選んで, 注文カルーセル
#         data_list = [jsn["Select_kinds_size"], jsn["Order_carousel"]]
#         data = {
#             'replyToken': token,
#             'messages': data_list
#         }
#
#         requests.post(reply_url, data=json.dumps(data), headers=headers)

@handler.add(PostbackEvent)
def postback(event):
    data = event.postback.data
    token = event.reply_token
    print(data)
    data_dic = ast.literal_eval(data)
    print(data_dic)
    if data_dic['action'] == 'rich_order':
        print(event.postback.params)
        # db_engine = create_engine(settings.db_uri, pool_pre_ping=True)
        # Session = sessionmaker(bind=db_engine)
        # s = Session()
        #
        # query = f'''
        #         select meal.id, meal.name, meal.image, meal.s_price, meal.m_price, meal.l_price, menu.date
        #         from "meal" inner join "menu" on meal.id = menu.meal_id
        #         where menu.date = '20190801';
        #         '''
        # df = pd.read_sql(query, db_engine)
        # print(df)

        # 種類とサイズを選んで, 注文カルーセル
        data_list = [jsn["Select_kinds_size"], jsn["Order_carousel"]]
        data = {
            'replyToken': token,
            'messages': data_list
        }
        requests.post(reply_url, data=json.dumps(data), headers=headers)