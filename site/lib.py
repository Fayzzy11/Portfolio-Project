"""Shared helpers for the Research Ledger site: formatting, i18n, HTML shell, tables and SVG charts."""
import html
import re
from datetime import date
from pathlib import Path

import markdown

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
DOCS = ROOT / "docs"
DATA = HERE / "data"
CONTENT = HERE / "content"

SITE = "Research Ledger"
AUTHOR = "Noah Doose"
REPO = "https://github.com/Fayzzy11/Portfolio-Project"
HORUS_URL = "https://fayzzy11.github.io/HORUS_AM/"
TODAY = date.today()
MONTHS_FR = ["janv.", "févr.", "mars", "avr.", "mai", "juin", "juil.", "août", "sept.", "oct.", "nov.", "déc."]

esc = html.escape

# ---------------------------------------------------------------- UI strings
UI = {
    "en": {
        "home": "Home", "strategies": "Strategies", "pitches": "Stock pitches", "research": "Research", "database": "Database",
        "journal": "Journal", "about": "About", "methodology": "Methodology", "skip": "Skip to content", "menu": "Menu",
        "theme": "Switch light or dark theme", "tagline": "Equity research & strategies", "on_page": "On this page",
        "sections": "Sections", "elsewhere": "Elsewhere", "code": "Code on GitHub", "horus": "Horus AM",
        "foot1": "Student research by Noah Doose, MSc Financial Markets & Investments (SKEMA Business School, Paris), CFA Level II candidate.",
        "foot2": "Educational and interview material. Nothing here is investment advice or an offer of any security. Licensed market data are not redistributed: pages show methodology and aggregated results only.",
        "built": "Updated", "lang_other": "FR", "lang_label": "Version française",
        "Overweight": "Overweight", "Neutral": "Neutral", "Underweight": "Underweight", "Sell": "Sell", "Buy": "Buy",
        "Bear": "Bear", "Base": "Base", "Bull": "Bull", "price": "Price", "target": "Target", "upside": "Upside",
        "read": "Read", "open": "Open", "all": "All", "of": "of",
    },
    "fr": {
        "home": "Accueil", "strategies": "Stratégies", "pitches": "Stock pitches", "research": "Recherche", "database": "Données",
        "journal": "Journal", "about": "À propos", "methodology": "Méthodologie", "skip": "Aller au contenu", "menu": "Menu",
        "theme": "Basculer en thème clair ou sombre", "tagline": "Recherche actions & stratégies", "on_page": "Sur cette page",
        "sections": "Rubriques", "elsewhere": "Ailleurs", "code": "Code sur GitHub", "horus": "Horus AM",
        "foot1": "Travail de recherche étudiant de Noah Doose, MSc Financial Markets & Investments (SKEMA Business School, Paris), candidat au CFA niveau II.",
        "foot2": "Contenu pédagogique et de préparation aux entretiens. Rien ici n'est un conseil en investissement ni une offre de titres. Les données de marché sous licence ne sont pas redistribuées : les pages montrent la méthode et des résultats agrégés.",
        "built": "Mis à jour le", "lang_other": "EN", "lang_label": "English version",
        "Overweight": "Surpondérer", "Neutral": "Neutre", "Underweight": "Sous-pondérer", "Sell": "Vendre", "Buy": "Acheter",
        "Bear": "Pessimiste", "Base": "Central", "Bull": "Optimiste", "price": "Cours", "target": "Objectif", "upside": "Potentiel",
        "read": "Lire", "open": "Ouvrir", "all": "Tous", "of": "sur",
    },
}

NAV = [("index", "home", ""), ("strategies", "strategies", "strategies/"), ("pitches", "pitches", "pitches/"),
       ("research", "research", "research/"), ("database", "database", "database/"), ("about", "about", "about/")]

