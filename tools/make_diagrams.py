#!/usr/bin/env python3
"""產生「3 分鐘初步自診」三張滲漏水路示意圖（SVG）。

用意：相片只影到一撻水漬，示意圖可以畫出「水點解會去到嗰度」，
      讀者對照的是水路而非外觀，判斷準確得多。

配色與線條依據宇見顧問《品牌手冊》v1.0：只用指定色票、平面無陰影、
線寬一致、不使用指南星或任何星形／羅盤符號。

用法：  python3 tools/make_diagrams.py
輸出：  assets/img/diagram-1.svg  供水管滲漏
        assets/img/diagram-2.svg  去水管／地台防水層滲漏
        assets/img/diagram-3.svg  外牆、窗框與冷氣凝結水
"""
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, 'assets', 'img')

C = {
    'blue': '#385890',    # U VISION BLUE
    'navy': '#183C70',    # DEEP NAVY
    'mid': '#6F8FB8',     # VISION MID
    'sky': '#DCE8F4',     # CLEAR SKY
    'ink': '#243447',     # INK
    'mist': '#F2F6FA',    # MIST
    'white': '#FFFFFF',
}
FONT = ("'Noto Sans TC','PingFang TC','Microsoft JhengHei',"
        "'Hiragino Sans TC',system-ui,sans-serif")

W, H = 640, 380


def esc(s):
    return (s.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;'))


class Svg:
    def __init__(self, title):
        self.p = []
        self.title = title

    def add(self, s):
        self.p.append(s)

    # ---- 基本圖形 ----
    def rect(self, x, y, w, h, fill='none', stroke=None, sw=2, rx=0, op=None):
        s = '<rect x="%g" y="%g" width="%g" height="%g" rx="%g" fill="%s"' % (x, y, w, h, rx, fill)
        if op is not None:
            s += ' fill-opacity="%g"' % op
        if stroke:
            s += ' stroke="%s" stroke-width="%g"' % (stroke, sw)
        self.add(s + '/>')

    def line(self, x1, y1, x2, y2, stroke=None, sw=2, dash=None, cap='round'):
        s = ('<line x1="%g" y1="%g" x2="%g" y2="%g" stroke="%s" stroke-width="%g" '
             'stroke-linecap="%s"' % (x1, y1, x2, y2, stroke or C['mid'], sw, cap))
        if dash:
            s += ' stroke-dasharray="%s"' % dash
        self.add(s + '/>')

    def path(self, d, stroke=None, sw=2, fill='none', dash=None, arrow=False, op=None):
        s = ('<path d="%s" fill="%s" stroke="%s" stroke-width="%g" '
             'stroke-linecap="round" stroke-linejoin="round"'
             % (d, fill, stroke or C['mid'], sw))
        if dash:
            s += ' stroke-dasharray="%s"' % dash
        if op is not None:
            s += ' stroke-opacity="%g"' % op
        if arrow:
            s += ' marker-end="url(#ar)"'
        self.add(s + '/>')

    def ellipse(self, cx, cy, rx, ry, fill, op=1.0):
        self.add('<ellipse cx="%g" cy="%g" rx="%g" ry="%g" fill="%s" fill-opacity="%g"/>'
                 % (cx, cy, rx, ry, fill, op))

    def circle(self, cx, cy, r, fill='none', stroke=None, sw=2, dash=None):
        s = '<circle cx="%g" cy="%g" r="%g" fill="%s"' % (cx, cy, r, fill)
        if stroke:
            s += ' stroke="%s" stroke-width="%g"' % (stroke, sw)
        if dash:
            s += ' stroke-dasharray="%s"' % dash
        self.add(s + '/>')

    def text(self, x, y, s, size=14, fill=None, weight='500', anchor='start', ls=0):
        self.add('<text x="%g" y="%g" font-family=%s font-size="%g" font-weight="%s" '
                 'fill="%s" text-anchor="%s" letter-spacing="%g">%s</text>'
                 % (x, y, '"%s"' % FONT, size, weight, fill or C['ink'], anchor, ls, esc(s)))

    def drop(self, cx, cy, s=1.0, fill=None, op=1.0):
        """一滴水（上尖下圓）。"""
        r = 5 * s
        d = ('M%g,%g C%g,%g %g,%g %g,%g C%g,%g %g,%g %g,%g Z'
             % (cx, cy - 2.2 * r,
                cx + 0.9 * r, cy - 0.6 * r, cx + r, cy + 0.15 * r, cx, cy + 1.2 * r,
                cx - r, cy + 0.15 * r, cx - 0.9 * r, cy - 0.6 * r, cx, cy - 2.2 * r))
        self.add('<path d="%s" fill="%s" fill-opacity="%g"/>' % (d, fill or C['blue'], op))

    def tag(self, x, y, s, size=15, anchor='start', fill=None):
        """細標籤文字。"""
        self.text(x, y, s, size=size, fill=fill or C['blue'], weight='600', anchor=anchor)

    def render(self):
        return ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 %d %d" width="100%%" '
                'role="img" aria-label="%s"><title>%s</title>'
                '<defs><marker id="ar" viewBox="0 0 10 10" refX="8" refY="5" '
                'markerWidth="6" markerHeight="6" orient="auto-start-reverse">'
                '<path d="M0,0 L10,5 L0,10 z" fill="%s"/></marker></defs>'
                '<rect width="%d" height="%d" rx="4" fill="%s"/>%s</svg>'
                % (W, H, esc(self.title), esc(self.title), C['blue'], W, H, C['mist'],
                   ''.join(self.p)))


