# Development Process Guide  
SUNIE / LUMIE

このドキュメントは、SUNIE / LUMIE をフォークして開発に参加する人のための  
**標準的な開発プロセス**をまとめたものです。

本プロジェクトは、Client（UI）・Server（API）・Worker（非同期処理）の  
三位一体構造で動作します。  
まずは OS ネイティブでの開発を行い、その後 Docker で本番想定の動作確認を行います。

---

# 1. 開発環境の前提

- Python 3.10+  
- pip / venv  
- Redis または RabbitMQ（Celery 用）  
- Git / GitHub  
- Docker / Docker Compose（後半で使用）

---

# 2. プロジェクト構造（概要）


---

# 3. 開発プロセス（推奨フロー）

## Step 1. OS ネイティブで 3 役を実装する

まずは Docker を使わず、  
**ローカル環境で Client / Server / Worker を単体で動かせる状態**を作ります。

### Client（Streamlit）

この段階では、  
- UI が動く  
- API が応答する  
- Worker がタスクを処理する  
という **基本的な流れが成立していれば OK** です。

---

## Step 2. bat ファイルで起動を自動化する（Windows）

開発効率を上げるため、  
`scripts/` に以下のような bat ファイルを用意します。

### run_client.bat

これにより、  
**ワンクリックで各コンポーネントを起動できる**ようになります。

---

## Step 3. 機能が揃ったら Docker 化する

OS ネイティブで動作が安定したら、  
次に Docker 上で 3 役を連携させます。

### client/Dockerfile  
### server/Dockerfile  
### worker/Dockerfile  
を用意し、ルートに `docker-compose.yml` を配置します。

### docker-compose.yml（例）

これで、  
**本番環境に近い構成での動作確認が可能**になります。

---

# 4. 開発の考え方（重要）

SUNIE / LUMIE の開発では、以下を重視します。

### ✔ 小さく作り、早く動かす  
まず OS ネイティブで動くものを作り、  
Docker 化は後半に回します。

### ✔ 概念の整合性を優先  
Client / Server / Worker の役割が明確であること。

### ✔ 本番を意識した構造  
Docker 化は「仕上げ」であり、  
本番環境への移行をスムーズにします。

---

# 5. よくある質問（FAQ）

### Q. いきなり Docker で開発してもいいですか？  
A. 推奨しません。  
初期段階で Docker を使うと、  
ビルド時間やログの見づらさで開発速度が落ちます。

### Q. Worker は必須ですか？  
A. 非同期処理（学習・推論など）を扱う場合は必須です。

### Q. Redis と RabbitMQ のどちらを使うべきですか？  
A. 開発は Redis、本番は RabbitMQ を推奨します。

---

# 6. 最後に

SUNIE / LUMIE は、  
**「学習・推論・意味構造の再設計」**を目指すプロジェクトです。

この開発プロセスは、  
あなたがスムーズに参加し、  
同じリズムで開発できるように設計されています。

あなたの貢献を歓迎します。
