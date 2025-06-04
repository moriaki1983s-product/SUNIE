# coding: utf-8




# 既成のモジュールをインポートする.
import os
import sys
import re
import pytz
import calendar
import datetime
from datetime import timedelta


# 1年の日数を宣言・定義する.
DAYS_IN_YEAR = float(365.25)




# 現在の日付と時刻を[datetime]型で取得する.
# 引数の説明 ~~
# EST1(東部標準時1) : America/New_York
# EST2(東部標準時2) : America/Detroit
# EST3(東部標準時3) : America/Toronto
# EST4(東部標準時4) : America/Indiana/Indianapolis
# CST(中部標準時) : America/Chicago
# MST(山岳標準時) : America/Denver
# PST(太平洋標準時) : America/Los_Angeles
# AKST(アラスカ標準時) : America/Anchorage
# MST(アリゾナ標準時・夏時間非適用) : America/Phoenix
# JST(日本標準時) : Asia/Tokyo
def retrieve_current_datetime_as_datetime_object(tz):
    if tz == "EST1":
        return datetime.datetime.now(pytz.timezone("America/New_York"))
    elif tz == "EST2":
        return datetime.datetime.now(pytz.timezone("America/Detroit"))
    elif tz == "EST3":
        return datetime.datetime.now(pytz.timezone("America/Toronto"))
    elif tz == "EST4":
        return datetime.datetime.now(pytz.timezone("America/Indiana/Indianapolis"))
    elif tz == "CST":
        return datetime.datetime.now(pytz.timezone("America/Chicago"))
    elif tz == "MST":
        return datetime.datetime.now(pytz.timezone("America/Denver"))
    elif tz == "PST":
        return datetime.datetime.now(pytz.timezone("America/Los_Angeles"))
    elif tz == "AKST":
        return datetime.datetime.now(pytz.timezone("America/Anchorage"))
    elif tz == "MST":
        return datetime.datetime.now(pytz.timezone("America/Phoenix"))
    elif tz == "JST":
        return datetime.datetime.now(pytz.timezone("Asia/Tokyo"))
    else:
        return None


# 現在の日付の年を[int]型で取得する.
# 引数の説明 ~~
# EST1(東部標準時1) : America/New_York
# EST2(東部標準時2) : America/Detroit
# EST3(東部標準時3) : America/Toronto
# EST4(東部標準時4) : America/Indiana/Indianapolis
# CST(中部標準時) : America/Chicago
# MST(山岳標準時) : America/Denver
# PST(太平洋標準時) : America/Los_Angeles
# AKST(アラスカ標準時) : America/Anchorage
# MST(アリゾナ標準時・夏時間非適用) : America/Phoenix
# JST(日本標準時) : Asia/Tokyo
def retrieve_current_year_as_integer(tz):
    if tz == "EST1":
        return datetime.datetime.now(pytz.timezone("America/New_York")).year
    elif tz == "EST2":
        return datetime.datetime.now(pytz.timezone("America/Detroit")).year
    elif tz == "EST3":
        return datetime.datetime.now(pytz.timezone("America/Toronto")).year
    elif tz == "EST4":
        return datetime.datetime.now(pytz.timezone("America/Indiana/Indianapolis")).year
    elif tz == "CST":
        return datetime.datetime.now(pytz.timezone("America/Chicago")).year
    elif tz == "MST":
        return datetime.datetime.now(pytz.timezone("America/Denver")).year
    elif tz == "PST":
        return datetime.datetime.now(pytz.timezone("America/Los_Angeles")).year
    elif tz == "AKST":
        return datetime.datetime.now(pytz.timezone("America/Anchorage")).year
    elif tz == "MST":
        return datetime.datetime.now(pytz.timezone("America/Phoenix")).year
    elif tz == "JST":
        return datetime.datetime.now(pytz.timezone("Asia/Tokyo")).year
    else:
        return None


# 現在の日付の月を[int]型で取得する.
# 引数の説明 ~~
# EST1(東部標準時1) : America/New_York
# EST2(東部標準時2) : America/Detroit
# EST3(東部標準時3) : America/Toronto
# EST4(東部標準時4) : America/Indiana/Indianapolis
# CST(中部標準時) : America/Chicago
# MST(山岳標準時) : America/Denver
# PST(太平洋標準時) : America/Los_Angeles
# AKST(アラスカ標準時) : America/Anchorage
# MST(アリゾナ標準時・夏時間非適用) : America/Phoenix
# JST(日本標準時) : Asia/Tokyo
def retrieve_current_month_as_integer(tz):
    if tz == "EST1":
        return datetime.datetime.now(pytz.timezone("America/New_York")).month
    elif tz == "EST2":
        return datetime.datetime.now(pytz.timezone("America/Detroit")).month
    elif tz == "EST3":
        return datetime.datetime.now(pytz.timezone("America/Toronto")).month
    elif tz == "EST4":
        return datetime.datetime.now(pytz.timezone("America/Indiana/Indianapolis")).month
    elif tz == "CST":
        return datetime.datetime.now(pytz.timezone("America/Chicago")).month
    elif tz == "MST":
        return datetime.datetime.now(pytz.timezone("America/Denver")).month
    elif tz == "PST":
        return datetime.datetime.now(pytz.timezone("America/Los_Angeles")).month
    elif tz == "AKST":
        return datetime.datetime.now(pytz.timezone("America/Anchorage")).month
    elif tz == "MST":
        return datetime.datetime.now(pytz.timezone("America/Phoenix")).month
    elif tz == "JST":
        return datetime.datetime.now(pytz.timezone("Asia/Tokyo")).month
    else:
        return None