# ---------------------------------------------------------------- 共用構件
def two_floors(s, upper_label='樓上單位', lower_label='你的單位'):
    """畫一個兩層樓的剖面：上層、樓板、下層。"""
    x0, x1 = 44, 596
    top, slab_y, slab_h, bot = 34, 178, 26, 322
    # 外框
    s.rect(x0, top, x1 - x0, bot - top, fill=C['white'], stroke=C['mid'], sw=2, rx=3)
    # 樓板
    s.rect(x0, slab_y, x1 - x0, slab_h, fill=C['sky'])
    s.line(x0, slab_y, x1, slab_y, C['mid'], 2, cap='butt')
    s.line(x0, slab_y + slab_h, x1, slab_y + slab_h, C['mid'], 2, cap='butt')
    # 樓層標示
    s.text(x0 + 14, top + 26, upper_label, size=15, fill=C['mid'], weight='600')
    s.text(x0 + 14, slab_y + slab_h + 28, lower_label, size=15, fill=C['navy'], weight='700')
    return x0, x1, top, slab_y, slab_h, bot


def wet_patch(s, cx, cy, rx=58):
    """下層天花的濕痕。"""
    s.ellipse(cx, cy, rx, 11, C['blue'], 0.20)
    s.ellipse(cx, cy, rx * 0.6, 7, C['blue'], 0.28)


def falling_drops(s, cx, y0, n=3, gap=34, s0=1.0):
    for i in range(n):
        s.drop(cx, y0 + i * gap, s0 - i * 0.12, op=0.85 - i * 0.16)


def caption(s, text):
    """圖底的一句判讀提示。"""
    s.rect(44, 336, 552, 30, fill=C['sky'], rx=3)
    s.text(320, 356, text, size=16, fill=C['navy'], weight='600', anchor='middle')


