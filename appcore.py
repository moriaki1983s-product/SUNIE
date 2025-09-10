# coding: utf-8




# 既成のモジュールをインポートする.
import os
import sys

# 独自のモジュール(engines)をインポートする.
import modules.engines.core.interpreter as intrprtr
import modules.engines.core.tagnet_builder as tgnt_bldr
import modules.engines.core.tagnet_clowler as tgnt_clwlr
import modules.engines.core.task_resolver as tsk_rslvr
import modules.engines.visual.image as img
import modules.engines.visual.graphic as grph
import modules.engines.audio.sound as snd
import modules.engines.audio.voice as vce
import modules.engines.video.clip as clp
import modules.engines.video.transition as trns

# 独自のモジュール(intelligences)をインポートする.
import modules.intelligences.reg_unit as reg
import modules.intelligences.cog_unit as cog
import modules.intelligences.emo_unit as emo
import modules.intelligences.sim_unit as sim
import modules.intelligences.etc_unit as etc




# Sunieの中核エンジンのクラスを宣言・定義する.
class CoreEngine:
    _instance = None
    dat = None

    # インスタンス生成のためのメソッドを宣言・定義する.
    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(CoreEngine, cls).__new__(cls, *args, **kwargs)
        return cls._instance

    # インスタンス初期化のためのメソッドを宣言・定義する.
    def __init__(self):
        self.interpreter = intrprtr.Interpreter()
        self.tagnet_builder = tgnt_bldr.TagnetBuilder()
        self.tagnet_clowler = tgnt_clwlr.TagnetClowlwer()
        self.task_resolver = tsk_rslvr.TaskResolver()
        self.reg = reg.RegUnit()
        self.cog = cog.CogUnit()
        self.emo = emo.EmoUnit()
        self.sim = sim.SimUnit()
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


    # 語句情報を学習するためのメソッドを宣言・定義する.
    def learn_word(self, spll_n_hdr, mn_n_bdy):
        return ""

    # 主題情報を学習するためのメソッドを宣言・定義する.
    def learn_theme(self, spll_n_hdr, mn_n_bdy):
        return ""

    # 分類情報を学習するためのメソッドを宣言・定義する.
    def learn_category(self, spll_n_hdr, mn_n_bdy):
        return ""

    # 事実情報を学習するためのメソッドを宣言・定義する.
    def learn_fact(self, spll_n_hdr, mn_n_bdy):
        return ""

    # 規則情報を学習するためのメソッドを宣言・定義する.
    def learn_rule(self, spll_n_hdr, mn_n_bdy):
        return ""

    # 反応情報を学習するためのメソッドを宣言・定義する.
    def learn_reaction(self, spll_n_hdr, mn_n_bdy):
        return ""

    # 各種のデータファイルを生成するためのメソッドを宣言・定義する.
    def generate_data_file(self, spll_n_hdr, mn_n_bdy):
        return ""
    

# Sunieの視覚エンジンのクラスを宣言・定義する.
class VisualEngine:
    _instance = None
    dat = None

    # インスタンス生成のためのメソッドを宣言・定義する.
    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(VisualEngine, cls).__new__(cls, *args, **kwargs)
        return cls._instance

    # インスタンス初期化のためのメソッドを宣言・定義する.
    def __init__(self):
        self.image = img.Image()
        self.graphic = grph.Graphic()
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


# Sunieの聴覚エンジンのクラスを宣言・定義する.
class AudioEngine:
    _instance = None
    dat = None

    # インスタンス生成のためのメソッドを宣言・定義する.
    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(AudioEngine, cls).__new__(cls, *args, **kwargs)
        return cls._instance

    # インスタンス初期化のためのメソッドを宣言・定義する.
    def __init__(self):
        self.sound = snd.Sound()
        self.voice = vce.Voice()
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


# Sunieの視聴覚エンジンのクラスを宣言・定義する.
class VideoEngine:
    _instance = None
    dat = None

    # インスタンス生成のためのメソッドを宣言・定義する.
    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(VideoEngine, cls).__new__(cls, *args, **kwargs)
        return cls._instance

    # インスタンス初期化のためのメソッドを宣言・定義する.
    def __init__(self):
        self.clip = clp.Clip()
        self.transition = trns.Transition()
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