# 現在の日付の日を[int]型で取得する.
# 引数の説明 ~~
# EST1(東部標準時1) : America/New_York
# EST2(東部標準時2) : America/Detroit
# EST3(東部標準時3) : America/Toronto
# EST4(東部標準時4) : America/Indiana/Indianapolis
# CST(中部標準時) : America/Chicago
# MST(山岳標準時) : America/Denver
# PST(太平洋標準時) : America/Los_Angeles
# AKST(アラスカ標準時) : America/Anchorage
# MST(アリゾナ標準時・夏時間非適用) : America/Phoenix
# JST(日本標準時) : Asia/Tokyo
def retrieve_current_day_as_integer(tz):
    if tz == "EST1":
        return datetime.datetime.now(pytz.timezone("America/New_York")).day
    elif tz == "EST2":
        return datetime.datetime.now(pytz.timezone("America/Detroit")).day
    elif tz == "EST3":
        return datetime.datetime.now(pytz.timezone("America/Toronto")).day
    elif tz == "EST4":
        return datetime.datetime.now(pytz.timezone("America/Indiana/Indianapolis")).day
    elif tz == "CST":
        return datetime.datetime.now(pytz.timezone("America/Chicago")).day
    elif tz == "MST":
        return datetime.datetime.now(pytz.timezone("America/Denver")).day
    elif tz == "PST":
        return datetime.datetime.now(pytz.timezone("America/Los_Angeles")).day
    elif tz == "AKST":
        return datetime.datetime.now(pytz.timezone("America/Anchorage")).day
    elif tz == "MST":
        return datetime.datetime.now(pytz.timezone("America/Phoenix")).day
    elif tz == "JST":
        return datetime.datetime.now(pytz.timezone("Asia/Tokyo")).day
    else:
        return None


# 現在の時刻の時を[int]型で取得する.
# 引数の説明 ~~
# EST1(東部標準時1) : America/New_York
# EST2(東部標準時2) : America/Detroit
# EST3(東部標準時3) : America/Toronto
# EST4(東部標準時4) : America/Indiana/Indianapolis
# CST(中部標準時) : America/Chicago
# MST(山岳標準時) : America/Denver
# PST(太平洋標準時) : America/Los_Angeles
# AKST(アラスカ標準時) : America/Anchorage
# MST(アリゾナ標準時・夏時間非適用) : America/Phoenix
# JST(日本標準時) : Asia/Tokyo
def retrieve_current_hour_as_integer(tz):
    if tz == "EST1":
        return datetime.datetime.now(pytz.timezone("America/New_York")).hour
    elif tz == "EST2":
        return datetime.datetime.now(pytz.timezone("America/Detroit")).hour
    elif tz == "EST3":
        return datetime.datetime.now(pytz.timezone("America/Toronto")).hour
    elif tz == "EST4":
        return datetime.datetime.now(pytz.timezone("America/Indiana/Indianapolis")).hour
    elif tz == "CST":
        return datetime.datetime.now(pytz.timezone("America/Chicago")).hour
    elif tz == "MST":
        return datetime.datetime.now(pytz.timezone("America/Denver")).hour
    elif tz == "PST":
        return datetime.datetime.now(pytz.timezone("America/Los_Angeles")).hour
    elif tz == "AKST":
        return datetime.datetime.now(pytz.timezone("America/Anchorage")).hour
    elif tz == "MST":
        return datetime.datetime.now(pytz.timezone("America/Phoenix")).hour
    elif tz == "JST":
        return datetime.datetime.now(pytz.timezone("Asia/Tokyo")).hour
    else:
        return None


# 現在の時刻の分を[int]型で取得する.
# 引数の説明 ~~
# EST1(東部標準時1) : America/New_York
# EST2(東部標準時2) : America/Detroit
# EST3(東部標準時3) : America/Toronto
# EST4(東部標準時4) : America/Indiana/Indianapolis
# CST(中部標準時) : America/Chicago
# MST(山岳標準時) : America/Denver
# PST(太平洋標準時) : America/Los_Angeles
# AKST(アラスカ標準時) : America/Anchorage
# MST(アリゾナ標準時・夏時間非適用) : America/Phoenix
# JST(日本標準時) : Asia/Tokyo
def retrieve_current_minute_as_integer(tz):
    if tz == "EST1":
        return datetime.datetime.now(pytz.timezone("America/New_York")).minute
    elif tz == "EST2":
        return datetime.datetime.now(pytz.timezone("America/Detroit")).minute
    elif tz == "EST3":
        return datetime.datetime.now(pytz.timezone("America/Toronto")).minute
    elif tz == "EST4":
        return datetime.datetime.now(pytz.timezone("America/Indiana/Indianapolis")).minute
    elif tz == "CST":
        return datetime.datetime.now(pytz.timezone("America/Chicago")).minute
    elif tz == "MST":
        return datetime.datetime.now(pytz.timezone("America/Denver")).minute
    elif tz == "PST":
        return datetime.datetime.now(pytz.timezone("America/Los_Angeles")).minute
    elif tz == "AKST":
        return datetime.datetime.now(pytz.timezone("America/Anchorage")).minute
    elif tz == "MST":
        return datetime.datetime.now(pytz.timezone("America/Phoenix")).minute
    elif tz == "JST":
        return datetime.datetime.now(pytz.timezone("Asia/Tokyo")).minute
    else:
        return None


# 現在の時刻の秒を[int]型で取得する.
# 引数の説明 ~~
# EST1(東部標準時1) : America/New_York
# EST2(東部標準時2) : America/Detroit
# EST3(東部標準時3) : America/Toronto
# EST4(東部標準時4) : America/Indiana/Indianapolis
# CST(中部標準時) : America/Chicago
# MST(山岳標準時) : America/Denver
# PST(太平洋標準時) : America/Los_Angeles
# AKST(アラスカ標準時) : America/Anchorage
# MST(アリゾナ標準時・夏時間非適用) : America/Phoenix
# JST(日本標準時) : Asia/Tokyo
def retrieve_current_second_as_integer(tz):
    if tz == "EST1":
        return datetime.datetime.now(pytz.timezone("America/New_York")).second
    elif tz == "EST2":
        return datetime.datetime.now(pytz.timezone("America/Detroit")).second
    elif tz == "EST3":
        return datetime.datetime.now(pytz.timezone("America/Toronto")).second
    elif tz == "EST4":
        return datetime.datetime.now(pytz.timezone("America/Indiana/Indianapolis")).second
    elif tz == "CST":
        return datetime.datetime.now(pytz.timezone("America/Chicago")).second
    elif tz == "MST":
        return datetime.datetime.now(pytz.timezone("America/Denver")).second
    elif tz == "PST":
        return datetime.datetime.now(pytz.timezone("America/Los_Angeles")).second
    elif tz == "AKST":
        return datetime.datetime.now(pytz.timezone("America/Anchorage")).second
    elif tz == "MST":
        return datetime.datetime.now(pytz.timezone("America/Phoenix")).second
    elif tz == "JST":
        return datetime.datetime.now(pytz.timezone("Asia/Tokyo")).second
    else:
        return None


