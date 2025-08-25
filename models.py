# coding: utf-8




# 既成のモジュールをインポートする.
import os
import sys
from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Text, Boolean, Date, DateTime, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.sql import func

# 設定のためのモジュールをインポートする.
import constants as consts




# SQLAlchemyを使用できるようにする.
engine = create_engine(consts.DATABASE_URI, isolation_level="AUTOCOMMIT", echo=False)

# すべてのテーブルの基底となるテーブルを宣言・定義する.
Base = declarative_base()

# セッションを作成・初期化する(=データベースエンジンとセッションの関連付けをする).
Session = sessionmaker(bind=engine)
db_session = Session(autocommit=False, autoflush=True, bind=engine)
db_session.expire_on_commit = False




# 語句テーブル(=SQLAlchemyクラス)を宣言・定義する.
class Word(Base):
      __tablename__ = "words"
      id = Column(Integer, primary_key=True, autoincrement=True)
      spell_and_header = Column(Text, nullable=False)
      mean_and_body = Column(Text, nullable=False)
      concept_and_notion = Column(Text, nullable=False)
      theme_tag = Column(Text, nullable=False)
      intent = Column(String(consts.INTENT_LENGTH), nullable=False)
      sentiment = Column(String(consts.SENTIMENT_LENGTH), nullable=False)
      sentiment_support = Column(String(consts.SENTIMENT_LENGTH), nullable=False)
      strength = Column(String(consts.STRENGTH_LENGTH), nullable=False)
      part_of_speech = Column(String(consts.PART_OF_SPEECH_LENGTH), nullable=False)
      first_character = Column(String(consts.FIRST_CHARACTER_LENGTH), nullable=False)
      last_character = Column(String(consts.LAST_CHARACTER_LENGTH), nullable=False)
      characters_count = Column(String(consts.CHARACTERS_COUNT_LENGTH), nullable=False)
      staff_name = Column(String(consts.STAFF_NAME_LENGTH), nullable=False)
      staff_kana_name = Column(String(consts.STAFF_KANA_NAME_LENGTH), nullable=False)
      created_at = Column(DateTime, nullable=False)
      updated_at = Column(DateTime, nullable=False)
      is_hidden = Column(Boolean, nullable=False)
      is_exclude = Column(Boolean, nullable=False)

      def __init__(self,
                   spell_and_header,
                   mean_and_body,
                   concept_and_notion,
                   theme_tag,
                   intent,
                   sentiment,
                   sentiment_support,
                   strength,
                   part_of_speech,
                   first_character,
                   last_character,
                   characters_count,
                   staff_name,
                   staff_kana_name,
                   created_at,
                   updated_at,
                   is_hidden,
                   is_exclude
                  ):
          self.spell_and_header = spell_and_header
          self.mean_and_body = mean_and_body
          self.concept_and_notion = concept_and_notion
          self.theme_tag = theme_tag
          self.intent = intent
          self.sentiment = sentiment
          self.sentiment_support = sentiment_support
          self.strength = strength
          self.part_of_speech = part_of_speech
          self.first_character = first_character
          self.last_character = last_character
          self.characters_count = characters_count
          self.staff_name = staff_name
          self.staff_kana_name = staff_kana_name
          self.created_at = created_at
          self.updated_at = updated_at
          self.is_hidden = is_hidden
          self.is_exclude = is_exclude


# 主題テーブル(=SQLAlchemyクラス)を宣言・定義する.
class Theme(Base):
      __tablename__ = "themes"
      id = Column(Integer, primary_key=True, autoincrement=True)
      spell_and_header = Column(Text, nullable=False)
      mean_and_body = Column(Text, nullable=False)
      concept_and_notion = Column(Text, nullable=False)
      category_tag = Column(Text, nullable=False)
      staff_name = Column(String(consts.STAFF_NAME_LENGTH), nullable=False)
      staff_kana_name = Column(String(consts.STAFF_KANA_NAME_LENGTH), nullable=False)
      created_at = Column(DateTime, default=datetime.now(timezone.utc))
      updated_at = Column(DateTime, default=datetime.now(timezone.utc))
      is_hidden = Column(Boolean, nullable=False)
      is_exclude = Column(Boolean, nullable=False)

      def __init__(self,
                   spell_and_header,
                   mean_and_body,
                   concept_and_notion,
                   category_tag,
                   staff_name,
                   staff_kana_name,
                   created_at,
                   updated_at,
                   is_hidden,
                   is_exclude
                   ):
          self.spell_and_header = spell_and_header
          self.mean_and_body = mean_and_body
          self.concept_and_notion = concept_and_notion
          self.category_tag = category_tag
          self.staff_name = staff_name
          self.staff_kana_name = staff_kana_name
          self.created_at = created_at
          self.updated_at = updated_at
          self.is_hidden = is_hidden
          self.is_exclude = is_exclude


