# coding: utf-8




# 既成のモジュールをインポートする.
import os
import sys
from flask_wtf import FlaskForm
from wtforms import (
     IntegerField,
     StringField,
     TextAreaField,
     PasswordField,
     SelectField,
     RadioField,
     BooleanField,
     DateField,
     DateTimeField,
     FileField,
     SubmitField
)

# 設定のためのモジュールをインポートする.
import constants as consts




# 職員入室フォーム(=FlaskFormクラス)を宣言・定義する.
class StaffEnterForm(FlaskForm):
      menu_choices = consts.MENU_CHOICE_FOR_STAFF_ENTER_FORM
      name = StringField("職員名 :", default="", render_kw={"autocomplete": "off"})
      password = PasswordField("パスワード :", default="", render_kw={"autocomplete": "off"})
      reason = SelectField("入室理由 :", default="", choices=menu_choices)
      decide = SubmitField("決定")
      cancel = SubmitField("取消")


# 職員退室フォーム(=FlaskFormクラス)を宣言・定義する.
class StaffExitForm(FlaskForm):
      menu_choices = consts.MENU_CHOICE_FOR_STAFF_EXIT_FORM
      reason = SelectField("退室理由 :", default="", choices=menu_choices)
      decide = SubmitField("決定")
      cancel = SubmitField("取消")


# 管理者入室フォーム(=FlaskFormクラス)を宣言・定義する.
class AdminEnterForm(FlaskForm):
      password = PasswordField("パスワード :", default="", render_kw={"autocomplete": "off"})
      decide = SubmitField("決定")
      cancel = SubmitField("取消")


# 管理者退室フォーム(=FlaskFormクラス)を宣言・定義する.
class AdminExitForm(FlaskForm):
      decide = SubmitField("決定")
      cancel = SubmitField("取消")


# 送信フォーム(=FlaskFormクラス)を宣言・定義する.
class SendForm(FlaskForm):
      message = TextAreaField("メッセージ本文 :", default="", render_kw={"autocomplete": "off", "rows": "8"})
      decide = SubmitField("決定")
      cancel = SubmitField("取消")


# 語句学習フォーム(=FlaskFormクラス)を宣言・定義する.
class LearnWordForm(FlaskForm):
      menu_choices1 = consts.MENU_CHOICE_1_FOR_LEARN_WORD_FORM
      menu_choices2 = consts.MENU_CHOICE_2_FOR_LEARN_WORD_FORM
      menu_choices3 = consts.MENU_CHOICE_3_FOR_LEARN_WORD_FORM
      menu_choices4 = consts.MENU_CHOICE_4_FOR_LEARN_WORD_FORM
      menu_choices5 = consts.MENU_CHOICE_5_FOR_LEARN_WORD_FORM
      menu_choices6 = consts.MENU_CHOICE_FOR_UNIVERSAL_FORM
      spell_and_header = TextAreaField("綴り&見出し :", default="", render_kw={"autocomplete": "off", "rows": "4"})
      mean_and_content = TextAreaField("意味&内容 :", default="", render_kw={"autocomplete": "off", "rows": "4"})
      theme_tag = TextAreaField("主題タグ :", render_kw={"autocomplete": "off", "rows": "4"})
      intent = SelectField("意図 :", default="", choices=menu_choices1)
      sentiment = SelectField("感情 :", default="", choices=menu_choices2)
      sentiment_support = SelectField("感情補助 :", default="", choices=menu_choices3)
      strength = SelectField("強度 :", default="", choices=menu_choices4)
      part_of_speech = SelectField("品詞分類 :", default="", choices=menu_choices5)
      is_hidden = SelectField("秘匿の是非 :", default="", choices=menu_choices6)
      is_exclude = SelectField("非処理の是非 :", default="", choices=menu_choices6)
      decide = SubmitField("決定")
      cancel = SubmitField("取消")


# 主題学習フォーム(=FlaskFormクラス)を宣言・定義する.
class LearnThemeForm(FlaskForm):
      menu_choices = consts.MENU_CHOICE_FOR_UNIVERSAL_FORM
      spell_and_header = TextAreaField("綴り&見出し :", default="", render_kw={"autocomplete": "off", "rows": "4"})
      mean_and_content = TextAreaField("意味&内容 :", default="", render_kw={"autocomplete": "off", "rows": "4"})
      category_tag = TextAreaField("分類タグ :", default="", render_kw={"autocomplete": "off", "rows": "4"})
      is_hidden = SelectField("秘匿の是非 :", default="", choices=menu_choices)
      is_exclude = SelectField("非処理の是非 :", default="", choices=menu_choices)
      decide = SubmitField("決定")
      cancel = SubmitField("取消")


# 分類学習フォーム(=FlaskFormクラス)を宣言・定義する.
class LearnCategoryForm(FlaskForm):
      menu_choices = consts.MENU_CHOICE_FOR_UNIVERSAL_FORM
      spell_and_header = TextAreaField("綴り&見出し :", default="", render_kw={"autocomplete": "off", "rows": "4"})
      mean_and_content = TextAreaField("意味&内容 :", default="", render_kw={"autocomplete": "off", "rows": "4"})
      parent_category_tag = TextAreaField("親分類タグ :", default="", render_kw={"autocomplete": "off", "rows": "4"})
      sibling_category_tag = TextAreaField("兄弟分類タグ :", default="", render_kw={"autocomplete": "off", "rows": "4"})
      child_category_tag = TextAreaField("子分類タグ :", default="", render_kw={"autocomplete": "off", "rows": "4"})
      is_hidden = SelectField("秘匿の是非 :", default="", choices=menu_choices)
      is_exclude = SelectField("非処理の是非 :", default="", choices=menu_choices)
      decide = SubmitField("決定")
      cancel = SubmitField("取消")


# 知識学習フォーム(=FlaskFormクラス)を宣言・定義する.
class LearnKnowledgeForm(FlaskForm):
      menu_choices = consts.MENU_CHOICE_FOR_UNIVERSAL_FORM
      spell_and_header = TextAreaField("綴り&見出し :", default="", render_kw={"autocomplete": "off", "rows": "4"})
      mean_and_content = TextAreaField("意味&内容 :", default="", render_kw={"autocomplete": "off", "rows": "4"})
      category_tag = TextAreaField("分類タグ :", default="", render_kw={"autocomplete": "off", "rows": "4"})
      attached_image_file = FileField("添付イメージ(省略可) :", default="", render_kw=consts.IMAGE_FILE_FORMAT)
      attached_sound_file = FileField("添付サウンド(省略可) :", default="", render_kw=consts.SOUND_FILE_FORMAT)
      attached_video_file = FileField("添付ビデオ(省略可) :", default="", render_kw=consts.VIDEO_FILE_FORMAT)
      is_hidden = SelectField("秘匿の是非 :", default="", choices=menu_choices)
      is_exclude = SelectField("非処理の是非 :", default="", choices=menu_choices)
      decide = SubmitField("決定")
      cancel = SubmitField("取消")


# 規則学習フォーム(=FlaskFormクラス)を宣言・定義する.
class LearnRuleForm(FlaskForm):
      menu_choices = consts.MENU_CHOICE_FOR_UNIVERSAL_FORM
      spell_and_header = TextAreaField("綴り&見出し :", default="", render_kw={"autocomplete": "off", "rows": "4"})
      mean_and_content = TextAreaField("意味&内容 :", default="", render_kw={"autocomplete": "off", "rows": "4"})
      category_tag = TextAreaField("分類タグ :", default="", render_kw={"autocomplete": "off", "rows": "4"})
      inference_and_speculation_condition = TextAreaField("推論条件 :", default="", render_kw={"autocomplete": "off", "rows": "4"})
      inference_and_speculation_result = TextAreaField("推論結果 :", default="", render_kw={"autocomplete": "off", "rows": "4"})
      is_hidden = SelectField("秘匿の是非 :", default="", choices=menu_choices)
      is_exclude = SelectField("非処理の是非 :", default="", choices=menu_choices)
      decide = SubmitField("決定")
      cancel = SubmitField("取消")


