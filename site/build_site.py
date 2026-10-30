"""Build the Research Ledger site into docs/ (GitHub Pages).

Usage (from the repository root):
    python site/build_site.py

Reads   site/data/*.json        aggregated results and pitch content (see export_from_pipeline.py)
        site/content/**/*.md    pages written by hand (about, journal, methodology, research notes, database)
        site/static/            site.css and site.js, copied to docs/assets/
Writes  docs/index.html, docs/strategies/, docs/pitches/, docs/research/, docs/database/, docs/journal/,
        docs/methodology/, docs/about/ and docs/assets/site.{css,js}.
Leaves  docs/trend-following/, docs/downloads/ and every file under docs/assets/ it does not generate untouched.
"""
import html
import json
import re
import shutil
import statistics
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
BUILT = date.today().strftime("%d %b %Y")

NAV = [("index", "Home", ""), ("strategies", "Strategies", "strategies/"), ("pitches", "Stock pitches", "pitches/"),
       ("research", "Research", "research/"), ("database", "Database", "database/"), ("journal", "Journal", "journal/"),
       ("about", "About", "about/")]

esc = html.escape


# ---------------------------------------------------------------- helpers
def pct(x, d=1, sign=False):
    if x is None:
        return "—"
    s = f"{x * 100:+.{d}f}%" if sign else f"{x * 100:.{d}f}%"
    return s.replace("-", "−")


def cls_sign(x):
    return "" if x is None else ("pos" if x > 0 else "neg" if x < 0 else "")


def fnum(x, d=1):
    return "—" if x is None else f"{x:,.{d}f}".replace("-", "−")


def money(sym, v):
    if v >= 1000:
        return f"{sym}{v:,.0f}"
    return f"{sym}{v:,.2f}"


def slugify(s):
    return re.sub(r"[^a-z0-9]+", "-", s.lower()).strip("-")


def md(text):
    out = markdown.markdown(text, extensions=["tables", "sane_lists", "attr_list"])
    out = out.replace("<table>", '<div class="tbl-wrap"><table class="t">').replace("</table>", "</table></div>")
    return out


def front(path):
    t = path.read_text(encoding="utf-8")
    meta = {}
    if t.startswith("---"):
        _, fm, t = t.split("---", 2)
        for line in fm.strip().splitlines():
            k, _, v = line.partition(":")
            meta[k.strip()] = v.strip()
    return meta, t.strip()


def strip_h1(t):
    return re.sub(r"^# .*\n+", "", t, count=1)


def tbl(head, rows, num_cols=(), cls="", sortable=False, row_cls=None):
    th = "".join(f'<th class="n">{esc(h)}</th>' if i in num_cols else f"<th>{esc(h)}</th>" for i, h in enumerate(head))
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


def section(id_, idx, title, inner, sub=""):
    p = f"<p>{sub}</p>" if sub else ""
    return f'<section class="sec" id="{id_}"><div class="shead"><span class="idx">{idx}</span><h2>{esc(title)}</h2>{p}</div>{inner}</section>'


def page(path, title, body, active, desc="", depth=0, scripts=""):
    r = "../" * depth
    nav = "".join(f'<a href="{r}{href}" class="{"on" if key == active else ""}">{lab}</a>' for key, lab, href in NAV)
    full_title = f"{title} · {SITE}" if title != SITE else f"{SITE} — {AUTHOR}"
    doc = f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{esc(full_title)}</title>
<meta name="description" content="{esc(desc)}">
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Archivo:wght@400;500;600;700;800&family=IBM+Plex+Mono:wght@400;500;600&family=Source+Serif+4:ital,opsz,wght@0,8..60,400;0,8..60,600;1,8..60,400&display=swap">
<link rel="stylesheet" href="{r}assets/site.css">
<link rel="icon" href="data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 32 32'%3E%3Crect x='1.5' y='1.5' width='29' height='29' fill='%23FAFBF9' stroke='%23141A17' stroke-width='3'/%3E%3Crect x='7' y='22' width='18' height='3' fill='%230E6B4F'/%3E%3C/svg%3E">
<script src="{r}assets/site.js"></script>
</head>
<body>
<a class="skip" href="#main">Skip to content</a>
<header class="top"><div class="wrap">
 <a class="brand" href="{r}"><span class="mark">ND</span><span><b>{SITE}</b><small>{AUTHOR} · equity research &amp; data</small></span></a>
 <nav class="nav" id="nav" aria-label="Main">{nav}</nav>
 <button class="tbtn menu" id="menu" aria-label="Menu" aria-expanded="false" aria-controls="nav"><svg viewBox="0 0 16 16" aria-hidden="true"><path d="M2 4h12M2 8h12M2 12h12" stroke="currentColor" stroke-width="1.6"/></svg></button>
 <button class="tbtn" id="theme" aria-label="Switch light or dark theme" title="Theme"><svg viewBox="0 0 16 16" aria-hidden="true"><circle cx="8" cy="8" r="6.5" fill="none" stroke="currentColor" stroke-width="1.5"/><path d="M8 1.5a6.5 6.5 0 0 1 0 13z" fill="currentColor"/></svg></button>
</div></header>
<main id="main">
{body}
</main>
<footer class="sitefoot"><div class="wrap">
 <div><b>{SITE}</b><p>Student research by {AUTHOR}, MSc Financial Markets &amp; Investments (SKEMA Business School, Paris), CFA Level II candidate.</p>
 <p>Educational and interview material. Nothing here is investment advice or an offer of any security. Licensed market data are not redistributed: pages show methodology and aggregated results only.</p></div>
 <div><b>Sections</b>{"".join(f'<a href="{r}{href}">{lab}</a>' for key, lab, href in NAV[1:])}<a href="{r}methodology/">Methodology</a></div>
 <div><b>Elsewhere</b><a href="{REPO}">Code on GitHub</a><a href="{r}trend-following/">Trend-following report</a><a href="{r}downloads/Portfolio_Tracker_Bloomberg.xlsx">Portfolio tracker (Excel)</a><p style="margin-top:12px">Built {BUILT}.</p></div>
