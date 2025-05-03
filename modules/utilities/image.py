# coding: utf-8




# 既成のモジュールをインポートする.
import os
import sys
import cv2
import numpy
import pandas
import base64
import random
import datetime
import matplotlib
from matplotlib.ticker import MaxNLocator

matplotlib.use("agg")
from PIL import Image
# from fer import FER

# 設定のためのモジュールをインポートする.
import constants as consts




def load_image(fl_pth):
    img = cv2.imread(fl_pth)

    return img


# 画像データを基に画像ファイルを作成する.
# [img] : 画像データ
# [lbl] : ファイル名の一部として含める修飾語(文)
def create_imagefile(img, lbl):
    if img is None:
        return None, False, "失敗: [img] が渡されていません."
    if lbl is None:
        return None, False, "失敗: [lbl] が渡されていません."
    if lbl == "":
        return None, False, "失敗: [lbl] が空です."

    crrnt_dttm = datetime.datetime.now().strftime("%Y%m%d%H%M%S%f")
    crtd_img_pth = consts.IMAGE_GENERATE_PATH + lbl + "_" + crrnt_dttm + ".jpg"
    cv2.imwrite(crtd_img_pth, img)

    return crtd_img_pth, True, "成功: 画像ファイルの作成ができました."


# (Webフォームの)データストリームから画像データを抽出して元の画像を復元する.
# [dat_strm] : (画像の)データストリーム
def restoration_image_from_datastream(dat_strm):
    if dat_strm is None:
        return None, False, "失敗: [dat_strm] が渡されていません."

    img_arry = numpy.asarray(bytearray(dat_strm.read()), dtype=numpy.uint8)
    rstrtn_img = cv2.imdecode(img_arry, 1)

    return rstrtn_img, True, "成功: 画像データの復元ができました."


# 単色の画像ファイルを作成する.
# [wdth] : 画像の幅
# [hght] : 画像の高さ
# [clr]  : 画像(全体)の色味(=ピクセルの値)
# 「色味」に関する説明~~
# [Red] - 赤色
# [Green] - 緑色
# [Blue] - 青色
# [Cyan] - 水色
# [Magenta] - 紫色
# [Yellow] - 黄色
# [Black] - 黒色
# [White] - 白色
def create_plain_image(wdth, hght, clr):
    if wdth is None:
        return None, False, "失敗: [wdth] が指定されていません."
    if hght is None:
        return None, False, "失敗: [hght] が指定されていません."
    if clr is None:
        return None, False, "失敗: [clr] が指定されていません."
    if isinstance(wdth, int) == False:
        return None, False, "失敗: [wdth] の型が違います."
    if isinstance(hght, int) == False:
        return None, False, "失敗: [hght] の型が違います."
    if isinstance(clr, str) == False:
        return None, False, "失敗: [clr] の型が違います."
    if clr == "":
        return None, False, "失敗: [clr] が空になっています."

    if clr == "Red":
        clr_tmp = (0, 0, 255)
    elif clr == "Green":
        clr_tmp = (0, 255, 0)
    elif clr == "Blue":
        clr_tmp = (255, 0, 0)
    elif clr == "Cyan":
        clr_tmp = (255, 255, 0)
    elif clr == "Magenta":
        clr_tmp = (255, 0, 255)
    elif clr == "Yellow":
        clr_tmp = (0, 255, 255)
    elif clr == "Black":
        clr_tmp = (0, 0, 0)
    elif clr == "White":
        clr_tmp = (255, 255, 255)
    else:
        return None, False, "失敗: [clr] の値が無効です."

    img_fnl = numpy.full(
        shape=(wdth, hght, consts.CV_COLOR_TYPE),
        fill_value=clr_tmp,
        dtype=numpy.uint8,
    )

    return img_fnl, True, "成功: 画像ファイルの作成ができました."


# PC標準のインカメラから送られる画像データを取得する.
def capture_image_by_incamera():
    cam = cv2.VideoCapture(0)

    if cam.isOpened() == False:
        cam.release()
        return None, False, "失敗: カメラが起動しませんでした."

    _, img = cam.read()

    if img is None:
        cam.release()
        return None, False, "失敗: 画像を撮影できませんでした."

    cam.release()

    ret_flg = cv2.imwrite(consts.CV_DETECT_FACE_IMAGE_PATH_AND_NAME, img)

    if ret_flg == False:
        return None, False, "失敗: 顔画像の保存ができませんでした."

    img_fnl = cv2.imread(consts.CV_DETECT_FACE_IMAGE_PATH_AND_NAME)
    return img_fnl, True, "成功: 画像の撮影・保存ができました."


# 指定の画像データのうち, 顔部分のみを切り取ってファイルとして保存する.
# [img] : 画像データ(=顔の含まれているもの)
# [usr_id] : ファイル名として付与するユーザーID
def memorize_face(img, usr_id):
    if img is None:
        return None, False, "失敗: [img] が指定されていません."
    if usr_id is None:
        return None, False, "失敗: [usr_id] が指定されていません."
    if isinstance(img, numpy.ndarray) == False:
        return None, False, "失敗: [img] の型が違います."
    if isinstance(usr_id, int) == False:
        return None, False, "失敗: [usr_id] の型が違います."
    if img.ndim != consts.CV_IMAGE_DIMENSION:
        return None, False, "失敗: [img] の次元数が違います."
    if usr_id < 1 or usr_id > consts.USER_NUMBER:
        return None, False, "失敗: [usr_id] の値が無効です."

    cv_clssfr = cv2.CascadeClassifier(consts.CV_DETECT_FACE_MODEL_PATH_AND_NAME)

    if cv_clssfr is None:
        return None, False, "失敗: [cv_clssfr] の構築ができませんでした."

    min_size = (int(img.shape[0] / 10), int(img.shape[1] / 10))
    faces = cv_clssfr.detectMultiScale(
        img, scaleFactor=1.1, minNeighbors=2, minSize=min_size
    )

    if len(faces) == 0:
        return None, False, "失敗: 顔の検出ができませんでした."

    for x, y, w, h in faces:
        face_img_pth = (
            consts.CV_DETECT_FACE_IMAGE_PATH
            + str(usr_id)
            + consts.CV_IMAGE_FILE_EXTENTION
        )
        ret_flg1 = cv2.imwrite(face_img_pth, img[y : y + h, x : x + w])
        ret_flg2 = cv2.imwrite(
            consts.CV_DETECT_FACE_IMAGE_PATH_AND_NAME, img[y : y + h, x : x + w]
        )
        break

    if ret_flg1 == False or ret_flg2 == False:
        return None, False, "失敗: 顔画像の保存ができませんでした."

    return face_img_pth, True, "成功: 顔画像の保存ができました."


# 画像データに含まれる顔に関する説明解析する(=学習・訓練データを生成する).
# [face_img_pth] : 画像データ(=顔の含まれているもの)が格納されているパス
def analyze_face(face_img_pth):
    face_smpls = []
    face_ids = []
    face_id = 0

    if face_img_pth is None:
        return False, "失敗: [face_img_pth] が指定されていません."
    if isinstance(face_img_pth, str) == False:
        return False, "失敗: [face_img_pth] の型が違います."
    if face_img_pth == "":
        return False, "失敗: [face_img_pth] が空になっています."

    img_bgr = cv2.imread(face_img_pth)
    img_gry = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2GRAY)
    img_nmpy = numpy.array(img_gry, "uint8")

    flnm_with_ext = os.path.split(face_img_pth)[-1]
    flnm = flnm_with_ext.split(".")[0]

    face_smpls.append(img_nmpy)
    face_ids.append(face_id)

    cv_rcgnzr = cv2.face.LBPHFaceRecognizer_create()

    if cv_rcgnzr is None:
        return False, "失敗: [cv_rcgnzr] の構築ができませんでした."

    cv_rcgnzr.train(face_smpls, numpy.array(face_ids))
    cv_rcgnzr.write(
        consts.CV_LEARN_TRAIN_FACE_PATH
        + str(flnm)
        + consts.CV_LEARN_TRAIN_FACE_FILE_EXTENTION
    )

    return True, "成功: 顔の解析ができました."


# 画像データに含まれる顔を照合する(＝照合エラー率を取得する).
# [img] : 画像データ(=顔の含まれるもの)
# [usr_id] : 学習・訓練ファイル(=yml形式)の名前として付与されているユーザーID
def recognize_face(img, usr_id):
    if usr_id is None:
        return None, False, "失敗: [usr_id] が指定されていません."
    if img is None:
        return None, False, "失敗: [img] が指定されていません."
    if isinstance(img, numpy.ndarray) == False:
        return None, False, "失敗: [img] の型が違います."
    if isinstance(usr_id, int) == False:
        return None, False, "失敗: [usr_id] の型が違います."
    if img.ndim != consts.CV_IMAGE_DIMENSION:
        return None, False, "失敗: [img] の次元数が違います."
    if usr_id < 1 or usr_id > consts.USER_NUMBER:
        return None, False, "失敗: [usr_id] の値が無効です."

    cv_rcgnzr = cv2.face.LBPHFaceRecognizer_create()

    if cv_rcgnzr is None:
        return None, False, "失敗: [cv_rcgnzr] の構築ができませんでした."

    cv_rcgnzr.read(
        consts.CV_LEARN_TRAIN_FACE_PATH
        + str(usr_id)
        + consts.CV_LEARN_TRAIN_FACE_FILE_EXTENTION
    )

    img_gry = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    _face_id, err_rt = cv_rcgnzr.predict(img_gry)

    if err_rt == -1:
        return (
            None,
            False,
            "失敗: 顔の照合ができませんでした, 顔が画角からはみ出しているか, カメラの正面を向いていません.",
        )

    return err_rt, True, "成功: 顔の照合に成功しました."


# # 顔画像(=表情)から感情を検出する(=最も強く表れた感情を取得する).
# # [img] : 画像データ(=顔の含まれるもの)
# def detect_emotion(img):
#     if img is None:
#         return None, None, False, "失敗: [img] が指定されていません."
#     if isinstance(img, numpy.ndarray) == False:
#         return None, None, False, "失敗: [img] の型が違います."
#     if img.ndim != consts.CV_IMAGE_DIMENSION:
#         return None, None, False, "失敗: [img] の次元数が違います."

#     fer_rcgnzr = FER(mtcnn=True)
#     typ, scr = fer_rcgnzr.top_emotion(img)

#     if typ is None or scr is None:
#         return (
#             None,
#             None,
#             False,
#             "失敗: 感情種別と感情強度のどちらか, あるいはその両方を取得できませんでした.",
#         )

#     return typ, scr, True, "成功: 感情種別と感情強度の両方を取得できました."


# # 顔画像(=表情)から感情を検出する(=複合する感情をまとめて取得する).
# # [img] : 画像データ(=顔の含まれるもの)
# def detect_emotions(img):
#     if img is None:
#         return None, False, "失敗: [img] が指定されていません."
#     if isinstance(img, numpy.ndarray) == False:
#         return None, False, "失敗: [img] の型が違います."
#     if img.ndim != consts.CV_IMAGE_DIMENSION:
#         return None, False, "失敗: [img] の次元数が違います."

#     fer_rcgnzr = FER(mtcnn=True)
#     typs_and_scrs = fer_rcgnzr.detect_emotions(img)

#     if typs_and_scrs is None:
#         return None, False, "失敗: 感情種別と感情強度の両方を取得できませんでした."

#     return typs_and_scrs, True, "成功: 感情種別と感情強度の両方を取得できました."


