"""Monthly factsheet (English and French) for the Global Value Rotation, from site/data/etf_strategies.json.

    python3 tools/factsheet/build_value_factsheet.py

Writes site/static/factsheets/Thoth_GlobalValueRotation_Factsheet_<YYYY-MM>_{EN,FR}.pdf and updates index.json.
Aggregated results only: no raw Bloomberg data. Requires playwright (python) with Chromium.
"""
import json, math, base64, sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]
DATA = json.loads((ROOT / "site/data/etf_strategies.json").read_text())
OUT = ROOT / "site/static/factsheets"; OUT.mkdir(parents=True, exist_ok=True)
BRAND = ROOT / "site/static/brand"
FONTS = Path("/home/claude/work/fonts/node_modules/@fontsource")   # local copies of Cormorant Garamond / Source Sans 3 (falls back to Google Fonts)

V = DATA["value"]
dates, nav, bnav = V["dates"], V["nav"], V["bench"]
r = [nav[0] - 1] + [nav[i] / nav[i - 1] - 1 for i in range(1, len(nav))]
b = [bnav[0] - 1] + [bnav[i] / bnav[i - 1] - 1 for i in range(1, len(bnav))]
MONTH = dates[-1]
NAMES = {"C_US": ("United States", "États-Unis"), "C_JP": ("Japan", "Japon"), "C_GB": ("United Kingdom", "Royaume-Uni"), "C_FR": ("France", "France"),
         "C_DE": ("Germany", "Allemagne"), "C_CH": ("Switzerland", "Suisse"), "C_NL": ("Netherlands", "Pays-Bas"), "C_IT": ("Italy", "Italie"),
         "C_ES": ("Spain", "Espagne"), "C_SE": ("Sweden", "Suède"), "C_DK": ("Denmark", "Danemark"), "C_CA": ("Canada", "Canada"),
         "C_AU": ("Australia", "Australie"), "C_HK": ("Hong Kong", "Hong Kong"), "S_EN": ("Energy", "Énergie"), "S_MT": ("Materials", "Matériaux"),
         "S_IN": ("Industrials", "Industrie"), "S_CD": ("Consumer Discretionary", "Consommation discrétionnaire"), "S_CS": ("Consumer Staples", "Consommation de base"),
         "S_HC": ("Health Care", "Santé"), "S_FN": ("Financials", "Finance"), "S_IT": ("Information Technology", "Technologies de l'information"),
         "S_TC": ("Communication Services", "Services de communication"), "S_UT": ("Utilities", "Services aux collectivités"), "S_RE": ("Real Estate", "Immobilier")}
MONTHS = {"en": ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"],
          "fr": ["janvier", "février", "mars", "avril", "mai", "juin", "juillet", "août", "septembre", "octobre", "novembre", "décembre"]}


def prod(x):
    p = 1.0
    for v in x: p *= 1 + v
    return p - 1


def ann(x):
    n = len(x); return (1 + prod(x)) ** (12 / n) - 1 if n else float("nan")


def window(x, k, annualise):
    if len(x) < k: return None
    return ann(x[-k:]) if annualise else prod(x[-k:])


def ytd(x):
    y = MONTH[:4]; idx = [i for i, d in enumerate(dates) if d.startswith(y)]
    return prod([x[i] for i in idx])


def mdd(x):
    n, pk, dd = 1, 1, 0
    for v in x:
        n *= 1 + v; pk = max(pk, n); dd = min(dd, n / pk - 1)
    return dd


def pct(v, lang, d=1, sign=False):
    if v is None or (isinstance(v, float) and math.isnan(v)): return "–"
    s = f"{v * 100:+.{d}f}" if sign else f"{v * 100:.{d}f}"
    s = s.replace("-", "−")
    return (s.replace(".", ",") + " %") if lang == "fr" else s + "%"


def num(v, lang, d=2):
    s = f"{v:.{d}f}".replace("-", "−"); return s.replace(".", ",") if lang == "fr" else s


def month_label(m, lang):
    y, mm = m.split("-"); return f"{MONTHS[lang][int(mm) - 1]} {y}" if lang == "fr" else f"{MONTHS[lang][int(mm) - 1]} {y}"