</div></footer>
{scripts}
</body>
</html>
"""
    out = DOCS / path
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(doc, encoding="utf-8")
    return out


# ---------------------------------------------------------------- SVG charts
def svg_hbars(labels, values, fmt, w=640, bar_h=26, gap=12, label_w=210, color="var(--green)", colors=None, maxv=None):
    maxv = maxv or max(abs(v) for v in values) or 1
    h = len(values) * (bar_h + gap) + 4
    plot = w - label_w - 70
    g = []
    for i, (l, v) in enumerate(zip(labels, values)):
        y = i * (bar_h + gap)
        bw = max(2, abs(v) / maxv * plot)
        c = colors[i] if colors else color
        g.append(f'<text class="lbl" x="{label_w - 12}" y="{y + bar_h / 2 + 4}" text-anchor="end">{esc(l)}</text>'
                 f'<rect x="{label_w}" y="{y}" width="{bw:.1f}" height="{bar_h}" rx="2" fill="{c}"/>'
                 f'<text class="val" x="{label_w + bw + 8:.1f}" y="{y + bar_h / 2 + 4}">{fmt(v)}</text>')
    return f'<svg viewBox="0 0 {w} {h}" role="img">{"".join(g)}</svg>'


def svg_diverging(labels, values, fmt, w=640, bar_h=24, gap=10, label_w=200, lim=None):
    lim = lim or max(abs(v) for v in values) * 1.1 or 1
    h = len(values) * (bar_h + gap) + 22
    plot = w - label_w - 20
    zero = label_w + plot / 2
    g = [f'<line class="axis" x1="{zero}" x2="{zero}" y1="0" y2="{h - 18}"/>']
    for i, (l, v) in enumerate(zip(labels, values)):
        y = i * (bar_h + gap)
        bw = abs(v) / lim * plot / 2
        x = zero if v >= 0 else zero - bw
        c = "var(--green)" if v >= 0 else "var(--red)"
        tx, anchor = (zero + bw + 6, "start") if v >= 0 else (zero - bw - 6, "end")
        g.append(f'<text class="lbl" x="{label_w - 12}" y="{y + bar_h / 2 + 4}" text-anchor="end">{esc(l)}</text>'
                 f'<rect x="{x:.1f}" y="{y}" width="{max(bw, 1.5):.1f}" height="{bar_h}" rx="2" fill="{c}"/>'
                 f'<text class="val" x="{tx:.1f}" y="{y + bar_h / 2 + 4}" text-anchor="{anchor}">{fmt(v)}</text>')
    g.append(f'<text x="{zero}" y="{h - 4}" text-anchor="middle">0</text>')
    return f'<svg viewBox="0 0 {w} {h}" role="img">{"".join(g)}</svg>'


def svg_columns(labels, values, fmt, w=760, h=240, color_pos="var(--green)", color_neg="var(--red)", m=(36, 10, 16, 34)):
    ml, mr, mt, mb = m
    lo, hi = min(0, min(values)), max(0, max(values))
    span = (hi - lo) or 1
    lo -= span * .08; hi += span * .12
    Y = lambda v: mt + (1 - (v - lo) / (hi - lo)) * (h - mt - mb)
    n = len(values)
    slot = (w - ml - mr) / n
    bw = slot * .62
    g = [f'<line class="axis" x1="{ml}" x2="{w - mr}" y1="{Y(0):.1f}" y2="{Y(0):.1f}"/>']
    for i, (l, v) in enumerate(zip(labels, values)):
        x = ml + i * slot + (slot - bw) / 2
        y0, y1 = sorted([Y(0), Y(v)])
        c = color_pos if v >= 0 else color_neg
        ty = Y(v) - 6 if v >= 0 else Y(v) + 14
        g.append(f'<rect x="{x:.1f}" y="{y0:.1f}" width="{bw:.1f}" height="{max(y1 - y0, 1):.1f}" rx="2" fill="{c}"/>'
                 f'<text class="val" x="{x + bw / 2:.1f}" y="{ty:.1f}" text-anchor="middle">{fmt(v)}</text>'
                 f'<text x="{x + bw / 2:.1f}" y="{h - 10}" text-anchor="middle">{esc(l)}</text>')
    return f'<svg viewBox="0 0 {w} {h}" role="img">{"".join(g)}</svg>'


def svg_grouped(labels, series, names, fmt, w=640, label_w=210, bar_h=14, gap=16, colors=("var(--green)", "var(--amber)", "var(--chart-bench)")):
    maxv = max(v for s in series for v in s if v is not None) or 1
    k = len(series)
    grp = k * bar_h + (k - 1) * 3
    h = len(labels) * (grp + gap) + 4
    plot = w - label_w - 70
    g = []
    for i, l in enumerate(labels):
        y = i * (grp + gap)
        g.append(f'<text class="lbl" x="{label_w - 12}" y="{y + grp / 2 + 4}" text-anchor="end">{esc(l)}</text>')
        for j, s in enumerate(series):
            v = s[i]
            if v is None:
                continue
            yy = y + j * (bar_h + 3)
            bw = max(2, v / maxv * plot)
            g.append(f'<rect x="{label_w}" y="{yy}" width="{bw:.1f}" height="{bar_h}" rx="2" fill="{colors[j]}"/>'
                     f'<text class="val" x="{label_w + bw + 6:.1f}" y="{yy + bar_h - 3}">{fmt(v)}</text>')
    legend = '<div class="legend" style="margin-top:8px">' + "".join(
        f'<span><i style="background:{colors[j]}"></i>{esc(n)}</span>' for j, n in enumerate(names)) + "</div>"
    return f'<svg viewBox="0 0 {w} {h}" role="img">{"".join(g)}</svg>' + legend


def svg_football(s, w=760):
    rows = s["scenarios_out"]
    price, sym = s["price"], s["sym"]
    vals = [r["value"] for r in rows] + [price] + ([s["valuation"]["consensus_target"]] if s["valuation"].get("consensus_target") else [])
    vals += [s["low52"], s["high52"]]
    span = max(vals) - min(vals)
    lo, hi = min(vals) - span * .22, max(vals) + span * .14
    label_w, mr = 190, 30
    X = lambda v: label_w + (v - lo) / (hi - lo) * (w - label_w - mr)
    items = [("52-week range", s["low52"], s["high52"], "var(--chart-bench)")]
    vb = {r["name"]: r["value"] for r in rows}
    items.append(("Scenario range (bear → bull)", vb["Bear"], vb["Bull"], "var(--green)"))
    if s["valuation"].get("consensus_target"):
        ct = s["valuation"]["consensus_target"]
        items.append(("Consensus target", ct, ct, "var(--amber)"))
    bh, gap = 22, 18
    top = 26
    h = top + len(items) * (bh + gap) + 30
    g = []
    for i, (lab, a, b, c) in enumerate(items):
        y = top + i * (bh + gap)
        g.append(f'<text class="lbl" x="{label_w - 12}" y="{y + bh / 2 + 4}" text-anchor="end">{esc(lab)}</text>')
        if a == b:
            g.append(f'<rect x="{X(a) - 3:.1f}" y="{y}" width="6" height="{bh}" fill="{c}"/><text class="val" x="{X(a) + 10:.1f}" y="{y + bh / 2 + 4}">{money(sym, a)}</text>')
        else:
            g.append(f'<rect x="{X(a):.1f}" y="{y}" width="{X(b) - X(a):.1f}" height="{bh}" rx="2" fill="{c}" opacity=".85"/>'
                     f'<text class="val" x="{X(a) - 6:.1f}" y="{y + bh / 2 + 4}" text-anchor="end">{money(sym, a)}</text>'
                     f'<text class="val" x="{X(b) + 6:.1f}" y="{y + bh / 2 + 4}">{money(sym, b)}</text>')
            if lab.startswith("Scenario"):
                g.append(f'<rect x="{X(vb["Base"]) - 1.5:.1f}" y="{y - 4}" width="3" height="{bh + 8}" fill="var(--ink)"/>')
    py = h - 26
    g.append(f'<line x1="{X(price):.1f}" x2="{X(price):.1f}" y1="{top - 14}" y2="{py}" stroke="var(--ink)" stroke-dasharray="4 3"/>'
             f'<text class="val" x="{X(price):.1f}" y="{top - 16}" text-anchor="middle">Price {money(sym, price)}</text>'
             f'<text x="{X(vb["Base"]):.1f}" y="{h - 6}" text-anchor="middle">Base target {money(sym, vb["Base"])}</text>')
    return f'<svg viewBox="0 0 {w} {h}" role="img" aria-label="Valuation range">{"".join(g)}</svg>'


# ---------------------------------------------------------------- data
VALUE = json.loads((DATA / "value_developed.json").read_text())
PITCHES = json.loads((DATA / "pitches.json").read_text(encoding="utf-8"))
REGION = {"France": "Europe", "United States": "Americas", "Japan": "Asia", "Hong Kong": "Asia"}
RCLS = {"Overweight": "r-ow", "Neutral": "r-n", "Underweight": "r-uw"}
for s in PITCHES:
    s["slug"] = slugify(f"{s['ticker']}-{s['name']}")
    s["region"] = REGION.get(s["country"], "Other")
    stem = f"{s['code']}_{re.sub(r'[^A-Za-z0-9]+', '_', s['name']).strip('_')}"
    s["files"] = {k: f"assets/pitches/{stem}{suf}" for k, suf in
                  [("pptx", "_pitch.pptx"), ("pdf", "_pitch.pdf"), ("note", "_note.pdf")]}
    s["files"] = {k: v for k, v in s["files"].items() if (DOCS / v).exists() or k == "note"}


def rating(r):
    return f'<span class="rating {RCLS.get(r, "")}">{esc(r)}</span>'


H = VALUE["headline"]
IC = VALUE["ic"]
IC_MEAN = statistics.mean(x["ic"] for x in IC)
IC_T = IC_MEAN / (statistics.stdev(x["ic"] for x in IC) / len(IC) ** .5)
Q = VALUE["quintiles"]
QI = Q["columns"].index("Q5-Q1")
SPREAD_6M = statistics.mean(r[QI] for r in Q["values"])
SPREAD_ANN = (1 + SPREAD_6M) ** 2 - 1


# ---------------------------------------------------------------- pages
def build_home():
    ew = H["EW"]
    research = sorted(research_notes(), key=lambda n: n["slug"], reverse=True)[:3]
    pitch_rows = "".join(
        f'<div class="row"><span><a href="pitches/{s["slug"]}/">{esc(s["name"])}</a><small>{esc(s["industry"])} · {esc(s["country"])}</small></span>'
        f'<b>{rating(s["rating"])}</b></div>' for s in PITCHES)
    body = f"""
<div class="wrap">
<section class="hero">
 <div>
  <div class="eyebrow">Systematic value · Fundamental pitches · Open methodology</div>
  <h1>Rules written <em>before</em> results. Every number traceable.</h1>
  <p>This is the working ledger of my equity research: a systematic value strategy on developed markets, the stock pitches
  that test what the screen picked, research notes on what went wrong and right, and a catalogue of the data behind it.</p>
  <div class="btns"><a class="btn primary" href="strategies/value-developed/">Read the value strategy</a><a class="btn" href="pitches/">Browse the pitches</a></div>
 </div>
 <div class="ledger">
  <header><span>Ledger · Systematic value DM</span><span>Jul 2021 – Jun 2026</span></header>
  <div class="row"><span>Equal weight, net of costs, hedged<small>vs MSCI World Net EUR {pct(ew["bench_return"])}</small></span><b>{pct(ew["ann_return"])}<small>a year</small></b></div>
  <div class="row"><span>Signal rank IC, sector-neutral<small>mean of {len(IC)} semi-annual dates, t ≈ {IC_T:.1f}</small></span><b>{IC_MEAN:.3f}</b></div>
  <div class="row"><span>Cheapest vs dearest quintile<small>average 6-month spread {pct(SPREAD_6M)}</small></span><b>{pct(SPREAD_ANN, 1, True)}<small>a year</small></b></div>
  <div class="row"><span>Max drawdown, equal weight<small>benchmark {pct(VALUE["performance"]["values"][-1][7])}</small></span><b class="neg">{pct(ew["max_drawdown"])}</b></div>
  <div class="row"><span>Universe researched<small>Bloomberg World, developed markets, 10 dated compositions</small></span><b>1,990</b></div>
 </div>
