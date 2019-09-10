# -*- coding: utf-8 -*-
from flask import Flask, request, abort
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

line_bot_api = LineBotApi(settings.access_token)

withcancel_id="richmenu-cd841ccd94b9a382f2b92c87eeeb82f1"
withoutcancel_id="richmenu-bffc4c758c6c93ba53a17d4e13ff1774"
non_id='richmenu-c56be3dcbee4749c75add044ec21ab66'

# #create rich menu
# url = 'https://api.line.me/v2/bot/richmenu'
# data = {
#     "size": {
#         "width": 2500,
#         "height": 843
#     },
#     "selected": True,
#     "name": "with cancel",
#     "chatBarText": "メニューを開く・閉じる",
#     "areas": [
#         {
#             "bounds": {
#                 "x": 0,
#                 "y": 0,
#                 "width": 625,
#                 "height": 843
#             },
#             "action": {
#                 "type": "postback",
#                 "data": "action=order"
#             }
#         },
#         {
#             "bounds": {
#                 "x": 625,
#                 "y": 0,
#                 "width": 625,
#                 "height": 843
#             },
#             "action": {
#                 "type": "postback",
#                 "data": "action=cancel"
#             }
#         },
#         {
#             "bounds": {
#                 "x": 1250,
#                 "y": 0,
#                 "width": 625,
#                 "height": 843
#             },
#             "action": {
#                 "type": "postback",
#                 "data": "action=check"
#             }
#         },
#         {
#             "bounds": {
#                 "x": 1875,
#                 "y": 0,
#                 "width": 625,
#                 "height": 843
#             },
#             "action": {
#                 "type": "postback",
#                 "data": "action=menu"
#             }
#         }
#     ]
# }
# headers = {
#     'Content-Type': 'application/json',
#     'Authorization': 'Bearer ' + settings.access_token
# }
# requests.post(url, data=json.dumps(data), headers=headers)

# #upload image
# with open('richmenu/withcancel.png', 'rb') as f:
#     line_bot_api.set_rich_menu_image(id, 'image/png', f)


# #check rich menu
# richmenus=line_bot_api.get_rich_menu_list()
# print(richmenus)

# #set default rich menu
# url=f'https://api.line.me/v2/bot/user/all/richmenu/{non_id}'
# headers = {
#     'Authorization': 'Bearer ' + settings.access_token
# }
# res=requests.post(url, headers=headers)
# print(res)

# #create rich menu
# url = 'https://api.line.me/v2/bot/richmenu'
# data = {
#     "size": {
#         "width": 2500,
#         "height": 843
#     },
#     "selected": True,
#     "name": "without cancel",
#     "chatBarText": "メニューを開く・閉じる",
#     "areas": [
#         {
#             "bounds": {
#                 "x": 0,
#                 "y": 0,
#                 "width": 834,
#                 "height": 843
#             },
#             "action": {
#                 "type": "postback",
#                 "data": "action=order"
#             }
#         },
#         {
#             "bounds": {
#                 "x": 834,
#                 "y": 0,
#                 "width": 833,
#                 "height": 843
#             },
#             "action": {
#                 "type": "postback",
#                 "data": "action=check"
#             }
#         },
#         {
#             "bounds": {
#                 "x": 1667,
#                 "y": 0,
#                 "width": 833,
#                 "height": 843
#             },
#             "action": {
#                 "type": "postback",
#                 "data": "action=menu"
#             }
#         }
#     ]
# }
# headers = {
#     'Content-Type': 'application/json',
#     'Authorization': 'Bearer ' + settings.access_token
# }
# requests.post(url, data=json.dumps(data), headers=headers)

# #upload image
# with open('richmenu/withoutcancel.png', 'rb') as f:
#     line_bot_api.set_rich_menu_image(withoutcancel_id, 'image/png', f)

# #create rich menu
# url = 'https://api.line.me/v2/bot/richmenu'
# data = {
#     "size": {
#         "width": 2500,
#         "height": 843
#     },
#     "selected": False,
#     "name": "non",
#     "chatBarText": "受付時間外",
#     "areas": [{
#             "bounds": {
#                 "x": 0,
#                 "y": 0,
#                 "width": 2500,
#                 "height": 843
#             },
#             "action": {
#                 "type": "postback",
#                 "data": "action=non"
#             }
#         }]
# }
# headers = {
#     'Content-Type': 'application/json',
#     'Authorization': 'Bearer ' + settings.access_token
# }
# res=requests.post(url, data=json.dumps(data), headers=headers)
# print(res)

# #upload image
# with open('richmenu/non.png', 'rb') as f:
#     line_bot_api.set_rich_menu_image(non_id, 'image/png', f)