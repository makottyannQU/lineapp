from flask_restplus import Namespace, Resource
from sqlalchemy import create_engine
import pandas as pd

import settings

db_engine = create_engine(settings.db_uri, pool_pre_ping=True)

namespace = Namespace('menu', description='メニュー関連のエンドポイント')


@namespace.route('/<int:date>')
class MenuController(Resource):
    def get(self, date):
        query = f'''
        select meal.name from (select * from menu where date = {date}) as menu inner join meal on menu.meal_id = meal.id
                '''
        df = pd.read_sql(query, db_engine)

        return df.to_dict(orient='records')