# 反応学習フォーム(=FlaskFormクラス)を宣言・定義する.
class LearnReactionForm(FlaskForm):
      menu_choices = consts.MENU_CHOICE_FOR_UNIVERSAL_FORM
      spell_and_header = TextAreaField("綴り&見出し :", default="", render_kw={"autocomplete": "off", "rows": "4"})
      mean_and_content = TextAreaField("意味&内容 :", default="", render_kw={"autocomplete": "off", "rows": "4"})
      staff_psychology = TextAreaField("職員心理 :", default="", render_kw={"autocomplete": "off", "rows": "4"})
      scene_and_background = TextAreaField("情景&背景 :", default="", render_kw={"autocomplete": "off", "rows": "4"})
      message_example_from_staff = TextAreaField("職員メッセージ例 :", default="", render_kw={"autocomplete": "off", "rows": "4"})
      message_example_from_application = TextAreaField("アプリメッセージ例 :", default="", render_kw={"autocomplete": "off", "rows": "4"})
      is_hidden = SelectField("秘匿の是非 :", default="", choices=menu_choices)
      is_exclude = SelectField("非処理の是非 :", default="", choices=menu_choices)
      decide = SubmitField("決定")
      cancel = SubmitField("取消")

  
# 生成フォーム(=FlaskFormクラス)を宣言・定義する.
class GenerateForm(FlaskForm):
      menu_choices = consts.MENU_CHOICE_FOR_UNIVERSAL_FORM
      spell_and_header = TextAreaField("綴り&見出し :", default="", render_kw={"autocomplete": "off", "rows": "4"})
      mean_and_content = TextAreaField("意味&内容 :", default="", render_kw={"autocomplete": "off", "rows": "4"})
      attached_image_file = FileField("添付イメージ :", default="", render_kw=consts.IMAGE_FILE_FORMAT)
      attached_sound_file = FileField("添付サウンド :", default="", render_kw=consts.SOUND_FILE_FORMAT)
      attached_video_file = FileField("添付ビデオ :", default="", render_kw=consts.VIDEO_FILE_FORMAT)
      is_hidden = SelectField("秘匿の是非 :", default="", choices=menu_choices)
      is_exclude = SelectField("非処理の是非 :", default="", choices=menu_choices)
      decide = SubmitField("決定")
      cancel = SubmitField("取消")


# 入退登録フォーム(=FlaskFormクラス)を宣言・定義する.
class RegisterEnterOrExitForm(FlaskForm):
      menu_choices1 = consts.MENU_CHOICE_FOR_REGISTER_ENTER_OR_EXIT_FORM
      menu_choices2 = consts.MENU_CHOICE_FOR_UNIVERSAL_FORM
      staff_name = StringField("職員名 :", default="", render_kw={"autocomplete": "off"})
      staff_kana_name = StringField("職員カナ名 :", default="", render_kw={"autocomplete": "off"})
      reason = SelectField("入退理由 :", default="", choices=menu_choices1)
      enter_or_exit_at = DateTimeField("入退日時 :", default="", format=consts.GENERAL_DATE_FORMAT)
      enter_or_exit_at_second = IntegerField("入退日時-秒数 :", default="", render_kw={"autocomplete": "off"})
      is_hidden = SelectField("秘匿の是非 :", default="", choices=menu_choices2)
      is_exclude = SelectField("非処理の是非 :", default="", choices=menu_choices2)
      decide = SubmitField("決定")
      cancel = SubmitField("取消")


# 職員登録フォーム(=FlaskFormクラス)を宣言・定義する.
class RegisterStaffForm(FlaskForm):
      menu_choices1 = consts.MENU_CHOICE_1_FOR_REGISTER_STAFF_FORM
      menu_choices2 = consts.MENU_CHOICE_2_FOR_REGISTER_STAFF_FORM
      menu_choices3 = consts.MENU_CHOICE_FOR_UNIVERSAL_FORM
      name = StringField("職員名 :", default="", render_kw={"autocomplete": "off"})
      kana_name = StringField("職員カナ名 :", default="", render_kw={"autocomplete": "off"})
      password = PasswordField("パスワード :", default="", render_kw={"autocomplete": "off"})
      sex = SelectField("性別 :", default="", choices=menu_choices1)
      blood_type = SelectField("血液型 :", default="", choices=menu_choices2)
      birth_date = DateField("生年月日 :", default="", format=consts.BIRTH_DATE_FORMAT)
      is_hidden = SelectField("秘匿の是非 :", default="", choices=menu_choices3)
      is_exclude = SelectField("非処理の是非 :", default="", choices=menu_choices3)
      decide = SubmitField("決定")
      cancel = SubmitField("取消")


# 語句検索フォーム(=FlaskFormクラス)を宣言・定義する.
class SearchWordForm(FlaskForm):
      menu_choices1 = consts.MENU_CHOICE_1_FOR_SEARCH_WORD_FORM
      menu_choices2 = consts.MENU_CHOICE_2_FOR_SEARCH_WORD_FORM
      menu_choices3 = consts.MENU_CHOICE_3_FOR_SEARCH_WORD_FORM
      menu_choices4 = consts.MENU_CHOICE_4_FOR_SEARCH_WORD_FORM
      menu_choices5 = consts.MENU_CHOICE_5_FOR_SEARCH_WORD_FORM
      menu_choices6 = consts.MENU_CHOICE_1_FOR_SEARCH_FORM
      menu_choices7 = consts.MENU_CHOICE_2_FOR_SEARCH_FORM
      id = StringField("ID :", default="", render_kw={"autocomplete": "off"})
      spell_and_header = TextAreaField("綴り&見出し :", default="", render_kw={"autocomplete": "off", "rows": "4"})
      mean_and_content = TextAreaField("意味&内容 :", default="", render_kw={"autocomplete": "off", "rows": "4"})
      theme_tag = TextAreaField("主題タグ :", render_kw={"autocomplete": "off", "rows": "4"})
      intent = SelectField("意図 :", default="", choices=menu_choices1)
      sentiment = SelectField("感情 :", default="", choices=menu_choices2)
      sentiment_support = SelectField("感情補助 :", default="", choices=menu_choices3)
      strength = SelectField("強度 :", default="", choices=menu_choices4)
      part_of_speech = SelectField("品詞分類 :", default="", choices=menu_choices5)
      staff_name = StringField("職員名 :", default="", render_kw={"autocomplete": "off"})
      staff_kana_name = StringField("職員カナ名 :", default="", render_kw={"autocomplete": "off"})
      created_at_begin = DateTimeField("作成日時(検索区間の始め) :", default="", format=consts.GENERAL_DATE_FORMAT)
      created_at_end = DateTimeField("作成日時(検索区間の終り) :", default="", format=consts.GENERAL_DATE_FORMAT)
      updated_at_begin = DateTimeField("更新日時(検索区間の始め) :", default="", format=consts.GENERAL_DATE_FORMAT)
      updated_at_end = DateTimeField("更新日時(検索区間の終り) :", default="", format=consts.GENERAL_DATE_FORMAT)
      sort_condition = RadioField("整序条件 :", default="condition-1", choices=menu_choices6)
      extract_condition = RadioField("抽出条件 :", default="condition-1", choices=menu_choices7)
      decide = SubmitField("決定")
      cancel = SubmitField("取消")


# 主題検索フォーム(=FlaskFormクラス)を宣言・定義する.
class SearchThemeForm(FlaskForm):
      menu_choices1 = consts.MENU_CHOICE_1_FOR_SEARCH_FORM
      menu_choices2 = consts.MENU_CHOICE_2_FOR_SEARCH_FORM
      id = StringField("ID :", default="", render_kw={"autocomplete": "off"})
      spell_and_header = TextAreaField("綴り&見出し :", default="", render_kw={"autocomplete": "off", "rows": "4"})
      mean_and_content = TextAreaField("意味&内容 :", default="", render_kw={"autocomplete": "off", "rows": "4"})
      category_tag = TextAreaField("分類タグ :", default="", render_kw={"autocomplete": "off", "rows": "4"})
      staff_name = StringField("職員名 :", default="", render_kw={"autocomplete": "off"})
      staff_kana_name = StringField("職員カナ名 :", default="", render_kw={"autocomplete": "off"})
      created_at_begin = DateTimeField("作成日時(検索区間の始め) :", default="", format=consts.GENERAL_DATE_FORMAT)
      created_at_end = DateTimeField("作成日時(検索区間の終り) :", default="", format=consts.GENERAL_DATE_FORMAT)
      updated_at_begin = DateTimeField("更新日時(検索区間の始め) :", default="", format=consts.GENERAL_DATE_FORMAT)
      updated_at_end = DateTimeField("更新日時(検索区間の終り) :", default="", format=consts.GENERAL_DATE_FORMAT)
      sort_condition = RadioField("整序条件 :", default="condition-1", choices=menu_choices1)
      extract_condition = RadioField("抽出条件 :", default="condition-1", choices=menu_choices2)
      decide = SubmitField("決定")
      cancel = SubmitField("取消")