# ---------------------------------------------------------------- 圖一：供水管
def diagram_1():
    s = Svg('供水管滲漏示意圖：樓上或牆內供水管長期有水壓，破裂後全日不停滴水')
    x0, x1, top, slab_y, slab_h, bot = two_floors(s)
    mid_y = slab_y + slab_h / 2
    brk = 372

    # 供水立管（由上而下）＋ 橫喉（埋在樓板內）
    s.path('M150,%g V%g' % (top + 16, mid_y), stroke=C['blue'], sw=7)
    s.path('M150,%g H%g' % (mid_y, 520), stroke=C['blue'], sw=7)
    # 水掣
    s.circle(150, top + 52, 9, fill=C['white'], stroke=C['blue'], sw=3)

    # 破裂點
    s.circle(brk, mid_y, 17, fill='none', stroke=C['navy'], sw=2, dash='4 4')
    s.line(brk - 6, mid_y - 6, brk + 6, mid_y + 6, C['navy'], 2.5)
    s.line(brk + 6, mid_y - 6, brk - 6, mid_y + 6, C['navy'], 2.5)

    wet_patch(s, brk, slab_y + slab_h + 6)
    falling_drops(s, brk, slab_y + slab_h + 34, n=3, gap=36)

    # 標籤
    s.tag(168, top + 44, '供水管（長期有水壓）')
    s.line(brk + 20, mid_y - 10, 470, 128, C['navy'], 1.5, dash='3 3')
    s.tag(474, 126, '破裂點', fill=C['navy'])
    s.tag(x0 + 14, bot - 16, '天花出現持續水痕', fill=C['blue'])

    caption(s, '全日不停・水質清澈・無異味')
    return s


# ---------------------------------------------------------------- 圖二：去水／地台
def diagram_2():
    s = Svg('去水管與地台防水層滲漏示意圖：樓上用水後，水經破損的防水層或去水喉接口滲落下層')
    x0, x1, top, slab_y, slab_h, bot = two_floors(s)
    mid_y = slab_y + slab_h / 2

    # 上層：花灑
    s.path('M186,%g V%g' % (top + 16, top + 38), stroke=C['mid'], sw=4)
    s.path('M166,%g H206' % (top + 38), stroke=C['mid'], sw=5)
    for dx in (-13, 0, 13):
        s.path('M%g,%g L%g,%g' % (186 + dx, top + 48, 186 + dx * 1.6, top + 88),
               stroke=C['blue'], sw=2.5, op=0.75)
    s.tag(222, top + 44, '樓上用水')

    # 地台防水層（中間有缺口＝破損）
    wp = slab_y - 16
    s.line(x0 + 8, wp, 286, wp, C['mid'], 3.5)
    s.line(334, wp, 424, wp, C['mid'], 3.5)
    s.line(486, wp, x1 - 8, wp, C['mid'], 3.5)
    s.tag(x0 + 14, wp - 12, '地台防水層')

    # 破損缺口
    s.circle(310, wp, 18, fill='none', stroke=C['navy'], sw=2, dash='4 4')
    s.path('M310,%g V%g' % (wp + 6, slab_y + slab_h - 2), stroke=C['blue'], sw=2.5, arrow=True)

    # 去水口與去水喉：垂直穿過樓板後轉橫
    s.rect(432, wp - 10, 46, 10, fill=C['white'], stroke=C['mid'], sw=2, rx=2)
    s.path('M455,%g V%g H%g' % (wp, mid_y + 4, 548), stroke=C['blue'], sw=7)
    s.circle(455, mid_y + 4, 16, fill='none', stroke=C['navy'], sw=2, dash='4 4')
    s.tag(492, wp - 12, '去水喉接口')

    # 兩處滲水
    wet_patch(s, 310, slab_y + slab_h + 6, rx=46)
    falling_drops(s, 310, slab_y + slab_h + 34, n=3, gap=32)
    wet_patch(s, 455, slab_y + slab_h + 6, rx=40)
    falling_drops(s, 455, slab_y + slab_h + 34, n=2, gap=32, s0=0.85)

    s.tag(x0 + 14, bot - 16, '用水後水痕擴大', fill=C['blue'])

    caption(s, '沖涼、洗碗或沖廁後明顯加劇')
    return s


