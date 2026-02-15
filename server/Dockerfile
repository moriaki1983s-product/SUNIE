FROM python:3.11-slim

# Graphviz や因果系ライブラリのための最低限の依存
RUN apt-get update && apt-get install -y --no-install-recommends \
    graphviz \
    build-essential \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 5000

# FastAPI なら uvicorn、Flask なら python app.py
# app.py 内で FastAPI or Flask を切り替える構成でも対応可能
CMD ["python", "app.py"]
