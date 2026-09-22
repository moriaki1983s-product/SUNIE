![SUNIE-LOGO](./logo.jpg)


SUNIE – AI Web Application for Education (Client & Server)

System Architecture of This Project (SUNIE-System)

Technology Stack & Overall Data Flow

Client (Streamlit) ←→ SQLite
⇅
Nginx
⇅
Server (Flask) ←→ PostgreSQL / Memgraph
⇅
──────────── System-Core ────────────
Celery
↓
Redis / RedisQueue
⇅
Celery Worker ←→ PostgreSQL / Memgraph

Detailed Control & Data Flow

Client (Streamlit) ←→ Nginx ←→
Server (Flask + gunicorn) ←→ PostgreSQL / Memgraph

Client (Streamlit) ←→ Nginx ←→
Server (Flask + gunicorn) ←→ System-Core  
※ System-Core =
Celery → RedisQueue ←→ Celery Worker ←→
PostgreSQL / Memgraph

Route ① represents the DB access path from the perspective of the Server (dashboard).
Route ② represents the DB access path associated with task execution from the perspective of Celery Workers.

Purpose and Role of Each Technology
Client (Streamlit) — Web UI / Web UX (Frontend)
Nginx — Asynchronous web server
Server (Flask + gunicorn) — API & dashboard (Backend)
RedisQueue — Message queue (task request management)
Celery — Task worker generation and management
PostgreSQL — Database specialized for learning and login history
Memgraph — Database specialized for educational material graph search

Reasons for Technology Selection
Technologies such as Nginx, Redis, RedisQueue, Celery, PostgreSQL, and Memgraph were chosen with future scalability and increased user volume in mind.
The use of gunicorn is a natural consequence of adopting Flask as the backend.

Particularly, Client (Streamlit) and Server (Flask + gunicorn) were selected because:

Both frontend and backend can be implemented entirely in Python, which is already widely used in Japanese public-school information science curricula.

This makes the system easier to pass through the review processes of local Boards of Education across Japan.

Core Principle of This Project (SUNIE-Architecture)
The “heart” of this project—the Celery-based inference worker—is a hybrid system combining rule-based logic and neural networks (LLM).

Hybrid AI Co-Worker (SUNIE / LUMIE System)
Start
—---------------------
↓
↓
Input Validation Layer  
Eliminates meaningless, inappropriate, or system-disruptive input
↓
↓
Input Encoding Layer (Natural Language Ambiguity Processing)  
Transforms ambiguous natural language (Gödel encoding, Cantor encoding, etc.)
Extracts user intent
Generates structured requests for the core
↓
↓
Simulation & Inference Core (Structured Execution of Simulation & Reasoning)  
Adjusts rotary mechanisms based on LLM-driven estimation of user psychology
Selects conceptual data and processing code based on rotary results
Graph-based search and retrieval of conceptual data
Relational search and retrieval of conceptual data processing code
Validity and soundness verification of conceptual data
Safety verification of conceptual data processing code
Constructs Gödelian & Cantorian chains (simulation & inference)
Executes Gödelian & Cantorian chains
Records audit logs in relational storage
Generates structured results (reports) for downstream layers
↓
↓
Output Decoding Layer (Natural Language Conversion of Structured Results)  
Converts artificial language into natural language (reverse Gödel/Cantor encoding, etc.)
Generates explanations and answers
↓
↓
Output Validation Layer  
Eliminates meaningless or inappropriate output that may confuse users
↓
↓
—---------------------
End

Key Point I Want to Emphasize Most
Through the technical ideas behind this next-generation AI I am designing,
I aim to solve long-standing challenges such as:

The Frame Problem

The Hallucination Problem

The Black Box Problem

And ultimately realize an AI that can perceive, think, judge, and express itself like a human being.

Ultimate Goal of This Project
My goal is for this next-generation AI to contribute to the improvement of education worldwide.
I envision a future where anyone can enjoy learning simply by using SUNIE.

More concretely, SUNIE aims to support understanding in the educational domain
and provide opportunities for academic rediscovery.
That is the future I dream of.

To Those Who Are Following the Development Progress
The logo of this project was designed with the image of “a sun illuminating the sea.”  
I am deeply grateful to everyone who has been watching over the progress of this project.
I hope you will continue to support SUNIE warmly as it evolves.

