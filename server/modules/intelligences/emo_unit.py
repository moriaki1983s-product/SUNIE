# coding: utf-8




# 既成のモジュールをインポートする.
import os
import sys

# 独自のモジュールをインポートする.
import modules.utilities.emotion as utils_emotion




# Emoユニットのクラスを定義する.
class EmoUnit:
    _instance = None
    dat = None

    # インスタンス生成のためのメソッドを定義する.
    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(EmoUnit, cls).__new__(cls, *args, **kwargs)
        return cls._instance

    # インスタンス初期化のためのメソッドを定義する.
    def __init__(self):
        self.dat = None

    # データを設定するためのメソッドを定義する.
    def set_data(self, dat):
        self.dat = dat

    # データを取得するためのメソッドを定義する.
    def get_data(self):
        return self.dat

    # データを消去するためのメソッドを定義する.
    def clear_data(self):
        self.dat = None

    # データを解析するためのメソッドを定義する.
    def analytical_drive(self):
        anlyzd_dat = None
        return anlyzd_dat

    # データを生成するためのメソッドを定義する.
    def generative_drive(self):
        gnrtd_dat = None
        return gnrtd_dat