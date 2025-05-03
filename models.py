# coding: utf-8




# 既成のモジュールをインポートする.
import os
import sys
from sqlalchemy import Column, Integer, String, Text, Boolean, create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

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
      mean_and_content = Column(Text, nullable=False)
      concept_and_notion = Column(Text, nullable=False)
      intent = Column(String(consts.INTENT_LENGTH), nullable=False)
      sentiment = Column(String(consts.SENTIMENT_LENGTH), nullable=False)
      strength = Column(String(consts.STRENGTH_LENGTH), nullable=False)
      part_of_speech = Column(String(consts.PART_OF_SPEECH_LENGTH), nullable=False)
      first_character = Column(String(consts.FIRST_CHARACTER_LENGTH), nullable=False)
      characters_count = Column(String(consts.CHARACTERS_COUNT_LENGTH), nullable=False)
      staff_name = Column(String(consts.STAFF_NAME_LENGTH), nullable=False)
      staff_kana_name = Column(String(consts.STAFF_KANA_NAME_LENGTH), nullable=False)
      created_at = Column(String(consts.DATE_TIME_LENGTH), nullable=False)
      updated_at = Column(String(consts.DATE_TIME_LENGTH), nullable=False)
      is_hidden = Column(Boolean, nullable=False)
      is_exclude = Column(Boolean, nullable=False)

      def __init__(self,
                   spell_and_header,
                   mean_and_content,
                   concept_and_notion,
                   intent,
                   sentiment,
                   strength,
                   part_of_speech,
                   first_character,
                   characters_count,
                   staff_name,
                   staff_kana_name,
                   created_at,
                   updated_at,
                   is_hidden,
                   is_exclude
                  ):
          self.spell_and_header = spell_and_header
          self.mean_and_content = mean_and_content
          self.concept_and_notion = concept_and_notion
          self.intent = intent
          self.sentiment = sentiment
          self.strength = strength
          self.part_of_speech = part_of_speech
          self.first_character = first_character
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
      mean_and_content = Column(Text, nullable=False)
      concept_and_notion = Column(Text, nullable=False)
      category_tags = Column(Text, nullable=False)
      staff_name = Column(String(consts.STAFF_NAME_LENGTH), nullable=False)
      staff_kana_name = Column(String(consts.STAFF_KANA_NAME_LENGTH), nullable=False)
      created_at = Column(String(consts.DATE_TIME_LENGTH), nullable=False)
      updated_at = Column(String(consts.DATE_TIME_LENGTH), nullable=False)
      is_hidden = Column(Boolean, nullable=False)
      is_exclude = Column(Boolean, nullable=False)

      def __init__(self,
                   spell_and_header,
                   mean_and_content,
                   concept_and_notion,
                   category_tags,
                   staff_name,
                   staff_kana_name,
                   created_at,
                   updated_at,
                   is_hidden,
                   is_exclude
                   ):
          self.spell_and_header = spell_and_header
          self.mean_and_content = mean_and_content
          self.concept_and_notion = concept_and_notion
          self.category_tags = category_tags
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
      mean_and_content = Column(Text, nullable=False)
      concept_and_notion = Column(Text, nullable=False)
      parent_category_tags = Column(Text, nullable=False)
      sibling_category_tags = Column(Text, nullable=False)
      child_category_tags = Column(Text, nullable=False)
      staff_name = Column(String(consts.STAFF_NAME_LENGTH), nullable=False)
      staff_kana_name = Column(String(consts.STAFF_KANA_NAME_LENGTH), nullable=False)
      created_at = Column(String(consts.DATE_TIME_LENGTH), nullable=False)
      updated_at = Column(String(consts.DATE_TIME_LENGTH), nullable=False)
      is_hidden = Column(Boolean, nullable=False)
      is_exclude = Column(Boolean, nullable=False)

      def __init__(self,
                   spell_and_header,
                   mean_and_content,
                   concept_and_notion,
                   parent_category_tags,
                   sibling_category_tags,
                   child_category_tags,
                   staff_name,
                   staff_kana_name,
                   created_at,
                   updated_at,
                   is_hidden,
                   is_exclude                   
                   ):
          self.spell_and_header = spell_and_header
          self.mean_and_content = mean_and_content
          self.concept_and_notion = concept_and_notion
          self.parent_category_tags = parent_category_tags
          self.sibling_category_tags = sibling_category_tags
          self.child_category_tags = child_category_tags
          self.staff_name = staff_name
          self.staff_kana_name = staff_kana_name
          self.created_at = created_at
          self.updated_at = updated_at
          self.is_hidden = is_hidden
          self.is_exclude = is_exclude