# 分類検索フォーム(=FlaskFormクラス)を宣言・定義する.
class SearchCategoryForm(FlaskForm):
      menu_choices1 = consts.MENU_CHOICE_1_FOR_SEARCH_FORM
      menu_choices2 = consts.MENU_CHOICE_2_FOR_SEARCH_FORM
      id = StringField("ID :", default="", render_kw={"autocomplete": "off"})
      spell_and_header = TextAreaField("綴り&見出し :", default="", render_kw={"autocomplete": "off", "rows": "4"})
      mean_and_content = TextAreaField("意味&内容 :", default="", render_kw={"autocomplete": "off", "rows": "4"})
      parent_category_tag = TextAreaField("親分類タグ :", default="", render_kw={"autocomplete": "off", "rows": "4"})
      sibling_category_tag = TextAreaField("兄弟分類タグ :", default="", render_kw={"autocomplete": "off", "rows": "4"})
      child_category_tag = TextAreaField("子分類タグ :", default="", render_kw={"autocomplete": "off", "rows": "4"})
      staff_name = StringField("職員名 :", default="", render_kw={"autocomplete": "off"})
      staff_kana_name = StringField("職員カナ名 :", default="", render_kw={"autocomplete": "off"})
      created_at_begin = DateTimeField("作成日時(検索区間の始め) :", default="", format=consts.GENERAL_DATE_FORMAT)
      created_at_end = DateTimeField("作成日時(検索区間の終り) :", default="", format=consts.GENERAL_DATE_FORMAT)
      updated_at_begin = DateTimeField("更新日時(検索区間の始め) :", default="", format=consts.GENERAL_DATE_FORMAT)
      updated_at_end = DateTimeField("更新日時(検索区間の終り) :", default="", format=consts.GENERAL_DATE_FORMAT)
      sort_condition = RadioField("整序条件 :", default="condition-1", choices=menu_choices1)
      extract_condition = RadioField("抽出条件 :", default="condition-1", choices=menu_choices2)
      decide = SubmitField("決定")
      cancel = SubmitField("取消")


# 知識検索フォーム(=FlaskFormクラス)を宣言・定義する.
class SearchKnowledgeForm(FlaskForm):
      menu_choices1 = consts.MENU_CHOICE_FOR_UNIVERSAL_FORM
      menu_choices2 = consts.MENU_CHOICE_1_FOR_SEARCH_FORM
      menu_choices3 = consts.MENU_CHOICE_2_FOR_SEARCH_FORM
      id = StringField("ID :", default="", render_kw={"autocomplete": "off"})
      spell_and_header = TextAreaField("綴り&見出し :", default="", render_kw={"autocomplete": "off", "rows": "4"})
      mean_and_content = TextAreaField("意味&内容 :", default="", render_kw={"autocomplete": "off", "rows": "4"})
      category_tag = TextAreaField("分類タグ :", default="", render_kw={"autocomplete": "off", "rows": "4"})
      has_image = SelectField("添付イメージの有無 :", default="", choices=menu_choices1)
      has_sound = SelectField("添付サウンドの有無 :", default="", choices=menu_choices1)
      has_video = SelectField("添付ビデオの有無 :", default="", choices=menu_choices1)
      staff_name = StringField("職員名 :", default="", render_kw={"autocomplete": "off"})
      staff_kana_name = StringField("職員カナ名 :", default="", render_kw={"autocomplete": "off"})
      created_at_begin = DateTimeField("作成日時(検索区間の始め) :", default="", format=consts.GENERAL_DATE_FORMAT)
      created_at_end = DateTimeField("作成日時(検索区間の終り) :", default="", format=consts.GENERAL_DATE_FORMAT)
      updated_at_begin = DateTimeField("更新日時(検索区間の始め) :", default="", format=consts.GENERAL_DATE_FORMAT)
      updated_at_end = DateTimeField("更新日時(検索区間の終り) :", default="", format=consts.GENERAL_DATE_FORMAT)
      sort_condition = RadioField("整序条件 :", default="condition-1", choices=menu_choices2)
      extract_condition = RadioField("抽出条件 :", default="condition-1", choices=menu_choices3)
      decide = SubmitField("決定")
      cancel = SubmitField("取消")


# 規則検索フォーム(=FlaskFormクラス)を宣言・定義する.
class SearchRuleForm(FlaskForm):
      menu_choices1 = consts.MENU_CHOICE_1_FOR_SEARCH_FORM
      menu_choices2 = consts.MENU_CHOICE_2_FOR_SEARCH_FORM
      id = StringField("ID :", default="", render_kw={"autocomplete": "off"})
      spell_and_header = TextAreaField("綴り&見出し :", default="", render_kw={"autocomplete": "off", "rows": "4"})
      mean_and_content = TextAreaField("意味&内容 :", default="", render_kw={"autocomplete": "off", "rows": "4"})
      category_tag = TextAreaField("分類タグ :", default="", render_kw={"autocomplete": "off", "rows": "4"})
      inference_and_speculation_condition = TextAreaField("推論条件 :", default="", render_kw={"autocomplete": "off", "rows": "4"})
      inference_and_speculation_result = TextAreaField("推論結果 :", default="", render_kw={"autocomplete": "off", "rows": "4"})
      staff_name = StringField("職員名 :", default="", render_kw={"autocomplete": "off"})
      staff_kana_name = StringField("職員カナ名 :", default="", render_kw={"autocomplete": "off"})
      created_at_begin = DateTimeField("作成日時(検索区間の始め) :", default="", format=consts.GENERAL_DATE_FORMAT)
      created_at_end = DateTimeField("作成日時(検索区間の終り) :", default="", format=consts.GENERAL_DATE_FORMAT)
      updated_at_begin = DateTimeField("更新日時(検索区間の始め) :", default="", format=consts.GENERAL_DATE_FORMAT)
      updated_at_end = DateTimeField("更新日時(検索区間の終り) :", default="", format=consts.GENERAL_DATE_FORMAT)
      sort_condition = RadioField("整序条件 :", default="condition-1", choices=menu_choices1)
      extract_condition = RadioField("抽出条件 :", default="condition-1", choices=menu_choices2)
      decide = SubmitField("決定")
      cancel = SubmitField("取消")


# 反応検索フォーム(=FlaskFormクラス)を宣言・定義する.
class SearchReactionForm(FlaskForm):
      menu_choices1 = consts.MENU_CHOICE_1_FOR_SEARCH_FORM
      menu_choices2 = consts.MENU_CHOICE_2_FOR_SEARCH_FORM
      id = StringField("ID :", default="", render_kw={"autocomplete": "off"})
      spell_and_header = TextAreaField("綴り&見出し :", default="", render_kw={"autocomplete": "off", "rows": "4"})
      mean_and_content = TextAreaField("意味&内容 :", default="", render_kw={"autocomplete": "off", "rows": "4"})
      staff_psychology = TextAreaField("職員心理 :", default="", render_kw={"autocomplete": "off", "rows": "4"})
      scene_and_background = TextAreaField("情景&背景 :", default="", render_kw={"autocomplete": "off", "rows": "4"})
      message_example_from_staff = TextAreaField("職員メッセージ例 :", default="", render_kw={"autocomplete": "off", "rows": "4"})
      message_example_from_application = TextAreaField("アプリメッセージ例 :", default="", render_kw={"autocomplete": "off", "rows": "4"})
      staff_name = StringField("職員名 :", default="", render_kw={"autocomplete": "off"})
      staff_kana_name = StringField("職員カナ名 :", default="", render_kw={"autocomplete": "off"})
      created_at_begin = DateTimeField("作成日時(検索区間の始め) :", default="", format=consts.GENERAL_DATE_FORMAT)
      created_at_end = DateTimeField("作成日時(検索区間の終り) :", default="", format=consts.GENERAL_DATE_FORMAT)
      updated_at_begin = DateTimeField("更新日時(検索区間の始め) :", default="", format=consts.GENERAL_DATE_FORMAT)
      updated_at_end = DateTimeField("更新日時(検索区間の終り) :", default="", format=consts.GENERAL_DATE_FORMAT)
      sort_condition = RadioField("整序条件 :", default="condition-1", choices=menu_choices1)
      extract_condition = RadioField("抽出条件 :", default="condition-1", choices=menu_choices2)
      decide = SubmitField("決定")
      cancel = SubmitField("取消")


