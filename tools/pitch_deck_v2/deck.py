"""Thoth Ledger stock-pitch deck, version 2 (10 Nov 2026): fewer words, larger type, one message per slide.
Layout engine only; the content of each pitch lives in specs/<CODE>.py (English and French side by side).

    python3 tools/pitch_deck_v2/deck.py <out_dir> [CODE ...]
"""
import importlib.util, json, sys
from pathlib import Path
from pptx import Presentation
from pptx.chart.data import CategoryChartData
from pptx.dml.color import RGBColor
from pptx.enum.chart import XL_CHART_TYPE, XL_LEGEND_POSITION, XL_LABEL_POSITION, XL_TICK_LABEL_POSITION
from pptx.enum.shapes import MSO_SHAPE, MSO_CONNECTOR
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.oxml.ns import qn
from pptx.util import Inches, Pt, Emu

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
LOGO_DARK = ROOT / "site/static/brand/mark_256.png"
LOGO_LIGHT = ROOT / "site/static/brand/mark_256_light.png"
PITCHES = {p["code"]: p for p in json.loads((ROOT / "site/data/pitches.json").read_text(encoding="utf-8"))}

NAVY, NAVY2, GOLD, GOLDINK, CREAM, CREAM2, LINE = "0A1A30", "1B3358", "B58F55", "7B5A2A", "F6F2EA", "FBF8F2", "E5DCCB"
SLATE, MUTED, RED, REDSOFT, GREEN, WHITE, GREY = "616A78", "B8C0CC", "A33A2B", "F6E3E0", "2E6B4E", "FFFFFF", "9AA1AB"
RATING_FILL = {"Overweight": GREEN, "Neutral": GOLDINK, "Underweight": RED, "Sell": RED}
RGB = RGBColor.from_string
SERIF, SANS = "Georgia", "Arial"


class Ctx:
    def __init__(self, lang): self.lang = lang

    def __call__(self, x):
        if isinstance(x, tuple) and len(x) == 2 and all(isinstance(i, str) for i in x):
            return x[0] if self.lang == "en" else x[1]
        if isinstance(x, (list, tuple)): return [self(i) for i in x]
        if isinstance(x, dict): return {k: self(v) for k, v in x.items()}
        return x


# ------------------------------------------------------------------ primitives
def fit(s, size, limit=7):
    """Shrink a headline number that would not fit its box."""
    n = len(s)
    return size if n <= limit else (round(size * 0.78) if n <= limit + 3 else round(size * 0.62))


def text(sl, x, y, w, h, t, sz=14, color=NAVY, bold=False, align=None, anchor=MSO_ANCHOR.TOP, font=SANS, italic=False, spacing=None):
    s = sl.shapes.add_textbox(Inches(x), Inches(y), Inches(w), Inches(h)); tf = s.text_frame
    tf.word_wrap = True; tf.margin_left = tf.margin_right = tf.margin_top = tf.margin_bottom = 0; tf.vertical_anchor = anchor
    paras = t if isinstance(t, list) else [t]
    for i, para in enumerate(paras):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        if align is not None: p.alignment = align
        if i and spacing: p.space_before = Pt(spacing)
        runs = para if isinstance(para, list) else [(para, bold)]
        for rt, rb in runs:
            r = p.add_run(); r.text = rt; f = r.font; f.size = Pt(sz); f.bold = rb; f.italic = italic; f.color.rgb = RGB(color); f.name = font
    return s


def rect(sl, x, y, w, h, fill, line=None, round_=True, adj=0.06):
    s = sl.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE if round_ else MSO_SHAPE.RECTANGLE, Inches(x), Inches(y), Inches(w), Inches(h))
    s.fill.solid(); s.fill.fore_color.rgb = RGB(fill); s.shadow.inherit = False
    if line: s.line.color.rgb = RGB(line); s.line.width = Pt(0.75)
    else: s.line.fill.background()
    if round_: s.adjustments[0] = adj
    return s


def dot(sl, x, y, d, fill, label=None, sz=14):
    s = sl.shapes.add_shape(MSO_SHAPE.OVAL, Inches(x), Inches(y), Inches(d), Inches(d))
    s.fill.solid(); s.fill.fore_color.rgb = RGB(fill); s.line.fill.background(); s.shadow.inherit = False
    if label is not None: text(sl, x, y, d, d, str(label), sz, WHITE, True, PP_ALIGN.CENTER, MSO_ANCHOR.MIDDLE)


