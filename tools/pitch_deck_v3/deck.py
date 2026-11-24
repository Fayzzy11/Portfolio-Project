"""Thoth Ledger stock-pitch deck, version 3 (24 Nov 2026).

Same storyline as the final Intel course deck (Doose & Endrizzi): claim on the cover, the call with three
pillars, the environment, where we differ, a catalyst timeline, the key catalyst, the numbers, relative value,
the valuation with a sensitivity grid, risks against scenarios, the conclusion and sources.
Layout only; the content of each pitch lives in specs/<CODE>.py (English and French side by side) and every
valuation number is computed in valmath.py from site/data/pitches.json.

    python3 tools/pitch_deck_v3/deck.py <out_dir> [CODE ...]
"""
import importlib.util
import re
import sys
from pathlib import Path

from pptx import Presentation
from pptx.chart.data import CategoryChartData
from pptx.dml.color import RGBColor
from pptx.enum.chart import XL_CHART_TYPE, XL_LEGEND_POSITION, XL_LABEL_POSITION, XL_TICK_LABEL_POSITION
from pptx.enum.shapes import MSO_SHAPE, MSO_CONNECTOR
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.oxml.ns import qn
from pptx.util import Inches, Pt

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import valmath as vm  # noqa: E402

ROOT = vm.ROOT
LOGO_DARK = ROOT / "site/static/brand/mark_256.png"
LOGO_LIGHT = ROOT / "site/static/brand/mark_256_light.png"
PITCHES = vm.PITCHES

NAVY, NAVY2, NAVY3, GOLD, GOLDINK, CREAM, BG, LINE = "0A1A30", "1B3358", "13294A", "B58F55", "7B5A2A", "F6F2EA", "F8F5EF", "E5DCCB"
SLATE, MUTED, RED, REDSOFT, GREEN, GREENSOFT, WHITE, GREY = "5A6372", "B8C0CC", "A33A2B", "F7E6E1", "2E6B4E", "E3EEE7", "FFFFFF", "9AA1AB"
RATING_FILL = {"Overweight": GREEN, "Neutral": GOLDINK, "Underweight": RED, "Sell": RED}
RATING_INK = {"Overweight": "9BD3B4", "Neutral": "E6C98F", "Underweight": "F0A39A", "Sell": "F0A39A"}
RGB = RGBColor.from_string
SERIF, SANS = "Georgia", "Arial"
NB = " "


def fr_typo(s):
    """French typography: no line break before % : ; ? ! or a currency unit, nor after < > ≥ ≤."""
    s = re.sub(r"(\d) (%|€|Md€|M€|Md\$|M\$|\$|¥|pb|pt|pts|x\b)", "\\1\u00a0\\2", s)
    s = re.sub(r" ([:;?!»])", "\u00a0\\1", s)
    s = re.sub(r"([<>≥≤«]) ", "\\1\u00a0", s)
    s = re.sub(r"(\d) (\d{3})\b", "\\1\u00a0\\2", s)
    return s


class Ctx:
    def __init__(self, lang):
        self.lang = lang

    def __call__(self, x):
        if isinstance(x, tuple) and len(x) == 2 and all(isinstance(i, str) for i in x):
            return x[0] if self.lang == "en" else fr_typo(x[1])
        if isinstance(x, (list, tuple)):
            return [self(i) for i in x]
        if isinstance(x, dict):
            return {k: self(v) for k, v in x.items()}
        return x


# ------------------------------------------------------------------ number formats
def num(x, d, lang):
    s = f"{x:,.{d}f}"
    if lang == "fr":
        s = s.replace(",", NB).replace(".", ",")
    return s


def money(sym, x, lang, d=None):
    if d is None:
        d = 0 if abs(x) >= 1000 else (1 if abs(x) >= 100 else 2)
    n = num(x, d, lang)
    if lang == "fr":
        return f"{n}{NB}{sym.replace('US$', '$US').replace('HK$', '$HK')}"
    return f"{sym}{n}"


def pct(x, d, lang, sign=False):
    s = num(abs(x) * 100, d, lang) + (NB + "%" if lang == "fr" else "%")
    if sign:
        s = ("+" if x >= 0 else "−") + s
    elif x < 0:
        s = "−" + s
    return s


# ------------------------------------------------------------------ primitives
def fit(s, size, limit=7):
    n = len(s)
    return size if n <= limit else (round(size * 0.8) if n <= limit + 3 else round(size * 0.64))