Directory Structure of SUNIE
コード
SUNIE/
├── client/
│   ├── app.py
│   ├── requirements.txt
│   └── Dockerfile
│
├── server/
│   ├── app.py
│   ├── celery_app.py
│   ├── tasks/
│   │   ├── __init__.py
│   │   └── system_task.py
│   └── requirements.txt
│
├── worker/
│   ├── Dockerfile
│   └── start-worker.sh
│
├── nginx/
│   └── nginx.conf
│
├── logo.jpg
├── diagram.jpg
├── docker-compose.yml
├── CITATION.cff
├── CONTRIBUTING.md
├── LICENSE.md
├── INSTALL.md
├── SETUP.md
├── USE.md
├── DEVELOP.md
└── README.md

Installation Guide for This Project

Startup Guide for This Project

Usage Guide for This Project

Development Guide for This Project

License & Disclaimer
These codes are released under the MIT License.
For details, please refer to the LICENSE file.

Modification: Allowed

Reuse: Allowed

Redistribution: Allowed

The contents of the code files are provided solely for informational purposes.
Any operation based on the code must be performed at your own responsibility and judgment.
While accuracy is pursued as much as possible, the author assumes no responsibility for any outcomes resulting from the use of the code.
Thank you for your understanding.

Creator / Developer
Akihiro Morishita (moriaki1983)

Contact
moriaki1983@outlook.jp





# SUNIE - 教育向けAI-WEBアプリケーション(Client & Server)

## 本件プロジェクトのシステム構成(SUNIE-System)
[SUNIEダイアグラム](./diagram.jpg)

**技術スタック＆システム全体のデータフロー**  

Client(Streamlit) ←→ SQLite  
⇅  
Nginx  
⇅  
Server(Flask) ←→ PostgreSQL/Memgraph  
⇅  
──────────── System-Core ────────────  
Celery  
↓  
Redis/RedisQueue  
⇅  
Celery-Worker ←→ PostgreSQL/Memgraph  

**制御＆データフローの詳細**

①「Client(Streamlit)」←→「Nginx」←→  
「Server(Flask + gunicorn)」←→「PostgreSQL」「Memgraph」。  

②「Client(Streamlit)」←→「Nginx」←→  
「Server(Flask + gunicorn)」←→「System-Core」。  
※「System-Core」＝  
「Celery」→「RedisQue」←→「Celery-Worker」←→  
「PostgreSQL」「Memgraph」。  

①は、Server(ダッシュボード)から観た、DBアクセスのルート。  
②は、Celery-Workerから観た、タスク処理に伴うDBアクセスのルート。  

**個々の技術の目的と役割**  

「Client(Streamlit)」＝Web-UI/Web-UX(フロントエンド)。  
「Nginx」＝非同期Webサーバー。  
「Server(Flask + gunicorn)」＝API＆ダッシュボード(バックエンド)。  
「RedisQue」＝メッセージキュー(タスク要求の整理)。  
「Celery」＝タスクワーカーの生成と管理。  
「PostgreSQL」＝学習・ログイン履歴保存特化データベース。  
「Memgraph」＝教材データ検索特化データベース。

**技術選定の理由**  

「Nginx」「Redis」「RedisQue」「Celery」「PostgreSQL」「Memgraph」については、  
将来的なユーザー数の増大や、システムの拡張を見越した技術選定です。  
また、「gunicorn」については、Flaskをバックエンドに採用する関係で必然的な選択になっています。  
特に、「Client(Streamlit)」「Server(Flask + gunicorn)」については、  
既に、日本の公立学校の情報科目の中で採用されているPythonだけでフロントとバックを一貫して記述できることと、  
日本の各自治体ごとに設置されている教育委員会の審議に通りやすくするために、このような選定としました。

## 本件プロジェクトの中心・中核原理(SUNIE-Architecture)
本件プロジェクトの、いわば「心臓部となる部分」(Celery式の推論ワーカー)は、  
ルールベースとニューラルネット(LLM)を混成したハイブリッド仕様となっています。  

**ハイブリッドAIコワーカー(SUNIE/LUMIE System)**  

