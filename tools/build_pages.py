#!/usr/bin/env python3
"""把 content/*.html 的內容片段，套上共用的頁首／頁尾，輸出成網站根目錄的各個頁面。

用法：  python3 tools/build_pages.py
新增或修改內容時，只需改 content/ 內的片段，再重新執行本script。
"""
import os, io

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

SITE = '澳門樓宇滲漏水自查互動指南'

# slug, 內容檔, 導覽標籤, <title>, meta description
PAGES = [
    ('index',     'home',    '首頁',     SITE,
     '根據樓宇滲漏水聯合處理中心《處理樓宇滲漏常識》製作的澳門滲漏水自查互動指南：流程圖、逐步自檢、責任界定與求助途徑。'),
    ('trilogy',   'intro',   '三部曲',   '處理滲漏三部曲 ｜ ' + SITE,
     '一部曲自行測試、二部曲提供檢修參考資訊、三部曲進行檢修，以及樓宇滲漏水聯合處理中心的角色與查詢方式。'),
    ('flow',      'flow',    '流程圖',   '自行檢測流程圖 ｜ ' + SITE,
     '官方「處理滲漏水之流程」流程圖，附手機友善的文字版拆解。'),
    ('selfcheck', 'quiz',    '互動自檢', '互動自檢 ｜ ' + SITE,
     '逐步問答與動手測試，盡量找出滲漏源頭，並產生可複製、可列印的自檢記錄。'),
    ('risk',      'risk',    '衛生級別', '衛生級別 ｜ ' + SITE,
     '衛生局的低、中、高風險分級特徵與圖片，以及業主不維修的法律後果。'),
    ('detect',    'pro',     '專業檢測', '專業現場滲漏檢測 ｜ ' + SITE,
     '目測、微波探濕、紅外線成像測溫、色粉測試等無破損滲漏檢測方法。'),
    ('duty',      'duty',    '維修責任', '業主維修責任 ｜ ' + SITE,
     '大廈共同部分與私人單位的維修責任分野、共同儲備基金，以及拒絕修理的後果。'),
    ('cases',     'cases',   '成功個案', '成功個案 ｜ ' + SITE,
     '刊物記載的三宗真實個案：鄰里合作如何令滲漏與塞渠問題迅速解決。'),
    ('help',      'help',    '求助途徑', '求助途徑 ｜ ' + SITE,
     '樓宇滲漏水聯合處理中心、合資格實體專業檢測、必要仲裁，以及向中心反映時須提供的資料清單。'),
    ('contact',   'contact', '聯絡我們', '聯絡宇見顧問 ｜ ' + SITE,
     '宇見顧問有限公司聯絡方式：電話、WhatsApp、微信、電郵、社交平台與地址，並提供 QR Code。'),
    ('source',    'source',  '資料來源', '資料來源與版權聲明 ｜ ' + SITE,
     '本站內容與圖片的出處、使用性質聲明，以及官方原刊物與專題網頁連結。'),
]

# 章節順序（供頁底「上一頁／下一頁」使用），不包括首頁與資料來源頁
CHAPTERS = ['trilogy', 'flow', 'selfcheck', 'risk', 'detect', 'duty', 'cases', 'help', 'contact']

FAVICON = ("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 32 32'%3E"
           "%3Cpath d='M16 3C11 10 7 15 7 19.5A9 9 0 0 0 25 19.5C25 15 21 10 16 3z' fill='%234fbee8'/%3E%3C/svg%3E")