def line(sl, x1, y1, x2, y2, color=LINE, w=1.5, dash=False):
    c = sl.shapes.add_connector(MSO_CONNECTOR.STRAIGHT, Inches(x1), Inches(y1), Inches(x2), Inches(y2))
    c.line.color.rgb = RGB(color); c.line.width = Pt(w)
    if dash: c.line.dash_style = 4
    return c


def chart_style(ch, legend=False, sz=12):
    ch.font.size = Pt(sz); ch.font.name = SANS; ch.font.color.rgb = RGB(NAVY)
    ch.has_legend = legend
    if legend: ch.legend.position = XL_LEGEND_POSITION.BOTTOM; ch.legend.include_in_layout = False; ch.legend.font.size = Pt(sz)
    va = ch.value_axis; va.has_major_gridlines = True; va.major_gridlines.format.line.color.rgb = RGB("ECE6DA")
    va.format.line.fill.background(); va.tick_labels.font.size = Pt(sz - 1); va.tick_labels.font.color.rgb = RGB(SLATE)
    ca = ch.category_axis; ca.format.line.color.rgb = RGB(GREY); ca.tick_labels.font.size = Pt(sz - 1); ca.has_major_gridlines = False
    ca.tick_label_position = XL_TICK_LABEL_POSITION.LOW


def chart_title(ch, t, sz=13):
    ch.has_title = True; tf = ch.chart_title.text_frame; tf.text = t
    r = tf.paragraphs[0].runs[0]; r.font.size = Pt(sz); r.font.bold = True; r.font.color.rgb = RGB(NAVY); r.font.name = SANS


def fill_series(s, col):
    s.format.fill.solid(); s.format.fill.fore_color.rgb = RGB(col); s.invert_if_negative = False


def data_labels(plot, fmt='0.0', sz=11, pos=XL_LABEL_POSITION.OUTSIDE_END):
    plot.has_data_labels = True; dl = plot.data_labels; dl.font.size = Pt(sz); dl.number_format = fmt; dl.number_format_is_linked = False; dl.position = pos


def table(sl, x, y, w, rows, widths, sz=13, rh=0.46, hl=(), aligns=None):
    nr, nc = len(rows), len(rows[0])
    gs = sl.shapes.add_table(nr, nc, Inches(x), Inches(y), Inches(w), Inches(rh * nr)); t = gs.table
    tblPr = gs._element.graphic.graphicData.tbl.tblPr
    for a in ("firstRow", "bandRow"): tblPr.set(a, "0")
    for j, wd in enumerate(widths): t.columns[j].width = Inches(wd)
    for i in range(nr):
        t.rows[i].height = Inches(rh)
        for j in range(nc):
            c = t.cell(i, j); c.margin_left = c.margin_right = Inches(0.12); c.margin_top = c.margin_bottom = Inches(0.03)
            c.vertical_anchor = MSO_ANCHOR.MIDDLE
            c.fill.solid(); c.fill.fore_color.rgb = RGB(NAVY if i == 0 else ("EFE3CC" if i in hl else (CREAM if j == 0 else WHITE)))
            p = c.text_frame.paragraphs[0]; c.text_frame.word_wrap = True
            p.alignment = aligns[j] if aligns else (PP_ALIGN.LEFT if j == 0 else PP_ALIGN.RIGHT)
            r = p.add_run(); r.text = str(rows[i][j]); f = r.font; f.name = SANS; f.size = Pt(sz)
            f.bold = i == 0 or j == 0 or i in hl; f.color.rgb = RGB(WHITE if i == 0 else NAVY)
            tcPr = c._tc.get_or_add_tcPr()
            for ln in ("a:lnL", "a:lnR", "a:lnT", "a:lnB"):
                e = tcPr.find(qn(ln))
                if e is None: e = tcPr.makeelement(qn(ln), {}); tcPr.insert(0, e)
                for ch in list(e): e.remove(ch)
                e.set("w", "6350" if ln == "a:lnB" else "0")
                if ln == "a:lnB":
                    sf = e.makeelement(qn("a:solidFill"), {}); sf.append(sf.makeelement(qn("a:srgbClr"), {"val": LINE})); e.append(sf)
                else: e.append(e.makeelement(qn("a:noFill"), {}))
    return gs


