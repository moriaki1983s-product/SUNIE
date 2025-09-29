# coding: utf-8




# 既成のモジュールをインポートする.
import os
import sys




# 管理者用初期パスワードを宣言・定義する.
ADMIN_INITIAL_PASSWORD = "secret"

# パスワードの誤入力を許容する数を宣言・定義する.
APP_LOCKOUT_NUMBER = 3

# セッションの持続時間(=分数)を宣言・定義する.
SESSION_TIME = 60

# 職員の最大数を宣言・定義する.
STAFF_NUMBER = 100

# 職員の有資格年齢範囲の上限を宣言・定義する.
STAFF_AGE_TOP = 65

# 職員の有資格年齢範囲の下限を宣言・定義する.
STAFF_AGE_BOTTOM = 18

# 全般ファイルの名前の長さを宣言・定義する.
GENERAL_FILE_NAME_LENGTH = 32

# 知識ファイルの名前の長さを宣言・定義する.
FACT_FILE_NAME_LENGTH = GENERAL_FILE_NAME_LENGTH

# 語句ファイルの名前の長さを宣言・定義する.
WORD_FILE_NAME_LENGTH = GENERAL_FILE_NAME_LENGTH

# 生成ファイルの名前の長さを宣言・定義する.
GENERATED_FILE_NAME_LENGTH = GENERAL_FILE_NAME_LENGTH

# 画像ファイルの名前の長さを宣言・定義する.
ARCHIVED_IMAGE_FILE_NAME_LENGTH = GENERAL_FILE_NAME_LENGTH

# 音声ファイルの名前の長さを宣言・定義する.
ARCHIVED_SOUND_FILE_NAME_LENGTH = GENERAL_FILE_NAME_LENGTH

# 動画ファイルの名前の長さを宣言・定義する.
ARCHIVED_VIDEO_FILE_NAME_LENGTH = GENERAL_FILE_NAME_LENGTH

# DBスキーマを構成する各種の情報の長さを宣言・定義する.
GENERAL_ITEM_LENGTH = 64

# IDの長さを宣言・定義する.
ID_LENGTH = GENERAL_ITEM_LENGTH

# 意図の長さを宣言・定義する.
INTENT_LENGTH = GENERAL_ITEM_LENGTH

# 感情の長さを宣言・定義する.
SENTIMENT_LENGTH = GENERAL_ITEM_LENGTH

# 意図&感情の強度の長さを宣言・定義する.
STRENGTH_LENGTH = GENERAL_ITEM_LENGTH

# 品詞分類の長さを宣言・定義する.
PART_OF_SPEECH_LENGTH = GENERAL_ITEM_LENGTH

# 第一文字の長さを宣言・定義する.
FIRST_CHARACTER_LENGTH = GENERAL_ITEM_LENGTH

# 第一文字の長さを宣言・定義する.
LAST_CHARACTER_LENGTH = GENERAL_ITEM_LENGTH

# 文字数の長さを宣言・定義する.
CHARACTERS_COUNT_LENGTH = GENERAL_ITEM_LENGTH

# 分類の長さを宣言・定義する.
CATEGORY_LENGTH = GENERAL_ITEM_LENGTH

# 関係種別の長さを宣言・定義する.
RELATION_TYPE_LENGTH = GENERAL_ITEM_LENGTH

# 入退理由の長さを宣言・定義する.
ENTER_OR_EXIT_REASON_LENGTH = GENERAL_ITEM_LENGTH

# 入退日時の長さを宣言・定義する.
ENTER_OR_EXIT_DATE_TIME_LENGTH = GENERAL_ITEM_LENGTH

# 入退日時(秒数)の長さを宣言・定義する.
ENTER_OR_EXIT_SECOND_LENGTH = GENERAL_ITEM_LENGTH

# 職員名の長さを宣言・定義する.
STAFF_NAME_LENGTH = GENERAL_ITEM_LENGTH

# 職員カナ名の長さを宣言・定義する.
STAFF_KANA_NAME_LENGTH = GENERAL_ITEM_LENGTH

# 誕生日の長さを宣言・定義する.
BIRTH_DATE_LENGTH = GENERAL_ITEM_LENGTH

# レコード日時の長さを宣言・定義する.
DATE_TIME_LENGTH = GENERAL_ITEM_LENGTH