# 「detect_emotion」の戻り値である「typ」を日本語の文字列に変換する.
# [typ] : 感情を表す値(=英語文字列)
def convert_emotion_to_string_ja(typ):
    if typ is None:
        return None, False, "失敗: [typ] が指定されていません."
    if isinstance(typ, str) == False:
        return None, False, "失敗: [typ] の型が違います."
    if typ == "":
        return None, False, "失敗: [typ] が空になっています"

    if typ == "angry":
        typ_ja = "憤怒"
    elif typ == "disgust":
        typ_ja = "嫌悪"
    elif typ == "fear":
        typ_ja = "恐怖"
    elif typ == "happy":
        typ_ja = "幸福"
    elif typ == "sad":
        typ_ja = "悲哀"
    elif typ == "surprise":
        typ_ja = "驚愕"
    elif typ == "neutral":
        typ_ja = "普通"
    else:
        return None, False, "失敗: [typ]が無効な値です."

    return typ_ja, True, "成功: 変換できました."


# 「detect_emotion」「convert_emotion_to_string_ja」,
# 上記の戻り値である「typ」を固有の識別番号に変換する.
# [typ] : 感情を表す値(=英語文字列 or 日本語文字列)
def convert_emotion_to_identify_number(typ):
    if typ is None:
        return None, False, "失敗: [typ] が指定されていません."
    if isinstance(typ, str) == False:
        return None, False, "失敗: [typ] の型が違います."
    if typ == "":
        return None, False, "失敗: [typ] が空になっています"

    if typ == "angry" or typ == "憤怒":
        typ_num = 0
    elif typ == "disgust" or typ == "嫌悪":
        typ_num = 1
    elif typ == "fear" or typ == "恐怖":
        typ_num = 2
    elif typ == "happy" or typ == "幸福":
        typ_num = 3
    elif typ == "sad" or typ == "悲哀":
        typ_num = 4
    elif typ == "surprise" or typ == "驚愕":
        typ_num = 5
    elif typ == "neutral" or typ == "普通":
        typ_num = 6
    else:
        return None, False, "失敗: [typ]が無効な値です."

    return typ_num, True, "成功: 識別番号への変換ができました."


# # 感情値を基にグラフを生成して画像ファイルとして保存する.
# # [emtns] : 感情データベースから取得したレコード群
# def generate_emotions_graphs(emtns):
#     is_on_flg_angry = False
#     is_on_flg_disgust = False
#     is_on_flg_fear = False
#     is_on_flg_happy = False
#     is_on_flg_sad = False
#     is_on_flg_surprise = False
#     is_on_flg_neutral = False
#     cols_angry = []
#     cols_disgust = []
#     cols_fear = []
#     cols_happy = []
#     cols_sad = []
#     cols_surprise = []
#     cols_neutral = []
#     ret_flgs = []

#     if emtns is None:
#         return None, False, "失敗: [emtns] が指定されていません."
#     if isinstance(emtns, list) == False:
#         return None, False, "失敗: [emtns] の型が違います."
#     if len(emtns) == 0:
#         return None, False, "失敗: [emtns] が空になっています"
#     if len(emtns[0]) != 6:
#         return None, False, "失敗: [emtns] の要素数が違います"

#     for emtn in emtns:
#         if isinstance(emtn[4], str) == False:
#             return None, False, "失敗: [emtns] の要素の型が違います"
#         if isinstance(emtn[5], str) == False:
#             return None, False, "失敗: [emtns] の要素の型が違います"
#         if emtn[4] == "angry" or emtn[4] == "憤怒":
#             cols_angry.append(float(emtn[5]))
#         if emtn[4] == "disgust" or emtn[4] == "嫌悪":
#             cols_disgust.append(float(emtn[5]))
#         if emtn[4] == "fear" or emtn[4] == "恐怖":
#             cols_fear.append(float(emtn[5]))
#         if emtn[4] == "happy" or emtn[4] == "幸福":
#             cols_happy.append(float(emtn[5]))
#         if emtn[4] == "sad" or emtn[4] == "悲哀":
#             cols_sad.append(float(emtn[5]))
#         if emtn[4] == "surprise" or emtn[4] == "驚愕":
#             cols_surprise.append(float(emtn[5]))
#         if emtn[4] == "neutral" or emtn[4] == "普通":
#             cols_neutral.append(float(emtn[5]))

#     is_on_flg_angry = len(cols_angry) != 0
#     is_on_flg_disgust = len(cols_disgust) != 0
#     is_on_flg_fear = len(cols_fear) != 0
#     is_on_flg_happy = len(cols_happy) != 0
#     is_on_flg_sad = len(cols_sad) != 0
#     is_on_flg_surprise = len(cols_surprise) != 0
#     is_on_flg_neutral = len(cols_neutral) != 0

#     if is_on_flg_angry:
#         df_scr_angry = pandas.DataFrame(cols_angry, columns=["User-Emotion-Angry"])
#     if is_on_flg_disgust:
#         df_scr_disgust = pandas.DataFrame(
#             cols_disgust, columns=["User-Emotion-Disgust"]
#         )
#     if is_on_flg_fear:
#         df_scr_fear = pandas.DataFrame(cols_fear, columns=["User-Emotion-fear"])
#     if is_on_flg_happy:
#         df_scr_happy = pandas.DataFrame(cols_happy, columns=["User-Emotion-Happy"])
#     if is_on_flg_sad:
#         df_scr_sad = pandas.DataFrame(cols_sad, columns=["User-Emotion-Sad"])
#     if is_on_flg_surprise:
#         df_scr_suprise = pandas.DataFrame(
#             cols_surprise, columns=["User-Emotion-Suprise"]
#         )
#     if is_on_flg_neutral:
#         df_scr_neutral = pandas.DataFrame(
#             cols_neutral, columns=["User-Emotion-Neutral"]
#         )

#     if is_on_flg_angry:
#         axs_angry = df_scr_angry.plot.hist(
#             title="angry",
#             grid=False,
#             colormap="Accent",
#             legend=False,
#             alpha=0.5,
#             range=(0.00, 0.99),
#         )

#         axs_angry.yaxis.set_major_locator(MaxNLocator(integer=True))
#         axs_angry.set_xlabel("score")
#         axs_angry.set_ylabel("freq")

#     if is_on_flg_disgust:
#         axs_disgust = df_scr_disgust.plot.hist(
#             title="disgust",
#             grid=False,
#             colormap="Accent",
#             legend=False,
#             alpha=0.5,
#             range=(0.00, 0.99),
#         )

#         axs_disgust.yaxis.set_major_locator(MaxNLocator(integer=True))
#         axs_disgust.set_xlabel("score")
#         axs_disgust.set_ylabel("freq")

#     if is_on_flg_fear:
#         axs_fear = df_scr_fear.plot.hist(
#             title="fear",
#             grid=False,
#             colormap="Accent",
#             legend=False,
#             alpha=0.5,
#             range=(0.00, 0.99),
#         )

#         axs_fear.yaxis.set_major_locator(MaxNLocator(integer=True))
#         axs_fear.set_xlabel("score")
#         axs_fear.set_ylabel("freq")

#     if is_on_flg_happy:
#         axs_happy = df_scr_happy.plot.hist(
#             title="happy",
#             grid=False,
#             colormap="Accent",
#             legend=False,
#             alpha=0.5,
#             range=(0.00, 0.99),
#         )

#         axs_happy.yaxis.set_major_locator(MaxNLocator(integer=True))
#         axs_happy.set_xlabel("score")
#         axs_happy.set_ylabel("freq")

#     if is_on_flg_sad:
#         axs_sad = df_scr_sad.plot.hist(
#             title="sad",
#             grid=False,
#             colormap="Accent",
#             legend=False,
#             alpha=0.5,
#             range=(0.00, 0.99),
#         )

#         axs_sad.yaxis.set_major_locator(MaxNLocator(integer=True))
#         axs_sad.set_xlabel("score")
#         axs_sad.set_ylabel("freq")

#     if is_on_flg_surprise:
#         axs_suprise = df_scr_suprise.plot.hist(
#             title="suprise",
#             grid=False,
#             colormap="Accent",
#             legend=False,
#             alpha=0.5,
#             range=(0.00, 0.99),
#         )

#         axs_suprise.yaxis.set_major_locator(MaxNLocator(integer=True))
#         axs_suprise.set_xlabel("score")
#         axs_suprise.set_ylabel("freq")

#     if is_on_flg_neutral:
#         axs_neutral = df_scr_neutral.plot.hist(
#             title="neutral",
#             grid=False,
#             colormap="Accent",
#             legend=False,
#             alpha=0.5,
#             range=(0.00, 0.99),
#         )

#         axs_neutral.yaxis.set_major_locator(MaxNLocator(integer=True))
#         axs_neutral.set_xlabel("score")
#         axs_neutral.set_ylabel("freq")

#     if is_on_flg_angry:
#         axs_angry.figure.savefig(consts.FER_ANALYZE_MOTION_ANGRY_PATH_AND_NAME)
#     if is_on_flg_disgust:
#         axs_disgust.figure.savefig(consts.FER_ANALYZE_EMOTION_DISGUST_PATH_AND_NAME)
#     if is_on_flg_fear:
#         axs_fear.figure.savefig(consts.FER_ANALYZE_EMOTION_FEAR_PATH_AND_NAME)
#     if is_on_flg_happy:
#         axs_happy.figure.savefig(consts.FER_ANALYZE_EMOTION_HAPPY_PATH_AND_NAME)
#     if is_on_flg_sad:
#         axs_sad.figure.savefig(consts.FER_ANALYZE_EMOTION_SAD_PATH_AND_NAME)
#     if is_on_flg_surprise:
#         axs_suprise.figure.savefig(consts.FER_ANALYZE_EMOTION_SURPRISE_PATH_AND_NAME)
#     if is_on_flg_neutral:
#         axs_neutral.figure.savefig(consts.FER_ANALYZE_EMOTION_NEUTRAL_PATH_AND_NAME)

#     ret_flgs.append(is_on_flg_angry)
#     ret_flgs.append(is_on_flg_disgust)
#     ret_flgs.append(is_on_flg_fear)
#     ret_flgs.append(is_on_flg_happy)
#     ret_flgs.append(is_on_flg_sad)
#     ret_flgs.append(is_on_flg_surprise)
#     ret_flgs.append(is_on_flg_neutral)

#     return ret_flgs, True, "成功: グラフの生成と保存ができました."


# 指定の画像を複製する.
# [img] : 画像データ
def copy_image(img):
    if img is None:
        return None, False, "失敗: [img] が指定されていません."
    if isinstance(img, numpy.ndarray) == False:
        return None, False, "失敗: [img] の型が違います."
    if img.ndim != consts.CV_IMAGE_DIMENSION:
        return None, False, "失敗: [img] の次元数が違います."

    img_cpy = img.copy()

    return img_cpy, True, "成功: 画像データの複製ができました."


# 指定の画像データを解析する.
# [img] : 画像データ
def analyze_image(img):
    cptn = "キャプション : 実装予定"

    if img is None:
        return None, False, "失敗: [img] が指定されていません."
    if isinstance(img, numpy.ndarray) == False:
        return None, False, "失敗: [img] の型が違います."
    if img.ndim != consts.CV_IMAGE_DIMENSION:
        return None, False, "失敗: [img] の次元数が違います."

    return cptn, True, "成功: 画像データの解析ができました."


# # 指定の画像データを基に時刻形式のファイル名を付与された画像ファイルを作成する.
# # [img] : 画像データ
# # [lbl] : (画像ファイルの名前の一部として付与される)レーベル
# def create_image_file_with_timestamp(img, lbl):
#     if img is None:
#         return None, False, "失敗: [img] が指定されていません."
#     if lbl is None:
#         return None, False, "失敗: [lbl] が指定されていません."
#     if isinstance(img, numpy.ndarray) == False:
#         return None, False, "失敗: [img] の型が違います."
#     if isinstance(lbl, str) == False:
#         return None, False, "失敗: [lbl] の型が違います."
#     if img.ndim != consts.CV_IMAGE_DIMENSION:
#         return None, False, "失敗: [img] の次元数が違います."
#     if len(lbl) > consts.LABEL_LENGTH:
#         return None, False, "失敗: [lbl] が長すぎます."