T = {
 "en": dict(kicker="MONTHLY FACTSHEET", title="Global Value Rotation", sub="ETF core (70%) · developed-market equities · EUR", asof="Data as of end of",
   obj_h="Objective", obj="Earn the long-run premium of cheap equity markets with smaller losses in bear markets: hold the cheapest developed countries and sectors, and halve equity exposure when the market turns. This ETF core is 70% of the value strategy; a stock satellite (30%) is in construction.",
   app_h="Approach", app="Value decides what to hold; a risk rule decides how much. The value signal is slow and is given time to work through a holding buffer; the risk rule is checked every month and never goes below 50% equities.",
   facts_h="Key facts", facts=[("Strategy type", "Systematic, long only, country and sector rotation"), ("Benchmark", "{bench}"), ("Universe", "14 MSCI countries · 11 MSCI World sectors"),
     ("Holdings", "8 UCITS ETFs (4 countries, 4 sectors), 50-100% invested"), ("Rebalancing", "Monthly"), ("Value signal", "E/P, B/P, dividend yield vs own 10-year history"),
     ("Risk rule", "50% cash if 2 of 3 indicators red (trend, credit, breadth)"), ("Currency", "EUR, unhedged"), ("Costs in backtest", "0.10% per trade · 0.25%/yr ETF fees"), ("Track record", "Backtest since January 2006 · live from Nov 2026")],
   perf_h="Performance (%)", cols=["1M", "3M", "YTD", "1Y", "3Y*", "5Y*", "10Y*", "Since 2006*"], strat="Strategy", bench_l="Benchmark", diff="Difference", annl="* annualised",
   growth_h="Growth of 100 since December 2005", cal_h="Calendar-year returns (%)",
   risk_h="Risk statistics (since January 2006)", risk=["Volatility", "Sharpe ratio", "Maximum drawdown", "Beta vs benchmark", "Tracking error", "Average equity exposure"],
   port_h="Portfolio for", on="Risk rule: 100% invested", off="Risk rule: 50% invested", sleeve_c="Country", sleeve_s="Sector",
   com_h="Monthly comment",
   com="In {month}, the strategy returned {m1} against {b1} for the benchmark. Since January {y}, it is {ytd} against {bytd}. Since 2006, 100 has grown to {g} against {bg}, with a worst loss of {dd} against {bdd}. The risk rule is {state} for the coming month.",
   st_on="at 100%", st_off="at 50%",
   how_h="How the strategy works", steps=[("Measure", "At each month end, the earnings yield, book yield and dividend yield of 25 indices (14 countries, 11 sectors)."),
     ("Score", "Each ratio is compared with the line's own 10-year history (z-score) and the three are averaged: a market is cheap when it is cheap versus its own past."),
     ("Select and keep", "Buy the 4 cheapest countries and the 4 cheapest sectors; keep a line while it stays among the 6 cheapest, so a value bet is not sold too early."),
     ("Dose the risk", "If at least two of three indicators are red (MSCI World below its 10-month average, euro high yield lagging short government bonds, fewer than half of the 25 lines in an uptrend), half the portfolio moves to cash; it returns to 100% when fewer than two indicators are red.")],
   why_h="Why it should work", why="Cheap markets have tended to outperform over the following years (Asness, Moskowitz and Pedersen, 2013), but they can keep falling in a crash. Simple trend and credit signals have historically flagged long bear markets (Faber, 2007). Halving exposure on those signals keeps most of the value premium while limiting the losses that make value hard to hold.",
   risks_h="Main risks", risks=["Value can lag for years when expensive growth leads (2016-2026).", "The risk rule can cut just before a quick rebound: 28 switches in 20 years.", "Eight lines can overlap (a cheap sector and a cheap country can be the same bet)."],
   gl_h="Glossary", gl=[("Sharpe ratio", "Return above the euro money-market rate divided by volatility."), ("Maximum drawdown", "Largest fall from a previous peak."),
     ("Tracking error", "Volatility of the return difference with the benchmark."), ("z-score", "Distance from the average, in standard deviations.")],
   disc="Student research project by Noah Doose (MSc Financial Markets & Investments, SKEMA Business School). Thoth Ledger is not an investment firm and offers no product or service. All figures are hypothetical backtest results of a model portfolio, computed on monthly index total returns in EUR with ETFs as proxies, net of the costs stated, before taxes. The rules were chosen among several pre-registered candidates; the clean out-of-sample test is the live record from November 2026. Past performance does not guarantee future returns. This document is not investment advice.",
   src="Sources: Bloomberg (MSCI country and sector indices, valuation ratios, euro money-market rates); Thoth Ledger calculations.", page="Page"),
 "fr": dict(kicker="REPORTING MENSUEL", title="Rotation Value mondiale", sub="Cœur ETF (70 %) · actions des pays développés · EUR", asof="Données à fin",
   obj_h="Objectif", obj="Capter la prime de long terme des marchés actions bon marché avec des pertes réduites en marché baissier : détenir les pays et secteurs développés les moins chers, et diviser par deux l'exposition quand le marché se retourne. Ce cœur ETF représente 70 % de la stratégie value ; un satellite actions (30 %) est en construction.",
   app_h="Approche", app="Le value décide quoi détenir ; une règle de risque décide combien. Le signal value est lent et on lui laisse le temps d'agir grâce à un tampon de détention ; la règle de risque est vérifiée chaque mois et ne descend jamais sous 50 % d'actions.",
   facts_h="Caractéristiques", facts=[("Type de stratégie", "Systématique, long uniquement, rotation pays et secteurs"), ("Indice de référence", "{bench}"), ("Univers", "14 pays MSCI · 11 secteurs MSCI World"),
     ("Positions", "8 ETF UCITS (4 pays, 4 secteurs), investi de 50 à 100 %"), ("Rebalancement", "Mensuel"), ("Signal value", "E/P, B/P, rendement du dividende vs historique propre sur 10 ans"),
     ("Règle de risque", "50 % cash si 2 indicateurs sur 3 rouges (tendance, crédit, largeur)"), ("Devise", "EUR, non couvert"), ("Frais du backtest", "0,10 % par transaction · 0,25 %/an de frais d'ETF"), ("Historique", "Backtest depuis janvier 2006 · réel depuis nov. 2026")],
   perf_h="Performances (%)", cols=["1M", "3M", "YTD", "1A", "3A*", "5A*", "10A*", "Depuis 2006*"], strat="Stratégie", bench_l="Indice", diff="Écart", annl="* annualisé",
   growth_h="Croissance de 100 depuis décembre 2005", cal_h="Rendements par année civile (%)",
   risk_h="Statistiques de risque (depuis janvier 2006)", risk=["Volatilité", "Ratio de Sharpe", "Perte maximale", "Bêta vs indice", "Tracking error", "Exposition actions moyenne"],
   port_h="Portefeuille pour", on="Règle de risque : investi à 100 %", off="Règle de risque : investi à 50 %", sleeve_c="Pays", sleeve_s="Secteur",
   com_h="Commentaire du mois",
   com="En {month}, la stratégie a rapporté {m1} contre {b1} pour l'indice. Depuis janvier {y}, elle affiche {ytd} contre {bytd}. Depuis 2006, 100 sont devenus {g} contre {bg}, avec une perte maximale de {dd} contre {bdd}. La règle de risque est {state} pour le mois qui vient.",
   st_on="à 100 %", st_off="à 50 %",
   how_h="Fonctionnement", steps=[("Mesurer", "À chaque fin de mois, le rendement bénéficiaire, le rendement comptable et le rendement du dividende de 25 indices (14 pays, 11 secteurs)."),
     ("Noter", "Chaque ratio est comparé à l'historique propre de la ligne sur 10 ans (z-score) et les trois sont moyennés : un marché est bon marché quand il l'est par rapport à son propre passé."),
     ("Choisir et garder", "Acheter les 4 pays et les 4 secteurs les moins chers ; garder une ligne tant qu'elle reste parmi les 6 moins chères, pour ne pas vendre un pari value trop tôt."),
     ("Doser le risque", "Si au moins deux indicateurs sur trois sont rouges (MSCI World sous sa moyenne de 10 mois, high yield euro en retard sur les obligations d'État courtes, moins de la moitié des 25 lignes en tendance haussière), la moitié du portefeuille passe en cash ; retour à 100 % quand moins de deux indicateurs sont rouges.")],
   why_h="Pourquoi cela devrait fonctionner", why="Les marchés bon marché ont eu tendance à surperformer les années suivantes (Asness, Moskowitz et Pedersen, 2013), mais ils peuvent continuer à baisser dans un krach. Des signaux simples de tendance et de crédit ont historiquement signalé les longs marchés baissiers (Faber, 2007). Diviser l'exposition par deux sur ces signaux garde l'essentiel de la prime value tout en limitant les pertes qui rendent le value difficile à tenir.",
   risks_h="Principaux risques", risks=["Le value peut rester distancé des années quand la croissance chère mène (2016-2026).", "La règle de risque peut réduire juste avant un rebond rapide : 28 bascules en 20 ans.", "Huit lignes peuvent se recouper (un secteur et un pays bon marché peuvent être le même pari)."],
   gl_h="Glossaire", gl=[("Ratio de Sharpe", "Rendement au-dessus du taux monétaire euro divisé par la volatilité."), ("Perte maximale", "Plus forte baisse depuis un sommet précédent."),
     ("Tracking error", "Volatilité de l'écart de rendement avec l'indice."), ("z-score", "Écart à la moyenne, en nombre d'écarts-types.")],
   disc="Projet de recherche étudiant de Noah Doose (MSc Financial Markets & Investments, SKEMA Business School). Thoth Ledger n'est pas une société de gestion et ne propose aucun produit ni service. Tous les chiffres sont des résultats hypothétiques de backtest d'un portefeuille modèle, calculés sur les rendements totaux mensuels d'indices en EUR, les ETF servant de proxys, nets des frais indiqués, avant impôts. Les règles ont été choisies parmi plusieurs candidates pré-enregistrées ; le test hors échantillon propre est le suivi réel à partir de novembre 2026. Les performances passées ne préjugent pas des performances futures. Ce document n'est pas un conseil en investissement.",
   src="Sources : Bloomberg (indices MSCI pays et secteurs, ratios de valorisation, taux monétaires euro) ; calculs Thoth Ledger.", page="Page"),
}


