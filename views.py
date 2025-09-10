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
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.exceptions import (
     BadRequest,
     NotFound,
     InternalServerError
)
from markupsafe import escape

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
     LearnFactForm,
     LearnRuleForm,
     LearnReactionForm,
     GenerateForm,
     RegisterEnterOrExitForm,
     RegisterStaffForm,
     SearchWordForm,
     SearchThemeForm,
     SearchCategoryForm,
     SearchFactForm,
     SearchRuleForm,
     SearchReactionForm,
     SearchGenerateForm,
     SearchHistoryForm,
     SearchEnterOrExitForm,
     SearchStaffForm,
     ModifyWordForm,
     ModifyThemeForm,
     ModifyCategoryForm,
     ModifyFactForm,
     ModifyRuleForm,
     ModifyReactionForm,
     ModifyEnterOrExitForm,
     ModifyStaffForm,
     DetailWordForm,
     DetailThemeForm,
     DetailCategoryForm,
     DetailFactForm,
     DetailRuleForm,
     DetailReactionForm,
     DetailGenerateForm,
     DetailHistoryForm,
     DetailEnterOrExitForm,
     DetailStaffForm,
     ImportWordForm,
     ImportThemeForm,
     ImportCategoryForm,
     ImportFactForm,
     ImportRuleForm,
     ImportReactionForm,
     ImportGenerateForm,
     ImportEnterOrExitForm,
     ExportWordForm,
     ExportThemeForm,
     ExportCategoryForm,
     ExportFactForm,
     ExportRuleForm,
     ExportReactionForm,
     ExportGenerateForm,
     ExportHistoryForm,
     ExportEnterOrExitForm,
     RetrieveGenerateForm,
     EnvironmentSettingForm,
     SecuritySettingForm,
     ResetDatabaseForm
)

# 各種モデルをインポートする.
from models import (
     db_session,
     Word,
     Theme,
     Category,
     Fact,
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

# Sunie独自の各種エンジンを生成する.
cr_engn = appcore.CoreEngine()
vis_engn = appcore.VisualEngine()
aud_engn = appcore.AudioEngine()
vid_engne = appcore.VideoEngine()

# アプリのログ(=動作記録)の保存を開始する.
cr_engn.etc.logging__start(consts.LOGGING_PATH)




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
    dcid_pttrn = cr_engn.etc.random_select(hm_back_cnddt)
    crrnt_hr = cr_engn.etc.retrieve_current_hour_as_integer("JST")
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
    rslt = cr_engn.etc.logging__info("view at /home")

    # ロギングに失敗したら, 例外を発生させる.
    if rslt == "NG":
        raise InternalServerError

    # アプリケーションの前回終了時から,
    # 未退室のままになっている職員を特定し,
    # 現在時刻をもって自動の打刻を済ませる.
    if is_frst_rqst:
        stffs = db_session.query(Staff).filter(Staff.is_exclude == False).order_by(Staff.id.asc()).all()
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
                   crrnt_dttm = cr_engn.etc.retrieve_current_datetime_as_datetime_object("JST")
                   db_session.add(EnterOrExit(staff_name=stff.name,
                                              staff_kana_name=stff.kana_name,
                                              reason="application-termination",
                                              enter_or_exit_at=crrnt_dttm,
                                              enter_or_exit_at_second="00",
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
    rslt = cr_engn.etc.logging__info("view at /usage")

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
    rslt = cr_engn.etc.logging__info("view at /guide")

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
    rslt = cr_engn.etc.logging__info("view at /staff_enter")

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
        stff = db_session.query(Staff).filter(Staff.name==stff_nm).first()
        db_session.close()

        # 指定職員が存在しない場合には, エラーメッセージを設定して,
        # 入力内容を空にしたFlaskフォームと共にテンプレートを返す.
        if stff is None:
            session["staff-enter-fault"] = str(int(session["staff-enter-fault"]) + 1)
            flash("その職員は登録されていません.")
            return render_template("staff_enter.html", form=stff_entr_form, happen_error=True)

        # パスワード誤りがある場合には, エラーメッセージを設定して,
        # 入力内容を空にしたFlaskフォームと共にテンプレートを返す.
        # if psswrd != stff.pass_word:
        if not check_password_hash(stff.hashed_password, psswrd):
            session["staff-enter-fault"] = str(int(session["staff-enter-fault"]) + 1)
            flash("そのパスワードは間違っています.")
            return render_template("staff_enter.html", form=stff_entr_form, happen_error=True)

        # 前回の入室後に, 退室処理が正常に実行されていない場合には, 自動退室記録をDBに登録する.
        ent_or_ext = (
        db_session.query(EnterOrExit).filter(EnterOrExit.staff_name==stff.name).order_by(EnterOrExit.id.desc()).first()
        )
        db_session.close()

        if ent_or_ext is not None:
            if (ent_or_ext.reason == "clock-in" or
                ent_or_ext.reason == "return-to-out" or
                ent_or_ext.reason == "after-break"):
                crrnt_dttm = cr_engn.etc.retrieve_current_datetime_as_datetime_object("JST")
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
        crrnt_dttm = cr_engn.etc.retrieve_current_datetime_as_datetime_object("JST")
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
    rslt = cr_engn.etc.logging__info("view at /staff_exit")

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
        crrnt_dttm = cr_engn.etc.retrieve_current_datetime_as_datetime_object("JST")
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
    config = configparser.ConfigParser()
    admn_entr_form = AdminEnterForm()

    # 該当のURLエンドポイントに入ったことをロギングする.
    rslt = cr_engn.etc.logging__info("view at /admin_enter")

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

        # もしも, 機密設定ファイルが存在しなければ, 全ての項目がデフォルト値のファイルを作成する.
        if not os.path.exists(consts.SECURITY_SETTING_PATH):
            config["security"] = {"hashed-password" : generate_password_hash(consts.ADMIN_INITIAL_PASSWORD)}
            with open(consts.SECURITY_SETTING_PATH, "w") as configfile:
                 config.write(configfile)

        # 機密設定ファイルの内容を読み込む.
        # ※各設定項目が消失していた場合, デフォルト値で各項目を復元する.
        config.read(consts.SECURITY_SETTING_PATH, encoding="utf-8")
        hshd_psswrd = config.get("security", "hashed-password", fallback=generate_password_hash(consts.ADMIN_INITIAL_PASSWORD))

        # パスワードに誤りがある場合, エラーメッセージを設定して, フォームと共にテンプレートを返す.
        if not check_password_hash(hshd_psswrd, psswrd):
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
    rslt = cr_engn.etc.logging__info("view at /admin_exit")

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
    rslt = cr_engn.etc.logging__info("view at /staff_dashboard")

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
    rslt = cr_engn.etc.logging__info("view at /admin_dashboard")

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
    stff_wrds = []
    stff_fcts = []
    stff_rls = []
    send_form = SendForm()

    # 該当のURLエンドポイントに入ったことをロギングする.
    rslt = cr_engn.etc.logging__info("view at /send")

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
            send_form.text_message.data = ""
            return render_template("send.html", form=send_form)

        # flaskフォームに入力・記憶されている内容をバリデーションする.
        # 基準を満たさない場合, フォームと共にテンプレートを返す.
        if send_form.text_message.data == "":
            flash("メッセージ本文が入力されていません.")
            return render_template("send.html", form=send_form, happen_error=True)
        spltd_ln_txts = cr_engn.reg.split_text_message_on_delimiter(send_form.text_message.data)
        if len(spltd_ln_txts) == 0:
            flash("改行コードのみの入力は無効です.")
            return render_template("send.html", form=send_form, happen_error=True)

        # 職員からのテキストメッセージを構成する全ての語句情報をDB検索して抽出する.
        # 英文などの空白で区切られている文を処理してから, 文字種を基準に処理する.
        for spltd_ln_txt in spltd_ln_txts:
            char_cnt = 0
            wrd_in_txt = (
            db_session.query(Word)
            .filter(Word.characters_count == len(spltd_ln_txt))
            .filter(Word.first_character == spltd_ln_txt[0])
            .filter(Word.last_character == spltd_ln_txt[-1])
            .filter(Word.spell_and_header == spltd_ln_txt)
            .order_by(Word.id.desc())
            .first()
            )
            if wrd_in_txt is not None:
                stff_wrds.append(wrd_in_txt)
                continue
            spltd_typ_txt = cr_engn.reg.split_text_message_character_type(spltd_ln_txt)
            for spltd_typ_wrd in spltd_typ_txt:
                wrd_in_txt = (
                db_session.query(Word)
                .filter(Word.characters_count == len(spltd_typ_wrd))
                .filter(Word.first_character == spltd_typ_wrd[0])
                .filter(Word.last_character == spltd_typ_wrd[-1])
                .filter(Word.spell_and_header == spltd_typ_wrd)
                .order_by(Word.id.desc())
                .first()
                )
                if wrd_in_txt is not None:
                    stff_wrds.append(wrd_in_txt)
                    char_cnt += len(spltd_typ_wrd)
                    continue
                txt_tmp = spltd_ln_txt[char_cnt:]
                i_sntnl = len(txt_tmp)
                j_sntnl = -1
                i = 0
                j = len(txt_tmp)
                while i < i_sntnl:
                      while j > j_sntnl:
                            txt_tmp2 = txt_tmp[i:j]
                            if txt_tmp2 != "":
                                wrd_in_txt = (
                                db_session.query(Word)
                                .filter(Word.characters_count == len(txt_tmp2))
                                .filter(Word.first_character == txt_tmp2[0])
                                .filter(Word.last_character == txt_tmp2[-1])
                                .filter(Word.spell_and_header == txt_tmp2)
                                .order_by(Word.id.desc())
                                .first()
                                )
                                if wrd_in_txt is not None:
                                    stff_wrds.append(wrd_in_txt)
                                    i += len(txt_tmp2)
                                    j = len(txt_tmp)
                                    break
                            j -= 1
                            continue
                      else:
                          i += 1
                          continue
                else:
                    break

        for stff_wrd in stff_wrds:
            fct_in_txt = (
            db_session.query(Fact.spell_and_header == stff_wrd.spell_and_header)
            .filter()
            .order_by(Fact.id.desc())
            .first()
            )
            if fct_in_txt is not None:
                stff_fcts.append(fct_in_txt)
                continue

        for stff_wrd in stff_wrds:
            rl_in_txt = (
            db_session.query(Rule.spell_and_header == stff_wrd.spell_and_header)
            .filter()
            .order_by(Rule.id.desc())
            .first()
            )
            if rl_in_txt is not None:
                stff_rls.append(rl_in_txt)
                continue

        print(stff_wrds)
        print(stff_fcts)
        print(stff_rls)

        # sunieエンジンに職員への返信テキスト(=メッセージ)を生成させる.
        # stff_fct, stff_intnt, stff_sntmnt = cr_engn.reg.analyze_words_in_texts(stff_wrds_in_txts)
        # app_wrds_in_txts= cr_engn.reg.generate_words_in_texts(stff_fct, stff_intnt, stff_sntmnt)
        # app_txt_msg = cr_engn.reg.asemble_text_message(app_wrds_in_txts)
        app_txt_msg = cr_engn.reg.asemble_text_message()

        # 履歴情報をレコードとして, DBに保存・登録する.
        stff_txt_msg = send_form.text_message.data
        crrnt_dttm = cr_engn.etc.retrieve_current_datetime_as_datetime_object("JST")
        db_session.add(History(staff_name=session["enter-name"],
                               staff_kana_name=session["enter-kana-name"],
                               staff_text_message=stff_txt_msg,
                               application_text_message=app_txt_msg,
                               created_at=crrnt_dttm,
                               updated_at=crrnt_dttm,
                               is_hidden=False,
                               is_exclude=False
                              ))
        db_session.commit()
        db_session.close()

        # 職員からの呼掛け内容とエンジン処理結果(=返信内容)を,
        # セッションに設定して, 返信ページへリダイレクトする.
        session["staff-text-message"] = stff_txt_msg
        session["application-text-message"] = app_txt_msg
        return redirect(url_for("view.reply"))


# 「reply」のためのビュー関数(=URLエンドポイント)を宣言・定義する.
@view.route("/reply", methods=["GET"])
def reply():
    # 該当のURLエンドポイントに入ったことをロギングする.
    rslt = cr_engn.etc.logging__info("view at /reply")

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
                               staff_text_message=session["staff-text-message"],
                               application_text_message=session["application-text-message"])


# 「learn_word」のためのビュー関数(=URLエンドポイント)を宣言・定義する.
@view.route("/learn_word", methods=["GET", "POST"])
def learn_word():
    # 関数内で使用する変数・オブジェクトを宣言・定義する.
    lrn_wrd_form = LearnWordForm()

    # 該当のURLエンドポイントに入ったことをロギングする.
    rslt = cr_engn.etc.logging__info("view at /learn_word")

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
            lrn_wrd_form.mean_and_body.data = ""
            lrn_wrd_form.intent.data = ""
            lrn_wrd_form.sentiment.data = ""
            lrn_wrd_form.sentiment_support.data = ""
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
        if lrn_wrd_form.mean_and_body.data == "":
            flash("意味&内容が入力されていません.")
            return render_template("learn_word.html", form=lrn_wrd_form, happen_error=True)
        if lrn_wrd_form.theme_tag.data == "":
            flash("主題タグが入力されていません.")
            return render_template("learn_word.html", form=lrn_wrd_form, happen_error=True)
        if lrn_wrd_form.intent.data == "":
            flash("意図が選択されていません.")
            return render_template("learn_word.html", form=lrn_wrd_form, happen_error=True)
        if lrn_wrd_form.sentiment.data == "":
            flash("感情が選択されていません.")
            return render_template("learn_word.html", form=lrn_wrd_form, happen_error=True)
        if lrn_wrd_form.sentiment_support.data == "":
            flash("感情補助が選択されていません.")
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
        cncpt_n_ntn = cr_engn.learn_word(lrn_wrd_form.spell_and_header.data,
                                    lrn_wrd_form.mean_and_body.data)

        # 語句情報をレコードとして, DBに保存・登録する.
        crrnt_dttm = cr_engn.etc.retrieve_current_datetime_as_datetime_object("JST")
        db_session.add(Word(spell_and_header=escape(lrn_wrd_form.spell_and_header.data),
                            mean_and_body=escape(lrn_wrd_form.mean_and_body.data),
                            concept_and_notion=cncpt_n_ntn,
                            theme_tag=escape(lrn_wrd_form.theme_tag.data),
                            intent=lrn_wrd_form.intent.data,
                            sentiment=lrn_wrd_form.sentiment.data,
                            sentiment_support=lrn_wrd_form.sentiment_support.data,
                            strength=lrn_wrd_form.strength.data,
                            part_of_speech=lrn_wrd_form.part_of_speech.data,
                            first_character=lrn_wrd_form.spell_and_header.data[0],
                            last_character=lrn_wrd_form.spell_and_header.data[-1],
                            characters_count=len(lrn_wrd_form.spell_and_header.data),
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
    rslt = cr_engn.etc.logging__info("view at /learn_theme")

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
            lrn_thm_form.mean_and_body.data = ""
            lrn_thm_form.category_tag.data = ""
            lrn_thm_form.is_hidden.data = False
            lrn_thm_form.is_exclude.data = False
            return render_template("learn_theme.html", form=lrn_thm_form)

        # flaskフォームに入力・記憶されている内容をバリデーションする.
        # 基準を満たさない場合は, 元のフォームと共にテンプレートを返す.
        if lrn_thm_form.spell_and_header.data == "":
            flash("綴り&見出しが入力されていません.")
            return render_template("learn_theme.html", form=lrn_thm_form, happen_error=True)
        if lrn_thm_form.mean_and_body.data == "":
            flash("意味&内容が入力されていません.")
            return render_template("learn_theme.html", form=lrn_thm_form, happen_error=True)
        if lrn_thm_form.category_tag.data == "":
            flash("分類タグが入力されていません.")
            return render_template("learn_theme.html", form=lrn_thm_form, happen_error=True)
        if lrn_thm_form.is_hidden.data == "":
            flash("秘匿の是非が選択されていません.")
            return render_template("learn_word.html", form=lrn_thm_form, happen_error=True)
        if lrn_thm_form.is_exclude.data == "":
            flash("非処理の是非が選択されていません.")
            return render_template("learn_word.html", form=lrn_thm_form, happen_error=True)

        #@ ここで, 主題情報を学習するための各種の高度な計算を行う.
        cncpt_n_ntn = cr_engn.learn_theme(lrn_thm_form.spell_and_header.data,
                                     lrn_thm_form.mean_and_body.data)

        # 主題情報をレコードとして, DBに保存・登録する.
        crrnt_dttm = cr_engn.etc.retrieve_current_datetime_as_datetime_object("JST")
        db_session.add(Theme(spell_and_header=escape(lrn_thm_form.spell_and_header.data),
                             mean_and_body=escape(lrn_thm_form.mean_and_body.data),
                             concept_and_notion=cncpt_n_ntn,
                             category_tag=escape(lrn_thm_form.category_tag.data),
                             staff_name=session["enter-name"],
                             staff_kana_name=session["enter-kana-name"],
                             created_at=crrnt_dttm,
                             updated_at=crrnt_dttm,
                             is_hidden=(True if lrn_thm_form.is_hidden == "yes" else False),
                             is_exclude=(True if lrn_thm_form.is_exclude == "yes" else False)
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
    rslt = cr_engn.etc.logging__info("view at /learn_category")

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
            lrn_ctgr_form.mean_and_body.data = ""
            lrn_ctgr_form.parent_category_tag.data = ""
            lrn_ctgr_form.sibling_category_tag.data = ""
            lrn_ctgr_form.child_category_tag.data = ""
            lrn_ctgr_form.is_hidden = False
            lrn_ctgr_form.is_exclude = False
            return render_template("learn_category.html", form=lrn_ctgr_form)

        # flaskフォームに入力・記憶されている内容をバリデーションする.
        # 基準を満たさない場合は, 元のフォームと共にテンプレートを返す.
        if lrn_ctgr_form.spell_and_header.data == "":
            flash("綴り&見出しが入力されていません.")
            return render_template("learn_category.html", form=lrn_ctgr_form, happen_error=True)
        if lrn_ctgr_form.mean_and_body.data == "":
            flash("意味&内容が入力されていません.")
            return render_template("learn_category.html", form=lrn_ctgr_form, happen_error=True)
        if lrn_ctgr_form.parent_category_tag.data == "":
            flash("親分類タグが入力されていません.")
            return render_template("learn_category.html", form=lrn_ctgr_form, happen_error=True)
        if lrn_ctgr_form.sibling_category_tag.data == "":
            flash("兄弟分類タグが入力されていません.")
            return render_template("learn_category.html", form=lrn_ctgr_form, happen_error=True)
        if lrn_ctgr_form.child_category_tag.data == "":
            flash("子分類タグが入力されていません.")
            return render_template("learn_category.html", form=lrn_ctgr_form, happen_error=True)
        if lrn_ctgr_form.is_hidden.data == "":
            flash("秘匿の是非が選択されていません.")
            return render_template("learn_word.html", form=lrn_ctgr_form, happen_error=True)
        if lrn_ctgr_form.is_exclude.data == "":
            flash("非処理の是非が選択されていません.")
            return render_template("learn_word.html", form=lrn_ctgr_form, happen_error=True)

        #@ ここで, 分類情報を学習するための各種の高度な計算を行う.
        cncpt_n_ntn = cr_engn.learn_category(lrn_ctgr_form.spell_and_header.data,
                                        lrn_ctgr_form.mean_and_body.data)

        # 分類情報をレコードとして, DBに保存・登録する.
        crrnt_dttm = cr_engn.etc.retrieve_current_datetime_as_datetime_object("JST")
        db_session.add(Category(spell_and_header=escape(lrn_ctgr_form.spell_and_header.data),
                                mean_and_body=escape(lrn_ctgr_form.mean_and_body.data),
                                concept_and_notion=cncpt_n_ntn,
                                parent_category_tag=escape(lrn_ctgr_form.parent_category_tag.data),
                                sibling_category_tag=escape(lrn_ctgr_form.sibling_category_tag.data),
                                child_category_tag=escape(lrn_ctgr_form.child_category_tag.data),
                                staff_name=session["enter-name"],
                                staff_kana_name=session["enter-kana-name"],
                                created_at=crrnt_dttm,
                                updated_at=crrnt_dttm,
                                is_hidden=(True if lrn_ctgr_form.is_hidden == "yes" else False),
                                is_exclude=(True if lrn_ctgr_form.is_exclude == "yes" else False)
                               ))
        db_session.commit()
        db_session.close()

        # 完了メッセージを設定して, テンプレートを返す.
        flash("分類を学習しました.")
        return render_template("learn_category.html", form=lrn_ctgr_form)


# 「learn_fact」のためのビュー関数(=URLエンドポイント)を宣言・定義する.
@view.route("/learn_fact", methods=["GET", "POST"])
def learn_fact():
    # 関数内で使用する変数・オブジェクトを宣言・定義する.
    fl_lbl = ""
    img_sv_pth = ""
    snd_sv_pth = ""
    vdo_sv_pth = ""
    lrn_fct_form = LearnFactForm()

    # 該当のURLエンドポイントに入ったことをロギングする.
    rslt = cr_engn.etc.logging__info("view at /learn_fact")

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
        session["referrer-page"] = "view.learn_fact"
        return render_template("learn_fact.html", form=lrn_fct_form)

    if request.method == "POST":
        # 直前に, GETメソッドで該当ページを取得しているかを調べる.
        # 取得していなければ, 強制的に現在ページへリダイレクトする.
        if session["referrer-page"] != "view.learn_fact":
            return redirect(url_for("view.staff_dashboard"))

        # フォームの取消ボタンが押下されたら, 空のフォームと共にテンプレートを返す.
        if lrn_fct_form.cancel.data:
            lrn_fct_form.spell_and_header.data = ""
            lrn_fct_form.mean_and_body.data = ""
            lrn_fct_form.category_tag.data = ""
            lrn_fct_form.attached_image_file.data = ""
            lrn_fct_form.attached_sound_file.data = ""
            lrn_fct_form.attached_video_file.data = ""
            lrn_fct_form.is_hidden = False
            lrn_fct_form.is_exclude = False
            return render_template("learn_fact.html", form=lrn_fct_form)

        # flaskフォームに入力・記憶されている内容をバリデーションする.
        # 基準を満たさない場合は, 元のフォームと共にテンプレートを返す.
        if lrn_fct_form.spell_and_header.data == "":
            flash("綴り&見出しが入力されていません.")
            return render_template("learn_fact.html", form=lrn_fct_form, happen_error=True)
        if lrn_fct_form.mean_and_body.data == "":
            flash("意味&内容が入力されていません.")
            return render_template("learn_fact.html", form=lrn_fct_form, happen_error=True)
        if lrn_fct_form.category_tag.data == "":
            flash("分類タグが入力されていません.")
            return render_template("learn_fact.html", form=lrn_fct_form, happen_error=True)
        if lrn_fct_form.is_hidden.data == "":
            flash("秘匿の是非が選択されていません.")
            return render_template("learn_fact.html", form=lrn_fct_form, happen_error=True)
        if lrn_fct_form.is_exclude.data == "":
            flash("非処理の是非が選択されていません.")
            return render_template("learn_fact.html", form=lrn_fct_form, happen_error=True)

        #@ ここで, 事実情報を学習するための各種の高度な計算を行う.
        cncpt_n_ntn = cr_engn.learn_category(lrn_fct_form.spell_and_header.data,
                                        lrn_fct_form.mean_and_body.data)

        # 事実情報をレコードとして, DBに保存・登録する.
        fl_lbl = cr_engn.etc.retrieve_current_time_as_file_label()
        crrnt_dttm = cr_engn.etc.retrieve_current_datetime_as_datetime_object("JST")
        img_sv_pth = cr_engn.etc.save_file(lrn_fct_form.attached_image_file.data, consts.ARCHIVE_IMAGE_PATH, fl_lbl)
        snd_sv_pth = cr_engn.etc.save_file(lrn_fct_form.attached_sound_file.data, consts.ARCHIVE_SOUND_PATH, fl_lbl)
        vdo_sv_pth = cr_engn.etc.save_file(lrn_fct_form.attached_video_file.data, consts.ARCHIVE_VIDEO_PATH, fl_lbl)
        db_session.add(Fact(spell_and_header=escape(lrn_fct_form.spell_and_header.data),
                            mean_and_body=escape(lrn_fct_form.mean_and_body.data),
                            concept_and_notion=cncpt_n_ntn,
                            category_tag=escape(lrn_fct_form.category_tag.data),
                            archived_image_file_path=img_sv_pth,
                            archived_sound_file_path=snd_sv_pth,
                            archived_video_file_path=vdo_sv_pth,
                            staff_name=session["enter-name"],
                            staff_kana_name=session["enter-kana-name"],
                            created_at=crrnt_dttm,
                            updated_at=crrnt_dttm,
                            is_hidden=(True if lrn_fct_form.is_hidden == "yes" else False),
                            is_exclude=(True if lrn_fct_form.is_exclude == "yes" else False)
                            ))
        db_session.commit()
        db_session.close()

        # 完了メッセージを設定して, テンプレートを返す.
        flash("事実を学習しました.")
        return render_template("learn_fact.html", form=lrn_fct_form)


# 「learn_rule」のためのビュー関数(=URLエンドポイント)を宣言・定義する.
@view.route("/learn_rule", methods=["GET", "POST"])
def learn_rule():
    # 関数内で使用する変数・オブジェクトを宣言・定義する.
    lrn_rl_form = LearnRuleForm()

    # 該当のURLエンドポイントに入ったことをロギングする.
    rslt = cr_engn.etc.logging__info("view at /learn_rule")

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
            lrn_rl_form.mean_and_body.data = ""
            lrn_rl_form.category_tag.data = ""
            lrn_rl_form.inference_and_speculation_condition.data = ""
            lrn_rl_form.inference_and_speculation_result.data = ""
            lrn_rl_form.is_hidden.data = False
            lrn_rl_form.is_exclude.data = False
            return render_template("learn_rule.html", form=lrn_rl_form)

        # flaskフォームに入力・記憶されている内容をバリデーションする.
        # 基準を満たさない場合は, 元のフォームと共にテンプレートを返す.
        if lrn_rl_form.spell_and_header.data == "":
            flash("綴り&見出しが入力されていません.")
            return render_template("learn_rule.html", form=lrn_rl_form, happen_error=True)
        if lrn_rl_form.mean_and_body.data == "":
            flash("意味&内容が入力されていません.")
            return render_template("learn_rule.html", form=lrn_rl_form, happen_error=True)
        if lrn_rl_form.category_tag.data == "":
            flash("分類タグが入力されていません.")
            return render_template("learn_rule.html", form=lrn_rl_form, happen_error=True)
        if lrn_rl_form.inference_and_speculation_condition.data == "":
            flash("推論条件が入力されていません.")
            return render_template("learn_rule.html", form=lrn_rl_form, happen_error=True)
        if lrn_rl_form.inference_and_speculation_result.data == "":
            flash("推論結果が入力されていません.")
            return render_template("learn_rule.html", form=lrn_rl_form, happen_error=True)
        if lrn_rl_form.is_hidden.data == "":
            flash("秘匿の是非が選択されていません.")
            return render_template("learn_rule.html", form=lrn_rl_form, happen_error=True)
        if lrn_rl_form.is_exclude.data == "":
            flash("非処理の是非が選択されていません.")
            return render_template("learn_rule.html", form=lrn_rl_form, happen_error=True)

        #@ ここで, 規則情報を学習するための各種の高度な計算を行う.
        cncpt_n_ntn = cr_engn.learn_rule(lrn_rl_form.spell_and_header.data,
                                    lrn_rl_form.mean_and_body.data)

        # 規則情報をレコードとして, DBに保存・登録する.
        crrnt_dttm = cr_engn.etc.retrieve_current_datetime_as_datetime_object("JST")
        db_session.add(Rule(spell_and_header=escape(lrn_rl_form.spell_and_header.data),
                            mean_and_body=escape(lrn_rl_form.mean_and_body.data),
                            concept_and_notion=cncpt_n_ntn,
                            category_tag=escape(lrn_rl_form.category_tag.data),
                            inference_and_speculation_condition=escape(lrn_rl_form.inference_and_speculation_condition.data),
                            inference_and_speculation_result=escape(lrn_rl_form.inference_and_speculation_result.data),
                            staff_name=session["enter-name"],
                            staff_kana_name=session["enter-kana-name"],
                            created_at=crrnt_dttm,
                            updated_at=crrnt_dttm,
                            is_hidden=(True if lrn_rl_form.is_hidden == "yes" else False),
                            is_exclude=(True if lrn_rl_form.is_exclude == "yes" else False)
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
    rslt = cr_engn.etc.logging__info("view at /learn_reaction")

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
            lrn_rctn_form.mean_and_body.data = ""
            lrn_rctn_form.staff_psychology.data = ""
            lrn_rctn_form.scene_and_background.data = ""
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
        if lrn_rctn_form.mean_and_body.data == "":
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
        cncpt_n_ntn = cr_engn.learn_reaction(lrn_rctn_form.spell_and_header.data,
                                        lrn_rctn_form.mean_and_body.data)

        # 反応情報をレコードとして, DBに保存・登録する.
        crrnt_dttm = cr_engn.etc.retrieve_current_datetime_as_datetime_object("JST")
        db_session.add(Reaction(spell_and_header=escape(lrn_rctn_form.spell_and_header.data),
                                mean_and_body=escape(lrn_rctn_form.mean_and_body.data),
                                concept_and_notion=cncpt_n_ntn,
                                staff_psychology=escape(lrn_rctn_form.staff_psychology.data),
                                scene_and_background=escape(lrn_rctn_form.scene_and_background.data),
                                staff_example_text_message=escape(lrn_rctn_form.message_example_from_staff.data),
                                application_example_text_message=escape(lrn_rctn_form.message_example_from_application.data),
                                staff_name=session["enter-name"],
                                staff_kana_name=session["enter-kana-name"],
                                created_at=crrnt_dttm,
                                updated_at=crrnt_dttm,
                                is_hidden=(True if lrn_rctn_form.is_hidden == "yes" else False),
                                is_exclude=(True if lrn_rctn_form.is_exclude == "yes" else False)
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
    rslt = cr_engn.etc.logging__info("view at /generate")

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
            gen_form.mean_and_body.data = ""
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
        if gen_form.mean_and_body.data == "":
            flash("意味&内容が入力されていません.")
            return render_template("generate.html", form=gen_form, happen_error=True)
        if gen_form.is_hidden.data == "":
            flash("秘匿の是非が選択されていません.")
            return render_template("generate.html", form=gen_form, happen_error=True)
        if gen_form.is_exclude.data == "":
            flash("非処理の是非が選択されていません.")
            return render_template("generate.html", form=gen_form, happen_error=True)

        #@ ここで, 各種のデータファイルを生成するための各種の高度な計算を行う.
        gnrtd_fl_pth = cr_engn.generate_data_file(gen_form.spell_and_header.data,
                                             gen_form.mean_and_body.data)
        gnrtd_fl_pth = consts.DUMMY_FILE_PATH # 暫定的にダミーファイルのパスを使用する.

        # 生成情報をレコードとして, DBに保存・登録する.
        crrnt_dttm = cr_engn.etc.retrieve_current_datetime_as_datetime_object("JST")
        db_session.add(Generate(spell_and_header=escape(gen_form.spell_and_header.data),
                                mean_and_body=escape(gen_form.mean_and_body.data),
                                generated_file_path=gnrtd_fl_pth,
                                staff_name=session["enter-name"],
                                staff_kana_name=session["enter-kana-name"],
                                created_at=crrnt_dttm,
                                updated_at=crrnt_dttm,
                                is_hidden=(True if gen_form.is_hidden == "yes" else False),
                                is_exclude=(True if gen_form.is_exclude == "yes" else False)
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
    rslt = cr_engn.etc.logging__info("view at /show_words")

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
                if len(str(wrd_tmp.id)) > 6:
                    id_tmp = wrd_tmp.id[0:6] + "..."
                else:
                    id_tmp = wrd_tmp.id
                if len(wrd_tmp.spell_and_header) > 6:
                    spll_n_hdr_tmp = wrd_tmp.spell_and_header[0:6] + "..."
                else:
                    spll_n_hdr_tmp = wrd_tmp.spell_and_header
                if len(wrd_tmp.mean_and_body) > 6:
                    mn_n_bdy_tmp = wrd_tmp.mean_and_body[0:6] + "..."
                else:
                    mn_n_bdy_tmp = wrd_tmp.mean_and_body
                if len(wrd_tmp.staff_name) > 6:
                    stff_nm_tmp = wrd_tmp.staff_name[0:6] + "..."
                else:
                    stff_nm_tmp = wrd_tmp.staff_name
                wrds_fnl.append([id_tmp,
                                 spll_n_hdr_tmp,
                                 mn_n_bdy_tmp,
                                 stff_nm_tmp
                                ])
                per_pg = consts.WORD_ITEM_PER_PAGE
                pg = request.args.get(get_page_parameter(), type=int, default=1)
                pg_dat = wrds_fnl[(pg - 1) * per_pg : pg * per_pg]
                pgntn = Pagination(page=pg,
                                   total=len(wrds_fnl),
                                   per_page=per_pg,
                                   css_framework=consts.PAGINATION_CSS
                                  )
                return render_template("show_words.html", page_data=pg_dat, pagination=pgntn) 

            per_pg = consts.WORD_ITEM_PER_PAGE
            pg = request.args.get(get_page_parameter(), type=int, default=1)
            pg_dat = wrds_fnl[(pg - 1) * per_pg : pg * per_pg]
            pgntn = Pagination(page=pg,
                               total=len(wrds_fnl),
                               per_page=per_pg,
                               css_framework=consts.PAGINATION_CSS
                              )
            return render_template("show_words.html", page_data=pg_dat, pagination=pgntn) 
        else:
            wrds_tmp = db_session.query(Word).order_by(Word.id.asc()).all()
            db_session.close()
            for wrd_tmp in wrds_tmp:
                 if len(str(wrd_tmp.id)) > 6:
                     id_tmp = wrd_tmp.id[0:6] + "..."
                 else:
                     id_tmp = wrd_tmp.id
                 if len(wrd_tmp.spell_and_header) > 6:
                     spll_n_hdr_tmp = wrd_tmp.spell_and_header[0:6] + "..."
                 else:
                     spll_n_hdr_tmp = wrd_tmp.spell_and_header
                 if len(wrd_tmp.mean_and_body) > 6:
                     mn_n_bdy_tmp = wrd_tmp.mean_and_body[0:6] + "..."
                 else:
                     mn_n_bdy_tmp = wrd_tmp.mean_and_body
                 if len(wrd_tmp.staff_name) > 6:
                     stff_nm_tmp = wrd_tmp.staff_name[0:6] + "..."
                 else:
                     stff_nm_tmp = wrd_tmp.staff_name
                 wrds_fnl.append([id_tmp,
                                  spll_n_hdr_tmp,
                                  mn_n_bdy_tmp,
                                  stff_nm_tmp
                                 ])
            per_pg = consts.WORD_ITEM_PER_PAGE
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

        # フォームが改竄されているので, その旨を通知するために例外を発生させる.
        raise BadRequest


# 「show_themes」のためのビュー関数(=URLエンドポイント)を宣言・定義する.
@view.route("/show_themes", methods=["GET", "POST"])
@view.route("/show_themes/<int:id>", methods=["GET", "POST"])
def show_themes(id=None):
    # 関数内で使用する変数・オブジェクトを宣言・定義する.
    thms_tmp = []
    thms_fnl = []

    # 該当のURLエンドポイントに入ったことをロギングする.
    rslt = cr_engn.etc.logging__info("view at /show_themes")

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
                if len(thm_tmp.mean_and_body) > 6:
                    mn_n_bdy_tmp = thm_tmp.mean_and_body[0:6] + "..."
                else:
                    mn_n_bdy_tmp = thm_tmp.mean_and_body
                if len(thm_tmp.staff_name) > 6:
                    stff_nm_tmp = thm_tmp.staff_name[0:6] + "..."
                else:
                    stff_nm_tmp = thm_tmp.staff_name
                thms_fnl.append([id_tmp,
                                 spll_n_hdr_tmp,
                                 mn_n_bdy_tmp,
                                 stff_nm_tmp
                                ])
                per_pg = consts.THEME_ITEM_PER_PAGE
                pg = request.args.get(get_page_parameter(), type=int, default=1)
                pg_dat = thms_fnl[(pg - 1) * per_pg : pg * per_pg]
                pgntn = Pagination(page=pg,
                                   total=len(thms_fnl),
                                   per_page=per_pg,
                                   css_framework=consts.PAGINATION_CSS
                                  )
                return render_template("show_themes.html", page_data=pg_dat, pagination=pgntn)

            per_pg = consts.THEME_ITEM_PER_PAGE
            pg = request.args.get(get_page_parameter(), type=int, default=1)
            pg_dat = thms_fnl[(pg - 1) * per_pg : pg * per_pg]
            pgntn = Pagination(page=pg,
                               total=len(thms_fnl),
                               per_page=per_pg,
                               css_framework=consts.PAGINATION_CSS
                              )
            return render_template("show_themes.html", page_data=pg_dat, pagination=pgntn)

        else:
            thms_tmp = db_session.query(Theme).order_by(Theme.id.asc()).all()
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
                 if len(thm_tmp.mean_and_body) > 6:
                     mn_n_bdy_tmp = thm_tmp.mean_and_body[0:6] + "..."
                 else:
                     mn_n_bdy_tmp = thm_tmp.mean_and_body
                 if len(thm_tmp.staff_name) > 6:
                     stff_nm_tmp = thm_tmp.staff_name[0:6] + "..."
                 else:
                     stff_nm_tmp = thm_tmp.staff_name
                 thms_fnl.append([id_tmp,
                                  spll_n_hdr_tmp,
                                  mn_n_bdy_tmp,
                                  stff_nm_tmp
                                 ])
            per_pg = consts.THEME_ITEM_PER_PAGE
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

        # フォームが改竄されているので, その旨を通知するために例外を発生させる.
        raise BadRequest


# 「show_categories」のためのビュー関数(=URLエンドポイント)を宣言・定義する.
@view.route("/show_categories", methods=["GET", "POST"])
@view.route("/show_categories/<int:id>", methods=["GET", "POST"])
def show_categories(id=None):
    # 関数内で使用する変数・オブジェクトを宣言・定義する.
    ctgrs_tmp = []
    ctgrs_fnl = []

    # 該当のURLエンドポイントに入ったことをロギングする.
    rslt = cr_engn.etc.logging__info("view at /show_categories")

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
                if len(ctgr_tmp.mean_and_body) > 6:
                    mn_n_bdy_tmp = ctgr_tmp.mean_and_body[0:6] + "..."
                else:
                    mn_n_bdy_tmp = ctgr_tmp.mean_and_body
                if len(ctgr_tmp.staff_name) > 6:
                    stff_nm_tmp = ctgr_tmp.staff_name[0:6] + "..."
                else:
                    stff_nm_tmp = ctgr_tmp.staff_name
                ctgrs_fnl.append([id_tmp,
                                  spll_n_hdr_tmp,
                                  mn_n_bdy_tmp,
                                  stff_nm_tmp
                                 ])
                per_pg = consts.CATEGORY_ITEM_PER_PAGE
                pg = request.args.get(get_page_parameter(), type=int, default=1)
                pg_dat = ctgrs_fnl[(pg - 1) * per_pg : pg * per_pg]
                pgntn = Pagination(page=pg,
                                   total=len(ctgrs_fnl),
                                   per_page=per_pg,
                                   css_framework=consts.PAGINATION_CSS
                                  )
                return render_template("show_categories.html", page_data=pg_dat, pagination=pgntn)

            per_pg = consts.CATEGORY_ITEM_PER_PAGE
            pg = request.args.get(get_page_parameter(), type=int, default=1)
            pg_dat = ctgrs_fnl[(pg - 1) * per_pg : pg * per_pg]
            pgntn = Pagination(page=pg,
                               total=len(ctgrs_fnl),
                               per_page=per_pg,
                               css_framework=consts.PAGINATION_CSS
                              )
            return render_template("show_categories.html", page_data=pg_dat, pagination=pgntn)

        else:
            ctgrs_tmp = db_session.query(Category).order_by(Category.id.asc()).all()
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
                if len(ctgr_tmp.mean_and_body) > 6:
                    mn_n_bdy_tmp = ctgr_tmp.mean_and_body[0:6] + "..."
                else:
                    mn_n_bdy_tmp = ctgr_tmp.mean_and_body
                if len(ctgr_tmp.staff_name) > 6:
                    stff_nm_tmp = ctgr_tmp.staff_name[0:6] + "..."
                else:
                    stff_nm_tmp = ctgr_tmp.staff_name
                ctgrs_fnl.append([id_tmp,
                                  spll_n_hdr_tmp,
                                  mn_n_bdy_tmp,
                                  stff_nm_tmp
                                 ])
            per_pg = consts.CATEGORY_ITEM_PER_PAGE
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

        # フォームが改竄されているので, その旨を通知するために例外を発生させる.
        raise BadRequest


# 「show_facts」のためのビュー関数(=URLエンドポイント)を宣言・定義する.
@view.route("/show_facts", methods=["GET", "POST"])
@view.route("/show_facts/<int:id>", methods=["GET", "POST"])
def show_facts(id=None):
    # 関数内で使用する変数・オブジェクトを宣言・定義する.
    fcts_tmp = []
    fcts_fnl = []

    # 該当のURLエンドポイントに入ったことをロギングする.
    rslt = cr_engn.etc.logging__info("view at /show_knowledges")

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
        if id > db_session.query(Fact).count():
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
        session["referrer-page"] = "view.show_facts"

        # 該当ページ内のボタンから遷移するためのセッション項目を削除する.
        session.pop("hidden-modify-item-id", None)
        session.pop("hidden-detail-item-id", None)

        # DBから事実レコードを取得してテンプレートと共に返す.
        # RIDを指定された場合は, 一つだけレコードを取得する.
        if id is not None:
            fct_tmp = db_session.query(Fact).filter(Fact.id==id).first()
            db_session.close()
            if fct_tmp is not None:
                if len(str(fct_tmp.id)) > 6:
                    id_tmp = fct_tmp.id[0:6] + "..."
                else:
                    id_tmp = fct_tmp.id
                if len(fct_tmp.spell_and_header) > 6:
                    spll_n_hdr_tmp = fct_tmp.spell_and_header[0:6] + "..."
                else:
                    spll_n_hdr_tmp = fct_tmp.spell_and_header
                if len(fct_tmp.mean_and_body) > 6:
                    mn_n_bdy_tmp = fct_tmp.mean_and_body[0:6] + "..."
                else:
                    mn_n_bdy_tmp = fct_tmp.mean_and_body
                if len(fct_tmp.staff_name) > 6:
                    stff_nm_tmp = fct_tmp.staff_name[0:6] + "..."
                else:
                    stff_nm_tmp = fct_tmp.staff_name
                fcts_fnl.append([id_tmp,
                                    spll_n_hdr_tmp,
                                    mn_n_bdy_tmp,
                                    stff_nm_tmp
                                  ])
                per_pg = consts.KNOWLEDGE_ITEM_PER_PAGE
                pg = request.args.get(get_page_parameter(), type=int, default=1)
                pg_dat = fcts_fnl[(pg - 1) * per_pg : pg * per_pg]
                pgntn = Pagination(page=pg,
                                   total=len(fcts_fnl),
                                   per_page=per_pg,
                                   css_framework=consts.PAGINATION_CSS
                                  )
                return render_template("show_facts.html", page_data=pg_dat, pagination=pgntn)

            per_pg = consts.KNOWLEDGE_ITEM_PER_PAGE
            pg = request.args.get(get_page_parameter(), type=int, default=1)
            pg_dat = fcts_fnl[(pg - 1) * per_pg : pg * per_pg]
            pgntn = Pagination(page=pg,
                               total=len(fcts_fnl),
                               per_page=per_pg,
                               css_framework=consts.PAGINATION_CSS
                              )
            return render_template("show_facts.html", page_data=pg_dat, pagination=pgntn)

        else:
            fcts_tmp = db_session.query(Fact).order_by(Fact.id.asc()).all()
            db_session.close()
            for fct_tmp in fcts_tmp:
                if len(str(fct_tmp.id)) > 6:
                    id_tmp = fct_tmp.id[0:6] + "..."
                else:
                    id_tmp = fct_tmp.id
                if len(fct_tmp.spell_and_header) > 6:
                    spll_n_hdr_tmp = fct_tmp.spell_and_header[0:6] + "..."
                else:
                    spll_n_hdr_tmp = fct_tmp.spell_and_header
                if len(fct_tmp.mean_and_body) > 6:
                    mn_n_bdy_tmp = fct_tmp.mean_and_body[0:6] + "..."
                else:
                    mn_n_bdy_tmp = fct_tmp.mean_and_body
                if len(fct_tmp.staff_name) > 6:
                    stff_nm_tmp = fct_tmp.staff_name[0:6] + "..."
                else:
                    stff_nm_tmp = fct_tmp.staff_name
                fcts_fnl.append([id_tmp,
                                    spll_n_hdr_tmp,
                                    mn_n_bdy_tmp,
                                    stff_nm_tmp
                                   ])
            per_pg = consts.KNOWLEDGE_ITEM_PER_PAGE
            pg = request.args.get(get_page_parameter(), type=int, default=1)
            pg_dat = fcts_fnl[(pg - 1) * per_pg : pg * per_pg]
            pgntn = Pagination(page=pg,
                               total=len(fcts_fnl),
                               per_page=per_pg,
                               css_framework=consts.PAGINATION_CSS
                              )
            return render_template("show_facts.html", page_data=pg_dat, pagination=pgntn)

    if request.method == "POST":
        # 直前に, GETメソッドで該当ページを取得しているかを調べる.
        # 取得していなければ, 強制的に現在ページへリダイレクトする.
        if session["referrer-page"] != "view.show_facts":
            return redirect(url_for("view.show_facts"))

        # フォームボタン群の中から, 押下されたボタンに応じたページへリダイレクトする.
        if request.form["hidden-modify-item-id"] != "":
            session["hidden-modify-item-id"] = request.form["hidden-modify-item-id"]
            return redirect(url_for("view.modify_fact"))
        if request.form["hidden-detail-item-id"] != "":
            session["hidden-detail-item-id"] = request.form["hidden-detail-item-id"]
            return redirect(url_for("view.detail_fact"))

        # フォームが改竄されているので, その旨を通知するために例外を発生させる.
        raise BadRequest


# 「show_rules」のためのビュー関数(=URLエンドポイント)を宣言・定義する.
@view.route("/show_rules", methods=["GET", "POST"])
@view.route("/show_rules/<int:id>", methods=["GET", "POST"])
def show_rules(id=None):
    # 関数内で使用する変数・オブジェクトを宣言・定義する.
    rls_tmp = []
    rls_fnl = []

    # 該当のURLエンドポイントに入ったことをロギングする.
    rslt = cr_engn.etc.logging__info("view at /show_rules")

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
                if len(rl_tmp.mean_and_body) > 6:
                    mn_n_bdy_tmp = rl_tmp.mean_and_body[0:6] + "..."
                else:
                    mn_n_bdy_tmp = rl_tmp.mean_and_body
                if len(rl_tmp.staff_name) > 6:
                    stff_nm_tmp = rl_tmp.staff_name[0:6] + "..."
                else:
                    stff_nm_tmp = rl_tmp.staff_name
                rls_fnl.append([id_tmp,
                                spll_n_hdr_tmp,
                                mn_n_bdy_tmp,
                                stff_nm_tmp
                               ])
                per_pg = consts.RULE_ITEM_PER_PAGE
                pg = request.args.get(get_page_parameter(), type=int, default=1)
                pg_dat = rls_fnl[(pg - 1) * per_pg : pg * per_pg]
                pgntn = Pagination(page=pg,
                                   total=len(rls_fnl),
                                   per_page=per_pg,
                                   css_framework=consts.PAGINATION_CSS
                                  )
                return render_template("show_rules.html", page_data=pg_dat, pagination=pgntn)

            per_pg = consts.RULE_ITEM_PER_PAGE
            pg = request.args.get(get_page_parameter(), type=int, default=1)
            pg_dat = rls_fnl[(pg - 1) * per_pg : pg * per_pg]
            pgntn = Pagination(page=pg,
                               total=len(rls_fnl),
                               per_page=per_pg,
                               css_framework=consts.PAGINATION_CSS
                              )
            return render_template("show_rules.html", page_data=pg_dat, pagination=pgntn)

        else:
            rls_tmp = db_session.query(Rule).order_by(Rule.id.asc()).all()
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
                if len(rl_tmp.mean_and_body) > 6:
                    mn_n_bdy_tmp = rl_tmp.mean_and_body[0:6] + "..."
                else:
                    mn_n_bdy_tmp = rl_tmp.mean_and_body
                if len(rl_tmp.staff_name) > 6:
                    stff_nm_tmp = rl_tmp.staff_name[0:6] + "..."
                else:
                    stff_nm_tmp = rl_tmp.staff_name
                rls_fnl.append([id_tmp,
                                spll_n_hdr_tmp,
                                mn_n_bdy_tmp,
                                stff_nm_tmp
                               ])
            per_pg = consts.RULE_ITEM_PER_PAGE
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

        # フォームが改竄されているので, その旨を通知するために例外を発生させる.
        raise BadRequest


# 「show_reactions」のためのビュー関数(=URLエンドポイント)を宣言・定義する.
@view.route("/show_reactions", methods=["GET", "POST"])
@view.route("/show_reactions/<int:id>", methods=["GET", "POST"])
def show_reactions(id=None):
    # 関数内で使用する変数・オブジェクトを宣言・定義する.
    rctns_tmp = []
    rctns_fnl = []

    # 該当のURLエンドポイントに入ったことをロギングする.
    rslt = cr_engn.etc.logging__info("view at /show_reactions")

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
                if len(rctn_tmp.mean_and_body) > 6:
                    mn_n_bdy_tmp = rctn_tmp.mean_and_body[0:6] + "..."
                else:
                    mn_n_bdy_tmp = rctn_tmp.mean_and_body
                if len(rctn_tmp.staff_name) > 6:
                    stff_nm_tmp = rctn_tmp.staff_name[0:6] + "..."
                else:
                    stff_nm_tmp = rctn_tmp.staff_name
                rctns_fnl.append([id_tmp,
                                spll_n_hdr_tmp,
                                mn_n_bdy_tmp,
                                stff_nm_tmp
                               ])
                per_pg = consts.RULE_ITEM_PER_PAGE
                pg = request.args.get(get_page_parameter(), type=int, default=1)
                pg_dat = rctns_fnl[(pg - 1) * per_pg : pg * per_pg]
                pgntn = Pagination(page=pg,
                                   total=len(rctns_fnl),
                                   per_page=per_pg,
                                   css_framework=consts.PAGINATION_CSS
                                  )
                return render_template("show_reactions.html", page_data=pg_dat, pagination=pgntn)

            per_pg = consts.RULE_ITEM_PER_PAGE
            pg = request.args.get(get_page_parameter(), type=int, default=1)
            pg_dat = rctns_fnl[(pg - 1) * per_pg : pg * per_pg]
            pgntn = Pagination(page=pg,
                               total=len(rctns_fnl),
                               per_page=per_pg,
                               css_framework=consts.PAGINATION_CSS
                              )
            return render_template("show_reactions.html", page_data=pg_dat, pagination=pgntn)

        else:
            rctns_tmp = db_session.query(Reaction).order_by(Reaction.id.asc()).all()
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
                if len(rctn_tmp.mean_and_body) > 6:
                    mn_n_bdy_tmp = rctn_tmp.mean_and_body[0:6] + "..."
                else:
                    mn_n_bdy_tmp = rctn_tmp.mean_and_body
                if len(rctn_tmp.staff_name) > 6:
                    stff_nm_tmp = rctn_tmp.staff_name[0:6] + "..."
                else:
                    stff_nm_tmp = rctn_tmp.staff_name
                rctns_fnl.append([id_tmp,
                                spll_n_hdr_tmp,
                                mn_n_bdy_tmp,
                                stff_nm_tmp
                               ])
            per_pg = consts.RULE_ITEM_PER_PAGE
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

        # フォームが改竄されているので, その旨を通知するために例外を発生させる.
        raise BadRequest


# 「show_generates」のためのビュー関数(=URLエンドポイント)を宣言・定義する.
@view.route("/show_generates", methods=["GET", "POST"])
@view.route("/show_generates/<int:id>", methods=["GET", "POST"])
def show_generates(id=None):
    # 関数内で使用する変数・オブジェクトを宣言・定義する.
    gens_tmp = []
    gens_fnl = []

    # 該当のURLエンドポイントに入ったことをロギングする.
    rslt = cr_engn.etc.logging__info("view at /show_generates")

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
                if len(gen_tmp.mean_and_body) > 6:
                    mn_n_bdy_tmp = gen_tmp.mean_and_body[0:6] + "..."
                else:
                    mn_n_bdy_tmp = gen_tmp.mean_and_body
                if len(gen_tmp.staff_name) > 6:
                    stff_nm_tmp = gen_tmp.staff_name[0:6] + "..."
                else:
                    stff_nm_tmp = gen_tmp.staff_name
                gens_fnl.append([id_tmp,
                                 spll_n_hdr_tmp,
                                 mn_n_bdy_tmp,
                                 stff_nm_tmp
                                ])
                per_pg = consts.GENERATE_ITEM_PER_PAGE
                pg = request.args.get(get_page_parameter(), type=int, default=1)
                pg_dat = gens_fnl[(pg - 1) * per_pg : pg * per_pg]
                pgntn = Pagination(page=pg,
                                   total=len(gens_fnl),
                                   per_page=per_pg,
                                   css_framework=consts.PAGINATION_CSS
                                  )
                return render_template("show_generates.html", page_data=pg_dat, pagination=pgntn)

            per_pg = consts.GENERATE_ITEM_PER_PAGE
            pg = request.args.get(get_page_parameter(), type=int, default=1)
            pg_dat = gens_fnl[(pg - 1) * per_pg : pg * per_pg]
            pgntn = Pagination(page=pg,
                               total=len(gens_fnl),
                               per_page=per_pg,
                               css_framework=consts.PAGINATION_CSS
                              )
            return render_template("show_generates.html", page_data=pg_dat, pagination=pgntn)

        else:
            gens_tmp = db_session.query(Generate).order_by(Generate.id.asc()).all()
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
                if len(gen_tmp.mean_and_body) > 6:
                    mn_n_bdy_tmp = gen_tmp.mean_and_body[0:6] + "..."
                else:
                    mn_n_bdy_tmp = gen_tmp.mean_and_body
                if len(gen_tmp.staff_name) > 6:
                    stff_nm_tmp = gen_tmp.staff_name[0:6] + "..."
                else:
                    stff_nm_tmp = gen_tmp.staff_name
                gens_fnl.append([id_tmp,
                                 spll_n_hdr_tmp,
                                 mn_n_bdy_tmp,
                                 stff_nm_tmp
                                ])
            per_pg = consts.GENERATE_ITEM_PER_PAGE
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

        # フォームが改竄されているので, その旨を通知するために例外を発生させる.
        raise BadRequest


# 「show_histories」のためのビュー関数(=URLエンドポイント)を宣言・定義する.
@view.route("/show_histories", methods=["GET", "POST"])
@view.route("/show_histories/<int:id>", methods=["GET", "POST"])
def show_histories(id=None):
    # 関数内で使用する変数・オブジェクトを宣言・定義する.
    hists_tmp = []
    hists_fnl = []

    # 該当のURLエンドポイントに入ったことをロギングする.
    rslt = cr_engn.etc.logging__info("view at /show_histories")

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
                if len(hist_tmp.staff_text_message) > 6:
                    stff_msg_tmp = hist_tmp.staff_text_message[0:6] + "..."
                else:
                    stff_msg_tmp = hist_tmp.staff_text_message
                if len(hist_tmp.application_text_message) > 6:
                    app_msg_tmp = hist_tmp.application_text_message[0:6] + "..."
                else:
                    app_msg_tmp = hist_tmp.application_text_message
                if len(hist_tmp.staff_name) > 6:
                    stff_nm_tmp = hist_tmp.staff_name[0:6] + "..."
                else:
                    stff_nm_tmp = hist_tmp.staff_name
                hists_fnl.append([id_tmp,
                                  stff_msg_tmp,
                                  app_msg_tmp,
                                  stff_nm_tmp
                                ])
                per_pg = consts.HISTORY_ITEM_PER_PAGE
                pg = request.args.get(get_page_parameter(), type=int, default=1)
                pg_dat = hists_fnl[(pg - 1) * per_pg : pg * per_pg]
                pgntn = Pagination(page=pg,
                                   total=len(hists_fnl),
                                   per_page=per_pg,
                                   css_framework=consts.PAGINATION_CSS
                                  )
                return render_template("show_histories.html", page_data=pg_dat, pagination=pgntn)

            per_pg = consts.HISTORY_ITEM_PER_PAGE
            pg = request.args.get(get_page_parameter(), type=int, default=1)
            pg_dat = hists_fnl[(pg - 1) * per_pg : pg * per_pg]
            pgntn = Pagination(page=pg,
                               total=len(hists_fnl),
                               per_page=per_pg,
                               css_framework=consts.PAGINATION_CSS
                              )
            return render_template("show_histories.html", page_data=pg_dat, pagination=pgntn)

        else:
            hists_tmp = db_session.query(History).order_by(History.id.asc()).all()
            db_session.close()
            for hist_tmp in hists_tmp:
                if len(str(hist_tmp.id)) > 6:
                    id_tmp = hist_tmp.id[0:6] + "..."
                else:
                    id_tmp = hist_tmp.id
                if len(hist_tmp.staff_text_message) > 6:
                    stff_msg_tmp = hist_tmp.staff_text_message[0:6] + "..."
                else:
                    stff_msg_tmp = hist_tmp.staff_text_message
                if len(hist_tmp.application_text_message) > 6:
                    app_msg_tmp = hist_tmp.application_text_message[0:6] + "..."
                else:
                    app_msg_tmp = hist_tmp.application_text_message
                if len(hist_tmp.staff_name) > 6:
                    stff_nm_tmp = hist_tmp.staff_name[0:6] + "..."
                else:
                    stff_nm_tmp = hist_tmp.staff_name
                hists_fnl.append([id_tmp,
                                  stff_msg_tmp,
                                  app_msg_tmp,
                                  stff_nm_tmp
                                ])
            per_pg = consts.HISTORY_ITEM_PER_PAGE
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
        if request.form["hidden-detail-item-id"] != "":
            session["hidden-detail-item-id"] = request.form["hidden-detail-item-id"]
            return redirect(url_for("view.detail_history"))

        # フォームが改竄されているので, その旨を通知するために例外を発生させる.
        raise BadRequest


# 「show_enters_or_exits」のためのビュー関数(=URLエンドポイント)を宣言・定義する.
@view.route("/show_enters_or_exits", methods=["GET", "POST"])
@view.route("/show_enters_or_exits/<int:id>", methods=["GET", "POST"])
def show_enters_or_exits(id=None):
    # 関数内で使用する変数・オブジェクトを宣言・定義する.
    ents_or_exts_tmp = []
    ents_or_exts_fnl = []

    # 該当のURLエンドポイントに入ったことをロギングする.
    rslt = cr_engn.etc.logging__info("view at /show_enters_or_exits")

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
                if str(cr_engn.etc.convert_datetime_object_to_string_for_timestamp(ent_or_ext_tmp.enter_or_exit_at, False)).split("T")[1].split(":")[2] == "00":
                    dt_tmp = str(cr_engn.etc.convert_datetime_object_to_string_for_timestamp(ent_or_ext_tmp.enter_or_exit_at, False)).split("T")[0] + " "
                    tm_tmp = (
                    str(cr_engn.etc.convert_datetime_object_to_string_for_timestamp(ent_or_ext_tmp.enter_or_exit_at, False)).split("T")[1].split(":")[0] + ":" +
                    str(cr_engn.etc.convert_datetime_object_to_string_for_timestamp(ent_or_ext_tmp.enter_or_exit_at, False)).split("T")[1].split(":")[1] + ":" +
                    str(ent_or_ext_tmp.enter_or_exit_at_second)
                    )
                    dttm_tmp = cr_engn.etc.modify_style_for_datetime_string(dt_tmp + tm_tmp, False)
                else:
                    dttm_tmp = (
                    cr_engn.etc.modify_style_for_datetime_string(cr_engn.etc.convert_datetime_object_to_string_for_timestamp(ent_or_ext_tmp.enter_or_exit_at, False), False)
                    )
                ents_or_exts_fnl.append([id_tmp,
                                         stff_nm_tmp,
                                         rsn_tmp,
                                         dttm_tmp
                                        ])
                per_pg = consts.ENTER_OR_EXIT_ITEM_PER_PAGE
                pg = request.args.get(get_page_parameter(), type=int, default=1)
                pg_dat = ents_or_exts_fnl[(pg - 1) * per_pg : pg * per_pg]
                pgntn = Pagination(page=pg,
                                   total=len(ents_or_exts_fnl),
                                   per_page=per_pg,
                                   css_framework=consts.PAGINATION_CSS
                                  )
                return render_template("show_enters_or_exits.html", page_data=pg_dat, pagination=pgntn)

            per_pg = consts.ENTER_OR_EXIT_ITEM_PER_PAGE
            pg = request.args.get(get_page_parameter(), type=int, default=1)
            pg_dat = ents_or_exts_fnl[(pg - 1) * per_pg : pg * per_pg]
            pgntn = Pagination(page=pg,
                               total=len(ents_or_exts_fnl),
                               per_page=per_pg,
                               css_framework=consts.PAGINATION_CSS
                              )
            return render_template("show_enters_or_exits.html", page_data=pg_dat, pagination=pgntn)

        else:
            ents_or_exts_tmp = db_session.query(EnterOrExit).order_by(EnterOrExit.id.asc()).all()
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
                if str(cr_engn.etc.convert_datetime_object_to_string_for_timestamp(ent_or_ext_tmp.enter_or_exit_at, True)).split("T")[1].split(":")[2] == "00":
                    dt_tmp = str(cr_engn.etc.convert_datetime_object_to_string_for_timestamp(ent_or_ext_tmp.enter_or_exit_at, True)).split("T")[0] + " "
                    tm_tmp = (
                    str(cr_engn.etc.convert_datetime_object_to_string_for_timestamp(ent_or_ext_tmp.enter_or_exit_at, True)).split("T")[1].split(":")[0] + ":" +
                    str(cr_engn.etc.convert_datetime_object_to_string_for_timestamp(ent_or_ext_tmp.enter_or_exit_at, True)).split("T")[1].split(":")[1] + ":" +
                    str(ent_or_ext_tmp.enter_or_exit_at_second)
                    )
                    dttm_tmp = cr_engn.etc.modify_style_for_datetime_string(dt_tmp + tm_tmp, False)
                else:
                    dttm_tmp = (
                    cr_engn.etc.modify_style_for_datetime_string(cr_engn.etc.convert_datetime_object_to_string_for_timestamp(ent_or_ext_tmp.enter_or_exit_at, False), False)
                    )
                ents_or_exts_fnl.append([id_tmp,
                                         stff_nm_tmp,
                                         rsn_tmp,
                                         dttm_tmp
                                        ])
            per_pg = consts.ENTER_OR_EXIT_ITEM_PER_PAGE
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

        # フォームが改竄されているので, その旨を通知するために例外を発生させる.
        raise BadRequest


# 「show_staffs」のためのビュー関数(=URLエンドポイント)を宣言・定義する.
@view.route("/show_staffs", methods=["GET", "POST"])
@view.route("/show_staffs/<int:id>", methods=["GET", "POST"])
def show_staffs(id=None):
    # 関数内で使用する変数・オブジェクトを宣言・定義する.
    stffs_tmp = []
    stffs_fnl = []

    # 該当のURLエンドポイントに入ったことをロギングする.
    rslt = cr_engn.etc.logging__info("view at /show_staffs")

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
                brth_dt_tmp = (
                cr_engn.etc.modify_style_for_datetime_string(cr_engn.etc.convert_datetime_object_to_string_for_eventday(stff_tmp.birth_date), False)
                )
                stffs_fnl.append([id_tmp,
                                  nm_tmp,
                                  sex_tmp,
                                  bld_typ_tmp,
                                  brth_dt_tmp
                                 ])
                per_pg = consts.STAFF_ITEM_PER_PAGE
                pg = request.args.get(get_page_parameter(), type=int, default=1)
                pg_dat = stffs_fnl[(pg - 1) * per_pg : pg * per_pg]
                pgntn = Pagination(page=pg,
                                   total=len(stffs_fnl),
                                   per_page=per_pg,
                                   css_framework=consts.PAGINATION_CSS
                                  )
                return render_template("show_staffs.html", page_data=pg_dat, pagination=pgntn)

            per_pg = consts.STAFF_ITEM_PER_PAGE
            pg = request.args.get(get_page_parameter(), type=int, default=1)
            pg_dat = stffs_fnl[(pg - 1) * per_pg : pg * per_pg]
            pgntn = Pagination(page=pg,
                               total=len(stffs_fnl),
                               per_page=per_pg,
                               css_framework=consts.PAGINATION_CSS
                              )
            return render_template("show_staffs.html", page_data=pg_dat, pagination=pgntn)

        else:
            stffs_tmp = db_session.query(Staff).order_by(Staff.id.asc()).all()
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
                 brth_dt_tmp = (
                 cr_engn.etc.modify_style_for_datetime_string(cr_engn.etc.convert_datetime_object_to_string_for_eventday(stff_tmp.birth_date), False)
                 )
                 stffs_fnl.append([id_tmp,
                                   nm_tmp,
                                   sex_tmp,
                                   bld_typ_tmp,
                                   brth_dt_tmp
                                  ])
            per_pg = consts.STAFF_ITEM_PER_PAGE
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

        # フォームが改竄されているので, その旨を通知するために例外を発生させる.
        raise BadRequest


# 「search_words」のためのビュー関数(=URLエンドポイント)を宣言・定義する.
@view.route("/search_words", methods=["GET", "POST"])
def search_words():
    # 関数内で使用する変数・オブジェクトを宣言・定義する.
    srch_wrd_form = SearchWordForm()

    # 該当のURLエンドポイントに入ったことをロギングする.
    rslt = cr_engn.etc.logging__info("view at /search_words")

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
        session.pop("mean-and-body", None)
        session.pop("intent", None)
        session.pop("sentiment", None)
        session.pop("sentiment-support", None)
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
            srch_wrd_form.id.data = ""
            srch_wrd_form.spell_and_header.data = ""
            srch_wrd_form.mean_and_body.data = ""
            srch_wrd_form.intent.data = ""
            srch_wrd_form.sentiment.data = ""
            srch_wrd_form.sentiment_support.data = ""
            srch_wrd_form.strength.data = ""
            srch_wrd_form.part_of_speech.data = ""
            srch_wrd_form.staff_name.data = ""
            srch_wrd_form.staff_kana_name.data = ""
            srch_wrd_form.created_at_begin.data = ""
            srch_wrd_form.created_at_end.data = ""
            srch_wrd_form.updated_at_begin.data = ""
            srch_wrd_form.updated_at_end.data = ""
            srch_wrd_form.sort_condition.data = "condition-1"
            srch_wrd_form.extract_condition.data = "condition-1"
            return render_template("search_words.html", form=srch_wrd_form)

        # 検索に係るセッション項目(=検索条件)を作成する.
        session["id"] = srch_wrd_form.id.data
        session["spell-and-header"] = srch_wrd_form.spell_and_header.data
        session["mean-and-body"] = srch_wrd_form.mean_and_body.data
        session["intent"] = srch_wrd_form.intent.data
        session["sentiment"] = srch_wrd_form.sentiment.data
        session["sentiment-support"] = srch_wrd_form.sentiment_support.data
        session["strength"] = srch_wrd_form.strength.data
        session["part-of-speech"] = srch_wrd_form.part_of_speech.data
        session["staff-name"] = srch_wrd_form.staff_name.data
        session["staff-kana-name"] = srch_wrd_form.staff_kana_name.data
        session["created-at-begin"] = srch_wrd_form.created_at_begin.data
        session["created-at-end"] = srch_wrd_form.created_at_end.data
        session["updated-at-begin"] = srch_wrd_form.updated_at_begin.data
        session["updated-at-end"] = srch_wrd_form.updated_at_end.data
        session["sort-condition"] = srch_wrd_form.sort_condition.data
        session["extract-condition"] = srch_wrd_form.extract_condition.data

        # 検索条件を保持したまま, 検索結果ページへリダイレクトする.
        return redirect(url_for("view.search_words_results"))


# 「search_themes」のためのビュー関数(=URLエンドポイント)を宣言・定義する.
@view.route("/search_themes", methods=["GET", "POST"])
def search_themes():
    # 関数内で使用する変数・オブジェクトを宣言・定義する.
    srch_thm_form = SearchThemeForm()

    # 該当のURLエンドポイントに入ったことをロギングする.
    rslt = cr_engn.etc.logging__info("view at /search_words")

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
        session.pop("mean-and-body", None)
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
            srch_thm_form.id.data = ""
            srch_thm_form.spell_and_header.data = ""
            srch_thm_form.mean_and_body.data = ""
            srch_thm_form.category_tag.data = ""
            srch_thm_form.staff_name.data = ""
            srch_thm_form.staff_kana_name.data = ""
            srch_thm_form.created_at_begin.data = ""
            srch_thm_form.created_at_end.data = ""
            srch_thm_form.updated_at_begin.data = ""
            srch_thm_form.updated_at_end.data = ""
            srch_thm_form.sort_condition.data = "condition-1"
            srch_thm_form.extract_condition.data = "condition-1"
            return render_template("search_themes.html", form=srch_thm_form)

        # 検索に係るセッション項目(=検索条件)を作成する.
        session["id"] = srch_thm_form.id
        session["spell-and-header"] = srch_thm_form.spell_and_header.data
        session["mean-and-body"] = srch_thm_form.mean_and_body.data
        session["category-tags"] = srch_thm_form.category_tag.data
        session["staff-name"] = srch_thm_form.staff_name.data
        session["staff-kana-name"] = srch_thm_form.staff_kana_name.data
        session["created-at-begin"] = srch_thm_form.created_at_begin.data
        session["created-at-end"] = srch_thm_form.created_at_end.data
        session["updated-at-begin"] = srch_thm_form.updated_at_begin.data
        session["updated-at-end"] = srch_thm_form.updated_at_end.data
        session["sort-condition"] = srch_thm_form.sort_condition.data
        session["extract-condition"] = srch_thm_form.extract_condition.data

        # 検索条件を保持したまま, 検索結果ページへリダイレクトする.
        return redirect(url_for("view.search_themes_results"))


# 「search_categories」のためのビュー関数(=URLエンドポイント)を宣言・定義する.
@view.route("/search_categories", methods=["GET", "POST"])
def search_categories():
    # 関数内で使用する変数・オブジェクトを宣言・定義する.
    srch_ctgr_form = SearchCategoryForm()

    # 該当のURLエンドポイントに入ったことをロギングする.
    rslt = cr_engn.etc.logging__info("view at /search_words")

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
        session.pop("mean-and-body", None)
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
            srch_ctgr_form.id.data = ""
            srch_ctgr_form.spell_and_header.data = ""
            srch_ctgr_form.mean_and_body.data = ""
            srch_ctgr_form.parent_category_tag.data = ""
            srch_ctgr_form.sibling_category_tag.data = ""
            srch_ctgr_form.child_category_tag.data = ""
            srch_ctgr_form.staff_name.data = ""
            srch_ctgr_form.staff_kana_name.data = ""
            srch_ctgr_form.created_at_begin.data = ""
            srch_ctgr_form.created_at_end.data = ""
            srch_ctgr_form.updated_at_begin.data = ""
            srch_ctgr_form.updated_at_end.data = ""
            srch_ctgr_form.sort_condition.data = "condition-1"
            srch_ctgr_form.extract_condition.data = "condition-1"
            return render_template("search_categories.html", form=srch_ctgr_form)

        # 検索に係るセッション項目(=検索条件)を作成する.
        session["id"] = srch_ctgr_form.id.data
        session["spell-and-header"] = srch_ctgr_form.spell_and_header.data
        session["mean-and-body"] = srch_ctgr_form.mean_and_body.data
        session["parent-category-tags"] = srch_ctgr_form.parent_category_tag.data
        session["sibling-category-tags"] = srch_ctgr_form.sibling_category_tag.data
        session["child-category-tags"] = srch_ctgr_form.child_category_tag.data
        session["staff-name"] = srch_ctgr_form.staff_name.data
        session["staff-kana-name"] = srch_ctgr_form.staff_kana_name.data
        session["created-at-begin"] = srch_ctgr_form.created_at_begin.data
        session["created-at-end"] = srch_ctgr_form.created_at_end.data
        session["updated-at-begin"] = srch_ctgr_form.updated_at_begin.data
        session["updated-at-end"] = srch_ctgr_form.updated_at_end.data
        session["sort-condition"] = srch_ctgr_form.sort_condition.data
        session["extract-condition"] = srch_ctgr_form.extract_condition.data

        # 検索条件を保持したまま, 検索結果ページへリダイレクトする.
        return redirect(url_for("view.search_categories_results"))


# 「search_knowledges」のためのビュー関数(=URLエンドポイント)を宣言・定義する.
@view.route("/search_knowledges", methods=["GET", "POST"])
def search_knowledges():
    # 関数内で使用する変数・オブジェクトを宣言・定義する.
    srch_fct_form = SearchFactForm()

    # 該当のURLエンドポイントに入ったことをロギングする.
    rslt = cr_engn.etc.logging__info("view at /search_knowledges")

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
        session.pop("mean-and-body", None)
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
        return render_template("search_knowledges.html", form=srch_fct_form)

    if request.method == "POST":
        # 直前に, GETメソッドで該当ページを取得しているかを調べる.
        # 取得していなければ, 強制的に現在ページへリダイレクトする.
        if session["referrer-page"] != "view.search_knowledges":
            return render_template("search_knowledges.html", form=srch_fct_form)

        # フォームの取消ボタンが押下されたら, 空のフォームと共にテンプレートを返す.
        if srch_fct_form.cancel.data:
            srch_fct_form.id.data = ""
            srch_fct_form.spell_and_header.data = ""
            srch_fct_form.mean_and_body.data = ""
            srch_fct_form.category_tag.data = ""
            srch_fct_form.has_image.data = ""
            srch_fct_form.has_sound.data = ""
            srch_fct_form.has_video.data = ""
            srch_fct_form.staff_name.data = ""
            srch_fct_form.staff_kana_name.data = ""
            srch_fct_form.created_at_begin.data = ""
            srch_fct_form.created_at_end.data = ""
            srch_fct_form.updated_at_begin.data = ""
            srch_fct_form.updated_at_end.data = ""
            srch_fct_form.sort_condition.data = "condition-1"
            srch_fct_form.extract_condition.data = "condition-1"
            return render_template("search_knowledges.html", form=srch_fct_form)

        # 検索に係るセッション項目(=検索条件)を作成する.
        session["id"] = srch_fct_form.id
        session["spell-and-header"] = srch_fct_form.spell_and_header.data
        session["mean-and-body"] = srch_fct_form.mean_and_body.data
        session["category-tags"] = srch_fct_form.category_tag.data
        session["has-image"] = srch_fct_form.has_image.data
        session["has-sound"] = srch_fct_form.has_sound.data
        session["has-video"] = srch_fct_form.has_video.data
        session["staff-name"] = srch_fct_form.staff_name.data
        session["staff-kana-name"] = srch_fct_form.staff_kana_name.data
        session["created-at-begin"] = srch_fct_form.created_at_begin.data
        session["created-at-end"] = srch_fct_form.created_at_end.data
        session["updated-at-begin"] = srch_fct_form.updated_at_begin.data
        session["updated-at-end"] = srch_fct_form.updated_at_end.data
        session["sort-condition"] = srch_fct_form.sort_condition.data
        session["extract-condition"] = srch_fct_form.extract_condition.data

        # 検索条件を保持したまま, 検索結果ページへリダイレクトする.
        return redirect(url_for("view.search_knowledges_results"))


# 「search_rules」のためのビュー関数(=URLエンドポイント)を宣言・定義する.
@view.route("/search_rules", methods=["GET", "POST"])
def search_rules():
    # 関数内で使用する変数・オブジェクトを宣言・定義する.
    srch_rl_form = SearchRuleForm()

    # 該当のURLエンドポイントに入ったことをロギングする.
    rslt = cr_engn.etc.logging__info("view at /search_rules")

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
        session.pop("mean-and-body", None)
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
            srch_rl_form.id.data = ""
            srch_rl_form.spell_and_header.data = ""
            srch_rl_form.mean_and_body.data = ""
            srch_rl_form.category_tag.data = ""
            srch_rl_form.inference_and_speculation_condition.data = ""
            srch_rl_form.inference_and_speculation_result.data = ""
            srch_rl_form.staff_name.data = ""
            srch_rl_form.staff_kana_name.data = ""
            srch_rl_form.created_at_begin.data = ""
            srch_rl_form.created_at_end.data = ""
            srch_rl_form.updated_at_begin.data = ""
            srch_rl_form.updated_at_end.data = ""
            srch_rl_form.sort_condition.data = "condition-1"
            srch_rl_form.extract_condition.data = "condition-1"
            return render_template("search_rules.html", form=srch_rl_form)

        # 検索に係るセッション項目(=検索条件)を作成する.
        session["id"] = srch_rl_form.id.data
        session["spell-and-header"] = srch_rl_form.spell_and_header.data
        session["mean-and-body"] = srch_rl_form.mean_and_body.data
        session["category-tags"] = srch_rl_form.category_tag.data
        session["inference-and-speculation-condition"] = srch_rl_form.inference_and_speculation_condition.data
        session["inference-and-speculation-result"] = srch_rl_form.inference_and_speculation_result.data
        session["staff-name"] = srch_rl_form.staff_name.data
        session["staff-kana-name"] = srch_rl_form.staff_kana_name.data
        session["created-at-begin"] = srch_rl_form.created_at_begin.data
        session["created-at-end"] = srch_rl_form.created_at_end.data
        session["updated-at-begin"] = srch_rl_form.updated_at_begin.data
        session["updated-at-end"] = srch_rl_form.updated_at_end.data
        session["sort-condition"] = srch_rl_form.sort_condition.data
        session["extract-condition"] = srch_rl_form.extract_condition.data

        # 検索条件を保持したまま, 検索結果ページへリダイレクトする.
        return redirect(url_for("view.search_rules_results"))


# 「search_reactions」のためのビュー関数(=URLエンドポイント)を宣言・定義する.
@view.route("/search_reactions", methods=["GET", "POST"])
def search_reactions():
    # 関数内で使用する変数・オブジェクトを宣言・定義する.
    srch_rctn_form = SearchReactionForm()

    # 該当のURLエンドポイントに入ったことをロギングする.
    rslt = cr_engn.etc.logging__info("view at /search_rules")

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
        session.pop("mean-and-body", None)
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
            srch_rctn_form.id.data = ""
            srch_rctn_form.spell_and_header.data = ""
            srch_rctn_form.mean_and_body.data = ""
            srch_rctn_form.staff_psychology.data = ""
            srch_rctn_form.scene_and_background.data = ""
            srch_rctn_form.message_example_from_staff.data = ""
            srch_rctn_form.message_example_from_application.data = ""
            srch_rctn_form.staff_name.data = ""
            srch_rctn_form.staff_kana_name.data = ""
            srch_rctn_form.created_at_begin.data = ""
            srch_rctn_form.created_at_end.data = ""
            srch_rctn_form.updated_at_begin.data = ""
            srch_rctn_form.updated_at_end.data = ""
            srch_rctn_form.sort_condition.data = "condition-1"
            srch_rctn_form.extract_condition.data = "condition-1"
            return render_template("search_reactions.html", form=srch_rctn_form)

        # 検索に係るセッション項目(=検索条件)を作成する.
        session["id"] = srch_rctn_form.id.data
        session["spell-and-header"] = srch_rctn_form.spell_and_header.data
        session["mean-and-body"] = srch_rctn_form.mean_and_body.data
        session["staff-psychology"] = srch_rctn_form.staff_psychology.data
        session["scene-and-background"] = srch_rctn_form.scene_and_background.data
        session["message-example-from-staff"] = srch_rctn_form.message_example_from_staff.data
        session["message-example-from-application"] = srch_rctn_form.message_example_from_application.data
        session["staff-name"] = srch_rctn_form.staff_name.data
        session["staff-kana-name"] = srch_rctn_form.staff_kana_name.data
        session["created-at-begin"] = srch_rctn_form.created_at_begin.data
        session["created-at-end"] = srch_rctn_form.created_at_end.data
        session["updated-at-begin"] = srch_rctn_form.updated_at_begin.data
        session["updated-at-end"] = srch_rctn_form.updated_at_end.data
        session["sort-condition"] = srch_rctn_form.sort_condition.data
        session["extract-condition"] = srch_rctn_form.extract_condition.data

        # 検索条件を保持したまま, 検索結果ページへリダイレクトする.
        return redirect(url_for("view.search_reactions_results"))


# 「search_generates」のためのビュー関数(=URLエンドポイント)を宣言・定義する.
@view.route("/search_generates", methods=["GET", "POST"])
def search_generates():
    # 関数内で使用する変数・オブジェクトを宣言・定義する.
    srch_gen_form = SearchGenerateForm()

    # 該当のURLエンドポイントに入ったことをロギングする.
    rslt = cr_engn.etc.logging__info("view at /search_generates")

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
        session.pop("mean-and-body", None)
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
            srch_gen_form.id.data = ""
            srch_gen_form.spell_and_header.data = ""
            srch_gen_form.mean_and_body.data = ""
            srch_gen_form.staff_name.data = ""
            srch_gen_form.staff_kana_name.data = ""
            srch_gen_form.created_at_begin.data = ""
            srch_gen_form.created_at_end.data = ""
            srch_gen_form.updated_at_begin.data = ""
            srch_gen_form.updated_at_end.data = ""
            srch_gen_form.sort_condition.data = "condition-1"
            srch_gen_form.extract_condition.data = "condition-1"
            return render_template("search_generates.html", form=srch_gen_form)

        # 検索に係るセッション項目(=検索条件)を作成する.
        session["id"] = srch_gen_form.id
        session["spell-and-header"] = srch_gen_form.spell_and_header.data
        session["mean-and-body"] = srch_gen_form.mean_and_body.data
        session["staff-name"] = srch_gen_form.staff_name.data
        session["staff-kana-name"] = srch_gen_form.staff_kana_name.data
        session["created-at-begin"] = srch_gen_form.created_at_begin.data
        session["created-at-end"] = srch_gen_form.created_at_end.data
        session["updated-at-begin"] = srch_gen_form.updated_at_begin.data
        session["updated-at-end"] = srch_gen_form.updated_at_end.data
        session["sort-condition"] = srch_gen_form.sort_condition.data
        session["extract-condition"] = srch_gen_form.extract_condition.data

        # 検索条件を保持したまま, 検索結果ページへリダイレクトする.
        return redirect(url_for("view.search_generates_results"))


# 「search_histories」のためのビュー関数(=URLエンドポイント)を宣言・定義する.
@view.route("/search_histories", methods=["GET", "POST"])
def search_histories():
    # 関数内で使用する変数・オブジェクトを宣言・定義する.
    srch_hist_form = SearchHistoryForm()

    # 該当のURLエンドポイントに入ったことをロギングする.
    rslt = cr_engn.etc.logging__info("view at /search_histories")

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
            srch_hist_form.id.data = ""
            srch_hist_form.staff_text_message.data = ""
            srch_hist_form.application_text_message.data = ""
            srch_hist_form.staff_name.data = ""
            srch_hist_form.staff_kana_name.data = ""
            srch_hist_form.created_at_begin.data = ""
            srch_hist_form.created_at_end.data = ""
            srch_hist_form.updated_at_begin.data = ""
            srch_hist_form.updated_at_end.data = ""
            srch_hist_form.sort_condition.data = "condition-1"
            srch_hist_form.extract_condition.data = "condition-1"
            return render_template("search_histories.html", form=srch_hist_form)

        # 検索に係るセッション項目(=検索条件)を作成する.
        session["id"] = srch_hist_form.id.data
        session["staff-message"] = srch_hist_form.staff_text_message.data
        session["application-message"] = srch_hist_form.application_text_message.data
        session["staff-name"] = srch_hist_form.staff_name.data
        session["staff-kana-name"] = srch_hist_form.staff_kana_name.data
        session["created-at-begin"] = srch_hist_form.created_at_begin.data
        session["created-at-end"] = srch_hist_form.created_at_end.data
        session["updated-at-begin"] = srch_hist_form.updated_at_begin.data
        session["updated-at-end"] = srch_hist_form.updated_at_end.data
        session["sort-condition"] = srch_hist_form.sort_condition.data
        session["extract-condition"] = srch_hist_form.extract_condition.data

        # 検索条件を保持したまま, 検索結果ページへリダイレクトする.
        return redirect(url_for("view.search_histories_results"))


# 「search_enters_or_exits」のためのビュー関数(=URLエンドポイント)を宣言・定義する.
@view.route("/search_enters_or_exits", methods=["GET", "POST"])
def search_enters_or_exits():
    # 関数内で使用する変数・オブジェクトを宣言・定義する.
    srch_entr_or_exit_form = SearchEnterOrExitForm()

    # 該当のURLエンドポイントに入ったことをロギングする.
    rslt = cr_engn.etc.logging__info("view at /enters_or_exits")

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
        session.pop("staff-name", None)
        session.pop("staff-kana-name", None)
        session.pop("reason", None)
        session.pop("enter-or-exit-at", None)
        session.pop("enter-or-exit-at-second", None)
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
            srch_entr_or_exit_form.id.data = ""
            srch_entr_or_exit_form.staff_name.data = ""
            srch_entr_or_exit_form.staff_kana_name.data = ""
            srch_entr_or_exit_form.reason.data = ""
            srch_entr_or_exit_form.enter_or_exit_at.data = ""
            srch_entr_or_exit_form.created_at_begin.data = ""
            srch_entr_or_exit_form.created_at_end.data = ""
            srch_entr_or_exit_form.updated_at_begin.data = ""
            srch_entr_or_exit_form.updated_at_end.data = ""
            srch_entr_or_exit_form.sort_condition.data = "condition-1"
            srch_entr_or_exit_form.extract_condition.data = "condition-1"
            return render_template("search_enters_or_exits.html", form=srch_entr_or_exit_form)

        # 検索に係るセッション項目(=検索条件)を作成する.
        session["id"] = srch_entr_or_exit_form.id.data
        session["staff-name"] = srch_entr_or_exit_form.staff_name.data
        session["staff-kana-name"] = srch_entr_or_exit_form.staff_kana_name.data
        session["reason"] = srch_entr_or_exit_form.reason.data
        session["enter-or-exit-at-begin"] = srch_entr_or_exit_form.enter_or_exit_at_begin.data
        session["enter-or-exit-at-end"] = srch_entr_or_exit_form.enter_or_exit_at_end.data
        session["created-at-begin"] = srch_entr_or_exit_form.created_at_begin.data
        session["created-at-end"] = srch_entr_or_exit_form.created_at_end.data
        session["updated-at-begin"] = srch_entr_or_exit_form.updated_at_begin.data
        session["updated-at-end"] = srch_entr_or_exit_form.updated_at_end.data
        session["sort-condition"] = srch_entr_or_exit_form.sort_condition.data
        session["extract-condition"] = srch_entr_or_exit_form.extract_condition.data

        # 検索条件を保持したまま, 検索結果ページへリダイレクトする.
        return redirect(url_for("view.search_enters_or_exits_results"))


# 「search_staffs」のためのビュー関数(=URLエンドポイント)を宣言・定義する.
@view.route("/search_staffs", methods=["GET", "POST"])
def search_staffs():
    # 関数内で使用する変数・オブジェクトを宣言・定義する.
    srch_stff_form = SearchStaffForm()

    # 該当のURLエンドポイントに入ったことをロギングする.
    rslt = cr_engn.etc.logging__info("view at /search_staffs")

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
            srch_stff_form.id.data = ""
            srch_stff_form.name.data = ""
            srch_stff_form.kana_name.data = ""
            srch_stff_form.sex.data = ""
            srch_stff_form.blood_type.data = ""
            srch_stff_form.birth_date.data = ""
            srch_stff_form.created_at_begin.data = ""
            srch_stff_form.created_at_end.data = ""
            srch_stff_form.updated_at_begin.data = ""
            srch_stff_form.updated_at_end.data = ""
            srch_stff_form.sort_condition.data = "condition-1"
            srch_stff_form.extract_condition.data = "condition-1"
            return render_template("search_staffs.html", form=srch_stff_form)

        # 検索に係るセッション項目(=検索条件)を作成する.
        session["id"] = srch_stff_form.id.data
        session["name"] = srch_stff_form.name.data
        session["kana-name"] = srch_stff_form.kana_name.data
        session["sex"] = srch_stff_form.sex.data
        session["blood-type"] = srch_stff_form.blood_type.data
        session["birth-date"] = srch_stff_form.birth_date.data
        session["created-at-begin"] = srch_stff_form.created_at_begin.data
        session["created-at-end"] = srch_stff_form.created_at_end.data
        session["updated-at-begin"] = srch_stff_form.updated_at_begin.data
        session["updated-at-end"] = srch_stff_form.updated_at_end.data
        session["sort-condition"] = srch_stff_form.sort_condition.data
        session["extract-condition"] = srch_stff_form.extract_condition.data

        # 検索条件を保持したまま, 検索結果ページへリダイレクトする.
        return redirect(url_for("view.search_staffs_results"))


# 「search_words_results」のためのビュー関数(=URLエンドポイント)を宣言・定義する.
@view.route("/search_words_results", methods=["GET", "POST"])
def search_words_results():
    # 関数内で使用する変数・オブジェクトを宣言・定義する.
    wrds_tmp = []
    wrds_fnl = []
    is_srch_done = False

    # 該当のURLエンドポイントに入ったことをロギングする.
    rslt = cr_engn.etc.logging__info("view at /search_words_results")

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

        # 検索条件(=検索キー)となる値をまとめて取得する.
        id = str(session["id"]).split(" ")
        spll_n_hdr = str(session["spell-and-header"])
        mn_n_bdy = str(session["mean-and-body"])
        intnt = str(session["intent"])
        sntmnt = str(session["sentiment"])
        sntmnt_spprt = str(session["sentiment-support"])
        strngth = str(session["strength"])
        prt_of_spch = str(session["part-of-speech"])
        stff_nm = str(session["staff-name"]).split(" ")
        stff_kn_nm = str(session["staff-kana-name"]).split(" ")
        crtd_at_bgn = session["created-at-begin"]
        crtd_at_end = session["created-at-end"]
        updtd_at_bgn = session["updated-at-begin"]
        updtd_at_end = session["updated-at-end"]
        srt_cndtn = str(session["sort-condition"])
        extrct_cndtn = str(session["extract-condition"])

        # 各種の検索条件に基づいてレコードを検索する.
        if (((len(id) == 1) and (id[0] == "")) == False):
            srch_trgt = id
            if ((srt_cndtn == "condition-1") and (extrct_cndtn == "condition-1")):
                  wrds_tmp = (
                  db_session.query(Word).filter(Word.id.in_(srch_trgt), Word.is_hidden == False).order_by(Word.id.asc()).all()
                  )
                  db_session.close()
                  is_srch_done = True
            elif ((srt_cndtn == "condition-1") and (extrct_cndtn == "condition-2")):
                  wrds_tmp = (
                  db_session.query(Word).filter(Word.id.in_(srch_trgt)).order_by(Word.id.asc()).all()
                  )
                  db_session.close()
                  is_srch_done = True
            elif ((srt_cndtn == "condition-2") and (extrct_cndtn == "condition-1")):
                  wrds_tmp = (
                  db_session.query(Word).filter(Word.id.in_(srch_trgt), Word.is_hidden == False).order_by(Word.id.desc()).all()
                  )
                  db_session.close()
                  is_srch_done = True
            else:
                  wrds_tmp = (
                  db_session.query(Word).filter(Word.id.in_(srch_trgt)).order_by(Word.id.desc()).all()
                  )
                  db_session.close()
                  is_srch_done = True
        if ((spll_n_hdr != "") and (is_srch_done == False)):
            srch_trgt = [spll_n_hdr]
            if ((srt_cndtn == "condition-1") and (extrct_cndtn == "condition-1")):
                  wrds_tmp = (
                  db_session.query(Word).filter(Word.spell_and_header.in_(srch_trgt), Word.is_hidden == False).order_by(Word.id.asc()).all()
                  )
                  db_session.close()
                  is_srch_done = True
            elif ((srt_cndtn == "condition-1") and (extrct_cndtn == "condition-2")):
                  wrds_tmp = (
                  db_session.query(Word).filter(Word.spell_and_header.in_(srch_trgt)).order_by(Word.id.asc()).all()
                  )
                  db_session.close()
                  is_srch_done = True
            elif ((srt_cndtn == "condition-2") and (extrct_cndtn == "condition-1")):
                  wrds_tmp = (
                  db_session.query(Word).filter(Word.spell_and_header.in_(srch_trgt), Word.is_hidden == False).order_by(Word.id.desc()).all()
                  )
                  db_session.close()
                  is_srch_done = True
            else:
                  wrds_tmp = (
                  db_session.query(Word).filter(Word.spell_and_header.in_(srch_trgt)).order_by(Word.id.desc()).all()
                  )
                  db_session.close()
                  is_srch_done = True
        if ((mn_n_bdy != "") and (is_srch_done == False)):
            srch_trgt = [mn_n_bdy]
            if ((srt_cndtn == "condition-1") and (extrct_cndtn == "condition-1")):
                  wrds_tmp = (
                  db_session.query(Word).filter(Word.mean_and_body.in_(srch_trgt), Word.is_hidden == False).order_by(Word.id.asc()).all()
                  )
                  db_session.close()
                  is_srch_done = True
            elif ((srt_cndtn == "condition-1") and (extrct_cndtn == "condition-2")):
                  wrds_tmp = (
                  db_session.query(Word).filter(Word.mean_and_body.in_(srch_trgt)).order_by(Word.id.asc()).all()
                  )
                  db_session.close()
                  is_srch_done = True
            elif ((srt_cndtn == "condition-2") and (extrct_cndtn == "condition-1")):
                  wrds_tmp = (
                  db_session.query(Word).filter(Word.mean_and_body.in_(srch_trgt), Word.is_hidden == False).order_by(Word.id.desc()).all()
                  )
                  db_session.close()
                  is_srch_done = True
            else:
                  wrds_tmp = (
                  db_session.query(Word).filter(Word.mean_and_body.in_(srch_trgt)).order_by(Word.id.desc()).all()
                  )
                  db_session.close()
                  is_srch_done = True
        if ((intnt != "") and (is_srch_done == False)):
            srch_trgt = [intnt]
            if ((srt_cndtn == "condition-1") and (extrct_cndtn == "condition-1")):
                  wrds_tmp = (
                  db_session.query(Word).filter(Word.intent.in_(srch_trgt), Word.is_hidden == False).order_by(Word.id.asc()).all()
                  )
                  db_session.close()
                  is_srch_done = True
            elif ((srt_cndtn == "condition-1") and (extrct_cndtn == "condition-2")):
                  wrds_tmp = (
                  db_session.query(Word).filter(Word.intent.in_(srch_trgt)).order_by(Word.id.asc()).all()
                  )
                  db_session.close()
                  is_srch_done = True
            elif ((srt_cndtn == "condition-2") and (extrct_cndtn == "condition-1")):
                  wrds_tmp = (
                  db_session.query(Word).filter(Word.intent.in_(srch_trgt), Word.is_hidden == False).order_by(Word.id.desc()).all()
                  )
                  db_session.close()
                  is_srch_done = True
            else:
                  wrds_tmp = (
                  db_session.query(Word).filter(Word.intent.in_(srch_trgt)).order_by(Word.id.desc()).all()
                  )
                  db_session.close()
                  is_srch_done = True
        if ((sntmnt != "") and (is_srch_done == False)):
            srch_trgt = [sntmnt]
            if ((srt_cndtn == "condition-1") and (extrct_cndtn == "condition-1")):
                  wrds_tmp = (
                  db_session.query(Word).filter(Word.sentiment.in_(srch_trgt), Word.is_hidden == False).order_by(Word.id.asc()).all()
                  )
                  db_session.close()
                  is_srch_done = True
            elif ((srt_cndtn == "condition-1") and (extrct_cndtn == "condition-2")):
                  wrds_tmp = (
                  db_session.query(Word).filter(Word.sentiment.in_(srch_trgt)).order_by(Word.id.asc()).all()
                  )
                  db_session.close()
                  is_srch_done = True
            elif ((srt_cndtn == "condition-2") and (extrct_cndtn == "condition-1")):
                  wrds_tmp = (
                  db_session.query(Word).filter(Word.sentiment.in_(srch_trgt), Word.is_hidden == False).order_by(Word.id.desc()).all()
                  )
                  db_session.close()
                  is_srch_done = True
            else:
                  wrds_tmp = (
                  db_session.query(Word).filter(Word.sentiment.in_(srch_trgt)).order_by(Word.id.desc()).all()
                  )
                  db_session.close()
                  is_srch_done = True
        if ((sntmnt_spprt != "") and (is_srch_done == False)):
            srch_trgt = [sntmnt_spprt]
            if ((srt_cndtn == "condition-1") and (extrct_cndtn == "condition-1")):
                  wrds_tmp = (
                  db_session.query(Word).filter(Word.sentiment_support.in_(srch_trgt), Word.is_hidden == False).order_by(Word.id.asc()).all()
                  )
                  db_session.close()
                  is_srch_done = True
            elif ((srt_cndtn == "condition-1") and (extrct_cndtn == "condition-2")):
                  wrds_tmp = (
                  db_session.query(Word).filter(Word.sentiment_support.in_(srch_trgt)).order_by(Word.id.asc()).all()
                  )
                  db_session.close()
                  is_srch_done = True
            elif ((srt_cndtn == "condition-2") and (extrct_cndtn == "condition-1")):
                  wrds_tmp = (
                  db_session.query(Word).filter(Word.sentiment_support.in_(srch_trgt), Word.is_hidden == False).order_by(Word.id.desc()).all()
                  )
                  db_session.close()
                  is_srch_done = True
            else:
                  wrds_tmp = (
                  db_session.query(Word).filter(Word.sentiment_support.in_(srch_trgt)).order_by(Word.id.desc()).all()
                  )
                  db_session.close()
                  is_srch_done = True
        if ((strngth != "") and (is_srch_done == False)):
            srch_trgt = [strngth]
            if ((srt_cndtn == "condition-1") and (extrct_cndtn == "condition-1")):
                  wrds_tmp = (
                  db_session.query(Word).filter(Word.strength.in_(srch_trgt), Word.is_hidden == False).order_by(Word.id.asc()).all()
                  )
                  db_session.close()
                  is_srch_done = True
            elif ((srt_cndtn == "condition-1") and (extrct_cndtn == "condition-2")):
                  wrds_tmp = (
                  db_session.query(Word).filter(Word.strength.in_(srch_trgt)).order_by(Word.id.asc()).all()
                  )
                  db_session.close()
                  is_srch_done = True
            elif ((srt_cndtn == "condition-2") and (extrct_cndtn == "condition-1")):
                  wrds_tmp = (
                  db_session.query(Word).filter(Word.strength.in_(srch_trgt), Word.is_hidden == False).order_by(Word.id.desc()).all()
                  )
                  db_session.close()
                  is_srch_done = True
            else:
                  wrds_tmp = (
                  db_session.query(Word).filter(Word.strength.in_(srch_trgt)).order_by(Word.id.desc()).all()
                  )
                  db_session.close()
                  is_srch_done = True
        if ((prt_of_spch != "") and (is_srch_done == False)):
            srch_trgt = [prt_of_spch]
            if ((srt_cndtn == "condition-1") and (extrct_cndtn == "condition-1")):
                  wrds_tmp = (
                  db_session.query(Word).filter(Word.part_of_speech.in_(srch_trgt), Word.is_hidden == False).order_by(Word.id.asc()).all()
                  )
                  db_session.close()
                  is_srch_done = True
            elif ((srt_cndtn == "condition-1") and (extrct_cndtn == "condition-2")):
                  wrds_tmp = (
                  db_session.query(Word).filter(Word.part_of_speech.in_(srch_trgt)).order_by(Word.id.asc()).all()
                  )
                  db_session.close()
                  is_srch_done = True
            elif ((srt_cndtn == "condition-2") and (extrct_cndtn == "condition-1")):
                  wrds_tmp = (
                  db_session.query(Word).filter(Word.part_of_speech.in_(srch_trgt), Word.is_hidden == False).order_by(Word.id.desc()).all()
                  )
                  db_session.close()
                  is_srch_done = True
            else:
                  wrds_tmp = (
                  db_session.query(Word).filter(Word.part_of_speech.in_(srch_trgt)).order_by(Word.id.desc()).all()
                  )
                  db_session.close()
                  is_srch_done = True
        if ((((len(stff_nm) == 1) and (stff_nm[0] == "")) == False) and (is_srch_done == False)):
            srch_trgt = stff_nm
            if ((srt_cndtn == "condition-1") and (extrct_cndtn == "condition-1")):
                  wrds_tmp = (
                  db_session.query(Word).filter(Word.staff_name.in_(srch_trgt), Word.is_hidden == False).order_by(Word.id.asc()).all()
                  )
                  db_session.close()
                  is_srch_done = True
            elif ((srt_cndtn == "condition-1") and (extrct_cndtn == "condition-2")):
                  wrds_tmp = (
                  db_session.query(Word).filter(Word.staff_name.in_(srch_trgt)).order_by(Word.id.asc()).all()
                  )
                  db_session.close()
                  is_srch_done = True
            elif ((srt_cndtn == "condition-2") and (extrct_cndtn == "condition-1")):
                  wrds_tmp = (
                  db_session.query(Word).filter(Word.staff_name.in_(srch_trgt), Word.is_hidden == False).order_by(Word.id.desc()).all()
                  )
                  db_session.close()
                  is_srch_done = True
            else:
                  wrds_tmp = (
                  db_session.query(Word).filter(Word.staff_name.in_(srch_trgt)).order_by(Word.id.desc()).all()
                  )
                  db_session.close()
                  is_srch_done = True
        if ((((len(stff_kn_nm) == 1) and (stff_kn_nm[0] == "")) == False) and (is_srch_done == False)):
            srch_trgt = stff_kn_nm
            if ((srt_cndtn == "condition-1") and (extrct_cndtn == "condition-1")):
                  wrds_tmp = (
                  db_session.query(Word).filter(Word.staff_kana_name.in_(srch_trgt), Word.is_hidden == False).order_by(Word.id.asc()).all()
                  )
                  db_session.close()
                  is_srch_done = True
            elif ((srt_cndtn == "condition-1") and (extrct_cndtn == "condition-2")):
                  wrds_tmp = (
                  db_session.query(Word).filter(Word.staff_kana_name.in_(srch_trgt)).order_by(Word.id.asc()).all()
                  )
                  db_session.close()
                  is_srch_done = True
            elif ((srt_cndtn == "condition-2") and (extrct_cndtn == "condition-1")):
                  wrds_tmp = (
                  db_session.query(Word).filter(Word.staff_kana_name.in_(srch_trgt), Word.is_hidden == False).order_by(Word.id.desc()).all()
                  )
                  db_session.close()
                  is_srch_done = True
            else:
                  wrds_tmp = (
                  db_session.query(Word).filter(Word.staff_kana_name.in_(srch_trgt)).order_by(Word.id.desc()).all()
                  )
                  db_session.close()
                  is_srch_done = True
        if (((crtd_at_bgn is not None) and (crtd_at_end is not None)) and (is_srch_done == False)):
            if ((srt_cndtn=="condition-1") and (extrct_cndtn=="condition-1")):
                  wrds_tmp = db_session.query(Word).filter(Word.created_at >= crtd_at_bgn, Word.created_at <= crtd_at_end, Word.is_hidden == False).order_by(Word.id.asc()).all()
                  db_session.close()
                  is_srch_done = True
            elif ((srt_cndtn=="condition-1") and (extrct_cndtn=="condition-2")):
                  wrds_tmp = db_session.query(Word).filter(Word.created_at >= crtd_at_bgn, Word.created_at <= crtd_at_end).order_by(Word.id.asc()).all()
                  db_session.close()
                  is_srch_done = True
            elif ((srt_cndtn=="condition-2") and (extrct_cndtn=="condition-1")):
                  wrds_tmp = db_session.query(Word).filter(Word.created_at >= crtd_at_bgn, Word.created_at <= crtd_at_end, Word.is_hidden == False).order_by(Word.id.desc()).all()
                  db_session.close()
                  is_srch_done = True
            else:
                  wrds_tmp = db_session.query(Word).filter(Word.created_at >= crtd_at_bgn, Word.created_at <= crtd_at_end).order_by(Word.id.desc()).all()
                  db_session.close()
                  is_srch_done = True
        if (((updtd_at_bgn is not None) and (updtd_at_end is not None)) and (is_srch_done == False)):
            if ((srt_cndtn=="condition-1") and (extrct_cndtn=="condition-1")):
                  wrds_tmp = db_session.query(Word).filter(Word.created_at >= updtd_at_bgn, Word.created_at <= updtd_at_end, Word.is_hidden == False).order_by(Word.id.asc()).all()
                  db_session.close()
            elif ((srt_cndtn=="condition-1") and (extrct_cndtn=="condition-2")):
                  wrds_tmp = db_session.query(Word).filter(Word.created_at >= updtd_at_bgn, Word.created_at <= updtd_at_end).order_by(Word.id.asc()).all()
                  db_session.close()
            elif ((srt_cndtn=="condition-2") and (extrct_cndtn=="condition-1")):
                  wrds_tmp = db_session.query(Word).filter(Word.created_at >= updtd_at_bgn, Word.created_at <= updtd_at_end, Word.is_hidden == False).order_by(Word.id.desc()).all()
                  db_session.close()
            else:
                  wrds_tmp = db_session.query(Word).filter(Word.created_at >= updtd_at_bgn, Word.created_at <= updtd_at_end).order_by(Word.id.desc()).all()
                  db_session.close()

        # 検索結果を整形し, 配列にセットしてテンプレートと共に返す.
        if wrds_tmp is not None:
            for wrd_tmp in wrds_tmp:
                if len(str(wrd_tmp.id)) > 6:
                    id_tmp = wrd_tmp.id[0:6] + "..."
                else:
                    id_tmp = wrd_tmp.id
                if len(wrd_tmp.spell_and_header) > 6:
                    spll_n_hdr_tmp = wrd_tmp.spell_and_header[0:6] + "..."
                else:
                    spll_n_hdr_tmp = wrd_tmp.spell_and_header
                if len(wrd_tmp.mean_and_body) > 6:
                    mn_n_bdy_tmp = wrd_tmp.mean_and_body[0:6] + "..."
                else:
                    mn_n_bdy_tmp = wrd_tmp.mean_and_body
                if len(wrd_tmp.staff_name) > 6:
                    stff_nm_tmp = wrd_tmp.staff_name[0:6] + "..."
                else:
                    stff_nm_tmp = wrd_tmp.staff_name
                wrds_fnl.append([id_tmp,
                                 spll_n_hdr_tmp,
                                 mn_n_bdy_tmp,
                                 stff_nm_tmp
                                ])
        per_pg = consts.WORD_ITEM_PER_PAGE
        pg = request.args.get(get_page_parameter(), type=int, default=1)
        pg_dat = wrds_fnl[(pg - 1) * per_pg : pg * per_pg]
        pgntn = Pagination(page=pg,
                           total=len(wrds_fnl),
                           per_page=per_pg,
                           css_framework=consts.PAGINATION_CSS
                          )
        return render_template("search_words_results.html", page_data=pg_dat, pagination=pgntn)

    if request.method == "POST":
        # 直前に, GETメソッドで該当ページを取得しているかを調べる.
        # 取得していなければ, 強制的に現在ページへリダイレクトする.
        if session["referrer-page"] != "view.search_words_results":
            return redirect(url_for("view.search_words_results"))

        # フォームボタン群の中から, 押下されたボタンに応じたページへリダイレクトする.
        if request.form["hidden-modify-item-id"] != "":
            session["hidden-modify-item-id"] = request.form["hidden-modify-item-id"]
            return redirect(url_for("view.modify_word"))
        if request.form["hidden-detail-item-id"] != "":
            session["hidden-detail-item-id"] = request.form["hidden-detail-item-id"]
            return redirect(url_for("view.detail_word"))

        # フォームが改竄されているので, その旨を通知するために例外を発生させる.
        raise BadRequest


# 「search_themes_results」のためのビュー関数(=URLエンドポイント)を宣言・定義する.
@view.route("/search_themes_results", methods=["GET", "POST"])
def search_themes_results():
    # 関数内で使用する変数・オブジェクトを宣言・定義する.
    thms_tmp = []
    thms_fnl = []
    is_srch_done = False

    # 該当のURLエンドポイントに入ったことをロギングする.
    rslt = cr_engn.etc.logging__info("view at /search_themes_results")

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

        # 検索条件(=検索キー)となる値をまとめて取得する.
        id = str(session["id"]).split(" ")
        spll_n_hdr = str(session["spell-and-header"])
        mn_n_bdy = str(session["mean-and-body"])
        ctgr_tgs = str(session["category-tags"]).split(" ")
        stff_nm = str(session["staff-name"]).split(" ")
        stff_kn_nm = str(session["staff-kana-name"]).split(" ")
        crtd_at_bgn = session["created-at-begin"]
        crtd_at_end = session["created-at-end"]
        updtd_at_bgn = session["updated-at-begin"]
        updtd_at_end = session["updated-at-end"]
        srt_cndtn = str(session["sort-condition"])
        extrct_cndtn = str(session["extract-condition"])

        # 各種の検索条件に基づいてレコードを検索する.
        if (((len(id) == 1) and (id[0] == "")) == False):
            srch_trgt = id
            if ((srt_cndtn == "condition-1") and (extrct_cndtn == "condition-1")):
                  thms_tmp = (
                  db_session.query(Theme).filter(Theme.id.in_(srch_trgt), Theme.is_hidden == False).order_by(Theme.id.asc()).all()
                  )
                  db_session.close()
                  is_srch_done = True
            elif ((srt_cndtn == "condition-1") and (extrct_cndtn == "condition-2")):
                  thms_tmp = (
                  db_session.query(Theme).filter(Theme.id.in_(srch_trgt)).order_by(Theme.id.asc()).all()
                  )
                  db_session.close()
                  is_srch_done = True
            elif ((srt_cndtn == "condition-2") and (extrct_cndtn == "condition-1")):
                  thms_tmp = (
                  db_session.query(Theme).filter(Theme.id.in_(srch_trgt), Theme.is_hidden == False).order_by(Theme.id.desc()).all()
                  )
                  db_session.close()
                  is_srch_done = True
            else:
                  thms_tmp = (
                  db_session.query(Theme).filter(Theme.id.in_(srch_trgt)).order_by(Theme.id.desc()).all()
                  )
                  db_session.close()
                  is_srch_done = True
        if ((spll_n_hdr != "") and (is_srch_done == False)):
            srch_trgt = [spll_n_hdr]
            if ((srt_cndtn == "condition-1") and (extrct_cndtn == "condition-1")):
                  thms_tmp = (
                  db_session.query(Theme).filter(Theme.spell_and_header.in_(srch_trgt), Theme.is_hidden == False).order_by(Theme.id.asc()).all()
                  )
                  db_session.close()
                  is_srch_done = True
            elif ((srt_cndtn == "condition-1") and (extrct_cndtn == "condition-2")):
                  thms_tmp = (
                  db_session.query(Theme).filter(Theme.spell_and_header.in_(srch_trgt)).order_by(Theme.id.asc()).all()
                  )
                  db_session.close()
                  is_srch_done = True
            elif ((srt_cndtn == "condition-2") and (extrct_cndtn == "condition-1")):
                  thms_tmp = (
                  db_session.query(Theme).filter(Theme.spell_and_header.in_(srch_trgt), Theme.is_hidden == False).order_by(Theme.id.desc()).all()
                  )
                  db_session.close()
                  is_srch_done = True
            else:
                  thms_tmp = (
                  db_session.query(Theme).filter(Theme.spell_and_header.in_(srch_trgt)).order_by(Theme.id.desc()).all()
                  )
                  db_session.close()
                  is_srch_done = True
        if ((mn_n_bdy != "") and (is_srch_done == False)):
            srch_trgt = [mn_n_bdy]
            if ((srt_cndtn == "condition-1") and (extrct_cndtn == "condition-1")):
                  thms_tmp = (
                  db_session.query(Theme).filter(Theme.mean_and_body.in_(srch_trgt), Theme.is_hidden == False).order_by(Theme.id.asc()).all()
                  )
                  db_session.close()
                  is_srch_done = True
            elif ((srt_cndtn == "condition-1") and (extrct_cndtn == "condition-2")):
                  thms_tmp = (
                  db_session.query(Theme).filter(Theme.mean_and_body.in_(srch_trgt)).order_by(Theme.id.asc()).all()
                  )
                  db_session.close()
                  is_srch_done = True
            elif ((srt_cndtn == "condition-2") and (extrct_cndtn == "condition-1")):
                  thms_tmp = (
                  db_session.query(Theme).filter(Theme.mean_and_body.in_(srch_trgt), Theme.is_hidden == False).order_by(Theme.id.desc()).all()
                  )
                  db_session.close()
                  is_srch_done = True
            else:
                  thms_tmp = (
                  db_session.query(Theme).filter(Theme.mean_and_body.in_(srch_trgt)).order_by(Theme.id.desc()).all()
                  )
                  db_session.close()
                  is_srch_done = True
        if (((len(ctgr_tgs) == 1) and (ctgr_tgs[0] == "")) == False):
            srch_trgt = ctgr_tgs
            if ((srt_cndtn == "condition-1") and (extrct_cndtn == "condition-1")):
                  thms_tmp = (
                  db_session.query(Theme).filter(Theme.mean_and_body.in_(srch_trgt), Theme.is_hidden == False).order_by(Theme.id.asc()).all()
                  )
                  db_session.close()
                  is_srch_done = True
            elif ((srt_cndtn == "condition-1") and (extrct_cndtn == "condition-2")):
                  thms_tmp = (
                  db_session.query(Theme).filter(Theme.mean_and_body.in_(srch_trgt)).order_by(Theme.id.asc()).all()
                  )
                  db_session.close()
                  is_srch_done = True
            elif ((srt_cndtn == "condition-2") and (extrct_cndtn == "condition-1")):
                  thms_tmp = (
                  db_session.query(Theme).filter(Theme.mean_and_body.in_(srch_trgt), Theme.is_hidden == False).order_by(Theme.id.desc()).all()
                  )
                  db_session.close()
                  is_srch_done = True
            else:
                  thms_tmp = (
                  db_session.query(Theme).filter(Theme.mean_and_body.in_(srch_trgt)).order_by(Theme.id.desc()).all()
                  )
                  db_session.close()
                  is_srch_done = True
        if ((((len(stff_nm) == 1) and (stff_nm[0] == "")) == False) and (is_srch_done == False)):
            srch_trgt = stff_nm
            if ((srt_cndtn == "condition-1") and (extrct_cndtn == "condition-1")):
                  thms_tmp = (
                  db_session.query(Theme).filter(Theme.staff_name.in_(srch_trgt), Theme.is_hidden == False).order_by(Theme.id.asc()).all()
                  )
                  db_session.close()
                  is_srch_done = True
            elif ((srt_cndtn == "condition-1") and (extrct_cndtn == "condition-2")):
                  thms_tmp = (
                  db_session.query(Theme).filter(Theme.staff_name.in_(srch_trgt)).order_by(Theme.id.asc()).all()
                  )
                  db_session.close()
                  is_srch_done = True
            elif ((srt_cndtn == "condition-2") and (extrct_cndtn == "condition-1")):
                  thms_tmp = (
                  db_session.query(Theme).filter(Theme.staff_name.in_(srch_trgt), Theme.is_hidden == False).order_by(Theme.id.desc()).all()
                  )
                  db_session.close()
                  is_srch_done = True
            else:
                  thms_tmp = (
                  db_session.query(Theme).filter(Theme.staff_name.in_(srch_trgt)).order_by(Theme.id.desc()).all()
                  )
                  db_session.close()
                  is_srch_done = True
        if ((((len(stff_kn_nm) == 1) and (stff_kn_nm[0] == "")) == False) and (is_srch_done == False)):
            srch_trgt = stff_kn_nm
            if ((srt_cndtn == "condition-1") and (extrct_cndtn == "condition-1")):
                  thms_tmp = (
                  db_session.query(Theme).filter(Theme.staff_kana_name.in_(srch_trgt), Theme.is_hidden == False).order_by(Theme.id.asc()).all()
                  )
                  db_session.close()
                  is_srch_done = True
            elif ((srt_cndtn == "condition-1") and (extrct_cndtn == "condition-2")):
                  thms_tmp = (
                  db_session.query(Theme).filter(Theme.staff_kana_name.in_(srch_trgt)).order_by(Theme.id.asc()).all()
                  )
                  db_session.close()
                  is_srch_done = True
            elif ((srt_cndtn == "condition-2") and (extrct_cndtn == "condition-1")):
                  thms_tmp = (
                  db_session.query(Theme).filter(Theme.staff_kana_name.in_(srch_trgt), Theme.is_hidden == False).order_by(Theme.id.desc()).all()
                  )
                  db_session.close()
                  is_srch_done = True
            else:
                  thms_tmp = (
                  db_session.query(Theme).filter(Theme.staff_kana_name.in_(srch_trgt)).order_by(Theme.id.desc()).all()
                  )
                  db_session.close()
                  is_srch_done = True
        if (((crtd_at_bgn is not None) and (crtd_at_end is not None)) and (is_srch_done == False)):
            if ((srt_cndtn=="condition-1") and (extrct_cndtn=="condition-1")):
                  thms_tmp = (
                  db_session.query(Theme).filter(Theme.created_at >= crtd_at_bgn, Theme.created_at <= crtd_at_end, Theme.is_hidden == False).order_by(Theme.id.asc()).all()
                  )
                  db_session.close()
                  is_srch_done = True
            elif ((srt_cndtn=="condition-1") and (extrct_cndtn=="condition-2")):
                  thms_tmp = (
                  db_session.query(Theme).filter(Theme.created_at >= crtd_at_bgn, Theme.created_at <= crtd_at_end).order_by(Theme.id.asc()).all()
                  )
                  db_session.close()
                  is_srch_done = True
            elif ((srt_cndtn=="condition-2") and (extrct_cndtn=="condition-1")):
                  thms_tmp = (
                  db_session.query(Theme).filter(Theme.created_at >= crtd_at_bgn, Theme.created_at <= crtd_at_end, Theme.is_hidden == False).order_by(Theme.id.desc()).all()
                  )
                  db_session.close()
                  is_srch_done = True
            else:
                  wrds_tmp = db_session.query(Theme).filter(Theme.created_at >= crtd_at_bgn, Theme.created_at <= crtd_at_end).order_by(Theme.id.desc()).all()
                  db_session.close()
                  is_srch_done = True
        if (((updtd_at_bgn is not None) and (updtd_at_end is not None)) and (is_srch_done == False)):
            if ((srt_cndtn=="condition-1") and (extrct_cndtn=="condition-1")):
                  thms_tmp = (
                  db_session.query(Theme).filter(Theme.created_at >= updtd_at_bgn, Theme.created_at <= updtd_at_end, Theme.is_hidden == False).order_by(Theme.id.asc()).all()
                  )
                  db_session.close()
            elif ((srt_cndtn=="condition-1") and (extrct_cndtn=="condition-2")):
                  thms_tmp = (
                  db_session.query(Theme).filter(Theme.created_at >= updtd_at_bgn, Theme.created_at <= updtd_at_end).order_by(Theme.id.asc()).all()
                  )
                  db_session.close()
            elif ((srt_cndtn=="condition-2") and (extrct_cndtn=="condition-1")):
                  thms_tmp = (
                  db_session.query(Theme).filter(Theme.created_at >= updtd_at_bgn, Theme.created_at <= updtd_at_end, Theme.is_hidden == False).order_by(Theme.id.desc()).all()
                  )
                  db_session.close()
            else:
                  thms_tmp = (
                  db_session.query(Theme).filter(Theme.created_at >= updtd_at_bgn, Theme.created_at <= updtd_at_end).order_by(Theme.id.desc()).all()
                  )
                  db_session.close()

        # 検索結果を整形し, 配列にセットしてテンプレートと共に返す.
        if thms_tmp is not None:
            for thm_tmp in thms_tmp:
                if len(str(thm_tmp.id)) > 6:
                    id_tmp = thm_tmp.id[0:6] + "..."
                else:
                    id_tmp = thm_tmp.id
                if len(thm_tmp.spell_and_header) > 6:
                    spll_n_hdr_tmp = thm_tmp.spell_and_header[0:6] + "..."
                else:
                    spll_n_hdr_tmp = thm_tmp.spell_and_header
                if len(thm_tmp.mean_and_body) > 6:
                    mn_n_bdy_tmp = thm_tmp.mean_and_body[0:6] + "..."
                else:
                    mn_n_bdy_tmp = thm_tmp.mean_and_body
                if len(thm_tmp.staff_name) > 6:
                    stff_nm_tmp = thm_tmp.staff_name[0:6] + "..."
                else:
                    stff_nm_tmp = thm_tmp.staff_name
                thms_fnl.append([id_tmp,
                                 spll_n_hdr_tmp,
                                 mn_n_bdy_tmp,
                                 stff_nm_tmp
                                ])
        per_pg = consts.THEME_ITEM_PER_PAGE
        pg = request.args.get(get_page_parameter(), type=int, default=1)
        pg_dat = thms_fnl[(pg - 1) * per_pg : pg * per_pg]
        pgntn = Pagination(page=pg,
                           total=len(thms_fnl),
                           per_page=per_pg,
                           css_framework=consts.PAGINATION_CSS
                          )
        return render_template("search_themes_results.html", page_data=pg_dat, pagination=pgntn)

    if request.method == "POST":
        # 直前に, GETメソッドで該当ページを取得しているかを調べる.
        # 取得していなければ, 強制的に現在ページへリダイレクトする.
        if session["referrer-page"] != "view.search_themes_results":
            return redirect(url_for("view.search_themes_results"))

        # フォームボタン群の中から, 押下されたボタンに応じたページへリダイレクトする.
        if request.form["hidden-modify-item-id"] != "":
            session["hidden-modify-item-id"] = request.form["hidden-modify-item-id"]
            return redirect(url_for("view.modify_theme"))
        if request.form["hidden-detail-item-id"] != "":
            session["hidden-detail-item-id"] = request.form["hidden-detail-item-id"]
            return redirect(url_for("view.detail_theme"))

        # フォームが改竄されているので, その旨を通知するために例外を発生させる.
        raise BadRequest


# 「search_categories_results」のためのビュー関数(=URLエンドポイント)を宣言・定義する.
@view.route("/search_categories_results", methods=["GET", "POST"])
def search_categories_results():
    # 関数内で使用する変数・オブジェクトを宣言・定義する.
    ctgrs_tmp = []
    ctgrs_fnl = []
    is_srch_done = False

    # 該当のURLエンドポイントに入ったことをロギングする.
    rslt = cr_engn.etc.logging__info("view at /search_categories_results")

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

        # 検索条件(=検索キー)となる値をまとめて取得する.
        id = str(session["id"]).split(" ")
        spll_n_hdr = str(session["spell-and-header"])
        mn_n_bdy = str(session["mean-and-body"])
        prnt_ctgr_tgs = str(session["parent-category-tags"]).split(" ")
        sblng_ctgr_tgs = str(session["sibling-category-tags"]).split(" ")
        chld_ctgr_tgs = str(session["child-category-tags"]).split(" ")
        stff_nm = str(session["staff-name"]).split(" ")
        stff_kn_nm = str(session["staff-kana-name"]).split(" ")
        crtd_at_bgn = session["created-at-begin"]
        crtd_at_end = session["created-at-end"]
        updtd_at_bgn = session["updated-at-begin"]
        updtd_at_end = session["updated-at-end"]
        srt_cndtn = str(session["sort-condition"])
        extrct_cndtn = str(session["extract-condition"])

        # 各種の検索条件に基づいてレコードを検索する.
        if (((len(id) == 1) and (id[0] == "")) == False):
            srch_trgt = id
            if ((srt_cndtn == "condition-1") and (extrct_cndtn == "condition-1")):
                  ctgrs_tmp = (
                  db_session.query(Category).filter(Category.id.in_(srch_trgt), Category.is_hidden == False).order_by(Category.id.asc()).all()
                  )
                  db_session.close()
                  is_srch_done = True
            elif ((srt_cndtn == "condition-1") and (extrct_cndtn == "condition-2")):
                  ctgrs_tmp = (
                  db_session.query(Category).filter(Category.id.in_(srch_trgt)).order_by(Category.id.asc()).all()
                  )
                  db_session.close()
                  is_srch_done = True
            elif ((srt_cndtn == "condition-2") and (extrct_cndtn == "condition-1")):
                  ctgrs_tmp = (
                  db_session.query(Category).filter(Category.id.in_(srch_trgt), Category.is_hidden == False).order_by(Category.id.desc()).all()
                  )
                  db_session.close()
                  is_srch_done = True
            else:
                  ctgrs_tmp = (
                  db_session.query(Category).filter(Category.id.in_(srch_trgt)).order_by(Category.id.desc()).all()
                  )
                  db_session.close()
                  is_srch_done = True
        if ((spll_n_hdr != "") and (is_srch_done == False)):
            srch_trgt = [spll_n_hdr]
            if ((srt_cndtn == "condition-1") and (extrct_cndtn == "condition-1")):
                  ctgrs_tmp = (
                  db_session.query(Category).filter(Category.spell_and_header.in_(srch_trgt), Category.is_hidden == False).order_by(Category.id.asc()).all()
                  )
                  db_session.close()
                  is_srch_done = True
            elif ((srt_cndtn == "condition-1") and (extrct_cndtn == "condition-2")):
                  ctgrs_tmp = (
                  db_session.query(Category).filter(Category.spell_and_header.in_(srch_trgt)).order_by(Category.id.asc()).all()
                  )
                  db_session.close()
                  is_srch_done = True
            elif ((srt_cndtn == "condition-2") and (extrct_cndtn == "condition-1")):
                  ctgrs_tmp = (
                  db_session.query(Category).filter(Category.spell_and_header.in_(srch_trgt), Category.is_hidden == False).order_by(Category.id.desc()).all()
                  )
                  db_session.close()
                  is_srch_done = True
            else:
                  ctgrs_tmp = (
                  db_session.query(Category).filter(Category.spell_and_header.in_(srch_trgt)).order_by(Category.id.desc()).all()
                  )
                  db_session.close()
                  is_srch_done = True
        if ((mn_n_bdy != "") and (is_srch_done == False)):
            srch_trgt = [mn_n_bdy]
            if ((srt_cndtn == "condition-1") and (extrct_cndtn == "condition-1")):
                  ctgrs_tmp = (
                  db_session.query(Category).filter(Category.mean_and_body.in_(srch_trgt), Category.is_hidden == False).order_by(Category.id.asc()).all()
                  )
                  db_session.close()
                  is_srch_done = True
            elif ((srt_cndtn == "condition-1") and (extrct_cndtn == "condition-2")):
                  ctgrs_tmp = (
                  db_session.query(Category).filter(Category.mean_and_body.in_(srch_trgt)).order_by(Category.id.asc()).all()
                  )
                  db_session.close()
                  is_srch_done = True
            elif ((srt_cndtn == "condition-2") and (extrct_cndtn == "condition-1")):
                  ctgrs_tmp = (
                  db_session.query(Category).filter(Category.mean_and_body.in_(srch_trgt), Category.is_hidden == False).order_by(Category.id.desc()).all()
                  )
                  db_session.close()
                  is_srch_done = True
            else:
                  ctgrs_tmp = (
                  db_session.query(Category).filter(Category.mean_and_body.in_(srch_trgt)).order_by(Category.id.desc()).all()
                  )
                  db_session.close()
                  is_srch_done = True
        if (((len(prnt_ctgr_tgs) == 1) and (prnt_ctgr_tgs[0] == "")) == False):
            srch_trgt = prnt_ctgr_tgs
            if ((srt_cndtn == "condition-1") and (extrct_cndtn == "condition-1")):
                  ctgrs_tmp = (
                  db_session.query(Category).filter(Category.mean_and_body.in_(srch_trgt), Category.is_hidden == False).order_by(Category.id.asc()).all()
                  )
                  db_session.close()
                  is_srch_done = True
            elif ((srt_cndtn == "condition-1") and (extrct_cndtn == "condition-2")):
                  ctgrs_tmp = (
                  db_session.query(Category).filter(Category.mean_and_body.in_(srch_trgt)).order_by(Category.id.asc()).all()
                  )
                  db_session.close()
                  is_srch_done = True
            elif ((srt_cndtn == "condition-2") and (extrct_cndtn == "condition-1")):
                  ctgrs_tmp = (
                  db_session.query(Category).filter(Category.mean_and_body.in_(srch_trgt), Category.is_hidden == False).order_by(Category.id.desc()).all()
                  )
                  db_session.close()
                  is_srch_done = True
            else:
                  ctgrs_tmp = (
                  db_session.query(Category).filter(Category.mean_and_body.in_(srch_trgt)).order_by(Category.id.desc()).all()
                  )
                  db_session.close()
                  is_srch_done = True
        if (((len(sblng_ctgr_tgs) == 1) and (sblng_ctgr_tgs[0] == "")) == False):
            srch_trgt = sblng_ctgr_tgs
            if ((srt_cndtn == "condition-1") and (extrct_cndtn == "condition-1")):
                  ctgrs_tmp = (
                  db_session.query(Category).filter(Category.mean_and_body.in_(srch_trgt), Category.is_hidden == False).order_by(Category.id.asc()).all()
                  )
                  db_session.close()
                  is_srch_done = True
            elif ((srt_cndtn == "condition-1") and (extrct_cndtn == "condition-2")):
                  ctgrs_tmp = (
                  db_session.query(Category).filter(Category.mean_and_body.in_(srch_trgt)).order_by(Category.id.asc()).all()
                  )
                  db_session.close()
                  is_srch_done = True
            elif ((srt_cndtn == "condition-2") and (extrct_cndtn == "condition-1")):
                  ctgrs_tmp = (
                  db_session.query(Category).filter(Category.mean_and_body.in_(srch_trgt), Category.is_hidden == False).order_by(Category.id.desc()).all()
                  )
                  db_session.close()
                  is_srch_done = True
            else:
                  ctgrs_tmp = (
                  db_session.query(Category).filter(Category.mean_and_body.in_(srch_trgt)).order_by(Category.id.desc()).all()
                  )
                  db_session.close()
                  is_srch_done = True
        if (((len(chld_ctgr_tgs) == 1) and (chld_ctgr_tgs[0] == "")) == False):
            srch_trgt = chld_ctgr_tgs
            if ((srt_cndtn == "condition-1") and (extrct_cndtn == "condition-1")):
                  ctgrs_tmp = (
                  db_session.query(Category).filter(Category.mean_and_body.in_(srch_trgt), Category.is_hidden == False).order_by(Category.id.asc()).all()
                  )
                  db_session.close()
                  is_srch_done = True
            elif ((srt_cndtn == "condition-1") and (extrct_cndtn == "condition-2")):
                  ctgrs_tmp = (
                  db_session.query(Category).filter(Category.mean_and_body.in_(srch_trgt)).order_by(Category.id.asc()).all()
                  )
                  db_session.close()
                  is_srch_done = True
            elif ((srt_cndtn == "condition-2") and (extrct_cndtn == "condition-1")):
                  ctgrs_tmp = (
                  db_session.query(Category).filter(Category.mean_and_body.in_(srch_trgt), Category.is_hidden == False).order_by(Category.id.desc()).all()
                  )
                  db_session.close()
                  is_srch_done = True
            else:
                  ctgrs_tmp = (
                  db_session.query(Category).filter(Category.mean_and_body.in_(srch_trgt)).order_by(Category.id.desc()).all()
                  )
                  db_session.close()
                  is_srch_done = True
        if ((((len(stff_nm) == 1) and (stff_nm[0] == "")) == False) and (is_srch_done == False)):
            srch_trgt = stff_nm
            if ((srt_cndtn == "condition-1") and (extrct_cndtn == "condition-1")):
                  ctgrs_tmp = (
                  db_session.query(Category).filter(Category.staff_name.in_(srch_trgt), Category.is_hidden == False).order_by(Category.id.asc()).all()
                  )
                  db_session.close()
                  is_srch_done = True
            elif ((srt_cndtn == "condition-1") and (extrct_cndtn == "condition-2")):
                  ctgrs_tmp = (
                  db_session.query(Category).filter(Category.staff_name.in_(srch_trgt)).order_by(Category.id.asc()).all()
                  )
                  db_session.close()
                  is_srch_done = True
            elif ((srt_cndtn == "condition-2") and (extrct_cndtn == "condition-1")):
                  ctgrs_tmp = (
                  db_session.query(Category).filter(Category.staff_name.in_(srch_trgt), Category.is_hidden == False).order_by(Category.id.desc()).all()
                  )
                  db_session.close()
                  is_srch_done = True
            else:
                  ctgrs_tmp = (
                  db_session.query(Category).filter(Category.staff_name.in_(srch_trgt)).order_by(Category.id.desc()).all()
                  )
                  db_session.close()
                  is_srch_done = True
        if ((((len(stff_kn_nm) == 1) and (stff_kn_nm[0] == "")) == False) and (is_srch_done == False)):
            srch_trgt = stff_kn_nm
            if ((srt_cndtn == "condition-1") and (extrct_cndtn == "condition-1")):
                  ctgrs_tmp = (
                  db_session.query(Category).filter(Category.staff_kana_name.in_(srch_trgt), Category.is_hidden == False).order_by(Category.id.asc()).all()
                  )
                  db_session.close()
                  is_srch_done = True
            elif ((srt_cndtn == "condition-1") and (extrct_cndtn == "condition-2")):
                  ctgrs_tmp = (
                  db_session.query(Category).filter(Category.staff_kana_name.in_(srch_trgt)).order_by(Category.id.asc()).all()
                  )
                  db_session.close()
                  is_srch_done = True
            elif ((srt_cndtn == "condition-2") and (extrct_cndtn == "condition-1")):
                  ctgrs_tmp = (
                  db_session.query(Category).filter(Category.staff_kana_name.in_(srch_trgt), Category.is_hidden == False).order_by(Category.id.desc()).all()
                  )
                  db_session.close()
                  is_srch_done = True
            else:
                  ctgrs_tmp = (
                  db_session.query(Category).filter(Category.staff_kana_name.in_(srch_trgt)).order_by(Category.id.desc()).all()
                  )
                  db_session.close()
                  is_srch_done = True
        if (((crtd_at_bgn is not None) and (crtd_at_end is not None)) and (is_srch_done == False)):
            if ((srt_cndtn=="condition-1") and (extrct_cndtn=="condition-1")):
                  ctgrs_tmp = (
                  db_session.query(Category).filter(Category.created_at >= crtd_at_bgn, Category.created_at <= crtd_at_end, Category.is_hidden == False).order_by(Category.id.asc()).all()
                  )
                  db_session.close()
                  is_srch_done = True
            elif ((srt_cndtn=="condition-1") and (extrct_cndtn=="condition-2")):
                  ctgrs_tmp = (
                  db_session.query(Category).filter(Category.created_at >= crtd_at_bgn, Category.created_at <= crtd_at_end).order_by(Category.id.asc()).all()
                  )
                  db_session.close()
                  is_srch_done = True
            elif ((srt_cndtn=="condition-2") and (extrct_cndtn=="condition-1")):
                  ctgrs_tmp = (
                  db_session.query(Category).filter(Category.created_at >= crtd_at_bgn, Category.created_at <= crtd_at_end, Category.is_hidden == False).order_by(Category.id.desc()).all()
                  )
                  db_session.close()
                  is_srch_done = True
            else:
                  ctgrs_tmp = (
                  db_session.query(Category).filter(Category.created_at >= crtd_at_bgn, Category.created_at <= crtd_at_end).order_by(Category.id.desc()).all()
                  )
                  db_session.close()
                  is_srch_done = True
        if (((updtd_at_bgn is not None) and (updtd_at_end is not None)) and (is_srch_done == False)):
            if ((srt_cndtn=="condition-1") and (extrct_cndtn=="condition-1")):
                  ctgrs_tmp = (
                  db_session.query(Category).filter(Category.created_at >= updtd_at_bgn, Category.created_at <= updtd_at_end, Category.is_hidden == False).order_by(Category.id.asc()).all()
                  )
                  db_session.close()
            elif ((srt_cndtn=="condition-1") and (extrct_cndtn=="condition-2")):
                  ctgrs_tmp = (
                  db_session.query(Category).filter(Category.created_at >= updtd_at_bgn, Category.created_at <= updtd_at_end).order_by(Category.id.asc()).all()
                  )
                  db_session.close()
            elif ((srt_cndtn=="condition-2") and (extrct_cndtn=="condition-1")):
                  ctgrs_tmp = (
                  db_session.query(Category).filter(Category.created_at >= updtd_at_bgn, Category.created_at <= updtd_at_end, Category.is_hidden == False).order_by(Category.id.desc()).all()
                  )
                  db_session.close()
            else:
                  ctgrs_tmp = (
                  db_session.query(Category).filter(Category.created_at >= updtd_at_bgn, Category.created_at <= updtd_at_end).order_by(Category.id.desc()).all()
                  )
                  db_session.close()

        # 検索結果を整形し, 配列にセットしてテンプレートと共に返す.
        if ctgrs_tmp is not None:
            for ctgr_tmp in ctgrs_tmp:
                if len(str(ctgr_tmp.id)) > 6:
                    id_tmp = ctgr_tmp.id[0:6] + "..."
                else:
                    id_tmp = ctgr_tmp.id
                if len(ctgr_tmp.spell_and_header) > 6:
                    spll_n_hdr_tmp = ctgr_tmp.spell_and_header[0:6] + "..."
                else:
                    spll_n_hdr_tmp = ctgr_tmp.spell_and_header
                if len(ctgr_tmp.mean_and_body) > 6:
                    mn_n_bdy_tmp = ctgr_tmp.mean_and_body[0:6] + "..."
                else:
                    mn_n_bdy_tmp = ctgr_tmp.mean_and_body
                if len(ctgr_tmp.staff_name) > 6:
                    stff_nm_tmp = ctgr_tmp.staff_name[0:6] + "..."
                else:
                    stff_nm_tmp = ctgr_tmp.staff_name
                ctgrs_fnl.append([id_tmp,
                                 spll_n_hdr_tmp,
                                 mn_n_bdy_tmp,
                                 stff_nm_tmp
                                ])
        per_pg = consts.CATEGORY_ITEM_PER_PAGE
        pg = request.args.get(get_page_parameter(), type=int, default=1)
        pg_dat = ctgrs_fnl[(pg - 1) * per_pg : pg * per_pg]
        pgntn = Pagination(page=pg,
                           total=len(ctgrs_fnl),
                           per_page=per_pg,
                           css_framework=consts.PAGINATION_CSS
                          )
        return render_template("search_categories_results.html", page_data=pg_dat, pagination=pgntn)

    if request.method == "POST":
        # 直前に, GETメソッドで該当ページを取得しているかを調べる.
        # 取得していなければ, 強制的に現在ページへリダイレクトする.
        if session["referrer-page"] != "view.search_categories_results":
            return redirect(url_for("view.search_categories_results"))

        # フォームボタン群の中から, 押下されたボタンに応じたページへリダイレクトする.
        if request.form["hidden-modify-item-id"] != "":
            session["hidden-modify-item-id"] = request.form["hidden-modify-item-id"]
            return redirect(url_for("view.modify_category"))
        if request.form["hidden-detail-item-id"] != "":
            session["hidden-detail-item-id"] = request.form["hidden-detail-item-id"]
            return redirect(url_for("view.detail_category"))

        # フォームが改竄されているので, その旨を通知するために例外を発生させる.
        raise BadRequest


# 「search_knowledges_results」のためのビュー関数(=URLエンドポイント)を宣言・定義する.
@view.route("/search_knowledges_results", methods=["GET", "POST"])
def search_knowledges_results():
    # 関数内で使用する変数・オブジェクトを宣言・定義する.
    fcts_tmp = []
    fcts_fnl = []
    is_srch_done = False

    # 該当のURLエンドポイントに入ったことをロギングする.
    rslt = cr_engn.etc.logging__info("view at /search_knowledges_results")

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

        # 検索条件(=検索キー)となる値をまとめて取得する.
        id = str(session["id"]).split(" ")
        spll_n_hdr = str(session["spell-and-header"])
        mn_n_bdy = str(session["mean-and-body"])
        ctgr_tgs = str(session["category-tags"]).split(" ")
        has_img = str(session["has-image"])
        has_snd = str(session["has-sound"])
        has_vdo = str(session["has-video"])
        stff_nm = str(session["staff-name"]).split(" ")
        stff_kn_nm = str(session["staff-kana-name"]).split(" ")
        crtd_at_bgn = session["created-at-begin"]
        crtd_at_end = session["created-at-end"]
        updtd_at_bgn = session["updated-at-begin"]
        updtd_at_end = session["updated-at-end"]
        srt_cndtn = str(session["sort-condition"])
        extrct_cndtn = str(session["extract-condition"])

        # 各種の検索条件に基づいてレコードを検索する.
        if (((len(id) == 1) and (id[0] == "")) == False):
            srch_trgt = id
            if ((srt_cndtn == "condition-1") and (extrct_cndtn == "condition-1")):
                  fcts_tmp = (
                  db_session.query(Fact).filter(Fact.id.in_(srch_trgt), Fact.is_hidden == False).order_by(Fact.id.asc()).all()
                  )
                  db_session.close()
                  is_srch_done = True
            elif ((srt_cndtn == "condition-1") and (extrct_cndtn == "condition-2")):
                  fcts_tmp = (
                  db_session.query(Fact).filter(Fact.id.in_(srch_trgt)).order_by(Fact.id.asc()).all()
                  )
                  db_session.close()
                  is_srch_done = True
            elif ((srt_cndtn == "condition-2") and (extrct_cndtn == "condition-1")):
                  fcts_tmp = (
                  db_session.query(Fact).filter(Fact.id.in_(srch_trgt), Fact.is_hidden == False).order_by(Fact.id.desc()).all()
                  )
                  db_session.close()
                  is_srch_done = True
            else:
                  fcts_tmp = (
                  db_session.query(Fact).filter(Fact.id.in_(srch_trgt)).order_by(Fact.id.desc()).all()
                  )
                  db_session.close()
                  is_srch_done = True
        if ((spll_n_hdr != "") and (is_srch_done == False)):
            srch_trgt = [spll_n_hdr]
            if ((srt_cndtn == "condition-1") and (extrct_cndtn == "condition-1")):
                  fcts_tmp = (
                  db_session.query(Fact).filter(Fact.spell_and_header.in_(srch_trgt), Fact.is_hidden == False).order_by(Fact.id.asc()).all()
                  )
                  db_session.close()
                  is_srch_done = True
            elif ((srt_cndtn == "condition-1") and (extrct_cndtn == "condition-2")):
                  fcts_tmp = (
                  db_session.query(Fact).filter(Fact.spell_and_header.in_(srch_trgt)).order_by(Fact.id.asc()).all()
                  )
                  db_session.close()
                  is_srch_done = True
            elif ((srt_cndtn == "condition-2") and (extrct_cndtn == "condition-1")):
                  fcts_tmp = (
                  db_session.query(Fact).filter(Fact.spell_and_header.in_(srch_trgt), Fact.is_hidden == False).order_by(Fact.id.desc()).all()
                  )
                  db_session.close()
                  is_srch_done = True
            else:
                  fcts_tmp = (
                  db_session.query(Fact).filter(Fact.spell_and_header.in_(srch_trgt)).order_by(Fact.id.desc()).all()
                  )
                  db_session.close()
                  is_srch_done = True
        if ((mn_n_bdy != "") and (is_srch_done == False)):
            srch_trgt = [mn_n_bdy]
            if ((srt_cndtn == "condition-1") and (extrct_cndtn == "condition-1")):
                  fcts_tmp = (
                  db_session.query(Fact).filter(Fact.mean_and_body.in_(srch_trgt), Fact.is_hidden == False).order_by(Fact.id.asc()).all()
                  )
                  db_session.close()
                  is_srch_done = True
            elif ((srt_cndtn == "condition-1") and (extrct_cndtn == "condition-2")):
                  fcts_tmp = (
                  db_session.query(Fact).filter(Fact.mean_and_body.in_(srch_trgt)).order_by(Fact.id.asc()).all()
                  )
                  db_session.close()
                  is_srch_done = True
            elif ((srt_cndtn == "condition-2") and (extrct_cndtn == "condition-1")):
                  fcts_tmp = (
                  db_session.query(Fact).filter(Fact.mean_and_body.in_(srch_trgt), Fact.is_hidden == False).order_by(Fact.id.desc()).all()
                  )
                  db_session.close()
                  is_srch_done = True
            else:
                  fcts_tmp = (
                  db_session.query(Fact).filter(Fact.mean_and_body.in_(srch_trgt)).order_by(Fact.id.desc()).all()
                  )
                  db_session.close()
                  is_srch_done = True
        if (((len(ctgr_tgs) == 1) and (ctgr_tgs[0] == "")) == False):
            srch_trgt = ctgr_tgs
            if ((srt_cndtn == "condition-1") and (extrct_cndtn == "condition-1")):
                  fcts_tmp = (
                  db_session.query(Fact).filter(Fact.mean_and_body.in_(srch_trgt), Fact.is_hidden == False).order_by(Fact.id.asc()).all()
                  )
                  db_session.close()
                  is_srch_done = True
            elif ((srt_cndtn == "condition-1") and (extrct_cndtn == "condition-2")):
                  fcts_tmp = (
                  db_session.query(Fact).filter(Fact.mean_and_body.in_(srch_trgt)).order_by(Fact.id.asc()).all()
                  )
                  db_session.close()
                  is_srch_done = True
            elif ((srt_cndtn == "condition-2") and (extrct_cndtn == "condition-1")):
                  fcts_tmp = (
                  db_session.query(Fact).filter(Fact.mean_and_body.in_(srch_trgt), Fact.is_hidden == False).order_by(Fact.id.desc()).all()
                  )
                  db_session.close()
                  is_srch_done = True
            else:
                  fcts_tmp = (
                  db_session.query(Fact).filter(Fact.mean_and_body.in_(srch_trgt)).order_by(Fact.id.desc()).all()
                  )
                  db_session.close()
                  is_srch_done = True
        if ((has_img != "") and (is_srch_done == False)):
            srch_trgt = [mn_n_bdy]
            if ((srt_cndtn == "condition-1") and (extrct_cndtn == "condition-1")):
                  fcts_tmp = (
                  db_session.query(Fact).filter(Fact.mean_and_body.in_(srch_trgt), Fact.is_hidden == False).order_by(Fact.id.asc()).all()
                  )
                  db_session.close()
                  is_srch_done = True
            elif ((srt_cndtn == "condition-1") and (extrct_cndtn == "condition-2")):
                  fcts_tmp = (
                  db_session.query(Fact).filter(Fact.mean_and_body.in_(srch_trgt)).order_by(Fact.id.asc()).all()
                  )
                  db_session.close()
                  is_srch_done = True
            elif ((srt_cndtn == "condition-2") and (extrct_cndtn == "condition-1")):
                  fcts_tmp = (
                  db_session.query(Fact).filter(Fact.mean_and_body.in_(srch_trgt), Fact.is_hidden == False).order_by(Fact.id.desc()).all()
                  )
                  db_session.close()
                  is_srch_done = True
            else:
                  fcts_tmp = (
                  db_session.query(Fact).filter(Fact.mean_and_body.in_(srch_trgt)).order_by(Fact.id.desc()).all()
                  )
                  db_session.close()
                  is_srch_done = True
        if ((has_snd != "") and (is_srch_done == False)):
            srch_trgt = [mn_n_bdy]
            if ((srt_cndtn == "condition-1") and (extrct_cndtn == "condition-1")):
                  fcts_tmp = (
                  db_session.query(Fact).filter(Fact.mean_and_body.in_(srch_trgt), Fact.is_hidden == False).order_by(Fact.id.asc()).all()
                  )
                  db_session.close()
                  is_srch_done = True
            elif ((srt_cndtn == "condition-1") and (extrct_cndtn == "condition-2")):
                  fcts_tmp = (
                  db_session.query(Fact).filter(Fact.mean_and_body.in_(srch_trgt)).order_by(Fact.id.asc()).all()
                  )
                  db_session.close()
                  is_srch_done = True
            elif ((srt_cndtn == "condition-2") and (extrct_cndtn == "condition-1")):
                  fcts_tmp = (
                  db_session.query(Fact).filter(Fact.mean_and_body.in_(srch_trgt), Fact.is_hidden == False).order_by(Fact.id.desc()).all()
                  )
                  db_session.close()
                  is_srch_done = True
            else:
                  fcts_tmp = (
                  db_session.query(Fact).filter(Fact.mean_and_body.in_(srch_trgt)).order_by(Fact.id.desc()).all()
                  )
                  db_session.close()
                  is_srch_done = True
        if ((has_vdo != "") and (is_srch_done == False)):
            srch_trgt = [mn_n_bdy]
            if ((srt_cndtn == "condition-1") and (extrct_cndtn == "condition-1")):
                  fcts_tmp = (
                  db_session.query(Fact).filter(Fact.mean_and_body.in_(srch_trgt), Fact.is_hidden == False).order_by(Fact.id.asc()).all()
                  )
                  db_session.close()
                  is_srch_done = True
            elif ((srt_cndtn == "condition-1") and (extrct_cndtn == "condition-2")):
                  fcts_tmp = (
                  db_session.query(Fact).filter(Fact.mean_and_body.in_(srch_trgt)).order_by(Fact.id.asc()).all()
                  )
                  db_session.close()
                  is_srch_done = True
            elif ((srt_cndtn == "condition-2") and (extrct_cndtn == "condition-1")):
                  fcts_tmp = (
                  db_session.query(Fact).filter(Fact.mean_and_body.in_(srch_trgt), Fact.is_hidden == False).order_by(Fact.id.desc()).all()
                  )
                  db_session.close()
                  is_srch_done = True
            else:
                  fcts_tmp = (
                  db_session.query(Fact).filter(Fact.mean_and_body.in_(srch_trgt)).order_by(Fact.id.desc()).all()
                  )
                  db_session.close()
                  is_srch_done = True
        if ((((len(stff_nm) == 1) and (stff_nm[0] == "")) == False) and (is_srch_done == False)):
            srch_trgt = stff_nm
            if ((srt_cndtn == "condition-1") and (extrct_cndtn == "condition-1")):
                  fcts_tmp = (
                  db_session.query(Fact).filter(Fact.staff_name.in_(srch_trgt), Fact.is_hidden == False).order_by(Fact.id.asc()).all()
                  )
                  db_session.close()
                  is_srch_done = True
            elif ((srt_cndtn == "condition-1") and (extrct_cndtn == "condition-2")):
                  fcts_tmp = (
                  db_session.query(Fact).filter(Fact.staff_name.in_(srch_trgt)).order_by(Fact.id.asc()).all()
                  )
                  db_session.close()
                  is_srch_done = True
            elif ((srt_cndtn == "condition-2") and (extrct_cndtn == "condition-1")):
                  fcts_tmp = (
                  db_session.query(Fact).filter(Fact.staff_name.in_(srch_trgt), Fact.is_hidden == False).order_by(Fact.id.desc()).all()
                  )
                  db_session.close()
                  is_srch_done = True
            else:
                  fcts_tmp = (
                  db_session.query(Fact).filter(Fact.staff_name.in_(srch_trgt)).order_by(Fact.id.desc()).all()
                  )
                  db_session.close()
                  is_srch_done = True
        if ((((len(stff_kn_nm) == 1) and (stff_kn_nm[0] == "")) == False) and (is_srch_done == False)):
            srch_trgt = stff_kn_nm
            if ((srt_cndtn == "condition-1") and (extrct_cndtn == "condition-1")):
                  fcts_tmp = (
                  db_session.query(Fact).filter(Fact.staff_kana_name.in_(srch_trgt), Fact.is_hidden == False).order_by(Fact.id.asc()).all()
                  )
                  db_session.close()
                  is_srch_done = True
            elif ((srt_cndtn == "condition-1") and (extrct_cndtn == "condition-2")):
                  fcts_tmp = (
                  db_session.query(Fact).filter(Fact.staff_kana_name.in_(srch_trgt)).order_by(Fact.id.asc()).all()
                  )
                  db_session.close()
                  is_srch_done = True
            elif ((srt_cndtn == "condition-2") and (extrct_cndtn == "condition-1")):
                  fcts_tmp = (
                  db_session.query(Fact).filter(Fact.staff_kana_name.in_(srch_trgt), Fact.is_hidden == False).order_by(Fact.id.desc()).all()
                  )
                  db_session.close()
                  is_srch_done = True
            else:
                  fcts_tmp = (
                  db_session.query(Fact).filter(Fact.staff_kana_name.in_(srch_trgt)).order_by(Fact.id.desc()).all()
                  )
                  db_session.close()
                  is_srch_done = True
        if (((crtd_at_bgn is not None) and (crtd_at_end is not None)) and (is_srch_done == False)):
            if ((srt_cndtn=="condition-1") and (extrct_cndtn=="condition-1")):
                  fcts_tmp = (
                  db_session.query(Fact).filter(Fact.created_at >= crtd_at_bgn, Fact.created_at <= crtd_at_end, Fact.is_hidden == False).order_by(Fact.id.asc()).all()
                  )
                  db_session.close()
                  is_srch_done = True
            elif ((srt_cndtn=="condition-1") and (extrct_cndtn=="condition-2")):
                  fcts_tmp = (
                  db_session.query(Fact).filter(Fact.created_at >= crtd_at_bgn, Fact.created_at <= crtd_at_end).order_by(Fact.id.asc()).all()
                  )
                  db_session.close()
                  is_srch_done = True
            elif ((srt_cndtn=="condition-2") and (extrct_cndtn=="condition-1")):
                  fcts_tmp = (
                  db_session.query(Fact).filter(Fact.created_at >= crtd_at_bgn, Fact.created_at <= crtd_at_end, Fact.is_hidden == False).order_by(Fact.id.desc()).all()
                  )
                  db_session.close()
                  is_srch_done = True
            else:
                  fcts_tmp = (
                  db_session.query(Fact).filter(Fact.created_at >= crtd_at_bgn, Fact.created_at <= crtd_at_end).order_by(Fact.id.desc()).all()
                  )
                  db_session.close()
                  is_srch_done = True
        if (((updtd_at_bgn is not None) and (updtd_at_end is not None)) and (is_srch_done == False)):
            if ((srt_cndtn=="condition-1") and (extrct_cndtn=="condition-1")):
                  fcts_tmp = (
                  db_session.query(Fact).filter(Fact.created_at >= updtd_at_bgn, Fact.created_at <= updtd_at_end, Fact.is_hidden == False).order_by(Fact.id.asc()).all()
                  )
                  db_session.close()
            elif ((srt_cndtn=="condition-1") and (extrct_cndtn=="condition-2")):
                  fcts_tmp = (
                  db_session.query(Fact).filter(Fact.created_at >= updtd_at_bgn, Fact.created_at <= updtd_at_end).order_by(Fact.id.asc()).all()
                  )
                  db_session.close()
            elif ((srt_cndtn=="condition-2") and (extrct_cndtn=="condition-1")):
                  fcts_tmp = (
                  db_session.query(Fact).filter(Fact.created_at >= updtd_at_bgn, Fact.created_at <= updtd_at_end, Fact.is_hidden == False).order_by(Fact.id.desc()).all()
                  )
                  db_session.close()
            else:
                  fcts_tmp = (
                  db_session.query(Fact).filter(Fact.created_at >= updtd_at_bgn, Fact.created_at <= updtd_at_end).order_by(Fact.id.desc()).all()
                  )
                  db_session.close()

        # 検索結果を整形し, 配列にセットしてテンプレートと共に返す.
        if fcts_tmp is not None:
            for fct_tmp in fcts_tmp:
                if len(str(fct_tmp.id)) > 6:
                    id_tmp = fct_tmp.id[0:6] + "..."
                else:
                    id_tmp = fct_tmp.id
                if len(fct_tmp.spell_and_header) > 6:
                    spll_n_hdr_tmp = fct_tmp.spell_and_header[0:6] + "..."
                else:
                    spll_n_hdr_tmp = fct_tmp.spell_and_header
                if len(fct_tmp.mean_and_body) > 6:
                    mn_n_bdy_tmp = fct_tmp.mean_and_body[0:6] + "..."
                else:
                    mn_n_bdy_tmp = fct_tmp.mean_and_body
                if len(fct_tmp.staff_name) > 6:
                    stff_nm_tmp = fct_tmp.staff_name[0:6] + "..."
                else:
                    stff_nm_tmp = fct_tmp.staff_name
                fcts_fnl.append([id_tmp,
                                 spll_n_hdr_tmp,
                                 mn_n_bdy_tmp,
                                 stff_nm_tmp
                                ])
        per_pg = consts.KNOWLEDGE_ITEM_PER_PAGE
        pg = request.args.get(get_page_parameter(), type=int, default=1)
        pg_dat = fcts_fnl[(pg - 1) * per_pg : pg * per_pg]
        pgntn = Pagination(page=pg,
                           total=len(fcts_fnl),
                           per_page=per_pg,
                           css_framework=consts.PAGINATION_CSS
                          )
        return render_template("search_knowledges_results.html", page_data=pg_dat, pagination=pgntn)

    if request.method == "POST":
        # 直前に, GETメソッドで該当ページを取得しているかを調べる.
        # 取得していなければ, 強制的に現在ページへリダイレクトする.
        if session["referrer-page"] != "view.search_knowledges_results":
            return redirect(url_for("view.search_knowledges_results"))

        # フォームボタン群の中から, 押下されたボタンに応じたページへリダイレクトする.
        if request.form["hidden-modify-item-id"] != "":
            session["hidden-modify-item-id"] = request.form["hidden-modify-item-id"]
            return redirect(url_for("view.modify_fact"))
        if request.form["hidden-detail-item-id"] != "":
            session["hidden-detail-item-id"] = request.form["hidden-detail-item-id"]
            return redirect(url_for("view.detail_fact"))

        # フォームが改竄されているので, その旨を通知するために例外を発生させる.
        raise BadRequest


# 「search_rules_results」のためのビュー関数(=URLエンドポイント)を宣言・定義する.
@view.route("/search_rules_results", methods=["GET", "POST"])
def search_rules_results():
    # 関数内で使用する変数・オブジェクトを宣言・定義する.
    rls_tmp = []
    rls_fnl = []
    is_srch_done = False

    # 該当のURLエンドポイントに入ったことをロギングする.
    rslt = cr_engn.etc.logging__info("view at /search_rules_results")

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

        # 検索条件(=検索キー)となる値をまとめて取得する.
        id = str(session["id"]).split(" ")
        spll_n_hdr = str(session["spell-and-header"])
        mn_n_bdy = str(session["mean-and-body"])
        ctgr_tgs = str(session["category-tags"]).split(" ")
        infrnc_n_spcltn_cndtn = str(session["inference-and-speculation-condition"])
        infrnc_n_spcltn_rslt = str(session["inference-and-speculation-result"])
        stff_nm = str(session["staff-name"]).split(" ")
        stff_kn_nm = str(session["staff-kana-name"]).split(" ")
        crtd_at_bgn = session["created-at-begin"]
        crtd_at_end = session["created-at-end"]
        updtd_at_bgn = session["updated-at-begin"]
        updtd_at_end = session["updated-at-end"]
        srt_cndtn = str(session["sort-condition"])
        extrct_cndtn = str(session["extract-condition"])

        # 各種の検索条件に基づいてレコードを検索する.
        if (((len(id) == 1) and (id[0] == "")) == False):
            srch_trgt = id
            if ((srt_cndtn == "condition-1") and (extrct_cndtn == "condition-1")):
                  rls_tmp = (
                  db_session.query(Rule).filter(Rule.id.in_(srch_trgt), Rule.is_hidden == False).order_by(Rule.id.asc()).all()
                  )
                  db_session.close()
                  is_srch_done = True
            elif ((srt_cndtn == "condition-1") and (extrct_cndtn == "condition-2")):
                  rls_tmp = (
                  db_session.query(Rule).filter(Rule.id.in_(srch_trgt)).order_by(Rule.id.asc()).all()
                  )
                  db_session.close()
                  is_srch_done = True
            elif ((srt_cndtn == "condition-2") and (extrct_cndtn == "condition-1")):
                  rls_tmp = (
                  db_session.query(Rule).filter(Rule.id.in_(srch_trgt), Rule.is_hidden == False).order_by(Rule.id.desc()).all()
                  )
                  db_session.close()
                  is_srch_done = True
            else:
                  rls_tmp = (
                  db_session.query(Rule).filter(Rule.id.in_(srch_trgt)).order_by(Rule.id.desc()).all()
                  )
                  db_session.close()
                  is_srch_done = True
        if ((spll_n_hdr != "") and (is_srch_done == False)):
            srch_trgt = [spll_n_hdr]
            if ((srt_cndtn == "condition-1") and (extrct_cndtn == "condition-1")):
                  rls_tmp = (
                  db_session.query(Rule).filter(Rule.spell_and_header.in_(srch_trgt), Rule.is_hidden == False).order_by(Rule.id.asc()).all()
                  )
                  db_session.close()
                  is_srch_done = True
            elif ((srt_cndtn == "condition-1") and (extrct_cndtn == "condition-2")):
                  rls_tmp = (
                  db_session.query(Rule).filter(Rule.spell_and_header.in_(srch_trgt)).order_by(Rule.id.asc()).all()
                  )
                  db_session.close()
                  is_srch_done = True
            elif ((srt_cndtn == "condition-2") and (extrct_cndtn == "condition-1")):
                  rls_tmp = (
                  db_session.query(Rule).filter(Rule.spell_and_header.in_(srch_trgt), Rule.is_hidden == False).order_by(Rule.id.desc()).all()
                  )
                  db_session.close()
                  is_srch_done = True
            else:
                  rls_tmp = (
                  db_session.query(Rule).filter(Rule.spell_and_header.in_(srch_trgt)).order_by(Rule.id.desc()).all()
                  )
                  db_session.close()
                  is_srch_done = True
        if ((mn_n_bdy != "") and (is_srch_done == False)):
            srch_trgt = [mn_n_bdy]
            if ((srt_cndtn == "condition-1") and (extrct_cndtn == "condition-1")):
                  rls_tmp = (
                  db_session.query(Rule).filter(Rule.mean_and_body.in_(srch_trgt), Rule.is_hidden == False).order_by(Rule.id.asc()).all()
                  )
                  db_session.close()
                  is_srch_done = True
            elif ((srt_cndtn == "condition-1") and (extrct_cndtn == "condition-2")):
                  rls_tmp = (
                  db_session.query(Rule).filter(Rule.mean_and_body.in_(srch_trgt)).order_by(Rule.id.asc()).all()
                  )
                  db_session.close()
                  is_srch_done = True
            elif ((srt_cndtn == "condition-2") and (extrct_cndtn == "condition-1")):
                  rls_tmp = (
                  db_session.query(Rule).filter(Rule.mean_and_body.in_(srch_trgt), Rule.is_hidden == False).order_by(Rule.id.desc()).all()
                  )
                  db_session.close()
                  is_srch_done = True
            else:
                  rls_tmp = (
                  db_session.query(Rule).filter(Rule.mean_and_body.in_(srch_trgt)).order_by(Rule.id.desc()).all()
                  )
                  db_session.close()
                  is_srch_done = True
        if (((len(ctgr_tgs) == 1) and (ctgr_tgs[0] == "")) == False):
            srch_trgt = ctgr_tgs
            if ((srt_cndtn == "condition-1") and (extrct_cndtn == "condition-1")):
                  rls_tmp = (
                  db_session.query(Rule).filter(Rule.mean_and_body.in_(srch_trgt), Rule.is_hidden == False).order_by(Rule.id.asc()).all()
                  )
                  db_session.close()
                  is_srch_done = True
            elif ((srt_cndtn == "condition-1") and (extrct_cndtn == "condition-2")):
                  rls_tmp = (
                  db_session.query(Rule).filter(Rule.mean_and_body.in_(srch_trgt)).order_by(Rule.id.asc()).all()
                  )
                  db_session.close()
                  is_srch_done = True
            elif ((srt_cndtn == "condition-2") and (extrct_cndtn == "condition-1")):
                  rls_tmp = (
                  db_session.query(Rule).filter(Rule.mean_and_body.in_(srch_trgt), Rule.is_hidden == False).order_by(Rule.id.desc()).all()
                  )
                  db_session.close()
                  is_srch_done = True
            else:
                  rls_tmp = (
                  db_session.query(Rule).filter(Rule.mean_and_body.in_(srch_trgt)).order_by(Rule.id.desc()).all()
                  )
                  db_session.close()
                  is_srch_done = True
        if ((infrnc_n_spcltn_cndtn != "") and (is_srch_done == False)):
            srch_trgt = [infrnc_n_spcltn_cndtn]
            if ((srt_cndtn == "condition-1") and (extrct_cndtn == "condition-1")):
                  rls_tmp = (
                  db_session.query(Rule).filter(Rule.mean_and_body.in_(srch_trgt), Rule.is_hidden == False).order_by(Rule.id.asc()).all()
                  )
                  db_session.close()
                  is_srch_done = True
            elif ((srt_cndtn == "condition-1") and (extrct_cndtn == "condition-2")):
                  rls_tmp = (
                  db_session.query(Rule).filter(Rule.mean_and_body.in_(srch_trgt)).order_by(Rule.id.asc()).all()
                  )
                  db_session.close()
                  is_srch_done = True
            elif ((srt_cndtn == "condition-2") and (extrct_cndtn == "condition-1")):
                  rls_tmp = (
                  db_session.query(Rule).filter(Rule.mean_and_body.in_(srch_trgt), Rule.is_hidden == False).order_by(Rule.id.desc()).all()
                  )
                  db_session.close()
                  is_srch_done = True
            else:
                  rls_tmp = (
                  db_session.query(Rule).filter(Rule.mean_and_body.in_(srch_trgt)).order_by(Rule.id.desc()).all()
                  )
                  db_session.close()
                  is_srch_done = True
        if ((infrnc_n_spcltn_rslt != "") and (is_srch_done == False)):
            srch_trgt = [infrnc_n_spcltn_rslt]
            if ((srt_cndtn == "condition-1") and (extrct_cndtn == "condition-1")):
                  rls_tmp = (
                  db_session.query(Rule).filter(Rule.mean_and_body.in_(srch_trgt), Rule.is_hidden == False).order_by(Rule.id.asc()).all()
                  )
                  db_session.close()
                  is_srch_done = True
            elif ((srt_cndtn == "condition-1") and (extrct_cndtn == "condition-2")):
                  rls_tmp = (
                  db_session.query(Rule).filter(Rule.mean_and_body.in_(srch_trgt)).order_by(Rule.id.asc()).all()
                  )
                  db_session.close()
                  is_srch_done = True
            elif ((srt_cndtn == "condition-2") and (extrct_cndtn == "condition-1")):
                  rls_tmp = (
                  db_session.query(Rule).filter(Rule.mean_and_body.in_(srch_trgt), Rule.is_hidden == False).order_by(Rule.id.desc()).all()
                  )
                  db_session.close()
                  is_srch_done = True
            else:
                  rls_tmp = (
                  db_session.query(Rule).filter(Rule.mean_and_body.in_(srch_trgt)).order_by(Rule.id.desc()).all()
                  )
                  db_session.close()
                  is_srch_done = True
        if ((((len(stff_nm) == 1) and (stff_nm[0] == "")) == False) and (is_srch_done == False)):
            srch_trgt = stff_nm
            if ((srt_cndtn == "condition-1") and (extrct_cndtn == "condition-1")):
                  rls_tmp = (
                  db_session.query(Rule).filter(Rule.staff_name.in_(srch_trgt), Rule.is_hidden == False).order_by(Rule.id.asc()).all()
                  )
                  db_session.close()
                  is_srch_done = True
            elif ((srt_cndtn == "condition-1") and (extrct_cndtn == "condition-2")):
                  rls_tmp = (
                  db_session.query(Rule).filter(Rule.staff_name.in_(srch_trgt)).order_by(Rule.id.asc()).all()
                  )
                  db_session.close()
                  is_srch_done = True
            elif ((srt_cndtn == "condition-2") and (extrct_cndtn == "condition-1")):
                  rls_tmp = (
                  db_session.query(Rule).filter(Rule.staff_name.in_(srch_trgt), Rule.is_hidden == False).order_by(Rule.id.desc()).all()
                  )
                  db_session.close()
                  is_srch_done = True
            else:
                  rls_tmp = (
                  db_session.query(Rule).filter(Rule.staff_name.in_(srch_trgt)).order_by(Rule.id.desc()).all()
                  )
                  db_session.close()
                  is_srch_done = True
        if ((((len(stff_kn_nm) == 1) and (stff_kn_nm[0] == "")) == False) and (is_srch_done == False)):
            srch_trgt = stff_kn_nm
            if ((srt_cndtn == "condition-1") and (extrct_cndtn == "condition-1")):
                  rls_tmp = (
                  db_session.query(Rule).filter(Rule.staff_kana_name.in_(srch_trgt), Rule.is_hidden == False).order_by(Rule.id.asc()).all()
                  )
                  db_session.close()
                  is_srch_done = True
            elif ((srt_cndtn == "condition-1") and (extrct_cndtn == "condition-2")):
                  rls_tmp = (
                  db_session.query(Rule).filter(Rule.staff_kana_name.in_(srch_trgt)).order_by(Rule.id.asc()).all()
                  )
                  db_session.close()
                  is_srch_done = True
            elif ((srt_cndtn == "condition-2") and (extrct_cndtn == "condition-1")):
                  rls_tmp = (
                  db_session.query(Rule).filter(Rule.staff_kana_name.in_(srch_trgt), Rule.is_hidden == False).order_by(Rule.id.desc()).all()
                  )
                  db_session.close()
                  is_srch_done = True
            else:
                  rls_tmp = (
                  db_session.query(Rule).filter(Rule.staff_kana_name.in_(srch_trgt)).order_by(Rule.id.desc()).all()
                  )
                  db_session.close()
                  is_srch_done = True
        if (((crtd_at_bgn is not None) and (crtd_at_end is not None)) and (is_srch_done == False)):
            if ((srt_cndtn=="condition-1") and (extrct_cndtn=="condition-1")):
                  rls_tmp = (
                  db_session.query(Rule).filter(Rule.created_at >= crtd_at_bgn, Rule.created_at <= crtd_at_end, Rule.is_hidden == False).order_by(Rule.id.asc()).all()
                  )
                  db_session.close()
                  is_srch_done = True
            elif ((srt_cndtn=="condition-1") and (extrct_cndtn=="condition-2")):
                  rls_tmp = (
                  db_session.query(Rule).filter(Rule.created_at >= crtd_at_bgn, Rule.created_at <= crtd_at_end).order_by(Rule.id.asc()).all()
                  )
                  db_session.close()
                  is_srch_done = True
            elif ((srt_cndtn=="condition-2") and (extrct_cndtn=="condition-1")):
                  rls_tmp = (
                  db_session.query(Rule).filter(Rule.created_at >= crtd_at_bgn, Rule.created_at <= crtd_at_end, Rule.is_hidden == False).order_by(Rule.id.desc()).all()
                  )
                  db_session.close()
                  is_srch_done = True
            else:
                  rls_tmp = (
                  db_session.query(Rule).filter(Rule.created_at >= crtd_at_bgn, Rule.created_at <= crtd_at_end).order_by(Rule.id.desc()).all()
                  )
                  db_session.close()
                  is_srch_done = True
        if (((updtd_at_bgn is not None) and (updtd_at_end is not None)) and (is_srch_done == False)):
            if ((srt_cndtn=="condition-1") and (extrct_cndtn=="condition-1")):
                  rls_tmp = (
                  db_session.query(Rule).filter(Rule.created_at >= updtd_at_bgn, Rule.created_at <= updtd_at_end, Rule.is_hidden == False).order_by(Rule.id.asc()).all()
                  )
                  db_session.close()
            elif ((srt_cndtn=="condition-1") and (extrct_cndtn=="condition-2")):
                  rls_tmp = (
                  db_session.query(Rule).filter(Rule.created_at >= updtd_at_bgn, Rule.created_at <= updtd_at_end).order_by(Rule.id.asc()).all()
                  )
                  db_session.close()
            elif ((srt_cndtn=="condition-2") and (extrct_cndtn=="condition-1")):
                  wrls_tmp = (
                  db_session.query(Rule).filter(Rule.created_at >= updtd_at_bgn, Rule.created_at <= updtd_at_end, Rule.is_hidden == False).order_by(Rule.id.desc()).all()
                  )
                  db_session.close()
            else:
                  rls_tmp = (
                  db_session.query(Rule).filter(Rule.created_at >= updtd_at_bgn, Rule.created_at <= updtd_at_end).order_by(Rule.id.desc()).all()
                  )
                  db_session.close()

        # 検索結果を整形し, 配列にセットしてテンプレートと共に返す.
        if rls_tmp is not None:
            for rl_tmp in rls_tmp:
                if len(str(rl_tmp.id)) > 6:
                    id_tmp = rl_tmp.id[0:6] + "..."
                else:
                    id_tmp = rl_tmp.id
                if len(rl_tmp.spell_and_header) > 6:
                    spll_n_hdr_tmp = rl_tmp.spell_and_header[0:6] + "..."
                else:
                    spll_n_hdr_tmp = rl_tmp.spell_and_header
                if len(rl_tmp.mean_and_body) > 6:
                    mn_n_bdy_tmp = rl_tmp.mean_and_body[0:6] + "..."
                else:
                    mn_n_bdy_tmp = rl_tmp.mean_and_body
                if len(rl_tmp.staff_name) > 6:
                    stff_nm_tmp = rl_tmp.staff_name[0:6] + "..."
                else:
                    stff_nm_tmp = rl_tmp.staff_name
                rls_fnl.append([id_tmp,
                                 spll_n_hdr_tmp,
                                 mn_n_bdy_tmp,
                                 stff_nm_tmp
                                ])
        per_pg = consts.RULE_ITEM_PER_PAGE
        pg = request.args.get(get_page_parameter(), type=int, default=1)
        pg_dat = rls_fnl[(pg - 1) * per_pg : pg * per_pg]
        pgntn = Pagination(page=pg,
                           total=len(rls_fnl),
                           per_page=per_pg,
                           css_framework=consts.PAGINATION_CSS
                          )
        return render_template("search_rules_results.html", page_data=pg_dat, pagination=pgntn)

    if request.method == "POST":
        # 直前に, GETメソッドで該当ページを取得しているかを調べる.
        # 取得していなければ, 強制的に現在ページへリダイレクトする.
        if session["referrer-page"] != "view.search_rules_results":
            return redirect(url_for("view.search_rules_results"))

        # フォームボタン群の中から, 押下されたボタンに応じたページへリダイレクトする.
        if request.form["hidden-modify-item-id"] != "":
            session["hidden-modify-item-id"] = request.form["hidden-modify-item-id"]
            return redirect(url_for("view.modify_rule"))
        if request.form["hidden-detail-item-id"] != "":
            session["hidden-detail-item-id"] = request.form["hidden-detail-item-id"]
            return redirect(url_for("view.detail_rule"))

        # フォームが改竄されているので, その旨を通知するために例外を発生させる.
        raise BadRequest


# 「search_reactions_results」のためのビュー関数(=URLエンドポイント)を宣言・定義する.
@view.route("/search_reactions_results", methods=["GET", "POST"])
def search_reactions_results():
    # 関数内で使用する変数・オブジェクトを宣言・定義する.
    rctns_tmp = []
    rctns_fnl = []
    is_srch_done = False

    # 該当のURLエンドポイントに入ったことをロギングする.
    rslt = cr_engn.etc.logging__info("view at /search_reactions_results")

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

        # 検索条件(=検索キー)となる値をまとめて取得する.
        id = str(session["id"]).split(" ")
        spll_n_hdr = str(session["spell-and-header"])
        mn_n_bdy = str(session["mean-and-body"])
        stff_psych = str(session["staff-psychology"])
        scn_n_bck = str(session["scene-and-background"])
        msg_exmpl_frm_stff = str(session["message-example-from-staff"])
        msg_exmpl_frm_app = str(session["message-example-from-application"])
        stff_nm = str(session["staff-name"]).split(" ")
        stff_kn_nm = str(session["staff-kana-name"]).split(" ")
        crtd_at_bgn = session["created-at-begin"]
        crtd_at_end = session["created-at-end"]
        updtd_at_bgn = session["updated-at-begin"]
        updtd_at_end = session["updated-at-end"]
        srt_cndtn = str(session["sort-condition"])
        extrct_cndtn = str(session["extract-condition"])

        # 各種の検索条件に基づいてレコードを検索する.
        if (((len(id) == 1) and (id[0] == "")) == False):
            srch_trgt = id
            if ((srt_cndtn == "condition-1") and (extrct_cndtn == "condition-1")):
                  rctns_tmp = (
                  db_session.query(Reaction).filter(Reaction.id.in_(srch_trgt), Reaction.is_hidden == False).order_by(Reaction.id.asc()).all()
                  )
                  db_session.close()
                  is_srch_done = True
            elif ((srt_cndtn == "condition-1") and (extrct_cndtn == "condition-2")):
                  rctns_tmp = (
                  db_session.query(Reaction).filter(Reaction.id.in_(srch_trgt)).order_by(Reaction.id.asc()).all()
                  )
                  db_session.close()
                  is_srch_done = True
            elif ((srt_cndtn == "condition-2") and (extrct_cndtn == "condition-1")):
                  rctns_tmp = (
                  db_session.query(Reaction).filter(Reaction.id.in_(srch_trgt), Reaction.is_hidden == False).order_by(Reaction.id.desc()).all()
                  )
                  db_session.close()
                  is_srch_done = True
            else:
                  rctns_tmp = (
                  db_session.query(Reaction).filter(Reaction.id.in_(srch_trgt)).order_by(Reaction.id.desc()).all()
                  )
                  db_session.close()
                  is_srch_done = True
        if ((spll_n_hdr != "") and (is_srch_done == False)):
            srch_trgt = [spll_n_hdr]
            if ((srt_cndtn == "condition-1") and (extrct_cndtn == "condition-1")):
                  rctns_tmp = (
                  db_session.query(Reaction).filter(Reaction.spell_and_header.in_(srch_trgt), Reaction.is_hidden == False).order_by(Reaction.id.asc()).all()
                  )
                  db_session.close()
                  is_srch_done = True
            elif ((srt_cndtn == "condition-1") and (extrct_cndtn == "condition-2")):
                  rctns_tmp = (
                  db_session.query(Reaction).filter(Reaction.spell_and_header.in_(srch_trgt)).order_by(Reaction.id.asc()).all()
                  )
                  db_session.close()
                  is_srch_done = True
            elif ((srt_cndtn == "condition-2") and (extrct_cndtn == "condition-1")):
                  rctns_tmp = (
                  db_session.query(Reaction).filter(Reaction.spell_and_header.in_(srch_trgt), Reaction.is_hidden == False).order_by(Reaction.id.desc()).all()
                  )
                  db_session.close()
                  is_srch_done = True
            else:
                  rctns_tmp = (
                  db_session.query(Reaction).filter(Reaction.spell_and_header.in_(srch_trgt)).order_by(Reaction.id.desc()).all()
                  )
                  db_session.close()
                  is_srch_done = True
        if ((mn_n_bdy != "") and (is_srch_done == False)):
            srch_trgt = [mn_n_bdy]
            if ((srt_cndtn == "condition-1") and (extrct_cndtn == "condition-1")):
                  rctns_tmp = (
                  db_session.query(Reaction).filter(Reaction.mean_and_body.in_(srch_trgt), Reaction.is_hidden == False).order_by(Reaction.id.asc()).all()
                  )
                  db_session.close()
                  is_srch_done = True
            elif ((srt_cndtn == "condition-1") and (extrct_cndtn == "condition-2")):
                  rctns_tmp = (
                  db_session.query(Reaction).filter(Reaction.mean_and_body.in_(srch_trgt)).order_by(Reaction.id.asc()).all()
                  )
                  db_session.close()
                  is_srch_done = True
            elif ((srt_cndtn == "condition-2") and (extrct_cndtn == "condition-1")):
                  rctns_tmp = (
                  db_session.query(Reaction).filter(Reaction.mean_and_body.in_(srch_trgt), Reaction.is_hidden == False).order_by(Reaction.id.desc()).all()
                  )
                  db_session.close()
                  is_srch_done = True
            else:
                  rctns_tmp = (
                  db_session.query(Reaction).filter(Reaction.mean_and_body.in_(srch_trgt)).order_by(Reaction.id.desc()).all()
                  )
                  db_session.close()
                  is_srch_done = True
        if ((stff_psych != "") and (is_srch_done == False)):
            srch_trgt = [stff_psych]
            if ((srt_cndtn == "condition-1") and (extrct_cndtn == "condition-1")):
                  rctns_tmp = (
                  db_session.query(Reaction).filter(Reaction.mean_and_body.in_(srch_trgt), Reaction.is_hidden == False).order_by(Reaction.id.asc()).all()
                  )
                  db_session.close()
                  is_srch_done = True
            elif ((srt_cndtn == "condition-1") and (extrct_cndtn == "condition-2")):
                  rctns_tmp = (
                  db_session.query(Reaction).filter(Reaction.mean_and_body.in_(srch_trgt)).order_by(Reaction.id.asc()).all()
                  )
                  db_session.close()
                  is_srch_done = True
            elif ((srt_cndtn == "condition-2") and (extrct_cndtn == "condition-1")):
                  rctns_tmp = (
                  db_session.query(Reaction).filter(Reaction.mean_and_body.in_(srch_trgt), Reaction.is_hidden == False).order_by(Reaction.id.desc()).all()
                  )
                  db_session.close()
                  is_srch_done = True
            else:
                  rctns_tmp = (
                  db_session.query(Reaction).filter(Reaction.mean_and_body.in_(srch_trgt)).order_by(Reaction.id.desc()).all()
                  )
                  db_session.close()
                  is_srch_done = True
        if ((scn_n_bck != "") and (is_srch_done == False)):
            srch_trgt = [scn_n_bck]
            if ((srt_cndtn == "condition-1") and (extrct_cndtn == "condition-1")):
                  rctns_tmp = (
                  db_session.query(Reaction).filter(Reaction.mean_and_body.in_(srch_trgt), Reaction.is_hidden == False).order_by(Reaction.id.asc()).all()
                  )
                  db_session.close()
                  is_srch_done = True
            elif ((srt_cndtn == "condition-1") and (extrct_cndtn == "condition-2")):
                  rctns_tmp = (
                  db_session.query(Reaction).filter(Reaction.mean_and_body.in_(srch_trgt)).order_by(Reaction.id.asc()).all()
                  )
                  db_session.close()
                  is_srch_done = True
            elif ((srt_cndtn == "condition-2") and (extrct_cndtn == "condition-1")):
                  rctns_tmp = (
                  db_session.query(Reaction).filter(Reaction.mean_and_body.in_(srch_trgt), Reaction.is_hidden == False).order_by(Reaction.id.desc()).all()
                  )
                  db_session.close()
                  is_srch_done = True
            else:
                  rctns_tmp = (
                  db_session.query(Reaction).filter(Reaction.mean_and_body.in_(srch_trgt)).order_by(Reaction.id.desc()).all()
                  )
                  db_session.close()
                  is_srch_done = True
        if ((msg_exmpl_frm_stff != "") and (is_srch_done == False)):
            srch_trgt = [msg_exmpl_frm_stff]
            if ((srt_cndtn == "condition-1") and (extrct_cndtn == "condition-1")):
                  rctns_tmp = (
                  db_session.query(Reaction).filter(Reaction.mean_and_body.in_(srch_trgt), Reaction.is_hidden == False).order_by(Reaction.id.asc()).all()
                  )
                  db_session.close()
                  is_srch_done = True
            elif ((srt_cndtn == "condition-1") and (extrct_cndtn == "condition-2")):
                  rctns_tmp = (
                  db_session.query(Reaction).filter(Reaction.mean_and_body.in_(srch_trgt)).order_by(Reaction.id.asc()).all()
                  )
                  db_session.close()
                  is_srch_done = True
            elif ((srt_cndtn == "condition-2") and (extrct_cndtn == "condition-1")):
                  rctns_tmp = (
                  db_session.query(Reaction).filter(Reaction.mean_and_body.in_(srch_trgt), Reaction.is_hidden == False).order_by(Reaction.id.desc()).all()
                  )
                  db_session.close()
                  is_srch_done = True
            else:
                  wrds_tmp = (
                  db_session.query(Reaction).filter(Reaction.mean_and_body.in_(srch_trgt)).order_by(Reaction.id.desc()).all()
                  )
                  db_session.close()
                  is_srch_done = True
        if ((msg_exmpl_frm_app != "") and (is_srch_done == False)):
            srch_trgt = [msg_exmpl_frm_app]
            if ((srt_cndtn == "condition-1") and (extrct_cndtn == "condition-1")):
                  rctns_tmp = (
                  db_session.query(Reaction).filter(Reaction.mean_and_body.in_(srch_trgt), Reaction.is_hidden == False).order_by(Reaction.id.asc()).all()
                  )
                  db_session.close()
                  is_srch_done = True
            elif ((srt_cndtn == "condition-1") and (extrct_cndtn == "condition-2")):
                  rctns_tmp = (
                  db_session.query(Reaction).filter(Reaction.mean_and_body.in_(srch_trgt)).order_by(Reaction.id.asc()).all()
                  )
                  db_session.close()
                  is_srch_done = True
            elif ((srt_cndtn == "condition-2") and (extrct_cndtn == "condition-1")):
                  rctns_tmp = (
                  db_session.query(Reaction).filter(Reaction.mean_and_body.in_(srch_trgt), Reaction.is_hidden == False).order_by(Reaction.id.desc()).all()
                  )
                  db_session.close()
                  is_srch_done = True
            else:
                  rctns_tmp = (
                  db_session.query(Reaction).filter(Reaction.mean_and_body.in_(srch_trgt)).order_by(Reaction.id.desc()).all()
                  )
                  db_session.close()
                  is_srch_done = True
        if ((((len(stff_nm) == 1) and (stff_nm[0] == "")) == False) and (is_srch_done == False)):
            srch_trgt = stff_nm
            if ((srt_cndtn == "condition-1") and (extrct_cndtn == "condition-1")):
                  rctns_tmp = (
                  db_session.query(Reaction).filter(Reaction.staff_name.in_(srch_trgt), Reaction.is_hidden == False).order_by(Reaction.id.asc()).all()
                  )
                  db_session.close()
                  is_srch_done = True
            elif ((srt_cndtn == "condition-1") and (extrct_cndtn == "condition-2")):
                  rctns_tmp = (
                  db_session.query(Reaction).filter(Reaction.staff_name.in_(srch_trgt)).order_by(Reaction.id.asc()).all()
                  )
                  db_session.close()
                  is_srch_done = True
            elif ((srt_cndtn == "condition-2") and (extrct_cndtn == "condition-1")):
                  rctns_tmp = (
                  db_session.query(Reaction).filter(Reaction.staff_name.in_(srch_trgt), Reaction.is_hidden == False).order_by(Reaction.id.desc()).all()
                  )
                  db_session.close()
                  is_srch_done = True
            else:
                  rctns_tmp = (
                  db_session.query(Reaction).filter(Reaction.staff_name.in_(srch_trgt)).order_by(Reaction.id.desc()).all()
                  )
                  db_session.close()
                  is_srch_done = True
        if ((((len(stff_kn_nm) == 1) and (stff_kn_nm[0] == "")) == False) and (is_srch_done == False)):
            srch_trgt = stff_kn_nm
            if ((srt_cndtn == "condition-1") and (extrct_cndtn == "condition-1")):
                  rctns_tmp = (
                  db_session.query(Reaction).filter(Reaction.staff_kana_name.in_(srch_trgt), Reaction.is_hidden == False).order_by(Reaction.id.asc()).all()
                  )
                  db_session.close()
                  is_srch_done = True
            elif ((srt_cndtn == "condition-1") and (extrct_cndtn == "condition-2")):
                  rctns_tmp = (
                  db_session.query(Reaction).filter(Reaction.staff_kana_name.in_(srch_trgt)).order_by(Reaction.id.asc()).all()
                  )
                  db_session.close()
                  is_srch_done = True
            elif ((srt_cndtn == "condition-2") and (extrct_cndtn == "condition-1")):
                  rctns_tmp = (
                  db_session.query(Reaction).filter(Reaction.staff_kana_name.in_(srch_trgt), Reaction.is_hidden == False).order_by(Reaction.id.desc()).all()
                  )
                  db_session.close()
                  is_srch_done = True
            else:
                  rctns_tmp = (
                  db_session.query(Reaction).filter(Reaction.staff_kana_name.in_(srch_trgt)).order_by(Reaction.id.desc()).all()
                  )
                  db_session.close()
                  is_srch_done = True
        if (((crtd_at_bgn is not None) and (crtd_at_end is not None)) and (is_srch_done == False)):
            if ((srt_cndtn=="condition-1") and (extrct_cndtn=="condition-1")):
                  rctns_tmp = (
                  db_session.query(Reaction).filter(Reaction.created_at >= crtd_at_bgn, Reaction.created_at <= crtd_at_end, Reaction.is_hidden == False).order_by(Reaction.id.asc()).all()
                  )
                  db_session.close()
                  is_srch_done = True
            elif ((srt_cndtn=="condition-1") and (extrct_cndtn=="condition-2")):
                  rctns_tmp = (
                  db_session.query(Reaction).filter(Reaction.created_at >= crtd_at_bgn, Reaction.created_at <= crtd_at_end).order_by(Reaction.id.asc()).all()
                  )
                  db_session.close()
                  is_srch_done = True
            elif ((srt_cndtn=="condition-2") and (extrct_cndtn=="condition-1")):
                  rctns_tmp = (
                  db_session.query(Reaction).filter(Reaction.created_at >= crtd_at_bgn, Reaction.created_at <= crtd_at_end, Reaction.is_hidden == False).order_by(Reaction.id.desc()).all()
                  )
                  db_session.close()
                  is_srch_done = True
            else:
                  rctns_tmp = (
                  db_session.query(Reaction).filter(Reaction.created_at >= crtd_at_bgn, Reaction.created_at <= crtd_at_end).order_by(Reaction.id.desc()).all()
                  )
                  db_session.close()
                  is_srch_done = True
        if (((updtd_at_bgn is not None) and (updtd_at_end is not None)) and (is_srch_done == False)):
            if ((srt_cndtn=="condition-1") and (extrct_cndtn=="condition-1")):
                  rctns_tmp = (
                  db_session.query(Reaction).filter(Reaction.created_at >= updtd_at_bgn, Reaction.created_at <= updtd_at_end, Reaction.is_hidden == False).order_by(Reaction.id.asc()).all()
                  )
                  db_session.close()
            elif ((srt_cndtn=="condition-1") and (extrct_cndtn=="condition-2")):
                  rctns_tmp = (
                  db_session.query(Reaction).filter(Reaction.created_at >= updtd_at_bgn, Reaction.created_at <= updtd_at_end).order_by(Reaction.id.asc()).all()
                  )
                  db_session.close()
            elif ((srt_cndtn=="condition-2") and (extrct_cndtn=="condition-1")):
                  rctns_tmp = (
                  db_session.query(Reaction).filter(Reaction.created_at >= updtd_at_bgn, Reaction.created_at <= updtd_at_end, Reaction.is_hidden == False).order_by(Reaction.id.desc()).all()
                  )
                  db_session.close()
            else:
                  rctns_tmp = (
                  db_session.query(Reaction).filter(Reaction.created_at >= updtd_at_bgn, Reaction.created_at <= updtd_at_end).order_by(Reaction.id.desc()).all()
                  )
                  db_session.close()

        # 検索結果を整形し, 配列にセットしてテンプレートと共に返す.
        if rctns_tmp is not None:
            for rctn_tmp in rctns_tmp:
                if len(str(rctn_tmp.id)) > 6:
                    id_tmp = rctn_tmp.id[0:6] + "..."
                else:
                    id_tmp = rctn_tmp.id
                if len(rctn_tmp.spell_and_header) > 6:
                    spll_n_hdr_tmp = rctn_tmp.spell_and_header[0:6] + "..."
                else:
                    spll_n_hdr_tmp = rctn_tmp.spell_and_header
                if len(rctn_tmp.mean_and_body) > 6:
                    mn_n_bdy_tmp = rctn_tmp.mean_and_body[0:6] + "..."
                else:
                    mn_n_bdy_tmp = rctn_tmp.mean_and_body
                if len(rctn_tmp.staff_name) > 6:
                    stff_nm_tmp = rctn_tmp.staff_name[0:6] + "..."
                else:
                    stff_nm_tmp = rctn_tmp.staff_name
                rctns_fnl.append([id_tmp,
                                 spll_n_hdr_tmp,
                                 mn_n_bdy_tmp,
                                 stff_nm_tmp
                                ])
        per_pg = consts.REACTION_ITEM_PER_PAGE
        pg = request.args.get(get_page_parameter(), type=int, default=1)
        pg_dat = rctns_fnl[(pg - 1) * per_pg : pg * per_pg]
        pgntn = Pagination(page=pg,
                           total=len(rctns_fnl),
                           per_page=per_pg,
                           css_framework=consts.PAGINATION_CSS
                          )
        return render_template("search_reactions_results.html", page_data=pg_dat, pagination=pgntn)

    if request.method == "POST":
        # 直前に, GETメソッドで該当ページを取得しているかを調べる.
        # 取得していなければ, 強制的に現在ページへリダイレクトする.
        if session["referrer-page"] != "view.search_reactions_results":
            return redirect(url_for("view.search_reactions_results"))

        # フォームボタン群の中から, 押下されたボタンに応じたページへリダイレクトする.
        if request.form["hidden-modify-item-id"] != "":
            session["hidden-modify-item-id"] = request.form["hidden-modify-item-id"]
            return redirect(url_for("view.modify_reaction"))
        if request.form["hidden-detail-item-id"] != "":
            session["hidden-detail-item-id"] = request.form["hidden-detail-item-id"]
            return redirect(url_for("view.detail_reaction"))

        # フォームが改竄されているので, その旨を通知するために例外を発生させる.
        raise BadRequest


# 「search_generates_results」のためのビュー関数(=URLエンドポイント)を宣言・定義する.
@view.route("/search_generates_results", methods=["GET", "POST"])
def search_generates_results():
    # 関数内で使用する変数・オブジェクトを宣言・定義する.
    gens_tmp = []
    gens_fnl = []
    is_srch_done = False

    # 該当のURLエンドポイントに入ったことをロギングする.
    rslt = cr_engn.etc.logging__info("view at /search_generates_results")

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

        # 検索条件(=検索キー)となる値をまとめて取得する.
        id = str(session["id"]).split(" ")
        spll_n_hdr = str(session["spell-and-header"])
        mn_n_bdy = str(session["mean-and-body"])
        stff_nm = str(session["staff-name"]).split(" ")
        stff_kn_nm = str(session["staff-kana-name"]).split(" ")
        crtd_at_bgn = session["created-at-begin"]
        crtd_at_end = session["created-at-end"]
        updtd_at_bgn = session["updated-at-begin"]
        updtd_at_end = session["updated-at-end"]
        srt_cndtn = str(session["sort-condition"])
        extrct_cndtn = str(session["extract-condition"])

        # 各種の検索条件に基づいてレコードを検索する.
        if (((len(id) == 1) and (id[0] == "")) == False):
            srch_trgt = id
            if ((srt_cndtn == "condition-1") and (extrct_cndtn == "condition-1")):
                  gens_tmp = (
                  db_session.query(Generate).filter(Generate.id.in_(srch_trgt), Generate.is_hidden == False).order_by(Generate.id.asc()).all()
                  )
                  db_session.close()
                  is_srch_done = True
            elif ((srt_cndtn == "condition-1") and (extrct_cndtn == "condition-2")):
                  gens_tmp = (
                  db_session.query(Generate).filter(Generate.id.in_(srch_trgt)).order_by(Generate.id.asc()).all()
                  )
                  db_session.close()
                  is_srch_done = True
            elif ((srt_cndtn == "condition-2") and (extrct_cndtn == "condition-1")):
                  gens_tmp = (
                  db_session.query(Generate).filter(Generate.id.in_(srch_trgt), Generate.is_hidden == False).order_by(Generate.id.desc()).all()
                  )
                  db_session.close()
                  is_srch_done = True
            else:
                  gens_tmp = (
                  db_session.query(Generate).filter(Generate.id.in_(srch_trgt)).order_by(Generate.id.desc()).all()
                  )
                  db_session.close()
                  is_srch_done = True
        if ((spll_n_hdr != "") and (is_srch_done == False)):
            srch_trgt = [spll_n_hdr]
            if ((srt_cndtn == "condition-1") and (extrct_cndtn == "condition-1")):
                  gens_tmp = (
                  db_session.query(Generate).filter(Generate.spell_and_header.in_(srch_trgt), Generate.is_hidden == False).order_by(Generate.id.asc()).all()
                  )
                  db_session.close()
                  is_srch_done = True
            elif ((srt_cndtn == "condition-1") and (extrct_cndtn == "condition-2")):
                  gens_tmp = (
                  db_session.query(Generate).filter(Generate.spell_and_header.in_(srch_trgt)).order_by(Generate.id.asc()).all()
                  )
                  db_session.close()
                  is_srch_done = True
            elif ((srt_cndtn == "condition-2") and (extrct_cndtn == "condition-1")):
                  gens_tmp = (
                  db_session.query(Generate).filter(Generate.spell_and_header.in_(srch_trgt), Generate.is_hidden == False).order_by(Generate.id.desc()).all()
                  )
                  db_session.close()
                  is_srch_done = True
            else:
                  gens_tmp = (
                  db_session.query(Generate).filter(Generate.spell_and_header.in_(srch_trgt)).order_by(Generate.id.desc()).all()
                  )
                  db_session.close()
                  is_srch_done = True
        if ((mn_n_bdy != "") and (is_srch_done == False)):
            srch_trgt = [mn_n_bdy]
            if ((srt_cndtn == "condition-1") and (extrct_cndtn == "condition-1")):
                  gens_tmp = (
                  db_session.query(Generate).filter(Generate.mean_and_body.in_(srch_trgt), Generate.is_hidden == False).order_by(Generate.id.asc()).all()
                  )
                  db_session.close()
                  is_srch_done = True
            elif ((srt_cndtn == "condition-1") and (extrct_cndtn == "condition-2")):
                  gens_tmp = (
                  db_session.query(Generate).filter(Generate.mean_and_body.in_(srch_trgt)).order_by(Generate.id.asc()).all()
                  )
                  db_session.close()
                  is_srch_done = True
            elif ((srt_cndtn == "condition-2") and (extrct_cndtn == "condition-1")):
                  gens_tmp = (
                  db_session.query(Generate).filter(Generate.mean_and_body.in_(srch_trgt), Generate.is_hidden == False).order_by(Generate.id.desc()).all()
                  )
                  db_session.close()
                  is_srch_done = True
            else:
                  gens_tmp = (
                  db_session.query(Generate).filter(Generate.mean_and_body.in_(srch_trgt)).order_by(Generate.id.desc()).all()
                  )
                  db_session.close()
                  is_srch_done = True
        if ((((len(stff_nm) == 1) and (stff_nm[0] == "")) == False) and (is_srch_done == False)):
            srch_trgt = stff_nm
            if ((srt_cndtn == "condition-1") and (extrct_cndtn == "condition-1")):
                  gens_tmp = (
                  db_session.query(Generate).filter(Generate.staff_name.in_(srch_trgt), Generate.is_hidden == False).order_by(Generate.id.asc()).all()
                  )
                  db_session.close()
                  is_srch_done = True
            elif ((srt_cndtn == "condition-1") and (extrct_cndtn == "condition-2")):
                  gens_tmp = (
                  db_session.query(Generate).filter(Generate.staff_name.in_(srch_trgt)).order_by(Generate.id.asc()).all()
                  )
                  db_session.close()
                  is_srch_done = True
            elif ((srt_cndtn == "condition-2") and (extrct_cndtn == "condition-1")):
                  gens_tmp = (
                  db_session.query(Generate).filter(Generate.staff_name.in_(srch_trgt), Generate.is_hidden == False).order_by(Generate.id.desc()).all()
                  )
                  db_session.close()
                  is_srch_done = True
            else:
                  gens_tmp = (
                  db_session.query(Generate).filter(Generate.staff_name.in_(srch_trgt)).order_by(Generate.id.desc()).all()
                  )
                  db_session.close()
                  is_srch_done = True
        if ((((len(stff_kn_nm) == 1) and (stff_kn_nm[0] == "")) == False) and (is_srch_done == False)):
            srch_trgt = stff_kn_nm
            if ((srt_cndtn == "condition-1") and (extrct_cndtn == "condition-1")):
                  gens_tmp = (
                  db_session.query(Generate).filter(Generate.staff_kana_name.in_(srch_trgt), Generate.is_hidden == False).order_by(Generate.id.asc()).all()
                  )
                  db_session.close()
                  is_srch_done = True
            elif ((srt_cndtn == "condition-1") and (extrct_cndtn == "condition-2")):
                  gens_tmp = (
                  db_session.query(Generate).filter(Generate.staff_kana_name.in_(srch_trgt)).order_by(Generate.id.asc()).all()
                  )
                  db_session.close()
                  is_srch_done = True
            elif ((srt_cndtn == "condition-2") and (extrct_cndtn == "condition-1")):
                  gens_tmp = (
                  db_session.query(Generate).filter(Generate.staff_kana_name.in_(srch_trgt), Generate.is_hidden == False).order_by(Generate.id.desc()).all()
                  )
                  db_session.close()
                  is_srch_done = True
            else:
                  gens_tmp = (
                  db_session.query(Generate).filter(Generate.staff_kana_name.in_(srch_trgt)).order_by(Generate.id.desc()).all()
                  )
                  db_session.close()
                  is_srch_done = True
        if (((crtd_at_bgn is not None) and (crtd_at_end is not None)) and (is_srch_done == False)):
            if ((srt_cndtn=="condition-1") and (extrct_cndtn=="condition-1")):
                  gens_tmp = (
                  db_session.query(Generate).filter(Generate.created_at >= crtd_at_bgn, Generate.created_at <= crtd_at_end, Generate.is_hidden == False).order_by(Generate.id.asc()).all()
                  )
                  db_session.close()
                  is_srch_done = True
            elif ((srt_cndtn=="condition-1") and (extrct_cndtn=="condition-2")):
                  gens_tmp = (
                  db_session.query(Generate).filter(Generate.created_at >= crtd_at_bgn, Generate.created_at <= crtd_at_end).order_by(Generate.id.asc()).all()
                  )
                  db_session.close()
                  is_srch_done = True
            elif ((srt_cndtn=="condition-2") and (extrct_cndtn=="condition-1")):
                  gens_tmp = (
                  db_session.query(Generate).filter(Generate.created_at >= crtd_at_bgn, Generate.created_at <= crtd_at_end, Generate.is_hidden == False).order_by(Generate.id.desc()).all()
                  )
                  db_session.close()
                  is_srch_done = True
            else:
                  gens_tmp = (
                  db_session.query(Generate).filter(Generate.created_at >= crtd_at_bgn, Generate.created_at <= crtd_at_end).order_by(Generate.id.desc()).all()
                  )
                  db_session.close()
                  is_srch_done = True
        if (((updtd_at_bgn is not None) and (updtd_at_end is not None)) and (is_srch_done == False)):
            if ((srt_cndtn=="condition-1") and (extrct_cndtn=="condition-1")):
                  gens_tmp = (
                  db_session.query(Generate).filter(Generate.created_at >= updtd_at_bgn, Generate.created_at <= updtd_at_end, Generate.is_hidden == False).order_by(Generate.id.asc()).all()
                  )
                  db_session.close()
            elif ((srt_cndtn=="condition-1") and (extrct_cndtn=="condition-2")):
                  gens_tmp = (
                  db_session.query(Generate).filter(Generate.created_at >= updtd_at_bgn, Generate.created_at <= updtd_at_end).order_by(Generate.id.asc()).all()
                  )
                  db_session.close()
            elif ((srt_cndtn=="condition-2") and (extrct_cndtn=="condition-1")):
                  gens_tmp = (
                  db_session.query(Generate).filter(Generate.created_at >= updtd_at_bgn, Generate.created_at <= updtd_at_end, Generate.is_hidden == False).order_by(Generate.id.desc()).all()
                  )
                  db_session.close()
            else:
                  gens_tmp = (
                  db_session.query(Generate).filter(Generate.created_at >= updtd_at_bgn, Generate.created_at <= updtd_at_end).order_by(Generate.id.desc()).all()
                  )
                  db_session.close()

        # 検索結果を整形し, 配列にセットしてテンプレートと共に返す.
        if gens_tmp is not None:
            for gen_tmp in gens_tmp:
                if len(str(gen_tmp.id)) > 6:
                    id_tmp = gen_tmp.id[0:6] + "..."
                else:
                    id_tmp = gen_tmp.id
                if len(gen_tmp.spell_and_header) > 6:
                    spll_n_hdr_tmp = gen_tmp.spell_and_header[0:6] + "..."
                else:
                    spll_n_hdr_tmp = gen_tmp.spell_and_header
                if len(gen_tmp.mean_and_body) > 6:
                    mn_n_bdy_tmp = gen_tmp.mean_and_body[0:6] + "..."
                else:
                    mn_n_bdy_tmp = gen_tmp.mean_and_body
                if len(gen_tmp.staff_name) > 6:
                    stff_nm_tmp = gen_tmp.staff_name[0:6] + "..."
                else:
                    stff_nm_tmp = gen_tmp.staff_name
                gens_fnl.append([id_tmp,
                                 spll_n_hdr_tmp,
                                 mn_n_bdy_tmp,
                                 stff_nm_tmp
                                ])
        per_pg = consts.GENERATE_ITEM_PER_PAGE
        pg = request.args.get(get_page_parameter(), type=int, default=1)
        pg_dat = gens_fnl[(pg - 1) * per_pg : pg * per_pg]
        pgntn = Pagination(page=pg,
                           total=len(gens_fnl),
                           per_page=per_pg,
                           css_framework=consts.PAGINATION_CSS
                          )
        return render_template("search_generatess_results.html", page_data=pg_dat, pagination=pgntn)

    if request.method == "POST":
        # 直前に, GETメソッドで該当ページを取得しているかを調べる.
        # 取得していなければ, 強制的に現在ページへリダイレクトする.
        if session["referrer-page"] != "view.search_generates_results":
            return redirect(url_for("view.search_generates_results"))

        # フォームボタン群の中から, 押下されたボタンに応じたページへリダイレクトする.
        if request.form["hidden-retrieve-item-id"] != "":
            session["hidden-retrieve-item-id"] = request.form["hidden-retrieve-item-id"]
            return redirect(url_for("view.retrieve_generate"))
        if request.form["hidden-detail-item-id"] != "":
            session["hidden-detail-item-id"] = request.form["hidden-detail-item-id"]
            return redirect(url_for("view.detail_generate"))

        # フォームが改竄されているので, その旨を通知するために例外を発生させる.
        raise BadRequest


# 「search_histories_results」のためのビュー関数(=URLエンドポイント)を宣言・定義する.
@view.route("/search_histories_results", methods=["GET", "POST"])
def search_histories_results():
    # 関数内で使用する変数・オブジェクトを宣言・定義する.
    hists_tmp = []
    hists_fnl = []
    is_srch_done = False

    # 該当のURLエンドポイントに入ったことをロギングする.
    rslt = cr_engn.etc.logging__info("view at /search_histories_results")

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

        # 検索条件(=検索キー)となる値をまとめて取得する.
        id = str(session["id"]).split(" ")
        stff_msg = str(session["staff-message"])
        app_msg = str(session["application-message"])
        stff_nm = str(session["staff-name"]).split(" ")
        stff_kn_nm = str(session["staff-kana-name"]).split(" ")
        crtd_at_bgn = session["created-at-begin"]
        crtd_at_end = session["created-at-end"]
        updtd_at_bgn = session["updated-at-begin"]
        updtd_at_end = session["updated-at-end"]
        srt_cndtn = str(session["sort-condition"])
        extrct_cndtn = str(session["extract-condition"])

        # 各種の検索条件に基づいてレコードを検索する.
        if (((len(id) == 1) and (id[0] == "")) == False):
            srch_trgt = id
            if ((srt_cndtn == "condition-1") and (extrct_cndtn == "condition-1")):
                  hists_tmp = (
                  db_session.query(History).filter(History.id.in_(srch_trgt), History.is_hidden == False).order_by(History.id.asc()).all()
                  )
                  db_session.close()
                  is_srch_done = True
            elif ((srt_cndtn == "condition-1") and (extrct_cndtn == "condition-2")):
                  hists_tmp = (
                  db_session.query(History).filter(History.id.in_(srch_trgt)).order_by(History.id.asc()).all()
                  )
                  db_session.close()
                  is_srch_done = True
            elif ((srt_cndtn == "condition-2") and (extrct_cndtn == "condition-1")):
                  hists_tmp = (
                  db_session.query(History).filter(History.id.in_(srch_trgt), History.is_hidden == False).order_by(History.id.desc()).all()
                  )
                  db_session.close()
                  is_srch_done = True
            else:
                  hists_tmp = (
                  db_session.query(History).filter(History.id.in_(srch_trgt)).order_by(History.id.desc()).all()
                  )
                  db_session.close()
                  is_srch_done = True
        if ((stff_msg != "") and (is_srch_done == False)):
            srch_trgt = [stff_msg]
            if ((srt_cndtn == "condition-1") and (extrct_cndtn == "condition-1")):
                  hists_tmp = (
                  db_session.query(History).filter(History.staff_text_message.in_(srch_trgt), History.is_hidden == False).order_by(History.id.asc()).all()
                  )
                  db_session.close()
                  is_srch_done = True
            elif ((srt_cndtn == "condition-1") and (extrct_cndtn == "condition-2")):
                  hists_tmp = (
                  db_session.query(History).filter(History.staff_text_message.in_(srch_trgt)).order_by(History.id.asc()).all()
                  )
                  db_session.close()
                  is_srch_done = True
            elif ((srt_cndtn == "condition-2") and (extrct_cndtn == "condition-1")):
                  hists_tmp = (
                  db_session.query(History).filter(History.staff_text_message.in_(srch_trgt), History.is_hidden == False).order_by(History.id.desc()).all()
                  )
                  db_session.close()
                  is_srch_done = True
            else:
                  hists_tmp = (
                  db_session.query(History).filter(History.staff_text_message.in_(srch_trgt)).order_by(History.id.desc()).all()
                  )
                  db_session.close()
                  is_srch_done = True
        if ((app_msg != "") and (is_srch_done == False)):
            srch_trgt = [app_msg]
            if ((srt_cndtn == "condition-1") and (extrct_cndtn == "condition-1")):
                  hists_tmp = (
                  db_session.query(History).filter(History.application_text_message.in_(srch_trgt), History.is_hidden == False).order_by(History.id.asc()).all()
                  )
                  db_session.close()
                  is_srch_done = True
            elif ((srt_cndtn == "condition-1") and (extrct_cndtn == "condition-2")):
                  hists_tmp = (
                  db_session.query(History).filter(History.application_text_message.in_(srch_trgt)).order_by(History.id.asc()).all()
                  )
                  db_session.close()
                  is_srch_done = True
            elif ((srt_cndtn == "condition-2") and (extrct_cndtn == "condition-1")):
                  hists_tmp = (
                  db_session.query(History).filter(History.application_text_message.in_(srch_trgt), History.is_hidden == False).order_by(History.id.desc()).all()
                  )
                  db_session.close()
                  is_srch_done = True
            else:
                  hists_tmp = (
                  db_session.query(History).filter(History.application_text_message.in_(srch_trgt)).order_by(History.id.desc()).all()
                  )
                  db_session.close()
                  is_srch_done = True
        if ((((len(stff_nm) == 1) and (stff_nm[0] == "")) == False) and (is_srch_done == False)):
            srch_trgt = stff_nm
            if ((srt_cndtn == "condition-1") and (extrct_cndtn == "condition-1")):
                  hists_tmp = (
                  db_session.query(History).filter(History.staff_name.in_(srch_trgt), History.is_hidden == False).order_by(History.id.asc()).all()
                  )
                  db_session.close()
                  is_srch_done = True
            elif ((srt_cndtn == "condition-1") and (extrct_cndtn == "condition-2")):
                  hists_tmp = (
                  db_session.query(History).filter(History.staff_name.in_(srch_trgt)).order_by(History.id.asc()).all()
                  )
                  db_session.close()
                  is_srch_done = True
            elif ((srt_cndtn == "condition-2") and (extrct_cndtn == "condition-1")):
                  hists_tmp = (
                  db_session.query(History).filter(History.staff_name.in_(srch_trgt), History.is_hidden == False).order_by(History.id.desc()).all()
                  )
                  db_session.close()
                  is_srch_done = True
            else:
                  hists_tmp = (
                  db_session.query(History).filter(History.staff_name.in_(srch_trgt)).order_by(History.id.desc()).all()
                  )
                  db_session.close()
                  is_srch_done = True
        if ((((len(stff_kn_nm) == 1) and (stff_kn_nm[0] == "")) == False) and (is_srch_done == False)):
            srch_trgt = stff_kn_nm
            if ((srt_cndtn == "condition-1") and (extrct_cndtn == "condition-1")):
                  hists_tmp = (
                  db_session.query(History).filter(History.staff_kana_name.in_(srch_trgt), History.is_hidden == False).order_by(History.id.asc()).all()
                  )
                  db_session.close()
                  is_srch_done = True
            elif ((srt_cndtn == "condition-1") and (extrct_cndtn == "condition-2")):
                  hists_tmp = (
                  db_session.query(History).filter(History.staff_kana_name.in_(srch_trgt)).order_by(History.id.asc()).all()
                  )
                  db_session.close()
                  is_srch_done = True
            elif ((srt_cndtn == "condition-2") and (extrct_cndtn == "condition-1")):
                  hists_tmp = (
                  db_session.query(History).filter(History.staff_kana_name.in_(srch_trgt), History.is_hidden == False).order_by(History.id.desc()).all()
                  )
                  db_session.close()
                  is_srch_done = True
            else:
                  hists_tmp = (
                  db_session.query(History).filter(History.staff_kana_name.in_(srch_trgt)).order_by(History.id.desc()).all()
                  )
                  db_session.close()
                  is_srch_done = True
        if (((crtd_at_bgn is not None) and (crtd_at_end is not None)) and (is_srch_done == False)):
            if ((srt_cndtn=="condition-1") and (extrct_cndtn=="condition-1")):
                  hists_tmp = (
                  db_session.query(History).filter(History.created_at >= crtd_at_bgn, History.created_at <= crtd_at_end, History.is_hidden == False).order_by(History.id.asc()).all()
                  )
                  db_session.close()
                  is_srch_done = True
            elif ((srt_cndtn=="condition-1") and (extrct_cndtn=="condition-2")):
                  hists_tmp = (
                  db_session.query(History).filter(History.created_at >= crtd_at_bgn, History.created_at <= crtd_at_end).order_by(History.id.asc()).all()
                  )
                  db_session.close()
                  is_srch_done = True
            elif ((srt_cndtn=="condition-2") and (extrct_cndtn=="condition-1")):
                  hists_tmp = (
                  db_session.query(History).filter(History.created_at >= crtd_at_bgn, History.created_at <= crtd_at_end, History.is_hidden == False).order_by(History.id.desc()).all()
                  )
                  db_session.close()
                  is_srch_done = True
            else:
                  hists_tmp = (
                  db_session.query(History).filter(History.created_at >= crtd_at_bgn, History.created_at <= crtd_at_end).order_by(History.id.desc()).all()
                  )
                  db_session.close()
                  is_srch_done = True
        if (((updtd_at_bgn is not None) and (updtd_at_end is not None)) and (is_srch_done == False)):
            if ((srt_cndtn=="condition-1") and (extrct_cndtn=="condition-1")):
                  hists_tmp = (
                  db_session.query(History).filter(History.created_at >= updtd_at_bgn, History.created_at <= updtd_at_end, History.is_hidden == False).order_by(History.id.asc()).all()
                  )
                  db_session.close()
            elif ((srt_cndtn=="condition-1") and (extrct_cndtn=="condition-2")):
                  hists_tmp = (
                  db_session.query(History).filter(History.created_at >= updtd_at_bgn, History.created_at <= updtd_at_end).order_by(History.id.asc()).all()
                  )
                  db_session.close()
            elif ((srt_cndtn=="condition-2") and (extrct_cndtn=="condition-1")):
                  hists_tmp = (
                  db_session.query(History).filter(History.created_at >= updtd_at_bgn, History.created_at <= updtd_at_end, History.is_hidden == False).order_by(History.id.desc()).all()
                  )
                  db_session.close()
            else:
                  hists_tmp = (
                  db_session.query(History).filter(History.created_at >= updtd_at_bgn, History.created_at <= updtd_at_end).order_by(History.id.desc()).all()
                  )
                  db_session.close()

        # 検索結果を整形し, 配列にセットしてテンプレートと共に返す.
        if hists_tmp is not None:
            for hist_tmp in hists_tmp:
                if len(str(hist_tmp.id)) > 6:
                    id_tmp = hist_tmp.id[0:6] + "..."
                else:
                    id_tmp = hist_tmp.id
                if len(hist_tmp.staff_text_message) > 6:
                    stff_msg_tmp = hist_tmp.staff_text_message[0:6] + "..."
                else:
                    stff_msg_tmp = hist_tmp.staff_text_message
                if len(hist_tmp.application_text_message) > 6:
                    app_msg_tmp = hist_tmp.application_text_message[0:6] + "..."
                else:
                    app_msg_tmp = hist_tmp.application_text_message
                if len(hist_tmp.staff_name) > 6:
                    stff_nm_tmp = hist_tmp.staff_name[0:6] + "..."
                else:
                    stff_nm_tmp = hist_tmp.staff_name
                hists_fnl.append([id_tmp,
                                 stff_msg_tmp,
                                 app_msg_tmp,
                                 stff_nm_tmp
                                ])
        per_pg = consts.HISTORY_ITEM_PER_PAGE
        pg = request.args.get(get_page_parameter(), type=int, default=1)
        pg_dat = hists_fnl[(pg - 1) * per_pg : pg * per_pg]
        pgntn = Pagination(page=pg,
                           total=len(hists_fnl),
                           per_page=per_pg,
                           css_framework=consts.PAGINATION_CSS
                          )
        return render_template("search_histories_results.html", page_data=pg_dat, pagination=pgntn)

    if request.method == "POST":
        # 直前に, GETメソッドで該当ページを取得しているかを調べる.
        # 取得していなければ, 強制的に現在ページへリダイレクトする.
        if session["referrer-page"] != "view.search_histories_results":
            return redirect(url_for("view.search_histories_results"))

        # フォームボタン群の中から, 押下されたボタンに応じたページへリダイレクトする.
        if request.form["hidden-detail-item-id"] != "":
            session["hidden-detail-item-id"] = request.form["hidden-detail-item-id"]
            return redirect(url_for("view.detail_history"))

        # フォームが改竄されているので, その旨を通知するために例外を発生させる.
        raise BadRequest


# 「search_enters_or_exits_results」のためのビュー関数(=URLエンドポイント)を宣言・定義する.
@view.route("/search_enters_or_exits_results", methods=["GET", "POST"])
def search_enters_or_exits_results():
    # 関数内で使用する変数・オブジェクトを宣言・定義する.
    entrs_or_exits_tmp = []
    entrs_or_exits_fnl = []
    is_srch_done = False

    # 該当のURLエンドポイントに入ったことをロギングする.
    rslt = cr_engn.etc.logging__info("view at /search_enters_or_exits_results")

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

        # 検索条件(=検索キー)となる値をまとめて取得する.
        id = str(session["id"]).split(" ")
        stff_nm = str(session["staff-name"]).split(" ")
        stff_kn_nm = str(session["staff-kana-name"]).split(" ")
        rsn = session["reason"]
        entr_or_exit_at_bgn = session["enter-or-exit-at-begin"]
        entr_or_exit_at_end = session["enter-or-exit-at-end"]
        entr_or_exit_at_scnd = str(session["enter-or-exit-at-second"])
        crtd_at_bgn = session["created-at-begin"]
        crtd_at_end = session["created-at-end"]
        updtd_at_bgn = session["updated-at-begin"]
        updtd_at_end = session["updated-at-end"]
        srt_cndtn = str(session["sort-condition"])
        extrct_cndtn = str(session["extract-condition"])

        # 各種の検索条件に基づいてレコードを検索する.
        if (((len(id) == 1) and (id[0] == "")) == False):
            srch_trgt = id
            if ((srt_cndtn == "condition-1") and (extrct_cndtn == "condition-1")):
                  entrs_or_exits_tmp = (
                  db_session.query(EnterOrExit).filter(EnterOrExit.id.in_(srch_trgt), EnterOrExit.is_hidden == False).order_by(EnterOrExit.id.asc()).all()
                  )
                  db_session.close()
                  is_srch_done = True
            elif ((srt_cndtn == "condition-1") and (extrct_cndtn == "condition-2")):
                  entrs_or_exits_tmp = (
                  db_session.query(EnterOrExit).filter(EnterOrExit.id.in_(srch_trgt)).order_by(EnterOrExit.id.asc()).all()
                  )
                  db_session.close()
                  is_srch_done = True
            elif ((srt_cndtn == "condition-2") and (extrct_cndtn == "condition-1")):
                  entrs_or_exits_tmp = (
                  db_session.query(EnterOrExit).filter(EnterOrExit.id.in_(srch_trgt), EnterOrExit.is_hidden == False).order_by(EnterOrExit.id.desc()).all()
                  )
                  db_session.close()
                  is_srch_done = True
            else:
                  entrs_or_exits_tmp = (
                  db_session.query(EnterOrExit).filter(EnterOrExit.id.in_(srch_trgt)).order_by(EnterOrExit.id.desc()).all()
                  )
                  db_session.close()
                  is_srch_done = True
        if ((((len(stff_nm) == 1) and (stff_nm[0] == "")) == False) and (is_srch_done == False)):
            srch_trgt = stff_nm
            if ((srt_cndtn == "condition-1") and (extrct_cndtn == "condition-1")):
                  entrs_or_exits_tmp = (
                  db_session.query(EnterOrExit).filter(EnterOrExit.staff_name.in_(srch_trgt), EnterOrExit.is_hidden == False).order_by(EnterOrExit.id.asc()).all()
                  )
                  db_session.close()
                  is_srch_done = True
            elif ((srt_cndtn == "condition-1") and (extrct_cndtn == "condition-2")):
                  entrs_or_exits_tmp = (
                  db_session.query(EnterOrExit).filter(EnterOrExit.staff_name.in_(srch_trgt)).order_by(EnterOrExit.id.asc()).all()
                  )
                  db_session.close()
                  is_srch_done = True
            elif ((srt_cndtn == "condition-2") and (extrct_cndtn == "condition-1")):
                  entrs_or_exits_tmp = (
                  db_session.query(EnterOrExit).filter(EnterOrExit.staff_name.in_(srch_trgt), EnterOrExit.is_hidden == False).order_by(EnterOrExit.id.desc()).all()
                  )
                  db_session.close()
                  is_srch_done = True
            else:
                  entrs_or_exits_tmp = (
                  db_session.query(EnterOrExit).filter(EnterOrExit.staff_name.in_(srch_trgt)).order_by(EnterOrExit.id.desc()).all()
                  )
                  db_session.close()
                  is_srch_done = True
        if ((((len(stff_kn_nm) == 1) and (stff_kn_nm[0] == "")) == False) and (is_srch_done == False)):
            srch_trgt = stff_kn_nm
            if ((srt_cndtn == "condition-1") and (extrct_cndtn == "condition-1")):
                  entrs_or_exits_tmp = (
                  db_session.query(EnterOrExit).filter(EnterOrExit.staff_kana_name.in_(srch_trgt), EnterOrExit.is_hidden == False).order_by(EnterOrExit.id.asc()).all()
                  )
                  db_session.close()
                  is_srch_done = True
            elif ((srt_cndtn == "condition-1") and (extrct_cndtn == "condition-2")):
                  entrs_or_exits_tmp = (
                  db_session.query(EnterOrExit).filter(EnterOrExit.staff_kana_name.in_(srch_trgt)).order_by(EnterOrExit.id.asc()).all()
                  )
                  db_session.close()
                  is_srch_done = True
            elif ((srt_cndtn == "condition-2") and (extrct_cndtn == "condition-1")):
                  entrs_or_exits_tmp = (
                  db_session.query(EnterOrExit).filter(EnterOrExit.staff_kana_name.in_(srch_trgt), EnterOrExit.is_hidden == False).order_by(EnterOrExit.id.desc()).all()
                  )
                  db_session.close()
                  is_srch_done = True
            else:
                  entrs_or_exits_tmp = (
                  db_session.query(EnterOrExit).filter(EnterOrExit.staff_kana_name.in_(srch_trgt)).order_by(EnterOrExit.id.desc()).all()
                  )
                  db_session.close()
                  is_srch_done = True
        if ((rsn != "") and (is_srch_done == False)):
            srch_trgt = [rsn]
            if ((srt_cndtn == "condition-1") and (extrct_cndtn == "condition-1")):
                  entrs_or_exits_tmp = (
                  db_session.query(EnterOrExit).filter(EnterOrExit.reason.in_(srch_trgt), EnterOrExit.is_hidden == False).order_by(EnterOrExit.id.asc()).all()
                  )
                  db_session.close()
                  is_srch_done = True
            elif ((srt_cndtn == "condition-1") and (extrct_cndtn == "condition-2")):
                  entrs_or_exits_tmp = (
                  db_session.query(EnterOrExit).filter(EnterOrExit.reason.in_(srch_trgt)).order_by(EnterOrExit.id.asc()).all()
                  )
                  db_session.close()
                  is_srch_done = True
            elif ((srt_cndtn == "condition-2") and (extrct_cndtn == "condition-1")):
                  entrs_or_exits_tmp = (
                  db_session.query(EnterOrExit).filter(EnterOrExit.reason.in_(srch_trgt), EnterOrExit.is_hidden == False).order_by(EnterOrExit.id.desc()).all()
                  )
                  db_session.close()
                  is_srch_done = True
            else:
                  entrs_or_exits_tmp = (
                  db_session.query(EnterOrExit).filter(EnterOrExit.reason.in_(srch_trgt)).order_by(EnterOrExit.id.desc()).all()
                  )
                  db_session.close()
                  is_srch_done = True
        if ((entr_or_exit_at_bgn is not None) and (entr_or_exit_at_end is not None) and (is_srch_done == False)):
            if ((srt_cndtn=="condition-1") and (extrct_cndtn=="condition-1")):
                  entrs_or_exits_tmp = (
                  db_session.query(EnterOrExit).filter(EnterOrExit.enter_or_exit_at >= entr_or_exit_at_bgn, EnterOrExit.enter_or_exit_at <= entr_or_exit_at_end, EnterOrExit.is_hidden == False).order_by(EnterOrExit.id.asc()).all()
                  )
                  db_session.close()
                  is_srch_done = True
            elif ((srt_cndtn=="condition-1") and (extrct_cndtn=="condition-2")):
                  entrs_or_exits_tmp = (
                  db_session.query(EnterOrExit).filter(EnterOrExit.enter_or_exit_at >= entr_or_exit_at_bgn, EnterOrExit.enter_or_exit_at <= entr_or_exit_at_end).order_by(EnterOrExit.id.asc()).all()
                  )
                  db_session.close()
                  is_srch_done = True
            elif ((srt_cndtn=="condition-2") and (extrct_cndtn=="condition-1")):
                  entrs_or_exits_tmp = (
                  db_session.query(EnterOrExit).filter(EnterOrExit.enter_or_exit_at >= entr_or_exit_at_bgn, EnterOrExit.enter_or_exit_at <= entr_or_exit_at_end, EnterOrExit.is_hidden == False).order_by(EnterOrExit.id.desc()).all()
                  )
                  db_session.close()
                  is_srch_done = True
            else:
                  entrs_or_exits_tmp = (
                  db_session.query(EnterOrExit).filter(EnterOrExit.enter_or_exit_at >= entr_or_exit_at_bgn, EnterOrExit.enter_or_exit_at <= entr_or_exit_at_end).order_by(EnterOrExit.id.desc()).all()
                  )
                  db_session.close()
                  is_srch_done = True
        if ((entr_or_exit_at_scnd != "") and (is_srch_done == False)):
            srch_trgt = [entr_or_exit_at_scnd]
            if ((srt_cndtn == "condition-1") and (extrct_cndtn == "condition-1")):
                  entrs_or_exits_tmp = (
                  db_session.query(EnterOrExit).filter(EnterOrExit.enter_or_exit_at_second.in_(srch_trgt), EnterOrExit.is_hidden == False).order_by(EnterOrExit.id.asc()).all()
                  )
                  db_session.close()
                  is_srch_done = True
            elif ((srt_cndtn == "condition-1") and (extrct_cndtn == "condition-2")):
                  entrs_or_exits_tmp = (
                  db_session.query(EnterOrExit).filter(EnterOrExit.enter_or_exit_at_second.in_(srch_trgt)).order_by(EnterOrExit.id.asc()).all()
                  )
                  db_session.close()
                  is_srch_done = True
            elif ((srt_cndtn == "condition-2") and (extrct_cndtn == "condition-1")):
                  entrs_or_exits_tmp = (
                  db_session.query(EnterOrExit).filter(EnterOrExit.enter_or_exit_at_second.in_(srch_trgt), EnterOrExit.is_hidden == False).order_by(EnterOrExit.id.desc()).all()
                  )
                  db_session.close()
                  is_srch_done = True
            else:
                  entrs_or_exits_tmp = (
                  db_session.query(EnterOrExit).filter(EnterOrExit.enter_or_exit_at_second.in_(srch_trgt)).order_by(EnterOrExit.id.desc()).all()
                  )
                  db_session.close()
                  is_srch_done = True
        if (((crtd_at_bgn is not None) and (crtd_at_end is not None)) and (is_srch_done == False)):
            if ((srt_cndtn=="condition-1") and (extrct_cndtn=="condition-1")):
                  entrs_or_exits_tmp = (
                  db_session.query(EnterOrExit).filter(EnterOrExit.created_at >= crtd_at_bgn, EnterOrExit.created_at <= crtd_at_end, EnterOrExit.is_hidden == False).order_by(EnterOrExit.id.asc()).all()
                  )
                  db_session.close()
                  is_srch_done = True
            elif ((srt_cndtn=="condition-1") and (extrct_cndtn=="condition-2")):
                  entrs_or_exits_tmp = (
                  db_session.query(EnterOrExit).filter(EnterOrExit.created_at >= crtd_at_bgn, EnterOrExit.created_at <= crtd_at_end).order_by(EnterOrExit.id.asc()).all()
                  )
                  db_session.close()
                  is_srch_done = True
            elif ((srt_cndtn=="condition-2") and (extrct_cndtn=="condition-1")):
                  entrs_or_exits_tmp = (
                  db_session.query(EnterOrExit).filter(EnterOrExit.created_at >= crtd_at_bgn, EnterOrExit.created_at <= crtd_at_end, EnterOrExit.is_hidden == False).order_by(EnterOrExit.id.desc()).all()
                  )
                  db_session.close()
                  is_srch_done = True
            else:
                  entrs_or_exits_tmp = (
                  db_session.query(EnterOrExit).filter(EnterOrExit.created_at >= crtd_at_bgn, EnterOrExit.created_at <= crtd_at_end).order_by(EnterOrExit.id.desc()).all()
                  )
                  db_session.close()
                  is_srch_done = True
        if (((updtd_at_bgn is not None) and (updtd_at_end is not None)) and (is_srch_done == False)):
            if ((srt_cndtn=="condition-1") and (extrct_cndtn=="condition-1")):
                  entrs_or_exits_tmp = (
                  db_session.query(EnterOrExit).filter(EnterOrExit.created_at >= updtd_at_bgn, EnterOrExit.created_at <= updtd_at_end, EnterOrExit.is_hidden == False).order_by(EnterOrExit.id.asc()).all()
                  )
                  db_session.close()
            elif ((srt_cndtn=="condition-1") and (extrct_cndtn=="condition-2")):
                  entrs_or_exits_tmp = (
                  db_session.query(EnterOrExit).filter(EnterOrExit.created_at >= updtd_at_bgn, EnterOrExit.created_at <= updtd_at_end).order_by(EnterOrExit.id.asc()).all()
                  )
                  db_session.close()
            elif ((srt_cndtn=="condition-2") and (extrct_cndtn=="condition-1")):
                  entrs_or_exits_tmp = (
                  db_session.query(EnterOrExit).filter(EnterOrExit.created_at >= updtd_at_bgn, EnterOrExit.created_at <= updtd_at_end, EnterOrExit.is_hidden == False).order_by(EnterOrExit.id.desc()).all()
                  )
                  db_session.close()
            else:
                  entrs_or_exits_tmp = db_session.query(EnterOrExit).filter(EnterOrExit.created_at >= updtd_at_bgn, EnterOrExit.created_at <= updtd_at_end).order_by(EnterOrExit.id.desc()).all()
                  db_session.close()

        # 検索結果を整形し, 配列にセットしてテンプレートと共に返す.
        if entrs_or_exits_tmp is not None:
            for entr_or_exit_tmp in entrs_or_exits_tmp:
                if len(str(entr_or_exit_tmp.id)) > 6:
                    id_tmp = entr_or_exit_tmp.id[0:6] + "..."
                else:
                    id_tmp = entr_or_exit_tmp.id
                if len(entr_or_exit_tmp.staff_name) > 6:
                    stff_nm_tmp = entr_or_exit_tmp.staff_name[0:6] + "..."
                else:
                    stff_nm_tmp = entr_or_exit_tmp.staff_name
                if len(entr_or_exit_tmp.reason) > 6:
                    rsn_tmp = entr_or_exit_tmp.reason[0:6] + "..."
                else:
                    rsn_tmp = entr_or_exit_tmp.reason
                if len(entr_or_exit_tmp.enter_or_exit_at) > 6:
                    entr_or_exit_at_tmp = entr_or_exit_tmp.enter_or_exit_at[0:6] + "..."
                else:
                    entr_or_exit_at_tmp = entr_or_exit_tmp.enter_or_exit_at
                entrs_or_exits_fnl.append([id_tmp,
                                           stff_nm_tmp,
                                           rsn_tmp,
                                           entr_or_exit_at_tmp
                                          ])
        per_pg = consts.ENTER_OR_EXIT_ITEM_PER_PAGE
        pg = request.args.get(get_page_parameter(), type=int, default=1)
        pg_dat = entrs_or_exits_fnl[(pg - 1) * per_pg : pg * per_pg]
        pgntn = Pagination(page=pg,
                           total=len(entrs_or_exits_fnl),
                           per_page=per_pg,
                           css_framework=consts.PAGINATION_CSS
                          )
        return render_template("search_enters_or_exits_results.html", page_data=pg_dat, pagination=pgntn)

    if request.method == "POST":
        # 直前に, GETメソッドで該当ページを取得しているかを調べる.
        # 取得していなければ, 強制的に現在ページへリダイレクトする.
        if session["referrer-page"] != "view.search_enters_or_exits_results":
            return redirect(url_for("view.search_enters_or_exits_results"))

        # フォームボタン群の中から, 押下されたボタンに応じたページへリダイレクトする.
        if request.form["hidden-modify-item-id"] != "":
            session["hidden-modify-item-id"] = request.form["hidden-modify-item-id"]
            return redirect(url_for("view.modify_enter_or_exit"))
        if request.form["hidden-detail-item-id"] != "":
            session["hidden-detail-item-id"] = request.form["hidden-detail-item-id"]
            return redirect(url_for("view.detail_enter_or_exit"))

        # フォームが改竄されているので, その旨を通知するために例外を発生させる.
        raise BadRequest


# 「search_staffs_results」のためのビュー関数(=URLエンドポイント)を宣言・定義する.
@view.route("/search_staffs_results", methods=["GET", "POST"])
def search_staffs_results():
    # 関数内で使用する変数・オブジェクトを宣言・定義する.
    stffs_tmp = []
    stffs_fnl = []
    is_srch_done = False

    # 該当のURLエンドポイントに入ったことをロギングする.
    rslt = cr_engn.etc.logging__info("view at /search_staffs_results")

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

        # 検索条件(=検索キー)となる値をまとめて取得する.
        id = str(session["id"]).split(" ")
        sex = session["sex"]
        bld_typ = session["blood-type"]
        brth_dt = session["birth-date"]
        stff_nm = str(session["staff-name"]).split(" ")
        stff_kn_nm = str(session["staff-kana-name"]).split(" ")
        crtd_at_bgn = session["created-at-begin"]
        crtd_at_end = session["created-at-end"]
        updtd_at_bgn = session["updated-at-begin"]
        updtd_at_end = session["updated-at-end"]
        srt_cndtn = str(session["sort-condition"])
        extrct_cndtn = str(session["extract-condition"])

        # 各種の検索条件に基づいてレコードを検索する.
        if (((len(id) == 1) and (id[0] == "")) == False):
            srch_trgt = id
            if ((srt_cndtn == "condition-1") and (extrct_cndtn == "condition-1")):
                  stffs_tmp = (
                  db_session.query(Staff).filter(Staff.id.in_(srch_trgt), Staff.is_hidden == False).order_by(Staff.id.asc()).all()
                  )
                  db_session.close()
                  is_srch_done = True
            elif ((srt_cndtn == "condition-1") and (extrct_cndtn == "condition-2")):
                  stffs_tmp = (
                  db_session.query(Staff).filter(Staff.id.in_(srch_trgt)).order_by(Staff.id.asc()).all()
                  )
                  db_session.close()
                  is_srch_done = True
            elif ((srt_cndtn == "condition-2") and (extrct_cndtn == "condition-1")):
                  stffs_tmp = (
                  db_session.query(Staff).filter(Staff.id.in_(srch_trgt), Staff.is_hidden == False).order_by(Staff.id.desc()).all()
                  )
                  db_session.close()
                  is_srch_done = True
            else:
                  stffs_tmp = (
                  db_session.query(Staff).filter(Staff.id.in_(srch_trgt)).order_by(Staff.id.desc()).all()
                  )
                  db_session.close()
                  is_srch_done = True
        if ((((len(stff_nm) == 1) and (stff_nm[0] == "")) == False) and (is_srch_done == False)):
            srch_trgt = stff_nm
            if ((srt_cndtn == "condition-1") and (extrct_cndtn == "condition-1")):
                  stffs_tmp = (
                  db_session.query(Staff).filter(Staff.name.in_(srch_trgt), Staff.is_hidden == False).order_by(Staff.id.asc()).all()
                  )
                  db_session.close()
                  is_srch_done = True
            elif ((srt_cndtn == "condition-1") and (extrct_cndtn == "condition-2")):
                  stffs_tmp = (
                  db_session.query(Staff).filter(Staff.name.in_(srch_trgt)).order_by(Staff.id.asc()).all()
                  )
                  db_session.close()
                  is_srch_done = True
            elif ((srt_cndtn == "condition-2") and (extrct_cndtn == "condition-1")):
                  stffs_tmp = (
                  db_session.query(Staff).filter(Staff.name.in_(srch_trgt), Staff.is_hidden == False).order_by(Staff.id.desc()).all()
                  )
                  db_session.close()
                  is_srch_done = True
            else:
                  stffs_tmp = (
                  db_session.query(Staff).filter(Staff.name.in_(srch_trgt)).order_by(Staff.id.desc()).all()
                  )
                  db_session.close()
                  is_srch_done = True
        if ((((len(stff_kn_nm) == 1) and (stff_kn_nm[0] == "")) == False) and (is_srch_done == False)):
            srch_trgt = stff_kn_nm
            if ((srt_cndtn == "condition-1") and (extrct_cndtn == "condition-1")):
                  stffs_tmp = (
                  db_session.query(Staff).filter(Staff.kana_name.in_(srch_trgt), Staff.is_hidden == False).order_by(Staff.id.asc()).all()
                  )
                  db_session.close()
                  is_srch_done = True
            elif ((srt_cndtn == "condition-1") and (extrct_cndtn == "condition-2")):
                  stffs_tmp = (
                  db_session.query(Staff).filter(Staff.kana_name.in_(srch_trgt)).order_by(Staff.id.asc()).all()
                  )
                  db_session.close()
                  is_srch_done = True
            elif ((srt_cndtn == "condition-2") and (extrct_cndtn == "condition-1")):
                  stffs_tmp = (
                  db_session.query(Staff).filter(Staff.kana_name.in_(srch_trgt), Staff.is_hidden == False).order_by(Staff.id.desc()).all()
                  )
                  db_session.close()
                  is_srch_done = True
            else:
                  stffs_tmp = (
                  db_session.query(Staff).filter(Staff.kana_name.in_(srch_trgt)).order_by(Staff.id.desc()).all()
                  )
                  db_session.close()
                  is_srch_done = True
        if ((sex != "") and (is_srch_done == False)):
            srch_trgt = [sex]
            if ((srt_cndtn == "condition-1") and (extrct_cndtn == "condition-1")):
                  stffs_tmp = (
                  db_session.query(Staff).filter(Staff.sex.in_(srch_trgt), Staff.is_hidden == False).order_by(Staff.id.asc()).all()
                  )
                  db_session.close()
                  is_srch_done = True
            elif ((srt_cndtn == "condition-1") and (extrct_cndtn == "condition-2")):
                  stffs_tmp = (
                  db_session.query(Staff).filter(Staff.sex.in_(srch_trgt)).order_by(Staff.id.asc()).all()
                  )
                  db_session.close()
                  is_srch_done = True
            elif ((srt_cndtn == "condition-2") and (extrct_cndtn == "condition-1")):
                  stffs_tmp = (
                  db_session.query(Staff).filter(Staff.sex.in_(srch_trgt), Staff.is_hidden == False).order_by(Staff.id.desc()).all()
                  )
                  db_session.close()
                  is_srch_done = True
            else:
                  stffs_tmp = (
                  db_session.query(Staff).filter(Staff.sex.in_(srch_trgt)).order_by(Staff.id.desc()).all()
                  )
                  db_session.close()
                  is_srch_done = True
        if ((bld_typ != "") and (is_srch_done == False)):
            srch_trgt = [bld_typ]
            if ((srt_cndtn == "condition-1") and (extrct_cndtn == "condition-1")):
                  stffs_tmp = (
                  db_session.query(Staff).filter(Staff.blood_type.in_(srch_trgt), Staff.is_hidden == False).order_by(Staff.id.asc()).all()
                  )
                  db_session.close()
                  is_srch_done = True
            elif ((srt_cndtn == "condition-1") and (extrct_cndtn == "condition-2")):
                  stffs_tmp = (
                  db_session.query(Staff).filter(Staff.blood_type.in_(srch_trgt)).order_by(Staff.id.asc()).all()
                  )
                  db_session.close()
                  is_srch_done = True
            elif ((srt_cndtn == "condition-2") and (extrct_cndtn == "condition-1")):
                  stffs_tmp = (
                  db_session.query(Staff).filter(Staff.blood_type.in_(srch_trgt), Staff.is_hidden == False).order_by(Staff.id.desc()).all()
                  )
                  db_session.close()
                  is_srch_done = True
            else:
                  entrs_or_exits_tmp = (
                  db_session.query(Staff).filter(Staff.blood_type.in_(srch_trgt)).order_by(Staff.id.desc()).all()
                  )
                  db_session.close()
                  is_srch_done = True
        if ((brth_dt != "") and (is_srch_done == False)):
            srch_trgt = [brth_dt]
            if ((srt_cndtn == "condition-1") and (extrct_cndtn == "condition-1")):
                  stffs_tmp = (
                  db_session.query(Staff).filter(Staff.birth_date.in_(srch_trgt), Staff.is_hidden == False).order_by(Staff.id.asc()).all()
                  )
                  db_session.close()
                  is_srch_done = True
            elif ((srt_cndtn == "condition-1") and (extrct_cndtn == "condition-2")):
                  stffs_tmp = (
                  db_session.query(Staff).filter(Staff.birth_date.in_(srch_trgt)).order_by(Staff.id.asc()).all()
                  )
                  db_session.close()
                  is_srch_done = True
            elif ((srt_cndtn == "condition-2") and (extrct_cndtn == "condition-1")):
                  stffs_tmp = (
                  db_session.query(Staff).filter(Staff.birth_date.in_(srch_trgt), Staff.is_hidden == False).order_by(Staff.id.desc()).all()
                  )
                  db_session.close()
                  is_srch_done = True
            else:
                  stffs_tmp = (
                  db_session.query(Staff).filter(Staff.birth_date.in_(srch_trgt)).order_by(Staff.id.desc()).all()
                  )
                  db_session.close()
                  is_srch_done = True
        if (((crtd_at_bgn is not None) and (crtd_at_end is not None)) and (is_srch_done == False)):
            if ((srt_cndtn=="condition-1") and (extrct_cndtn=="condition-1")):
                  stffs_tmp = (
                  db_session.query(Staff).filter(Staff.created_at >= crtd_at_bgn, Staff.created_at <= crtd_at_end, Staff.is_hidden == False).order_by(Staff.id.asc()).all()
                  )
                  db_session.close()
                  is_srch_done = True
            elif ((srt_cndtn=="condition-1") and (extrct_cndtn=="condition-2")):
                  stffs_tmp = (
                  db_session.query(Staff).filter(Staff.created_at >= crtd_at_bgn, Staff.created_at <= crtd_at_end).order_by(Staff.id.asc()).all()
                  )
                  db_session.close()
                  is_srch_done = True
            elif ((srt_cndtn=="condition-2") and (extrct_cndtn=="condition-1")):
                  stffs_tmp = (
                  db_session.query(Staff).filter(Staff.created_at >= crtd_at_bgn, Staff.created_at <= crtd_at_end, Staff.is_hidden == False).order_by(Staff.id.desc()).all()
                  )
                  db_session.close()
                  is_srch_done = True
            else:
                  stffs_tmp = (
                  db_session.query(Staff).filter(Staff.created_at >= crtd_at_bgn, Staff.created_at <= crtd_at_end).order_by(Staff.id.desc()).all()
                  )
                  db_session.close()
                  is_srch_done = True
        if (((updtd_at_bgn is not None) and (updtd_at_end is not None)) and (is_srch_done == False)):
            if ((srt_cndtn=="condition-1") and (extrct_cndtn=="condition-1")):
                  stffs_tmp = (
                  db_session.query(Staff).filter(Staff.created_at >= updtd_at_bgn, Staff.created_at <= updtd_at_end, Staff.is_hidden == False).order_by(Staff.id.asc()).all()
                  )
                  db_session.close()
            elif ((srt_cndtn=="condition-1") and (extrct_cndtn=="condition-2")):
                  stffs_tmp = (
                  db_session.query(Staff).filter(Staff.created_at >= updtd_at_bgn, Staff.created_at <= updtd_at_end).order_by(Staff.id.asc()).all()
                  )
                  db_session.close()
            elif ((srt_cndtn=="condition-2") and (extrct_cndtn=="condition-1")):
                  stffs_tmp = (
                  db_session.query(Staff).filter(Staff.created_at >= updtd_at_bgn, Staff.created_at <= updtd_at_end, Staff.is_hidden == False).order_by(Staff.id.desc()).all()
                  )
                  db_session.close()
            else:
                  stffs_tmp = (
                  db_session.query(Staff).filter(Staff.created_at >= updtd_at_bgn, Staff.created_at <= updtd_at_end).order_by(Staff.id.desc()).all()
                  )
                  db_session.close()

        # 検索結果を整形し, 配列にセットしてテンプレートと共に返す.
        if stffs_tmp is not None:
            for stff_tmp in stffs_tmp:
                if len(str(stff_tmp.id)) > 6:
                    id_tmp = stff_tmp.id[0:6] + "..."
                else:
                    id_tmp = stff_tmp.id
                if len(stff_tmp.name) > 6:
                    nm_tmp = stff_tmp.name[0:6] + "..."
                else:
                    nm_tmp = stff_tmp.name
                if len(stff_tmp.sex) > 6:
                    sex_tmp = stff_tmp.sex[0:6] + "..."
                else:
                    sex_tmp = stff_tmp.sex
                if len(stff_tmp.blood_type) > 6:
                    bld_typ_tmp = stff_tmp.blood_type[0:6] + "..."
                else:
                    bld_typ_tmp = stff_tmp.blood_type
                stffs_fnl.append([id_tmp,
                                 nm_tmp,
                                 sex_tmp,
                                 bld_typ_tmp
                                ])
        per_pg = consts.STAFF_ITEM_PER_PAGE
        pg = request.args.get(get_page_parameter(), type=int, default=1)
        pg_dat = stffs_fnl[(pg - 1) * per_pg : pg * per_pg]
        pgntn = Pagination(page=pg,
                           total=len(stffs_fnl),
                           per_page=per_pg,
                           css_framework=consts.PAGINATION_CSS
                          )
        return render_template("search_staffs_results.html", page_data=pg_dat, pagination=pgntn)

    if request.method == "POST":
        # 直前に, GETメソッドで該当ページを取得しているかを調べる.
        # 取得していなければ, 強制的に現在ページへリダイレクトする.
        if session["referrer-page"] != "view.search_staffs_results":
            return redirect(url_for("view.search_staffs_results"))

        # フォームボタン群の中から, 押下されたボタンに応じたページへリダイレクトする.
        if request.form["hidden-modify-item-id"] != "":
            session["hidden-modify-item-id"] = request.form["hidden-modify-item-id"]
            return redirect(url_for("view.modify_staff"))
        if request.form["hidden-detail-item-id"] != "":
            session["hidden-detail-item-id"] = request.form["hidden-detail-item-id"]
            return redirect(url_for("view.detail_staff"))

        # フォームが改竄されているので, その旨を通知するために例外を発生させる.
        raise BadRequest


# 「register_enter_or_exit」のためのビュー関数(=URLエンドポイント)を宣言・定義する.
@view.route("/register_enter_or_exit", methods=["GET", "POST"])
def register_enter_or_exit():
    # 関数内で使用する変数・オブジェクトを宣言・定義する.
    rgstr_entr_or_exit_form = RegisterEnterOrExitForm()

    # 該当のURLエンドポイントに入ったことをロギングする.
    rslt = cr_engn.etc.logging__info("view at /register_enter_or_exit")

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
        if rgstr_entr_or_exit_form.enter_or_exit_at_second.data is None:
            flash("入退日時-秒数が入力されていません.")
            return render_template("register_enter_or_exit.html", form=rgstr_entr_or_exit_form, happen_error=True)
        if ((rgstr_entr_or_exit_form.enter_or_exit_at_second.data < 0) or (rgstr_entr_or_exit_form.enter_or_exit_at_second.data > 59)):
            flash("入退日時-秒数が有効な範囲を超えています.")
            return render_template("register_enter_or_exit.html", form=rgstr_entr_or_exit_form, happen_error=True)
        if rgstr_entr_or_exit_form.is_hidden.data == "":
            flash("秘匿の是非が選択されていません.")
            return render_template("register_enter_or_exit.html", form=rgstr_entr_or_exit_form, happen_error=True)
        if rgstr_entr_or_exit_form.is_exclude.data == "":
            flash("非処理の是非が選択されていません.")
            return render_template("register_enter_or_exit.html", form=rgstr_entr_or_exit_form, happen_error=True)

        # 入退情報をレコードとして, DBに保存・登録する.
        if rgstr_entr_or_exit_form.enter_or_exit_at_second.data < 10:
            crrnt_dttm_scnd = "0" + str(rgstr_entr_or_exit_form.enter_or_exit_at_second.data)
        else:
            crrnt_dttm_scnd = str(rgstr_entr_or_exit_form.enter_or_exit_at_second.data)
        crrnt_dttm = cr_engn.etc.retrieve_current_datetime_as_datetime_object("JST")
        db_session.add(EnterOrExit(staff_name = rgstr_entr_or_exit_form.staff_name.data,
                                   staff_kana_name = rgstr_entr_or_exit_form.staff_kana_name.data,
                                   reason = rgstr_entr_or_exit_form.reason.data,
                                   enter_or_exit_at = rgstr_entr_or_exit_form.enter_or_exit_at.data,
                                   enter_or_exit_at_second = crrnt_dttm_scnd,
                                   created_at=crrnt_dttm,
                                   updated_at=crrnt_dttm,
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
    rslt = cr_engn.etc.logging__info("view at /register_staff")

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
            rgstr_stff_form.password.data = ""
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
        if rgstr_stff_form.password.data == "":
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
        if not cr_engn.reg.check_katakana_uppercase_in_ja(rgstr_stff_form.kana_name.data):
            flash("職員カナ名は, カタカナのみにしてください.")
            return render_template("register_staff.html", form=rgstr_stff_form, happen_error=True)
        if len(rgstr_stff_form.password.data) > consts.PASSWORD_LENGTH:
            flash("パスワードは, " + str(consts.PASSWORD_LENGTH) + "文字以内にしてください.")
            return render_template("register_staff.html", form=rgstr_stff_form, happen_error=True)
        if ((" " in rgstr_stff_form.name.data) or ("　" in rgstr_stff_form.name.data)):
            flash("職員名の一部として, 半角スペースと全角スペースは使用できません.")
            return render_template("register_staff.html", form=rgstr_stff_form, happen_error=True)
        if ((" " in rgstr_stff_form.kana_name.data) or ("　" in rgstr_stff_form.kana_name.data)):
            flash("職員カナ名の一部として, 半角スペースと全角スペースは使用できません.")
            return render_template("register_staff.html", form=rgstr_stff_form, happen_error=True)
        if " " in rgstr_stff_form.password.data:
            flash("パスワードの一部として, 半角スペースは使用できません.")
            return render_template("register_staff.html", form=rgstr_stff_form, happen_error=True)

        drtn_in_dys__crit1 = cr_engn.etc.retrieve_timedelta_from_years(consts.STAFF_AGE_TOP)
        drtn_in_dys__crit2 = cr_engn.etc.retrieve_timedelta_from_years(consts.STAFF_AGE_BOTTOM)
        drtn_in_dys__brth_to_prsnt = cr_engn.etc.retrieve_timedelta_from_date_object(rgstr_stff_form.birth_date.data)

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
        hshd_psswrd = generate_password_hash(rgstr_stff_form.password.data)
        crrnt_dttm = cr_engn.etc.retrieve_current_datetime_as_datetime_object("JST")
        db_session.add(Staff(name=rgstr_stff_form.name.data,
                             kana_name=rgstr_stff_form.kana_name.data,
                             hashed_password=hshd_psswrd,
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
    rslt = cr_engn.etc.logging__info("view at /modify_word")

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
        session["referrer-page"] = "view.modify_word"

        # 指定IDの語句レコードをDBから取得する.
        wrd = (
        db_session.query(Word).filter(Word.id == session["hidden-modify-item-id"]).first()
        )
        db_session.close()

        # フォームにレコードの内容を複写して, フォームと共にテンプレートを返す.
        mod_wrd_form.spell_and_header.data = wrd.spell_and_header
        mod_wrd_form.mean_and_body.data = wrd.mean_and_body
        mod_wrd_form.theme_tag.data = wrd.theme_tag
        mod_wrd_form.intent.data = wrd.intent
        mod_wrd_form.sentiment.data = wrd.sentiment
        mod_wrd_form.sentiment_support.data = wrd.sentiment_support
        mod_wrd_form.strength.data = wrd.strength
        mod_wrd_form.part_of_speech.data = wrd.part_of_speech
        mod_wrd_form.staff_name.data = wrd.staff_name
        mod_wrd_form.staff_kana_name.data = wrd.staff_kana_name
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
            return redirect(url_for("view.admin_dashboard"))

        # flaskフォームに入力・記憶されている内容をバリデーションする.
        # 基準を満たさない場合, フォームと共にテンプレートを返す.
        if mod_wrd_form.spell_and_header.data == "":
            flash("綴り&見出しが入力されていません.")
            return render_template("modify_word.html", form=mod_wrd_form, happen_error=True)
        if mod_wrd_form.mean_and_body.data == "":
            flash("意味&内容が入力されていません.")
            return render_template("modify_word.html", form=mod_wrd_form, happen_error=True)
        if mod_wrd_form.theme_tag.data == "":
            flash("主題タグが入力されていません.")
            return render_template("modify_word.html", form=mod_wrd_form, happen_error=True)
        if mod_wrd_form.intent.data == "":
            flash("意図が選択されていません.")
            return render_template("modify_word.html", form=mod_wrd_form, happen_error=True)
        if mod_wrd_form.sentiment.data == "":
            flash("感情が選択されていません.")
            return render_template("modify_word.html", form=mod_wrd_form, happen_error=True)
        if mod_wrd_form.sentiment_support.data == "":
            flash("感情補助が選択されていません.")
            return render_template("modify_word.html", form=mod_wrd_form, happen_error=True)
        if mod_wrd_form.strength.data == "":
            flash("強度が選択されていません.")
            return render_template("modify_word.html", form=mod_wrd_form, happen_error=True)
        if mod_wrd_form.part_of_speech.data == "":
            flash("品詞分類が選択されていません.")
            return render_template("modify_word.html", form=mod_wrd_form, happen_error=True)
        if mod_wrd_form.staff_name.data == "":
            flash("職員名が入力されていません.")
            return render_template("modify_word.html", form=mod_wrd_form, happen_error=True)
        if mod_wrd_form.staff_kana_name.data == "":
            flash("職員カナ名が入力されていません.")
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
        crrnt_dttm = cr_engn.etc.retrieve_current_datetime_as_datetime_object("JST")
        wrd.spell_and_header = escape(mod_wrd_form.spell_and_header.data)
        wrd.mean_and_body = escape(mod_wrd_form.mean_and_body.data)
        wrd.theme_tag = escape(mod_wrd_form.theme_tag.data)
        wrd.intent = mod_wrd_form.intent.data
        wrd.sentiment = mod_wrd_form.sentiment.data
        wrd.sentiment_support = mod_wrd_form.sentiment_support.data
        wrd.strength = mod_wrd_form.strength.data
        wrd.part_of_speech = mod_wrd_form.part_of_speech.data
        wrd.first_character = mod_wrd_form.spell_and_header.data[0]
        wrd.last_character = mod_wrd_form.spell_and_header.data[-1]
        wrd.characters_count = len(mod_wrd_form.spell_and_header.data)
        wrd.staff_name = escape(mod_wrd_form.staff_name.data)
        wrd.staff_kana_name = escape(mod_wrd_form.staff_kana_name.data)
        wrd.updated_at = crrnt_dttm
        wrd.is_hidden = (True if mod_wrd_form.is_hidden.data == "yes" else False)
        wrd.is_exclude = (True if mod_wrd_form.is_exclude.data == "yes" else False)
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
    rslt = cr_engn.etc.logging__info("view at /modify_theme")

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
        mod_thm_form.mean_and_body.data = thm.mean_and_body
        mod_thm_form.category_tag.data = thm.category_tag
        mod_thm_form.staff_name.data = thm.staff_name
        mod_thm_form.staff_kana_name.data = thm.staff_kana_name
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
        if mod_thm_form.mean_and_body.data == "":
            flash("意味&内容が入力されていません.")
            return render_template("modify_theme.html", form=mod_thm_form, happen_error=True)
        if mod_thm_form.category_tag.data == "":
            flash("分類タグが入力されていません.")
            return render_template("modify_theme.html", form=mod_thm_form, happen_error=True)
        if mod_thm_form.staff_name.data == "":
            flash("職員名が入力されていません.")
            return render_template("modify_word.html", form=mod_thm_form, happen_error=True)
        if mod_thm_form.staff_kana_name.data == "":
            flash("職員カナ名が入力されていません.")
            return render_template("modify_word.html", form=mod_thm_form, happen_error=True)
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
        crrnt_dttm = cr_engn.etc.retrieve_current_datetime_as_datetime_object("JST")
        thm.spell_and_header = escape(mod_thm_form.spell_and_header.data)
        thm.mean_and_body = escape(mod_thm_form.mean_and_body.data)
        thm.category_tag = escape(mod_thm_form.category_tag.data)
        thm.staff_name = escape(mod_thm_form.staff_name.data)
        thm.staff_kana_name = escape(mod_thm_form.staff_kana_name.data)
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
    rslt = cr_engn.etc.logging__info("view at /modify_category")

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
        mod_ctgr_form.mean_and_body.data = ctgr.mean_and_body
        mod_ctgr_form.parent_category_tag.data = ctgr.parent_category_tag
        mod_ctgr_form.sibling_category_tag.data = ctgr.sibling_category_tag
        mod_ctgr_form.child_category_tag.data = ctgr.child_category_tag
        mod_ctgr_form.staff_name.data = ctgr.staff_name
        mod_ctgr_form.staff_kana_name.data = ctgr.staff_kana_name
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
        if mod_ctgr_form.mean_and_body.data == "":
            flash("意味&内容が入力されていません.")
            return render_template("modify_category.html", form=mod_ctgr_form, happen_error=True)
        if mod_ctgr_form.parent_category_tag.data == "":
            flash("親分類タグが入力されていません.")
            return render_template("modify_category.html", form=mod_ctgr_form, happen_error=True)
        if mod_ctgr_form.sibling_category_tag.data == "":
            flash("兄弟分類タグが入力されていません.")
            return render_template("modify_category.html", form=mod_ctgr_form, happen_error=True)
        if mod_ctgr_form.child_category_tag.data == "":
            flash("子分類タグが入力されていません.")
            return render_template("modify_category.html", form=mod_ctgr_form, happen_error=True)
        if mod_ctgr_form.staff_name.data == "":
            flash("職員名が入力されていません.")
            return render_template("modify_word.html", form=mod_ctgr_form, happen_error=True)
        if mod_ctgr_form.staff_kana_name.data == "":
            flash("職員カナ名が入力されていません.")
            return render_template("modify_word.html", form=mod_ctgr_form, happen_error=True)
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
        crrnt_dttm = cr_engn.etc.retrieve_current_datetime_as_datetime_object("JST")
        ctgr.spell_and_header = escape(mod_ctgr_form.spell_and_header.data)
        ctgr.mean_and_body = escape(mod_ctgr_form.mean_and_body.data)
        ctgr.parent_category_tag = escape(mod_ctgr_form.parent_category_tag.data)
        ctgr.sibling_category_tag = escape(mod_ctgr_form.sibling_category_tag.data)
        ctgr.child_category_tag = escape(mod_ctgr_form.child_category_tag.data)
        ctgr.staff_name = escape(mod_ctgr_form.staff_name.data)
        ctgr.staff_kana_name = escape(mod_ctgr_form.staff_kana_name.data)
        ctgr.updated_at = crrnt_dttm
        ctgr.is_hidden = (True if mod_ctgr_form.is_hidden.data == "yes" else False)
        ctgr.is_exclude = (True if mod_ctgr_form.is_exclude.data == "yes" else False)
        db_session.commit()
        db_session.close()

        # 完了メッセージを設定して, テンプレートを返す.
        flash("分類を変更しました.")
        return render_template("modify_fact.html", form=mod_ctgr_form)


# 「modify_fact」のためのビュー関数(=URLエンドポイント)を宣言・定義する.
@view.route("/modify_fact", methods=["GET", "POST"])
def modify_fact():
    # 関数内で使用する変数・オブジェクトを宣言・定義する.
    mod_fct_form = ModifyFactForm()

    # 該当のURLエンドポイントに入ったことをロギングする.
    rslt = cr_engn.etc.logging__info("view at /modify_fact")

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
        session["referrer-page"] = "view.modify_fact"

        # 指定IDの事実レコードをDBから取得する.
        fct = (
        db_session.query(Fact).filter(Fact.id == session["hidden-modify-item-id"]).first()
        )
        db_session.close()

        # フォームにレコードの内容を複写して, フォームと共にテンプレートを返す.
        mod_fct_form.spell_and_header.data = fct.spell_and_header
        mod_fct_form.mean_and_body.data = fct.mean_and_body
        mod_fct_form.category_tag.data = fct.category_tag
        mod_fct_form.staff_name.data = fct.staff_name
        mod_fct_form.staff_kana_name.data = fct.staff_kana_name
        mod_fct_form.is_hidden.data = ("yes" if fct.is_hidden == True else "no")
        mod_fct_form.is_exclude.data = ("yes" if fct.is_exclude == True else "no")
        return render_template("modify_fact.html", form=mod_fct_form,
                               archived_image_file_path=fct.archived_image_file_path,
                               archived_sound_file_path=fct.archived_sound_file_path,
                               archived_video_file_path=fct.archived_video_file_path
                              )

    if request.method == "POST":
        # 直前に, GETメソッドで該当ページを取得しているかを調べる.
        # 取得していなければ, 強制的に現在ページへリダイレクトする.
        if session["referrer-page"] != "view.modify_fact":
            return redirect(url_for("view.modify_fact"))

        # フォームの取消ボタンが押下されたら, 強制的に現在ページへリダイレクトする.
        if mod_fct_form.cancel.data:
            return redirect(url_for("view.admin_dashboard"))

        # flaskフォームに入力・記憶されている内容をバリデーションする.
        # 基準を満たさない場合は, 元のフォームと共にテンプレートを返す.
        if mod_fct_form.spell_and_header.data == "":
            flash("綴り&見出しが入力されていません.")
            return render_template("modify_fact.html", form=mod_fct_form, happen_error=True)
        if mod_fct_form.mean_and_body.data == "":
            flash("意味&内容が入力されていません.")
            return render_template("modify_fact.html", form=mod_fct_form, happen_error=True)
        if mod_fct_form.category_tag.data == "":
            flash("分類タグが入力されていません.")
            return render_template("modify_fact.html", form=mod_fct_form, happen_error=True)
        if mod_fct_form.staff_name == "":
            flash("職員名が入力されていません.")
            return render_template("modify_fact.html", form=mod_fct_form, happen_error=True)
        if mod_fct_form.staff_kana_name == "":
            flash("職員カナ名が入力されていません.")
            return render_template("modify_fact.html", form=mod_fct_form, happen_error=True)
        if mod_fct_form.is_hidden.data == "":
            flash("秘匿の是非が選択されていません.")
            return render_template("modify_fact.html", form=mod_fct_form, happen_error=True)
        if mod_fct_form.is_exclude.data == "":
            flash("非処理の是非が選択されていません.")
            return render_template("modify_fact.html", form=mod_fct_form, happen_error=True)

        # 指定IDの事実レコードを取得し, その内容を上書きしてから, DBセッションを閉じる.
        fct = (
        db_session.query(Fact).filter(Fact.id == session["hidden-modify-item-id"]).first()
        )

        # 指定IDの事実レコードを取得し, その内容を上書きしてから, DBセッションを閉じる.
        fl_lbl = cr_engn.etc.retrieve_current_time_as_file_label()
        crrnt_dttm = cr_engn.etc.retrieve_current_datetime_as_datetime_object("JST")
        archvd_img_fl_pth = cr_engn.etc.save_file(mod_fct_form.attached_image_file.data, consts.ARCHIVE_IMAGE_PATH, fl_lbl)
        archvd_snd_fl_pth = cr_engn.etc.save_file(mod_fct_form.attached_sound_file.data, consts.ARCHIVE_SOUND_PATH, fl_lbl)
        archvd_vdo_fl_pth = cr_engn.etc.save_file(mod_fct_form.attached_video_file.data, consts.ARCHIVE_VIDEO_PATH, fl_lbl)
        fct.spell_and_header = escape(mod_fct_form.spell_and_header.data)
        fct.mean_and_body = escape(mod_fct_form.mean_and_body.data)
        fct.category_tag = escape(mod_fct_form.category_tag.data)
        fct.archived_image_file_path = archvd_img_fl_pth
        fct.archived_sound_file_path = archvd_snd_fl_pth
        fct.archived_video_file_path = archvd_vdo_fl_pth
        fct.staff_name = escape(mod_fct_form.staff_name.data)
        fct.staff_kana_name = escape(mod_fct_form.staff_kana_name.data)
        fct.updated_at = crrnt_dttm
        fct.is_hidden = (True if mod_fct_form.is_hidden.data == "yes" else False)
        fct.is_exclude = (True if mod_fct_form.is_exclude.data == "yes" else False)
        db_session.commit()
        db_session.close()

        # 完了メッセージを設定して, テンプレートを返す.
        flash("事実を変更しました.")
        return render_template("modify_fact.html", form=mod_fct_form,
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
    rslt = cr_engn.etc.logging__info("view at /modify_rule")

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
        mod_rl_form.mean_and_body.data = rl.mean_and_body
        mod_rl_form.category_tag.data = rl.category_tag
        mod_rl_form.inference_and_speculation_condition.data = rl.inference_and_speculation_condition
        mod_rl_form.inference_and_speculation_result.data = rl.inference_and_speculation_result
        mod_rl_form.staff_name.data = rl.staff_name
        mod_rl_form.staff_kana_name.data = rl.staff_kana_name
        mod_rl_form.is_hidden.data = ("yes" if rl.is_hidden == True else "no")
        mod_rl_form.is_exclude.data = ("yes" if rl.is_exclude == True else "no")
        return render_template("modify_fact.html", form=mod_rl_form)

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
        if mod_rl_form.mean_and_body.data == "":
            flash("意味&内容が入力されていません.")
            return render_template("modify_rule.html", form=mod_rl_form, happen_error=True)
        if mod_rl_form.category_tag.data == "":
            flash("分類タグが入力されていません.")
            return render_template("modify_rule.html", form=mod_rl_form, happen_error=True)
        if mod_rl_form.inference_and_speculation_condition.data == "":
            flash("推論条件が入力されていません.")
            return render_template("modify_rule.html", form=mod_rl_form, happen_error=True)
        if mod_rl_form.inference_and_speculation_result.data == "":
            flash("推論結果が入力されていません.")
            return render_template("modify_rule.html", form=mod_rl_form, happen_error=True)
        if mod_rl_form.staff_name.data == "":
            flash("職員名が入力されていません.")
            return render_template("modify_word.html", form=mod_rl_form, happen_error=True)
        if mod_rl_form.staff_kana_name.data == "":
            flash("職員カナ名が入力されていません.")
            return render_template("modify_word.html", form=mod_rl_form, happen_error=True)
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
        crrnt_dttm = cr_engn.etc.retrieve_current_datetime_as_datetime_object("JST")
        rl.spell_and_header = escape(mod_rl_form.spell_and_header.data)
        rl.mean_and_body = escape(mod_rl_form.mean_and_body.data)
        rl.category_tag = escape(mod_rl_form.category_tag.data)
        rl.inference_and_speculation_condition = escape(mod_rl_form.inference_and_speculation_condition.data)
        rl.inference_and_speculation_result = escape(mod_rl_form.inference_and_speculation_result.data)
        rl.staff_name = escape(mod_rl_form.staff_name.data)
        rl.staff_kana_name = escape(mod_rl_form.staff_kana_name.data)
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
    rslt = cr_engn.etc.logging__info("view at /modify_reaction")

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
        mod_rctn_form.mean_and_body.data = rctn.mean_and_body
        mod_rctn_form.staff_psychology.data = rctn.staff_psychology
        mod_rctn_form.scene_and_background.data = rctn.scene_and_background
        mod_rctn_form.message_example_from_staff.data = rctn.staff_example_text_message
        mod_rctn_form.message_example_from_application.data = rctn.application_example_text_message
        mod_rctn_form.staff_name.data = rctn.staff_name
        mod_rctn_form.staff_kana_name.data = rctn.staff_kana_name
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
        if mod_rctn_form.mean_and_body.data == "":
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
        if mod_rctn_form.staff_name.data == "":
            flash("職員名が入力されていません.")
            return render_template("modify_word.html", form=mod_rctn_form, happen_error=True)
        if mod_rctn_form.staff_kana_name.data == "":
            flash("職員カナ名が入力されていません.")
            return render_template("modify_word.html", form=mod_rctn_form, happen_error=True)
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
        crrnt_dttm = cr_engn.etc.retrieve_current_datetime_as_datetime_object("JST")
        rctn.spell_and_header = escape(mod_rctn_form.spell_and_header.data)
        rctn.mean_and_body = escape(mod_rctn_form.mean_and_body.data)
        rctn.staff_psychology = escape(mod_rctn_form.staff_psychology.data)
        rctn.scene_and_background = escape(mod_rctn_form.scene_and_background.data)
        rctn.message_example_from_staff = escape(mod_rctn_form.message_example_from_staff.data)
        rctn.message_example_from_application = escape(mod_rctn_form.message_example_from_application.data)
        rctn.staff_name = escape(mod_rctn_form.staff_name.data)
        rctn.staff_kana_name = escape(mod_rctn_form.staff_kana_name.data)
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
    rslt = cr_engn.etc.logging__info("view at /modify_enter_or_exit")

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
        session["referrer-page"] = "view.modify_enter_or_exit"

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
        mod_entr_or_exit_form.enter_or_exit_at_second.data = entr_or_exit.enter_or_exit_at_second
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
            return render_template("modify_enter_or_exit.html", form=mod_entr_or_exit_form, happen_error=True)
        if mod_entr_or_exit_form.staff_kana_name.data == "":
            flash("職員カナ名が入力されていません.")
            return render_template("modify_enter_or_exit.html", form=mod_entr_or_exit_form, happen_error=True)
        if mod_entr_or_exit_form.reason.data == "":
            flash("入退理由が入力されていません.")
            return render_template("modify_enter_or_exit.html", form=mod_entr_or_exit_form, happen_error=True)
        if mod_entr_or_exit_form.enter_or_exit_at.data is None:
            flash("入退日時が入力されていません.")
            return render_template("modify_enter_or_exit.html", form=mod_entr_or_exit_form, happen_error=True)
        if mod_entr_or_exit_form.enter_or_exit_at_second.data is None:
            flash("入退日時-秒数が入力されていません.")
            return render_template("modify_enter_or_exit.html", form=mod_entr_or_exit_form, happen_error=True)
        if ((mod_entr_or_exit_form.enter_or_exit_at_second.data < 0) or (mod_entr_or_exit_form.enter_or_exit_at_second.data > 59)):
            flash("入退日時-秒数が有効な範囲を超えています.")
            return render_template("modify_enter_or_exit.html", form=mod_entr_or_exit_form, happen_error=True)
        if mod_entr_or_exit_form.is_hidden.data == "":
            flash("秘匿の是非が選択されていません.")
            return render_template("modify_enter_or_exit.html", form=mod_entr_or_exit_form, happen_error=True)
        if mod_entr_or_exit_form.is_exclude.data == "":
            flash("非処理の是非が選択されていません.")
            return render_template("modify_enter_or_exit.html", form=mod_entr_or_exit_form, happen_error=True)

        # 指定IDの入退レコードを取得し, その内容を上書きしてから, DBセッションを閉じる.
        entr_or_exit = (
        db_session.query(EnterOrExit).filter(EnterOrExit.id == int(session["hidden-modify-item-id"])).first()
        )
        crrnt_dttm = cr_engn.etc.retrieve_current_datetime_as_datetime_object("JST")
        if mod_entr_or_exit_form.enter_or_exit_at_second.data == "":
            crrnt_dttm_scnd = "00"
        elif ((int(mod_entr_or_exit_form.enter_or_exit_at_second.data) < 10) and
               (len(str(mod_entr_or_exit_form.enter_or_exit_at_second.data)) == 1)):
            crrnt_dttm_scnd = "0" + str(mod_entr_or_exit_form.enter_or_exit_at_second.data)
        else:
            crrnt_dttm_scnd = str(mod_entr_or_exit_form.enter_or_exit_at_second.data)
        entr_or_exit.staff_name = escape(mod_entr_or_exit_form.staff_name.data)
        entr_or_exit.staff_kana_name = escape(mod_entr_or_exit_form.staff_kana_name.data)
        entr_or_exit.reason = mod_entr_or_exit_form.reason.data
        entr_or_exit.enter_or_exit_at = cr_engn.etc.convert_datetime_object_to_string_for_timestamp(mod_entr_or_exit_form.enter_or_exit_at.data, True)
        entr_or_exit.enter_or_exit_at_second = crrnt_dttm_scnd
        entr_or_exit.updated_at = crrnt_dttm
        entr_or_exit.is_hidden = (True if mod_entr_or_exit_form.is_hidden.data == "yes" else False)
        entr_or_exit.is_exclude = (True if mod_entr_or_exit_form.is_exclude.data == "yes" else False)
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
    rslt = cr_engn.etc.logging__info("view at /modify_staff")

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
        print(stff.hashed_password)
        # フォームにレコードの内容を複写して, フォームと共にテンプレートを返す.
        mod_stff_form.name.data = stff.name
        mod_stff_form.kana_name.data = stff.kana_name
        # mod_stff_form.password.data = stff.hashed_password
        mod_stff_form.sex.data = stff.sex
        mod_stff_form.blood_type.data = stff.blood_type
        mod_stff_form.birth_date.data = stff.birth_date
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
        # if mod_stff_form.password.data == "":
        #     flash("パスワードが入力されていません.")
        #     return render_template("modify_staff.html", form=mod_stff_form, happen_error=True)
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
        if not cr_engn.reg.check_katakana_uppercase_in_ja(mod_stff_form.kana_name.data):
            flash("職員カナ名は, カタカナのみにしてください.")
            return render_template("modify_staff.html", form=mod_stff_form, happen_error=True)
        # if len(mod_stff_form.password.data) > consts.PASSWORD_LENGTH:
        #     flash("パスワードは, " + str(consts.PASSWORD_LENGTH) + "文字以内にしてください.")
        #     return render_template("modify_staff.html", form=mod_stff_form, happen_error=True)
        if ((" " in mod_stff_form.name.data) or ("　" in mod_stff_form.name.data)):
            flash("職員名の一部として, 半角スペースと全角スペースは使用できません.")
            return render_template("modify_staff.html", form=mod_stff_form, happen_error=True)
        if ((" " in mod_stff_form.kana_name.data) or ("　" in mod_stff_form.kana_name.data)):
            flash("職員カナ名の一部として, 半角スペースと全角スペースは使用できません.")
            return render_template("modify_staff.html", form=mod_stff_form, happen_error=True)
        # if " " in mod_stff_form.password.data:
        #     flash("パスワードの一部として, 半角スペースは使用できません.")
        #     return render_template("modify_staff.html", form=mod_stff_form, happen_error=True)

        drtn_in_dys__crit1 = cr_engn.etc.retrieve_timedelta_from_years(consts.STAFF_AGE_TOP)
        drtn_in_dys__crit2 = cr_engn.etc.retrieve_timedelta_from_years(consts.STAFF_AGE_BOTTOM)
        drtn_in_dys__brth_to_prsnt = cr_engn.etc.retrieve_timedelta_from_date_object(mod_stff_form.birth_date.data)

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
        crrnt_dttm = cr_engn.etc.retrieve_current_datetime_as_datetime_object("JST")
        stff.name = escape(mod_stff_form.name.data)
        stff.kana_name = escape(mod_stff_form.kana_name.data)
        # stff.hashed_password = generate_password_hash(mod_stff_form.password.data)
        stff.sex = mod_stff_form.sex.data
        stff.blood_type = mod_stff_form.blood_type.data
        stff.birth_date = mod_stff_form.birth_date.data
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
    rslt = cr_engn.etc.logging__info("view at /detail_word")

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
        dtl_wrd_form.mean_and_body.data = wrd.mean_and_body
        dtl_wrd_form.concept_and_notion.data = wrd.concept_and_notion
        dtl_wrd_form.theme_tag.data = wrd.theme_tag
        dtl_wrd_form.intent.data = wrd.intent
        dtl_wrd_form.sentiment.data = wrd.sentiment
        dtl_wrd_form.sentiment_support.data = wrd.sentiment_support
        dtl_wrd_form.strength.data = wrd.strength
        dtl_wrd_form.part_of_speech.data = wrd.part_of_speech
        dtl_wrd_form.first_character.data = wrd.first_character
        dtl_wrd_form.last_character.data = wrd.last_character
        dtl_wrd_form.characters_count.data = wrd.characters_count
        dtl_wrd_form.staff_name.data = wrd.staff_name
        dtl_wrd_form.staff_kana_name.data = wrd.staff_kana_name
        dtl_wrd_form.created_at.data = wrd.created_at
        dtl_wrd_form.updated_at.data = wrd.updated_at
        dtl_wrd_form.is_hidden.data = ("yes" if wrd.is_hidden == True else "no")
        dtl_wrd_form.is_exclude.data = ("yes" if wrd.is_exclude == True else "no")
        return render_template("detail_word.html", form=dtl_wrd_form)


# 「detail_theme」のためのビュー関数(=URLエンドポイント)を宣言・定義する.
@view.route("/detail_theme", methods=["GET"])
def detail_theme():
    dtl_thm_form = DetailThemeForm()

    # 該当のURLエンドポイントに入ったことをロギングする.
    rslt = cr_engn.etc.logging__info("view at /detail_theme")

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
        dtl_thm_form.mean_and_body.data = thm.mean_and_body
        dtl_thm_form.concept_and_notion = thm.concept_and_notion
        dtl_thm_form.category_tag.data = thm.category_tag
        dtl_thm_form.staff_name.data = thm.staff_name
        dtl_thm_form.staff_kana_name.data = thm.staff_kana_name
        dtl_thm_form.created_at.data = thm.created_at
        dtl_thm_form.updated_at.data = thm.updated_at
        dtl_thm_form.is_hidden.data = ("yes" if thm.is_hidden == True else "no")
        dtl_thm_form.is_exclude.data = ("yes" if thm.is_exclude == True else "no")
        return render_template("detail_theme.html", form=dtl_thm_form)


# 「detail_category」のためのビュー関数(=URLエンドポイント)を宣言・定義する.
@view.route("/detail_category", methods=["GET"])
def detail_category():
    dtl_ctgr_form = DetailCategoryForm()

    # 該当のURLエンドポイントに入ったことをロギングする.
    rslt = cr_engn.etc.logging__info("view at /detail_category")

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
        dtl_ctgr_form.mean_and_body.data = ctgr.mean_and_body
        dtl_ctgr_form.concept_and_notion = ctgr.concept_and_notion
        dtl_ctgr_form.parent_category_tag.data = ctgr.parent_category_tag
        dtl_ctgr_form.sibling_category_tag.data = ctgr.sibling_category_tag
        dtl_ctgr_form.child_category_tag.data = ctgr.child_category_tag
        dtl_ctgr_form.staff_name.data = ctgr.staff_name
        dtl_ctgr_form.staff_kana_name.data = ctgr.staff_kana_name
        dtl_ctgr_form.created_at.data = ctgr.created_at
        dtl_ctgr_form.updated_at.data = ctgr.updated_at
        dtl_ctgr_form.is_hidden.data = ("yes" if ctgr.is_hidden == True else "no")
        dtl_ctgr_form.is_exclude.data = ("yes" if ctgr.is_exclude == True else "no")
        return render_template("detail_category.html", form=dtl_ctgr_form)


# 「detail_fact」のためのビュー関数(=URLエンドポイント)を宣言・定義する.
@view.route("/detail_fact", methods=["GET"])
def detail_knowledge():
    dtl_fct_form = DetailFactForm()

    # 該当のURLエンドポイントに入ったことをロギングする.
    rslt = cr_engn.etc.logging__info("view at /detail_fact")

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

    # [show_facts][search_facts]ページを介さずに,
    # 不正アクセスされたら, 直前画面のページヘリダイレクトする.
    if "hidden-detail-item-id" not in session:
        return redirect(url_for("view.admin_dashboard"))

    if request.method == "GET":
        # セッションに現在ページの情報を設定して,
        # Flaskフォームと共にテンプレートを返す.
        session["referrer-page"] = "view.detail_fact"

        # 指定IDの事実レコードをDBから取得する.
        fct = db_session.query(Fact).filter(Fact.id == session["hidden-detail-item-id"]).first()
        db_session.close()

        # フォームにレコードの内容を複写して, フォームと共にテンプレートを返す.
        dtl_fct_form.id.data = fct.id
        dtl_fct_form.spell_and_header.data = fct.spell_and_header
        dtl_fct_form.mean_and_body.data = fct.mean_and_body
        dtl_fct_form.concept_and_notion.data = fct.concept_and_notion
        dtl_fct_form.category_tag.data = fct.category_tag
        dtl_fct_form.archived_image_file_path.data = fct.archived_image_file_path
        dtl_fct_form.archived_sound_file_path.data = fct.archived_sound_file_path
        dtl_fct_form.archived_video_file_path.data = fct.archived_video_file_path
        dtl_fct_form.staff_name.data = fct.staff_name
        dtl_fct_form.staff_kana_name.data = fct.staff_kana_name
        dtl_fct_form.created_at.data = fct.created_at
        dtl_fct_form.updated_at.data = fct.updated_at
        dtl_fct_form.is_hidden.data = ("yes" if fct.is_hidden == True else "no")
        dtl_fct_form.is_exclude.data = ("yes" if fct.is_exclude == True else "no")
        return render_template("detail_facts.html", form=dtl_fct_form,
                                archived_image_file_path=fct.archived_image_file_path,
                                archived_sound_file_path=fct.archived_sound_file_path,
                                archived_video_file_path=fct.archived_video_file_path
                               )


# 「detail_rule」のためのビュー関数(=URLエンドポイント)を宣言・定義する.
@view.route("/detail_rule", methods=["GET"])
def detail_rule():
    dtl_rl_form = DetailRuleForm()

    # 該当のURLエンドポイントに入ったことをロギングする.
    rslt = cr_engn.etc.logging__info("view at /detail_rule")

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
        dtl_rl_form.mean_and_body.data = rl.mean_and_body
        dtl_rl_form.concept_and_notion = rl.concept_and_notion
        dtl_rl_form.category_tag.data = rl.category_tag
        dtl_rl_form.inference_and_speculation_condition.data = rl.inference_and_speculation_condition
        dtl_rl_form.inference_and_speculation_result.data = rl.inference_and_speculation_result
        dtl_rl_form.staff_name.data = rl.staff_name
        dtl_rl_form.staff_kana_name.data = rl.staff_kana_name
        dtl_rl_form.created_at.data = rl.created_at
        dtl_rl_form.updated_at.data = rl.updated_at
        dtl_rl_form.is_hidden.data = ("yes" if rl.is_hidden == True else "no")
        dtl_rl_form.is_exclude.data = ("yes" if rl.is_exclude == True else "no")
        return render_template("detail_rule.html", form=dtl_rl_form)


# 「detail_reaction」のためのビュー関数(=URLエンドポイント)を宣言・定義する.
@view.route("/detail_reaction", methods=["GET"])
def detail_reaction():
    dtl_rl_form = DetailReactionForm()

    # 該当のURLエンドポイントに入ったことをロギングする.
    rslt = cr_engn.etc.logging__info("view at /detail_rule")

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
        dtl_rl_form.mean_and_body.data = rctn.mean_and_body
        dtl_rl_form.concept_and_notion.data = rctn.concept_and_notion
        dtl_rl_form.staff_psychology.data = rctn.staff_psychology
        dtl_rl_form.scene_and_background.data = rctn.scene_and_background
        dtl_rl_form.staff_example_text_message.data = rctn.staff_example_text_message
        dtl_rl_form.application_example_text_message.data = rctn.application_example_text_message
        dtl_rl_form.staff_name.data = rctn.staff_name
        dtl_rl_form.staff_kana_name.data = rctn.staff_kana_name
        dtl_rl_form.created_at.data = rctn.created_at
        dtl_rl_form.updated_at.data = rctn.updated_at
        dtl_rl_form.is_hidden.data = ("yes" if rctn.is_hidden == True else "no")
        dtl_rl_form.is_exclude.data = ("yes" if rctn.is_exclude == True else "no")
        return render_template("detail_reaction.html", form=dtl_rl_form)


# 「detail_generate」のためのビュー関数(=URLエンドポイント)を宣言・定義する.
@view.route("/detail_generate", methods=["GET"])
def detail_generate():
    dtl_gen_form = DetailGenerateForm()

    # 該当のURLエンドポイントに入ったことをロギングする.
    rslt = cr_engn.etc.logging__info("view at /detail_generate")

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
        dtl_gen_form.mean_and_body.data = gen.mean_and_body
        dtl_gen_form.generated_file_path.data = gen.generated_file_path
        dtl_gen_form.staff_name.data = gen.staff_name
        dtl_gen_form.staff_kana_name.data = gen.staff_kana_name
        dtl_gen_form.created_at.data = gen.created_at
        dtl_gen_form.updated_at.data = gen.updated_at
        dtl_gen_form.is_hidden.data = ("yes" if gen.is_hidden == True else "no")
        dtl_gen_form.is_exclude.data = ("yes" if gen.is_exclude == True else "no")
        return render_template("detail_generate.html", form=dtl_gen_form,
                               generated_file_path=gen.generated_file_path)


# 「detail_history」のためのビュー関数(=URLエンドポイント)を宣言・定義する.
@view.route("/detail_history", methods=["GET"])
def detail_history():
    dtl_hist_form = DetailHistoryForm()

    # 該当のURLエンドポイントに入ったことをロギングする.
    rslt = cr_engn.etc.logging__info("view at /detail_history")

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
        dtl_hist_form.staff_text_message.data = hist.staff_text_message
        dtl_hist_form.application_text_message.data = hist.application_text_message
        dtl_hist_form.staff_name.data = hist.staff_name
        dtl_hist_form.staff_kana_name.data = hist.staff_kana_name
        dtl_hist_form.created_at.data = hist.created_at
        dtl_hist_form.updated_at.data = hist.updated_at
        dtl_hist_form.is_hidden.data = ("yes" if hist.is_hidden == True else "no")
        dtl_hist_form.is_exclude.data = ("yes" if hist.is_exclude == True else "no")
        return render_template("detail_history.html", form=dtl_hist_form)


# 「detail_enter_or_exit」のためのビュー関数(=URLエンドポイント)を宣言・定義する.
@view.route("/detail_enter_or_exit", methods=["GET"])
def detail_enter_or_exit():
    dtl_entr_or_exit_form = DetailEnterOrExitForm()

    # 該当のURLエンドポイントに入ったことをロギングする.
    rslt = cr_engn.etc.logging__info("view at /detail_enter_or_exit")

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
        dtl_entr_or_exit_form.enter_or_exit_at_second.data = entr_or_exit.enter_or_exit_at_second
        dtl_entr_or_exit_form.created_at.data = entr_or_exit.created_at
        dtl_entr_or_exit_form.updated_at.data = entr_or_exit.updated_at
        dtl_entr_or_exit_form.is_hidden.data = ("yes" if entr_or_exit.is_hidden == True else "no")
        dtl_entr_or_exit_form.is_exclude.data = ("yes" if entr_or_exit.is_exclude == True else "no")
        return render_template("detail_enter_or_exit.html", form=dtl_entr_or_exit_form)


# 「detail_staff」のためのビュー関数(=URLエンドポイント)を宣言・定義する.
@view.route("/detail_staff", methods=["GET"])
def detail_staff():
    dtl_stff_form = DetailStaffForm()

    # 該当のURLエンドポイントに入ったことをロギングする.
    rslt = cr_engn.etc.logging__info("view at /detail_staff")

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
        dtl_stff_form.password.data = stff.hashed_password
        dtl_stff_form.sex.data = stff.sex
        dtl_stff_form.blood_type.data = stff.blood_type
        dtl_stff_form.birth_date.data = stff.birth_date
        dtl_stff_form.created_at.data = stff.created_at
        dtl_stff_form.updated_at.data = stff.updated_at
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
    rslt = cr_engn.etc.logging__info("view at /import_words")

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
                   #@ ここで, 語句情報を学習するための各種の高度な計算を行う.
                   cncpt_n_ntn = cr_engn.learn_word(escape(child.find("spell-and-header").text),
                                               escape(child.find("mean-and-body").text))
                   crrnt_dttm = cr_engn.etc.retrieve_current_datetime_as_datetime_object("JST")
                   db_session.add(Word(spell_and_header=escape(child.find("spell-and-header").text),
                                       mean_and_body=escape(child.find("mean-and-body").text),
                                       concept_and_notion=cncpt_n_ntn,
                                       theme_tag=escape(child.find("theme-tag").text),
                                       intent=child.find("intent").text,
                                       sentiment=child.find("sentiment").text,
                                       sentiment_support=child.find("sentiment-support").text,
                                       strength=child.find("strength").text,
                                       first_character=child.find("spell-and-header").text[0],
                                       last_character=child.find("spell-and-header").text[-1],
                                       characters_count=len(child.find("spell-and-header").text),
                                       staff_name=escape(child.find("staff-name").text),
                                       staff_kana_name=escape(child.find("staff-kana-name").text),
                                       created_at=(
                                       cr_engn.etc.convert_string_to_datetime_object_for_timestamp(cr_engn.etc.modify_style_for_datetime_string(child.find("created-at").text, True), True)
                                       ),
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
    rslt = cr_engn.etc.logging__info("view at /import_themes")

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
                   #@ ここで, 主題情報を学習するための各種の高度な計算を行う.
                   cncpt_n_ntn = cr_engn.learn_theme(escape(child.find("spell-and-header").text),
                                                escape(child.find("mean-and-body").text))
                   crrnt_dttm = cr_engn.etc.retrieve_current_datetime_as_datetime_object("JST")
                   db_session.add(Theme(spell_and_header=escape(child.find("spell-and-header").text),
                                        mean_and_body=escape(child.find("mean-and-body").text),
                                        concept_and_notion=cncpt_n_ntn,
                                        intent=child.find("intent").text,
                                        category_tag=escape(child.find("category-tags").text),
                                        staff_name=escape(child.find("staff-name").text),
                                        staff_kana_name=escape(child.find("staff-kana-name").text),
                                        created_at=(
                                        cr_engn.etc.convert_string_to_datetime_object_for_timestamp(cr_engn.etc.modify_style_for_datetime_string(child.find("created-at").text, True), True)
                                        ),
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
    rslt = cr_engn.etc.logging__info("view at /import_categories")

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
                   #@ ここで, 分類情報を学習するための各種の高度な計算を行う.
                   cncpt_n_ntn = cr_engn.learn_category(escape(child.find("spell-and-header").text),
                                                   escape(child.find("mean-and-body").text))
                   crrnt_dttm = cr_engn.etc.retrieve_current_datetime_as_datetime_object("JST")
                   db_session.add(Category(spell_and_header=escape(child.find("spell-and-header").text),
                                           mean_and_body=escape(child.find("mean-and-body").text),
                                           concept_and_notion=cncpt_n_ntn,
                                           parent_category_tag=escape(child.find("parent-category-tags").text),
                                           sibling_category_tag=escape(child.find("sibling-category-tags").text),
                                           child_category_tag=escape(child.find("child-category-tags").text),
                                           staff_name=escape(child.find("staff-name").text),
                                           staff_kana_name=escape(child.find("staff-kana-name").text),
                                           created_at=(
                                           cr_engn.etc.convert_string_to_datetime_object_for_timestamp(cr_engn.etc.modify_style_for_datetime_string(child.find("created-at").text, True), True)
                                           ),
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


# 「import_facts」のためのビュー関数(=URLエンドポイント)を宣言・定義する.
@view.route("/import_facts", methods=["GET", "POST"])
def import_facts():
    # 関数内で使用する変数・オブジェクトを宣言・定義する.
    sccss_cnt = 0
    fail_cnt = 0
    pass_cnt = 0
    imprt_fct_form = ImportFactForm()

    # 該当のURLエンドポイントに入ったことをロギングする.
    rslt = cr_engn.etc.logging__info("view at /import_facts")

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
        session["referrer-page"] = "view.import_facts"
        return render_template("import_facts.html", form=imprt_fct_form)

    if request.method == "POST":
        # 直前に, GETメソッドで該当ページを取得しているかを調べる.
        # 取得していなければ, 強制的に現在ページへリダイレクトする.
        if session["referrer-page"] != "view.import_facts":
            return redirect(url_for("view.import_facts"))

        # フォームの取消ボタンが押されたら, 直前画面のページヘリダイレクトする.
        if imprt_fct_form.cancel.data:
            return redirect(url_for("view.admin_dashboard"))

        # フォームと共に送信されたファイルを取得して, 名前を安全な形式に変更する.
        xml_fl = imprt_fct_form.imported_file.data
        fl_nm = secure_filename(xml_fl.filename)
        if fl_nm == "":
            flash("事実ファイルが選択されていません.")
            return render_template("import_facts.html", form=imprt_fct_form)

        # 事実ファイルを一旦, 一時領域に保存してから, その内容を読み取る.
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
                   #@ ここで, 事実情報を学習するための各種の高度な計算を行う.
                   cncpt_n_ntn = cr_engn.learn_fact(escape(child.find("spell-and-header").text),
                                               escape(child.find("mean-and-body").text))
                   crrnt_dttm = cr_engn.etc.retrieve_current_datetime_as_datetime_object("JST")
                   db_session.add(Fact(spell_and_header=escape(child.find("spell-and-header").text),
                                       mean_and_body=escape(child.find("mean-and-body").text),
                                       concept_and_notion=cncpt_n_ntn, 
                                       category_tag=escape(child.find("category-tags").text),
                                       archived_image_file_path=child.find("archived-image-file-path").text,
                                       archived_sound_file_path=child.find("archived-sound-file-path").text,
                                       archived_video_file_path=child.find("archived-video-file-path").text,
                                       staff_name=escape(child.find("staff-name").text),
                                       staff_kana_name=escape(child.find("staff-kana-name").text),
                                       created_at=(
                                       cr_engn.etc.convert_string_to_datetime_object_for_timestamp(cr_engn.etc.modify_style_for_datetime_string(child.find("created-at").text, True), True)
                                       ),
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
        flash("事実ファイルの取込を実行しました.")
        flash("成功数:" + str(sccss_cnt) + ", " + "失敗数:" + str(fail_cnt) + ", " + "棄却数:" + str(pass_cnt) + ", " + "総件数:" + str(sccss_cnt+fail_cnt+pass_cnt) + ";")
        return render_template("import_facts.html", form=imprt_fct_form)


# 「import_rules」のためのビュー関数(=URLエンドポイント)を宣言・定義する.
@view.route("/import_rules", methods=["GET", "POST"])
def import_rules():
    # 関数内で使用する変数・オブジェクトを宣言・定義する.
    sccss_cnt = 0
    fail_cnt = 0
    pass_cnt = 0
    imprt_rl_form = ImportRuleForm()

    # 該当のURLエンドポイントに入ったことをロギングする.
    rslt = cr_engn.etc.logging__info("view at /import_rules")

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
                   #@ ここで, 規則情報を学習するための各種の高度な計算を行う.
                   cncpt_n_ntn = cr_engn.learn_rule(escape(child.find("spell-and-header").text),
                                               escape(child.find("mean-and-body").text))
                   crrnt_dttm = cr_engn.etc.retrieve_current_datetime_as_datetime_object("JST")
                   db_session.add(Rule(spell_and_header=escape(child.find("spell-and-header").text),
                                       mean_and_body=escape(child.find("mean-and-body").text),
                                       concept_and_notion=cncpt_n_ntn,
                                       category_tag=escape(child.find("category-tags").text),
                                       inference_and_speculation_condition=escape(child.find("inference-and-speculation-condition").text),
                                       inference_and_speculation_result=escape(child.find("inference-and-speculation-result").text),
                                       staff_name=escape(child.find("staff-name").text),
                                       staff_kana_name=escape(child.find("staff-kana-name").text),
                                       created_at=(
                                       cr_engn.etc.convert_string_to_datetime_object_for_timestamp(cr_engn.etc.modify_style_for_datetime_string(child.find("created-at").text, True), True)
                                       ),
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
    rslt = cr_engn.etc.logging__info("view at /import_reactions")

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
                   #@ ここで, 反応情報を学習するための各種の高度な計算を行う.
                   cncpt_n_ntn = cr_engn.learn_reaction(escape(child.find("spell-and-header").text),
                                                   escape(child.find("mean-and-body").text))
                   crrnt_dttm = cr_engn.etc.retrieve_current_datetime_as_datetime_object("JST")
                   db_session.add(Reaction(spell_and_header=escape(child.find("spell-and-header").text),
                                           mean_and_body=escape(child.find("mean-and-body").text),
                                           concept_and_notion=cncpt_n_ntn,
                                           staff_psychology=escape(child.find("staff-psychology").text),
                                           scene_and_background=escape(child.find("scene-and-background").text),
                                           message_example_from_staff=escape(child.find("message-example-from-staff").text),
                                           message_example_from_application=escape(child.find("message-example-from-application").text),
                                           staff_name=escape(child.find("staff-name").text),
                                           staff_kana_name=escape(child.find("staff-kana-name").text),
                                           created_at=(
                                           cr_engn.etc.convert_string_to_datetime_object_for_timestamp(cr_engn.etc.modify_style_for_datetime_string(child.find("created-at").text, True), True)
                                           ),
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
    rslt = cr_engn.etc.logging__info("view at /import_generates")

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
                   crrnt_dttm = cr_engn.etc.retrieve_current_datetime_as_datetime_object("JST")
                   db_session.add(Generate(spell_and_header=escape(child.find("spell-and-header").text),
                                           mean_and_body=escape(child.find("mean-and-body").text),
                                           generated_file_path=child.find("generated-file-path").text,
                                           staff_name=escape(child.find("staff-name").text),
                                           staff_kana_name=escape(child.find("staff-kana-name").text),
                                           created_at=(
                                           cr_engn.etc.convert_string_to_datetime_object_for_timestamp(cr_engn.etc.modify_style_for_datetime_string(child.find("created-at").text, True), True)
                                           ),
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
    rslt = cr_engn.etc.logging__info("view at /import_enters_or_exits")

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
            if not cr_engn.etc.check_timestamp_by_display_style(rcd[3]):
                continue
            if not cr_engn.etc.check_timestamp_by_display_style(rcd[4]):
                continue
            if not cr_engn.etc.check_timestamp_by_display_style(rcd[5]):
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
            dttm1 = cr_engn.etc.convert_string_to_datetime_object_for_timestamp(cr_engn.etc.modify_style_for_datetime_string(rcd[3], True))
            dttm2 = cr_engn.etc.convert_string_to_datetime_object_for_timestamp(cr_engn.etc.modify_style_for_datetime_string(rcd[4], True))
            is_hddn = True if rcd[6] == "はい" else False
            is_excld = True if rcd[7] == "はい" else False
            crrnt_dttm3 = cr_engn.etc.retrieve_current_datetime_as_datetime_object("JST")
            db_session.add(EnterOrExit(staff_name=stff_nm,
                                       staff_kana_name=stff_kn_nm,
                                       reason=rsn,
                                       enter_or_exit_at=dttm1,
                                       created_at=dttm2,
                                       updated_at=crrnt_dttm3,
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
    rslt = cr_engn.etc.logging__info("view at /export_words")

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

        # ID昇順で, 非処理フラグの立っていない語句レコードをDBから取得する.
        wrds = db_session.query(Word).filter(Word.is_exclude == False).order_by(Word.id.asc()).all()
        db_session.close()

        # DBから取得した語句レコードの内容をXMLファイルに書き込むための準備をする.
        root = ET.Element("Word-Dictionary")
        for wrd in wrds:
            wrd_elm = ET.SubElement(root, "Word-Entry")
            ET.SubElement(wrd_elm, "spell-and-header").text = wrd.spell_and_header
            ET.SubElement(wrd_elm, "mean-and-body").text = wrd.mean_and_body
            ET.SubElement(wrd_elm, "theme-tag").text = wrd.theme_tag
            ET.SubElement(wrd_elm, "intent").text = wrd.intent
            ET.SubElement(wrd_elm, "sentiment").text = wrd.sentiment
            ET.SubElement(wrd_elm, "sentiment-support").text = wrd.sentiment_support
            ET.SubElement(wrd_elm, "strength").text = wrd.strength
            ET.SubElement(wrd_elm, "part-of-speech").text = wrd.part_of_speech
            ET.SubElement(wrd_elm, "staff-name").text = wrd.staff_name
            ET.SubElement(wrd_elm, "staff-kana-name").text = wrd.staff_kana_name
            ET.SubElement(wrd_elm, "created-at").text = cr_engn.etc.modify_style_for_datetime_string(cr_engn.etc.convert_datetime_object_to_string_for_timestamp(wrd.created_at), False)
            ET.SubElement(wrd_elm, "updated_at").text = cr_engn.etc.modify_style_for_datetime_string(cr_engn.etc.convert_datetime_object_to_string_for_timestamp(wrd.updated_at), False)
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
    rslt = cr_engn.etc.logging__info("view at /export_themes")

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

        # ID昇順で, 非処理フラグの立っていない主題レコードをDBから取得する.
        thms = db_session.query(Theme).filter(Theme.is_exclude == False).order_by(Theme.id.asc()).all()
        db_session.close()

        # DBから取得した主題レコードの内容をXMLファイルに書き込むための準備をする.
        root = ET.Element("Theme-Dictionary")
        for thm in thms:
            thm_elm = ET.SubElement(root, "Theme-Entry")
            ET.SubElement(thm_elm, "spell-and-header").text = thm.spell_and_header
            ET.SubElement(thm_elm, "mean-and-body").text = thm.mean_and_body
            ET.SubElement(thm_elm, "category-tags").text = thm.category_tag
            ET.SubElement(thm_elm, "staff-name").text = thm.staff_name
            ET.SubElement(thm_elm, "staff-kana-name").text = thm.staff_kana_name
            ET.SubElement(thm_elm, "created-at").text = cr_engn.etc.modify_style_for_datetime_string(cr_engn.etc.convert_datetime_object_to_string_for_timestamp(thm.created_at), False)
            ET.SubElement(thm_elm, "updated_at").text = cr_engn.etc.modify_style_for_datetime_string(cr_engn.etc.convert_datetime_object_to_string_for_timestamp(thm.updated_at), False)
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
    rslt = cr_engn.etc.logging__info("view at /export_categories")

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

        # ID昇順で, 非処理フラグの立っていない分類レコードをDBから取得する.
        ctgrs = db_session.query(Category).filter(Category.is_exclude == False).order_by(Category.id.asc()).all()
        db_session.close()

        # DBから取得した分類レコードの内容をXMLファイルに書き込むための準備をする.
        root = ET.Element("Category-Dictionary")
        for ctgr in ctgrs:
            ctgr_elm = ET.SubElement(root, "Category-Entry")
            ET.SubElement(ctgr_elm, "spell-and-header").text = ctgr.spell_and_header
            ET.SubElement(ctgr_elm, "mean-and-body").text = ctgr.mean_and_body
            ET.SubElement(ctgr_elm, "parent-category-tags").text = ctgr.parent_category_tag
            ET.SubElement(ctgr_elm, "sibling-category-tags").text = ctgr.sibling_category_tag
            ET.SubElement(ctgr_elm, "child-category-tags").text = ctgr.child_category_tag
            ET.SubElement(ctgr_elm, "staff-name").text = ctgr.staff_name
            ET.SubElement(ctgr_elm, "staff-kana-name").text = ctgr.staff_kana_name
            ET.SubElement(ctgr_elm, "created-at").text = cr_engn.etc.modify_style_for_datetime_string(cr_engn.etc.convert_datetime_object_to_string_for_timestamp(ctgr.created_at), False)
            ET.SubElement(ctgr_elm, "updated_at").text = cr_engn.etc.modify_style_for_datetime_string(cr_engn.etc.convert_datetime_object_to_string_for_timestamp(ctgr.updated_at), False)
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


# 「export_facts」のためのビュー関数(=URLエンドポイント)を宣言・定義する.
@view.route("/export_facts", methods=["GET", "POST"])
def export_facts():
    # 関数内で使用する変数・オブジェクトを宣言・定義する.
    exprt_fct_form = ExportFactForm()

    # 該当のURLエンドポイントに入ったことをロギングする.
    rslt = cr_engn.etc.logging__info("view at /export_facts")

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
        session["referrer-page"] = "view.export_facts"
        return render_template("export_facts.html", form=exprt_fct_form)

    if request.method == "POST":
        # 直前に, GETメソッドで該当ページを取得しているかを調べる.
        # 取得していなければ, 強制的に現在ページへリダイレクトする.
        if session["referrer-page"] != "view.export_facts":
            return redirect(url_for("view.export_facts"))

        # フォームの取消ボタンが押されたら, 直前画面のページヘリダイレクトする.
        if exprt_fct_form.cancel.data:
            return redirect(url_for("view.admin_dashboard"))

        # ID昇順で, 非処理フラグの立っていない事実レコードをDBから取得する.
        fcts = db_session.query(Fact).filter(Fact.is_exclude == False).order_by(Fact.id.asc()).all()
        db_session.close()

        # DBから取得した事実レコードの内容をXMLファイルに書き込むための準備をする.
        root = ET.Element("fact-Dictionary")
        for fct in fcts:
            fct_elm = ET.SubElement(root, "fact-Entry")
            ET.SubElement(fct_elm, "spell-and-header").text = fct.spell_and_header
            ET.SubElement(fct_elm, "mean-and-body").text = fct.mean_and_body
            ET.SubElement(fct_elm, "category-tags").text = fct.category_tag
            ET.SubElement(fct_elm, "archived-image-file-path").text = fct.archived_image_file_path
            ET.SubElement(fct_elm, "archived-sound-file-path").text = fct.archived_sound_file_path
            ET.SubElement(fct_elm, "archived-video-file-path").text = fct.archived_video_file_path
            ET.SubElement(fct_elm, "staff-name").text = fct.staff_name
            ET.SubElement(fct_elm, "staff-kana-name").text = fct.staff_kana_name
            ET.SubElement(fct_elm, "created-at").text = cr_engn.etc.modify_style_for_datetime_string(cr_engn.etc.convert_datetime_object_to_string_for_timestamp(fct.created_at), False)
            ET.SubElement(fct_elm, "updated_at").text = cr_engn.etc.modify_style_for_datetime_string(cr_engn.etc.convert_datetime_object_to_string_for_timestamp(fct.updated_at), False)
            ET.SubElement(fct_elm, "is-hidden").text = "はい" if fct.is_hidden == "yes" else "いいえ"
            ET.SubElement(fct_elm, "is-exclude").text = "いいえ"

        # XML文書内容を読み易いように整形する.
        xml_txt = MD.parseString(ET.tostring(root, "utf-8")).toprettyxml(indent="   ")

        # 書出し先ファイルが既に存在すれば, それを削除する.
        if os.path.exists(consts.FACT_EXPORT_PATH):
            os.remove(consts.FACT_EXPORT_PATH)

        # 書出し先ファイルを新規作成して, 先のXML文書内容を書き込んで閉じる. 
        with open(consts.FACT_EXPORT_PATH, 'x', encoding='UTF-8') as xml_fl:
             xml_fl.write(xml_txt)

        # 書出し先ファイルをクライアントへ送信する. 
        return send_file(consts.FACT_EXPORT_PATH, as_attachment=True)


# 「export_rules」のためのビュー関数(=URLエンドポイント)を宣言・定義する.
@view.route("/export_rules", methods=["GET", "POST"])
def export_rules():
    # 関数内で使用する変数・オブジェクトを宣言・定義する.
    exprt_rl_form = ExportRuleForm()

    # 該当のURLエンドポイントに入ったことをロギングする.
    rslt = cr_engn.etc.logging__info("view at /export_rules")

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

        # ID昇順で, 非処理フラグの立っていない規則レコードをDBから取得する.
        rls = db_session.query(Rule).filter(Rule.is_exclude == False).order_by(Rule.id.asc()).all()
        db_session.close()

        # DBから取得した規則レコードの内容をXMLファイルに書き込むための準備をする.
        root = ET.Element("Rule-Dictionary")
        for rl in rls:
            rl_elm = ET.SubElement(root, "Rule-Entry")
            ET.SubElement(rl_elm, "spell-and-header").text = rl.spell_and_header
            ET.SubElement(rl_elm, "mean-and-body").text = rl.mean_and_body
            ET.SubElement(rl_elm, "category-tags").text = rl.category_tag
            ET.SubElement(rl_elm, "inference-condition").text = rl.inference_and_speculation_condition
            ET.SubElement(rl_elm, "inference-result").text = rl.inference_and_speculation_result
            ET.SubElement(rl_elm, "staff-name").text = rl.staff_name
            ET.SubElement(rl_elm, "staff-kana-name").text = rl.staff_kana_name
            ET.SubElement(rl_elm, "created-at").text = cr_engn.etc.modify_style_for_datetime_string(cr_engn.etc.convert_datetime_object_to_string_for_timestamp(rl.created_at), False)
            ET.SubElement(rl_elm, "updated_at").text = cr_engn.etc.modify_style_for_datetime_string(cr_engn.etc.convert_datetime_object_to_string_for_timestamp(rl.updated_at), False)
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
    rslt = cr_engn.etc.logging__info("view at /export_reactions")

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

        # ID昇順で, 非処理フラグの立っていない反応レコードをDBから取得する.
        rctns = db_session.query(Reaction).filter(Reaction.is_exclude == False).order_by(Reaction.id.asc()).all()
        db_session.close()

        # DBから取得した反応レコードの内容をXMLファイルに書き込むための準備をする.
        root = ET.Element("Reaction-Dictionary")
        for rctn in rctns:
            rctn_elm = ET.SubElement(root, "Reaction-Entry")
            ET.SubElement(rctn_elm, "spell-and-header").text = rctn.spell_and_header
            ET.SubElement(rctn_elm, "mean-and-body").text = rctn.mean_and_body
            ET.SubElement(rctn_elm, "staff-psychology").text = rctn.staff_psychology
            ET.SubElement(rctn_elm, "scene-and-background").text = rctn.scene_and_background
            ET.SubElement(rctn_elm, "message-example-from-staff").text = rctn.message_example_from_staff
            ET.SubElement(rctn_elm, "message-example-from-application").text = rctn.message_example_from_application
            ET.SubElement(rctn_elm, "staff-name").text = rctn.staff_name
            ET.SubElement(rctn_elm, "staff-kana-name").text = rctn.staff_kana_name
            ET.SubElement(rctn_elm, "created-at").text = cr_engn.etc.modify_style_for_datetime_string(cr_engn.etc.convert_datetime_object_to_string_for_timestamp(rctn.created_at), False)
            ET.SubElement(rctn_elm, "updated_at").text = cr_engn.etc.modify_style_for_datetime_string(cr_engn.etc.convert_datetime_object_to_string_for_timestamp(rctn.updated_at), False)
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
    rslt = cr_engn.etc.logging__info("view at /export_words")

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

        # ID昇順で, 非処理フラグの立っていない生成レコードをDBから取得する.
        gens = db_session.query(Generate).filter(Generate.is_exclude == False).order_by(Generate.id.asc()).all()
        db_session.close()

        # DBから取得した生成レコードの内容をXMLファイルに書き込むための準備をする.
        root = ET.Element("Generate-Dictionary")
        for gen in gens:
            gen_elm = ET.SubElement(root, "Generate-Entry")
            ET.SubElement(gen_elm, "spell-and-header").text = gen.spell_and_header
            ET.SubElement(gen_elm, "mean-and-body").text = gen.mean_and_body
            ET.SubElement(gen_elm, "generated-file-path").text = gen.generated_file_path
            ET.SubElement(gen_elm, "staff-name").text = gen.staff_name
            ET.SubElement(gen_elm, "staff-kana-name").text = gen.staff_kana_name
            ET.SubElement(gen_elm, "created-at").text = cr_engn.etc.modify_style_for_datetime_string(cr_engn.etc.convert_datetime_object_to_string_for_timestamp(gen.created_at), False)
            ET.SubElement(gen_elm, "updated_at").text = cr_engn.etc.modify_style_for_datetime_string(cr_engn.etc.convert_datetime_object_to_string_for_timestamp(gen.updated_at), False)
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
    rslt = cr_engn.etc.logging__info("view at /export_words")

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

        # ID昇順で, 非処理フラグの立っていない履歴レコードをDBから取得する.
        hists = db_session.query(History).filter(History.is_exclude == False).order_by(History.id.asc()).all()
        db_session.close()

        # DBから取得した履歴レコードの内容をXMLファイルに書き込むための準備をする.
        root = ET.Element("History-Dictionary")
        for hist in hists:
            hist_elm = ET.SubElement(root, "History-Entry")
            ET.SubElement(hist_elm, "first-character").text = hist.staff_text_message
            ET.SubElement(hist_elm, "characters-count").text = hist.application_text_message
            ET.SubElement(hist_elm, "staff-name").text = hist.staff_name
            ET.SubElement(hist_elm, "staff-kana-name").text = hist.staff_kana_name
            ET.SubElement(hist_elm, "created-at").text = cr_engn.etc.modify_style_for_datetime_string(cr_engn.etc.convert_datetime_object_to_string_for_timestamp(hist.created_at), False)
            ET.SubElement(hist_elm, "updated_at").text = cr_engn.etc.modify_style_for_datetime_string(cr_engn.etc.convert_datetime_object_to_string_for_timestamp(hist.updated_at), False)
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
    rslt = cr_engn.etc.logging__info("view at /export_enters_or_exits")

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

        # ID昇順で, 非処理フラグの立っていない入退レコードをDBから取得する.
        ents_or_exts = db_session.query(EnterOrExit).filter(EnterOrExit.is_exclude == False).order_by(EnterOrExit.id.asc()).all()
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
            if str(cr_engn.etc.convert_datetime_object_to_string_for_timestamp(ent_or_ext.enter_or_exit_at)).split("T")[1].split(":")[2] == "00":
                dt_tmp = str(cr_engn.etc.convert_datetime_object_to_string_for_timestamp(ent_or_ext.enter_or_exit_at)).split("T")[0] + " "
                tm_tmp = (
                str(cr_engn.etc.convert_datetime_object_to_string_for_timestamp(ent_or_ext.enter_or_exit_at)).split("T")[1].split(":")[0] + ":" +
                str(cr_engn.etc.convert_datetime_object_to_string_for_timestamp(ent_or_ext.enter_or_exit_at)).split("T")[1].split(":")[1] + ":" +
                str(ent_or_ext.enter_or_exit_at_second)
                )
                dttm1 = cr_engn.etc.modify_style_for_datetime_string(dt_tmp + tm_tmp, False)
            else:
                dttm1 = cr_engn.etc.modify_style_for_datetime_string(cr_engn.etc.convert_datetime_object_to_string_for_timestamp(ent_or_ext.enter_or_exit_at), False)
            dttm2 = cr_engn.etc.modify_style_for_datetime_string(cr_engn.etc.convert_datetime_object_to_string_for_timestamp(ent_or_ext.created_at), False)
            dttm3 = cr_engn.etc.modify_style_for_datetime_string(cr_engn.etc.convert_datetime_object_to_string_for_timestamp(ent_or_ext.updated_at), False)
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
    rslt = cr_engn.etc.logging__info("view at /retrieve_generate")

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
        if not cr_engn.etc.check_exist_file(gen.generated_file_path):
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
    rslt = cr_engn.etc.logging__info("view at /reset_database")

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
        return render_template("reset_databacr_engn.html", form=rst_db_form)

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
            rst_db_form.facts.data = False
            rst_db_form.rules.data = False
            rst_db_form.reactions.data = False
            rst_db_form.generates.data = False
            rst_db_form.histories.data = False
            rst_db_form.enters_or_exits.data = False
            rst_db_form.staffs.data = False
            return render_template("reset_databacr_engn.html", form=rst_db_form)

        # フォームのチェックボックスに全くチェックが入っていない場合の処理をする.
        if (not rst_db_form.words.data and
            not rst_db_form.themes.data and
            not rst_db_form.categories.data and
            not rst_db_form.facts.data and
            not rst_db_form.rules.data and
            not rst_db_form.reactions.data and
            not rst_db_form.generates.data and
            not rst_db_form.histories.data and
            not rst_db_form.enters_or_exits.data and
            not rst_db_form.staffs.data):
            flash("DBをリセットしませんでした.")
            return render_template("reset_databacr_engn.html", form=rst_db_form)

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
        if rst_db_form.facts.data:
            db_session.query(Fact).delete()
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
        rst_db_form.facts.data = False
        rst_db_form.rules.data = False
        rst_db_form.reactions.data = False
        rst_db_form.generates.data = False
        rst_db_form.histories.data = False
        rst_db_form.enters_or_exits.data = False
        rst_db_form.staffs.data = False
        flash("DBをリセットしました.")
        return render_template("reset_databacr_engn.html", form=rst_db_form)


# 「environment_settings」のためのビュー関数(=URLエンドポイント)を宣言・定義する.
@view.route("/environment_settings", methods=["GET", "POST"])
def environment_settings():
    # 関数内で使用する変数・オブジェクトを宣言・定義する.
    config = configparser.ConfigParser()
    env_sttng_form = EnvironmentSettingForm()

    # 該当のURLエンドポイントに入ったことをロギングする.
    rslt = cr_engn.etc.logging__info("view at /environment_settings")

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
        session["referrer-page"] = "view.environment_settings"

        # もしも, 設定ファイルが存在しなければ, すべての項目がデフォルト値のファイルを作成する.
        if not os.path.exists(consts.ENVIRONMENT_SETTING_PATH):
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
            with open(consts.ENVIRONMENT_SETTING_PATH, "w") as configfile:
                 config.write(configfile)

        # 設定ファイルの内容をflaskフォームに読み込んで, フォームと共にテンプレートを返す.
        # ※各設定項目が消失していた場合, デフォルト値で各項目を復元する.
        config.read(consts.ENVIRONMENT_SETTING_PATH, encoding="utf-8")
        env_sttng_form.short_term_memory_size.data = config.get("memory-size", "short-term-memory-size", fallback=consts.SHORT_TERM_MEMORY_SIZE_DEFAULT)
        env_sttng_form.long_term_memory_size.data = config.get("memory-size", "long-term-memory-size", fallback=consts.LONG_TERM_MEMORY_SIZE_DEFAULT)
        env_sttng_form.learn_depth.data = config.get("cpu-or-gpu-power", "learn-depth", fallback=consts.LEARN_DEPTH_DEFAULT)
        env_sttng_form.inference_and_speculation_depth.data = config.get("cpu-or-gpu-power", "inference-and-speculation-depth", fallback=consts.INFERENCE_AND_SPECULATION_DEPTH_DEFAULT)
        env_sttng_form.in_memorize.data = config.getboolean("faster-processing", "in-memorize", fallback=consts.IN_MEMORIZE_DEFAULT)
        env_sttng_form.dictionary_entries_integration.data = config.getboolean("faster-processing", "dictionary-entries-integration", fallback=consts.DICTIONARY_ENTRIES_INETEGRATION_DEFAULT)
        env_sttng_form.global_Information_sharing.data = config.getboolean("advanced", "global-Information-sharing", fallback=consts.GLOBAL_INFORMATION_SHARING_DEFAULT)
        env_sttng_form.background_processing.data = config.getboolean("advanced", "background-processing", fallback=consts.BACKGROUND_PROCESSING_DEFAULT)
        env_sttng_form.policy_based_decisions.data = config.getboolean("others", "policy-based-decisions", fallback=consts.POLICY_BASED_DECISIONS_DEFAULT)
        env_sttng_form.personalized_conversations.data = config.getboolean("others", "personalized-conversations", fallback=consts.PERSONALIZED_CONVERSATIONS_DEFAULT)
        return render_template("environment_settings.html", form=env_sttng_form)

    if request.method == "POST":
        # 直前に, GETメソッドで該当ページを取得しているかを調べる.
        # 取得していなければ, 強制的に現在ページへリダイレクトする.
        if session["referrer-page"] != "view.environment_settings":
            return redirect(url_for("view.environment_settings"))

        # フォームの取消ボタンが押下されたら, 現在の設定内容を読み込んだフォームと共にテンプレートを返す.
        # ※各設定項目が消失していた場合, デフォルト値で各項目を復元する.
        if env_sttng_form.cancel.data == True:
            config.read(consts.ENVIRONMENT_SETTING_PATH, encoding="utf-8")
            env_sttng_form.short_term_memory_size.data = config.get("memory-size", "short-term-memory-size", fallback=consts.SHORT_TERM_MEMORY_SIZE_DEFAULT)
            env_sttng_form.long_term_memory_size.data = config.get("memory-size", "long-term-memory-size", fallback=consts.LONG_TERM_MEMORY_SIZE_DEFAULT)
            env_sttng_form.learn_depth.data = config.get("cpu-or-gpu-power", "learn-depth", fallback=consts.LEARN_DEPTH_DEFAULT)
            env_sttng_form.inference_and_speculation_depth.data = config.get("cpu-or-gpu-power", "inference-and-speculation-depth", fallback=consts.INFERENCE_AND_SPECULATION_DEPTH_DEFAULT)
            env_sttng_form.in_memorize.data = config.getboolean("faster-processing", "in-memorize", fallback=consts.IN_MEMORIZE_DEFAULT)
            env_sttng_form.dictionary_entries_integration.data = config.getboolean("faster-processing", "dictionary-entries-integration", fallback=consts.DICTIONARY_ENTRIES_INETEGRATION_DEFAULT)
            env_sttng_form.global_Information_sharing.data = config.getboolean("advanced", "global-Information-sharing", fallback=consts.GLOBAL_INFORMATION_SHARING_DEFAULT)
            env_sttng_form.background_processing.data = config.getboolean("advanced", "background-processing", fallback=consts.BACKGROUND_PROCESSING_DEFAULT)
            env_sttng_form.policy_based_decisions.data = config.getboolean("others", "policy-based-decisions", fallback=consts.POLICY_BASED_DECISIONS_DEFAULT)
            env_sttng_form.personalized_conversations.data = config.getboolean("others", "personalized-conversations", fallback=consts.PERSONALIZED_CONVERSATIONS_DEFAULT)
            return render_template("environment_settings.html", form=env_sttng_form)

        # flaskフォームに入力・記憶されている内容をバリデーションする.
        # 基準を満たさない場合は, 元のフォームと共にテンプレートを返す.
        if ((int(env_sttng_form.short_term_memory_size.data) < consts.SHORT_TERM_MEMORY_SIZE_BOTTOM) or (int(env_sttng_form.short_term_memory_size.data) > consts.SHORT_TERM_MEMORY_SIZE_TOP)):
            flash("短期記憶の値が無効です, " + "[" + str(consts.SHORT_TERM_MEMORY_SIZE_BOTTOM) + "~" + str(consts.SHORT_TERM_MEMORY_SIZE_TOP) + "]" + "の範囲内で指定してください.")
            return render_template("environment_settings.html", form=env_sttng_form, happen_error=True)
        if ((int(env_sttng_form.long_term_memory_size.data) < consts.LONG_TERM_MEMORY_SIZE_BOTTOM) or (int(env_sttng_form.long_term_memory_size.data) > consts.LONG_TERM_MEMORY_SIZE_TOP)):
            flash("長期記憶の値が無効です, " + "[" + str(consts.LONG_TERM_MEMORY_SIZE_BOTTOM) + "~" + str(consts.LONG_TERM_MEMORY_SIZE_TOP) + "]" + "の範囲内で指定してください.")
            return render_template("environment_settings.html", form=env_sttng_form, happen_error=True)
        if ((int(env_sttng_form.learn_depth.data) < consts.LEARN_DEPTH_BOTTOM) or (int(env_sttng_form.learn_depth.data) > consts.LEARN_DEPTH_TOP)):
            flash("学習の深さの値が無効です, " + "[" + str(consts.LEARN_DEPTH_BOTTOM) + "~" + str(consts.LEARN_DEPTH_TOP) + "]" + "の範囲内で指定してください.")
            return render_template("environment_settings.html", form=env_sttng_form, happen_error=True)
        if ((int(env_sttng_form.inference_and_speculation_depth.data) < consts.INFERENCE_AND_SPECULATION_DEPTH_BOTTOM) or (int(env_sttng_form.inference_and_speculation_depth.data) > consts.INFERENCE_AND_SPECULATION_DEPTH_TOP)):
            flash("推論の深さの値が無効です, " + "[" + str(consts.INFERENCE_AND_SPECULATION_DEPTH_BOTTOM) + "~" + str(consts.INFERENCE_AND_SPECULATION_DEPTH_TOP) + "]" + "の範囲内で指定してください.")
            return render_template("environment_settings.html", form=env_sttng_form, happen_error=True)

        # flaskフォームの内容を読み込んで, 設定ファイルを上書きする.
        config.read(consts.ENVIRONMENT_SETTING_PATH, encoding="utf-8")
        config.set("memory-size", "short-term-memory-size", str(env_sttng_form.short_term_memory_size.data))
        config.set("memory-size", "long-term-memory-size", str(env_sttng_form.long_term_memory_size.data))
        config.set("cpu-or-gpu-power", "learn-depth", str(env_sttng_form.learn_depth.data))
        config.set("cpu-or-gpu-power", "inference-and-speculation-depth", str(env_sttng_form.inference_and_speculation_depth.data))
        config.set("faster-processing", "in-memorize", str(env_sttng_form.in_memorize.data))
        config.set("faster-processing", "dictionary-entries-integration", str(env_sttng_form.dictionary_entries_integration.data))
        config.set("advanced", "global-Information-sharing", str(env_sttng_form.global_Information_sharing.data))
        config.set("advanced", "background-processing", str(env_sttng_form.background_processing.data))
        config.set("others", "policy-based-decisions", str(env_sttng_form.policy_based_decisions.data))
        config.set("others", "personalized-conversations", str(env_sttng_form.personalized_conversations.data))
        with open(consts.ENVIRONMENT_SETTING_PATH, 'w') as configfile:
             config.write(configfile)

        # 完了メッセージを設定してテンプレートを返す.
        flash("環境設定値を上書きしました.")
        return render_template("environment_settings.html", form=env_sttng_form)


# 「security_settings」のためのビュー関数(=URLエンドポイント)を宣言・定義する.
@view.route("/security_settings", methods=["GET", "POST"])
def security_settings():
    # 関数内で使用する変数・オブジェクトを宣言・定義する.
    config = configparser.ConfigParser()
    sec_sttng_form = SecuritySettingForm()

    # 該当のURLエンドポイントに入ったことをロギングする.
    rslt = cr_engn.etc.logging__info("view at /security_settings")

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
        session["referrer-page"] = "view.security_settings"

        # もしも, 設定ファイルが存在しなければ, すべての項目がデフォルト値のファイルを作成する.
        if not os.path.exists(consts.SECURITY_SETTING_PATH):
            config["security"] = {"hashed-password" : generate_password_hash(consts.ADMIN_INITIAL_PASSWORD)}
            with open(consts.SECURITY_SETTING_PATH, "w") as configfile:
                 config.write(configfile)

        # 設定ファイルの内容をflaskフォームに読み込んで, フォームと共にテンプレートを返す.
        # ※各設定項目が消失していた場合, デフォルト値で各項目を復元する.
        config.read(consts.SECURITY_SETTING_PATH, encoding="utf-8")
        sec_sttng_form.new_password.data = config.get("security", "hashed-password", fallback=generate_password_hash(consts.ADMIN_INITIAL_PASSWORD))
        return render_template("security_settings.html", form=sec_sttng_form)

    if request.method == "POST":
        # 直前に, GETメソッドで該当ページを取得しているかを調べる.
        # 取得していなければ, 強制的に現在ページへリダイレクトする.
        if session["referrer-page"] != "view.security_settings":
            return redirect(url_for("view.security_settings"))

        # フォームの取消ボタンが押下されたら, 空のフォームと共にテンプレートを返す.
        if sec_sttng_form.cancel.data:
            sec_sttng_form.new_password.data = ""
            return render_template("security_settings.html", form=sec_sttng_form)

        # flaskフォームに入力・記憶されている内容をバリデーションする.
        # 基準を満たさない場合は, 元のフォームと共にテンプレートを返す.
        if sec_sttng_form.new_password.data == "":
            flash("パスワードが入力されていません.")
            return render_template("security_settings.html", form=sec_sttng_form, happen_error=True)
        if sec_sttng_form.confirm_password.data == "":
            flash("パスワード(確認)が入力されていません.")
            return render_template("security_settings.html", form=sec_sttng_form, happen_error=True)
        if len(sec_sttng_form.new_password.data) > consts.PASSWORD_LENGTH:
            flash("パスワードは, " + str(consts.PASSWORD_LENGTH) + "文字以内にしてください.")
            return render_template("security_settings.html", form=sec_sttng_form, happen_error=True)
        if len(sec_sttng_form.confirm_password.data) > consts.PASSWORD_LENGTH:
            flash("パスワード(確認)は, " + str(consts.PASSWORD_LENGTH) + "文字以内にしてください.")
            return render_template("security_settings.html", form=sec_sttng_form, happen_error=True)
        if " " in sec_sttng_form.new_password.data:
            flash("パスワードの一部として, 半角スペースは使用できません.")
            return render_template("security_settings.html", form=sec_sttng_form, happen_error=True)
        if " " in sec_sttng_form.confirm_password.data:
            flash("パスワード(確認)の一部として, 半角スペースは使用できません.")
            return render_template("security_settings.html", form=sec_sttng_form, happen_error=True)
        if sec_sttng_form.new_password.data != sec_sttng_form.confirm_password.data:
            flash("二つのパスワードが一致しません, 再度入力してください.")
            return render_template("security_settings.html", form=sec_sttng_form, happen_error=True)

        # flaskフォームの内容を読み込んで, 設定ファイルを上書きする.
        config.read(consts.SECURITY_SETTING_PATH, encoding="utf-8")
        config.set("security", "hashed-password", generate_password_hash(sec_sttng_form.new_password.data))
        with open(consts.SECURITY_SETTING_PATH, 'w') as configfile:
             config.write(configfile)

        # 完了メッセージを設定してテンプレートを返す.
        flash("機密設定値を上書きしました.")
        return render_template("security_settings.html", form=sec_sttng_form)


# エラー処理のためのカスタム関数を宣言・定義する.
# ※指定URLにクエリパラメータが含まれている場合は400番エラーを返す.
# ※この関数は, 都度, リクエストの直前に呼び出される.
@view.before_request
def check_query_parameters():
    if request.args:
        raise NotFound