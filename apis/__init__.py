# coding:utf8
from flask import Blueprint
from flask_restplus import Api

from .order import namespace as order_namespace

blueprint = Blueprint('api', __name__)

api = Api(
    app=blueprint,
    title='lineapp API',
    version='0.1',
    description='REST API',
    # doc='/doc/'
)

api.add_namespace(order_namespace)