# 生成検索フォーム(=FlaskFormクラス)を宣言・定義する.
class SearchGenerateForm(FlaskForm):
      menu_choices1 = consts.MENU_CHOICE_1_FOR_SEARCH_FORM
      menu_choices2 = consts.MENU_CHOICE_2_FOR_SEARCH_FORM
      id = StringField("ID :", default="", render_kw={"autocomplete": "off"})
      spell_and_header = TextAreaField("綴り&見出し :", default="", render_kw={"autocomplete": "off", "rows": "4"})
      mean_and_content = TextAreaField("意味&内容 :", default="", render_kw={"autocomplete": "off", "rows": "4"})
      staff_name = StringField("職員名 :", default="", render_kw={"autocomplete": "off"})
      staff_kana_name = StringField("職員カナ名 :", default="", render_kw={"autocomplete": "off"})
      created_at_begin = DateTimeField("作成日時(検索区間の始め) :", default="", format=consts.GENERAL_DATE_FORMAT)
      created_at_end = DateTimeField("作成日時(検索区間の終り) :", default="", format=consts.GENERAL_DATE_FORMAT)
      updated_at_begin = DateTimeField("更新日時(検索区間の始め) :", default="", format=consts.GENERAL_DATE_FORMAT)
      updated_at_end = DateTimeField("更新日時(検索区間の終り) :", default="", format=consts.GENERAL_DATE_FORMAT)
      sort_condition = RadioField("整序条件 :", default="condition-1", choices=menu_choices1)
      extract_condition = RadioField("抽出条件 :", default="condition-1", choices=menu_choices2)
      decide = SubmitField("決定")
      cancel = SubmitField("取消")


# 履歴検索フォーム(=FlaskFormクラス)を宣言・定義する.
class SearchHistoryForm(FlaskForm):
      menu_choices1 = consts.MENU_CHOICE_1_FOR_SEARCH_FORM
      menu_choices2 = consts.MENU_CHOICE_2_FOR_SEARCH_FORM
      id = StringField("ID :", default="", render_kw={"autocomplete": "off"})
      staff_message = TextAreaField("職員メッセージ :", default="", render_kw={"autocomplete": "off", "rows": "4"})
      application_message = TextAreaField("アプリメッセージ :", default="", render_kw={"autocomplete": "off", "rows": "4"})
      staff_name = StringField("職員名 :", default="", render_kw={"autocomplete": "off"})
      staff_kana_name = StringField("職員カナ名 :", default="", render_kw={"autocomplete": "off"})
      created_at_begin = DateTimeField("作成日時(検索区間の始め) :", default="", format=consts.GENERAL_DATE_FORMAT)
      created_at_end = DateTimeField("作成日時(検索区間の終り) :", default="", format=consts.GENERAL_DATE_FORMAT)
      updated_at_begin = DateTimeField("更新日時(検索区間の始め) :", default="", format=consts.GENERAL_DATE_FORMAT)
      updated_at_end = DateTimeField("更新日時(検索区間の終り) :", default="", format=consts.GENERAL_DATE_FORMAT)
      sort_condition = RadioField("整序条件 :", default="condition-1", choices=menu_choices1)
      extract_condition = RadioField("抽出条件 :", default="condition-1", choices=menu_choices2)
      decide = SubmitField("決定")
      cancel = SubmitField("取消")


# 入退検索フォーム(=FlaskFormクラス)を宣言・定義する.
class SearchEnterOrExitForm(FlaskForm):
      menu_choices1 = consts.MENU_CHOICE_FOR_SEARCH_ENTER_OR_EXIT_FORM
      menu_choices2 = consts.MENU_CHOICE_1_FOR_SEARCH_FORM
      menu_choices3 = consts.MENU_CHOICE_2_FOR_SEARCH_FORM
      id = StringField("ID :", default="", render_kw={"autocomplete": "off"})
      staff_name = StringField("職員名 :", default="", render_kw={"autocomplete": "off"})
      staff_kana_name = StringField("職員カナ名 :", default="", render_kw={"autocomplete": "off"})
      reason = SelectField("入退室理由 :", default="", choices=menu_choices1)
      enter_or_exit_at_begin = DateTimeField("入退日時(検索区間の始め) :", default="", format=consts.GENERAL_DATE_FORMAT)
      enter_or_exit_at_end = DateTimeField("入退日時(検索区間の終り) :", default="", format=consts.GENERAL_DATE_FORMAT)
      enter_or_exit_at_second = StringField("入退日時-秒数 :", default="", render_kw={"autocomplete": "off"})
      created_at_begin = DateTimeField("作成日時(検索区間の始め) :", default="", format=consts.GENERAL_DATE_FORMAT)
      created_at_end = DateTimeField("作成日時(検索区間の終り) :", default="", format=consts.GENERAL_DATE_FORMAT)
      updated_at_begin = DateTimeField("更新日時(検索区間の始め) :", default="", format=consts.GENERAL_DATE_FORMAT)
      updated_at_end = DateTimeField("更新日時(検索区間の終り) :", default="", format=consts.GENERAL_DATE_FORMAT)
      sort_condition = RadioField("整序条件 :", default="condition-1", choices=menu_choices2)
      extract_condition = RadioField("抽出条件 :", default="condition-1", choices=menu_choices3)
      decide = SubmitField("決定")
      cancel = SubmitField("取消")


# 職員検索フォーム(=FlaskFormクラス)を宣言・定義する.
class SearchStaffForm(FlaskForm):
      menu_choices1 = consts.MENU_CHOICE_1_FOR_REGISTER_STAFF_FORM
      menu_choices2 = consts.MENU_CHOICE_2_FOR_REGISTER_STAFF_FORM
      menu_choices3 = consts.MENU_CHOICE_1_FOR_SEARCH_FORM
      menu_choices4 = consts.MENU_CHOICE_2_FOR_SEARCH_FORM
      id = StringField("ID :", default="", render_kw={"autocomplete": "off"})
      name = StringField("職員名 :", default="", render_kw={"autocomplete": "off"})
      kana_name = StringField("職員カナ名 :", default="", render_kw={"autocomplete": "off"})
      sex = SelectField("性別 :", default="", choices=menu_choices1)
      blood_type = SelectField("血液型 :", default="", choices=menu_choices2)
      birth_date = DateField("生年月日 :", default="", format=consts.BIRTH_DATE_FORMAT)
      created_at_begin = DateTimeField("作成日時(検索区間の始め) :", default="", format=consts.GENERAL_DATE_FORMAT)
      created_at_end = DateTimeField("作成日時(検索区間の終り) :", default="", format=consts.GENERAL_DATE_FORMAT)
      updated_at_begin = DateTimeField("更新日時(検索区間の始め) :", default="", format=consts.GENERAL_DATE_FORMAT)
      updated_at_end = DateTimeField("更新日時(検索区間の終り) :", default="", format=consts.GENERAL_DATE_FORMAT)
      sort_condition = RadioField("整序条件 :", default="condition-1", choices=menu_choices3)
      extract_condition = RadioField("抽出条件 :", default="condition-1", choices=menu_choices4)
      decide = SubmitField("決定")
      cancel = SubmitField("取消")


