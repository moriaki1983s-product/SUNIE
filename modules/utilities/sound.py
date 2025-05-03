# coding: utf-8




# 既成のモジュールをインポートする.
import os
import sys
import numpy as np
import librosa
import soundfile as sf




# # 画像の特徴量抽出
# image = Image.open('example.jpg')
# image_array = np.array(image)

# # 音声の特徴量抽出
# audio, sr = librosa.load('example.wav')
# mfcc = librosa.feature.mfcc(y=audio, sr=sr)

# 特徴量の演算・変換
# 画像のフィルタリング（例：エッジ検出）
from scipy import ndimage
# filtered_image = ndimage.sobel(image_array)

# # 音声のエフェクト（例：ノイズ除去）
# filtered_audio = librosa.effects.preemphasis(audio)

# # 生成・出力
# output_image = Image.fromarray(filtered_image)
# output_image.save('filtered_example.jpg')

# librosa.output.write_wav('filtered_example.wav', filtered_audio, sr)


# # サンプリングレートと周波数の設定
# sr = 22050  # サンプリングレート
# T = 2.0     # 信号の持続時間
# f = 440.0   # 正弦波の周波数

# # 時間軸の生成
# t = np.linspace(0, T, int(T * sr), endpoint=False)

# # 正弦波の生成
# x = 0.5 * np.sin(2 * np.pi * f * t)

# # 音声ファイルとして保存
# sf.write('sine_wave.wav', x, sr)


# このコードでは、22050 Hzのサンプリングレートで、2秒間の440 Hzの正弦波を生成し、それをsine_wave.wavとして保存しています。librosaとsoundfileライブラリを利用することで、音声ファイルの作成が容易に行えます。

# librosaを使ってさらに高度な音声生成や解析を行うことも可能です。質問や他のアイデアがあれば、ぜひ教えてくださいね！💧✨

# def a(dat_strm):
#     samplerate = 48000
#     data = np.asarray(bytearray(dat_strm.read()), dtype=float)
#     sf.write(sttgs.SOUND_ARCHIVE_PATH + "out.wav", data, samplerate, subtype="PCM_24")
#     return (sttgs.SOUND_ARCHIVE_PATH + "out.wav")


# samplerate = 48000    # サンプリングレート
# freq = 1000           # 正弦波の周波数
# n = np.arange(samplerate*2)  # サンプリング番号
# data = np.sin(2.0*np.pi*freq*n/samplerate) # 正弦波作成
# sf.write("out1.wav", data, samplerate, subtype="PCM_24") # 書き込み