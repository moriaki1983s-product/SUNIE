/* ページの値・表示リセットの機能 */


// 該当ページに特定のドキュメント要素が含まれていたら, イベントハンドラーを設定する.
// ※[cancel]ボタンで, ページ内の全ての[text]型要素の値をリセットする.
var cancelButton = document.getElementById('cancel');
var textInputs = document.querySelectorAll('input[type="text"]');
if ((cancelButton !== null) && (textInputs !== null)) {
    cancelButton.addEventListener('click', function () {
        textInputs.forEach(function (textInput) {
            textInput.style.color = 'white';
            textInput.value = '';
        })
    })
}


// 該当ページに特定のドキュメント要素が含まれていたら, イベントハンドラーを設定する.
// ※[cancel]ボタンで, ページ内の全ての[date]型要素の値をリセットする.
var cancelButton = document.getElementById('cancel');
var dateInputs = document.querySelectorAll('input[type="date"]');
if ((cancelButton !== null) && (dateInputs !== null)) {
    cancelButton.addEventListener('click', function () {
        dateInputs.forEach(function (dateInput) {
            dateInput.style.color = 'white';
            dateInput.value = '';
        })
    })
}


// 該当ページに特定のドキュメント要素が含まれていたら, イベントハンドラーを設定する.
// ※[cancel]ボタンで, ページ内の全ての選択型メニューをリセットする(=一番上の項目が選択された状態にする).
var cancelButton = document.getElementById('cancel');
var selectMenus = document.querySelectorAll('select');
if ((cancelButton !== null) && (selectMenus !== null)) {
    cancelButton.addEventListener('click', function () {
        selectMenus.forEach(function (selectMenu) {
            selectMenu.selectedIndex = 0;
        })
    })
}


// 該当ページに特定のドキュメント要素が含まれていたら, イベントハンドラーを設定する.
// ※[show_ ~~][search_~~_results]といった名前のページに埋め込まれる隠しタグ値をリセットする.
// ※この隠しタグ値は、上記ページ内からボタンクリックでページ遷移するために必要な情報です.
if (document.getElementById('hidden-modify-item-id') !== null) {
    window.addEventListener('unload', function () {
        document.getElementById('hidden-modify-item-id').value = "";
    })
}
if (document.getElementById('hidden-detail-item-id') !== null) {
    window.addEventListener('unload', function () {
        document.getElementById('hidden-detail-item-id').value = "";
    })
}
if (document.getElementById('hidden-retrieve-item-id') !== null) {
    window.addEventListener('unload', function () {
        document.getElementById('hidden-retrieve-item-id').value = "";
    })
}