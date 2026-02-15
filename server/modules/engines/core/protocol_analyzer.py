# coding: utf-8




# 既成のモジュールをインポートする.
import os
import sys

# 独自のモジュールをインポートする.
# import modules.intelligences.reg_unit as reg
# import modules.intelligences.cog_unit as cog
# import modules.intelligences.emo_unit as emo
# import modules.intelligences.sim_unit as sim
# import modules.intelligences.etc_unit as etc




# Sunieエンジンのクラスを宣言・定義する.
class ProtocolAnalyzer:
    _instance = None
    dat = None

    # インスタンス生成のためのメソッドを宣言・定義する.
    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(ProtocolAnalyzer, cls).__new__(cls, *args, **kwargs)
        return cls._instance

    # インスタンス初期化のためのメソッドを宣言・定義する.
    def __init__(self):
        # self.reg = reg.RegUnit()
        # self.cog = cog.CogUnit()
        # self.emo = emo.EmoUnit()
        # self.sim = sim.SimUnit()
        # self.etc = etc.EtcUnit()
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

    # 職員メッセージに含まれる語句群をソースとして,
    # これらを解釈・実行するためのメソッドを宣言・定義する.
    def execution(self, stff_wrds):
        thm = ""
        intnt = ""
        sntmnt = ""

        return thm, intnt, sntmnt