FR_NAMES = {
    "France": "France", "United States": "États-Unis", "Japan": "Japon", "Hong Kong": "Hong Kong", "United Kingdom": "Royaume-Uni",
    "Germany": "Allemagne", "Switzerland": "Suisse", "Netherlands": "Pays-Bas", "Italy": "Italie", "Spain": "Espagne",
    "Sweden": "Suède", "Denmark": "Danemark", "Canada": "Canada", "Australia": "Australie",
    "Consumer Discretionary": "Consommation discrétionnaire", "Consumer Staples": "Consommation de base", "Financials": "Finance",
    "Information Technology": "Technologies de l'information", "Materials": "Matériaux", "Health Care": "Santé",
    "Industrials": "Industrie", "Utilities": "Services aux collectivités", "Energy": "Énergie",
    "Communication Services": "Services de communication", "Real Estate": "Immobilier",
    "Euronext Paris": "Euronext Paris", "NYSE": "NYSE", "Tokyo Stock Exchange": "Bourse de Tokyo", "HKEX": "HKEX",
    "Equities": "Actions", "Bonds": "Obligations", "Commodities": "Matières premières",
}


def t(lang, key):
    return UI[lang].get(key, key)


def tr(lang, s):
    """Translate a proper name (country, sector, exchange) when a French form exists."""
    return FR_NAMES.get(s, s) if lang == "fr" else s


# ---------------------------------------------------------------- number formatting
def _dec(s, lang):
    if lang != "fr":
        return s
    return s.replace(",", " ").replace(".", ",")


def pct(x, d=1, sign=False, lang="en"):
    if x is None:
        return "—"
    s = f"{x * 100:+,.{d}f}" if sign else f"{x * 100:,.{d}f}"
    s = _dec(s, lang).replace("-", "−")
    return s + (" %" if lang == "fr" else "%")


def num(x, d=1, lang="en"):
    if x is None:
        return "—"
    return _dec(f"{x:,.{d}f}", lang).replace("-", "−")


def money(sym, v, lang="en", d=None):
    if d is None:
        d = 0 if v >= 1000 else 2
    s = _dec(f"{v:,.{d}f}", lang)
    return f"{s} {sym}" if lang == "fr" else f"{sym}{s}"


def cls_sign(x):
    return "" if x is None else ("pos" if x > 0 else "neg" if x < 0 else "")


def slugify(s):
    return re.sub(r"[^a-z0-9]+", "-", s.lower()).strip("-")


def fr_date(d):
    return f"{d.day} {MONTHS_FR[d.month - 1]} {d.year}"


def built(lang):
    return fr_date(TODAY) if lang == "fr" else TODAY.strftime("%d %b %Y")


# ---------------------------------------------------------------- markdown
def md(text):
    out = markdown.markdown(text, extensions=["tables", "sane_lists", "attr_list"])
    return out.replace("<table>", '<div class="tbl-wrap"><table class="t">').replace("</table>", "</table></div>")


def md_inline(text):
    return markdown.markdown(text).replace("<p>", "").replace("</p>", "")


def front(path):
    txt = path.read_text(encoding="utf-8")
    meta = {}
    if txt.startswith("---"):
        _, fm, txt = txt.split("---", 2)
        for line in fm.strip().splitlines():
            k, _, v = line.partition(":")
            meta[k.strip()] = v.strip()
    return meta, txt.strip()


def strip_h1(txt):
    return re.sub(r"^# .*\n+", "", txt, count=1)


# ---------------------------------------------------------------- HTML blocks
def tbl(head, rows, num_cols=(), cls="", sortable=False, row_cls=None):
    th = "".join(f'<th class="n">{h}</th>' if i in num_cols else f"<th>{h}</th>" for i, h in enumerate(head))
    body = []
    for r_i, r in enumerate(rows):
        tds = []
        for i, c in enumerate(r):
            v = None
            if isinstance(c, tuple):
                c, v = c
            attr = f' data-v="{v}"' if v is not None else ""
            tds.append(f'<td class="n"{attr}>{c}</td>' if i in num_cols else f"<td{attr}>{c}</td>")
        rc = row_cls(r_i, r) if row_cls else ""
        body.append(f'<tr class="{rc}">' + "".join(tds) + "</tr>")
    s = " data-sortable" if sortable else ""
    return f'<div class="tbl-wrap {cls}"><table class="t"{s}><thead><tr>{th}</tr></thead><tbody>{"".join(body)}</tbody></table></div>'


