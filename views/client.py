# -*- coding: utf-8 -*-
from flask import request, abort, Blueprint, current_app
import pandas as pd
from sqlalchemy import create_engine, func
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
import createjson

import settings
from models import *

blueprint = Blueprint('client', __name__, url_prefix='/', static_folder='/views/static',
                      template_folder='/views/templates')

db_engine = create_engine(settings.db_uri, pool_pre_ping=True)

line_bot_api = LineBotApi(settings.access_token)
handler = WebhookHandler(settings.secret_key)

size_list = ['小盛', '並盛', '大盛']

#  http postする時のヘッダー
headers = {
    'Content-Type': 'application/json',
    'Authorization': 'Bearer ' + settings.access_token
}
# replyする時はここにjsonをpostする
reply_url = 'https://api.line.me/v2/bot/message/reply'
img_url = settings.img_url


def operation():
    now = datetime.datetime.now().time()
    for time in settings.operationtime:
        if now < time[0]:
            return time[1]
    return 'none'


def notify(message):
    line_notify_api = 'https://notify-api.line.me/api/notify'
    group_headers = {'Authorization': 'Bearer ' + settings.notify_token}
    payload = {'message': message}
    try:
        requests.post(line_notify_api, data=payload, headers=group_headers)
    except:
        current_app.logger.info('LINE Notify Error : ' + message)


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


@handler.add(MessageEvent, message=TextMessage)
def message_text(event):
    user_id = event.source.user_id
    text = event.message.text
    current_app.logger.info(f'user_id:{user_id} text:{text}')

    if text not in ['はい', 'いいえ']:
        message = settings.temp_message
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text=message))