開始
—---------------------
↓
↓
入力検証層(入力の検証)
無意味・不適切な語句、システムを混乱させるような入力の排除
↓
↓
入力エンコーディング層(自然言語の曖昧性処理)
曖昧な自然言語の変換(ゲーデル符号化＆カントール符号化 等)
ユーザー意図の抽出
後続のコアに渡すための構造化要求の生成
↓
↓
シミュレーションと推論コア(シミュレーションと推論の構造化実行)
LLMによるユーザー心理の推定・評価に基づくロタリーの調整
ロタリーの実施結果に基づく概念データとその処理コードの選定
要求に含まれる概念データのグラフベース検索・取得
概念データ処理コードのリレーショナルベース検索・取得
概念データの有効性・妥当性検証
安全ステージでの概念データ処理コードの安全性検証
ゲーデリアン＆カントーリアンに基づくチェーン(シミュレーション＆推論)の構成
ゲーデリアン＆カントーリアンに基づくチェーン(シミュレーション＆推論)の実行
監査ログのリレーショナルベース記録・保存
後続の層に渡すための構造化結果(レポート)の生成
↓
↓
出力復号層(構造化結果の自然言語化)
明確な人工言語の変換(逆ゲーデル符号化＆逆カントール符号化 等)
説明・回答の生成
↓
↓
出力検証層(出力の検証)
無意味・不適切な語句、ユーザーを混乱させるような出力の排除
↓
↓
—---------------------
終了



## もっとも強調・アピールしたい点
私の構想・開発する、この次世代AIの技術的アイデアによって、  
長年にわたって議論されてきた「フレーム問題」「ハルシネーション問題」「ブラックボックス問題」が解決されて、  
「人間のように 物事を知覚したり 思考したり 判断したり 表現できるAI」を実現させたいと思っています。



## 本件プロジェクトの最終的な目標
私の構想・開発する、この次世代AIによって「全世界の教育の向上に資すること」です。  
「誰もが SUNIEを利用することで 楽しんで教育を受けることができる」。  
より具体的に言えば、教育分野における理解の支援(学術的な再発見機会の提供)。  
そのような未来を夢見ています・・・。



## 開発状況をチェックして下さっている方々へ
本件プロジェクトのロゴは「海を照らす太陽」をイメージして作成しました。  
プロジェクトの進捗を見守ってくださる方々には、感謝の気持ちで一杯です・・・。  
今後とも、本件アプリの進捗を温かく見守って下さると幸いです。



## SUNIEのディレクトリ構造
SUNIE/
├── client/
│   ├── app.py
│   ├── requirements.txt
│   └── Dockerfile
│
├── server/
│   ├── app.py
│   ├── celery_app.py
│   ├── tasks/
│   │   ├── __init__.py
│   │   └── system_task.py
│   └── requirements.txt
│
├── worker/
│   ├── Dockerfile
│   └── start-worker.sh
│
├── nginx/
│   └── nginx.conf
│
├── logo.jpg
├── diagram.jpg
├── docker-compose.yml
├── CITATION.cff
├── CONTRIBUTING.md
├── LICENSE.md
├── INSTALL.md
├── SETUP.md
├── USE.md
├── DEVELOP.md
└── README.md



## 本件プロジェクトの導入方法
[SUNIEガイド1](INSTALL.md)



## 本件プロジェクトの立上げ方法
[SUNIEガイド2](SETUP.md)



## 本件プロジェクトの利用方法
[SUNIEガイド3](USE.md)



## 本件プロジェクトの開発方法
[SUNIEガイド4](DEVELOP.md)



## ライセンス＆免責事項
これらのコードはMITライセンスのもとで公開されています。詳しくは「LISENCE」ファイルを参照してください。

- 改変: 可
- 再利用: 可
- 再頒布: 可

コードファイルに記載された内容は、情報提供のみを目的としています。
したがって、コードを参考にした運用は必ずご自身の責任と判断において行ってください。
コードの内容については、できる限り正確を期していますが、コードの内容に基づく運用結果について、作者は一切の責任を負いかねます。
あらかじめご了承ください。



## 製作・開発者
森下哲博(moriaki1983)




## 連絡先
moriaki1983@outlook.jp