#     dt_now = datetime.datetime.now().strftime("%Y%m%d%H%M%S%f")
#     gnrtd_img_pth = consts.GENERAL_IMAGE_PATH + dt_now + lbl + CV_IMAGE_FILE_EXTENTION
#     ret = cv2.imwrite(gnrtd_img_pth, img)

#     if ret == False:
#         return None, False, "失敗: 画像ファイルの作成ができませんでした."

#     return gnrtd_img_pth, True, "成功: 画像ファイルの作成ができました."


# 指定の画像データの幅・高さと大きさ(=総ピクセル数)を取得する.
# [img] : 画像データ
def retrieve_width_hight_and_size(img):
    if img is None:
        return None, None, None, False, "失敗: 画像情報の取得ができませんでした."
    if isinstance(img, numpy.ndarray) == False:
        return None, None, None, False, "失敗: [img] の型が違います."
    if img.ndim != consts.CV_IMAGE_DIMENSION:
        return None, None, None, False, "失敗: [img] の次元数が違います."

    wdth = img.shape[1]
    hght = img.shape[0]
    size = img.size

    return wdth, hght, size, True, "成功: 画像情報の取得ができました."


# 指定の画像データ内の単一ピクセルを変更する.
# [img] : 画像データ
# [x] : 画像内のx座標
# [y] : 画像内のy座標
# [clr] : 色味(=ピクセルの値)
# 「色味」に関する説明~~
# [Red] - 赤色
# [Green] - 緑色
# [Blue] - 青色
# [Cyan] - 水色
# [Magenta] - 紫色
# [Yellow] - 黄色
# [Black] - 黒色
# [White] - 白色
def change_pixel(img, x, y, clr):
    if img is None:
        return False, "失敗: [img] が指定されていません."
    if x is None:
        return False, "失敗: [x] が指定されていません."
    if y is None:
        return False, "失敗: [y] が指定されていません."
    if clr is None:
        return False, "失敗: [clr] が指定されていません."
    if isinstance(img, numpy.ndarray) == False:
        return False, "失敗: [img] の型が違います."
    if isinstance(x, int) == False:
        return False, "失敗: [x] の型が違います."
    if isinstance(y, int) == False:
        return False, "失敗: [y] の型が違います."
    if isinstance(clr, str) == False:
        return False, "失敗: [clr] の型が違います."
    if img.ndim != consts.CV_IMAGE_DIMENSION:
        return False, "失敗: [img] の次元数が違います."
    if x < 0 or x > img.shape[1]:
        return False, "失敗: [img] に対する [x] の値が無効です."
    if y < 0 or y > img.shape[0]:
        return False, "失敗: [img] に対する [y] の値が無効です."
    if clr == "":
        return False, "失敗: [clr] が空になっています."

    if clr == "Red":
        clr_tmp = (0, 0, 255)
    elif clr == "Green":
        clr_tmp = (0, 255, 0)
    elif clr == "Blue":
        clr_tmp = (255, 0, 0)
    elif clr == "Cyan":
        clr_tmp = (255, 255, 0)
    elif clr == "Magenta":
        clr_tmp = (255, 0, 255)
    elif clr == "Yellow":
        clr_tmp = (0, 255, 255)
    elif clr == "Black":
        clr_tmp = (0, 0, 0)
    elif clr == "White":
        clr_tmp = (255, 255, 255)
    else:
        return False, "失敗: [clr] の値が無効です."

    img[x, y] = clr_tmp
    return True, "成功: ピクセルの変更ができました."


# # 指定の画像データ内の単一ピクセルを取得する.
# # [img] : 画像データ
# # [x] : 画像内のx座標
# # [y] : 画像内のy座標
# def retrieve_pixel(img, x, y):
#     if img is None:
#         return None, False, "失敗: [img] が指定されていません."
#     if x is None:
#         return None, False, "失敗: [x] が指定されていません."
#     if y is None:
#         return None, False, "失敗: [y] が指定されていません."
#     if img is None:
#         return "失敗: [img] が指定されていません."
#     if usr_id is None:
#         return False, "失敗: [usr_id] が指定されていません."
#     if isinstance(img, numpy.ndarray) == False:
#         return False, "失敗: [img] の型が違います."
#     if isinstance(x, int) == False:
#         return False, "失敗: [x] の型が違います."
#     if isinstance(y, int) == False:
#         return False, "失敗: [y] の型が違います."
#     if img.ndim != consts.CV_IMAGE_DIMENSION:
#         return False, "失敗: [img] の次元数が違います."
#     if x < 0 or x > img.shape[1]:
#         return False, "失敗: [img] に対する [x] の値が無効です."
#     if y < 0 or y > img.shape[0]:
#         return False, "失敗: [img] に対する [y] の値が無効です."

#     return img[x, y], True, "成功: ピクセルの取得ができました."


# 指定の画像データ内の矩形範囲内の複数ピクセルを変更する.
# [img] : 画像データ
# [x1] : 画像内の開始x座標
# [y1] : 画像内の開始y座標
# [x2] : 画像内の終了x座標
# [y2] : 画像内の終了y座標
# [clr] : 色味(=ピクセルの値)
# 「色味」に関する説明~~
# [Red] - 赤色
# [Green] - 緑色
# [Blue] - 青色
# [Cyan] - 水色
# [Magenta] - 紫色
# [Yellow] - 黄色
# [Black] - 黒色
# [White] - 白色
def change_pixels_by_rectangle(img, x1, y1, x2, y2, clr):
    if img is None:
        return False, "失敗: [img] が指定されていません."
    if x1 is None:
        return False, "失敗: [x1] が指定されていません."
    if y1 is None:
        return False, "失敗: [y1] が指定されていません."
    if x2 is None:
        return False, "失敗: [x2] が指定されていません."
    if y2 is None:
        return False, "失敗: [y2] が指定されていません."
    if clr is None:
        return False, "失敗: [clr] が指定されていません."
    if isinstance(img, numpy.ndarray) == False:
        return False, "失敗: [img] の型が違います."
    if isinstance(x1, int) == False:
        return False, "失敗: [x1] の型が違います."
    if isinstance(y1, int) == False:
        return False, "失敗: [y1] の型が違います."
    if isinstance(x2, int) == False:
        return False, "失敗: [x2] の型が違います."
    if isinstance(y2, int) == False:
        return False, "失敗: [y2] の型が違います."
    if isinstance(clr, str) == False:
        return False, "失敗: [clr] の型が違います."
    if img.ndim != consts.CV_IMAGE_DIMENSION:
        return False, "失敗: [img] の次元数が違います."
    if clr == "":
        return False, "失敗: [clr] が空になっています."

    if clr == "Red":
        clr_tmp = (0, 0, 255)
    elif clr == "Green":
        clr_tmp = (0, 255, 0)
    elif clr == "Blue":
        clr_tmp = (255, 0, 0)
    elif clr == "Cyan":
        clr_tmp = (255, 255, 0)
    elif clr == "Magenta":
        clr_tmp = (255, 0, 255)
    elif clr == "Yellow":
        clr_tmp = (0, 255, 255)
    elif clr == "Black":
        clr_tmp = (0, 0, 0)
    elif clr == "White":
        clr_tmp = (255, 255, 255)
    else:
        return False, "失敗: [clr] の値が無効です."

    img[x1:y1, x1:y2] = clr_tmp
    return True, "成功: ピクセルの変更ができました."


# 指定の画像データのカラー形式をBGRからRGBに変換する.
# [img] : 画像データ
# ※OpenCVは, BGR形式の画像データしか扱えない.
def convert_image_color_bgr_to_rgb(img):
    if img is None:
        return None, False, "失敗: [img] が指定されていません."
    if isinstance(img, numpy.ndarray) == False:
        return None, False, "失敗: [img] の型が違います."
    if img.ndim != consts.CV_IMAGE_DIMENSION:
        return None, False, "失敗: [img] の次元数が違います."

    img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

    return img_rgb, True, "成功: カラー形式の変換ができました."


# 指定の画像データのカラー形式をRGBからBGRに変換する.
# [img] : 画像データ
# ※OpenCVは, BGR形式の画像データしか扱えない.
def convert_imagecolor_rgb_to_bgr(img):
    if img is None:
        return None, False, "失敗: [img] が指定されていません."
    if isinstance(img, numpy.ndarray) == False:
        return None, False, "失敗: [img] の型が違います."
    if img.ndim != consts.CV_IMAGE_DIMENSION:
        return None, False, "失敗: [img] の次元数が違います."

    img_bgr = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)

    return img_bgr, True, "成功: カラー形式の変換ができました."


# 指定の画像データのサイズを変更する.
# 変更後の幅と高さをピクセルで指定する.
# [img] : 画像データ
# [wdth] : 画像データの幅
# [hght] : 画像データの高さ
def resize_image_by_pixels(img, wdth, hght):
    if img is None:
        return None, False, "失敗: [img] が指定されていません."
    if wdth is None:
        return None, False, "失敗: [wdth] が指定されていません."
    if hght is None:
        return None, False, "失敗: [hght] が指定されていません."
    if isinstance(img, numpy.ndarray) == False:
        return None, False, "失敗: [img] の型が違います."
    if isinstance(wdth, int) == False:
        return None, False, "失敗: [wdth] の型が違います."
    if isinstance(hght, int) == False:
        return None, False, "失敗: [hght] の型が違います."
    if img.ndim != consts.CV_IMAGE_DIMENSION:
        return None, False, "失敗: [img] の次元数が違います."
    if wdth < 0:
        return None, False, "失敗: [wdth] の値が無効です."
    if hght < 0:
        return None, False, "失敗: [hght] の値が無効です."

    img_fnl = cv2.resize(img, (wdth, hght))

    return img_fnl, True, "成功: 画像サイズの変更ができました."


# 指定の画像データのサイズを変更する.
# 変更後の幅と高さを倍率で指定する.
# [img] : 画像データ
# [sx] : 画像データの幅の倍率
# [sy] : 画像データの高さの倍率
def resize_image_by_scales(img, sx, sy):
    if img is None:
        return None, False, "失敗: [img] が指定されていません."
    if sx is None:
        return None, False, "失敗: [sx] が指定されていません."
    if sy is None:
        return None, False, "失敗: [sy] が指定されていません."
    if isinstance(img, numpy.ndarray) == False:
        return None, False, "失敗: [img] の型が違います."
    if isinstance(sx, int) == False:
        return None, False, "失敗: [sx] の型が違います."
    if isinstance(sy, int) == False:
        return None, False, "失敗: [sy] の型が違います."
    if img.ndim != consts.CV_IMAGE_DIMENSION:
        return None, False, "失敗: [img] の次元数が違います."
    if sx == 0:
        return None, False, "失敗: [sx] の値が無効です."
    if sy == 0:
        return None, False, "失敗: [sy] の値が無効です."

    img_fnl = cv2.resize(img, None, sx, sy)

    return img_fnl, True, "成功: 画像サイズの変更ができました."


