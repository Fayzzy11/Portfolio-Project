"""Build the Research Ledger site (English at docs/, French at docs/fr/) for GitHub Pages.

Usage (from the repository root):
    python site/build_site.py

Reads   site/data/*.json         results and pitch content (English) + pitches_fr.json (French fields)
        site/content/{en,fr}/    hand-written pages in Markdown (about, journal, methodology, research notes, checklist)
        site/static/             site.css and site.js, copied to docs/assets/
Writes  every page in both languages. Leaves docs/trend-following/ (archived futures study) and docs/downloads/ untouched.
"""
import json
import re
import shutil
import statistics

from lib import (AUTHOR, CONTENT, DATA, DOCS, HERE, HORUS_URL, ICON_DL, ICON_EXT, SITE, cls_sign, doc_layout, esc, front,
                 md, md_inline, money, nav_chart, num, page, pct, phead, section, slugify, stat, strip_h1, svg_columns,
                 svg_diverging, svg_football, svg_grouped, svg_hbars, t, tbl, tr)

LANGS = ("en", "fr")
L = lambda lang, en, fr: fr if lang == "fr" else en  # inline bilingual text

# ---------------------------------------------------------------- data
VALUE = json.loads((DATA / "value_developed.json").read_text())
PITCHES = json.loads((DATA / "pitches.json").read_text(encoding="utf-8"))
PITCH_FR = json.loads((DATA / "pitches_fr.json").read_text(encoding="utf-8"))
HORUS = json.loads((DATA / "horus_smart_beta.json").read_text())
RCLS = {"Overweight": "r-ow", "Neutral": "r-n", "Underweight": "r-uw", "Sell": "r-uw", "Buy": "r-ow"}
REGION = {"France": "europe", "United States": "americas", "Japan": "asia", "Hong Kong": "asia"}
for s in PITCHES:
    s["slug"] = slugify(f"{s['ticker']}-{s['name']}")
    stem = f"{s['code']}_{re.sub(r'[^A-Za-z0-9]+', '_', s['name']).strip('_')}"
    s["files"] = {k: f"assets/pitches/{stem}{suf}" for k, suf in [("pptx", "_pitch.pptx"), ("pdf", "_pitch.pdf")]
                  if (DOCS / f"assets/pitches/{stem}{suf}").exists()}

H = VALUE["headline"]
IC = VALUE["ic"]
IC_MEAN = statistics.mean(x["ic"] for x in IC)
IC_T = IC_MEAN / (statistics.stdev(x["ic"] for x in IC) / len(IC) ** .5)
Q = VALUE["quintiles"]
QI = Q["columns"].index("Q5-Q1")
SPREAD_6M = statistics.mean(r[QI] for r in Q["values"])
SPREAD_ANN = (1 + SPREAD_6M) ** 2 - 1

# ---------------------------------------------------------------- strategy universes (rules fixed 30 Oct 2026)
COUNTRIES = [("US", "United States", "MXUS", "SPX"), ("JP", "Japan", "MXJP", "TPX"), ("GB", "United Kingdom", "MXGB", "UKX"),
             ("FR", "France", "MXFR", "SBF120"), ("DE", "Germany", "MXDE", "CDAX"), ("CH", "Switzerland", "MXCH", "SPI"),
             ("NL", "Netherlands", "MXNL", "AEX"), ("IT", "Italy", "MXIT", "FTSEMIB"), ("ES", "Spain", "MXES", "IBEX"),
             ("SE", "Sweden", "MXSE", "OMX"), ("DK", "Denmark", "MXDK", "KAX"), ("CA", "Canada", "MXCA", "SPTSX"),
             ("AU", "Australia", "MXAU", "AS51"), ("HK", "Hong Kong", "MXHK", "HSI")]
SECTORS = [("EN", "Energy", "MXWO0EN"), ("MT", "Materials", "MXWO0MT"), ("IN", "Industrials", "MXWO0IN"),
           ("CD", "Consumer Discretionary", "MXWO0CD"), ("CS", "Consumer Staples", "MXWO0CS"), ("HC", "Health Care", "MXWO0HC"),
           ("FN", "Financials", "MXWO0FN"), ("IT", "Information Technology", "MXWO0IT"), ("TC", "Communication Services", "MXWO0TC"),
           ("UT", "Utilities", "MXWO0UT"), ("RE", "Real Estate", "MXWO0RE")]
TREND = [("Equities", "US equities", "Actions américaines", "MSCI USA net", "iShares Core S&P 500"),
         ("Equities", "Euro area equities", "Actions zone euro", "MSCI EMU net", "iShares Core MSCI EMU"),
         ("Equities", "Japanese equities", "Actions japonaises", "MSCI Japan net", "iShares Core MSCI Japan IMI"),
         ("Equities", "Emerging equities", "Actions émergentes", "MSCI EM net", "iShares Core MSCI EM IMI"),
         ("Bonds", "US Treasuries", "Bons du Trésor américain", "Bloomberg US Treasury", "iShares $ Treasury 7-10yr"),
         ("Bonds", "Euro government bonds", "Obligations d'État zone euro", "Bloomberg Euro Treasury", "iShares Core Euro Govt Bond"),
         ("Bonds", "Global aggregate bonds", "Obligations mondiales", "Bloomberg Global Aggregate", "to select"),
         ("Bonds", "US investment-grade credit", "Crédit IG américain", "Bloomberg US Corporate", "to select"),
         ("Commodities", "Gold", "Or", "Gold spot", "Xetra-Gold"),
         ("Commodities", "Silver", "Argent", "Silver spot", "iShares Physical Silver"),
         ("Commodities", "Broad commodities", "Matières premières diversifiées", "Bloomberg Commodity TR", "iShares Diversified Commodity Swap"),
         ("Commodities", "Crude oil", "Pétrole brut", "BCOM WTI TR", "WisdomTree WTI Crude Oil"),
         ("Commodities", "Copper", "Cuivre", "BCOM Copper TR", "WisdomTree Copper"),
         ("Commodities", "Agriculture", "Agriculture", "BCOM Agriculture TR", "to select")]
SECTOR_CODE = {nm: code for code, nm, _ in SECTORS}
COUNTRY_CODE = {nm: code for code, nm, *_ in COUNTRIES}


def month_name(ym, lang):
    y, m = map(int, ym.split("-"))
    en = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"]
    fr = ["janvier", "février", "mars", "avril", "mai", "juin", "juillet", "août", "septembre", "octobre", "novembre", "décembre"]
    return f"{(fr if lang == 'fr' else en)[m - 1]} {y}"


def price_note(s, lang):
    if lang != "fr":
        return s["price_note"]
    x = s["price_note"].replace("intraday", "en séance").replace("close", "clôture").replace("Oct", "oct.").replace("before H1 results", "avant les résultats S1")
    return x


def rating(r, lang):
    return f'<span class="rating {RCLS.get(r, "")}">{esc(t(lang, r))}</span>'


def pf(s, lang, key):
    """Pitch field in the requested language (French overrides when available)."""
    if lang == "fr" and key in PITCH_FR.get(s["code"], {}):
        return PITCH_FR[s["code"]][key]
    if key == "stories":
        return [x[3] for x in s["valuation"]["scenarios"]]
    if key in ("method", "explain"):
        return s["valuation"][key]
    return s[key]


def fr_inputs(x):
    for a, b in [("EPS ", "BPA "), ("x TBV", "x l'ANCT"), (" at ", " à "), (" yield", " de rendement"), ("x book", "x les fonds propres"),
                 ("BVPS", "par action"), ("FCF ", "FCF "), ("RoTE ", "RoTE "), ("CoE", "CoE"), ("US$", "US$")]:
        x = x.replace(a, b)
    return re.sub(r"(\d)\.(\d)", r"\1,\2", x)


def pitch_links(pitches, lang, lr):
    return ", ".join(f'<a href="{lr}pitches/{s["slug"]}/">{esc(s["name"])}</a>' for s in pitches) or "—"