</section>

<section class="sec">
 <div class="shead"><span class="idx">§ 01</span><h2>What is in the ledger</h2></div>
 <div class="tiles">
  <a class="tile" href="strategies/"><span class="n">01 · Strategies</span><h3>Two backtested strategies</h3><p>Systematic value on 1,990 developed-market stocks, and multi-asset trend following over 25 years.</p><div class="go">Open →</div></a>
  <a class="tile" href="pitches/"><span class="n">02 · Stock pitches</span><h3>Eight pitches, eight learning notes</h3><p>Holdings of the December 2025 portfolio: five conviction calls, one hold and two cautionary cases.</p><div class="go">Open →</div></a>
  <a class="tile" href="research/"><span class="n">03 · Research</span><h3>Notes from the work</h3><p>Short write-ups of findings: a 2%-a-year dividend bug, why the optimiser lost to 1/N.</p><div class="go">Open →</div></a>
  <a class="tile" href="database/"><span class="n">04 · Database</span><h3>Data catalogue</h3><p>Every dataset and Bloomberg field used, coverage by date, cleaning rules and the anti-bias checklist.</p><div class="go">Open →</div></a>
  <a class="tile" href="journal/"><span class="n">05 · Journal</span><h3>Decisions, dated</h3><p>What was decided, when and why, from the investment policy to the last robustness test.</p><div class="go">Open →</div></a>
  <a class="tile" href="methodology/"><span class="n">06 · Methodology</span><h3>How results are produced</h3><p>Sources, integrity rules and the tools used, in one page.</p><div class="go">Open →</div></a>
 </div>
</section>

<section class="sec">
 <div class="cols2" style="gap:40px;align-items:start">
  <div>
   <div class="shead"><span class="idx">§ 02</span><h2>Latest pitches</h2><p>Calls as of 29 October 2026, with price targets from scenario valuations.</p></div>
   <div class="ledger">{pitch_rows}<div class="row"><span><a href="pitches/">Open the pitch library →</a></span><b></b></div></div>
  </div>
  <div>
   <div class="shead"><span class="idx">§ 03</span><h2>Latest research</h2></div>
   <div class="notes">{"".join(f'<a class="noteitem" style="grid-template-columns:1fr" href="research/{n["slug"]}/"><div><div class="d">{esc(n["date"])}</div><h3>{esc(n["title"])}</h3><p>{esc(n["summary"])}</p></div></a>' for n in research)}</div>
  </div>
 </div>
</section>

<section class="sec">
 <div class="shead"><span class="idx">§ 04</span><h2>House rules</h2><p>The constraints every result on this site respects.</p></div>
 <div class="cols2">
  <div class="box accent"><h4>Parameters before results</h4><p>Universe, signal, constraints and costs are written down before any backtest runs. Every variant tested is shown, not only the best one.</p></div>
  <div class="box accent"><h4>No survivorship, no look-ahead</h4><p>Index membership is taken as it was at each date. Accounts are used six months after year-end and never before publication.</p></div>
  <div class="box accent"><h4>Too good means check first</h4><p>A result that beats the benchmark by a steady margin is treated as a data error until proven otherwise. One such check found a 2%-a-year bug.</p></div>
  <div class="box accent"><h4>Costs and taxes included</h4><p>15 bp per trade, dividend withholding tax as in the MSCI net convention, and the carry cost of currency hedges.</p></div>
 </div>
</section>
</div>"""
    page("index.html", SITE, body, "index", "Equity research ledger by Noah Doose: systematic value strategy, stock pitches, research notes and data catalogue.")


def research_notes():
    out = []
    for p in sorted((CONTENT / "research").glob("*.md")):
        meta, text = front(p)
        out.append(dict(slug=p.stem, title=meta.get("title", p.stem), date=meta.get("date", ""), summary=meta.get("summary", ""), text=text))
    return out


def build_research():
    notes = sorted(research_notes(), key=lambda n: n["slug"], reverse=True)
    items = "".join(f'<a class="noteitem" href="{n["slug"]}/"><span class="d">{esc(n["date"])}</span><div><h3>{esc(n["title"])}</h3><p>{esc(n["summary"])}</p></div><span class="go">Read →</span></a>' for n in notes)
    body = f"""<div class="wrap"><header class="phead"><div class="eyebrow">Research notes</div><h1>Findings, written up when they happen</h1>
<p class="lede">Short notes on what the work revealed: data errors caught, construction choices tested, lessons from the pitches. Each one states the evidence and what changed as a result.</p></header>
<section class="sec"><div class="notes">{items}</div></section></div>"""
    page("research/index.html", "Research", body, "research", "Research notes by Noah Doose.", 1)
    for i, n in enumerate(notes):
        body = f"""<div class="wrap"><header class="phead"><div class="crumbs"><a href="../">Research</a> / {esc(n["date"])}</div>
<h1>{esc(n["title"])}</h1><p class="lede">{esc(n["summary"])}</p></header>
<section class="sec"><article class="prose">{md(n["text"])}</article></section>
<section class="sec noprint"><div class="btns"><a class="btn" href="../">← All research notes</a><a class="btn" href="../../strategies/value-developed/">The value strategy</a></div></section></div>"""
        page(f"research/{n['slug']}/index.html", n["title"], body, "research", n["summary"], 2)


def simple_md_page(name, active, eyebrow, lede, depth=1):
    meta, text = front(CONTENT / f"{name}.md")
    m = re.match(r"^# (.*)$", text, re.M)
    title = m.group(1) if m else meta.get("title", name.title())
    body = f"""<div class="wrap"><header class="phead"><div class="eyebrow">{esc(eyebrow)}</div><h1>{esc(title)}</h1><p class="lede">{lede}</p></header>
<section class="sec"><article class="prose">{md(strip_h1(text))}</article></section></div>"""
    page(f"{name}/index.html", meta.get("title", title), body, active, lede, depth)


# ---------------------------------------------------------------- strategies
def build_strategies():
    ew = H["EW"]
    tf = json.loads((ROOT / "strategies/trend_following/results/results.json").read_text())
    ref = tf["meta"]["reference"]
    st = tf["stats"]["full"][ref]
    body = f"""<div class="wrap"><header class="phead"><div class="eyebrow">Strategies</div><h1>Two strategies, built the same way</h1>
<p class="lede">Each strategy starts from a written policy, fixes its parameters before the first backtest and reports every variant tested, net of costs.</p></header>
<section class="sec"><div class="grid">
 <article class="card"><div class="meta"><span>Equities · developed markets</span><span>Backtest complete · Oct 2026</span></div>
  <h3><a href="value-developed/">Systematic Value — Developed Markets</a></h3>
  <p>Intra-sector value composite on 1,990 developed large and mid caps, 50 names, three weighting schemes, semi-annual rebalancing, benchmarked on MSCI World Net EUR.</p>
  <div class="stats" style="margin-top:6px">
   <div class="stat"><div class="k">Return, EW</div><div class="v">{pct(ew["ann_return"])}</div><div class="s">vs {pct(ew["bench_return"])}</div></div>
   <div class="stat"><div class="k">Signal IC</div><div class="v">{IC_MEAN:.3f}</div><div class="s">t ≈ {IC_T:.1f}</div></div></div>
  <div class="foot"><span class="figs"><span>2021-2026 · weekly</span></span><a class="btn sm" href="value-developed/">Open report →</a></div></article>
 <article class="card"><div class="meta"><span>Multi-asset futures</span><span>Report · Oct 2026</span></div>
  <h3><a href="../trend-following/">Multi-Asset Trend Following</a></h3>
  <p>Time-series momentum on {tf["meta"]["n_markets"]} futures markets (equities, bonds, currencies, commodities), {int(tf["meta"]["vol_target"] * 100)}% volatility target, design and validation periods split at {tf["meta"]["split"][:4]}, compared with an MSCI World Value proxy.</p>
  <div class="stats" style="margin-top:6px">
   <div class="stat"><div class="k">Return, blend</div><div class="v">{pct(st["annual_return"])}</div><div class="s">{st["years"]:.0f} years</div></div>
   <div class="stat"><div class="k">Sharpe ratio</div><div class="v">{st["sharpe"]:.2f}</div><div class="s">max DD {pct(st["max_drawdown"], 0)}</div></div></div>
  <div class="foot"><span class="figs"><span>{tf["meta"]["start"][:4]}-{tf["meta"]["end"][:4]} · daily</span></span><a class="btn sm" href="../trend-following/">Open report →</a></div></article>
