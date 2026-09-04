FROM python:3.11-slim

WORKDIR /app

# worker ディレクトリに requirements.txt を置く
COPY worker/requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

# worker のコード
COPY worker .

CMD ["celery", "-A", "celery_app.celery", "worker", "--loglevel=INFO"]