# 現在の時刻のマイクロ秒を[int]型で取得する.
# 引数の説明 ~~
# EST1(東部標準時1) : America/New_York
# EST2(東部標準時2) : America/Detroit
# EST3(東部標準時3) : America/Toronto
# EST4(東部標準時4) : America/Indiana/Indianapolis
# CST(中部標準時) : America/Chicago
# MST(山岳標準時) : America/Denver
# PST(太平洋標準時) : America/Los_Angeles
# AKST(アラスカ標準時) : America/Anchorage
# MST(アリゾナ標準時・夏時間非適用) : America/Phoenix
# JST(日本標準時) : Asia/Tokyo
def retrieve_current_microsecond_as_integer(tz):
    if tz == "EST1":
        return datetime.datetime.now(pytz.timezone("America/New_York")).microsecond
    elif tz == "EST2":
        return datetime.datetime.now(pytz.timezone("America/Detroit")).microsecond
    elif tz == "EST3":
        return datetime.datetime.now(pytz.timezone("America/Toronto")).microsecond
    elif tz == "EST4":
        return datetime.datetime.now(pytz.timezone("America/Indiana/Indianapolis")).microsecond
    elif tz == "CST":
        return datetime.datetime.now(pytz.timezone("America/Chicago")).microsecond
    elif tz == "MST":
        return datetime.datetime.now(pytz.timezone("America/Denver")).microsecond
    elif tz == "PST":
        return datetime.datetime.now(pytz.timezone("America/Los_Angeles")).microsecond
    elif tz == "AKST":
        return datetime.datetime.now(pytz.timezone("America/Anchorage")).microsecond
    elif tz == "MST":
        return datetime.datetime.now(pytz.timezone("America/Phoenix")).microsecond
    elif tz == "JST":
        return datetime.datetime.now(pytz.timezone("Asia/Tokyo")).microsecond
    else:
        return None


# 現在の日付と時刻を文字列型で取得する.
# [tz]引数の説明 ~~
# EST1(東部標準時1) : America/New_York
# EST2(東部標準時2) : America/Detroit
# EST3(東部標準時3) : America/Toronto
# EST4(東部標準時4) : America/Indiana/Indianapolis
# CST(中部標準時) : America/Chicago
# MST(山岳標準時) : America/Denver
# PST(太平洋標準時) : America/Los_Angeles
# AKST(アラスカ標準時) : America/Anchorage
# MST(アリゾナ標準時・夏時間非適用) : America/Phoenix
# JST(日本標準時) : Asia/Tokyo
# [is_iso]引数の説明 ~~
# [True]の場合, ISO形式.
# [False]の場合, 標準形式.
def retrieve_current_datetime_as_string(tz, is_iso):
    if tz == "EST1":
        crrnt_dttm = datetime.datetime.now(pytz.timezone("America/New_York"))
    elif tz == "EST2":
        crrnt_dttm = datetime.datetime.now(pytz.timezone("America/Detroit"))
    elif tz == "EST3":
        crrnt_dttm = datetime.datetime.now(pytz.timezone("America/Toronto"))
    elif tz == "EST4":
        crrnt_dttm = datetime.datetime.now(pytz.timezone("America/Indiana/Indianapolis"))
    elif tz == "CST":
        crrnt_dttm = datetime.datetime.now(pytz.timezone("America/Chicago"))
    elif tz == "MST":
        crrnt_dttm = datetime.datetime.now(pytz.timezone("America/Denver"))
    elif tz == "PST":
        crrnt_dttm = datetime.datetime.now(pytz.timezone("America/Los_Angeles"))
    elif tz == "AKST":
        crrnt_dttm = datetime.datetime.now(pytz.timezone("America/Anchorage"))
    elif tz == "MST":
        crrnt_dttm = datetime.datetime.now(pytz.timezone("America/Phoenix"))
    elif tz == "JST":
        crrnt_dttm = datetime.datetime.now(pytz.timezone("Asia/Tokyo"))
    else:
        return None

    if is_iso:
        return datetime.datetime.strftime(crrnt_dttm, "%Y-%m-%dT%H:%M:%S")
    else:
        return datetime.datetime.strftime(crrnt_dttm, "%Y-%m-%d %H:%M:%S")


# 現在の日付と時刻を文字列型で取得する.
# [tz]引数の説明 ~~
# EST1(東部標準時1) : America/New_York
# EST2(東部標準時2) : America/Detroit
# EST3(東部標準時3) : America/Toronto
# EST4(東部標準時4) : America/Indiana/Indianapolis
# CST(中部標準時) : America/Chicago
# MST(山岳標準時) : America/Denver
# PST(太平洋標準時) : America/Los_Angeles
# AKST(アラスカ標準時) : America/Anchorage
# MST(アリゾナ標準時・夏時間非適用) : America/Phoenix
# JST(日本標準時) : Asia/Tokyo
# [is_iso]引数の説明 ~~
# [True]の場合, ISO形式.
# [False]の場合, 標準形式.
def retrieve_current_datetime_as_string(tz, is_iso):
    if tz == "EST1":
        crrnt_dttm = datetime.datetime.now(pytz.timezone("America/New_York"))
    elif tz == "EST2":
        crrnt_dttm = datetime.datetime.now(pytz.timezone("America/Detroit"))
    elif tz == "EST3":
        crrnt_dttm = datetime.datetime.now(pytz.timezone("America/Toronto"))
    elif tz == "EST4":
        crrnt_dttm = datetime.datetime.now(pytz.timezone("America/Indiana/Indianapolis"))
    elif tz == "CST":
        crrnt_dttm = datetime.datetime.now(pytz.timezone("America/Chicago"))
    elif tz == "MST":
        crrnt_dttm = datetime.datetime.now(pytz.timezone("America/Denver"))
    elif tz == "PST":
        crrnt_dttm = datetime.datetime.now(pytz.timezone("America/Los_Angeles"))
    elif tz == "AKST":
        crrnt_dttm = datetime.datetime.now(pytz.timezone("America/Anchorage"))
    elif tz == "MST":
        crrnt_dttm = datetime.datetime.now(pytz.timezone("America/Phoenix"))
    elif tz == "JST":
        crrnt_dttm = datetime.datetime.now(pytz.timezone("Asia/Tokyo"))
    else:
        return None

    if is_iso:
        return datetime.datetime.strftime(crrnt_dttm, "%Y-%m-%dT%H:%M:%S")
    else:
        return datetime.datetime.strftime(crrnt_dttm, "%Y-%m-%d %H:%M:%S")


