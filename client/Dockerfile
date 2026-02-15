FROM python:3.11-slim

# 必要な OS パッケージ（Graphviz が必要な場合に備えて）
RUN apt-get update && apt-get install -y --no-install-recommends \
    graphviz \
    build-essential \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# 先に requirements.txt をコピーしてキャッシュを効かせる
COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

# アプリ本体をコピー
COPY . .

EXPOSE 8501

CMD ["streamlit", "run", "app.py", "--server.address=0.0.0.0"]
