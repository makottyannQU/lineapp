from flask import session
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from uuid import uuid4
import pandas as pd
# import psycopg2  # for psql in heroku
import pymysql

import settings
from models import *

db_engine = create_engine(settings.db_uri, pool_pre_ping=True)
Session = sessionmaker(bind=db_engine)
s = Session()


# # print a table
# query = f'''
#         select * from meal;
#         '''
# df = pd.read_sql(query, db_engine)
# print(df)


# # print a row
# users=s.query(Users).filter_by(id == 'U6c8f1bb0cfb39e08bb5052f6d6fb632d').first()
# print(users)


# # add a row
# id=str(uuid4())
# meal = Meal(id=id, name='チキン南蛮',image=f'image/{id}.png',price=300)
# s.add(meal)
# s.commit()


# # delete a row
# s.query(Users).filter(Users.id == 'U6c8f1bb0cfb39e08bb5052f6d6fb632d').delete()
# s.commit()


# # marge tables users,meal,orders
# user_id='U6c8f1bb0cfb39e08bb5052f6d6fb632d'
# query = f'''
#         select order1.date, users.name, meal.name, meal.price  from ( select * from orders where user_id = '{user_id}' )
#         as order1 inner join meal on order1.meal_id = meal.id inner join users on order1.user_id = users.id ;
#         '''
# df = pd.read_sql(query, db_engine)
# print(df)

