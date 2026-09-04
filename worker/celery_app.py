# celery_app.py

from celery import Celery

# Redis を使う場合（SUNIE の標準構成）
# broker: タスクを受け取るキュー
# backend: 結果を保存（必要なら）
celery = Celery(
    "sunie_worker",
    broker="redis://redis:6379/0",
    backend="redis://redis:6379/1"
)

# 最小限のタスク
@celery.task
def add(x, y):
    return x + y
