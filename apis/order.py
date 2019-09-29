from flask import abort, session
from flask_restplus import Namespace, fields, Resource
from sqlalchemy import create_engine
import pandas as pd

import settings
from models import db, Orders,Meal

db_engine = create_engine(settings.db_uri, pool_pre_ping=True)

namespace = Namespace('order', description='注文関連のエンドポイント')

@namespace.route('/<int:date>/<string:user_id>')
class OrderController(Resource):
    # @namespace.marshal_with(order_spec)
    def get(self, date, user_id):
        users=user_id.split('&')
        query = f'''
                select orders.date, orders.user_id, users.name as user_name, orders.meal_id, meal.name as meal_name,
                orders.size, orders.timestamp, meal.s_price, meal.m_price, meal.l_price
                from (select * from orders where date = {date} and  status != -1) as orders inner join
                users on orders.user_id = users.id inner join meal on orders.meal_id = meal.id
                '''
        df = pd.read_sql(query, db_engine)
        df=df[df['user_id'].isin(users)]
        df.loc[df['size'] == 0, 'price'] = df['s_price']
        df.loc[df['size'] == 1, 'price'] = df['m_price']
        df.loc[df['size'] == 2, 'price'] = df['l_price']
        del df['s_price']
        del df['m_price']
        del df['l_price']
        df['price'] = df['price'].astype(int)

        return df.to_dict(orient='records')