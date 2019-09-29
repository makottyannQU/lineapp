# -*- coding: utf-8 -*-
from flask import Flask, request, abort, redirect, render_template, url_for, Blueprint, send_from_directory
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
# import psycopg2  # for psql in heroku

import settings
from models import *

blueprint = Blueprint('host', __name__, url_prefix='/', static_folder='/views/static',
                      template_folder='/views/templates')

db_engine = create_engine(settings.db_uri, pool_pre_ping=True)

line_bot_api = LineBotApi(settings.access_token)
handler = WebhookHandler(settings.secret_key)

defalt_stock = 100


def operation():
    now = datetime.datetime.now().time()
    for time in settings.operationtime:
        if now < time[0]:
            return time[1]
    return 'non'


@blueprint.route('/')
def index():
    return render_template('index.html', error=0)


@blueprint.route('/menu')
def menu():
    try:
        date = request.args['date']
        query = f'''
                    select menu.date, "meal".name  from ( select * from "menu" where date = {date})
                    as menu inner join "meal" on menu.meal_id = "meal".id;
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
        # print('DB登録開始')
        try:
            date = request.form['date']
            meals = request.form.getlist('meal')
            select = request.form.getlist('check_meal')
        except:
            # return redirect(url_for('index', error=1, date=date))
            return render_template('index.html', error=1)
        if len(set(meals)) != len(meals):
            # return redirect(url_for('index', error=1, date=date))
            return render_template('index.html', error=1)
        menus = []
        for i in range(len(meals)):
            # print(meals)
            # print(select)

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
                    menus.append(Menu(date=int(
                        date), meal_id=meals[i], s_stock=s_stock, m_stock=m_stock, l_stock=l_stock))
        db.session.add_all(menus)
        db.session.commit()
        return render_template('index.html', error=0)
    else:
        return render_template('addmenu.html')


@blueprint.route('/editmenu', methods=['GET', 'POST'])
def editmenu():
    if request.method == 'POST':
        # print('DB登録開始(メニュー変更開始)))')

        date = request.form['date']
        menu_count = int(request.form['menu_count'])
        data_for_DB = []
        temp_list = []
        temp_stock_list = []
        # print(request.form)
        # print(date)

        query = f'''
                select * from menu where date = {date};
                '''
        menu_df = pd.read_sql(query, db_engine)
        if len(menu_df) > 0:
            query = f'''
                    select orders.meal_id, orders.size, sum(count) as count from ( select meal_id, size, count from orders
                    where date = {date} and status != -1) as orders group by orders.meal_id, orders.size;
                    '''
            df = pd.read_sql(query, db_engine)
            ordernum = {}
            for index, row in menu_df.iterrows():
                id = row.meal_id
                tmp = df[df['meal_id'] == id]
                if len(tmp) > 0:
                    try:
                        s_count = tmp[tmp['size'] == 0]['count'].iloc[0]
                    except:
                        s_count = 0
                    try:
                        m_count = tmp[tmp['size'] == 1]['count'].iloc[0]
                    except:
                        m_count = 0
                    try:
                        l_count = tmp[tmp['size'] == 2]['count'].iloc[0]
                    except:
                        l_count = 0
                else:
                    s_count = 0
                    m_count = 0
                    l_count = 0
                ordernum[id] = {'s_count': s_count, 'm_count': m_count, 'l_count': l_count, 's_stock': row.s_stock,
                                'm_stock': row.m_stock, 'l_stock': row.l_stock}
        else:
            return render_template('index.html', error=1)

        for i in range(menu_count):
            # temp_stock_list.clear()
            # temp_list.clear()
            # temp_stock_list.append(request.form['S_stock'+str(i+1)])
            # temp_stock_list.append(request.form['M_stock'+str(i+1)])
            # temp_stock_list.append(request.form['L_stock' + str(i + 1)])
            # temp_list.append(request.form['edit_meal'+str(i+1)])
            # temp_list.append(temp_stock_list)
            MEAL_ID = request.form['edit_meal' + str(i + 1)]
            S_STOCK = request.form['S_stock' + str(i + 1)]
            M_STOCK = request.form['M_stock' + str(i + 1)]
            L_STOCK = request.form['L_stock' + str(i + 1)]
            try:
                count = ordernum[MEAL_ID]
                if (int(S_STOCK) < count['s_count']):
                    return render_template('index.html', error=1)
                if (int(M_STOCK) < count['m_count']):
                    return render_template('index.html', error=1)
                if (int(L_STOCK) < count['l_count']):
                    return render_template('index.html', error=1)
            except:
                pass

            data_for_DB.append(Menu(date=int(
                date), meal_id=MEAL_ID, s_stock=S_STOCK, m_stock=M_STOCK, l_stock=L_STOCK))
        # 変更のため元のデータを削除する
        selected_records = db.session.query(Menu).filter(
            Menu.date == int(date))  # .all() は省略可
        for x in selected_records:
            db.session.delete(x)
        db.session.add_all(data_for_DB)
        db.session.commit()
        # print(data_for_DB)

        return render_template('index.html', error=0)
    else:
        return render_template('edit.html')


@blueprint.route('/member')
def member():
    query = f'''
            select orders.date, users.id, users.name, profile.name as fullname, profile.grade, profile.department, profile.course,
            profile.club from (select user_id, max(date) as date from orders group by user_id ) as orders
            inner join users on orders.user_id = users.id
            left outer join profile on orders.user_id = profile.user_id order by date desc;
            '''
    df = pd.read_sql(query, db_engine)
    df['grade']=df['grade'].fillna(-1).astype(int).replace(-1, 'None')
    profile = df.to_dict(orient='records')
    return render_template('member.html', profile=profile)


@blueprint.route('/meal')
def meal():
    query = f'select * from meal;'
    df = pd.read_sql(query, db_engine)
    data = df.to_dict(orient='records')
    return render_template('meal.html', data=data)


@blueprint.route('/editmeal', methods=['GET', 'POST'])
def editmeal():
    if request.method == 'POST':
        # print('DB登録開始(弁当編集)))')
        id_of_meal = request.form['id']
        name = request.form['name']
        s_price = int(request.form['s_price'])
        m_price = int(request.form['m_price'])
        l_price = int(request.form['l_price'])

        # print(id_of_meal)
        # print(name)
        # print(s_price)
        # print(m_price)
        # print(l_price)

        # 変更のためセレクトされたmealレコードを抽出する
        selected_meal_record = db.session.query(Meal).filter(
            Meal.id == id_of_meal).first()
        # 更新  
        selected_meal_record.name = name
        selected_meal_record.s_price = s_price
        selected_meal_record.m_price = m_price
        selected_meal_record.l_price = l_price
        try:
            image = request.files['image']
            if 'image' in image.content_type:
                id = str(uuid4())
                path = f'upload/{id}.png'
                image.save(path)
                selected_meal_record.image = path
        except:
            pass
        db.session.commit()

        return render_template('index.html', error=0)
    else:
        # print('弁当編集ページ')
        meal_data = []
        # print(request.args.get("id"))
        meal_id = request.args.get("id")
        selected_meal = db.session.query(
            Meal).filter(Meal.id == meal_id).all()
        # print(selected_meal[0].name)
        # for x in selected_meal:
        #     print(x.name)
        return render_template('editmeal.html', selected_meal=selected_meal[0])


@blueprint.route('/deletemeal', methods=['GET'])
def deletemeal():
    meal_id = request.args.get("id")
    db.session.query(Meal).filter(Meal.id == meal_id).delete()
    db.session.commit()
    return render_template('index.html', error=0)


@blueprint.route('/look_in_DB')
def look_in_DB():
    query = f'select * from meal;'
    df = pd.read_sql(query, db_engine)
    meals = df.to_dict(orient='records')
    query = f'select * from menu;'
    df = pd.read_sql(query, db_engine)
    menu = df.to_dict(orient='records')
    query = f'select * from orders;'
    df = pd.read_sql(query, db_engine)
    orders = df.to_dict(orient='records')
    query = f'select * from users;'
    df = pd.read_sql(query, db_engine)
    users = df.to_dict(orient='records')

    return render_template('look_in_DB.html', meals=meals, menu=menu, orders=orders, users=users)


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
        return render_template('index.html', error=0)
    else:
        return render_template('addmeal.html')


@blueprint.route('/ordercheck')
def ordercheck():
    col_max = 10
    size_list = ['小盛', '並盛', '大盛']
    query = f'''
            select s1.date, meal.name as meal_name, s1.size, users.name as user_name from (select * from orders where status = 1) as s1 inner join
            ( select max(date) as date from orders where status = 1 ) as s2 on s1.date = s2.date
            inner join users on s1.user_id = users.id inner join meal on s1.meal_id = meal.id order by s1.timestamp;
            '''
    df = pd.read_sql(query, db_engine)
    if len(df) == 0:
        return render_template('no_order_view.html')
    else:
        date = str(df.date[0])
        date = date[0:4] + '年' + date[4:6] + '月' + date[6:8] + '日'
        ordercheck_dict = []
        meal_grouped = df.groupby('meal_name', sort=False)
        for meal_name, meal_group in meal_grouped:
            num = 0
            num2 = 0
            meal_group = meal_group.sort_values('size')
            size_grouped = meal_group.groupby('size', sort=False)
            tmp = []
            for size, size_group in size_grouped:
                l = size_group.user_name.to_list()
                tmp2 = []
                for i in range(0, len(l), col_max):
                    tmp2.append(l[i:i + col_max])
                for i in range(col_max - len(tmp2[-1])):
                    tmp2[-1].append('')
                num += len(l)
                num2 += len(tmp2)
                tmp.append({'size': size_list[size], 'num': len(l), 'span': len(tmp2), 'member': tmp2})
            ordercheck_dict.append({'meal_name': meal_name, 'num': num, 'span': num2, 'each_size': tmp})
    return render_template('ordercheck.html', date=date, orders=ordercheck_dict)


@blueprint.route('/update_calendar', methods=['POST'])
def update_calendar():
    year = int(request.form['year'])
    month = int(request.form['month'])
    holiday = [str(x[0].day) for x in jpholiday.month_holidays(year, month)]
    ym = f'{year:04d}{month:02d}'
    query = f'''
            select menu.date, meal.name,menu.meal_id, menu.s_stock,menu.m_stock ,menu.l_stock from ( select * from menu where date between {ym}00 and {ym}32)
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
        menus.append({"day": day, "title": menu, "meal_id": row["meal_id"], "s_orders": 0, "m_orders": 0, "l_orders": 0,
                      "s_stock": row["s_stock"], "m_stock": row["m_stock"], "l_stock": row["l_stock"], "type": type})

    dict = {
        "year": year,
        "month": month,
        "event": menus,
        "holiday": holiday
    }

    # 　orderテーブル
    order_check_list = []
    # order_check_count_dict = {}
    # for i in range(1, 31):
    # order_check_count_dict[i] = {}
    # for x in menus:
    # print(x['meal_id'])
    # order_check_count_dict[int(x['day'])][x['meal_id']] = [0,0,0]
    temp = 0
    query = f'''
            select * from orders where status != -1 and date between {ym}00 and {ym}32 ORDER BY date ASC
            '''
    df = pd.read_sql(query, db_engine)
    # print(df)
    # print(order_check_count_dict)
    for index, row in df.iterrows():
        day = int(str(row['date'])[-2:])
        meal_id = row['meal_id']

        if row['size'] == 0:
            # order_check_count_dict[day][row['meal_id']][0] += 1
            for y in dict['event']:
                if int(y['day']) == day and y['meal_id'] == meal_id:
                    y['s_orders'] += row['count']
        elif row['size'] == 1:
            # order_check_count_dict[day][row['meal_id']][1] += 1
            for y in dict['event']:
                if int(y['day']) == day and y['meal_id'] == meal_id:
                    y['m_orders'] += row['count']
                    # print('addorder')
        elif row['size'] == 2:
            # order_check_count_dict[day][row['meal_id']][2] += 1
            for y in dict['event']:
                if int(y['day']) == day and y['meal_id'] == meal_id:
                    y['l_orders'] += row['count']
        else:
            # print('sizeエラー')
            pass
        if temp != day:
            order_check_list.append(day)
        temp = day
        # order_check_count_dict[day].append({})
        # order_check_count_dict[day] +=1

    dict['order_check_list'] = order_check_list
    # dict['order_check_count_dict'] = order_check_count_dict
    # print(order_check_list)
    # print(order_check_count_dict)

    return json.dumps(dict, ensure_ascii=False)


@blueprint.route('/get_meals', methods=['GET'])
def get_meals():
    query = f'select * from meal;'
    df = pd.read_sql(query, db_engine)
    meals = df.to_dict(orient='records')
    return json.dumps(meals, ensure_ascii=False)


@blueprint.route('/upload/<string:path>')
def upload(path):
    return send_from_directory('../upload', path)
