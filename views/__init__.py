# coding:utf8
from flask import Flask
from logging import DEBUG
from logging.config import dictConfig
from models import db
from views.client import blueprint as client
from views.host import blueprint as host
import settings

dictConfig({
    'version': 1,  # ?
    'formatters': {
        'default': {'format': '[%(asctime)s] %(levelname)s in %(module)s: %(message)s'},
        'myformatter': {'format': '%(asctime)s %(levelname)8s %(filename)s:L%(lineno)d: %(message)s'},
    },
    'handlers': {
        'wsgi': {
            'class': 'logging.StreamHandler',
            'stream': 'ext://flask.logging.wsgi_errors_stream',
            # 'formatter': 'default'
            'formatter': 'myformatter'
        },
        'file': {
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': 'logs/debug.log',
            'formatter': 'myformatter',
            'maxBytes': 1024 * 1024,
            'backupCount': 10,
        },
    },
    'root': {
        'level': 'DEBUG',
        # 'handlers': ['wsgi', 'file'],
        'handlers': ['file'],
    },
})

app = Flask(__name__)
app.logger.setLevel(DEBUG)
app.config['JSON_AS_ASCII'] = settings.JSON_AS_ASCII
app.config['SQLALCHEMY_DATABASE_URI'] = settings.SQLALCHEMY_DATABASE_URI
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = settings.SQLALCHEMY_TRACK_MODIFICATIONS
app.config['SWAGGER_UI_DOC_EXPANSION'] = settings.SWAGGER_UI_DOC_EXPANSION
app.config['RESTPLUS_VALIDATE'] = settings.RESTPLUS_VALIDATE
app.config['UPLOADED_CONTENT_DIR'] = settings.UPLOADED_CONTENT_DIR


with app.app_context():
    db.init_app(app)
    # db.drop_all()  # Remove on release
    db.create_all()

app.register_blueprint(client)
app.register_blueprint(host)
