# coding: utf-8




# 既成のモジュールをインポートする.
import os
import sys

# 独自のモジュールをインポートする.
import modules.utilities.log as utils_log
import modules.utilities.time as utils_time
import modules.utilities.data as utils_data
import modules.utilities.random as utils_random




# Etcユニットのクラスを定義する.
class EtcUnit:
    _instance = None
    cstm_lggr = None
    dat = None

    # インスタンス生成のためのメソッドを定義する.
    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(EtcUnit, cls).__new__(cls, *args, **kwargs)
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


    # 「modules.utilities.log」への委譲メソッドを定義する.
    # ※詳細なコメントについては, 該当モジュールを参照すること.
    def logging__start(self, fl_nm):
        self.cstm_lggr = utils_log.CustomLogger(fl_nm)

    def logging__debug(self, msg):
        if self.cstm_lggr is not None:
            return self.cstm_lggr.logging__debug(msg)

    def logging__info(self, msg):
        if self.cstm_lggr is not None:
            return self.cstm_lggr.logging__info(msg)

    def logging__warning(self, msg):
        if self.cstm_lggr is not None:
            return self.cstm_lggr.logging__warning(msg)

    def logging__error(self, msg):
        if self.cstm_lggr is not None:
            return self.cstm_lggr.logging__error(msg)

    def logging__critical(self, msg):
        if self.cstm_lggr is not None:
            return self.cstm_lggr.logging__critical(msg)


    # 「modules.utilities.data」への委譲メソッドを定義する.
    # ※詳細なコメントについては, 該当モジュールを参照すること.
    def check_exist_file(self, fl_pth):
        return utils_data.check_exist_file(fl_pth)

    def check_exist_folder(self, fldr_pth):
        return utils_data.check_exist_folder(fldr_pth)

    def retrieve_file_type(self, fl_nm_or_fl_pth):
        return utils_data.retrieve_file_type(fl_nm_or_fl_pth)

    def check_image_file(self, fl_nm_or_fl_pth):
        return utils_data.check_image_file(fl_nm_or_fl_pth)

    def check_sound_file(self, fl_nm_or_fl_pth):
        return utils_data.check_sound_file(fl_nm_or_fl_pth)

    def check_video_file(self, fl_nm_or_fl_pth):
        return utils_data.check_video_file(fl_nm_or_fl_pth)

    def check_under_folder(self, pth, fldr):
        return utils_data.check_under_folder(pth, fldr)

    def save_file(self, fl, fl_pth, fl_lbl):
        return utils_data.save_file(fl, fl_pth, fl_lbl)


    # 「modules.utilities.time」への委譲メソッドを定義する.
    # ※詳細なコメントについては, 該当モジュールを参照すること.
    def retrieve_current_datetime_as_datetime_object(self, tz):
        return utils_time.retrieve_current_datetime_as_datetime_object(tz)

    def retrieve_current_year_as_integer(self, tz):
        return utils_time.retrieve_current_year_as_integer(tz)

    def retrieve_current_month_as_integer(self, tz):
        return utils_time.retrieve_current_month_as_integer(tz)

    def retrieve_current_day_as_integer(self, tz):
        return utils_time.retrieve_current_day_as_integer(tz)

    def retrieve_current_hour_as_integer(self, tz):
        return utils_time.retrieve_current_hour_as_integer(tz)

    def retrieve_current_minute_as_integer(self, tz):
        return utils_time.retrieve_current_minute_as_integer(tz)

    def retrieve_current_second_as_integer(self, tz):
        return utils_time.retrieve_current_second_as_integer(tz)

    def retrieve_current_microsecond_as_integer(self, tz):
        return utils_time.retrieve_current_microsecond_as_integer(tz)

    def retrieve_current_datetime_as_string(self, tz, is_iso):
        return utils_time.retrieve_current_datetime_as_string(tz, is_iso)

    def retrieve_current_year_as_string(self, tz):
        return utils_time.retrieve_current_year_as_string(tz)

    def retrieve_current_month_as_string(self, tz):
        return utils_time.retrieve_current_month_as_string(tz)

    def retrieve_current_day_as_string(self, tz):
        return utils_time.retrieve_current_day_as_string(tz)

    def retrieve_current_hour_as_string(self, tz):
        return utils_time.retrieve_current_hour_as_string(tz)

    def retrieve_current_minute_as_string(self, tz):
        return utils_time.retrieve_current_minute_as_string(tz)

    def retrieve_current_second_as_string(self, tz):
        return utils_time.retrieve_current_second_as_string(tz)

    def retrieve_current_microsecond_as_string(self, tz):
        return utils_time.retrieve_current_microsecond_as_string(tz)

    def retrieve_current_weekday_as_integer(self, tz):
        return utils_time.retrieve_current_weekday_as_integer(tz)

    def retrieve_current_weekday_as_string(self, tz, lng):
        return utils_time.retrieve_current_weekday_as_string(tz, lng)

    def retrieve_current_time_as_file_label(self):
        return utils_time.retrieve_current_time_as_file_label()

    def retrieve_timedelta_from_days(self, dys):
        return utils_time.retrieve_timedelta_from_days(dys)

    def retrieve_timedelta_from_years(self, yrs):
        return utils_time.retrieve_timedelta_from_years(yrs)

    def retrieve_timedelta_from_date_object(self, dt_obj):
        return utils_time.retrieve_timedelta_from_date_object(dt_obj)

    def retrieve_timedelta_from_date_string(self, dt_str):
        return utils_time.retrieve_timedelta_from_date_string(dt_str)

    def modify_style_for_datetime_string(self, dttm_str, is_iso):
        return utils_time.modify_style_for_datetime_string(dttm_str, is_iso)

    def convert_datetime_object_to_string_for_eventday(self, dt_obj):
        return utils_time.convert_datetime_object_to_string_for_eventday(dt_obj)

    def convert_datetime_object_to_string_for_timestamp(self, dttm_obj, is_iso):
        return utils_time.convert_datetime_object_to_string_for_timestamp(dttm_obj, is_iso)

    def convert_string_to_datetime_object_for_eventday(self, dt_str):
        return utils_time.convert_string_to_datetime_object_for_eventday(dt_str)

    def convert_string_to_datetime_object_for_timestamp(self, dttm_str, is_iso):
        return utils_time.convert_string_to_datetime_object_for_timestamp(dttm_str, is_iso)

    def check_timestamp_by_iso_style(self, txt):
        return utils_time.check_timestamp_by_iso_style(txt)

    def check_timestamp_by_display_style(self, txt):
        return utils_time.check_timestamp_by_display_style(txt)


    # 「modules.utilities.radom」への委譲メソッドを定義する.
    # ※詳細なコメントについては, 該当モジュールを参照すること.
    def random_select(self, stts):
        return utils_random.random_select(stts)

    def random_selects(self, stts, wghts, smpl_num):
        return utils_random.random_selects(stts, wghts, smpl_num)