# ---------------------------------------------------------------- 圖三：外牆／窗／冷氣
def diagram_3():
    s = Svg('外牆、窗框與冷氣凝結水示意圖：雨水由外牆裂紋或窗框膠位滲入，冷氣則產生凝結水')
    x0, x1 = 44, 596
    top, bot = 34, 322
    wall_x, wall_w = 150, 50

    # 整幅剖面：室外｜外牆｜室內
    s.rect(x0, top, x1 - x0, bot - top, fill=C['white'], stroke=C['mid'], sw=2, rx=3)
    s.rect(x0, top, wall_x - x0, bot - top, fill=C['mist'])
    s.rect(wall_x, top, wall_w, bot - top, fill=C['sky'])
    s.line(wall_x, top, wall_x, bot, C['mid'], 2, cap='butt')
    s.line(wall_x + wall_w, top, wall_x + wall_w, bot, C['mid'], 2, cap='butt')

    s.text(x0 + 12, top + 24, '室外（落雨）', size=15, fill=C['mid'], weight='600')
    s.text(wall_x + 7, top + 24, '外牆', size=15, fill=C['mid'], weight='600')
    s.text(x1 - 14, top + 24, '室內', size=15, fill=C['navy'], weight='700', anchor='end')

    # 落雨
    for i in range(6):
        y = 74 + i * 38
        s.path('M%g,%g L%g,%g' % (62 + (i % 3) * 22, y, 74 + (i % 3) * 22, y + 22),
               stroke=C['mid'], sw=2.5, op=0.55)

    # 外牆微裂紋 → 滲入室內
    s.path('M%g,110 l11,15 l-8,12 l12,14 l-7,12' % (wall_x + 10), stroke=C['navy'], sw=2.4)
    s.line(wall_x + 34, 126, 268, 98, C['navy'], 1.5, dash='3 3')
    s.tag(272, 96, '外牆微裂紋', fill=C['navy'])
    s.ellipse(wall_x + wall_w + 13, 182, 13, 46, C['blue'], 0.22)
    s.path('M%g,146 C%g,152 %g,158 %g,162'
           % (wall_x + wall_w + 1, wall_x + wall_w + 6, wall_x + wall_w + 10, wall_x + wall_w + 13),
           stroke=C['blue'], sw=2.5, arrow=True)

    # 窗 + 窗邊膠位
    win_y0, win_y1 = 224, 292
    s.rect(wall_x + 5, win_y0, wall_w - 10, win_y1 - win_y0, fill=C['white'],
           stroke=C['mid'], sw=2, rx=2)
    s.line(wall_x + 5, (win_y0 + win_y1) / 2, wall_x + wall_w - 5, (win_y0 + win_y1) / 2,
           C['mid'], 1.5)
    s.line(wall_x + wall_w - 5, win_y0, wall_x + wall_w - 5, win_y1, C['navy'], 3.5, dash='6 4')
    s.line(wall_x + wall_w + 6, win_y1 - 14, 288, 288, C['navy'], 1.5, dash='3 3')
    s.tag(292, 292, '窗框密封膠老化', fill=C['navy'])
    s.drop(wall_x + wall_w + 14, win_y1 - 2, 0.9, op=0.8)
    s.drop(wall_x + wall_w + 14, win_y1 + 18, 0.75, op=0.6)

    # 冷氣機與凝結水
    ac_x, ac_y = 430, 108
    s.tag(ac_x, ac_y - 12, '冷氣凝結水或去水喉')
    s.rect(ac_x, ac_y, 120, 38, fill=C['white'], stroke=C['mid'], sw=2, rx=4)
    for i in range(3):
        s.line(ac_x + 18 + i * 30, ac_y + 25, ac_x + 34 + i * 30, ac_y + 25, C['mid'], 2.5)
    s.path('M%g,%g V%g' % (ac_x + 98, ac_y + 38, ac_y + 78), stroke=C['blue'], sw=4)
    s.drop(ac_x + 98, ac_y + 96, 0.9, op=0.8)
    s.drop(ac_x + 98, ac_y + 118, 0.75, op=0.6)
    s.ellipse(ac_x + 98, bot - 18, 36, 9, C['blue'], 0.20)

    caption(s, '落大雨、起風或開冷氣時才出現')
    return s


def main():
    os.makedirs(OUT, exist_ok=True)
    for i, fn in enumerate((diagram_1, diagram_2, diagram_3), 1):
        svg = fn().render()
        p = os.path.join(OUT, 'diagram-%d.svg' % i)
        with open(p, 'w', encoding='utf-8') as f:
            f.write(svg)
        print('wrote %s (%d bytes)' % (p, len(svg)))


if __name__ == '__main__':
    main()
