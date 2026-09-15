#!/usr/bin/env python3
"""把網站的全部文字抽出成一份可校訂的文檔（Markdown），方便逐段精簡。

來源：
  content/*.html      各頁面的內容片段
  assets/js/data.js   互動自檢的決策樹、求助途徑、反映資料清單

用法：  python3 tools/export_text.py
輸出：  build/網頁全部文字內容.md
"""
import json
import os
import re
import subprocess
from html.parser import HTMLParser

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT_DIR = os.path.join(ROOT, 'build')

# 頁面順序與標題（與 tools/build_pages.py 一致）
PAGES = [
    ('home',    'index.html',     '首頁'),
    ('intro',   'trilogy.html',   '處理滲漏三部曲'),
    ('flow',    'flow.html',      '自行檢測流程圖'),
    ('quiz',    'selfcheck.html', '互動自檢（頁面外框）'),
    ('risk',    'risk.html',      '衛生級別'),
    ('pro',     'detect.html',    '專業現場滲漏檢測'),
    ('duty',    'duty.html',      '業主維修責任'),
    ('cases',   'cases.html',     '成功個案'),
    ('help',    'help.html',      '求助途徑'),
    ('contact', 'contact.html',   '聯絡宇見顧問'),
    ('source',  'source.html',    '資料來源與版權聲明'),
]

BLOCK = {'h1', 'h2', 'h3', 'h4', 'p', 'li', 'figcaption', 'td', 'th', 'a', 'div', 'span'}


class Blocks(HTMLParser):
    """把片段抽成 (種類, 文字) 的清單。"""

    SKIP_CLASSES = ('sec-num', 'step-badge', 'toc-n')

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.out = []
        self.stack = []
        self.buf = []
        self.kind = None
        self.skip = 0
        self.in_toc_b = False

    def _flush(self):
        t = re.sub(r'\s+', ' ', ''.join(self.buf)).strip()
        if t:
            self.out.append((self.kind or 'p', t))
        self.buf = []
        self.kind = None

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        cls = a.get('class', '')
        if self.skip:
            self.skip += 1
            return
        if tag == 'span' and any(c in cls for c in self.SKIP_CLASSES):
            self.skip = 1      # 只略過編號文字，不打斷所在的段落／標題
            return
        if tag == 'img':
            self.out.append(('img', a.get('src', '') + '　｜　alt：' + (a.get('alt') or '（無）')))
            return
        if tag == 'a':
            self.stack.append(cls)
        if tag in ('h1', 'h2', 'h3', 'h4'):
            self._flush()
            self.kind = 'h2' if tag == 'h1' else tag
        elif tag == 'b' and 'toc-card' in ' '.join(self.stack):
            self._flush()
            self.kind = 'h3'
            self.in_toc_b = True
        elif tag == 'li':
            self._flush()
            self.kind = 'li'
        elif tag == 'figcaption' or (tag == 'p' and 'imgsrc' in a.get('class', '')):
            self._flush()
            self.kind = 'caption'
        elif tag == 'p':
            self._flush()
            cls = a.get('class', '')
            self.kind = 'small' if 'small' in cls else 'p'
        elif tag in ('td', 'th'):
            self._flush()
            self.kind = 'cell'
        elif tag == 'div' and 'note' in a.get('class', ''):
            self._flush()
            self.kind = 'note'
        elif tag == 'a' and 'btn' in a.get('class', ''):
            self._flush()
            self.kind = 'btn'

    def handle_endtag(self, tag):
        if self.skip:
            self.skip -= 1
            return
        if tag == 'b':
            if self.in_toc_b:
                self._flush()
                self.in_toc_b = False
        elif tag in ('h1', 'h2', 'h3', 'h4', 'p', 'li', 'figcaption', 'td', 'th', 'div', 'a'):
            self._flush()
        if tag == 'a' and self.stack:
            self.stack.pop()

    def handle_data(self, data):
        if not self.skip:
            self.buf.append(data)