</div></section></div>"""
    page("strategies/index.html", "Strategies", body, "strategies", "Backtested strategies by Noah Doose.", 1)


def build_value():
    perf = VALUE["performance"]
    pc = perf["columns"]
    ci = {c: i for i, c in enumerate(pc)}
    ew = H["EW"]
    toc = [("summary", "Summary"), ("method", "Method"), ("performance", "Performance"), ("years", "Year by year"),
           ("signal", "The signal"), ("attribution", "Attribution"), ("factors", "Factor exposures"),
           ("robustness", "Robustness"), ("limits", "Limits"), ("documents", "Documents")]
    # performance table
    rows = []
    for name, v in zip(perf["index"], perf["values"]):
        m = re.match(r"^(.*?) \((.*)\)$", name)
        label = f'{esc(m.group(1))}<small style="display:block;color:var(--slate);font-weight:400">{esc(m.group(2))}</small>' if m else esc(name)
        rows.append([label, pct(v[ci["ann_return"]]), pct(v[ci["ann_vol"]]), fnum(v[ci["sharpe"]], 2),
                     f'<span class="{cls_sign(v[ci["active_return"]])}">{pct(v[ci["active_return"]], 1, True)}</span>' if "MSCI" not in name else "—",
                     pct(v[ci["tracking_error"]]) if "MSCI" not in name else "—",
                     fnum(v[ci["info_ratio"]], 2) if v[ci["info_ratio"]] is not None else "—",
                     pct(v[ci["max_drawdown"]]),
                     pct(v[ci["turnover_oneway_ann"]], 0) if v[ci["turnover_oneway_ann"]] is not None else "—"])
    perf_tbl = tbl(["Portfolio", "Return", "Vol.", "Sharpe", "Active", "TE", "IR", "Max DD", "Turnover"],
                   rows, num_cols=range(1, 9), cls="perf",
                   row_cls=lambda i, r: "hl" if r[0].startswith("Equal weight<") and ">hedged, net" in r[0] else ("bench" if "MSCI" in r[0] else ""))
    # calendar
    cal = VALUE["calendar"]
    def heat(v):
        a = min(abs(v) / .25, 1) * .55 + .08
        col = "14,107,79" if v >= 0 else "178,58,46"
        return f'<span style="display:block;margin:-10px -14px;padding:10px 14px;background:rgba({col},{a:.2f})">{pct(v, 1, True)}</span>'
    cal_rows = []
    for y, vals in zip(cal["index"], cal["values"]):
        lab = y + (" (H1)" if y == "2026" else " (from Jul)" if y == "2021" else "")
        cal_rows.append([lab] + [heat(v) for v in vals] + [f'<span class="{cls_sign(vals[0] - vals[3])}">{pct(vals[0] - vals[3], 1, True)}</span>'])
    cal_tbl = tbl(["Year"] + cal["columns"] + ["EW − benchmark"], cal_rows, num_cols=range(1, 6))
    # IC
    ic_svg = svg_columns([x["date"][2:7].replace("-", "/") for x in IC], [x["ic"] for x in IC], lambda v: f"{v:+.2f}".replace("-", "−"), w=520, h=250, m=(10, 10, 16, 30))
    qavg = [statistics.mean(r[i] for r in Q["values"]) for i in range(5)]
    q_svg = svg_columns(["Q1 dear", "Q2", "Q3", "Q4", "Q5 cheap"], qavg, lambda v: pct(v, 1), w=520, h=250,
                        color_pos="var(--green)")
    # attribution
    att = VALUE["attribution"]
    arows = [[esc(a["method"]), esc(a["dimension"].replace("fx_overlay", "FX hedge").title() if a["dimension"] != "fx_overlay" else "FX hedge"),
              f'<span class="{cls_sign(a["allocation"])}">{pct(a["allocation"], 2, True)}</span>',
              f'<span class="{cls_sign(a["selection"])}">{pct(a["selection"], 2, True)}</span>' if a["selection"] is not None else "—"] for a in att]
    att_tbl = tbl(["Weighting", "Dimension", "Allocation, a year", "Selection, a year"], arows, num_cols=(2, 3))
    ew_att = [a for a in att if a["method"] == "Equal weight"]
    sec = [a for a in ew_att if a["dimension"] == "sector"][0]
    fx = [a for a in ew_att if a["dimension"] == "fx_overlay"][0]
    att_svg = svg_diverging(["Selection within sectors", "Sector allocation", "Currency hedge"],
                            [sec["selection"], sec["allocation"], fx["allocation"]], lambda v: pct(v, 1, True), w=620, label_w=200)
    # factors
    F = VALUE["factors"]
    fcols = [c for c in F["columns"] if "excess" in c]
    fi = {k: i for i, k in enumerate(F["index"])}
    names = {"const": "Alpha, a year", "MKT (EUR)": "Market (EUR)", "SMB": "Size (SMB)", "HML": "Value (HML)",
             "RMW": "Profitability (RMW)", "CMA": "Investment (CMA)", "MOM": "Momentum (MOM)", "R2": "R²"}
    frows = []
    for k, lab in names.items():
        r = [lab]
        for c in fcols:
            v = F["values"][fi[k]][F["columns"].index(c)]
            r.append(pct(v, 1, True) if k == "const" else f"{v:.2f}".replace("-", "−"))
        frows.append(r)
    f_tbl = tbl(["Loading"] + [c.replace(" excess (unhedged)", "") for c in fcols], frows, num_cols=range(1, 4))
    # robustness
    rob = [r for r in VALUE["robustness"] if r["method"] in ("Equal weight", "Score-tilted")]
    rrows = [[esc(r["variant"]), pct(r["ann_return"]), f'<span class="{cls_sign(r["active_return"])}">{pct(r["active_return"], 1, True)}</span>',
              pct(r["tracking_error"]), pct(r["max_drawdown"]), pct(r["turnover_oneway_ann"], 0) if r["turnover_oneway_ann"] else "—"] for r in rob]
    r_tbl = tbl(["Variant (equal weight unless stated)", "Return", "Active", "Tracking error", "Max DD", "Turnover"], rrows, num_cols=range(1, 6),
                row_cls=lambda i, r: "hl" if r[0].startswith("Base") else "")
    nav_json = json.dumps(VALUE["nav"]).replace("</", "<\\/")
    chk = "".join(f'<label><input type="checkbox" data-s="{esc(k)}" checked>{esc(k)}</label>' for k in VALUE["nav"]["series"])
    method = tbl(["Step", "Rule"], [
        ["Universe", "Bloomberg World Large &amp; Mid Cap members in 24 developed countries, <b>composition dated at each rebalance</b>; free-float cap above €1bn, 3-month ADV above €5m; one line per issuer"],
        ["Signal", "EV/EBIT, P/B, FCF yield and EV/Sales expressed as yields (banks and insurers: P/B and P/E); winsorised at 1/99%; z-scored <b>within GICS sector</b>; equal-weight composite"],
        ["Accounting lag", "A fiscal year is used from year-end + 6 months and never before its announcement date"],
        ["Selection", "50 names maximising total score in the cheapest sector quintile, within ±10-point sector and country bands versus the benchmark (exact integer programme); a buffer keeps holdings still in the top two quintiles"],
        ["Weighting", "Equal weight · minimum variance (Ledoit-Wolf covariance, 250 weeks) · mean-variance; 0.5%-4% per name, long only"],
        ["Rebalancing", "Semi-annual, ten dates from June 2021 to December 2025; trades at the first Friday after the decision date; 15 bp per trade"],
        ["Currency", "EUR base; currencies carried by five or more names are hedged with forwards"],
        ["Benchmark", "MSCI World Net Total Return EUR (MSDEWIN)"]])
    secs = [
        section("summary", "01", "Summary", f"""
<div class="stats">
 <div class="stat"><div class="k">Return, equal weight</div><div class="v">{pct(ew["ann_return"])}</div><div class="s">benchmark {pct(ew["bench_return"])}</div></div>
 <div class="stat"><div class="k">Active return</div><div class="v {cls_sign(ew["active_return"])}">{pct(ew["active_return"], 1, True)}</div><div class="s">tracking error {pct(ew["tracking_error"])}</div></div>
 <div class="stat"><div class="k">Max drawdown</div><div class="v">{pct(ew["max_drawdown"])}</div><div class="s">beta {ew["beta"]:.2f}</div></div>
 <div class="stat"><div class="k">Signal IC</div><div class="v">{IC_MEAN:.3f}</div><div class="s">t ≈ {IC_T:.1f}, {len(IC)} dates</div></div>
 <div class="stat"><div class="k">Q5 − Q1 spread</div><div class="v">{pct(SPREAD_ANN, 1, True)}</div><div class="s">a year, compounded</div></div>
</div>
<div class="callout"><b>The signal worked; the portfolio broke even.</b> Cheap stocks beat expensive ones within their sector, and stock
selection added {pct(sec["selection"], 1, True)} a year. But the portfolio held no mega-cap growth in 2023-24, sector allocation cost
{pct(sec["allocation"], 1, True)} and the dollar hedge {pct(fx["allocation"], 1, True)}. Net of costs and withholding tax, equal weight matched
the benchmark; both optimisers lagged it by more than 2 points a year.</div>"""),
        section("method", "02", "Method", method, "Every rule below was fixed before the first backtest ran."),
        section("performance", "03", "Performance", f"""
