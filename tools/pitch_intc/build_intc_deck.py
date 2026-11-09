"""Intel (INTC) stock pitch deck, English and French, in the same 12-slide layout as the other Thoth Ledger pitches.
Source material: Noah Doose & Victor Endrizzi, Intel initiation report, model and course deck (SKEMA Equity Research, Nov 2026).
Uses an existing pitch deck as the template (masters, colours, footer), removes its slides and rebuilds 12 new ones.

    python3 tools/pitch_intc/build_intc_deck.py <out_dir>
"""
import copy, sys
from pathlib import Path
from pptx import Presentation
from pptx.chart.data import CategoryChartData
from pptx.dml.color import RGBColor
from pptx.enum.chart import XL_CHART_TYPE, XL_LEGEND_POSITION, XL_LABEL_POSITION
from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.util import Inches, Pt

ROOT = Path(__file__).resolve().parents[2]
TEMPLATE = ROOT / "docs/assets/pitches/316_HK_Orient_Overseas_International_pitch.pptx"
OUT = Path(sys.argv[1] if len(sys.argv) > 1 else ".")

# Thoth Ledger charter (the template deck is restyled by tools/decks_style/restyle_thoth.py)
INK, GREEN, MINT, ROW, SLATE, RED = "0A1A30", "1B3358", "EFE3CC", "F7F3EC", "616A78", "A33A2B"
CARD, CARDLN, MUTED, MUTED2, REDSOFT, MINT2, WHITE = "142846", "2A4066", "B8C0CC", "8C97A8", "F6E3E0", "F6F2EA", "FFFFFF"
RGB = lambda h: RGBColor.from_string(h)


# ------------------------------------------------------------------ helpers
def tb(sl, x, y, w, h, text, sz=13, color=INK, bold=False, align=None, anchor=MSO_ANCHOR.TOP, spc=None, italic=False):
    s = sl.shapes.add_textbox(Inches(x), Inches(y), Inches(w), Inches(h)); tf = s.text_frame
    tf.word_wrap = True; tf.margin_left = tf.margin_right = tf.margin_top = tf.margin_bottom = 0; tf.vertical_anchor = anchor
    paras = text if isinstance(text, list) else [text]
    for i, p_ in enumerate(paras):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        if align: p.alignment = align
        runs = p_ if isinstance(p_, list) else [(p_, bold)]
        for t, b in runs:
            r = p.add_run(); r.text = t; f = r.font; f.size = Pt(sz); f.bold = b; f.italic = italic; f.color.rgb = RGB(color); f.name = "Arial"
            if spc: r.font._element.set("spc", str(spc))
        if i: p.space_before = Pt(4)
    return s


def box(sl, x, y, w, h, fill, line=None, shape=MSO_SHAPE.ROUNDED_RECTANGLE, adj=0.03):
    s = sl.shapes.add_shape(shape, Inches(x), Inches(y), Inches(w), Inches(h))
    s.fill.solid(); s.fill.fore_color.rgb = RGB(fill)
    if line: s.line.color.rgb = RGB(line); s.line.width = Pt(0.75)
    else: s.line.fill.background()
    if shape == MSO_SHAPE.ROUNDED_RECTANGLE: s.adjustments[0] = adj
    s.shadow.inherit = False
    return s


def pill(sl, x, y, w, h, text, fill=RED, sz=13):
    box(sl, x, y, w, h, fill, fill, adj=0.5); tb(sl, x, y, w, h, text, sz, WHITE, True, PP_ALIGN.CENTER, MSO_ANCHOR.MIDDLE)


def num_dot(sl, x, y, n):
    s = sl.shapes.add_shape(MSO_SHAPE.OVAL, Inches(x), Inches(y), Inches(0.5), Inches(0.5))
    s.fill.solid(); s.fill.fore_color.rgb = RGB(GREEN); s.line.fill.background(); s.shadow.inherit = False
    tb(sl, x, y, 0.5, 0.5, str(n), 15, WHITE, True, PP_ALIGN.CENTER, MSO_ANCHOR.MIDDLE)


def content(prs, kicker, title):
    sl = prs.slides.add_slide(prs.slide_layouts[2])
    for ph in sl.placeholders:
        idx = ph.placeholder_format.idx
        if idx == 100: ph.text_frame.text = kicker
        elif idx == 101: ph.text_frame.text = title
    return sl


def source(sl, text):
    tb(sl, 0.6, 6.66, 12.13, 0.3, text, 9, SLATE, italic=True, anchor=MSO_ANCHOR.MIDDLE)


def table(sl, x, y, w, rows, widths, sz=12, rh=0.4, hl=(), first_bold=True, aligns=None):
    nr, nc = len(rows), len(rows[0])
    gs = sl.shapes.add_table(nr, nc, Inches(x), Inches(y), Inches(w), Inches(rh * nr)); t = gs.table
    tblPr = gs._element.graphic.graphicData.tbl.tblPr
    for a in ("firstRow", "bandRow"): tblPr.set(a, "0")
    st = tblPr.find("{http://schemas.openxmlformats.org/drawingml/2006/main}tableStyleId")
    if st is not None: st.text = "{5940675A-B579-460E-94D1-54222C63F5DA}"   # "No style, table grid" -> overridden below
    for j, wd in enumerate(widths): t.columns[j].width = Inches(wd)
    for i in range(nr):
        t.rows[i].height = Inches(rh)
        for j in range(nc):
            c = t.cell(i, j); c.margin_left = c.margin_right = Inches(0.12); c.margin_top = c.margin_bottom = Inches(0.02)
            c.vertical_anchor = MSO_ANCHOR.MIDDLE
            c.fill.solid(); c.fill.fore_color.rgb = RGB(GREEN if i == 0 else (MINT if i in hl else (ROW if j == 0 else WHITE)))
            tf = c.text_frame; tf.word_wrap = True; p = tf.paragraphs[0]
            p.alignment = (aligns[j] if aligns else (PP_ALIGN.LEFT if j == 0 else PP_ALIGN.RIGHT))
            r = p.add_run(); r.text = str(rows[i][j]); f = r.font; f.name = "Arial"; f.size = Pt(sz)
            f.bold = i == 0 or (j == 0 and first_bold) or i in hl; f.color.rgb = RGB(WHITE if i == 0 else INK)
            tcPr = c._tc.get_or_add_tcPr()
            for ln in ("a:lnL", "a:lnR", "a:lnT", "a:lnB"):
                from pptx.oxml.ns import qn
                e = tcPr.find(qn(ln))
                if e is None: e = tcPr.makeelement(qn(ln), {}); tcPr.insert(0, e)
                e.set("w", "6350" if ln == "a:lnB" else "0")
                for ch in list(e): e.remove(ch)
                if ln == "a:lnB":
                    sf = e.makeelement(qn("a:solidFill"), {}); clr = sf.makeelement(qn("a:srgbClr"), {"val": "E5DCCB"}); sf.append(clr); e.append(sf)
                else: e.append(e.makeelement(qn("a:noFill"), {}))
    return gs