def section(id_, title, inner, sub="", alt=False):
    p = f"<p>{sub}</p>" if sub else ""
    return f'<section class="sec{" alt" if alt else ""}" id="{id_}"><div class="shead"><h2>{title}</h2>{p}</div>{inner}</section>'


def stat(k, v, s="", cls=""):
    return f'<div class="stat"><div class="k">{k}</div><div class="v {cls}">{v}</div>{f"<div class=s>{s}</div>" if s else ""}</div>'


def doc_layout(lang, toc, sections):
    links = "".join(f'<a href="#{i}">{label}</a>' for i, label in toc)
    return (f'<div class="wrap"><div class="doc"><nav class="toc" aria-label="{t(lang, "on_page")}"><b>{t(lang, "on_page")}</b>{links}</nav>'
            f'<div>{"".join(sections)}</div></div></div>')


def phead(eyebrow, title, lede, crumbs=""):
    c = f'<div class="crumbs">{crumbs}</div>' if crumbs else ""
    return (f'<header class="phead"><div class="wrap">{c}<div class="eyebrow">{eyebrow}</div><h1>{title}</h1>'
            f'<p class="lede">{lede}</p></div></header>')


ICON_EXT = '<svg viewBox="0 0 16 16" aria-hidden="true"><path d="M6 3H3v10h10v-3M9 3h4v4M13 3 7 9" fill="none" stroke="currentColor" stroke-width="1.6"/></svg>'
ICON_DL = '<svg viewBox="0 0 16 16" aria-hidden="true"><path d="M8 2v8m-3.5-3.5L8 10l3.5-3.5M3 13h10" fill="none" stroke="currentColor" stroke-width="1.6"/></svg>'


def page(rel, lang, title, body, active, desc="", scripts=""):
    """rel: path relative to the language root, e.g. 'pitches/index.html'."""
    prefix = "fr/" if lang == "fr" else ""
    out = DOCS / prefix / rel
    depth = len(Path(prefix + rel).parts) - 1
    r = "../" * depth                       # to the site root (docs/)
    lr = r + prefix                          # to the language root
    other_root = r + ("" if lang == "fr" else "fr/")
    other = other_root + rel.replace("index.html", "")
    nav = "".join(f'<a href="{lr}{href}" class="{"on" if key == active else ""}">{t(lang, lab)}</a>' for key, lab, href in NAV)
    nav += f'<a href="{HORUS_URL}" rel="noopener">{t(lang, "horus")} ↗</a>'
    full_title = f"{title} · {SITE}" if title != SITE else f"{SITE} — {AUTHOR}"
    alt_lang = "fr" if lang == "en" else "en"
    doc = f"""<!doctype html>
<html lang="{lang}">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{esc(full_title)}</title>
<meta name="description" content="{esc(desc)}">
<link rel="alternate" hreflang="{alt_lang}" href="{other}">
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;650;700;750&family=IBM+Plex+Mono:wght@400;500&display=swap">
<link rel="stylesheet" href="{r}assets/site.css">
<link rel="icon" href="data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 32 32'%3E%3Crect width='32' height='32' rx='7' fill='%230B6E4F'/%3E%3Ctext x='16' y='21.5' font-family='Arial' font-weight='700' font-size='14' fill='white' text-anchor='middle'%3END%3C/text%3E%3C/svg%3E">
<script src="{r}assets/site.js"></script>
</head>
<body>
<a class="skip" href="#main">{t(lang, "skip")}</a>
<header class="top"><div class="wrap">
 <a class="brand" href="{lr}"><span class="mark">ND</span><span><b>{AUTHOR}</b><small>{SITE} · {t(lang, "tagline")}</small></span></a>
 <nav class="nav" id="nav" aria-label="Main">{nav}</nav>
 <div class="tools">
  <a class="tbtn" href="{other}" hreflang="{alt_lang}" title="{t(lang, "lang_label")}">{t(lang, "lang_other")}</a>
  <button class="tbtn" id="theme" aria-label="{t(lang, "theme")}" title="{t(lang, "theme")}"><svg viewBox="0 0 16 16" aria-hidden="true"><circle cx="8" cy="8" r="6.5" fill="none" stroke="currentColor" stroke-width="1.5"/><path d="M8 1.5a6.5 6.5 0 0 1 0 13z" fill="currentColor"/></svg></button>
  <button class="tbtn menu" id="menu" aria-label="{t(lang, "menu")}" aria-expanded="false" aria-controls="nav"><svg viewBox="0 0 16 16" aria-hidden="true"><path d="M2 4h12M2 8h12M2 12h12" stroke="currentColor" stroke-width="1.6"/></svg></button>
 </div>
</div></header>
<main id="main">
{body}
</main>
<footer class="sitefoot"><div class="wrap">
 <div><b>{AUTHOR} · {SITE}</b><p>{t(lang, "foot1")}</p><p>{t(lang, "foot2")}</p></div>
 <div><b>{t(lang, "sections")}</b>{"".join(f'<a href="{lr}{href}">{t(lang, lab)}</a>' for key, lab, href in NAV[1:])}<a href="{lr}journal/">{t(lang, "journal")}</a><a href="{lr}methodology/">{t(lang, "methodology")}</a></div>
 <div><b>{t(lang, "elsewhere")}</b><a href="{HORUS_URL}">Horus Asset Management ↗</a><a href="{REPO}">{t(lang, "code")} ↗</a><p style="margin-top:12px">{t(lang, "built")} {built(lang)}.</p></div>
</div></footer>
{scripts}
</body>
</html>
"""
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(doc, encoding="utf-8")
    return out