# 現在の日付の年を[str]型で取得する.
# [tz]引数の説明 ~~
# EST1(東部標準時1) : America/New_York
# EST2(東部標準時2) : America/Detroit
# EST3(東部標準時3) : America/Toronto
# EST4(東部標準時4) : America/Indiana/Indianapolis
# CST(中部標準時) : America/Chicago
# MST(山岳標準時) : America/Denver
# PST(太平洋標準時) : America/Los_Angeles
# AKST(アラスカ標準時) : America/Anchorage
# MST(アリゾナ標準時・夏時間非適用) : America/Phoenix
# JST(日本標準時) : Asia/Tokyo
def retrieve_current_year_as_string(tz):
    if tz == "EST1":
        return str(datetime.datetime.now(pytz.timezone("America/New_York")).year)
    elif tz == "EST2":
        return str(datetime.datetime.now(pytz.timezone("America/Detroit")).year)
    elif tz == "EST3":
        return str(datetime.datetime.now(pytz.timezone("America/Toronto")).year)
    elif tz == "EST4":
        return str(datetime.datetime.now(pytz.timezone("America/Indiana/Indianapolis")).year)
    elif tz == "CST":
        return str(datetime.datetime.now(pytz.timezone("America/Chicago")).year)
    elif tz == "MST":
        return str(datetime.datetime.now(pytz.timezone("America/Denver")).year)
    elif tz == "PST":
        return str(datetime.datetime.now(pytz.timezone("America/Los_Angeles")).year)
    elif tz == "AKST":
        return str(datetime.datetime.now(pytz.timezone("America/Anchorage")).year)
    elif tz == "MST":
        return str(datetime.datetime.now(pytz.timezone("America/Phoenix")).year)
    elif tz == "JST":
        return str(datetime.datetime.now(pytz.timezone("Asia/Tokyo")).year)
    else:
        return None


# 現在の日付の月を[str]型で取得する.
# [tz]引数の説明 ~~
# EST1(東部標準時1) : America/New_York
# EST2(東部標準時2) : America/Detroit
# EST3(東部標準時3) : America/Toronto
# EST4(東部標準時4) : America/Indiana/Indianapolis
# CST(中部標準時) : America/Chicago
# MST(山岳標準時) : America/Denver
# PST(太平洋標準時) : America/Los_Angeles
# AKST(アラスカ標準時) : America/Anchorage
# MST(アリゾナ標準時・夏時間非適用) : America/Phoenix
# JST(日本標準時) : Asia/Tokyo
def retrieve_current_month_as_string(tz):
    if tz == "EST1":
        return str(datetime.datetime.now(pytz.timezone("America/New_York")).month)
    elif tz == "EST2":
        return str(datetime.datetime.now(pytz.timezone("America/Detroit")).month)
    elif tz == "EST3":
        return str(datetime.datetime.now(pytz.timezone("America/Toronto")).month)
    elif tz == "EST4":
        return str(datetime.datetime.now(pytz.timezone("America/Indiana/Indianapolis")).month)
    elif tz == "CST":
        return str(datetime.datetime.now(pytz.timezone("America/Chicago")).month)
    elif tz == "MST":
        return str(datetime.datetime.now(pytz.timezone("America/Denver")).month)
    elif tz == "PST":
        return str(datetime.datetime.now(pytz.timezone("America/Los_Angeles")).month)
    elif tz == "AKST":
        return str(datetime.datetime.now(pytz.timezone("America/Anchorage")).month)
    elif tz == "MST":
        return str(datetime.datetime.now(pytz.timezone("America/Phoenix")).month)
    elif tz == "JST":
        return str(datetime.datetime.now(pytz.timezone("Asia/Tokyo")).month)
    else:
        return None


# 現在の日付の日を[str]型で取得する.
# [tz]引数の説明 ~~
# EST1(東部標準時1) : America/New_York
# EST2(東部標準時2) : America/Detroit
# EST3(東部標準時3) : America/Toronto
# EST4(東部標準時4) : America/Indiana/Indianapolis
# CST(中部標準時) : America/Chicago
# MST(山岳標準時) : America/Denver
# PST(太平洋標準時) : America/Los_Angeles
# AKST(アラスカ標準時) : America/Anchorage
# MST(アリゾナ標準時・夏時間非適用) : America/Phoenix
# JST(日本標準時) : Asia/Tokyo
def retrieve_current_day_as_string(tz):
    if tz == "EST1":
        return str(datetime.datetime.now(pytz.timezone("America/New_York")).day)
    elif tz == "EST2":
        return str(datetime.datetime.now(pytz.timezone("America/Detroit")).day)
    elif tz == "EST3":
        return str(datetime.datetime.now(pytz.timezone("America/Toronto")).day)
    elif tz == "EST4":
        return str(datetime.datetime.now(pytz.timezone("America/Indiana/Indianapolis")).day)
    elif tz == "CST":
        return str(datetime.datetime.now(pytz.timezone("America/Chicago")).day)
    elif tz == "MST":
        return str(datetime.datetime.now(pytz.timezone("America/Denver")).day)
    elif tz == "PST":
        return str(datetime.datetime.now(pytz.timezone("America/Los_Angeles")).day)
    elif tz == "AKST":
        return str(datetime.datetime.now(pytz.timezone("America/Anchorage")).day)
    elif tz == "MST":
        return str(datetime.datetime.now(pytz.timezone("America/Phoenix")).day)
    elif tz == "JST":
        return str(datetime.datetime.now(pytz.timezone("Asia/Tokyo")).day)
    else:
        return None