def font_css():
    css = []
    for fam, d, specs in (("Cormorant Garamond", "cormorant-garamond", [(500, "normal"), (600, "normal"), (600, "italic")]),
                          ("Source Sans 3", "source-sans-3", [(400, "normal"), (600, "normal"), (700, "normal")])):
        for w, st in specs:
            f = FONTS / d / "files" / f"{d}-latin-{w}-{st}.woff2"
            if f.exists():
                css.append(f"@font-face{{font-family:'{fam}';font-weight:{w};font-style:{st};src:url(data:font/woff2;base64,{base64.b64encode(f.read_bytes()).decode()}) format('woff2')}}")
    return "\n".join(css) if css else "@import url('https://fonts.googleapis.com/css2?family=Cormorant+Garamond:ital,wght@0,500;0,600;1,600&family=Source+Sans+3:wght@400;600;700&display=swap');"


def growth_svg(lang):
    W, H, l, rr, t, bb = 700, 210, 46, 8, 8, 22
    s = [100.0]; q = [100.0]
    for x, y in zip(r, b): s.append(s[-1] * (1 + x)); q.append(q[-1] * (1 + y))
    lo, hi = min(min(s), min(q)) * 0.95, max(max(s), max(q)) * 1.03
    n = len(s)
    X = lambda i: l + (W - l - rr) * i / (n - 1); Y = lambda v: t + (H - t - bb) * (1 - (v - lo) / (hi - lo))
    g = ""
    for k in range(5):
        v = lo + (hi - lo) * k / 4
        g += f'<line x1="{l}" x2="{W - rr}" y1="{Y(v):.1f}" y2="{Y(v):.1f}" stroke="#E5DCCB" stroke-width=".7"/><text x="{l - 6}" y="{Y(v) + 3:.1f}" text-anchor="end">{v:.0f}</text>'
    for i, d in enumerate(["2005-12"] + dates):
        if d.endswith("-12") and int(d[:4]) % 4 == 1:
            g += f'<text x="{X(i):.1f}" y="{H - 6}" text-anchor="middle">{int(d[:4]) + 1}</text>'
    p = lambda a: "M" + " L".join(f"{X(i):.1f} {Y(v):.1f}" for i, v in enumerate(a))
    g += f'<path d="{p(q)}" fill="none" stroke="#9AA1AB" stroke-width="1.4"/><path d="{p(s)}" fill="none" stroke="#0A1A30" stroke-width="1.9"/>'
    return f'<svg viewBox="0 0 {W} {H}" class="ch">{g}</svg>', s[-1], q[-1]