# ------------------------------------------------------------------ slide frame
class Deck:
    def __init__(self, spec, lang):
        self.t, self.lang = Ctx(lang), lang; self.S = self.t(spec)
        self.prs = Presentation(); self.prs.slide_width = Inches(13.333); self.prs.slide_height = Inches(7.5)
        self.blank = self.prs.slide_layouts[6]; self.n = 0

    def footer(self, sl):
        S, t = self.S, self.t
        line(sl, 0.6, 6.95, 12.73, 6.95, LINE, 0.75)
        text(sl, 0.6, 7.02, 11.0, 0.25, t(S["footer"]), 9, SLATE, anchor=MSO_ANCHOR.MIDDLE)
        text(sl, 12.13, 7.02, 0.6, 0.25, str(self.n), 9, SLATE, align=PP_ALIGN.RIGHT, anchor=MSO_ANCHOR.MIDDLE)

    def slide(self, title, kicker=None):
        self.n += 1; sl = self.prs.slides.add_slide(self.blank)
        bg = sl.background.fill; bg.solid(); bg.fore_color.rgb = RGB(WHITE)
        if kicker: text(sl, 0.6, 0.32, 10.5, 0.3, self.t(kicker).upper(), 11, GOLDINK, True)
        text(sl, 0.6, 0.6, 11.2, 1.0, self.t(title), 25, NAVY, True, font=SERIF, anchor=MSO_ANCHOR.TOP)
        sl.shapes.add_picture(str(LOGO_DARK), Inches(12.18), Inches(0.3), Inches(0.55), Inches(0.55))
        self.footer(sl)
        return sl

    def source(self, sl, s):
        if s: text(sl, 0.6, 6.62, 12.1, 0.28, self.t(s), 9, SLATE, italic=True, anchor=MSO_ANCHOR.MIDDLE)

    # -------------------------------------------------------------- 1 cover
    def cover(self):
        S, t = self.S, self.t
        self.n += 1; sl = self.prs.slides.add_slide(self.blank)
        bg = sl.background.fill; bg.solid(); bg.fore_color.rgb = RGB(NAVY)
        sl.shapes.add_picture(str(LOGO_LIGHT), Inches(11.9), Inches(0.45), Inches(0.85), Inches(0.85))
        text(sl, 0.7, 0.75, 10.5, 0.35, t(S["kicker"]).upper(), 12, GOLD, True)
        text(sl, 0.7, 1.3, 10.8, 1.1, S["company"], 46 if len(S["company"]) <= 22 else 34, WHITE, True, font=SERIF, anchor=MSO_ANCHOR.MIDDLE)
        text(sl, 0.7, 2.45, 10.8, 0.4, t(S["ticker_line"]), 15, MUTED)
        text(sl, 0.7, 3.05, 10.5, 1.0, t(S["headline"]), 22, WHITE, font=SERIF, italic=True)
        boxes = [(t(S["rating_label"]), t(("Rating", "Avis")), RATING_FILL[S["rating"]]), (S["target_s"], t(S["target_cap"]), None),
                 (S["price_s"], t(S["price_cap"]), None), (S["upside_s"], t(S["upside_cap"]), None)]
        for i, (big, cap, fill) in enumerate(boxes):
            x = 0.7 + 3.0 * i
            rect(sl, x, 4.55, 2.75, 1.35, fill or "13294A", None if fill else "2A4066", adj=0.08)
            text(sl, x, 4.68, 2.75, 0.75, big, 30 if len(big) <= 8 else 22, WHITE, True, PP_ALIGN.CENTER, MSO_ANCHOR.MIDDLE)
            text(sl, x, 5.42, 2.75, 0.35, cap, 12, WHITE if fill else MUTED, align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE)
        text(sl, 0.7, 6.65, 11.9, 0.3, t(S["byline"]), 11, MUTED)

    # -------------------------------------------------------------- 2 the call
    def call(self, d):
        S, t = self.S, self.t
        sl = self.slide(d["title"], ("The call", "L’avis"))
        rect(sl, 0.6, 1.75, 3.6, 4.75, NAVY, adj=0.04)
        text(sl, 0.9, 1.95, 3.0, 0.3, t(("OUR CALL", "NOTRE AVIS")), 11, GOLD, True)
        text(sl, 0.9, 2.3, 3.0, 0.7, t(S["rating_label"]), 34 if len(t(S["rating_label"])) <= 8 else 19, WHITE, True, font=SERIF, anchor=MSO_ANCHOR.MIDDLE)
        for i, (k, v) in enumerate(t(d.get("panel") or S["_panel"])):
            y = 3.25 + 0.62 * i
            line(sl, 0.9, y - 0.06, 3.9, y - 0.06, "2A4066", 0.75)
            text(sl, 0.9, y, 1.9, 0.5, k, 13, MUTED, anchor=MSO_ANCHOR.MIDDLE)
            text(sl, 2.6, y, 1.3, 0.5, v, 16, WHITE, True, PP_ALIGN.RIGHT, MSO_ANCHOR.MIDDLE)
        for i, c in enumerate(d["cards"]):
            title_, line_, big, cap = t(c)
            y = 1.75 + 1.62 * i
            rect(sl, 4.5, y, 8.23, 1.45, CREAM2, LINE)
            dot(sl, 4.75, y + 0.45, 0.5, NAVY2, i + 1)
            text(sl, 5.45, y + 0.22, 4.7, 0.4, title_, 16, NAVY, True)
            text(sl, 5.45, y + 0.66, 4.7, 0.7, line_, 13, SLATE)
            text(sl, 10.0, y + 0.18, 2.55, 0.65, big, fit(big, 28), NAVY2, True, PP_ALIGN.RIGHT, MSO_ANCHOR.MIDDLE)
            text(sl, 10.0, y + 0.85, 2.55, 0.45, cap, 11, SLATE, align=PP_ALIGN.RIGHT)
        self.source(sl, d.get("source"))

    # -------------------------------------------------------------- 3 business: chart + cards
    def business(self, d):
        t = self.t; sl = self.slide(d["title"], ("The company", "La société"))
        c = d["chart"]; cd = CategoryChartData(); cd.categories = t(c["cats"])
        for nm, vals in c["series"]: cd.add_series(t(nm), vals)
        kind = XL_CHART_TYPE.BAR_CLUSTERED if c.get("horizontal") else XL_CHART_TYPE.COLUMN_CLUSTERED
        ch = sl.shapes.add_chart(kind, Inches(0.6), Inches(1.75), Inches(6.4), Inches(4.75), cd).chart
        chart_style(ch, legend=len(c["series"]) > 1); chart_title(ch, t(c["title"]))
        for s_, col in zip(ch.plots[0].series, (NAVY2, GOLD, GREY)): fill_series(s_, col)
        for (si, pi, col) in c.get("highlight", []):
            pt = ch.plots[0].series[si].points[pi]; pt.format.fill.solid(); pt.format.fill.fore_color.rgb = RGB(col)
        data_labels(ch.plots[0], c.get("fmt", "0.0")); ch.plots[0].gap_width = 70
        if c.get("horizontal"): ch.category_axis.reverse_order = True; ch.value_axis.visible = False; ch.value_axis.has_major_gridlines = False
        for i, (h, b) in enumerate(t(d["cards"])):
            y = 1.75 + 1.62 * i
            rect(sl, 7.35, y, 5.38, 1.45, CREAM2, LINE)
            line(sl, 7.35, y + 0.1, 7.35, y + 1.35, GOLD, 3)
            text(sl, 7.6, y + 0.18, 4.95, 0.4, h, 15, NAVY, True)
            text(sl, 7.6, y + 0.6, 4.95, 0.8, b, 13, SLATE)
        self.source(sl, d.get("source"))

    # -------------------------------------------------------------- 4 four KPI cards
    def kpis(self, d, kicker=("Industry and macro", "Secteur et macro")):
        t = self.t; sl = self.slide(d["title"], kicker)
        for i, (big, lab, b) in enumerate(t(d["cards"])):
            x, y = 0.6 + 6.17 * (i % 2), 1.75 + 2.45 * (i // 2)
            rect(sl, x, y, 5.95, 2.25, CREAM2, LINE)
            text(sl, x + 0.3, y + 0.22, 2.7, 0.8, big, fit(big, 34), NAVY2, True, anchor=MSO_ANCHOR.MIDDLE)
            text(sl, x + 3.05, y + 0.25, 2.65, 0.75, lab, 15, NAVY, True, anchor=MSO_ANCHOR.MIDDLE)
            text(sl, x + 0.3, y + 1.15, 5.35, 1.0, b, 13, SLATE)
        self.source(sl, d.get("source"))

    # -------------------------------------------------------------- 5a why the screen picked it
    def screen(self, d):
        S, t = self.S, self.t; P = PITCHES[S["code"]]; f = P["facts"]
        sl = self.slide(d["title"], ("Why the screen picked it", "Pourquoi le screen l’a choisi"))
        keys = [k for k in ("P/E", "EV/EBIT", "P/FCF", "P/B", "EV/Sales") if f["multiples"].get(k) is not None and f["peer_median"].get(k) is not None]
        cd = CategoryChartData(); cd.categories = keys
        cd.add_series(S["company"], [round(f["multiples"][k], 2) for k in keys]); cd.add_series(t(("Peer median", "Médiane des pairs")), [round(f["peer_median"][k], 2) for k in keys])
        ch = sl.shapes.add_chart(XL_CHART_TYPE.COLUMN_CLUSTERED, Inches(0.6), Inches(1.75), Inches(7.0), Inches(4.75), cd).chart
        chart_style(ch, legend=True); chart_title(ch, t(("Multiples at the Dec 2025 rebalance (x) · lower = cheaper", "Multiples au rebalancement de déc. 2025 (x) · plus bas = moins cher")))
        fill_series(ch.plots[0].series[0], NAVY2); fill_series(ch.plots[0].series[1], "D9CBB0"); data_labels(ch.plots[0], '0.0"x"'); ch.plots[0].gap_width = 60
        stats = [(f"{f['sector_rank']} / {f['sector_n']}", t(("Value rank in its sector", "Rang value dans son secteur")), t(d.get("rank_line", ""))),
                 (t(d["held"][0]), t(d["held"][1]), t(d["held"][2])),
                 (t(d["fit"][0]), t(d["fit"][1]), t(d["fit"][2]))]
        for i, (big, lab, b) in enumerate(stats):
            y = 1.75 + 1.62 * i
            rect(sl, 7.95, y, 4.78, 1.45, NAVY if i == 2 else CREAM2, None if i == 2 else LINE)
            text(sl, 8.2, y + 0.15, 4.3, 0.55, big, fit(big, 24, 14), GOLD if i == 2 else NAVY2, True)
            text(sl, 8.2, y + 0.68, 4.3, 0.3, lab, 13, WHITE if i == 2 else NAVY, True)
            text(sl, 8.2, y + 0.98, 4.3, 0.45, b, 11, MUTED if i == 2 else SLATE)
        self.source(sl, d.get("source") or (f"Source: Thoth Ledger stock screen, Bloomberg data (FY to {f['fy_used'][:7]}, used with a 6-month lag); peers = same GICS industry group.",
                                            f"Source : screen titres Thoth Ledger, données Bloomberg (exercice clos {f['fy_used'][:7]}, utilisé avec 6 mois de décalage) ; pairs = même groupe d’industries GICS."))

    # -------------------------------------------------------------- 5b where we differ (non-screen pitch)
    def differ(self, d):
        t = self.t; sl = self.slide(d["title"], ("Where we differ", "Où nous différons"))
        cols = t(d["cols"])
        for i, (lab, street, ours, gap, note) in enumerate(cols):
            x = 0.6 + 4.1 * i
            rect(sl, x, 1.75, 3.9, 3.65, CREAM2, LINE)
            text(sl, x + 0.3, 1.95, 3.3, 0.3, lab.upper(), 11, GOLDINK, True)
            text(sl, x + 0.3, 2.3, 3.3, 0.3, t(("Street (Bloomberg)", "Consensus (Bloomberg)")), 11, SLATE)
            text(sl, x + 0.3, 2.6, 3.3, 0.55, street, 26, GREY, True)
            text(sl, x + 0.3, 3.25, 3.3, 0.3, t(("Our view", "Notre vue")), 11, RED, True)
            text(sl, x + 0.3, 3.55, 3.3, 0.65, ours, 34, NAVY, True)
            rect(sl, x + 0.3, 4.3, 1.6, 0.38, REDSOFT, adj=0.5); text(sl, x + 0.3, 4.3, 1.6, 0.38, gap, 13, RED, True, PP_ALIGN.CENTER, MSO_ANCHOR.MIDDLE)
            text(sl, x + 0.3, 4.8, 3.3, 0.55, note, 11, SLATE)
        rect(sl, 0.6, 5.6, 12.13, 0.85, NAVY, adj=0.1)
        text(sl, 0.9, 5.6, 11.6, 0.85, t(d["banner"]), 16, WHITE, True, anchor=MSO_ANCHOR.MIDDLE)
        self.source(sl, d.get("source"))

    # -------------------------------------------------------------- 6 variant perception
    def variant(self, d):
        t = self.t; sl = self.slide(d["title"], ("Variant perception", "Variant perception"))
        text(sl, 0.6, 1.7, 5.3, 0.3, t(("THE MARKET SAYS", "LE MARCHÉ DIT")), 11, SLATE, True)
        text(sl, 6.85, 1.7, 5.9, 0.3, t(("WE SAY", "NOUS DISONS")), 11, GOLDINK, True)
        rows = t(d["rows"]); hgt = 4.45 / len(rows)
        for i, (a, b) in enumerate(rows):
            y = 2.05 + hgt * i
            rect(sl, 0.6, y, 5.6, hgt - 0.18, CREAM, None)
            text(sl, 0.85, y, 5.1, hgt - 0.18, "“" + a + "”", 15, SLATE, italic=True, anchor=MSO_ANCHOR.MIDDLE, font=SERIF)
            arr = sl.shapes.add_shape(MSO_SHAPE.RIGHT_ARROW, Inches(6.28), Inches(y + (hgt - 0.18) / 2 - 0.16), Inches(0.45), Inches(0.32))
            arr.fill.solid(); arr.fill.fore_color.rgb = RGB(GOLD); arr.line.fill.background(); arr.shadow.inherit = False
            rect(sl, 6.85, y, 5.88, hgt - 0.18, WHITE, NAVY2)
            text(sl, 7.1, y, 5.4, hgt - 0.18, b, 14, NAVY, anchor=MSO_ANCHOR.MIDDLE)
        self.source(sl, d.get("source"))

    # -------------------------------------------------------------- 7 financials
    def financials(self, d):
        t = self.t; sl = self.slide(d["title"], ("Financials", "Chiffres clés"))
        rows = t(d["rows"]); nc = len(rows[0])
        first = 3.0; rest = (8.2 - first) / (nc - 1)
        table(sl, 0.6, 1.8, 8.2, rows, [first] + [rest] * (nc - 1), sz=14, rh=0.5, hl=d.get("hl", ()))
        rect(sl, 9.15, 1.8, 3.58, 4.4, NAVY, adj=0.05)
        text(sl, 9.45, 2.0, 3.0, 0.3, t(("WHAT TO WATCH", "À SURVEILLER")), 11, GOLD, True)
        text(sl, 9.45, 2.4, 3.0, 0.8, t(d["watch_big"]), fit(t(d["watch_big"]), 30, 9), WHITE, True)
        text(sl, 9.45, 3.25, 3.0, 2.8, t(d["watch"]), 14, MUTED)
        self.source(sl, d.get("source"))

    # -------------------------------------------------------------- 8 valuation
    def valuation(self, d):
        S, t = self.S, self.t; P = PITCHES[S["code"]]
        sl = self.slide(d["title"], ("Valuation", "Valorisation"))
        sc = {o["name"]: o["value"] for o in P["scenarios_out"]}
        cats = [t(("Bear", "Pessimiste")), t(("Price", "Cours")), t(("Base", "Central")), t(("Bull", "Optimiste"))]
        vals = [sc["Bear"], P["price"], sc["Base"], sc["Bull"]]
        order = sorted(range(4), key=lambda k: vals[k])
        cats = [cats[k] for k in order]; vals = [vals[k] for k in order]
        ct = P["valuation"].get("consensus_target")
        if ct: cats.append(t(("Street target", "Objectif consensus"))); vals.append(ct)
        cd = CategoryChartData(); cd.categories = cats; cd.add_series("v", [round(v, 2) for v in vals])
        ch = sl.shapes.add_chart(XL_CHART_TYPE.COLUMN_CLUSTERED, Inches(0.6), Inches(1.75), Inches(6.9), Inches(4.75), cd).chart
        chart_style(ch); chart_title(ch, t(d["chart_title"]))
        se = ch.plots[0].series[0]; fill_series(se, "D9CBB0"); ch.plots[0].gap_width = 55
        cols = {t(("Price", "Cours")): GREY, t(("Base", "Central")): NAVY2, t(("Street target", "Objectif consensus")): "D3D7DD", t(("Bear", "Pessimiste")): "E7B9B1", t(("Bull", "Optimiste")): "C7D9CC"}
        for k, c in enumerate(cats):
            pt = se.points[k]; pt.format.fill.solid(); pt.format.fill.fore_color.rgb = RGB(cols.get(c, "D9CBB0"))
        data_labels(ch.plots[0], d.get("fmt", '0.0'), 12)
        rect(sl, 7.85, 1.75, 4.88, 4.75, NAVY, adj=0.04)
        text(sl, 8.15, 1.95, 4.3, 0.3, t(("HOW WE GET THERE", "COMMENT NOUS Y ARRIVONS")), 11, GOLD, True)
        text(sl, 8.15, 2.3, 4.3, 0.5, t(d["method"]), 14, WHITE, True)
        for i, (h, b) in enumerate(t(d["steps"])):
            y = 3.0 + 1.12 * i
            dot(sl, 8.15, y, 0.42, GOLD, i + 1, 13)
            text(sl, 8.75, y - 0.04, 3.8, 0.4, h, 15, WHITE, True)
            text(sl, 8.75, y + 0.36, 3.8, 0.7, b, 12, MUTED)
        self.source(sl, d.get("source"))

    # -------------------------------------------------------------- 9 catalysts
    def catalysts(self, d):
        t = self.t; sl = self.slide(d["title"], ("Catalysts", "Catalyseurs"))
        ev = t(d["events"]); n = len(ev); w = (12.13 - 0.25 * (n - 1)) / n; key = d.get("key", 0)
        line(sl, 0.6 + w / 2, 2.12, 0.6 + (w + 0.25) * (n - 1) + w / 2, 2.12, GOLD, 2)
        for i, (date, kind, h, b) in enumerate(ev):
            x = 0.6 + (w + 0.25) * i
            text(sl, x, 1.65, w, 0.32, date, 15, NAVY, True, PP_ALIGN.CENTER)
            dot(sl, x + w / 2 - 0.13, 2.0, 0.26, RED if i == key else NAVY2)
            rect(sl, x, 2.5, w, 2.75, REDSOFT if i == key else CREAM2, RED if i == key else LINE)
            text(sl, x + 0.22, 2.68, w - 0.44, 0.3, kind.upper(), 11, RED if i == key else GOLDINK, True)
            text(sl, x + 0.22, 3.02, w - 0.44, 0.75, h, 16, NAVY, True)
            text(sl, x + 0.22, 3.82, w - 0.44, 1.35, b, 12, SLATE)
        rect(sl, 0.6, 5.5, 12.13, 0.9, CREAM, None, adj=0.1)
        text(sl, 0.9, 5.5, 11.6, 0.9, [[(t(("The number to watch: ", "Le chiffre à surveiller : ")), True), (t(d["watch"]), False)]], 15, NAVY, anchor=MSO_ANCHOR.MIDDLE)
        self.source(sl, d.get("source"))

    # -------------------------------------------------------------- 10 risks
    def risks(self, d):
        t = self.t; sl = self.slide(d["title"], ("Risks", "Risques"))
        for i, (h, b) in enumerate(t(d["risks"])):
            y = 1.75 + 1.62 * i
            rect(sl, 0.6, y, 7.6, 1.45, CREAM2, LINE)
            dot(sl, 0.85, y + 0.45, 0.5, GOLDINK, "!", 16)
            text(sl, 1.55, y + 0.2, 6.4, 0.45, h, 16, NAVY, True)
            text(sl, 1.55, y + 0.66, 6.4, 0.75, b, 13, SLATE)
        rect(sl, 8.55, 1.75, 4.18, 4.75, REDSOFT, "E8C3BD", adj=0.04)
        text(sl, 8.85, 1.95, 3.6, 0.3, t(d.get("trig_head", ("WE CHANGE THE CALL IF", "NOUS CHANGEONS D’AVIS SI"))), 11, RED, True)
        for i, tr in enumerate(t(d["triggers"])):
            y = 2.45 + 1.3 * i
            text(sl, 8.85, y, 0.4, 0.4, "→", 18, RED, True)
            text(sl, 9.25, y, 3.25, 1.2, tr, 14, NAVY)
        self.source(sl, d.get("source"))

    # -------------------------------------------------------------- 11 closing
    def closing(self, d):
        S, t = self.S, self.t
        self.n += 1; sl = self.prs.slides.add_slide(self.blank)
        bg = sl.background.fill; bg.solid(); bg.fore_color.rgb = RGB(NAVY)
        sl.shapes.add_picture(str(LOGO_LIGHT), Inches(11.9), Inches(0.45), Inches(0.85), Inches(0.85))
        text(sl, 0.7, 0.9, 11.0, 1.0, t(S["rating_label"]), 54 if len(t(S["rating_label"])) <= 8 else 44, "F0A39A" if S["rating"] in ("Underweight", "Sell") else ("9BD3B4" if S["rating"] == "Overweight" else "E6C98F"), True, font=SERIF)
        text(sl, 0.7, 2.0, 11.0, 0.6, t(d["line1"]), 26, WHITE, True)
        text(sl, 0.7, 2.7, 11.0, 0.9, t(d["line2"]), 18, MUTED, italic=True, font=SERIF)
        for i, (big, lab, sub) in enumerate(t(d["boxes"])):
            x = 0.7 + 4.0 * i
            rect(sl, x, 3.85, 3.7, 1.75, "13294A", "2A4066", adj=0.06)
            text(sl, x, 4.0, 3.7, 0.75, big, fit(big, 30, 11), WHITE, True, PP_ALIGN.CENTER, MSO_ANCHOR.MIDDLE)
            text(sl, x + 0.2, 4.78, 3.3, 0.35, lab, 13, WHITE, True, PP_ALIGN.CENTER)
            text(sl, x + 0.2, 5.12, 3.3, 0.4, sub, 11, MUTED, align=PP_ALIGN.CENTER)
        text(sl, 0.7, 6.05, 6.0, 0.6, t(("Questions?", "Questions ?")), 26, GOLD, True, font=SERIF)
        text(sl, 0.7, 6.85, 11.9, 0.3, t(S["byline"]), 10, MUTED)

    # -------------------------------------------------------------- 12 sources
    def sources(self):
        S, t = self.S, self.t; P = PITCHES[S["code"]]
        sl = self.slide(("Sources and disclosures", "Sources et avertissements"), None)
        items = [f"[{x['tag']}] {x['label']}" for x in P["sources"]] + t(S.get("extra_sources", ([], [])))
        half = (len(items) + 1) // 2
        text(sl, 0.6, 1.6, 5.95, 4.0, items[:half], 10, NAVY, spacing=3)
        text(sl, 6.78, 1.6, 5.95, 4.0, items[half:], 10, NAVY, spacing=3)
        text(sl, 0.6, 5.75, 12.13, 0.9, t(S.get("disclosure", COMMON_DISC)), 10, SLATE)

    def build(self, out):
        S = self.S
        self.cover(); self.call(S["call"]); self.business(S["business"]); self.kpis(S["macro"])
        (self.differ if "differ" in S else self.screen)(S.get("differ") or S["screen"])
        self.variant(S["variant"]); self.financials(S["fin"]); self.valuation(S["val"])
        self.catalysts(S["cat"]); self.risks(S["risks"]); self.closing(S["close"]); self.sources()
        name = f"{S['stem']}_pitch{'' if self.lang == 'en' else '_FR'}.pptx"
        self.prs.save(str(Path(out) / name)); return name


def load(code):
    sys.path.insert(0, str(HERE / "specs"))
    spec = importlib.util.spec_from_file_location(code, HERE / "specs" / f"{code}.py")
    m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m); return m.SPEC