<figure class="ch chartbox" id="navchart"><figcaption><span>Cumulative performance, net of costs, hedged <small>· rebased to 100 · weekly</small></span>
<span class="seg"><button data-mode="nav" aria-pressed="true">Growth</button><button data-mode="dd" aria-pressed="false">Drawdown</button></span>
<span class="seg"><button data-range="1" aria-pressed="false">1Y</button><button data-range="3" aria-pressed="false">3Y</button><button data-range="all" aria-pressed="true">All</button></span></figcaption>
<div class="toggles" style="margin-bottom:8px">{chk}</div><div class="plot"></div><div class="tip"></div></figure>
<h3>Statistics, 2 July 2021 – 26 June 2026</h3>{perf_tbl}
<p class="cap">Hedged = currencies held by five or more names hedged to EUR. Costs: 15 bp per trade. Withholding tax at MSCI-style statutory rates. TE = tracking error, IR = information ratio. Turnover one-way, annualised.</p>"""),
        section("years", "04", "Year by year", cal_tbl + '<p class="cap">2021 starts in July; 2026 covers the first half only.</p>',
                "Value paid in 2022 and 2025, and lagged badly in 2024, when the benchmark rose on mega-cap growth the strategy could not own."),
        section("signal", "05", "The signal", f"""<div class="cols2">
<figure class="ch"><figcaption><span>Rank IC at each rebalance <small>· sector-neutral, next 6 months</small></span></figcaption>{ic_svg}</figure>
<figure class="ch"><figcaption><span>Average 6-month return by quintile <small>· Q5 = cheapest</small></span></figcaption>{q_svg}</figure></div>
<p class="cap">The information coefficient is the rank correlation between the score at each date and the next six-month return, measured within sectors. Positive at {sum(1 for x in IC if x["ic"] > 0)} of {len(IC)} dates.</p>"""),
        section("attribution", "06", "Attribution", f"""<figure class="ch" style="margin-bottom:18px"><figcaption><span>Equal weight: where the active return came from <small>· a year</small></span></figcaption>{att_svg}</figure>{att_tbl}""",
                "Brinson attribution by sector and by country, plus the cost of the currency overlay."),
        section("factors", "07", "Factor exposures", f_tbl + '<p class="cap">Weekly regressions of unhedged excess returns on Fama-French developed five factors plus momentum (Kenneth French Data Library), 260 weeks. Alpha is the annualised intercept.</p>',
                "A clear value (HML) and small-cap tilt, and a negative momentum loading: buying what has fallen."),
        section("robustness", "08", "Robustness", r_tbl, "Each variant changes one rule and keeps the others. None was adopted after seeing its result."),
        section("limits", "09", "Limits", """<div class="prose"><ul>
<li><b>Five years, ten rebalances, one regime.</b> No claim of statistically significant alpha.</li>
<li>Bloomberg's World index stands in for MSCI's (MSCI constituents not licensed); a replica built from security returns tracks MSCI World Net with 0.996 correlation.</li>
<li>Current GICS sectors applied to history; no market impact in costs; idealised weekly hedge.</li>
<li>Negative momentum loading (−0.27): the natural next step is a value + momentum + quality composite.</li></ul></div>"""),
        section("documents", "10", "Documents", """<div class="links">
<a class="btn" href="../../assets/value-developed/Investment_Note_Systematic_Value.pdf">Investment note (PDF)</a>
<a class="btn" href="../../pitches/">Eight stock pitches</a><a class="btn" href="../../database/">Data catalogue</a>
<a class="btn" href="../../research/2026-10-30-optimiser-vs-equal-weight/">Why the optimiser lost</a></div>"""),
    ]
    tocs = "".join(f'<a href="#{i}">{t}</a>' for i, t in toc)
    body = f"""<div class="wrap"><header class="phead"><div class="crumbs"><a href="../">Strategies</a> / value-developed</div>
<h1>Systematic Value — Developed Markets</h1>
<p class="lede">Cheap stocks, measured on several fundamentals and compared only with their sector peers, should outperform over a full cycle.
This strategy harvests that premium with transparent rules, controls sector and country bets, and asks one construction question:
does an optimiser beat equal weighting on the same ideas?</p></header>
<div class="doc"><nav class="toc" aria-label="On this page"><b>On this page</b>{tocs}</nav><div>{"".join(secs)}</div></div></div>"""
    page("strategies/value-developed/index.html", "Systematic Value — Developed Markets", body, "strategies",
         "Five-year backtest of a sector-neutral value strategy on developed markets.", 2,
         scripts=f"<script>window.NAV={nav_json};</script>")


# ---------------------------------------------------------------- pitches
ZLAB = {"ebit_ev": "EBIT / EV", "b_p": "Book / price", "fcf_p": "FCF yield", "s_ev": "Sales / EV", "e_p": "Earnings / price"}


def build_pitch_index():
    sectors = sorted({s["sector"] for s in PITCHES})
    cards = []
    for s in PITCHES:
        f = s["files"]
        links = f'<a class="chip" href="{s["slug"]}/"><b>Read note</b></a>' + "".join(
            f'<a class="chip" href="../{f[k]}">{lab}</a>' for k, lab in [("pptx", "PPTX"), ("pdf", "Deck PDF"), ("note", "Note PDF")] if k in f)
        cards.append(f"""<article class="card" data-item data-rating="{s["rating"].lower()}" data-region="{s["region"].lower()}" data-sector="{slugify(s["sector"])}">
<div class="meta"><span>{esc(s["ticker"])} · {esc(s["exchange"])} · {esc(s["country"])}</span><span style="color:var(--green-ink)">{esc(s["sector"])}</span></div>
<h3><a href="{s["slug"]}/">{esc(s["name"])}</a></h3>
<div>{rating(s["rating"])} <span class="chip" style="height:24px">{esc(s["role"])}</span></div>
<p>{esc(s["headline"])}</p>
<div class="foot"><span class="figs"><span>Price <b>{money(s["sym"], s["price"])}</b></span><span>Target <b>{money(s["sym"], s["target"])}</b></span><b class="{cls_sign(s["upside"])}">{pct(s["upside"], 0, True)}</b></span></div>
<div class="links">{links}</div></article>""")
    def group(key, label, vals):
        return f'<div class="fgroup"><span>{label}</span><button class="fbtn" data-f="{key}" data-v="all" aria-pressed="true">All</button>' + "".join(
            f'<button class="fbtn" data-f="{key}" data-v="{v}" aria-pressed="false">{l}</button>' for v, l in vals) + "</div>"
    filt = (group("rating", "Call", [("overweight", "Overweight"), ("neutral", "Neutral"), ("underweight", "Underweight")]) +
            group("region", "Region", [("europe", "Europe"), ("americas", "Americas"), ("asia", "Asia")]) +
            group("sector", "Sector", [(slugify(x), x) for x in sectors]))
    rows = [[f'<a href="{s["slug"]}/">{esc(s["name"])}</a>', esc(s["sector"]), esc(s["country"]), rating(s["rating"]),
             money(s["sym"], s["price"]), money(s["sym"], s["target"]), (f'<span class="{cls_sign(s["upside"])}">{pct(s["upside"], 0, True)}</span>', s["upside"]),
             esc(s["valuation"]["method"])] for s in PITCHES]
    body = f"""<div class="wrap"><header class="phead"><div class="eyebrow">Stock pitches · October 2026</div><h1>What the screen bought, examined one by one</h1>
<p class="lede">Eight holdings of the December 2025 value portfolio, researched from company filings in October 2026. Each has a twelve-slide deck in a
buy-side format and a learning note that explains the business, the macro, the numbers and the valuation from first principles.</p></header>
<section class="sec" data-filter-scope>
<div class="filters">{filt}<input class="search" type="search" placeholder="Search company, sector, thesis…" data-search aria-label="Search pitches"><span class="count"></span></div>
<div class="grid">{"".join(cards)}</div><div class="empty">No pitch matches these filters.</div></section>
<section class="sec"><div class="shead"><span class="idx">Σ</span><h2>The book at a glance</h2><p>Click a column header to sort. Upside is to the base-case scenario value.</p></div>
{tbl(["Company", "Sector", "Country", "Call", "Price", "Target", "Upside", "Valuation method"], rows, num_cols=(4, 5, 6), sortable=True)}
<p class="cap">Prices as of 29 October 2026. Calls: Overweight above +15% upside, Neutral between −10% and +15%, Underweight below −10%. Student research, not investment advice.</p></section></div>"""
    page("pitches/index.html", "Stock pitches", body, "pitches", "Eight stock pitches with decks and learning notes.", 1)


def src_item(i, x):
    link = ""
    if x["url"]:
        host = re.sub(r"^https?://(www[.])?", "", x["url"]).split("/")[0]
        link = f' · <a href="{esc(x["url"])}">{esc(host)}</a>'
    return f'<li><span class="tag">{esc(x["tag"] or str(i + 1))}</span><span>{esc(x["label"])}{link}</span></li>'


def build_pitch(s):
    f = s["facts"]
    v = s["valuation"]
    n = s["note"]
    sym = s["sym"]
    toc = [("overview", "Overview"), ("business", "The business"), ("macro", "Industry & macro"), ("history", "What happened"),
           ("screen", "Why the screen picked it"), ("thesis", "Thesis"), ("variant", "Variant perception"), ("financials", "Financials"),
           ("valuation", "Valuation"), ("catalysts", "Catalysts"), ("risks", "Risks & sell rules"), ("interview", "Interview prep"),
           ("glossary", "Glossary"), ("sources", "Sources")]
    dl = "".join(f'<a class="btn sm" href="../../{s["files"][k]}">{lab}</a>' for k, lab in [("pptx", "Deck (.pptx)"), ("pdf", "Deck (PDF)"), ("note", "This note (PDF)")] if k in s["files"])
    up = s["upside"]
    head = f"""<header class="pitchhead"><div>
