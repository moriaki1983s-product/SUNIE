FROM python:3.11-slim

WORKDIR /app

COPY ../server/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY ../server .

CMD ["celery", "-A", "celery_app.celery", "worker", "--loglevel=INFO"]