@handler.add(PostbackEvent)
def postback(event):
    Session = sessionmaker(bind=db_engine)
    s = Session()

    reply_json = []
    data = event.postback.data
    user_id = event.source.user_id
    # current_app.logger.info(f'user_id:{user_id} text:{data}')

    data_dic = ast.literal_eval(data)
    operation_status = operation()
    if operation_status == 'none':
        return 0
    now = datetime.datetime.now()

    if data_dic['action'] == 'rich_none':
        return 0


    elif data_dic['action'] == 'rich_order':
        if operation_status == 'am':
            date = now
        elif operation_status == 'pm':
            date = now + datetime.timedelta(days=1)
        else:
            return 0

        tmpdate = date.strftime('%Y%m%d')
        query = f'''
                select date from menu where date >= {tmpdate} order by date limit 1;
                '''
        df = pd.read_sql(query, db_engine)
        if len(df) > 0:
            date = df.date[0]
            query = f'''
                    select menu.date, menu.meal_id, meal.name as meal_name, meal.image as image_path, meal.s_price,
                    meal.m_price, meal.l_price, menu.s_stock, menu.m_stock, menu.l_stock
                    from (select * from menu where date = {date}) as menu inner join meal on menu.meal_id = meal.id;
                    '''
            df = pd.read_sql(query, db_engine)
            df['image_path'] = img_url + df['image_path']
            size_flag = [sum(df['s_price']) > 0, sum(df['m_price']) > 0, sum(df['l_price']) > 0]

            query = f'''
                    select orders.meal_id, orders.size, sum(count) as count from ( select meal_id, size, count from orders
                    where date = {date} and status != -1) as orders group by orders.meal_id, orders.size;
                    '''
            count = pd.read_sql(query, db_engine)

            for i, row in count.iterrows():
                size = row['size']
                if size == 0:
                    tmp = 's_stock'
                elif size == 1:
                    tmp = 'm_stock'
                else:
                    tmp = 'l_stock'
                df.loc[df['meal_id'] == row['meal_id'], tmp] = df[df['meal_id'] == row['meal_id']][tmp] - row['count']

            order_dict = df.to_dict(orient='records')
            reply_json.append(createjson.order(order_dict, size_flag))
            if int(tmpdate) != int(date):
                reply_json.append(createjson.danger(date))
        else:
            reply_json.append(createjson.text("現在、注文できるメニューがありません"))


    elif data_dic['action'] == 'rich_check':
        if operation_status == 'am':
            date = now
        elif operation_status == 'pm':
            date = now + datetime.timedelta(days=1)
        date = date.strftime('%Y%m%d')
        query = f'''
                select orders.date, orders.meal_id, meal.name as meal_name, orders.size from ( select * from orders
                where date >= {date} and user_id = '{user_id}' and status = 1 ) as orders inner join meal on orders.meal_id = meal.id;
                '''
        df = pd.read_sql(query, db_engine)
        if len(df) > 0:
            check_dict = df.iloc[0].to_dict()
            reply_json.append(createjson.check_order(check_dict))
        else:
            reply_json.append(createjson.text("注文がありません"))


    elif data_dic['action'] == 'rich_cancel':
        if operation_status == 'am':
            date = now
        elif operation_status == 'pm':
            date = now + datetime.timedelta(days=1)
        date = date.strftime('%Y%m%d')
        query = f'''
                select orders.date, orders.meal_id, meal.name as meal_name, orders.size from ( select * from orders
                where date >= {date} and user_id = '{user_id}' and status = 1 ) as orders inner join meal on orders.meal_id = meal.id;
                '''
        df = pd.read_sql(query, db_engine)
        if len(df) > 0:
            cancel_dict = df.iloc[0].to_dict()
            reply_json.append(createjson.cancel_confirm(cancel_dict))
        else:
            reply_json.append(createjson.text("注文がありません"))


    elif data_dic['action'] == 'rich_menu':
        if operation_status == 'am':
            date = now
        elif operation_status == 'pm':
            date = now + datetime.timedelta(days=1)
        date = date.strftime('%Y%m%d')
        query = f'''
                select menu.date, meal.name as meal_name from ( select * from menu where date >= {date} )
                as menu inner join meal on menu.meal_id = meal.id order by date;
                '''
        df = pd.read_sql(query, db_engine)
        grouped = df.groupby('date', sort=False)
        menu_dict = []
        for date, group in grouped:
            menu_dict.append({'date': date, 'meals': group.meal_name.to_list()})

        if len(menu_dict) == 0:
            reply_json.append(createjson.text("メニューがありません"))
        else:
            reply_json.append(createjson.menu_info(menu_dict))


    elif data_dic['action'] == 'order':
        order_date = data_dic['date']
        meal_id = data_dic['meal_id']
        size = data_dic['size']

        if operation_status == 'am':
            date = now
        elif operation_status == 'pm':
            date = now + datetime.timedelta(days=1)
        date = int(date.strftime('%Y%m%d'))

        if order_date < date:
            reply_json.append(createjson.text("その商品は注文できません。"))
        else:
            menu = s.query(Menu).filter_by(date=order_date, meal_id=meal_id).first()
            if menu:
                count = s.query(Orders).filter_by(date=order_date, meal_id=meal_id, size=size, status=1).count()
                if size == 0:
                    stock = menu.s_stock
                elif size == 1:
                    stock = menu.m_stock
                else:
                    stock = menu.l_stock
                if count < stock:
                    order = s.query(Orders).filter_by(user_id=user_id, date=order_date).first()
                    if order:
                        if order.status == 1:
                            reply_json.append(createjson.text('すでに注文があります。\n注文を変更する場合は現在の注文をキャンセルしてから注文してください。'))
                        else:
                            order.meal_id = meal_id
                            order.size = size
                            order.status = 1
                            s.commit()
                            reply_json.append(createjson.text('ありがとうございます(^o^)\n注文が完了しました'))

                            users = s.query(Users).filter_by(id=user_id, status=1).first()
                            name = line_bot_api.get_profile(user_id).display_name
                            if users:
                                if users.status != 1:
                                    users.status = 1
                                users.name = name
                            else:
                                s.add(Users(id=user_id, name=name))
                            s.commit()

                            profile = s.query(Profile).filter_by(user_id=user_id).first()
                            if profile == None:
                                reply_json.append(createjson.enquete_message())
                                reply_json.append(createjson.enquete_confirm())

                            meal = s.query(Meal).filter_by(id=meal_id).first()
                            notify(f'{name}が『{meal.name} {size_list[size]}』を注文しました')
                    else:
                        order = Orders(user_id=user_id, date=order_date, meal_id=meal_id, size=size)
                        s.add(order)
                        s.commit()
                        reply_json.append(createjson.text('ありがとうございます(^o^)\n注文が完了しました'))

                        users = s.query(Users).filter_by(id=user_id, status=1).first()
                        name = line_bot_api.get_profile(user_id).display_name
                        if users:
                            if users.status != 1:
                                users.status = 1
                            users.name = name
                        else:
                            s.add(Users(id=user_id, name=name))
                        s.commit()

                        profile = s.query(Profile).filter_by(user_id=user_id).first()
                        if profile == None:
                            reply_json.append(createjson.enquete_message())
                            reply_json.append(createjson.enquete_confirm())

                        meal = s.query(Meal).filter_by(id=meal_id).first()
                        notify(f'{name}が『{meal.name} {size_list[size]}』を注文しました')
                else:
                    reply_json.append(createjson.text('売り切れました'))
            else:
                reply_json.append(createjson.text("その商品は注文できません。"))



    elif data_dic['action'] == 'cancelyes':
        date = data_dic['date']
        meal_id = data_dic['meal_id']
        size = data_dic['size']

        orders = s.query(Orders).filter_by(user_id=user_id, date=int(date), meal_id=meal_id, size=size,
                                           status=1).first()
        if orders:
            orders.status = -1
            s.commit()
            reply_json.append(createjson.text("キャンセルが完了しました"))

            user = s.query(Users).filter_by(id=user_id).first()
            meal = s.query(Meal).filter_by(id=meal_id).first()
            notify(f'{user.name}が『{meal.name} {size_list[size]}』をキャンセルしました')
        else:
            reply_json.append(createjson.text("キャンセルできませんでした"))


    elif data_dic['action'] == 'enquete_agree':
        profile = s.query(Profile).filter_by(user_id=user_id).first()
        if profile == None:
            s.add(Profile(user_id=user_id))
            s.commit()
        reply_json.append(createjson.enquete_grade())


    elif data_dic['action'] == 'enquete_disagree':
        reply_json.append(createjson.enquete2_confirm())


    elif data_dic['action'] == 'enquete2_agree':
        profile = s.query(Profile).filter_by(user_id=user_id).first()
        if profile == None:
            s.add(Profile(user_id=user_id))
            s.commit()
        reply_json.append(createjson.text('今後このアンケートは表示しません'))


    elif data_dic['action'] == 'enquete2_disagree':
        reply_json.append(createjson.text('次回注文時に再度アンケートします'))


    elif data_dic['action'] == 'enquete_grade':
        value = data_dic['value']
        profile = s.query(Profile).filter_by(user_id=user_id).first()
        if profile == None:
            s.add(Profile(user_id=user_id, grade=value))
        else:
            profile.grade = value
        s.commit()
        reply_json.append(createjson.enquete_department())

    elif data_dic['action'] == 'enquete_department':
        value = data_dic['value']
        profile = s.query(Profile).filter_by(user_id=user_id).first()
        courselist = settings.department[value]
        if len(courselist) > 1:
            if profile == None:
                s.add(Profile(user_id=user_id, department=value))
            else:
                profile.department = value
            reply_json.append(createjson.enquete_course(courselist))
        else:
            course = courselist[0]
            if profile == None:
                s.add(Profile(user_id=user_id, department=value, course=course))
            else:
                profile.department = value
                profile.course = course
            reply_json.append(createjson.text('ご協力ありがとうございました!'))
            reply_json.append(createjson.coupon())
        s.commit()


    elif data_dic['action'] == 'enquete_course':
        value = data_dic['value']
        profile = s.query(Profile).filter_by(user_id=user_id).first()
        if profile == None:
            s.add(Profile(user_id=user_id, course=value))
        else:
            profile.course = value
        s.commit()
        reply_json.append(createjson.text('ご協力ありがとうございました!'))
        reply_json.append(createjson.coupon())


    else:
        return 0

    data = {'replyToken': event.reply_token, 'messages': reply_json}
    # current_app.logger.info(str(reply_json))
    res = requests.post(reply_url, data=json.dumps(data), headers=headers)
    # print(res.text)  # for error check
    # s.close()