# 性別の長さを宣言・定義する.
SEX_LENGTH = 16

# 血液型の長さを宣言・定義する.
BLOOD_TYPE_LENGTH = 16

# 生パスワードの長さを宣言・定義する.
PASSWORD_LENGTH = 16

# ハッシュ化パスワードの長さを宣言・定義する.
HASHED_PASSWORD_LENGTH = 128

# 一画面ごとに表示する各種の情報の数を宣言・定義する.
GENERAL_ITEM_PER_PAGE = 100

# 一画面ごとに表示する語句情報の数を宣言・定義する.
WORD_ITEM_PER_PAGE = GENERAL_ITEM_PER_PAGE

# 一画面ごとに表示する主題情報の数を宣言・定義する.
THEME_ITEM_PER_PAGE = GENERAL_ITEM_PER_PAGE

# 一画面ごとに表示する分類情報の数を宣言・定義する.
CATEGORY_ITEM_PER_PAGE = GENERAL_ITEM_PER_PAGE

# 一画面ごとに表示する知識情報の数を宣言・定義する.
FACT_ITEM_PER_PAGE = GENERAL_ITEM_PER_PAGE

# 一画面ごとに表示する規則情報の数を宣言・定義する.
RULE_ITEM_PER_PAGE = GENERAL_ITEM_PER_PAGE

# 一画面ごとに表示する反応情報の数を宣言・定義する.
REACTION_ITEM_PER_PAGE = GENERAL_ITEM_PER_PAGE

# 一画面ごとに表示する生成情報の数を宣言・定義する.
GENERATE_ITEM_PER_PAGE = GENERAL_ITEM_PER_PAGE

# 一画面ごとに表示する履歴情報の数を宣言・定義する.
HISTORY_ITEM_PER_PAGE = GENERAL_ITEM_PER_PAGE

# 一画面ごとに表示する入退情報の数を宣言・定義する.
ENTER_OR_EXIT_ITEM_PER_PAGE = GENERAL_ITEM_PER_PAGE

# 一画面ごとに表示する職員情報の数を宣言・定義する.
STAFF_ITEM_PER_PAGE = 10

# ページネイション周りのCSSを宣言・定義する.
PAGINATION_CSS = "bootstrap4"

# データベースの絶対パスを宣言・定義する.
BASE_DIR = os.path.abspath(os.path.dirname(__file__))

# データベースの相対パスを宣言・定義する.
DATABASE_PATH = "./app.db"

# データベースのURIを宣言・定義する.
DATABASE_URI = "sqlite:///app.db?charset=utf8"

# アーカイブする元ファイルのパスを宣言・定義する.
ARCHIVE_PATH = "./resources/dynamics/archives/"

# アーカイブする元ファイル(=イメージ)のパスを宣言・定義する.
ARCHIVE_IMAGE_PATH = ARCHIVE_PATH + "images/"

# アーカイブする元ファイル(=サウンド)のパスを宣言・定義する.
ARCHIVE_SOUND_PATH = ARCHIVE_PATH + "sounds/"

# アーカイブする元ファイル(=ビデオ)のパスを宣言・定義する.
ARCHIVE_VIDEO_PATH = ARCHIVE_PATH + "videos/"

# 生成するファイルのパスを宣言・定義する.
GENERATE_PATH = "./resources/dynamics/generates/"

# 生成するファイル(=イメージ)のパスを宣言・定義する.
IMAGE_GENERATE_PATH = GENERATE_PATH + "images/"

# 生成するファイル(=サウンド)のパスを宣言・定義する.
SOUND_GENERATE_PATH = GENERATE_PATH + "sounds/"

# 生成するファイル(=ビデオ)のパスを宣言・定義する.
VIDEO_GENERATE_PATH = GENERATE_PATH + "videos/"

# MBの単位を宣言・定義する.
MEGABYTE_UNIT = int(1024 * 1024)

# 添付イメージの制限長(MB単位)を宣言・定義する.
ARCHIVE_IMAGE_LENGTH = int(10 * MEGABYTE_UNIT)

# 添付サウンドの制限長(MB単位)を宣言・定義する.
ARCHIVE_SOUND_LENGTH = int(10 * MEGABYTE_UNIT)