# 現在の時刻の時を[str]型で取得する.
# [tz]引数の説明 ~~
# EST1(東部標準時1) : America/New_York
# EST2(東部標準時2) : America/Detroit
# EST3(東部標準時3) : America/Toronto
# EST4(東部標準時4) : America/Indiana/Indianapolis
# CST(中部標準時) : America/Chicago
# MST(山岳標準時) : America/Denver
# PST(太平洋標準時) : America/Los_Angeles
# AKST(アラスカ標準時) : America/Anchorage
# MST(アリゾナ標準時・夏時間非適用) : America/Phoenix
# JST(日本標準時) : Asia/Tokyo
def retrieve_current_hour_as_string(tz):
    if tz == "EST1":
        return str(datetime.datetime.now(pytz.timezone("America/New_York")).hour)
    elif tz == "EST2":
        return str(datetime.datetime.now(pytz.timezone("America/Detroit")).hour)
    elif tz == "EST3":
        return str(datetime.datetime.now(pytz.timezone("America/Toronto")).hour)
    elif tz == "EST4":
        return str(datetime.datetime.now(pytz.timezone("America/Indiana/Indianapolis")).hour)
    elif tz == "CST":
        return str(datetime.datetime.now(pytz.timezone("America/Chicago")).hour)
    elif tz == "MST":
        return str(datetime.datetime.now(pytz.timezone("America/Denver")).hour)
    elif tz == "PST":
        return str(datetime.datetime.now(pytz.timezone("America/Los_Angeles")).hour)
    elif tz == "AKST":
        return str(datetime.datetime.now(pytz.timezone("America/Anchorage")).hour)
    elif tz == "MST":
        return str(datetime.datetime.now(pytz.timezone("America/Phoenix")).hour)
    elif tz == "JST":
        return str(datetime.datetime.now(pytz.timezone("Asia/Tokyo")).hour)
    else:
        return None


# 現在の時刻の分を[str]型で取得する.
# [tz]引数の説明 ~~
# EST1(東部標準時1) : America/New_York
# EST2(東部標準時2) : America/Detroit
# EST3(東部標準時3) : America/Toronto
# EST4(東部標準時4) : America/Indiana/Indianapolis
# CST(中部標準時) : America/Chicago
# MST(山岳標準時) : America/Denver
# PST(太平洋標準時) : America/Los_Angeles
# AKST(アラスカ標準時) : America/Anchorage
# MST(アリゾナ標準時・夏時間非適用) : America/Phoenix
# JST(日本標準時) : Asia/Tokyo
def retrieve_current_minute_as_string(tz):
    if tz == "EST1":
        return str(datetime.datetime.now(pytz.timezone("America/New_York")).minute)
    elif tz == "EST2":
        return str(datetime.datetime.now(pytz.timezone("America/Detroit")).minute)
    elif tz == "EST3":
        return str(datetime.datetime.now(pytz.timezone("America/Toronto")).minute)
    elif tz == "EST4":
        return str(datetime.datetime.now(pytz.timezone("America/Indiana/Indianapolis")).minute)
    elif tz == "CST":
        return str(datetime.datetime.now(pytz.timezone("America/Chicago")).minute)
    elif tz == "MST":
        return str(datetime.datetime.now(pytz.timezone("America/Denver")).minute)
    elif tz == "PST":
        return str(datetime.datetime.now(pytz.timezone("America/Los_Angeles")).minute)
    elif tz == "AKST":
        return str(datetime.datetime.now(pytz.timezone("America/Anchorage")).minute)
    elif tz == "MST":
        return str(datetime.datetime.now(pytz.timezone("America/Phoenix")).minute)
    elif tz == "JST":
        return str(datetime.datetime.now(pytz.timezone("Asia/Tokyo")).minute)
    else:
        return None


# 現在の時刻の秒を[str]型で取得する.
# [tz]引数の説明 ~~
# EST1(東部標準時1) : America/New_York
# EST2(東部標準時2) : America/Detroit
# EST3(東部標準時3) : America/Toronto
# EST4(東部標準時4) : America/Indiana/Indianapolis
# CST(中部標準時) : America/Chicago
# MST(山岳標準時) : America/Denver
# PST(太平洋標準時) : America/Los_Angeles
# AKST(アラスカ標準時) : America/Anchorage
# MST(アリゾナ標準時・夏時間非適用) : America/Phoenix
# JST(日本標準時) : Asia/Tokyo
def retrieve_current_second_as_string(tz):
    if tz == "EST1":
        return str(datetime.datetime.now(pytz.timezone("America/New_York")).second)
    elif tz == "EST2":
        return str(datetime.datetime.now(pytz.timezone("America/Detroit")).second)
    elif tz == "EST3":
        return str(datetime.datetime.now(pytz.timezone("America/Toronto")).second)
    elif tz == "EST4":
        return str(datetime.datetime.now(pytz.timezone("America/Indiana/Indianapolis")).second)
    elif tz == "CST":
        return str(datetime.datetime.now(pytz.timezone("America/Chicago")).second)
    elif tz == "MST":
        return str(datetime.datetime.now(pytz.timezone("America/Denver")).second)
    elif tz == "PST":
        return str(datetime.datetime.now(pytz.timezone("America/Los_Angeles")).second)
    elif tz == "AKST":
        return str(datetime.datetime.now(pytz.timezone("America/Anchorage")).second)
    elif tz == "MST":
        return str(datetime.datetime.now(pytz.timezone("America/Phoenix")).second)
    elif tz == "JST":
        return str(datetime.datetime.now(pytz.timezone("Asia/Tokyo")).second)
    else:
        return None


