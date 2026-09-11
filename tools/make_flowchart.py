#!/usr/bin/env python3
"""產生自製的「處理滲漏水之流程」SVG 流程圖。

流程結構參照樓宇滲漏水聯合處理中心《處理樓宇滲漏常識》P.24 的官方流程，
但版面、圖形、配色及文字排版均為本站自行繪製，不使用原圖。

用法：  python3 tools/make_flowchart.py
輸出：  assets/img/flowchart-redraw.svg
"""
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, 'assets', 'img', 'flowchart-redraw.svg')

W, H = 880, 1150

C = {
    'ink': '#12384b',
    'line': '#7fc4e3',
    'blue': '#1b7fa8',
    'blue_soft': '#e7f6fd',
    'green': '#6aa521',
    'green_soft': '#f0f8e2',
    'coral': '#e08670',
    'amber': '#e0a022',
    'rail': '#9fdcf4',
    'white': '#ffffff',
}

FONT = ("'Noto Sans TC','PingFang TC','Microsoft JhengHei',"
        "'Hiragino Sans TC',system-ui,sans-serif")

parts = []
add = parts.append


def text(x, y, lines, size=17, weight='400', fill=None, anchor='middle', lh=23):
    fill = fill or C['ink']
    start = y - (len(lines) - 1) * lh / 2.0
    spans = ''.join(
        '<tspan x="%g" y="%g">%s</tspan>' % (x, start + i * lh, ln)
        for i, ln in enumerate(lines))
    add('<text x="%g" y="%g" text-anchor="%s" font-size="%g" font-weight="%s" '
        'fill="%s" font-family=%s dominant-baseline="middle">%s</text>'
        % (x, y, anchor, size, weight, fill, '"%s"' % FONT, spans))


def box(cx, cy, w, h, lines, tone='blue', size=17, weight='700'):
    stroke = C['green'] if tone == 'green' else C['blue']
    fill = C['green_soft'] if tone == 'green' else C['white']
    add('<rect x="%g" y="%g" width="%g" height="%g" rx="13" fill="%s" '
        'stroke="%s" stroke-width="2.5"/>'
        % (cx - w / 2, cy - h / 2, w, h, fill, stroke))
    text(cx, cy, lines, size=size, weight=weight)


def pill(cx, cy, w, h, label, color):
    add('<rect x="%g" y="%g" width="%g" height="%g" rx="%g" fill="%s"/>'
        % (cx - w / 2, cy - h / 2, w, h, h / 2, color))
    text(cx, cy, [label], size=21, weight='900', fill=C['white'])


def diamond(cx, cy, rx, ry, lines, size=17):
    pts = '%g,%g %g,%g %g,%g %g,%g' % (cx, cy - ry, cx + rx, cy, cx, cy + ry, cx - rx, cy)
    add('<polygon points="%s" fill="%s" stroke="%s" stroke-width="2.5" '
        'stroke-linejoin="round"/>' % (pts, C['blue_soft'], C['blue']))
    text(cx, cy, lines, size=size, weight='700')


def path(d, arrow=True):
    add('<path d="%s" fill="none" stroke="%s" stroke-width="2.5" '
        'stroke-linecap="round" stroke-linejoin="round"%s/>'
        % (d, C['line'], ' marker-end="url(#ar)"' if arrow else ''))


def tag(cx, cy, label, yes=True):
    color = C['blue'] if yes else C['green']
    add('<circle cx="%g" cy="%g" r="16" fill="%s"/>' % (cx, cy, color))
    text(cx, cy, [label], size=16, weight='900', fill=C['white'])


def rail(y0, y1, label):
    add('<rect x="14" y="%g" width="40" height="%g" rx="12" fill="%s" '
        'fill-opacity="0.45"/>' % (y0, y1 - y0, C['rail']))
    add('<text transform="translate(34,%g) rotate(-90)" text-anchor="middle" '
        'font-size="17" font-weight="900" fill="%s" font-family="%s" '
        'dominant-baseline="middle" letter-spacing="4">%s</text>'
        % ((y0 + y1) / 2, C['blue'], FONT, label))