# 指定の２つの画像データをアルファ合成する.
# [img1] : １つ目の画像データ
# [img2] : ２つ目の画像データ
# [blnd_rto] : 合成の比率
# 「合成の比率」に関する説明~~
# [1:9] : １つ目の画像データを10%, ２つ目の画像データを90%の割合で合成
# [2:8] : １つ目の画像データを20%, ２つ目の画像データを80%の割合で合成
# [3:7] : １つ目の画像データを30%, ２つ目の画像データを70%の割合で合成
# [4:6] : １つ目の画像データを40%, ２つ目の画像データを60%の割合で合成
# [5:5] : １つ目の画像データを50%, ２つ目の画像データを50%の割合で合成
# [6:4] : １つ目の画像データを60%, ２つ目の画像データを40%の割合で合成
# [7:3] : １つ目の画像データを70%, ２つ目の画像データを30%の割合で合成
# [8:2] : １つ目の画像データを80%, ２つ目の画像データを20%の割合で合成
# [9:1] : １つ目の画像データを90%, ２つ目の画像データを10%の割合で合成
def alphablend_image(img1, img2, blnd_rto):
    if img1 is None:
        return None, False, "失敗: [img1] が指定されていません."
    if img2 is None:
        return None, False, "失敗: [img2] が指定されていません."
    if blnd_rto is None:
        return None, False, "失敗: [blnd_rto] が指定されていません."
    if isinstance(img1, numpy.ndarray) == False:
        return None, False, "失敗: [img1] の型が違います."
    if isinstance(img2, numpy.ndarray) == False:
        return None, False, "失敗: [img2] の型が違います."
    if isinstance(blnd_rto, str) == False:
        return None, False, "失敗: [blnd_rto] の型が違います."
    if img1.ndim != consts.CV_IMAGE_DIMENSION:
        return None, False, "失敗: [img1] の次元数が違います."
    if img2.ndim != consts.CV_IMAGE_DIMENSION:
        return None, False, "失敗: [img2] の次元数が違います."
    if blnd_rto == "":
        return None, False, "失敗: [blnd_rto] が空になっています."

    if blnd_rto == "1:9":
        img_fnl = cv2.addWeighted(img1, 0.1, img2, 0.9, 0)
    elif blnd_rto == "2:8":
        img_fnl = cv2.addWeighted(img1, 0.2, img2, 0.8, 0)
    elif blnd_rto == "3:7":
        img_fnl = cv2.addWeighted(img1, 0.3, img2, 0.7, 0)
    elif blnd_rto == "4:6":
        img_fnl = cv2.addWeighted(img1, 0.4, img2, 0.6, 0)
    elif blnd_rto == "5:5":
        img_fnl = cv2.addWeighted(img1, 0.5, img2, 0.5, 0)
    elif blnd_rto == "6:4":
        img_fnl = cv2.addWeighted(img1, 0.6, img2, 0.4, 0)
    elif blnd_rto == "7:3":
        img_fnl = cv2.addWeighted(img1, 0.7, img2, 0.3, 0)
    elif blnd_rto == "8:2":
        img_fnl = cv2.addWeighted(img1, 0.8, img2, 0.2, 0)
    elif blnd_rto == "9:1":
        img_fnl = cv2.addWeighted(img1, 0.9, img2, 0.1, 0)
    else:
        return None, False, "失敗: [blnd_rto] の値が無効です."

    return img_fnl, True, "成功: 画像のアルファ合成ができました."


# 指定の画像データをグレイスケール化する.
# [img] : 画像データ
def convert_image_to_grayscale(img):
    if img is None:
        return None, False, "失敗: [img] が指定されていません."
    if isinstance(img, numpy.ndarray) == False:
        return None, False, "失敗: [img] の型が違います."
    if img.ndim != consts.CV_IMAGE_DIMENSION:
        return None, False, "失敗: [img] の次元数が違います."

    img_gry = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    return img_gry, True, "成功: 画像のグレイスケール化ができました."


# 指定の画像データを２値化(=モノクローム化)する.
# [img] : 画像データ
def convert_image_to_binary(img):
    if img is None:
        return None, False, "失敗: [img] が指定されていません."
    if isinstance(img, numpy.ndarray) == False:
        return None, False, "失敗: [img] の型が違います."
    if img.ndim != consts.CV_IMAGE_DIMENSION:
        return None, False, "失敗: [img] の次元数が違います."

    img_gry = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    _, img_fnl = cv2.threshold(img_gry, 100, 255, cv2.THRESH_BINARY)

    return img_fnl, True, "成功: 画像の２値化(=モノクロ化)ができました."


# 指定の２つの画像データを指定の方法で合成する.
# [img1] : １つ目の画像データ
# [img2] : ２つ目の画像データ
# [cmpst_typ] : 合成の方法
# 「合成の方法」に関する説明~~
# [logical-or] - 論理和
# [logical-and] - 論理積
# [logical-xor] - 排他的論理和
def composit_images(img1, img2, cmpst_typ):
    if img1 is None:
        return None, False, "失敗: [img1] が指定されていません."
    if img2 is None:
        return None, False, "失敗: [img2] が指定されていません."
    if cmpst_typ is None:
        return None, "失敗: [cmpst_typ] が指定されていません."
    if isinstance(img1, numpy.ndarray) == False:
        return None, False, "失敗: [img1] の型が違います."
    if isinstance(img2, numpy.ndarray) == False:
        return None, False, "失敗: [img2] の型が違います."
    if isinstance(cmpst_typ, str) == False:
        return None, False, "失敗: [cmpst_typ] の型が違います."
    if img1.ndim != consts.CV_IMAGE_DIMENSION:
        return None, False, "失敗: [img1] の次元数が違います."
    if img2.ndim != consts.CV_IMAGE_DIMENSION:
        return None, False, "失敗: [img2] の次元数が違います."
    if cmpst_typ == "":
        return None, False, "失敗: [cmpst_typ] が空になっています."

    if cmpst_typ == "logical-or":
        img_fnl = cv2.bitwise_or(img1, img2)
    elif cmpst_typ == "logical-and":
        img_fnl = cv2.bitwise_and(img1, img2)
    elif cmpst_typ == "logical-xor":
        img_fnl = cv2.bitwise_xor(img1, img2)
    else:
        return None, False, "失敗: [cmpst_typ] の値が無効です."

    return img_fnl, True, "成功: 画像データの合成ができました."


# 指定の画像データの色味を反転する.
# [img] : 画像データ
# [invrt_typ] : 反転の方法
# 「反転の方法」に関する説明~~
# [logical-not]           - 論理否定
# [negative-and-positive] - ネガポジ
def invert_imagecolor(img, invrt_typ):
    if img is None:
        return None, "失敗: [img] が指定されていません."
    if invrt_typ is None:
        return None, False, "失敗: [invrt_typ] が指定されていません."
    if isinstance(img, numpy.ndarray) == False:
        return None, False, "失敗: [img] の型が違います."
    if isinstance(invrt_typ, str) == False:
        return None, False, "失敗: [img] の型が違います."
    if img.ndim != consts.CV_IMAGE_DIMENSION:
        return None, False, "失敗: [img] の次元数が違います."
    if invrt_typ == "":
        return None, False, "失敗: [invrt_typ] が空になっています."

    if invrt_typ == "logical-not":
        img_fnl = cv2.bitwise_not(img)
    elif invrt_typ == "negative-and-positive":
        img_fnl = (img * -1) + 255
        img_fnl = numpy.clip(img_fnl, 0, 255).astype(numpy.uint8)
    else:
        return None, False, "失敗: [invrt_typ] の値が無効です."

    return img_fnl, True, "成功: 色味の反転ができました."


# 指定の画像データに指定のフィルターを適用する.
# [img] : 画像データ
# [fltr_typ] : フィルターの種類
# 「フィルターの種類」に関する説明~~
# [Box] - ボックスフィルター
# [Median] - メディアンフィルター
# [Bilateral] - バイラテラルフィルター
# [Gaussian] - ガウシアンフィルター
# [Sobel] - ソーベルフィルター
# [Laplacian] - ラプラシアンフィルター
# [Envoz] - エンヴォスフィルター
# [Previt] - プレヴィットフィルター
# [Sharpen] - シャープンフィルター
def filter_image(img, fltr_typ):
    if img is None:
        return None, "失敗: [img] が指定されていません."
    if fltr_typ is None:
        return None, False, "失敗: [fltr_typ] が指定されていません."
    if isinstance(img, numpy.ndarray) == False:
        return None, False, "失敗: [img] の型が違います."
    if isinstance(fltr_typ, str) == False:
        return None, False, "失敗: [fltr_typ] の型が違います."
    # if img.ndim != consts.CV_IMAGE_DIMENSION:
    #     return None, False, "失敗: [img] の次元数が違います."
    if fltr_typ == "":
        return None, False, "失敗: [fltr_typ] が空になっています."

    if fltr_typ == "Box":
        # img_fnl = cv2.blur(img, -1, (5, 5))
        pass
    elif fltr_typ == "Median":
        img_fnl = cv2.medianBlur(img, 3)
    elif fltr_typ == "Bilateral":
        img_fnl = cv2.bilateralFilter(img, 9, 75, 75)
    elif fltr_typ == "Gaussian":
        img_fnl = cv2.GaussianBlur(img, (5, 5), 0, 0)
    elif fltr_typ == "Sobel":
        img_fnl = cv2.Sobel(img, cv2.CV_64F, 1, 0, 3)
    elif fltr_typ == "Laplacian":
        img_fnl = cv2.filter2D(
            img, cv2.CV_64F, numpy.array([[1, 1, 1], [1, -8, 1], [1, 1, 1]])
        )
    elif fltr_typ == "Envoz":
        img_fnl = cv2.filter2D(
            img, cv2.CV_64F, numpy.array([[0, -1, 0], [0, 0, 0], [0, 1, 0]])
        )
    elif fltr_typ == "Previt":
        img_fnl = cv2.filter2D(
            img, cv2.CV_64F, numpy.array([[-1, -1, -1], [0, 0, 0], [1, 1, 1]])
        )
    elif fltr_typ == "Sharpen":
        img_fnl = cv2.filter2D(
            img, -1, numpy.array([[0, -1, 0], [-1, 5, -1], [0, -1, 0]])
        )
    else:
        return None, False, "失敗: [fltr_typ] の値が無効です."

    return img_fnl, True, "成功: 画像データへのフィルターの適用ができました."


# 指定の画像ファイルから画像データを読込みする.
# [flnm] : 画像ファイルの名前(=拡張子なし)
# ※jpg形式の画像ファイルのみが有効.
# ※[GENERAL_IMAGE_PATH]内が対象.
def read_image(flnm):
    if flnm is None:
        return None, False, "失敗: [flnm] が指定されていません."
    if isinstance(flnm, str) == False:
        return None, False, "失敗: [flnm] の型が違います."
    if flnm == "":
        return None, False, "失敗: [flnm] が空になっています."
    if os.path.exists(consts.GENERAL_IMAGE_PATH) == False:
        return None, False, "失敗: 所定のフォルダーが無くなっています."
    if (
        os.path.exists(
            consts.GENERAL_IMAGE_PATH + flnm + consts.CV_IMAGE_FILE_EXTENTION
        )
        == False
    ):
        return None, False, "失敗: [flnm] によって指定されたファイルが存在しません."

    img_fnl = cv2.imread(
        consts.GENERAL_IMAGE_PATH + flnm + consts.CV_IMAGE_FILE_EXTENTION
    )

    return img_fnl, True, "成功: 画像データの読込みができました."


# # 指定の画像ファイルに画像データを書込みする.
# # [img] : 画像データ
# # [flnm] : 画像ファイルの名前(=拡張子なし)
# # ※jpg形式の画像ファイルのみが有効.
# # ※[GENERAL_IMAGE_PATH]内が対象.
# def write_image(img, flnm):
#     if img is None:
#         return None, False, "失敗: [img] が指定されていません."
#     if flnm is None:
#         return None, False, "失敗: [flnm] が指定されていません."
#     if isinstance(img, numpy.ndarray) == False:
#         return None, False, "失敗: [img] の型が違います."
#     if isinstance(flnm, str) == False:
#         return None, False, "失敗: [flnm] の型が違います."
#     if img.ndim != consts.CV_IMAGE_DIMENSION:
#         return None, False, "失敗: [img] の次元数が違います."
#     if flnm == "":
#         return None, False, "失敗: [flnm] が空になっています."
#     if os.path.exists(consts.GENERAL_IMAGE_PATH) == False:
#         return None, False, "失敗: 所定のフォルダーが無くなっています."

