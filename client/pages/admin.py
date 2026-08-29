import streamlit as st
import sqlite3
from pathlib import Path

DB_PATH = "db/nollm.db"

# -----------------------------
# DB 接続
# -----------------------------
def get_conn():
    Path("db").mkdir(exist_ok=True)
    return sqlite3.connect(DB_PATH)

# -----------------------------
# 関数一覧の取得
# -----------------------------
def load_functions():
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT name, change_key, change_value, message FROM functions")
    rows = cur.fetchall()
    conn.close()
    return rows

# -----------------------------
# 関数の追加
# -----------------------------
def add_function(name, key, value, message):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO functions (name, change_key, change_value, message)
        VALUES (?, ?, ?, ?)
    """, (name, key, value, message))
    conn.commit()
    conn.close()

# -----------------------------
# 関数の削除
# -----------------------------
def delete_function(name):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("DELETE FROM functions WHERE name = ?", (name,))
    conn.commit()
    conn.close()

# -----------------------------
# 関数チェーンの取得
# -----------------------------
def load_chain():
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("""
        SELECT step_order, step_name, ref_type, ref_name
        FROM function_chain
        ORDER BY step_order ASC
    """)
    rows = cur.fetchall()
    conn.close()
    return rows

# -----------------------------
# チェーンの追加
# -----------------------------
def add_chain_step(order, name, ref_type, ref_name):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO function_chain (step_order, step_name, ref_type, ref_name)
        VALUES (?, ?, ?, ?)
    """, (order, name, ref_type, ref_name))
    conn.commit()
    conn.close()

# -----------------------------
# チェーンの削除
# -----------------------------
def delete_chain_step(order):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("DELETE FROM function_chain WHERE step_order = ?", (order,))
    conn.commit()
    conn.close()

# -----------------------------
# ロタリーの取得
# -----------------------------
def load_lottery(name):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("""
        SELECT id, probability, action_type, action_name, label
        FROM lottery_rules
        WHERE lottery_name = ?
        ORDER BY id ASC
    """, (name,))
    rows = cur.fetchall()
    conn.close()
    return rows

# -----------------------------
# ロタリーの追加
# -----------------------------
def add_lottery_rule(name, prob, action_type, action_name, label):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO lottery_rules (lottery_name, probability, action_type, action_name, label)
        VALUES (?, ?, ?, ?, ?)
    """, (name, prob, action_type, action_name, label))
    conn.commit()
    conn.close()

# -----------------------------
# ロタリーの削除
# -----------------------------
def delete_lottery_rule(rule_id):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("DELETE FROM lottery_rules WHERE id = ?", (rule_id,))
    conn.commit()
    conn.close()

# -----------------------------
# UI
# -----------------------------
st.title("🛠️ NoLLM 管理画面（DB 駆動ロジック編集）")
st.write("関数・チェーン・ロタリーを GUI で編集できます。")

tab1, tab2, tab3 = st.tabs(["関数（Functions）", "関数チェーン（Chain）", "ロタリー（Lottery）"])

# -----------------------------
# 1. 関数管理
# -----------------------------
with tab1:
    st.subheader("📦 関数一覧")
    funcs = load_functions()
    for f in funcs:
        st.markdown(f"- **{f[0]}**: `{f[1]} = {f[2]}` → {f[3]}")

    st.subheader("➕ 関数を追加")
    name = st.text_input("関数名")
    key = st.text_input("変更する属性キー（例: dim_color）")
    value = st.text_input("変更後の値（例: Brown）")
    msg = st.text_area("ログメッセージ")

    if st.button("関数を追加"):
        add_function(name, key, value, msg)
        st.success("関数を追加しました。")

    st.subheader("🗑️ 関数を削除")
    del_name = st.selectbox("削除する関数名", [f[0] for f in funcs])
    if st.button("削除する"):
        delete_function(del_name)
        st.warning("削除しました。")

# -----------------------------
# 2. 関数チェーン管理
# -----------------------------
with tab2:
    st.subheader("🔗 関数チェーン一覧")
    chain = load_chain()
    for c in chain:
        st.markdown(f"- **{c[0]}**: {c[1]} → ({c[2]}) {c[3]}")

    st.subheader("➕ チェーンステップ追加")
    order = st.number_input("ステップ順序", min_value=1, step=1)
    step_name = st.text_input("ステップ名")
    ref_type = st.selectbox("参照タイプ", ["function", "condition", "lottery"])
    ref_name = st.text_input("参照名（関数名・条件名・ロタリー名）")

    if st.button("チェーンに追加"):
        add_chain_step(order, step_name, ref_type, ref_name)
        st.success("チェーンに追加しました。")

    st.subheader("🗑️ チェーンステップ削除")
    del_order = st.selectbox("削除するステップ順序", [c[0] for c in chain])
    if st.button("ステップ削除"):
        delete_chain_step(del_order)
        st.warning("削除しました。")

# -----------------------------
# 3. ロタリー管理
# -----------------------------
with tab3:
    st.subheader("🎲 ロタリー（LOTTERY_COLOR）")
    rules = load_lottery("LOTTERY_COLOR")

    for r in rules:
        st.markdown(f"- **ID {r[0]}**: P={r[1]} / {r[2]} → {r[3]} / {r[4]}")

    st.subheader("➕ ロタリールール追加")
    prob = st.number_input("確率（0〜1）", min_value=0.0, max_value=1.0, step=0.01)
    action_type = st.selectbox("アクションタイプ", ["function", "none"])
    action_name = st.text_input("関数名（none の場合は空）")
    label = st.text_input("ラベル（例: 茶色になる）")

    if st.button("ロタリーに追加"):
        add_lottery_rule("LOTTERY_COLOR", prob, action_type, action_name, label)
        st.success("ロタリーに追加しました。")

    st.subheader("🗑️ ロタリールール削除")
    del_id = st.selectbox("削除するルール ID", [r[0] for r in rules])
    if st.button("ルール削除"):
        delete_lottery_rule(del_id)
        st.warning("削除しました。")