# 添付ビデオの制限長(MB単位)を宣言・定義する.
ARCHIVE_VIDEO_LENGTH = int(100 * MEGABYTE_UNIT)

# アプリ記録ファイルの制限長(MB単位)を宣言・定義する.
LOGGING_LENGTH = int(1 * MEGABYTE_UNIT)

# アプリが一時的に使用するファイル(=キャッシュ)のパスを宣言・定義する.
TEMPORARY_PATH = "./temporaries/"

# アプリが一時的に使用する語句エクスポートファイルのパスを宣言・定義する.
WORD_EXPORT_PATH = TEMPORARY_PATH + "words__export.xml"

# アプリが一時的に使用する主題エクスポートファイルのパスを宣言・定義する.
THEME_EXPORT_PATH = TEMPORARY_PATH + "themes__export.xml"

# アプリが一時的に使用する関係エクスポートファイルのパスを宣言・定義する.
CATEGORY_EXPORT_PATH = TEMPORARY_PATH + "categories__export.xml"

# アプリが一時的に使用する知識エクスポートファイルのパスを宣言・定義する.
FACT_EXPORT_PATH = TEMPORARY_PATH + "knowledges__export.xml"

# アプリが一時的に使用する規則エクスポートファイルのパスを宣言・定義する.
RULE_EXPORT_PATH = TEMPORARY_PATH + "rules__export.xml"

# アプリが一時的に使用する反応エクスポートファイルのパスを宣言・定義する.
REACTION_EXPORT_PATH = TEMPORARY_PATH + "reactions__export.xml"

# アプリが一時的に使用する生成エクスポートファイルのパスを宣言・定義する.
GENETATE_EXPORT_PATH = TEMPORARY_PATH + "generates__export.xml"

# アプリが一時的に使用する履歴エクスポートファイルのパスを宣言・定義する.
HISTORY_EXPORT_PATH = TEMPORARY_PATH + "histories__export.xml"

# アプリが一時的に使用する入退エクスポートファイルのパスを宣言・定義する.
ENTER_OR_EXIT_EXPORT_PATH = TEMPORARY_PATH + "enters_or_exits__export.csv"

# アプリ機密ファイルのパスを宣言・定義する.
SECURITY_SETTING_PATH = "./appsec.ini"

# アプリ設定ファイルのパスを宣言・定義する.
ENVIRONMENT_SETTING_PATH = "./appenv.ini"

# アプリ記録ファイルのパスを宣言・定義する.
LOGGING_PATH = "./app.log"

# ホーム画面となるページの背景画像ファイルのパスを宣言・定義する.
HOME_IMAGE_A_PATH = "statics/visionmarks/home-image_a.jpg"
HOME_IMAGE_B_PATH = "statics/visionmarks/home-image_b.jpg"

# ガイド画面となるページの背景画像ファイルのパスを宣言・定義する.
GUIDE_IMAGE_PATH = "statics/visionmarks/guide-image.jpg"

# ヘルプ画面となるページの背景画像ファイルのパスを宣言・定義する.
USAGE_IMAGE_PATH = "statics/visionmarks/usage-image.jpg"

# ダッシュボード画面となるページの背景画像ファイルのパスを宣言・定義する.
STAFF_BOARD_IMAGE_PATH = "statics/visionmarks/dashboard-image-for-staff.jpg"
ADMIN_BOARD_IMAGE_PATH = "statics/visionmarks/dashboard-image-for-admin.jpg"

# エラー画面となるページの背景画像ファイルのパスを宣言・定義する.
ERROR_IMAGE_PATH = "statics/visionmarks/error-image.jpg"

# ダミーの文書ファイルのパスを宣言・定義する.
DUMMY_FILE_PATH = "./resources/dynamics/generates/dummy.txt"

# 画面・ページ表示上の職員発話の長さを宣言・定義する.
STAFF_MESSAGE_DISPLAY_LENGTH = 16

# 画面・ページ表示上のアプリ発話の長さを宣言・定義する.
APP_MESSAGE_DISPLAY_LENGTH = 16

# 入力・処理上の職員発話の長さを宣言・定義する.
STAFF_MESSAGE_INPUT_LENGTH = 65536

# 入力・処理上のアプリ発話の長さを宣言・定義する.
APP_MESSAGE_OUTPUT_LENGTH = 262144