# 分類テーブル(=SQLAlchemyクラス)を宣言・定義する.
class Category(Base):
      __tablename__ = "categories"
      id = Column(Integer, primary_key=True, autoincrement=True)
      spell_and_header = Column(Text, nullable=False)
      mean_and_body = Column(Text, nullable=False)
      concept_and_notion = Column(Text, nullable=False)
      parent_category_tag = Column(Text, nullable=False)
      sibling_category_tag = Column(Text, nullable=False)
      child_category_tag = Column(Text, nullable=False)
      staff_name = Column(String(consts.STAFF_NAME_LENGTH), nullable=False)
      staff_kana_name = Column(String(consts.STAFF_KANA_NAME_LENGTH), nullable=False)
      created_at = Column(DateTime, default=datetime.now(timezone.utc))
      updated_at = Column(DateTime, default=datetime.now(timezone.utc))
      is_hidden = Column(Boolean, nullable=False)
      is_exclude = Column(Boolean, nullable=False)

      def __init__(self,
                   spell_and_header,
                   mean_and_body,
                   concept_and_notion,
                   parent_category_tag,
                   sibling_category_tag,
                   child_category_tag,
                   staff_name,
                   staff_kana_name,
                   created_at,
                   updated_at,
                   is_hidden,
                   is_exclude                   
                   ):
          self.spell_and_header = spell_and_header
          self.mean_and_body = mean_and_body
          self.concept_and_notion = concept_and_notion
          self.parent_category_tag = parent_category_tag
          self.sibling_category_tag = sibling_category_tag
          self.child_category_tag = child_category_tag
          self.staff_name = staff_name
          self.staff_kana_name = staff_kana_name
          self.created_at = created_at
          self.updated_at = updated_at
          self.is_hidden = is_hidden
          self.is_exclude = is_exclude


# 事実テーブル(=SQLAlchemyクラス)を宣言・定義する.
class Fact(Base):
      __tablename__ = "facts"
      id = Column(Integer, primary_key=True, autoincrement=True)
      spell_and_header = Column(Text, nullable=False)
      mean_and_body = Column(Text, nullable=False)
      concept_and_notion = Column(Text, nullable=False)
      category_tag = Column(Text, nullable=False)
      archived_image_file_path = Column(String(consts.ARCHIVED_IMAGE_FILE_NAME_LENGTH), nullable=False)
      archived_sound_file_path = Column(String(consts.ARCHIVED_SOUND_FILE_NAME_LENGTH), nullable=False)
      archived_video_file_path = Column(String(consts.ARCHIVED_VIDEO_FILE_NAME_LENGTH), nullable=False)
      staff_name = Column(String(consts.STAFF_NAME_LENGTH), nullable=False)
      staff_kana_name = Column(String(consts.STAFF_KANA_NAME_LENGTH), nullable=False)
      created_at = Column(DateTime, default=datetime.now(timezone.utc))
      updated_at = Column(DateTime, default=datetime.now(timezone.utc))
      is_hidden = Column(Boolean, nullable=False)
      is_exclude = Column(Boolean, nullable=False)

      def __init__(self,
                   spell_and_header,
                   mean_and_body,
                   concept_and_notion,
                   category_tag,
                   archived_image_file_path,
                   archived_sound_file_path,
                   archived_video_file_path,
                   staff_name,
                   staff_kana_name,
                   created_at,
                   updated_at,
                   is_hidden,
                   is_exclude                   
                   ):
          self.spell_and_header = spell_and_header
          self.mean_and_body = mean_and_body
          self.concept_and_notion = concept_and_notion
          self.category_tag = category_tag
          self.archived_image_file_path = archived_image_file_path
          self.archived_sound_file_path = archived_sound_file_path
          self.archived_video_file_path = archived_video_file_path
          self.staff_name = staff_name
          self.staff_kana_name = staff_kana_name
          self.created_at = created_at
          self.updated_at = updated_at
          self.is_hidden = is_hidden
          self.is_exclude = is_exclude