#     ret_flg = cv2.imwrite(
#         consts.GENERAL_IMAGE_PATH + flnm + consts.CV_IMAGE_FILE_EXTENTION
#     )

#     if ret_flg == False:
#         return None, False, "失敗: 画像データの書き込みができませんでした."

#     return flpth_and_flnm, True, "成功: 画像データの書き込みができました."


# 指定の画像データを回転する.
# [img] : 画像データ
# [rot_typ] : 回転の方法
# 「回転の方法」に関する説明~~
# [clock-90deg]       - 時計回り90度
# [conterclock-90deg] - 反時計回り90度
# [180deg]            - 180度
def rotate_image(img, rot_typ):
    if img is None:
        return None, False, "失敗: [img] が指定されていません."
    if rot_typ is None:
        return None, False, "失敗: [rot_typ] が指定されていません."
    if isinstance(img, numpy.ndarray) == False:
        return None, False, "失敗: [img] の型が違います."
    if isinstance(rot_typ, str) == False:
        return None, False, "失敗: [rot_typ] の型が違います."
    # if img.ndim != consts.CV_IMAGE_DIMENSION:
    #     return None, False, "失敗: [img] の次元数が違います."
    if rot_typ == "":
        return None, False, "失敗: [rot_typ] が空になっています."

    if rot_typ == "clock-90deg":
        img_fnl = cv2.rotate(img, cv2.ROTATE_90_CLOCKWISE)
    elif rot_typ == "conterclock-90deg":
        img_fnl = cv2.rotate(img, cv2.ROTATE_90_COUNTERCLOCKWISE)
    elif rot_typ == "180deg":
        img_fnl = cv2.rotate(img, cv2.ROTATE_180)
    else:
        return None, False, "失敗: 画像データの回転ができませんでした."

    return img_fnl, True, "成功: 画像データの回転ができました."


# 指定の画像データに文字列を描画する.
# [img] : 画像データ
# [txt] : 文字列(英数字と半角記号のみ有効)
# [x] : 文字列の左下開始X座標
# [y] : 文字列の左下開始Y座標
# [clr] : 文字の色味(=ピクセルの値)
# 「色味」に関する説明~~
# [Red] - 赤色
# [Green] - 緑色
# [Blue] - 青色
# [Cyan] - 水色
# [Magenta] - 紫色
# [Yellow] - 黄色
# [Black] - 黒色
# [White] - 白色
def draw_text_to_image(img, txt, x, y, clr):
    if img is None:
        return False, "失敗: [img] が指定されていません."
    if txt is None:
        return False, "失敗: [txt] が指定されていません."
    if x is None:
        return False, "失敗: [x] が指定されていません."
    if y is None:
        return False, "失敗: [y] が指定されていません."
    if clr is None:
        return False, "失敗: [clr] が指定されていません."
    if isinstance(img, numpy.ndarray) == False:
        return False, "失敗: [img] の型が違います."
    if isinstance(txt, str) == False:
        return False, "失敗: [img] の型が違います."
    if isinstance(x, int) == False:
        return False, "失敗: [x] の型が違います."
    if isinstance(y, int) == False:
        return False, "失敗: [y] の型が違います."
    if isinstance(clr, str) == False:
        return False, "失敗: [clr] の型が違います."
    if img.ndim != consts.CV_IMAGE_DIMENSION:
        return False, "失敗: [img] の次元数が違います."
    if clr == "":
        return False, "失敗: [clr] が空になっています."

    if clr == "Red":
        clr_tmp = (0, 0, 255)
    elif clr == "Green":
        clr_tmp = (0, 255, 0)
    elif clr == "Blue":
        clr_tmp = (255, 0, 0)
    elif clr == "Cyan":
        clr_tmp = (255, 255, 0)
    elif clr == "Magenta":
        clr_tmp = (255, 0, 255)
    elif clr == "Yellow":
        clr_tmp = (0, 255, 255)
    elif clr == "Black":
        clr_tmp = (0, 0, 0)
    elif clr == "White":
        clr_tmp = (255, 255, 255)
    else:
        return False, "失敗: [clr] の値が無効です."

    cv2.putText(
        img=img,
        text=txt,
        org=(x, y),
        fontFace=consts.CV_FONT_FACE,
        fontScale=consts.CV_FONT_SCALE,
        color=clr_tmp,
        thickness=consts.CV_LINE_THICKNESS,
        lineType=consts.CV_LINE_TYPE,
        bottomLeftOrigin=consts.CV_FONT_BOTTOM_LEFT_ORIGIN,
    )

    return True, "成功: 文字列の描画ができました."


# 指定の画像データに直線を描画する.
# [img] : 画像データ
# [x1] : 直線の開始x座標
# [y1] : 直線の開始y座標
# [x2] : 直線の終了x座標
# [y2] : 直線の終了y座標
# [clr] : 線の色味(=ピクセルの値)
# 「色味」に関する説明~~
# [Red] - 赤色
# [Green] - 緑色
# [Blue] - 青色
# [Cyan] - 水色
# [Magenta] - 紫色
# [Yellow] - 黄色
# [Black] - 黒色
# [White] - 白色
def draw_line_to_image(img, x1, y1, x2, y2, clr):
    if img is None:
        return False, "失敗: [img] が指定されていません."
    if x1 is None:
        return False, "失敗: [x1] が指定されていません."
    if y1 is None:
        return False, "失敗: [y1] が指定されていません."
    if x2 is None:
        return False, "失敗: [x2] が指定されていません."
    if y2 is None:
        return False, "失敗: [y2] が指定されていません."
    if clr is None:
        return False, "失敗: [clr] が指定されていません."
    if clr is None:
        return False, "失敗: [clr] が指定されていません."
    if isinstance(img, numpy.ndarray) == False:
        return False, "失敗: [img] の型が違います."
    if isinstance(x1, int) == False:
        return False, "失敗: [x1] の型が違います."
    if isinstance(y1, int) == False:
        return False, "失敗: [y1] の型が違います."
    if isinstance(x2, int) == False:
        return False, "失敗: [x2] の型が違います."
    if isinstance(y2, int) == False:
        return False, "失敗: [y2] の型が違います."
    if img.ndim != consts.CV_IMAGE_DIMENSION:
        return False, "失敗: [img] の次元数が違います."
    if clr == "":
        return False, "失敗: [clr] が空になっています."

    if clr == "Red":
        clr_tmp = (0, 0, 255)
    elif clr == "Green":
        clr_tmp = (0, 255, 0)
    elif clr == "Blue":
        clr_tmp = (255, 0, 0)
    elif clr == "Cyan":
        clr_tmp = (255, 255, 0)
    elif clr == "Magenta":
        clr_tmp = (255, 0, 255)
    elif clr == "Yellow":
        clr_tmp = (0, 255, 255)
    elif clr == "Black":
        clr_tmp = (0, 0, 0)
    elif clr == "White":
        clr_tmp = (255, 255, 255)
    else:
        return False, "失敗: [clr] の値が無効です."

    cv2.line(
        img=img,
        pt1=(x1, y1),
        pt2=(x2, y2),
        color=clr_tmp,
        thickness=consts.CV_LINE_THICKNESS,
        lineType=consts.CV_LINE_TYPE,
        shift=consts.CV_LINE_SHIFT,
    )

    return True, "成功: 直線の描画ができました."


# # 指定の画像データに円を描画する.
# # [img] : 画像データ
# # [x] : 円の中心のx座標
# # [y] : 円の中心のy座標
# # [rds] : 円の半径
# # [clr] : 線の色味(=ピクセルの値)
# # [is_fil] : 塗り潰しの制御
# # 「色味」に関する説明~~
# # [Red] - 赤色
# # [Green] - 緑色
# # [Blue] - 青色
# # [Cyan] - 水色
# # [Magenta] - 紫色
# # [Yellow] - 黄色
# # [Black] - 黒色
# # [White] - 白色
# def draw_circle_to_image(img, x, y, rds, clr, is_fil):
#     if img is None:
#         return False, "失敗: [img] が指定されていません."
#     if txt is None:
#         return False, "失敗: [txt] が指定されていません."
#     if x is None:
#         return False, "失敗: [x] が指定されていません."
#     if y is None:
#         return False, "失敗: [y] が指定されていません."
#     if clr is None:
#         return False, "失敗: [clr] が指定されていません."
#     if isinstance(img, numpy.ndarray) == False:
#         return False, "失敗: [img] の型が違います."
#     if isinstance(x, int) == False:
#         return False, "失敗: [x] の型が違います."
#     if isinstance(y, int) == False:
#         return False, "失敗: [y] の型が違います."
#     if isinstance(rds, int) == False:
#         return False, "失敗: [rds] の型が違います."
#     if isinstance(clr, str) == False:
#         return False, "失敗: [clr] の型が違います."
#     if img.ndim != consts.CV_IMAGE_DIMENSION:
#         return False, "失敗: [img] の次元数が違います."
#     if clr == "":
#         return False, "失敗: [clr] が空になっています."

#     if clr == "Red":
#         clr_tmp = (0, 0, 255)
#     elif clr == "Green":
#         clr_tmp = (0, 255, 0)
#     elif clr == "Blue":
#         clr_tmp = (255, 0, 0)
#     elif clr == "Cyan":
#         clr_tmp = (255, 255, 0)
#     elif clr == "Magenta":
#         clr_tmp = (255, 0, 255)
#     elif clr == "Yellow":
#         clr_tmp = (0, 255, 255)
#     elif clr == "Black":
#         clr_tmp = (0, 0, 0)
#     elif clr == "White":
#         clr_tmp = (255, 255, 255)
#     else:
#         return "失敗: [clr] の値が無効です."

#     if is_fil == True:
#         cv2.circle(
#             img=img,
#             center=(x, y),
#             radius=rds,
#             color=clr_tmp,
#             thickness=-1,
#             lineType=consts.CV_LINE_TYPE,
#             shift=consts.CV_LINE_SHIFT,
#         )

#     if is_fil == False:
#         cv2.circle(
#             img=img,
#             center=(x, y),
#             radius=rds,
#             color=clr_tmp,
#             thickness=consts.CV_LINE_THICKNESS,
#             lineType=consts.CV_LINE_TYPE,
#             shift=consts.CV_LINE_SHIFT,
#         )

#     return True, "成功: 円の描画ができました."


# # 指定の画像データに楕円を描画する.
# # [img] : 画像データ
# # [x] : 楕円の中心x座標
# # [y] : 楕円の中心y座標
# # [a] : 楕円の横方向の半径
# # [b] : 楕円の縦方向の半径
# # [dec_ang] : 楕円の偏角(=回転角)
# # [clr] : 線の色味(=ピクセルの値)
# # [is_fil] : 塗り潰しの制御
# # 「色味」に関する説明~~
# # [Red] - 赤色
# # [Green] - 緑色
# # [Blue] - 青色
# # [Cyan] - 水色
# # [Magenta] - 紫色
# # [Yellow] - 黄色
# # [Black] - 黒色
# # [White] - 白色
# def draw_ellipse_to_image(img, x, y, a, b, dec_ang, clr, is_fil):
#     if img is None:
#         return False, "失敗: [img] が指定されていません."
#     if x is None:
#         return False, "失敗: [x] が指定されていません."
#     if y is None:
#         return False, "失敗: [y] が指定されていません."
#     if a is None:
#         return False, "失敗: [a] が指定されていません."
#     if b is None:
#         return False, "失敗: [b] が指定されていません."
#     if ang is None:
#         return False, "失敗: [ang] が指定されていません."
#     if clr is None:
#         return False, "失敗: [clr] が指定されていません."
#     if isinstance(img, numpy.ndarray) == False:
#         return False, "失敗: [img] の型が違います."
#     if isinstance(x, int) == False:
#         return False, "失敗: [x] の型が違います."
#     if isinstance(y, int) == False:
#         return False, "失敗: [y] の型が違います."
#     if isinstance(a, int) == False:
#         return False, "失敗: [a] の型が違います."
#     if isinstance(b, int) == False:
#         return False, "失敗: [b] の型が違います."
#     if isinstance(ang, int) == False:
#         return False, "失敗: [ang] の型が違います."
#     if isinstance(clr, str) == False:
#         return False, "失敗: [clr] の型が違います."
#     if img.ndim != consts.CV_IMAGE_DIMENSION:
#         return False, "失敗: [img] の次元数が違います."
#     if clr == "":
#         return False, "失敗: [clr] が空になっています."