# 短期記憶の大きさの下限を宣言・定義する.
SHORT_TERM_MEMORY_SIZE_BOTTOM = 1

# 短期記憶の大きさの上限を宣言・定義する.
SHORT_TERM_MEMORY_SIZE_TOP = 10

# 長期記憶の大きさの下限を宣言・定義する.
LONG_TERM_MEMORY_SIZE_BOTTOM = 1

# 長期記憶の大きさの上限を宣言・定義する.
LONG_TERM_MEMORY_SIZE_TOP = 10

# 学習の深さの下限を宣言・定義する.
LEARN_DEPTH_BOTTOM = 1

# 学習の深さの上限を宣言・定義する.
LEARN_DEPTH_TOP = 10

# 推論測の深さの下限を宣言・定義する.
INFERENCE_AND_SPECULATION_DEPTH_BOTTOM = 1

# 推論測の深さの上限を宣言・定義する.
INFERENCE_AND_SPECULATION_DEPTH_TOP = 10

# 短期記憶のデフォルト値を宣言・定義する.
SHORT_TERM_MEMORY_SIZE_DEFAULT = "1"

# 長期記憶のデフォルト値を宣言・定義する.
LONG_TERM_MEMORY_SIZE_DEFAULT = "1"

# 学習の深さのデフォルト値を宣言・定義する.
LEARN_DEPTH_DEFAULT = "1"

# 推論測の深さのデフォルト値を宣言・定義する.
INFERENCE_AND_SPECULATION_DEPTH_DEFAULT = "1"

# インメモリー化のデフォルト値を宣言・定義する.
IN_MEMORIZE_DEFAULT = "False"

# 辞書項目統合のデフォルト値を宣言・定義する.
DICTIONARY_ENTRIES_INETEGRATION_DEFAULT = "False"

# グローバル情報共有のデフォルト値を宣言・定義する.
GLOBAL_INFORMATION_SHARING_DEFAULT = "False"

# バックグラウンド処理のデフォルト値を宣言・定義する.
BACKGROUND_PROCESSING_DEFAULT = "False"

# ポリシーベース決定のデフォルト値を宣言・定義する.
POLICY_BASED_DECISIONS_DEFAULT = "False"

# 個別化会話のデフォルト値を宣言・定義する.
PERSONALIZED_CONVERSATIONS_DEFAULT = "False"

# CSP対策のためのアプリURLを宣言・定義する.
APP_URL_FOR_CSP = "http://localhost:5000"

# Talisman用のCSPを宣言・定義する.
CSP = {
    "default-src": ["'self'", APP_URL_FOR_CSP],
    "script-src": ["'self'", "'unsafe-inline'", APP_URL_FOR_CSP],
    "style-src": ["'self'", "'unsafe-inline'", APP_URL_FOR_CSP],
    "img-src": ["'self'", APP_URL_FOR_CSP, "data:"],
    "sound-src": ["'self'", APP_URL_FOR_CSP, "data:"],
    "video-src": ["'self'", APP_URL_FOR_CSP, "data:"]
}

# Talisman用のHTTPS強制フラッグを宣言・定義する.
FORCE_HTTPS = False

# 職員入室フォーム内の理由メニューを宣言・定義する.
MENU_CHOICE_FOR_STAFF_ENTER_FORM = [
    ("", ""),
    ("clock-in", "出勤"),
    ("after-break", "休憩明け"),
    ("return-to-out", "外出戻り")
]

# 職員退室フォーム内の理由メニューを宣言・定義する.
MENU_CHOICE_FOR_STAFF_EXIT_FORM = [
    ("", ""),
    ("clock-out", "退勤"),
    ("out", "外出"),
    ("break", "休憩")
]

