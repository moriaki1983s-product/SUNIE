# coding: utf-8




# 既成のモジュールをインポートする.
import random
import numpy as np



#ランダムに決定される状態値を[str]型で取得する.
def random_select(stts):
    random.seed(None) # シードをリセット
    return random.choice(stts)


#ランダムに決定される複数の状態値を[str-list]型で取得する.
def random_selects(stts, wghts, smpl_num):
    return random.choices(stts, weights=wghts, k=smpl_num)
