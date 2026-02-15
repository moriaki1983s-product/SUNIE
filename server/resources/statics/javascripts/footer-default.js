/* 全てのページで使用するフッターの機能 */


// フッターがクリックされると, ページトップに自動でスクロールされるようにする.
var btn = $('.footer');
btn.click(function () { $('body,html').animate({ scrollTop: 0 }, 500); return false; });