# 語句学習フォーム内の意図メニューを宣言・定義する.
MENU_CHOICE_1_FOR_LEARN_WORD_FORM = [
    ("", ""),
    ("benefactive-type", "施与型"), #「～してあげよう」
    ("request-type", "依頼型"), #「～してくれ」
    ("volitional-type", "意志型"), #「～するつもり(だ)」
    ("speculative-type", "推量型"), #「～だろう」
    ("prohibitive-type", "禁止型"), #「～してはいけない」
    ("permissive-type", "許可型"), #「～してもよい」
    ("desiderative-type", "希望型"),#「～したい」
    ("emotive-type", "感情型"), #「～(してもらって)うれしい」
    ("obligative-type", "義務型"), #「～するべき(だ)」
    ("potential-type", "可能型"), #「～することができる」
    ("confirmation-type", "確認型"), #「～しますか(？)」
    ("suggestion-type", "提案型"), #「～はどうだろう」
    ("gratitude-type", "感謝型"), #「～(してもらって)ありがたい」
    ("apology-type", "謝罪型"), #「～(してしまって)すまない」
    ("agreement-type", "同意型"), #「はい」
    ("disagreement-type", "不同意型"), #「いいえ」
    ("explanation-type", "説明型"), #「～ということ(だ)」
    ("advice-type", "助言型"), #「～してはどう(か)(？)」
    ("guidance-type", "指導型"), #「～してあげよう」
    ("disclosure-and-declaration-type", "開示&宣言型"), #「～です」
    ("notification-and-announcement-type", "周知&告知型"), #「～とのこと(です)」
    ("inquiry-and-question-type", "質問&疑問型"), #「～(ということ)ですか？」
    ("directive-and-command-type", "指示&命令型"), #「～しなさい」
    ("unknown-type", "その他型（分類不明）")
]

# 語句学習フォーム内の感情メニューを宣言・定義する.
MENU_CHOICE_2_FOR_LEARN_WORD_FORM = [
    ("", ""),
    ("angry", "怒り"),
    ("sad", "悲しい"),
    ("lonely", "寂しい"),
    ("normal", "普通"),
    ("happy", "楽しい"),
    ("joyful", "嬉しい"),
    ("peaceful", "安らぎ"),
    ("unknown", "その他(分類不明)")
]

# 語句学習フォーム内の感情補助メニューを宣言・定義する.
MENU_CHOICE_3_FOR_LEARN_WORD_FORM = [
    ("", ""),
    ("calm", "冷静"),
    ("surprise", "驚き"),
    ("confusion", "戸惑い"),
    ("distress", "動揺"),
    ("excitement", "興奮"),
    ("unknown", "その他(分類不明)")
]

# 語句学習フォーム内の強度メニューを宣言・定義する.
MENU_CHOICE_4_FOR_LEARN_WORD_FORM = [
    ("", ""),
    ("very-weak", "とても弱い"),
    ("weak", "弱い"),
    ("slightly-weak", "やや弱い"),
    ("normal", "普通"),
    ("slightly-strong", "やや強い"),
    ("strong", "強い"),
    ("very-strong", "とても強い"),
    ("unknown", "その他(分類不明)")
]

# 語句学習フォーム内の品詞分類メニューを宣言・定義する
MENU_CHOICE_5_FOR_LEARN_WORD_FORM = [
    ("", ""),
    ("noun", "名詞"),  # 物・事・概念などを表す語（例：本、情報）
    ("pron", "代名詞"),  # 名詞の代わりに使う語（例：私、それ）
    ("propn", "固有名詞"),  # 人名・地名などの固有の名称（例：東京、太郎）
    ("adj", "形容詞"),  # 名詞を修飾する語（例：大きい、美しい）
    ("verb", "動詞"),  # 動作や状態を表す語（例：走る、考える）
    ("adv", "副詞"),  # 動詞・形容詞などを修飾する語（例：すぐに、とても）
    ("aux", "助動詞"),  # 動詞に意味を加える補助語（例：〜たい、〜れる）
    ("adp", "前置詞"),  # 英語などで名詞の前に置かれる語（例：in, on）※日本語では助詞に近い
    ("cconj", "等位接続詞"),  # 対等な語句や文をつなぐ語（例：そして、または）
    ("sconj", "従属接続詞"),  # 主従関係のある文をつなぐ語（例：〜ので、〜ながら）
    ("det", "限定詞"),  # 名詞の範囲や数量を限定する語（例：この、すべての）
    ("intj", "間投詞"),  # 感情や反応を表す語（例：あっ、わーい）
    ("num", "数詞"),  # 数量や順序を表す語（例：一、三番目）
    ("part", "助詞"),  # 文法関係を示す語（例：が、を、に）
    ("clf", "類別詞"),  # 数量詞に付く分類語（例：一冊、一人）※日本語特有
    ("cop", "連結詞"),  # 主語と述語をつなぐ語（例：「〜は〜だ」の「だ」）
    ("mark", "接続標識"),  # 従属節の導入語（例：「〜が」「〜ので」など）
    ("punct", "読点"),  # 文中の区切り（例：、）
    ("period", "句点"),  # 文末の区切り（例：。）
    ("sym", "記号"),  # 数式や特殊記号（例：＋、％）
    ("unknown", "その他(分類不明)")
]


