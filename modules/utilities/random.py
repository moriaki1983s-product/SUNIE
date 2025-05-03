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


# # ランダムに決定される状態値を[str]型で取得する.
# def random_select2(stts):
#     np.random.seed(None) # シードをリセット
#     # 与えられた各状態値の重み付けを実施する(=自動的に重み値を生成する).
#     wghts = [1.0 / len(stts) for _ in stts]  # 均等な重み付け

#     return np.random.choice(stts, size=10, p=wghts)