COMMON_DISC = ("Student research by Noah Doose (MSc Financial Markets & Investments, SKEMA Business School) for educational purposes and job interviews. Not investment advice or a solicitation. Market data (prices, consensus, forward multiples) is third-party as of the date shown and will be refreshed from Bloomberg; company figures come from the filings listed. Screen data: Thoth Ledger pipeline on Bloomberg data extracted on the SKEMA terminal (Oct 2026).",
               "Travail étudiant de Noah Doose (MSc Financial Markets & Investments, SKEMA Business School) à visée pédagogique et de préparation aux entretiens. Pas un conseil en investissement ni une sollicitation. Les données de marché (cours, consensus, multiples prévisionnels) sont de source tierce à la date indiquée et seront mises à jour depuis Bloomberg ; les chiffres des sociétés viennent des publications citées. Données du screen : pipeline Thoth Ledger sur des données Bloomberg extraites sur le terminal de SKEMA (oct. 2026).")

if __name__ == "__main__":
    out = Path(sys.argv[1]); out.mkdir(parents=True, exist_ok=True)
    codes = sys.argv[2:] or sorted(p.stem for p in (HERE / "specs").glob("*.py") if not p.stem.startswith("_"))
    for c in codes:
        sp = load(c)
        for lg in ("en", "fr"): print(Deck(sp, lg).build(out))