# 現在の時刻のマイクロ秒を[str]型で取得する.
# [tz]引数の説明 ~~
# EST1(東部標準時1) : America/New_York
# EST2(東部標準時2) : America/Detroit
# EST3(東部標準時3) : America/Toronto
# EST4(東部標準時4) : America/Indiana/Indianapolis
# CST(中部標準時) : America/Chicago
# MST(山岳標準時) : America/Denver
# PST(太平洋標準時) : America/Los_Angeles
# AKST(アラスカ標準時) : America/Anchorage
# MST(アリゾナ標準時・夏時間非適用) : America/Phoenix
# JST(日本標準時) : Asia/Tokyo
def retrieve_current_microsecond_as_string(tz):
    if tz == "EST1":
        return str(datetime.datetime.now(pytz.timezone("America/New_York")).microsecond)
    elif tz == "EST2":
        return str(datetime.datetime.now(pytz.timezone("America/Detroit")).microsecond)
    elif tz == "EST3":
        return str(datetime.datetime.now(pytz.timezone("America/Toronto")).microsecond)
    elif tz == "EST4":
        return str(datetime.datetime.now(pytz.timezone("America/Indiana/Indianapolis")).microsecond)
    elif tz == "CST":
        return str(datetime.datetime.now(pytz.timezone("America/Chicago")).microsecond)
    elif tz == "MST":
        return str(datetime.datetime.now(pytz.timezone("America/Denver")).microsecond)
    elif tz == "PST":
        return str(datetime.datetime.now(pytz.timezone("America/Los_Angeles")).microsecond)
    elif tz == "AKST":
        return str(datetime.datetime.now(pytz.timezone("America/Anchorage")).microsecond)
    elif tz == "MST":
        return str(datetime.datetime.now(pytz.timezone("America/Phoenix")).microsecond)
    elif tz == "JST":
        return str(datetime.datetime.now(pytz.timezone("Asia/Tokyo")).microsecond)
    else:
        return None


# 現在の曜日を[int]型で取得する.
# 引数の説明 ~~
# EST1(東部標準時1) : America/New_York
# EST2(東部標準時2) : America/Detroit
# EST3(東部標準時3) : America/Toronto
# EST4(東部標準時4) : America/Indiana/Indianapolis
# CST(中部標準時) : America/Chicago
# MST(山岳標準時) : America/Denver
# PST(太平洋標準時) : America/Los_Angeles
# AKST(アラスカ標準時) : America/Anchorage
# MST(アリゾナ標準時・夏時間非適用) : America/Phoenix
# JST(日本標準時) : Asia/Tokyo
# 戻り値の説明 ~~
# [0](月曜日)から[6](日曜日)までの数値.
def retrieve_current_weekday_as_integer(tz):
    if tz == "EST1":
        return datetime.datetime.now(pytz.timezone("America/New_York")).weekday()
    elif tz == "EST2":
        return datetime.datetime.now(pytz.timezone("America/Detroit")).weekday()
    elif tz == "EST3":
        return datetime.datetime.now(pytz.timezone("America/Toronto")).weekday()
    elif tz == "EST4":
        return datetime.datetime.now(pytz.timezone("America/Indiana/Indianapolis")).weekday()
    elif tz == "CST":
        return datetime.datetime.now(pytz.timezone("America/Chicago")).weekday()
    elif tz == "MST":
        return datetime.datetime.now(pytz.timezone("America/Denver")).weekday()
    elif tz == "PST":
        return datetime.datetime.now(pytz.timezone("America/Los_Angeles")).weekday()
    elif tz == "AKST":
        return datetime.datetime.now(pytz.timezone("America/Anchorage")).weekday()
    elif tz == "MST":
        return datetime.datetime.now(pytz.timezone("America/Phoenix")).weekday()
    elif tz == "JST":
        return datetime.datetime.now(pytz.timezone("Asia/Tokyo")).weekday()
    else:
        return None


# 現在の曜日を[str]型で取得する.
# 引数の説明 ~~
# EST1(東部標準時1) : America/New_York
# EST2(東部標準時2) : America/Detroit
# EST3(東部標準時3) : America/Toronto
# EST4(東部標準時4) : America/Indiana/Indianapolis
# CST(中部標準時) : America/Chicago
# MST(山岳標準時) : America/Denver
# PST(太平洋標準時) : America/Los_Angeles
# AKST(アラスカ標準時) : America/Anchorage
# MST(アリゾナ標準時・夏時間非適用) : America/Phoenix
# JST(日本標準時) : Asia/Tokyo
# [lng]引数の説明 ~~
# ["en"]の場合, 英語.
# ["ja"]の場合, 日本語.
def retrieve_current_weekday_as_string(tz, lng):
    if tz == "EST1":
        wkdy_tmp = datetime.datetime.now(pytz.timezone("America/New_York")).weekday()
    elif tz == "EST2":
        wkdy_tmp = datetime.datetime.now(pytz.timezone("America/Detroit")).weekday()
    elif tz == "EST3":
        wkdy_tmp = datetime.datetime.now(pytz.timezone("America/Toronto")).weekday()
    elif tz == "EST4":
        wkdy_tmp = datetime.datetime.now(pytz.timezone("America/Indiana/Indianapolis")).weekday()
    elif tz == "CST":
        wkdy_tmp = datetime.datetime.now(pytz.timezone("America/Chicago")).weekday()
    elif tz == "MST":
        wkdy_tmp = datetime.datetime.now(pytz.timezone("America/Denver")).weekday()
    elif tz == "PST":
        wkdy_tmp = datetime.datetime.now(pytz.timezone("America/Los_Angeles")).weekday()
    elif tz == "AKST":
        wkdy_tmp = datetime.datetime.now(pytz.timezone("America/Anchorage")).weekday()
    elif tz == "MST":
        wkdy_tmp = datetime.datetime.now(pytz.timezone("America/Phoenix")).weekday()
    elif tz == "JST":
        wkdy_tmp = datetime.datetime.now(pytz.timezone("Asia/Tokyo")).weekday()
    else:
        return None

    if lng == "en":
        match wkdy_tmp:
              case wkdy_tmp if wkdy_tmp == 0:
                   return "monday"
              case wkdy_tmp if wkdy_tmp == 1:
                   return "tuesday"
              case wkdy_tmp if wkdy_tmp == 2:
                   return "wednesday"
              case wkdy_tmp if wkdy_tmp == 3:
                   return "thursday"
              case wkdy_tmp if wkdy_tmp == 4:
                   return "friday"
              case wkdy_tmp if wkdy_tmp == 5:
                   return "saturday"
              case wkdy_tmp if wkdy_tmp == 6:
                   return "sunday"
    elif lng == "ja":
        match wkdy_tmp:
              case wkdy_tmp if wkdy_tmp == 0:
                   return "月曜日"
              case wkdy_tmp if wkdy_tmp == 1:
                   return "火曜日"
              case wkdy_tmp if wkdy_tmp == 2:
                   return "水曜日"
              case wkdy_tmp if wkdy_tmp == 3:
                   return "木曜日"
              case wkdy_tmp if wkdy_tmp == 4:
                   return "金曜日"
              case wkdy_tmp if wkdy_tmp == 5:
                   return "土曜日"
              case wkdy_tmp if wkdy_tmp == 6:
                   return "日曜日"
    else:
        return None