# 語句変更フォーム(=FlaskFormクラス)を宣言・定義する.
class ModifyWordForm(FlaskForm):
      menu_choices1 = consts.MENU_CHOICE_1_FOR_SEARCH_WORD_FORM
      menu_choices2 = consts.MENU_CHOICE_2_FOR_SEARCH_WORD_FORM
      menu_choices3 = consts.MENU_CHOICE_3_FOR_SEARCH_WORD_FORM
      menu_choices4 = consts.MENU_CHOICE_4_FOR_SEARCH_WORD_FORM
      menu_choices5 = consts.MENU_CHOICE_5_FOR_SEARCH_WORD_FORM
      menu_choices6 = consts.MENU_CHOICE_FOR_UNIVERSAL_FORM
      spell_and_header = TextAreaField("綴り&見出し :", render_kw={"autocomplete": "off", "rows": "4"})
      mean_and_content = TextAreaField("意味&内容 :", render_kw={"autocomplete": "off", "rows": "4"})
      theme_tag = TextAreaField("主題タグ :", render_kw={"autocomplete": "off", "rows": "4"})
      intent = SelectField("意図 :", choices=menu_choices1)
      sentiment = SelectField("感情 :", choices=menu_choices2)
      sentiment_support = SelectField("感情補助 :", choices=menu_choices3)
      strength = SelectField("強度 :", choices=menu_choices4)
      part_of_speech = SelectField("品詞分類 :", choices=menu_choices5)
      staff_name = StringField("職員名 :", render_kw={"autocomplete": "off"})
      staff_kana_name = StringField("職員カナ名 :", render_kw={"autocomplete": "off"})
      is_hidden = SelectField("秘匿の是非 :", default="", choices=menu_choices6)
      is_exclude = SelectField("非処理の是非 :", default="", choices=menu_choices6)
      decide = SubmitField("決定")
      cancel = SubmitField("取消")


# 主題変更フォーム(=FlaskFormクラス)を宣言・定義する.
class ModifyThemeForm(FlaskForm):
      menu_choices = consts.MENU_CHOICE_FOR_UNIVERSAL_FORM
      spell_and_header = TextAreaField("綴り&見出し :", render_kw={"autocomplete": "off", "rows": "4"})
      mean_and_content = TextAreaField("意味&内容 :", render_kw={"autocomplete": "off", "rows": "4"})
      category_tag = TextAreaField("分類タグ :", render_kw={"autocomplete": "off", "rows": "4"})
      staff_name = StringField("職員名 :", render_kw={"autocomplete": "off"})
      staff_kana_name = StringField("職員カナ名 :", render_kw={"autocomplete": "off"})
      is_hidden = SelectField("秘匿の是非 :", default="", choices=menu_choices)
      is_exclude = SelectField("非処理の是非 :", default="", choices=menu_choices)
      decide = SubmitField("決定")
      cancel = SubmitField("取消")


# 分類変更フォーム(=FlaskFormクラス)を宣言・定義する.
class ModifyCategoryForm(FlaskForm):
      menu_choices = consts.MENU_CHOICE_FOR_UNIVERSAL_FORM
      spell_and_header = TextAreaField("綴り&見出し :", default="", render_kw={"autocomplete": "off", "rows": "4"})
      mean_and_content = TextAreaField("意味&内容 :", default="", render_kw={"autocomplete": "off", "rows": "4"})
      parent_category_tag = TextAreaField("親分類タグ :", default="", render_kw={"autocomplete": "off", "rows": "4"})
      sibling_category_tag = TextAreaField("兄弟分類タグ :", default="", render_kw={"autocomplete": "off", "rows": "4"})
      child_category_tag = TextAreaField("子分類タグ :", default="", render_kw={"autocomplete": "off", "rows": "4"})
      staff_name = StringField("職員名 :", default="", render_kw={"autocomplete": "off"})
      staff_kana_name = StringField("職員カナ名 :", default="", render_kw={"autocomplete": "off"})
      is_hidden = SelectField("秘匿の是非 :", default="", choices=menu_choices)
      is_exclude = SelectField("非処理の是非 :", default="", choices=menu_choices)
      decide = SubmitField("決定")
      cancel = SubmitField("取消")


# 知識変更フォーム(=FlaskFormクラス)を宣言・定義する.
class ModifyKnowledgeForm(FlaskForm):
      menu_choices = consts.MENU_CHOICE_FOR_UNIVERSAL_FORM
      spell_and_header = TextAreaField("綴り&見出し :", default="", render_kw={"autocomplete": "off", "rows": "4"})
      mean_and_content = TextAreaField("意味&内容 :", default="", render_kw={"autocomplete": "off", "rows": "4"})
      category_tag = TextAreaField("分類タグ :", default="", render_kw={"autocomplete": "off", "rows": "4"})
      attached_image_file = FileField("添付イメージ(省略可) :", default="", render_kw=consts.IMAGE_FILE_FORMAT)
      attached_sound_file = FileField("添付サウンド(省略可) :", default="", render_kw=consts.SOUND_FILE_FORMAT)
      attached_video_file = FileField("添付ビデオ(省略可) :", default="", render_kw=consts.VIDEO_FILE_FORMAT)
      staff_name = StringField("職員名 :", default="", render_kw={"autocomplete": "off"})
      staff_kana_name = StringField("職員カナ名 :", default="", render_kw={"autocomplete": "off"})
      is_hidden = SelectField("秘匿の是非 :", default="", choices=menu_choices)
      is_exclude = SelectField("非処理の是非 :", default="", choices=menu_choices)
      decide = SubmitField("決定")
      cancel = SubmitField("取消")


# 規則変更フォーム(=FlaskFormクラス)を宣言・定義する.
class ModifyRuleForm(FlaskForm):
      menu_choices = consts.MENU_CHOICE_FOR_UNIVERSAL_FORM
      spell_and_header = TextAreaField("綴り&見出し :", default="", render_kw={"autocomplete": "off", "rows": "4"})
      mean_and_content = TextAreaField("意味&内容 :", default="", render_kw={"autocomplete": "off", "rows": "4"})
      category_tag = TextAreaField("分類タグ :", default="", render_kw={"autocomplete": "off", "rows": "4"})
      inference_and_speculation_condition = TextAreaField("推論条件 :", default="", render_kw={"autocomplete": "off", "rows": "4"})
      inference_and_speculation_result = TextAreaField("推論結果 :", default="", render_kw={"autocomplete": "off", "rows": "4"})
      staff_name = StringField("職員名 :", render_kw={"autocomplete": "off"})
      staff_kana_name = StringField("職員カナ名 :", render_kw={"autocomplete": "off"})
      is_hidden = SelectField("秘匿の是非 :", default="", choices=menu_choices)
      is_exclude = SelectField("非処理の是非 :", default="", choices=menu_choices)
      decide = SubmitField("決定")
      cancel = SubmitField("取消")


# 反応変更フォーム(=FlaskFormクラス)を宣言・定義する.
class ModifyReactionForm(FlaskForm):
      menu_choices = consts.MENU_CHOICE_FOR_UNIVERSAL_FORM
      spell_and_header = TextAreaField("綴り&見出し :", default="", render_kw={"autocomplete": "off", "rows": "4"})
      mean_and_content = TextAreaField("意味&内容 :", default="", render_kw={"autocomplete": "off", "rows": "4"})
      staff_psychology = TextAreaField("職員心理 :", default="", render_kw={"autocomplete": "off", "rows": "4"})
      scene_and_background = TextAreaField("情景&背景 :", default="", render_kw={"autocomplete": "off", "rows": "4"})
      message_example_from_staff = TextAreaField("職員メッセージ例 :", default="", render_kw={"autocomplete": "off", "rows": "4"})
      message_example_from_application = TextAreaField("アプリメッセージ例 :", default="", render_kw={"autocomplete": "off", "rows": "4"})
      staff_name = StringField("職員名 :", render_kw={"autocomplete": "off"})
      staff_kana_name = StringField("職員カナ名 :", render_kw={"autocomplete": "off"})
      is_hidden = SelectField("秘匿の是非 :", default="", choices=menu_choices)
      is_exclude = SelectField("非処理の是非 :", default="", choices=menu_choices)
      decide = SubmitField("決定")
      cancel = SubmitField("取消")


