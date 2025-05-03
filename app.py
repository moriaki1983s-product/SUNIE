# coding: utf-8




# 既成のモジュールをインポートする.
import os
import sys
import logging
from logging.handlers import RotatingFileHandler
from flask import (
    Flask,
    render_template
)
from datetime import timedelta
from flask_sqlalchemy import SQLAlchemy
from flask_talisman import Talisman
from werkzeug.exceptions import HTTPException

# 設定のためのモジュールをインポートする.
import constants as consts

# TensorFlowが, oneDNNのカスタムオペレーションを使用しないように設定する.
# GPU非搭載マシン上でのTensorFlowからのメッセージ出力抑止のために実施する.
os.environ["TF_ENABLE_ONEDNN_OPTS"] = "0"


# Flaskの本体を構築する.
app = Flask(__name__, static_folder="resources", template_folder="templates")

# URLの末尾スラッシュの有無を無視するように設定する.
# ※本来は, スラッシュ無がリソース, スラッシュ有がディレクトリと識別される.
app.url_map.strict_slashes = False

# loggingを設定・構成する.
handler = RotatingFileHandler(consts.LOGGING_PATH, maxBytes=consts.LOGGING_LENGTH, backupCount=1)
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)

# Flaskとloggingを連携させて, ログレベルを設定する.
app.logger.addHandler(handler)
app.logger.setLevel(logging.ERROR)

# HTTP例外(=クライアント側起因のエラー)のエラーハンドラー(=エラー処理関数)を宣言・定義する.
def http_exception_handler(e):
    app.logger.error("view at /http_error")
    return render_template("http_error.html",
                           code=e.code, name=e.name,
                           description=e.description, background_image=consts.ERROR_IMAGE_PATH), e.code

# Flaskに設定情報を読み込ませる.
app.config.from_object("configurations")

# 外部ファイルで定義したビュー関数群をインポートする.
from views import view

# インポートしたビュー関数群をFlaskに登録する.
app.register_blueprint(view)

# Flaskにカスタムエラーハンドラー(=エラー処理関数)を登録する.
app.register_error_handler(HTTPException, http_exception_handler)

# Flaskアプリにおけるセッション持続時間を設定する.
app.permanent_session_lifetime = timedelta(minutes=consts.SESSION_TIME)

# FlaskとTalismanを連携させる.
Talisman(app, content_security_policy=consts.CSP, force_https=consts.FORCE_HTTPS)

# FlaskとSQLAlchemyを連携させる.
db = SQLAlchemy(app)

# データベースを構築する.
with app.app_context():
     db.create_all()


# 当該モジュールが実行起点かどうかを確認した上でFlask本体を起動する.
if __name__ == "__main__":
    app.run()