def cal_svg(lang):
    years = sorted(V["calendar"], key=int)[-10:]
    vals = [(V["calendar"][y], V["bench_calendar"][y]) for y in years]
    W, H, l, t, bb = 700, 150, 30, 10, 20
    m = max(max(abs(a), abs(c)) for a, c in vals) * 1.1
    Y = lambda v: t + (H - t - bb) * (0.5 - v / (2 * m))
    bw = (W - l) / len(years)
    g = f'<line x1="{l}" x2="{W}" y1="{Y(0):.1f}" y2="{Y(0):.1f}" stroke="#D3C4A6"/>'
    for i, ((a, c), y) in enumerate(zip(vals, years)):
        x = l + i * bw + bw * 0.16
        for j, (v, col) in enumerate(((a, "#0A1A30"), (c, "#B9BEC6"))):
            xx = x + j * bw * 0.34; y0, y1 = sorted((Y(0), Y(v)))
            g += f'<rect x="{xx:.1f}" y="{y0:.1f}" width="{bw * 0.32:.1f}" height="{max(y1 - y0, .5):.1f}" fill="{col}"/>'
        g += f'<text x="{x + bw * 0.33:.1f}" y="{H - 5}" text-anchor="middle">{y}</text>'
        g += f'<text x="{x + bw * 0.16:.1f}" y="{(Y(a) - 3) if a >= 0 else (Y(a) + 9):.1f}" text-anchor="middle" class="v">{a * 100:.0f}</text>'
    return f'<svg viewBox="0 0 {W} {H}" class="ch">{g}</svg>'