<div class="crumbs noprint"><a href="../">Stock pitches</a> / {esc(s["ticker"])}</div>
<div class="eyebrow" style="margin-top:12px">{esc(s["industry"])} · {esc(s["country"])} · {esc(s["exchange"])}: {esc(s["ticker"])}</div>
<h1>{esc(s["name"])}</h1><p class="headline">{esc(s["headline"])}</p>
<div class="tags">{rating(s["rating"])}<span class="chip">{esc(s["role"])}</span>{f'<span class="chip">Conviction: {esc(s["conviction"])}</span>' if s["conviction"] != "Case study" else ""}<span class="chip">{esc(s["horizon"])}</span></div>
<div class="dl">{dl}</div></div>
<div class="callbox"><div class="ledger"><header><span>The call</span><span>{esc(s["price_note"])}</span></header>
<div class="row"><span>Rating</span><b>{rating(s["rating"])}</b></div>
<div class="row"><span>Price</span><b class="big">{money(sym, s["price"])}</b></div>
<div class="row"><span>Base-case value<small>{esc(v["method"])}</small></span><b class="big">{money(sym, s["target"])}</b></div>
<div class="row"><span>Upside to base case</span><b class="big {cls_sign(up)}">{pct(up, 0, True)}</b></div>
<div class="row"><span>Market cap</span><b>{sym}{s["mcap_bn"]:,.1f}bn</b></div>
<div class="row"><span>52-week range</span><b>{money(sym, s["low52"])} – {money(sym, s["high52"])}</b></div></div></div></header>"""
    stats = '<div class="stats">' + "".join(f'<div class="stat"><div class="k">{esc(k)}</div><div class="v" style="font-size:22px">{esc(val)}</div></div>' for k, val in s["key_stats"]) + "</div>"
    # segments
    sg = s["segments"]
    unit = sg["unit"]
    fmt = (lambda x: f"{x:g}%") if unit == "%" else (lambda x: f"{x:,.1f}{unit}" if unit == "m" else f"{x:,.0f} {unit}")
    if sg.get("values2"):
        seg_svg = svg_grouped(sg["labels"], [sg["values"], sg["values2"]], sg["series"], lambda x: f"{x:,.0f}")
    else:
        seg_svg = svg_hbars(sg["labels"], sg["values"], fmt)
    biz_boxes = '<div class="cols2" style="margin-top:18px">' + "".join(f'<div class="box"><h4>{esc(a)}</h4><p>{esc(b)}</p></div>' for a, b in s["business"]) + "</div>"
    macro_cards = '<div class="cols2" style="margin-top:18px">' + "".join(
        f'<div class="box accent"><div class="k">{esc(a)}</div><div class="big">{esc(b)}</div><p>{esc(c)}</p></div>' for a, b, c in s["macro"]) + "</div>"
    hist = '<ul class="timeline">' + "".join(f'<li><div class="d">{esc(d)}</div><p>{esc(t)}</p></li>' for d, t in n["history"]) + "</ul>"
    # screen
    mult = f["multiples"]
    mrows = []
    for k in mult:
        a, b, c = mult.get(k), f["peer_median"].get(k), f["sector_median"].get(k)
        mrows.append([k, f"{a:.2f}x" if a is not None else "—", f"{b:.2f}x" if b is not None else "—", f"{c:.2f}x" if c is not None else "—"])
    m_tbl = tbl(["Multiple, Dec 2025", s["name"], "Peer median", "Sector median"], mrows, num_cols=(1, 2, 3))
    z = f["z"]
    zk = [k for k in ZLAB if z.get(k) is not None]
    z_svg = svg_diverging([ZLAB[k] for k in zk], [z[k] for k in zk], lambda x: f"{x:+.1f}".replace("-", "−"), w=820, label_w=170, bar_h=22,
                          lim=max(5.5, max(abs(z[k]) for k in zk) * 1.15))
    w = f.get("weights_last") or {}
    held = ", ".join(d[:7] for d in f.get("dates_held", []))
    h1 = f.get("h1_2026_return")
    screen = f"""<div class="prose"><p>{esc(n["model_long"])}</p></div>
<div class="stats" style="margin:18px 0">
 <div class="stat"><div class="k">Value score, Dec 2025</div><div class="v">{f["score"]:+.2f}</div><div class="s">rank {f["sector_rank"]} of {f["sector_n"]} in {esc(f["sector"])}</div></div>
 <div class="stat"><div class="k">Accounts used</div><div class="v" style="font-size:20px">FY to {esc(f["fy_used"][:7])}</div><div class="s">year-end + 6-month lag</div></div>
 <div class="stat"><div class="k">Weight, Dec 2025</div><div class="v" style="font-size:17px">{pct(w.get("EW"), 1)} / {pct(w.get("MV"), 1)} / {pct(w.get("MVO"), 1)}</div><div class="s">equal · min-var · mean-var</div></div>
 <div class="stat"><div class="k">H1 2026 return</div><div class="v {cls_sign(h1)}">{pct(h1, 1, True)}</div><div class="s">benchmark {pct(f.get("h1_2026_benchmark"), 1, True)}</div></div>
</div>
<figure class="ch" style="margin-bottom:18px"><figcaption><span>Z-scores within sector <small>· Dec 2025 rebalance · above 0 = cheaper than the sector average</small></span></figcaption>{z_svg}</figure>
<div>{m_tbl}<p class="cap">Multiples on the accounts the model could use at the time. Peer set: same GICS industry group in the developed universe. Held at: {esc(held)}.</p></div>"""
    thesis = '<div class="num-list">' + "".join(f'<div class="box"><h4>{esc(a)}</h4><p>{esc(b)}</p></div>' for a, b in s["thesis"]) + "</div>"
    variant = '<div class="vs"><div class="h">What the market says</div><div class="h">What the evidence says</div>' + "".join(
        f"<div>“{esc(a)}”</div><div>{esc(b)}</div>" for a, b in s["variant"]) + "</div>"
    fin = s["financials"]
    fin_tbl = tbl(fin["cols"] if fin["cols"][0] else ["Line"] + fin["cols"][1:], [[esc(c) for c in r] for r in fin["rows"]], num_cols=range(1, len(fin["cols"])))
    # valuation
    sc_rows = [[f'<b>{esc(r["name"])}</b>', esc(r["inputs"]), money(sym, r["value"]), f'<span class="{cls_sign(r["upside"])}">{pct(r["upside"], 0, True)}</span>', esc(r["story"])]
               for r in s["scenarios_out"]]
    sc_tbl = tbl(["Scenario", "Inputs", "Value / share", "vs price", "What has to happen"], sc_rows, num_cols=(2, 3),
                 row_cls=lambda i, r: "hl" if "Base" in r[0] else "")
    extra = ""
    if v.get("sotp"):
        tot = sum(x[1] for x in v["sotp"])
        extra = "<h3>Sum of the parts (cross-check)</h3>" + tbl(["Component", "Per share"], [[esc(a), money(sym, b)] for a, b in v["sotp"]] + [["<b>Total</b>", f"<b>{money(sym, tot)}</b>"]], num_cols=(1,)) + \
            f'<p class="cap">The listed parts add up to {money(sym, tot)} per share. At {money(sym, s["price"])}, the market implicitly values everything else at about {money(sym, s["price"] - tot)} per share.</p>'
    if v.get("profits"):
        yrs = sorted(v["profits"])
        extra = '<figure class="ch" style="margin-top:18px"><figcaption><span>Profit attributable through the cycle <small>· US$m</small></span></figcaption>' + svg_columns(yrs, [v["profits"][y] for y in yrs], lambda x: f"{x:,.0f}", w=760, h=230) + "</figure>" + \
            f'<p class="cap">Normalised profit excludes {", ".join(str(x) for x in v["exclude"])}: US${v["normal_profit_usd_m"]:,.0f}m, or US${v["normal_eps_usd"]:.2f} per share.</p>'
    ct = v.get("consensus_target")
    val = f"""<div class="prose"><p><b>Method: {esc(v["method"])}.</b> {esc(v["explain"])}</p></div>
{sc_tbl}<figure class="ch" style="margin-top:18px"><figcaption><span>Valuation range <small>· base case marked</small></span></figcaption>{svg_football(s)}</figure>
{f'<p class="cap">Consensus target: {money(sym, ct)} ({pct(ct / s["price"] - 1, 0, True)}). Rating thresholds: Overweight above +15%, Neutral −10% to +15%, Underweight below −10%.</p>' if ct else ''}{extra}"""
    cat = '<ul class="timeline">' + "".join(f'<li><div class="d">{esc(d)}</div><p>{esc(t)}</p></li>' for d, t in s["catalysts"]) + "</ul>"
    risks = tbl(["Risk", "Mitigant"], [[esc(a), esc(b)] for a, b in s["risks"]]) + \
        '<div class="sell" style="margin-top:18px"><b>We change the call if</b><ul>' + "".join(f"<li>{esc(t)}</li>" for t in s["triggers"]) + "</ul></div>" + \
        f'<h3>The {"bull" if s["rating"] == "Underweight" else "bear"} case, taken seriously</h3><div class="prose"><p>{esc(n["bear_long"])}</p></div>'
    qa = "".join(f'<details class="qa" open><summary>{esc(q)}</summary><div>{esc(a)}</div></details>' for q, a in n["interview"])
    gloss = '<dl class="gloss">' + "".join(f"<dt>{esc(a)}</dt><dd>{esc(b)}</dd>" for a, b in n["glossary"]) + "</dl>"
    src = '<ol class="src">' + "".join(src_item(i, x) for i, x in enumerate(s["sources"])) + "</ol>" + \
        f'<p class="cap">Company figures from filings and releases listed above. Screen data (multiples, z-scores, weights) from the Bloomberg extract of 26-29 October 2026, aggregated. Peers: {esc(s["peers_text"])}</p>'
    secs = [
        section("overview", "01", "Overview", f'<div class="prose"><p>{esc(n["intro"])}</p><blockquote>{esc(s["one_liner"])}</blockquote></div>{stats}'),
        section("business", "02", "The business", "<div class='prose'>" + "".join(f"<p>{esc(p)}</p>" for p in n["business_long"]) + "</div>"
                + f'<figure class="ch" style="margin-top:18px"><figcaption><span>{esc(sg["title"])}</span></figcaption>{seg_svg}</figure>{biz_boxes}'),
        section("macro", "03", "Industry & macro", "<div class='prose'>" + "".join(f"<p>{esc(p)}</p>" for p in n["macro_long"]) + "</div>" + macro_cards),
        section("history", "04", "What happened", hist, "The events that shaped the stock, in order."),
        section("screen", "05", "Why the screen picked it", screen),
        section("thesis", "06", "Investment thesis", thesis),
        section("variant", "07", "Variant perception", variant, "Where our reading differs from the obvious one."),
        section("financials", "08", "Financials", fin_tbl + f'<p class="cap">{esc(fin["note"])}</p>'),
        section("valuation", "09", "Valuation", val),
        section("catalysts", "10", "Catalysts", cat),
        section("risks", "11", "Risks & sell rules", risks),
        section("interview", "12", "Interview prep", qa, "Questions a portfolio manager is likely to ask, with short answers."),
        section("glossary", "13", "Glossary", gloss),
        section("sources", "14", "Sources", src),
    ]
    tocs = "".join(f'<a href="#{i}">{t}</a>' for i, t in toc)
    printhead = f'<div class="printonly cap" style="margin-bottom:8px">{SITE} · {AUTHOR} · Learning note · {esc(s["price_note"])} · Student research, not investment advice.</div>'
    body = f"""<div class="wrap">{printhead}{head}
