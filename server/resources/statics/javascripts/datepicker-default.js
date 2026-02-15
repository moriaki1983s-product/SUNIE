/* ブラウザ標準の日付ピッカーの表示の不具合を解消するための機能 */


// 該当ページに特定のドキュメント要素が含まれていたら, イベントハンドラーを設定する.
// ※ページ内のすべての[date]型要素について,フォーカス状態になったら, 表示状態にする.
// これとは逆に、非フォーカス状態になったら非表示状態にする(=文字色を[white]に変更する).
var dateInputs = document.querySelectorAll('input[type="date"]');
if (dateInputs !== null) {
    dateInputs.forEach(function (dateInput) {
        if (!dateInput.hasAttribute('readonly')) {
            if (dateInput.value === "") {
                dateInput.style.color = 'white';
            }
            dateInput.addEventListener('focus', function () {
                dateInput.style.color = 'black';
            })
            dateInput.addEventListener('blur', function () {
                if (dateInput.value === '') {
                    dateInput.style.color = 'white';
                }
            })
        }
    })
}

// ※ページ内のすべての[date]型要素について,フォーカス状態になったら, 表示状態にする.
// これとは逆に、非フォーカス状態になったら非表示状態にする(=文字色を[white]に変更する).
var dateTimeInputs = document.querySelectorAll('input[type="datetime-local"]');
if (dateTimeInputs !== null) {
    dateTimeInputs.forEach(function (dateTimeInput) {
        if (!dateTimeInput.hasAttribute('readonly')) {
            if (dateTimeInput.value === "") {
                dateTimeInput.style.color = 'white';
            }
            dateTimeInput.addEventListener('focus', function () {
                dateTimeInput.style.color = 'black';
            })
            dateTimeInput.addEventListener('blur', function () {
                if (dateTimeInput.value === '') {
                    dateTimeInput.style.color = 'white';
                }
            })
        }
    })
}