# 規則学習フォーム内の規則メニューを宣言・定義する.
MENU_CHOICE_FOR_LEARN_RULE_FORM = [
    ("", ""),
    ("superior-priority", "上位&優先"),
    ("equal-and-competition", "同等&競合"),
    ("subordinate-inferior", "下位&劣後"), 
    ("unknown", "その他(分類不明)")
]

# 知識学習フォーム内の知識メニューを宣言・定義する.
MENU_CHOICE_1_FOR_LEARN_FACT_FORM = [
    ("", ""),
    ("god", "神"),
    ("human", "人間"),
    ("organism", "生物"),
    ("nature-and-environment", "自然&環境"),
    ("place-and-space", "場所&空間"),
    ("action-and-behavior", "行為&行動"),
    ("event-and-phenomenon", "事象&現象"),
    ("technology-and-tool", "技術&道具"),
    ("object-and-property", "物品&財物"),
    ("currency-and-money", "通貨&貨幣"),
    ("law-and-system", "法律&制度"),
    ("organization-and-group", "組織&団体"),
    ("thought-and-belief", "思想&信仰"),
    ("energy-and-matter", "気&エネルギー"),
    ("unknown", "その他(分類不明)")
]

# 入退登録フォーム内の理由メニューを宣言・定義する.
MENU_CHOICE_FOR_REGISTER_ENTER_OR_EXIT_FORM = [
    ("", ""),
    ("clock-in", "出勤"),
    ("after-break", "休憩明け"),
    ("return-to-out", "外出戻り"),
    ("clock-out", "退勤"),
    ("out", "外出"),
    ("break", "休憩")
]

# 職員登録フォーム内の性別メニューを宣言・定義する.
MENU_CHOICE_1_FOR_REGISTER_STAFF_FORM = [
    ("", ""),
    ("man", "男性"),
    ("woman", "女性"),
    ("unknown", "その他(分類不明)")
]

# 職員登録フォーム内の血液型メニューを宣言・定義する.
MENU_CHOICE_2_FOR_REGISTER_STAFF_FORM = [
    ("", ""),
    ("type-a", "A型"),
    ("type-b", "B型"),
    ("type-ab", "AB型"),
    ("type-o", "O型"),
    ("unknown", "その他(分類不明)")
]

# 職員検索フォーム内の理由メニューを宣言・定義する.
MENU_CHOICE_FOR_SEARCH_ENTER_OR_EXIT_FORM = [
    ("", ""),
    ("clock-in", "出勤"),
    ("after-break", "休憩明け"),
    ("return-to-out", "外出戻り"),
    ("clock-out", "退勤"),
    ("out", "外出"),
    ("break", "休憩"),
    ("unknown", "その他(分類不明)")
]

# 語句検索フォーム内の意図メニューを宣言・定義する.
MENU_CHOICE_1_FOR_SEARCH_WORD_FORM = MENU_CHOICE_1_FOR_LEARN_WORD_FORM

# 語句検索フォーム内の感情メニューを宣言・定義する.
MENU_CHOICE_2_FOR_SEARCH_WORD_FORM = MENU_CHOICE_2_FOR_LEARN_WORD_FORM

# 語句検索フォーム内の感情補助メニューを宣言・定義する.
MENU_CHOICE_3_FOR_SEARCH_WORD_FORM = MENU_CHOICE_3_FOR_LEARN_WORD_FORM

# 語句検索フォーム内の強度メニューを宣言・定義する.
MENU_CHOICE_4_FOR_SEARCH_WORD_FORM = MENU_CHOICE_4_FOR_LEARN_WORD_FORM

# 語句検索フォーム内の品詞分類メニューを宣言・定義する.
MENU_CHOICE_5_FOR_SEARCH_WORD_FORM = MENU_CHOICE_5_FOR_LEARN_WORD_FORM

