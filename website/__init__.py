from flask import Flask
from dotenv import load_dotenv
from flask_pymongo import PyMongo
import os
import logging

conn = PyMongo()

def create_app():
    load_dotenv()

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
    )
    log = logging.getLogger(__name__)

    app = Flask(__name__)
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
    app.config['MONGO_URI'] = os.getenv('MONGO_URI')
    app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024
    conn.init_app(app)

    if conn is not None:
        log.info("Successful connection to MongoDB Atlas")
    else:
        log.error("Not connected to MongoDB Atlas")

    from .views import views

    app.register_blueprint(views, url_prefix='/')

    return app