# ---------------------------------------------------------------- 版面座標
A, B, Cx = 160, 450, 752          # 三條直欄
YES_RAIL = 288                    # 「是」共用回流線
NO_RAIL = 790                     # 「否」繞行線

add('<defs><marker id="ar" viewBox="0 0 10 10" refX="9" refY="5" '
    'markerWidth="7" markerHeight="7" orient="auto-start-reverse">'
    '<path d="M0,0 L10,5 L0,10 z" fill="%s"/></marker></defs>' % C['line'])

rail(24, 290, '自行測試')
rail(298, 940, '提供檢修參考資訊')
rail(948, 1130, '進行檢修')

# ── 一部曲：自行測試 ──────────────────────────────────────────
pill(B, 48, 156, 46, '開始', C['coral'])
path('M%g,71 V%g' % (B, 106))

box(B, 132, 210, 52, ['自行測試'])
path('M%g,158 V%g' % (B, 176))

diamond(B, 230, 132, 54, ['找到', '滲漏源頭'])
tag(B - 34, 300, '是')
path('M%g,284 V%g' % (B, 322))                       # 是：向下
tag(600, 230, '否')
path('M%g,230 H%g V%g' % (B + 132, Cx, 306))         # 否：向右，轉入中心協助欄

# ── 中心協助欄 ───────────────────────────────────────────────
box(Cx, 360, 214, 108, ['反映人準備資料', '並向中心尋求協助'], tone='green', size=16)
path('M%g,414 V%g' % (Cx, 452))
box(Cx, 522, 214, 132, ['經檢測推定', '滲漏源頭後，', '中心呼籲責任人檢修'], tone='green', size=16)
path('M%g,588 V890 H%g' % (Cx, B + 132))             # 併入底部「責任人願意檢修」

# ── 二部曲：提供檢修參考資訊 ──────────────────────────────────
diamond(B, 384, 140, 62, ['源頭', '在反映人單位內'], size=16)
tag(B - 176, 384, '是')
path('M%g,384 H%g V%g' % (B - 140, A, 516))          # 是：向左 → 自行檢修
tag(B + 34, 458, '否')
path('M%g,446 V%g' % (B, 478))                       # 否：向下 → 協商

box(A, 550, 190, 60, ['責任人自行檢修'])
path('M%g,580 V1092 H%g' % (A, B - 84), arrow=False)  # 直落，匯入「完成」

box(B, 512, 232, 60, ['反映人與責任人協商解決'], tone='green')
path('M%g,542 V%g' % (B, 574))

diamond(B, 632, 128, 54, ['責任人願意檢修'], size=16)
tag(B - 166, 632, '是')
path('M%g,632 H%g V1000 H%g' % (B - 128, YES_RAIL, B - 113))  # 是 → 進行檢修
tag(B + 34, 706, '否')
path('M%g,686 V%g' % (B, 722))                       # 否 → 再向中心求助

box(B, 772, 250, 78, ['反映人準備資料並向中心', '尋求協助，中心呼籲責任人檢修'],
    tone='green', size=15)
path('M%g,811 V%g' % (B, 836))

diamond(B, 890, 132, 50, ['責任人願意檢修'], size=16)
tag(B - 170, 890, '是')
path('M%g,890 H%g' % (B - 132, YES_RAIL), arrow=False)
tag(B + 40, 940, '否')
path('M%g,940 V958 H%g V1092 H%g' % (B, NO_RAIL, B + 84))     # 否 → 繞右下方匯入「完成」

# ── 三部曲：進行檢修 ─────────────────────────────────────────
box(B, 1000, 214, 56, ['責任人進行檢修'])
path('M%g,1028 V%g' % (B, 1062))

pill(B, 1092, 156, 46, '完成', C['amber'])

svg = ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 %d %d" '
       'width="100%%" role="img" aria-label="處理滲漏水之流程圖">'
       '<title>處理滲漏水之流程</title>'
       '<rect width="%d" height="%d" fill="#ffffff"/>'
       '<text x="440" y="0" font-size="0"> </text>%s</svg>'
       % (W, H, W, H, ''.join(parts)))

with open(OUT, 'w', encoding='utf-8') as f:
    f.write(svg)
print('wrote %s (%d bytes)' % (OUT, len(svg)))
