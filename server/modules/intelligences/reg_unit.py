# coding: utf-8




# 既成のモジュールをインポートする.
import os
import sys

# 独自のモジュールをインポートする.
import modules.utilities.text as utils_text




# Regユニットのクラスを定義する.
class RegUnit:
    _instance = None
    dat = None

    # インスタンス生成のためのメソッドを定義する.
    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(RegUnit, cls).__new__(cls, *args, **kwargs)
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
        anlyzd_dat = self.dat
        return anlyzd_dat

    # データを生成するためのメソッドを定義する.
    def generative_drive(self):
        gnrtd_dat = self.dat
        return gnrtd_dat


    # 「modules.utilities.text」への委譲メソッドを定義する.
    # ※詳細なコメントについては, 該当モジュールを参照すること.
    def perform_morphological_analysis_on_natural_text(self, txt):
        chars = utils_text.characterize_and_tagging(txt)
        tkns_mrg = utils_text.tokenize_and_tagging(chars)

        return tkns_mrg

    def split_text_message_on_delimiter(self, txt_msg):
        return utils_text.split_text_message_on_delimiter(txt_msg)

    def split_text_message_character_type(self, txt_msg):
        return utils_text.split_text_message_character_type(txt_msg)

    def analyze_words_in_texts(self, stff_wrds_in_txts):
        return utils_text.analyze_words_in_texts(stff_wrds_in_txts)

    def generate_words_in_texts(self, stff_fct, stff_intnt, stff_sntmnt):
        return utils_text.generate_words_in_texts(self, stff_fct, stff_intnt, stff_sntmnt)

    # def asemble_text_message(self, app_wrds_in_txts):
    #     return utils_text.asemble_text_message(app_wrds_in_txts)
    def asemble_text_message(self):
        return utils_text.asemble_text_message()

    def check_numeric_in_en(self, txt):
        return utils_text.check_numeric_in_en(txt)

    def check_alphabetic_numeric_and_symbol_with_space_in_en(self, txt):
        return utils_text.check_alphabetic_numeric_and_symbol_with_space_in_en(txt)

    def check_katakana_uppercase_in_ja(self, txt):
        return utils_text.check_katakana_uppercase_in_ja(txt)