# ---------------------------------------------------------------- horus statistics
def horus_stats():
    r, b, rf = HORUS["r_p3"], HORUS["r_bench"], HORUS["rf"]
    n = len(r)

    def one(x):
        g = pk = 1.0
        mdd = 0
        nav = []
        for v in x:
            g *= 1 + v
            pk = max(pk, g)
            mdd = min(mdd, g / pk - 1)
            nav.append(g)
        m = sum(x) / n
        sd = (sum((v - m) ** 2 for v in x) / (n - 1)) ** .5
        ex = [a - c for a, c in zip(x, rf)]
        me = sum(ex) / n
        se = (sum((v - me) ** 2 for v in ex) / (n - 1)) ** .5
        cagr = nav[-1] ** (12 / n) - 1
        rf_ann = (1 + sum(rf) / n) ** 12 - 1
        # same convention as the Horus AM website: (CAGR - average risk-free rate) / volatility
        return dict(cagr=cagr, vol=sd * 12 ** .5, sharpe=(cagr - rf_ann) / (sd * 12 ** .5), mdd=mdd, nav=nav)

    p, q = one(r), one(b)
    act = [a - c for a, c in zip(r, b)]
    te = statistics.stdev(act) * 12 ** .5
    cov = sum((a - sum(r) / n) * (c - sum(b) / n) for a, c in zip(r, b)) / (n - 1)
    beta = cov / statistics.variance(b)
    y0 = int(HORUS["start"][:4])
    years, ann_p, ann_b = [], [], []
    for i in range(0, n, 12):
        gp = gb = 1.0
        for v in r[i:i + 12]:
            gp *= 1 + v
        for v in b[i:i + 12]:
            gb *= 1 + v
        years.append(y0 + i // 12)
        ann_p.append(gp - 1)
        ann_b.append(gb - 1)
    ahead = sum(1 for a, c in zip(ann_p, ann_b) if a > c)
    dates = []
    y, m = map(int, HORUS["start"].split("-"))
    for _ in range(n):
        dates.append(f"{y}-{m:02d}")
        m += 1
        if m > 12:
            y, m = y + 1, 1
    return dict(p=p, b=q, te=te, ir=(p["cagr"] - q["cagr"]) / te, beta=beta, years=years, ann_p=ann_p, ann_b=ann_b,
                ahead=ahead, dates=dates)


HS = horus_stats()
HORUS_ETF = {"IWM": ("US small caps", "Petites cap. US"), "IJH": ("US mid caps", "Moyennes cap. US"),
             "XLK": ("US technology", "Technologie US"), "XLE": ("US energy", "Énergie US"), "XLV": ("US health care", "Santé US"),
             "XLB": ("US materials", "Matériaux US"), "TLT": ("US Treasuries 20y+", "Trésor US 20 ans+"),
             "IEF": ("US Treasuries 7-10y", "Trésor US 7-10 ans"), "SHY": ("US Treasuries 1-3y", "Trésor US 1-3 ans"),
             "AGG": ("US aggregate bonds", "Obligations US agrégées"), "TIP": ("US inflation-linked", "Indexées inflation US"),
             "LQD": ("US investment-grade corporates", "Crédit IG US"), "RXRGEX": ("German government bonds", "État allemand")}


# ---------------------------------------------------------------- HOME
def build_home(lang):
    lr = "" if lang == "en" else ""
    ew = H["EW"]
    hp = HS["p"]
    ow = sum(1 for s in PITCHES if s["rating"] == "Overweight")
    cards = strategy_cards(lang, "")
    pitch_rows = "".join(
        f'<a class="noteitem" style="grid-template-columns:1fr auto" href="pitches/{s["slug"]}/"><div><h3>{esc(s["name"])}</h3>'
        f'<p>{esc(pf(s, lang, "headline"))}</p></div><span>{rating(s["rating"], lang)}</span></a>' for s in PITCHES[:4])
    notes = research_notes(lang)[:2]
    body = f"""
<section class="hero"><div class="wrap">
 <div>
  <div class="eyebrow">{L(lang, "Equity research · Systematic strategies · Open data", "Recherche actions · Stratégies systématiques · Données ouvertes")}</div>
  <h1>{L(lang, "Rules written before results. Every number traceable.", "Des règles écrites avant les résultats. Chaque chiffre traçable.")}</h1>
  <p class="lede">{L(lang, "I am Noah Doose, an MSc Financial Markets & Investments student at SKEMA and a CFA Level II candidate. This site is my research ledger: strategies anyone can replicate with ETFs, stock pitches that test them name by name, and the data behind every result.",
                     "Je suis Noah Doose, étudiant en MSc Financial Markets & Investments à SKEMA et candidat au CFA niveau II. Ce site est mon carnet de recherche : des stratégies réplicables par tous avec des ETF, des stock pitches qui les testent titre par titre, et les données derrière chaque résultat.")}</p>
  <div class="btns"><a class="btn primary" href="strategies/">{L(lang, "Explore the strategies", "Découvrir les stratégies")}</a><a class="btn" href="pitches/">{L(lang, "Read the stock pitches", "Lire les stock pitches")}</a></div>
 </div>
 <div class="panel"><header><span>{L(lang, "Key figures", "Chiffres clés")}</span><span>{L(lang, "backtests, net of costs", "backtests, nets de frais")}</span></header>
  <div class="kpis">
   <div class="kpi"><div class="k">Horus Smart Beta 60/40</div><div class="v">{pct(hp["cagr"], 1, lang=lang)}</div><div class="s">{L(lang, "a year since 2007 vs", "par an depuis 2007 vs")} {pct(HS["b"]["cagr"], 1, lang=lang)}</div></div>
   <div class="kpi"><div class="k">{L(lang, "Value signal (stock level)", "Signal value (titres)")}</div><div class="v">{num(IC_MEAN, 3, lang)}</div><div class="s">{L(lang, "rank IC, t ≈", "IC de rang, t ≈")} {num(IC_T, 1, lang)}</div></div>
   <div class="kpi"><div class="k">{L(lang, "Stock pitches", "Stock pitches")}</div><div class="v">{len(PITCHES)}</div><div class="s">{ow} {L(lang, "Overweight, 2 case studies", "Surpondérer, 2 cas d'école")}</div></div>
   <div class="kpi"><div class="k">{L(lang, "Securities researched", "Titres étudiés")}</div><div class="v">1 990</div><div class="s">{L(lang, "developed markets, 10 dates", "marchés développés, 10 dates")}</div></div>
  </div>
  <footer>{L(lang, "Hypothetical backtests. Past performance does not guarantee future returns.", "Backtests hypothétiques. Les performances passées ne préjugent pas des performances futures.")}</footer>
 </div>
</div></section>

<section class="sec"><div class="wrap">
 <div class="shead"><h2>{L(lang, "Three strategies, one discipline", "Trois stratégies, une même discipline")}</h2>
 <p>{L(lang, "Each strategy can be held with a handful of UCITS ETFs, is rebalanced on a fixed calendar and was specified before its backtest was run.", "Chaque stratégie se détient avec quelques ETF UCITS, se rebalance à date fixe et a été spécifiée avant que son backtest ne tourne.")}</p></div>
 {cards}
</div></section>

<section class="sec alt"><div class="wrap">
 <div class="cols2" style="gap:48px;align-items:start">
  <div><div class="shead"><h2>{L(lang, "From top-down to bottom-up", "Du top-down au bottom-up")}</h2>
   <p>{L(lang, "The value rotation chooses cheap countries and sectors. The stock screen finds the cheapest companies inside them. The pitches check, one company at a time, whether cheap means mispriced.", "La rotation value choisit les pays et secteurs bon marché. Le screen titres trouve les sociétés les moins chères à l'intérieur. Les pitches vérifient, une société à la fois, si bon marché veut dire mal valorisé.")}</p></div>
   <div class="btns"><a class="btn" href="pitches/">{L(lang, "All pitches", "Tous les pitches")} →</a></div></div>
  <div class="notes">{pitch_rows}</div>
 </div>
</div></section>

<section class="sec"><div class="wrap">
 <div class="horus">
  <div><div class="eyebrow">{L(lang, "Also by me", "Mon autre projet")}</div><h3>Horus Asset Management</h3>
   <p>{L(lang, "A student investment boutique I built with four classmates for the SKEMA Portfolio Management course. Its flagship, Horus Smart Beta 60/40, is also in my strategies.", "Une boutique de gestion étudiante créée avec quatre camarades pour le cours de Portfolio Management de SKEMA. Sa stratégie phare, Horus Smart Beta 60/40, figure aussi parmi mes stratégies.")}</p></div>
  <div class="btns"><a class="btn" href="{HORUS_URL}">{L(lang, "Visit Horus AM", "Visiter Horus AM")} {ICON_EXT}</a><a class="btn ghost" href="strategies/horus-smart-beta/">{L(lang, "The strategy", "La stratégie")}</a></div>
 </div>
</div></section>

<section class="sec alt"><div class="wrap">
 <div class="shead"><h2>{L(lang, "Latest research", "Dernières notes de recherche")}</h2></div>
 <div class="notes">{"".join(f'<a class="noteitem" href="research/{n["slug"]}/"><span class="d">{esc(n["date"])}</span><div><h3>{esc(n["title"])}</h3><p>{esc(n["summary"])}</p></div><span class="go">{t(lang, "read")} →</span></a>' for n in notes)}</div>
</div></section>"""
    page("index.html", lang, SITE, body, "index",
         L(lang, "Equity research by Noah Doose: ETF-replicable strategies, stock pitches and data.",
           "Recherche actions de Noah Doose : stratégies réplicables en ETF, stock pitches et données."))


def strategy_cards(lang, lr):
    hp = HS["p"]
    status = L(lang, "Backtest in progress", "Backtest en cours")
    return f"""<div class="grid three">
 <article class="card"><div class="tags"><span class="tag green">{L(lang, "Equities · ETF", "Actions · ETF")}</span><span class="tag amber">{status}</span></div>
  <h3><a href="{lr}strategies/value-rotation/">{L(lang, "Global Value Rotation", "Rotation Value mondiale")}</a></h3>
  <p>{L(lang, "Each month, buy the cheapest developed countries and sectors relative to their own history: eight ETFs, equal weight.", "Chaque mois, acheter les pays et secteurs développés les moins chers par rapport à leur propre historique : huit ETF à parts égales.")}</p>
  <div class="mini"><div><span>{L(lang, "Universe", "Univers")}</span><b>25 ETF</b></div><div><span>{L(lang, "Holdings", "Lignes")}</span><b>8</b></div><div><span>{L(lang, "Rebalance", "Rebalancement")}</span><b>{L(lang, "Monthly", "Mensuel")}</b></div></div>
  <div class="foot"><span>{L(lang, "Linked to the stock pitches", "Reliée aux stock pitches")}</span><b>→</b></div></article>
 <article class="card"><div class="tags"><span class="tag green">{L(lang, "Multi-asset · ETF", "Multi-actifs · ETF")}</span><span class="tag amber">{status}</span></div>
  <h3><a href="{lr}strategies/trend-following/">{L(lang, "Multi-Asset Trend", "Trend multi-actifs")}</a></h3>
  <p>{L(lang, "Hold equities, bonds and commodities only while they trend up, sized by risk, cash otherwise. Long only, no leverage.", "Détenir actions, obligations et matières premières seulement quand elles sont en tendance haussière, dimensionnées par le risque, sinon du cash. Long uniquement, sans levier.")}</p>
  <div class="mini"><div><span>{L(lang, "Universe", "Univers")}</span><b>14 ETF</b></div><div><span>{L(lang, "Target vol.", "Vol. cible")}</span><b>10%</b></div><div><span>{L(lang, "Rebalance", "Rebalancement")}</span><b>{L(lang, "Monthly", "Mensuel")}</b></div></div>
  <div class="foot"><span>{L(lang, "Futures study archived", "Étude futures archivée")}</span><b>→</b></div></article>
 <article class="card"><div class="tags"><span class="tag gold">Horus AM</span><span class="tag">{L(lang, "Live since 2007 (backtest)", "Backtest depuis 2007")}</span></div>
  <h3><a href="{lr}strategies/horus-smart-beta/">Horus Smart Beta 60/40</a></h3>
  <p>{L(lang, "A permanent 60/40 whose equity half holds the two ETFs most exposed to size, growth and momentum, chosen each January.", "Un 60/40 permanent dont la poche actions détient les deux ETF les plus exposés à la taille, la croissance et le momentum, choisis chaque janvier.")}</p>
  <div class="mini"><div><span>CAGR</span><b>{pct(hp["cagr"], 1, lang=lang)}</b></div><div><span>Sharpe</span><b>{num(hp["sharpe"], 2, lang)}</b></div><div><span>Max DD</span><b>{pct(hp["mdd"], 0, lang=lang)}</b></div></div>
  <div class="foot"><span>60/40 : {pct(HS["b"]["cagr"], 1, lang=lang)}</span><b>→</b></div></article>
</div>"""


# ---------------------------------------------------------------- STRATEGIES INDEX
def build_strategies(lang):
    body = phead(t(lang, "strategies"), L(lang, "Strategies you can hold with ETFs", "Des stratégies que l'on peut détenir avec des ETF"),
                 L(lang, "Three rules-based strategies, each implementable with UCITS ETFs and rebalanced on a fixed calendar, plus the stock-level research engine that feeds the pitches.",
                   "Trois stratégies systématiques, chacune réplicable avec des ETF UCITS et rebalancée à date fixe, plus le moteur de recherche titre par titre qui alimente les pitches."))
    body += f'<section class="sec"><div class="wrap">{strategy_cards(lang, "../")}</div></section>'
    body += f"""<section class="sec alt"><div class="wrap"><div class="shead"><h2>{L(lang, "Research behind the strategies", "La recherche derrière les stratégies")}</h2></div>
<div class="grid">
 <article class="card"><div class="meta">{L(lang, "Stock level · 1,990 developed-market stocks · 2021-2026", "Titres · 1 990 actions de pays développés · 2021-2026")}</div>
  <h3><a href="value-developed/">{L(lang, "Stock-level value screen", "Screen value titre par titre")}</a></h3>
  <p>{L(lang, "The research engine behind the value rotation and the pitches: sector-neutral value composite, 50 names, three weighting schemes.", "Le moteur de recherche derrière la rotation value et les pitches : composite value neutre par secteur, 50 titres, trois pondérations.")}</p>
  <div class="foot"><span>{L(lang, "Equal weight", "Équipondéré")} {pct(H["EW"]["ann_return"], 1, lang=lang)} · IC {num(IC_MEAN, 3, lang)}</span><b>→</b></div></article>
 <article class="card"><div class="meta">{L(lang, "Futures · 17 markets · 2001-2026 · English and French", "Futures · 17 marchés · 2001-2026 · anglais et français")}</div>
  <h3><a href="{'../trend-following/' if lang == 'en' else '../../trend-following/fr/'}">{L(lang, "Trend following with futures (archived study)", "Trend following en futures (étude archivée)")}</a></h3>
  <p>{L(lang, "The original time-series momentum study on futures, with design and validation periods. The ETF strategy above replaces it as the investable version.", "L'étude d'origine de momentum en séries temporelles sur futures, avec périodes de conception et de validation. La stratégie ETF ci-dessus la remplace comme version investissable.")}</p>
  <div class="foot"><span>{L(lang, "Full report", "Rapport complet")}</span><b>→</b></div></article>
</div></div></section>"""
    page("strategies/index.html", lang, t(lang, "strategies"), body, "strategies",
         L(lang, "ETF-replicable strategies by Noah Doose.", "Stratégies réplicables en ETF de Noah Doose."))


# ---------------------------------------------------------------- VALUE ROTATION
def status_block(lang):
    return f"""<div class="status"><span class="dot"></span><div><b>{L(lang, "Backtest in progress", "Backtest en cours")}</b>
<p>{L(lang, "The rules below were fixed on 30 October 2026, before the data were extracted. Monthly index data (2000-2026) are being extracted from the Bloomberg terminal; results will be published here with every variant tested.",
      "Les règles ci-dessous ont été fixées le 30 octobre 2026, avant l'extraction des données. Les données mensuelles d'indices (2000-2026) sont en cours d'extraction sur le terminal Bloomberg ; les résultats seront publiés ici avec toutes les variantes testées.")}</p></div></div>"""


def build_value_rotation(lang):
    lr = "../../"
    by_country = {}
    by_sector = {}
    for s in PITCHES:
        by_country.setdefault(COUNTRY_CODE.get(s["country"]), []).append(s)
        by_sector.setdefault(SECTOR_CODE.get(s["sector"]), []).append(s)
    crow = [[f"<b>{esc(tr(lang, nm))}</b>", f'<span class="mono">{mx} Index</span>', f'<span class="mono">{loc} Index</span>', pitch_links(by_country.get(code, []), lang, lr)]
            for code, nm, mx, loc in COUNTRIES]
    srow = [[f"<b>{esc(tr(lang, nm))}</b>", f'<span class="mono">{mx} Index</span>', pitch_links(by_sector.get(code, []), lang, lr)] for code, nm, mx in SECTORS]
    rules = tbl([L(lang, "Step", "Étape"), L(lang, "Rule", "Règle")], [
        [L(lang, "Universe", "Univers"), L(lang, "14 developed-country indices and the 11 GICS sectors of MSCI World: 25 lines, each held through one UCITS ETF.", "14 indices de pays développés et les 11 secteurs GICS du MSCI World : 25 lignes, chacune détenue via un ETF UCITS.")],
        [L(lang, "Signal", "Signal"), L(lang, "Average of three z-scores: earnings yield (E/P), book yield (B/P) and dividend yield, each measured against the line's own trailing 10-year history (at least 5 years). A country is cheap when it is cheap versus its own past, so structurally cheap markets are not bought forever.", "Moyenne de trois z-scores : rendement bénéficiaire (E/P), rendement comptable (B/P) et rendement du dividende, chacun mesuré par rapport à l'historique propre de la ligne sur 10 ans glissants (5 ans minimum). Un pays est bon marché quand il l'est par rapport à son propre passé : les marchés structurellement peu chers ne sont pas achetés éternellement.")],
        [L(lang, "Selection", "Sélection"), L(lang, "Two sleeves of equal size: the 4 cheapest countries and the 4 cheapest sectors.", "Deux poches de même taille : les 4 pays les moins chers et les 4 secteurs les moins chers.")],
        [L(lang, "Weighting", "Pondération"), L(lang, "Equal weight, 12.5% per ETF; fully invested, long only.", "Équipondération, 12,5 % par ETF ; investi en totalité, long uniquement.")],
        [L(lang, "Rebalancing", "Rebalancement"), L(lang, "Monthly: signal at the last trading day of the month, trades on the first trading day of the next month.", "Mensuel : signal au dernier jour de bourse du mois, ordres le premier jour de bourse du mois suivant.")],
        [L(lang, "Costs", "Frais"), L(lang, "0.10% per unit of turnover and 0.25% a year of ETF fees.", "0,10 % par unité de rotation et 0,25 % par an de frais d'ETF.")],
        [L(lang, "Benchmark", "Benchmark"), L(lang, "MSCI World Net Total Return in EUR.", "MSCI World Net Total Return en EUR.")],
        [L(lang, "Test plan", "Plan de test"), L(lang, "Backtest January 2006 to September 2026 in EUR. Variants published whatever the result: 3 or 6 lines per sleeve, a 12-month momentum filter, countries only, sectors only.", "Backtest de janvier 2006 à septembre 2026 en EUR. Variantes publiées quel que soit le résultat : 3 ou 6 lignes par poche, filtre momentum 12 mois, pays seuls, secteurs seuls.")],
    ])
    toc = [("idea", L(lang, "The idea", "L'idée")), ("rules", L(lang, "Rules", "Règles")), ("universe", L(lang, "Universe", "Univers")),
           ("pitches", L(lang, "Link with the pitches", "Lien avec les pitches")), ("results", L(lang, "Results", "Résultats")),
           ("risks", L(lang, "Risks", "Risques"))]
    secs = [
        section("idea", L(lang, "The idea", "L'idée"), f"""<div class="prose"><p>{L(lang,
            "Value works across markets, not only across stocks: countries and sectors that are cheap relative to their own history have tended to outperform over the following years (Asness, Moskowitz and Pedersen, 2013, <i>Value and Momentum Everywhere</i>). Countries and sectors are also easy to hold: one ETF each, cheap, liquid, available to any European investor.",
            "Le value fonctionne entre marchés, pas seulement entre actions : les pays et secteurs bon marché par rapport à leur propre historique ont eu tendance à surperformer les années suivantes (Asness, Moskowitz et Pedersen, 2013, <i>Value and Momentum Everywhere</i>). Pays et secteurs sont aussi faciles à détenir : un ETF chacun, peu coûteux, liquide, accessible à tout investisseur européen.")}</p>
<p>{L(lang, "The rotation is the top-down half of my value process. The stock-level screen and the pitches are the bottom-up half.", "La rotation est la moitié top-down de mon processus value. Le screen titres et les pitches en sont la moitié bottom-up.")}</p></div>
<div class="steps" style="margin-top:22px">
 <div class="box"><h4>{L(lang, "Measure", "Mesurer")}</h4><p>{L(lang, "E/P, B/P and dividend yield of 25 indices at each month end.", "E/P, B/P et rendement du dividende de 25 indices à chaque fin de mois.")}</p></div>
 <div class="box"><h4>{L(lang, "Score", "Noter")}</h4><p>{L(lang, "Each ratio versus the line's own 10-year history, averaged.", "Chaque ratio rapporté à l'historique propre de la ligne sur 10 ans, puis moyenné.")}</p></div>
 <div class="box"><h4>{L(lang, "Select", "Sélectionner")}</h4><p>{L(lang, "The 4 cheapest countries and the 4 cheapest sectors.", "Les 4 pays et les 4 secteurs les moins chers.")}</p></div>
 <div class="box"><h4>{L(lang, "Hold", "Détenir")}</h4><p>{L(lang, "Eight ETFs at 12.5% each until the next month end.", "Huit ETF à 12,5 % chacun jusqu'à la fin du mois suivant.")}</p></div>
</div>"""),
        section("rules", L(lang, "Rules", "Règles"), rules, L(lang, "Fixed before any data was extracted. Changing a rule after seeing a result would be one more trial, and would weaken every statistic.", "Fixées avant toute extraction de données. Changer une règle après avoir vu un résultat serait un essai de plus et affaiblirait chaque statistique.")),
        section("universe", L(lang, "Universe", "Univers"),
                f'<h3 style="margin-top:0">{L(lang, "Countries", "Pays")}</h3>' +
                tbl([L(lang, "Country", "Pays"), L(lang, "MSCI index", "Indice MSCI"), L(lang, "Fallback index", "Indice de secours"), L(lang, "Our pitches", "Nos pitches")], crow) +
                f'<h3>{L(lang, "Sectors (MSCI World)", "Secteurs (MSCI World)")}</h3>' +
                tbl([L(lang, "Sector", "Secteur"), L(lang, "MSCI index", "Indice MSCI"), L(lang, "Our pitches", "Nos pitches")], srow) +
                f'<p class="cap">{L(lang, "Each line is implemented with a UCITS ETF listed in euros; the index history is used before the ETF existed. Fallback indices are used only if MSCI valuation data are not licensed on the terminal.", "Chaque ligne est implémentée avec un ETF UCITS coté en euros ; l’historique de l’indice est utilisé avant la création de l’ETF. Les indices de secours ne servent que si les données de valorisation MSCI ne sont pas licenciées sur le terminal.")}</p>'),
        section("pitches", L(lang, "Link with the pitches", "Lien avec les pitches"), f"""<div class="cols3">
 <div class="box accent"><div class="k">{L(lang, "1 · Top-down", "1 · Top-down")}</div><h4 style="margin-top:6px">{L(lang, "Value rotation", "Rotation value")}</h4><p>{L(lang, "Which countries and sectors are cheap this month.", "Quels pays et secteurs sont bon marché ce mois-ci.")}</p></div>
 <div class="box accent"><div class="k">{L(lang, "2 · Screen", "2 · Screen")}</div><h4 style="margin-top:6px"><a href="../value-developed/">{L(lang, "Stock-level value screen", "Screen value titres")}</a></h4><p>{L(lang, "The cheapest companies within each sector, 1,990 stocks.", "Les sociétés les moins chères de chaque secteur, sur 1 990 actions.")}</p></div>
 <div class="box accent"><div class="k">{L(lang, "3 · Bottom-up", "3 · Bottom-up")}</div><h4 style="margin-top:6px"><a href="{lr}pitches/">{t(lang, "pitches")}</a></h4><p>{L(lang, "Is cheap mispriced, or cheap for a reason? Each pitch answers for one name.", "Bon marché veut-il dire mal valorisé, ou bon marché pour une raison ? Chaque pitch répond pour un titre.")}</p></div>
</div><div class="callout">{L(lang, "When the rotation holds a country or a sector, the pitches in that country or sector are the names I would add to express the view through single stocks. The universe tables above list them.", "Quand la rotation détient un pays ou un secteur, les pitches de ce pays ou de ce secteur sont les titres que j’ajouterais pour exprimer la vue en actions individuelles. Les tableaux d’univers ci-dessus les listent.")}</div>""", alt=False),
        section("results", L(lang, "Results", "Résultats"), status_block(lang)),
        section("risks", L(lang, "Risks", "Risques"), f"""<div class="cols3">
 <div class="box"><h4>{L(lang, "Value traps at market level", "Pièges à valeur à l’échelle d’un marché")}</h4><p>{L(lang, "A country can stay cheap for years (Italy, Hong Kong). Measuring cheapness against its own history limits this, but does not remove it.", "Un pays peut rester bon marché des années (Italie, Hong Kong). Mesurer la décote par rapport à son propre historique limite ce risque sans le supprimer.")}</p></div>
 <div class="box"><h4>{L(lang, "Concentration", "Concentration")}</h4><p>{L(lang, "Eight lines can overlap: a cheap Financials sector and a cheap Italy are partly the same bet.", "Huit lignes peuvent se recouper : un secteur Finance bon marché et une Italie bon marché sont en partie le même pari.")}</p></div>
 <div class="box"><h4>{L(lang, "Growth markets", "Marchés de croissance")}</h4><p>{L(lang, "When expensive growth leads, as in 2023-24, a value rotation lags the benchmark.", "Quand la croissance chère mène, comme en 2023-24, une rotation value fait moins bien que le benchmark.")}</p></div>
</div>"""),
    ]
    body = phead(L(lang, "Strategy · Equities · ETF", "Stratégie · Actions · ETF"), L(lang, "Global Value Rotation", "Rotation Value mondiale"),
                 L(lang, "Each month, hold the four cheapest developed countries and the four cheapest sectors, measured against their own history. Eight UCITS ETFs, equal weight.",
                   "Chaque mois, détenir les quatre pays développés et les quatre secteurs les moins chers par rapport à leur propre historique. Huit ETF UCITS à parts égales."),
                 f'<a href="../">{t(lang, "strategies")}</a> / value-rotation')
    body += doc_layout(lang, toc, secs)
    page("strategies/value-rotation/index.html", lang, L(lang, "Global Value Rotation", "Rotation Value mondiale"), body, "strategies",
         L(lang, "Monthly value rotation across developed countries and sectors with UCITS ETFs.", "Rotation value mensuelle entre pays et secteurs développés avec des ETF UCITS."))


# ---------------------------------------------------------------- TREND FOLLOWING (ETF)
def build_trend(lang):
    rows = [[esc(tr(lang, ac)), f"<b>{esc(L(lang, en, fr))}</b>", esc(idx), esc(etf if etf != "to select" else L(lang, "to select", "à choisir"))] for ac, en, fr, idx, etf in TREND]
    rules = tbl([L(lang, "Step", "Étape"), L(lang, "Rule", "Règle")], [
        [L(lang, "Universe", "Univers"), L(lang, "14 ETFs: 4 equity regions, 4 bond markets, 6 commodities.", "14 ETF : 4 régions actions, 4 marchés obligataires, 6 matières premières.")],
        [L(lang, "Signal", "Signal"), L(lang, "For each asset, the sign of its excess return over cash on 3, 6 and 12 months, averaged: from −1 to +1. The same blend as the futures study, chosen there for robustness, not for its result.", "Pour chaque actif, le signe de son rendement excédentaire sur le cash à 3, 6 et 12 mois, moyenné : de −1 à +1. Le même mélange que dans l’étude futures, choisi pour sa robustesse et non pour son résultat.")],
        [L(lang, "Position", "Position"), L(lang, "Long when the signal is positive, in proportion to it; cash otherwise. No short positions: an ETF investor cannot short cheaply.", "Long quand le signal est positif, proportionnellement à celui-ci ; cash sinon. Pas de position courte : un investisseur en ETF ne peut pas vendre à découvert à bas coût.")],
        [L(lang, "Sizing", "Dimensionnement"), L(lang, "Each asset gets the same risk (inverse of its 12-month volatility); the portfolio is scaled to a 10% volatility target, with at most 100% invested.", "Chaque actif reçoit le même risque (inverse de sa volatilité 12 mois) ; le portefeuille est ajusté pour viser 10 % de volatilité, avec au plus 100 % investi.")],
        [L(lang, "Rebalancing", "Rebalancement"), L(lang, "Monthly, at the first trading day of the month.", "Mensuel, au premier jour de bourse du mois.")],
        [L(lang, "Cash", "Cash"), L(lang, "Money-market rate (€STR, Euribor before 2019) on the uninvested part.", "Taux monétaire (€STR, Euribor avant 2019) sur la part non investie.")],
        [L(lang, "Costs", "Frais"), L(lang, "0.10% per unit of turnover and 0.30% a year of ETF fees.", "0,10 % par unité de rotation et 0,30 % par an de frais d’ETF.")],
        [L(lang, "Test plan", "Plan de test"), L(lang, "January 2001 to September 2026 in EUR; design period to 2015, validation afterwards, untouched. References: MSCI World Net EUR and a 60/40.", "Janvier 2001 à septembre 2026 en EUR ; conception jusqu’en 2015, validation ensuite, sans retouche. Références : MSCI World Net EUR et un 60/40.")],
    ])
    toc = [("idea", L(lang, "The idea", "L'idée")), ("rules", L(lang, "Rules", "Règles")), ("universe", L(lang, "Universe", "Univers")),
           ("results", L(lang, "Results", "Résultats")), ("archive", L(lang, "Futures study", "Étude futures"))]
    archive = "../../trend-following/" if lang == "en" else "../../../trend-following/fr/"
    secs = [
        section("idea", L(lang, "The idea", "L'idée"), f"""<div class="prose"><p>{L(lang,
            "Markets that have risen over the past months tend to keep rising for a while, across asset classes and over a century of data (Moskowitz, Ooi and Pedersen, 2012; Hurst, Ooi and Pedersen, 2017). Trend following does not forecast; it follows, and it steps aside when a market turns down.",
            "Les marchés qui ont monté ces derniers mois ont tendance à continuer de monter un temps, dans toutes les classes d’actifs et sur plus d’un siècle de données (Moskowitz, Ooi et Pedersen, 2012 ; Hurst, Ooi et Pedersen, 2017). Le trend following ne prévoit pas : il suit, et il se retire quand un marché se retourne.")}</p>
<p>{L(lang, "This version is built for a private investor in Europe: UCITS ETFs only, long or cash, monthly trades. It is the investable counterpart of my earlier futures study.", "Cette version est pensée pour un investisseur particulier en Europe : uniquement des ETF UCITS, long ou cash, des ordres mensuels. C’est la contrepartie investissable de mon étude précédente sur futures.")}</p></div>"""),
        section("rules", L(lang, "Rules", "Règles"), rules, L(lang, "Fixed before the data extraction of 30 October 2026.", "Fixées avant l’extraction des données du 30 octobre 2026.")),
        section("universe", L(lang, "Universe", "Univers"), tbl([L(lang, "Asset class", "Classe d’actifs"), L(lang, "Market", "Marché"), L(lang, "Index (history)", "Indice (historique)"), L(lang, "UCITS ETF", "ETF UCITS")], rows)),
        section("results", L(lang, "Results", "Résultats"), status_block(lang)),
        section("archive", L(lang, "Futures study", "Étude futures"), f"""<div class="prose"><p>{L(lang,
            "The original study used 17 futures markets, long and short, from 2001 to 2026. Its 3/6/12-month blend earned 6.9% a year with a 0.64 Sharpe ratio; its long/cash ETF approximation 4.7% with 7.5% volatility. The full report stays online.",
            "L’étude d’origine portait sur 17 marchés à terme, long et court, de 2001 à 2026. Son mélange 3/6/12 mois a rapporté 6,9 % par an avec un ratio de Sharpe de 0,64 ; son approximation ETF long/cash 4,7 % avec 7,5 % de volatilité. Le rapport complet reste en ligne.")}</p></div>
<div class="btns"><a class="btn" href="{archive}">{L(lang, "Open the futures report", "Ouvrir le rapport futures")} →</a></div>"""),
    ]
    body = phead(L(lang, "Strategy · Multi-asset · ETF", "Stratégie · Multi-actifs · ETF"), L(lang, "Multi-Asset Trend", "Trend multi-actifs"),
                 L(lang, "Fourteen ETFs across equities, bonds and commodities. Each one is held only while its trend is up, sized by risk, with the rest in cash. Rebalanced monthly.",
                   "Quatorze ETF en actions, obligations et matières premières. Chacun n’est détenu que lorsque sa tendance est haussière, dimensionné par le risque, le reste en cash. Rebalancement mensuel."),
                 f'<a href="../">{t(lang, "strategies")}</a> / trend-following')
    body += doc_layout(lang, toc, secs)
    page("strategies/trend-following/index.html", lang, L(lang, "Multi-Asset Trend", "Trend multi-actifs"), body, "strategies",
         L(lang, "Monthly long/cash trend following with UCITS ETFs.", "Trend following mensuel long/cash avec des ETF UCITS."))


# ---------------------------------------------------------------- HORUS SMART BETA
def build_horus(lang):
    hp, hb = HS["p"], HS["b"]
    nameP, nameB = "Horus Smart Beta 60/40", L(lang, "Benchmark 60/40", "Benchmark 60/40")
    nav = {"dates": HS["dates"], "series": {nameP: [round(x, 5) for x in hp["nav"]], nameB: [round(x, 5) for x in hb["nav"]]},
           "colors": {nameP: "--gold", nameB: "--bench"}, "bench": [nameB], "main": nameP}
    chart = nav_chart("navchart", L(lang, "Growth of 100", "Croissance de 100"), L(lang, "monthly, USD", "mensuel, USD"),
                      [("5", "5Y" if lang == "en" else "5A"), ("10", "10Y" if lang == "en" else "10A"), ("all", L(lang, "All", "Tout"))],
                      [("nav", L(lang, "Growth", "Croissance")), ("dd", "Drawdown")], [nameP, nameB])
    srow = [[L(lang, "Annual return (CAGR)", "Rendement annuel (CAGR)"), pct(hp["cagr"], 1, lang=lang), pct(hb["cagr"], 1, lang=lang)],
            [L(lang, "Volatility", "Volatilité"), pct(hp["vol"], 1, lang=lang), pct(hb["vol"], 1, lang=lang)],
            ["Sharpe", num(hp["sharpe"], 2, lang), num(hb["sharpe"], 2, lang)],
            [L(lang, "Maximum drawdown", "Perte maximale"), pct(hp["mdd"], 1, lang=lang), pct(hb["mdd"], 1, lang=lang)],
            [L(lang, "Beta vs benchmark", "Bêta vs benchmark"), num(HS["beta"], 2, lang), "1,00" if lang == "fr" else "1.00"],
            [L(lang, "Tracking error", "Tracking error"), pct(HS["te"], 1, lang=lang), "—"],
            [L(lang, "Years ahead of the benchmark", "Années devant le benchmark"), f'{HS["ahead"]}/{len(HS["years"])}', "—"]]
    stats_tbl = tbl([L(lang, "Statistic", "Statistique"), nameP, nameB], srow, num_cols=(1, 2))
    ann = svg_columns(HS["years"], [x * 100 for x in HS["ann_p"]], lambda v: num(v, 0, lang), w=980, h=260,
                      series2=[x * 100 for x in HS["ann_b"]], names=[nameP, nameB])
    sel_rows = []
    for y in sorted(HORUS["sel"], reverse=True):
        eq = [k for k, w in HORUS["sel"][y].items() if w >= .3 - 1e-9]
        bd = [k for k, w in HORUS["sel"][y].items() if w < .3 - 1e-9]
        name = lambda k: f'<span class="mono">{k}</span> {esc(HORUS_ETF.get(k, (k, k))[1 if lang == "fr" else 0])}'
        sel_rows.append([f"<b>{y}</b>", "<br>".join(name(k) for k in eq), "<br>".join(name(k) for k in bd)])
    sel_tbl = tbl([L(lang, "Year", "Année"), L(lang, "Equities, 30% each", "Actions, 30 % chacune"), L(lang, "Bonds, 20% each", "Obligations, 20 % chacune")], sel_rows)
    toc = [("results", L(lang, "Results", "Résultats")), ("process", L(lang, "Process", "Processus")), ("years", L(lang, "Year by year", "Année par année")),
           ("holdings", L(lang, "Holdings", "Portefeuilles")), ("risks", L(lang, "Risks", "Risques")), ("horus", "Horus AM")]
    secs = [
        section("results", L(lang, "Results", "Résultats"), f"""<div class="stats" style="margin-bottom:18px">
 {stat(L(lang, "Annual return", "Rendement annuel"), pct(hp["cagr"], 1, lang=lang), L(lang, "vs", "vs") + " " + pct(hb["cagr"], 1, lang=lang))}
 {stat("Sharpe", num(hp["sharpe"], 2, lang), L(lang, "vs", "vs") + " " + num(hb["sharpe"], 2, lang))}
 {stat(L(lang, "Max drawdown", "Perte maximale"), pct(hp["mdd"], 1, lang=lang), L(lang, "vs", "vs") + " " + pct(hb["mdd"], 1, lang=lang))}
 {stat(L(lang, "Years ahead", "Années devant"), f'{HS["ahead"]}/{len(HS["years"])}', L(lang, "calendar years", "années civiles"))}
</div>{chart}<h3>{L(lang, "Statistics, January 2007 to", "Statistiques, janvier 2007 à")} {month_name(HORUS["end"], lang)}</h3>{stats_tbl}
<p class="cap">{L(lang, "Hypothetical backtest in USD, out of sample: each January the rule uses only the three previous years. Benchmark: 60% MSCI World, 40% Bloomberg Global Aggregate. Sharpe ratios use the US 3-month T-bill.", "Backtest hypothétique en USD, hors échantillon : chaque janvier, la règle n’utilise que les trois années précédentes. Benchmark : 60 % MSCI World, 40 % Bloomberg Global Aggregate. Ratios de Sharpe calculés avec le T-bill américain à 3 mois.")}</p>"""),
        section("process", L(lang, "Process", "Processus"), f"""<div class="steps">
 <div class="box"><h4>{L(lang, "Measure", "Mesurer")}</h4><p>{L(lang, "A Carhart regression for each of 12 equity ETFs on the last 36 months: exposure to size, value and momentum.", "Une régression de Carhart pour chacun des 12 ETF actions sur les 36 derniers mois : exposition à la taille, au value et au momentum.")}</p></div>
 <div class="box"><h4>{L(lang, "Score", "Noter")}</h4><p>{L(lang, "z(size) + z(−value) + z(momentum): small, growth and momentum count equally.", "z(taille) + z(−value) + z(momentum) : petites capitalisations, croissance et momentum comptent à égalité.")}</p></div>
 <div class="box"><h4>{L(lang, "Select", "Sélectionner")}</h4><p>{L(lang, "The two best-scored equity ETFs at 30% each, and the two bond ETFs with the best 3-year Sharpe ratio at 20% each.", "Les deux ETF actions les mieux notés à 30 % chacun, et les deux ETF obligataires au meilleur Sharpe sur 3 ans à 20 % chacun.")}</p></div>
 <div class="box"><h4>{L(lang, "Hold", "Détenir")}</h4><p>{L(lang, "Four funds for twelve months, then start again each January.", "Quatre fonds pendant douze mois, puis on recommence chaque janvier.")}</p></div>
</div>"""),
        section("years", L(lang, "Year by year", "Année par année"), f'<figure class="ch"><figcaption><span>{L(lang, "Calendar-year returns", "Rendements par année civile")} <small>· %</small></span></figcaption>{ann}</figure>'),
        section("holdings", L(lang, "Holdings", "Portefeuilles"), sel_tbl, L(lang, "The factors never change; the funds that carry them do.", "Les facteurs ne changent jamais ; les fonds qui les portent, si.")),
        section("risks", L(lang, "Risks", "Risques"), f"""<div class="cols3">
 <div class="box"><h4>{L(lang, "Mega-cap years", "Années des méga-capitalisations")}</h4><p>{L(lang, "When a few giants lead, small caps lag: 2023 to 2025 were behind the benchmark.", "Quand quelques géants mènent, les petites capitalisations décrochent : 2023 à 2025 ont été en retard sur le benchmark.")}</p></div>
 <div class="box"><h4>{L(lang, "Momentum reversals", "Retournements du momentum")}</h4><p>{L(lang, "Momentum can crash, as in 2009; it is one factor of three for that reason.", "Le momentum peut s’effondrer, comme en 2009 ; c’est pour cela qu’il ne pèse qu’un tiers.")}</p></div>
 <div class="box"><h4>{L(lang, "Not a shelter", "Pas un abri")}</h4><p>{L(lang, "The 60/40 is permanent: in 2008 and 2022 the equity half fell with the market.", "Le 60/40 est permanent : en 2008 et 2022, la poche actions a baissé avec le marché.")}</p></div>
</div>"""),
        section("horus", "Horus Asset Management", f"""<div class="horus"><div><div class="eyebrow">{L(lang, "Group project · SKEMA 2026", "Projet de groupe · SKEMA 2026")}</div><h3>{L(lang, "The full story is on the Horus AM website", "L’histoire complète est sur le site d’Horus AM")}</h3>
<p>{L(lang, "Factsheets, a return simulator, a holdings explorer and the factor analysis, in English and French.", "Factsheets, simulateur de rendement, explorateur des portefeuilles et analyse factorielle, en anglais et en français.")}</p></div>
<div class="btns"><a class="btn" href="{HORUS_URL}">{L(lang, "Visit Horus AM", "Visiter Horus AM")} {ICON_EXT}</a></div></div>"""),
    ]
    body = phead(L(lang, "Strategy · Horus Asset Management", "Stratégie · Horus Asset Management"), "Horus Smart Beta 60/40",
                 L(lang, "Same 60/40, smarter equities and bonds inside. Strategic factors that never change (size, growth, momentum) and a tactical ETF selection every January.",
                   "Le même 60/40, avec des actions et des obligations mieux choisies. Des facteurs stratégiques qui ne changent jamais (taille, croissance, momentum) et une sélection tactique d’ETF chaque janvier."),
                 f'<a href="../">{t(lang, "strategies")}</a> / horus-smart-beta')
    body += doc_layout(lang, toc, secs)
    nav_json = json.dumps(nav).replace("</", "<\\/")
    page("strategies/horus-smart-beta/index.html", lang, "Horus Smart Beta 60/40", body, "strategies",
         L(lang, "Horus Smart Beta 60/40: factor ETF selection inside a permanent 60/40.", "Horus Smart Beta 60/40 : sélection factorielle d’ETF dans un 60/40 permanent."),
         scripts=f"<script>window.NAV={nav_json};</script>")


# ---------------------------------------------------------------- STOCK-LEVEL VALUE SCREEN
def build_value_screen(lang):
    perf = VALUE["performance"]
    ci = {c: i for i, c in enumerate(perf["columns"])}
    ew = H["EW"]
    LBL = {"Equal weight": L(lang, "Equal weight", "Équipondéré"), "Minimum variance": L(lang, "Minimum variance", "Variance minimale"),
           "Mean-variance": L(lang, "Mean-variance", "Moyenne-variance"), "MSCI World Net EUR": "MSCI World Net EUR",
           "hedged, net of costs": L(lang, "hedged, net of costs", "couvert, net de frais"), "hedged, before costs": L(lang, "hedged, before costs", "couvert, avant frais"),
           "unhedged, net of costs": L(lang, "unhedged, net of costs", "non couvert, net de frais")}
    rows = []
    for name, v in zip(perf["index"], perf["values"]):
        m = re.match(r"^(.*?) \((.*)\)$", name)
        label = f'{LBL.get(m.group(1))}<small style="display:block">{LBL.get(m.group(2), m.group(2))}</small>' if m else LBL.get(name, name)
        bench = "MSCI" in name
        rows.append([label, pct(v[ci["ann_return"]], 1, lang=lang), pct(v[ci["ann_vol"]], 1, lang=lang), num(v[ci["sharpe"]], 2, lang),
                     "—" if bench else f'<span class="{cls_sign(v[ci["active_return"]])}">{pct(v[ci["active_return"]], 1, True, lang)}</span>',
                     "—" if bench else pct(v[ci["tracking_error"]], 1, lang=lang), pct(v[ci["max_drawdown"]], 1, lang=lang),
                     pct(v[ci["turnover_oneway_ann"]], 0, lang=lang) if v[ci["turnover_oneway_ann"]] is not None else "—"])
    perf_tbl = tbl([L(lang, "Portfolio", "Portefeuille"), L(lang, "Return", "Rendement"), "Vol.", "Sharpe", L(lang, "Active", "Actif"), "TE",
                    "Max DD", L(lang, "Turnover", "Rotation")], rows, num_cols=range(1, 8),
                   row_cls=lambda i, r: "hl" if i == 0 else ("bench" if "MSCI" in r[0] else ""))
    names = {"Equal weight": LBL["Equal weight"], "Minimum variance": LBL["Minimum variance"], "Mean-variance": LBL["Mean-variance"], "MSCI World Net EUR": "MSCI World Net EUR"}
    navd = VALUE["nav"]
    nav = {"dates": navd["dates"], "series": {names[k]: v for k, v in navd["series"].items()},
           "colors": {names["Equal weight"]: "--accent", names["Minimum variance"]: "--s2", names["Mean-variance"]: "--s3", "MSCI World Net EUR": "--bench"},
           "bench": ["MSCI World Net EUR"], "main": names["Equal weight"]}
    chart = nav_chart("navchart", L(lang, "Cumulative performance, net of costs, hedged", "Performance cumulée, nette de frais, couverte"),
                      L(lang, "weekly, rebased to 100", "hebdomadaire, base 100"), [("1", "1Y" if lang == "en" else "1A"), ("3", "3Y" if lang == "en" else "3A"), ("all", L(lang, "All", "Tout"))],
                      [("nav", L(lang, "Growth", "Croissance")), ("dd", "Drawdown")], list(nav["series"]))
    cal = VALUE["calendar"]
    cal_rows = []
    for y, vals in zip(cal["index"], cal["values"]):
        lab = y + {"2026": L(lang, " (H1)", " (S1)"), "2021": L(lang, " (from Jul)", " (dès juil.)")}.get(y, "")
        cal_rows.append([lab] + [f'<span class="{cls_sign(v)}">{pct(v, 1, True, lang)}</span>' for v in vals] +
                        [f'<b class="{cls_sign(vals[0] - vals[3])}">{pct(vals[0] - vals[3], 1, True, lang)}</b>'])
    cal_tbl = tbl([L(lang, "Year", "Année")] + [names[c] for c in cal["columns"]] + [L(lang, "EW − benchmark", "Équi. − benchmark")], cal_rows, num_cols=range(1, 6))
    ic_svg = svg_columns([x["date"][2:7].replace("-", "/") for x in IC], [x["ic"] for x in IC], lambda v: num(v, 2, lang), w=520, h=250, m=(10, 10, 16, 30))
    qavg = [statistics.mean(r[i] for r in Q["values"]) for i in range(5)]
    q_svg = svg_columns(["Q1", "Q2", "Q3", "Q4", "Q5"], qavg, lambda v: pct(v, 1, lang=lang), w=520, h=250)
    att = [a for a in VALUE["attribution"] if a["method"] == "Equal weight"]
    sec_ = [a for a in att if a["dimension"] == "sector"][0]
    fx = [a for a in att if a["dimension"] == "fx_overlay"][0]
    att_svg = svg_diverging([L(lang, "Selection within sectors", "Sélection dans les secteurs"), L(lang, "Sector allocation", "Allocation sectorielle"), L(lang, "Currency hedge", "Couverture de change")],
                            [sec_["selection"], sec_["allocation"], fx["allocation"]], lambda v: pct(v, 1, True, lang), w=640, label_w=220)
    method = tbl([L(lang, "Step", "Étape"), L(lang, "Rule", "Règle")], [
        [L(lang, "Universe", "Univers"), L(lang, "Bloomberg World large and mid caps in 24 developed countries, composition dated at each rebalance; free-float cap above €1bn, ADV above €5m.", "Grandes et moyennes capitalisations Bloomberg World de 24 pays développés, composition datée à chaque rebalancement ; flottant au-dessus de 1 Md€, volume quotidien au-dessus de 5 M€.")],
        [L(lang, "Signal", "Signal"), L(lang, "EV/EBIT, P/B, FCF yield and EV/Sales as yields (banks: P/B and P/E), winsorised, z-scored within each GICS sector, averaged.", "EV/EBIT, P/B, rendement FCF et EV/Sales exprimés en rendements (banques : P/B et P/E), winsorisés, z-scorés dans chaque secteur GICS, moyennés.")],
        [L(lang, "Accounting lag", "Décalage comptable"), L(lang, "Fiscal year used from year-end + 6 months, never before publication.", "Exercice utilisé à partir de la clôture + 6 mois, jamais avant sa publication.")],
        [L(lang, "Selection", "Sélection"), L(lang, "50 names from the cheapest sector quintile, ±10-point sector and country bands vs the benchmark.", "50 titres du quintile le moins cher de chaque secteur, bandes ±10 points par secteur et par pays vs le benchmark.")],
        [L(lang, "Weighting", "Pondération"), L(lang, "Equal weight · minimum variance · mean-variance; 0.5%-4% per name.", "Équipondéré · variance minimale · moyenne-variance ; 0,5 %-4 % par titre.")],
        [L(lang, "Rebalancing", "Rebalancement"), L(lang, "Semi-annual, ten dates from June 2021 to December 2025; 15 bp per trade.", "Semestriel, dix dates de juin 2021 à décembre 2025 ; 15 pb par transaction.")],
    ])
    toc = [("summary", L(lang, "Summary", "Synthèse")), ("method", L(lang, "Method", "Méthode")), ("performance", "Performance"),
           ("years", L(lang, "Year by year", "Année par année")), ("signal", L(lang, "The signal", "Le signal")),
           ("attribution", "Attribution"), ("limits", L(lang, "Limits", "Limites"))]
    secs = [
        section("summary", L(lang, "Summary", "Synthèse"), f"""<div class="stats">
 {stat(L(lang, "Return, equal weight", "Rendement, équipondéré"), pct(ew["ann_return"], 1, lang=lang), L(lang, "benchmark", "benchmark") + " " + pct(ew["bench_return"], 1, lang=lang))}
 {stat(L(lang, "Active return", "Rendement actif"), pct(ew["active_return"], 1, True, lang), "TE " + pct(ew["tracking_error"], 1, lang=lang), cls_sign(ew["active_return"]))}
 {stat(L(lang, "Signal IC", "IC du signal"), num(IC_MEAN, 3, lang), f"t ≈ {num(IC_T, 1, lang)}")}
 {stat(L(lang, "Cheap − dear quintile", "Quintile bon marché − cher"), pct(SPREAD_ANN, 1, True, lang), L(lang, "a year", "par an"))}
</div><div class="callout"><b>{L(lang, "The signal worked; the portfolio broke even.", "Le signal a fonctionné ; le portefeuille a fait jeu égal.")}</b> {L(lang,
  f"Stock selection inside sectors added {pct(sec_['selection'], 1, True)} a year, but holding no mega-cap growth in 2023-24 cost {pct(sec_['allocation'], 1, True)} in sector allocation and the dollar hedge {pct(fx['allocation'], 1, True)}. This is why the investable version moved to a country and sector rotation, where the sector bet is the strategy itself.",
  f"La sélection dans les secteurs a apporté {pct(sec_['selection'], 1, True, 'fr')} par an, mais l’absence de méga-capitalisations de croissance en 2023-24 a coûté {pct(sec_['allocation'], 1, True, 'fr')} en allocation sectorielle et la couverture du dollar {pct(fx['allocation'], 1, True, 'fr')}. C’est pour cela que la version investissable est devenue une rotation pays et secteurs, où le pari sectoriel est la stratégie elle-même.")}</div>"""),
        section("method", L(lang, "Method", "Méthode"), method),
        section("performance", "Performance", chart + "<h3>" + L(lang, "Statistics, July 2021 – June 2026", "Statistiques, juillet 2021 – juin 2026") + "</h3>" + perf_tbl),
        section("years", L(lang, "Year by year", "Année par année"), cal_tbl),
        section("signal", L(lang, "The signal", "Le signal"), f"""<div class="cols2">
<figure class="ch"><figcaption><span>{L(lang, "Rank IC at each rebalance", "IC de rang à chaque rebalancement")}</span></figcaption>{ic_svg}</figure>
<figure class="ch"><figcaption><span>{L(lang, "Average 6-month return by quintile", "Rendement moyen à 6 mois par quintile")} <small>· Q5 = {L(lang, "cheapest", "moins cher")}</small></span></figcaption>{q_svg}</figure></div>"""),
        section("attribution", "Attribution", f'<figure class="ch"><figcaption><span>{L(lang, "Equal weight: sources of active return", "Équipondéré : sources du rendement actif")} <small>· {L(lang, "a year", "par an")}</small></span></figcaption>{att_svg}</figure>'),
        section("limits", L(lang, "Limits", "Limites"), f"""<div class="prose"><ul>
<li>{L(lang, "Five years, ten rebalances, one regime: no claim of significant alpha.", "Cinq ans, dix rebalancements, un seul régime : aucune prétention d’alpha significatif.")}</li>
<li>{L(lang, "Bloomberg World stands in for MSCI World (constituents not licensed); replica correlation 0.996.", "Bloomberg World remplace MSCI World (constituants non licenciés) ; corrélation de la réplique 0,996.")}</li>
<li>{L(lang, "Current GICS sectors applied to history; no market impact in costs.", "Secteurs GICS actuels appliqués à l’historique ; pas d’impact de marché dans les coûts.")}</li></ul></div>
<div class="btns"><a class="btn" href="{'../../' if lang == 'en' else '../../../'}assets/value-developed/Investment_Note_Systematic_Value.pdf">{L(lang, "Investment note (PDF, English)", "Note d’investissement (PDF, anglais)")}</a><a class="btn" href="../../database/">{L(lang, "Data catalogue", "Catalogue des données")}</a></div>"""),
    ]
    body = phead(L(lang, "Research engine · Stocks", "Moteur de recherche · Actions"), L(lang, "Stock-level value screen", "Screen value titre par titre"),
                 L(lang, "A sector-neutral value composite on 1,990 developed-market stocks, tested over five years with three weighting schemes. It finds the names behind the pitches.",
                   "Un composite value neutre par secteur sur 1 990 actions de pays développés, testé sur cinq ans avec trois pondérations. C’est lui qui trouve les titres des pitches."),
                 f'<a href="../">{t(lang, "strategies")}</a> / value-developed')
    body += doc_layout(lang, toc, secs)
    page("strategies/value-developed/index.html", lang, L(lang, "Stock-level value screen", "Screen value titre par titre"), body, "strategies",
         L(lang, "Five-year backtest of a sector-neutral value screen on developed markets.", "Backtest sur cinq ans d’un screen value neutre par secteur sur les marchés développés."),
         scripts="<script>window.NAV=" + json.dumps(nav).replace("</", "<\\/") + ";</script>")


# ---------------------------------------------------------------- PITCHES
def build_pitch_index(lang):
    cards = []
    for s in PITCHES:
        f = s["files"]
        root = "../" if lang == "en" else "../../"
        dl = "".join(f'<a class="btn sm" href="{root}{f[k]}">{ICON_DL} {lab}</a>' for k, lab in [("pptx", "PowerPoint"), ("pdf", "PDF")] if k in f)
        cards.append(f"""<article class="card" data-item data-rating="{s['rating'].lower()}" data-region="{REGION.get(s['country'], 'other')}">
<div class="meta">{esc(s['ticker'])} · {esc(tr(lang, s['exchange']))} · {esc(tr(lang, s['country']))} · {esc(tr(lang, s['sector']))}</div>
<h3><a href="{s['slug']}/">{esc(s['name'])}</a></h3>
<div class="tags">{rating(s['rating'], lang)}<span class="tag">{esc(pf(s, lang, 'role'))}</span></div>
<p>{esc(pf(s, lang, 'headline'))}</p>
<div class="mini"><div><span>{t(lang, 'price')}</span><b>{money(s['sym'], s['price'], lang)}</b></div><div><span>{t(lang, 'target')}</span><b>{money(s['sym'], s['target'], lang)}</b></div><div><span>{t(lang, 'upside')}</span><b class="{cls_sign(s['upside'])}">{pct(s['upside'], 0, True, lang)}</b></div></div>
<div class="foot links">{dl}</div></article>""")

    def group(key, label, vals):
        return f'<div class="fgroup"><span>{label}</span><button class="fbtn" data-f="{key}" data-v="all" aria-pressed="true">{t(lang, "all")}</button>' + "".join(
            f'<button class="fbtn" data-f="{key}" data-v="{v}" aria-pressed="false">{lab}</button>' for v, lab in vals) + "</div>"
    filt = (group("rating", L(lang, "Call", "Avis"), [("overweight", t(lang, "Overweight")), ("neutral", t(lang, "Neutral")), ("underweight", t(lang, "Underweight"))]) +
            group("region", L(lang, "Region", "Région"), [("europe", "Europe"), ("americas", L(lang, "Americas", "Amériques")), ("asia", L(lang, "Asia", "Asie"))]))
    body = phead(t(lang, "pitches"), L(lang, "What the screen bought, examined one by one", "Ce que le screen a acheté, examiné titre par titre"),
                 L(lang, "Holdings of the December 2025 value portfolio, researched from company filings in October 2026. Each pitch has a twelve-slide deck in a buy-side format.",
                   "Des titres du portefeuille value de décembre 2025, étudiés à partir des publications des sociétés en octobre 2026. Chaque pitch a un deck de douze slides au format buy-side."))
    body += f"""<section class="sec"><div class="wrap" data-filter-scope>
<div class="filters">{filt}<input class="search" type="search" placeholder="{L(lang, 'Search a company, a sector…', 'Chercher une société, un secteur…')}" data-search aria-label="Search"><span class="count"></span></div>
<div class="grid">{"".join(cards)}</div><div class="empty">{L(lang, "No pitch matches these filters.", "Aucun pitch ne correspond à ces filtres.")}</div>
<p class="cap" style="margin-top:20px">{L(lang, "Prices as of 29 October 2026. Calls: Overweight above +15% upside to the base case, Neutral between −10% and +15%, Underweight below −10%. Student research, not investment advice.",
   "Cours au 29 octobre 2026. Avis : Surpondérer au-delà de +15 % de potentiel vers le scénario central, Neutre entre −10 % et +15 %, Sous-pondérer en dessous de −10 %. Travail étudiant, pas un conseil en investissement.")}</p>
</div></section>"""
    page("pitches/index.html", lang, t(lang, "pitches"), body, "pitches", L(lang, "Stock pitches with downloadable decks.", "Stock pitches avec decks téléchargeables."))


def build_pitch(s, lang):
    v = s["valuation"]
    sym = s["sym"]
    f = s["files"]
    lr = "../../"
    dl = "".join(f'<a class="btn {"primary" if k == "pptx" else ""}" href="{lr if lang == "en" else "../../../"}{f[k]}">{ICON_DL} {lab}</a>'
                 for k, lab in [("pptx", L(lang, "Download the deck (PowerPoint)", "Télécharger le deck (PowerPoint)")), ("pdf", L(lang, "PDF version", "Version PDF"))] if k in f)
    up = s["upside"]
    head = f"""<header class="pitchhead"><div class="wrap"><div>
<div class="crumbs"><a href="../">{t(lang, "pitches")}</a> / {esc(s["ticker"])}</div>
<div class="eyebrow" style="margin-top:12px">{esc(pf(s, lang, "industry"))} · {esc(tr(lang, s["country"]))} · {esc(tr(lang, s["exchange"]))}: {esc(s["ticker"])}</div>
<h1>{esc(s["name"])}</h1><p class="headline">{esc(pf(s, lang, "headline"))}</p>
<div class="tags">{rating(s["rating"], lang)}<span class="tag">{esc(pf(s, lang, "role"))}</span><span class="tag">{L(lang, "Horizon", "Horizon")} {esc(pf(s, lang, "horizon"))}</span></div>
<div class="btns" style="margin-top:22px">{dl}</div></div>
<div class="panel call"><header><span>{L(lang, "The call", "L’avis")}</span><span>{esc(price_note(s, lang))}</span></header>
<div class="row"><span>{t(lang, "price")}</span><b class="big">{money(sym, s["price"], lang)}</b></div>
<div class="row"><span>{L(lang, "Base-case value", "Valeur centrale")}<small>{esc(pf(s, lang, "method"))}</small></span><b class="big">{money(sym, s["target"], lang)}</b></div>
<div class="row"><span>{t(lang, "upside")}</span><b class="big {cls_sign(up)}">{pct(up, 0, True, lang)}</b></div>
<div class="row"><span>{L(lang, "52-week range", "Plus bas / plus haut 52 sem.")}</span><b>{money(sym, s["low52"], lang)} – {money(sym, s["high52"], lang)}</b></div></div>
</div></header>"""
    ks = pf(s, lang, "key_stats")
    stats = '<div class="stats" style="margin-top:22px">' + "".join(stat(esc(k), esc(x)) for k, x in ks) + "</div>"
    thesis = '<div class="numlist">' + "".join(f'<div class="box"><h4>{esc(a)}</h4><p>{esc(b)}</p></div>' for a, b in pf(s, lang, "thesis")) + "</div>"
    stories = pf(s, lang, "stories")
    inp = lambda r: '<span style="white-space:nowrap">' + esc(fr_inputs(r["inputs"]) if lang == "fr" else r["inputs"]) + "</span>"
    sc_rows = [[f'<b>{t(lang, r["name"])}</b>', inp(r), money(sym, r["value"], lang),
                f'<span class="{cls_sign(r["upside"])}">{pct(r["upside"], 0, True, lang)}</span>', esc(stories[i])] for i, r in enumerate(s["scenarios_out"])]
    sc_tbl = tbl([L(lang, "Scenario", "Scénario"), L(lang, "Inputs", "Hypothèses"), L(lang, "Value / share", "Valeur / action"), L(lang, "vs price", "vs cours"),
                  L(lang, "What has to happen", "Ce qu’il faut voir")], sc_rows, num_cols=(2, 3), row_cls=lambda i, r: "hl" if i == 1 else "")
    ff = svg_football(s, lang, dict(range52=L(lang, "52-week range", "Plage 52 semaines"), scen=L(lang, "Scenarios (bear → bull)", "Scénarios (pessimiste → optimiste)"),
                                    cons=L(lang, "Consensus target", "Objectif du consensus"), price=t(lang, "price"), base=L(lang, "Base case", "Scénario central")))
    val = f"""<div class="prose"><p><b>{esc(pf(s, lang, "method"))}.</b> {esc(pf(s, lang, "explain"))}</p></div>{sc_tbl}
<figure class="ch" style="margin-top:18px"><figcaption><span>{L(lang, "Valuation range", "Fourchette de valorisation")}</span></figcaption>{ff}</figure>"""
    cat = '<ul class="timeline">' + "".join(f'<li><div class="d">{esc(d)}</div><p>{esc(x)}</p></li>' for d, x in pf(s, lang, "catalysts")) + "</ul>"
    trig = ('<div class="sell"><b>' + L(lang, "We change the call if", "Nous changeons d’avis si") + "</b><ul>" +
            "".join(f"<li>{esc(x)}</li>" for x in pf(s, lang, "triggers")) + "</ul></div>")
    fct = s["facts"]
    cc, scode = COUNTRY_CODE.get(s["country"]), SECTOR_CODE.get(s["sector"])
    strat = f"""<div class="cols2">
<div class="box accent"><div class="k">{L(lang, "Value rotation (ETF)", "Rotation value (ETF)")}</div><h4 style="margin-top:6px">{esc(tr(lang, s["country"]))} · {esc(tr(lang, s["sector"]))}</h4>
<p>{L(lang, "This name belongs to the country sleeve and to the sector sleeve of the same names in the rotation universe. When the rotation holds either, this pitch is a way to express the view in a single stock.", "Ce titre appartient à la poche pays et à la poche secteur correspondantes de l’univers de la rotation. Quand la rotation détient l’une ou l’autre, ce pitch permet d’exprimer la vue en action individuelle.")}</p>
<p style="margin-top:10px"><a href="{lr if lang == 'en' else '../../'}strategies/value-rotation/#universe">{L(lang, "See the universe", "Voir l’univers")} →</a></p></div>
<div class="box accent"><div class="k">{L(lang, "Stock-level screen", "Screen titres")}</div><h4 style="margin-top:6px">{L(lang, "Rank", "Rang")} {fct["sector_rank"]} {t(lang, "of")} {fct["sector_n"]} · score {num(fct["score"], 2, lang)}</h4>
<p>{L(lang, f"Value score at the December 2025 rebalance, within {fct['sector']}, on accounts for the fiscal year to {fct['fy_used'][:7]}.", f"Score value au rebalancement de décembre 2025, au sein du secteur {tr('fr', fct['sector'])}, sur les comptes de l’exercice clos en {fct['fy_used'][:7]}.")}</p>
<p style="margin-top:10px"><a href="{lr if lang == 'en' else '../../'}strategies/value-developed/">{L(lang, "See the screen", "Voir le screen")} →</a></p></div></div>"""
    toc = [("summary", L(lang, "In one paragraph", "En un paragraphe")), ("thesis", L(lang, "Thesis", "Thèse")), ("valuation", L(lang, "Valuation", "Valorisation")),
           ("catalysts", L(lang, "Catalysts and risks", "Catalyseurs et risques")), ("strategies", L(lang, "In our strategies", "Dans nos stratégies")),
           ("deck", "Deck")]
    secs = [
        section("summary", L(lang, "In one paragraph", "En un paragraphe"), f'<div class="prose"><p style="font-size:19px">{esc(pf(s, lang, "one_liner"))}</p></div>{stats}'),
        section("thesis", L(lang, "Investment thesis", "Thèse d’investissement"), thesis),
        section("valuation", L(lang, "Valuation", "Valorisation"), val),
        section("catalysts", L(lang, "Catalysts and risks", "Catalyseurs et risques"), f'<div class="cols2" style="align-items:start"><div>{cat}</div>{trig}</div>'),
        section("strategies", L(lang, "In our strategies", "Dans nos stratégies"), strat),
        section("deck", "Deck", f'<div class="box" style="display:flex;justify-content:space-between;align-items:center;gap:18px;flex-wrap:wrap"><div><h4>{L(lang, "The full pitch", "Le pitch complet")}</h4><p>{L(lang, "Twelve slides: summary, company, macro, why the screen picked it, track record, financials, variant perception, valuation, catalysts, risks and sources.", "Douze slides : synthèse, société, macro, pourquoi le screen l’a choisi, historique, financiers, variant perception, valorisation, catalyseurs, risques et sources.")}</p></div><div class="btns">{dl}</div></div>'),
    ]
    body = head + doc_layout(lang, toc, secs) + f'<div class="wrap"><p class="cap" style="margin:8px 0 48px">{L(lang, "Student research for educational and interview purposes. Not investment advice.", "Travail de recherche étudiant à visée pédagogique et de préparation aux entretiens. Pas un conseil en investissement.")}</p></div>'
    page(f"pitches/{s['slug']}/index.html", lang, s["name"], body, "pitches", pf(s, lang, "headline"))


# ---------------------------------------------------------------- RESEARCH
def research_notes(lang):
    out = []
    for p in sorted((CONTENT / lang / "research").glob("*.md"), reverse=True):
        meta, text = front(p)
        out.append(dict(slug=p.stem, title=meta.get("title", p.stem), date=meta.get("date", ""), summary=meta.get("summary", ""), text=text))
    return out


def build_research(lang):
    notes = research_notes(lang)
    items = "".join(f'<a class="noteitem" href="{n["slug"]}/"><span class="d">{esc(n["date"])}</span><div><h3>{esc(n["title"])}</h3><p>{esc(n["summary"])}</p></div><span class="go">{t(lang, "read")} →</span></a>' for n in notes)
    body = phead(t(lang, "research"), L(lang, "Findings, written up when they happen", "Des découvertes, écrites quand elles arrivent"),
                 L(lang, "Short notes on what the work revealed: data errors caught, construction choices tested, lessons from the pitches.",
                   "De courtes notes sur ce que le travail a révélé : erreurs de données détectées, choix de construction testés, leçons des pitches."))
    body += f'<section class="sec"><div class="wrap"><div class="notes">{items}</div></div></section>'
    page("research/index.html", lang, t(lang, "research"), body, "research", L(lang, "Research notes.", "Notes de recherche."))
    for n in notes:
        body = phead(n["date"], esc(n["title"]), esc(n["summary"]), f'<a href="../">{t(lang, "research")}</a>')
        body += f'<section class="sec"><div class="wrap"><article class="prose">{md(n["text"])}</article><div class="btns" style="margin-top:32px"><a class="btn" href="../">← {t(lang, "research")}</a></div></div></section>'
        page(f"research/{n['slug']}/index.html", lang, n["title"], body, "research", n["summary"])


def simple_page(name, lang, active, eyebrow, lede):
    meta, text = front(CONTENT / lang / f"{name}.md")
    m = re.match(r"^# (.*)$", text, re.M)
    title = m.group(1) if m else meta.get("title", name)
    body = phead(eyebrow, esc(title), lede) + f'<section class="sec"><div class="wrap"><article class="prose">{md(strip_h1(text))}</article></div></section>'
    page(f"{name}/index.html", lang, meta.get("title", title), body, active, lede)


# ---------------------------------------------------------------- DATABASE
DATASETS = [
    ("Index compositions", "Compositions d’indices", "BDS · INDX_MWEIGHT_HIST + END_DATE_OVERRIDE", "10 dates, 2021-2025", "4,117 tickers", "4 117 titres", "Stock screen", "Screen titres"),
    ("Weekly prices", "Prix hebdomadaires", "BDH · PX_LAST, Currency = EUR", "2016-2026", "986,418 obs.", "986 418 obs.", "Stock screen", "Screen titres"),
    ("Dividends", "Dividendes", "BDS · DVD_HIST_ALL", "2016-2026", "44,198 records", "44 198 lignes", "Stock screen", "Screen titres"),
    ("Annual fundamentals", "Fondamentaux annuels", "BDH · 8 fields, FILING_STATUS = OR, EUR", "FY 2015-2025", "1,967 tickers", "1 967 titres", "Stock screen", "Screen titres"),
    ("Rebalance snapshots", "Instantanés aux rebalancements", "BDH · CUR_MKT_CAP, EQY_FREE_FLOAT_PCT, TURNOVER", "10 dates", "1,989 tickers", "1 989 titres", "Stock screen", "Screen titres"),
    ("Country and sector valuation", "Valorisation pays et secteurs", "BDH monthly · PX_LAST, PE_RATIO, PX_TO_BOOK_RATIO, EQY_DVD_YLD_12M", "2000-2026", "25 indices + fallbacks", "25 indices + secours", "Value rotation", "Rotation value"),
    ("Multi-asset total returns", "Rendements totaux multi-actifs", "BDH monthly · PX_LAST, Currency = EUR", "2000-2026", "14 + 14 indices", "14 + 14 indices", "Trend · Value rotation", "Trend · Rotation value"),
    ("Market series", "Séries de marché", "BDH · MSDEWIN, EURUSD, ESTRON, EUR003M", "2000-2026", "7 series", "7 séries", "All", "Toutes"),
    ("Factor returns", "Rendements des facteurs", "Kenneth French Data Library", "2016-2026", "6 factors", "6 facteurs", "Stock screen", "Screen titres"),
]
FIELDS = [
    ("INDX_MWEIGHT_HIST", "Index members and weights at a past date", "Membres et poids d’un indice à une date passée", "BDS",
     "Default is today's list: always pass END_DATE_OVERRIDE, or the backtest is survivorship-biased.", "Par défaut, c’est la liste du jour : toujours passer END_DATE_OVERRIDE, sinon le backtest a un biais du survivant."),
    ("PX_LAST", "Last price or index level", "Dernier cours ou niveau d’indice", "BDH",
     "For stocks it came back adjusted for dividends: already a total-return series. Adding dividends double-counts ~2% a year.", "Pour les actions, il est revenu ajusté des dividendes : c’est déjà une série de rendement total. Ajouter les dividendes compte ~2 % par an deux fois."),
    ("PE_RATIO", "Trailing price-to-earnings of an index", "PER passé d’un indice", "BDH", "Negative or missing when aggregate earnings are negative: use E/P, not P/E, in the score.", "Négatif ou manquant quand les bénéfices agrégés sont négatifs : utiliser E/P plutôt que P/E dans le score."),
    ("PX_TO_BOOK_RATIO", "Price-to-book", "Cours / valeur comptable", "BDH", "Structurally different across sectors: compare each line with its own history.", "Structurellement différent entre secteurs : comparer chaque ligne à son propre historique."),
    ("EQY_DVD_YLD_12M", "Trailing 12-month dividend yield, %", "Rendement du dividende sur 12 mois, %", "BDH", "In percent, not decimal.", "En pourcentage, pas en décimal."),
    ("DVD_HIST_ALL", "Dividend history", "Historique des dividendes", "BDS", "Amount in payment currency, which the extract does not store.", "Montant dans la devise de paiement, que l’extraction ne stocke pas."),
    ("CNTRY_OF_RISK", "Country of economic risk", "Pays de risque économique", "BDP", "Can differ from domicile (Irish-domiciled US groups).", "Peut différer du pays de domicile (groupes américains domiciliés en Irlande)."),
    ("GICS_SECTOR_NAME", "GICS sector", "Secteur GICS", "BDP", "Current classification only, applied to the whole history.", "Classification actuelle seulement, appliquée à tout l’historique."),
    ("FILING_STATUS = OR", "Originally reported figures", "Chiffres publiés à l’origine", "override", "Avoids restated numbers that were not known at the time.", "Évite les chiffres retraités qui n’étaient pas connus à l’époque."),
    ("ANNOUNCEMENT_DT", "Results announcement date", "Date de publication des résultats", "BDH", "A fiscal year is never used before this date.", "Un exercice n’est jamais utilisé avant cette date."),
    ("CUR_MKT_CAP", "Market capitalisation", "Capitalisation boursière", "BDH", "Company-level total: share classes do not create false discounts.", "Total au niveau société : les catégories d’actions ne créent pas de fausse décote."),
    ("Currency = EUR", "Override: convert at Bloomberg rates", "Override : conversion aux taux Bloomberg", "override", "Returns in EUR include currency moves: what a euro investor earns unhedged.", "Les rendements en EUR incluent le change : ce que gagne un investisseur en euros non couvert."),
    ("MSDEWIN Index", "MSCI World Net TR, EUR", "MSCI World Net TR, EUR", "BDH", "Net of withholding tax: compare with net, not gross, returns.", "Net de retenue à la source : comparer avec des rendements nets, pas bruts."),
]


def build_database(lang):
    cov = VALUE["coverage"]
    cov_rows = [[c[0], num(int(c[1]), 0, lang), num(int(c[3]), 0, lang), pct(float(c[4]) / 100, 1, lang=lang), num(int(c[6]), 0, lang)] for c in cov[1:]]
    cov_tbl = tbl([L(lang, "Date", "Date"), L(lang, "Index members", "Membres de l’indice"), L(lang, "Developed", "Développés"), L(lang, "DM weight", "Poids DM"), L(lang, "Eligible", "Éligibles")], cov_rows, num_cols=range(1, 5))
    ds_tbl = tbl([L(lang, "Dataset", "Jeu de données"), L(lang, "Retrieval", "Extraction"), L(lang, "Period", "Période"), L(lang, "Coverage", "Couverture"), L(lang, "Used by", "Utilisé par")],
                 [[f"<b>{esc(L(lang, a, b))}</b>", f'<span class="mono" style="font-size:13.5px">{esc(c if lang == "en" else c.replace("monthly", "mensuel").replace("8 fields", "8 champs"))}</span>', esc(d), esc(L(lang, e, f)), esc(L(lang, g, h))] for a, b, c, d, e, f, g, h in DATASETS])
    fld = f"""<div data-filter-scope><div class="filters"><input class="search" type="search" placeholder="{L(lang, 'Search a field or a pitfall…', 'Chercher un champ ou un piège…')}" data-search aria-label="Search"><span class="count"></span></div>
<div class="tbl-wrap"><table class="t"><thead><tr><th>{L(lang, "Field", "Champ")}</th><th>{L(lang, "Meaning", "Signification")}</th><th>{L(lang, "Function", "Fonction")}</th><th>{L(lang, "Pitfall", "Piège")}</th></tr></thead><tbody>
{"".join(f'<tr data-item><td><span class="mono">{esc(a)}</span></td><td>{esc(L(lang, b, c))}</td><td>{esc(d)}</td><td>{esc(L(lang, e, f))}</td></tr>' for a, b, c, d, e, f in FIELDS)}
</tbody></table></div><div class="empty">—</div></div>"""
    meta, bias = front(CONTENT / lang / "bias_checklist.md")
    brows = []
    for line in strip_h1(bias).splitlines():
        c = [x.strip() for x in line.strip().strip("|").split("|")]
        if not line.startswith("|") or len(c) < 5 or c[0] in ("#", "") or set(c[0]) <= set("-: "):
            continue
        st = c[4].replace("**", "")
        ok = st.startswith("OK") or st.startswith("Fixed") or st.startswith("Corrigé")
        head_, _, rest = st.partition(" — ")
        head_ = head_.split(" (")[0]
        brows.append([c[0], f"<b>{md_inline(c[1])}</b>", md_inline(c[2]),
                      f'<span class="rating {"r-ow" if ok else "r-n"}" style="white-space:nowrap">{esc(head_)}</span>' + (f'<small style="display:block;margin-top:4px">{esc(rest)}</small>' if rest else "")])
    bias_tbl = tbl(["#", L(lang, "Risk", "Risque"), L(lang, "Control", "Contrôle"), L(lang, "Status", "Statut")], brows)
    toc = [("overview", L(lang, "Overview", "Vue d’ensemble")), ("datasets", L(lang, "Datasets", "Jeux de données")), ("fields", L(lang, "Bloomberg fields", "Champs Bloomberg")),
           ("coverage", L(lang, "Coverage", "Couverture")), ("bias", L(lang, "Anti-bias checklist", "Checklist anti-biais")), ("licence", L(lang, "Licence", "Licence"))]
    secs = [
        section("overview", L(lang, "Overview", "Vue d’ensemble"), f"""<div class="stats">
{stat(L(lang, "Securities", "Titres"), num(4117, 0, lang), L(lang, "union of 10 compositions", "union de 10 compositions"))}{stat(L(lang, "Developed", "Développés"), num(1990, 0, lang), L(lang, "24 countries", "24 pays"))}
{stat(L(lang, "Weekly prices", "Prix hebdo"), "986k", L(lang, "observations", "observations"))}{stat(L(lang, "Indices for the ETF strategies", "Indices des stratégies ETF"), "53", L(lang, "monthly, 2000-2026", "mensuel, 2000-2026"))}</div>
<div class="callout amber"><b>{L(lang, "What this page is.", "Ce qu’est cette page.")}</b> {L(lang, "A catalogue of the data behind every result: what was extracted, how, and with which settings. The raw data stay offline: Bloomberg terms do not allow redistribution, and no data file is downloadable from this site.", "Un catalogue des données derrière chaque résultat : ce qui a été extrait, comment, et avec quels paramètres. Les données brutes restent hors ligne : les conditions de Bloomberg n’autorisent pas leur redistribution, et aucun fichier de données n’est téléchargeable sur ce site.")}</div>"""),
        section("datasets", L(lang, "Datasets", "Jeux de données"), ds_tbl),
        section("fields", L(lang, "Bloomberg fields", "Champs Bloomberg"), fld, L(lang, "Every field and override used, with the trap each one hides.", "Chaque champ et override utilisé, avec le piège qu’il cache.")),
        section("coverage", L(lang, "Coverage", "Couverture"), cov_tbl, L(lang, "Stock screen universe at each rebalance.", "Univers du screen titres à chaque rebalancement.")),
        section("bias", L(lang, "Anti-bias checklist", "Checklist anti-biais"), bias_tbl, L(lang, "Written before the backtest was interpreted. Rule one: if a result looks good, check survivorship, look-ahead and units first.", "Écrite avant d’interpréter le backtest. Règle numéro un : si un résultat paraît bon, vérifier d’abord le biais du survivant, le look-ahead et les unités.")),
        section("licence", L(lang, "Licence", "Licence"), f'<div class="prose"><p>{L(lang, "Bloomberg and MSCI data are licensed to SKEMA Business School for teaching. This site publishes methodology, field definitions, coverage counts and aggregated results only.", "Les données Bloomberg et MSCI sont licenciées à SKEMA Business School pour l’enseignement. Ce site ne publie que la méthode, la définition des champs, des statistiques de couverture et des résultats agrégés.")}</p></div>'),
    ]
    body = phead(t(lang, "database"), L(lang, "The data behind the work", "Les données derrière le travail"),
                 L(lang, "Every dataset, every Bloomberg field and override, the coverage at each date and the checks that cleaned it.",
                   "Chaque jeu de données, chaque champ et override Bloomberg, la couverture à chaque date et les contrôles qui les ont nettoyés."))
    body += doc_layout(lang, toc, secs)
    page("database/index.html", lang, t(lang, "database"), body, "database", L(lang, "Data catalogue.", "Catalogue des données."))


# ---------------------------------------------------------------- MAIN
def clean_docs():
    """Remove generated pages and files that must not be published any more (note PDFs, old pages)."""
    for p in (DOCS / "assets/pitches").glob("*_note.pdf"):
        p.unlink()
    for d in ["fr", "pitches", "research", "strategies", "database", "journal", "methodology", "about", "static"]:
        if (DOCS / d).exists():
            shutil.rmtree(DOCS / d)
    for f in ["home_template.html"]:
        if (DOCS / f).exists():
            (DOCS / f).unlink()


def main():
    clean_docs()
    (DOCS / "assets").mkdir(parents=True, exist_ok=True)
    for f in ("site.css", "site.js"):
        shutil.copy(HERE / "static" / f, DOCS / "assets" / f)
    (DOCS / ".nojekyll").touch()
    for lang in LANGS:
        build_home(lang)
        build_strategies(lang)
        build_value_rotation(lang)
        build_trend(lang)
        build_horus(lang)
        build_value_screen(lang)
        build_pitch_index(lang)
        for s in PITCHES:
            build_pitch(s, lang)
        build_research(lang)
        build_database(lang)
        simple_page("journal", lang, "", t(lang, "journal"), L(lang, "Decisions and milestones, dated.", "Décisions et étapes, datées."))
        simple_page("methodology", lang, "", t(lang, "methodology"), L(lang, "Where the data come from and the rules every result respects.", "D’où viennent les données et les règles que chaque résultat respecte."))
        simple_page("about", lang, "about", t(lang, "about"), L(lang, "Who is behind this ledger and why it exists.", "Qui tient ce carnet et pourquoi il existe."))
    print("site built in", DOCS)


if __name__ == "__main__":
    main()