def html(lang):
    L = T[lang]
    bench = V["bench_name"]
    st, bs = V["stats"], V["bench_stats"]
    ks = [(1, False), (3, False), ("ytd", False), (12, False), (36, True), (60, True), (120, True), ("all", True)]
    def row(x):
        out = []
        for k, a in ks:
            out.append(ytd(x) if k == "ytd" else ann(x) if k == "all" else window(x, k, a))
        return out
    pr, br = row(r), row(b)
    perf = "".join(f"<th>{c}</th>" for c in L["cols"])
    tr = lambda nm, v, cls="": f'<tr class="{cls}"><td>{nm}</td>' + "".join(f"<td>{pct(x, lang, 1, sign=False)}</td>" for x in v) + "</tr>"
    perf_rows = tr(L["strat"], pr, "main") + tr(L["bench_l"] + f" <small>({bench.replace(' Net EUR', '')})</small>", br) + \
        f'<tr class="diff"><td>{L["diff"]}</td>' + "".join(f"<td>{pct(None if a is None else a - c, lang, 1, sign=True)}</td>" for a, c in zip(pr, br)) + "</tr>"
    gsvg, g, bg = growth_svg(lang)
    h = V["holdings"]
    lines = "".join(f'<tr><td>{L["sleeve_c"] if k.startswith("C_") else L["sleeve_s"]}</td><td><b>{NAMES[k][0 if lang == "en" else 1]}</b></td><td>{pct(0.125 * h.get("exposure", 1.0), lang)}</td></tr>' for k in h["selection"])
    risk_vals = [pct(st["vol"], lang), num(st["sharpe"], lang), pct(st["mdd"], lang), num(st["beta"], lang), pct(st["te"], lang), pct(V["invested_avg"], lang, 0)]
    risk_b = [pct(bs["vol"], lang), num(bs["sharpe"], lang), pct(bs["mdd"], lang), "1" + (",00" if lang == "fr" else ".00"), "–", "100" + (" %" if lang == "fr" else "%")]
    risk = "".join(f"<tr><td>{n}</td><td>{a}</td><td>{c}</td></tr>" for n, a, c in zip(L["risk"], risk_vals, risk_b))
    facts = "".join(f"<tr><td>{a}</td><td>{c.format(bench=bench)}</td></tr>" for a, c in L["facts"])
    com = L["com"].format(month=month_label(MONTH, lang), m1=pct(r[-1], lang, 1, True), b1=pct(b[-1], lang, 1, True), y=MONTH[:4], ytd=pct(ytd(r), lang, 1, True),
                          bytd=pct(ytd(b), lang, 1, True), g=num(g, lang, 0), bg=num(bg, lang, 0), dd=pct(st["mdd"], lang, 0), bdd=pct(bs["mdd"], lang, 0),
                          state=L["st_on"] if h["risk_on"] else L["st_off"])
    nxt = ["2026-10"] if MONTH == "2026-09" else [MONTH]
    y, m = map(int, MONTH.split("-")); m += 1
    if m == 13: y, m = y + 1, 1
    port_month = month_label(f"{y}-{m:02d}", lang)
    logo = base64.b64encode((BRAND / "mark_256.png").read_bytes()).decode()
    steps = "".join(f'<div class="step"><span>{i + 1}</span><b>{a}</b><p>{c}</p></div>' for i, (a, c) in enumerate(L["steps"]))
    gl = "".join(f"<p><b>{a}.</b> {c}</p>" for a, c in L["gl"])
    risks = "".join(f"<li>{x}</li>" for x in L["risks"])
    return f"""<!doctype html><html lang="{lang}"><head><meta charset="utf-8"><style>
{font_css()}
@page{{size:A4;margin:0}}*{{box-sizing:border-box}}
body{{margin:0;font:400 8.6pt/1.42 'Source Sans 3',Arial,sans-serif;color:#2E3747;background:#fff}}
.pg{{width:210mm;height:297mm;padding:13mm 13mm 11mm;position:relative;page-break-after:always;background:#FCFBF8}}
.top{{display:flex;align-items:center;gap:10px;border-bottom:1.5px solid #B58F55;padding-bottom:8px}}
.top img{{width:40px;height:40px}}.brand{{font:600 15pt/1 'Cormorant Garamond',serif;letter-spacing:.16em;color:#0A1A30}}
.brand small{{display:block;font:700 6.5pt 'Source Sans 3';letter-spacing:.2em;color:#7B5A2A;margin-top:3px}}
.top .r{{margin-left:auto;text-align:right;font-size:7.5pt;color:#616A78}}.top .r b{{display:block;color:#7B5A2A;letter-spacing:.18em;font-size:7pt}}
h1{{font:600 25pt/1.05 'Cormorant Garamond',serif;color:#0A1A30;margin:10px 0 2px}}.sub{{color:#7B5A2A;font:700 7pt 'Source Sans 3';letter-spacing:.16em;text-transform:uppercase}}
h2{{font:600 12.5pt/1.1 'Cormorant Garamond',serif;color:#0A1A30;margin:10px 0 4px;border-bottom:.6px solid #E5DCCB;padding-bottom:2px}}
.g{{display:grid;grid-template-columns:62mm 1fr;gap:7mm}}p{{margin:0 0 5px}}
table{{width:100%;border-collapse:collapse;font-size:7.8pt}}td,th{{padding:2.6px 4px;border-bottom:.5px solid #E5DCCB;text-align:left}}
th{{font:700 6.6pt 'Source Sans 3';letter-spacing:.06em;color:#7B5A2A;text-transform:uppercase;background:#F6F2EA}}
.perf td:not(:first-child),.perf th:not(:first-child),.risk td:not(:first-child),.hold td:last-child{{text-align:right;font-variant-numeric:tabular-nums}}
.perf tr.main td{{font-weight:700;color:#0A1A30}}.perf tr.diff td{{color:#616A78;font-style:italic}}
.facts td:first-child{{color:#616A78;width:42%}}.facts td{{font-size:7.5pt}}
.ch{{width:100%;height:auto}}.ch text{{font:6.5pt 'Source Sans 3';fill:#616A78}}.ch text.v{{font-size:5.8pt;fill:#0A1A30}}
.leg{{font-size:7pt;color:#616A78}}.leg i{{display:inline-block;width:12px;height:2px;vertical-align:middle;margin:0 4px 0 8px}}
.state{{display:inline-block;padding:2px 7px;border:1px solid #B58F55;color:#7B5A2A;font:700 6.8pt 'Source Sans 3';letter-spacing:.08em;text-transform:uppercase;margin-bottom:4px}}
.com{{background:#F6F2EA;border-left:2px solid #B58F55;padding:6px 8px}}
.foot{{position:absolute;left:13mm;right:13mm;bottom:8mm;font-size:6.4pt;color:#616A78;border-top:.6px solid #E5DCCB;padding-top:4px;display:flex;justify-content:space-between}}
.step{{display:grid;grid-template-columns:20px 1fr;gap:2px 8px;margin-bottom:7px}}.step span{{grid-row:span 2;width:18px;height:18px;border:1px solid #B58F55;border-radius:50%;display:grid;place-items:center;font:600 9pt 'Cormorant Garamond';color:#7B5A2A}}
.step b{{color:#0A1A30}}.step p{{margin:0}}ul{{margin:0;padding-left:14px}}li{{margin-bottom:3px}}
.disc{{font-size:7pt;color:#616A78;border:.6px solid #E5DCCB;padding:7px 9px;background:#fff}}
</style></head><body>
<div class="pg">
 <div class="top"><img src="data:image/png;base64,{logo}"><div class="brand">THOTH LEDGER<small>NOAH DOOSE · {'SYSTEMATIC STRATEGIES' if lang == 'en' else 'STRATÉGIES SYSTÉMATIQUES'}</small></div>
  <div class="r"><b>{L['kicker']}</b>{L['asof']} {month_label(MONTH, lang)}</div></div>
 <h1>{L['title']}</h1><div class="sub">{L['sub']}</div>
 <div class="g" style="margin-top:6px">
  <div>
   <h2>{L['obj_h']}</h2><p>{L['obj']}</p>
   <h2>{L['app_h']}</h2><p>{L['app']}</p>
   <h2>{L['facts_h']}</h2><table class="facts">{facts}</table>
   <h2>{L['port_h']} {port_month}</h2><div class="state">{L['on'] if h['risk_on'] else L['off']}</div>
   <table class="hold">{lines}</table>
  </div>
  <div>
   <h2>{L['perf_h']}</h2><table class="perf"><tr><th></th>{perf}</tr>{perf_rows}</table><p class="leg" style="margin-top:2px">{L['annl']}</p>
   <h2>{L['growth_h']}</h2><div class="leg"><i style="background:#0A1A30"></i>{L['strat']} ({num(g, lang, 0)})<i style="background:#9AA1AB"></i>{bench} ({num(bg, lang, 0)})</div>{gsvg}
   <h2>{L['cal_h']}</h2><div class="leg"><i style="background:#0A1A30;height:6px"></i>{L['strat']}<i style="background:#B9BEC6;height:6px"></i>{L['bench_l']}</div>{cal_svg(lang)}
   <h2>{L['risk_h']}</h2><table class="risk"><tr><th></th><th>{L['strat']}</th><th>{L['bench_l']}</th></tr>{risk}</table>
   <h2>{L['com_h']}</h2><div class="com">{com}</div>
  </div>
 </div>
 <div class="foot"><span>{L['src']}</span><span>{L['page']} 1/2</span></div>
</div>
<div class="pg">
 <div class="top"><img src="data:image/png;base64,{logo}"><div class="brand">THOTH LEDGER<small>{L['title'].upper()}</small></div><div class="r"><b>{L['kicker']}</b>{month_label(MONTH, lang)}</div></div>
 <div class="g" style="grid-template-columns:1fr 1fr;margin-top:8px">
  <div><h2>{L['how_h']}</h2>{steps}<h2>{L['why_h']}</h2><p>{L['why']}</p></div>
  <div><h2>{L['risks_h']}</h2><ul>{risks}</ul><h2>{L['gl_h']}</h2>{gl}</div>
 </div>
 <h2>{'Important information' if lang == 'en' else 'Informations importantes'}</h2><div class="disc">{L['disc']}</div>
 <div class="foot"><span>thothledger · fayzzy11.github.io/Portfolio-Project</span><span>{L['page']} 2/2</span></div>
</div></body></html>"""


def main():
    from playwright.sync_api import sync_playwright
    files = {}
    with sync_playwright() as p:
        br = p.chromium.launch()
        for lang in ("en", "fr"):
            pg = br.new_page(); pg.set_content(html(lang), wait_until="networkidle")
            name = f"Thoth_GlobalValueRotation_Factsheet_{MONTH}_{lang.upper()}.pdf"
            pg.pdf(path=str(OUT / name), format="A4", print_background=True); files[lang] = name
        br.close()
    idx_p = OUT / "index.json"
    idx = json.loads(idx_p.read_text()) if idx_p.exists() else {}
    lst = [e for e in idx.get("value", []) if e["month"] != MONTH] + [dict(month=MONTH, **files)]
    idx["value"] = sorted(lst, key=lambda e: e["month"], reverse=True)
    idx_p.write_text(json.dumps(idx, indent=1))
    print("factsheets", files)


if __name__ == "__main__":
    main()
