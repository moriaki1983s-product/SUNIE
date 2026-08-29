import streamlit as st
import sqlite3
import random
import time
from copy import deepcopy
from pathlib import Path

DB_PATH = "db/nollm.db"


# ==============================
# 1. DB 初期化（スキーマ & 初期データ）
# ==============================

def init_db():
    Path("db").mkdir(exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    # 属性次元（初期状態）
    cur.execute("""
    CREATE TABLE IF NOT EXISTS dimensions (
        key TEXT PRIMARY KEY,
        initial_value TEXT
    )
    """)

    # 関数定義（＝状態差分ルール）
    cur.execute("""
    CREATE TABLE IF NOT EXISTS functions (
        name TEXT PRIMARY KEY,
        change_key TEXT NOT NULL,
        change_value TEXT NOT NULL,
        message TEXT NOT NULL
    )
    """)

    # 条件分岐（条件名 → 属性値が一致したら関数を実行）
    cur.execute("""
    CREATE TABLE IF NOT EXISTS conditions (
        name TEXT PRIMARY KEY,
        key TEXT NOT NULL,
        expected_value TEXT NOT NULL,
        action_name TEXT NOT NULL
    )
    """)

    # 関数チェーン（順序付き）
    cur.execute("""
    CREATE TABLE IF NOT EXISTS function_chain (
        step_order INTEGER PRIMARY KEY,
        step_name TEXT NOT NULL,
        ref_type TEXT NOT NULL,   -- 'function' / 'condition' / 'lottery'
        ref_name TEXT NOT NULL
    )
    """)

    # ロタリー（確率選択ルール）
    cur.execute("""
    CREATE TABLE IF NOT EXISTS lottery_rules (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        lottery_name TEXT NOT NULL,
        probability REAL NOT NULL,
        action_type TEXT NOT NULL,  -- 'function' / 'none'
        action_name TEXT,           -- 関数名 or NULL
        label TEXT NOT NULL
    )
    """)

    # --- 初期データ投入（なければ） ---

    # dimensions
    cur.execute("SELECT COUNT(*) FROM dimensions")
    if cur.fetchone()[0] == 0:
        cur.executemany(
            "INSERT INTO dimensions (key, initial_value) VALUES (?, ?)",
            [
                ("dim_color", "Red"),
                ("dim_shape", "Round"),
                ("dim_moisture", "High"),
            ],
        )

    # functions（関数の中身はすべて DB に）
    cur.execute("SELECT COUNT(*) FROM functions")
    if cur.fetchone()[0] == 0:
        cur.executemany(
            "INSERT INTO functions (name, change_key, change_value, message) VALUES (?, ?, ?, ?)",
            [
                (
                    "func_evaporate",
                    "dim_moisture",
                    "Low",
                    "水分が High → Low に変化しました。",
                ),
                (
                    "func_shrink",
                    "dim_shape",
                    "Shrunk",
                    "形状が Round → Shrunk に変化しました。",
                ),
                (
                    "func_discolor_brown",
                    "dim_color",
                    "Brown",
                    "色が Red → Brown に変化しました。",
                ),
                (
                    "func_discolor_black",
                    "dim_color",
                    "Black",
                    "色が Red/Brown → Black に変化しました。",
                ),
            ],
        )

    # conditions（条件分岐も DB に）
    cur.execute("SELECT COUNT(*) FROM conditions")
    if cur.fetchone()[0] == 0:
        cur.executemany(
            "INSERT INTO conditions (name, key, expected_value, action_name) VALUES (?, ?, ?, ?)",
            [
                (
                    "COND_SHRINK_IF_MOISTURE_LOW",
                    "dim_moisture",
                    "Low",
                    "func_shrink",
                ),
            ],
        )

    # function_chain（実行フローも DB に）
    cur.execute("SELECT COUNT(*) FROM function_chain")
    if cur.fetchone()[0] == 0:
        cur.executemany(
            "INSERT INTO function_chain (step_order, step_name, ref_type, ref_name) VALUES (?, ?, ?, ?)",
            [
                (1, "evaporate", "function", "func_evaporate"),
                (2, "shrink_if_dry", "condition", "COND_SHRINK_IF_MOISTURE_LOW"),
                (3, "lottery_color", "lottery", "LOTTERY_COLOR"),
            ],
        )

    # lottery_rules（ロタリーも DB 駆動）
    cur.execute("SELECT COUNT(*) FROM lottery_rules WHERE lottery_name = 'LOTTERY_COLOR'")
    if cur.fetchone()[0] == 0:
        cur.executemany(
            "INSERT INTO lottery_rules (lottery_name, probability, action_type, action_name, label) VALUES (?, ?, ?, ?, ?)",
            [
                ("LOTTERY_COLOR", 0.60, "function", "func_discolor_brown", "茶色になる"),
                ("LOTTERY_COLOR", 0.30, "function", "func_discolor_black", "黒焦げになる"),
                ("LOTTERY_COLOR", 0.10, "none",     None,                 "変化なし"),
            ],
        )

    conn.commit()
    conn.close()


# ==============================
# 2. DB から定義を読み込む
# ==============================

def load_initial_status():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("SELECT key, initial_value FROM dimensions")
    rows = cur.fetchall()
    conn.close()
    return {k: v for k, v in rows}


def load_function_chain():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("""
        SELECT step_order, step_name, ref_type, ref_name
        FROM function_chain
        ORDER BY step_order ASC
    """)
    rows = cur.fetchall()
    conn.close()
    return [
        {
            "order": o,
            "step_name": s,
            "ref_type": t,
            "ref_name": r,
        }
        for o, s, t, r in rows
    ]


def load_lottery_rules(lottery_name):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("""
        SELECT probability, action_type, action_name, label
        FROM lottery_rules
        WHERE lottery_name = ?
        ORDER BY id ASC
    """, (lottery_name,))
    rows = cur.fetchall()
    conn.close()
    return [
        {
            "prob": p,
            "action_type": at,
            "action_name": an,
            "label": l,
        }
        for p, at, an, l in rows
    ]


# ==============================
# 3. 状態遷移エンジン（完全 DB 駆動）
# ==============================

def apply_changes(status, key, value):
    new_status = deepcopy(status)
    new_status[key] = value
    return new_status


def log_event(message, status_snapshot, logs):
    logs.append({
        "timestamp": time.time(),
        "message": message,
        "status": deepcopy(status_snapshot),
    })


def execute_db_function(func_name, status):
    """関数の中身も DB にある：change_key / change_value / message"""
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("""
        SELECT change_key, change_value, message
        FROM functions
        WHERE name = ?
    """, (func_name,))
    row = cur.fetchone()
    conn.close()

    if row is None:
        return status, f"[{func_name}] 未定義の関数です。"

    key, value, msg = row
    new_status = apply_changes(status, key, value)
    return new_status, msg


def execute_condition(cond_name, status):
    """条件分岐も DB に定義されている"""
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("""
        SELECT key, expected_value, action_name
        FROM conditions
        WHERE name = ?
    """, (cond_name,))
    row = cur.fetchone()
    conn.close()

    if row is None:
        return status, f"[{cond_name}] 未定義の条件です。"

    key, expected, action_name = row
    if status.get(key) == expected:
        new_status, msg = execute_db_function(action_name, status)
        return new_status, f"[{cond_name}] 条件成立: {msg}"
    else:
        return status, f"[{cond_name}] 条件不成立: {key} != {expected}（処理スキップ）"


def execute_lottery(lottery_name, status):
    rules = load_lottery_rules(lottery_name)
    r = random.random()

    logs_local = []
    logs_local.append(f"[{lottery_name}] ロタリーを振りました。出目: {r:.2f}")

    acc = 0.0
    for rule in rules:
        acc += rule["prob"]
        if r < acc:
            label = rule["label"]
            action_type = rule["action_type"]
            action_name = rule["action_name"]

            if action_type == "none":
                logs_local.append(f"[{lottery_name}] 結果: {label}（状態変化なし）")
                return status, logs_local

            if action_type == "function":
                new_status, msg = execute_db_function(action_name, status)
                logs_local.append(f"[{lottery_name}] 結果: {label}")
                logs_local.append(f"[{lottery_name}] {msg}")
                return new_status, logs_local

            logs_local.append(f"[{lottery_name}] 未知の action_type: {action_type}")
            return status, logs_local

    logs_local.append(f"[{lottery_name}] フォールバック（変化なし）")
    return status, logs_local


def execute_chain_db_driven(initial_status):
    chain = load_function_chain()
    status = deepcopy(initial_status)
    logs = []

    for step in chain:
        step_name = step["step_name"]
        ref_type = step["ref_type"]
        ref_name = step["ref_name"]

        if ref_type == "function":
            new_status, msg = execute_db_function(ref_name, status)
            status = new_status
            log_event(f"[{step_name}] {msg}", status, logs)

        elif ref_type == "condition":
            new_status, msg = execute_condition(ref_name, status)
            status = new_status
            log_event(f"[{step_name}] {msg}", status, logs)

        elif ref_type == "lottery":
            new_status, local_logs = execute_lottery(ref_name, status)
            status = new_status
            for m in local_logs:
                log_event(f"[{step_name}] {m}", status, logs)

        else:
            log_event(f"[{step_name}] 未知の ref_type: {ref_type}", status, logs)

    return status, logs


# ==============================
# 4. Streamlit UI
# ==============================

def main():
    init_db()

    st.title("🍏 関数まで DB に完全移行した NoLLM 状態遷移エンジン PoC")
    st.write("属性次元・関数・条件分岐・ロタリー・関数チェーンをすべて SQLite に持たせ、Python は実行エンジンだけになります。")

    if "apple_status" not in st.session_state:
        st.session_state.apple_status = load_initial_status()

    st.subheader("1. 現在の状態（属性次元）")
    st.json(st.session_state.apple_status)

    if st.button("🔥 リンゴを加熱する（DB定義チェーンを実行）"):
        final_status, logs = execute_chain_db_driven(st.session_state.apple_status)
        st.session_state.apple_status = final_status

        st.subheader("2. 実行ログ（完全 DB 駆動・説明可能）")
        for log in logs:
            ts = time.strftime("%H:%M:%S", time.localtime(log["timestamp"]))
            st.markdown(f"- `{ts}` {log['message']}")

        st.subheader("3. 遷移後の最終状態")
        st.json(st.session_state.apple_status)
        st.success("DB 駆動の状態遷移が完了しました。")

    if st.button("🔄 状態をリセット"):
        st.session_state.apple_status = load_initial_status()
        st.info("状態を初期値にリセットしました。")


if __name__ == "__main__":
    main()