#     if clr == "Red":
#         clr_tmp = (0, 0, 255)
#     elif clr == "Green":
#         clr_tmp = (0, 255, 0)
#     elif clr == "Blue":
#         clr_tmp = (255, 0, 0)
#     elif clr == "Cyan":
#         clr_tmp = (255, 255, 0)
#     elif clr == "Magenta":
#         clr_tmp = (255, 0, 255)
#     elif clr == "Yellow":
#         clr_tmp = (0, 255, 255)
#     elif clr == "Black":
#         clr_tmp = (0, 0, 0)
#     elif clr == "White":
#         clr_tmp = (255, 255, 255)
#     else:
#         return False, "失敗: [clr] の値が無効です."

#     if is_fil == True:
#         cv2.ellipse(
#             img,
#             center=(x, y),
#             axes=(a, b),
#             angle=dec_ang,
#             startAngle=0,
#             endAngle=360,
#             color=clr_tmp,
#             thickness=-1,
#             lineType=consts.CV_LINE_TYPE,
#             shift=consts.CV_LINE_SHIFT,
#         )

#     if is_fil == False:
#         cv2.ellipse(
#             img,
#             center=(x, y),
#             axes=(a, b),
#             angle=dec_ang,
#             startAngle=0,
#             endAngle=360,
#             color=clr_tmp,
#             thickness=consts.CV_LINE_THICKNESS,
#             lineType=consts.CV_LINE_TYPE,
#             shift=consts.CV_LINE_SHIFT,
#         )

#     return True, "成功: 楕円の描画ができました."


# # 指定の画像データに円弧を描画する.
# # [img] : 画像データ
# # [x] : 円弧の中心x座標
# # [y] : 円弧の中心y座標
# # [a] : 円弧の横方向の半径
# # [b] : 円弧の縦方向の半径
# # [dec_ang] : 円弧の偏角(=回転角)
# # [bgn_ang] : 円弧の開始角
# # [end_ang] : 円弧の終了角
# # [clr] : 線の色味(=ピクセルの値)
# # [is_fil] : 塗り潰しの制御
# # 「色味」に関する説明~~
# # [Red] - 赤色
# # [Green] - 緑色
# # [Blue] - 青色
# # [Cyan] - 水色
# # [Magenta] - 紫色
# # [Yellow] - 黄色
# # [Black] - 黒色
# # [White] - 白色
# def draw_arc_to_image(img, x, y, a, b, dec_ang, bgn_ang, end_ang, clr, is_fil):
#     if img is None:
#         return False, "失敗: [img] が指定されていません."
#     if x is None:
#         return False, "失敗: [x] が指定されていません."
#     if y is None:
#         return False, "失敗: [y] が指定されていません."
#     if a is None:
#         return False, "失敗: [a] が指定されていません."
#     if b is None:
#         return False, "失敗: [b] が指定されていません."
#     if ang is None:
#         return False, "失敗: [ang] が指定されていません."
#     if clr is None:
#         return False, "失敗: [clr] が指定されていません."
#     if isinstance(img, numpy.ndarray) == False:
#         return False, "失敗: [img] の型が違います."
#     if isinstance(x, int) == False:
#         return False, "失敗: [x] の型が違います."
#     if isinstance(y, int) == False:
#         return False, "失敗: [y] の型が違います."
#     if isinstance(a, int) == False:
#         return False, "失敗: [a] の型が違います."
#     if isinstance(b, int) == False:
#         return False, "失敗: [b] の型が違います."
#     if isinstance(ang, int) == False:
#         return False, "失敗: [ang] の型が違います."
#     if isinstance(clr, str) == False:
#         return False, "失敗: [clr] の型が違います."
#     if img.ndim != consts.CV_IMAGE_DIMENSION:
#         return False, "失敗: [img] の次元数が違います."
#     if clr == "":
#         return False, "失敗: [clr] が空になっています."

#     if clr == "Red":
#         clr_tmp = (0, 0, 255)
#     elif clr == "Green":
#         clr_tmp = (0, 255, 0)
#     elif clr == "Blue":
#         clr_tmp = (255, 0, 0)
#     elif clr == "Cyan":
#         clr_tmp = (255, 255, 0)
#     elif clr == "Magenta":
#         clr_tmp = (255, 0, 255)
#     elif clr == "Yellow":
#         clr_tmp = (0, 255, 255)
#     elif clr == "Black":
#         clr_tmp = (0, 0, 0)
#     elif clr == "White":
#         clr_tmp = (255, 255, 255)
#     else:
#         return False, "失敗: [clr] の値が無効です."

#     if is_fil == True:
#         cv2.ellipse(
#             img,
#             center=(x, y),
#             axes=(a, b),
#             angle=dec_ang,
#             startAngle=bgn_ang,
#             endAngle=end_ang,
#             color=clr_tmp,
#             thickness=-1,
#             lineType=consts.CV_LINE_TYPE,
#             shift=consts.CV_LINE_SHIFT,
#         )

#     if is_fil == False:
#         cv2.ellipse(
#             img,
#             center=(x, y),
#             axes=(a, b),
#             angle=dec_ang,
#             startAngle=bgn_ang,
#             endAngle=end_ang,
#             color=clr_tmp,
#             thickness=consts.CV_LINE_THICKNESS,
#             lineType=consts.CV_LINE_TYPE,
#             shift=consts.CV_LINE_SHIFT,
#         )

#     return True, "成功: 楕円の描画ができました."


# 指定の画像データに矩形を描画する.
# [img] : 画像データ
# [x1] : 矩形の開始x座標
# [y1] : 矩形の開始y座標
# [x2] : 矩形の終了x座標
# [y2] : 矩形の終了y座標
# [clr] : 線の色味(=ピクセルの値)
# [is_fil] : 塗り潰しの制御
# 「色味」に関する説明~~
# [Red] - 赤色
# [Green] - 緑色
# [Blue] - 青色
# [Cyan] - 水色
# [Magenta] - 紫色
# [Yellow] - 黄色
# [Black] - 黒色
# [White] - 白色
def draw_rectangle_to_image(img, x1, y1, x2, y2, clr, is_fil):
    if img is None:
        return False, "失敗: [img] が指定されていません."
    if x1 is None:
        return False, "失敗: [x1] が指定されていません."
    if y1 is None:
        return False, "失敗: [y1] が指定されていません."
    if x2 is None:
        return False, "失敗: [x2] が指定されていません."
    if y2 is None:
        return False, "失敗: [y2] が指定されていません."
    if clr is None:
        return False, "失敗: [clr] が指定されていません."
    if isinstance(img, numpy.ndarray) == False:
        return False, "失敗: [img] の型が違います."
    if isinstance(x1, int) == False:
        return False, "失敗: [x1] の型が違います."
    if isinstance(y1, int) == False:
        return False, "失敗: [y1] の型が違います."
    if isinstance(x2, int) == False:
        return False, "失敗: [x2] の型が違います."
    if isinstance(y2, int) == False:
        return False, "失敗: [y2] の型が違います."
    if img.ndim != consts.CV_IMAGE_DIMENSION:
        return False, "失敗: [img] の次元数が違います."
    if clr == "":
        return False, "失敗: [clr] が空になっています."

    if clr == "Red":
        clr_tmp = (0, 0, 255)
    elif clr == "Green":
        clr_tmp = (0, 255, 0)
    elif clr == "Blue":
        clr_tmp = (255, 0, 0)
    elif clr == "Cyan":
        clr_tmp = (255, 255, 0)
    elif clr == "Magenta":
        clr_tmp = (255, 0, 255)
    elif clr == "Yellow":
        clr_tmp = (0, 255, 255)
    elif clr == "Black":
        clr_tmp = (0, 0, 0)
    elif clr == "White":
        clr_tmp = (255, 255, 255)
    else:
        return False, "失敗: [clr] の値が無効です."

    if is_fil == True:
        cv2.rectangle(
            img,
            pt1=(x1, y1),
            pt2=(x2, y2),
            color=clr_tmp,
            thickness=-1,
            lineType=consts.CV_LINE_TYPE,
            shift=consts.CV_LINE_SHIFT,
        )

    if is_fil == False:
        cv2.rectangle(
            img,
            pt1=(x1, y1),
            pt2=(x2, y2),
            color=clr_tmp,
            thickness=consts.CV_LINE_THICKNESS,
            lineType=consts.CV_LINE_TYPE,
            shift=consts.CV_LINE_SHIFT,
        )

    return True, "成功: 矩形の描画ができました."


# 指定の画像データに多角形を(塗り潰しなし)を描画する.
# [clr] : 色味(=ピクセルの値)

# polylines関数 : 複数の座標を結ぶことで、画像内へ折れ線を描画する関数。
# polylines関数 - 公式ドキュメント : https://docs.opencv.org/3.4.0/d6/d6e/group__imgproc__draw.html#gaa3c25f9fb764b6bef791bf034f6e26f5

# 第一引数(必須) : 多次元配列(画像情報)

###############################
# 第二引数(必須) : 複数の座標。numpy.ndarray型。
# numpy.ndarray型とは? : https://note.nkmk.me/python-list-array-numpy-ndarray/
# 例) : [np.array([(100, 150), (50, 200), (30, 20)])] ⏩ (x座標100px, y座標150px)と(x座標50px, y座標200px)を結ぶ。(x座標50px, y座標200px)と(x座標30px, y座標20px)を結ぶ。
# ※ 第二引数を指定する際は、画像の左上角が(0, 0)であることに留意する。
############################### 

# 第三引数(必須) : 複数の座標(第二引数)の始点と終点を結ぶのか指定する。
# 始点とは? : https://www.weblio.jp/content/%E5%A7%8B%E7%82%B9#:~:text=%E3%81%97%E2%80%90%E3%81%A6%E3%82%93%E3%80%90%E5%A7%8B%E7%82%B9%E3%80%91,%E2%87%94%E7%B5%82%E7%82%B9%E3%80%82
# 終点とは? : https://dictionary.goo.ne.jp/word/%E7%B5%82%E7%82%B9/
# True(始点と終点を結ぶ) or False(始点と終点を結ばない)で設定します。
# 第二引数の値が、[np.array([(100, 150), (50, 200), (30, 20)])]の場合、(100, 150)と(30, 20)を結ぶのか設定すると考えると良いでしょう。
# 例) : True ⏩ 複数の座標(第二引数)の始点と終点を結ぶ。

###############################
# 第四引数(必須) : 折れ線の色を指定する。B(Blue)G(Green)R(Red)形式で指定する。tuple型。
# 例) : (255, 0, 0) ⏩ 折れ線の色を青色にする。
# 以下のサイトを利用して、折れ線の色を考えると良いでしょう。
# https://www.peko-step.com/tool/tfcolor.html
###############################

# <第五引数以降(順不同、任意)>
# thickness : 折れ線の太さ(px)を指定する。int型(0以上の整数)。デフォルト(thicknessを指定しない場合)は1が設定される。
# 0を指定する場合、デフォルト(thicknessを指定しない場合)と同じ(1)になる。
# 例) thickness=4 ⏩ 折れ線の太さを4pxとする。

