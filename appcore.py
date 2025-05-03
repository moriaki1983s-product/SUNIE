# coding: utf-8




# 既成のモジュールをインポートする.
import os
import sys
import random

# 独自のモジュールをインポートする.
import modules.intelligences.reg_neo as reg_neo
import modules.intelligences.cog_neo as cog_neo
import modules.intelligences.emo_neo as emo_neo
import modules.intelligences.sim_neo as sim_neo
import modules.intelligences.etc_neo as etc_neo




# Sunieエンジンのクラスを宣言・定義する.
class SunieEngine:
    _instance = None
    dat = None

    # インスタンス生成のためのメソッドを宣言・定義する.
    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(SunieEngine, cls).__new__(cls, *args, **kwargs)
        return cls._instance

    # インスタンス初期化のためのメソッドを宣言・定義する.
    def __init__(self):
        self.reg = reg_neo.RegUnit()
        self.cog = cog_neo.CogUnit()
        self.emo = emo_neo.EmoUnit()
        self.sim = sim_neo.SimUnit()
        self.etc = etc_neo.EtcUnit()
        self.dat = None

    # データを設定するためのメソッドを宣言・定義する.
    def set_data(self, dat):
        self.dat = dat

    # データを取得するためのメソッドを宣言・定義する.
    def get_data(self):
        return self.dat

    # データを消去するためのメソッドを宣言・定義する.
    def clear_data(self):
        self.dat = None

    # データを解析するためのメソッドを宣言・定義する.
    def analytical_drive(self):
        anlyzd_dat = self.dat
        return anlyzd_dat

    # データを生成するためのメソッドを宣言・定義する.
    def generative_drive(self):
        gnrtd_dat = self.dat
        return gnrtd_dat

    # 返信メッセージを生成するためのメソッドを宣言・定義する.
    def generate_message(self, msg):
        sntmnt_cnddt = ["JOY", "ANGER", "PITY", "COMFORT", "MIXED", "NEUTRAL"]
        dcid_sntmnt = random.choice(sntmnt_cnddt)

        if dcid_sntmnt == "JOY":
            msg_cnddt = ["お世話になってます♪", "またまた～♪"]
            gnrtd_msg = random.choice(msg_cnddt)

        elif dcid_sntmnt == "ANGER":
            msg_cnddt = ["それで？", "何が言いたいの？"]
            gnrtd_msg = random.choice(msg_cnddt)

        elif dcid_sntmnt == "PITY":
            msg_cnddt = ["ええと・・・", "・・・"]
            gnrtd_msg = random.choice(msg_cnddt)

        elif dcid_sntmnt == "COMFORT":
            msg_cnddt = ["くつろいでね", "元気でね"]
            gnrtd_msg = random.choice(msg_cnddt)

        elif dcid_sntmnt == "MIXED":
            msg_cnddt = ["どうしたらいいですか？", "オロオロ 汗"]
            gnrtd_msg = random.choice(msg_cnddt)

        else:
            msg_cnddt = ["どうしました？", "お元気そうで"]
            gnrtd_msg = random.choice(msg_cnddt)

        return gnrtd_msg

    # 語句情報を学習するためのメソッドを宣言・定義する.
    def learn_word(self, spll_n_hdr, mn_n_cntnt):
        return ""

    # 主題情報を学習するためのメソッドを宣言・定義する.
    def learn_theme(self, spll_n_hdr, mn_n_cntnt):
        return ""

    # 分類情報を学習するためのメソッドを宣言・定義する.
    def learn_category(self, spll_n_hdr, mn_n_cntnt):
        return ""

    # 知識情報を学習するためのメソッドを宣言・定義する.
    def learn_knowledge(self, spll_n_hdr, mn_n_cntnt):
        return ""

    # 規則情報を学習するためのメソッドを宣言・定義する.
    def learn_rule(self, spll_n_hdr, mn_n_cntnt):
        return ""

    # 反応情報を学習するためのメソッドを宣言・定義する.
    def learn_reaction(self, spll_n_hdr, mn_n_cntnt):
        return ""

    # 各種のデータファイルを生成するためのメソッドを宣言・定義する.
    def generate_data_file(self, spll_n_hdr, mn_n_cntnt):
        return ""