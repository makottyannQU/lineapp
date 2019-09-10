# coding:utf8
from flask import Flask
from models import db
from views.client import blueprint as client
from views.host import blueprint as host
import settings

app = Flask(__name__)
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
