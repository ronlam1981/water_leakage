/* 一按複製聯絡資料。
   唯一一段 JavaScript：無外部程式庫、無追蹤、不收集任何資料。 */
(function () {
  'use strict';

  /* 無 JavaScript 時，複製掣以 CSS 隱藏；號碼本身仍然可見、可自行選取。 */
  document.documentElement.classList.add('js');

  function flash(btn, text) {
    var original = btn.getAttribute('data-label') || btn.textContent;
    btn.setAttribute('data-label', original);
    btn.textContent = text;
    btn.classList.add('is-done');
    window.setTimeout(function () {
      btn.textContent = original;
      btn.classList.remove('is-done');
    }, 1800);
  }

  /* 舊瀏覽器或非安全來源（file://）的後備做法 */
  function legacyCopy(value) {
    var box = document.createElement('textarea');
    box.value = value;
    box.setAttribute('readonly', '');
    box.style.position = 'fixed';
    box.style.top = '-1000px';
    box.style.opacity = '0';
    document.body.appendChild(box);
    box.select();
    var ok = false;
    try { ok = document.execCommand('copy'); } catch (e) { ok = false; }
    document.body.removeChild(box);
    return ok;
  }

  document.addEventListener('click', function (e) {
    var btn = e.target.closest ? e.target.closest('.copy') : null;
    if (!btn) return;
    e.preventDefault();

    var value = btn.getAttribute('data-copy') || '';
    if (!value) return;

    if (navigator.clipboard && navigator.clipboard.writeText) {
      navigator.clipboard.writeText(value).then(
        function () { flash(btn, '已複製 ✓'); },
        function () { flash(btn, legacyCopy(value) ? '已複製 ✓' : '請長按複製'); }
      );
    } else {
      flash(btn, legacyCopy(value) ? '已複製 ✓' : '請長按複製');
    }
  });
})();
