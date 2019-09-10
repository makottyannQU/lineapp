# -*- coding: utf-8 -*-
from flask import Flask, request, abort, redirect, render_template, url_for, Blueprint
import pandas as pd
import pymysql
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import numpy as np
import datetime
import json
from uuid import uuid4
import os
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage, FollowEvent, UnfollowEvent
import jpholiday
import psycopg2  # for psql in heroku

import settings
from models import *

blueprint = Blueprint('host', __name__, url_prefix='/', static_folder='/views/static',
                      template_folder='/views/templates')

db_engine = create_engine(settings.db_uri, pool_pre_ping=True)

line_bot_api = LineBotApi(settings.access_token)
handler = WebhookHandler(settings.secret_key)

defalt_stock = 100

def operation():
    now=datetime.datetime.now().time()
    for time in settings.operationtime:
        if now<time[0]:
            return time[1]
    return 'non'


@blueprint.route('/')
def index():
    return render_template('index.html')


@blueprint.route('/menu')
def menu():
    try:
        date = request.args['date']
        query = f'''
                    select menu.date, meal.name  from ( select * from menu where date = {date})
                    as menu inner join meal on menu.meal_id = meal.id;
                    '''
        df = pd.read_sql(query, db_engine)
        menus = df.to_dict(orient='records')
    except:
        return render_template('index.html')

    if len(menus) > 0:
        return render_template('editmenu.html', menus=menus, date=date)
    else:
        return render_template('addmenu.html', date=date)


@blueprint.route('/addmenu', methods=['GET', 'POST'])
def addmenu():
    if request.method == 'POST':
        print('DB登録開始')
        try:
            date = request.form['date']
            meals = request.form.getlist('meal')
            select = request.form.getlist('check_meal')
        except:
            return render_template('addmenu.html', error='正しく入力してください', date=date)
        if len(set(meals)) != len(meals):
            return render_template('addmenu.html', error='正しく入力してください', date=date)
        menus = []
        for i in range(len(meals)):
            print(meals)
            print(select)

            if len(meals[i]) > 0:
                tmp = []
                for s in select:
                    if str(i + 1) == s[-1]:
                        tmp.append(s[0])
                if 's' in tmp:
                    s_stock = defalt_stock
                else:
                    s_stock = 0
                if 'm' in tmp:
                    m_stock = defalt_stock
                else:
                    m_stock = 0
                if 'l' in tmp:
                    l_stock = defalt_stock
                else:
                    l_stock = 0
                if s_stock + m_stock + l_stock > 0:
                    menus.blueprintend(Menu(date=int(
                        date), meal_id=meals[i], s_stock=s_stock, m_stock=m_stock, l_stock=l_stock))
        db.session.add_all(menus)
        db.session.commit()
        return redirect(url_for('index'))
    else:
        return render_template('addmenu.html')


@blueprint.route('/member')
def member():
    query = f'select * from profile;'
    df = pd.read_sql(query, db_engine)
    profile = df.to_dict(orient='records')
    return render_template('member.html', profile=profile)


@blueprint.route('/meal')
def meal():
    query = f'select * from meal;'
    df = pd.read_sql(query, db_engine)
    data = df.to_dict(orient='records')
    return render_template('meal.html', data=data)


@blueprint.route('/look_in_DB')
def look_in_DB():
    query = f'select * from meal;'
    df = pd.read_sql(query, db_engine)
    meals = df.to_dict(orient='records')
    query = f'select * from menu;'
    df = pd.read_sql(query, db_engine)
    menu = df.to_dict(orient='records')

    return render_template('look_in_DB.html', meals=meals, menu=menu)


@blueprint.route('/addmeal', methods=['GET', 'POST'])
def addmeal():
    if request.method == 'POST':
        try:
            name = request.form['name']
            s_price = int(request.form['s_price'])
            m_price = int(request.form['m_price'])
            l_price = int(request.form['l_price'])
            image = request.files['image']
        except:
            return render_template('addmeal.html', error='正しく入力してください')
        id = str(uuid4())
        path = f'upload/{id}.png'
        image.save(path)
        meal = Meal(id=id, name=name, image=path, s_price=s_price,
                    m_price=m_price, l_price=l_price)
        db.session.add(meal)
        db.session.commit()
        return redirect(url_for('meal'))
    else:
        return render_template('addmeal.html')


@blueprint.route('/editmeal', methods=['GET', 'POST'])
def editmeal():
    if request.method == 'POST':

        return redirect(url_for('meal'))
    else:
        return render_template('addmeal.html')


@blueprint.route('/ordercheck')
def ordercheck():
    return render_template('ordercheck.html')


@blueprint.route('/update_calendar', methods=['POST'])
def update_calendar():
    year = int(request.form['year'])
    month = int(request.form['month'])
    holiday = [str(x[0].day) for x in jpholiday.month_holidays(year, month)]
    ym = f'{year:04d}{month:02d}'
    query = f'''
            select menu.date, meal.name  from ( select * from menu where date between {ym}00 and {ym}32)
            as menu inner join meal on menu.meal_id = meal.id;
            '''
    df = pd.read_sql(query, db_engine)
    menus = []
    for index, row in df.iterrows():
        day = str(int(str(row['date'])[-2:]))
        menu = row['name']
        if '丼' in menu:
            type = 'green'
        else:
            type = 'red'
        menus.append({"day": day, "title": menu, "type": type})

    dict = {
        "year": year,
        "month": month,
        "event": menus,
        "holiday": holiday
    }

    return json.dumps(dict, ensure_ascii=False)


@blueprint.route('/get_meals', methods=['GET'])
def get_meals():
    query = f'select * from meal;'
    df = pd.read_sql(query, db_engine)
    meals = df.to_dict(orient='records')
    return json.dumps(meals, ensure_ascii=False)