# 入退変更フォーム(=FlaskFormクラス)を宣言・定義する.
class ModifyEnterOrExitForm(FlaskForm):
      menu_choices1 = consts.MENU_CHOICE_FOR_REGISTER_ENTER_OR_EXIT_FORM
      menu_choices2 = consts.MENU_CHOICE_FOR_UNIVERSAL_FORM
      staff_name = StringField("職員名 :", default="", render_kw={"autocomplete": "off"})
      staff_kana_name = StringField("職員カナ名 :", default="", render_kw={"autocomplete": "off"})
      reason = SelectField("入退室理由 :", default="", choices=menu_choices1)
      enter_or_exit_at = DateTimeField("入退日時 :", default="", format=consts.GENERAL_DATE_FORMAT)
      enter_or_exit_at_second = IntegerField("入退日時-秒数 :", default="", render_kw={"autocomplete": "off"})
      is_hidden = SelectField("秘匿の是非 :", default="", choices=menu_choices2)
      is_exclude = SelectField("非処理の是非 :", default="", choices=menu_choices2)
      decide = SubmitField("決定")
      cancel = SubmitField("取消")


# 職員変更フォーム(=FlaskFormクラス)を宣言・定義する.
class ModifyStaffForm(FlaskForm):
      menu_choices1 = consts.MENU_CHOICE_1_FOR_REGISTER_STAFF_FORM
      menu_choices2 = consts.MENU_CHOICE_2_FOR_REGISTER_STAFF_FORM
      menu_choices3 = consts.MENU_CHOICE_FOR_UNIVERSAL_FORM
      name = StringField("職員名 :", default="", render_kw={"autocomplete": "off"})
      kana_name = StringField("職員カナ名 :", default="", render_kw={"autocomplete": "off"})
      # password = PasswordField("パスワード :", default="", render_kw={"autocomplete": "off"})
      sex = SelectField("性別 :", default="", choices=menu_choices1)
      blood_type = SelectField("血液型 :", default="", choices=menu_choices2)
      birth_date = DateField("生年月日 :", default="", format=consts.BIRTH_DATE_FORMAT)
      is_hidden = SelectField("秘匿の是非 :", default="", choices=menu_choices3)
      is_exclude = SelectField("非処理の是非 :", default="", choices=menu_choices3)
      decide = SubmitField("決定")
      cancel = SubmitField("取消")


# 語句詳細フォーム(=FlaskFormクラス)を宣言・定義する.
class DetailWordForm(FlaskForm):
      menu_choices1 = consts.MENU_CHOICE_1_FOR_DETAIL_WORD_FORM
      menu_choices2 = consts.MENU_CHOICE_2_FOR_DETAIL_WORD_FORM
      menu_choices3 = consts.MENU_CHOICE_3_FOR_DETAIL_WORD_FORM
      menu_choices4 = consts.MENU_CHOICE_4_FOR_DETAIL_WORD_FORM
      menu_choices5 = consts.MENU_CHOICE_5_FOR_DETAIL_WORD_FORM
      menu_choices6 = consts.MENU_CHOICE_FOR_UNIVERSAL_FORM
      id = StringField("ID :", default="", render_kw={"disabled": True})
      spell_and_header = TextAreaField("綴り&見出し :", default="", render_kw={"rows": "4", "disabled": True})
      mean_and_content = TextAreaField("意味&内容 :", default="", render_kw={"rows": "4", "disabled": True})
      concept_and_notion = TextAreaField("概念&観念 :", default="", render_kw={"rows": "4", "disabled": True})
      theme_tag = TextAreaField("主題タグ :", render_kw={"autocomplete": "off", "rows": "4", "disabled": True})
      intent = SelectField("意図 :", default="", choices=menu_choices1, render_kw={"disabled": True})
      sentiment = SelectField("感情 :", default="", choices=menu_choices2, render_kw={"disabled": True})
      sentiment_support = SelectField("感情補助 :", default="", choices=menu_choices3, render_kw={"disabled": True})
      strength = SelectField("強度 :", default="", choices=menu_choices4, render_kw={"disabled": True})
      part_of_speech = SelectField("品詞分類 :", default="", choices=menu_choices5, render_kw={"disabled": True})
      staff_name = StringField("職員名 :", default="", render_kw={"disabled": True})
      staff_kana_name = StringField("職員カナ名 :", default="", render_kw={"disabled": True})
      created_at = DateTimeField("作成日時 :", default="", format=consts.GENERAL_DATE_FORMAT, render_kw={"disabled": True})
      updated_at = DateTimeField("更新日時 :", default="", format=consts.GENERAL_DATE_FORMAT, render_kw={"disabled": True})
      is_hidden = SelectField("秘匿の是非 :", default="", choices=menu_choices6, render_kw={"disabled": True})
      is_exclude = SelectField("非処理の是非 :", default="", choices=menu_choices6, render_kw={"disabled": True})


# 主題詳細フォーム(=FlaskFormクラス)を宣言・定義する.
class DetailThemeForm(FlaskForm):
      menu_choices = consts.MENU_CHOICE_FOR_UNIVERSAL_FORM
      id = StringField("ID :", default="", render_kw={"disabled": True})
      spell_and_header = TextAreaField("綴り&見出し :", default="", render_kw={"rows": "4", "disabled": True})
      mean_and_content = TextAreaField("意味&内容 :", default="", render_kw={"rows": "4", "disabled": True})
      concept_and_notion = TextAreaField("概念&観念 :", default="", render_kw={"rows": "4", "disabled": True})
      category_tag = TextAreaField("分類タグ :", default="", render_kw={"rows": "4", "disabled": True})
      staff_name = StringField("職員名 :", default="", render_kw={"disabled": True})
      staff_kana_name = StringField("職員カナ名 :", default="", render_kw={"disabled": True})
      created_at = DateTimeField("作成日時 :", default="", format=consts.GENERAL_DATE_FORMAT, render_kw={"disabled": True})
      updated_at = DateTimeField("更新日時 :", default="", format=consts.GENERAL_DATE_FORMAT, render_kw={"disabled": True})
      is_hidden = SelectField("秘匿の是非 :", default="", choices=menu_choices, render_kw={"disabled": True})
      is_exclude = SelectField("非処理の是非 :", default="", choices=menu_choices, render_kw={"disabled": True})


# 分類詳細フォーム(=FlaskFormクラス)を宣言・定義する.
class DetailCategoryForm(FlaskForm):
      menu_choices = consts.MENU_CHOICE_FOR_UNIVERSAL_FORM
      id = StringField("ID :", default="", render_kw={"disabled": True})
      spell_and_header = TextAreaField("綴り&見出し :", default="", render_kw={"rows": "4", "disabled": True})
      mean_and_content = TextAreaField("意味&内容 :", default="", render_kw={"rows": "4", "disabled": True})
      concept_and_notion = TextAreaField("概念&観念 :", default="", render_kw={"rows": "4", "disabled": True})
      parent_category_tag = TextAreaField("親分類タグ :", default="", render_kw={"rows": "4", "disabled": True})
      sibling_category_tag = TextAreaField("兄弟分類タグ :", default="", render_kw={"rows": "4", "disabled": True})
      child_category_tag = TextAreaField("子分類タグ :", default="", render_kw={"rows": "4", "disabled": True})
      staff_name = StringField("職員名 :", default="", render_kw={"disabled": True})
      staff_kana_name = StringField("職員カナ名 :", default="", render_kw={"disabled": True})
      created_at = DateTimeField("作成日時 :", default="", format=consts.GENERAL_DATE_FORMAT, render_kw={"disabled": True})
      updated_at = DateTimeField("更新日時 :", default="", format=consts.GENERAL_DATE_FORMAT, render_kw={"disabled": True})
      is_hidden = SelectField("秘匿の是非 :", default="", choices=menu_choices, render_kw={"disabled": True})
      is_exclude = SelectField("非処理の是非 :", default="", choices=menu_choices, render_kw={"disabled": True})