# ---------------------------------------------------------------- SVG charts
def svg_hbars(labels, values, fmt, w=640, bar_h=26, gap=12, label_w=210, color="var(--accent)"):
    maxv = max(abs(v) for v in values) or 1
    h = len(values) * (bar_h + gap) + 4
    plot = w - label_w - 80
    g = []
    for i, (lab, v) in enumerate(zip(labels, values)):
        y = i * (bar_h + gap)
        bw = max(2, abs(v) / maxv * plot)
        g.append(f'<text class="lbl" x="{label_w - 12}" y="{y + bar_h / 2 + 4}" text-anchor="end">{esc(lab)}</text>'
                 f'<rect x="{label_w}" y="{y}" width="{bw:.1f}" height="{bar_h}" rx="3" fill="{color}"/>'
                 f'<text class="val" x="{label_w + bw + 8:.1f}" y="{y + bar_h / 2 + 4}">{fmt(v)}</text>')
    return f'<svg viewBox="0 0 {w} {h}" role="img">{"".join(g)}</svg>'


def svg_diverging(labels, values, fmt, w=640, bar_h=24, gap=10, label_w=200, lim=None):
    lim = lim or max(abs(v) for v in values) * 1.1 or 1
    h = len(values) * (bar_h + gap) + 22
    plot = w - label_w - 20
    zero = label_w + plot / 2
    g = [f'<line class="axis" x1="{zero}" x2="{zero}" y1="0" y2="{h - 18}"/>']
    for i, (lab, v) in enumerate(zip(labels, values)):
        y = i * (bar_h + gap)
        bw = abs(v) / lim * plot / 2
        x = zero if v >= 0 else zero - bw
        c = "var(--pos)" if v >= 0 else "var(--neg)"
        tx, anchor = (zero + bw + 6, "start") if v >= 0 else (zero - bw - 6, "end")
        g.append(f'<text class="lbl" x="{label_w - 12}" y="{y + bar_h / 2 + 4}" text-anchor="end">{esc(lab)}</text>'
                 f'<rect x="{x:.1f}" y="{y}" width="{max(bw, 1.5):.1f}" height="{bar_h}" rx="3" fill="{c}"/>'
                 f'<text class="val" x="{tx:.1f}" y="{y + bar_h / 2 + 4}" text-anchor="{anchor}">{fmt(v)}</text>')
    g.append(f'<text x="{zero}" y="{h - 4}" text-anchor="middle">0</text>')
    return f'<svg viewBox="0 0 {w} {h}" role="img">{"".join(g)}</svg>'