# 検索フォーム全般のための整序条件メニューを宣言・定義する.
MENU_CHOICE_1_FOR_SEARCH_FORM = [
    ("condition-1", "ID 昇順"),
    ("condition-2", "ID 降順")
]

# 検索フォーム全般のための抽出条件メニューを宣言・定義する.
MENU_CHOICE_2_FOR_SEARCH_FORM = [
    ("condition-1", "秘匿されていないものが対象"),
    ("condition-2", "秘匿されていないものも対象")
]

# 大多数のフォーム内の是非メニューを宣言・定義する.
MENU_CHOICE_FOR_UNIVERSAL_FORM = [
    ("", ""),
    ("yes", "はい"),
    ("no", "いいえ")    
]

# 語句変更フォーム内の意図メニューを宣言・定義する.
MENU_CHOICE_1_FOR_MODIFY_WORD_FORM = MENU_CHOICE_1_FOR_LEARN_WORD_FORM

# 語句変更フォーム内の感情メニューを宣言・定義する.
MENU_CHOICE_2_FOR_MODIFY_WORD_FORM = MENU_CHOICE_2_FOR_LEARN_WORD_FORM

# 語句変更フォーム内の感情補助メニューを宣言・定義する.
MENU_CHOICE_3_FOR_MODIFY_WORD_FORM = MENU_CHOICE_3_FOR_LEARN_WORD_FORM

# 語句変更フォーム内の強度メニューを宣言・定義する.
MENU_CHOICE_4_FOR_MODIFY_WORD_FORM = MENU_CHOICE_4_FOR_LEARN_WORD_FORM

# 語句変更フォーム内の品詞分類メニューを宣言・定義する.
MENU_CHOICE_5_FOR_MODIFY_WORD_FORM = MENU_CHOICE_5_FOR_LEARN_WORD_FORM

# 語句詳細フォーム内の意図メニューを宣言・定義する.
MENU_CHOICE_1_FOR_DETAIL_WORD_FORM = MENU_CHOICE_1_FOR_LEARN_WORD_FORM

# 語句詳細フォーム内の感情メニューを宣言・定義する.
MENU_CHOICE_2_FOR_DETAIL_WORD_FORM = MENU_CHOICE_2_FOR_LEARN_WORD_FORM

# 語句詳細フォーム内の感情補助メニューを宣言・定義する.
MENU_CHOICE_3_FOR_DETAIL_WORD_FORM = MENU_CHOICE_3_FOR_LEARN_WORD_FORM

# 語句詳細フォーム内の強度メニューを宣言・定義する.
MENU_CHOICE_4_FOR_DETAIL_WORD_FORM = MENU_CHOICE_4_FOR_LEARN_WORD_FORM

# 語句詳細フォーム内の品詞分類メニューを宣言・定義する.
MENU_CHOICE_5_FOR_DETAIL_WORD_FORM = MENU_CHOICE_5_FOR_LEARN_WORD_FORM

# フォーム内の日時の表示形式を宣言・定義する. 
GENERAL_DATE_FORMAT = "%Y-%m-%dT%H:%M"

# フォーム内の誕生日の表示形式を宣言・定義する.
BIRTH_DATE_FORMAT = "%Y-%m-%d"

# フォーム内で扱えるイメージファイルの形式(=拡張子)を宣言・定義する.
IMAGE_FILE_FORMAT = {"accept": "image/jpeg, image/png, image/gif, image/bmp"}

# フォーム内で扱えるサウンドファイルの形式(=拡張子)を宣言・定義する.
SOUND_FILE_FORMAT = {"accept": "audio/mp3, audio/wav"}

# フォーム内で扱えるビデオファイルの形式(=拡張子)を宣言・定義する.
VIDEO_FILE_FORMAT = {"accept": "video/mpeg, video/mp4, video/avi"}

# フォーム内で扱えるドキュメントファイルの形式(=拡張子)を宣言・定義する.
DOCUMENT_FILE_FORMAT = {"accept": "application/xml"}

# フォーム内で扱えるプレーンファイルの形式(=拡張子)を宣言・定義する.
PLAIN_FILE_FORMAT = {"accept": "text/csv"}