# 規則テーブル(=SQLAlchemyクラス)を宣言・定義する.
class Rule(Base):
      __tablename__ = "rules"
      id = Column(Integer, primary_key=True, autoincrement=True)
      spell_and_header = Column(Text, nullable=False)
      mean_and_body = Column(Text, nullable=False)
      concept_and_notion = Column(Text, nullable=False)
      category_tag = Column(Text, nullable=False)
      inference_and_speculation_condition = Column(Text, nullable=False)
      inference_and_speculation_result = Column(Text, nullable=False)
      staff_name = Column(String(consts.STAFF_NAME_LENGTH), nullable=False)
      staff_kana_name = Column(String(consts.STAFF_KANA_NAME_LENGTH), nullable=False)
      created_at = Column(DateTime, default=datetime.now(timezone.utc))
      updated_at = Column(DateTime, default=datetime.now(timezone.utc))
      is_hidden = Column(Boolean, nullable=False)
      is_exclude = Column(Boolean, nullable=False)

      def __init__(self,
                   spell_and_header,
                   mean_and_body,
                   concept_and_notion,
                   category_tag,
                   inference_and_speculation_condition,
                   inference_and_speculation_result,
                   staff_name,
                   staff_kana_name,
                   created_at,
                   updated_at,
                   is_hidden,
                   is_exclude
                   ):
          self.spell_and_header = spell_and_header
          self.mean_and_body = mean_and_body
          self.concept_and_notion = concept_and_notion
          self.category_tag = category_tag
          self.inference_and_speculation_condition = inference_and_speculation_condition
          self.inference_and_speculation_result = inference_and_speculation_result
          self.staff_name = staff_name
          self.staff_kana_name = staff_kana_name
          self.created_at = created_at
          self.updated_at = updated_at
          self.is_hidden = is_hidden
          self.is_exclude = is_exclude


# 反応テーブル(=SQLAlchemyクラス)を宣言・定義する.
class Reaction(Base):
      __tablename__ = "reactions"
      id = Column(Integer, primary_key=True, autoincrement=True)
      spell_and_header = Column(Text, nullable=False)
      mean_and_body = Column(Text, nullable=False)
      concept_and_notion = Column(Text, nullable=False)
      staff_psychology = Column(Text, nullable=False)
      scene_and_background = Column(Text, nullable=False)
      staff_example_message = Column(Text, nullable=False)
      application_example_message = Column(Text, nullable=False)
      staff_name = Column(String(consts.STAFF_NAME_LENGTH), nullable=False)
      staff_kana_name = Column(String(consts.STAFF_KANA_NAME_LENGTH), nullable=False)
      created_at = Column(DateTime, default=datetime.now(timezone.utc))
      updated_at = Column(DateTime, default=datetime.now(timezone.utc))
      is_hidden = Column(Boolean, nullable=False)
      is_exclude = Column(Boolean, nullable=False)

      def __init__(self,
                   spell_and_header,
                   mean_and_body,
                   concept_and_notion,
                   staff_psychology,
                   scene_and_background,
                   staff_example_message,
                   application_example_message,
                   staff_name,
                   staff_kana_name,
                   created_at,
                   updated_at,
                   is_hidden,
                   is_exclude                   
                   ):
          self.spell_and_header = spell_and_header
          self.mean_and_body = mean_and_body
          self.concept_and_notion = concept_and_notion
          self.staff_psychology = staff_psychology
          self.scene_and_background = scene_and_background
          self.staff_example_message = staff_example_message
          self.application_example_message = application_example_message
          self.staff_name = staff_name
          self.staff_kana_name = staff_kana_name
          self.created_at = created_at
          self.updated_at = updated_at
          self.is_hidden = is_hidden
          self.is_exclude = is_exclude


# 生成テーブル(=SQLAlchemyクラス)を宣言・定義する.
class Generate(Base):
      __tablename__ = "generates"
      id = Column(Integer, primary_key=True, autoincrement=True)
      spell_and_header = Column(Text, nullable=False)
      mean_and_body = Column(Text, nullable=False)
      generated_file_path = Column(String(consts.GENERATED_FILE_NAME_LENGTH), nullable=False)
      staff_name = Column(String(consts.STAFF_NAME_LENGTH), nullable=False)
      staff_kana_name = Column(String(consts.STAFF_KANA_NAME_LENGTH), nullable=False)
      created_at = Column(DateTime, default=datetime.now(timezone.utc))
      updated_at = Column(DateTime, default=datetime.now(timezone.utc))
      is_hidden = Column(Boolean, nullable=False)
      is_exclude = Column(Boolean, nullable=False)

      def __init__(self,
                   spell_and_header,
                   mean_and_body,
                   generated_file_path,
                   staff_name,
                   staff_kana_name,
                   created_at,
                   updated_at,
                   is_hidden,
                   is_exclude
                   ):
          self.spell_and_header = spell_and_header
          self.mean_and_body = mean_and_body
          self.generated_file_path = generated_file_path
          self.staff_name = staff_name
          self.staff_kana_name = staff_kana_name
          self.created_at = created_at
          self.updated_at = updated_at
          self.is_hidden = is_hidden
          self.is_exclude = is_exclude


