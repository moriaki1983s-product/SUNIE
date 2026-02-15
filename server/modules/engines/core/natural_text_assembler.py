# coding: utf-8




# 既成のモジュールをインポートする.
import os
import sys

# 独自のモジュールをインポートする.
# import modules.intelligences.reg_unit as reg
# import modules.intelligences.cog_unit as cog
# import modules.intelligences.emo_unit as emo
# import modules.intelligences.sim_unit as sim
import modules.intelligences.etc_unit as etc




# Sunieエンジンのクラスを宣言・定義する.
class NaturalTextAssembler:
    _instance = None
    dat = None

    # インスタンス生成のためのメソッドを宣言・定義する.
    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(NaturalTextAssembler, cls).__new__(cls, *args, **kwargs)
        return cls._instance

    # インスタンス初期化のためのメソッドを宣言・定義する.
    def __init__(self):
        # self.reg = reg.RegUnit()
        # self.cog = cog.CogUnit()
        # self.emo = emo.EmoUnit()
        # self.sim = sim.SimUnit()
        self.etc = etc.EtcUnit()
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

    # 最終結果コード(=Final-Result-code)をソースとして,
    # これを解釈・実行するためのメソッドを宣言・定義する.
    def execution(self, fr_code):
        sntmnt_cnddt = ["JOY", "ANGER", "PITY", "COMFORT", "MIXED", "NEUTRAL"]
        dcid_sntmnt = self.etc.random_select(sntmnt_cnddt)

        if dcid_sntmnt == "JOY":
            msg_cnddt = ["お世話になってます♪", "またまた～♪"]
            gnrtd_msg = self.etc.random_select(msg_cnddt)

        elif dcid_sntmnt == "ANGER":
            msg_cnddt = ["それで？", "何が言いたいの？"]
            gnrtd_msg = self.etc.random_select(msg_cnddt)

        elif dcid_sntmnt == "PITY":
            msg_cnddt = ["ええと・・・", "・・・"]
            gnrtd_msg = self.etc.random_select(msg_cnddt)

        elif dcid_sntmnt == "COMFORT":
            msg_cnddt = ["くつろいでね", "元気でね"]
            gnrtd_msg = self.etc.random_select(msg_cnddt)

        elif dcid_sntmnt == "MIXED":
            msg_cnddt = ["どうしたらいいですか？", "オロオロ 汗"]
            gnrtd_msg = self.etc.random_select(msg_cnddt)

        else:
            msg_cnddt = ["どうしました？", "お元気そうで"]
            gnrtd_msg = self.etc.random_select(msg_cnddt)

        return gnrtd_msg