# 知識詳細フォーム(=FlaskFormクラス)を宣言・定義する.
class DetailKnowledgeForm(FlaskForm):
      menu_choices = consts.MENU_CHOICE_FOR_UNIVERSAL_FORM
      id = StringField("ID :", default="", render_kw={"disabled": True})
      spell_and_header = TextAreaField("綴り&見出し :", default="", render_kw={"rows": "4", "disabled": True})
      mean_and_content = TextAreaField("意味&内容 :", default="", render_kw={"rows": "4", "disabled": True})
      concept_and_notion = TextAreaField("概念&観念 :", default="", render_kw={"rows": "4", "disabled": True})
      category_tag = TextAreaField("分類タグ :", default="", render_kw={"rows": "4", "disabled": True})
      archived_image_file_path = StringField("アーカイブ済イメージのパス :", default="", render_kw={"disabled": True})
      archived_sound_file_path = StringField("アーカイブ済サウンドのパス :", default="", render_kw={"disabled": True})
      archived_video_file_path = StringField("アーカイブ済ビデオのパス :", default="", render_kw={"disabled": True})
      staff_name = StringField("職員名 :", default="", render_kw={"disabled": True})
      staff_kana_name = StringField("職員カナ名 :", default="", render_kw={"disabled": True})
      created_at = DateTimeField("作成日時 :", default="", format=consts.GENERAL_DATE_FORMAT, render_kw={"disabled": True})
      updated_at = DateTimeField("更新日時 :", default="", format=consts.GENERAL_DATE_FORMAT, render_kw={"disabled": True})
      is_hidden = SelectField("秘匿の是非 :", default="", choices=menu_choices, render_kw={"disabled": True})
      is_exclude = SelectField("非処理の是非 :", default="", choices=menu_choices, render_kw={"disabled": True})


# 規則詳細フォーム(=FlaskFormクラス)を宣言・定義する.
class DetailRuleForm(FlaskForm):
      menu_choices = consts.MENU_CHOICE_FOR_UNIVERSAL_FORM
      id = StringField("ID :", default="", render_kw={"disabled": True})
      spell_and_header = TextAreaField("綴り&見出し :", default="", render_kw={"rows": "4", "disabled": True})
      mean_and_content = TextAreaField("意味&内容 :", default="", render_kw={"rows": "4", "disabled": True})
      concept_and_notion = TextAreaField("概念&観念 :", default="", render_kw={"rows": "4", "disabled": True})
      category_tag = TextAreaField("分類タグ :", default="", render_kw={"rows": "4", "disabled": True})
      inference_and_speculation_condition = TextAreaField("推論条件 :", default="", render_kw={"rows": "4", "disabled": True})
      inference_and_speculation_result = TextAreaField("推論結果 :", default="", render_kw={"rows": "4", "disabled": True})
      staff_name = StringField("職員名 :", default="", render_kw={"disabled": True})
      staff_kana_name = StringField("職員カナ名 :", default="", render_kw={"disabled": True})
      created_at = DateTimeField("作成日時 :", default="", format=consts.GENERAL_DATE_FORMAT, render_kw={"disabled": True})
      updated_at = DateTimeField("更新日時 :", default="", format=consts.GENERAL_DATE_FORMAT, render_kw={"disabled": True})
      is_hidden = SelectField("秘匿の是非 :", default="", choices=menu_choices, render_kw={"disabled": True})
      is_exclude = SelectField("非処理の是非 :", default="", choices=menu_choices, render_kw={"disabled": True})


# 反応詳細フォーム(=FlaskFormクラス)を宣言・定義する.
class DetailReactionForm(FlaskForm):
      menu_choices = consts.MENU_CHOICE_FOR_UNIVERSAL_FORM
      id = StringField("ID :", default="", render_kw={"disabled": True})
      spell_and_header = TextAreaField("綴り&見出し :", default="", render_kw={"rows": "4", "disabled": True})
      mean_and_content = TextAreaField("意味&内容 :", default="", render_kw={"rows": "4", "disabled": True})
      concept_and_notion = TextAreaField("概念&観念 :", default="", render_kw={"rows": "4", "disabled": True})
      staff_psychology = TextAreaField("職員心理 :", default="", render_kw={"rows": "4", "disabled": True})
      scene_and_background = TextAreaField("情景&背景 :", default="", render_kw={"rows": "4", "disabled": True})
      message_example_from_staff = TextAreaField("職員メッセージ例 :", default="", render_kw={"rows": "4", "disabled": True})
      message_example_from_application = TextAreaField("アプリメッセージ例 :", default="", render_kw={"rows": "4", "disabled": True})
      staff_name = StringField("職員名 :", default="", render_kw={"disabled": True})
      staff_kana_name = StringField("職員カナ名 :", default="", render_kw={"disabled": True})
      created_at = DateTimeField("作成日時 :", default="", format=consts.GENERAL_DATE_FORMAT, render_kw={"disabled": True})
      updated_at = DateTimeField("更新日時 :", default="", format=consts.GENERAL_DATE_FORMAT, render_kw={"disabled": True})
      is_hidden = SelectField("秘匿の是非 :", default="", choices=menu_choices, render_kw={"disabled": True})
      is_exclude = SelectField("非処理の是非 :", default="", choices=menu_choices, render_kw={"disabled": True})
      decide = SubmitField("決定")
      cancel = SubmitField("取消")


# 生成詳細フォーム(=FlaskFormクラス)を宣言・定義する.
class DetailGenerateForm(FlaskForm):
      menu_choices = consts.MENU_CHOICE_FOR_UNIVERSAL_FORM
      id = StringField("ID :", default="", render_kw={"disabled": True})
      spell_and_header = TextAreaField("綴り&見出し :", default="", render_kw={"rows": "4", "disabled": True})
      mean_and_content = TextAreaField("意味&内容 :", default="", render_kw={"rows": "4", "disabled": True})
      concept_and_notion = TextAreaField("概念&観念 :", default="", render_kw={"rows": "4", "disabled": True})
      generated_file_path = StringField("生成ファイルのパス :", default="", render_kw={"disabled": True})
      staff_name = StringField("職員名 :", default="", render_kw={"disabled": True})
      staff_kana_name = StringField("職員カナ名 :", default="", render_kw={"disabled": True})
      created_at = DateTimeField("作成日時 :", default="", format=consts.GENERAL_DATE_FORMAT, render_kw={"disabled": True})
      updated_at = DateTimeField("更新日時 :", default="", format=consts.GENERAL_DATE_FORMAT, render_kw={"disabled": True})
      is_hidden = SelectField("秘匿の是非 :", default="", choices=menu_choices, render_kw={"disabled": True})
      is_exclude = SelectField("非処理の是非 :", default="", choices=menu_choices, render_kw={"disabled": True})


# 履歴詳細フォーム(=FlaskFormクラス)を宣言・定義する.
class DetailHistoryForm(FlaskForm):
      menu_choices = consts.MENU_CHOICE_FOR_UNIVERSAL_FORM
      id = StringField("ID :", default="", render_kw={"disabled": True})
      staff_message = TextAreaField("職員メッセージ :", default="", render_kw={"rows": "4", "disabled": True})
      application_message = TextAreaField("アプリメッセージ :", default="", render_kw={"rows": "4", "disabled": True})
      staff_name = StringField("職員名 :", default="", render_kw={"disabled": True})
      staff_kana_name = StringField("職員カナ名 :", default="", render_kw={"disabled": True})
      created_at = DateTimeField("作成日時 :", default="", format=consts.GENERAL_DATE_FORMAT, render_kw={"disabled": True})
      updated_at = DateTimeField("更新日時 :", default="", format=consts.GENERAL_DATE_FORMAT, render_kw={"disabled": True})
      is_hidden = SelectField("秘匿の是非 :", default="", choices=menu_choices, render_kw={"disabled": True})
      is_exclude = SelectField("非処理の是非 :", default="", choices=menu_choices, render_kw={"disabled": True})


# 入退詳細フォーム(=FlaskFormクラス)を宣言・定義する.
class DetailEnterOrExitForm(FlaskForm):
      menu_choices1 = consts.MENU_CHOICE_FOR_REGISTER_ENTER_OR_EXIT_FORM
      menu_choices2 = consts.MENU_CHOICE_FOR_UNIVERSAL_FORM
      id = StringField("ID :", default="", render_kw={"disabled": True})
      staff_name = StringField("職員名 :", default="", render_kw={"disabled": True})
      staff_kana_name = StringField("職員カナ名 :", default="", render_kw={"disabled": True})
      reason = SelectField("入退室理由 :", default="", choices=menu_choices1, render_kw={"disabled": True})
      enter_or_exit_at = DateTimeField("入退日時 :", default="", format=consts.GENERAL_DATE_FORMAT, render_kw={"disabled": True})
      enter_or_exit_at_second = IntegerField("入退日時-秒数 :", default="", render_kw={"disabled": True})
      created_at = DateTimeField("作成日時 :", default="", format=consts.GENERAL_DATE_FORMAT, render_kw={"disabled": True})
      updated_at = DateTimeField("更新日時 :", default="", format=consts.GENERAL_DATE_FORMAT, render_kw={"disabled": True})
      is_hidden = SelectField("秘匿の是非 :", default="", choices=menu_choices2, render_kw={"disabled": True})
      is_exclude = SelectField("非処理の是非 :", default="", choices=menu_choices2, render_kw={"disabled": True})


