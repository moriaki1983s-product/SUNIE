① Windows の初期設定（2分）
✔ Windows Update を一度だけ実行
（放置でOK。裏で勝手に進む）

✔ Microsoft Store を開いて「Windows Terminal」をインストール
あなたは Terminal をよく使うので、最初に入れておくとスムーズ。

② WSL2 + Ubuntu の導入（3分）
Windows Terminal を開いて、これだけ。

コード
wsl --install
自動で：

WSL2

Ubuntu

必要なコンポーネント

が全部入る。

再起動後、Ubuntu が起動してユーザー名とパスワードを設定するだけ。

③ Ubuntu の初期設定（3分）
Ubuntu が起動したら、まず更新。

コード
sudo apt update && sudo apt upgrade -y
次に、SUNIE/LUMIE に必要な最低限のパッケージを入れる。

コード
sudo apt install -y python3 python3-pip python3-venv \
    redis-server postgresql graphviz
これで SUNIE/LUMIE の基盤がすべて揃う。

④ PostgreSQL の初期設定（1分）
コード
sudo service postgresql start
必要ならユーザー作成：

コード
sudo -u postgres createuser -s $USER
⑤ SUNIE/LUMIE のディレクトリを作る（1分）
コード
mkdir -p ~/sunie/{server,client}
GitHub からコードを持ってくる場合は：

コード
git clone https://github.com/あなたのリポジトリ
（Web-UI 中心なら、ここは後でOK）

⑥ 起動スクリプトを配置（1分）
あなたが作った：

start_sunie.sh

stop_sunie.sh

sunie-control.sh

を ~/sunie/ に置いて、権限付与。

コード
chmod +x *.sh
🌄 これで準備完了
ここまでで 10分以内。
あとは SUNIE を起動するだけ。

コード
./sunie-control.sh start
あなたの新しいマシンで、
SUNIE/LUMIE が“OSとして”動き始める瞬間です。


git clone https://github.com/あなた/SUNIE ~/sunie


~/sunie/
    server/
    client/
    scripts/
        start_sunie.sh
        stop_sunie.sh
        sunie-control.sh
    logs/