# 履歴テーブル(=SQLAlchemyクラス)を宣言・定義する.
class History(Base):
      __tablename__ = "histories"
      id = Column(Integer, primary_key=True, autoincrement=True)
      staff_text_message = Column(Text, nullable=False)
      application_text_message = Column(Text, nullable=False)
      staff_name = Column(String(consts.STAFF_NAME_LENGTH), nullable=False)
      staff_kana_name = Column(String(consts.STAFF_KANA_NAME_LENGTH), nullable=False)
      created_at = Column(DateTime, default=datetime.now(timezone.utc))
      updated_at = Column(DateTime, default=datetime.now(timezone.utc))
      is_hidden = Column(Boolean, nullable=False)
      is_exclude = Column(Boolean, nullable=False)

      def __init__(self,
                   staff_text_message,
                   application_text_message,
                   staff_name,
                   staff_kana_name,
                   created_at,
                   updated_at,
                   is_hidden,
                   is_exclude                   
                   ):
          self.staff_text_message = staff_text_message
          self.application_text_message = application_text_message
          self.staff_name = staff_name
          self.staff_kana_name = staff_kana_name
          self.created_at = created_at
          self.updated_at = updated_at
          self.is_hidden = is_hidden
          self.is_exclude = is_exclude


# 入退テーブル(=SQLAlchemyクラス)を宣言・定義する.
class EnterOrExit(Base):
      __tablename__ = "enters_or_exits"
      id = Column(Integer, primary_key=True, autoincrement=True)
      staff_name = Column(String(consts.STAFF_NAME_LENGTH), nullable=False)
      staff_kana_name = Column(String(consts.STAFF_KANA_NAME_LENGTH), nullable=False)
      reason = Column(String(consts.ENTER_OR_EXIT_REASON_LENGTH), nullable=False)
      enter_or_exit_at = Column(DateTime, nullable=False)
      enter_or_exit_at_second = Column(Integer, nullable=False)
      created_at = Column(DateTime, nullable=False)
      updated_at = Column(DateTime, nullable=False)
      is_hidden = Column(Boolean, nullable=False)
      is_exclude = Column(Boolean, nullable=False)

      def __init__(self,
                   staff_name,
                   staff_kana_name,
                   reason,
                   enter_or_exit_at,
                   enter_or_exit_at_second,
                   created_at,
                   updated_at,
                   is_hidden,
                   is_exclude                   
                   ):
          self.staff_name = staff_name
          self.staff_kana_name = staff_kana_name
          self.reason = reason
          self.enter_or_exit_at = enter_or_exit_at
          self.enter_or_exit_at_second = enter_or_exit_at_second
          self.created_at = created_at
          self.updated_at = updated_at
          self.is_hidden = is_hidden
          self.is_exclude = is_exclude


# 職員テーブル(=SQLAlchemyクラス)を宣言・定義する.
class Staff(Base):
      __tablename__ = "staffs"
      id = Column(Integer, primary_key=True, autoincrement=True)
      name = Column(String(consts.STAFF_NAME_LENGTH), unique=True, nullable=False)
      kana_name = Column(String(consts.STAFF_KANA_NAME_LENGTH), unique=True, nullable=False)
      hashed_password = Column(String(consts.HASHED_PASSWORD_LENGTH), nullable=False)
      sex = Column(String(consts.SEX_LENGTH), nullable=False)
      blood_type = Column(String(consts.BLOOD_TYPE_LENGTH), nullable=False)
      birth_date = Column(Date, nullable=False)
      created_at = Column(DateTime, default=datetime.now(timezone.utc))
      updated_at = Column(DateTime, default=datetime.now(timezone.utc))
      is_hidden = Column(Boolean, nullable=False)
      is_exclude = Column(Boolean, nullable=False)

      def __init__(self,
                   name,
                   kana_name,
                   hashed_password,
                   sex,
                   blood_type,
                   birth_date,
                   created_at,
                   updated_at,
                   is_hidden,
                   is_exclude                   
                   ):
          self.name = name
          self.kana_name = kana_name
          self.hashed_password = hashed_password
          self.sex = sex
          self.blood_type = blood_type
          self.birth_date = birth_date
          self.created_at = created_at
          self.updated_at = updated_at
          self.is_hidden = is_hidden
          self.is_exclude = is_exclude


# データベースを作成・初期化する(=各種テーブルを一括で作成する).
Base.metadata.create_all(bind=engine, checkfirst=True)