# 職員詳細フォーム(=FlaskFormクラス)を宣言・定義する.
class DetailStaffForm(FlaskForm):
      menu_choices1 = consts.MENU_CHOICE_1_FOR_REGISTER_STAFF_FORM
      menu_choices2 = consts.MENU_CHOICE_2_FOR_REGISTER_STAFF_FORM
      menu_choices3 = consts.MENU_CHOICE_FOR_UNIVERSAL_FORM
      id = StringField("ID :", default="", render_kw={"disabled": True})
      name = StringField("職員名 :", default="", render_kw={"disabled": True})
      kana_name = StringField("職員カナ名 :", default="", render_kw={"disabled": True})
      password = StringField("パスワード :", default="", render_kw={"disabled": True})
      sex = SelectField("性別 :", default="", choices=menu_choices1, render_kw={"disabled": True})
      blood_type = SelectField("血液型 :", default="", choices=menu_choices2, render_kw={"disabled": True})
      birth_date = DateField("生年月日 :", default="", format=consts.BIRTH_DATE_FORMAT, render_kw={"disabled": True})
      created_at = DateTimeField("作成日時 :", default="", format=consts.GENERAL_DATE_FORMAT, render_kw={"disabled": True})
      updated_at = DateTimeField("更新日時 :", default="", format=consts.GENERAL_DATE_FORMAT, render_kw={"disabled": True})
      is_hidden = SelectField("秘匿の是非 :", default="", choices=menu_choices3, render_kw={"disabled": True})
      is_exclude = SelectField("非処理の是非 :", default="", choices=menu_choices3, render_kw={"disabled": True})


# 語句取込フォーム(=FlaskFormクラス)を宣言・定義する.
class ImportWordForm(FlaskForm):
      imported_file = FileField("取込ファイル :", default="", render_kw=consts.DOCUMENT_FILE_FORMAT)
      decide = SubmitField("決定")
      cancel = SubmitField("取消")


# 主題取込フォーム(=FlaskFormクラス)を宣言・定義する.
class ImportThemeForm(FlaskForm):
      imported_file = FileField("取込ファイル :", default="", render_kw=consts.DOCUMENT_FILE_FORMAT)
      decide = SubmitField("決定")
      cancel = SubmitField("取消")


# 分類取込フォーム(=FlaskFormクラス)を宣言・定義する.
class ImportCategoryForm(FlaskForm):
      imported_file = FileField("取込ファイル :", default="", render_kw=consts.DOCUMENT_FILE_FORMAT)
      decide = SubmitField("決定")
      cancel = SubmitField("取消")


# 知識取込フォーム(=FlaskFormクラス)を宣言・定義する.
class ImportKnowledgeForm(FlaskForm):
      imported_file = FileField("取込ファイル :", default="", render_kw=consts.DOCUMENT_FILE_FORMAT)
      decide = SubmitField("決定")
      cancel = SubmitField("取消")


# 規則取込フォーム(=FlaskFormクラス)を宣言・定義する.
class ImportRuleForm(FlaskForm):
      imported_file = FileField("取込ファイル :", default="", render_kw=consts.DOCUMENT_FILE_FORMAT)
      decide = SubmitField("決定")
      cancel = SubmitField("取消")


# 反応取込フォーム(=FlaskFormクラス)を宣言・定義する.
class ImportReactionForm(FlaskForm):
      imported_file = FileField("取込ファイル :", default="", render_kw=consts.DOCUMENT_FILE_FORMAT)
      decide = SubmitField("決定")
      cancel = SubmitField("取消")


# 生成取込フォーム(=FlaskFormクラス)を宣言・定義する.
class ImportGenerateForm(FlaskForm):
      imported_file = FileField("取込ファイル :", default="", render_kw=consts.DOCUMENT_FILE_FORMAT)
      decide = SubmitField("決定")
      cancel = SubmitField("取消")


# 入退取込フォーム(=FlaskFormクラス)を宣言・定義する.
class ImportEnterOrExitForm(FlaskForm):
      imported_file = FileField("取込ファイル :", default="", render_kw=consts.PLAIN_FILE_FORMAT)
      decide = SubmitField("決定")
      cancel = SubmitField("取消")


# 語句書出フォーム(=FlaskFormクラス)を宣言・定義する.
class ExportWordForm(FlaskForm):
      decide = SubmitField("決定")
      cancel = SubmitField("取消")


# 主題書出フォーム(=FlaskFormクラス)を宣言・定義する.
class ExportThemeForm(FlaskForm):
      decide = SubmitField("決定")
      cancel = SubmitField("取消")


# 分類書出フォーム(=FlaskFormクラス)を宣言・定義する.
class ExportCategoryForm(FlaskForm):
      decide = SubmitField("決定")
      cancel = SubmitField("取消")


# 知識書出フォーム(=FlaskFormクラス)を宣言・定義する.
class ExportKnowledgeForm(FlaskForm):
      decide = SubmitField("決定")
      cancel = SubmitField("取消")


# 規則書出フォーム(=FlaskFormクラス)を宣言・定義する.
class ExportRuleForm(FlaskForm):
      decide = SubmitField("決定")
      cancel = SubmitField("取消")


# 反応書出フォーム(=FlaskFormクラス)を宣言・定義する.
class ExportReactionForm(FlaskForm):
      decide = SubmitField("決定")
      cancel = SubmitField("取消")


# 生成書出フォーム(=FlaskFormクラス)を宣言・定義する.
class ExportGenerateForm(FlaskForm):
      decide = SubmitField("決定")
      cancel = SubmitField("取消")


# 履歴書出フォーム(=FlaskFormクラス)を宣言・定義する.
class ExportHistoryForm(FlaskForm):
      decide = SubmitField("決定")
      cancel = SubmitField("取消")


# 入退書出フォーム(=FlaskFormクラス)を宣言・定義する.
class ExportEnterOrExitForm(FlaskForm):
      decide = SubmitField("決定")
      cancel = SubmitField("取消")


# 生成取得フォーム(=FlaskFormクラス)を宣言・定義する.
class RetrieveGenerateForm(FlaskForm):
      decide = SubmitField("決定")
      cancel = SubmitField("取消")


# 環境設定フォーム(=FlaskFormクラス)を宣言・定義する.
class EnvironmentSettingForm(FlaskForm):
      short_term_memory_size = IntegerField("短期記憶 :")
      long_term_memory_size = IntegerField("長期記憶 :")
      learn_depth = IntegerField("学習の深さ :")
      inference_and_speculation_depth = IntegerField("推論の深さ :")
      in_memorize = BooleanField("インメモリー高速化 :")
      dictionary_entries_integration = BooleanField("辞書内項目の統合化 :")
      global_Information_sharing = BooleanField("グローバル情報共有 :")
      background_processing = BooleanField("バックグラウンド化 :")
      policy_based_decisions = BooleanField("ポリシーベース決定 :")
      personalized_conversations = BooleanField("会話進行の個人特化 :")
      decide = SubmitField("決定")
      cancel = SubmitField("取消")


# 機密設定フォーム(=FlaskFormクラス)を宣言・定義する.
class SecuritySettingForm(FlaskForm):
      new_password = PasswordField("新しいパスワード :", default="", render_kw={"autocomplete": "off"})
      decide = SubmitField("決定")
      cancel = SubmitField("取消")


# DBリセットフォーム(=FlaskFormクラス)を宣言・定義する.
class ResetDatabaseForm(FlaskForm):
      words = BooleanField("語句 :")
      themes = BooleanField("主題 :")
      categories = BooleanField("分類 :")
      knowledges = BooleanField("知識 :")
      rules = BooleanField("規則 :")
      reactions = BooleanField("反応 :")
      generates = BooleanField("生成 :")
      histories = BooleanField("履歴 :")
      enters_or_exits = BooleanField("入退 :")
      staffs = BooleanField("職員 :")
      decide = SubmitField("決定")
      cancel = SubmitField("取消")