# ファイルラベルとしての現在の日時を取得する.
def retrieve_current_datetime_as_file_label():
    return datetime.datetime.now().strftime("%Y%m%d%H%M%S%f")


# 指定の期間(=日数)を[timedelta]型で取得する.
def retrieve_timedelta_from_days(dys):
    return timedelta(days=(dys))


# 指定の期間(=年数)を[timedelta]型で取得する.
def retrieve_timedelta_from_years(yrs):
    return timedelta(days=(yrs * DAYS_IN_YEAR))


# 指定の日付[datetime]型から現在までの期間(=日数)を[timedelta]型で取得する.
def retrieve_timedelta_from_date_object(dt_obj):
    crrnt_dttm_obj = datetime.datetime.now()
    dttm_obj = datetime.datetime.combine(dt_obj, datetime.datetime.min.time())
    return (crrnt_dttm_obj - dttm_obj)


# 指定の日付[str]型から現在までの期間(=日数)を[timedelta]型で取得する.
def retrieve_timedelta_from_date_string(dt_str):
    crrnt_dttm_obj = datetime.datetime.now()
    dt_obj = datetime.datetime.strptime(dt_str, "%Y-%m-%d").date()
    dttm_obj = datetime.datetime.combine(dt_obj, datetime.datetime.min.time())
    return (crrnt_dttm_obj - dttm_obj)


# 日時情報を表す文字列をISO形式(=内部表現)に変換する.
# ※ISO形式とは, Web標準のカレンダーのための形式.
def modify_style_for_datetime_string(dttm_str, is_iso):
    if is_iso:
        return str(dttm_str).replace("/", "-").replace(" ", "T")
    return str(dttm_str).replace("-", "/").replace("T", " ")


# [datetime]型の日付情報を[str]型に変換する.
def convert_datetime_object_to_string_for_eventday(dt_obj):
    return datetime.datetime.strftime(dt_obj, "%Y-%m-%d")


# [datetime]型の日時情報を[str]型に変換する.
def convert_datetime_object_to_string_for_timestamp(dttm_obj, is_iso):
    if is_iso:
        return datetime.datetime.strftime(dttm_obj, "%Y-%m-%dT%H:%M:%S")
    return datetime.datetime.strftime(dttm_obj, "%Y-%m-%d %H:%M:%S")


# [str]型の日付情報(=イベントデイ)を[datetime]型に変換する.
def convert_string_to_datetime_object_for_eventday(dt_str):
    return datetime.datetime.strptime(dt_str, "%Y-%m-%d")


# [str]型の日時情報(=タイムスタンプ)を[datetime]型に変換する.
def convert_string_to_datetime_object_for_timestamp(dttm_str, is_iso):
    if is_iso:
        return datetime.datetime.strptime(dttm_str, "%Y-%m-%dT%H:%M:%S")
    return datetime.datetime.strptime(dttm_str, "%Y-%m-%d %H:%M:%S")


# 対象の文字列がISO形式のタイムスタンプ(=日時情報)かを判定する.
# ※この関数は, ミリ秒部とTZオフセット部を含む形式を正規とする.
# ※この関数は, ISO形式のタイムスタンプに対してのみ有効である.
def check_timestamp_by_iso_style(txt):
    cmpl1 = re.compile(
    r"^[0-9][0-9][0-9][0-9]/[0-9][0-9]/[0-9][0-9] [0-9][0-9]:[0-9][0-9]:[0-9][0-9].[0-9][0-9][0-9][0-9][0-9][0-9](\+)[0-9][0-9]:[0-9][0-9]$"
    )
    cmpl2 = re.compile(
    r"^[0-9][0-9][0-9][0-9]/[0-9][0-9]/[0-9][0-9] [0-9][0-9]:[0-9][0-9]:[0-9][0-9].[0-9][0-9][0-9][0-9][0-9][0-9](\-)[0-9][0-9]:[0-9][0-9]$"
    )
    if (cmpl1.fullmatch(txt) is None) or (cmpl2.fullmatch(txt) is None):
        return False

    dt_prt = txt.split(" ")[0]
    tm_prt = txt.split(" ")[1]
    yr_prt = dt_prt.split("/")[0]
    mnth_prt = dt_prt.split("/")[1]
    dy_prt = dt_prt.split("/")[2]
    hr_prt = tm_prt.split(":")[0]
    mnts_prt = tm_prt.split(":")[1]
    scnd_prt = tm_prt.split(":")[2]
    mlscnd_prt = txt.split(".")[1].split("+")[0]
    hr_tz_prt = txt.split("+")[1].split(":")[0]
    mnts_tz_prt = txt.split("+")[1].split(":")[1]

    if (int(yr_prt) < int("0001") or int(yr_prt) > int("9999")):
        return False
    if (int(mnth_prt) < 1 or int(mnth_prt) > 12):
        return False
    if (int(dy_prt) < 1 or int(dy_prt) > 31):
        return False
    if (int(hr_prt) < 0 or int(hr_prt) > 23):
        return False
    if (int(mnts_prt) < 0 or int(mnts_prt) > 59):
        return False
    if (int(scnd_prt) < 0 or int(scnd_prt) > 59):
        return False
    if (int(mlscnd_prt) < 000000 or int(mlscnd_prt) > 999999):
        return False
    if (int(hr_tz_prt) < 0 or int(hr_tz_prt) > 23):
        return False
    if (int(mnts_tz_prt) < 0 or int(mnts_tz_prt) > 59):
        return False

    if int(mnth_prt) == 1:
        if calendar.monthrange(int(yr_prt), 1)[1] < int(dy_prt):
            return False
    if int(mnth_prt) == 2:
        if calendar.monthrange(int(yr_prt), 2)[1] < int(dy_prt):
            return False
    if int(mnth_prt) == 3:
        if calendar.monthrange(int(yr_prt), 3)[1] < int(dy_prt):
            return False
    if int(mnth_prt) == 4:
        if calendar.monthrange(int(yr_prt), 4)[1] < int(dy_prt):
            return False
    if int(mnth_prt) == 5:
        if calendar.monthrange(int(yr_prt), 5)[1] < int(dy_prt):
            return False
    if int(mnth_prt) == 6:
        if calendar.monthrange(int(yr_prt), 6)[1] < int(dy_prt):
            return False
    if int(mnth_prt) == 7:
        if calendar.monthrange(int(yr_prt), 7)[1] < int(dy_prt):
            return False
    if int(mnth_prt) == 8:
        if calendar.monthrange(int(yr_prt), 8)[1] < int(dy_prt):
            return False
    if int(mnth_prt) == 9:
        if calendar.monthrange(int(yr_prt), 9)[1] < int(dy_prt):
            return False
    if int(mnth_prt) == 10:
        if calendar.monthrange(int(yr_prt), 10)[1] < int(dy_prt):
            return False
    if int(mnth_prt) == 11:
        if calendar.monthrange(int(yr_prt), 11)[1] < int(dy_prt):
            return False
    if int(mnth_prt) == 12:
        if calendar.monthrange(int(yr_prt), 12)[1] < int(dy_prt):
            return False

    return True


