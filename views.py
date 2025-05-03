# coding: utf-8




# 既成のモジュールをインポートする.
import os
import sys
import csv
import datetime
import configparser
import xml.dom.minidom as MD
import xml.etree.ElementTree as ET
from flask import (
     Blueprint,     
     request,
     session,
     url_for,
     flash,
     send_file,
     redirect,
     render_template
)
from flask_paginate import Pagination, get_page_parameter
from werkzeug.utils import secure_filename
from werkzeug.exceptions import (
     NotFound,
     InternalServerError
)

# 各種フォームをインポートする.
from forms import (
     StaffEnterForm,
     StaffExitForm,
     AdminEnterForm,
     AdminExitForm,
     SendForm,
     LearnWordForm,
     LearnThemeForm,
     LearnCategoryForm,
     LearnKnowledgeForm,
     LearnRuleForm,
     LearnReactionForm,
     GenerateForm,
     RegisterEnterOrExitForm,
     RegisterStaffForm,
     SearchWordForm,
     SearchThemeForm,
     SearchCategoryForm,
     SearchKnowledgeForm,
     SearchRuleForm,
     SearchReactionForm,
     SearchGenerateForm,
     SearchHistoryForm,
     SearchEnterOrExitForm,
     SearchStaffForm,
     ModifyWordForm,
     ModifyThemeForm,
     ModifyCategoryForm,
     ModifyKnowledgeForm,
     ModifyRuleForm,
     ModifyReactionForm,
     ModifyEnterOrExitForm,
     ModifyStaffForm,
     DetailWordForm,
     DetailThemeForm,
     DetailCategoryForm,
     DetailKnowledgeForm,
     DetailRuleForm,
     DetailReactionForm,
     DetailGenerateForm,
     DetailHistoryForm,
     DetailEnterOrExitForm,
     DetailStaffForm,
     ImportWordForm,
     ImportThemeForm,
     ImportCategoryForm,
     ImportKnowledgeForm,
     ImportRuleForm,
     ImportReactionForm,
     ImportGenerateForm,
     ImportEnterOrExitForm,
     ExportWordForm,
     ExportThemeForm,
     ExportCategoryForm,
     ExportKnowledgeForm,
     ExportRuleForm,
     ExportReactionForm,
     ExportGenerateForm,
     ExportHistoryForm,
     ExportEnterOrExitForm,
     RetrieveGenerateForm,
     SettingForm,
     ResetDatabaseForm
)

# 各種モデルをインポートする.
from models import (
     db_session,
     Word,
     Theme,
     Category,
     Knowledge,
     Rule,
     Reaction,
     Generate,
     History,
     EnterOrExit,
     Staff
)

# 独自のモジュールをインポートする.
import appcore

# 設定のためのモジュールをインポートする.
import constants as consts

# ビュー関数群にBlueprintにおける名前を付与する.
view = Blueprint("view", __name__)

# Flaskの初回起動時処理を実行するためのフラッグ変数を宣言する.
is_frst_rqst = True

# Sunie独自のエンジンを生成する.
se = appcore.SunieEngine()

# アプリのログ(=動作記録)の保存を開始する.
se.etc.logging__start(consts.LOGGING_PATH)




# 「home」のためのビュー関数(=URLエンドポイント)を宣言・定義する. 
@view.route("/", methods=["GET"])
@view.route("/index", methods=["GET"])
@view.route("/home", methods=["GET"])
def home():
    # 関数内で使用する変数・オブジェクトを宣言・定義する.
    global is_frst_rqst
    session.clear()
    session["enter-name"] = ""
    session["enter-kana-name"] = ""
    session["staff-enter-fault"] = "0"
    session["admin-enter-fault"] = "0"
    session["is-staff-enter"] = False
    session["is-admin-enter"] = False
    session["referrer-page"] = "view.home"
    hm_back_cnddt = ["PATTERN-A", "PATTERN-B"]
    dcid_pttrn = se.etc.random_select(hm_back_cnddt)
    crrnt_hr = se.etc.retrieve_current_hour_as_integer("JST")
    match crrnt_hr:
          case crrnt_hr if 0 <= crrnt_hr < 6:
               tm_ped = "midnight"
          case crrnt_hr if 6 <= crrnt_hr < 12:
               tm_ped = "morning"
          case crrnt_hr if 12 <= crrnt_hr < 18:
               tm_ped = "afternoon"
          case _:
               tm_ped = "evening/night"

    # 該当のURLエンドポイントに入ったことをロギングする.
    rslt = se.etc.logging__info("view at /home")

    # ロギングに失敗したら, 例外を発生させる.
    if rslt == "NG":
        raise InternalServerError

    # アプリケーションの前回終了時から,
    # 未退室のままになっている職員を特定し,
    # 現在時刻をもって自動の打刻を済ませる.
    if is_frst_rqst:
        stffs = db_session.query(Staff).filter(Staff.is_exclude==False)
        db_session.close()

        for stff in stffs:
            ent_or_ext = (
                db_session.query(EnterOrExit).filter(EnterOrExit.staff_name == stff.name).order_by(EnterOrExit.id.desc()).first()
            )
            db_session.close()
            if ent_or_ext is not None:
               if (ent_or_ext.reason == "clock-in" or
                   ent_or_ext.reason == "return-to-out" or
                   ent_or_ext.reason == "after-break"):
                   crrnt_dttm = se.etc.retrieve_current_datetime_as_string("JST", True)
                   db_session.add(EnterOrExit(staff_name=stff.name,
                                              staff_kana_name=stff.kana_name,
                                              reason="application-termination",
                                              enter_or_exit_at=crrnt_dttm,
                                              created_at=crrnt_dttm,
                                              updated_at=crrnt_dttm,
                                              is_hidden=False,
                                              is_exclude=False
                                             ))
                   db_session.commit()
                   db_session.close()
        is_frst_rqst = False

    # ホーム画面のページに表示する背景画像をランダムに選択・設定して, テンプレートを返す.
    if dcid_pttrn == "PATTERN-A":
        return render_template("home.html", time_period=tm_ped, background_image=consts.HOME_IMAGE_A_PATH)
    else:
        return render_template("home.html", time_period=tm_ped, background_image=consts.HOME_IMAGE_B_PATH)


# 「usage」のためのビュー関数(=URLエンドポイント)を宣言・定義する. 
@view.route("/usage", methods=["GET"])
def usage():
    # 関数内で使用する変数・オブジェクトを宣言・定義する.
    session.clear()
    session["enter-name"] = ""
    session["enter-kana-name"] = ""
    session["staff-enter-fault"] = "0"
    session["admin-enter-fault"] = "0"
    session["is-staff-enter"] = False
    session["is-admin-enter"] = False
    session["referrer-page"] = "view.usage"

    # 該当のURLエンドポイントに入ったことをロギングする.
    rslt = se.etc.logging__info("view at /usage")

    # ロギングに失敗したら, 例外を発生させる.
    if rslt == "NG":
        raise InternalServerError

    # ヘルプ画面のページなので, そのままテンプレートを返す.
    return render_template("usage.html", background_image=consts.USAGE_IMAGE_PATH)


# 「guide」のためのビュー関数(=URLエンドポイント)を宣言・定義する. 
@view.route("/guide", methods=["GET"])
def guide():
    # 関数内で使用する変数・オブジェクトを宣言・定義する.
    session.clear()
    session["enter-name"] = ""
    session["enter-kana-name"] = ""
    session["staff-enter-fault"] = "0"
    session["admin-enter-fault"] = "0"
    session["is-staff-enter"] = False
    session["is-admin-enter"] = False
    session["referrer-page"] = "view.guide"

    # 該当のURLエンドポイントに入ったことをロギングする.
    rslt = se.etc.logging__info("view at /guide")

    # ロギングに失敗したら, 例外を発生させる.
    if rslt == "NG":
        raise InternalServerError

    # ガイド画面のページなので, そのままテンプレートを返す.
    return render_template("guide.html", background_image=consts.GUIDE_IMAGE_PATH)


# 「staff_enter」のためのビュー関数(=URLエンドポイント)を宣言・定義する.
@view.route("/staff_enter", methods=["GET", "POST"])
def staff_enter():
    # 関数内で使用する変数・オブジェクトを宣言・定義する.
    stff_nm = ""
    psswrd = ""
    rsn = ""
    crrnt_dttm = ""
    stff_entr_form = StaffEnterForm()

    # 該当のURLエンドポイントに入ったことをロギングする.
    rslt = se.etc.logging__info("view at /staff_enter")

    # ロギングに失敗したら, 例外を発生させる.
    if rslt == "NG":
        raise InternalServerError

    # セッション未作成ならば, ホーム画面のページヘリダイレクトする.
    if not session:
        return redirect(url_for("view.home"))

    # セッション失効or未初期化ならば, ホーム画面のページヘリダイレクトする.
    if "staff-enter-fault" not in session:
        return redirect(url_for("view.home"))

    if request.method == "GET":
        # セッションに現在ページの情報を設定して,
        # Flaskフォームと共にテンプレートを返す.
        session["referrer-page"] = "view.staff_enter" 
        return render_template("staff_enter.html", form=stff_entr_form)

    if request.method == "POST":
        # 直前に, GETメソッドで該当ページを取得しているかを調べる.
        # 取得していなければ, 強制的に現在ページへリダイレクトする.
        if session["referrer-page"] != "view.staff_enter":
            return redirect(url_for("view.home"))

        # フォームの取消ボタンが押下されたら, 空のフォームと共に該当ページを返す.
        if stff_entr_form.cancel.data:
            stff_entr_form.name.data = ""
            stff_entr_form.password.data = ""
            stff_entr_form.reason.data = ""
            return render_template("staff_enter.html", form=stff_entr_form)

        # 既定の回数分, 連続して入室失敗したら, エラーメッセージを設定する.
        # その際に, 入力内容を空にしたFlaskフォームと共にテンプレートを返す.
        if int(session["staff-enter-fault"]) >= consts.APP_LOCKOUT_NUMBER:
            flash("連続して入力を間違えたので, 入室できなくなりました.")
            return render_template("staff_enter.html", form=stff_entr_form)

        # フォームに入力されているすべての内容を検証する.
        # もしも誤りがあれば, フォームと共にページを返す. 
        if stff_entr_form.name.data == "":
            flash("職員名が入力されていません.")
            return render_template("staff_enter.html", form=stff_entr_form, happen_error=True)
        if stff_entr_form.password.data == "":
            flash("パスワードが入力されていません.")
            return render_template("staff_enter.html", form=stff_entr_form, happen_error=True)
        if stff_entr_form.reason.data == "":
            flash("入室理由が選択されていません.")
            return render_template("staff_enter.html", form=stff_entr_form, happen_error=True)

        # フォームに入力・記憶されている内容を取得する.
        stff_nm = stff_entr_form.name.data
        psswrd = stff_entr_form.password.data
        rsn = stff_entr_form.reason.data

        # 入力された名前が使用・登録されているかを確認する.
        stff = db_session.query(Staff).filter(Staff.name == stff_nm).first()
        db_session.close()

        # 指定職員が存在しない場合には, エラーメッセージを設定して,
        # 入力内容を空にしたFlaskフォームと共にテンプレートを返す.
        if stff is None:
            session["staff-enter-fault"] = str(int(session["staff-enter-fault"]) + 1)
            flash("その職員は登録されていません.")
            return render_template("staff_enter.html", form=stff_entr_form, happen_error=True)

        # パスワード誤りがある場合には, エラーメッセージを設定して,
        # 入力内容を空にしたFlaskフォームと共にテンプレートを返す.
        if psswrd != stff.pass_word:
            session["staff-enter-fault"] = str(int(session["staff-enter-fault"]) + 1)
            flash("そのパスワードは間違っています.")
            return render_template("staff_enter.html", form=stff_entr_form, happen_error=True)

        # 前回の入室後に, 退室処理が正常に実行されていない場合には, 自動退室記録をDBに登録する.
        ent_or_ext = (
            db_session.query(EnterOrExit).filter(EnterOrExit.staff_name == stff.name).order_by(EnterOrExit.id.desc()).first()
        )
        db_session.close()

        if ent_or_ext is not None:
            if (ent_or_ext.reason == "clock-in" or
                ent_or_ext.reason == "return-to-out" or
                ent_or_ext.reason == "after-break"):
                crrnt_dttm = se.etc.retrieve_current_datetime_as_string("JST", True)
                db_session.add(EnterOrExit(staff_name=stff.name,
                                           staff_kana_name=stff.kana_name,
                                           reason="forget-or-revocation",
                                           enter_or_exit_at=crrnt_dttm,
                                           enter_or_exit_at_second="00",
                                           created_at=crrnt_dttm,
                                           updated_at=crrnt_dttm,
                                           is_hidden=False,
                                           is_exclude=False
                                          ))
                db_session.commit()
                db_session.close()

        # 現在のタイムスタンプを取得して, 入室記録をDBに登録する.
        crrnt_dttm = se.etc.retrieve_current_datetime_as_string("JST", True)
        db_session.add(EnterOrExit(staff_name=stff.name,
                                   staff_kana_name=stff.kana_name,
                                   reason=rsn,
                                   enter_or_exit_at=crrnt_dttm,
                                   enter_or_exit_at_second="00",
                                   created_at=crrnt_dttm,
                                   updated_at=crrnt_dttm,
                                   is_hidden=False,
                                   is_exclude=False
                                  ))
        db_session.commit()
        db_session.close()

        # 入室した職員の情報をセッションに設定して,
        # 以降, セッションを参照して職員を特定する.
        session["enter-name"] = stff.name
        session["enter-kana-name"] = stff.kana_name
 
        # 職員としての入室状態をセッションに設定する.
        session["is-staff-enter"] = True

        # 職員用のダッシュボード画面のページへリダイレクトする.
        return redirect(url_for("view.staff_dashboard"))


# 「staff_exit」のためのビュー関数(=URLエンドポイント)を宣言・定義する.
@view.route("/staff_exit", methods=["GET", "POST"])
def staff_exit():
    # 関数内で使用する変数・オブジェクトを宣言・定義する.
    stff_exit_form = StaffExitForm()

    # 該当のURLエンドポイントに入ったことをロギングする.
    rslt = se.etc.logging__info("view at /staff_exit")

    # ロギングに失敗したら, 例外を発生させる.
    if rslt == "NG":
        raise InternalServerError

    # セッション未作成ならば, ホーム画面のページヘリダイレクトする.
    if not session:
        return redirect(url_for("view.home"))

    # セッション失効or未初期化ならば, ホーム画面のページヘリダイレクトする.
    if "is-staff-enter" not in session:
        return redirect(url_for("view.home"))

    # 職員未入室の状態ならば, 直前画面のページヘリダイレクトする.
    if session["is-staff-enter"] == False:
       return redirect(url_for(session["referrer-page"]))

    if request.method == "GET":
        # セッションに現在ページの情報を設定して,
        # Flaskフォームと共にテンプレートを返す.
        session["referrer-page"] = "view.staff_exit"
        return render_template("staff_exit.html", form=stff_exit_form)

    if request.method == "POST":
        # 直前に, GETメソッドで該当ページを取得しているかを調べる.
        # 取得していなければ, 強制的に現在ページへリダイレクトする.
        if session["referrer-page"] != "view.staff_exit":
            return redirect(url_for("view.staff_dashboard"))

        # フォームの取消ボタンが押下されたら, 空のフォームと共にテンプレートを返す.
        if stff_exit_form.cancel.data:
            stff_exit_form.reason.data = ""
            return render_template("staff_exit.html", form=stff_exit_form)

        # flaskフォームに入力・記憶されている内容をバリデーションする.
        # 基準を満たさない場合, フォームと共にテンプレートを返す.
        if stff_exit_form.reason.data == "":
            flash("退室理由が入力されていません.")
            return render_template("staff_exit.html", form=stff_exit_form, happen_error=True)

        # 現在のタイムスタンプを取得して, 退室記録をDBに登録する.
        crrnt_dttm = se.etc.retrieve_current_datetime_as_string("JST", True)
        db_session.add(EnterOrExit(staff_name=session["enter-name"],
                                   staff_kana_name=session["enter-kana-name"],
                                   reason=stff_exit_form.reason.data,
                                   enter_or_exit_at=crrnt_dttm,
                                   enter_or_exit_at_second="00",
                                   created_at=crrnt_dttm,
                                   updated_at=crrnt_dttm,
                                   is_hidden=False,
                                   is_exclude=False
                                   ))
        db_session.commit()
        db_session.close()

        # セッションの内容を初期化して, ホーム画面のページへリダイレクトする.
        session["enter-name"] == ""
        session["enter-kana-name"] == ""
        session["is-staff-enter"] = False
        return redirect(url_for("view.home"))


# 「admin_enter」のためのビュー関数(=URLエンドポイント)を宣言・定義する.
@view.route("/admin_enter", methods=["GET", "POST"])
def admin_enter():
    # 関数内で使用する変数・オブジェクトを宣言・定義する.
    admn_entr_form = AdminEnterForm()

    # 該当のURLエンドポイントに入ったことをロギングする.
    rslt = se.etc.logging__info("view at /admin_enter")

    # ロギングに失敗したら, 例外を発生させる.
    if rslt == "NG":
        raise InternalServerError

    # セッション未作成ならば, ホーム画面のページヘリダイレクトする.
    if not session:
        return redirect(url_for("view.home"))

    # セッション失効or未初期化ならば, ホーム画面のページヘリダイレクトする.
    if "admin-enter-fault" not in session:
        return redirect(url_for("view.home"))

    if request.method == "GET":
        # セッションに現在ページの情報を設定して,
        # Flaskフォームと共にテンプレートを返す.
        session["referrer-page"] = "view.admin_enter"
        return render_template("admin_enter.html", form=admn_entr_form)

    if request.method == "POST":
        # 直前に, GETメソッドで該当ページを取得しているかを調べる.
        # 取得していなければ, 強制的に現在ページへリダイレクトする.
        if session["referrer-page"] != "view.admin_enter":
            return redirect(url_for("view.home"))

        # フォームの取消ボタンが押下されたら, 空のフォームと共にテンプレートを返す.
        if admn_entr_form.cancel.data:
            admn_entr_form.password.data = ""
            return render_template("admin_enter.html", form=admn_entr_form)

        # 入室失敗が既定数に達したら, エラーメッセージを設定して,
        # 入力内容を空にしたFlaskフォームと共にテンプレートを返す.
        if int(session["admin-enter-fault"]) >= consts.APP_LOCKOUT_NUMBER:
            flash("連続して入力を間違えたので, 入室できなくなりました.")
            return render_template("admin_enter.html", form=admn_entr_form, happen_error=True)

        # flaskフォームに入力・記憶されている内容をバリデーションする.
        # 基準を満たさない場合, フォームと共にテンプレートを返す.
        if admn_entr_form.password.data == "":
            flash("パスワードが入力されていません.")
            return render_template("admin_enter.html", form=admn_entr_form, happen_error=True)

        # フォームに入力・記憶されている内容を取得する.
        psswrd = admn_entr_form.password.data

        # パスワードに誤りがある場合, エラーメッセージを設定して, フォームと共にテンプレートを返す.
        if psswrd != consts.ADMIN_PASSWORD:
            session["admin-enter-fault"] = str(int(session["admin-enter-fault"]) + 1)
            flash("そのパスワードは間違っています.")
            return render_template("admin_enter.html", form=admn_entr_form, happen_error=True)

        # セッションに管理者入室の状態を設定する.
        session["is-admin-enter"] = True

        # 管理者用のダッシュボード画面のページへリダイレクトする.
        return redirect(url_for("view.admin_dashboard"))


# 「admin_exit」のためのビュー関数(=URLエンドポイント)を宣言・定義する.
@view.route("/admin_exit", methods=["GET", "POST"])
def admin_exit():
    # 関数内で使用する変数・オブジェクトを宣言・定義する.
    admn_exit_form = AdminExitForm()

    # 該当のURLエンドポイントに入ったことをロギングする.
    rslt = se.etc.logging__info("view at /admin_exit")

    # ロギングに失敗したら, 例外を発生させる.
    if rslt == "NG":
        raise InternalServerError

    # セッション未作成ならば, ホーム画面のページヘリダイレクトする.
    if not session:
        return redirect(url_for("view.home"))

    # セッション失効or未初期化ならば, ホーム画面のページヘリダイレクトする.
    if "is-admin-enter" not in session:
        return redirect(url_for("view.home"))

    # 管理者未入室の状態ならば, ホーム画面のページヘリダイレクトする.
    if session["is-admin-enter"] == False:
       return redirect(url_for("view.home"))

    if request.method == "GET":
        # セッションに現在ページの情報を設定して,
        # Flaskフォームと共にテンプレートを返す.
        session["referrer-page"] = "view.admin_exit"
        return render_template("admin_exit.html", form=admn_exit_form)

    if request.method == "POST":
        # 直前に, GETメソッドで該当ページを取得しているかを調べる.
        # 取得していなければ, 強制的に現在ページへリダイレクトする.
        if session["referrer-page"] != "view.admin_exit":
            return redirect(url_for("view.admin_dashboard"))

        # フォームの取消ボタンが押下されたら,
        # ダッシュボード画面のページへリダイレクトする.
        if admn_exit_form.cancel.data:
            return redirect(url_for("view.admin_dashboard"))

    # セッションの内容を初期化して, ホーム画面のページへリダイレクトする.
    session["is-admin-enter"] = False
    return redirect(url_for("view.home"))


# 「staff_dashboard」のためのビュー関数(=URLエンドポイント)を宣言・定義する.
@view.route("/staff_dashboard", methods=["GET"])
def staff_dashboard():
    # 該当のURLエンドポイントに入ったことをロギングする.
    rslt = se.etc.logging__info("view at /staff_dashboard")

    # ロギングに失敗したら, 例外を発生させる.
    if rslt == "NG":
        raise InternalServerError

    # セッション未作成ならば, ホーム画面のページヘリダイレクトする.
    if not session:
        return redirect(url_for("view.home"))

    # セッション失効or未初期化ならば, ホーム画面のページヘリダイレクトする.
    if "is-staff-enter" not in session:
        return redirect(url_for("view.home"))

    # 職員未入室の状態ならば, ホーム画面のページヘリダイレクトする.
    if session["is-staff-enter"] == False:
       return redirect(url_for("view.home"))

    if request.method == "GET":
        # セッションに現在ページの情報を設定して, テンプレートを返す.
        session["referrer-page"] = "view.staff_dashboard"
        return render_template("staff_dashboard.html",
            background_image=consts.STAFF_BOARD_IMAGE_PATH)


# 「admin_dashboard」のためのビュー関数(=URLエンドポイント)を宣言・定義する.
@view.route("/admin_dashboard", methods=["GET"])
def admin_dashboard():
    # 該当のURLエンドポイントに入ったことをロギングする.
    rslt = se.etc.logging__info("view at /admin_dashboard")

    # ロギングに失敗したら, 例外を発生させる.
    if rslt == "NG":
        raise InternalServerError

    # セッション未作成ならば, ホーム画面のページヘリダイレクトする.
    if not session:
        return redirect(url_for("view.home"))

    # セッション失効or未初期化ならば, ホーム画面のページヘリダイレクトする.
    if "is-admin-enter" not in session:
        return redirect(url_for("view.home"))

    # 管理者未入室の状態ならば, ホーム画面のページヘリダイレクトする.
    if session["is-admin-enter"] == False:
        return redirect(url_for("view.home"))

    if request.method == "GET":
        # セッションに現在ページの情報を設定して, テンプレートを返す.
        session["referrer-page"] = "view.admin_dashboard"
        return render_template("admin_dashboard.html",
            background_image=consts.ADMIN_BOARD_IMAGE_PATH)


# 「send」のためのビュー関数(=URLエンドポイント)を宣言・定義する.
@view.route("/send", methods=["GET", "POST"])
def send():
    # 関数内で使用する変数・オブジェクトを宣言・定義する.
    txt_from_stff = ""
    txt_from_app = ""
    send_form = SendForm()

    # 該当のURLエンドポイントに入ったことをロギングする.
    rslt = se.etc.logging__info("view at /send")

    # ロギングに失敗したら, 例外を発生させる.
    if rslt == "NG":
        raise InternalServerError

    # セッション未作成ならば, ホーム画面のページヘリダイレクトする.
    if not session:
        return redirect(url_for("view.home"))

    # セッション失効or未初期化ならば, ホーム画面のページヘリダイレクトする.
    if "is-staff-enter" not in session:
        return redirect(url_for("view.home"))

    # 職員未入室の状態ならば, ホーム画面のページヘリダイレクトする.
    if session["is-staff-enter"] == False:
       return redirect(url_for("view.home"))

    if request.method == "GET":
        # セッションに現在ページの情報を設定して,
        # Flaskフォームと共にテンプレートを返す.
        session["referrer-page"] = "view.send"
        return render_template("send.html", form=send_form)

    if request.method == "POST":
        # 直前に, GETメソッドで該当ページを取得しているかを調べる.
        # 取得していなければ, 強制的に現在ページへリダイレクトする.
        if session["referrer-page"] != "view.send":
            return redirect(url_for("view.staff_dashboard"))

        # フォームの取消ボタンが押下されたら, 空のフォームと共にテンプレートを返す.
        if send_form.cancel.data:
            send_form.message.data = ""
            return render_template("send.html", form=send_form)

        # flaskフォームに入力・記憶されている内容をバリデーションする.
        # 基準を満たさない場合, フォームと共にテンプレートを返す.
        if send_form.message.data == "":
            flash("メッセージ本文が入力されていません.")
            return render_template("send.html", form=send_form, happen_error=True)

        # sunieエンジンに職員への返信メッセージを生成させる.
        txt_from_stff = send_form.message.data
        txt_from_app = se.generate_message(txt_from_stff)

        # 履歴情報をレコードとして, DBに保存・登録する.
        crrnt_dttm = se.etc.retrieve_current_datetime_as_string("JST", True)
        db_session.add(History(staff_name=session["enter-name"],
                               staff_kana_name=session["enter-kana-name"],
                               staff_message=txt_from_stff,
                               application_message=txt_from_app,
                               created_at=crrnt_dttm,
                               updated_at=crrnt_dttm,
                               is_hidden=False,
                               is_exclude=False
                              ))
        db_session.commit()
        db_session.close()

        # 職員からの呼掛け内容とエンジン処理結果(=返信内容)を,
        # セッションに設定して, 返信ページへリダイレクトする.
        session["text-from-staff"] = txt_from_stff
        session["text-from-application"] = txt_from_app
        return redirect(url_for("view.reply"))


# 「reply」のためのビュー関数(=URLエンドポイント)を宣言・定義する.
@view.route("/reply", methods=["GET"])
def reply():
    # 該当のURLエンドポイントに入ったことをロギングする.
    rslt = se.etc.logging__info("view at /reply")

    # ロギングに失敗したら, 例外を発生させる.
    if rslt == "NG":
        raise InternalServerError

    # セッション未作成ならば, ホーム画面のページヘリダイレクトする.
    if not session:
        return redirect(url_for("view.home"))

    # セッション失効or未初期化ならば, ホーム画面のページヘリダイレクトする.
    if "is-staff-enter" not in session:
        return redirect(url_for("view.home"))

    # 職員未入室の状態ならば, ホーム画面のページヘリダイレクトする.
    if session["is-staff-enter"] == False:
       return redirect(url_for("view.home"))

    # 直前に, GETメソッドでメッセ送信用ページを取得しているかを調べる.
    # 取得していなければ, 強制的に職員ダッシュボードへリダイレクトする.
    if ((session["referrer-page"] != "view.send") and
        (session["referrer-page"] != "view.reply")):
        return redirect(url_for("view.staff_dashboard"))

    if request.method == "GET":
        # セッションに現在ページの情報を設定して,
        # Flaskフォームと共にテンプレートを返す.
        session["referrer-page"] = "view.reply"
        return render_template("reply.html",
                               text_from_staff=session["text-from-staff"],
                               text_from_application=session["text-from-application"])


# 「learn_word」のためのビュー関数(=URLエンドポイント)を宣言・定義する.
@view.route("/learn_word", methods=["GET", "POST"])
def learn_word():
    # 関数内で使用する変数・オブジェクトを宣言・定義する.
    lrn_wrd_form = LearnWordForm()

    # 該当のURLエンドポイントに入ったことをロギングする.
    rslt = se.etc.logging__info("view at /learn_word")

    # ロギングに失敗したら, 例外を発生させる.
    if rslt == "NG":
        raise InternalServerError

    # セッション未作成ならば, ホーム画面のページヘリダイレクトする.
    if not session:
        return redirect(url_for("view.home"))

    # セッション失効or未初期化ならば, ホーム画面のページヘリダイレクトする.
    if "is-staff-enter" not in session:
        return redirect(url_for("view.home"))

    # 職員未入室の状態ならば, ホーム画面のページヘリダイレクトする.
    if session["is-staff-enter"] == False:
       return redirect(url_for("view.home"))

    if request.method == "GET":
        # セッションに現在ページの情報を設定して,
        # Flaskフォームと共にテンプレートを返す.
        session["referrer-page"] = "view.learn_word"
        return render_template("learn_word.html", form=lrn_wrd_form)

    if request.method == "POST":
        # 直前に, GETメソッドで該当ページを取得しているかを調べる.
        # 取得していなければ, 強制的に現在ページへリダイレクトする.
        if session["referrer-page"] != "view.learn_word":
            return redirect(url_for("view.staff_dashboard"))

        # フォームの取消ボタンが押下されたら, 空のフォームと共にテンプレートを返す.
        if lrn_wrd_form.cancel.data:
            lrn_wrd_form.spell_and_header.data = ""
            lrn_wrd_form.mean_and_content.data = ""
            lrn_wrd_form.intent.data = ""
            lrn_wrd_form.sentiment.data = ""
            lrn_wrd_form.strength.data = ""
            lrn_wrd_form.part_of_speech.data = ""
            lrn_wrd_form.is_hidden=False
            lrn_wrd_form.is_exclude=False
            return render_template("learn_word.html", form=lrn_wrd_form)

        # flaskフォームに入力・記憶されている内容をバリデーションする.
        # 基準を満たさない場合, フォームと共にテンプレートを返す.
        if lrn_wrd_form.spell_and_header.data == "":
            flash("綴り&見出しが入力されていません.")
            return render_template("learn_word.html", form=lrn_wrd_form, happen_error=True)
        if lrn_wrd_form.mean_and_content.data == "":
            flash("意味&内容が入力されていません.")
            return render_template("learn_word.html", form=lrn_wrd_form, happen_error=True)
        if lrn_wrd_form.intent.data == "":
            flash("意図が選択されていません.")
            return render_template("learn_word.html", form=lrn_wrd_form, happen_error=True)
        if lrn_wrd_form.sentiment.data == "":
            flash("感情が選択されていません.")
            return render_template("learn_word.html", form=lrn_wrd_form, happen_error=True)
        if lrn_wrd_form.strength.data == "":
            flash("強度が入力されていません.")
            return render_template("learn_word.html", form=lrn_wrd_form, happen_error=True)
        if lrn_wrd_form.part_of_speech.data == "":
            flash("品詞分類が選択されていません.")
            return render_template("learn_word.html", form=lrn_wrd_form, happen_error=True)
        if lrn_wrd_form.is_hidden.data == "":
            flash("秘匿の是非が選択されていません.")
            return render_template("learn_word.html", form=lrn_wrd_form, happen_error=True)
        if lrn_wrd_form.is_exclude.data == "":
            flash("非処理の是非が選択されていません.")
            return render_template("learn_word.html", form=lrn_wrd_form, happen_error=True)

        #@ ここで, 語句情報を学習するための各種の高度な計算を行う.
        cncpt_n_ntn = se.learn_word(lrn_wrd_form.spell_and_header.data,
                                    lrn_wrd_form.mean_and_content.data)

        # 語句情報をレコードとして, DBに保存・登録する.
        crrnt_dttm = se.etc.retrieve_current_datetime_as_string("JST", True)
        db_session.add(Word(spell_and_header=lrn_wrd_form.spell_and_header.data,
                            mean_and_content=lrn_wrd_form.mean_and_content.data,
                            concept_and_notion=cncpt_n_ntn,
                            intent = lrn_wrd_form.intent.data,
                            sentiment = lrn_wrd_form.sentiment.data,
                            strength = lrn_wrd_form.strength.data,
                            part_of_speech = lrn_wrd_form.part_of_speech.data,
                            first_character = lrn_wrd_form.spell_and_header.data[0],
                            characters_count = len(lrn_wrd_form.spell_and_header.data),
                            staff_name=session["enter-name"],
                            staff_kana_name=session["enter-kana-name"],
                            created_at=crrnt_dttm,
                            updated_at=crrnt_dttm,
                            is_hidden=(True if lrn_wrd_form.is_hidden == "yes" else False),
                            is_exclude=(True if lrn_wrd_form.is_exclude == "yes" else False)
                           ))
        db_session.commit()
        db_session.close()

        # 完了メッセージを設定して, テンプレートを返す.
        flash("語句を学習しました.")
        return render_template("learn_word.html", form=lrn_wrd_form)


# 「learn_theme」のためのビュー関数(=URLエンドポイント)を宣言・定義する.
@view.route("/learn_theme", methods=["GET", "POST"])
def learn_theme():
    # 関数内で使用する変数・オブジェクトを宣言・定義する.
    lrn_thm_form = LearnThemeForm()

    # 該当のURLエンドポイントに入ったことをロギングする.
    rslt = se.etc.logging__info("view at /learn_theme")

    # ロギングに失敗したら, 例外を発生させる.
    if rslt == "NG":
        raise InternalServerError

    # セッション未作成ならば, ホーム画面のページヘリダイレクトする.
    if not session:
        return redirect(url_for("view.home"))

    # セッション失効or未初期化ならば, ホーム画面のページヘリダイレクトする.
    if "is-staff-enter" not in session:
        return redirect(url_for("view.home"))

    # 職員未入室の状態ならば, ホーム画面のページヘリダイレクトする.
    if session["is-staff-enter"] == False:
       return redirect(url_for("view.home"))

    if request.method == "GET":
        # セッションに現在ページの情報を設定して,
        # Flaskフォームと共にテンプレートを返す.
        session["referrer-page"] = "view.learn_theme"
        return render_template("learn_theme.html", form=lrn_thm_form)

    if request.method == "POST":
        # 直前に, GETメソッドで該当ページを取得しているかを調べる.
        # 取得していなければ, 強制的に現在ページへリダイレクトする.
        if session["referrer-page"] != "view.learn_theme":
            return redirect(url_for("view.staff_dashboard"))

        # フォームの取消ボタンが押下されたら, 空のフォームと共にテンプレートを返す.
        if lrn_thm_form.cancel.data:
            lrn_thm_form.spell_and_header.data = ""
            lrn_thm_form.mean_and_content.data = ""
            lrn_thm_form.category_tags.data = ""
            lrn_thm_form.is_hidden = False
            lrn_thm_form.is_exclude = False
            return render_template("learn_theme.html", form=lrn_thm_form)

        # flaskフォームに入力・記憶されている内容をバリデーションする.
        # 基準を満たさない場合は, 元のフォームと共にテンプレートを返す.
        if lrn_thm_form.spell_and_header.data == "":
            flash("綴り&見出しが入力されていません.")
            return render_template("learn_theme.html", form=lrn_thm_form, happen_error=True)
        if lrn_thm_form.mean_and_content.data == "":
            flash("意味&内容が入力されていません.")
            return render_template("learn_theme.html", form=lrn_thm_form, happen_error=True)
        if lrn_thm_form.category_tags.data == "":
            flash("分類タグが入力されていません.")
            return render_template("learn_theme.html", form=lrn_thm_form, happen_error=True)
        if lrn_thm_form.is_hidden.data == "":
            flash("秘匿の是非が選択されていません.")
            return render_template("learn_word.html", form=lrn_thm_form, happen_error=True)
        if lrn_thm_form.is_exclude.data == "":
            flash("非処理の是非が選択されていません.")
            return render_template("learn_word.html", form=lrn_thm_form, happen_error=True)

        #@ ここで, 主題情報を学習するための各種の高度な計算を行う.
        cncpt_n_ntn = se.learn_theme(lrn_thm_form.spell_and_header.data,
                                     lrn_thm_form.mean_and_content.data)

        # 主題情報をレコードとして, DBに保存・登録する.
        crrnt_dttm = se.etc.retrieve_current_datetime_as_string("JST", True)
        db_session.add(Theme(spell_and_header=lrn_thm_form.spell_and_header.data,
                             mean_and_content=lrn_thm_form.mean_and_content.data,
                             concept_and_notion=cncpt_n_ntn,
                             category_tags=lrn_thm_form.category_tags.data,
                             staff_name=session["enter-name"],
                             staff_kana_name=session["enter-kana-name"],
                             created_at=crrnt_dttm,
                             updated_at=crrnt_dttm,
                             is_hidden=(True if lrn_thm_form.is_hidden == "yes" else False),
                             is_exclude=(True if lrn_thm_form.is_exclude == "yes" else False),
                            ))
        db_session.commit()
        db_session.close()

        # 完了メッセージを設定して, テンプレートを返す.
        flash("主題を学習しました.")
        return render_template("learn_theme.html", form=lrn_thm_form)


# 「learn_category」のためのビュー関数(=URLエンドポイント)を宣言・定義する.
@view.route("/learn_category", methods=["GET", "POST"])
def learn_category():
    # 関数内で使用する変数・オブジェクトを宣言・定義する.
    lrn_ctgr_form = LearnCategoryForm()

    # 該当のURLエンドポイントに入ったことをロギングする.
    rslt = se.etc.logging__info("view at /learn_category")

    # ロギングに失敗したら, 例外を発生させる.
    if rslt == "NG":
        raise InternalServerError

    # セッション未作成ならば, ホーム画面のページヘリダイレクトする.
    if not session:
        return redirect(url_for("view.home"))

    # セッション失効or未初期化ならば, ホーム画面のページヘリダイレクトする.
    if "is-staff-enter" not in session:
        return redirect(url_for("view.home"))

    # 職員未入室の状態ならば, ホーム画面のページヘリダイレクトする.
    if session["is-staff-enter"] == False:
       return redirect(url_for("view.home"))

    if request.method == "GET":
        # セッションに現在ページの情報を設定して,
        # Flaskフォームと共にテンプレートを返す.
        session["referrer-page"] = "view.learn_category"
        return render_template("learn_category.html", form=lrn_ctgr_form)

    if request.method == "POST":
        # 直前に, GETメソッドで該当ページを取得しているかを調べる.
        # 取得していなければ, 強制的に現在ページへリダイレクトする.
        if session["referrer-page"] != "view.learn_category":
            return redirect(url_for("view.staff_dashboard"))

        # フォームの取消ボタンが押下されたら, 空のフォームと共にテンプレートを返す.
        if lrn_ctgr_form.cancel.data:
            lrn_ctgr_form.spell_and_header.data = ""
            lrn_ctgr_form.mean_and_content.data = ""
            lrn_ctgr_form.parent_category_tags.data = ""
            lrn_ctgr_form.sibling_category_tags.data = ""
            lrn_ctgr_form.child_category_tags.data = ""
            lrn_ctgr_form.is_hidden = False
            lrn_ctgr_form.is_exclude = False
            return render_template("learn_category.html", form=lrn_ctgr_form)

        # flaskフォームに入力・記憶されている内容をバリデーションする.
        # 基準を満たさない場合は, 元のフォームと共にテンプレートを返す.
        if lrn_ctgr_form.spell_and_header.data == "":
            flash("綴り&見出しが入力されていません.")
            return render_template("learn_category.html", form=lrn_ctgr_form, happen_error=True)
        if lrn_ctgr_form.mean_and_content.data == "":
            flash("意味&内容が入力されていません.")
            return render_template("learn_category.html", form=lrn_ctgr_form, happen_error=True)
        if lrn_ctgr_form.parent_category_tags.data == "":
            flash("親分類タグが入力されていません.")
            return render_template("learn_category.html", form=lrn_ctgr_form, happen_error=True)
        if lrn_ctgr_form.sibling_category_tags.data == "":
            flash("兄弟分類タグが入力されていません.")
            return render_template("learn_category.html", form=lrn_ctgr_form, happen_error=True)
        if lrn_ctgr_form.child_category_tags.data == "":
            flash("子分類タグが入力されていません.")
            return render_template("learn_category.html", form=lrn_ctgr_form, happen_error=True)
        if lrn_ctgr_form.is_hidden.data == "":
            flash("秘匿の是非が選択されていません.")
            return render_template("learn_word.html", form=lrn_ctgr_form, happen_error=True)
        if lrn_ctgr_form.is_exclude.data == "":
            flash("非処理の是非が選択されていません.")
            return render_template("learn_word.html", form=lrn_ctgr_form, happen_error=True)

        #@ ここで, 分類情報を学習するための各種の高度な計算を行う.
        cncpt_n_ntn = se.learn_category(lrn_ctgr_form.spell_and_header.data,
                                        lrn_ctgr_form.mean_and_content.data)

        # 分類情報をレコードとして, DBに保存・登録する.
        crrnt_dttm = se.etc.retrieve_current_datetime_as_string("JST", True)
        db_session.add(Category(spell_and_header=lrn_ctgr_form.spell_and_header.data,
                                mean_and_content=lrn_ctgr_form.mean_and_content.data,
                                concept_and_notion=cncpt_n_ntn,
                                parent_category_tags=lrn_ctgr_form.parent_category_tags.data,
                                sibling_category_tags=lrn_ctgr_form.sibling_category_tags.data,
                                child_category_tags=lrn_ctgr_form.child_category_tags.data,
                                staff_name=session["enter-name"],
                                staff_kana_name=session["enter-kana-name"],
                                created_at=crrnt_dttm,
                                updated_at=crrnt_dttm,
                                is_hidden=(True if lrn_ctgr_form.is_hidden == "yes" else False),
                                is_exclude=(True if lrn_ctgr_form.is_exclude == "yes" else False),
                               ))
        db_session.commit()
        db_session.close()

        # 完了メッセージを設定して, テンプレートを返す.
        flash("分類を学習しました.")
        return render_template("learn_category.html", form=lrn_ctgr_form)


# 「learn_knowledge」のためのビュー関数(=URLエンドポイント)を宣言・定義する.
@view.route("/learn_knowledge", methods=["GET", "POST"])
def learn_knowledge():
    # 関数内で使用する変数・オブジェクトを宣言・定義する.
    fl_lbl = ""
    img_sv_pth = ""
    snd_sv_pth = ""
    vdo_sv_pth = ""
    lrn_knwldg_form = LearnKnowledgeForm()

    # 該当のURLエンドポイントに入ったことをロギングする.
    rslt = se.etc.logging__info("view at /learn_knowledge")

    # ロギングに失敗したら, 例外を発生させる.
    if rslt == "NG":
        raise InternalServerError

    # セッション未作成ならば, ホーム画面のページヘリダイレクトする.
    if not session:
        return redirect(url_for("view.home"))

    # セッション失効or未初期化ならば, ホーム画面のページヘリダイレクトする.
    if "is-staff-enter" not in session:
        return redirect(url_for("view.home"))

    # 職員未入室の状態ならば, ホーム画面のページヘリダイレクトする.
    if session["is-staff-enter"] == False:
       return redirect(url_for("view.home"))

    if request.method == "GET":
        # セッションに現在ページの情報を設定して,
        # Flaskフォームと共にテンプレートを返す.
        session["referrer-page"] = "view.learn_knowledge"
        return render_template("learn_knowledge.html", form=lrn_knwldg_form)

    if request.method == "POST":
        # 直前に, GETメソッドで該当ページを取得しているかを調べる.
        # 取得していなければ, 強制的に現在ページへリダイレクトする.
        if session["referrer-page"] != "view.learn_knowledge":
            return redirect(url_for("view.staff_dashboard"))

        # フォームの取消ボタンが押下されたら, 空のフォームと共にテンプレートを返す.
        if lrn_knwldg_form.cancel.data:
            lrn_knwldg_form.spell_and_header.data = ""
            lrn_knwldg_form.mean_and_content.data = ""
            lrn_knwldg_form.category_tags.data = ""
            lrn_knwldg_form.attached_image_file.data = ""
            lrn_knwldg_form.attached_sound_file.data = ""
            lrn_knwldg_form.attached_video_file.data = ""
            lrn_knwldg_form.is_hidden = False
            lrn_knwldg_form.is_exclude = False
            return render_template("learn_knowledge.html", form=lrn_knwldg_form)

        # flaskフォームに入力・記憶されている内容をバリデーションする.
        # 基準を満たさない場合は, 元のフォームと共にテンプレートを返す.
        if lrn_knwldg_form.spell_and_header.data == "":
            flash("綴り&見出しが入力されていません.")
            return render_template("learn_knowledge.html", form=lrn_knwldg_form, happen_error=True)
        if lrn_knwldg_form.mean_and_content.data == "":
            flash("意味&内容が入力されていません.")
            return render_template("learn_knowledge.html", form=lrn_knwldg_form, happen_error=True)
        if lrn_knwldg_form.category_tags.data == "":
            flash("分類タグが入力されていません.")
            return render_template("learn_knowledge.html", form=lrn_knwldg_form, happen_error=True)
        if lrn_knwldg_form.is_hidden.data == "":
            flash("秘匿の是非が選択されていません.")
            return render_template("learn_knowledge.html", form=lrn_knwldg_form, happen_error=True)
        if lrn_knwldg_form.is_exclude.data == "":
            flash("非処理の是非が選択されていません.")
            return render_template("learn_knowledge.html", form=lrn_knwldg_form, happen_error=True)

        #@ ここで, 知識情報を学習するための各種の高度な計算を行う.
        cncpt_n_ntn = se.learn_category(lrn_knwldg_form.spell_and_header.data,
                                        lrn_knwldg_form.mean_and_content.data)

        # 知識情報をレコードとして, DBに保存・登録する.
        fl_lbl = se.etc.retrieve_current_datetime_as_file_label()
        crrnt_dttm = se.etc.retrieve_current_datetime_as_string("JST", True)
        img_sv_pth = se.etc.archive_file(lrn_knwldg_form.attached_image_file.data, consts.ARCHIVE_IMAGE_PATH, fl_lbl)
        snd_sv_pth = se.etc.archive_file(lrn_knwldg_form.attached_sound_file.data, consts.ARCHIVE_SOUND_PATH, fl_lbl)
        vdo_sv_pth = se.etc.archive_file(lrn_knwldg_form.attached_video_file.data, consts.ARCHIVE_VIDEO_PATH, fl_lbl)
        db_session.add(Knowledge(spell_and_header=lrn_knwldg_form.spell_and_header.data,
                                 mean_and_content=lrn_knwldg_form.mean_and_content.data,
                                 concept_and_notion=cncpt_n_ntn,
                                 category_tags=lrn_knwldg_form.category_tags.data,
                                 archived_image_file_path=img_sv_pth,
                                 archived_sound_file_path=snd_sv_pth,
                                 archived_video_file_path=vdo_sv_pth,
                                 staff_name=session["enter-name"],
                                 staff_kana_name=session["enter-kana-name"],
                                 created_at=crrnt_dttm,
                                 updated_at=crrnt_dttm,
                                 is_hidden=(True if lrn_knwldg_form.is_hidden == "yes" else False),
                                 is_exclude=(True if lrn_knwldg_form.is_exclude == "yes" else False),
                                ))
        db_session.commit()
        db_session.close()

        # 完了メッセージを設定して, テンプレートを返す.
        flash("知識を学習しました.")
        return render_template("learn_knowledge.html", form=lrn_knwldg_form)


# 「learn_rule」のためのビュー関数(=URLエンドポイント)を宣言・定義する.
@view.route("/learn_rule", methods=["GET", "POST"])
def learn_rule():
    # 関数内で使用する変数・オブジェクトを宣言・定義する.
    lrn_rl_form = LearnRuleForm()

    # 該当のURLエンドポイントに入ったことをロギングする.
    rslt = se.etc.logging__info("view at /learn_rule")

    # ロギングに失敗したら, 例外を発生させる.
    if rslt == "NG":
        raise InternalServerError

    # セッション未作成ならば, ホーム画面のページヘリダイレクトする.
    if not session:
        return redirect(url_for("view.home"))

    # セッション失効or未初期化ならば, ホーム画面のページヘリダイレクトする.
    if "is-staff-enter" not in session:
        return redirect(url_for("view.home"))

    # 職員未入室の状態ならば, ホーム画面のページヘリダイレクトする.
    if session["is-staff-enter"] == False:
       return redirect(url_for("view.home"))

    if request.method == "GET":
        # セッションに現在ページの情報を設定して,
        # Flaskフォームと共にテンプレートを返す.
        session["referrer-page"] = "view.learn_rule"
        return render_template("learn_rule.html", form=lrn_rl_form)

    if request.method == "POST":
        # 直前に, GETメソッドで該当ページを取得しているかを調べる.
        # 取得していなければ, 強制的に現在ページへリダイレクトする.
        if session["referrer-page"] != "view.learn_rule":
            return redirect(url_for("view.staff_dashboard"))

        # フォームの取消ボタンが押下されたら, 空のフォームと共にテンプレートを返す.
        if lrn_rl_form.cancel.data:
            lrn_rl_form.spell_and_header.data = ""
            lrn_rl_form.mean_and_content.data = ""
            lrn_rl_form.category_tags.data = ""
            lrn_rl_form.inference_condition.data = ""
            lrn_rl_form.inference_result.data = ""
            lrn_rl_form.is_hidden.data = False
            lrn_rl_form.is_exclude.data = False
            return render_template("learn_rule.html", form=lrn_rl_form)

        # flaskフォームに入力・記憶されている内容をバリデーションする.
        # 基準を満たさない場合は, 元のフォームと共にテンプレートを返す.
        if lrn_rl_form.spell_and_header.data == "":
            flash("綴り&見出しが入力されていません.")
            return render_template("learn_rule.html", form=lrn_rl_form, happen_error=True)
        if lrn_rl_form.mean_and_content.data == "":
            flash("意味&内容が入力されていません.")
            return render_template("learn_rule.html", form=lrn_rl_form, happen_error=True)
        if lrn_rl_form.category_tags.data == "":
            flash("分類タグが入力されていません.")
            return render_template("learn_rule.html", form=lrn_rl_form, happen_error=True)
        if lrn_rl_form.inference_condition.data == "":
            flash("推論条件が入力されていません.")
            return render_template("learn_rule.html", form=lrn_rl_form, happen_error=True)
        if lrn_rl_form.inference_result.data == "":
            flash("推論結果が入力されていません.")
            return render_template("learn_rule.html", form=lrn_rl_form, happen_error=True)
        if lrn_rl_form.is_hidden.data == "":
            flash("秘匿の是非が選択されていません.")
            return render_template("learn_rule.html", form=lrn_rl_form, happen_error=True)
        if lrn_rl_form.is_exclude.data == "":
            flash("非処理の是非が選択されていません.")
            return render_template("learn_rule.html", form=lrn_rl_form, happen_error=True)

        #@ ここで, 規則情報を学習するための各種の高度な計算を行う.
        cncpt_n_ntn = se.learn_rule(lrn_rl_form.spell_and_header.data,
                                    lrn_rl_form.mean_and_content.data)

        # 規則情報をレコードとして, DBに保存・登録する.
        crrnt_dttm = se.etc.retrieve_current_datetime_as_string("JST", True)
        db_session.add(Rule(spell_and_header=lrn_rl_form.spell_and_header.data,
                            mean_and_content=lrn_rl_form.mean_and_content.data,
                            concept_and_notion=cncpt_n_ntn,
                            category_tags=lrn_rl_form.category_tags.data,
                            inference_condition=lrn_rl_form.inference_condition.data,
                            inference_result=lrn_rl_form.inference_result.data,
                            staff_name=session["enter-name"],
                            staff_kana_name=session["enter-kana-name"],
                            created_at=crrnt_dttm,
                            updated_at=crrnt_dttm,
                            is_hidden=(True if lrn_rl_form.is_hidden == "yes" else False),
                            is_exclude=(True if lrn_rl_form.is_exclude == "yes" else False),
                           ))
        db_session.commit()
        db_session.close()

        # 完了メッセージを設定して, テンプレートを返す.
        flash("規則を学習しました.")
        return render_template("learn_rule.html", form=lrn_rl_form)


# 「learn_reaction」のためのビュー関数(=URLエンドポイント)を宣言・定義する.
@view.route("/learn_reaction", methods=["GET", "POST"])
def learn_reaction():
    # 関数内で使用する変数・オブジェクトを宣言・定義する.
    lrn_rctn_form = LearnReactionForm()

    # 該当のURLエンドポイントに入ったことをロギングする.
    rslt = se.etc.logging__info("view at /learn_reaction")

    # ロギングに失敗したら, 例外を発生させる.
    if rslt == "NG":
        raise InternalServerError

    # セッション未作成ならば, ホーム画面のページヘリダイレクトする.
    if not session:
        return redirect(url_for("view.home"))

    # セッション失効or未初期化ならば, ホーム画面のページヘリダイレクトする.
    if "is-staff-enter" not in session:
        return redirect(url_for("view.home"))

    # 職員未入室の状態ならば, ホーム画面のページヘリダイレクトする.
    if session["is-staff-enter"] == False:
       return redirect(url_for("view.home"))

    if request.method == "GET":
        # セッションに現在ページの情報を設定して,
        # Flaskフォームと共にテンプレートを返す.
        session["referrer-page"] = "view.learn_reaction"
        return render_template("learn_reaction.html", form=lrn_rctn_form)

    if request.method == "POST":
        # 直前に, GETメソッドで該当ページを取得しているかを調べる.
        # 取得していなければ, 強制的に現在ページへリダイレクトする.
        if session["referrer-page"] != "view.learn_reaction":
            return redirect(url_for("view.staff_dashboard"))

        # フォームの取消ボタンが押下されたら, 空のフォームと共にテンプレートを返す.
        if lrn_rctn_form.cancel.data:
            lrn_rctn_form.spell_and_header.data = ""
            lrn_rctn_form.mean_and_content.data = ""
            lrn_rctn_form.staff_psychology.data = ""
            lrn_rctn_form.scene_and_background.data = ""
            lrn_rctn_form.message_example_from_staff.data = ""
            lrn_rctn_form.message_example_from_staff.data = ""
            lrn_rctn_form.message_example_from_application.data = ""
            lrn_rctn_form.is_hidden.data = False
            lrn_rctn_form.is_exclude.data = False
            return render_template("learn_reaction.html", form=lrn_rctn_form)

        # flaskフォームに入力・記憶されている内容をバリデーションする.
        # 基準を満たさない場合は, 元のフォームと共にテンプレートを返す.
        if lrn_rctn_form.spell_and_header.data == "":
            flash("綴り&見出しが入力されていません.")
            return render_template("learn_reaction.html", form=lrn_rctn_form, happen_error=True)
        if lrn_rctn_form.mean_and_content.data == "":
            flash("意味&内容が入力されていません.")
            return render_template("learn_reaction.html", form=lrn_rctn_form, happen_error=True)
        if lrn_rctn_form.staff_psychology.data == "":
            flash("職員心理が入力されていません.")
            return render_template("learn_reaction.html", form=lrn_rctn_form, happen_error=True)
        if lrn_rctn_form.scene_and_background.data == "":
            flash("情景&背景が入力されていません.")
            return render_template("learn_reaction.html", form=lrn_rctn_form, happen_error=True)
        if lrn_rctn_form.message_example_from_staff.data == "":
            flash("職員メッセージ例が入力されていません.")
            return render_template("learn_reaction.html", form=lrn_rctn_form, happen_error=True)
        if lrn_rctn_form.message_example_from_application.data == "":
            flash("アプリメッセージ例が入力されていません.")
            return render_template("learn_reaction.html", form=lrn_rctn_form, happen_error=True)
        if lrn_rctn_form.is_hidden.data == "":
            flash("秘匿の是非が選択されていません.")
            return render_template("learn_reaction.html", form=lrn_rctn_form, happen_error=True)
        if lrn_rctn_form.is_exclude.data == "":
            flash("非処理の是非が選択されていません.")
            return render_template("learn_reaction.html", form=lrn_rctn_form, happen_error=True)

        #@ ここで, 反応情報を学習するための各種の高度な計算を行う.
        cncpt_n_ntn = se.learn_reaction(lrn_rctn_form.spell_and_header.data,
                                        lrn_rctn_form.mean_and_content.data)

        # 反応情報をレコードとして, DBに保存・登録する.
        crrnt_dttm = se.etc.retrieve_current_datetime_as_string("JST", True)
        db_session.add(Reaction(spell_and_header=lrn_rctn_form.spell_and_header.data,
                                mean_and_content=lrn_rctn_form.mean_and_content.data,
                                concept_and_notion=cncpt_n_ntn,
                                staff_psychology=lrn_rctn_form.staff_psychology.data,
                                scene_and_background=lrn_rctn_form.scene_and_background.data,
                                message_example_from_staff=lrn_rctn_form.message_example_from_staff.data,
                                message_example_from_application=lrn_rctn_form.message_example_from_application.data,
                                staff_name=session["enter-name"],
                                staff_kana_name=session["enter-kana-name"],
                                created_at=crrnt_dttm,
                                updated_at=crrnt_dttm,
                                is_hidden=(True if lrn_rctn_form.is_hidden == "yes" else False),
                                is_exclude=(True if lrn_rctn_form.is_exclude == "yes" else False),
                               ))
        db_session.commit()
        db_session.close()

        # 完了メッセージを設定して, テンプレートを返す.
        flash("反応を学習しました.")
        return render_template("learn_reaction.html", form=lrn_rctn_form)


# 「generate」のためのビュー関数(=URLエンドポイント)を宣言・定義する.
@view.route("/generate", methods=["GET", "POST"])
def generate():
    # 関数内で使用する変数・オブジェクトを宣言・定義する.
    gen_form = GenerateForm()

    # 該当のURLエンドポイントに入ったことをロギングする.
    rslt = se.etc.logging__info("view at /generate")

    # ロギングに失敗したら, 例外を発生させる.
    if rslt == "NG":
        raise InternalServerError

    # セッション未作成ならば, ホーム画面のページヘリダイレクトする.
    if not session:
        return redirect(url_for("view.home"))

    # セッション失効or未初期化ならば, ホーム画面のページヘリダイレクトする.
    if "is-staff-enter" not in session:
        return redirect(url_for("view.home"))

    # 職員未入室の状態ならば, ホーム画面のページヘリダイレクトする.
    if session["is-staff-enter"] == False:
       return redirect(url_for("view.home"))

    if request.method == "GET":
        # セッションに現在ページの情報を設定して,
        # Flaskフォームと共にテンプレートを返す.
        session["referrer-page"] = "view.generate"
        return render_template("generate.html", form=gen_form)

    if request.method == "POST":
        # 直前に, GETメソッドで該当ページを取得しているかを調べる.
        # 取得していなければ, 強制的に現在ページへリダイレクトする.
        if session["referrer-page"] != "view.generate":
            return redirect(url_for("view.generate"))

        # フォームの取消ボタンが押下されたら, 空のフォームと共にテンプレートを返す.
        if gen_form.cancel.data:
            gen_form.spell_and_header.data = ""
            gen_form.mean_and_content.data = ""
            gen_form.attached_image_file.data = ""
            gen_form.attached_sound_file.data = ""
            gen_form.attached_video_file.data = ""
            gen_form.is_hidden.data = False
            gen_form.is_exclude.data = False
            return render_template("generate.html", form=gen_form)

        # flaskフォームに入力・記憶されている内容をバリデーションする.
        # 基準を満たさない場合は, 元のフォームと共にテンプレートを返す.
        if gen_form.spell_and_header.data == "":
            flash("綴り&見出しが入力されていません.")
            return render_template("generate.html", form=gen_form, happen_error=True)
        if gen_form.mean_and_content.data == "":
            flash("意味&内容が入力されていません.")
            return render_template("generate.html", form=gen_form, happen_error=True)
        if gen_form.is_hidden.data == "":
            flash("秘匿の是非が選択されていません.")
            return render_template("generate.html", form=gen_form, happen_error=True)
        if gen_form.is_exclude.data == "":
            flash("非処理の是非が選択されていません.")
            return render_template("generate.html", form=gen_form, happen_error=True)

        #@ ここで, 各種のデータファイルを生成するための各種の高度な計算を行う.
        gnrtd_fl_pth = se.generate_data_file(gen_form.spell_and_header.data,
                                             gen_form.mean_and_content.data)
        gnrtd_fl_pth = consts.DUMMY_FILE_PATH # 暫定的にダミーファイルのパスを使用する.

        # 生成情報をレコードとして, DBに保存・登録する.
        crrnt_dttm = se.etc.retrieve_current_datetime_as_string("JST", True)
        db_session.add(Generate(spell_and_header=gen_form.spell_and_header.data,
                                mean_and_content=gen_form.mean_and_content.data,
                                generated_file_path=gnrtd_fl_pth,
                                staff_name=session["enter-name"],
                                staff_kana_name=session["enter-kana-name"],
                                created_at=crrnt_dttm,
                                updated_at=crrnt_dttm,
                                is_hidden=(True if gen_form.is_hidden == "yes" else False),
                                is_exclude=(True if gen_form.is_exclude == "yes" else False),
                                ))
        db_session.commit()
        db_session.close()

        # 完了メッセージを設定して, テンプレートを返す.
        flash("データファイルを生成しました.")
        return render_template("generate.html", form=gen_form)


# 「show_words」のためのビュー関数(=URLエンドポイント)を宣言・定義する.
@view.route("/show_words", methods=["GET", "POST"])
@view.route("/show_words/<int:id>", methods=["GET", "POST"])
def show_words(id=None):
    # 関数内で使用する変数・オブジェクトを宣言・定義する.
    wrds_tmp = []
    wrds_fnl = []

    # 該当のURLエンドポイントに入ったことをロギングする.
    rslt = se.etc.logging__info("view at /show_words")

    # ロギングに失敗したら, 例外を発生させる.
    if rslt == "NG":
        raise InternalServerError

    # 指定URLにパスパラメータが含まれていて,
    # かつ不正な値であれば, 例外を発生させる.
    if id is not None:
        if id == 0:
            raise NotFound

    # パスパラメータとして指定されたレコードIDが, 
    # 総レコード数を超えていたら,例外を発生させる.
    if id is not None:
        if id > db_session.query(Word).count():
            raise NotFound

    # セッション未作成ならば, ホーム画面のページヘリダイレクトする.
    if not session:
        return redirect(url_for("view.home"))

    # セッション失効or未初期化ならば, ホーム画面のページヘリダイレクトする.
    if "is-admin-enter" not in session:
        return redirect(url_for("view.home"))

    # 管理者未入室の状態ならば, ホーム画面のページヘリダイレクトする.
    if session["is-admin-enter"] == False:
        return redirect(url_for("view.home"))

    if request.method == "GET":
        # セッションに現在ページの情報を設定して,
        # Flaskフォームと共にテンプレートを返す.
        session["referrer-page"] = "view.show_words"

        # 該当ページ内のボタンから遷移するためのセッション項目を削除する.
        session.pop("hidden-modify-item-id", None)
        session.pop("hidden-detail-item-id", None)

        # DBから語句レコードを取得してテンプレートと共に返す.
        # RIDを指定された場合は, 一つだけレコードを取得する.
        if id is not None:
            wrd_tmp = db_session.query(Word).filter(Word.id==id).first()
            db_session.close()

            if wrd_tmp is not None:
                if len(wrd_tmp.id) > 6:
                    id_tmp = wrd_tmp.id[0:6] + "..."
                else:
                    id_tmp = wrd_tmp.id
                if len(wrd_tmp.spell_and_header) > 6:
                    spll_n_hdr_tmp = wrd_tmp.spell_and_header[0:6] + "..."
                else:
                    spll_n_hdr_tmp = wrd_tmp.spell_and_header
                if len(wrd_tmp.mean_and_content) > 6:
                    mn_n_cntnt_tmp = wrd_tmp.mean_and_content[0:6] + "..."
                else:
                    mn_n_cntnt_tmp = wrd_tmp.mean_and_content
                if len(wrd_tmp.staff_name) > 6:
                    stff_nm_tmp = wrd_tmp.staff_name[0:6] + "..."
                else:
                    stff_nm_tmp = wrd_tmp.staff_name
                wrds_fnl.append([id_tmp,
                                 spll_n_hdr_tmp,
                                 mn_n_cntnt_tmp,
                                 stff_nm_tmp
                                ])
                per_pg = consts.WORD_PER_PAGE
                pg = request.args.get(get_page_parameter(), type=int, default=1)
                pg_dat = wrds_fnl[(pg - 1) * per_pg : pg * per_pg]
                pgntn = Pagination(page=pg,
                                   total=len(wrds_fnl),
                                   per_page=per_pg,
                                   css_framework=consts.PAGINATION_CSS
                                  )
                return render_template("show_words.html", page_data=pg_dat, pagination=pgntn) 

            per_pg = consts.WORD_PER_PAGE
            pg = request.args.get(get_page_parameter(), type=int, default=1)
            pg_dat = wrds_fnl[(pg - 1) * per_pg : pg * per_pg]
            pgntn = Pagination(page=pg,
                               total=len(wrds_fnl),
                               per_page=per_pg,
                               css_framework=consts.PAGINATION_CSS
                              )
            return render_template("show_words.html", page_data=pg_dat, pagination=pgntn) 
        else:
            wrds_tmp = db_session.query(Word).order_by(Word.id).all()
            db_session.close()
            for wrd_tmp in wrds_tmp:
                 if len(wrd_tmp.id) > 6:
                     id_tmp = wrd_tmp.id[0:6] + "..."
                 else:
                     id_tmp = wrd_tmp.id
                 if len(wrd_tmp.spell_and_header) > 6:
                     spll_n_hdr_tmp = wrd_tmp.spell_and_header[0:6] + "..."
                 else:
                     spll_n_hdr_tmp = wrd_tmp.spell_and_header
                 if len(wrd_tmp.mean_and_content) > 6:
                     mn_n_cntnt_tmp = wrd_tmp.mean_and_content[0:6] + "..."
                 else:
                     mn_n_cntnt_tmp = wrd_tmp.mean_and_content
                 if len(wrd_tmp.staff_name) > 6:
                     stff_nm_tmp = wrd_tmp.staff_name[0:6] + "..."
                 else:
                     stff_nm_tmp = wrd_tmp.staff_name
                 wrds_fnl.append([id_tmp,
                                  spll_n_hdr_tmp,
                                  mn_n_cntnt_tmp,
                                  stff_nm_tmp
                                 ])
            per_pg = consts.WORD_PER_PAGE
            pg = request.args.get(get_page_parameter(), type=int, default=1)
            pg_dat = wrds_fnl[(pg - 1) * per_pg : pg * per_pg]
            pgntn = Pagination(page=pg,
                               total=len(wrds_fnl),
                               per_page=per_pg,
                               css_framework=consts.PAGINATION_CSS
                              )
            return render_template("show_words.html", page_data=pg_dat, pagination=pgntn)

    if request.method == "POST":
        # 直前に, GETメソッドで該当ページを取得しているかを調べる.
        # 取得していなければ, 強制的に現在ページへリダイレクトする.
        if session["referrer-page"] != "view.show_words":
            return redirect(url_for("view.show_words"))

        # フォームボタン群の中から, 押下されたボタンに応じたページへリダイレクトする.
        if request.form["hidden-modify-item-id"] != "":
            session["hidden-modify-item-id"] = request.form["hidden-modify-item-id"]
            return redirect(url_for("view.modify_word"))
        if request.form["hidden-detail-item-id"] != "":
            session["hidden-detail-item-id"] = request.form["hidden-detail-item-id"]
            return redirect(url_for("view.detail_word"))


# 「show_themes」のためのビュー関数(=URLエンドポイント)を宣言・定義する.
@view.route("/show_themes", methods=["GET", "POST"])
@view.route("/show_themes/<int:id>", methods=["GET", "POST"])
def show_themes(id=None):
    # 関数内で使用する変数・オブジェクトを宣言・定義する.
    thms_tmp = []
    thms_fnl = []

    # 該当のURLエンドポイントに入ったことをロギングする.
    rslt = se.etc.logging__info("view at /show_themes")

    # ロギングに失敗したら, 例外を発生させる.
    if rslt == "NG":
        raise InternalServerError

    # 指定URLにパスパラメータが含まれていて,
    # かつ不正な値であれば, 例外を発生させる.
    if id is not None:
        if id == 0:
            raise NotFound

    # パスパラメータとして指定されたレコードIDが, 
    # 総レコード数を超えていたら,例外を発生させる.
    if id is not None:
        if id > db_session.query(Theme).count():
            raise NotFound

    # セッション未作成ならば, ホーム画面のページヘリダイレクトする.
    if not session:
        return redirect(url_for("view.home"))

    # セッション失効or未初期化ならば, ホーム画面のページヘリダイレクトする.
    if "is-admin-enter" not in session:
        return redirect(url_for("view.home"))

    # 管理者未入室の状態ならば, ホーム画面のページヘリダイレクトする.
    if session["is-admin-enter"] == False:
        return redirect(url_for("view.home"))

    if request.method == "GET":
        # セッションに現在ページの情報を設定して,
        # Flaskフォームと共にテンプレートを返す.
        session["referrer-page"] = "view.show_themes"

        # 該当ページ内のボタンから遷移するためのセッション項目を削除する.
        session.pop("hidden-modify-item-id", None)
        session.pop("hidden-detail-item-id", None)

        # DBから主題レコードを取得してテンプレートと共に返す.
        # RIDを指定された場合は, 一つだけレコードを取得する.
        if id is not None:
            thm_tmp = db_session.query(Theme).filter(Theme.id==id).first()
            db_session.close()
            if thm_tmp is not None:
                if len(str(thm_tmp.id)) > 6:
                    id_tmp = thm_tmp.id[0:6] + "..."
                else:
                    id_tmp = thm_tmp.id
                if len(thm_tmp.spell_and_header) > 6:
                    spll_n_hdr_tmp = thm_tmp.spell_and_header[0:6] + "..."
                else:
                    spll_n_hdr_tmp = thm_tmp.spell_and_header
                if len(thm_tmp.mean_and_content) > 6:
                    mn_n_cntnt_tmp = thm_tmp.mean_and_content[0:6] + "..."
                else:
                    mn_n_cntnt_tmp = thm_tmp.mean_and_content
                if len(thm_tmp.staff_name) > 6:
                    stff_nm_tmp = thm_tmp.staff_name[0:6] + "..."
                else:
                    stff_nm_tmp = thm_tmp.staff_name
                thms_fnl.append([id_tmp,
                                 spll_n_hdr_tmp,
                                 mn_n_cntnt_tmp,
                                 stff_nm_tmp
                                ])
                per_pg = consts.THEME_PER_PAGE
                pg = request.args.get(get_page_parameter(), type=int, default=1)
                pg_dat = thms_fnl[(pg - 1) * per_pg : pg * per_pg]
                pgntn = Pagination(page=pg,
                                   total=len(thms_fnl),
                                   per_page=per_pg,
                                   css_framework=consts.PAGINATION_CSS
                                  )
                return render_template("show_themes.html", page_data=pg_dat, pagination=pgntn)

            per_pg = consts.THEME_PER_PAGE
            pg = request.args.get(get_page_parameter(), type=int, default=1)
            pg_dat = thms_fnl[(pg - 1) * per_pg : pg * per_pg]
            pgntn = Pagination(page=pg,
                               total=len(thms_fnl),
                               per_page=per_pg,
                               css_framework=consts.PAGINATION_CSS
                              )
            return render_template("show_themes.html", page_data=pg_dat, pagination=pgntn)

        else:
            thms_tmp = db_session.query(Theme).order_by(Theme.id).all()
            db_session.close()
            for thm_tmp in thms_tmp:
                 if len(str(thm_tmp.id)) > 6:
                     id_tmp = thm_tmp.id[0:6] + "..."
                 else:
                     id_tmp = thm_tmp.id
                 if len(thm_tmp.spell_and_header) > 6:
                     spll_n_hdr_tmp = thm_tmp.spell_and_header[0:6] + "..."
                 else:
                     spll_n_hdr_tmp = thm_tmp.spell_and_header
                 if len(thm_tmp.mean_and_content) > 6:
                     mn_n_cntnt_tmp = thm_tmp.mean_and_content[0:6] + "..."
                 else:
                     mn_n_cntnt_tmp = thm_tmp.mean_and_content
                 if len(thm_tmp.staff_name) > 6:
                     stff_nm_tmp = thm_tmp.staff_name[0:6] + "..."
                 else:
                     stff_nm_tmp = thm_tmp.staff_name
                 thms_fnl.append([id_tmp,
                                  spll_n_hdr_tmp,
                                  mn_n_cntnt_tmp,
                                  stff_nm_tmp
                                 ])
            per_pg = consts.THEME_PER_PAGE
            pg = request.args.get(get_page_parameter(), type=int, default=1)
            pg_dat = thms_fnl[(pg - 1) * per_pg : pg * per_pg]
            pgntn = Pagination(page=pg,
                               total=len(thms_fnl),
                               per_page=per_pg,
                               css_framework=consts.PAGINATION_CSS
                              )
            return render_template("show_themes.html", page_data=pg_dat, pagination=pgntn)

    if request.method == "POST":
        # 直前に, GETメソッドで該当ページを取得しているかを調べる.
        # 取得していなければ, 強制的に現在ページへリダイレクトする.
        if session["referrer-page"] != "view.show_themes":
            return redirect(url_for("view.show_themes"))

        # フォームボタン群の中から, 押下されたボタンに応じたページへリダイレクトする.
        if request.form["hidden-modify-item-id"] != "":
            session["hidden-modify-item-id"] = request.form["hidden-modify-item-id"]
            return redirect(url_for("view.modify_word"))
        if request.form["hidden-detail-item-id"] != "":
            session["hidden-detail-item-id"] = request.form["hidden-detail-item-id"]
            return redirect(url_for("view.detail_word"))


# 「show_categories」のためのビュー関数(=URLエンドポイント)を宣言・定義する.
@view.route("/show_categories", methods=["GET", "POST"])
@view.route("/show_categories/<int:id>", methods=["GET", "POST"])
def show_categories(id=None):
    # 関数内で使用する変数・オブジェクトを宣言・定義する.
    ctgrs_tmp = []
    ctgrs_fnl = []

    # 該当のURLエンドポイントに入ったことをロギングする.
    rslt = se.etc.logging__info("view at /show_categories")

    # ロギングに失敗したら, 例外を発生させる.
    if rslt == "NG":
        raise InternalServerError

    # 指定URLにパスパラメータが含まれていて,
    # かつ不正な値であれば, 例外を発生させる.
    if id is not None:
        if id == 0:
            raise NotFound

    # パスパラメータとして指定されたレコードIDが, 
    # 総レコード数を超えていたら,例外を発生させる.
    if id is not None:
        if id > db_session.query(Category).count():
            raise NotFound

    # セッション未作成ならば, ホーム画面のページヘリダイレクトする.
    if not session:
        return redirect(url_for("view.home"))

    # セッション失効or未初期化ならば, ホーム画面のページヘリダイレクトする.
    if "is-admin-enter" not in session:
        return redirect(url_for("view.home"))

    # 管理者未入室の状態ならば, ホーム画面のページヘリダイレクトする.
    if session["is-admin-enter"] == False:
        return redirect(url_for("view.home"))

    if request.method == "GET":
        # セッションに現在ページの情報を設定して,
        # Flaskフォームと共にテンプレートを返す.
        session["referrer-page"] = "view.show_categories"

        # 該当ページ内のボタンから遷移するためのセッション項目を削除する.
        session.pop("hidden-modify-item-id", None)
        session.pop("hidden-detail-item-id", None)

        # DBから分類レコードを取得してテンプレートと共に返す.
        # RIDを指定された場合は, 一つだけレコードを取得する.
        if id is not None:
            ctgr_tmp = db_session.query(Category).filter(Category.id==id).first()
            db_session.close()
            if ctgr_tmp is not None:
                if len(str(ctgr_tmp.id)) > 6:
                    id_tmp = ctgr_tmp.id[0:6] + "..."
                else:
                    id_tmp = ctgr_tmp.id
                if len(ctgr_tmp.spell_and_header) > 6:
                    spll_n_hdr_tmp = ctgr_tmp.spell_and_header[0:6] + "..."
                else:
                    spll_n_hdr_tmp = ctgr_tmp.spell_and_header
                if len(ctgr_tmp.mean_and_content) > 6:
                    mn_n_cntnt_tmp = ctgr_tmp.mean_and_content[0:6] + "..."
                else:
                    mn_n_cntnt_tmp = ctgr_tmp.mean_and_content
                if len(ctgr_tmp.staff_name) > 6:
                    stff_nm_tmp = ctgr_tmp.staff_name[0:6] + "..."
                else:
                    stff_nm_tmp = ctgr_tmp.staff_name
                ctgrs_fnl.append([id_tmp,
                                  spll_n_hdr_tmp,
                                  mn_n_cntnt_tmp,
                                  stff_nm_tmp
                                 ])
                per_pg = consts.CATEGORY_PER_PAGE
                pg = request.args.get(get_page_parameter(), type=int, default=1)
                pg_dat = ctgrs_fnl[(pg - 1) * per_pg : pg * per_pg]
                pgntn = Pagination(page=pg,
                                   total=len(ctgrs_fnl),
                                   per_page=per_pg,
                                   css_framework=consts.PAGINATION_CSS
                                  )
                return render_template("show_categories.html", page_data=pg_dat, pagination=pgntn)

            per_pg = consts.CATEGORY_PER_PAGE
            pg = request.args.get(get_page_parameter(), type=int, default=1)
            pg_dat = ctgrs_fnl[(pg - 1) * per_pg : pg * per_pg]
            pgntn = Pagination(page=pg,
                               total=len(ctgrs_fnl),
                               per_page=per_pg,
                               css_framework=consts.PAGINATION_CSS
                              )
            return render_template("show_categories.html", page_data=pg_dat, pagination=pgntn)

        else:
            ctgrs_tmp = db_session.query(Category).order_by(Category.id).all()
            db_session.close()
            for ctgr_tmp in ctgrs_tmp:
                if len(str(ctgr_tmp.id)) > 6:
                    id_tmp = ctgr_tmp.id[0:6] + "..."
                else:
                    id_tmp = ctgr_tmp.id
                if len(ctgr_tmp.spell_and_header) > 6:
                    spll_n_hdr_tmp = ctgr_tmp.spell_and_header[0:6] + "..."
                else:
                    spll_n_hdr_tmp = ctgr_tmp.spell_and_header
                if len(ctgr_tmp.mean_and_content) > 6:
                    mn_n_cntnt_tmp = ctgr_tmp.mean_and_content[0:6] + "..."
                else:
                    mn_n_cntnt_tmp = ctgr_tmp.mean_and_content
                if len(ctgr_tmp.staff_name) > 6:
                    stff_nm_tmp = ctgr_tmp.staff_name[0:6] + "..."
                else:
                    stff_nm_tmp = ctgr_tmp.staff_name
                ctgrs_fnl.append([id_tmp,
                                  spll_n_hdr_tmp,
                                  mn_n_cntnt_tmp,
                                  stff_nm_tmp
                                 ])
            per_pg = consts.CATEGORY_PER_PAGE
            pg = request.args.get(get_page_parameter(), type=int, default=1)
            pg_dat = ctgrs_fnl[(pg - 1) * per_pg : pg * per_pg]
            pgntn = Pagination(page=pg,
                               total=len(ctgrs_fnl),
                               per_page=per_pg,
                               css_framework=consts.PAGINATION_CSS
                              )
            return render_template("show_categories.html", page_data=pg_dat, pagination=pgntn)

    if request.method == "POST":
        # 直前に, GETメソッドで該当ページを取得しているかを調べる.
        # 取得していなければ, 強制的に現在ページへリダイレクトする.
        if session["referrer-page"] != "view.show_categories":
            return redirect(url_for("view.show_categories"))

        # フォームボタン群の中から, 押下されたボタンに応じたページへリダイレクトする.
        if request.form["hidden-modify-item-id"] != "":
            session["hidden-modify-item-id"] = request.form["hidden-modify-item-id"]
            return redirect(url_for("view.modify_category"))
        if request.form["hidden-detail-item-id"] != "":
            session["hidden-detail-item-id"] = request.form["hidden-detail-item-id"]
            return redirect(url_for("view.detail_category"))


# 「show_knowledges」のためのビュー関数(=URLエンドポイント)を宣言・定義する.
@view.route("/show_knowledges", methods=["GET", "POST"])
@view.route("/show_knowledges/<int:id>", methods=["GET", "POST"])
def show_knowledges(id=None):
    # 関数内で使用する変数・オブジェクトを宣言・定義する.
    knwldgs_tmp = []
    knwldgs_fnl = []

    # 該当のURLエンドポイントに入ったことをロギングする.
    rslt = se.etc.logging__info("view at /show_knowledges")

    # ロギングに失敗したら, 例外を発生させる.
    if rslt == "NG":
        raise InternalServerError

    # 指定URLにパスパラメータが含まれていて,
    # かつ不正な値であれば, 例外を発生させる.
    if id is not None:
        if id == 0:
            raise NotFound

    # パスパラメータとして指定されたレコードIDが, 
    # 総レコード数を超えていたら,例外を発生させる.
    if id is not None:
        if id > db_session.query(Knowledge).count():
            raise NotFound

    # セッション未作成ならば, ホーム画面のページヘリダイレクトする.
    if not session:
        return redirect(url_for("view.home"))

    # セッション失効or未初期化ならば, ホーム画面のページヘリダイレクトする.
    if "is-admin-enter" not in session:
        return redirect(url_for("view.home"))

    # 管理者未入室の状態ならば, ホーム画面のページヘリダイレクトする.
    if session["is-admin-enter"] == False:
        return redirect(url_for("view.home"))

    if request.method == "GET":
        # セッションに現在ページの情報を設定して,
        # Flaskフォームと共にテンプレートを返す.
        session["referrer-page"] = "view.show_knowledges"

        # 該当ページ内のボタンから遷移するためのセッション項目を削除する.
        session.pop("hidden-modify-item-id", None)
        session.pop("hidden-detail-item-id", None)

        # DBから知識レコードを取得してテンプレートと共に返す.
        # RIDを指定された場合は, 一つだけレコードを取得する.
        if id is not None:
            knwldg_tmp = db_session.query(Knowledge).filter(Knowledge.id==id).first()
            db_session.close()
            if knwldg_tmp is not None:
                if len(str(knwldg_tmp.id)) > 6:
                    id_tmp = knwldg_tmp.id[0:6] + "..."
                else:
                    id_tmp = knwldg_tmp.id
                if len(knwldg_tmp.spell_and_header) > 6:
                    spll_n_hdr_tmp = knwldg_tmp.spell_and_header[0:6] + "..."
                else:
                    spll_n_hdr_tmp = knwldg_tmp.spell_and_header
                if len(knwldg_tmp.mean_and_content) > 6:
                    mn_n_cntnt_tmp = knwldg_tmp.mean_and_content[0:6] + "..."
                else:
                    mn_n_cntnt_tmp = knwldg_tmp.mean_and_content
                if len(knwldg_tmp.staff_name) > 6:
                    stff_nm_tmp = knwldg_tmp.staff_name[0:6] + "..."
                else:
                    stff_nm_tmp = knwldg_tmp.staff_name
                knwldgs_fnl.append([id_tmp,
                                    spll_n_hdr_tmp,
                                    mn_n_cntnt_tmp,
                                    stff_nm_tmp
                                  ])
                per_pg = consts.KNOWLEDGE_PER_PAGE
                pg = request.args.get(get_page_parameter(), type=int, default=1)
                pg_dat = knwldgs_fnl[(pg - 1) * per_pg : pg * per_pg]
                pgntn = Pagination(page=pg,
                                   total=len(knwldgs_fnl),
                                   per_page=per_pg,
                                   css_framework=consts.PAGINATION_CSS
                                  )
                return render_template("show_knowledges.html", page_data=pg_dat, pagination=pgntn)

            per_pg = consts.KNOWLEDGE_PER_PAGE
            pg = request.args.get(get_page_parameter(), type=int, default=1)
            pg_dat = knwldgs_fnl[(pg - 1) * per_pg : pg * per_pg]
            pgntn = Pagination(page=pg,
                               total=len(knwldgs_fnl),
                               per_page=per_pg,
                               css_framework=consts.PAGINATION_CSS
                              )
            return render_template("show_knowledges.html", page_data=pg_dat, pagination=pgntn)

        else:
            knwldgs_tmp = db_session.query(Knowledge).order_by(Knowledge.id).all()
            db_session.close()
            for knwldg_tmp in knwldgs_tmp:
                if len(str(knwldg_tmp.id)) > 6:
                    id_tmp = knwldg_tmp.id[0:6] + "..."
                else:
                    id_tmp = knwldg_tmp.id
                if len(knwldg_tmp.spell_and_header) > 6:
                    spll_n_hdr_tmp = knwldg_tmp.spell_and_header[0:6] + "..."
                else:
                    spll_n_hdr_tmp = knwldg_tmp.spell_and_header
                if len(knwldg_tmp.mean_and_content) > 6:
                    mn_n_cntnt_tmp = knwldg_tmp.mean_and_content[0:6] + "..."
                else:
                    mn_n_cntnt_tmp = knwldg_tmp.mean_and_content
                if len(knwldg_tmp.staff_name) > 6:
                    stff_nm_tmp = knwldg_tmp.staff_name[0:6] + "..."
                else:
                    stff_nm_tmp = knwldg_tmp.staff_name
                knwldgs_fnl.append([id_tmp,
                                    spll_n_hdr_tmp,
                                    mn_n_cntnt_tmp,
                                    stff_nm_tmp
                                   ])
            per_pg = consts.KNOWLEDGE_PER_PAGE
            pg = request.args.get(get_page_parameter(), type=int, default=1)
            pg_dat = knwldgs_fnl[(pg - 1) * per_pg : pg * per_pg]
            pgntn = Pagination(page=pg,
                               total=len(knwldgs_fnl),
                               per_page=per_pg,
                               css_framework=consts.PAGINATION_CSS
                              )
            return render_template("show_knowledges.html", page_data=pg_dat, pagination=pgntn)

    if request.method == "POST":
        # 直前に, GETメソッドで該当ページを取得しているかを調べる.
        # 取得していなければ, 強制的に現在ページへリダイレクトする.
        if session["referrer-page"] != "view.show_knowledges":
            return redirect(url_for("view.show_knowledges"))

        # フォームボタン群の中から, 押下されたボタンに応じたページへリダイレクトする.
        if request.form["hidden-modify-item-id"] != "":
            session["hidden-modify-item-id"] = request.form["hidden-modify-item-id"]
            return redirect(url_for("view.modify_knowledge"))
        if request.form["hidden-detail-item-id"] != "":
            session["hidden-detail-item-id"] = request.form["hidden-detail-item-id"]
            return redirect(url_for("view.detail_knowledge"))


# 「show_rules」のためのビュー関数(=URLエンドポイント)を宣言・定義する.
@view.route("/show_rules", methods=["GET", "POST"])
@view.route("/show_rules/<int:id>", methods=["GET", "POST"])
def show_rules(id=None):
    # 関数内で使用する変数・オブジェクトを宣言・定義する.
    rls_tmp = []
    rls_fnl = []

    # 該当のURLエンドポイントに入ったことをロギングする.
    rslt = se.etc.logging__info("view at /show_rules")

    # ロギングに失敗したら, 例外を発生させる.
    if rslt == "NG":
        raise InternalServerError

    # 指定URLにパスパラメータが含まれていて,
    # かつ不正な値であれば, 例外を発生させる.
    if id is not None:
        if id == 0:
            raise NotFound

    # パスパラメータとして指定されたレコードIDが, 
    # 総レコード数を超えていたら,例外を発生させる.
    if id is not None:
        if id > db_session.query(Rule).count():
            raise NotFound

    # セッション未作成ならば, ホーム画面のページヘリダイレクトする.
    if not session:
        return redirect(url_for("view.home"))

    # セッション失効or未初期化ならば, ホーム画面のページヘリダイレクトする.
    if "is-admin-enter" not in session:
        return redirect(url_for("view.home"))

    # 管理者未入室の状態ならば, ホーム画面のページヘリダイレクトする.
    if session["is-admin-enter"] == False:
        return redirect(url_for("view.home"))

    if request.method == "GET":
        # セッションに現在ページの情報を設定して,
        # Flaskフォームと共にテンプレートを返す.
        session["referrer-page"] = "view.show_rules"

        # 該当ページ内のボタンから遷移するためのセッション項目を削除する.
        session.pop("hidden-modify-item-id", None)
        session.pop("hidden-detail-item-id", None)

        # DBから規則レコードを取得してテンプレートと共に返す.
        # RIDを指定された場合は, 一つだけレコードを取得する.
        if id is not None:
            rl_tmp = db_session.query(Rule).filter(Rule.id==id).first()
            db_session.close()
            if rl_tmp is not None:
                if len(str(rl_tmp.id)) > 6:
                    id_tmp = rl_tmp.id[0:6] + "..."
                else:
                    id_tmp = rl_tmp.id
                if len(rl_tmp.spell_and_header) > 6:
                    spll_n_hdr_tmp = rl_tmp.spell_and_header[0:6] + "..."
                else:
                    spll_n_hdr_tmp = rl_tmp.spell_and_header
                if len(rl_tmp.mean_and_content) > 6:
                    mn_n_cntnt_tmp = rl_tmp.mean_and_content[0:6] + "..."
                else:
                    mn_n_cntnt_tmp = rl_tmp.mean_and_content
                if len(rl_tmp.staff_name) > 6:
                    stff_nm_tmp = rl_tmp.staff_name[0:6] + "..."
                else:
                    stff_nm_tmp = rl_tmp.staff_name
                rls_fnl.append([id_tmp,
                                spll_n_hdr_tmp,
                                mn_n_cntnt_tmp,
                                stff_nm_tmp
                               ])
                per_pg = consts.RULE_PER_PAGE
                pg = request.args.get(get_page_parameter(), type=int, default=1)
                pg_dat = rls_fnl[(pg - 1) * per_pg : pg * per_pg]
                pgntn = Pagination(page=pg,
                                   total=len(rls_fnl),
                                   per_page=per_pg,
                                   css_framework=consts.PAGINATION_CSS
                                  )
                return render_template("show_rules.html", page_data=pg_dat, pagination=pgntn)

            per_pg = consts.RULE_PER_PAGE
            pg = request.args.get(get_page_parameter(), type=int, default=1)
            pg_dat = rls_fnl[(pg - 1) * per_pg : pg * per_pg]
            pgntn = Pagination(page=pg,
                               total=len(rls_fnl),
                               per_page=per_pg,
                               css_framework=consts.PAGINATION_CSS
                              )
            return render_template("show_rules.html", page_data=pg_dat, pagination=pgntn)

        else:
            rls_tmp = db_session.query(Rule).order_by(Rule.id).all()
            db_session.close()
            for rl_tmp in rls_tmp:
                if len(str(rl_tmp.id)) > 6:
                    id_tmp = rl_tmp.id[0:6] + "..."
                else:
                    id_tmp = rl_tmp.id
                if len(rl_tmp.spell_and_header) > 6:
                    spll_n_hdr_tmp = rl_tmp.spell_and_header[0:6] + "..."
                else:
                    spll_n_hdr_tmp = rl_tmp.spell_and_header
                if len(rl_tmp.mean_and_content) > 6:
                    mn_n_cntnt_tmp = rl_tmp.mean_and_content[0:6] + "..."
                else:
                    mn_n_cntnt_tmp = rl_tmp.mean_and_content
                if len(rl_tmp.staff_name) > 6:
                    stff_nm_tmp = rl_tmp.staff_name[0:6] + "..."
                else:
                    stff_nm_tmp = rl_tmp.staff_name
                rls_fnl.append([id_tmp,
                                spll_n_hdr_tmp,
                                mn_n_cntnt_tmp,
                                stff_nm_tmp
                               ])
            per_pg = consts.RULE_PER_PAGE
            pg = request.args.get(get_page_parameter(), type=int, default=1)
            pg_dat = rls_fnl[(pg - 1) * per_pg : pg * per_pg]
            pgntn = Pagination(page=pg,
                               total=len(rls_fnl),
                               per_page=per_pg,
                               css_framework=consts.PAGINATION_CSS
                              )
            return render_template("show_rules.html", page_data=pg_dat, pagination=pgntn)

    if request.method == "POST":
        # 直前に, GETメソッドで該当ページを取得しているかを調べる.
        # 取得していなければ, 強制的に現在ページへリダイレクトする.
        if session["referrer-page"] != "view.show_rules":
            return redirect(url_for("view.show_rules"))

        # フォームボタン群の中から, 押下されたボタンに応じたページへリダイレクトする.
        if request.form["hidden-modify-item-id"] != "":
            session["hidden-modify-item-id"] = request.form["hidden-modify-item-id"]
            return redirect(url_for("view.modify_rule"))
        if request.form["hidden-detail-item-id"] != "":
            session["hidden-detail-item-id"] = request.form["hidden-detail-item-id"]
            return redirect(url_for("view.detail_rule"))


# 「show_reactions」のためのビュー関数(=URLエンドポイント)を宣言・定義する.
@view.route("/show_reactions", methods=["GET", "POST"])
@view.route("/show_reactions/<int:id>", methods=["GET", "POST"])
def show_reactions(id=None):
    # 関数内で使用する変数・オブジェクトを宣言・定義する.
    rctns_tmp = []
    rctns_fnl = []

    # 該当のURLエンドポイントに入ったことをロギングする.
    rslt = se.etc.logging__info("view at /show_reactions")

    # ロギングに失敗したら, 例外を発生させる.
    if rslt == "NG":
        raise InternalServerError

    # 指定URLにパスパラメータが含まれていて,
    # かつ不正な値であれば, 例外を発生させる.
    if id is not None:
        if id == 0:
            raise NotFound

    # パスパラメータとして指定されたレコードIDが, 
    # 総レコード数を超えていたら,例外を発生させる.
    if id is not None:
        if id > db_session.query(Rule).count():
            raise NotFound

    # セッション未作成ならば, ホーム画面のページヘリダイレクトする.
    if not session:
        return redirect(url_for("view.home"))

    # セッション失効or未初期化ならば, ホーム画面のページヘリダイレクトする.
    if "is-admin-enter" not in session:
        return redirect(url_for("view.home"))

    # 管理者未入室の状態ならば, ホーム画面のページヘリダイレクトする.
    if session["is-admin-enter"] == False:
        return redirect(url_for("view.home"))

    if request.method == "GET":
        # セッションに現在ページの情報を設定して,
        # Flaskフォームと共にテンプレートを返す.
        session["referrer-page"] = "view.show_reactions"

        # 該当ページ内のボタンから遷移するためのセッション項目を削除する.
        session.pop("hidden-modify-item-id", None)
        session.pop("hidden-detail-item-id", None)

        # DBから規則レコードを取得してテンプレートと共に返す.
        # RIDを指定された場合は, 一つだけレコードを取得する.
        if id is not None:
            rctn_tmp = db_session.query(Reaction).filter(Reaction.id==id).first()
            db_session.close()
            if rctn_tmp is not None:
                if len(str(rctn_tmp.id)) > 6:
                    id_tmp = rctn_tmp.id[0:6] + "..."
                else:
                    id_tmp = rctn_tmp.id
                if len(rctn_tmp.spell_and_header) > 6:
                    spll_n_hdr_tmp = rctn_tmp.spell_and_header[0:6] + "..."
                else:
                    spll_n_hdr_tmp = rctn_tmp.spell_and_header
                if len(rctn_tmp.mean_and_content) > 6:
                    mn_n_cntnt_tmp = rctn_tmp.mean_and_content[0:6] + "..."
                else:
                    mn_n_cntnt_tmp = rctn_tmp.mean_and_content
                if len(rctn_tmp.staff_name) > 6:
                    stff_nm_tmp = rctn_tmp.staff_name[0:6] + "..."
                else:
                    stff_nm_tmp = rctn_tmp.staff_name
                rctns_fnl.append([id_tmp,
                                spll_n_hdr_tmp,
                                mn_n_cntnt_tmp,
                                stff_nm_tmp
                               ])
                per_pg = consts.RULE_PER_PAGE
                pg = request.args.get(get_page_parameter(), type=int, default=1)
                pg_dat = rctns_fnl[(pg - 1) * per_pg : pg * per_pg]
                pgntn = Pagination(page=pg,
                                   total=len(rctns_fnl),
                                   per_page=per_pg,
                                   css_framework=consts.PAGINATION_CSS
                                  )
                return render_template("show_reactions.html", page_data=pg_dat, pagination=pgntn)

            per_pg = consts.RULE_PER_PAGE
            pg = request.args.get(get_page_parameter(), type=int, default=1)
            pg_dat = rctns_fnl[(pg - 1) * per_pg : pg * per_pg]
            pgntn = Pagination(page=pg,
                               total=len(rctns_fnl),
                               per_page=per_pg,
                               css_framework=consts.PAGINATION_CSS
                              )
            return render_template("show_reactions.html", page_data=pg_dat, pagination=pgntn)

        else:
            rctns_tmp = db_session.query(Reaction).order_by(Reaction.id).all()
            db_session.close()
            for rctn_tmp in rctns_tmp:
                if len(str(rctn_tmp.id)) > 6:
                    id_tmp = rctn_tmp.id[0:6] + "..."
                else:
                    id_tmp = rctn_tmp.id
                if len(rctn_tmp.spell_and_header) > 6:
                    spll_n_hdr_tmp = rctn_tmp.spell_and_header[0:6] + "..."
                else:
                    spll_n_hdr_tmp = rctn_tmp.spell_and_header
                if len(rctn_tmp.mean_and_content) > 6:
                    mn_n_cntnt_tmp = rctn_tmp.mean_and_content[0:6] + "..."
                else:
                    mn_n_cntnt_tmp = rctn_tmp.mean_and_content
                if len(rctn_tmp.staff_name) > 6:
                    stff_nm_tmp = rctn_tmp.staff_name[0:6] + "..."
                else:
                    stff_nm_tmp = rctn_tmp.staff_name
                rctns_fnl.append([id_tmp,
                                spll_n_hdr_tmp,
                                mn_n_cntnt_tmp,
                                stff_nm_tmp
                               ])
            per_pg = consts.RULE_PER_PAGE
            pg = request.args.get(get_page_parameter(), type=int, default=1)
            pg_dat = rctns_fnl[(pg - 1) * per_pg : pg * per_pg]
            pgntn = Pagination(page=pg,
                               total=len(rctns_fnl),
                               per_page=per_pg,
                               css_framework=consts.PAGINATION_CSS
                              )
            return render_template("show_reactions.html", page_data=pg_dat, pagination=pgntn)

    if request.method == "POST":
        # 直前に, GETメソッドで該当ページを取得しているかを調べる.
        # 取得していなければ, 強制的に現在ページへリダイレクトする.
        if session["referrer-page"] != "view.show_reactions":
            return redirect(url_for("view.show_reactions"))

        # フォームボタン群の中から, 押下されたボタンに応じたページへリダイレクトする.
        if request.form["hidden-modify-item-id"] != "":
            session["hidden-modify-item-id"] = request.form["hidden-modify-item-id"]
            return redirect(url_for("view.modify_reaction"))
        if request.form["hidden-detail-item-id"] != "":
            session["hidden-detail-item-id"] = request.form["hidden-detail-item-id"]
            return redirect(url_for("view.detail_reaction"))


# 「show_generates」のためのビュー関数(=URLエンドポイント)を宣言・定義する.
@view.route("/show_generates", methods=["GET", "POST"])
@view.route("/show_generates/<int:id>", methods=["GET", "POST"])
def show_generates(id=None):
    # 関数内で使用する変数・オブジェクトを宣言・定義する.
    gens_tmp = []
    gens_fnl = []

    # 該当のURLエンドポイントに入ったことをロギングする.
    rslt = se.etc.logging__info("view at /show_generates")

    # ロギングに失敗したら, 例外を発生させる.
    if rslt == "NG":
        raise InternalServerError

    # 指定URLにパスパラメータが含まれていて,
    # かつ不正な値であれば, 例外を発生させる.
    if id is not None:
        if id == 0:
            raise NotFound

    # パスパラメータとして指定されたレコードIDが, 
    # 総レコード数を超えていたら,例外を発生させる.
    if id is not None:
        if id > db_session.query(Generate).count():
            raise NotFound

    # セッション未作成ならば, ホーム画面のページヘリダイレクトする.
    if not session:
        return redirect(url_for("view.home"))

    # セッション失効or未初期化ならば, ホーム画面のページヘリダイレクトする.
    if "is-admin-enter" not in session:
        return redirect(url_for("view.home"))

    # 管理者未入室の状態ならば, ホーム画面のページヘリダイレクトする.
    if session["is-admin-enter"] == False:
        return redirect(url_for("view.home"))

    if request.method == "GET":
        # セッションに現在ページの情報を設定して,
        # Flaskフォームと共にテンプレートを返す.
        session["referrer-page"] = "view.show_generates"

        # 該当ページ内のボタンから遷移するためのセッション項目を削除する.
        session.pop("hidden-retrieve-item-id", None)
        session.pop("hidden-detail-item-id", None)

        # DBから生成レコードを取得してテンプレートと共に返す.
        # RIDを指定された場合は, 一つだけレコードを取得する.
        if id is not None:
            gen_tmp = db_session.query(Generate).filter(Generate.id==id).first()
            db_session.close()
            if gen_tmp is not None:
                if len(str(gen_tmp.id)) > 6:
                   id_tmp = gen_tmp.id[0:6] + "..."
                else:
                   id_tmp = gen_tmp.id
                if len(gen_tmp.spell_and_header) > 6:
                    spll_n_hdr_tmp = gen_tmp.spell_and_header[0:6] + "..."
                else:
                    spll_n_hdr_tmp = gen_tmp.spell_and_header
                if len(gen_tmp.mean_and_content) > 6:
                    mn_n_cntnt_tmp = gen_tmp.mean_and_content[0:6] + "..."
                else:
                    mn_n_cntnt_tmp = gen_tmp.mean_and_content
                if len(gen_tmp.staff_name) > 6:
                    stff_nm_tmp = gen_tmp.staff_name[0:6] + "..."
                else:
                    stff_nm_tmp = gen_tmp.staff_name
                gens_fnl.append([id_tmp,
                                 spll_n_hdr_tmp,
                                 mn_n_cntnt_tmp,
                                 stff_nm_tmp
                                ])
                per_pg = consts.GENERATE_PER_PAGE
                pg = request.args.get(get_page_parameter(), type=int, default=1)
                pg_dat = gens_fnl[(pg - 1) * per_pg : pg * per_pg]
                pgntn = Pagination(page=pg,
                                   total=len(gens_fnl),
                                   per_page=per_pg,
                                   css_framework=consts.PAGINATION_CSS
                                  )
                return render_template("show_generates.html", page_data=pg_dat, pagination=pgntn)

            per_pg = consts.GENERATE_PER_PAGE
            pg = request.args.get(get_page_parameter(), type=int, default=1)
            pg_dat = gens_fnl[(pg - 1) * per_pg : pg * per_pg]
            pgntn = Pagination(page=pg,
                               total=len(gens_fnl),
                               per_page=per_pg,
                               css_framework=consts.PAGINATION_CSS
                              )
            return render_template("show_generates.html", page_data=pg_dat, pagination=pgntn)

        else:
            gens_tmp = db_session.query(Generate).order_by(Generate.id).all()
            db_session.close()
            for gen_tmp in gens_tmp:
                if len(str(gen_tmp.id)) > 6:
                    id_tmp = gen_tmp.id[0:6] + "..."
                else:
                    id_tmp = gen_tmp.id
                if len(gen_tmp.spell_and_header) > 6:
                    spll_n_hdr_tmp = gen_tmp.spell_and_header[0:6] + "..."
                else:
                    spll_n_hdr_tmp = gen_tmp.spell_and_header
                if len(gen_tmp.mean_and_content) > 6:
                    mn_n_cntnt_tmp = gen_tmp.mean_and_content[0:6] + "..."
                else:
                    mn_n_cntnt_tmp = gen_tmp.mean_and_content
                if len(gen_tmp.staff_name) > 6:
                    stff_nm_tmp = gen_tmp.staff_name[0:6] + "..."
                else:
                    stff_nm_tmp = gen_tmp.staff_name
                gens_fnl.append([id_tmp,
                                 spll_n_hdr_tmp,
                                 mn_n_cntnt_tmp,
                                 stff_nm_tmp
                                ])
            per_pg = consts.GENERATE_PER_PAGE
            pg = request.args.get(get_page_parameter(), type=int, default=1)
            pg_dat = gens_fnl[(pg - 1) * per_pg : pg * per_pg]
            pgntn = Pagination(page=pg,
                               total=len(gens_fnl),
                               per_page=per_pg,
                               css_framework=consts.PAGINATION_CSS
                              )
            return render_template("show_generates.html", page_data=pg_dat, pagination=pgntn)

    if request.method == "POST":
        # 直前に, GETメソッドで該当ページを取得しているかを調べる.
        # 取得していなければ, 強制的に現在ページへリダイレクトする.
        if session["referrer-page"] != "view.show_generates":
            return redirect(url_for("view.show_generates"))

        # フォームボタン群の中から, 押下されたボタンに応じたページへリダイレクトする.
        if request.form["hidden-retrieve-item-id"] != "":
            session["hidden-retrieve-item-id"] = request.form["hidden-retrieve-item-id"]
            return redirect(url_for("view.retrieve_generate"))
        if request.form["hidden-detail-item-id"] != "":
            session["hidden-detail-item-id"] = request.form["hidden-detail-item-id"]
            return redirect(url_for("view.detail_generate"))


# 「show_histories」のためのビュー関数(=URLエンドポイント)を宣言・定義する.
@view.route("/show_histories", methods=["GET", "POST"])
@view.route("/show_histories/<int:id>", methods=["GET", "POST"])
def show_histories(id=None):
    # 関数内で使用する変数・オブジェクトを宣言・定義する.
    hists_tmp = []
    hists_fnl = []

    # 該当のURLエンドポイントに入ったことをロギングする.
    rslt = se.etc.logging__info("view at /show_histories")

    # ロギングに失敗したら, 例外を発生させる.
    if rslt == "NG":
        raise InternalServerError

    # 指定URLにパスパラメータが含まれていて,
    # かつ不正な値であれば, 例外を発生させる.
    if id is not None:
        if id == 0:
            raise NotFound

    # パスパラメータとして指定されたレコードIDが, 
    # 総レコード数を超えていたら,例外を発生させる.
    if id is not None:
        if id > db_session.query(History).count():
            raise NotFound

    # セッション未作成ならば, ホーム画面のページヘリダイレクトする.
    if not session:
        return redirect(url_for("view.home"))

    # セッション失効or未初期化ならば, ホーム画面のページヘリダイレクトする.
    if "is-admin-enter" not in session:
        return redirect(url_for("view.home"))

    # 管理者未入室の状態ならば, ホーム画面のページヘリダイレクトする.
    if session["is-admin-enter"] == False:
        return redirect(url_for("view.home"))

    if request.method == "GET":
        # セッションに現在ページの情報を設定して,
        # Flaskフォームと共にテンプレートを返す.
        session["referrer-page"] = "view.show_histories"

        # 該当ページ内のボタンから遷移するためのセッション項目を削除する.
        session.pop("hidden-modify-item-id", None)
        session.pop("hidden-detail-item-id", None)

        # DBから履歴レコードを取得してテンプレートと共に返す.
        # RIDを指定された場合は, 一つだけレコードを取得する.
        if id is not None:
            hist_tmp = db_session.query(History).filter(History.id==id).first()
            db_session.close()
            if hist_tmp is not None:
                if len(str(hist_tmp.id)) > 6:
                    id_tmp = hist_tmp.id[0:6] + "..."
                else:
                    id_tmp = hist_tmp.id
                if len(hist_tmp.staff_message) > 6:
                    stff_msg_tmp = hist_tmp.staff_message[0:6] + "..."
                else:
                    stff_msg_tmp = hist_tmp.staff_message
                if len(hist_tmp.application_message) > 6:
                    app_msg_tmp = hist_tmp.application_message[0:6] + "..."
                else:
                    app_msg_tmp = hist_tmp.application_message
                if len(hist_tmp.staff_name) > 6:
                    stff_nm_tmp = hist_tmp.staff_name[0:6] + "..."
                else:
                    stff_nm_tmp = hist_tmp.staff_name
                hists_fnl.append([id_tmp,
                                  stff_msg_tmp,
                                  app_msg_tmp,
                                  stff_nm_tmp
                                ])
                per_pg = consts.HISTORY_PER_PAGE
                pg = request.args.get(get_page_parameter(), type=int, default=1)
                pg_dat = hists_fnl[(pg - 1) * per_pg : pg * per_pg]
                pgntn = Pagination(page=pg,
                                   total=len(hists_fnl),
                                   per_page=per_pg,
                                   css_framework=consts.PAGINATION_CSS
                                  )
                return render_template("show_histories.html", page_data=pg_dat, pagination=pgntn)

            per_pg = consts.HISTORY_PER_PAGE
            pg = request.args.get(get_page_parameter(), type=int, default=1)
            pg_dat = hists_fnl[(pg - 1) * per_pg : pg * per_pg]
            pgntn = Pagination(page=pg,
                               total=len(hists_fnl),
                               per_page=per_pg,
                               css_framework=consts.PAGINATION_CSS
                              )
            return render_template("show_histories.html", page_data=pg_dat, pagination=pgntn)

        else:
            hists_tmp = db_session.query(History).order_by(History.id).all()
            db_session.close()
            for hist_tmp in hists_tmp:
                if len(str(hist_tmp.id)) > 6:
                    id_tmp = hist_tmp.id[0:6] + "..."
                else:
                    id_tmp = hist_tmp.id
                if len(hist_tmp.staff_message) > 6:
                    stff_msg_tmp = hist_tmp.staff_message[0:6] + "..."
                else:
                    stff_msg_tmp = hist_tmp.staff_message
                if len(hist_tmp.application_message) > 6:
                    app_msg_tmp = hist_tmp.application_message[0:6] + "..."
                else:
                    app_msg_tmp = hist_tmp.application_message
                if len(hist_tmp.staff_name) > 6:
                    stff_nm_tmp = hist_tmp.staff_name[0:6] + "..."
                else:
                    stff_nm_tmp = hist_tmp.staff_name
                hists_fnl.append([id_tmp,
                                  stff_msg_tmp,
                                  app_msg_tmp,
                                  stff_nm_tmp
                                ])
            per_pg = consts.HISTORY_PER_PAGE
            pg = request.args.get(get_page_parameter(), type=int, default=1)
            pg_dat = hists_fnl[(pg - 1) * per_pg : pg * per_pg]
            pgntn = Pagination(page=pg,
                               total=len(hists_fnl),
                               per_page=per_pg,
                               css_framework=consts.PAGINATION_CSS
                              )
            return render_template("show_histories.html", page_data=pg_dat, pagination=pgntn)

    if request.method == "POST":
        # 直前に, GETメソッドで該当ページを取得しているかを調べる.
        # 取得していなければ, 強制的に現在ページへリダイレクトする.
        if session["referrer-page"] != "view.show_histories":
            return redirect(url_for("view.show_histories"))

        # フォームボタン群の中から, 押下されたボタンに応じたページへリダイレクトする.
        if request.form["hidden-modify-item-id"] != "":
            session["hidden-modify-item-id"] = request.form["hidden-modify-item-id"]
            return redirect(url_for("view.modify_history"))
        if request.form["hidden-detail-item-id"] != "":
            session["hidden-detail-item-id"] = request.form["hidden-detail-item-id"]
            return redirect(url_for("view.detail_history"))


# 「show_enters_or_exits」のためのビュー関数(=URLエンドポイント)を宣言・定義する.
@view.route("/show_enters_or_exits", methods=["GET", "POST"])
@view.route("/show_enters_or_exits/<int:id>", methods=["GET", "POST"])
def show_enters_or_exits(id=None):
    # 関数内で使用する変数・オブジェクトを宣言・定義する.
    ents_or_exts_tmp = []
    ents_or_exts_fnl = []

    # 該当のURLエンドポイントに入ったことをロギングする.
    rslt = se.etc.logging__info("view at /show_enters_or_exits")

    # ロギングに失敗したら, 例外を発生させる.
    if rslt == "NG":
        raise InternalServerError

    # 指定URLにパスパラメータが含まれていて,
    # かつ不正な値であれば, 例外を発生させる.
    if id is not None:
        if id == 0:
            raise NotFound

    # パスパラメータとして指定されたレコードIDが, 
    # 総レコード数を超えていたら,例外を発生させる.
    if id is not None:
        if id > db_session.query(EnterOrExit).count():
            raise NotFound

    # セッション未作成ならば, ホーム画面のページヘリダイレクトする.
    if not session:
        return redirect(url_for("view.home"))

    # セッション失効or未初期化ならば, ホーム画面のページヘリダイレクトする.
    if "is-admin-enter" not in session:
        return redirect(url_for("view.home"))

    # 管理者未入室の状態ならば, ホーム画面のページヘリダイレクトする.
    if session["is-admin-enter"] == False:
        return redirect(url_for("view.home"))

    if request.method == "GET":
        # セッションに現在ページの情報を設定して,
        # Flaskフォームと共にテンプレートを返す.
        session["referrer-page"] = "view.show_enters_or_exits"

        # 該当ページ内のボタンから遷移するためのセッション項目を削除する.
        session.pop("hidden-modify-item-id", None)
        session.pop("hidden-detail-item-id", None)


        # DBから入退レコードを取得してテンプレートと共に返す.
        # RIDを指定された場合は, 一つだけレコードを取得する.
        if id is not None:
            ent_or_ext_tmp = db_session.query(EnterOrExit).filter(EnterOrExit.id==id).first()
            db_session.close()
            if ent_or_ext_tmp is not None:
                if len(str(ent_or_ext_tmp.id)) > 6:
                    id_tmp = ent_or_ext_tmp.id[0:6] + "..."
                else:
                    id_tmp = ent_or_ext_tmp.id
                if len(ent_or_ext_tmp.staff_name) > 6:
                    stff_nm_tmp = ent_or_ext_tmp.staff_name[0:6] + "..."
                else:
                    stff_nm_tmp = ent_or_ext_tmp.staff_name
                if ent_or_ext_tmp.reason == "clock-in":
                    rsn_tmp = "出勤"
                elif ent_or_ext_tmp.reason == "return-to-out":
                    rsn_tmp = "外出戻り"
                elif ent_or_ext_tmp.reason == "after-break":
                    rsn_tmp = "休憩明け"
                elif ent_or_ext_tmp.reason == "clock-out":
                    rsn_tmp = "退勤"
                elif ent_or_ext_tmp.reason == "out":
                    rsn_tmp = "外出"
                elif ent_or_ext_tmp.reason == "break":
                    rsn_tmp = "休憩"
                elif ent_or_ext_tmp.reason == "forget-or-revocation":
                    rsn_tmp = "忘却or失効"
                elif ent_or_ext_tmp.reason == "application-termination":
                    rsn_tmp = "アプリ終了"
                else:
                    rsn_tmp = "その他(分類不明)"
                dttm_tmp = se.etc.convert_datetime_string_to_display_style(ent_or_ext_tmp.enter_or_exit_at)
                # dttm_tmp = se.etc.convert_datetime_string_to_display_style(ent_or_ext_tmp.enter_or_exit_at)
                ents_or_exts_fnl.append([id_tmp,
                                         stff_nm_tmp,
                                         rsn_tmp,
                                         dttm_tmp
                                        ])
                per_pg = consts.ENTER_OR_EXIT_PER_PAGE
                pg = request.args.get(get_page_parameter(), type=int, default=1)
                pg_dat = ents_or_exts_fnl[(pg - 1) * per_pg : pg * per_pg]
                pgntn = Pagination(page=pg,
                                   total=len(ents_or_exts_fnl),
                                   per_page=per_pg,
                                   css_framework=consts.PAGINATION_CSS
                                  )
                return render_template("show_enters_or_exits.html", page_data=pg_dat, pagination=pgntn)

            per_pg = consts.ENTER_OR_EXIT_PER_PAGE
            pg = request.args.get(get_page_parameter(), type=int, default=1)
            pg_dat = ents_or_exts_fnl[(pg - 1) * per_pg : pg * per_pg]
            pgntn = Pagination(page=pg,
                               total=len(ents_or_exts_fnl),
                               per_page=per_pg,
                               css_framework=consts.PAGINATION_CSS
                              )
            return render_template("show_enters_or_exits.html", page_data=pg_dat, pagination=pgntn)

        else:
            ents_or_exts_tmp = db_session.query(EnterOrExit).order_by(EnterOrExit.id).all()
            db_session.close()
            for ent_or_ext_tmp in ents_or_exts_tmp:
                if len(str(ent_or_ext_tmp.id)) > 6:
                    id_tmp = ent_or_ext_tmp.id[0:6] + "..."
                else:
                    id_tmp = ent_or_ext_tmp.id
                if len(ent_or_ext_tmp.staff_name) > 6:
                    stff_nm_tmp = ent_or_ext_tmp.staff_name[0:6] + "..."
                else:
                    stff_nm_tmp = ent_or_ext_tmp.staff_name
                if ent_or_ext_tmp.reason == "clock-in":
                    rsn_tmp = "出勤"
                elif ent_or_ext_tmp.reason == "return-to-out":
                    rsn_tmp = "外出戻り"
                elif ent_or_ext_tmp.reason == "after-break":
                    rsn_tmp = "休憩明け"
                elif ent_or_ext_tmp.reason == "clock-out":
                    rsn_tmp = "退勤"
                elif ent_or_ext_tmp.reason == "out":
                    rsn_tmp = "外出"
                elif ent_or_ext_tmp.reason == "break":
                    rsn_tmp = "休憩"
                elif ent_or_ext_tmp.reason == "forget-or-revocation":
                    rsn_tmp = "忘却or失効"
                elif ent_or_ext_tmp.reason == "application-termination":
                    rsn_tmp = "アプリ終了"
                else:
                    rsn_tmp = "その他(分類不明)"
                dttm_tmp = se.etc.convert_datetime_string_to_display_style(ent_or_ext_tmp.enter_or_exit_at)
                ents_or_exts_fnl.append([id_tmp,
                                         stff_nm_tmp,
                                         rsn_tmp,
                                         dttm_tmp
                                        ])
            per_pg = consts.ENTER_OR_EXIT_PER_PAGE
            pg = request.args.get(get_page_parameter(), type=int, default=1)
            pg_dat = ents_or_exts_fnl[(pg - 1) * per_pg : pg * per_pg]
            pgntn = Pagination(page=pg,
                               total=len(ents_or_exts_fnl),
                               per_page=per_pg,
                               css_framework=consts.PAGINATION_CSS
                              )
            return render_template("show_enters_or_exits.html", page_data=pg_dat, pagination=pgntn)

    if request.method == "POST":
        # 直前に, GETメソッドで該当ページを取得しているかを調べる.
        # 取得していなければ, 強制的に現在ページへリダイレクトする.
        if session["referrer-page"] != "view.show_enters_or_exits":
            return redirect(url_for("view.show_enters_or_exits"))

        # フォームボタン群の中から, 押下されたボタンに応じたページへリダイレクトする.
        if request.form["hidden-modify-item-id"] != "":
            session["hidden-modify-item-id"] = request.form["hidden-modify-item-id"]
            return redirect(url_for("view.modify_enter_or_exit"))
        if request.form["hidden-detail-item-id"] != "":
            session["hidden-detail-item-id"] = request.form["hidden-detail-item-id"]
            return redirect(url_for("view.detail_enter_or_exit"))


# 「show_staffs」のためのビュー関数(=URLエンドポイント)を宣言・定義する.
@view.route("/show_staffs", methods=["GET", "POST"])
@view.route("/show_staffs/<int:id>", methods=["GET", "POST"])
def show_staffs(id=None):
    # 関数内で使用する変数・オブジェクトを宣言・定義する.
    stffs_tmp = []
    stffs_fnl = []

    # 該当のURLエンドポイントに入ったことをロギングする.
    rslt = se.etc.logging__info("view at /show_staffs")

    # ロギングに失敗したら, 例外を発生させる.
    if rslt == "NG":
        raise InternalServerError

    # 指定URLにパスパラメータが含まれていて,
    # かつ不正な値であれば, 例外を発生させる.
    if id is not None:
        if id == 0:
            raise NotFound

    # パスパラメータとして指定されたレコードIDが, 
    # 総レコード数を超えていたら,例外を発生させる.
    if id is not None:
        if id > db_session.query(Staff).count():
            raise NotFound

    # セッション未作成ならば, ホーム画面のページヘリダイレクトする.
    if not session:
        return redirect(url_for("view.home"))

    # セッション失効or未初期化ならば, ホーム画面のページヘリダイレクトする.
    if "is-admin-enter" not in session:
        return redirect(url_for("view.home"))

    # 管理者未入室の状態ならば, ホーム画面のページヘリダイレクトする.
    if session["is-admin-enter"] == False:
        return redirect(url_for("view.home"))

    if request.method == "GET":
        # セッションに現在ページの情報を設定して,
        # Flaskフォームと共にテンプレートを返す.
        session["referrer-page"] = "view.show_staffs"

        # 該当ページ内のボタンから遷移するためのセッション項目を削除する.
        session.pop("hidden-modify-item-id", None)
        session.pop("hidden-detail-item-id", None)

        # DBから職員レコードを取得してテンプレートと共に返す.
        # RIDを指定された場合は, 一つだけレコードを取得する.
        if id is not None:
            stff_tmp = db_session.query(Staff).filter(Staff.id==id).first()
            db_session.close()
            if stff_tmp is not None:
                if len(str(stff_tmp.id)) > 6:
                    id_tmp = stff_tmp.id[0:6] + "..."
                else:
                    id_tmp = stff_tmp.id
                if len(stff_tmp.name) > 6:
                    nm_tmp = stff_tmp.name[0:6] + "..."
                else:
                    nm_tmp = stff_tmp.name
                if stff_tmp.sex == "man":
                    sex_tmp = "男性"
                elif stff_tmp.sex == "woman":
                    sex_tmp = "女性"
                else:
                    sex_tmp = "その他(分類不明)"
                if stff_tmp.blood_type == "type-a":
                    bld_typ_tmp = "A型"
                elif stff_tmp.blood_type == "type-b":
                    bld_typ_tmp = "B型"
                elif stff_tmp.blood_type == "type-ab":
                    bld_typ_tmp = "AB型"
                elif stff_tmp.blood_type == "type-o":
                    bld_typ_tmp = "O型"
                else:
                    bld_typ_tmp = "その他(分類不明)"
                brth_dt_tmp = se.etc.convert_datetime_string_to_display_style(stff_tmp.birth_date)
                stffs_fnl.append([id_tmp,
                                  nm_tmp,
                                  sex_tmp,
                                  bld_typ_tmp,
                                  brth_dt_tmp
                                 ])
                per_pg = consts.STAFF_PER_PAGE
                pg = request.args.get(get_page_parameter(), type=int, default=1)
                pg_dat = stffs_fnl[(pg - 1) * per_pg : pg * per_pg]
                pgntn = Pagination(page=pg,
                                   total=len(stffs_fnl),
                                   per_page=per_pg,
                                   css_framework=consts.PAGINATION_CSS
                                  )
                return render_template("show_staffs.html", page_data=pg_dat, pagination=pgntn)

            per_pg = consts.STAFF_PER_PAGE
            pg = request.args.get(get_page_parameter(), type=int, default=1)
            pg_dat = stffs_fnl[(pg - 1) * per_pg : pg * per_pg]
            pgntn = Pagination(page=pg,
                               total=len(stffs_fnl),
                               per_page=per_pg,
                               css_framework=consts.PAGINATION_CSS
                              )
            return render_template("show_staffs.html", page_data=pg_dat, pagination=pgntn)

        else:
            stffs_tmp = db_session.query(Staff).order_by(Staff.id).all()
            db_session.close()
            for stff_tmp in stffs_tmp:
                 if len(str(stff_tmp.id)) > 6:
                     id_tmp = stff_tmp.id[0:6] + "..."
                 else:
                     id_tmp = stff_tmp.id
                 if len(stff_tmp.name) > 6:
                     nm_tmp = stff_tmp.name[0:6] + "..."
                 else:
                     nm_tmp = stff_tmp.name
                 if stff_tmp.sex == "man":
                     sex_tmp = "男性"
                 elif stff_tmp.sex == "woman":
                     sex_tmp = "女性"
                 else:
                     sex_tmp = "その他(分類不明)"
                 if stff_tmp.blood_type == "type-a":
                     bld_typ_tmp = "A型"
                 elif stff_tmp.blood_type == "type-b":
                     bld_typ_tmp = "B型"
                 elif stff_tmp.blood_type == "type-ab":
                     bld_typ_tmp = "AB型"
                 elif stff_tmp.blood_type == "type-o":
                     bld_typ_tmp = "O型"
                 else:
                     bld_typ_tmp = "その他(分類不明)"
                 brth_dt_tmp = se.etc.convert_datetime_string_to_display_style(stff_tmp.birth_date)
                 stffs_fnl.append([id_tmp,
                                   nm_tmp,
                                   sex_tmp,
                                   bld_typ_tmp,
                                   brth_dt_tmp
                                  ])
            per_pg = consts.STAFF_PER_PAGE
            pg = request.args.get(get_page_parameter(), type=int, default=1)
            pg_dat = stffs_fnl[(pg - 1) * per_pg : pg * per_pg]
            pgntn = Pagination(page=pg,
                               total=len(stffs_fnl),
                               per_page=per_pg,
                               css_framework=consts.PAGINATION_CSS
                              )
            return render_template("show_staffs.html", page_data=pg_dat, pagination=pgntn)

    if request.method == "POST":
        # 直前に, GETメソッドで該当ページを取得しているかを調べる.
        # 取得していなければ, 強制的に現在ページへリダイレクトする.
        if session["referrer-page"] != "view.show_staffs":
            return redirect(url_for("view.show_staffs"))

        # フォームボタン群の中から, 押下されたボタンに応じたページへリダイレクトする.
        if request.form["hidden-modify-item-id"] != "":
            session["hidden-modify-item-id"] = request.form["hidden-modify-item-id"]
            return redirect(url_for("view.modify_staff"))
        if request.form["hidden-detail-item-id"] != "":
            session["hidden-detail-item-id"] = request.form["hidden-detail-item-id"]
            return redirect(url_for("view.detail_staff"))


# 「search_words」のためのビュー関数(=URLエンドポイント)を宣言・定義する.
@view.route("/search_words", methods=["GET", "POST"])
def search_words():
    # 関数内で使用する変数・オブジェクトを宣言・定義する.
    srch_wrd_form = SearchWordForm()

    # 該当のURLエンドポイントに入ったことをロギングする.
    rslt = se.etc.logging__info("view at /search_words")

    # ロギングに失敗したら, 例外を発生させる.
    if rslt == "NG":
        raise InternalServerError

    # セッション未作成ならば, ホーム画面のページヘリダイレクトする.
    if not session:
        return redirect(url_for("view.home"))

    # セッション失効or未初期化ならば, ホーム画面のページヘリダイレクトする.
    if "is-admin-enter" not in session:
        return redirect(url_for("view.home"))

    # 管理者未入室の状態ならば, ホーム画面のページヘリダイレクトする.
    if session["is-admin-enter"] == False:
        return redirect(url_for("view.home"))

    if request.method == "GET":
        # セッションに現在ページの情報を設定して,
        # Flaskフォームと共にテンプレートを返す.
        session["referrer-page"] = "view.search_words"

        # 検索に係るセッション項目(=検索条件)を削除してからテンプレートを返す.
        session.pop("id", None)
        session.pop("spell-and-header", None)
        session.pop("mean-and-content", None)
        session.pop("intent", None)
        session.pop("sentiment", None)
        session.pop("strength", None)
        session.pop("part-of-speech", None)
        session.pop("staff-name", None)
        session.pop("staff-kana-name", None)
        session.pop("created-at-begin", None)
        session.pop("created-at-end", None)
        session.pop("updated-at-begin", None)
        session.pop("updated-at-end", None)
        session.pop("sort-condition", None)
        session.pop("extract-condition", None)
        return render_template("search_words.html", form=srch_wrd_form)

    if request.method == "POST":
        # 直前に, GETメソッドで該当ページを取得しているかを調べる.
        # 取得していなければ, 強制的に現在ページへリダイレクトする.
        if session["referrer-page"] != "view.search_words":
            return render_template("search_words.html", form=srch_wrd_form)

        # フォームの取消ボタンが押下されたら, 空のフォームと共にテンプレートを返す.
        if srch_wrd_form.cancel.data:
            srch_wrd_form.id = ""
            srch_wrd_form.spell_and_header = ""
            srch_wrd_form.mean_and_content = ""
            srch_wrd_form.intent = ""
            srch_wrd_form.sentiment = ""
            srch_wrd_form.strength = ""
            srch_wrd_form.part_of_speech = ""
            srch_wrd_form.staff_name = ""
            srch_wrd_form.staff_kana_name = ""
            srch_wrd_form.created_at_begin = ""
            srch_wrd_form.created_at_end = ""
            srch_wrd_form.updated_at_begin = ""
            srch_wrd_form.updated_at_end = ""
            srch_wrd_form.sort_condition = "condition-1"
            srch_wrd_form.extract_condition = "condition-1"
            return render_template("search_words.html", form=srch_wrd_form)

        # 検索に係るセッション項目(=検索条件)を作成する.
        session["id"] = srch_wrd_form.id
        session["spell-and-header"] = srch_wrd_form.spell_and_header
        session["mean-and-content"] = srch_wrd_form.mean_and_content
        session["intent"] = srch_wrd_form.intent
        session["sentiment"] = srch_wrd_form.sentiment
        session["strength"] = srch_wrd_form.strength
        session["part-of-speech"] = srch_wrd_form.part_of_speech
        session["staff-name"] = srch_wrd_form.staff_name
        session["staff-kana-name"] = srch_wrd_form.staff_kana_name
        session["created-at-begin"] = srch_wrd_form.created_at_begin
        session["created-at-end"] = srch_wrd_form.created_at_end
        session["updated-at-begin"] = srch_wrd_form.updated_at_begin
        session["updated-at-end"] = srch_wrd_form.updated_at_end
        session["sort-condition"] = srch_wrd_form.sort_condition
        session["extract-condition"] = srch_wrd_form.extract_condition

        # 検索条件を保持したまま, 検索結果ページへリダイレクトする.
        return redirect(url_for("view.search_words_results"))


# 「search_themes」のためのビュー関数(=URLエンドポイント)を宣言・定義する.
@view.route("/search_themes", methods=["GET", "POST"])
def search_themes():
    # 関数内で使用する変数・オブジェクトを宣言・定義する.
    srch_thm_form = SearchThemeForm()

    # 該当のURLエンドポイントに入ったことをロギングする.
    rslt = se.etc.logging__info("view at /search_words")

    # ロギングに失敗したら, 例外を発生させる.
    if rslt == "NG":
        raise InternalServerError

    # セッション未作成ならば, ホーム画面のページヘリダイレクトする.
    if not session:
        return redirect(url_for("view.home"))

    # セッション失効or未初期化ならば, ホーム画面のページヘリダイレクトする.
    if "is-admin-enter" not in session:
        return redirect(url_for("view.home"))

    # 管理者未入室の状態ならば, ホーム画面のページヘリダイレクトする.
    if session["is-admin-enter"] == False:
        return redirect(url_for("view.home"))

    if request.method == "GET":
        # セッションに現在ページの情報を設定して,
        # Flaskフォームと共にテンプレートを返す.
        session["referrer-page"] = "view.search_themes"

        # 検索に係るセッション項目(=検索条件)を削除してからテンプレートを返す.
        session.pop("id", None)
        session.pop("spell-and-header", None)
        session.pop("mean-and-content", None)
        session.pop("category-tags", None)
        session.pop("staff-name", None)
        session.pop("staff-kana-name", None)
        session.pop("created-at-begin", None)
        session.pop("created-at-end", None)
        session.pop("updated-at-begin", None)
        session.pop("updated-at-end", None)
        session.pop("sort-condition", None)
        session.pop("extract-condition", None)
        return render_template("search_themes.html", form=srch_thm_form)

    if request.method == "POST":
        # 直前に, GETメソッドで該当ページを取得しているかを調べる.
        # 取得していなければ, 強制的に現在ページへリダイレクトする.
        if session["referrer-page"] != "view.search_themes":
            return render_template("search_themes.html", form=srch_thm_form)

        # フォームの取消ボタンが押下されたら, 空のフォームと共にテンプレートを返す.
        if srch_thm_form.cancel.data:
            srch_thm_form.id = ""
            srch_thm_form.spell_and_header = ""
            srch_thm_form.mean_and_content = ""
            srch_thm_form.category_tags = ""
            srch_thm_form.staff_name = ""
            srch_thm_form.staff_kana_name = ""
            srch_thm_form.created_at_begin = ""
            srch_thm_form.created_at_end = ""
            srch_thm_form.updated_at_begin = ""
            srch_thm_form.updated_at_end = ""
            srch_thm_form.sort_condition = "condition-1"
            srch_thm_form.extract_condition = "condition-1"
            return render_template("search_themes.html", form=srch_thm_form)

        # 検索に係るセッション項目(=検索条件)を作成する.
        session["id"] = srch_thm_form.id
        session["spell-and-header"] = srch_thm_form.spell_and_header
        session["mean-and-content"] = srch_thm_form.mean_and_content
        session["category-tags"] = srch_thm_form.category_tags
        session["staff-name"] = srch_thm_form.staff_name
        session["staff-kana-name"] = srch_thm_form.staff_kana_name
        session["created-at-begin"] = srch_thm_form.created_at_begin
        session["created-at-end"] = srch_thm_form.created_at_end
        session["updated-at-begin"] = srch_thm_form.updated_at_begin
        session["updated-at-end"] = srch_thm_form.updated_at_end
        session["sort-condition"] = srch_thm_form.sort_condition
        session["extract-condition"] = srch_thm_form.extract_condition

        # 検索条件を保持したまま, 検索結果ページへリダイレクトする.
        return redirect(url_for("view.search_themes_results"))


# 「search_categories」のためのビュー関数(=URLエンドポイント)を宣言・定義する.
@view.route("/search_categories", methods=["GET", "POST"])
def search_categories():
    # 関数内で使用する変数・オブジェクトを宣言・定義する.
    srch_ctgr_form = SearchCategoryForm()

    # 該当のURLエンドポイントに入ったことをロギングする.
    rslt = se.etc.logging__info("view at /search_words")

    # ロギングに失敗したら, 例外を発生させる.
    if rslt == "NG":
        raise InternalServerError

    # セッション未作成ならば, ホーム画面のページヘリダイレクトする.
    if not session:
        return redirect(url_for("view.home"))

    # セッション失効or未初期化ならば, ホーム画面のページヘリダイレクトする.
    if "is-admin-enter" not in session:
        return redirect(url_for("view.home"))

    # 管理者未入室の状態ならば, ホーム画面のページヘリダイレクトする.
    if session["is-admin-enter"] == False:
        return redirect(url_for("view.home"))

    if request.method == "GET":
        # セッションに現在ページの情報を設定して,
        # Flaskフォームと共にテンプレートを返す.
        session["referrer-page"] = "view.search_categories"

        # 検索に係るセッション項目(=検索条件)を削除してからテンプレートを返す.
        session.pop("id", None)
        session.pop("spell-and-header", None)
        session.pop("mean-and-content", None)
        session.pop("parent-category-tags", None)
        session.pop("sibling-category-tags", None)
        session.pop("child-category-tags", None)
        session.pop("staff-name", None)
        session.pop("staff-kana-name", None)
        session.pop("created-at-begin", None)
        session.pop("created-at-end", None)
        session.pop("updated-at-begin", None)
        session.pop("updated-at-end", None)
        session.pop("sort-condition", None)
        session.pop("extract-condition", None)
        return render_template("search_categories.html", form=srch_ctgr_form)

    if request.method == "POST":
        # 直前に, GETメソッドで該当ページを取得しているかを調べる.
        # 取得していなければ, 強制的に現在ページへリダイレクトする.
        if session["referrer-page"] != "view.search_categories":
            return render_template("search_categories.html", form=srch_ctgr_form)

        # フォームの取消ボタンが押下されたら, 空のフォームと共にテンプレートを返す.
        if srch_ctgr_form.cancel.data:
            srch_ctgr_form.id = ""
            srch_ctgr_form.spell_and_header = ""
            srch_ctgr_form.mean_and_content = ""
            srch_ctgr_form.parent_category_tags = ""
            srch_ctgr_form.sibling_category_tags = ""
            srch_ctgr_form.child_category_tags = ""
            srch_ctgr_form.staff_name = ""
            srch_ctgr_form.staff_kana_name = ""
            srch_ctgr_form.created_at_begin = ""
            srch_ctgr_form.created_at_end = ""
            srch_ctgr_form.updated_at_begin = ""
            srch_ctgr_form.updated_at_end = ""
            srch_ctgr_form.sort_condition = "condition-1"
            srch_ctgr_form.extract_condition = "condition-1"
            return render_template("search_categories.html", form=srch_ctgr_form)

        # 検索に係るセッション項目(=検索条件)を作成する.
        session["id"] = srch_ctgr_form.id
        session["spell-and-header"] = srch_ctgr_form.spell_and_header
        session["mean-and-content"] = srch_ctgr_form.mean_and_content
        session["parent-category-tags"] = srch_ctgr_form.parent_category_tags
        session["sibling-category-tags"] = srch_ctgr_form.sibling_category_tags
        session["child-category-tags"] = srch_ctgr_form.child_category_tags
        session["staff-name"] = srch_ctgr_form.staff_name
        session["staff-kana-name"] = srch_ctgr_form.staff_kana_name
        session["created-at-begin"] = srch_ctgr_form.created_at_begin
        session["created-at-end"] = srch_ctgr_form.created_at_end
        session["updated-at-begin"] = srch_ctgr_form.updated_at_begin
        session["updated-at-end"] = srch_ctgr_form.updated_at_end
        session["sort-condition"] = srch_ctgr_form.sort_condition
        session["extract-condition"] = srch_ctgr_form.extract_condition

        # 検索条件を保持したまま, 検索結果ページへリダイレクトする.
        return redirect(url_for("view.search_categories_results"))


# 「search_knowledges」のためのビュー関数(=URLエンドポイント)を宣言・定義する.
@view.route("/search_knowledges", methods=["GET", "POST"])
def search_knowledges():
    # 関数内で使用する変数・オブジェクトを宣言・定義する.
    srch_knwldg_form = SearchKnowledgeForm()

    # 該当のURLエンドポイントに入ったことをロギングする.
    rslt = se.etc.logging__info("view at /search_knowledges")

    # ロギングに失敗したら, 例外を発生させる.
    if rslt == "NG":
        raise InternalServerError

    # セッション未作成ならば, ホーム画面のページヘリダイレクトする.
    if not session:
        return redirect(url_for("view.home"))

    # セッション失効or未初期化ならば, ホーム画面のページヘリダイレクトする.
    if "is-admin-enter" not in session:
        return redirect(url_for("view.home"))

    # 管理者未入室の状態ならば, ホーム画面のページヘリダイレクトする.
    if session["is-admin-enter"] == False:
        return redirect(url_for("view.home"))

    if request.method == "GET":
        # セッションに現在ページの情報を設定して,
        # Flaskフォームと共にテンプレートを返す.
        session["referrer-page"] = "view.search_knowledges"

        # 検索に係るセッション項目(=検索条件)を削除してからテンプレートを返す.
        session.pop("id", None)
        session.pop("spell-and-header", None)
        session.pop("mean-and-content", None)
        session.pop("category-tags", None)
        session.pop("has-image", None)
        session.pop("has-sound", None)
        session.pop("has-video", None)
        session.pop("staff-name", None)
        session.pop("staff-kana-name", None)
        session.pop("created-at-begin", None)
        session.pop("created-at-end", None)
        session.pop("updated-at-begin", None)
        session.pop("updated-at-end", None)
        session.pop("sort-condition", None)
        session.pop("extract-condition", None)
        return render_template("search_knowledges.html", form=srch_knwldg_form)

    if request.method == "POST":
        # 直前に, GETメソッドで該当ページを取得しているかを調べる.
        # 取得していなければ, 強制的に現在ページへリダイレクトする.
        if session["referrer-page"] != "view.search_knowledges":
            return render_template("search_knowledges.html", form=srch_knwldg_form)

        # フォームの取消ボタンが押下されたら, 空のフォームと共にテンプレートを返す.
        if srch_knwldg_form.cancel.data:
            srch_knwldg_form.id = ""
            srch_knwldg_form.spell_and_header = ""
            srch_knwldg_form.mean_and_content = ""
            srch_knwldg_form.category_tags = ""
            srch_knwldg_form.has_image = ""
            srch_knwldg_form.has_sound = ""
            srch_knwldg_form.has_video = ""
            srch_knwldg_form.staff_name = ""
            srch_knwldg_form.staff_kana_name = ""
            srch_knwldg_form.created_at_begin = ""
            srch_knwldg_form.created_at_end = ""
            srch_knwldg_form.updated_at_begin = ""
            srch_knwldg_form.updated_at_end = ""
            srch_knwldg_form.sort_condition = "condition-1"
            srch_knwldg_form.extract_condition = "condition-1"
            return render_template("search_knowledges.html", form=srch_knwldg_form)

        # 検索に係るセッション項目(=検索条件)を作成する.
        session["id"] = srch_knwldg_form.id
        session["spell-and-header"] = srch_knwldg_form.spell_and_header
        session["mean-and-content"] = srch_knwldg_form.mean_and_content
        session["category-tags"] = srch_knwldg_form.category_tags
        session["has-image"] = srch_knwldg_form.has_image
        session["has-sound"] = srch_knwldg_form.has_sound
        session["has-video"] = srch_knwldg_form.has_video
        session["staff-name"] = srch_knwldg_form.staff_name
        session["staff-kana-name"] = srch_knwldg_form.staff_kana_name
        session["created-at-begin"] = srch_knwldg_form.created_at_begin
        session["created-at-end"] = srch_knwldg_form.created_at_end
        session["updated-at-begin"] = srch_knwldg_form.updated_at_begin
        session["updated-at-end"] = srch_knwldg_form.updated_at_end
        session["sort-condition"] = srch_knwldg_form.sort_condition
        session["extract-condition"] = srch_knwldg_form.extract_condition

        # 検索条件を保持したまま, 検索結果ページへリダイレクトする.
        return redirect(url_for("view.search_knowledges_results"))


# 「search_rules」のためのビュー関数(=URLエンドポイント)を宣言・定義する.
@view.route("/search_rules", methods=["GET", "POST"])
def search_rules():
    # 関数内で使用する変数・オブジェクトを宣言・定義する.
    srch_rl_form = SearchRuleForm()

    # 該当のURLエンドポイントに入ったことをロギングする.
    rslt = se.etc.logging__info("view at /search_rules")

    # ロギングに失敗したら, 例外を発生させる.
    if rslt == "NG":
        raise InternalServerError

    # セッション未作成ならば, ホーム画面のページヘリダイレクトする.
    if not session:
        return redirect(url_for("view.home"))

    # セッション失効or未初期化ならば, ホーム画面のページヘリダイレクトする.
    if "is-admin-enter" not in session:
        return redirect(url_for("view.home"))

    # 管理者未入室の状態ならば, ホーム画面のページヘリダイレクトする.
    if session["is-admin-enter"] == False:
        return redirect(url_for("view.home"))

    if request.method == "GET":
        # セッションに現在ページの情報を設定して,
        # Flaskフォームと共にテンプレートを返す.
        session["referrer-page"] = "view.search_rules"

        # 検索に係るセッション項目(=検索条件)を削除してからテンプレートを返す.
        session.pop("id", None)
        session.pop("spell-and-header", None)
        session.pop("mean-and-content", None)
        session.pop("category-tags", None)
        session.pop("inference-condition", None)
        session.pop("inference-result", None)
        session.pop("staff-name", None)
        session.pop("staff-kana-name", None)
        session.pop("created-at-begin", None)
        session.pop("created-at-end", None)
        session.pop("updated-at-begin", None)
        session.pop("updated-at-end", None)
        session.pop("sort-condition", None)
        session.pop("extract-condition", None)
        return render_template("search_rules.html", form=srch_rl_form)

    if request.method == "POST":
        # 直前に, GETメソッドで該当ページを取得しているかを調べる.
        # 取得していなければ, 強制的に現在ページへリダイレクトする.
        if session["referrer-page"] != "view.search_rules":
            return render_template("search_rules.html", form=srch_rl_form)

        # フォームの取消ボタンが押下されたら, 空のフォームと共にテンプレートを返す.
        if srch_rl_form.cancel.data:
            srch_rl_form.id = ""
            srch_rl_form.spell_and_header = ""
            srch_rl_form.mean_and_content = ""
            srch_rl_form.category_tags = ""
            srch_rl_form.inference_condition = ""
            srch_rl_form.inference_result = ""
            srch_rl_form.staff_name = ""
            srch_rl_form.staff_kana_name = ""
            srch_rl_form.created_at_begin = ""
            srch_rl_form.created_at_end = ""
            srch_rl_form.updated_at_begin = ""
            srch_rl_form.updated_at_end = ""
            srch_rl_form.sort_condition = "condition-1"
            srch_rl_form.extract_condition = "condition-1"
            return render_template("search_rules.html", form=srch_rl_form)

        # 検索に係るセッション項目(=検索条件)を作成する.
        session["id"] = srch_rl_form.id
        session["spell-and-header"] = srch_rl_form.spell_and_header
        session["mean-and-content"] = srch_rl_form.mean_and_content
        session["category-tags"] = srch_rl_form.category_tags
        session["inference-condition"] = srch_rl_form.inference_condition
        session["inference-result"] = srch_rl_form.inference_result
        session["staff-name"] = srch_rl_form.staff_name
        session["staff-kana-name"] = srch_rl_form.staff_kana_name
        session["created-at-begin"] = srch_rl_form.created_at_begin
        session["created-at-end"] = srch_rl_form.created_at_end
        session["updated-at-begin"] = srch_rl_form.updated_at_begin
        session["updated-at-end"] = srch_rl_form.updated_at_end
        session["sort-condition"] = srch_rl_form.sort_condition
        session["extract-condition"] = srch_rl_form.extract_condition

        # 検索条件を保持したまま, 検索結果ページへリダイレクトする.
        return redirect(url_for("view.search_rules_results"))


# 「search_reactions」のためのビュー関数(=URLエンドポイント)を宣言・定義する.
@view.route("/search_reactions", methods=["GET", "POST"])
def search_reactions():
    # 関数内で使用する変数・オブジェクトを宣言・定義する.
    srch_rctn_form = SearchReactionForm()

    # 該当のURLエンドポイントに入ったことをロギングする.
    rslt = se.etc.logging__info("view at /search_rules")

    # ロギングに失敗したら, 例外を発生させる.
    if rslt == "NG":
        raise InternalServerError

    # セッション未作成ならば, ホーム画面のページヘリダイレクトする.
    if not session:
        return redirect(url_for("view.home"))

    # セッション失効or未初期化ならば, ホーム画面のページヘリダイレクトする.
    if "is-admin-enter" not in session:
        return redirect(url_for("view.home"))

    # 管理者未入室の状態ならば, ホーム画面のページヘリダイレクトする.
    if session["is-admin-enter"] == False:
        return redirect(url_for("view.home"))

    if request.method == "GET":
        # セッションに現在ページの情報を設定して,
        # Flaskフォームと共にテンプレートを返す.
        session["referrer-page"] = "view.search_reactions"

        # 検索に係るセッション項目(=検索条件)を削除してからテンプレートを返す.
        session.pop("id", None)
        session.pop("spell-and-header", None)
        session.pop("mean-and-content", None)
        session.pop("staff-psychology", None)
        session.pop("scene-and-background", None)
        session.pop("message-example-from-staff", None)
        session.pop("message-example-from-application", None)
        session.pop("staff-name", None)
        session.pop("staff-kana-name", None)
        session.pop("created-at-begin", None)
        session.pop("created-at-end", None)
        session.pop("updated-at-begin", None)
        session.pop("updated-at-end", None)
        session.pop("sort-condition", None)
        session.pop("extract-condition", None)
        return render_template("search_reactions.html", form=srch_rctn_form)

    if request.method == "POST":
        # 直前に, GETメソッドで該当ページを取得しているかを調べる.
        # 取得していなければ, 強制的に現在ページへリダイレクトする.
        if session["referrer-page"] != "view.search_reactions":
            return render_template("search_reactions.html", form=srch_rctn_form)

        # フォームの取消ボタンが押下されたら, 空のフォームと共にテンプレートを返す.
        if srch_rctn_form.cancel.data:
            srch_rctn_form.id = ""
            srch_rctn_form.spell_and_header = ""
            srch_rctn_form.mean_and_content = ""
            srch_rctn_form.staff_psychology = ""
            srch_rctn_form.scene_and_background = ""
            srch_rctn_form.message_example_from_staff = ""
            srch_rctn_form.message_example_from_application = ""
            srch_rctn_form.staff_name = ""
            srch_rctn_form.staff_kana_name = ""
            srch_rctn_form.created_at_begin = ""
            srch_rctn_form.created_at_end = ""
            srch_rctn_form.updated_at_begin = ""
            srch_rctn_form.updated_at_end = ""
            srch_rctn_form.sort_condition = "condition-1"
            srch_rctn_form.extract_condition = "condition-1"
            return render_template("search_reactions.html", form=srch_rctn_form)

        # 検索に係るセッション項目(=検索条件)を作成する.
        session["id"] = srch_rctn_form.id
        session["spell-and-header"] = srch_rctn_form.spell_and_header
        session["mean-and-content"] = srch_rctn_form.mean_and_content
        session["staff-psychology"] = srch_rctn_form.staff_psychology
        session["scene-and-background"] = srch_rctn_form.scene_and_background
        session["message-example-from-staff"] = srch_rctn_form.message_example_from_staff
        session["message-example-from-application"] = srch_rctn_form.message_example_from_application
        session["staff-name"] = srch_rctn_form.staff_name
        session["staff-kana-name"] = srch_rctn_form.staff_kana_name
        session["created-at-begin"] = srch_rctn_form.created_at_begin
        session["created-at-end"] = srch_rctn_form.created_at_end
        session["updated-at-begin"] = srch_rctn_form.updated_at_begin
        session["updated-at-end"] = srch_rctn_form.updated_at_end
        session["sort-condition"] = srch_rctn_form.sort_condition
        session["extract-condition"] = srch_rctn_form.extract_condition

        # 検索条件を保持したまま, 検索結果ページへリダイレクトする.
        return redirect(url_for("view.search_reactions_results"))


# 「search_generates」のためのビュー関数(=URLエンドポイント)を宣言・定義する.
@view.route("/search_generates", methods=["GET", "POST"])
def search_generates():
    # 関数内で使用する変数・オブジェクトを宣言・定義する.
    srch_gen_form = SearchGenerateForm()

    # 該当のURLエンドポイントに入ったことをロギングする.
    rslt = se.etc.logging__info("view at /search_generates")

    # ロギングに失敗したら, 例外を発生させる.
    if rslt == "NG":
        raise InternalServerError

    # セッション未作成ならば, ホーム画面のページヘリダイレクトする.
    if not session:
        return redirect(url_for("view.home"))

    # セッション失効or未初期化ならば, ホーム画面のページヘリダイレクトする.
    if "is-admin-enter" not in session:
        return redirect(url_for("view.home"))

    # 管理者未入室の状態ならば, ホーム画面のページヘリダイレクトする.
    if session["is-admin-enter"] == False:
        return redirect(url_for("view.home"))

    if request.method == "GET":
        # セッションに現在ページの情報を設定して,
        # Flaskフォームと共にテンプレートを返す.
        session["referrer-page"] = "view.search_generates"

        # 検索に係るセッション項目(=検索条件)を削除してからテンプレートを返す.
        session.pop("id", None)
        session.pop("spell-and-header", None)
        session.pop("mean-and-content", None)
        session.pop("staff-name", None)
        session.pop("staff-kana-name", None)
        session.pop("created-at-begin", None)
        session.pop("created-at-end", None)
        session.pop("updated-at-begin", None)
        session.pop("updated-at-end", None)
        session.pop("sort-condition", None)
        session.pop("extract-condition", None)
        return render_template("search_generates.html", form=srch_gen_form)

    if request.method == "POST":
        # 直前に, GETメソッドで該当ページを取得しているかを調べる.
        # 取得していなければ, 強制的に現在ページへリダイレクトする.
        if session["referrer-page"] != "view.search_generates":
            return render_template("search_generates.html", form=srch_gen_form)

        # フォームの取消ボタンが押下されたら, 空のフォームと共にテンプレートを返す.
        if srch_gen_form.cancel.data:
            srch_gen_form.id = ""
            srch_gen_form.spell_and_header = ""
            srch_gen_form.mean_and_content = ""
            srch_gen_form.staff_name = ""
            srch_gen_form.staff_kana_name = ""
            srch_gen_form.created_at_begin = ""
            srch_gen_form.created_at_end = ""
            srch_gen_form.updated_at_begin = ""
            srch_gen_form.updated_at_end = ""
            srch_gen_form.sort_condition = "condition-1"
            srch_gen_form.extract_condition = "condition-1"
            return render_template("search_generates.html", form=srch_gen_form)

        # 検索に係るセッション項目(=検索条件)を作成する.
        session["id"] = srch_gen_form.id
        session["spell-and-header"] = srch_gen_form.spell_and_header
        session["mean-and-content"] = srch_gen_form.mean_and_content
        session["staff-name"] = srch_gen_form.staff_name
        session["staff-kana-name"] = srch_gen_form.staff_kana_name
        session["created-at-begin"] = srch_gen_form.created_at_begin
        session["created-at-end"] = srch_gen_form.created_at_end
        session["updated-at-begin"] = srch_gen_form.updated_at_begin
        session["updated-at-end"] = srch_gen_form.updated_at_end
        session["sort-condition"] = srch_gen_form.sort_condition
        session["extract-condition"] = srch_gen_form.extract_condition

        # 検索条件を保持したまま, 検索結果ページへリダイレクトする.
        return redirect(url_for("view.search_generates_results"))


# 「search_histories」のためのビュー関数(=URLエンドポイント)を宣言・定義する.
@view.route("/search_histories", methods=["GET", "POST"])
def search_histories():
    # 関数内で使用する変数・オブジェクトを宣言・定義する.
    srch_hist_form = SearchHistoryForm()

    # 該当のURLエンドポイントに入ったことをロギングする.
    rslt = se.etc.logging__info("view at /search_histories")

    # ロギングに失敗したら, 例外を発生させる.
    if rslt == "NG":
        raise InternalServerError

    # セッション未作成ならば, ホーム画面のページヘリダイレクトする.
    if not session:
        return redirect(url_for("view.home"))

    # セッション失効or未初期化ならば, ホーム画面のページヘリダイレクトする.
    if "is-admin-enter" not in session:
        return redirect(url_for("view.home"))

    # 管理者未入室の状態ならば, ホーム画面のページヘリダイレクトする.
    if session["is-admin-enter"] == False:
        return redirect(url_for("view.home"))

    if request.method == "GET":
        # セッションに現在ページの情報を設定して,
        # Flaskフォームと共にテンプレートを返す.
        session["referrer-page"] = "view.search_histories"

        # 検索に係るセッション項目(=検索条件)を削除してからテンプレートを返す.
        session.pop("id", None)
        session.pop("staff-message", None)
        session.pop("application-message", None)
        session.pop("staff-name", None)
        session.pop("staff-kana-name", None)
        session.pop("created-at-begin", None)
        session.pop("created-at-end", None)
        session.pop("updated-at-begin", None)
        session.pop("updated-at-end", None)
        session.pop("sort-condition", None)
        session.pop("extract-condition", None)
        return render_template("search_histories.html", form=srch_hist_form)

    if request.method == "POST":
        # 直前に, GETメソッドで該当ページを取得しているかを調べる.
        # 取得していなければ, 強制的に現在ページへリダイレクトする.
        if session["referrer-page"] != "view.search_histories":
            return render_template("search_histories.html", form=srch_hist_form)

        # フォームの取消ボタンが押下されたら, 空のフォームと共にテンプレートを返す.
        if srch_hist_form.cancel.data:
            srch_hist_form.id = ""
            srch_hist_form.staff_message = ""
            srch_hist_form.application_message = ""
            srch_hist_form.staff_name = ""
            srch_hist_form.staff_kana_name = ""
            srch_hist_form.created_at_begin = ""
            srch_hist_form.created_at_end = ""
            srch_hist_form.updated_at_begin = ""
            srch_hist_form.updated_at_end = ""
            srch_hist_form.sort_condition = "condition-1"
            srch_hist_form.extract_condition = "condition-1"
            return render_template("search_histories.html", form=srch_hist_form)

        # 検索に係るセッション項目(=検索条件)を作成する.
        session["id"] = srch_hist_form.id
        session["staff-message"] = srch_hist_form.staff_message
        session["application-message"] = srch_hist_form.application_message
        session["staff-name"] = srch_hist_form.staff_name
        session["staff-kana-name"] = srch_hist_form.staff_kana_name
        session["created-at-begin"] = srch_hist_form.created_at_begin
        session["created-at-end"] = srch_hist_form.created_at_end
        session["updated-at-begin"] = srch_hist_form.updated_at_begin
        session["updated-at-end"] = srch_hist_form.updated_at_end
        session["sort-condition"] = srch_hist_form.sort_condition
        session["extract-condition"] = srch_hist_form.extract_condition

        # 検索条件を保持したまま, 検索結果ページへリダイレクトする.
        return redirect(url_for("view.search_histories_results"))


# 「search_enters_or_exits」のためのビュー関数(=URLエンドポイント)を宣言・定義する.
@view.route("/search_enters_or_exits", methods=["GET", "POST"])
def search_enters_or_exits():
    # 関数内で使用する変数・オブジェクトを宣言・定義する.
    srch_entr_or_exit_form = SearchEnterOrExitForm()

    # 該当のURLエンドポイントに入ったことをロギングする.
    rslt = se.etc.logging__info("view at /enters_or_exits")

    # ロギングに失敗したら, 例外を発生させる.
    if rslt == "NG":
        raise InternalServerError

    # セッション未作成ならば, ホーム画面のページヘリダイレクトする.
    if not session:
        return redirect(url_for("view.home"))

    # セッション失効or未初期化ならば, ホーム画面のページヘリダイレクトする.
    if "is-admin-enter" not in session:
        return redirect(url_for("view.home"))

    # 管理者未入室の状態ならば, ホーム画面のページヘリダイレクトする.
    if session["is-admin-enter"] == False:
        return redirect(url_for("view.home"))

    if request.method == "GET":
        # セッションに現在ページの情報を設定して,
        # Flaskフォームと共にテンプレートを返す.
        session["referrer-page"] = "view.search_enters_or_exits"

        # 検索に係るセッション項目(=検索条件)を削除してからテンプレートを返す.
        session.pop("id", None)
        session.pop("reason", None)
        session.pop("enter-or-exit-at", None)
        session.pop("staff-name", None)
        session.pop("staff-kana-name", None)
        session.pop("created-at-begin", None)
        session.pop("created-at-end", None)
        session.pop("updated-at-begin", None)
        session.pop("updated-at-end", None)
        session.pop("sort-condition", None)
        session.pop("extract-condition", None)
        return render_template("search_enters_or_exits.html", form=srch_entr_or_exit_form)

    if request.method == "POST":
        # 直前に, GETメソッドで該当ページを取得しているかを調べる.
        # 取得していなければ, 強制的に現在ページへリダイレクトする.
        if session["referrer-page"] != "view.search_enters_or_exits":
            return render_template("search_enters_or_exits.html", form=srch_entr_or_exit_form)

        # フォームの取消ボタンが押下されたら, 空のフォームと共にテンプレートを返す.
        if srch_entr_or_exit_form.cancel.data:
            srch_entr_or_exit_form.id = ""
            srch_entr_or_exit_form.reason = ""
            srch_entr_or_exit_form.enter_or_exit_at = ""
            srch_entr_or_exit_form.staff_name = ""
            srch_entr_or_exit_form.staff_kana_name = ""
            srch_entr_or_exit_form.created_at_begin = ""
            srch_entr_or_exit_form.created_at_end = ""
            srch_entr_or_exit_form.updated_at_begin = ""
            srch_entr_or_exit_form.updated_at_end = ""
            srch_entr_or_exit_form.sort_condition = "condition-1"
            srch_entr_or_exit_form.extract_condition = "condition-1"
            return render_template("search_enters_or_exits.html", form=srch_entr_or_exit_form)

        # 検索に係るセッション項目(=検索条件)を作成する.
        session["id"] = srch_entr_or_exit_form.id
        session["reason"] = srch_entr_or_exit_form.reason
        session["enter-or-exit-at"] = srch_entr_or_exit_form.enter_or_exit_at
        session["staff-name"] = srch_entr_or_exit_form.staff_name
        session["staff-kana-name"] = srch_entr_or_exit_form.staff_kana_name
        session["created-at-begin"] = srch_entr_or_exit_form.created_at_begin
        session["created-at-end"] = srch_entr_or_exit_form.created_at_end
        session["updated-at-begin"] = srch_entr_or_exit_form.updated_at_begin
        session["updated-at-end"] = srch_entr_or_exit_form.updated_at_end
        session["sort-condition"] = srch_entr_or_exit_form.sort_condition
        session["extract-condition"] = srch_entr_or_exit_form.extract_condition

        # 検索条件を保持したまま, 検索結果ページへリダイレクトする.
        return redirect(url_for("view.search_enters_or_exits_results"))


# 「search_staffs」のためのビュー関数(=URLエンドポイント)を宣言・定義する.
@view.route("/search_staffs", methods=["GET", "POST"])
def search_staffs():
    # 関数内で使用する変数・オブジェクトを宣言・定義する.
    srch_stff_form = SearchStaffForm()

    # 該当のURLエンドポイントに入ったことをロギングする.
    rslt = se.etc.logging__info("view at /search_staffs")

    # ロギングに失敗したら, 例外を発生させる.
    if rslt == "NG":
        raise InternalServerError

    # セッション未作成ならば, ホーム画面のページヘリダイレクトする.
    if not session:
        return redirect(url_for("view.home"))

    # セッション失効or未初期化ならば, ホーム画面のページヘリダイレクトする.
    if "is-admin-enter" not in session:
        return redirect(url_for("view.home"))

    # 管理者未入室の状態ならば, ホーム画面のページヘリダイレクトする.
    if session["is-admin-enter"] == False:
        return redirect(url_for("view.home"))

    if request.method == "GET":
        # セッションに現在ページの情報を設定して,
        # Flaskフォームと共にテンプレートを返す.
        session["referrer-page"] = "view.search_staffs"

        # 検索に係るセッション項目(=検索条件)を削除してからテンプレートを返す.
        session.pop("id", None)
        session.pop("name", None)
        session.pop("kana-name", None)
        session.pop("sex", None)
        session.pop("blood-type", None)
        session.pop("birth-date", None)
        session.pop("created-at-begin", None)
        session.pop("created-at-end", None)
        session.pop("updated-at-begin", None)
        session.pop("updated-at-end", None)
        session.pop("sort-condition", None)
        session.pop("extract-condition", None)
        return render_template("search_staffs.html", form=srch_stff_form)

    if request.method == "POST":
        # 直前に, GETメソッドで該当ページを取得しているかを調べる.
        # 取得していなければ, 強制的に現在ページへリダイレクトする.
        if session["referrer-page"] != "view.search_staffs":
            return render_template("search_staffs.html", form=srch_stff_form)

        # フォームの取消ボタンが押下されたら, 空のフォームと共にテンプレートを返す.
        if srch_stff_form.cancel.data:
            srch_stff_form.id = ""
            srch_stff_form.name = ""
            srch_stff_form.kana_name = ""
            srch_stff_form.sex = ""
            srch_stff_form.blood_type = ""
            srch_stff_form.birth_date = ""
            srch_stff_form.created_at_begin = ""
            srch_stff_form.created_at_end = ""
            srch_stff_form.updated_at_begin = ""
            srch_stff_form.updated_at_end = ""
            srch_stff_form.sort_condition = "condition-1"
            srch_stff_form.extract_condition = "condition-1"
            return render_template("search_staffs.html", form=srch_stff_form)

        # 検索に係るセッション項目(=検索条件)を作成する.
        session["id"] = srch_stff_form.id
        session["name"] = srch_stff_form.name
        session["kana-name"] = srch_stff_form.kana_name
        session["sex"] = srch_stff_form.sex
        session["blood-type"] = srch_stff_form.blood_type
        session["birth-date"] = srch_stff_form.birth_date
        session["created-at-begin"] = srch_stff_form.created_at_begin
        session["created-at-end"] = srch_stff_form.created_at_end
        session["updated-at-begin"] = srch_stff_form.updated_at_begin
        session["updated-at-end"] = srch_stff_form.updated_at_end
        session["sort-condition"] = srch_stff_form.sort_condition
        session["extract-condition"] = srch_stff_form.extract_condition

        # 検索条件を保持したまま, 検索結果ページへリダイレクトする.
        return redirect(url_for("view.search_staffs_results"))


# 「search_words_results」のためのビュー関数(=URLエンドポイント)を宣言・定義する.
@view.route("/search_words_results", methods=["GET", "POST"])
def search_words_results():
    # 該当のURLエンドポイントに入ったことをロギングする.
    rslt = se.etc.logging__info("view at /search_words_results")

    # ロギングに失敗したら, 例外を発生させる.
    if rslt == "NG":
        raise InternalServerError

    # セッション未作成ならば, ホーム画面のページヘリダイレクトする.
    if not session:
        return redirect(url_for("view.home"))

    # セッション失効or未初期化ならば, ホーム画面のページヘリダイレクトする.
    if "is-admin-enter" not in session:
        return redirect(url_for("view.home"))

    # 管理者未入室の状態ならば, ホーム画面のページヘリダイレクトする.
    if session["is-admin-enter"] == False:
        return redirect(url_for("view.home"))

    if request.method == "GET":
        # セッションに現在ページの情報を設定する.
        session["referrer-page"] = "view.search_words_results"

        #@ ここで, モデルへの検索を行い, 検索結果をまとめて返す.
        return render_template("search_words_results.html")

    if request.method == "POST":
        # 直前に, GETメソッドで該当ページを取得しているかを調べる.
        # 取得していなければ, 強制的に現在ページへリダイレクトする.
        if session["referrer-page"] != "view.search_words_results":
            return redirect(url_for("view.search_words_results"))

        #@ ここで, フォーム内のボタンが押されたときの動作を実装する.
        #@ ※ここには, 仮のコードを記述しておいた...
        return redirect(url_for("view.search_words_results"))


# 「search_themes_results」のためのビュー関数(=URLエンドポイント)を宣言・定義する.
@view.route("/search_themes_results", methods=["GET", "POST"])
def search_themes_results():
    # 該当のURLエンドポイントに入ったことをロギングする.
    rslt = se.etc.logging__info("view at /search_themes_results")

    # ロギングに失敗したら, 例外を発生させる.
    if rslt == "NG":
        raise InternalServerError

    # セッション未作成ならば, ホーム画面のページヘリダイレクトする.
    if not session:
        return redirect(url_for("view.home"))

    # セッション失効or未初期化ならば, ホーム画面のページヘリダイレクトする.
    if "is-admin-enter" not in session:
        return redirect(url_for("view.home"))

    # 管理者未入室の状態ならば, ホーム画面のページヘリダイレクトする.
    if session["is-admin-enter"] == False:
        return redirect(url_for("view.home"))

    if request.method == "GET":
        # セッションに現在ページの情報を設定する.
        session["referrer-page"] = "view.search_themes_results"

        #@ ここで, モデルへの検索を行い, 検索結果をまとめて返す.
        return render_template("search_themes_results.html")

    if request.method == "POST":
        # 直前に, GETメソッドで該当ページを取得しているかを調べる.
        # 取得していなければ, 強制的に現在ページへリダイレクトする.
        if session["referrer-page"] != "view.search_themes_results":
            return redirect(url_for("view.search_themes_results"))

        #@ ここで, フォーム内のボタンが押されたときの動作を実装する.
        #@ ※ここには, 仮のコードを記述しておいた...
        return redirect(url_for("view.search_themes_results"))


# 「search_categories_results」のためのビュー関数(=URLエンドポイント)を宣言・定義する.
@view.route("/search_categories_results", methods=["GET", "POST"])
def search_categories_results():
    # 該当のURLエンドポイントに入ったことをロギングする.
    rslt = se.etc.logging__info("view at /search_categories_results")

    # ロギングに失敗したら, 例外を発生させる.
    if rslt == "NG":
        raise InternalServerError

    # セッション未作成ならば, ホーム画面のページヘリダイレクトする.
    if not session:
        return redirect(url_for("view.home"))

    # セッション失効or未初期化ならば, ホーム画面のページヘリダイレクトする.
    if "is-admin-enter" not in session:
        return redirect(url_for("view.home"))

    # 管理者未入室の状態ならば, ホーム画面のページヘリダイレクトする.
    if session["is-admin-enter"] == False:
        return redirect(url_for("view.home"))

    if request.method == "GET":
        # セッションに現在ページの情報を設定する.
        session["referrer-page"] = "view.search_categories_results"

        #@ ここで, モデルへの検索を行い, 検索結果をまとめて返す.
        return render_template("search_categories_results.html")

    if request.method == "POST":
        # 直前に, GETメソッドで該当ページを取得しているかを調べる.
        # 取得していなければ, 強制的に現在ページへリダイレクトする.
        if session["referrer-page"] != "view.search_categories_results":
            return redirect(url_for("view.search_categories_results"))

        #@ ここで, フォーム内のボタンが押されたときの動作を実装する.
        #@ ※ここには, 仮のコードを記述しておいた...
        return redirect(url_for("view.search_categories_results"))


# 「search_knowledges_results」のためのビュー関数(=URLエンドポイント)を宣言・定義する.
@view.route("/search_knowledges_results", methods=["GET", "POST"])
def search_knowledges_results():
    # 該当のURLエンドポイントに入ったことをロギングする.
    rslt = se.etc.logging__info("view at /search_knowledges_results")

    # ロギングに失敗したら, 例外を発生させる.
    if rslt == "NG":
        raise InternalServerError

    # セッション未作成ならば, ホーム画面のページヘリダイレクトする.
    if not session:
        return redirect(url_for("view.home"))

    # セッション失効or未初期化ならば, ホーム画面のページヘリダイレクトする.
    if "is-admin-enter" not in session:
        return redirect(url_for("view.home"))

    # 管理者未入室の状態ならば, ホーム画面のページヘリダイレクトする.
    if session["is-admin-enter"] == False:
        return redirect(url_for("view.home"))

    if request.method == "GET":
        # セッションに現在ページの情報を設定する.
        session["referrer-page"] = "view.search_knowledges_results"

        #@ ここで, モデルへの検索を行い, 検索結果をまとめて返す.
        return render_template("search_knowledges_results.html")

    if request.method == "POST":
        # 直前に, GETメソッドで該当ページを取得しているかを調べる.
        # 取得していなければ, 強制的に現在ページへリダイレクトする.
        if session["referrer-page"] != "view.search_knowledges_results":
            return redirect(url_for("view.search_knowledges_results"))

        #@ ここで, フォーム内のボタンが押されたときの動作を実装する.
        #@ ※ここには, 仮のコードを記述しておいた...
        return redirect(url_for("view.search_knowledges_results"))


# 「search_rules_results」のためのビュー関数(=URLエンドポイント)を宣言・定義する.
@view.route("/search_rules_results", methods=["GET", "POST"])
def search_rules_results():
    # 該当のURLエンドポイントに入ったことをロギングする.
    rslt = se.etc.logging__info("view at /search_rules_results")

    # ロギングに失敗したら, 例外を発生させる.
    if rslt == "NG":
        raise InternalServerError

    # セッション未作成ならば, ホーム画面のページヘリダイレクトする.
    if not session:
        return redirect(url_for("view.home"))

    # セッション失効or未初期化ならば, ホーム画面のページヘリダイレクトする.
    if "is-admin-enter" not in session:
        return redirect(url_for("view.home"))

    # 管理者未入室の状態ならば, ホーム画面のページヘリダイレクトする.
    if session["is-admin-enter"] == False:
        return redirect(url_for("view.home"))

    if request.method == "GET":
        # セッションに現在ページの情報を設定する.
        session["referrer-page"] = "view.search_rules_results"

        #@ ここで, モデルへの検索を行い, 検索結果をまとめて返す.
        return render_template("search_rules_results.html")

    if request.method == "POST":
        # 直前に, GETメソッドで該当ページを取得しているかを調べる.
        # 取得していなければ, 強制的に現在ページへリダイレクトする.
        if session["referrer-page"] != "view.search_rules_results":
            return redirect(url_for("view.search_rules_results"))

        #@ ここで, フォーム内のボタンが押されたときの動作を実装する.
        #@ ※ここには, 仮のコードを記述しておいた...
        return redirect(url_for("view.search_rules_results"))


# 「search_reactions_results」のためのビュー関数(=URLエンドポイント)を宣言・定義する.
@view.route("/search_reactions_results", methods=["GET", "POST"])
def search_reactions_results():
    # 該当のURLエンドポイントに入ったことをロギングする.
    rslt = se.etc.logging__info("view at /search_reactions_results")

    # ロギングに失敗したら, 例外を発生させる.
    if rslt == "NG":
        raise InternalServerError

    # セッション未作成ならば, ホーム画面のページヘリダイレクトする.
    if not session:
        return redirect(url_for("view.home"))

    # セッション失効or未初期化ならば, ホーム画面のページヘリダイレクトする.
    if "is-admin-enter" not in session:
        return redirect(url_for("view.home"))

    # 管理者未入室の状態ならば, ホーム画面のページヘリダイレクトする.
    if session["is-admin-enter"] == False:
        return redirect(url_for("view.home"))

    if request.method == "GET":
        # セッションに現在ページの情報を設定する.
        session["referrer-page"] = "view.search_reactions_results"

        #@ ここで, モデルへの検索を行い, 検索結果をまとめて返す.
        return render_template("search_reactions_results.html")

    if request.method == "POST":
        # 直前に, GETメソッドで該当ページを取得しているかを調べる.
        # 取得していなければ, 強制的に現在ページへリダイレクトする.
        if session["referrer-page"] != "view.search_reactions_results":
            return redirect(url_for("view.search_reactions_results"))

        #@ ここで, フォーム内のボタンが押されたときの動作を実装する.
        #@ ※ここには, 仮のコードを記述しておいた...
        return redirect(url_for("view.search_reactions_results"))


# 「search_generates_results」のためのビュー関数(=URLエンドポイント)を宣言・定義する.
@view.route("/search_generates_results", methods=["GET", "POST"])
def search_generates_results():
    # 該当のURLエンドポイントに入ったことをロギングする.
    rslt = se.etc.logging__info("view at /search_generates_results")

    # ロギングに失敗したら, 例外を発生させる.
    if rslt == "NG":
        raise InternalServerError

    # セッション未作成ならば, ホーム画面のページヘリダイレクトする.
    if not session:
        return redirect(url_for("view.home"))

    # セッション失効or未初期化ならば, ホーム画面のページヘリダイレクトする.
    if "is-admin-enter" not in session:
        return redirect(url_for("view.home"))

    # 管理者未入室の状態ならば, ホーム画面のページヘリダイレクトする.
    if session["is-admin-enter"] == False:
        return redirect(url_for("view.home"))

    if request.method == "GET":
        # セッションに現在ページの情報を設定する.
        session["referrer-page"] = "view.search_generates_results"

        #@ ここで, モデルへの検索を行い, 検索結果をまとめて返す.
        return render_template("search_generatess_results.html")

    if request.method == "POST":
        # 直前に, GETメソッドで該当ページを取得しているかを調べる.
        # 取得していなければ, 強制的に現在ページへリダイレクトする.
        if session["referrer-page"] != "view.search_generates_results":
            return redirect(url_for("view.search_generates_results"))

        #@ ここで, フォーム内のボタンが押されたときの動作を実装する.
        #@ ※ここには, 仮のコードを記述しておいた...
        return redirect(url_for("view.search_generates_results"))


# 「search_histories_results」のためのビュー関数(=URLエンドポイント)を宣言・定義する.
@view.route("/search_histories_results", methods=["GET", "POST"])
def search_histories_results():
    # 該当のURLエンドポイントに入ったことをロギングする.
    rslt = se.etc.logging__info("view at /search_histories_results")

    # ロギングに失敗したら, 例外を発生させる.
    if rslt == "NG":
        raise InternalServerError

    # セッション未作成ならば, ホーム画面のページヘリダイレクトする.
    if not session:
        return redirect(url_for("view.home"))

    # セッション失効or未初期化ならば, ホーム画面のページヘリダイレクトする.
    if "is-admin-enter" not in session:
        return redirect(url_for("view.home"))

    # 管理者未入室の状態ならば, ホーム画面のページヘリダイレクトする.
    if session["is-admin-enter"] == False:
        return redirect(url_for("view.home"))

    if request.method == "GET":
        # セッションに現在ページの情報を設定する.
        session["referrer-page"] = "view.search_histories_results"

        #@ ここで, モデルへの検索を行い, 検索結果をまとめて返す.
        return render_template("search_histories_results.html")

    if request.method == "POST":
        # 直前に, GETメソッドで該当ページを取得しているかを調べる.
        # 取得していなければ, 強制的に現在ページへリダイレクトする.
        if session["referrer-page"] != "view.search_histories_results":
            return redirect(url_for("view.search_histories_results"))

        #@ ここで, フォーム内のボタンが押されたときの動作を実装する.
        #@ ※ここには, 仮のコードを記述しておいた...
        return redirect(url_for("view.search_histories_results"))


# 「search_enters_or_exits_results」のためのビュー関数(=URLエンドポイント)を宣言・定義する.
@view.route("/search_enters_or_exits_results", methods=["GET", "POST"])
def search_enters_or_exits_results():
    # 該当のURLエンドポイントに入ったことをロギングする.
    rslt = se.etc.logging__info("view at /search_enters_or_exits_results")

    # ロギングに失敗したら, 例外を発生させる.
    if rslt == "NG":
        raise InternalServerError

    # セッション未作成ならば, ホーム画面のページヘリダイレクトする.
    if not session:
        return redirect(url_for("view.home"))

    # セッション失効or未初期化ならば, ホーム画面のページヘリダイレクトする.
    if "is-admin-enter" not in session:
        return redirect(url_for("view.home"))

    # 管理者未入室の状態ならば, ホーム画面のページヘリダイレクトする.
    if session["is-admin-enter"] == False:
        return redirect(url_for("view.home"))

    if request.method == "GET":
        # セッションに現在ページの情報を設定する.
        session["referrer-page"] = "view.search_enters_or_exits_results"

        #@ ここで, モデルへの検索を行い, 検索結果をまとめて返す.
        return render_template("search_enters_or_exits_results.html")

    if request.method == "POST":
        # 直前に, GETメソッドで該当ページを取得しているかを調べる.
        # 取得していなければ, 強制的に現在ページへリダイレクトする.
        if session["referrer-page"] != "view.search_enters_or_exits_results":
            return redirect(url_for("view.search_enters_or_exits_results"))

        #@ ここで, フォーム内のボタンが押されたときの動作を実装する.
        #@ ※ここには, 仮のコードを記述しておいた...
        return redirect(url_for("view.search_enters_or_exits_results"))


# 「search_staffs_results」のためのビュー関数(=URLエンドポイント)を宣言・定義する.
@view.route("/search_staffs_results", methods=["GET", "POST"])
def search_staffs_results():
    # 該当のURLエンドポイントに入ったことをロギングする.
    rslt = se.etc.logging__info("view at /search_staffs_results")

    # ロギングに失敗したら, 例外を発生させる.
    if rslt == "NG":
        raise InternalServerError

    # セッション未作成ならば, ホーム画面のページヘリダイレクトする.
    if not session:
        return redirect(url_for("view.home"))

    # セッション失効or未初期化ならば, ホーム画面のページヘリダイレクトする.
    if "is-admin-enter" not in session:
        return redirect(url_for("view.home"))

    # 管理者未入室の状態ならば, ホーム画面のページヘリダイレクトする.
    if session["is-admin-enter"] == False:
        return redirect(url_for("view.home"))

    if request.method == "GET":
        # セッションに現在ページの情報を設定する.
        session["referrer-page"] = "view.search_staffs_results"

        #@ ここで, モデルへの検索を行い, 検索結果をまとめて返す.
        return render_template("search_staffs_results.html")

    if request.method == "POST":
        # 直前に, GETメソッドで該当ページを取得しているかを調べる.
        # 取得していなければ, 強制的に現在ページへリダイレクトする.
        if session["referrer-page"] != "view.search_staffs_results":
            return redirect(url_for("view.search_staffs_results"))

        #@ ここで, フォーム内のボタンが押されたときの動作を実装する.
        #@ ※ここには, 仮のコードを記述しておいた...
        return redirect(url_for("view.search_staffs_results"))


# 「register_enter_or_exit」のためのビュー関数(=URLエンドポイント)を宣言・定義する.
@view.route("/register_enter_or_exit", methods=["GET", "POST"])
def register_enter_or_exit():
    # 関数内で使用する変数・オブジェクトを宣言・定義する.
    rgstr_entr_or_exit_form = RegisterEnterOrExitForm()

    # 該当のURLエンドポイントに入ったことをロギングする.
    rslt = se.etc.logging__info("view at /register_enter_or_exit")

    # ロギングに失敗したら, 例外を発生させる.
    if rslt == "NG":
        raise InternalServerError

    # セッション未作成ならば, ホーム画面のページヘリダイレクトする.
    if not session:
        return redirect(url_for("view.home"))

    # セッション失効or未初期化ならば, ホーム画面のページヘリダイレクトする.
    if "is-admin-enter" not in session:
        return redirect(url_for("view.home"))

    # 管理者未入室の状態ならば, ホーム画面のページヘリダイレクトする.
    if session["is-admin-enter"] == False:
        return redirect(url_for("view.home"))

    if request.method == "GET":
        # セッションに現在ページの情報を設定して, フォームと共にテンプレートを返す.
        session["referrer-page"] = "view.register_enter_or_exit"
        return render_template("register_enter_or_exit.html", form=rgstr_entr_or_exit_form)

    if request.method == "POST":
        # 直前に, GETメソッドで該当ページを取得しているかを調べる.
        # 取得していなければ, 強制的に現在ページへリダイレクトする.
        if session["referrer-page"] != "view.register_enter_or_exit":
            return redirect(url_for("view.register_enter_or_exit"))

        # フォームの取消ボタンが押下されたら, 空のフォームと共にテンプレートを返す.
        if rgstr_entr_or_exit_form.cancel.data:
            rgstr_entr_or_exit_form.staff_name.data = ""
            rgstr_entr_or_exit_form.staff_kana_name.data = ""
            rgstr_entr_or_exit_form.reason.data = ""
            rgstr_entr_or_exit_form.enter_or_exit_at.data = None
            rgstr_entr_or_exit_form.enter_or_exit_at_second.data = ""
            rgstr_entr_or_exit_form.is_hidden.data = ""
            rgstr_entr_or_exit_form.is_exclude.data = ""
            return render_template("register_enter_or_exit.html", form=rgstr_entr_or_exit_form)

        # flaskフォームに入力・記憶されている内容をバリデーションする.
        # 基準を満たさない場合は, 元のフォームと共にテンプレートを返す.
        if rgstr_entr_or_exit_form.staff_name.data == "":
            flash("職員名が入力されていません.")
            return render_template("register_enter_or_exit.html", form=rgstr_entr_or_exit_form, happen_error=True)
        if rgstr_entr_or_exit_form.staff_kana_name.data == "":
            flash("職員カナ名が入力されていません.")
            return render_template("register_enter_or_exit.html", form=rgstr_entr_or_exit_form, happen_error=True)
        if rgstr_entr_or_exit_form.reason.data == "":
            flash("入退理由が入力されていません.")
            return render_template("register_enter_or_exit.html", form=rgstr_entr_or_exit_form, happen_error=True)
        if rgstr_entr_or_exit_form.enter_or_exit_at.data is None:
            flash("入退日時が入力されていません.")
            return render_template("register_enter_or_exit.html", form=rgstr_entr_or_exit_form, happen_error=True)
        if not se.reg.check_numeric_in_en(rgstr_entr_or_exit_form.enter_or_exit_at_second.data):
            flash("入退日時-秒数が有効な数字ではありません.")
            return render_template("register_enter_or_exit.html", form=rgstr_entr_or_exit_form, happen_error=True)
        if ((int(rgstr_entr_or_exit_form.enter_or_exit_at_second.data) < 0) or
             (int(rgstr_entr_or_exit_form.enter_or_exit_at_second.data) > 59)):
            flash("入退日時-秒数が有効な範囲を超えています.")
            return render_template("register_enter_or_exit.html", form=rgstr_entr_or_exit_form, happen_error=True)
        if rgstr_entr_or_exit_form.is_hidden.data == "":
            flash("秘匿の是非が選択されていません.")
            return render_template("register_enter_or_exit.html", form=rgstr_entr_or_exit_form, happen_error=True)
        if rgstr_entr_or_exit_form.is_exclude.data == "":
            flash("非処理の是非が選択されていません.")
            return render_template("register_enter_or_exit.html", form=rgstr_entr_or_exit_form, happen_error=True)

        # 入退情報をレコードとして, DBに保存・登録する.
        crrnt_dttm = se.etc.retrieve_current_datetime_as_string("JST", True)
        if rgstr_entr_or_exit_form.enter_or_exit_at_second.data == "":
            crrnt_dttm_scnd = "00"
        elif ((int(rgstr_entr_or_exit_form.enter_or_exit_at_second.data) < 10) and
               (len(rgstr_entr_or_exit_form.enter_or_exit_at_second.data) == 1)):
            crrnt_dttm_scnd = "0" + rgstr_entr_or_exit_form.enter_or_exit_at_second.data
        else:
            crrnt_dttm_scnd = rgstr_entr_or_exit_form.enter_or_exit_at_second.data
        db_session.add(EnterOrExit(staff_name = rgstr_entr_or_exit_form.staff_name.data,
                                   staff_kana_name = rgstr_entr_or_exit_form.staff_kana_name.data,
                                   reason = rgstr_entr_or_exit_form.reason.data,
                                   enter_or_exit_at = rgstr_entr_or_exit_form.enter_or_exit_at.data,
                                   enter_or_exit_at_second = crrnt_dttm_scnd,
                                   created_at= crrnt_dttm,
                                   updated_at = crrnt_dttm,
                                   is_hidden = (True if rgstr_entr_or_exit_form.is_hidden.data == "yes" else False),
                                   is_exclude = (True if rgstr_entr_or_exit_form.is_exclude.data == "yes" else False)
        ))
        db_session.commit()
        db_session.close()

        # 完了メッセージを設定して, 空のフォームと共にテンプレートを返す.
        flash("入退を登録しました.")
        return render_template("register_enter_or_exit.html", form=rgstr_entr_or_exit_form)


# 「register_staff」のためのビュー関数(=URLエンドポイント)を宣言・定義する.
@view.route("/register_staff", methods=["GET", "POST"])
def register_staff():
    # 関数内で使用する変数・オブジェクトを宣言・定義する.
    rgstr_stff_form = RegisterStaffForm()

    # 該当のURLエンドポイントに入ったことをロギングする.
    rslt = se.etc.logging__info("view at /register_staff")

    # ロギングに失敗したら, 例外を発生させる.
    if rslt == "NG":
        raise InternalServerError

    # セッション未作成ならば, ホーム画面のページヘリダイレクトする.
    if not session:
        return redirect(url_for("view.home"))

    # セッション失効or未初期化ならば, ホーム画面のページヘリダイレクトする.
    if "is-admin-enter" not in session:
        return redirect(url_for("view.home"))

    # 管理者未入室の状態ならば, ホーム画面のページヘリダイレクトする.
    if session["is-admin-enter"] == False:
        return redirect(url_for("view.home"))

    if request.method == "GET":
        # セッションに現在ページの情報を設定して,フォームと共にテンプレートを返す.
        session["referrer-page"] = "view.register_staff"
        return render_template("register_staff.html", form=rgstr_stff_form)

    if request.method == "POST":
        # 直前に, GETメソッドで該当ページを取得しているかを調べる.
        # 取得していなければ, 強制的に現在ページへリダイレクトする.
        if session["referrer-page"] != "view.register_staff":
            return redirect(url_for("view.register_staff"))

        # フォームの取消ボタンが押下されたら, 空のフォームと共にテンプレートを返す.
        if rgstr_stff_form.cancel.data:
            rgstr_stff_form.name.data = ""
            rgstr_stff_form.kana_name.data = ""
            rgstr_stff_form.pass_word.data = ""
            rgstr_stff_form.sex.data = ""
            rgstr_stff_form.blood_type.data = ""
            rgstr_stff_form.birth_date.data = ""
            rgstr_stff_form.is_hidden.data = ""
            rgstr_stff_form.is_exclude.data = ""
            return render_template("register_staff.html", form=rgstr_stff_form)

        # 現時点で, 登録されている職員の数を確認して, それ以上登録できるかを判定する.
        # できなければ, エラーメッセージを設定して, フォームと共にテンプレートを返す.
        stffs = db_session.query(Staff).all()
        db_session.close()
        if len(stffs) >= consts.STAFF_NUMBER:
            flash("登録数の上限に達しているため, これ以上職員を登録できません.")
            return render_template("register_staff.html", form=rgstr_stff_form, happen_error=True)

        # 現時点で, 登録されている職員名を確認して, 重複せずに登録できるかを判定する.
        # できなければ, エラーメッセージを設定して, フォームと共にテンプレートを返す.
        for stff in stffs:
            if stff.name == rgstr_stff_form.name.data:
               flash("その職員名は, 既に使用・登録されています.")
               return render_template("register_staff.html", form=rgstr_stff_form, happen_error=True)
            if stff.kana_name == rgstr_stff_form.kana_name.data:
               flash("その職員カナ名は, 既に使用・登録されています.")
               return render_template("register_staff.html", form=rgstr_stff_form, happen_error=True)

        # flaskフォームに入力・記憶されている内容をバリデーションする.
        # 基準を満たさない場合, フォームと共にテンプレートを返す.
        if rgstr_stff_form.name.data == "":
            flash("職員名が入力されていません.")
            return render_template("register_staff.html", form=rgstr_stff_form, happen_error=True)
        if rgstr_stff_form.kana_name.data == "":
            flash("職員カナ名が入力されていません.")
            return render_template("register_staff.html", form=rgstr_stff_form, happen_error=True)
        if rgstr_stff_form.pass_word.data == "":
            flash("パスワードが入力されていません.")
            return render_template("register_staff.html", form=rgstr_stff_form, happen_error=True)
        if rgstr_stff_form.sex.data == "":
            flash("性別が選択されていません.")
            return render_template("register_staff.html", form=rgstr_stff_form, happen_error=True)
        if rgstr_stff_form.blood_type.data == "none":
            flash("血液型が選択されていません.")
            return render_template("register_staff.html", form=rgstr_stff_form, happen_error=True)
        if rgstr_stff_form.birth_date.data is None:
            flash("生年月日が選択されていません.")
            return render_template("register_staff.html", form=rgstr_stff_form, happen_error=True)
        if len(rgstr_stff_form.name.data) > consts.STAFF_NAME_LENGTH:
            flash("職員名は, " + str(consts.STAFF_NAME_LENGTH) + "文字以内にしてください.")
            return render_template("register_staff.html", form=rgstr_stff_form, happen_error=True)
        if len(rgstr_stff_form.kana_name.data) > consts.STAFF_KANA_NAME_LENGTH:
            flash("職員カナ名は, " + str(consts.STAFF_KANA_NAME_LENGTH) + "文字以内にしてください.")
            return render_template("register_staff.html", form=rgstr_stff_form, happen_error=True)
        if not se.reg.check_katakana_uppercase_in_ja(rgstr_stff_form.kana_name.data):
            flash("職員カナ名は, カタカナのみにしてください.")
            return render_template("register_staff.html", form=rgstr_stff_form, happen_error=True)
        if len(rgstr_stff_form.pass_word.data) > consts.PASSWORD_LENGTH:
            flash("パスワードは, " + str(consts.PASSWORD_LENGTH) + "文字以内にしてください.")
            return render_template("register_staff.html", form=rgstr_stff_form, happen_error=True)
        if not se.reg.check_alphabetic_numeric_and_symbol_with_space_in_en(rgstr_stff_form.pass_word.data):
            flash("パスワードは, 半角英数字と半角記号の組合せにしてください.")
            return render_template("register_staff.html", form=rgstr_stff_form, happen_error=True)
        if ((" " in rgstr_stff_form.name.data) or ("　" in rgstr_stff_form.name.data)):
            flash("職員名の一部として, 半角スペースと全角スペースは使用できません.")
            return render_template("register_staff.html", form=rgstr_stff_form, happen_error=True)
        if ((" " in rgstr_stff_form.kana_name.data) or ("　" in rgstr_stff_form.kana_name.data)):
            flash("職員カナ名の一部として, 半角スペースと全角スペースは使用できません.")
            return render_template("register_staff.html", form=rgstr_stff_form, happen_error=True)
        if ((" " in rgstr_stff_form.pass_word.data) or ("　" in rgstr_stff_form.pass_word.data)):
            flash("パスワードの一部として, 半角スペースと全角スペースは使用できません.")
            return render_template("register_staff.html", form=rgstr_stff_form, happen_error=True)

        drtn_in_dys__crit1 = se.etc.retrieve_timedelta_from_years(consts.STAFF_AGE_TOP)
        drtn_in_dys__crit2 = se.etc.retrieve_timedelta_from_years(consts.STAFF_AGE_BOTTOM)
        drtn_in_dys__brth_to_prsnt = se.etc.retrieve_timedelta_from_date_object(rgstr_stff_form.birth_date.data)

        if drtn_in_dys__brth_to_prsnt > drtn_in_dys__crit1:
            flash("本アプリは, " + str(consts.STAFF_AGE_TOP) + "歳超の方には提供しておりません.")
            return render_template("register_staff.html", form=rgstr_stff_form, happen_error=True)
        if drtn_in_dys__brth_to_prsnt < drtn_in_dys__crit2:
            flash("本アプリは, " + str(consts.STAFF_AGE_BOTTOM) + "歳未満の方には提供しておりません.")
            return render_template("register_staff.html", form=rgstr_stff_form, happen_error=True)
        if rgstr_stff_form.is_hidden.data == "":
            flash("秘匿の是非が入力されていません.")
            return render_template("register_staff.html", form=rgstr_stff_form, happen_error=True)
        if rgstr_stff_form.is_exclude.data == "":
            flash("非処理の是非が入力されていません.")
            return render_template("register_staff.html", form=rgstr_stff_form, happen_error=True)

        # 職員情報をレコードとして, DBに保存・登録する.
        crrnt_dttm = se.etc.retrieve_current_datetime_as_string("JST", True)
        db_session.add(Staff(name=rgstr_stff_form.name.data,
                             kana_name=rgstr_stff_form.kana_name.data,
                             pass_word=rgstr_stff_form.pass_word.data,
                             sex=rgstr_stff_form.sex.data,
                             blood_type=rgstr_stff_form.blood_type.data,
                             birth_date=rgstr_stff_form.birth_date.data,
                             created_at=crrnt_dttm,
                             updated_at=crrnt_dttm,
                             is_hidden=(True if rgstr_stff_form.is_hidden.data == "yes" else False),
                             is_exclude=(True if rgstr_stff_form.is_exclude.data == "yes" else False)
                             ))
        db_session.commit()
        db_session.close()

        # 完了メッセージを設定して, 空のフォームと共にテンプレートを返す.
        flash("職員を登録しました.")
        return render_template("register_staff.html", form=rgstr_stff_form)


# 「modify_word」のためのビュー関数(=URLエンドポイント)を宣言・定義する.
@view.route("/modify_word", methods=["GET", "POST"])
def modify_word():
    # 関数内で使用する変数・オブジェクトを宣言・定義する.
    mod_wrd_form = ModifyWordForm()

    # 該当のURLエンドポイントに入ったことをロギングする.
    rslt = se.etc.logging__info("view at /modify_word")

    # ロギングに失敗したら, 例外を発生させる.
    if rslt == "NG":
        raise InternalServerError

    # セッション未作成ならば, ホーム画面のページヘリダイレクトする.
    if not session:
        return redirect(url_for("view.home"))

    # セッション失効or未初期化ならば, ホーム画面のページヘリダイレクトする.
    if "is-admin-enter" not in session:
        return redirect(url_for("view.home"))

    # 管理者未入室の状態ならば, ホーム画面のページヘリダイレクトする.
    if session["is-admin-enter"] == False:
        return redirect(url_for("view.home"))

    # [show_knowledges][search_knowledges]ページを介さずに,
    # 不正アクセスされたら, 直前画面のページヘリダイレクトする.
    if "hidden-modify-item-id" not in session:
        return redirect(url_for(session["referrer-page"]))

    if request.method == "GET":
        # セッションに現在ページの情報を設定して,
        # Flaskフォームと共にテンプレートを返す.
        session["referrer-page"] = "view.admin_dashboard"

        # 指定IDの語句レコードをDBから取得する.
        wrd = (
            db_session.query(Word).filter(Word.id == session["hidden-modify-item-id"]).first()
        )
        db_session.close()

        # フォームにレコードの内容を複写して, フォームと共にテンプレートを返す.
        mod_wrd_form.spell_and_header.data = wrd.spell_and_header
        mod_wrd_form.mean_and_content.data = wrd.mean_and_content
        mod_wrd_form.intent.data = wrd.intent
        mod_wrd_form.sentiment.data = wrd.sentiment
        mod_wrd_form.strength.data = wrd.strength
        mod_wrd_form.part_of_speech.data = wrd.part_of_speech
        mod_wrd_form.is_hidden.data = ("yes" if wrd.is_hidden == True else "no")
        mod_wrd_form.is_exclude.data = ("yes" if wrd.is_exclude == True else "no")
        return render_template("modify_word.html", form=mod_wrd_form)

    if request.method == "POST":
        # 直前に, GETメソッドで該当ページを取得しているかを調べる.
        # 取得していなければ, 強制的に現在ページへリダイレクトする.
        if session["referrer-page"] != "view.modify_word":
            return redirect(url_for("view.modify_word"))

        # フォームの取消ボタンが押下されたら, 強制的に現在ページへリダイレクトする.
        if mod_wrd_form.cancel.data:
            return redirect(url_for("view.modify_word"))

        # flaskフォームに入力・記憶されている内容をバリデーションする.
        # 基準を満たさない場合, フォームと共にテンプレートを返す.
        if mod_wrd_form.spell_and_header.data == "":
            flash("綴り&見出しが入力されていません.")
            return render_template("modify_word.html", form=mod_wrd_form, happen_error=True)
        if mod_wrd_form.mean_and_content.data == "":
            flash("意味&内容が入力されていません.")
            return render_template("modify_word.html", form=mod_wrd_form, happen_error=True)
        if mod_wrd_form.intent.data == "":
            flash("意図が選択されていません.")
            return render_template("modify_word.html", form=mod_wrd_form, happen_error=True)
        if mod_wrd_form.sentiment.data == "":
            flash("感情が選択されていません.")
            return render_template("modify_word.html", form=mod_wrd_form, happen_error=True)
        if mod_wrd_form.strength.data == "":
            flash("強度が入力されていません.")
            return render_template("modify_word.html", form=mod_wrd_form, happen_error=True)
        if mod_wrd_form.part_of_speech.data == "":
            flash("品詞分類が選択されていません.")
            return render_template("modify_word.html", form=mod_wrd_form, happen_error=True)
        if mod_wrd_form.is_hidden.data == "":
            flash("秘匿の是非が選択されていません.")
            return render_template("modify_word.html", form=mod_wrd_form, happen_error=True)
        if mod_wrd_form.is_exclude.data == "":
            flash("非処理の是非が選択されていません.")
            return render_template("modify_word.html", form=mod_wrd_form, happen_error=True)

        # 指定IDの語句レコードを取得し, その内容を上書きしてから, DBセッションを閉じる.
        wrd = (
            db_session.query(Word).filter(Word.id == session["hidden-modify-item-id"]).first()
        )
        crrnt_dttm = se.etc.retrieve_current_datetime_as_string("JST", True)
        wrd.spell_and_header=mod_wrd_form.spell_and_header.data
        wrd.mean_and_content=mod_wrd_form.mean_and_content.data
        wrd.intent = mod_wrd_form.intent.data
        wrd.sentiment = mod_wrd_form.sentiment.data
        wrd.strength = mod_wrd_form.strength.data
        wrd.part_of_speech = mod_wrd_form.part_of_speech.data
        wrd.first_character = mod_wrd_form.spell_and_header.data[0]
        wrd.characters_count = len(mod_wrd_form.spell_and_header.data)
        wrd.staff_name=session["enter-name"]
        wrd.staff_kana_name=session["enter-kana-name"]
        wrd.updated_at=crrnt_dttm
        wrd.is_hidden=(True if mod_wrd_form.is_hidden == "yes" else False)
        wrd.is_exclude=(True if mod_wrd_form.is_exclude == "yes" else False)
        db_session.commit()
        db_session.close()

        # 完了メッセージを設定して, テンプレートを返す.
        flash("語句を変更しました.")
        return render_template("modify_word.html", form=mod_wrd_form)


# 「modify_theme」のためのビュー関数(=URLエンドポイント)を宣言・定義する.
@view.route("/modify_theme", methods=["GET", "POST"])
def modify_theme():
    # 関数内で使用する変数・オブジェクトを宣言・定義する.
    mod_thm_form = ModifyThemeForm()

    # 該当のURLエンドポイントに入ったことをロギングする.
    rslt = se.etc.logging__info("view at /modify_theme")

    # ロギングに失敗したら, 例外を発生させる.
    if rslt == "NG":
        raise InternalServerError

    # セッション未作成ならば, ホーム画面のページヘリダイレクトする.
    if not session:
        return redirect(url_for("view.home"))

    # セッション失効or未初期化ならば, ホーム画面のページヘリダイレクトする.
    if "is-admin-enter" not in session:
        return redirect(url_for("view.home"))

    # 管理者未入室の状態ならば, ホーム画面のページヘリダイレクトする.
    if session["is-admin-enter"] == False:
        return redirect(url_for("view.home"))

    # [show_themes][search_themes]ページを介さずに,
    # 不正アクセスされたら, 直前画面のページヘリダイレクトする.
    if "hidden-modify-item-id" not in session:
        return redirect(url_for(session["referrer-page"]))

    if request.method == "GET":
        # セッションに現在ページの情報を設定して,
        # Flaskフォームと共にテンプレートを返す.
        session["referrer-page"] = "view.modify_theme"

        # 指定IDの主題レコードをDBから取得する.
        thm = (
            db_session.query(Theme).filter(Theme.id == session["hidden-modify-item-id"]).first()
        )
        db_session.close()

        # フォームにレコードの内容を複写して, フォームと共にテンプレートを返す.
        mod_thm_form.spell_and_header.data = thm.spell_and_header
        mod_thm_form.mean_and_content.data = thm.mean_and_content
        mod_thm_form.category_tags.data = thm.category_tags
        mod_thm_form.is_hidden.data = ("yes" if thm.is_hidden == True else "no")
        mod_thm_form.is_exclude.data = ("yes" if thm.is_exclude == True else "no")
        return render_template("learn_theme.html", form=mod_thm_form)

    if request.method == "POST":
        # 直前に, GETメソッドで該当ページを取得しているかを調べる.
        # 取得していなければ, 強制的に現在ページへリダイレクトする.
        if session["referrer-page"] != "view.modify_theme":
            return redirect(url_for("view.modify_theme"))

        # フォームの取消ボタンが押下されたら, 強制的に現在ページへリダイレクトする.
        if mod_thm_form.cancel.data:
            return redirect(url_for("view.admin_dashboard"))

        # flaskフォームに入力・記憶されている内容をバリデーションする.
        # 基準を満たさない場合は, 元のフォームと共にテンプレートを返す.
        if mod_thm_form.spell_and_header.data == "":
            flash("綴り&見出しが入力されていません.")
            return render_template("modify_theme.html", form=mod_thm_form, happen_error=True)
        if mod_thm_form.mean_and_content.data == "":
            flash("意味&内容が入力されていません.")
            return render_template("modify_theme.html", form=mod_thm_form, happen_error=True)
        if mod_thm_form.category_tags.data == "":
            flash("分類タグが入力されていません.")
            return render_template("modify_theme.html", form=mod_thm_form, happen_error=True)
        if mod_thm_form.is_hidden.data == "":
            flash("秘匿の是非が選択されていません.")
            return render_template("modify_theme.html", form=mod_thm_form, happen_error=True)
        if mod_thm_form.is_exclude.data == "":
            flash("非処理の是非が選択されていません.")
            return render_template("modify_theme.html", form=mod_thm_form, happen_error=True)

        # 指定IDの主題レコードを取得し, その内容を上書きしてから, DBセッションを閉じる.
        thm = (
            db_session.query(Theme).filter(Theme.id == session["hidden-modify-item-id"]).first()
        )
        crrnt_dttm = se.etc.retrieve_current_datetime_as_string("JST", True)
        thm.spell_and_header = mod_thm_form.spell_and_header.data
        thm.mean_and_content = mod_thm_form.mean_and_content.data
        thm.category_tags = mod_thm_form.category_tags.data
        thm.updated_at = crrnt_dttm
        thm.is_hidden = (True if mod_thm_form.is_hidden.data == "Yes" else False)
        thm.is_exclude = (True if mod_thm_form.is_exclude.data == "Yes" else False)
        db_session.commit()
        db_session.close()

        # 完了メッセージを設定して, テンプレートを返す.
        flash("主題を変更しました.")
        return render_template("modify_theme.html", form=mod_thm_form)


# 「modify_category」のためのビュー関数(=URLエンドポイント)を宣言・定義する.
@view.route("/modify_category", methods=["GET", "POST"])
def modify_category():
    # 関数内で使用する変数・オブジェクトを宣言・定義する.
    mod_ctgr_form = ModifyCategoryForm()

    # 該当のURLエンドポイントに入ったことをロギングする.
    rslt = se.etc.logging__info("view at /modify_category")

    # ロギングに失敗したら, 例外を発生させる.
    if rslt == "NG":
        raise InternalServerError

    # セッション未作成ならば, ホーム画面のページヘリダイレクトする.
    if not session:
        return redirect(url_for("view.home"))

    # セッション失効or未初期化ならば, ホーム画面のページヘリダイレクトする.
    if "is-admin-enter" not in session:
        return redirect(url_for("view.home"))

    # 管理者未入室の状態ならば, ホーム画面のページヘリダイレクトする.
    if session["is-admin-enter"] == False:
        return redirect(url_for("view.home"))

    # [show_categories][search_categories]ページを介さずに,
    # 不正アクセスされたら, 直前画面のページヘリダイレクトする.
    if "hidden-modify-item-id" not in session:
        return redirect(url_for(session["referrer-page"]))

    if request.method == "GET":
        # セッションに現在ページの情報を設定して,
        # Flaskフォームと共にテンプレートを返す.
        session["referrer-page"] = "view.modify_category"

        # 指定IDの分類レコードをDBから取得する.
        ctgr = (
            db_session.query(Category).filter(Category.id == session["hidden-modify-item-id"]).first()
        )
        db_session.close()

        # フォームにレコードの内容を複写して, フォームと共にテンプレートを返す.
        mod_ctgr_form.spell_and_header.data = ctgr.spell_and_header
        mod_ctgr_form.mean_and_content.data = ctgr.mean_and_content
        mod_ctgr_form.parent_category_tags.data = ctgr.parent_category_tags
        mod_ctgr_form.sibling_category_tags.data = ctgr.sibling_category_tags
        mod_ctgr_form.child_category_tags.data = ctgr.child_category_tags
        mod_ctgr_form.is_hidden = ("yes" if ctgr.is_hidden == True else "no")
        mod_ctgr_form.is_exclude = ("yes" if ctgr.is_exclude == True else "no")
        return render_template("learn_category.html", form=mod_ctgr_form)

    if request.method == "POST":
        # 直前に, GETメソッドで該当ページを取得しているかを調べる.
        # 取得していなければ, 強制的に現在ページへリダイレクトする.
        if session["referrer-page"] != "view.modify_category":
            return redirect(url_for("view.modify_category"))

        # フォームの取消ボタンが押下されたら, 強制的に現在ページへリダイレクトする.
        if mod_ctgr_form.cancel.data:
            return redirect(url_for("view.admin_dashboard"))

        # flaskフォームに入力・記憶されている内容をバリデーションする.
        # 基準を満たさない場合は, 元のフォームと共にテンプレートを返す.
        if mod_ctgr_form.spell_and_header.data == "":
            flash("綴り&見出しが入力されていません.")
            return render_template("modify_category.html", form=mod_ctgr_form, happen_error=True)
        if mod_ctgr_form.mean_and_content.data == "":
            flash("意味&内容が入力されていません.")
            return render_template("modify_category.html", form=mod_ctgr_form, happen_error=True)
        if mod_ctgr_form.parent_category_tags.data == "":
            flash("親分類タグが入力されていません.")
            return render_template("modify_category.html", form=mod_ctgr_form, happen_error=True)
        if mod_ctgr_form.sibling_category_tags.data == "":
            flash("兄弟分類タグが入力されていません.")
            return render_template("modify_category.html", form=mod_ctgr_form, happen_error=True)
        if mod_ctgr_form.child_category_tags.data == "":
            flash("子分類タグが入力されていません.")
            return render_template("modify_category.html", form=mod_ctgr_form, happen_error=True)
        if mod_ctgr_form.is_hidden.data == "":
            flash("秘匿の是非が選択されていません.")
            return render_template("modify_word.html", form=mod_ctgr_form, happen_error=True)
        if mod_ctgr_form.is_exclude.data == "":
            flash("非処理の是非が選択されていません.")
            return render_template("modify_word.html", form=mod_ctgr_form, happen_error=True)

        # 指定IDの分類レコードを取得し, その内容を上書きしてから, DBセッションを閉じる.
        ctgr = (
            db_session.query(Category).filter(Category.id == session["hidden-modify-item-id"]).first()
        )
        crrnt_dttm = se.etc.retrieve_current_datetime_as_string("JST", True)
        ctgr.spell_and_header = mod_ctgr_form.spell_and_header.data
        ctgr.mean_and_content = mod_ctgr_form.mean_and_content.data
        ctgr.parent_category_tags = mod_ctgr_form.parent_category_tags.data
        ctgr.sibling_category_tags = mod_ctgr_form.sibling_category_tags.data
        ctgr.child_category_tags = mod_ctgr_form.child_category_tags.data
        ctgr.staff_name = session["enter-name"]
        ctgr.staff_kana_name = session["enter-kana-name"]
        ctgr.updated_at = crrnt_dttm
        ctgr.is_hidden = (True if mod_ctgr_form.is_hidden.data == "yes" else False)
        ctgr.is_exclude = (True if mod_ctgr_form.is_exclude.data == "yes" else False)
        db_session.commit()
        db_session.close()

        # 完了メッセージを設定して, テンプレートを返す.
        flash("分類を変更しました.")
        return render_template("modify_knowledge.html", form=mod_ctgr_form)


# 「modify_knowledge」のためのビュー関数(=URLエンドポイント)を宣言・定義する.
@view.route("/modify_knowledge", methods=["GET", "POST"])
def modify_knowledge():
    # 関数内で使用する変数・オブジェクトを宣言・定義する.
    mod_knwldg_form = ModifyKnowledgeForm()

    # 該当のURLエンドポイントに入ったことをロギングする.
    rslt = se.etc.logging__info("view at /modify_knowledge")

    # ロギングに失敗したら, 例外を発生させる.
    if rslt == "NG":
        raise InternalServerError

    # セッション未作成ならば, ホーム画面のページヘリダイレクトする.
    if not session:
        return redirect(url_for("view.home"))

    # セッション失効or未初期化ならば, ホーム画面のページヘリダイレクトする.
    if "is-admin-enter" not in session:
        return redirect(url_for("view.home"))

    # 管理者未入室の状態ならば, ホーム画面のページヘリダイレクトする.
    if session["is-admin-enter"] == False:
        return redirect(url_for("view.home"))

    # [show_knowledges][search_knowledges]ページを介さずに,
    # 不正アクセスされたら, 直前画面のページヘリダイレクトする.
    if "hidden-modify-item-id" not in session:
        return redirect(url_for(session["referrer-page"]))

    if request.method == "GET":
        # セッションに現在ページの情報を設定して,
        # Flaskフォームと共にテンプレートを返す.
        session["referrer-page"] = "view.modify_knowledge"

        # 指定IDの知識レコードをDBから取得する.
        knwldg = (
            db_session.query(Knowledge).filter(Knowledge.id == session["hidden-modify-item-id"]).first()
        )
        db_session.close()

        # フォームにレコードの内容を複写して, フォームと共にテンプレートを返す.
        mod_knwldg_form.spell_and_header.data = knwldg.spell_and_header
        mod_knwldg_form.mean_and_content.data = knwldg.mean_and_content
        mod_knwldg_form.category_tags.data = knwldg.category_tags
        mod_knwldg_form.staff_name.data = knwldg.staff_name
        mod_knwldg_form.staff_kana_name.data = knwldg.staff_kana_name
        mod_knwldg_form.is_hidden.data = ("yes" if knwldg.is_hidden == True else "no")
        mod_knwldg_form.is_exclude.data = ("yes" if knwldg.is_exclude == True else "no")
        return render_template("modify_knowledge.html", form=mod_knwldg_form,
                               archived_image_file_path=knwldg.archived_image_file_path,
                               archived_sound_file_path=knwldg.archived_sound_file_path,
                               archived_video_file_path=knwldg.archived_video_file_path
                              )

    if request.method == "POST":
        # 直前に, GETメソッドで該当ページを取得しているかを調べる.
        # 取得していなければ, 強制的に現在ページへリダイレクトする.
        if session["referrer-page"] != "view.modify_knowledge":
            return redirect(url_for("view.modify_knowledge"))

        # フォームの取消ボタンが押下されたら, 強制的に現在ページへリダイレクトする.
        if mod_knwldg_form.cancel.data:
            return redirect(url_for("view.admin_dashboard"))

        # flaskフォームに入力・記憶されている内容をバリデーションする.
        # 基準を満たさない場合は, 元のフォームと共にテンプレートを返す.
        if mod_knwldg_form.spell_and_header.data == "":
            flash("綴り&見出しが入力されていません.")
            return render_template("modify_knowledge.html", form=mod_knwldg_form, happen_error=True)
        if mod_knwldg_form.mean_and_content.data == "":
            flash("意味&内容が入力されていません.")
            return render_template("modify_knowledge.html", form=mod_knwldg_form, happen_error=True)
        if mod_knwldg_form.category_tags.data == "":
            flash("分類タグが入力されていません.")
            return render_template("modify_knowledge.html", form=mod_knwldg_form, happen_error=True)
        if mod_knwldg_form.is_hidden.data == "":
            flash("秘匿の是非が選択されていません.")
            return render_template("modify_knowledge.html", form=mod_knwldg_form, happen_error=True)
        if mod_knwldg_form.is_exclude.data == "":
            flash("非処理の是非が選択されていません.")
            return render_template("modify_knowledge.html", form=mod_knwldg_form, happen_error=True)

        # 指定IDの知識レコードを取得し, その内容を上書きしてから, DBセッションを閉じる.
        knwldg = (
            db_session.query(Knowledge).filter(Knowledge.id == session["hidden-modify-item-id"]).first()
        )

        # 指定IDの知識レコードを取得し, その内容を上書きしてから, DBセッションを閉じる.
        fl_lbl = se.etc.retrieve_current_datetime_as_file_label()
        crrnt_dttm = se.etc.retrieve_current_datetime_as_string("JST", True)
        archvd_img_fl_pth = se.etc.archive_file(mod_knwldg_form.attached_image_file.data, consts.ARCHIVE_IMAGE_PATH, fl_lbl)
        archvd_snd_fl_pth = se.etc.archive_file(mod_knwldg_form.attached_sound_file.data, consts.ARCHIVE_SOUND_PATH, fl_lbl)
        archvd_vdo_fl_pth = se.etc.archive_file(mod_knwldg_form.attached_video_file.data, consts.ARCHIVE_VIDEO_PATH, fl_lbl)
        knwldg.spell_and_header = mod_knwldg_form.spell_and_header.data
        knwldg.mean_and_content = mod_knwldg_form.mean_and_content.data
        knwldg.category_tags = mod_knwldg_form.category_tags.data
        knwldg.archived_image_file_path = archvd_img_fl_pth
        knwldg.archived_sound_file_path = archvd_snd_fl_pth
        knwldg.archived_video_file_path = archvd_vdo_fl_pth
        knwldg.updated_at = crrnt_dttm
        knwldg.is_hidden = (True if mod_knwldg_form.is_hidden.data == "yes" else False)
        knwldg.is_exclude = (True if mod_knwldg_form.is_exclude.data == "yes" else False)
        db_session.commit()
        db_session.close()

        # 完了メッセージを設定して, テンプレートを返す.
        flash("知識を変更しました.")
        return render_template("modify_knowledge.html", form=mod_knwldg_form,
                               archived_image_file_path=archvd_img_fl_pth,
                               archived_sound_file_path=archvd_snd_fl_pth,
                               archived_video_file_path=archvd_vdo_fl_pth
                              )


# 「modify_rule」のためのビュー関数(=URLエンドポイント)を宣言・定義する.
@view.route("/modify_rule", methods=["GET", "POST"])
def modify_rule():
    # 関数内で使用する変数・オブジェクトを宣言・定義する.
    mod_rl_form = ModifyRuleForm()

    # 該当のURLエンドポイントに入ったことをロギングする.
    rslt = se.etc.logging__info("view at /modify_rule")

    # ロギングに失敗したら, 例外を発生させる.
    if rslt == "NG":
        raise InternalServerError

    # セッション未作成ならば, ホーム画面のページヘリダイレクトする.
    if not session:
        return redirect(url_for("view.home"))

    # セッション失効or未初期化ならば, ホーム画面のページヘリダイレクトする.
    if "is-admin-enter" not in session:
        return redirect(url_for("view.home"))

    # 管理者未入室の状態ならば, ホーム画面のページヘリダイレクトする.
    if session["is-admin-enter"] == False:
        return redirect(url_for("view.home"))

    # [show_rules][search_rules]ページを介さずに,
    # 不正アクセスされたら, 直前画面のページヘリダイレクトする.
    if "hidden-modify-item-id" not in session:
        return redirect(url_for(session["referrer-page"]))

    if request.method == "GET":
        # セッションに現在ページの情報を設定して,
        # Flaskフォームと共にテンプレートを返す.
        session["referrer-page"] = "view.modify_rule"

        # 指定IDの規則レコードをDBから取得する.
        rl = (
        db_session.query(Rule).filter(Rule.id == session["hidden-modify-item-id"]).first()
        )
        db_session.close()

        # フォームにレコードの内容を複写して, フォームと共にテンプレートを返す.
        mod_rl_form.spell_and_header.data = rl.spell_and_header
        mod_rl_form.mean_and_content.data = rl.mean_and_content
        mod_rl_form.category_tags.data = rl.category_tags
        mod_rl_form.inference_condition.data = rl.inference_condition
        mod_rl_form.inference_result.data = rl.inference_result
        mod_rl_form.is_hidden.data = ("yes" if rl.is_hidden == True else "no")
        mod_rl_form.is_exclude.data = ("yes" if rl.is_exclude == True else "no")
        return render_template("modify_knowledge.html", form=mod_rl_form)

    if request.method == "POST":
        # 直前に, GETメソッドで該当ページを取得しているかを調べる.
        # 取得していなければ, 強制的に現在ページへリダイレクトする.
        if session["referrer-page"] != "view.modify_rule":
            return redirect(url_for("view.modify_rule"))

        # フォームの取消ボタンが押下されたら, 強制的に現在ページへリダイレクトする.
        if mod_rl_form.cancel.data:
            return redirect(url_for("view.admin_dashboard"))

        # flaskフォームに入力・記憶されている内容をバリデーションする.
        # 基準を満たさない場合は, 元のフォームと共にテンプレートを返す.
        if mod_rl_form.spell_and_header.data == "":
            flash("綴り&見出しが入力されていません.")
            return render_template("modify_rule.html", form=mod_rl_form, happen_error=True)
        if mod_rl_form.mean_and_content.data == "":
            flash("意味&内容が入力されていません.")
            return render_template("modify_rule.html", form=mod_rl_form, happen_error=True)
        if mod_rl_form.category_tags.data == "":
            flash("分類タグが入力されていません.")
            return render_template("modify_rule.html", form=mod_rl_form, happen_error=True)
        if mod_rl_form.inference_condition.data == "":
            flash("推論条件が入力されていません.")
            return render_template("modify_rule.html", form=mod_rl_form, happen_error=True)
        if mod_rl_form.inference_result.data == "":
            flash("推論結果が入力されていません.")
            return render_template("modify_rule.html", form=mod_rl_form, happen_error=True)
        if mod_rl_form.is_hidden.data == "":
            flash("秘匿の是非が選択されていません.")
            return render_template("modify_rule.html", form=mod_rl_form, happen_error=True)
        if mod_rl_form.is_exclude.data == "":
            flash("非処理の是非が選択されていません.")
            return render_template("modify_rule.html", form=mod_rl_form, happen_error=True)

        # 指定IDの規則レコードを取得し, その内容を上書きしてから, DBセッションを閉じる.
        rl = (
        db_session.query(Rule).filter(Rule.id == session["hidden-modify-item-id"]).first()
        )
        crrnt_dttm = se.etc.retrieve_current_datetime_as_string("JST", True)
        rl.spell_and_header = mod_rl_form.spell_and_header.data
        rl.mean_and_content = mod_rl_form.mean_and_content.data
        rl.category_tags = mod_rl_form.category_tags.data
        rl.inference_condition = mod_rl_form.inference_condition.data
        rl.inference_result = mod_rl_form.inference_result.data
        rl.updated_at = crrnt_dttm
        rl.is_hidden = (True if mod_rl_form.is_hidden.data == "yes" else False)
        rl.is_exclude = (True if mod_rl_form.is_exclude.data == "yes" else False)
        db_session.commit()
        db_session.close()

        # 完了メッセージを設定して, テンプレートを返す.
        flash("規則を変更しました.")
        return render_template("modify_rule.html", form=mod_rl_form)


# 「modify_reaction」のためのビュー関数(=URLエンドポイント)を宣言・定義する.
@view.route("/modify_reaction", methods=["GET", "POST"])
def modify_reaction():
    # 関数内で使用する変数・オブジェクトを宣言・定義する.
    mod_rctn_form = ModifyReactionForm()

    # 該当のURLエンドポイントに入ったことをロギングする.
    rslt = se.etc.logging__info("view at /modify_reaction")

    # ロギングに失敗したら, 例外を発生させる.
    if rslt == "NG":
        raise InternalServerError

    # セッション未作成ならば, ホーム画面のページヘリダイレクトする.
    if not session:
        return redirect(url_for("view.home"))

    # セッション失効or未初期化ならば, ホーム画面のページヘリダイレクトする.
    if "is-admin-enter" not in session:
        return redirect(url_for("view.home"))

    # 管理者未入室の状態ならば, ホーム画面のページヘリダイレクトする.
    if session["is-admin-enter"] == False:
        return redirect(url_for("view.home"))

    # [show_rules][search_rules]ページを介さずに,
    # 不正アクセスされたら, 直前画面のページヘリダイレクトする.
    if "hidden-modify-item-id" not in session:
        return redirect(url_for(session["referrer-page"]))

    if request.method == "GET":
        # セッションに現在ページの情報を設定して,
        # Flaskフォームと共にテンプレートを返す.
        session["referrer-page"] = "view.modify_reaction"

        # 指定IDの反応レコードをDBから取得する.
        rctn = (
        db_session.query(Reaction).filter(Reaction.id == session["hidden-modify-item-id"]).first()
        )
        db_session.close()

        # フォームにレコードの内容を複写して, フォームと共にテンプレートを返す.
        mod_rctn_form.spell_and_header.data = rctn.spell_and_header
        mod_rctn_form.mean_and_content.data = rctn.mean_and_content
        mod_rctn_form.staff_psychology.data = rctn.staff_psychology
        mod_rctn_form.scene_and_background.data = rctn.scene_and_background
        mod_rctn_form.message_example_from_staff.data = rctn.message_example_from_staff
        mod_rctn_form.message_example_from_application.data = rctn.message_example_from_application
        mod_rctn_form.is_hidden.data = ("yes" if rctn.is_hidden == True else "no")
        mod_rctn_form.is_exclude.data = ("yes" if rctn.is_exclude == True else "no")
        return render_template("modify_reaction.html", form=mod_rctn_form)

    if request.method == "POST":
        # 直前に, GETメソッドで該当ページを取得しているかを調べる.
        # 取得していなければ, 強制的に現在ページへリダイレクトする.
        if session["referrer-page"] != "view.modify_reaction":
            return redirect(url_for("view.modify_reaction"))

        # フォームの取消ボタンが押下されたら, 強制的に現在ページへリダイレクトする.
        if mod_rctn_form.cancel.data:
            return redirect(url_for("view.admin_dashboard"))

        # flaskフォームに入力・記憶されている内容をバリデーションする.
        # 基準を満たさない場合は, 元のフォームと共にテンプレートを返す.
        if mod_rctn_form.spell_and_header.data == "":
            flash("綴り&見出しが入力されていません.")
            return render_template("modify_reaction.html", form=mod_rctn_form, happen_error=True)
        if mod_rctn_form.mean_and_content.data == "":
            flash("意味&内容が入力されていません.")
            return render_template("modify_reaction.html", form=mod_rctn_form, happen_error=True)
        if mod_rctn_form.staff_psychology.data == "":
            flash("職員心理が入力されていません.")
            return render_template("modify_reaction.html", form=mod_rctn_form, happen_error=True)
        if mod_rctn_form.scene_and_background.data == "":
            flash("情景&背景が入力されていません.")
            return render_template("modify_reaction.html", form=mod_rctn_form, happen_error=True)
        if mod_rctn_form.message_example_from_staff.data == "":
            flash("職員メッセージ例が入力されていません.")
            return render_template("modify_reaction.html", form=mod_rctn_form, happen_error=True)
        if mod_rctn_form.message_example_from_application.data == "":
            flash("アプリメッセージ例が入力されていません.")
            return render_template("modify_reaction.html", form=mod_rctn_form, happen_error=True)
        if mod_rctn_form.is_hidden.data == "":
            flash("秘匿の是非が選択されていません.")
            return render_template("modify_reaction.html", form=mod_rctn_form, happen_error=True)
        if mod_rctn_form.is_exclude.data == "":
            flash("非処理の是非が選択されていません.")
            return render_template("modify_reaction.html", form=mod_rctn_form, happen_error=True)

        # 指定IDの反応レコードを取得し, その内容を上書きしてから, DBセッションを閉じる.
        rctn = (
        db_session.query(Reaction).filter(Reaction.id == session["hidden-modify-item-id"]).first()
        )
        crrnt_dttm = se.etc.retrieve_current_datetime_as_string("JST", True)
        rctn.spell_and_header = mod_rctn_form.spell_and_header.data
        rctn.mean_and_content = mod_rctn_form.mean_and_content.data
        rctn.staff_psychology = mod_rctn_form.staff_psychology.data
        rctn.scene_and_background = mod_rctn_form.scene_and_background.data
        rctn.message_example_from_staff = mod_rctn_form.message_example_from_staff.data
        rctn.message_example_from_application = mod_rctn_form.message_example_from_application.data
        rctn.updated_at = crrnt_dttm
        rctn.is_hidden = (True if mod_rctn_form.is_hidden.data == "yes" else False)
        rctn.is_exclude = (True if mod_rctn_form.is_exclude.data == "yes" else False)
        db_session.commit()
        db_session.close()

        # 完了メッセージを設定して, テンプレートを返す.
        flash("反応を変更しました.")
        return render_template("modify_reaction.html", form=mod_rctn_form)


# 「modify_enter_or_exit」のためのビュー関数(=URLエンドポイント)を宣言・定義する.
@view.route("/modify_enter_or_exit", methods=["GET", "POST"])
def modify_enter_or_exit():
    # 関数内で使用する変数・オブジェクトを宣言・定義する.
    mod_entr_or_exit_form = ModifyEnterOrExitForm()

    # 該当のURLエンドポイントに入ったことをロギングする.
    rslt = se.etc.logging__info("view at /modify_enter_or_exit")

    # ロギングに失敗したら, 例外を発生させる.
    if rslt == "NG":
        raise InternalServerError

    # セッション未作成ならば, ホーム画面のページヘリダイレクトする.
    if not session:
        return redirect(url_for("view.home"))

    # セッション失効or未初期化ならば, ホーム画面のページヘリダイレクトする.
    if "is-admin-enter" not in session:
        return redirect(url_for("view.home"))

    # 管理者未入室の状態ならば, ホーム画面のページヘリダイレクトする.
    if session["is-admin-enter"] == False:
        return redirect(url_for("view.home"))

    # [show_enters_or_exits][search_enters_or_exits]ページを介さずに,
    # 不正アクセスされたら, 直前画面のページヘリダイレクトする.
    if "hidden-modify-item-id" not in session:
        return redirect(url_for(session["referrer-page"]))

    if request.method == "GET":
        # セッションに現在ページの情報を設定して,
        # Flaskフォームと共にテンプレートを返す.
        session["referrer-page"] = "view.admin_dashboard"

        # 指定IDの入退レコードをDBから取得する.
        entr_or_exit = (
        db_session.query(EnterOrExit).filter(EnterOrExit.id == int(session["hidden-modify-item-id"])).first()
        )
        db_session.close()
    
        # フォームにレコードの内容を複写して, フォームと共にテンプレートを返す.
        mod_entr_or_exit_form.staff_name.data = entr_or_exit.staff_name
        mod_entr_or_exit_form.staff_kana_name.data = entr_or_exit.staff_kana_name
        mod_entr_or_exit_form.reason.data = entr_or_exit.reason
        mod_entr_or_exit_form.enter_or_exit_at.data = entr_or_exit.enter_or_exit_at
        mod_entr_or_exit_form.is_hidden.data = ("yes" if entr_or_exit.is_hidden == True else "no")
        mod_entr_or_exit_form.is_exclude.data = ("yes" if entr_or_exit.is_exclude == True else "no")
        return render_template("modify_enter_or_exit.html", form=mod_entr_or_exit_form)

    if request.method == "POST":
        # 直前に, GETメソッドで該当ページを取得しているかを調べる.
        # 取得していなければ, 強制的に現在ページへリダイレクトする.
        if session["referrer-page"] != "view.modify_enter_or_exit":
            return redirect(url_for("view.modify_enter_or_exit"))

        # フォームの取消ボタンが押下されたら, 強制的に現在ページへリダイレクトする.
        if mod_entr_or_exit_form.cancel.data:
            return redirect(url_for("view.modify_enter_or_exit"))

        # flaskフォームに入力・記憶されている内容をバリデーションする.
        # 基準を満たさない場合は, 元のフォームと共にテンプレートを返す.
        if mod_entr_or_exit_form.staff_name.data == "":
            flash("職員名が入力されていません.")
            return render_template("modify_rule.html", form=mod_entr_or_exit_form, happen_error=True)
        if mod_entr_or_exit_form.staff_kana_name.data == "":
            flash("職員カナ名が入力されていません.")
            return render_template("modify_rule.html", form=mod_entr_or_exit_form, happen_error=True)
        if mod_entr_or_exit_form.reason.data == "":
            flash("入退理由が入力されていません.")
            return render_template("modify_rule.html", form=mod_entr_or_exit_form, happen_error=True)
        if mod_entr_or_exit_form.enter_or_exit_at.data == "":
            flash("入退日時が入力されていません.")
            return render_template("modify_rule.html", form=mod_entr_or_exit_form, happen_error=True)
        if mod_entr_or_exit_form.is_hidden.data == "":
            flash("秘匿の是非が選択されていません.")
            return render_template("modify_rule.html", form=mod_entr_or_exit_form, happen_error=True)
        if mod_entr_or_exit_form.is_exclude.data == "":
            flash("非処理の是非が選択されていません.")
            return render_template("modify_rule.html", form=mod_entr_or_exit_form, happen_error=True)

        # 指定IDの入退レコードを取得し, その内容を上書きしてから, DBセッションを閉じる.
        entr_or_exit = (
        db_session.query(EnterOrExit).filter(EnterOrExit.id == int(session["hidden-modify-item-id"])).first()
        )
        crrnt_dttm = se.etc.retrieve_current_datetime_as_string("JST", True)
        entr_or_exit.staff_name = mod_entr_or_exit_form.staff_name.data
        entr_or_exit.staff_kana_name = mod_entr_or_exit_form.staff_kana_name.data
        entr_or_exit.reason = mod_entr_or_exit_form.reason.data
        entr_or_exit.enter_or_exit_at = mod_entr_or_exit_form.enter_or_exit_at.data
        entr_or_exit.updated_at = crrnt_dttm
        entr_or_exit.is_hidden = mod_entr_or_exit_form.is_hidden.data = (True if mod_entr_or_exit_form.is_hidden.data == "yes" else False)
        entr_or_exit.is_exclude = mod_entr_or_exit_form.is_exclude.data = (True if mod_entr_or_exit_form.is_exclude.data == "yes" else False)
        db_session.commit()
        db_session.close()

        # 完了メッセージを設定して, テンプレートを返す.
        flash("入退を変更しました.")
        return render_template("modify_enter_or_exit.html", form=mod_entr_or_exit_form)


# 「modify_staff」のためのビュー関数(=URLエンドポイント)を宣言・定義する.
@view.route("/modify_staff", methods=["GET", "POST"])
def modify_staff():
    # 関数内で使用する変数・オブジェクトを宣言・定義する.
    mod_stff_form = ModifyStaffForm()

    # 該当のURLエンドポイントに入ったことをロギングする.
    rslt = se.etc.logging__info("view at /modify_staff")

    # ロギングに失敗したら, 例外を発生させる.
    if rslt == "NG":
        raise InternalServerError

    # セッション未作成ならば, ホーム画面のページヘリダイレクトする.
    if not session:
        return redirect(url_for("view.home"))

    # セッション失効or未初期化ならば, ホーム画面のページヘリダイレクトする.
    if "is-admin-enter" not in session:
        return redirect(url_for("view.home"))

    # 管理者未入室の状態ならば, ホーム画面のページヘリダイレクトする.
    if session["is-admin-enter"] == False:
        return redirect(url_for("view.home"))

    # [show_staffs][search_staffs]ページを介さずに,
    # 不正アクセスされたら, 直前画面のページヘリダイレクトする.
    if "hidden-modify-item-id" not in session:
        return redirect(url_for(session["referrer-page"]))

    if request.method == "GET":
        # セッションに現在ページの情報を設定して,
        # Flaskフォームと共にテンプレートを返す.
        session["referrer-page"] = "view.modify_staff"

        # 指定IDの職員レコードをDBから取得する.
        stff = (
        db_session.query(Staff).filter(Staff.id == int(session["hidden-modify-item-id"])).first()
        )
        db_session.close()
    
        # フォームにレコードの内容を複写して, フォームと共にテンプレートを返す.
        mod_stff_form.name.data = stff.name
        mod_stff_form.kana_name.data = stff.kana_name
        mod_stff_form.pass_word.data = stff.pass_word
        mod_stff_form.sex.data = stff.sex
        mod_stff_form.blood_type.data = stff.blood_type
        mod_stff_form.birth_date.data = datetime.datetime.strptime(stff.birth_date, "%Y-%m-%d")
        mod_stff_form.is_hidden.data = ("yes" if stff.is_hidden == True else "no")
        mod_stff_form.is_exclude.data = ("yes" if stff.is_exclude == True else "no")
        return render_template("modify_staff.html", form=mod_stff_form)

    if request.method == "POST":
        # 直前に, GETメソッドで該当ページを取得しているかを調べる.
        # 取得していなければ, 強制的に現在ページへリダイレクトする.
        if session["referrer-page"] != "view.modify_staff":
            return redirect(url_for("view.modify_staff"))

        # フォームの取消ボタンが押下されたら, 強制的に現在ページへリダイレクトする.
        if mod_stff_form.cancel.data:
            return redirect(url_for("view.admin_dashboard"))

        # flaskフォームに入力・記憶されている内容をバリデーションする.
        # 基準を満たさない場合, フォームと共にテンプレートを返す.
        if mod_stff_form.name.data == "":
            flash("職員名が入力されていません.")
            return render_template("modify_staff.html", form=mod_stff_form, happen_error=True)
        if mod_stff_form.kana_name.data == "":
            flash("職員カナ名が入力されていません.")
            return render_template("modify_stafff.html", form=mod_stff_form, happen_error=True)
        if mod_stff_form.pass_word.data == "":
            flash("パスワードが入力されていません.")
            return render_template("modify_staff.html", form=mod_stff_form, happen_error=True)
        if mod_stff_form.sex.data == "":
            flash("性別が選択されていません.")
            return render_template("modify_staff.html", form=mod_stff_form, happen_error=True)
        if mod_stff_form.blood_type.data == "none":
            flash("血液型が選択されていません.")
            return render_template("modify_staff.html", form=mod_stff_form, happen_error=True)
        if mod_stff_form.birth_date.data is None:
            flash("生年月日が選択されていません.")
            return render_template("modify_staff.html", form=mod_stff_form, happen_error=True)
        if len(mod_stff_form.name.data) > consts.STAFF_NAME_LENGTH:
            flash("職員名は, " + str(consts.STAFF_NAME_LENGTH) + "文字以内にしてください.")
            return render_template("modify_staff.html", form=mod_stff_form, happen_error=True)
        if len(mod_stff_form.kana_name.data) > consts.STAFF_KANA_NAME_LENGTH:
            flash("職員カナ名は, " + str(consts.STAFF_KANA_NAME_LENGTH) + "文字以内にしてください.")
            return render_template("modify_staff.html", form=mod_stff_form, happen_error=True)
        if not se.reg.check_katakana_uppercase_in_ja(mod_stff_form.kana_name.data):
            flash("職員カナ名は, カタカナのみにしてください.")
            return render_template("modify_staff.html", form=mod_stff_form, happen_error=True)
        if len(mod_stff_form.pass_word.data) > consts.PASSWORD_LENGTH:
            flash("パスワードは, " + str(consts.PASSWORD_LENGTH) + "文字以内にしてください.")
            return render_template("modify_staff.html", form=mod_stff_form, happen_error=True)
        if not se.reg.check_alphabetic_numeric_and_symbol_with_space_in_en(mod_stff_form.pass_word.data):
            flash("パスワードは, 半角英数字と半角記号の組合せにしてください.")
            return render_template("modify_staff.html", form=mod_stff_form, happen_error=True)
        if ((" " in mod_stff_form.name.data) or ("　" in mod_stff_form.name.data)):
            flash("職員名の一部として, 半角スペースと全角スペースは使用できません.")
            return render_template("modify_staff.html", form=mod_stff_form, happen_error=True)
        if ((" " in mod_stff_form.kana_name.data) or ("　" in mod_stff_form.kana_name.data)):
            flash("職員カナ名の一部として, 半角スペースと全角スペースは使用できません.")
            return render_template("modify_staff.html", form=mod_stff_form, happen_error=True)
        if ((" " in mod_stff_form.pass_word.data) or ("　" in mod_stff_form.pass_word.data)):
            flash("パスワードの一部として, 半角スペースと全角スペースは使用できません.")
            return render_template("modify_staff.html", form=mod_stff_form, happen_error=True)

        drtn_in_dys__crit1 = se.etc.retrieve_timedelta_from_years(consts.STAFF_AGE_TOP)
        drtn_in_dys__crit2 = se.etc.retrieve_timedelta_from_years(consts.STAFF_AGE_BOTTOM)
        drtn_in_dys__brth_to_prsnt = se.etc.retrieve_timedelta_from_date_object(mod_stff_form.birth_date.data)

        if drtn_in_dys__brth_to_prsnt > drtn_in_dys__crit1:
            flash("本アプリは, " + str(consts.STAFF_AGE_TOP) + "歳超の方には提供しておりません.")
            return render_template("modify_staff.html", form=mod_stff_form, happen_error=True)
        if drtn_in_dys__brth_to_prsnt < drtn_in_dys__crit2:
            flash("本アプリは, " + str(consts.STAFF_AGE_BOTTOM) + "歳未満の方には提供しておりません.")
            return render_template("modify_staff.html", form=mod_stff_form, happen_error=True)
        if mod_stff_form.is_hidden.data == "":
            flash("秘匿の是非が入力されていません.")
            return render_template("modify_staff.html", form=mod_stff_form, happen_error=True)
        if mod_stff_form.is_exclude.data == "":
            flash("非処理の是非が入力されていません.")
            return render_template("modify_staff.html", form=mod_stff_form, happen_error=True)

        # 指定IDの職員レコードを取得し, その内容を上書きしてから, DBセッションを閉じる.
        stff = (
        db_session.query(Staff).filter(Staff.id == int(session["hidden-modify-item-id"])).first()
        )
        crrnt_dttm = se.etc.retrieve_current_datetime_as_string("JST", True)
        stff.name = mod_stff_form.name.data
        stff.kana_name = mod_stff_form.kana_name.data
        stff.pass_word = mod_stff_form.pass_word.data
        stff.sex = mod_stff_form.sex.data
        stff.blood_type = mod_stff_form.blood_type.data
        stff.birth_date = mod_stff_form.birth_date.data
        stff.created_at = crrnt_dttm
        stff.updated_at = crrnt_dttm
        stff.is_hidden = (True if mod_stff_form.is_hidden.data == "yes" else False)
        stff.is_exclude = (True if mod_stff_form.is_exclude.data == "yes" else False)
        db_session.commit()
        db_session.close()

        # 完了メッセージを設定して, テンプレートを返す.
        flash("職員を変更しました.")
        return render_template("modify_staff.html", form=mod_stff_form)


# 「detail_word」のためのビュー関数(=URLエンドポイント)を宣言・定義する.
@view.route("/detail_word", methods=["GET"])
def detail_word():
    dtl_wrd_form = DetailWordForm()

    # 該当のURLエンドポイントに入ったことをロギングする.
    rslt = se.etc.logging__info("view at /detail_word")

    # ロギングに失敗したら, 例外を発生させる.
    if rslt == "NG":
        raise InternalServerError

    # セッション未作成ならば, ホーム画面のページヘリダイレクトする.
    if not session:
        return redirect(url_for("view.home"))

    # セッション失効or未初期化ならば, ホーム画面のページヘリダイレクトする.
    if "is-admin-enter" not in session:
        return redirect(url_for("view.home"))

    # 管理者未入室の状態ならば, ホーム画面のページヘリダイレクトする.
    if session["is-admin-enter"] == False:
        return redirect(url_for("view.home"))

    # [show_words][search_words]ページを介さずに,
    # 不正アクセスされたら, 直前画面のページヘリダイレクトする.
    if "hidden-detail-item-id" not in session:
        return redirect(url_for("view.admin_dashboard"))

    if request.method == "GET":
        # セッションに現在ページの情報を設定して,
        # Flaskフォームと共にテンプレートを返す.
        session["referrer-page"] = "view.detail_word"

        # 指定IDの語句レコードをDBから取得する.
        wrd = db_session.query(Word).filter(Word.id == session["hidden-detail-item-id"]).first()
        db_session.close()

        # フォームにレコードの内容を複写して, フォームと共にテンプレートを返す.
        dtl_wrd_form.id.data = wrd.id
        dtl_wrd_form.spell_and_header.data = wrd.spell_and_header
        dtl_wrd_form.mean_and_content.data = wrd.mean_and_content
        dtl_wrd_form.concept_and_notion = wrd.concept_and_notion
        dtl_wrd_form.intent.data = wrd.intent
        dtl_wrd_form.sentiment.data = wrd.sentiment
        dtl_wrd_form.strength.data = wrd.strength
        dtl_wrd_form.part_of_speech.data = wrd.part_of_speech
        dtl_wrd_form.staff_name.data = wrd.staff_name
        dtl_wrd_form.staff_kana_name.data = wrd.staff_kana_name
        dtl_wrd_form.created_at.data = se.etc.convert_string_to_datetime_object_for_timestamp(wrd.created_at)
        dtl_wrd_form.updated_at.data = se.etc.convert_string_to_datetime_object_for_timestamp(wrd.updated_at)
        dtl_wrd_form.is_hidden.data = ("yes" if wrd.is_hidden == True else "no")
        dtl_wrd_form.is_exclude.data = ("yes" if wrd.is_exclude == True else "no")
        return render_template("detail_word.html", form=dtl_wrd_form)


# 「detail_theme」のためのビュー関数(=URLエンドポイント)を宣言・定義する.
@view.route("/detail_theme", methods=["GET"])
def detail_theme():
    dtl_thm_form = DetailThemeForm()

    # 該当のURLエンドポイントに入ったことをロギングする.
    rslt = se.etc.logging__info("view at /detail_theme")

    # ロギングに失敗したら, 例外を発生させる.
    if rslt == "NG":
        raise InternalServerError

    # セッション未作成ならば, ホーム画面のページヘリダイレクトする.
    if not session:
        return redirect(url_for("view.home"))

    # セッション失効or未初期化ならば, ホーム画面のページヘリダイレクトする.
    if "is-admin-enter" not in session:
        return redirect(url_for("view.home"))

    # 管理者未入室の状態ならば, ホーム画面のページヘリダイレクトする.
    if session["is-admin-enter"] == False:
        return redirect(url_for("view.home"))

    # [show_themes][search_themes]ページを介さずに,
    # 不正アクセスされたら, 直前画面のページヘリダイレクトする.
    if "hidden-detail-item-id" not in session:
        return redirect(url_for("view.admin_dashboard"))

    if request.method == "GET":
        # セッションに現在ページの情報を設定して,
        # Flaskフォームと共にテンプレートを返す.
        session["referrer-page"] = "view.detail_theme"

        # 指定IDの主題レコードをDBから取得する.
        thm = db_session.query(Theme).filter(Theme.id == session["hidden-detail-item-id"]).first()
        db_session.close()

        # フォームにレコードの内容を複写して, フォームと共にテンプレートを返す.
        dtl_thm_form.id.data = thm.id
        dtl_thm_form.spell_and_header.data = thm.spell_and_header
        dtl_thm_form.mean_and_content.data = thm.mean_and_content
        dtl_thm_form.concept_and_notion = thm.concept_and_notion
        dtl_thm_form.category_tags.data = thm.category_tags
        dtl_thm_form.staff_name.data = thm.staff_name
        dtl_thm_form.staff_kana_name.data = thm.staff_kana_name
        dtl_thm_form.created_at.data = se.etc.convert_string_to_datetime_object_for_timestamp(thm.created_at)
        dtl_thm_form.updated_at.data = se.etc.convert_string_to_datetime_object_for_timestamp(thm.updated_at)
        dtl_thm_form.is_hidden.data = ("yes" if thm.is_hidden == True else "no")
        dtl_thm_form.is_exclude.data = ("yes" if thm.is_exclude == True else "no")
        return render_template("detail_theme.html", form=dtl_thm_form)


# 「detail_category」のためのビュー関数(=URLエンドポイント)を宣言・定義する.
@view.route("/detail_category", methods=["GET"])
def detail_category():
    dtl_ctgr_form = DetailCategoryForm()

    # 該当のURLエンドポイントに入ったことをロギングする.
    rslt = se.etc.logging__info("view at /detail_category")

    # ロギングに失敗したら, 例外を発生させる.
    if rslt == "NG":
        raise InternalServerError

    # セッション未作成ならば, ホーム画面のページヘリダイレクトする.
    if not session:
        return redirect(url_for("view.home"))

    # セッション失効or未初期化ならば, ホーム画面のページヘリダイレクトする.
    if "is-admin-enter" not in session:
        return redirect(url_for("view.home"))

    # 管理者未入室の状態ならば, ホーム画面のページヘリダイレクトする.
    if session["is-admin-enter"] == False:
        return redirect(url_for("view.home"))

    # [show_categories][search_categories]ページを介さずに,
    # 不正アクセスされたら, 直前画面のページヘリダイレクトする.
    if "hidden-detail-item-id" not in session:
        return redirect(url_for("view.admin_dashboard"))

    if request.method == "GET":
        # セッションに現在ページの情報を設定して,
        # Flaskフォームと共にテンプレートを返す.
        session["referrer-page"] = "view.detail_category"

        # 指定IDの分類レコードをDBから取得する.
        ctgr = db_session.query(Category).filter(Category.id == session["hidden-detail-item-id"]).first()
        db_session.close()

        # フォームにレコードの内容を複写して, フォームと共にテンプレートを返す.
        dtl_ctgr_form.id.data = ctgr.id
        dtl_ctgr_form.spell_and_header.data = ctgr.spell_and_header
        dtl_ctgr_form.mean_and_content.data = ctgr.mean_and_content
        dtl_ctgr_form.concept_and_notion = ctgr.concept_and_notion
        dtl_ctgr_form.parent_category_tags.data = ctgr.parent_category_tags
        dtl_ctgr_form.sibling_category_tags.data = ctgr.sibling_category_tags
        dtl_ctgr_form.child_category_tags.data = ctgr.child_category_tags
        dtl_ctgr_form.staff_name.data = ctgr.staff_name
        dtl_ctgr_form.staff_kana_name.data = ctgr.staff_kana_name
        dtl_ctgr_form.created_at.data = se.etc.convert_string_to_datetime_object_for_timestamp(ctgr.created_at)
        dtl_ctgr_form.updated_at.data = se.etc.convert_string_to_datetime_object_for_timestamp(ctgr.updated_at)
        dtl_ctgr_form.is_hidden.data = ("yes" if ctgr.is_hidden == True else "no")
        dtl_ctgr_form.is_exclude.data = ("yes" if ctgr.is_exclude == True else "no")
        return render_template("detail_category.html", form=dtl_ctgr_form)


# 「detail_knowledge」のためのビュー関数(=URLエンドポイント)を宣言・定義する.
@view.route("/detail_knowledge", methods=["GET"])
def detail_knowledge():
    dtl_knwldg_form = DetailKnowledgeForm()

    # 該当のURLエンドポイントに入ったことをロギングする.
    rslt = se.etc.logging__info("view at /detail_knowledge")

    # ロギングに失敗したら, 例外を発生させる.
    if rslt == "NG":
        raise InternalServerError

    # セッション未作成ならば, ホーム画面のページヘリダイレクトする.
    if not session:
        return redirect(url_for("view.home"))

    # セッション失効or未初期化ならば, ホーム画面のページヘリダイレクトする.
    if "is-admin-enter" not in session:
        return redirect(url_for("view.home"))

    # 管理者未入室の状態ならば, ホーム画面のページヘリダイレクトする.
    if session["is-admin-enter"] == False:
        return redirect(url_for("view.home"))

    # [show_knowledges][search_knowledges]ページを介さずに,
    # 不正アクセスされたら, 直前画面のページヘリダイレクトする.
    if "hidden-detail-item-id" not in session:
        return redirect(url_for("view.admin_dashboard"))

    if request.method == "GET":
        # セッションに現在ページの情報を設定して,
        # Flaskフォームと共にテンプレートを返す.
        session["referrer-page"] = "view.detail_knowledge"

        # 指定IDの知識レコードをDBから取得する.
        knwldg = db_session.query(Knowledge).filter(Knowledge.id == session["hidden-detail-item-id"]).first()
        db_session.close()

        # フォームにレコードの内容を複写して, フォームと共にテンプレートを返す.
        dtl_knwldg_form.id.data = knwldg.id
        dtl_knwldg_form.spell_and_header.data = knwldg.spell_and_header
        dtl_knwldg_form.mean_and_content.data = knwldg.mean_and_content
        dtl_knwldg_form.concept_and_notion = knwldg.concept_and_notion
        dtl_knwldg_form.category_tags.data = knwldg.category_tags
        dtl_knwldg_form.archived_image_file_path.data = knwldg.archived_image_file_path
        dtl_knwldg_form.archived_sound_file_path.data = knwldg.archived_sound_file_path
        dtl_knwldg_form.archived_video_file_path.data = knwldg.archived_video_file_path
        dtl_knwldg_form.staff_name.data = knwldg.staff_name
        dtl_knwldg_form.staff_kana_name.data = knwldg.staff_kana_name
        dtl_knwldg_form.created_at.data = se.etc.convert_string_to_datetime_object_for_timestamp(knwldg.created_at)
        dtl_knwldg_form.updated_at.data = se.etc.convert_string_to_datetime_object_for_timestamp(knwldg.updated_at)
        dtl_knwldg_form.is_hidden.data = ("yes" if knwldg.is_hidden == True else "no")
        dtl_knwldg_form.is_exclude.data = ("yes" if knwldg.is_exclude == True else "no")
        return render_template("detail_knowledge.html", form=dtl_knwldg_form,
                                archived_image_file_path=knwldg.archived_image_file_path,
                                archived_sound_file_path=knwldg.archived_sound_file_path,
                                archived_video_file_path=knwldg.archived_video_file_path
                               )


# 「detail_rule」のためのビュー関数(=URLエンドポイント)を宣言・定義する.
@view.route("/detail_rule", methods=["GET"])
def detail_rule():
    dtl_rl_form = DetailRuleForm()

    # 該当のURLエンドポイントに入ったことをロギングする.
    rslt = se.etc.logging__info("view at /detail_rule")

    # ロギングに失敗したら, 例外を発生させる.
    if rslt == "NG":
        raise InternalServerError

    # セッション未作成ならば, ホーム画面のページヘリダイレクトする.
    if not session:
        return redirect(url_for("view.home"))

    # セッション失効or未初期化ならば, ホーム画面のページヘリダイレクトする.
    if "is-admin-enter" not in session:
        return redirect(url_for("view.home"))

    # 管理者未入室の状態ならば, ホーム画面のページヘリダイレクトする.
    if session["is-admin-enter"] == False:
        return redirect(url_for("view.home"))

    # [show_rules][search_rules]ページを介さずに,
    # 不正アクセスされたら, 直前画面のページヘリダイレクトする.
    if "hidden-detail-item-id" not in session:
        return redirect(url_for("view.admin_dashboard"))

    if request.method == "GET":
        # セッションに現在ページの情報を設定して,
        # Flaskフォームと共にテンプレートを返す.
        session["referrer-page"] = "view.detail_rule"

        # 指定IDの規則レコードをDBから取得する.
        rl = db_session.query(Rule).filter(Rule.id == session["hidden-detail-item-id"]).first()
        db_session.close()

        # フォームにレコードの内容を複写して, フォームと共にテンプレートを返す.
        dtl_rl_form.id.data = rl.id
        dtl_rl_form.spell_and_header.data = rl.spell_and_header
        dtl_rl_form.mean_and_content.data = rl.mean_and_content
        dtl_rl_form.concept_and_notion = rl.concept_and_notion
        dtl_rl_form.category_tags.data = rl.category_tags
        dtl_rl_form.inference_condition.data = rl.inference_condition
        dtl_rl_form.inference_result.data = rl.inference_result
        dtl_rl_form.staff_name.data = rl.staff_name
        dtl_rl_form.staff_kana_name.data = rl.staff_kana_name
        dtl_rl_form.created_at.data = se.etc.convert_string_to_datetime_object_for_timestamp(rl.created_at)
        dtl_rl_form.updated_at.data = se.etc.convert_string_to_datetime_object_for_timestamp(rl.updated_at)
        dtl_rl_form.is_hidden.data = ("yes" if rl.is_hidden == True else "no")
        dtl_rl_form.is_exclude.data = ("yes" if rl.is_exclude == True else "no")
        return render_template("detail_rule.html", form=dtl_rl_form)


# 「detail_reaction」のためのビュー関数(=URLエンドポイント)を宣言・定義する.
@view.route("/detail_reaction", methods=["GET"])
def detail_reaction():
    dtl_rl_form = DetailReactionForm()

    # 該当のURLエンドポイントに入ったことをロギングする.
    rslt = se.etc.logging__info("view at /detail_rule")

    # ロギングに失敗したら, 例外を発生させる.
    if rslt == "NG":
        raise InternalServerError

    # セッション未作成ならば, ホーム画面のページヘリダイレクトする.
    if not session:
        return redirect(url_for("view.home"))

    # セッション失効or未初期化ならば, ホーム画面のページヘリダイレクトする.
    if "is-admin-enter" not in session:
        return redirect(url_for("view.home"))

    # 管理者未入室の状態ならば, ホーム画面のページヘリダイレクトする.
    if session["is-admin-enter"] == False:
        return redirect(url_for("view.home"))

    # [show_reactions][search_reactions]ページを介さずに,
    # 不正アクセスされたら, 直前画面のページヘリダイレクトする.
    if "hidden-detail-item-id" not in session:
        return redirect(url_for("view.admin_dashboard"))

    if request.method == "GET":
        # セッションに現在ページの情報を設定して,
        # Flaskフォームと共にテンプレートを返す.
        session["referrer-page"] = "view.detail_reaction"

        # 指定IDの反応レコードをDBから取得する.
        rctn = db_session.query(Reaction).filter(Reaction.id == session["hidden-detail-item-id"]).first()
        db_session.close()

        # フォームにレコードの内容を複写して, フォームと共にテンプレートを返す.
        dtl_rl_form.id.data = rctn.id
        dtl_rl_form.spell_and_header.data = rctn.spell_and_header
        dtl_rl_form.mean_and_content.data = rctn.mean_and_content
        dtl_rl_form.concept_and_notion = rctn.concept_and_notion
        dtl_rl_form.staff_psychology.data = rctn.staff_psychology
        dtl_rl_form.scene_and_background.data = rctn.scene_and_background
        dtl_rl_form.message_example_from_staff.data = rctn.message_example_from_staff
        dtl_rl_form.message_example_from_application.data = rctn.message_example_from_application
        dtl_rl_form.staff_name.data = rctn.staff_name
        dtl_rl_form.staff_kana_name.data = rctn.staff_kana_name
        dtl_rl_form.created_at.data = se.etc.convert_string_to_datetime_object_for_timestamp(rctn.created_at)
        dtl_rl_form.updated_at.data = se.etc.convert_string_to_datetime_object_for_timestamp(rctn.updated_at)
        dtl_rl_form.is_hidden.data = ("yes" if rctn.is_hidden == True else "no")
        dtl_rl_form.is_exclude.data = ("yes" if rctn.is_exclude == True else "no")
        return render_template("detail_reaction.html", form=dtl_rl_form)


# 「detail_generate」のためのビュー関数(=URLエンドポイント)を宣言・定義する.
@view.route("/detail_generate", methods=["GET"])
def detail_generate():
    dtl_gen_form = DetailGenerateForm()

    # 該当のURLエンドポイントに入ったことをロギングする.
    rslt = se.etc.logging__info("view at /detail_generate")

    # ロギングに失敗したら, 例外を発生させる.
    if rslt == "NG":
        raise InternalServerError

    # セッション未作成ならば, ホーム画面のページヘリダイレクトする.
    if not session:
        return redirect(url_for("view.home"))

    # セッション失効or未初期化ならば, ホーム画面のページヘリダイレクトする.
    if "is-admin-enter" not in session:
        return redirect(url_for("view.home"))

    # 管理者未入室の状態ならば, ホーム画面のページヘリダイレクトする.
    if session["is-admin-enter"] == False:
        return redirect(url_for("view.home"))

    # [show_generates][search_generates]ページを介さずに,
    # 不正アクセスされたら, 直前画面のページヘリダイレクトする.
    if "hidden-detail-item-id" not in session:
        return redirect(url_for("view.admin_dashboard"))

    if request.method == "GET":
        # セッションに現在ページの情報を設定して,
        # Flaskフォームと共にテンプレートを返す.
        session["referrer-page"] = "view.detail_generate"

        # 指定IDの生成レコードをDBから取得する.
        gen = db_session.query(Generate).filter(Generate.id == session["hidden-detail-item-id"]).first()
        db_session.close()

        # フォームにレコードの内容を複写して, フォームと共にテンプレートを返す.
        dtl_gen_form.id.data = gen.id
        dtl_gen_form.spell_and_header.data = gen.spell_and_header
        dtl_gen_form.mean_and_content.data = gen.mean_and_content
        dtl_gen_form.generated_file_path.data = gen.generated_file_path
        dtl_gen_form.staff_name.data = gen.staff_name
        dtl_gen_form.staff_kana_name.data = gen.staff_kana_name
        dtl_gen_form.created_at.data = se.etc.convert_string_to_datetime_object_for_timestamp(gen.created_at)
        dtl_gen_form.updated_at.data = se.etc.convert_string_to_datetime_object_for_timestamp(gen.updated_at)
        dtl_gen_form.is_hidden.data = ("yes" if gen.is_hidden == True else "no")
        dtl_gen_form.is_exclude.data = ("yes" if gen.is_exclude == True else "no")
        return render_template("detail_generate.html", form=dtl_gen_form,
                               generated_file_path=gen.generated_file_path)


# 「detail_history」のためのビュー関数(=URLエンドポイント)を宣言・定義する.
@view.route("/detail_history", methods=["GET"])
def detail_history():
    dtl_hist_form = DetailHistoryForm()

    # 該当のURLエンドポイントに入ったことをロギングする.
    rslt = se.etc.logging__info("view at /detail_history")

    # ロギングに失敗したら, 例外を発生させる.
    if rslt == "NG":
        raise InternalServerError

    # セッション未作成ならば, ホーム画面のページヘリダイレクトする.
    if not session:
        return redirect(url_for("view.home"))

    # セッション失効or未初期化ならば, ホーム画面のページヘリダイレクトする.
    if "is-admin-enter" not in session:
        return redirect(url_for("view.home"))

    # 管理者未入室の状態ならば, ホーム画面のページヘリダイレクトする.
    if session["is-admin-enter"] == False:
        return redirect(url_for("view.home"))

    # [show_histories][search_histories]ページを介さずに,
    # 不正アクセスされたら, 直前画面のページヘリダイレクトする.
    if "hidden-detail-item-id" not in session:
        return redirect(url_for("view.admin_dashboard"))

    if request.method == "GET":
        # セッションに現在ページの情報を設定して,
        # Flaskフォームと共にテンプレートを返す.
        session["referrer-page"] = "view.detail_history"

        # 指定IDの履歴レコードをDBから取得する.
        hist = db_session.query(History).filter(History.id == session["hidden-detail-item-id"]).first()
        db_session.close()

        # フォームにレコードの内容を複写して, フォームと共にテンプレートを返す.
        dtl_hist_form.id.data = hist.id
        dtl_hist_form.staff_message.data = hist.staff_message
        dtl_hist_form.application_message.data = hist.application_message
        dtl_hist_form.staff_name.data = hist.staff_name
        dtl_hist_form.staff_kana_name.data = hist.staff_kana_name
        dtl_hist_form.created_at.data = se.etc.convert_string_to_datetime_object_for_timestamp(hist.created_at)
        dtl_hist_form.updated_at.data = se.etc.convert_string_to_datetime_object_for_timestamp(hist.updated_at)
        dtl_hist_form.is_hidden.data = ("yes" if hist.is_hidden == True else "no")
        dtl_hist_form.is_exclude.data = ("yes" if hist.is_exclude == True else "no")
        return render_template("detail_history.html", form=dtl_hist_form)


# 「detail_enter_or_exit」のためのビュー関数(=URLエンドポイント)を宣言・定義する.
@view.route("/detail_enter_or_exit", methods=["GET"])
def detail_enter_or_exit():
    dtl_entr_or_exit_form = DetailEnterOrExitForm()

    # 該当のURLエンドポイントに入ったことをロギングする.
    rslt = se.etc.logging__info("view at /detail_enter_or_exit")

    # ロギングに失敗したら, 例外を発生させる.
    if rslt == "NG":
        raise InternalServerError

    # セッション未作成ならば, ホーム画面のページヘリダイレクトする.
    if not session:
        return redirect(url_for("view.home"))

    # セッション失効or未初期化ならば, ホーム画面のページヘリダイレクトする.
    if "is-admin-enter" not in session:
        return redirect(url_for("view.home"))

    # 管理者未入室の状態ならば, ホーム画面のページヘリダイレクトする.
    if session["is-admin-enter"] == False:
        return redirect(url_for("view.home"))

    # [show_enters_or_exits][search_enters_or_exits]ページを介さずに,
    # 不正アクセスされたら, 直前画面のページヘリダイレクトする.
    if "hidden-detail-item-id" not in session:
        return redirect(url_for("view.admin_dashboard"))

    if request.method == "GET":
        # セッションに現在ページの情報を設定して,
        # Flaskフォームと共にテンプレートを返す.
        session["referrer-page"] = "view.detail_enter_or_exit"

        # 指定IDの入退レコードをDBから取得する.
        entr_or_exit = db_session.query(EnterOrExit).filter(EnterOrExit.id == session["hidden-detail-item-id"]).first()
        db_session.close()

        # フォームにレコードの内容を複写して, フォームと共にテンプレートを返す.
        dtl_entr_or_exit_form.id.data = entr_or_exit.id
        dtl_entr_or_exit_form.staff_name.data = entr_or_exit.staff_name
        dtl_entr_or_exit_form.staff_kana_name.data = entr_or_exit.staff_kana_name
        dtl_entr_or_exit_form.reason.data = entr_or_exit.reason
        dtl_entr_or_exit_form.enter_or_exit_at.data = entr_or_exit.enter_or_exit_at
        dtl_entr_or_exit_form.created_at.data = se.etc.convert_string_to_datetime_object_for_timestamp(entr_or_exit.created_at)
        dtl_entr_or_exit_form.updated_at.data = se.etc.convert_string_to_datetime_object_for_timestamp(entr_or_exit.updated_at)
        dtl_entr_or_exit_form.is_hidden.data = ("yes" if entr_or_exit.is_hidden == True else "no")
        dtl_entr_or_exit_form.is_exclude.data = ("yes" if entr_or_exit.is_exclude == True else "no")
        return render_template("detail_enter_or_exit.html", form=dtl_entr_or_exit_form)


# 「detail_staff」のためのビュー関数(=URLエンドポイント)を宣言・定義する.
@view.route("/detail_staff", methods=["GET"])
def detail_staff():
    dtl_stff_form = DetailStaffForm()

    # 該当のURLエンドポイントに入ったことをロギングする.
    rslt = se.etc.logging__info("view at /detail_staff")

    # ロギングに失敗したら, 例外を発生させる.
    if rslt == "NG":
        raise InternalServerError

    # セッション未作成ならば, ホーム画面のページヘリダイレクトする.
    if not session:
        return redirect(url_for("view.home"))

    # セッション失効or未初期化ならば, ホーム画面のページヘリダイレクトする.
    if "is-admin-enter" not in session:
        return redirect(url_for("view.home"))

    # 管理者未入室の状態ならば, ホーム画面のページヘリダイレクトする.
    if session["is-admin-enter"] == False:
        return redirect(url_for("view.home"))

    # [show_staffs][search_staffs]ページを介さずに,
    # 不正アクセスされたら, 直前画面のページヘリダイレクトする.
    if "hidden-detail-item-id" not in session:
        return redirect(url_for("view.admin_dashboard"))

    if request.method == "GET":
        # セッションに現在ページの情報を設定して,
        # Flaskフォームと共にテンプレートを返す.
        session["referrer-page"] = "view.detail_staff"

        # 指定IDの職員レコードをDBから取得する.
        stff = db_session.query(Staff).filter(Staff.id == session["hidden-detail-item-id"]).first()
        db_session.close()

        # フォームにレコードの内容を複写して, フォームと共にテンプレートを返す.
        dtl_stff_form.id.data = stff.id
        dtl_stff_form.name.data = stff.name
        dtl_stff_form.kana_name.data = stff.kana_name
        dtl_stff_form.pass_word.data = stff.pass_word
        dtl_stff_form.sex.data = stff.sex
        dtl_stff_form.blood_type.data = stff.blood_type
        dtl_stff_form.birth_date.data = se.etc.convert_string_to_datetime_object_for_eventday(stff.birth_date)
        dtl_stff_form.created_at.data = se.etc.convert_string_to_datetime_object_for_timestamp(stff.created_at)
        dtl_stff_form.updated_at.data = se.etc.convert_string_to_datetime_object_for_timestamp(stff.updated_at)
        dtl_stff_form.is_hidden.data = ("yes" if stff.is_hidden == True else "no")
        dtl_stff_form.is_exclude.data = ("yes" if stff.is_exclude == True else "no")
        return render_template("detail_staff.html", form=dtl_stff_form)


# 「import_words」のためのビュー関数(=URLエンドポイント)を宣言・定義する.
@view.route("/import_words", methods=["GET", "POST"])
def import_words():
    # 関数内で使用する変数・オブジェクトを宣言・定義する.
    sccss_cnt = 0
    fail_cnt = 0
    pass_cnt = 0
    imprt_wrd_form = ImportWordForm()

    # 該当のURLエンドポイントに入ったことをロギングする.
    rslt = se.etc.logging__info("view at /import_words")

    # ロギングに失敗したら, 例外を発生させる.
    if rslt == "NG":
        raise InternalServerError

    # セッション未作成ならば, ホーム画面のページヘリダイレクトする.
    if not session:
        return redirect(url_for("view.home"))

    # セッション失効or未初期化ならば, ホーム画面のページヘリダイレクトする.
    if "is-admin-enter" not in session:
        return redirect(url_for("view.home"))

    # 管理者未入室の状態ならば, ホーム画面のページヘリダイレクトする.
    if session["is-admin-enter"] == False:
        return redirect(url_for("view.home"))

    if request.method == "GET":
        # セッションに現在ページの情報を設定して,
        # Flaskフォームと共にテンプレートを返す.
        session["referrer-page"] = "view.import_words"
        return render_template("import_words.html", form=imprt_wrd_form)

    if request.method == "POST":
        # 直前に, GETメソッドで該当ページを取得しているかを調べる.
        # 取得していなければ, 強制的に現在ページへリダイレクトする.
        if session["referrer-page"] != "view.import_words":
            return redirect(url_for("view.import_words"))

        # フォームの取消ボタンが押されたら, 直前画面のページヘリダイレクトする.
        if imprt_wrd_form.cancel.data:
            return redirect(url_for("view.admin_dashboard"))

        # フォームと共に送信されたファイルを取得して, 名前を安全な形式に変更する.
        xml_fl = imprt_wrd_form.imported_file.data
        fl_nm = secure_filename(xml_fl.filename)
        if fl_nm == "":
            flash("語句ファイルが選択されていません.")
            return render_template("import_words.html", form=imprt_wrd_form)

        # ファイルを一旦, 一時領域に保存してから, その内容を読み取る.
        xml_fl.save(os.path.join(consts.TEMPORARY_PATH, fl_nm))
        xml_fl = open(os.path.join(consts.TEMPORARY_PATH, fl_nm), 'r', encoding='UTF-8')

        # 不正なデータがないことを確認した上で, 
        # DBテーブルにレコードを転写・複写する.
        tree = ET.parse(xml_fl)
        root = tree.getroot()
        for child in root:
            if child.find("is-exclude").text == "はい":
                pass_cnt += 1
                continue
            try:
                   crrnt_dttm = se.etc.retrieve_current_datetime_as_string("JST", True)
                   db_session.add(Word(spell_and_header=child.find("spell-and-header").text,
                                       mean_and_content=child.find("mean-and-content").text,
                                       intent=child.find("intent").text,
                                       sentiment=child.find("sentiment").text,
                                       strength=child.find("strength").text,
                                       first_character=child.find("spell-and-header").text[0],
                                       characters_count=len(child.find("spell-and-header").text),
                                       staff_name=child.find("staff-name").text,
                                       staff_kana_name=child.find("staff-kana-name").text,
                                       created_at=child.find("created-at").text,
                                       updated_at=crrnt_dttm,
                                       is_hidden=child.find("is-hidden").text,
                                       is_exclude="no"
                                      ))
                   db_session.commit()
                   sccss_cnt += 1
                   continue

            except AttributeError:
                   sccss_cnt += 1
                   fail_cnt += 1
                   continue
            finally:
                   db_session.close()

        # 完了メッセージを設定して, テンプレートを返す.
        flash("語句ファイルの取込を実行しました.")
        flash("成功数:" + str(sccss_cnt) + ", " + "失敗数:" + str(fail_cnt) + ", " + "棄却数:" + str(pass_cnt) + ", " + "総件数:" + str(sccss_cnt+fail_cnt+pass_cnt) + ";")
        return render_template("import_words.html", form=imprt_wrd_form)


# 「import_themes」のためのビュー関数(=URLエンドポイント)を宣言・定義する.
@view.route("/import_themes", methods=["GET", "POST"])
def import_themes():
    # 関数内で使用する変数・オブジェクトを宣言・定義する.
    sccss_cnt = 0
    fail_cnt = 0
    pass_cnt = 0
    imprt_thm_form = ImportThemeForm()

    # 該当のURLエンドポイントに入ったことをロギングする.
    rslt = se.etc.logging__info("view at /import_themes")

    # ロギングに失敗したら, 例外を発生させる.
    if rslt == "NG":
        raise InternalServerError

    # セッション未作成ならば, ホーム画面のページヘリダイレクトする.
    if not session:
        return redirect(url_for("view.home"))

    # セッション失効or未初期化ならば, ホーム画面のページヘリダイレクトする.
    if "is-admin-enter" not in session:
        return redirect(url_for("view.home"))

    # 管理者未入室の状態ならば, ホーム画面のページヘリダイレクトする.
    if session["is-admin-enter"] == False:
        return redirect(url_for("view.home"))

    if request.method == "GET":
        # セッションに現在ページの情報を設定して,
        # Flaskフォームと共にテンプレートを返す.
        session["referrer-page"] = "view.import_themes"
        return render_template("import_themes.html", form=imprt_thm_form)

    if request.method == "POST":
        # 直前に, GETメソッドで該当ページを取得しているかを調べる.
        # 取得していなければ, 強制的に現在ページへリダイレクトする.
        if session["referrer-page"] != "view.import_themes":
            return redirect(url_for("view.import_themes"))

        # フォームの取消ボタンが押されたら, 直前画面のページヘリダイレクトする.
        if imprt_thm_form.cancel.data:
            return redirect(url_for("view.admin_dashboard"))

        # フォームと共に送信されたファイルを取得して, 名前を安全な形式に変更する.
        xml_fl = imprt_thm_form.imported_file.data
        fl_nm = secure_filename(xml_fl.filename)
        if fl_nm == "":
            flash("主題ファイルが選択されていません.")
            return render_template("import_themes.html", form=imprt_thm_form)

        # 主題ファイルを一旦, 一時領域に保存してから, その内容を読み取る.
        xml_fl.save(os.path.join(consts.TEMPORARY_PATH, fl_nm))
        xml_fl = open(os.path.join(consts.TEMPORARY_PATH, fl_nm), 'r', encoding='UTF-8')

        # 不正なデータがないことを確認した上で, 
        # DBテーブルにレコードを転写・複写する.
        tree = ET.parse(xml_fl)
        root = tree.getroot()
        for child in root:
            if child.find("is-exclude").text == "はい":
                pass_cnt += 1
                continue
            try:
                   crrnt_dttm = se.etc.retrieve_current_datetime_as_string("JST", True)
                   db_session.add(Theme(spell_and_header=child.find("spell-and-header").text,
                                        mean_and_content=child.find("mean-and-content").text,
                                        intent=child.find("intent").text,
                                        category_tags=child.find("category-tags").text,
                                        staff_name=child.find("staff-name").text,
                                        staff_kana_name=child.find("staff-kana-name").text,
                                        created_at=child.find("created-at").text,
                                        updated_at=crrnt_dttm,
                                        is_hidden=child.find("is-hidden").text,
                                        is_exclude="no"
                                       ))
                   db_session.commit()
                   sccss_cnt += 1
                   continue

            except AttributeError:
                   sccss_cnt += 1
                   fail_cnt += 1
                   continue
            finally:
                   db_session.close()

        # 完了メッセージを設定して, テンプレートを返す.
        flash("主題ファイルの取込を実行しました.")
        flash("成功数:" + str(sccss_cnt) + ", " + "失敗数:" + str(fail_cnt) + ", " + "棄却数:" + str(pass_cnt) + ", " + "総件数:" + str(sccss_cnt+fail_cnt+pass_cnt) + ";")
        return render_template("import_themes.html", form=imprt_thm_form)


# 「import_categories」のためのビュー関数(=URLエンドポイント)を宣言・定義する.
@view.route("/import_categories", methods=["GET", "POST"])
def import_categories():
    # 関数内で使用する変数・オブジェクトを宣言・定義する.
    sccss_cnt = 0
    fail_cnt = 0
    pass_cnt = 0
    imprt_ctgr_form = ImportCategoryForm()

    # 該当のURLエンドポイントに入ったことをロギングする.
    rslt = se.etc.logging__info("view at /import_categories")

    # ロギングに失敗したら, 例外を発生させる.
    if rslt == "NG":
        raise InternalServerError

    # セッション未作成ならば, ホーム画面のページヘリダイレクトする.
    if not session:
        return redirect(url_for("view.home"))

    # セッション失効or未初期化ならば, ホーム画面のページヘリダイレクトする.
    if "is-admin-enter" not in session:
        return redirect(url_for("view.home"))

    # 管理者未入室の状態ならば, ホーム画面のページヘリダイレクトする.
    if session["is-admin-enter"] == False:
        return redirect(url_for("view.home"))

    if request.method == "GET":
        # セッションに現在ページの情報を設定して,
        # Flaskフォームと共にテンプレートを返す.
        session["referrer-page"] = "view.import_categories"
        return render_template("import_categories.html", form=imprt_ctgr_form)

    if request.method == "POST":
        # 直前に, GETメソッドで該当ページを取得しているかを調べる.
        # 取得していなければ, 強制的に現在ページへリダイレクトする.
        if session["referrer-page"] != "view.import_categories":
            return redirect(url_for("view.import_categories"))

        # フォームの取消ボタンが押されたら, 直前画面のページヘリダイレクトする.
        if imprt_ctgr_form.cancel.data:
            return redirect(url_for("view.admin_dashboard"))

        # フォームと共に送信されたファイルを取得して, 名前を安全な形式に変更する.
        xml_fl = imprt_ctgr_form.imported_file.data
        fl_nm = secure_filename(xml_fl.filename)
        if fl_nm == "":
            flash("分類ファイルが選択されていません.")
            return render_template("import_categories.html", form=imprt_ctgr_form)

        # 分類ファイルを一旦, 一時領域に保存してから, その内容を読み取る.
        xml_fl.save(os.path.join(consts.TEMPORARY_PATH, fl_nm))
        xml_fl = open(os.path.join(consts.TEMPORARY_PATH, fl_nm), 'r', encoding='UTF-8')

        # 不正なデータがないことを確認した上で, 
        # DBテーブルにレコードを転写・複写する.
        tree = ET.parse(xml_fl)
        root = tree.getroot()
        for child in root:
            if child.find("is-exclude").text == "はい":
                pass_cnt += 1
                continue
            try:
                   crrnt_dttm = se.etc.retrieve_current_datetime_as_string("JST", True)
                   db_session.add(Category(spell_and_header=child.find("spell-and-header").text,
                                           mean_and_content=child.find("mean-and-content").text,
                                           parent_category_tags=child.find("parent-category-tags").text,
                                           sibling_category_tags=child.find("sibling-category-tags").text,
                                           child_category_tags=child.find("child-category-tags").text,
                                           staff_name=child.find("staff-name").text,
                                           staff_kana_name=child.find("staff-kana-name").text,
                                           created_at=child.find("created-at").text,
                                           updated_at=crrnt_dttm,
                                           is_hidden=child.find("is-hidden").text,
                                           is_exclude="no"
                                          ))
                   db_session.commit()
                   sccss_cnt += 1
                   continue

            except AttributeError:
                   sccss_cnt += 1
                   fail_cnt += 1
                   continue
            finally:
                   db_session.close()

        # 完了メッセージを設定して, テンプレートを返す.
        flash("分類ファイルの取込を実行しました.")
        flash("成功数:" + str(sccss_cnt) + ", " + "失敗数:" + str(fail_cnt) + ", " + "棄却数:" + str(pass_cnt) + ", " + "総件数:" + str(sccss_cnt+fail_cnt+pass_cnt) + ";")
        return render_template("import_categories.html", form=imprt_ctgr_form)


# 「import_knowledges」のためのビュー関数(=URLエンドポイント)を宣言・定義する.
@view.route("/import_knowledges", methods=["GET", "POST"])
def import_knowledges():
    # 関数内で使用する変数・オブジェクトを宣言・定義する.
    sccss_cnt = 0
    fail_cnt = 0
    pass_cnt = 0
    imprt_knwldg_form = ImportKnowledgeForm()

    # 該当のURLエンドポイントに入ったことをロギングする.
    rslt = se.etc.logging__info("view at /import_knowledges")

    # ロギングに失敗したら, 例外を発生させる.
    if rslt == "NG":
        raise InternalServerError

    # セッション未作成ならば, ホーム画面のページヘリダイレクトする.
    if not session:
        return redirect(url_for("view.home"))

    # セッション失効or未初期化ならば, ホーム画面のページヘリダイレクトする.
    if "is-admin-enter" not in session:
        return redirect(url_for("view.home"))

    # 管理者未入室の状態ならば, ホーム画面のページヘリダイレクトする.
    if session["is-admin-enter"] == False:
        return redirect(url_for("view.home"))

    if request.method == "GET":
        # セッションに現在ページの情報を設定して,
        # Flaskフォームと共にテンプレートを返す.
        session["referrer-page"] = "view.import_knowledges"
        return render_template("import_knowledges.html", form=imprt_knwldg_form)

    if request.method == "POST":
        # 直前に, GETメソッドで該当ページを取得しているかを調べる.
        # 取得していなければ, 強制的に現在ページへリダイレクトする.
        if session["referrer-page"] != "view.import_knowledges":
            return redirect(url_for("view.import_knowledges"))

        # フォームの取消ボタンが押されたら, 直前画面のページヘリダイレクトする.
        if imprt_knwldg_form.cancel.data:
            return redirect(url_for("view.admin_dashboard"))

        # フォームと共に送信されたファイルを取得して, 名前を安全な形式に変更する.
        xml_fl = imprt_knwldg_form.imported_file.data
        fl_nm = secure_filename(xml_fl.filename)
        if fl_nm == "":
            flash("知識ファイルが選択されていません.")
            return render_template("import_knowledges.html", form=imprt_knwldg_form)

        # 知識ファイルを一旦, 一時領域に保存してから, その内容を読み取る.
        xml_fl.save(os.path.join(consts.TEMPORARY_PATH, fl_nm))
        xml_fl = open(os.path.join(consts.TEMPORARY_PATH, fl_nm), 'r', encoding='UTF-8')

        # 不正なデータがないことを確認した上で, 
        # DBテーブルにレコードを転写・複写する.
        tree = ET.parse(xml_fl)
        root = tree.getroot()
        for child in root:
            if child.find("is-exclude").text == "はい":
                pass_cnt += 1
                continue
            try:
                   crrnt_dttm = se.etc.retrieve_current_datetime_as_string("JST", True)
                   db_session.add(Knowledge(spell_and_header=child.find("spell-and-header").text,
                                            mean_and_content=child.find("mean-and-content").text,
                                            category_tags=child.find("category-tags").text,
                                            archived_image_file_path=child.find("archived-image-file-path").text,
                                            archived_sound_file_path=child.find("archived-sound-file-path").text,
                                            archived_video_file_path=child.find("archived-video-file-path").text,
                                            staff_name=child.find("staff-name").text,
                                            staff_kana_name=child.find("staff-kana-name").text,
                                            created_at=child.find("created-at").text,
                                            updated_at=crrnt_dttm,
                                            is_hidden=child.find("is-hidden").text,
                                            is_exclude="no"
                                           ))
                   db_session.commit()
                   sccss_cnt += 1
                   continue

            except AttributeError:
                   sccss_cnt += 1
                   fail_cnt += 1
                   continue
            finally:
                   db_session.close()

        # 完了メッセージを設定して, テンプレートを返す.
        flash("知識ファイルの取込を実行しました.")
        flash("成功数:" + str(sccss_cnt) + ", " + "失敗数:" + str(fail_cnt) + ", " + "棄却数:" + str(pass_cnt) + ", " + "総件数:" + str(sccss_cnt+fail_cnt+pass_cnt) + ";")
        return render_template("import_knowledges.html", form=imprt_knwldg_form)


# 「import_rules」のためのビュー関数(=URLエンドポイント)を宣言・定義する.
@view.route("/import_rules", methods=["GET", "POST"])
def import_rules():
    # 関数内で使用する変数・オブジェクトを宣言・定義する.
    sccss_cnt = 0
    fail_cnt = 0
    pass_cnt = 0
    imprt_rl_form = ImportRuleForm()

    # 該当のURLエンドポイントに入ったことをロギングする.
    rslt = se.etc.logging__info("view at /import_rules")

    # ロギングに失敗したら, 例外を発生させる.
    if rslt == "NG":
        raise InternalServerError

    # セッション未作成ならば, ホーム画面のページヘリダイレクトする.
    if not session:
        return redirect(url_for("view.home"))

    # セッション失効or未初期化ならば, ホーム画面のページヘリダイレクトする.
    if "is-admin-enter" not in session:
        return redirect(url_for("view.home"))

    # 管理者未入室の状態ならば, ホーム画面のページヘリダイレクトする.
    if session["is-admin-enter"] == False:
        return redirect(url_for("view.home"))

    if request.method == "GET":
        # セッションに現在ページの情報を設定して,
        # Flaskフォームと共にテンプレートを返す.
        session["referrer-page"] = "view.import_rules"
        return render_template("import_rules.html", form=imprt_rl_form)

    if request.method == "POST":
        # 直前に, GETメソッドで該当ページを取得しているかを調べる.
        # 取得していなければ, 強制的に現在ページへリダイレクトする.
        if session["referrer-page"] != "view.import_rules":
            return redirect(url_for("view.import_rules"))

        # フォームの取消ボタンが押されたら, 直前画面のページヘリダイレクトする.
        if imprt_rl_form.cancel.data:
            return redirect(url_for("view.admin_dashboard"))

        # フォームと共に送信されたファイルを取得して, 名前を安全な形式に変更する.
        xml_fl = imprt_rl_form.imported_file.data
        fl_nm = secure_filename(xml_fl.filename)
        if fl_nm == "":
            flash("規則ファイルが選択されていません.")
            return render_template("import_rules.html", form=imprt_rl_form)

        # 規則ファイルを一旦, 一時領域に保存してから, その内容を読み取る.
        xml_fl.save(os.path.join(consts.TEMPORARY_PATH, fl_nm))
        xml_fl = open(os.path.join(consts.TEMPORARY_PATH, fl_nm), 'r', encoding='UTF-8')

        # 不正なデータがないことを確認した上で, 
        # DBテーブルにレコードを転写・複写する.
        tree = ET.parse(xml_fl)
        root = tree.getroot()
        for child in root:
            if child.find("is-exclude").text == "はい":
                pass_cnt += 1
                continue
            try:
                   crrnt_dttm = se.etc.retrieve_current_datetime_as_string("JST", True)
                   db_session.add(Rule(spell_and_header=child.find("spell-and-header").text,
                                       mean_and_content=child.find("mean-and-content").text,
                                       intent=child.find("intent").text,
                                       category_tags=child.find("category-tags").text,
                                       inference_condition=child.find("inference-condition").text,
                                       inference_result=child.find("inference-result").text,
                                       staff_name=child.find("staff-name").text,
                                       staff_kana_name=child.find("staff-kana-name").text,
                                       created_at=child.find("created-at").text,
                                       updated_at=crrnt_dttm,
                                       is_hidden=child.find("is-hidden").text,
                                       is_exclude="no"
                                      ))
                   db_session.commit()
                   sccss_cnt += 1
                   continue

            except AttributeError:
                   sccss_cnt += 1
                   fail_cnt += 1
                   continue
            finally:
                   db_session.close()

        # 完了メッセージを設定して, テンプレートを返す.
        flash("規則ファイルの取込を実行しました.")
        flash("成功数:" + str(sccss_cnt) + ", " + "失敗数:" + str(fail_cnt) + ", " + "棄却数:" + str(pass_cnt) + ", " + "総件数:" + str(sccss_cnt+fail_cnt+pass_cnt) + ";")
        return render_template("import_rules.html", form=imprt_rl_form)


# 「import_reactions」のためのビュー関数(=URLエンドポイント)を宣言・定義する.
@view.route("/import_reactions", methods=["GET", "POST"])
def import_reactions():
    # 関数内で使用する変数・オブジェクトを宣言・定義する.
    sccss_cnt = 0
    fail_cnt = 0
    pass_cnt = 0
    imprt_rctn_form = ImportReactionForm()

    # 該当のURLエンドポイントに入ったことをロギングする.
    rslt = se.etc.logging__info("view at /import_reactions")

    # ロギングに失敗したら, 例外を発生させる.
    if rslt == "NG":
        raise InternalServerError

    # セッション未作成ならば, ホーム画面のページヘリダイレクトする.
    if not session:
        return redirect(url_for("view.home"))

    # セッション失効or未初期化ならば, ホーム画面のページヘリダイレクトする.
    if "is-admin-enter" not in session:
        return redirect(url_for("view.home"))

    # 管理者未入室の状態ならば, ホーム画面のページヘリダイレクトする.
    if session["is-admin-enter"] == False:
        return redirect(url_for("view.home"))

    if request.method == "GET":
        # セッションに現在ページの情報を設定して,
        # Flaskフォームと共にテンプレートを返す.
        session["referrer-page"] = "view.import_reactions"
        return render_template("import_reactions.html", form=imprt_rctn_form)

    if request.method == "POST":
        # 直前に, GETメソッドで該当ページを取得しているかを調べる.
        # 取得していなければ, 強制的に現在ページへリダイレクトする.
        if session["referrer-page"] != "view.import_reactions":
            return redirect(url_for("view.import_reactions"))

        # フォームの取消ボタンが押されたら, 直前画面のページヘリダイレクトする.
        if imprt_rctn_form.cancel.data:
            return redirect(url_for("view.admin_dashboard"))

        # フォームと共に送信されたファイルを取得して, 名前を安全な形式に変更する.
        xml_fl = imprt_rctn_form.imported_file.data
        fl_nm = secure_filename(xml_fl.filename)
        if fl_nm == "":
            flash("反応ファイルが選択されていません.")
            return render_template("import_reactions.html", form=imprt_rctn_form)

        # 反応ファイルを一旦, 一時領域に保存してから, その内容を読み取る.
        xml_fl.save(os.path.join(consts.TEMPORARY_PATH, fl_nm))
        xml_fl = open(os.path.join(consts.TEMPORARY_PATH, fl_nm), 'r', encoding='UTF-8')

        # 不正なデータがないことを確認した上で, 
        # DBテーブルにレコードを転写・複写する.
        tree = ET.parse(xml_fl)
        root = tree.getroot()
        for child in root:
            if child.find("is-exclude").text == "はい":
                pass_cnt += 1
                continue
            try:
                   crrnt_dttm = se.etc.retrieve_current_datetime_as_string("JST", True)
                   db_session.add(Reaction(spell_and_header=child.find("spell-and-header").text,
                                           mean_and_content=child.find("mean-and-content").text,
                                           staff_psychology=child.find("staff-psychology").text,
                                           scene_and_background=child.find("scene-and-background").text,
                                           message_example_from_staff=child.find("message-example-from-staff").text,
                                           message_example_from_application=child.find("message-example-from-application").text,
                                           staff_name=child.find("staff-name").text,
                                           staff_kana_name=child.find("staff-kana-name").text,
                                           created_at=child.find("created-at").text,
                                           updated_at=crrnt_dttm,
                                           is_hidden=child.find("is-hidden").text,
                                           is_exclude="no"
                                          ))
                   db_session.commit()
                   sccss_cnt += 1
                   continue

            except AttributeError:
                   sccss_cnt += 1
                   fail_cnt += 1
                   continue
            finally:
                   db_session.close()

        # 完了メッセージを設定して, テンプレートを返す.
        flash("反応ファイルの取込を実行しました.")
        flash("成功数:" + str(sccss_cnt) + ", " + "失敗数:" + str(fail_cnt) + ", " + "棄却数:" + str(pass_cnt) + ", " + "総件数:" + str(sccss_cnt+fail_cnt+pass_cnt) + ";")
        return render_template("import_reactions.html", form=imprt_rctn_form)


# 「import_generates」のためのビュー関数(=URLエンドポイント)を宣言・定義する.
@view.route("/import_generates", methods=["GET", "POST"])
def import_generates():
    # 関数内で使用する変数・オブジェクトを宣言・定義する.
    sccss_cnt = 0
    fail_cnt = 0
    pass_cnt = 0
    imprt_gen_form = ImportGenerateForm()

    # 該当のURLエンドポイントに入ったことをロギングする.
    rslt = se.etc.logging__info("view at /import_generates")

    # ロギングに失敗したら, 例外を発生させる.
    if rslt == "NG":
        raise InternalServerError

    # セッション未作成ならば, ホーム画面のページヘリダイレクトする.
    if not session:
        return redirect(url_for("view.home"))

    # セッション失効or未初期化ならば, ホーム画面のページヘリダイレクトする.
    if "is-admin-enter" not in session:
        return redirect(url_for("view.home"))

    # 管理者未入室の状態ならば, ホーム画面のページヘリダイレクトする.
    if session["is-admin-enter"] == False:
        return redirect(url_for("view.home"))

    if request.method == "GET":
        # セッションに現在ページの情報を設定して,
        # Flaskフォームと共にテンプレートを返す.
        session["referrer-page"] = "view.import_generates"
        return render_template("import_generates.html", form=imprt_gen_form)

    if request.method == "POST":
        # 直前に, GETメソッドで該当ページを取得しているかを調べる.
        # 取得していなければ, 強制的に現在ページへリダイレクトする.
        if session["referrer-page"] != "view.import_generates":
            return redirect(url_for("view.import_generates"))

        # フォームの取消ボタンが押されたら, 直前画面のページヘリダイレクトする.
        if imprt_gen_form.cancel.data:
            return redirect(url_for("view.admin_dashboard"))

        # フォームと共に送信されたファイルを取得して, 名前を安全な形式に変更する.
        xml_fl = imprt_gen_form.imported_file.data
        fl_nm = secure_filename(xml_fl.filename)
        if fl_nm == "":
            flash("語句ファイルが選択されていません.")
            return render_template("import_generates.html", form=imprt_gen_form)

        # ファイルを一旦, 一時領域に保存してから, その内容を読み取る.
        xml_fl.save(os.path.join(consts.TEMPORARY_PATH, fl_nm))
        xml_fl = open(os.path.join(consts.TEMPORARY_PATH, fl_nm), 'r', encoding='UTF-8')

        # 不正なデータがないことを確認した上で, 
        # DBテーブルにレコードを転写・複写する.
        tree = ET.parse(xml_fl)
        root = tree.getroot()
        for child in root:
            if child.find("is-exclude").text == "はい":
                pass_cnt += 1
                continue
            try:
                   crrnt_dttm = se.etc.retrieve_current_datetime_as_string("JST", True)
                   db_session.add(Generate(spell_and_header=child.find("spell-and-header").text,
                                           mean_and_content=child.find("mean-and-content").text,
                                           generated_file_path=child.find("generated-file-path").text,
                                           staff_name=child.find("staff-name").text,
                                           staff_kana_name=child.find("staff-kana-name").text,
                                           created_at=child.find("created-at").text,
                                           updated_at=crrnt_dttm,
                                           is_hidden=child.find("is-hidden").text,
                                           is_exclude="no"
                                          ))
                   db_session.commit()
                   sccss_cnt += 1
                   continue

            except AttributeError:
                   sccss_cnt += 1
                   fail_cnt += 1
                   continue
            finally:
                   db_session.close()

        # 完了メッセージを設定して, テンプレートを返す.
        flash("語句ファイルの取込を実行しました.")
        flash("成功数:" + str(sccss_cnt) + ", " + "失敗数:" + str(fail_cnt) + ", " + "棄却数:" + str(pass_cnt) + ", " + "総件数:" + str(sccss_cnt+fail_cnt+pass_cnt) + ";")
        return render_template("import_generates.html", form=imprt_gen_form)


# 「import_enters_or_exits」のためのビュー関数(=URLエンドポイント)を宣言・定義する.
@view.route("/import_enters_or_exits", methods=["GET", "POST"])
def import_enters_or_exits():
    # 関数内で使用する変数・オブジェクトを宣言・定義する.
    imprt_entr_n_exit_form = ImportEnterOrExitForm()

    # 該当のURLエンドポイントに入ったことをロギングする.
    rslt = se.etc.logging__info("view at /import_enters_or_exits")

    # ロギングに失敗したら, 例外を発生させる.
    if rslt == "NG":
        raise InternalServerError

    # セッション未作成ならば, ホーム画面のページヘリダイレクトする.
    if not session:
        return redirect(url_for("view.home"))

    # セッション失効or未初期化ならば, ホーム画面のページヘリダイレクトする.
    if "is-admin-enter" not in session:
        return redirect(url_for("view.home"))

    # 管理者未入室の状態ならば, ホーム画面のページヘリダイレクトする.
    if session["is-admin-enter"] == False:
        return redirect(url_for("view.home"))

    if request.method == "GET":
        # セッションに現在ページの情報を設定して,
        # Flaskフォームと共にテンプレートを返す.
        session["referrer-page"] = "view.import_enters_or_exits"
        return render_template("import_enters_or_exits.html", form=imprt_entr_n_exit_form)

    if request.method == "POST":
        # 直前に, GETメソッドで該当ページを取得しているかを調べる.
        # 取得していなければ, 強制的に現在ページへリダイレクトする.
        if session["referrer-page"] != "view.import_enters_or_exits":
            return redirect(url_for("view.import_enters_or_exits"))

        # フォームの取消ボタンが押されたら, 直前画面のページヘリダイレクトする.
        if imprt_entr_n_exit_form.cancel.data:
            return redirect(url_for("view.admin_dashboard"))

        # フォームと共に送信されたファイルを取得して, 名前を安全な形式に変更する.
        csv_fl = imprt_entr_n_exit_form.imported_file.data
        fl_nm = secure_filename(csv_fl.filename)
        if fl_nm == "":
            flash("入退ファイルが選択されていません.")
            return render_template("import_enters_or_exits.html", form=imprt_entr_n_exit_form)

        # ファイルを一旦, 一時領域に保存してから, その内容を読み取る.
        csv_fl.save(os.path.join(consts.TEMPORARY_PATH, fl_nm))
        csv_fl = open(os.path.join(consts.TEMPORARY_PATH, fl_nm), 'r', encoding='UTF-8')
        rcds = csv.reader(csv_fl)

        # ファイル内容をレコード単位で読み取り, 不正なデータがないかを確認する.
        for rcd in rcds:
            if len(rcd) != 8:
                continue
            if rcd[7] == "はい":
                continue
            if len(rcd[0]) > consts.STAFF_NAME_LENGTH:
                continue
            if len(rcd[0]) > consts.STAFF_KANA_NAME_LENGTH:
                continue
            if (" " in rcd[0] or "　" in rcd[0]):
                continue
            if (" " in rcd[1] or "　" in rcd[1]):
                continue
            if ("\'" in rcd[0] or "\"" in rcd[0]):
                continue
            if ("\'" in rcd[1] or "\"" in rcd[1]):
                continue
            if (rcd[0] == "" or rcd[1] == "" or
                rcd[2] == "" or rcd[3] == "" or
                rcd[4] == "" or rcd[5] == "" or
                rcd[6] == "" or rcd[7] == ""):
                 continue
            if (rcd[2] != "出勤" and rcd[2] != "外出戻り" and
                rcd[2] != "休憩明け" and rcd[2] != "退勤" and
                rcd[2] != "外出" and rcd[2] != "休憩" and
                rcd[2] != "忘却or失効" and rcd[2] != "アプリ終了"):
                 continue
            if not se.etc.check_timestamp_by_display_style(rcd[3]):
                continue
            if not se.etc.check_timestamp_by_display_style(rcd[4]):
                continue
            if not se.etc.check_timestamp_by_display_style(rcd[5]):
                continue

            # 不正なデータがないことを確認した上で, 
            # DBテーブルにレコードを転写・複写する.
            stff_nm = rcd[0]
            stff_kn_nm = rcd[1]
            if rcd[2] == "出勤":
                rsn = "clock-in"
            elif rcd[2] == "外出戻り":
                rsn = "return-to-out"
            elif rcd[2] == "休憩明け":
                rsn = "after-break"
            elif rcd[2] == "退勤":
                rsn = "clock-out"
            elif rcd[2] == "外出":
                rsn = "out"
            elif rcd[2] == "休憩":
                rsn = "break"
            elif rcd[2] == "忘却or失効":
                rsn = "forget-or-revocation"
            elif rcd[2] == "アプリ終了":
                rsn = "application-termination"
            else:
                rsn = "unknown"
            dttm1 = se.etc.convert_datetime_string_to_iso_style(rcd[3])
            dttm2 = se.etc.convert_datetime_string_to_iso_style(rcd[4])
            crrnt_dttm = se.etc.retrieve_current_datetime_as_string("JST", True)
            is_hddn = True if rcd[6] == "はい" else False
            is_excld = True if rcd[7] == "はい" else False
            db_session.add(EnterOrExit(staff_name=stff_nm,
                                       staff_kana_name=stff_kn_nm,
                                       reason=rsn,
                                       enter_or_exit_at=dttm1,
                                       created_at=dttm2,
                                       updated_at=crrnt_dttm,
                                       is_hidden=is_hddn,
                                       is_exclude=is_excld
                                      ))
            db_session.commit()
        db_session.close()
        csv_fl.close()

        # 完了メッセージを設定して, テンプレートを返す.
        flash("入退ファイルの取込を実行しました.")
        return render_template("import_enters_or_exits.html", form=imprt_entr_n_exit_form)


# 「export_words」のためのビュー関数(=URLエンドポイント)を宣言・定義する.
@view.route("/export_words", methods=["GET", "POST"])
def export_words():
    # 関数内で使用する変数・オブジェクトを宣言・定義する.
    exprt_wrd_form = ExportWordForm()

    # 該当のURLエンドポイントに入ったことをロギングする.
    rslt = se.etc.logging__info("view at /export_words")

    # ロギングに失敗したら, 例外を発生させる.
    if rslt == "NG":
        raise InternalServerError

    # セッション未作成ならば, ホーム画面のページヘリダイレクトする.
    if not session:
        return redirect(url_for("view.home"))

    # セッション失効or未初期化ならば, ホーム画面のページヘリダイレクトする.
    if "is-admin-enter" not in session:
        return redirect(url_for("view.home"))

    # 管理者未入室の状態ならば, ホーム画面のページヘリダイレクトする.
    if session["is-admin-enter"] == False:
        return redirect(url_for("view.home"))

    if request.method == "GET":
        # セッションに現在ページの情報を設定して,
        # Flaskフォームと共にテンプレートを返す.
        session["referrer-page"] = "view.export_words"
        return render_template("export_words.html", form=exprt_wrd_form)

    if request.method == "POST":
        # 直前に, GETメソッドで該当ページを取得しているかを調べる.
        # 取得していなければ, 強制的に現在ページへリダイレクトする.
        if session["referrer-page"] != "view.export_words":
            return redirect(url_for("view.export_words"))

        # フォームの取消ボタンが押されたら, 直前画面のページヘリダイレクトする.
        if exprt_wrd_form.cancel.data:
            return redirect(url_for("view.admin_dashboard"))

        # ID昇順で, 全ての語句レコードをDBから取得する.
        wrds = db_session.query(Word).filter(Word.is_exclude==False).order_by(Word.id.asc()).all()
        db_session.close()

        # DBから取得した語句レコードの内容をXMLファイルに書き込むための準備をする.
        root = ET.Element("Word-Dictionary")
        for wrd in wrds:
            wrd_elm = ET.SubElement(root, "Word-Entry")
            ET.SubElement(wrd_elm, "spell-and-header").text = wrd.spell_and_header
            ET.SubElement(wrd_elm, "mean-and-content").text = wrd.mean_and_content
            ET.SubElement(wrd_elm, "intent").text = wrd.intent
            ET.SubElement(wrd_elm, "sentiment").text = wrd.sentiment
            ET.SubElement(wrd_elm, "strength").text = wrd.strength
            ET.SubElement(wrd_elm, "part-of-speech").text = wrd.part_of_speech
            ET.SubElement(wrd_elm, "staff-name").text = wrd.staff_name
            ET.SubElement(wrd_elm, "staff-kana-name").text = wrd.staff_kana_name
            ET.SubElement(wrd_elm, "created-at").text = se.etc.convert_datetime_string_to_display_style(wrd.created_at)
            ET.SubElement(wrd_elm, "renew-date-time").text = se.etc.convert_datetime_string_to_display_style(wrd.updated_at)
            ET.SubElement(wrd_elm, "is-hidden").text = "はい" if wrd.is_hidden == "yes" else "いいえ"
            ET.SubElement(wrd_elm, "is-exclude").text = "いいえ"

        # XML文書内容を読み易いように整形する.
        xml_txt = MD.parseString(ET.tostring(root, "utf-8")).toprettyxml(indent="   ")

        # 書出し先ファイルが既に存在すれば, それを削除する.
        if os.path.exists(consts.WORD_EXPORT_PATH):
            os.remove(consts.WORD_EXPORT_PATH)

        # 書出し先ファイルを新規作成して, 先のXML文書内容を書き込んで閉じる. 
        with open(consts.WORD_EXPORT_PATH, 'x', encoding='UTF-8') as xml_fl:
             xml_fl.write(xml_txt)

        # 書出し先ファイルをクライアントへ送信する. 
        return send_file(consts.WORD_EXPORT_PATH, as_attachment=True)


# 「export_themes」のためのビュー関数(=URLエンドポイント)を宣言・定義する.
@view.route("/export_themes", methods=["GET", "POST"])
def export_themes():
    # 関数内で使用する変数・オブジェクトを宣言・定義する.
    exprt_thm_form = ExportThemeForm()

    # 該当のURLエンドポイントに入ったことをロギングする.
    rslt = se.etc.logging__info("view at /export_themes")

    # ロギングに失敗したら, 例外を発生させる.
    if rslt == "NG":
        raise InternalServerError

    # セッション未作成ならば, ホーム画面のページヘリダイレクトする.
    if not session:
        return redirect(url_for("view.home"))

    # セッション失効or未初期化ならば, ホーム画面のページヘリダイレクトする.
    if "is-admin-enter" not in session:
        return redirect(url_for("view.home"))

    # 管理者未入室の状態ならば, ホーム画面のページヘリダイレクトする.
    if session["is-admin-enter"] == False:
        return redirect(url_for("view.home"))

    if request.method == "GET":
        # セッションに現在ページの情報を設定して,
        # Flaskフォームと共にテンプレートを返す.
        session["referrer-page"] = "view.export_themes"
        return render_template("export_themes.html", form=exprt_thm_form)

    if request.method == "POST":
        # 直前に, GETメソッドで該当ページを取得しているかを調べる.
        # 取得していなければ, 強制的に現在ページへリダイレクトする.
        if session["referrer-page"] != "view.export_themes":
            return redirect(url_for("view.export_themes"))

        # フォームの取消ボタンが押されたら, 直前画面のページヘリダイレクトする.
        if exprt_thm_form.cancel.data:
            return redirect(url_for("view.admin_dashboard"))

        # ID昇順で, 全ての主題レコードをDBから取得する.
        thms = db_session.query(Theme).filter(Theme.is_exclude==False).order_by(Theme.id.asc()).all()
        db_session.close()

        # DBから取得した主題レコードの内容をXMLファイルに書き込むための準備をする.
        root = ET.Element("Theme-Dictionary")
        for thm in thms:
            thm_elm = ET.SubElement(root, "Theme-Entry")
            ET.SubElement(thm_elm, "spell-and-header").text = thm.spell_and_header
            ET.SubElement(thm_elm, "mean-and-content").text = thm.mean_and_content
            ET.SubElement(thm_elm, "category-tags").text = thm.category_tags
            ET.SubElement(thm_elm, "staff-name").text = thm.staff_name
            ET.SubElement(thm_elm, "staff-kana-name").text = thm.staff_kana_name
            ET.SubElement(thm_elm, "created-at").text = se.etc.convert_datetime_string_to_display_style(thm.created_at)
            ET.SubElement(thm_elm, "renew-date-time").text = se.etc.convert_datetime_string_to_display_style(thm.updated_at)
            ET.SubElement(thm_elm, "is-hidden").text = "はい" if thm.is_hidden == "yes" else "いいえ"
            ET.SubElement(thm_elm, "is-exclude").text = "いいえ"

        # XML文書内容を読み易いように整形する.
        xml_txt = MD.parseString(ET.tostring(root, "utf-8")).toprettyxml(indent="   ")

        # 書出し先ファイルが既に存在すれば, それを削除する.
        if os.path.exists(consts.THEME_EXPORT_PATH):
            os.remove(consts.THEME_EXPORT_PATH)

        # 書出し先ファイルを新規作成して, 先のXML文書内容を書き込んで閉じる. 
        with open(consts.THEME_EXPORT_PATH, 'x', encoding='UTF-8') as xml_fl:
             xml_fl.write(xml_txt)

        # 書出し先ファイルをクライアントへ送信する. 
        return send_file(consts.THEME_EXPORT_PATH, as_attachment=True)


# 「export_categories」のためのビュー関数(=URLエンドポイント)を宣言・定義する.
@view.route("/export_categories", methods=["GET", "POST"])
def export_categories():
    # 関数内で使用する変数・オブジェクトを宣言・定義する.
    exprt_ctgr_form = ExportCategoryForm()

    # 該当のURLエンドポイントに入ったことをロギングする.
    rslt = se.etc.logging__info("view at /export_categories")

    # ロギングに失敗したら, 例外を発生させる.
    if rslt == "NG":
        raise InternalServerError

    # セッション未作成ならば, ホーム画面のページヘリダイレクトする.
    if not session:
        return redirect(url_for("view.home"))

    # セッション失効or未初期化ならば, ホーム画面のページヘリダイレクトする.
    if "is-admin-enter" not in session:
        return redirect(url_for("view.home"))

    # 管理者未入室の状態ならば, ホーム画面のページヘリダイレクトする.
    if session["is-admin-enter"] == False:
        return redirect(url_for("view.home"))

    if request.method == "GET":
        # セッションに現在ページの情報を設定して,
        # Flaskフォームと共にテンプレートを返す.
        session["referrer-page"] = "view.export_categories"
        return render_template("export_categories.html", form=exprt_ctgr_form)

    if request.method == "POST":
        # 直前に, GETメソッドで該当ページを取得しているかを調べる.
        # 取得していなければ, 強制的に現在ページへリダイレクトする.
        if session["referrer-page"] != "view.export_categories":
            return redirect(url_for("view.export_categories"))

        # フォームの取消ボタンが押されたら, 直前画面のページヘリダイレクトする.
        if exprt_ctgr_form.cancel.data:
            return redirect(url_for("view.admin_dashboard"))

        # ID昇順で, 全ての分類レコードをDBから取得する.
        ctgrs = db_session.query(Category).filter(Category.is_exclude==False).order_by(Category.id.asc()).all()
        db_session.close()

        # DBから取得した分類レコードの内容をXMLファイルに書き込むための準備をする.
        root = ET.Element("Category-Dictionary")
        for ctgr in ctgrs:
            ctgr_elm = ET.SubElement(root, "Category-Entry")
            ET.SubElement(ctgr_elm, "spell-and-header").text = ctgr.spell_and_header
            ET.SubElement(ctgr_elm, "mean-and-content").text = ctgr.mean_and_content
            ET.SubElement(ctgr_elm, "intent").text = ctgr.parent_category_tags
            ET.SubElement(ctgr_elm, "sentiment").text = ctgr.child_category_tags
            ET.SubElement(ctgr_elm, "staff-name").text = ctgr.staff_name
            ET.SubElement(ctgr_elm, "staff-kana-name").text = ctgr.staff_kana_name
            ET.SubElement(ctgr_elm, "created-at").text = se.etc.convert_datetime_string_to_display_style(ctgr.created_at)
            ET.SubElement(ctgr_elm, "renew-date-time").text = se.etc.convert_datetime_string_to_display_style(ctgr.updated_at)
            ET.SubElement(ctgr_elm, "is-hidden").text = "はい" if ctgr.is_hidden == "yes" else "いいえ"
            ET.SubElement(ctgr_elm, "is-exclude").text = "いいえ"

        # XML文書内容を読み易いように整形する.
        xml_txt = MD.parseString(ET.tostring(root, "utf-8")).toprettyxml(indent="   ")

        # 書出し先ファイルが既に存在すれば, それを削除する.
        if os.path.exists(consts.CATEGORY_EXPORT_PATH):
            os.remove(consts.CATEGORY_EXPORT_PATH)

        # 書出し先ファイルを新規作成して, 先のXML文書内容を書き込んで閉じる. 
        with open(consts.CATEGORY_EXPORT_PATH, 'x', encoding='UTF-8') as xml_fl:
             xml_fl.write(xml_txt)

        # 書出し先ファイルをクライアントへ送信する. 
        return send_file(consts.CATEGORY_EXPORT_PATH, as_attachment=True)


# 「export_knowledges」のためのビュー関数(=URLエンドポイント)を宣言・定義する.
@view.route("/export_knowledges", methods=["GET", "POST"])
def export_knowledges():
    # 関数内で使用する変数・オブジェクトを宣言・定義する.
    exprt_knwldg_form = ExportKnowledgeForm()

    # 該当のURLエンドポイントに入ったことをロギングする.
    rslt = se.etc.logging__info("view at /export_knowledges")

    # ロギングに失敗したら, 例外を発生させる.
    if rslt == "NG":
        raise InternalServerError

    # セッション未作成ならば, ホーム画面のページヘリダイレクトする.
    if not session:
        return redirect(url_for("view.home"))

    # セッション失効or未初期化ならば, ホーム画面のページヘリダイレクトする.
    if "is-admin-enter" not in session:
        return redirect(url_for("view.home"))

    # 管理者未入室の状態ならば, ホーム画面のページヘリダイレクトする.
    if session["is-admin-enter"] == False:
        return redirect(url_for("view.home"))

    if request.method == "GET":
        # セッションに現在ページの情報を設定して,
        # Flaskフォームと共にテンプレートを返す.
        session["referrer-page"] = "view.export_knowledges"
        return render_template("export_knowledges.html", form=exprt_knwldg_form)

    if request.method == "POST":
        # 直前に, GETメソッドで該当ページを取得しているかを調べる.
        # 取得していなければ, 強制的に現在ページへリダイレクトする.
        if session["referrer-page"] != "view.export_knowledges":
            return redirect(url_for("view.export_knowledges"))

        # フォームの取消ボタンが押されたら, 直前画面のページヘリダイレクトする.
        if exprt_knwldg_form.cancel.data:
            return redirect(url_for("view.admin_dashboard"))

        # ID昇順で, 全ての知識レコードをDBから取得する.
        knwldgs = db_session.query(Knowledge).filter(Knowledge.is_exclude==False).order_by(Knowledge.id.asc()).all()
        db_session.close()

        # DBから取得した知識レコードの内容をXMLファイルに書き込むための準備をする.
        root = ET.Element("Knowledge-Dictionary")
        for knwldg in knwldgs:
            knwldg_elm = ET.SubElement(root, "Knowledge-Entry")
            ET.SubElement(knwldg_elm, "spell-and-header").text = knwldg.spell_and_header
            ET.SubElement(knwldg_elm, "mean-and-content").text = knwldg.mean_and_content
            ET.SubElement(knwldg_elm, "category-tags").text = knwldg.category_tags
            ET.SubElement(knwldg_elm, "archived-image-file-path").text = knwldg.archived_image_file_path
            ET.SubElement(knwldg_elm, "archived-sound-file-path").text = knwldg.archived_sound_file_path
            ET.SubElement(knwldg_elm, "archived-video-file-path").text = knwldg.archived_video_file_path
            ET.SubElement(knwldg_elm, "staff-name").text = knwldg.staff_name
            ET.SubElement(knwldg_elm, "staff-kana-name").text = knwldg.staff_kana_name
            ET.SubElement(knwldg_elm, "created-at").text = se.etc.convert_datetime_string_to_display_style(knwldg.created_at)
            ET.SubElement(knwldg_elm, "renew-date-time").text = se.etc.convert_datetime_string_to_display_style(knwldg.updated_at)
            ET.SubElement(knwldg_elm, "is-hidden").text = "はい" if knwldg.is_hidden == "yes" else "いいえ"
            ET.SubElement(knwldg_elm, "is-exclude").text = "いいえ"

        # XML文書内容を読み易いように整形する.
        xml_txt = MD.parseString(ET.tostring(root, "utf-8")).toprettyxml(indent="   ")

        # 書出し先ファイルが既に存在すれば, それを削除する.
        if os.path.exists(consts.KNOWLEDGE_EXPORT_PATH):
            os.remove(consts.KNOWLEDGE_EXPORT_PATH)

        # 書出し先ファイルを新規作成して, 先のXML文書内容を書き込んで閉じる. 
        with open(consts.KNOWLEDGE_EXPORT_PATH, 'x', encoding='UTF-8') as xml_fl:
             xml_fl.write(xml_txt)

        # 書出し先ファイルをクライアントへ送信する. 
        return send_file(consts.KNOWLEDGE_EXPORT_PATH, as_attachment=True)


# 「export_rules」のためのビュー関数(=URLエンドポイント)を宣言・定義する.
@view.route("/export_rules", methods=["GET", "POST"])
def export_rules():
    # 関数内で使用する変数・オブジェクトを宣言・定義する.
    exprt_rl_form = ExportRuleForm()

    # 該当のURLエンドポイントに入ったことをロギングする.
    rslt = se.etc.logging__info("view at /export_rules")

    # ロギングに失敗したら, 例外を発生させる.
    if rslt == "NG":
        raise InternalServerError

    # セッション未作成ならば, ホーム画面のページヘリダイレクトする.
    if not session:
        return redirect(url_for("view.home"))

    # セッション失効or未初期化ならば, ホーム画面のページヘリダイレクトする.
    if "is-admin-enter" not in session:
        return redirect(url_for("view.home"))

    # 管理者未入室の状態ならば, ホーム画面のページヘリダイレクトする.
    if session["is-admin-enter"] == False:
        return redirect(url_for("view.home"))

    if request.method == "GET":
        # セッションに現在ページの情報を設定して,
        # Flaskフォームと共にテンプレートを返す.
        session["referrer-page"] = "view.export_rules"
        return render_template("export_rules.html", form=exprt_rl_form)

    if request.method == "POST":
        # 直前に, GETメソッドで該当ページを取得しているかを調べる.
        # 取得していなければ, 強制的に現在ページへリダイレクトする.
        if session["referrer-page"] != "view.export_rules":
            return redirect(url_for("view.export_rules"))

        # フォームの取消ボタンが押されたら, 直前画面のページヘリダイレクトする.
        if exprt_rl_form.cancel.data:
            return redirect(url_for("view.admin_dashboard"))

        # ID昇順で, 全ての知識レコードをDBから取得する.
        rls = db_session.query(Rule).filter(Rule.is_exclude==False).order_by(Rule.id.asc()).all()
        db_session.close()

        # DBから取得した知識レコードの内容をXMLファイルに書き込むための準備をする.
        root = ET.Element("Rule-Dictionary")
        for rl in rls:
            rl_elm = ET.SubElement(root, "Rule-Entry")
            ET.SubElement(rl_elm, "spell-and-header").text = rl.spell_and_header
            ET.SubElement(rl_elm, "mean-and-content").text = rl.mean_and_content
            ET.SubElement(rl_elm, "category-tags").text = rl.category_tags
            ET.SubElement(rl_elm, "inference-condition").text = rl.inference_condition
            ET.SubElement(rl_elm, "inference-result").text = rl.inference_result
            ET.SubElement(rl_elm, "staff-name").text = rl.staff_name
            ET.SubElement(rl_elm, "staff-kana-name").text = rl.staff_kana_name
            ET.SubElement(rl_elm, "created-at").text = se.etc.convert_datetime_string_to_display_style(rl.created_at)
            ET.SubElement(rl_elm, "renew-date-time").text = se.etc.convert_datetime_string_to_display_style(rl.updated_at)
            ET.SubElement(rl_elm, "is-hidden").text = "はい" if rl.is_hidden == "yes" else "いいえ"
            ET.SubElement(rl_elm, "is-exclude").text = "いいえ"

        # XML文書内容を読み易いように整形する.
        xml_txt = MD.parseString(ET.tostring(root, "utf-8")).toprettyxml(indent="   ")

        # 書出し先ファイルが既に存在すれば, それを削除する.
        if os.path.exists(consts.RULE_EXPORT_PATH):
            os.remove(consts.RULE_EXPORT_PATH)

        # 書出し先ファイルを新規作成して, 先のXML文書内容を書き込んで閉じる. 
        with open(consts.RULE_EXPORT_PATH, 'x', encoding='UTF-8') as xml_fl:
             xml_fl.write(xml_txt)

        # 書出し先ファイルをクライアントへ送信する. 
        return send_file(consts.RULE_EXPORT_PATH, as_attachment=True)


# 「export_reactions」のためのビュー関数(=URLエンドポイント)を宣言・定義する.
@view.route("/export_reactions", methods=["GET", "POST"])
def export_reactions():
    # 関数内で使用する変数・オブジェクトを宣言・定義する.
    exprt_rctn_form = ExportReactionForm()

    # 該当のURLエンドポイントに入ったことをロギングする.
    rslt = se.etc.logging__info("view at /export_reactions")

    # ロギングに失敗したら, 例外を発生させる.
    if rslt == "NG":
        raise InternalServerError

    # セッション未作成ならば, ホーム画面のページヘリダイレクトする.
    if not session:
        return redirect(url_for("view.home"))

    # セッション失効or未初期化ならば, ホーム画面のページヘリダイレクトする.
    if "is-admin-enter" not in session:
        return redirect(url_for("view.home"))

    # 管理者未入室の状態ならば, ホーム画面のページヘリダイレクトする.
    if session["is-admin-enter"] == False:
        return redirect(url_for("view.home"))

    if request.method == "GET":
        # セッションに現在ページの情報を設定して,
        # Flaskフォームと共にテンプレートを返す.
        session["referrer-page"] = "view.export_reactions"
        return render_template("export_reactions.html", form=exprt_rctn_form)

    if request.method == "POST":
        # 直前に, GETメソッドで該当ページを取得しているかを調べる.
        # 取得していなければ, 強制的に現在ページへリダイレクトする.
        if session["referrer-page"] != "view.export_reactions":
            return redirect(url_for("view.export_reactions"))

        # フォームの取消ボタンが押されたら, 直前画面のページヘリダイレクトする.
        if exprt_rctn_form.cancel.data:
            return redirect(url_for("view.admin_dashboard"))

        # ID昇順で, 全ての知識レコードをDBから取得する.
        rctns = db_session.query(Reaction).filter(Reaction.is_exclude==False).order_by(Reaction.id.asc()).all()
        db_session.close()

        # DBから取得した知識レコードの内容をXMLファイルに書き込むための準備をする.
        root = ET.Element("Reaction-Dictionary")
        for rctn in rctns:
            rctn_elm = ET.SubElement(root, "Reaction-Entry")
            ET.SubElement(rctn_elm, "spell-and-header").text = rctn.spell_and_header
            ET.SubElement(rctn_elm, "mean-and-content").text = rctn.mean_and_content
            ET.SubElement(rctn_elm, "staff-psychology").text = rctn.staff_psychology
            ET.SubElement(rctn_elm, "scene-and-background").text = rctn.scene_and_background
            ET.SubElement(rctn_elm, "message-example-from-staff").text = rctn.message_example_from_staff
            ET.SubElement(rctn_elm, "message-example-from-application").text = rctn.message_example_from_application
            ET.SubElement(rctn_elm, "staff-name").text = rctn.staff_name
            ET.SubElement(rctn_elm, "staff-kana-name").text = rctn.staff_kana_name
            ET.SubElement(rctn_elm, "created-at").text = se.etc.convert_datetime_string_to_display_style(rctn.created_at)
            ET.SubElement(rctn_elm, "renew-date-time").text = se.etc.convert_datetime_string_to_display_style(rctn.updated_at)
            ET.SubElement(rctn_elm, "is-hidden").text = "はい" if rctn.is_hidden == "yes" else "いいえ"
            ET.SubElement(rctn_elm, "is-exclude").text = "いいえ"

        # XML文書内容を読み易いように整形する.
        xml_txt = MD.parseString(ET.tostring(root, "utf-8")).toprettyxml(indent="   ")

        # 書出し先ファイルが既に存在すれば, それを削除する.
        if os.path.exists(consts.REACTION_EXPORT_PATH):
            os.remove(consts.REACTION_EXPORT_PATH)

        # 書出し先ファイルを新規作成して, 先のXML文書内容を書き込んで閉じる. 
        with open(consts.REACTION_EXPORT_PATH, 'x', encoding='UTF-8') as xml_fl:
             xml_fl.write(xml_txt)

        # 書出し先ファイルをクライアントへ送信する. 
        return send_file(consts.REACTION_EXPORT_PATH, as_attachment=True)


# 「export_generates」のためのビュー関数(=URLエンドポイント)を宣言・定義する.
@view.route("/export_generates", methods=["GET", "POST"])
def export_generates():
    # 関数内で使用する変数・オブジェクトを宣言・定義する.
    exprt_gen_form = ExportGenerateForm()

    # 該当のURLエンドポイントに入ったことをロギングする.
    rslt = se.etc.logging__info("view at /export_words")

    # ロギングに失敗したら, 例外を発生させる.
    if rslt == "NG":
        raise InternalServerError

    # セッション未作成ならば, ホーム画面のページヘリダイレクトする.
    if not session:
        return redirect(url_for("view.home"))

    # セッション失効or未初期化ならば, ホーム画面のページヘリダイレクトする.
    if "is-admin-enter" not in session:
        return redirect(url_for("view.home"))

    # 管理者未入室の状態ならば, ホーム画面のページヘリダイレクトする.
    if session["is-admin-enter"] == False:
        return redirect(url_for("view.home"))

    if request.method == "GET":
        # セッションに現在ページの情報を設定して,
        # Flaskフォームと共にテンプレートを返す.
        session["referrer-page"] = "view.export_generates"
        return render_template("export_generates.html", form=exprt_gen_form)

    if request.method == "POST":
        # 直前に, GETメソッドで該当ページを取得しているかを調べる.
        # 取得していなければ, 強制的に現在ページへリダイレクトする.
        if session["referrer-page"] != "view.export_generates":
            return redirect(url_for("view.export_generates"))

        # フォームの取消ボタンが押されたら, 直前画面のページヘリダイレクトする.
        if exprt_gen_form.cancel.data:
            return redirect(url_for("view.admin_dashboard"))

        # ID昇順で, 全ての生成レコードをDBから取得する.
        gens = db_session.query(Generate).filter(Generate.is_exclude==False).order_by(Generate.id.asc()).all()
        db_session.close()

        # DBから取得した生成レコードの内容をXMLファイルに書き込むための準備をする.
        root = ET.Element("Generate-Dictionary")
        for gen in gens:
            gen_elm = ET.SubElement(root, "Generate-Entry")
            ET.SubElement(gen_elm, "spell-and-header").text = gen.spell_and_header
            ET.SubElement(gen_elm, "mean-and-content").text = gen.mean_and_content
            ET.SubElement(gen_elm, "generated-file-path").text = gen.generated_file_path
            ET.SubElement(gen_elm, "staff-name").text = gen.staff_name
            ET.SubElement(gen_elm, "staff-kana-name").text = gen.staff_kana_name
            ET.SubElement(gen_elm, "created-at").text = se.etc.convert_datetime_string_to_display_style(gen.created_at)
            ET.SubElement(gen_elm, "renew-date-time").text = se.etc.convert_datetime_string_to_display_style(gen.updated_at)
            ET.SubElement(gen_elm, "is-hidden").text = "はい" if gen.is_hidden == "yes" else "いいえ"
            ET.SubElement(gen_elm, "is-exclude").text = "いいえ"

        # XML文書内容を読み易いように整形する.
        xml_txt = MD.parseString(ET.tostring(root, "utf-8")).toprettyxml(indent="   ")

        # 書出し先ファイルが既に存在すれば, それを削除する.
        if os.path.exists(consts.GENETATE_EXPORT_PATH):
            os.remove(consts.GENETATE_EXPORT_PATH)

        # 書出し先ファイルを新規作成して, 先のXML文書内容を書き込んで閉じる. 
        with open(consts.GENETATE_EXPORT_PATH, 'x', encoding='UTF-8') as xml_fl:
             xml_fl.write(xml_txt)

        # 書出し先ファイルをクライアントへ送信する. 
        return send_file(consts.GENETATE_EXPORT_PATH, as_attachment=True)


# 「export_histories」のためのビュー関数(=URLエンドポイント)を宣言・定義する.
@view.route("/export_histories", methods=["GET", "POST"])
def export_histories():
    # 関数内で使用する変数・オブジェクトを宣言・定義する.
    exprt_hist_form = ExportHistoryForm()

    # 該当のURLエンドポイントに入ったことをロギングする.
    rslt = se.etc.logging__info("view at /export_words")

    # ロギングに失敗したら, 例外を発生させる.
    if rslt == "NG":
        raise InternalServerError

    # セッション未作成ならば, ホーム画面のページヘリダイレクトする.
    if not session:
        return redirect(url_for("view.home"))

    # セッション失効or未初期化ならば, ホーム画面のページヘリダイレクトする.
    if "is-admin-enter" not in session:
        return redirect(url_for("view.home"))

    # 管理者未入室の状態ならば, ホーム画面のページヘリダイレクトする.
    if session["is-admin-enter"] == False:
        return redirect(url_for("view.home"))

    if request.method == "GET":
        # セッションに現在ページの情報を設定して,
        # Flaskフォームと共にテンプレートを返す.
        session["referrer-page"] = "view.export_histories"
        return render_template("export_histories.html", form=exprt_hist_form)

    if request.method == "POST":
        # 直前に, GETメソッドで該当ページを取得しているかを調べる.
        # 取得していなければ, 強制的に現在ページへリダイレクトする.
        if session["referrer-page"] != "view.export_histories":
            return redirect(url_for("view.export_histories"))

        # フォームの取消ボタンが押されたら, 直前画面のページヘリダイレクトする.
        if exprt_hist_form.cancel.data:
            return redirect(url_for("view.admin_dashboard"))

        # ID昇順で, 全ての履歴レコードをDBから取得する.
        hists = db_session.query(History).filter(History.is_exclude==False).order_by(History.id.asc()).all()
        db_session.close()

        # DBから取得した履歴レコードの内容をXMLファイルに書き込むための準備をする.
        root = ET.Element("History-Dictionary")
        for hist in hists:
            hist_elm = ET.SubElement(root, "History-Entry")
            ET.SubElement(hist_elm, "first-character").text = hist.staff_message
            ET.SubElement(hist_elm, "characters-count").text = hist.application_message
            ET.SubElement(hist_elm, "staff-name").text = hist.staff_name
            ET.SubElement(hist_elm, "staff-kana-name").text = hist.staff_kana_name
            ET.SubElement(hist_elm, "created-at").text = se.etc.convert_datetime_string_to_display_style(hist.created_at)
            ET.SubElement(hist_elm, "renew-date-time").text = se.etc.convert_datetime_string_to_display_style(hist.updated_at)
            ET.SubElement(hist_elm, "is-hidden").text = "はい" if hist.is_hidden == "yes" else "いいえ"
            ET.SubElement(hist_elm, "is-exclude").text = "いいえ"

        # XML文書内容を読み易いように整形する.
        xml_txt = MD.parseString(ET.tostring(root, "utf-8")).toprettyxml(indent="   ")

        # 書出し先ファイルが既に存在すれば, それを削除する.
        if os.path.exists(consts.HISTORY_EXPORT_PATH):
            os.remove(consts.HISTORY_EXPORT_PATH)

        # 書出し先ファイルを新規作成して, 先のXML文書内容を書き込んで閉じる. 
        with open(consts.HISTORY_EXPORT_PATH, 'x', encoding='UTF-8') as xml_fl:
             xml_fl.write(xml_txt)

        # 書出し先ファイルをクライアントへ送信する. 
        return send_file(consts.HISTORY_EXPORT_PATH, as_attachment=True)


# 「export_enters_or_exits」のためのビュー関数(=URLエンドポイント)を宣言・定義する.
@view.route("/export_enters_or_exits", methods=["GET", "POST"])
def export_enters_or_exits():
    # 関数内で使用する変数・オブジェクトを宣言・定義する.
    fl_buf = []
    exprt_entr_or_exit_form = ExportEnterOrExitForm()

    # 該当のURLエンドポイントに入ったことをロギングする.
    rslt = se.etc.logging__info("view at /export_enters_or_exits")

    # ロギングに失敗したら, 例外を発生させる.
    if rslt == "NG":
        raise InternalServerError

    # セッション未作成ならば, ホーム画面のページヘリダイレクトする.
    if not session:
        return redirect(url_for("view.home"))

    # セッション失効or未初期化ならば, ホーム画面のページヘリダイレクトする.
    if "is-admin-enter" not in session:
        return redirect(url_for("view.home"))

    # 管理者未入室の状態ならば, ホーム画面のページヘリダイレクトする.
    if session["is-admin-enter"] == False:
        return redirect(url_for("view.home"))

    if request.method == "GET":
        # セッションに現在ページの情報を設定して,
        # Flaskフォームと共にテンプレートを返す.
        session["referrer-page"] = "view.export_enters_or_exits"
        return render_template("export_enters_or_exits.html", form=exprt_entr_or_exit_form)

    if request.method == "POST":
        # 直前に, GETメソッドで該当ページを取得しているかを調べる.
        # 取得していなければ, 強制的に現在ページへリダイレクトする.
        if session["referrer-page"] != "view.export_enters_or_exits":
            return redirect(url_for("view.export_enters_or_exits"))

        # フォームの取消ボタンが押されたら, 直前画面のページヘリダイレクトする.
        if exprt_entr_or_exit_form.cancel.data:
            return redirect(url_for("view.admin_dashboard"))

        # ID昇順で, 全ての入退レコードをDBから取得する.
        ents_or_exts = db_session.query(EnterOrExit).filter(EnterOrExit.is_exclude==False).order_by(EnterOrExit.id.asc()).all()
        db_session.close()

        # DBから取得した入退レコードの内容を変換・整形して配列に格納する.
        for ent_or_ext in ents_or_exts:
            stff_nm = ent_or_ext.staff_name
            stff_kn_nm = ent_or_ext.staff_kana_name
            if ent_or_ext.reason == "clock-in":
                rsn = "出勤"
            elif ent_or_ext.reason == "return-to-out":
                rsn = "外出戻り"
            elif ent_or_ext.reason == "after-break":
                rsn = "休憩明け"
            elif ent_or_ext.reason == "clock-out":
                rsn = "退勤"
            elif ent_or_ext.reason == "out":
                rsn = "外出"
            elif ent_or_ext.reason == "break":
                rsn = "休憩"
            elif ent_or_ext.reason == "forget-or-revocation":
                rsn = "忘却or失効"
            elif ent_or_ext.reason == "application-termination":
                rsn = "アプリ終了"
            else:
                rsn = "その他(分類不明)"
            dttm1 = se.etc.convert_datetime_string_to_display_style(ent_or_ext.enter_or_exit_at)
            dttm2 = se.etc.convert_datetime_string_to_display_style(ent_or_ext.created_at)
            dttm3 = se.etc.convert_datetime_string_to_display_style(ent_or_ext.updated_at)
            is_hddn = "はい" if ent_or_ext.is_hidden == "yes" else "いいえ"
            is_excld = "いいえ"
            fl_rcd = (stff_nm + "," + stff_kn_nm + "," + rsn + ","
                      + dttm1 + "," + dttm2 + "," + dttm3 + "," + is_hddn + "," + is_excld + "\n")
            fl_buf.append(fl_rcd)

        # 書出し先ファイルが既に存在すれば, それを削除する.
        if os.path.exists(consts.ENTER_OR_EXIT_EXPORT_PATH):
            os.remove(consts.ENTER_OR_EXIT_EXPORT_PATH)

        # 書出し先ファイルを新規作成して, 先の配列の内容を書き込んで閉じる.
        fl = open(consts.ENTER_OR_EXIT_EXPORT_PATH, 'x', encoding='UTF-8')
        fl.writelines(fl_buf)
        fl.close()

        # 書出し先ファイルをクライアントへ送信する. 
        return send_file(consts.ENTER_OR_EXIT_EXPORT_PATH, as_attachment=True)


# 「retrieve_generate」のためのビュー関数(=URLエンドポイント)を宣言・定義する.
@view.route("/retrieve_generate", methods=["GET", "POST"])
def retrieve_generate():
    # 関数内で使用する変数・オブジェクトを宣言・定義する.
    rtrv_gen_form = RetrieveGenerateForm()

    # 該当のURLエンドポイントに入ったことをロギングする.
    rslt = se.etc.logging__info("view at /retrieve_generate")

    # ロギングに失敗したら, 例外を発生させる.
    if rslt == "NG":
        raise InternalServerError

    # セッション未作成ならば, ホーム画面のページヘリダイレクトする.
    if not session:
        return redirect(url_for("view.home"))

    # セッション失効or未初期化ならば, ホーム画面のページヘリダイレクトする.
    if "is-admin-enter" not in session:
        return redirect(url_for("view.home"))

    # 管理者未入室の状態ならば, ホーム画面のページヘリダイレクトする.
    if session["is-admin-enter"] == False:
        return redirect(url_for("view.home"))

    # [show_generates][search_generates]ページを介さずに,
    # 不正アクセスされたら, 直前画面のページヘリダイレクトする.
    if "hidden-retrieve-item-id" not in session:
        return redirect(url_for(session["referrer-page"]))

    if request.method == "GET":
        # セッションに現在ページの情報を設定して,
        # Flaskフォームと共にテンプレートを返す.
        session["referrer-page"] = "view.retrieve_generate"
        return render_template("retrieve_generate.html", form=rtrv_gen_form)

    if request.method == "POST":
        # 直前に, GETメソッドで該当ページを取得しているかを調べる.
        # 取得していなければ, 強制的に現在ページへリダイレクトする.
        if session["referrer-page"] != "view.retrieve_generate":
            return redirect(url_for("view.retrieve_generate"))

        # フォームの取消ボタンが押されたら, 直前画面のページヘリダイレクトする.
        if rtrv_gen_form.cancel.data:
            return redirect(url_for("view.admin_dashboard"))

        # 指定IDの生成レコードをDBから取得する.
        gen = (
        db_session.query(Generate).filter(Generate.id == session["hidden-retrieve-item-id"]).first()
        )
        db_session.close()

        # もし生成レコードと関連付けられている生成ファイルが存在しなければ,
        # エラーメッセージを設定して, 空のフォームと共にテンプレートを返す.
        if not se.etc.check_exist_file(gen.generated_file_path):
            flash("生成ファイルが存在しません, ファイルが削除済みか破損しています.")
            return render_template("retrieve_generate.html", form=rtrv_gen_form)

        # 生成ファイルをクライアントへ送信する.
        return send_file(gen.generated_file_path, as_attachment=True)


# 「reset_database」のためのビュー関数(=URLエンドポイント)を宣言・定義する.
@view.route("/reset_database", methods=["GET", "POST"])
def reset_database():
    # 関数内で使用する変数・オブジェクトを宣言・定義する.
    rst_db_form = ResetDatabaseForm()

    # 該当のURLエンドポイントに入ったことをロギングする.
    rslt = se.etc.logging__info("view at /reset_database")

    # ロギングに失敗したら, 例外を発生させる.
    if rslt == "NG":
        raise InternalServerError

    # セッション未作成ならば, ホーム画面のページヘリダイレクトする.
    if not session:
        return redirect(url_for("view.home"))

    # セッション失効or未初期化ならば, ホーム画面のページヘリダイレクトする.
    if "is-admin-enter" not in session:
        return redirect(url_for("view.home"))

    # 管理者未入室の状態ならば, ホーム画面のページヘリダイレクトする.
    if session["is-admin-enter"] == False:
        return redirect(url_for("view.home"))

    if request.method == "GET":
        # セッションに現在ページの情報を設定して,
        # Flaskフォームと共にテンプレートを返す.
        session["referrer-page"] = "view.reset_database"
        return render_template("reset_database.html", form=rst_db_form)

    if request.method == "POST":
        # 直前に, GETメソッドで該当ページを取得しているかを調べる.
        # 取得していなければ, 強制的に現在ページへリダイレクトする.
        if session["referrer-page"] != "view.reset_database":
            return redirect(url_for("view.reset_database"))

        # フォームの取消ボタンが押されたら, 初期状態のフォームと共にテンプレートを返す.
        if rst_db_form.cancel.data:
            rst_db_form.words.data = False
            rst_db_form.themes.data = False
            rst_db_form.categories.data = False
            rst_db_form.knowledges.data = False
            rst_db_form.rules.data = False
            rst_db_form.reactions.data = False
            rst_db_form.generates.data = False
            rst_db_form.histories.data = False
            rst_db_form.enters_or_exits.data = False
            rst_db_form.staffs.data = False
            return render_template("reset_database.html", form=rst_db_form)

        # フォームのチェックボックスに全くチェックが入っていない場合の処理をする.
        if (not rst_db_form.words.data and
            not rst_db_form.themes.data and
            not rst_db_form.categories.data and
            not rst_db_form.knowledges.data and
            not rst_db_form.rules.data and
            not rst_db_form.reactions.data and
            not rst_db_form.generates.data and
            not rst_db_form.histories.data and
            not rst_db_form.enters_or_exits.data and
            not rst_db_form.staffs.data):
            flash("DBをリセットしませんでした.")
            return render_template("reset_database.html", form=rst_db_form)

        # フォームのチェックが入っている箇所に対応するテーブルを削除する.
        if rst_db_form.words.data:
            db_session.query(Word).delete()
            db_session.close()
        if rst_db_form.themes.data:
            db_session.query(Theme).delete()
            db_session.close()
        if rst_db_form.categories.data:
            db_session.query(Category).delete()
            db_session.close()
        if rst_db_form.knowledges.data:
            db_session.query(Knowledge).delete()
            db_session.close()
        if rst_db_form.rules.data:
            db_session.query(Rule).delete()
            db_session.close()
        if rst_db_form.reactions.data:
            db_session.query(Reaction).delete()
            db_session.close()
        if rst_db_form.generates.data:
            db_session.query(Generate).delete()
            db_session.close()
        if rst_db_form.histories.data:
            db_session.query(History).delete()
            db_session.close()
        if rst_db_form.enters_or_exits.data:
            db_session.query(EnterOrExit).delete()
            db_session.close()
        if rst_db_form.staffs.data:
            db_session.query(Staff).delete()
            db_session.close()

        # フォームを初期状態にし, 完了メッセージを設定してテンプレートを返す.
        rst_db_form.words.data = False
        rst_db_form.themes.data = False
        rst_db_form.categories.data = False
        rst_db_form.knowledges.data = False
        rst_db_form.rules.data = False
        rst_db_form.reactions.data = False
        rst_db_form.generates.data = False
        rst_db_form.histories.data = False
        rst_db_form.enters_or_exits.data = False
        rst_db_form.staffs.data = False
        flash("DBをリセットしました.")
        return render_template("reset_database.html", form=rst_db_form)


# 「settings」のためのビュー関数(=URLエンドポイント)を宣言・定義する.
@view.route("/settings", methods=["GET", "POST"])
def settings():
    # 関数内で使用する変数・オブジェクトを宣言・定義する.
    config = configparser.ConfigParser()
    sttng_form = SettingForm()

    # 該当のURLエンドポイントに入ったことをロギングする.
    rslt = se.etc.logging__info("view at /settings")

    # ロギングに失敗したら, 例外を発生させる.
    if rslt == "NG":
        raise InternalServerError

    # セッション未作成ならば, ホーム画面のページヘリダイレクトする.
    if not session:
        return redirect(url_for("view.home"))

    # セッション失効or未初期化ならば, ホーム画面のページヘリダイレクトする.
    if "is-admin-enter" not in session:
        return redirect(url_for("view.home"))

    # 管理者未入室の状態ならば, ホーム画面のページヘリダイレクトする.
    if session["is-admin-enter"] == False:
        return redirect(url_for("view.home"))

    if request.method == "GET":
        # セッションに現在ページの情報を設定して,
        # Flaskフォームと共にテンプレートを返す.
        session["referrer-page"] = "view.settings"

        # もしも, 設定ファイルが存在しなければ, すべての項目がデフォルト値のファイルを作成する.
        if not os.path.exists(consts.SETTING_PATH):
            config["memory-size"] = {"short-term-memory-size" : consts.SHORT_TERM_MEMORY_SIZE_DEFAULT,
                                     "long-term-memory-size" : consts.LONG_TERM_MEMORY_SIZE_DEFAULT}
            config["cpu-or-gpu-power"] = {"learn-depth" : consts.LEARN_DEPTH_DEFAULT,
                                          "inference-and-speculation-depth" : consts.INFERENCE_AND_SPECULATION_DEPTH_DEFAULT}
            config["faster-processing"] = {"in-memorize" : consts.IN_MEMORIZE_DEFAULT,
                                           "dictionary-entries-integration" : consts.DICTIONARY_ENTRIES_INETEGRATION_DEFAULT}
            config["advanced"] = {"global-Information-sharing" : consts.GLOBAL_INFORMATION_SHARING_DEFAULT,
                                  "background-processing" : consts.BACKGROUND_PROCESSING_DEFAULT}
            config["others"] = {"policy-based-decisions" : consts.POLICY_BASED_DECISIONS_DEFAULT,
                                "personalized-conversations" : consts.PERSONALIZED_CONVERSATIONS_DEFAULT}
            with open(consts.SETTING_PATH, "w") as configfile:
                 config.write(configfile)

        # 設定ファイルの内容をflaskフォームに読み込んで, フォームと共にテンプレートを返す.
        # ※設定項目が消えていた場合, デフォルト値で各項目を復元する.
        config.read(consts.SETTING_PATH, encoding="utf-8")
        sttng_form.short_term_memory_size.data = config.get("memory-size", "short-term-memory-size", fallback=consts.SHORT_TERM_MEMORY_SIZE_DEFAULT)
        sttng_form.long_term_memory_size.data = config.get("memory-size", "long-term-memory-size", fallback=consts.LONG_TERM_MEMORY_SIZE_DEFAULT)
        sttng_form.learn_depth.data = config.get("cpu-or-gpu-power", "learn-depth", fallback=consts.LEARN_DEPTH_DEFAULT)
        sttng_form.inference_and_speculation_depth.data = config.get("cpu-or-gpu-power", "inference-and-speculation-depth", fallback=consts.INFERENCE_AND_SPECULATION_DEPTH_DEFAULT)
        sttng_form.in_memorize.data = config.getboolean("faster-processing", "in-memorize", fallback=consts.IN_MEMORIZE_DEFAULT)
        sttng_form.dictionary_entries_integration.data = config.getboolean("faster-processing", "dictionary-entries-integration", fallback=consts.DICTIONARY_ENTRIES_INETEGRATION_DEFAULT)
        sttng_form.global_Information_sharing.data = config.getboolean("advanced", "global-Information-sharing", fallback=consts.GLOBAL_INFORMATION_SHARING_DEFAULT)
        sttng_form.background_processing.data = config.getboolean("advanced", "background-processing", fallback=consts.BACKGROUND_PROCESSING_DEFAULT)
        sttng_form.policy_based_decisions.data = config.getboolean("others", "policy-based-decisions", fallback=consts.POLICY_BASED_DECISIONS_DEFAULT)
        sttng_form.personalized_conversations.data = config.getboolean("others", "personalized-conversations", fallback=consts.PERSONALIZED_CONVERSATIONS_DEFAULT)
        return render_template("settings.html", form=sttng_form)

    if request.method == "POST":
        # 直前に, GETメソッドで該当ページを取得しているかを調べる.
        # 取得していなければ, 強制的に現在ページへリダイレクトする.
        if session["referrer-page"] != "view.settings":
            return redirect(url_for("view.settings"))

        # フォームの取消ボタンが押下されたら, 現在の設定内容を読み込んだフォームと共にテンプレートを返す.
        # ※各定項目が消えていた場合, デフォルト値で各項目を復元する.
        if sttng_form.cancel.data == True:
            config.read(consts.SETTING_PATH, encoding="utf-8")
            sttng_form.short_term_memory_size.data = config.get("memory-size", "short-term-memory-size", fallback=consts.SHORT_TERM_MEMORY_SIZE_DEFAULT)
            sttng_form.long_term_memory_size.data = config.get("memory-size", "long-term-memory-size", fallback=consts.LONG_TERM_MEMORY_SIZE_DEFAULT)
            sttng_form.learn_depth.data = config.get("cpu-or-gpu-power", "learn-depth", fallback=consts.LEARN_DEPTH_DEFAULT)
            sttng_form.inference_and_speculation_depth.data = config.get("cpu-or-gpu-power", "inference-and-speculation-depth", fallback=consts.INFERENCE_AND_SPECULATION_DEPTH_DEFAULT)
            sttng_form.in_memorize.data = config.getboolean("faster-processing", "in-memorize", fallback=consts.IN_MEMORIZE_DEFAULT)
            sttng_form.dictionary_entries_integration.data = config.getboolean("faster-processing", "dictionary-entries-integration", fallback=consts.DICTIONARY_ENTRIES_INETEGRATION_DEFAULT)
            sttng_form.global_Information_sharing.data = config.getboolean("advanced", "global-Information-sharing", fallback=consts.GLOBAL_INFORMATION_SHARING_DEFAULT)
            sttng_form.background_processing.data = config.getboolean("advanced", "background-processing", fallback=consts.BACKGROUND_PROCESSING_DEFAULT)
            sttng_form.policy_based_decisions.data = config.getboolean("others", "policy-based-decisions", fallback=consts.POLICY_BASED_DECISIONS_DEFAULT)
            sttng_form.personalized_conversations.data = config.getboolean("others", "personalized-conversations", fallback=consts.PERSONALIZED_CONVERSATIONS_DEFAULT)
            return render_template("settings.html", form=sttng_form)

        # flaskフォームの内容を読み込んで, 設定ファイルを上書きする.
        config.read(consts.SETTING_PATH, encoding="utf-8")
        config.set("memory-size", "short-term-memory-size", sttng_form.short_term_memory_size.data)
        config.set("memory-size", "long-term-memory-size", sttng_form.long_term_memory_size.data)
        config.set("cpu-or-gpu-power", "learn-depth", sttng_form.learn_depth.data)
        config.set("cpu-or-gpu-power", "inference-and-speculation-depth", sttng_form.inference_and_speculation_depth.data)
        config.set("faster-processing", "in-memorize", str(sttng_form.in_memorize.data))
        config.set("faster-processing", "dictionary-entries-integration", str(sttng_form.dictionary_entries_integration.data))
        config.set("advanced", "global-Information-sharing", str(sttng_form.global_Information_sharing.data))
        config.set("advanced", "background-processing", str(sttng_form.background_processing.data))
        config.set("others", "policy-based-decisions", str(sttng_form.policy_based_decisions.data))
        config.set("others", "personalized-conversations", str(sttng_form.personalized_conversations.data))
        with open(consts.SETTING_PATH, 'w') as configfile:
             config.write(configfile)

        # 完了メッセージを設定してテンプレートを返す.
        flash("設定値を上書きしました.")
        return render_template("settings.html", form=sttng_form)


# エラー処理のためのカスタム関数を宣言・定義する.
# ※指定URLにクエリパラメータが含まれている場合は400番エラーを返す.
# ※この関数は, 都度, リクエストの直前に呼び出される.
@view.before_request
def check_query_parameters():
    if request.args:
        raise NotFound