<div class="doc"><nav class="toc" aria-label="On this page"><b>{esc(s["name"])}</b>{tocs}</nav><div>{"".join(secs)}
<p class="cap" style="margin-top:20px">Student research for educational and interview purposes. Not investment advice. Prices as of {esc(s["price_note"])}.</p></div></div></div>"""
    page(f"pitches/{s['slug']}/index.html", f"{s['name']} — learning note", body, "pitches", s["headline"], 2)


# ---------------------------------------------------------------- database
DATASETS = [
    ("Index compositions", "WORLD Index", "BDS · INDX_MWEIGHT_HIST with END_DATE_OVERRIDE", "10 dates, Jun 2021 – Dec 2025", "4,117 tickers (union), 2,248-3,335 per date", "Point-in-time universe"),
    ("Security reference", "each ticker", "BDP · NAME, CRNCY, GICS_SECTOR_NAME, GICS_INDUSTRY_GROUP_NAME, CNTRY_OF_RISK, CNTRY_OF_DOMICILE, ID_BB_GLOBAL, MARKET_STATUS", "static", "4,117 tickers", "Developed-market filter, sectors"),
    ("Weekly prices", "each DM ticker", "BDH · PX_LAST, weekly, Currency = EUR", "Jun 2016 – Jun 2026", "986,418 observations, 1,988 tickers", "Returns, covariance"),
    ("Dividends", "each DM ticker", "BDS · DVD_HIST_ALL with DVD_START_DT / DVD_END_DT", "2016 – 2026", "44,198 records, 1,631 tickers", "Withholding-tax haircut"),
    ("Annual fundamentals", "each DM ticker", "BDH · 8 fields, Per = Y, EQY_FUND_CRNCY = EUR, FILING_STATUS = OR", "fiscal years 2015 – 2025", "1,967 tickers", "Value signal"),
    ("Rebalance snapshots", "each DM ticker", "BDH · CUR_MKT_CAP, EQY_FREE_FLOAT_PCT, TURNOVER at each rebalance date", "10 dates", "1,989 tickers", "Liquidity filters, EV"),
    ("Market series", "13 FX pairs, indices, rates", "BDH · PX_LAST weekly: EURxxx Curncy, MSDEWIN, NDDUWI, WORLD Index, ESTRON, EONIA", "Jun 2016 – Jun 2026", "18 series", "FX conversion, hedging, benchmark"),
    ("Factor returns", "Kenneth French Data Library", "Developed 5 factors + momentum, daily, compounded weekly", "2016 – 2026", "6 factors", "Factor regressions"),
    ("Short rates", "OECD via FRED", "3-month interbank rate by currency, monthly", "2016 – 2026", "13 currencies", "Hedge carry"),
]
FIELDS = [
    ("INDX_MWEIGHT_HIST", "Index members and weights at a past date", "Compositions", "BDS", "Default is today's list: always pass END_DATE_OVERRIDE, or the backtest is survivorship-biased."),
    ("CNTRY_OF_RISK", "Country of economic risk", "Reference", "BDP", "Used for the developed-market filter and country bands; can differ from domicile (e.g. Irish-domiciled US groups)."),
    ("GICS_SECTOR_NAME", "GICS sector", "Reference", "BDP", "Current classification only: applied to the whole history (known limit)."),
    ("GICS_INDUSTRY_GROUP_NAME", "GICS industry group", "Reference", "BDP", "Defines peer sets in the pitches."),
    ("CRNCY", "Trading currency", "Reference", "BDP", "GBp and ILs are sub-units (pence, agorot)."),
    ("MARKET_STATUS", "Listing status (ACTV, DLST…)", "Reference", "BDP", "Delisted names stay in the dated compositions."),
    ("PX_LAST", "Last price", "Prices", "BDH", "Came back adjusted for cash dividends: it is already a total-return series. Adding dividends double-counts ~2% a year."),
    ("DVD_HIST_ALL", "Dividend history (dates, amount, type)", "Dividends", "BDS", "Amount in payment currency, which the extract does not store; split-adjusted basis."),
    ("SALES_REV_TURN", "Revenue", "Fundamentals", "BDH", "Negative values set to missing for EV/Sales."),
    ("EBIT", "Operating income", "Fundamentals", "BDH", "Not used for banks and insurers."),
    ("NET_INCOME", "Net income", "Fundamentals", "BDH", "Earnings yield for financials."),
    ("CF_FREE_CASH_FLOW", "Free cash flow", "Fundamentals", "BDH", "Standardised definition, comparable across countries."),
    ("TOT_COMMON_EQY", "Common equity (book value)", "Fundamentals", "BDH", "Negative book kept: ranks as expensive."),
    ("NET_DEBT", "Net debt", "Fundamentals", "BDH", "Enterprise value = market cap + net debt + minorities."),
    ("MINORITY_NONCONTROLLING_INTEREST", "Minority interests", "Fundamentals", "BDH", "Part of enterprise value."),
    ("BS_SH_OUT", "Shares outstanding", "Fundamentals", "BDH", "Smoke test only: ratios use company totals, never per-share data."),
    ("ANNOUNCEMENT_DT", "Results announcement date", "Fundamentals", "BDH", "A fiscal year is never used before this date (look-ahead guard)."),
    ("FILING_STATUS = OR", "Override: originally reported figures", "Fundamentals", "override", "Avoids restated numbers that were not known at the time."),
    ("EQY_FUND_CRNCY = EUR", "Override: fundamentals in EUR", "Fundamentals", "override", "Same currency as the market cap snapshot."),
    ("CUR_MKT_CAP", "Market capitalisation", "Snapshots", "BDH", "Company-level total, so share classes do not create false discounts."),
    ("EQY_FREE_FLOAT_PCT", "Free float, %", "Snapshots", "BDH", "Capped at 100% (21 aberrant readings)."),
    ("TURNOVER", "Value traded", "Snapshots", "BDH", "Quarterly sum divided by weekdays gives average daily value traded (ADV)."),
    ("MSDEWIN Index", "MSCI World Net Total Return, EUR", "Market", "BDH", "Benchmark. Net of withholding tax: compare with net, not gross, returns."),
    ("ESTRON Index", "€STR overnight rate", "Market", "BDH", "Risk-free rate; EONIA froze after January 2022."),
    ("EURxxx Curncy", "FX, units of currency per EUR", "Market", "BDH", "13 pairs, weekly."),
]


def build_database():
    cov = VALUE["coverage"]
    cov_rows = [[c[0], f'{int(c[1]):,}', f'{int(c[3]):,}', f"{float(c[4]):.1f}%", f'{int(c[5]):,}', f'{int(c[6]):,}'] for c in cov[1:]]
    cov_tbl = tbl(["Date", "WORLD members", "Developed", "DM weight", "Liquid", "Eligible"], cov_rows, num_cols=range(1, 6))
    rep = VALUE["replica"]
    rep_tbl = tbl(rep[0], [[esc(c) for c in r] for r in rep[1:]], num_cols=(1, 2))
    ds_tbl = tbl(["Dataset", "Source", "Retrieval", "Period", "Coverage", "Used for"],
                 [[f"<b>{esc(a)}</b>", esc(b), f'<span class="mono" style="font-size:13px">{esc(c)}</span>', esc(d), esc(e), esc(f)] for a, b, c, d, e, f in DATASETS])
    fld_rows = [[f'<span class="mono">{esc(a)}</span>', esc(b), esc(c), esc(d), esc(e)] for a, b, c, d, e in FIELDS]
    fld = f"""<div data-filter-scope><div class="filters"><input class="search" type="search" placeholder="Search a field, a dataset or a pitfall…" data-search aria-label="Search fields">