# 対象の文字列がISO形式のタイムスタンプ(=日時情報)かを判定する.
# ※この関数は, ミリ秒部とTZオフセット部を含む形式を正規とする.
# ※この関数は, 表示形式のタイムスタンプに対してのみ有効である.
def check_timestamp_by_display_style(txt):
    cmpl1 = re.compile(
    r"^[0-9][0-9][0-9][0-9]-[0-9][0-9]-[0-9][0-9]T[0-9][0-9]:[0-9][0-9]:[0-9][0-9].[0-9][0-9][0-9][0-9][0-9][0-9](\+)[0-9][0-9]:[0-9][0-9]$"
    )
    cmpl2 = re.compile(
    r"^[0-9][0-9][0-9][0-9]-[0-9][0-9]-[0-9][0-9]T[0-9][0-9]:[0-9][0-9]:[0-9][0-9].[0-9][0-9][0-9][0-9][0-9][0-9](\-)[0-9][0-9]:[0-9][0-9]$"
    )
    if (cmpl1.fullmatch(txt) is None) or (cmpl2.fullmatch(txt) is None):
        return False

    dt_prt = txt.split("T")[0]
    tm_prt = txt.split("T")[1]
    yr_prt = dt_prt.split("-")[0]
    mnth_prt = dt_prt.split("-")[1]
    dy_prt = dt_prt.split("-")[2]
    hr_prt = tm_prt.split(":")[0]
    mnts_prt = tm_prt.split(":")[1]
    scnd_prt = tm_prt.split(":")[2]
    mlscnd_prt = txt.split(".")[1].split("+")[0]
    hr_tz_prt = txt.split("+")[1].split(":")[0]
    mnts_tz_prt = txt.split("+")[1].split(":")[1]

    if (int(yr_prt) < int("0001") or int(yr_prt) > int("9999")):
        return False
    if (int(mnth_prt) < 1 or int(mnth_prt) > 12):
        return False
    if (int(dy_prt) < 1 or int(dy_prt) > 31):
        return False
    if (int(hr_prt) < 0 or int(hr_prt) > 23):
        return False
    if (int(mnts_prt) < 0 or int(mnts_prt) > 59):
        return False
    if (int(scnd_prt) < 0 or int(scnd_prt) > 59):
        return False
    if (int(mlscnd_prt) < 000000 or int(mlscnd_prt) > 999999):
        return False
    if (int(hr_tz_prt) < 0 or int(hr_tz_prt) > 23):
        return False
    if (int(mnts_tz_prt) < 0 or int(mnts_tz_prt) > 59):
        return False

    if int(mnth_prt) == 1:
        if calendar.monthrange(int(yr_prt), 1)[1] < int(dy_prt):
            return False
    if int(mnth_prt) == 2:
        if calendar.monthrange(int(yr_prt), 2)[1] < int(dy_prt):
            return False
    if int(mnth_prt) == 3:
        if calendar.monthrange(int(yr_prt), 3)[1] < int(dy_prt):
            return False
    if int(mnth_prt) == 4:
        if calendar.monthrange(int(yr_prt), 4)[1] < int(dy_prt):
            return False
    if int(mnth_prt) == 5:
        if calendar.monthrange(int(yr_prt), 5)[1] < int(dy_prt):
            return False
    if int(mnth_prt) == 6:
        if calendar.monthrange(int(yr_prt), 6)[1] < int(dy_prt):
            return False
    if int(mnth_prt) == 7:
        if calendar.monthrange(int(yr_prt), 7)[1] < int(dy_prt):
            return False
    if int(mnth_prt) == 8:
        if calendar.monthrange(int(yr_prt), 8)[1] < int(dy_prt):
            return False
    if int(mnth_prt) == 9:
        if calendar.monthrange(int(yr_prt), 9)[1] < int(dy_prt):
            return False
    if int(mnth_prt) == 10:
        if calendar.monthrange(int(yr_prt), 10)[1] < int(dy_prt):
            return False
    if int(mnth_prt) == 11:
        if calendar.monthrange(int(yr_prt), 11)[1] < int(dy_prt):
            return False
    if int(mnth_prt) == 12:
        if calendar.monthrange(int(yr_prt), 12)[1] < int(dy_prt):
            return False

    return True