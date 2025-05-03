# coding: utf-8




# 既成のモジュールをインポートする.
import os
import sys

# 設定のためのモジュールをインポートする.
import constants as consts




# Flask, SQLAlchemy等の主要なモジュールの構成・設定情報を宣言・定義する.
DEBUG = True
HOST = "localhost"
PORT = 5000
SECRET_KEY = "python-flask-application__session-secret-key"
SQLALCHEMY_DATABASE_URI = f'sqlite:///{consts.BASE_DIR}/app.db?charset=utf8'
SQLALCHEMY_TRACK_MODIFICATIONS = False