<div class="fgroup"><span>Dataset</span><button class="fbtn" data-f="ds" data-v="all" aria-pressed="true">All</button>{"".join(f'<button class="fbtn" data-f="ds" data-v="{slugify(x)}" aria-pressed="false">{x}</button>' for x in dict.fromkeys(f[2] for f in FIELDS))}</div><span class="count"></span></div>
<div class="tbl-wrap"><table class="t"><thead><tr><th>Field</th><th>Meaning</th><th>Dataset</th><th>Function</th><th>Pitfall / rule</th></tr></thead><tbody>
{"".join(f'<tr data-item data-ds="{slugify(f[2])}"><td>{r[0]}</td><td>{r[1]}</td><td>{r[2]}</td><td>{r[3]}</td><td>{r[4]}</td></tr>' for f, r in zip(FIELDS, fld_rows))}
</tbody></table></div><div class="empty">No field matches.</div></div>"""
    _, bias = front(CONTENT / "database/bias_checklist.md")
    brows = []
    for line in strip_h1(bias).splitlines():
        c = [x.strip() for x in line.strip().strip("|").split("|")]
        if not line.startswith("|") or len(c) < 5 or c[0] in ("#", "") or set(c[0]) <= set("-: "):
            continue
        inline = lambda t: markdown.markdown(t).replace("<p>", "").replace("</p>", "")
        st = c[4]
        tone = "r-ow" if st.startswith("OK") or "Fixed" in st else "r-n"
        brows.append([c[0], f"<b>{inline(c[1])}</b>",
                      f'{inline(c[2])}<small style="display:block;color:var(--slate);margin-top:4px;word-break:break-word">Evidence: {inline(c[3])}</small>',
                      f'<span class="rating {tone}" style="white-space:nowrap">{inline(st.split(" — ")[0].split(" (")[0].replace("**", ""))}</span>'
                      + (f'<small style="display:block;color:var(--slate);margin-top:4px">{inline(st.split(" — ", 1)[1])}</small>' if " — " in st else "")])
    bias_tbl = tbl(["#", "Risk", "Control and evidence", "Status"], brows, num_cols=(0,))
    rules = """<div class="cols2">
<div class="box"><h4>Prices</h4><p>Weekly Friday grid; Tel Aviv lines stamped on Sundays moved to the Friday before. Gaps up to eight weeks bridged; a held line that stops trading earns 0% after its last price.</p></div>
<div class="box"><h4>Dividends</h4><p>Event study on ~38,000 ex-dates: the price does not drop on ex-date, so PX_LAST already includes dividends. Dividend records only size the withholding-tax haircut.</p></div>
<div class="box"><h4>Fundamentals</h4><p>Year-end + 6 months and never before announcement (471 late filers blocked). Negative sales and EV ≤ 0 set to missing; negative book kept.</p></div>
<div class="box"><h4>Issuers and liquidity</h4><p>One line per issuer (share classes and dual listings merged on identical accounts, the most traded kept). Liquidity filters remove 466 of 14,369 member-dates, de-duplication 199 more.</p></div>
</div>"""
    toc = [("overview", "Overview"), ("catalogue", "Datasets"), ("fields", "Field dictionary"), ("coverage", "Coverage by date"),
           ("checks", "Consistency checks"), ("cleaning", "Cleaning rules"), ("bias", "Anti-bias checklist"), ("licence", "Licence")]
    secs = [
        section("overview", "01", "Overview", """<div class="stats">
<div class="stat"><div class="k">Securities</div><div class="v">4,117</div><div class="s">union of 10 compositions</div></div>
<div class="stat"><div class="k">Developed</div><div class="v">1,990</div><div class="s">24 countries</div></div>
<div class="stat"><div class="k">Weekly prices</div><div class="v">986k</div><div class="s">observations</div></div>
<div class="stat"><div class="k">Dividends</div><div class="v">44,198</div><div class="s">records</div></div>
<div class="stat"><div class="k">Fundamentals</div><div class="v">8</div><div class="s">fields, 11 fiscal years</div></div></div>
<div class="callout amber"><b>What this page is.</b> A catalogue of the data behind the value strategy: what was extracted, how, with which settings, how
complete it is and which rules cleaned it. The raw data stay offline: Bloomberg terms do not allow redistribution.</div>"""),
        section("catalogue", "02", "Datasets", ds_tbl + '<p class="cap">Extracted through the Bloomberg Excel add-in on 26-29 October 2026 and frozen as values in one workbook (WORLD_RAW_20261029.xlsx).</p>'),
        section("fields", "03", "Field dictionary", fld, "Every Bloomberg field and override used, with the trap each one hides."),
        section("coverage", "04", "Coverage by date", cov_tbl + '<p class="cap">Eligible = developed, free-float cap above €1bn, ADV above €5m, one line per issuer. The eligible set covers 97.7-98.5% of developed benchmark weight at each date.</p>',
                "Index membership shrinks over time (index methodology), so the eligible universe falls from about 1,640 to 1,100 names."),
        section("checks", "05", "Consistency checks", rep_tbl + '<p class="cap">Replica = developed members of WORLD, cap-weighted at each date, buy-and-hold, built from our own security returns. Weekly correlation with MSDEWIN 0.996, tracking error 1.2%, annual gap −0.3%.</p>',
                "Rebuilding the benchmark from security returns is the test that caught the dividend double count."),
        section("cleaning", "06", "Cleaning rules", rules),
        section("bias", "07", "Anti-bias checklist", bias_tbl, "Written before the backtest was interpreted. Rule one: if a result looks good, check survivorship, look-ahead and units before any other explanation."),
        section("licence", "08", "Licence", """<div class="prose"><p>Bloomberg and MSCI data are licensed to SKEMA Business School for teaching use. This site publishes methodology,
field definitions, coverage counts and aggregated portfolio results only. No security-level time series is redistributed. Factor data come from the
Kenneth French Data Library; short rates from the OECD via FRED.</p></div>"""),
    ]
    tocs = "".join(f'<a href="#{i}">{t}</a>' for i, t in toc)
    body = f"""<div class="wrap"><header class="phead"><div class="eyebrow">Database</div><h1>The data behind the work</h1>
<p class="lede">Every dataset, every Bloomberg field and override, the coverage at each date and the rules that cleaned it, so any number on this site can be traced back.</p></header>
<div class="doc"><nav class="toc" aria-label="On this page"><b>On this page</b>{tocs}</nav><div>{"".join(secs)}</div></div></div>"""
    page("database/index.html", "Database", body, "database", "Data catalogue: datasets, Bloomberg fields, coverage and cleaning rules.", 1)


# ---------------------------------------------------------------- main
def main():
    (DOCS / "assets").mkdir(parents=True, exist_ok=True)
    for f in ("site.css", "site.js"):
        shutil.copy(HERE / "static" / f, DOCS / "assets" / f)
    old = DOCS / "static"
    if old.exists():
        shutil.rmtree(old)
    for f in ("home_template.html",):
        if (DOCS / f).exists():
            (DOCS / f).unlink()
    (DOCS / ".nojekyll").touch()
    build_home()
    build_strategies()
    build_value()
    build_pitch_index()
    for s in PITCHES:
        build_pitch(s)
    build_research()
    build_database()
    simple_md_page("journal", "journal", "Journal", "Decisions and milestones, dated. The full decision log with rejected alternatives lives in the repository.")
    simple_md_page("methodology", "", "Methodology", "Where the data come from, the rules every result respects, and the tools used.")
    simple_md_page("about", "about", "About", "Who is behind this ledger and why it exists.")
    print("site built in", DOCS)


if __name__ == "__main__":
    main()
