# -*- coding: utf-8 -*-
from flask import request, abort,Blueprint,current_app
import pandas as pd
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import numpy as np
import datetime
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage, FollowEvent, UnfollowEvent
import psycopg2  # for psql in heroku
import requests
import json

import settings
from models import *

blueprint = Blueprint('client', __name__, url_prefix='/', static_folder='/views/static',
                      template_folder='/views/templates')

db_engine = create_engine(settings.db_uri, pool_pre_ping=True)

line_bot_api = LineBotApi(settings.access_token)
handler = WebhookHandler(settings.secret_key)

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

@handler.add(FollowEvent)
def handle_follow(event):
    profile = line_bot_api.get_profile(event.source.user_id)

    user = User(id=profile.user_id, name=profile.display_name)
    db.session.add(user)
    db.session.commit()
    # print(profile.user_id, profile.display_name, profile.picture_url, profile.status_message)
    current_app.logger.info(f'User add {profile.user_id}.')

    text = f'初めまして{profile.display_name}さん\nまこっちゃん弁当です'
    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text)
    )


@handler.add(UnfollowEvent)
def handle_follow(event):
    Session = sessionmaker(bind=db_engine)
    s = Session()
    s.query(User).filter(User.id == event.source.user_id).delete()
    s.commit()
    current_app.logger.info(f'User delete {event.source.user_id}.')


@handler.add(MessageEvent, message=TextMessage)
def message_text(event):

    token = event.reply_token
    url = 'https://api.line.me/v2/bot/message/reply'
    data = {
        'replyToken': token,
        'messages': [
            {
                "type": "text",
                "text": "カルーセル表示"
            },
            {
                "type": "template",
                "altText": "this is a carousel template",
                "template": {
                    "type": "carousel",
                    "columns": [
                        {
                            "thumbnailImageUrl": "https://example.com/bot/images/item1.jpg",
                            "imageBackgroundColor": "#FFFFFF",
                            "title": "this is menu",
                            "text": "description",
                            "defaultAction": {
                                "type": "uri",
                                "label": "View detail",
                                "uri": "http://example.com/page/123"
                            },
                            "actions": [
                                {
                                    "type": "postback",
                                    "label": "Buy",
                                    "data": "action=buy&itemid=111"
                                },
                                {
                                    "type": "postback",
                                    "label": "Add to cart",
                                    "data": "action=add&itemid=111"
                                },
                                {
                                    "type": "uri",
                                    "label": "View detail",
                                    "uri": "http://example.com/page/111"
                                }
                            ]
                        },
                        {
                            "thumbnailImageUrl": "https://example.com/bot/images/item2.jpg",
                            "imageBackgroundColor": "#000000",
                            "title": "this is menu",
                            "text": "description",
                            "defaultAction": {
                                "type": "uri",
                                "label": "View detail",
                                "uri": "http://example.com/page/222"
                            },
                            "actions": [
                                {
                                    "type": "postback",
                                    "label": "Buy",
                                    "data": "action=buy&itemid=222"
                                },
                                {
                                    "type": "postback",
                                    "label": "Add to cart",
                                    "data": "action=add&itemid=222"
                                },
                                {
                                    "type": "uri",
                                    "label": "View detail",
                                    "uri": "http://example.com/page/222"
                                }
                            ]
                        }
                    ],
                    "imageAspectRatio": "rectangle",
                    "imageSize": "cover"
                }
            }
        ]
    }
    headers = {
        'Content-Type': 'application/json',
        'Authorization': 'Bearer ' + settings.access_token
    }
    requests.post(url, data=json.dumps(data), headers=headers)