# 知識テーブル(=SQLAlchemyクラス)を宣言・定義する.
class Knowledge(Base):
      __tablename__ = "knowledges"
      id = Column(Integer, primary_key=True, autoincrement=True)
      spell_and_header = Column(Text, nullable=False)
      mean_and_content = Column(Text, nullable=False)
      concept_and_notion = Column(Text, nullable=False)
      category_tags = Column(Text, nullable=False)
      archived_image_file_path = Column(String(consts.ARCHIVED_IMAGE_FILE_NAME_LENGTH), nullable=False)
      archived_sound_file_path = Column(String(consts.ARCHIVED_SOUND_FILE_NAME_LENGTH), nullable=False)
      archived_video_file_path = Column(String(consts.ARCHIVED_VIDEO_FILE_NAME_LENGTH), nullable=False)
      staff_name = Column(String(consts.STAFF_NAME_LENGTH), nullable=False)
      staff_kana_name = Column(String(consts.STAFF_KANA_NAME_LENGTH), nullable=False)
      created_at = Column(String(consts.DATE_TIME_LENGTH), nullable=False)
      updated_at = Column(String(consts.DATE_TIME_LENGTH), nullable=False)
      is_hidden = Column(Boolean, nullable=False)
      is_exclude = Column(Boolean, nullable=False)

      def __init__(self,
                   spell_and_header,
                   mean_and_content,
                   concept_and_notion,
                   category_tags,
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
          self.mean_and_content = mean_and_content
          self.concept_and_notion = concept_and_notion
          self.category_tags = category_tags
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
      mean_and_content = Column(Text, nullable=False)
      concept_and_notion = Column(Text, nullable=False)
      category_tags = Column(Text, nullable=False)
      inference_condition = Column(Text, nullable=False)
      inference_result = Column(Text, nullable=False)
      staff_name = Column(String(consts.STAFF_NAME_LENGTH), nullable=False)
      staff_kana_name = Column(String(consts.STAFF_KANA_NAME_LENGTH), nullable=False)
      created_at = Column(String(consts.DATE_TIME_LENGTH), nullable=False)
      updated_at = Column(String(consts.DATE_TIME_LENGTH), nullable=False)
      is_hidden = Column(Boolean, nullable=False)
      is_exclude = Column(Boolean, nullable=False)

      def __init__(self,
                   spell_and_header,
                   mean_and_content,
                   concept_and_notion,
                   category_tags,
                   inference_condition,
                   inference_result,
                   staff_name,
                   staff_kana_name,
                   created_at,
                   updated_at,
                   is_hidden,
                   is_exclude                   
                   ):
          self.spell_and_header = spell_and_header
          self.mean_and_content = mean_and_content
          self.concept_and_notion = concept_and_notion
          self.category_tags = category_tags
          self.inference_condition = inference_condition
          self.inference_result = inference_result
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
      mean_and_content = Column(Text, nullable=False)
      concept_and_notion = Column(Text, nullable=False)
      staff_psychology = Column(Text, nullable=False)
      scene_and_background = Column(Text, nullable=False)
      message_example_from_staff = Column(Text, nullable=False)
      message_example_from_application = Column(Text, nullable=False)
      staff_name = Column(String(consts.STAFF_NAME_LENGTH), nullable=False)
      staff_kana_name = Column(String(consts.STAFF_KANA_NAME_LENGTH), nullable=False)
      created_at = Column(String(consts.DATE_TIME_LENGTH), nullable=False)
      updated_at = Column(String(consts.DATE_TIME_LENGTH), nullable=False)
      is_hidden = Column(Boolean, nullable=False)
      is_exclude = Column(Boolean, nullable=False)

      def __init__(self,
                   spell_and_header,
                   mean_and_content,
                   concept_and_notion,
                   staff_psychology,
                   scene_and_background,
                   message_example_from_staff,
                   message_example_from_application,
                   staff_name,
                   staff_kana_name,
                   created_at,
                   updated_at,
                   is_hidden,
                   is_exclude                   
                   ):
          self.spell_and_header = spell_and_header
          self.mean_and_content = mean_and_content
          self.concept_and_notion = concept_and_notion
          self.staff_psychology = staff_psychology
          self.scene_and_background = scene_and_background
          self.msessage_example_from_staff = message_example_from_staff
          self.msessage_example_from_application = message_example_from_application
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
      mean_and_content = Column(Text, nullable=False)
      generated_file_path = Column(String(consts.GENERATED_FILE_NAME_LENGTH), nullable=False)
      staff_name = Column(String(consts.STAFF_NAME_LENGTH), nullable=False)
      staff_kana_name = Column(String(consts.STAFF_KANA_NAME_LENGTH), nullable=False)
      created_at = Column(String(consts.DATE_TIME_LENGTH), nullable=False)
      updated_at = Column(String(consts.DATE_TIME_LENGTH), nullable=False)
      is_hidden = Column(Boolean, nullable=False)
      is_exclude = Column(Boolean, nullable=False)

      def __init__(self,
                   spell_and_header,
                   mean_and_content,
                   generated_file_path,
                   staff_name,
                   staff_kana_name,
                   created_at,
                   updated_at,
                   is_hidden,
                   is_exclude
                   ):
          self.spell_and_header = spell_and_header
          self.mean_and_content = mean_and_content
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
      staff_message = Column(Text, nullable=False)
      application_message = Column(Text, nullable=False)
      staff_name = Column(String(consts.STAFF_NAME_LENGTH), nullable=False)
      staff_kana_name = Column(String(consts.STAFF_KANA_NAME_LENGTH), nullable=False)
      created_at = Column(String(consts.DATE_TIME_LENGTH), nullable=False)
      updated_at = Column(String(consts.DATE_TIME_LENGTH), nullable=False)
      is_hidden = Column(Boolean, nullable=False)
      is_exclude = Column(Boolean, nullable=False)

      def __init__(self,
                   staff_message,
                   application_message,
                   staff_name,
                   staff_kana_name,
                   created_at,
                   updated_at,
                   is_hidden,
                   is_exclude                   
                   ):
          self.staff_message = staff_message
          self.application_message = application_message
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
      enter_or_exit_at = Column(String(consts.DATE_TIME_LENGTH), nullable=False)
      enter_or_exit_at_second = Column(String(consts.DATE_TIME_SECOND_LENGTH), nullable=False)
      created_at = Column(String(consts.DATE_TIME_LENGTH), nullable=False)
      updated_at = Column(String(consts.DATE_TIME_LENGTH), nullable=False)
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
      pass_word = Column(String(consts.PASSWORD_LENGTH), nullable=False)
      sex = Column(String(consts.SEX_LENGTH), nullable=False)
      blood_type = Column(String(consts.BLOOD_TYPE_LENGTH), nullable=False)
      birth_date = Column(String(consts.BIRTH_DATE_LENGTH), nullable=False)
      created_at = Column(String(consts.DATE_TIME_LENGTH), nullable=False)
      updated_at = Column(String(consts.DATE_TIME_LENGTH), nullable=False)
      is_hidden = Column(Boolean, nullable=False)
      is_exclude = Column(Boolean, nullable=False)

      def __init__(self,
                   name,
                   kana_name,
                   pass_word,
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
          self.pass_word = pass_word
          self.sex = sex
          self.blood_type = blood_type
          self.birth_date = birth_date
          self.created_at = created_at
          self.updated_at = updated_at
          self.is_hidden = is_hidden
          self.is_exclude = is_exclude


# データベースを作成・初期化する(=各種テーブルを一括で作成する).
Base.metadata.create_all(bind=engine, checkfirst=True)