HEAD = '''<!DOCTYPE html>
<html lang="zh-Hant-MO">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{title}</title>
<meta name="description" content="{desc}">
<meta name="theme-color" content="#1b7fa8">
<meta property="og:title" content="{title}">
<meta property="og:description" content="{desc}">
<meta property="og:type" content="website">
<link rel="icon" href="{favicon}">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Noto+Sans+TC:wght@400;700;900&display=swap" rel="stylesheet">
<link rel="stylesheet" href="assets/css/style.css">
</head>
<body>

<header class="topbar">
  <div class="wrap">
    <a class="brand" href="index.html">
      <svg class="drop" viewBox="0 0 32 32" aria-hidden="true"><path d="M16 3C11 10 7 15 7 19.5A9 9 0 0 0 25 19.5C25 15 21 10 16 3z" fill="#4fbee8"/></svg>
      滲漏水自查互動指南
    </a>
    <nav class="navlinks">
{nav}
    </nav>
  </div>
</header>

<main>
<section id="{slug}" class="{cls}">
{content}
</section>
{pagenav}
</main>

<footer>
  <div class="wrap fgrid">
    <div>
      <p><b style="color:#fff">{site}</b></p>
      <p>
        本網頁內容依據樓宇滲漏水聯合處理中心（由房屋局、土地工務局、衛生局、法務局、市政署組成）出版之
        《處理樓宇滲漏常識》（2023 年 09 月）及同名宣傳單張整理編製，圖片截取自該等公開刊物，版權歸原出版機構所有。
        本站為非牟利公益推廣頁面，並非官方網站 —— 詳見<a href="source.html">資料來源與版權聲明</a>。
      </p>
      <p>
        本工具提供的是<b>參考性的自我檢測指引</b>，不構成專業檢測結論或法律意見。
        正式的滲漏水檢測報告，須由第 9/2023 號法律規範的合資格實體簽發。
      </p>
    </div>
    <div>
      <p><b style="color:#fff">官方求助</b></p>
      <p>樓宇滲漏水聯合處理中心<br>電話：<a href="tel:+85328594875">2859 4875</a><br>電郵：<a href="mailto:CITIA@ihm.gov.mo">CITIA@ihm.gov.mo</a><br>地址：澳門鴨涌馬路 220 號青蔥大廈地下 L</p>
      <p><b style="color:#fff">製作</b><br>宇見顧問有限公司 U Vision Consulting<br>© <span id="year">2026</span></p>
    </div>
  </div>
</footer>

<div class="fab">
  <a class="wa" href="https://wa.me/85366798555" target="_blank" rel="noopener" aria-label="WhatsApp 聯絡宇見顧問">💬</a>
  <a class="tel" href="tel:+85366798555" aria-label="致電宇見顧問">📞</a>
</div>

<script src="assets/js/data.js"></script>
<script src="assets/js/app.js"></script>
</body>
</html>
'''


def nav_html(current):
    out = []
    for slug, _c, label, _t, _d in PAGES:
        cls = []
        if slug == current:
            cls.append('on')
        if slug == 'contact':
            cls.append('cta')
        attr = ' class="%s"' % ' '.join(cls) if cls else ''
        aria = ' aria-current="page"' if slug == current else ''
        out.append('      <a href="%s.html"%s%s>%s</a>' % (slug, attr, aria, label))
    return '\n'.join(out)


def pagenav_html(slug):
    if slug not in CHAPTERS:
        return ''
    i = CHAPTERS.index(slug)
    label = {s: l for s, _c, l, _t, _d in PAGES}
    prev_s = CHAPTERS[i - 1] if i > 0 else 'index'
    next_s = CHAPTERS[i + 1] if i < len(CHAPTERS) - 1 else 'source'
    prev_l = '首頁' if prev_s == 'index' else label[prev_s]
    next_l = '資料來源與版權聲明' if next_s == 'source' else label[next_s]
    return ('<nav class="pagenav"><div class="wrap">'
            '<a class="pn prev" href="%s.html"><span>上一頁</span><b>%s</b></a>'
            '<a class="pn next" href="%s.html"><span>下一頁</span><b>%s</b></a>'
            '</div></nav>') % (prev_s, prev_l, next_s, next_l)


def build():
    for slug, cfile, _label, title, desc in PAGES:
        content = open(os.path.join(ROOT, 'content', cfile + '.html'), encoding='utf-8').read().rstrip()
        html = HEAD.format(
            title=title, desc=desc, favicon=FAVICON, site=SITE,
            nav=nav_html(slug), slug=slug,
            cls='contact' if slug == 'contact' else 'page',
            content=content, pagenav=pagenav_html(slug))
        with io.open(os.path.join(ROOT, slug + '.html'), 'w', encoding='utf-8') as f:
            f.write(html)
        print('built %s.html  (%d bytes)' % (slug, len(html)))


if __name__ == '__main__':
    build()
