# ベースイメージ（必要に応じて Python バージョン変更）
FROM python:3.11-slim

# 環境変数
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# 作業ディレクトリ
WORKDIR /app

# 必要なシステムパッケージ（SQLite は標準で入っていることが多いが、念のため）
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        sqlite3 \
    && rm -rf /var/lib/apt/lists/*

# 依存関係のコピー＆インストール
# requirements.txt 例：
# streamlit
# sqlalchemy
# aiosqlite など
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# アプリ本体をコピー
COPY . /app

# ポート指定（Streamlit のデフォルトは 8501）
EXPOSE 8501

# Streamlit の設定（コンテナ内から外部アクセスを許可）
# app.py が Streamlit アプリのエントリポイントだと仮定
CMD ["streamlit", "run", "app.py", "--server.address=0.0.0.0"]