# lineType : 折れ線の種類を指定する。cv2.LINE_4(4連結)、cv2.LINE_8(8連結)、cv2.LINE_AA(アンチエイリアス)のどれかを指定する。
# デフォルト(lineTypeを指定しない場合)はcv2.LINE_8が設定される。
# アンチエイリアスとは? : https://e-words.jp/w/%E3%82%A2%E3%83%B3%E3%83%81%E3%82%A8%E3%82%A4%E3%83%AA%E3%82%A2%E3%82%B9.html
# cv2.LINE_4(4連結)、cv2.LINE_8(8連結)は、ブレゼンハムのアルゴリズムを用いて折れ線を描画する。
# ブレゼンハムのアルゴリズムとは? : https://ja.wikipedia.org/wiki/%E3%83%96%E3%83%AC%E3%82%BC%E3%83%B3%E3%83%8F%E3%83%A0%E3%81%AE%E3%82%A2%E3%83%AB%E3%82%B4%E3%83%AA%E3%82%BA%E3%83%A0
# また太い折れ線の(thicknessの値が大きい)の端は丸く描画されます。

# shift : 第二引数の座標位置をずらすために利用します。int型(0以上の整数)。デフォルト(shiftを指定しない場合)は0が設定される。
# (x * 2^(-shift), y * 2^(-shift))の結果を、第二引数の値とする。
# 例) 第二引数を[np.array([(100, 150), (50, 200), (30, 20)])]、shiftへ1を指定すると、第二引数を[np.array([(50, 75), (25, 100), (15, 10)])]に変更される。
# cv2.polylines(img, [np.array([(整数, 整数), (整数, 整数), ...])], True or False, (0~255の整数, 0~255の整数, 0~255の整数), thickness=0以上の整数, lineType=(cv2.LINE_4, cv2.LINE_8, cv2.LINE_AA)のどれか, shift=0以上の整数)
# cv2.polylines(img, [np.array([(200, 200), (210, 230), (300, 260), (350, 300)])], False, (255, 255, 0), thickness=3)
# def draw():
#     img = cv2.polyLines(img, [pts], isClosed, color)


# 指定の画像データに多角形を(塗り潰しなし)を描画する.
# [clr] : 色味(=ピクセルの値)

# fillPoly関数 : 複数の座標を結ぶことで、画像内へ多角形を描画する関数。
# fillPoly関数 - 公式ドキュメント : https://docs.opencv.org/3.4.0/d6/d6e/group__imgproc__draw.html#ga311160e71d37e3b795324d097cb3a7dc

# 第一引数(必須) : 多次元配列(画像情報)

###############################
# 第二引数(必須) : 複数の座標。numpy.ndarray型。
# numpy.ndarray型とは? : https://note.nkmk.me/python-list-array-numpy-ndarray/
# 例) : [np.array([(100, 150), (50, 200), (30, 20)])] ⏩ (x座標100px, y座標150px)と(x座標50px, y座標200px)を結ぶ。(x座標50px, y座標200px)と(x座標30px, y座標20px)を結ぶ。(x座標30px, y座標20px)と(x座標100px, y座標150px)を結ぶ。
# ※ 第二引数を指定する際は、画像の左上角が(0, 0)であることに留意する。
############################### 

###############################
# 第三引数(必須) : 多角形の色を指定する。B(Blue)G(Green)R(Red)形式で指定する。tuple型。
# tuple型とは? : https://atmarkit.itmedia.co.jp/ait/articles/1906/14/news015.html
# 例) : (255, 0, 0) ⏩ 多角形の色を青色にする。
# 以下のサイトを利用して、多角形の色を考えると良いでしょう。
# https://www.peko-step.com/tool/tfcolor.html
###############################

# <第四引数以降(順不同、任意)>
# lineType : 多角形の枠線の種類を指定する。cv2.LINE_4(4連結)、cv2.LINE_8(8連結)、cv2.LINE_AA(アンチエイリアス)のどれかを指定する。
# デフォルト(lineTypeを指定しない場合)はcv2.LINE_8が設定される。
# アンチエイリアスとは? : https://e-words.jp/w/%E3%82%A2%E3%83%B3%E3%83%81%E3%82%A8%E3%82%A4%E3%83%AA%E3%82%A2%E3%82%B9.html
# cv2.LINE_4(4連結)、cv2.LINE_8(8連結)は、ブレゼンハムのアルゴリズムを用いて多角形の枠線を描画する。
# ブレゼンハムのアルゴリズムとは? : https://ja.wikipedia.org/wiki/%E3%83%96%E3%83%AC%E3%82%BC%E3%83%B3%E3%83%8F%E3%83%A0%E3%81%AE%E3%82%A2%E3%83%AB%E3%82%B4%E3%83%AA%E3%82%BA%E3%83%A0

# shift : 第二引数の座標位置をずらすために利用します。int型(0以上の整数)。デフォルト(shiftを指定しない場合)は0が設定される。
# (x * 2^(-shift), y * 2^(-shift))の結果を、第二引数の値とする。
# 例) 第二引数を[np.array([(100, 150), (50, 200), (30, 20)])]、shiftへ1を指定すると、第二引数を[np.array([(50, 75), (25, 100), (15, 10)])]に変更する。

# offset : 第二引数で指定した座標を平行移動するために、利用します。tuple型。デフォルト(offsetを指定しない場合)は(0, 0)が設定される。
# 平行移動とは? : https://manapedia.jp/text/2505
# 例) : 第二引数を[np.array([(100, 150), (50, 200), (30, 20)])]、offsetへ(10, 20)を指定すると、第二引数を[np.array([(110, 170), (60, 220), (40, 40)])]に変更する。
#cv2.fillPoly(img, [np.array([(整数, 整数), (整数, 整数), ...])], (0~255の整数, 0~255の整数, 0~255の整数), lineType=(cv2.LINE_4, cv2.LINE_8, cv2.LINE_AA)のどれか, shift=0以上の整数, offset=(整数, 整数))
#cv2.fillPoly(img, [np.array([(210, 200), (220, 300), (300, 340), (340, 220)])], (255, 0, 0))
# def draw():
#     img = cv2.fillPoly(img, [pts], color)


# 指定の画像データに多角形を(塗り潰しなし)を描画する.
# [clr] : 色味(=ピクセルの値)

# fillConvexPoly関数 : 複数の座標を結ぶことで、画像内へ多角形を描画する関数。
# fillConvexPoly関数 - 公式ドキュメント : https://docs.opencv.org/3.4.0/d6/d6e/group__imgproc__draw.html#ga9bb982be9d641dc51edd5e8ae3624e1f

# 第一引数(必須) : 多次元配列(画像情報)

###############################
# 第二引数(必須) : 複数の座標。numpy.ndarray型。
# numpy.ndarray型とは? : https://note.nkmk.me/python-list-array-numpy-ndarray/
# 例) : np.array([(100, 150), (50, 200), (30, 20)]) ⏩ (x座標100px, y座標150px)と(x座標50px, y座標200px)を結ぶ。(x座標50px, y座標200px)と(x座標30px, y座標20px)を結ぶ。(x座標30px, y座標20px)と(x座標100px, y座標150px)を結ぶ。
# ※ 第二引数を指定する際は、画像の左上角が(0, 0)であることに留意する。
###############################

###############################
# 第三引数(必須) : 多角形の色を指定する。B(Blue)G(Green)R(Red)形式で指定する。tuple型。
# tuple型とは? : https://atmarkit.itmedia.co.jp/ait/articles/1906/14/news015.html
# 例) : (255, 0, 0) ⏩ 多角形の色を青色にする。
# 以下のサイトを利用して、多角形の色を考えると良いでしょう。
# https://www.peko-step.com/tool/tfcolor.html
###############################

# <第四引数以降(順不同、任意)>
# lineType : 多角形の枠線の種類を指定する。cv2.LINE_4(4連結)、cv2.LINE_8(8連結)、cv2.LINE_AA(アンチエイリアス)のどれかを指定する。
# デフォルト(lineTypeを指定しない場合)はcv2.LINE_8が設定される。
# アンチエイリアスとは? : https://e-words.jp/w/%E3%82%A2%E3%83%B3%E3%83%81%E3%82%A8%E3%82%A4%E3%83%AA%E3%82%A2%E3%82%B9.html
# cv2.LINE_4(4連結)、cv2.LINE_8(8連結)は、ブレゼンハムのアルゴリズムを用いて多角形の枠線を描画する。
# ブレゼンハムのアルゴリズムとは? : https://ja.wikipedia.org/wiki/%E3%83%96%E3%83%AC%E3%82%BC%E3%83%B3%E3%83%8F%E3%83%A0%E3%81%AE%E3%82%A2%E3%83%AB%E3%82%B4%E3%83%AA%E3%82%BA%E3%83%A0

# shift : 第二引数の座標位置をずらすために利用します。int型(0以上の整数)。デフォルト(shiftを指定しない場合)は0が設定される。
# (x * 2^(-shift), y * 2^(-shift))の結果を、第二引数の値とする。
# 例) 第二引数をnp.array([(100, 150), (50, 200), (30, 20)])、shiftへ1を指定すると、第二引数をnp.array([(50, 75), (25, 100), (15, 10)])に変更する。

#cv2.fillConvexPoly(img, np.array([(整数, 整数), (整数, 整数), ...]), (0~255の整数, 0~255の整数, 0~255の整数), lineType=(cv2.LINE_4, cv2.LINE_8, cv2.LINE_AA)のどれか, shift=0以上の整数)
#cv2.fillConvexPoly(img, np.array([(210, 200), (220, 300), (300, 340), (340, 220)]), (255, 0, 0))
# def draw():
#     img = cv2.fillConvexPoly(img, pts, color)


# 指定の画像データに矢印線を描画する.
# [img] : 画像データ
# [x1] : 矢印線の開始x座標
# [y1] : 矢印線の開始y座標
# [x2] : 矢印線の終了x座標
# [y2] : 矢印線の終了y座標
# [clr] : 線の色味(=ピクセルの値)
# 「色味」に関する説明~~
# [Red] - 赤色
# [Green] - 緑色
# [Blue] - 青色
# [Cyan] - 水色
# [Magenta] - 紫色
# [Yellow] - 黄色
# [Black] - 黒色
# [White] - 白色
def draw_arrowedline_to_image(img, x1, y1, x2, y2, clr):
    if img is None:
        return False, "失敗: [img] が指定されていません."
    if x1 is None:
        return False, "失敗: [x1] が指定されていません."
    if y1 is None:
        return False, "失敗: [y1] が指定されていません."
    if x2 is None:
        return False, "失敗: [x2] が指定されていません."
    if y2 is None:
        return False, "失敗: [y2] が指定されていません."
    if clr is None:
        return False, "失敗: [clr] が指定されていません."
    if isinstance(img, numpy.ndarray) == False:
        return False, "失敗: [img] の型が違います."
    if isinstance(x1, int) == False:
        return False, "失敗: [x1] の型が違います."
    if isinstance(y1, int) == False:
        return False, "失敗: [y1] の型が違います."
    if isinstance(x2, int) == False:
        return False, "失敗: [x2] の型が違います."
    if isinstance(y2, int) == False:
        return False, "失敗: [y2] の型が違います."
    if img.ndim != consts.CV_IMAGE_DIMENSION:
        return False, "失敗: [img] の次元数が違います."
    if clr == "":
        return False, "失敗: [clr] が空になっています."

    if clr == "Red":
        clr_tmp = (0, 0, 255)
    elif clr == "Green":
        clr_tmp = (0, 255, 0)
    elif clr == "Blue":
        clr_tmp = (255, 0, 0)
    elif clr == "Cyan":
        clr_tmp = (255, 255, 0)
    elif clr == "Magenta":
        clr_tmp = (255, 0, 255)
    elif clr == "Yellow":
        clr_tmp = (0, 255, 255)
    elif clr == "Black":
        clr_tmp = (0, 0, 0)
    elif clr == "White":
        clr_tmp = (255, 255, 255)
    else:
        return False, "失敗: [clr] の値が無効です."

    cv2.arrowedLine(
        img=img,
        pt1=(x1, y1),
        pt2=(x2, y2),
        color=clr_tmp,
        thickness=consts.CV_LINE_THICKNESS,
        line_type=consts.CV_LINE_TYPE,
        shift=consts.CV_LINE_SHIFT,
        tipLength=consts.CV_LINE_TIP_LENGTH,
    )

    return True, "成功: 矢印線の描画ができました."


