/* ===========================================================
   互動自檢引擎
   =========================================================== */
(function () {
  'use strict';

  var D = window.LEAK_DATA;
  var shell, body, pills, bar, crumbs;
  var state = { answers: {}, history: [], current: null, picked: [] };

  var STAGES = ['一部曲 自行測試', '二部曲 提供檢修參考資訊', '三部曲 進行檢修'];

  function esc(s) {
    return String(s).replace(/[&<>"]/g, function (c) {
      return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c];
    });
  }

  function el(html) {
    var t = document.createElement('template');
    t.innerHTML = html.trim();
    return t.content.firstElementChild;
  }

  /* ---------- 進度 ---------- */
  function setProgress(node) {
    var stage = node.stage || 1;
    Array.prototype.forEach.call(pills.children, function (p, i) {
      p.classList.toggle('on', i === stage - 1);
    });
    var pct;
    if (node.kind === 'result') pct = 100;
    else pct = Math.min(90, 18 + state.history.length * 26);
    bar.style.width = pct + '%';
  }

  function renderCrumbs() {
    if (!state.picked.length) { crumbs.innerHTML = ''; return; }
    crumbs.innerHTML = '你的選擇：' + state.picked.map(function (p) {
      return '<span>' + esc(p) + '</span>';
    }).join('');
  }

  /* ---------- 共用片段 ---------- */
  function figureHTML(img) {
    if (!img) return '';
    return '<figure class="figure"><img src="' + img.src + '" alt="' + esc(img.alt || '') + '" loading="lazy">' +
      (img.caption ? '<figcaption>' + img.caption + '</figcaption>' : '') + '</figure>';
  }

  function notesHTML(notes) {
    if (!notes || !notes.length) return '';
    return notes.map(function (n) {
      return '<div class="note ' + (n.tone || '') + '">' + n.html + '</div>';
    }).join('');
  }

  function howtoHTML(steps) {
    if (!steps || !steps.length) return '';
    return '<ol class="howto">' + steps.map(function (s) { return '<li>' + s + '</li>'; }).join('') + '</ol>';
  }

  function optionsHTML(options) {
    return '<div class="options">' + options.map(function (o, i) {
      return '<button class="opt" data-i="' + i + '" type="button">' +
        (o.tag ? '<span class="opt-tag">' + esc(o.tag) + '</span>' : '') +
        '<span class="opt-label">' + o.label + '</span>' +
        '<span class="opt-desc">' + o.desc + '</span>' +
        '</button>';
    }).join('') + '</div>';
  }

  function navHTML(isResult) {
    var h = '<div class="quiz-nav">';
    if (state.history.length) h += '<button class="btn btn-ghost btn-sm" data-act="back" type="button">← 返回上一步</button>';
    h += '<button class="btn btn-ghost btn-sm" data-act="restart" type="button">↺ 重新開始</button>';
    if (isResult) {
      h += '<button class="btn btn-green btn-sm" data-act="print" type="button">🖨 列印／存成 PDF</button>';
      h += '<a class="btn btn-primary btn-sm" href="contact.html">需要有人幫手？聯絡宇見顧問</a>';
    }
    h += '</div>';
    return h;
  }

  /* ---------- 結果 ---------- */
  function reportText() {
    var L = D.LABELS, a = state.answers, lines = [];
    lines.push('【澳門樓宇滲漏水 · 自檢記錄】');
    lines.push('自檢日期：' + new Date().toLocaleString('zh-Hant'));
    lines.push('');
    lines.push('1. 滲漏形態：' + ((L.symptom[a.symptom]) || '未填寫'));
    lines.push('2. 滲漏位置：' + ((L.position[a.position]) || '未填寫'));
    lines.push('3. 已做的自行測試：' + (a.test || '（未進行或未記錄）'));
    lines.push('4. 自檢初步結論：' + (a.resultTitle || ''));
    lines.push('');
    lines.push('── 向樓宇滲漏水聯合處理中心反映時，請一併準備以下資料 ──');
    D.CHECKLIST.forEach(function (c, i) { lines.push((i + 1) + '. ' + c); });
    lines.push('');
    lines.push('※ 本記錄由「澳門樓宇滲漏水自查互動指南」自動產生，內容依據樓宇滲漏水聯合處理中心《處理樓宇滲漏常識》(2023年9月)，僅供參考，不構成專業檢測結論。');
    return lines.join('\n');
  }

  function resultHTML(node) {
    var a = state.answers;
    var h = '';
    h += '<div class="result-head tone-' + node.tone + '">' +
      '<div class="verdict">' + esc(node.verdict) + '</div>' +
      '<h3>' + node.title + '</h3>' +
      '<p>' + node.summary + '</p></div>';

    if (a.position && D.POSITION_HINT[a.position]) {
      h += '<div class="note"><b>位置線索：</b>' + D.POSITION_HINT[a.position] + '</div>';
    }
    h += figureHTML(node.img);
    h += notesHTML(node.notes);

    h += '<div class="rgrid">';
    if (node.cause) {
      h += '<div class="rbox"><h4>常見成因</h4><ul>' +
        node.cause.map(function (c) { return '<li>' + c + '</li>'; }).join('') + '</ul></div>';
    }
    if (node.actions) {
      h += '<div class="rbox"><h4>建議下一步</h4><ul>' +
        node.actions.map(function (c) { return '<li>' + c + '</li>'; }).join('') + '</ul></div>';
    }
    h += '</div>';

    if (node.urgent) h += '<div class="note warn">' + node.urgent + '</div>';

    if (node.showChecklist) {
      h += '<div class="note ok"><b>向中心反映前，請先備妥以下資料（刊物 P.11）：</b><ul>' +
        D.CHECKLIST.map(function (c) { return '<li>' + c + '</li>'; }).join('') + '</ul></div>';
    }

    if (node.showHelp) {
      h += '<div class="note"><b>仍未解決？</b>請前往「<a href="help.html">求助途徑</a>」一頁，' +
        '當中列出聯合處理中心、專業檢測、必要仲裁三條路，以及可以陪你走完全程的' +
        '<a href="contact.html">宇見顧問有限公司</a>。</div>';
    }

    h += '<div class="report"><h4>📋 你的自檢記錄（可複製後直接貼入電郵或 WhatsApp）</h4>' +
      '<pre id="reportText">' + esc(reportText()) + '</pre>' +
      '<button class="btn btn-primary btn-sm" data-act="copy" type="button">複製自檢記錄</button> ' +
      '<span class="small muted" id="copyHint"></span></div>';

    return h;
  }

  /* ---------- 主渲染 ---------- */
  function render(id) {
    var node = D.nodes[id];
    if (!node) return;
    state.current = id;

    var h = '';
    if (node.kind === 'result') {
      state.answers.resultTitle = node.title.replace(/<[^>]+>/g, '');
      h = resultHTML(node);
    } else {
      h += '<h3 class="q-title">' + node.title + '</h3>';
      h += '<p class="q-lead">' + node.lead + '</p>';
      h += figureHTML(node.img);
      h += howtoHTML(node.howto);
      h += notesHTML(node.notes);
      h += optionsHTML(node.options);
    }
    h += navHTML(node.kind === 'result');

    body.innerHTML = h;
    renderCrumbs();
    setProgress(node);

    body.querySelectorAll('.opt').forEach(function (btn) {
      btn.addEventListener('click', function () {
        var o = node.options[+btn.dataset.i];
        state.history.push({ id: id, picked: state.picked.slice(), answers: JSON.parse(JSON.stringify(state.answers)) });
        if (o.set) Object.keys(o.set).forEach(function (k) { state.answers[k] = o.set[k]; });
        state.picked.push(o.label.replace(/<[^>]+>/g, ''));
        render(o.next);
        scrollToQuiz();
      });
    });

    body.querySelectorAll('[data-act]').forEach(function (btn) {
      btn.addEventListener('click', function () {
        var act = btn.dataset.act;
        if (act === 'back') {
          var prev = state.history.pop();
          if (prev) { state.picked = prev.picked; state.answers = prev.answers; render(prev.id); scrollToQuiz(); }
        } else if (act === 'restart') {
          state = { answers: {}, history: [], current: null, picked: [] };
          render(D.start); scrollToQuiz();
        } else if (act === 'print') {
          window.print();
        } else if (act === 'copy') {
          var txt = document.getElementById('reportText').textContent;
          var hint = document.getElementById('copyHint');
          navigator.clipboard.writeText(txt).then(function () {
            hint.textContent = '✓ 已複製到剪貼簿';
          }).catch(function () {
            hint.textContent = '請長按上方文字手動複製';
          });
        }
      });
    });
  }

  function scrollToQuiz() {
    var top = shell.getBoundingClientRect().top + window.pageYOffset - 76;
    window.scrollTo({ top: top, behavior: 'smooth' });
  }

  /* ---------- 求助途徑 ---------- */
  function renderHelp() {
    var wrap = document.getElementById('helpGrid');
    if (!wrap) return;
    wrap.innerHTML = D.HELP.map(function (c) {
      return '<div class="help-card ' + c.cls + '">' +
        '<div class="tag">' + esc(c.tag) + '</div>' +
        '<h3>' + esc(c.title) + '</h3>' +
        '<p class="small">' + c.body + '</p>' +
        '<ul class="small">' + c.lines.map(function (l) {
          return '<li><b>' + esc(l.k) + '：</b>' +
            (l.href ? '<a href="' + l.href + '"' + (/^https?:/.test(l.href) ? ' target="_blank" rel="noopener"' : '') + '>' + esc(l.v) + '</a>' : esc(l.v)) +
            '</li>';
        }).join('') + '</ul>' +
        (c.foot ? '<p class="small muted">' + c.foot + '</p>' : '') +
        '</div>';
    }).join('');
  }

  function renderChecklist() {
    var ul = document.getElementById('checklist');
    if (!ul) return;
    ul.innerHTML = D.CHECKLIST.map(function (c) { return '<li>' + c + '</li>'; }).join('');
  }

  /* ---------- 啟動 ---------- */
  document.addEventListener('DOMContentLoaded', function () {
    var y = document.getElementById('year');
    if (y) y.textContent = new Date().getFullYear();

    renderHelp();
    renderChecklist();

    shell = document.getElementById('quizShell');
    body = document.getElementById('quizBody');
    pills = document.getElementById('stagePills');
    bar = document.getElementById('progressBar');
    crumbs = document.getElementById('crumbs');
    if (!shell || !body || !pills || !bar || !crumbs) return;   // 此頁沒有自檢工具

    pills.innerHTML = STAGES.map(function (s, i) {
      return '<span class="pill' + (i === 0 ? ' on' : '') + '">' + s + '</span>';
    }).join('');

    render(D.start);
  });
})();