def svg_columns(labels, values, fmt, w=760, h=240, m=(36, 10, 16, 34), series2=None, names=None):
    """Column chart; optional second series drawn side by side (benchmark)."""
    ml, mr, mt, mb = m
    allv = list(values) + (list(series2) if series2 else [])
    lo, hi = min(0, min(allv)), max(0, max(allv))
    span = (hi - lo) or 1
    lo -= span * .08
    hi += span * .14
    Y = lambda v: mt + (1 - (v - lo) / (hi - lo)) * (h - mt - mb)
    n = len(values)
    slot = (w - ml - mr) / n
    k = 2 if series2 else 1
    bw = slot * (.62 if k == 1 else .36)
    g = [f'<line class="axis" x1="{ml}" x2="{w - mr}" y1="{Y(0):.1f}" y2="{Y(0):.1f}"/>']
    for i, lab in enumerate(labels):
        x0 = ml + i * slot + (slot - bw * k - (2 if k == 2 else 0)) / 2
        for j, ser in enumerate([values] + ([series2] if series2 else [])):
            v = ser[i]
            x = x0 + j * (bw + 2)
            y0, y1 = sorted([Y(0), Y(v)])
            if j == 0:
                c = "var(--pos)" if v >= 0 else "var(--neg)"
            else:
                c = "var(--bench)"
            g.append(f'<rect x="{x:.1f}" y="{y0:.1f}" width="{bw:.1f}" height="{max(y1 - y0, 1):.1f}" rx="2" fill="{c}" opacity="{1 if j == 0 else .55}"><title>{esc(str(lab))}: {fmt(v)}</title></rect>')
            if k == 1:
                ty = Y(v) - 6 if v >= 0 else Y(v) + 15
                g.append(f'<text class="val" x="{x + bw / 2:.1f}" y="{ty:.1f}" text-anchor="middle">{fmt(v)}</text>')
        g.append(f'<text x="{ml + i * slot + slot / 2:.1f}" y="{h - 10}" text-anchor="middle">{esc(str(lab))}</text>')
    out = f'<svg viewBox="0 0 {w} {h}" role="img">{"".join(g)}</svg>'
    if series2 and names:
        out += (f'<div class="legend" style="margin-top:8px"><span><i style="background:var(--pos)"></i>{esc(names[0])}</span>'
                f'<span><i style="background:var(--bench)"></i>{esc(names[1])}</span></div>')
    return out


def svg_grouped(labels, series, names, fmt, w=640, label_w=210, bar_h=14, gap=16,
                colors=("var(--accent)", "var(--s2)", "var(--bench)")):
    maxv = max(v for s in series for v in s if v is not None) or 1
    k = len(series)
    grp = k * bar_h + (k - 1) * 3
    h = len(labels) * (grp + gap) + 4
    plot = w - label_w - 80
    g = []
    for i, lab in enumerate(labels):
        y = i * (grp + gap)
        g.append(f'<text class="lbl" x="{label_w - 12}" y="{y + grp / 2 + 4}" text-anchor="end">{esc(lab)}</text>')
        for j, s in enumerate(series):
            v = s[i]
            yy = y + j * (bar_h + 3)
            bw = max(2, v / maxv * plot)
            g.append(f'<rect x="{label_w}" y="{yy}" width="{bw:.1f}" height="{bar_h}" rx="2" fill="{colors[j]}"/>'
                     f'<text class="val" x="{label_w + bw + 6:.1f}" y="{yy + bar_h - 3}">{fmt(v)}</text>')
    legend = '<div class="legend" style="margin-top:8px">' + "".join(
        f'<span><i style="background:{colors[j]}"></i>{esc(n)}</span>' for j, n in enumerate(names)) + "</div>"
    return f'<svg viewBox="0 0 {w} {h}" role="img">{"".join(g)}</svg>' + legend