def text(sl, x, y, w, h, t, sz=14, color=NAVY, bold=False, align=None, anchor=MSO_ANCHOR.TOP, font=SANS, italic=False, spacing=None, lsp=None):
    s = sl.shapes.add_textbox(Inches(x), Inches(y), Inches(w), Inches(h))
    tf = s.text_frame
    tf.word_wrap = True
    tf.margin_left = tf.margin_right = tf.margin_top = tf.margin_bottom = 0
    tf.vertical_anchor = anchor
    paras = t if isinstance(t, list) else [t]
    for i, para in enumerate(paras):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        if align is not None:
            p.alignment = align
        if i and spacing:
            p.space_before = Pt(spacing)
        if lsp:
            p.line_spacing = lsp
        runs = para if isinstance(para, list) else [(para, bold)]
        for run in runs:
            rt, rb = run[0], run[1]
            rc = run[2] if len(run) > 2 else color
            r = p.add_run()
            r.text = rt
            f = r.font
            f.size = Pt(sz)
            f.bold = rb
            f.italic = italic
            f.color.rgb = RGB(rc)
            f.name = font
    return s


def rect(sl, x, y, w, h, fill, line=None, round_=True, adj=0.06, lw=0.75):
    s = sl.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE if round_ else MSO_SHAPE.RECTANGLE, Inches(x), Inches(y), Inches(w), Inches(h))
    s.fill.solid()
    s.fill.fore_color.rgb = RGB(fill)
    s.shadow.inherit = False
    if line:
        s.line.color.rgb = RGB(line)
        s.line.width = Pt(lw)
    else:
        s.line.fill.background()
    if round_:
        s.adjustments[0] = adj
    return s


def dot(sl, x, y, d, fill, label=None, sz=13, color=WHITE):
    s = sl.shapes.add_shape(MSO_SHAPE.OVAL, Inches(x), Inches(y), Inches(d), Inches(d))
    s.fill.solid()
    s.fill.fore_color.rgb = RGB(fill)
    s.line.fill.background()
    s.shadow.inherit = False
    if label is not None:
        text(sl, x, y, d, d, str(label), sz, color, True, PP_ALIGN.CENTER, MSO_ANCHOR.MIDDLE)


def line(sl, x1, y1, x2, y2, color=LINE, w=1.5, dash=False):
    c = sl.shapes.add_connector(MSO_CONNECTOR.STRAIGHT, Inches(x1), Inches(y1), Inches(x2), Inches(y2))
    c.line.color.rgb = RGB(color)
    c.line.width = Pt(w)
    if dash:
        c.line.dash_style = 4
    return c


def arrow(sl, x, y, up=False, good=False):
    a = sl.shapes.add_shape(MSO_SHAPE.UP_ARROW if up else MSO_SHAPE.DOWN_ARROW, Inches(x), Inches(y), Inches(0.2), Inches(0.26))
    a.fill.solid()
    a.fill.fore_color.rgb = RGB(GREEN if good else RED)
    a.line.fill.background()
    a.shadow.inherit = False


def chart_style(ch, legend=False, sz=11):
    ch.font.size = Pt(sz)
    ch.font.name = SANS
    ch.font.color.rgb = RGB(NAVY)
    ch.has_legend = legend
    if legend:
        ch.legend.position = XL_LEGEND_POSITION.BOTTOM
        ch.legend.include_in_layout = False
        ch.legend.font.size = Pt(sz)
    va = ch.value_axis
    va.has_major_gridlines = True
    va.major_gridlines.format.line.color.rgb = RGB("ECE6DA")
    va.format.line.fill.background()
    va.tick_labels.font.size = Pt(sz - 1)
    va.tick_labels.font.color.rgb = RGB(SLATE)
    ca = ch.category_axis
    ca.format.line.color.rgb = RGB(GREY)
    ca.tick_labels.font.size = Pt(sz - 1)
    ca.has_major_gridlines = False
    ca.tick_label_position = XL_TICK_LABEL_POSITION.LOW


def chart_title(ch, t, sz=12):
    ch.has_title = True
    tf = ch.chart_title.text_frame
    tf.text = t
    r = tf.paragraphs[0].runs[0]
    r.font.size = Pt(sz)
    r.font.bold = True
    r.font.color.rgb = RGB(NAVY)
    r.font.name = SANS


def fill_series(s, col):
    s.format.fill.solid()
    s.format.fill.fore_color.rgb = RGB(col)
    s.invert_if_negative = False


def data_labels(plot, fmt='0.0', sz=11, pos=XL_LABEL_POSITION.OUTSIDE_END):
    plot.has_data_labels = True
    dl = plot.data_labels
    dl.font.size = Pt(sz)
    dl.font.bold = True
    dl.number_format = fmt
    dl.number_format_is_linked = False
    dl.position = pos


