# -*- coding: utf-8 -*-
import requests
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import pandas as pd
import datetime

import settings
from models import *

db_engine = create_engine(settings.db_uri, pool_pre_ping=True)


# python -c "import changerichmenu; changerichmenu.withcancel()"


def withcancel():
    url = f'https://api.line.me/v2/bot/user/all/richmenu/{settings.withcancel_richmenu_id}'
    headers = {
        'Authorization': 'Bearer ' + settings.access_token
    }
    requests.post(url, headers=headers)


def withoutcancel():
    Session = sessionmaker(bind=db_engine)
    s = Session()
    now = datetime.datetime.now()
    date = now.strftime('%Y%m%d')
    menu = s.query(Menu).filter(Menu.date == int(date)).first()
    if menu:
        url = f'https://api.line.me/v2/bot/user/all/richmenu/{settings.withoutcancel_richmenu_id}'
        headers = {
            'Authorization': 'Bearer ' + settings.access_token
        }
        requests.post(url, headers=headers)


def nonenoon():
    url = f'https://api.line.me/v2/bot/user/all/richmenu/{settings.none_richmenu_id}'
    headers = {
        'Authorization': 'Bearer ' + settings.access_token
    }
    requests.post(url, headers=headers)

    Session = sessionmaker(bind=db_engine)
    s = Session()
    now = datetime.datetime.now()
    date = now.strftime('%Y%m%d')
    menu = s.query(Menu).filter(Menu.date == int(date)).first()
    if menu:
        orders = s.query(Orders).filter(Orders.status == 1).all()
        for row in orders:
            row.status = 0
        s.commit()


def nonenight():
    url = f'https://api.line.me/v2/bot/user/all/richmenu/{settings.none_richmenu_id}'
    headers = {
        'Authorization': 'Bearer ' + settings.access_token
    }
    requests.post(url, headers=headers)

    Session = sessionmaker(bind=db_engine)
    s = Session()
    now = datetime.datetime.now()
    date = now + datetime.timedelta(days=1)
    date = date.strftime('%Y%m%d')
    menu = s.query(Menu).filter(Menu.date == int(date)).all()
    if len(menu) > 0:
        query = f'''
                select orders.meal_id, orders.size, sum(count) as count from ( select meal_id, size, count from orders
                where date = {date} and status != -1) as orders group by orders.meal_id, orders.size;
                '''
        count = pd.read_sql(query, db_engine)
        for row in menu:
            id = row.meal_id
            try:
                row.s_stock = int(count[(count['meal_id'] == id) & (count['size'] == 0)]['count'].values[0])
            except:
                row.s_stock = 0
            try:
                row.m_stock = int(count[(count['meal_id'] == id) & (count['size'] == 1)]['count'].values[0])
            except:
                row.m_stock = 0
            try:
                row.l_stock = int(count[(count['meal_id'] == id) & (count['size'] == 2)]['count'].values[0])
            except:
                row.l_stock = 0
        s.commit()


def upgrade():
    Session = sessionmaker(bind=db_engine)
    s = Session()
    profile = s.query(Profile).filter(Profile.grade > 0).all()
    for row in profile:
        row.grade=row.grade+1
    s.commit()


if __name__ == '__main__':
    withcancel()