def svg_football(s, lang, labels, w=760):
    """labels: dict with keys range52, scen, cons, price, base."""
    rows = s["scenarios_out"]
    price, sym = s["price"], s["sym"]
    vb = {r["name"]: r["value"] for r in rows}
    ct = s["valuation"].get("consensus_target")
    vals = [r["value"] for r in rows] + [price, s["low52"], s["high52"]] + ([ct] if ct else [])
    span = max(vals) - min(vals)
    lo, hi = min(vals) - span * .24, max(vals) + span * .16
    label_w, mr = (250 if lang == 'fr' else 210), 30
    X = lambda v: label_w + (v - lo) / (hi - lo) * (w - label_w - mr)
    items = [(labels["range52"], s["low52"], s["high52"], "var(--bench)"), (labels["scen"], vb["Bear"], vb["Bull"], "var(--accent)")]
    if ct:
        items.append((labels["cons"], ct, ct, "var(--s2)"))
    bh, gap, top = 22, 18, 28
    h = top + len(items) * (bh + gap) + 30
    m = lambda v: money(sym, v, lang)
    g = []
    for i, (lab, a, b, c) in enumerate(items):
        y = top + i * (bh + gap)
        g.append(f'<text class="lbl" x="{label_w - 12}" y="{y + bh / 2 + 4}" text-anchor="end">{esc(lab)}</text>')
        if a == b:
            g.append(f'<rect x="{X(a) - 3:.1f}" y="{y}" width="6" height="{bh}" rx="2" fill="{c}"/><text class="val" x="{X(a) + 10:.1f}" y="{y + bh / 2 + 4}">{m(a)}</text>')
        else:
            g.append(f'<rect x="{X(a):.1f}" y="{y}" width="{X(b) - X(a):.1f}" height="{bh}" rx="3" fill="{c}" opacity=".85"/>'
                     f'<text class="val" x="{X(a) - 6:.1f}" y="{y + bh / 2 + 4}" text-anchor="end">{m(a)}</text>'
                     f'<text class="val" x="{X(b) + 6:.1f}" y="{y + bh / 2 + 4}">{m(b)}</text>')
            if i == 1:
                g.append(f'<rect x="{X(vb["Base"]) - 1.5:.1f}" y="{y - 4}" width="3" height="{bh + 8}" fill="var(--ink)"/>')
    g.append(f'<line x1="{X(price):.1f}" x2="{X(price):.1f}" y1="{top - 14}" y2="{h - 26}" stroke="var(--ink)" stroke-dasharray="4 3"/>'
             f'<text class="val" x="{X(price):.1f}" y="{top - 17}" text-anchor="middle">{labels["price"]} {m(price)}</text>'
             f'<text x="{X(vb["Base"]):.1f}" y="{h - 6}" text-anchor="middle">{labels["base"]} {m(vb["Base"])}</text>')
    return f'<svg viewBox="0 0 {w} {h}" role="img">{"".join(g)}</svg>'


def nav_chart(id_, title, sub, ranges, modes, series):
    rng = "".join(f'<button data-range="{r}" aria-pressed="{"true" if r == "all" else "false"}">{lab}</button>' for r, lab in ranges)
    md_ = "".join(f'<button data-mode="{m}" aria-pressed="{"true" if i == 0 else "false"}">{lab}</button>' for i, (m, lab) in enumerate(modes))
    chk = "".join(f'<label><input type="checkbox" data-s="{esc(k)}" checked>{esc(k)}</label>' for k in series)
    return (f'<figure class="ch chartbox" id="{id_}"><figcaption><span>{title} <small>· {sub}</small></span>'
            f'<span class="seg">{md_}</span><span class="seg">{rng}</span></figcaption>'
            f'<div class="toggles" style="margin-bottom:8px">{chk}</div><div class="plot"></div><div class="tip"></div></figure>')