LABEL = {'h2': '大標題', 'h3': '小標題', 'h4': '小標題', 'p': '正文', 'small': '正文（小字）',
         'li': '項目', 'caption': '圖片說明', 'cell': '表格', 'note': '提示框',
         'btn': '按鈕', 'img': '圖片'}


def strip_tags(s):
    return re.sub(r'\s+', ' ', re.sub(r'<[^>]+>', '', s or '')).strip()


def count(s):
    """中文字數（不計空白與標點以外的符號，粗略估算）。"""
    return len(re.sub(r'\s', '', s))


def main():
    os.makedirs(OUT_DIR, exist_ok=True)

    quiz = json.loads(subprocess.check_output(
        ['node', '-e',
         "global.window={};require('./assets/js/data.js');"
         "const d=window.LEAK_DATA;"
         "console.log(JSON.stringify({nodes:d.nodes,HELP:d.HELP,CHECKLIST:d.CHECKLIST,"
         "POSITION_HINT:d.POSITION_HINT}))"],
        cwd=ROOT).decode('utf-8'))

    md = []
    w = md.append
    stats = []

    w('# 澳門樓宇滲漏水自查互動指南 — 網頁全部文字內容')
    w('')
    w('本文檔由 `tools/export_text.py` 自動產生，內容與網站完全一致，供全面精簡校訂之用。')
    w('')
    w('**校訂方法：** 直接在本文檔上刪改。每一段都標明了來源檔案與段落種類，改完交回，我會按標示改回網站。')
    w('')
    w('- 第一部分：各頁面文字（來源 `content/*.html`）')
    w('- 第二部分：互動自檢文字（來源 `assets/js/data.js`）')
    w('- 第三部分：求助途徑與反映資料清單（來源 `assets/js/data.js`）')
    w('')
    w('---')
    w('')

    # ---------------- 第一部分 ----------------
    body = []
    body.append('## 第一部分　各頁面文字')
    body.append('')
    for key, page, title in PAGES:
        path = os.path.join(ROOT, 'content', key + '.html')
        src = open(path, encoding='utf-8').read()
        parser = Blocks()
        parser.feed(src)
        parser._flush()
        chars = sum(count(t) for k, t in parser.out if k != 'img')
        stats.append(('頁面：' + title, page, chars))

        body.append('### %s　`%s`' % (title, page))
        body.append('')
        body.append('> 內容檔：`content/%s.html`　約 %d 字' % (key, chars))
        body.append('')
        for kind, text in parser.out:
            if kind == 'img':
                body.append('- 〔圖片〕`%s`' % text)
            elif kind in ('h2', 'h3', 'h4'):
                body.append('**〔%s〕%s**' % (LABEL[kind], text))
                body.append('')
            else:
                body.append('〔%s〕%s' % (LABEL.get(kind, kind), text))
                body.append('')
        body.append('---')
        body.append('')

    # ---------------- 第二部分 ----------------
    KIND = {'question': '提問', 'test': '動手測試', 'result': '結論'}
    body.append('## 第二部分　互動自檢文字')
    body.append('')
    body.append('共 %d 個節點。每個節點的標題、引言、圖片說明、注意事項、操作步驟與選項，'
                '都可以獨立刪改。' % len(quiz['nodes']))
    body.append('')

    order = ['q_symptom', 't_observe', 'q_pos_supply', 't_supply', 'q_supply_negative',
             'q_pos_drain', 't_drain', 'q_blockage']
    rest = [k for k in quiz['nodes'] if k not in order]
    total_quiz = 0

    for nid in order + rest:
        n = quiz['nodes'][nid]
        texts = []
        body.append('### 〔%s〕%s' % (KIND.get(n['kind'], n['kind']), strip_tags(n.get('title', ''))))
        body.append('')
        body.append('> 節點代號：`%s`' % nid)
        body.append('')
        texts.append(n.get('title', ''))

        if n.get('verdict'):
            body.append('〔結論標籤〕%s' % strip_tags(n['verdict']))
            body.append('')
        for field, label in (('lead', '引言'), ('summary', '結論摘要'), ('urgent', '提醒')):
            if n.get(field):
                body.append('〔%s〕%s' % (label, strip_tags(n[field])))
                body.append('')
                texts.append(n[field])
        if n.get('img'):
            body.append('- 〔圖片〕`%s`' % n['img'].get('src', ''))
            body.append('- 〔圖片說明〕%s' % strip_tags(n['img'].get('caption', '')))
            body.append('')
            texts.append(n['img'].get('caption', ''))
        for s in n.get('howto', []):
            body.append('〔操作步驟〕%s' % strip_tags(s))
            texts.append(s)
        if n.get('howto'):
            body.append('')
        for note in n.get('notes', []):
            body.append('〔注意事項〕%s' % strip_tags(note.get('html', '')))
            texts.append(note.get('html', ''))
        if n.get('notes'):
            body.append('')
        for field, label in (('cause', '常見成因'), ('actions', '建議下一步')):
            for item in n.get(field, []):
                body.append('〔%s〕%s' % (label, strip_tags(item)))
                texts.append(item)
            if n.get(field):
                body.append('')
        for i, o in enumerate(n.get('options', []), 1):
            tagtxt = ('（%s）' % o['tag']) if o.get('tag') else ''
            body.append('**〔選項 %d〕%s%s**' % (i, tagtxt, strip_tags(o['label'])))
            body.append('')
            body.append('〔選項說明〕%s' % strip_tags(o['desc']))
            body.append('')
            texts.append(o['label'])
            texts.append(o['desc'])
        chars = sum(count(strip_tags(t)) for t in texts)
        total_quiz += chars
        body.append('> 本節點約 %d 字' % chars)
        body.append('')
        body.append('---')
        body.append('')

    stats.append(('互動自檢', 'assets/js/data.js（%d 個節點）' % len(quiz['nodes']), total_quiz))

    # ---------------- 第三部分 ----------------
    body.append('## 第三部分　求助途徑與反映資料清單')
    body.append('')
    help_chars = 0
    for c in quiz['HELP']:
        body.append('### %s' % strip_tags(c['title']))
        body.append('')
        body.append('〔分段標籤〕%s' % strip_tags(c['tag']))
        body.append('')
        body.append('〔內文〕%s' % strip_tags(c['body']))
        body.append('')
        for l in c['lines']:
            body.append('〔資料行〕%s：%s' % (strip_tags(l['k']), strip_tags(l['v'])))
        body.append('')
        if c.get('foot'):
            body.append('〔附註〕%s' % strip_tags(c['foot']))
            body.append('')
        help_chars += count(strip_tags(c['title'] + c['body'] + (c.get('foot') or '')))
    body.append('### 向中心反映時須提供的資料（%d 項）' % len(quiz['CHECKLIST']))
    body.append('')
    for i, c in enumerate(quiz['CHECKLIST'], 1):
        body.append('%d. %s' % (i, strip_tags(c)))
        help_chars += count(strip_tags(c))
    body.append('')
    stats.append(('求助途徑與清單', 'assets/js/data.js', help_chars))

    # ---------------- 字數總表（放在最前） ----------------
    w('## 字數概覽（精簡時可按此決定下刀位置）')
    w('')
    w('| 區塊 | 來源 | 約字數 |')
    w('|---|---|---|')
    for name, src, chars in stats:
        w('| %s | `%s` | %s |' % (name, src, format(chars, ',')))
    w('| **合計** | | **%s** |' % format(sum(s[2] for s in stats), ','))
    w('')
    w('---')
    w('')

    md.extend(body)

    out = os.path.join(OUT_DIR, '網頁全部文字內容.md')
    with open(out, 'w', encoding='utf-8') as f:
        f.write('\n'.join(md))
    print('wrote %s (%d bytes, 合計約 %d 字)' % (out, os.path.getsize(out), sum(s[2] for s in stats)))


if __name__ == '__main__':
    main()
