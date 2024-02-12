from flask import Flask
from pymongo import MongoClient
from dotenv import load_dotenv
from flask_pymongo import PyMongo
import os

conn = PyMongo()

def create_app():
    load_dotenv()

    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'KitzuNash120cjweskm'
    app.config['MONGO_URI'] = os.getenv('MONGO_URI')
    app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024
    conn.init_app(app)

    from .views import views
    from .auth import auth

    app.register_blueprint(views, url_prefix='/')
    app.register_blueprint(auth, url_prefix='/')


    return app