def style_chart(ch, legend=True, sz=11):
    ch.font.size = Pt(sz); ch.font.name = "Arial"; ch.font.color.rgb = RGB(INK)
    ch.has_legend = legend
    if legend: ch.legend.position = XL_LEGEND_POSITION.BOTTOM; ch.legend.include_in_layout = False; ch.legend.font.size = Pt(sz)
    va = ch.value_axis; va.has_major_gridlines = True; va.major_gridlines.format.line.color.rgb = RGB("ECE6DA")
    va.format.line.fill.background(); va.tick_labels.font.size = Pt(sz - 1); va.tick_labels.font.color.rgb = RGB(SLATE)
    ca = ch.category_axis; ca.format.line.color.rgb = RGB("888888"); ca.tick_labels.font.size = Pt(sz - 1); ca.has_major_gridlines = False


# ------------------------------------------------------------------ content
def build(lang):
    E = lang == "en"
    T = lambda en, fr: en if E else fr
    N = (lambda s: s) if E else (lambda s: s.replace(".", ",").replace("$", "").strip())   # minimal number localisation where needed
    prs = Presentation(str(TEMPLATE))
    # drop the template slides
    sldIdLst = prs.slides._sldIdLst
    for sid in list(sldIdLst):
        prs.part.drop_rel(sid.rId); sldIdLst.remove(sid)
    # footer of the content layout
    for sh in prs.slide_layouts[2].shapes:
        if sh.has_text_frame and "Noah Doose" in sh.text_frame.text:
            r = sh.text_frame.paragraphs[0].runs[0]
            r.text = T("Intel (Nasdaq: INTC)  ·  Noah Doose & Victor Endrizzi  ·  Student research, not investment advice  ·  Data as of 6 Nov 2026",
                       "Intel (Nasdaq : INTC)  ·  Noah Doose & Victor Endrizzi  ·  Travail étudiant, pas un conseil en investissement  ·  Données au 6 nov. 2026")
            for extra in sh.text_frame.paragraphs[0].runs[1:]: extra.text = ""

    def usd(x, d=2):
        s = f"${x:,.{d}f}"
        return s if E else (f"{x:,.{d}f}".replace(",", " ").replace(".", ",") + " $")
    pc = lambda s: s if E else s.replace(".", ",").replace("%", " %")
    SELL = T("SELL", "VENDRE")

    # 1 ---------------------------------------------------------------- cover
    sl = prs.slides.add_slide(prs.slide_layouts[1])
    tb(sl, 0.6, 0.55, 9.0, 0.3, T("STOCK PITCH  ·  SHORT IDEA  ·  6 NOVEMBER 2026", "STOCK PITCH  ·  IDÉE DE VENTE  ·  6 NOVEMBRE 2026"), 11, MINT, True, anchor=MSO_ANCHOR.MIDDLE, spc=150)
    tb(sl, 0.6, 1.05, 8.1, 1.1, "Intel Corporation", 40, WHITE, True, anchor=MSO_ANCHOR.MIDDLE)
    tb(sl, 0.6, 2.2, 8.1, 0.35, T("Nasdaq: INTC  ·  Information Technology / Semiconductors  ·  United States", "Nasdaq : INTC  ·  Technologies de l’information / Semi-conducteurs  ·  États-Unis"), 14, MUTED, anchor=MSO_ANCHOR.MIDDLE)
    tb(sl, 0.6, 2.85, 7.8, 1.5, T("The 2026 margin peak is behind us: the Street still prices a shortage windfall as if it were permanent.",
                                  "Le pic de marge de 2026 est derrière nous : le marché valorise encore une aubaine de pénurie comme si elle était durable."), 20, WHITE)
    box(sl, 8.9, 1.05, 3.83, 3.45, CARD, CARDLN, adj=0.023)
    pill(sl, 9.2, 1.35, 2.0, 0.42, SELL)
    tb(sl, 11.35, 1.35, 1.23, 0.42, T("Initiation", "Initiation"), 10, MUTED, anchor=MSO_ANCHOR.MIDDLE)
    for i, (k, v, c) in enumerate([(T("Price", "Cours"), usd(56.28), WHITE), (T("Target (base case)", "Objectif (central)"), usd(32, 0), WHITE),
                                   (T("Upside / downside", "Potentiel"), pc("−43%"), "F0A39A"), (T("Horizon", "Horizon"), T("12-18 months", "12-18 mois"), WHITE)]):
        tb(sl, 9.2, 2.0 + 0.55 * i, 2.0, 0.45, k, 13, MUTED, anchor=MSO_ANCHOR.MIDDLE)
        tb(sl, 11.0, 2.0 + 0.55 * i, 1.43, 0.45, v, 17 if i < 3 else 13, c, True, PP_ALIGN.RIGHT, MSO_ANCHOR.MIDDLE)
    tb(sl, 9.2, 4.14, 3.23, 0.3, T("Price: close, 6 Nov 2026", "Cours : clôture du 6 nov. 2026"), 10, MUTED2, anchor=MSO_ANCHOR.MIDDLE)
    for i, (v, k) in enumerate([(T("$306bn", "306 Md$"), T("Market cap (diluted)", "Capitalisation (diluée)")), (usd(1.33), T("2027E EPS (Street $1.78)", "BPA 2027E (consensus 1,78 $)")),
                                (T("32.5x", "32,5x"), T("P/E on Street NTM EPS", "PER sur BPA 12 mois consensus")), (T("−$5.7bn", "−5,7 Md$"), T("Free cash flow 2027E", "Free cash flow 2027E"))]):
        tb(sl, 0.6 + 3.05 * i, 5.05, 2.73, 0.7, v, 28, WHITE, True, anchor=MSO_ANCHOR.BOTTOM)
        tb(sl, 0.6 + 3.05 * i, 5.8, 2.73, 0.35, k, 12, MUTED, anchor=MSO_ANCHOR.MIDDLE)
    tb(sl, 0.6, 6.85, 12.13, 0.3, T("Noah Doose & Victor Endrizzi  ·  MSc Financial Markets & Investments, SKEMA Business School  ·  Equity Research course  ·  Student research, not investment advice",
                                     "Noah Doose & Victor Endrizzi  ·  MSc Financial Markets & Investments, SKEMA Business School  ·  Cours d’Equity Research  ·  Travail étudiant, pas un conseil en investissement"), 10, MUTED2, anchor=MSO_ANCHOR.MIDDLE)

    # 2 ---------------------------------------------------------------- executive summary
    sl = content(prs, T("01  EXECUTIVE SUMMARY", "01  SYNTHÈSE"), T("2026 margins were a shortage windfall: our 2027 EPS is 25% below the Street",
                                                                     "Les marges de 2026 étaient une aubaine de pénurie : notre BPA 2027 est 25 % sous le consensus"))
    box(sl, 0.6, 1.85, 4.0, 4.6, MINT2, "E5DCCB")
    pill(sl, 0.9, 2.1, 1.9, 0.4, SELL)
    tb(sl, 0.9, 2.6, 3.4, 0.6, usd(32, 0), 30, INK, True, anchor=MSO_ANCHOR.MIDDLE)
    tb(sl, 0.9, 3.2, 3.4, 0.4, T("price target, −43% vs $56.28", "objectif de cours, −43 % vs 56,28 $"), 13, SLATE)
    tb(sl, 0.9, 3.8, 3.45, 2.5, T("Intel's 2026 recovery came from a shortage: reserved inventory sold in Q1, price rises and a server boom it could only partly supply. The Q4 guide (gross margin 38%, EPS $0.25) shows the peak is behind it, yet consensus still models 42.5% and $1.78 for 2027.",
                                  "La reprise de 2026 vient d’une pénurie : stocks réservés vendus au T1, hausses de prix et un boom des serveurs qu’Intel n’a pu servir qu’en partie. La guidance du T4 (marge brute 38 %, BPA 0,25 $) montre que le pic est passé ; le consensus table encore sur 42,5 % et 1,78 $ en 2027."), 12, INK)
    pts = [(T("Margins peaked in 2026", "Les marges ont culminé en 2026"),
            T("Non-GAAP gross margin rose from 41.0% (Q1) to 44.1% (Q3), then Intel guided 38% for Q4. We keep 2027 near the run-rate: 39.7% non-GAAP vs 42.5% for the Street.",
              "Marge brute non-GAAP de 41,0 % (T1) à 44,1 % (T3), puis 38 % annoncés pour le T4. Nous restons près de ce rythme en 2027 : 39,7 % non-GAAP contre 42,5 % pour le consensus.")),
           (T("Servers capped, PCs shrinking", "Serveurs plafonnés, PC en recul"),
            T("Server CPU demand grows >30% but Intel is short of substrates and Intel 3 output; PC units fall ~10% in 2027. Revenue is only 5% below consensus: the gap is margins.",
              "La demande de CPU serveurs croît de plus de 30 %, mais Intel manque de substrats et de production Intel 3 ; les PC reculent d’environ 10 % en 2027. Le chiffre d’affaires n’est que 5 % sous le consensus : l’écart vient des marges.")),
           (T("Capex and dilution absorb the cash", "Capex et dilution absorbent le cash"),
            T("Capex rises 'strongly' in 2027, free cash flow turns negative (−$5.7bn), diluted shares are up 29% since 2023 and ~$1.1bn a year of profit goes to fab partners.",
              "Le capex monte « fortement » en 2027, le free cash flow redevient négatif (−5,7 Md$), le nombre d’actions diluées a augmenté de 29 % depuis 2023 et ~1,1 Md$ de bénéfice par an revient aux partenaires des usines."))]
    for i, (h, b) in enumerate(pts):
        y = 1.9 + 1.57 * i; num_dot(sl, 4.95, y, i + 1)
        tb(sl, 5.65, y - 0.05, 7.08, 0.4, h, 15, INK, True, anchor=MSO_ANCHOR.MIDDLE)
        tb(sl, 5.65, y + 0.37, 7.08, 1.05, b, 12, INK)
    source(sl, T("Source: Intel Q1-Q3 2026 prepared remarks and 10-Qs; Bloomberg consensus (BEst, 6 Nov 2026); own model.", "Source : présentations et 10-Q T1-T3 2026 d’Intel ; consensus Bloomberg (BEst, 6 nov. 2026) ; notre modèle."))

    # 3 ---------------------------------------------------------------- company
    sl = content(prs, T("02  COMPANY SNAPSHOT", "02  LA SOCIÉTÉ"), T("Two businesses moving in opposite directions", "Deux activités qui vont dans des directions opposées"))
    blocks = [(T("Client Computing (CCPG), 61% of revenue", "Client Computing (CCPG), 61 % du CA"), T("x86 processors for PCs: $32.2bn in 2025 at a 28.9% operating margin. Units × share × price.", "Processeurs x86 pour PC : 32,2 Md$ en 2025 à 28,9 % de marge opérationnelle. Volumes × part de marché × prix.")),
              (T("Data Center & AI (DCAI), 32%", "Data Center & AI (DCAI), 32 %"), T("Server CPUs and custom chips: $16.9bn, +53% in 9M 2026. The growth engine, but supply-constrained into 2028.", "CPU serveurs et puces sur mesure : 16,9 Md$, +53 % sur 9 mois 2026. Le moteur de croissance, mais contraint par l’offre jusqu’en 2028.")),
              (T("Intel Foundry", "Intel Foundry"), T("Makes almost all of Intel's chips and tries to win outside customers. Lost $10.3bn in 2025 and $6.4bn in 9M 2026: the products earn, the factories lose.", "Fabrique presque toutes les puces d’Intel et cherche des clients externes. Perte de 10,3 Md$ en 2025 et de 6,4 Md$ sur 9 mois 2026 : les produits gagnent, les usines perdent.")),
              (T("Capital", "Capital"), T("CEO Lip-Bu Tan prioritises manufacturing: $20bn gross capex in 2026, 'up strongly' in 2027. Equity from the US government, SoftBank, Nvidia and a $20bn offering at $95 (Aug 2026). No dividend since 2024.", "Le DG Lip-Bu Tan donne la priorité à la production : 20 Md$ de capex brut en 2026, en « forte » hausse en 2027. Fonds propres apportés par l’État américain, SoftBank, Nvidia et une émission de 20 Md$ à 95 $ (août 2026). Pas de dividende depuis 2024."))]
    for i, (h, b) in enumerate(blocks):
        tb(sl, 0.6, 1.85 + 1.15 * i, 6.4, 0.32, h, 14, GREEN, True)
        tb(sl, 0.6, 2.18 + 1.15 * i, 6.4, 0.8, b, 12, INK)
    cd = CategoryChartData(); cd.categories = ["Client", "Data Center & AI", "Foundry", T("Other", "Autres")]
    cd.add_series(T("Revenue", "Chiffre d’affaires"), (32.2, 16.9, 17.8, 3.6)); cd.add_series(T("Operating income", "Résultat opérationnel"), (9.3, 3.4, -10.3, 0.3))
    gf = sl.shapes.add_chart(XL_CHART_TYPE.COLUMN_CLUSTERED, Inches(7.4), Inches(1.8), Inches(5.33), Inches(4.6), cd); ch = gf.chart
    style_chart(ch); ch.has_title = True; ch.chart_title.text_frame.text = T("2025, $bn (operating income incl. intersegment)", "2025, Md$ (résultat opérationnel, intersegments inclus)")
    ch.chart_title.text_frame.paragraphs[0].runs[0].font.size = Pt(12); ch.chart_title.text_frame.paragraphs[0].runs[0].font.bold = True
    for s_, col in zip(ch.plots[0].series, (GREEN, INK)):
        s_.format.fill.solid(); s_.format.fill.fore_color.rgb = RGB(col); s_.invert_if_negative = False
    pt = ch.plots[0].series[1].points[2]; pt.format.fill.solid(); pt.format.fill.fore_color.rgb = RGB(RED)
    from pptx.enum.chart import XL_TICK_LABEL_POSITION
    ch.category_axis.tick_label_position = XL_TICK_LABEL_POSITION.LOW
    ch.plots[0].has_data_labels = True; dl = ch.plots[0].data_labels; dl.font.size = Pt(10); dl.number_format = '0.0'; dl.number_format_is_linked = False; dl.position = XL_LABEL_POSITION.OUTSIDE_END
    source(sl, T("Source: Intel 10-K FY2025 (segment note), 10-Q Q3 2026.", "Source : Intel 10-K 2025 (note sectorielle), 10-Q T3 2026."))

    # 4 ---------------------------------------------------------------- industry
    sl = content(prs, T("03  INDUSTRY AND MACRO BACKDROP", "03  SECTEUR ET MACRO"), T("What moves the stock beyond the company", "Ce qui fait bouger le titre au-delà de la société"))
    cards = [(pc("−10%"), T("PC units, 2027", "Unités PC, 2027"), T("A memory shortage pushes PC prices up while IT budgets are tight: Intel expects the market to fall ~12% in 2026 and ~10% in 2027. PCs are about half of Intel's revenue.", "La pénurie de mémoire renchérit les PC alors que les budgets IT sont serrés : Intel prévoit un marché en baisse d’environ 12 % en 2026 et 10 % en 2027. Les PC font environ la moitié du CA d’Intel.")),
             (pc(">30%"), T("Server CPU units", "Unités CPU serveurs"), T("AI agents need more CPUs: industry server units grow >30% in 2026 and 2027. Intel is short of EMIB substrates and Intel 3 output, and lost Fab 28 (Israel) in October: AMD takes the share.", "Les agents IA consomment plus de CPU : +30 % d’unités serveurs en 2026 et 2027. Intel manque de substrats EMIB et de production Intel 3, et a perdu la Fab 28 (Israël) en octobre : AMD prend la part de marché.")),
             (pc("~45%"), T("US capacity at risk", "Capacité US à risque"), T("Democrats won both chambers on 3 November after campaigning on data-centre oversight; Goldman flags that moratoria could affect ~45% of planned US capacity. A bear-case risk.", "Les démocrates ont gagné les deux chambres le 3 novembre en faisant campagne sur l’encadrement des data centers ; Goldman estime que des moratoires pourraient toucher ~45 % de la capacité prévue aux États-Unis. Un risque du scénario pessimiste.")),
             (pc(">90%"), T("TSMC's share of Apple", "Part de TSMC chez Apple"), T("Chip designers want a second source beside TSMC and 18A yields are improving, but the reported Apple deal is unconfirmed and covers low-end chips from mid-2027.", "Les concepteurs de puces veulent une seconde source à côté de TSMC et les rendements 18A progressent, mais l’accord rapporté avec Apple n’est pas confirmé et ne couvre que des puces d’entrée de gamme à partir de mi-2027."))]
    for i, (v, h, b) in enumerate(cards):
        x, y = 0.6 + 6.27 * (i % 2), 1.85 + 2.4 * (i // 2)
        box(sl, x, y, 5.87, 2.15, ROW, "E5DCCB")
        tb(sl, x + 0.3, y + 0.2, 2.6, 0.8, v, 30, GREEN, True, anchor=MSO_ANCHOR.MIDDLE)
        tb(sl, x + 3.0, y + 0.25, 2.57, 0.7, h, 14, INK, True, anchor=MSO_ANCHOR.MIDDLE)
        tb(sl, x + 0.3, y + 1.05, 5.27, 1.0, b, 11, INK)
    source(sl, T("Source: Intel Q3 2026 prepared remarks (29 Oct 2026); Goldman Sachs (Nov 2026); WSJ (May 2026) via Tech Times; course Session 3.", "Source : présentation d’Intel du T3 2026 (29 oct. 2026) ; Goldman Sachs (nov. 2026) ; WSJ (mai 2026) via Tech Times ; cours, séance 3."))

    # 5 ---------------------------------------------------------------- where we differ
    sl = content(prs, T("04  WHERE WE DIFFER FROM THE STREET", "04  OÙ NOUS DIFFÉRONS DU CONSENSUS"), T("The Street needs margins back above 42%; Intel just guided 38%", "Le consensus a besoin de marges au-dessus de 42 % ; Intel vient d’annoncer 38 %"))
    rows = [["2027E", T("Street (Bloomberg)", "Consensus (Bloomberg)"), T("Our model", "Notre modèle"), T("Gap", "Écart")],
            [T("Revenue", "Chiffre d’affaires"), T("$69.3bn", "69,3 Md$"), T("$66.1bn", "66,1 Md$"), pc("−4.5%")],
            [T("Revenue growth", "Croissance du CA"), pc("+12.1%"), pc("+7.2%"), T("−4.9 pt", "−4,9 pt")],
            [T("Gross margin (non-GAAP)", "Marge brute (non-GAAP)"), pc("42.5%"), pc("39.7%"), T("−2.8 pt", "−2,8 pt")],
            [T("Adjusted EPS", "BPA ajusté"), usd(1.78), usd(1.33), pc("−25.2%")],
            [T("Free cash flow", "Free cash flow"), T("−$2.7bn", "−2,7 Md$"), T("−$5.7bn", "−5,7 Md$"), T("−$3.0bn", "−3,0 Md$")]]
    table(sl, 0.6, 1.85, 7.2, rows, [2.7, 1.7, 1.5, 1.3], sz=13, rh=0.5, hl=(4,))
    box(sl, 8.2, 1.85, 4.53, 3.0, MINT2, "E5DCCB")
    tb(sl, 8.5, 2.05, 3.95, 0.35, T("THE NUMBER THAT MATTERS", "LE CHIFFRE QUI COMPTE"), 11, GREEN, True, spc=120)
    tb(sl, 8.5, 2.45, 3.95, 2.3, T("Four quarters at Intel's Q4 guide of 25 cents is one dollar. The Street needs $1.78 — 44 cents a quarter, back to the Q3 peak. We have $1.33.",
                                   "Quatre trimestres à la guidance du T4 (25 cents) font un dollar. Le consensus a besoin de 1,78 $ — 44 cents par trimestre, retour au pic du T3. Nous avons 1,33 $."), 15, INK, True)
    tb(sl, 0.6, 5.05, 12.1, 1.4, [[(T("Why revenue is close but EPS is far: ", "Pourquoi le CA est proche mais le BPA loin : "), True),
                                    (T("Intel owns its fabs, so lower margins on the same volume and depreciation rising from $13.0bn to $16.1bn by 2028 hit EPS much harder than revenue. Each point of gross margin is worth about $0.10-0.11 of EPS (1% × $66bn × (1 − 12% tax) ÷ 5.48bn shares).",
                                       "Intel possède ses usines : une marge plus faible sur le même volume et des amortissements qui passent de 13,0 à 16,1 Md$ d’ici 2028 pèsent bien plus sur le BPA que sur le CA. Chaque point de marge brute vaut environ 0,10-0,11 $ de BPA (1 % × 66 Md$ × (1 − 12 % d’impôt) ÷ 5,48 Md d’actions)."), False)]], 12, INK)
    source(sl, T("Source: Bloomberg BEst consensus (6 Nov 2026); own model (Income Statement, Consensus sheets). Our GAAP gross margin is 38.5% (non-GAAP ≈ +1.2 pt).", "Source : consensus Bloomberg BEst (6 nov. 2026) ; notre modèle. Notre marge brute GAAP est de 38,5 % (non-GAAP ≈ +1,2 pt)."))

    # 6 ---------------------------------------------------------------- Q4 guide
    sl = content(prs, T("05  THE Q4 GUIDE", "05  LA GUIDANCE DU T4"), T("A beat in Q3, but the guide broke the outlook: the stock fell 28.6% in a day", "Un T3 au-dessus des attentes, mais la guidance a cassé les perspectives : −28,6 % en une séance"))
    cd = CategoryChartData(); cd.categories = [T("Q1 26", "T1 26"), T("Q2 26", "T2 26"), T("Q3 26", "T3 26"), T("Q4 26 guide", "T4 26 guid."), T("2027 Street /qtr", "2027 consensus /trim."), T("2027 ours /qtr", "2027 nous /trim.")]
    cd.add_series(T("Non-GAAP EPS ($)", "BPA non-GAAP ($)"), (0.29, 0.42, 0.52, 0.25, 0.44, 0.33))
    gf = sl.shapes.add_chart(XL_CHART_TYPE.COLUMN_CLUSTERED, Inches(0.6), Inches(1.8), Inches(6.6), Inches(4.7), cd); ch = gf.chart
    style_chart(ch, legend=False); ch.has_title = True; ch.chart_title.text_frame.text = T("Non-GAAP EPS per quarter ($)", "BPA non-GAAP par trimestre ($)")
    ch.chart_title.text_frame.paragraphs[0].runs[0].font.size = Pt(12); ch.chart_title.text_frame.paragraphs[0].runs[0].font.bold = True
    se = ch.plots[0].series[0]; se.format.fill.solid(); se.format.fill.fore_color.rgb = RGB("A9B4C4")
    for k, col in ((3, GREEN), (4, "888888"), (5, RED)):
        pt = se.points[k]; pt.format.fill.solid(); pt.format.fill.fore_color.rgb = RGB(col)
    ch.plots[0].has_data_labels = True; dl = ch.plots[0].data_labels; dl.number_format = '"$"0.00' if E else '0,00" $"'; dl.number_format_is_linked = False; dl.font.size = Pt(11); dl.position = XL_LABEL_POSITION.OUTSIDE_END
    ch.plots[0].gap_width = 60
    rows = [[T("Q3 2026 (29 Oct)", "T3 2026 (29 oct.)"), T("Reported", "Publié"), T("Consensus", "Consensus")],
            [T("Revenue", "Chiffre d’affaires"), T("$16.5bn", "16,5 Md$"), T("$16.6bn", "16,6 Md$")],
            [T("Non-GAAP gross margin", "Marge brute non-GAAP"), pc("44.1%"), pc("~42%")],
            [T("Non-GAAP EPS", "BPA non-GAAP"), usd(0.52), usd(0.41)],
            [T("Q4 revenue guide", "Guidance CA T4"), T("$15-16bn", "15-16 Md$"), T("~$17.1bn", "~17,1 Md$")],
            [T("Q4 EPS guide", "Guidance BPA T4"), usd(0.25), usd(0.43)]]
    table(sl, 7.6, 1.85, 5.13, rows, [2.33, 1.4, 1.4], sz=12, rh=0.42, hl=(5,))
    tb(sl, 7.6, 4.6, 5.13, 1.9, T("Intel guided gross margin down ~6 points on 'lower overall revenue against our fixed-cost base'. We did not raise numbers after the beat: the guide matters more than the quarter. Since then: −10.3% on 5 November (midterms), +7.7% on 6 November to $56.28, −60% from the June peak of $141.",
                                  "Intel a annoncé une marge brute en baisse d’environ 6 points, « un chiffre d’affaires plus faible face à notre base de coûts fixes ». Nous n’avons pas relevé nos chiffres après la publication : la guidance compte plus que le trimestre. Depuis : −10,3 % le 5 novembre (élections), +7,7 % le 6 novembre à 56,28 $, −60 % depuis le pic de juin à 141 $."), 12, INK)
    source(sl, T("Source: Intel Q1-Q3 2026 releases and prepared remarks; Bloomberg consensus (6 Nov 2026); own model ($1.33 ÷ 4 a quarter).", "Source : publications et présentations d’Intel T1-T3 2026 ; consensus Bloomberg (6 nov. 2026) ; notre modèle (1,33 $ ÷ 4 par trimestre)."))

    # 7 ---------------------------------------------------------------- financials
    sl = content(prs, T("06  FINANCIAL FORECAST", "06  PRÉVISIONS FINANCIÈRES"), T("Revenue by segment, margins near the Q4 run-rate, depreciation rising with the capex wave", "CA par segment, marges proches du rythme du T4, amortissements en hausse avec la vague de capex"))
    rows = [[T("$m, FY Dec", "M$, exercice déc."), "2024A", "2025A", "2026E", "2027E", "2028E"],
            [T("Revenue", "Chiffre d’affaires"), "53,101", "52,853", "61,718", "66,132", "73,223"],
            [T("Growth", "Croissance"), pc("−2.1%"), pc("−0.5%"), pc("+16.8%"), pc("+7.2%"), pc("+10.7%")],
            [T("Gross margin (GAAP)", "Marge brute (GAAP)"), pc("32.7%"), pc("34.8%"), pc("40.0%"), pc("38.5%"), pc("40.5%")],
            [T("EBITDA margin", "Marge d’EBITDA"), pc("−0.6%"), pc("18.0%"), pc("24.2%"), pc("31.5%"), pc("35.0%")],
            [T("Adjusted EPS ($)", "BPA ajusté ($)"), "–", "–", "1.48", "1.33", "1.70"],
            [T("Consensus EPS ($)", "BPA consensus ($)"), "–", "–", "1.49", "1.78", "3.00"],
            [T("Capex, net ($m)", "Capex net (M$)"), "23,186", "16,095", "19,785", "25,130", "24,164"],
            [T("Diluted shares (m)", "Actions diluées (M)"), "4,280", "4,530", "5,218", "5,480", "5,525"]]
    if not E: rows = [[c.replace(",", " ") if i and j else c for j, c in enumerate(r)] for i, r in enumerate(rows)]
    if not E: rows = [[c.replace(".", ",") if i in (5, 6) and j else c for j, c in enumerate(r)] for i, r in enumerate(rows)]
    table(sl, 0.6, 1.85, 7.9, rows, [2.4, 1.1, 1.1, 1.1, 1.1, 1.1], sz=12, rh=0.44, hl=(5,))
    tb(sl, 8.9, 1.85, 3.83, 4.5, [[(T("Revenue build. ", "Construction du CA. "), True), (T("Client = PC units × Intel share × price: 2027E units −10%, share −3%, price +4% → −9%. Data center = server units × share/supply × price: +30%, −8%, +5% → +26%. Total +7%.", "Client = unités PC × part d’Intel × prix : 2027E unités −10 %, part −3 %, prix +4 % → −9 %. Data center = unités serveurs × part/offre × prix : +30 %, −8 %, +5 % → +26 %. Total +7 %."), False)],
                                  [(T("Margins. ", "Marges. "), True), (T("GAAP gross margin 38.5% in 2027E, recovering to 46% by 2033E as 18A/14A costs fall, still below the 55-60% of the 2010s. D&A rises from $13.0bn to $16.1bn by 2028E.", "Marge brute GAAP de 38,5 % en 2027E, remontant à 46 % en 2033E avec la baisse des coûts 18A/14A, encore loin des 55-60 % des années 2010. Amortissements de 13,0 à 16,1 Md$ en 2028E."), False)],
                                  [(T("Below the line. ", "Sous le résultat opérationnel. "), True), (T("Tax 12% in 2027E, ~$1.1bn of minorities a year (Brookfield, Apollo fab partners), shares +0.8% a year from stock pay, no buybacks.", "Impôt de 12 % en 2027E, ~1,1 Md$ de minoritaires par an (Brookfield, Apollo), actions +0,8 % par an avec la rémunération en actions, pas de rachats."), False)]], 12, INK)
    source(sl, T("Source: Intel 10-K FY2025 and 10-Qs 2026 (2026E = 9 months reported + Q4 guide); Bloomberg BEst consensus (6 Nov 2026); own estimates.", "Source : Intel 10-K 2025 et 10-Q 2026 (2026E = 9 mois publiés + guidance T4) ; consensus Bloomberg BEst (6 nov. 2026) ; nos estimations."))

    # 8 ---------------------------------------------------------------- variant perception
    sl = content(prs, T("07  VARIANT PERCEPTION", "07  VARIANT PERCEPTION"), T("Where we differ from the market", "Où nous différons du marché"))
    tb(sl, 0.6, 1.8, 5.9, 0.35, T("WHAT THE MARKET BELIEVES", "CE QUE CROIT LE MARCHÉ"), 11, SLATE, True, spc=120)
    tb(sl, 6.8, 1.8, 5.9, 0.35, T("OUR VIEW", "NOTRE VUE"), 11, GREEN, True, spc=120)
    vp = [(T("“2026 margins are the new base: 42.5% in 2027, $3.00 of EPS in 2028.”", "« Les marges de 2026 sont la nouvelle base : 42,5 % en 2027, 3,00 $ de BPA en 2028. »"),
           T("They came from reserved inventory, price rises and a shortage. Intel itself guides 38% for Q4 'against our fixed-cost base'.", "Elles viennent de stocks réservés, de hausses de prix et d’une pénurie. Intel annonce elle-même 38 % pour le T4 « face à notre base de coûts fixes ».")),
          (T("“Intel is an AI winner: server CPUs are booming.”", "« Intel est un gagnant de l’IA : les CPU serveurs explosent. »"),
           T("We agree on demand; the problem is supply. Substrates, Intel 3 and Fab 28 cap Intel's shipments; AMD takes the share. We still model data center +26%.", "D’accord sur la demande ; le problème est l’offre. Substrats, Intel 3 et Fab 28 plafonnent les livraisons ; AMD prend la part. Nous modélisons tout de même +26 % en data center.")),
          (T("“After a 60% fall, it is priced in.”", "« Après −60 %, tout est dans le prix. »"),
           T("Not on earnings: the stock trades at 32.5x Street NTM EPS and 42.4x ours, against 16.8x for peers. The price still assumes margins return above 42%.", "Pas sur les bénéfices : le titre vaut 32,5x le BPA 12 mois du consensus et 42,4x le nôtre, contre 16,8x pour les pairs. Le prix suppose toujours un retour des marges au-dessus de 42 %.")),
          (T("“The Apple deal makes the foundry a business.”", "« L’accord avec Apple fait de la fonderie une vraie activité. »"),
           T("Unconfirmed by both companies, low-end chips from mid-2027, TSMC keeps >90% of Apple's volume: ~$1.2bn of external foundry revenue in 2027E. Intel Foundry still loses ~$1.9bn a quarter.", "Non confirmé par les deux sociétés, puces d’entrée de gamme à partir de mi-2027, TSMC garde plus de 90 % des volumes d’Apple : ~1,2 Md$ de CA fonderie externe en 2027E. Intel Foundry perd encore ~1,9 Md$ par trimestre."))]
    for i, (a, b) in enumerate(vp):
        y = 2.2 + 1.08 * i
        box(sl, 0.6, y, 5.9, 0.98, ROW, "E5DCCB"); tb(sl, 0.85, y + 0.08, 5.4, 0.82, a, 12, SLATE, italic=True, anchor=MSO_ANCHOR.MIDDLE)
        box(sl, 6.8, y, 5.93, 0.98, MINT2, "E5DCCB"); tb(sl, 7.05, y + 0.08, 5.45, 0.82, b, 11, INK, anchor=MSO_ANCHOR.MIDDLE)
    source(sl, T("Source: Bloomberg consensus and NTM multiples (6 Nov 2026); Intel prepared remarks Q3 2026; WSJ (May 2026) via Tech Times; own model.", "Source : consensus et multiples 12 mois Bloomberg (6 nov. 2026) ; présentation d’Intel T3 2026 ; WSJ (mai 2026) via Tech Times ; notre modèle."))

    # 9 ---------------------------------------------------------------- valuation
    sl = content(prs, T("08  VALUATION", "08  VALORISATION"), T("Price target $32: every method sits below the share price", "Objectif de 32 $ : toutes les méthodes sont sous le cours"))
    rows = [[T("Method", "Méthode"), T("Value", "Valeur"), T("Weight", "Poids"), T("Contrib.", "Contrib.")],
            [T("DCF (WACC 11.5%, g 2.5%)", "DCF (WACC 11,5 %, g 2,5 %)"), usd(20.96), "30%" if E else "30 %", usd(6.29)],
            [T("EV/EBITDA comps (13.3x median)", "Comparables VE/EBITDA (médiane 13,3x)"), usd(48.68), "40%" if E else "40 %", usd(19.47)],
            [T("P/E comps (16.8x median)", "Comparables PER (médiane 16,8x)"), usd(22.31), "30%" if E else "30 %", usd(6.69)],
            [T("Price target (rounded)", "Objectif (arrondi)"), usd(32, 0), "100%" if E else "100 %", usd(32.45)]]
    table(sl, 0.6, 1.85, 6.6, rows, [3.3, 1.1, 1.0, 1.2], sz=12, rh=0.46, hl=(4,))
    tb(sl, 0.6, 4.3, 6.6, 2.2, [[(T("Cross-check: ", "Contrôle : "), True), (T("$1.33 × 24.1x = $32. We pay a 43% premium to the peer median P/E because 2027 is a trough year, far less than the 51.2x hidden in the Street's $90.91 target.", "1,33 $ × 24,1x = 32 $. Nous payons une prime de 43 % sur le PER médian des pairs car 2027 est une année de creux, bien moins que les 51,2x implicites dans l’objectif du consensus à 90,91 $."), False)],
                                [(T("Weights: ", "Pondérations : "), True), (T("EV/EBITDA gets most weight because GAAP EPS is distorted by one-offs and the $13.7bn Escrowed Shares derivative; the DCF only 30% because 59% of its value is terminal value and FCF is negative in 2027-28.", "VE/EBITDA pèse le plus car le BPA GAAP est faussé par des éléments ponctuels et le dérivé Escrowed Shares de 13,7 Md$ ; le DCF seulement 30 % car 59 % de sa valeur est terminale et le FCF est négatif en 2027-28."), False)]], 11, INK)
    cd = CategoryChartData(); cd.categories = [T("Street PT", "Objectif consensus"), T("Lower EPS", "BPA plus bas"), T("Lower multiple", "Multiple plus bas"), T("Our PT", "Notre objectif")]
    base = (0, 67.98, 32.0, 0); vals = (90.91, 22.93, 35.98, 32.0)
    cd.add_series("base", base); cd.add_series("value", vals)
    gf = sl.shapes.add_chart(XL_CHART_TYPE.COLUMN_STACKED, Inches(7.5), Inches(1.8), Inches(5.23), Inches(4.7), cd); ch = gf.chart
    style_chart(ch, legend=False); ch.has_title = True; ch.chart_title.text_frame.text = T("From the Street's target to ours ($/share)", "De l’objectif du consensus au nôtre ($/action)")
    ch.chart_title.text_frame.paragraphs[0].runs[0].font.size = Pt(12); ch.chart_title.text_frame.paragraphs[0].runs[0].font.bold = True
    b0, v0 = ch.plots[0].series; b0.format.fill.background(); ch.plots[0].gap_width = 55
    v0.format.fill.solid(); v0.format.fill.fore_color.rgb = RGB(RED)
    for k, col in ((0, "888888"), (3, GREEN)):
        pt = v0.points[k]; pt.format.fill.solid(); pt.format.fill.fore_color.rgb = RGB(col)
    labs = [usd(90.91), "−" + usd(22.93), "−" + usd(35.98), usd(32, 0)]
    for k, lab in enumerate(labs):
        p_ = v0.points[k]; p_.data_label.has_text_frame = True; p_.data_label.text_frame.text = lab
        p_.data_label.text_frame.paragraphs[0].runs[0].font.size = Pt(11); p_.data_label.text_frame.paragraphs[0].runs[0].font.bold = True
        p_.data_label.position = XL_LABEL_POSITION.INSIDE_END
        p_.data_label.text_frame.paragraphs[0].runs[0].font.color.rgb = RGB(WHITE)
    source(sl, T("Source: own model (DCF, Comps, Valuation Summary, Target Price sheets); Bloomberg NTM consensus for AMD, Nvidia, Qualcomm, Arm, TSMC, GlobalFoundries, Texas Instruments, Broadcom (6 Nov 2026).", "Source : notre modèle (feuilles DCF, Comps, Valuation Summary, Target Price) ; consensus 12 mois Bloomberg pour AMD, Nvidia, Qualcomm, Arm, TSMC, GlobalFoundries, Texas Instruments, Broadcom (6 nov. 2026)."))

    # 10 --------------------------------------------------------------- catalysts
    sl = content(prs, T("09  CATALYSTS", "09  CATALYSEURS"), T("Four dated catalysts; January's guide is the one that resets the Street", "Quatre catalyseurs datés ; la guidance de janvier est celle qui recale le consensus"))
    ev = [(T("Late Jan 2027", "Fin janv. 2027"), T("Q4 results and first 2027 outlook (gross margin, capex). If consensus moves to our $1.33 at its own 51.2x: −$22.93 a share.", "Résultats du T4 et premières perspectives 2027 (marge brute, capex). Si le consensus rejoint nos 1,33 $ à son propre 51,2x : −22,93 $ par action.")),
          (T("Jan 2027", "Janv. 2027"), T("IDC/Gartner Q4 PC data and CES (Nova Lake). The Street pencils in an H2 2027 PC recovery; Intel plans units ~−10%.", "Données PC du T4 (IDC/Gartner) et CES (Nova Lake). Le consensus prévoit une reprise des PC au S2 2027 ; Intel prévoit ~−10 %.")),
          (T("H1 2027", "S1 2027"), T("Data-centre policy after the midterms: each −10% on data center revenue ≈ −$0.19 of EPS. Bear-case risk.", "Politique des data centers après les élections : chaque −10 % de CA data center ≈ −0,19 $ de BPA. Risque du scénario pessimiste.")),
          (T("Q2-Q3 2027", "T2-T3 2027"), T("First Apple chips on 18A-P (Ming-Chi Kuo timing): ~$1.2bn of external foundry revenue, too small to change group margins.", "Premières puces Apple sur 18A-P (calendrier Ming-Chi Kuo) : ~1,2 Md$ de CA fonderie externe, trop peu pour changer les marges du groupe."))]
    ln = sl.shapes.add_connector(1, Inches(0.85), Inches(2.45), Inches(12.4), Inches(2.45)); ln.line.color.rgb = RGB("A9B4C4"); ln.line.width = Pt(2)
    for i, (d, t) in enumerate(ev):
        x = 0.6 + 3.05 * i
        tb(sl, x, 1.85, 2.8, 0.35, d, 14, GREEN, True)
        dot = sl.shapes.add_shape(MSO_SHAPE.OVAL, Inches(x + 0.1), Inches(2.33), Inches(0.24), Inches(0.24)); dot.fill.solid(); dot.fill.fore_color.rgb = RGB(GREEN); dot.line.fill.background()
        tb(sl, x, 2.8, 2.8, 2.4, t, 12, INK)
    box(sl, 0.6, 5.35, 12.13, 0.95, MINT2, "E5DCCB")
    tb(sl, 0.9, 5.35, 11.6, 0.95, [[(T("The number to watch: ", "Le chiffre à surveiller : "), True), (T("the 2027 gross-margin guide in late January. Below 40% non-GAAP, consensus has to move toward our numbers; above 42% with data center over $9bn a quarter, we are wrong.", "la guidance de marge brute 2027 fin janvier. Sous 40 % non-GAAP, le consensus doit se rapprocher de nos chiffres ; au-dessus de 42 % avec un data center à plus de 9 Md$ par trimestre, nous avons tort."), False)]], 13, INK, anchor=MSO_ANCHOR.MIDDLE)
    source(sl, T("Source: Intel prepared remarks Q3 2026; Bloomberg consensus (6 Nov 2026); course Session 3 (midterms); own model.", "Source : présentation d’Intel T3 2026 ; consensus Bloomberg (6 nov. 2026) ; cours, séance 3 (élections) ; notre modèle."))

    # 11 --------------------------------------------------------------- risks
    sl = content(prs, T("10  RISKS AND COVER DISCIPLINE", "10  RISQUES ET DISCIPLINE DE RACHAT"), T("Bull $71, bear $20: the skew still favours a Sell", "Haussier 71 $, baissier 20 $ : l’asymétrie favorise toujours la vente"))
    rows = [[T("Scenario", "Scénario"), T("Key assumptions", "Hypothèses clés"), T("Value", "Valeur"), T("vs price", "vs cours"), T("Prob.", "Prob.")],
            [T("Bull", "Haussier"), T("Supply fixed, Apple ramps, 14A anchor customer, PCs back in H2 2027 → $1.78 × 40x", "Offre rétablie, Apple monte en charge, client 14A, PC de retour au S2 2027 → 1,78 $ × 40x"), usd(71.04), pc("+26%"), pc("20%")],
            [T("Base", "Central"), T("PC −10%, supply-capped servers, GM 38.5% → $1.33 × 24.1x", "PC −10 %, serveurs plafonnés, MB 38,5 % → 1,33 $ × 24,1x"), usd(32, 0), pc("−43%"), pc("55%")],
            [T("Bear", "Baissier"), T("Data-centre moratoria, PC −15%, AMD gains, 14A slips → $0.90 × 22x", "Moratoires sur les data centers, PC −15 %, AMD gagne, 14A glisse → 0,90 $ × 22x"), usd(19.80), pc("−65%"), pc("25%")],
            [T("Probability-weighted", "Pondéré"), "", usd(36.76), pc("−35%"), pc("100%")]]
    table(sl, 0.6, 1.85, 7.9, rows, [1.6, 3.6, 1.0, 0.95, 0.75], sz=11, rh=0.62, hl=(2,), aligns=[PP_ALIGN.LEFT, PP_ALIGN.LEFT, PP_ALIGN.RIGHT, PP_ALIGN.RIGHT, PP_ALIGN.RIGHT])
    tb(sl, 0.6, 5.1, 7.9, 1.4, T("Short squeeze: sentiment swings violently (Intel +24% on its Q1 print). Signposts: short interest and estimate revisions. We would not short ahead of the January print without a stop.",
                                 "Short squeeze : le sentiment change violemment (Intel +24 % sur ses résultats du T1). Signaux : positions vendeuses et révisions d’estimations. Nous ne vendrions pas à découvert avant la publication de janvier sans stop."), 12, INK)
    box(sl, 8.9, 1.85, 3.83, 4.6, REDSOFT, "E8C3BD")
    tb(sl, 9.15, 2.05, 3.4, 0.35, T("WE CHANGE THE CALL IF", "NOUS CHANGEONS D’AVIS SI"), 11, RED, True, spc=120)
    tb(sl, 9.15, 2.5, 3.4, 3.8, ["• " + T("Data center revenue above $9bn a quarter at gross margin above 42% (supply fixed early).", "Le CA data center dépasse 9 Md$ par trimestre avec une marge brute au-dessus de 42 % (offre rétablie tôt)."),
                                 "• " + T("Apple volumes confirmed together with a 14A anchor customer and prepayments.", "Les volumes d’Apple sont confirmés avec un client de référence 14A et des prépaiements."),
                                 "• " + T("DRAM contract prices fall early and IDC data show PCs recovering in H1 2027.", "Les prix contractuels de la DRAM baissent tôt et les données IDC montrent une reprise des PC dès le S1 2027.")], 12, INK)
    source(sl, T("Source: own model (Scenarios sheet); Intel prepared remarks; Bloomberg (6 Nov 2026).", "Source : notre modèle (feuille Scenarios) ; présentations d’Intel ; Bloomberg (6 nov. 2026)."))

    # 12 --------------------------------------------------------------- sources
    sl = content(prs, T("11  SOURCES AND DISCLOSURES", "11  SOURCES ET AVERTISSEMENTS"), T("Sources", "Sources"))
    src = ["[1] Intel Corporation, Form 10-K for the fiscal year ended 27 December 2025 (SEC EDGAR).",
           "[2] Intel Corporation, Forms 10-Q for the quarters ended 28 March, 27 June and 26 September 2026 (SEC EDGAR).",
           T("[3] Intel Corporation, CEO/CFO prepared remarks, Q1-Q3 2026 earnings calls (Q3: 29 October 2026).", "[3] Intel Corporation, présentations du DG et du DAF, T1-T3 2026 (T3 : 29 octobre 2026)."),
           "[4] Intel Corporation, \"Intel announces upsize and pricing of $20 billion common stock offering\", 11 August 2026.",
           T("[5] Bloomberg L.P., INTC US Equity: BEst consensus, ANR, beta, peers (NTM), weekly prices, 6 November 2026.", "[5] Bloomberg L.P., INTC US Equity : consensus BEst, ANR, bêta, pairs (12 mois), cours hebdomadaires, 6 novembre 2026."),
           "[6] StockTitan (6 Nov 2026); Forbes (5 Nov 2026), chip-stock moves after the midterms.",
           "[7] Tech Times (20 Jun 2026), Gadget Hacks (2026): reports on the Apple-Intel agreement (WSJ, May 2026).",
           "[8] Damodaran, A. (1 Nov 2026), implied equity risk premium, NYU Stern.",
           T("[9] SKEMA Business School, Equity Research course materials, Sessions 1-4 (Paul Wuh).", "[9] SKEMA Business School, supports du cours d’Equity Research, séances 1-4 (Paul Wuh).")]
    tb(sl, 0.6, 1.85, 12.13, 3.4, src, 11, INK)
    tb(sl, 0.6, 5.3, 12.13, 1.2, T("Disclosure: student research by Noah Doose and Victor Endrizzi, prepared for the Equity Research course at SKEMA Business School (November 2026) and adapted to the Thoth Ledger pitch format. Intel was assigned by the instructor; it is not a holding of the Thoth Ledger value strategy. AI (Claude) was used for extraction from filings, first drafts and formatting; every figure was checked against the filings and Bloomberg, and the rating, target and thesis are the authors' own. Not investment advice; prices as of 6 November 2026.",
                                   "Avertissement : travail étudiant de Noah Doose et Victor Endrizzi, réalisé pour le cours d’Equity Research de SKEMA Business School (novembre 2026) et adapté au format des pitches de Thoth Ledger. Intel a été attribué par l’enseignant ; ce n’est pas une ligne de la stratégie value de Thoth Ledger. L’IA (Claude) a servi à l’extraction des documents, aux premiers jets et à la mise en forme ; chaque chiffre a été vérifié dans les publications et sur Bloomberg, et l’avis, l’objectif et la thèse sont ceux des auteurs. Pas un conseil en investissement ; cours au 6 novembre 2026."), 10, SLATE)
    name = f"INTC_US_Intel_pitch{'' if E else '_FR'}.pptx"
    prs.save(str(OUT / name)); print(OUT / name)


if __name__ == "__main__":
    OUT.mkdir(parents=True, exist_ok=True)
    for lg in ("en", "fr"):
        build(lg)