def bar_chart(sl, x, y, w, h, title, cats, series, colors, fmt, point_colors=None, legend=None, horizontal=False, sz=11):
    cd = CategoryChartData()
    cd.categories = cats
    for nm, vals in series:
        cd.add_series(nm, vals)
    kind = XL_CHART_TYPE.BAR_CLUSTERED if horizontal else XL_CHART_TYPE.COLUMN_CLUSTERED
    ch = sl.shapes.add_chart(kind, Inches(x), Inches(y), Inches(w), Inches(h), cd).chart
    chart_style(ch, legend=len(series) > 1 if legend is None else legend, sz=sz)
    chart_title(ch, title)
    for s_, col in zip(ch.plots[0].series, colors):
        fill_series(s_, col)
    if point_colors:
        for i, col in enumerate(point_colors):
            if col:
                pt = ch.plots[0].series[0].points[i]
                pt.format.fill.solid()
                pt.format.fill.fore_color.rgb = RGB(col)
    data_labels(ch.plots[0], fmt, sz)
    ch.plots[0].gap_width = 60
    if horizontal:
        ch.category_axis.reverse_order = True
        ch.value_axis.visible = False
        ch.value_axis.has_major_gridlines = False
    return ch


def cell_border(c, color=LINE, bottom_only=True):
    tcPr = c._tc.get_or_add_tcPr()
    for ln in ("a:lnL", "a:lnR", "a:lnT", "a:lnB"):
        e = tcPr.find(qn(ln))
        if e is None:
            e = tcPr.makeelement(qn(ln), {})
            tcPr.insert(0, e)
        for ch in list(e):
            e.remove(ch)
        on = ln == "a:lnB" or not bottom_only
        e.set("w", "6350" if on else "0")
        if on:
            sf = e.makeelement(qn("a:solidFill"), {})
            sf.append(sf.makeelement(qn("a:srgbClr"), {"val": color}))
            e.append(sf)
        else:
            e.append(e.makeelement(qn("a:noFill"), {}))


def table(sl, x, y, w, rows, widths, sz=12, rh=0.42, hl=(), fills=None, bold_cells=(), colors=None, aligns=None, head=True):
    nr, nc = len(rows), len(rows[0])
    gs = sl.shapes.add_table(nr, nc, Inches(x), Inches(y), Inches(w), Inches(rh * nr))
    t = gs.table
    tblPr = gs._element.graphic.graphicData.tbl.tblPr
    for a in ("firstRow", "bandRow"):
        tblPr.set(a, "0")
    for j, wd in enumerate(widths):
        t.columns[j].width = Inches(wd)
    for i in range(nr):
        t.rows[i].height = Inches(rh)
        for j in range(nc):
            c = t.cell(i, j)
            c.margin_left = c.margin_right = Inches(0.08)
            c.margin_top = c.margin_bottom = Inches(0.02)
            c.vertical_anchor = MSO_ANCHOR.MIDDLE
            fill = NAVY if (head and i == 0) else ("EFE3CC" if i in hl else (CREAM if j == 0 else WHITE))
            if fills and fills.get((i, j)):
                fill = fills[(i, j)]
            c.fill.solid()
            c.fill.fore_color.rgb = RGB(fill)
            p = c.text_frame.paragraphs[0]
            c.text_frame.word_wrap = True
            p.alignment = aligns[j] if aligns else (PP_ALIGN.LEFT if j == 0 else PP_ALIGN.RIGHT)
            r = p.add_run()
            r.text = str(rows[i][j])
            f = r.font
            f.name = SANS
            f.size = Pt(sz)
            f.bold = (head and i == 0) or j == 0 or i in hl or (i, j) in bold_cells
            col = WHITE if (head and i == 0) else NAVY
            if colors and colors.get((i, j)):
                col = colors[(i, j)]
            f.color.rgb = RGB(col)
            cell_border(c)
    return gs


