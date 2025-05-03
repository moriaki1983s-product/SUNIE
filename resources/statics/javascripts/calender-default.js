/* ダッシュボード画面のページに埋め込むカレンダーの機能 */


// 現在の日付を取得しておいて, 後で使用する.
var oldDate = new Date().getDate();


/* 時刻表記を整形する関数 */
function set2fig(num) {
    var ret;

    // 渡された値が[10]を超えていたら, 先頭に文字のゼロを付ける.
    if (num < 10) { ret = '0' + num; }
    else { ret = num; }
    return ret;
}


/* 日付を表示する関数 */
function dateRender() {
    var now = new Date();
    var year = now.getFullYear();
    var month = now.getMonth() + 1;
    var date = now.getDate();
    var days = ['日', '月', '火', '水', '木', '金', '土']
    var day = days[now.getDay()];
    var conts = year + '年' + month + '月' + date + '日' + '（' + day + '）'

    // ドキュメント要素の内容として, 現在の日付を設定する.
    document.getElementById('current-date').innerHTML = conts;
}


/* 時刻を表示する関数 */
function timeRender() {
    var nowTime = new Date();
    var nowHour = set2fig(nowTime.getHours());
    var nowMin = set2fig(nowTime.getMinutes());
    var nowSec = set2fig(nowTime.getSeconds());
    var conts = nowHour + ':' + nowMin + ':' + nowSec;
    var newDate = nowTime.getDate();

    // 日付が変わったかどうかを調べて,
    // 変わっていたら, 日付を更新する.
    if (newDate !== oldDate) {
        dateRender();
        oldDate = newDate
    }

    // ドキュメント要素の内容として, 現在の時刻を設定する.
    document.getElementById('current-time').innerHTML = conts;
}


// 該当ページに特定のドキュメント要素が含まれていたら, イベントハンドラーを設定する.
if ((document.getElementById('current-date') !== null) &&
    (document.getElementById('current-time') !== null)) {
    document.addEventListener('DOMContentLoaded', function () {
        dateRender();
        timeRender();
        setInterval(timeRender, 1000); // ※CSP対策のため, 関数参照を直接渡す.
    })
}