# coding: utf-8




# 既成のモジュールをインポートする.
import os
import sys
import mimetypes




# 指定されたパスに対応するファイルが,
# 存在することを確認するための関数を宣言・定義する.
def check_exist_file(fl_pth):
    return (os.path.exists(fl_pth) and os.path.isfile(fl_pth))


# 指定されたパスに対応するフォルダーが,
# 存在することを確認するための関数を宣言・定義する.
def check_exist_folder(fldr_pth):
    return (os.path.exists(fldr_pth) and os.path.isdir(fldr_pth))


# 指定されたパスに対応するファイルないしフォルダーが, 
# 存在することを確認するための関数を宣言・定義する.
def check_exist_file_or_folder(fl_or_fldr_pth):
    return os.path.exists(fl_or_fldr_pth)


# 指定されたファイル名, ないし指定されたファイルパスに含まれる,
# ファイルのMIMEタイプと拡張子を取得するための関数を宣言・定義する.
def retrieve_file_type(fl_nm_or_fl_pth):
    # ファイルのMIMEタイプと拡張子を取得する.
    fl_mime, fl_enc = mimetypes.guess_type(fl_nm_or_fl_pth)
    return fl_mime, fl_enc


# 指定されたファイル名, ないしファイルパスを基に,
# ファイルの種類がイメージであるかを確認するための関数を宣言・定義する.
def check_image_file(fl_nm_or_fl_pth):
    fl_mime, _ = retrieve_file_type(fl_nm_or_fl_pth)

    if (fl_mime =="image/jpeg" or fl_mime == "image/png"
        or fl_mime == "image/gif" or fl_mime == "image/bmp"):
        return True
    else:
        return False


# 指定されたファイル名, ないしファイルパスを基に,
# ファイルの種類がサウンドであるかを確認するための関数を宣言・定義する.
def check_sound_file(fl_nm_or_fl_pth):
    fl_mime, _ = retrieve_file_type(fl_nm_or_fl_pth)

    if (fl_mime == "audio/mp3" or fl_mime == "audio/wav"):
        return True
    else:
        return False


# 指定されたファイル名, ないしファイルパスを基に,
# ファイルの種類がビデオであるかを確認するための関数を宣言・定義する.
def check_video_file(fl_nm_or_fl_pth):
    fl_mime, _ = retrieve_file_type(fl_nm_or_fl_pth)

    if (fl_mime == "video/mpeg" or fl_mime == "video/mp4" or fl_mime == "video/avi"):
        return True
    else:
        return False


# 特定パスが, 特定フォルダーの配下にあるかを確認するための関数を宣言・定義する.
def check_under_folder(pth, fldr):
    # パスを絶対パスに変換する.
    abs_pth = os.path.abspath(pth)
    abs_fldr = os.path.abspath(fldr)

    # パスがフォルダー配下にあるかを確認する.
    return (os.path.commonpath([abs_pth, abs_fldr]) == abs_fldr)


# ファイルをアーカイブするための関数を宣言・定義する.
def archive_file(fl, fl_pth, fl_lbl):
    fl_pth_tmp = ""

    if fl.filename == "":
        return fl_pth_tmp
    else:
        fl_ext = fl.filename.split(".")[-1]
        fl_pth_tmp = fl_pth + fl_lbl + "." + fl_ext
        fl.save(fl_pth_tmp)
        return fl_pth_tmp