# ------------------------------------------------------------------ the deck
class Deck:
    def __init__(self, spec, lang):
        self.t, self.lang = Ctx(lang), lang
        self.S = self.t(spec)
        self.P = PITCHES[spec["code"]]
        self.prs = Presentation()
        self.prs.slide_width = Inches(13.333)
        self.prs.slide_height = Inches(7.5)
        self.blank = self.prs.slide_layouts[6]
        self.n = 0

    # frame -------------------------------------------------------------
    def footer(self, sl, dark=False):
        S = self.S
        line(sl, 0.6, 7.0, 12.73, 7.0, "2A4066" if dark else LINE, 0.75)
        text(sl, 0.6, 7.06, 11.0, 0.24, S["footer"], 8.5, MUTED if dark else SLATE, anchor=MSO_ANCHOR.MIDDLE)
        text(sl, 12.13, 7.06, 0.6, 0.24, str(self.n), 8.5, MUTED if dark else SLATE, align=PP_ALIGN.RIGHT, anchor=MSO_ANCHOR.MIDDLE)

    def slide(self, title):
        self.n += 1
        sl = self.prs.slides.add_slide(self.blank)
        bg = sl.background.fill
        bg.solid()
        bg.fore_color.rgb = RGB(BG)
        text(sl, 0.6, 0.32, 11.25, 0.95, title, 23 if len(title) <= 92 else (20 if len(title) <= 112 else 18), NAVY, True, font=SERIF, anchor=MSO_ANCHOR.MIDDLE, lsp=0.95)
        sl.shapes.add_picture(str(LOGO_DARK), Inches(12.18), Inches(0.36), Inches(0.55), Inches(0.55))
        self.footer(sl)
        return sl

    def dark(self):
        self.n += 1
        sl = self.prs.slides.add_slide(self.blank)
        bg = sl.background.fill
        bg.solid()
        bg.fore_color.rgb = RGB(NAVY)
        sl.shapes.add_picture(str(LOGO_LIGHT), Inches(11.85), Inches(0.5), Inches(0.9), Inches(0.9))
        return sl

    def card(self, sl, x, y, w, h, fill=WHITE, border=LINE):
        return rect(sl, x, y, w, h, fill, border, adj=0.05)

    def source(self, sl, s, y=6.66):
        if s:
            text(sl, 0.6, y, 12.13, 0.26, s, 8.5, SLATE, italic=True, anchor=MSO_ANCHOR.MIDDLE)

    # 1 cover ------------------------------------------------------------
    def cover(self):
        S, P = self.S, self.P
        sl = self.dark()
        text(sl, 0.75, 0.62, 10.5, 0.7, S["company"], 30 if len(S["company"]) <= 24 else 24, WHITE, True, font=SERIF, anchor=MSO_ANCHOR.MIDDLE)
        text(sl, 0.75, 1.5, 10.8, 0.3, S["kicker"].upper(), 11.5, GOLD, True)
        text(sl, 0.75, 1.9, 11.2, 1.25, S["claim"], 34 if len(S["claim"]) <= 40 else 28, WHITE, True, font=SERIF, anchor=MSO_ANCHOR.MIDDLE, lsp=0.95)
        text(sl, 0.75, 3.25, 11.0, 0.5, S["sub"], 17 if len(S["sub"]) <= 95 else 15, MUTED, italic=True, font=SERIF)
        tiles = [(S["rating_label"], self.t(("Rating", "Recommandation")), RATING_FILL[S["rating"]]),
                 (S["target_s"], S["target_cap"], None), (S["price_s"], S["price_cap"], None), (S["upside_s"], S["upside_cap"], None)]
        for i, (big, cap, fill) in enumerate(tiles):
            x = 0.75 + 2.98 * i
            rect(sl, x, 4.25, 2.75, 1.4, fill or NAVY3, None if fill else "2A4066", adj=0.08)
            text(sl, x, 4.38, 2.75, 0.75, big, fit(big, 30, 8), WHITE, True, PP_ALIGN.CENTER, MSO_ANCHOR.MIDDLE)
            text(sl, x + 0.1, 5.12, 2.55, 0.4, cap, 11.5, WHITE if fill else MUTED, align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE)
        text(sl, 0.75, 6.55, 11.8, 0.3, S["byline"], 10.5, MUTED)

    # 2 the call -----------------------------------------------------------
    def call(self, d):
        S = self.S
        sl = self.slide(d["title"])
        rect(sl, 0.6, 1.5, 3.3, 4.95, NAVY, adj=0.04)
        text(sl, 0.85, 1.7, 2.9, 0.3, self.t(("OUR CALL", "NOTRE AVIS")), 10.5, GOLD, True)
        rl = S["rating_label"]
        text(sl, 0.85, 2.0, 2.9, 0.75, rl, 32 if len(rl) <= 7 else (24 if len(rl) <= 10 else 19), WHITE, True, font=SERIF, anchor=MSO_ANCHOR.MIDDLE)
        for i, (k, v, col) in enumerate(d["panel"]):
            y = 2.95 + 0.7 * i
            line(sl, 0.85, y - 0.05, 3.65, y - 0.05, "2A4066", 0.75)
            text(sl, 0.85, y, 1.65, 0.6, k, 11.5, MUTED, anchor=MSO_ANCHOR.MIDDLE)
            text(sl, 2.3, y, 1.35, 0.6, v, 15 if len(v) <= 9 else 12, {"red": "F0A39A", "green": "9BD3B4"}.get(col, WHITE), True, PP_ALIGN.RIGHT, MSO_ANCHOR.MIDDLE)
        for i, (h, chain, big, col) in enumerate(d["pillars"]):
            y = 1.5 + 1.7 * i
            self.card(sl, 4.15, y, 8.58, 1.55)
            dot(sl, 4.38, y + 0.5, 0.55, NAVY2, i + 1, 15)
            text(sl, 5.15, y + 0.2, 5.0, 0.42, h, 16, NAVY, True)
            text(sl, 5.15, y + 0.66, 5.0, 0.8, chain, 12.5, SLATE)
            text(sl, 10.25, y + 0.15, 2.3, 1.25, big, 15 if len(big) <= 24 else 13, {"red": RED, "green": GREEN}.get(col, NAVY2), True, PP_ALIGN.RIGHT, MSO_ANCHOR.MIDDLE)
        self.source(sl, d.get("source"))

    # 3 environment ---------------------------------------------------------
    def environment(self, d):
        sl = self.slide(d["title"])
        self.card(sl, 0.6, 1.5, 6.3, 4.95)
        c = d["chart"]
        bar_chart(sl, 0.75, 1.6, 6.0, 4.4, c["title"], c["cats"], c["series"], c.get("colors", (NAVY2, GOLD, GREY)), c.get("fmt", "0.0"),
                  c.get("point_colors"), horizontal=c.get("horizontal", False))
        text(sl, 0.8, 6.05, 5.9, 0.32, c.get("note", ""), 9, SLATE, italic=True)
        for i, (h, b) in enumerate(d["drivers"]):
            y = 1.5 + 1.7 * i
            risk = i == d.get("risk_card", -1)
            self.card(sl, 7.15, y, 5.58, 1.55, REDSOFT if risk else WHITE, "E8C3BD" if risk else LINE)
            dot(sl, 7.37, y + 0.22, 0.42, RED if risk else NAVY2, i + 1, 12)
            text(sl, 7.95, y + 0.2, 4.6, 0.4, h, 14, NAVY, True)
            text(sl, 7.95, y + 0.62, 4.6, 0.9, b, 12, SLATE)
        self.source(sl, d.get("source"))

    # 4 where we differ -------------------------------------------------------
    def differ(self, d):
        sl = self.slide(d["title"])
        for i, col in enumerate(d["cols"]):
            lab, lh, lv, rh, rv, ev = col[:6]
            flag = col[6] if len(col) > 6 else "down"           # up / down (green / red), upr = up in red, downg = down in green
            up, good = flag in ("up", "upr"), flag in ("up", "downg")
            x = 0.6 + 4.1 * i
            self.card(sl, x, 1.5, 3.93, 4.95)
            text(sl, x + 0.28, 1.68, 3.4, 0.3, lab.upper(), 10.5, GOLDINK, True)
            text(sl, x + 0.28, 2.08, 3.4, 0.28, lh.upper(), 9.5, SLATE, True)
            text(sl, x + 0.28, 2.38, 3.4, 0.6, lv, fit(lv, 28, 8), GREY, True, anchor=MSO_ANCHOR.MIDDLE)
            arrow(sl, x + 0.3, 3.1, up, good)
            text(sl, x + 0.6, 3.1, 3.0, 0.28, rh.upper(), 9.5, GREEN if good else RED, True, anchor=MSO_ANCHOR.MIDDLE)
            text(sl, x + 0.28, 3.48, 3.4, 0.7, rv, fit(rv, 32, 8), NAVY, True, anchor=MSO_ANCHOR.MIDDLE)
            text(sl, x + 0.28, 4.35, 3.4, 1.95, ev, 12, SLATE)
        self.source(sl, d.get("source"))

    # 5 catalyst timeline -------------------------------------------------------
    def timeline(self, d):
        sl = self.slide(d["title"])
        ev = d["events"]
        n = len(ev)
        w = (12.13 - 0.2 * (n - 1)) / n
        key = d.get("key", 0)
        line(sl, 0.6 + w / 2, 2.0, 0.6 + (w + 0.2) * (n - 1) + w / 2, 2.0, "9FB3D1", 2)
        for i, (date, kind, h, mkt, us) in enumerate(ev):
            x = 0.6 + (w + 0.2) * i
            k = i == key
            text(sl, x, 1.45, w, 0.32, date, 14, NAVY, True, PP_ALIGN.CENTER)
            dot(sl, x + w / 2 - 0.14, 1.86, 0.28, RED if k else NAVY2)
            self.card(sl, x, 2.3, w, 3.85, REDSOFT if k else WHITE, RED if k else LINE)
            text(sl, x + 0.2, 2.45, w - 0.4, 0.28, kind.upper(), 10, RED if k else GOLDINK, True)
            text(sl, x + 0.2, 2.75, w - 0.4, 0.8, h, 14.5, NAVY, True)
            text(sl, x + 0.2, 3.62, w - 0.4, 1.0, mkt, 11, SLATE)
            text(sl, x + 0.2, 4.62, w - 0.4, 1.45, us, 11, RED if k else NAVY, True)
        if d.get("risk"):
            text(sl, 0.6, 6.25, 12.13, 0.35, d["risk"], 11, SLATE, italic=True, anchor=MSO_ANCHOR.MIDDLE)
        self.source(sl, d.get("source"))

    # 6 key catalyst -------------------------------------------------------------
    def key_catalyst(self, d):
        sl = self.slide(d["title"])
        heads = self.t([("What", "Quoi"), ("When", "Quand"), ("Market expects", "Le marché attend"), ("We expect – why", "Nous attendons – pourquoi"), ("Impact", "Impact")])
        for i, (h, b) in enumerate(zip(heads, d["items"])):
            y = 1.5 + 0.99 * i
            dot(sl, 0.6, y + 0.02, 0.42, RED if i == 4 else NAVY2, i + 1, 12)
            text(sl, 1.2, y, 4.9, 0.3, h, 13, NAVY, True)
            text(sl, 1.2, y + 0.3, 4.9, 0.66, b, 12, RED if i == 4 else SLATE, i == 4)
        self.card(sl, 6.4, 1.5, 6.33, 4.95)
        c = d["chart"]
        bar_chart(sl, 6.55, 1.6, 6.03, 4.4, c["title"], c["cats"], c["series"], c.get("colors", (NAVY2, GOLD, GREY)), c.get("fmt", "0.0"),
                  c.get("point_colors"), legend=c.get("legend"))
        text(sl, 6.6, 6.05, 6.0, 0.32, c.get("note", ""), 9, SLATE, italic=True)
        self.source(sl, d.get("source"))

    # 7 the numbers -----------------------------------------------------------
    def numbers(self, d):
        sl = self.slide(d["title"])
        rows = d["rows"]
        nc = len(rows[0])
        first = 2.7
        rest = (8.1 - first) / (nc - 1)
        rh = min(0.5, 4.3 / len(rows))
        table(sl, 0.6, 1.5, 8.1, rows, [first] + [rest] * (nc - 1), sz=12.5, rh=rh, hl=d.get("hl", ()))
        if d.get("note"):
            text(sl, 0.6, 1.62 + rh * len(rows), 8.1, 0.7, d["note"], 9.5, SLATE, italic=True)
        rect(sl, 9.0, 1.5, 3.73, 4.95, NAVY, adj=0.04)
        text(sl, 9.25, 1.7, 3.3, 0.3, self.t(("HOW TO READ IT", "COMMENT LE LIRE")), 10.5, GOLD, True)
        for i, (h, b) in enumerate(d["read"]):
            y = 2.15 + 1.4 * i
            dot(sl, 9.25, y, 0.36, GOLD, i + 1, 11, NAVY)
            text(sl, 9.75, y - 0.03, 2.85, 0.42, h, 13, WHITE, True)
            text(sl, 9.75, y + 0.38, 2.85, 0.95, b, 11, MUTED)
        self.source(sl, d.get("source"))

    # 8 relative value -------------------------------------------------------------
    def relative(self, d):
        S, P, t = self.S, self.P, self.t
        f = P["facts"]
        sl = self.slide(d["title"])
        keys = ["P/E", "P/B", "EV/EBIT", "P/FCF", "EV/Sales"]
        lab = {"P/E": ("P/E", "PER"), "P/B": ("P/B", "P/B"), "EV/EBIT": ("EV/EBIT", "VE/EBIT"), "P/FCF": ("P/FCF", "P/FCF"), "EV/Sales": ("EV/Sales", "VE/CA")}
        nm = t(("n.m.", "n.s."))
        fx = lambda v: nm if v is None else num(v, 2 if v < 1 else (1 if v < 100 else 0), self.lang) + "x"
        rows = [[t(("Multiple", "Multiple")), S["short"], t(("Peer median", "Médiane pairs")), t(("Sector median", "Médiane secteur")), t(("vs peers", "vs pairs"))]]
        colors = {}
        for k in keys:
            a, pm, sm = f["multiples"].get(k), f["peer_median"].get(k), f["sector_median"].get(k)
            disc = "—" if (a is None or pm is None or a <= 0) else pct(a / pm - 1, 0, self.lang, sign=True)
            rows.append([t(lab[k]), fx(a), fx(pm), fx(sm), disc])
            if disc != "—":
                colors[(len(rows) - 1, 4)] = GREEN if a < pm else RED
        table(sl, 0.6, 1.5, 7.4, rows, [1.6, 1.55, 1.45, 1.45, 1.35], sz=13, rh=0.5, colors=colors, bold_cells={(i, 1) for i in range(1, 6)})
        text(sl, 0.6, 4.65, 7.4, 1.75, d["read"], 11.5, SLATE)
        for i, (big, lab_, sub, col) in enumerate(d["callouts"]):
            y = 1.5 + 1.7 * i
            dark_ = i == 2
            self.card(sl, 8.3, y, 4.43, 1.55, NAVY if dark_ else WHITE, None if dark_ else LINE)
            text(sl, 8.5, y + 0.15, 1.85, 1.25, big, fit(big, 28, 6), GOLD if dark_ else {"red": RED, "green": GREEN}.get(col, NAVY2), True, anchor=MSO_ANCHOR.MIDDLE)
            text(sl, 10.4, y + 0.2, 2.2, 0.55, lab_, 12, WHITE if dark_ else NAVY, True)
            text(sl, 10.4, y + 0.78, 2.2, 0.7, sub, 10.5, MUTED if dark_ else SLATE)
        self.source(sl, d.get("source") or t((f"Source: Thoth Ledger screen, Bloomberg data, 31 Dec 2025 rebalance (FY to {f['fy_used'][:7]}, used with a 6-month lag). Peers: same GICS industry group in the developed-market universe.",
                                             f"Source : screen Thoth Ledger, données Bloomberg, rebalancement du 31 déc. 2025 (exercice clos {f['fy_used'][:7]}, utilisé avec 6 mois de décalage). Pairs : même groupe d’industries GICS dans l’univers des marchés développés.")))

    # 9 valuation -------------------------------------------------------------------
    def valuation(self, d):
        P, t, lg = self.P, self.t, self.lang
        sl = self.slide(d["title"])
        self.card(sl, 0.6, 1.5, 7.05, 4.95)
        text(sl, 0.82, 1.65, 6.6, 0.3, d["grid_title"], 12.5, NAVY, True)
        rows, cols, m = vm.grid(P)
        a0, b0 = vm.base_inputs(P)
        px = P["price"]
        sym = P["sym"]
        rf, cf = d["row_fmt"], d["col_fmt"]
        head = [d["corner"]] + ([t(("Value", "Valeur")), t(("vs price", "vs cours"))] if cols == [None] else [cf(c, lg) for c in cols])
        trows = [head]
        fills, colors, bold = {}, {}, set()
        for i, (r, vals) in enumerate(zip(rows, m)):
            if cols == [None]:
                v = vals[0]
                trows.append([rf(r, lg), money(sym, v, lg, 0 if abs(v) >= 1000 else (0 if sym == "¥" else 1)), pct(v / px - 1, 0, lg, sign=True)])
                for j in (1, 2):
                    fills[(i + 1, j)] = GREENSOFT if v >= px * 1.15 else (REDSOFT if v <= px * 0.9 else WHITE)
                if abs(r - a0) < 1e-9:
                    bold |= {(i + 1, 1), (i + 1, 2)}
                    fills[(i + 1, 1)] = fills[(i + 1, 2)] = "EFE3CC"
            else:
                row = [rf(r, lg)]
                for j, (c, v) in enumerate(zip(cols, vals)):
                    row.append(money(sym, v, lg, 0 if (abs(v) >= 100 or sym == "¥") else 1))
                    fills[(i + 1, j + 1)] = GREENSOFT if v >= px * 1.15 else (REDSOFT if v <= px * 0.9 else WHITE)
                    if abs(r - a0) < 1e-9 and abs(c - b0) < 1e-9:
                        fills[(i + 1, j + 1)] = "EFE3CC"
                        bold.add((i + 1, j + 1))
                trows.append(row)
        nc = len(trows[0])
        w0 = 1.7
        table(sl, 0.82, 2.08, 6.6, trows, [w0] + [(6.6 - w0) / (nc - 1)] * (nc - 1), sz=12.5, rh=min(0.52, 3.3 / len(trows)), fills=fills, bold_cells=bold,
              aligns=[PP_ALIGN.LEFT] + [PP_ALIGN.CENTER] * (nc - 1))
        text(sl, 0.82, 5.55, 6.6, 0.8, d["grid_note"], 10, SLATE)
        rect(sl, 7.95, 1.5, 4.78, 4.95, NAVY, adj=0.04)
        text(sl, 8.2, 1.68, 4.3, 0.3, t(("HOW WE GET THERE", "COMMENT ON Y ARRIVE")), 10.5, GOLD, True)
        for i, (h, b) in enumerate(d["steps"]):
            y = 2.12 + 1.07 * i
            dot(sl, 8.2, y, 0.38, GOLD, i + 1, 11, NAVY)
            text(sl, 8.72, y - 0.04, 3.85, 0.42, h, 13.5, WHITE, True)
            text(sl, 8.72, y + 0.36, 3.85, 0.66, b, 10.5, MUTED)
        self.source(sl, d.get("source"))

    # 10 risks and scenarios ----------------------------------------------------------
    def risks(self, d):
        P, t, lg = self.P, self.t, self.lang
        sl = self.slide(d["title"])
        for i, (h, b) in enumerate(d["risks"]):
            y = 1.5 + 1.52 * i
            self.card(sl, 0.6, y, 6.95, 1.4)
            dot(sl, 0.82, y + 0.42, 0.52, GOLDINK, "!", 16)
            text(sl, 1.55, y + 0.15, 5.8, 0.4, h, 14.5, NAVY, True)
            text(sl, 1.55, y + 0.57, 5.8, 0.8, b, 11.5, SLATE)
        self.card(sl, 7.8, 1.5, 4.93, 4.42)
        sc = {o["name"]: o["value"] for o in P["scenarios_out"]}
        items = [(t(("Bear", "Pessimiste")), sc["Bear"], RED), (t(("Base", "Central")), sc["Base"], NAVY2), (t(("Price", "Cours")), P["price"], GREY), (t(("Bull", "Optimiste")), sc["Bull"], GREEN)]
        items.sort(key=lambda z: z[1])
        fmt = '#,##0' if P["sym"] == "¥" or P["price"] >= 1000 else ('0.0' if P["price"] >= 100 else '0.0')
        bar_chart(sl, 7.95, 1.6, 4.63, 3.75, t(("Value per share", "Valeur par action")) + f" ({P['sym'] if lg == 'en' else P['sym'].replace('US$', '$US').replace('HK$', '$HK')})",
                  [z[0] for z in items], [("v", [round(z[1], 2) for z in items])], [GREY], fmt, [z[2] for z in items], legend=False)
        text(sl, 8.0, 5.33, 4.55, 0.55, d["scen_note"], 9.5, SLATE)
        rect(sl, 0.6, 6.06, 12.13, 0.5, REDSOFT, "E8C3BD", adj=0.2)
        text(sl, 0.82, 6.06, 11.7, 0.5, [[(t(("We change the call if: ", "Nous changeons d’avis si : ")), True, RED), (d["triggers"], False, NAVY)]], 10.5, NAVY, anchor=MSO_ANCHOR.MIDDLE)

    # 11 conclusion ----------------------------------------------------------------
    def conclusion(self, d):
        S = self.S
        sl = self.dark()
        rl = S["rating_label"]
        text(sl, 0.75, 0.55, 10.0, 1.0, rl, 54 if len(rl) <= 8 else 40, RATING_INK[S["rating"]], True, font=SERIF, anchor=MSO_ANCHOR.MIDDLE)
        text(sl, 0.75, 1.65, 10.8, 0.65, d["line1"], 28, WHITE, True)
        text(sl, 0.75, 2.35, 10.8, 0.6, d["line2"], 17, MUTED, italic=True, font=SERIF)
        for i, p_ in enumerate(d["points"]):
            y = 3.3 + 0.78 * i
            dot(sl, 0.75, y, 0.44, GOLD, i + 1, 13, NAVY)
            text(sl, 1.4, y - 0.02, 11.0, 0.5, p_, 15.5, WHITE, anchor=MSO_ANCHOR.MIDDLE)
        text(sl, 0.75, 5.85, 6.0, 0.6, self.t(("Questions?", "Questions ?")), 28, GOLD, True, font=SERIF)
        text(sl, 0.75, 6.7, 11.9, 0.3, S["byline"], 10, MUTED)

    # 12 sources ------------------------------------------------------------------
    def sources(self, d):
        P, t = self.P, self.t
        sl = self.slide(t(("Sources and data notes", "Sources et notes sur les données")))
        items = [x["label"] for x in P["sources"]]
        prim = [s for s in items if "third-party" not in s]
        third = [s for s in items if "third-party" in s]
        items = prim + third
        n = len(items)
        sz = 9.5 if n <= 10 else (8.5 if n <= 13 else 8)
        step = 4.85 / n
        for i, s_ in enumerate(items):
            y = 1.5 + step * i
            dot(sl, 0.6, y + 0.02, 0.26, GOLDINK if "third-party" in s_ else NAVY2, i + 1, 8)
            text(sl, 1.0, y, 7.5, step, s_.replace(" (third-party market data; to be replaced by Bloomberg, Dec 2026)", t((" — third-party market data", " — donnée de marché tierce"))), sz, NAVY)
        rect(sl, 8.85, 1.5, 3.88, 4.95, NAVY, adj=0.04)
        text(sl, 9.1, 1.68, 3.4, 0.3, t(("DATA NOTES", "NOTES SUR LES DONNÉES")), 10.5, GOLD, True)
        text(sl, 9.1, 2.1, 3.4, 4.2, d["notes"], 11, MUTED, spacing=8)

    def build(self, out):
        S = self.S
        self.cover()
        self.call(S["call"])
        self.environment(S["env"])
        self.differ(S["differ"])
        self.timeline(S["timeline"])
        self.key_catalyst(S["key"])
        self.numbers(S["numbers"])
        self.relative(S["relative"])
        self.valuation(S["valuation"])
        self.risks(S["risks"])
        self.conclusion(S["conclusion"])
        self.sources(S["sources"])
        name = f"{S['stem']}_pitch{'' if self.lang == 'en' else '_FR'}.pptx"
        self.prs.save(str(Path(out) / name))
        return name


def load(code):
    spec = importlib.util.spec_from_file_location(code, HERE / "specs" / f"{code}.py")
    sys.path.insert(0, str(HERE / "specs"))
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m.SPEC


if __name__ == "__main__":
    out = Path(sys.argv[1])
    out.mkdir(parents=True, exist_ok=True)
    codes = sys.argv[2:] or sorted(p.stem for p in (HERE / "specs").glob("*.py") if not p.stem.startswith("_"))
    for c in codes:
        sp = load(c)
        for lg in ("en", "fr"):
            print(Deck(sp, lg).build(out))