# 指定の画像データにマーカーを描画する.
# [img] : 画像データ
# [x] : マーカーのx座標
# [y] : マーカーのy座標
# [clr] : 線の色味(=ピクセルの値)
# 「色味」に関する説明~~
# [Red] - 赤色
# [Green] - 緑色
# [Blue] - 青色
# [Cyan] - 水色
# [Magenta] - 紫色
# [Yellow] - 黄色
# [Black] - 黒色
# [White] - 白色
def draw_marker_to_image(img, x, y, clr):
    if img is None:
        return False, "失敗: [img] が指定されていません."
    if x is None:
        return False, "失敗: [x] が指定されていません."
    if y is None:
        return False, "失敗: [y] が指定されていません."
    if clr is None:
        return False, "失敗: [clr] が指定されていません."
    if isinstance(img, numpy.ndarray) == False:
        return False, "失敗: [img] の型が違います."
    if isinstance(x, int) == False:
        return False, "失敗: [x] の型が違います."
    if isinstance(y, int) == False:
        return False, "失敗: [y] の型が違います."
    if img.ndim != consts.CV_IMAGE_DIMENSION:
        return False, "失敗: [img] の次元数が違います."
    if clr == "":
        return False, "失敗: [clr] が空になっています."

    if clr == "Red":
        clr_tmp = (0, 0, 255)
    elif clr == "Green":
        clr_tmp = (0, 255, 0)
    elif clr == "Blue":
        clr_tmp = (255, 0, 0)
    elif clr == "Cyan":
        clr_tmp = (255, 255, 0)
    elif clr == "Magenta":
        clr_tmp = (255, 0, 255)
    elif clr == "Yellow":
        clr_tmp = (0, 255, 255)
    elif clr == "Black":
        clr_tmp = (0, 0, 0)
    elif clr == "White":
        clr_tmp = (255, 255, 255)
    else:
        return False, "失敗: [clr] の値が無効です."

    cv2.drawMarker(
        img=img,
        position=(x, y),
        color=clr_tmp,
        markerType=consts.CV_LINE_MARKER_TYPE,
        markerSize=consts.CV_LINE_MARKER_SIZE,
        thickness=consts.CV_LINE_THICKNESS,
        line_type=consts.CV_LINE_TYPE
    )

    return True, "成功: マーカーの描画ができました."


# 指定の画像内にある円を検出する.
# [img] : 画像データ
# [clr1] : 円の外周の色味(=ピクセルの値)
# [clr2] : 円の中心の色味(=ピクセルの値)
# [is_drw] : 円の描画の制御
def detect_circles_from_image(img, clr1, clr2, is_drw):
    if img is None:
        return None, False, "失敗: [img] が指定されていません."
    if clr1 is None:
        return None, False, "失敗: [clr1] が指定されていません."
    if clr2 is None:
        return None, False, "失敗: [clr2] が指定されていません."
    if is_drw is None:
        return None, False, "失敗: [is_drw] が指定されていません."
    if isinstance(img, numpy.ndarray) == False:
        return None, False, "失敗: [img] の型が違います."
    if isinstance(clr1, str) == False:
        return None, False,"失敗: [clr1] の型が違います."
    if isinstance(clr2, int) == False:
        return None, False,"失敗: [clr2] の型が違います."
    if isinstance(is_drw, bool) == False:
        return None, False,"失敗: [is_drw] の型が違います."
    if img.ndim != consts.CV_IMAGE_DIMENSION:
        return None, False,"失敗: [img] の次元数が違います."
    if clr1 == "":
        return None, False,"失敗: [clr1] が空になっています."
    if clr2 == "":
        return None, False,"失敗: [clr2] が空になっています."

    img_gry = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    crcls = cv2.HoughCircles(
        img_gry,
        cv2.HOUGH_GRADIENT,
        dp=1,
        minDist=20,
        param1=100,
        param2=60,
        minRadius=0,
        maxRadius=0,
    )

    crcls = numpy.uint16(numpy.around(crcls))

    if is_drw == False:
        return crcls, True, "成功: 円の検出ができました(描画はしませんでした)."

    if is_drw == True:
        crcls_cpy = crcls.copy()

        for crcl_cpy in crcls_cpy[0, :]:
            cv2.circle(
                img=img,
                center=(crcl_cpy[0], crcl_cpy[1]),
                radius=crcl_cpy[2],
                color=consts.CV_LINE_COLOR,
                thickness=consts.CV_LINE_THICKNESS,
                lineType=consts.CV_LINE_TYPE,
                shift=consts.CV_LINE_SHIFT,
            )

        return crcls, True, "成功: 円の検出ができました(描画もしました)."


# 指定の画像内にある線を検出する.
# [img] : 画像データ
# [is_drw] : 線の描画の制御
def detect_lines_from_image(img, clr, is_drw):
    if img is None:
        return None, False, "失敗: [img] が指定されていません."
    if clr is None:
        return None, False, "失敗: [clr] が指定されていません."
    if is_drw is None:
        return None, False, "失敗: [is_drw] が指定されていません."
    if isinstance(img, numpy.ndarray) == False:
        return None, False, "失敗: [img] の型が違います."
    if isinstance(clr, str) == False:
        return None, False, "失敗: [clr] の型が違います."
    if isinstance(is_drw, bool) == False:
        return None, False, "失敗: [is_drw] の型が違います."
    if img.ndim != consts.CV_IMAGE_DIMENSION:
        return None, False, "失敗: [img] の次元数が違います."
    if clr == "":
        return None, False, "失敗: [clr] が空になっています."

    img_gry = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    rvrsd_img_gry = cv2.bitwise_not(img_gry)

    lns = cv2.HoughLinesP(
        img=rvrsd_img_gry,
        rho=1,
        theta=numpy.pi / 360,
        threshold=80,
        minLineLength=400,
        maxLineGap=5,
    )

    if is_drw == False:
        return lns, True, "成功: 線の検出ができました(描画はしませんでした)."

    if is_drw == True:
        lns_cpy = lns.copy()

        for ln_cpy in lns_cpy:
            x1, y1, x2, y2 = ln_cpy[0]
            cv2.line(
                img=img,
                pt1=(x1, y1),
                pt2=(x2, y2),
                color=consts.CV_COLOR,
                thickness=consts.CV_THICKNESS,
                shift=consts.CV_LINE_SHIFT,
            )

        return lns, True, "成功: 線の検出ができました(描画もしました)."


# # 指定の画像内にある輪郭を検出する.
# # [img] : 画像データ
# # [is_drw] : 線の描画の制御
# def detect_contours_from_image(img):
#     if img is None:
#         return None, False, "失敗: [img] が指定されていません."
#     if is_drw is None:
#         return None, False, "失敗: [is_drw] が指定されていません."
#     if isinstance(img, numpy.ndarray) == False:
#         return False, "失敗: [img] の型が違います."
#     if img.ndim != consts.CV_IMAGE_DIMENSION:
#         return False, "失敗: [img] の次元数が違います."

#     img_gry = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
#     img_blr = cv2.blur(img_gry, (9, 9))
#     _, img_thrsh = cv2.threshold(img_blr, 100, 255, cv2.THRESH_BINARY)
#     cntrs, _ = cv2.findContours(img_thrsh, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)

#     if is_drw == False:
#         return cntrs, True, "成功: 輪郭の検出ができました(描画はしませんでした)."

#     if is_drw == True:
#         cntrs_cpy = cntrs.copy()
#         cv2.drawContours(
#             img, cntrs_cpy, -1, consts.CV_LINE_COLOR, consts.CV_LINE_THICKNESS
#         )
#         return cntrs, True, "成功: 輪郭の検出ができました(描画もしました)."


# 指定の画像の内にある瞳を検出する.
# [img] : 画像データ
# [is_drw] : (瞳を囲む)矩形の描画の制御
def detect_eyes_from_image(img, is_drw):
    if img is None:
        return None, False, "失敗: [img] が指定されていません."
    if is_drw is None:
        return None, False, "失敗: [is_drw] が指定されていません."
    if isinstance(img, numpy.ndarray) == False:
        return None, False, "失敗: [img] の型が違います."
    if isinstance(is_drw, bool) == False:
        return None, False, "失敗: [is_drw] の型が違います."
    if img.ndim != consts.CV_IMAGE_DIMENSION:
        return None, False, "失敗: [img] の次元数が違います."

    cv_clssfr = cv2.CascadeClassifier(consts.CV_DETECT_EYE_MODEL_PATH_AND_NAME)

    if cv_clssfr is None:
        return None, False, "失敗: [cv_clssfr] の構築ができませんでした."

    img_gry = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    eyes_rcts = cv_clssfr.detectMultiScale(img_gry)

    if eyes_rcts is None:
        return None, False, "失敗: 瞳の検出ができませんでした."

    if is_drw == False:
        return eyes_rcts, True, "成功: 瞳の検出ができました(描画はしませんでした)."

    if is_drw == True:
        eyes_rcts_cpy = eyes_rcts.copy()

        for eyes_rct_cpy in eyes_rcts_cpy:
            cv2.rectangle(
                img=img,
                rec=eyes_rct_cpy,
                color=consts.CV_LINE_COLOR,
                thickness=consts.CV_LINE_THICKNESS,
                lineType=consts.CV_LINE_TYPE,
                shift=consts.CV_LINE_SHIFT,
            )

        return eyes_rcts, True, "成功: 瞳の検出ができました(描画もしました)."


# 指定の画像内にある顔を検出する.
# [img] : 画像データ
# [is_drw] : (顔を囲む)矩形の描画の制御
def detect_faces_from_image(img, is_drw):
    if img is None:
        return None, False, "失敗: [img] が指定されていません."
    if is_drw is None:
        return None, False, "失敗: [is_drw] が指定されていません."
    if isinstance(img, numpy.ndarray) == False:
        return None, False, "失敗: [img] の型が違います."
    if isinstance(is_drw, bool) == False:
        return None, False, "失敗: [is_drw] の型が違います."
    # if img.ndim != consts.CV_IMAGE_DIMENSION:
    #     return None, False, "失敗: [img] の次元数が違います."

    img_gry = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    clssfr = cv2.CascadeClassifier(consts.CV_DETECT_FACE_MODEL_PATH_AND_NAME)

    if clssfr is None:
        return None, False, "失敗: [clssfr] の構築ができませんでした."

    hght, wdth = img_gry.shape
    min_size = (int(hght / 10), int(wdth / 10))
    face_rcts = clssfr.detectMultiScale(
        img_gry, scaleFactor=1.1, minNeighbors=2, minSize=min_size
    )

    if face_rcts is None:
        return None, False, "失敗: 顔の検出ができませんでした."

    if is_drw == False:
        return face_rcts, True, "成功: 顔の検出ができました(描画はしませんでした)."

    if is_drw == True:
        face_rcts_cpy = face_rcts.copy()

        for face_rct_cpy in face_rcts_cpy:
            cv2.rectangle(
                img=img,
                rec=face_rct_cpy,
                color=consts.CV_LINE_COLOR,
                thickness=consts.CV_LINE_THICKNESS,
                lineType=consts.CV_LINE_TYPE,
                shift=consts.CV_LINE_SHIFT,
            )

        return face_rcts, True, "成功: 顔の検出ができました(描画もしました)."

