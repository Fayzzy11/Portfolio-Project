"""Build the Thoth Ledger site (English at docs/, French at docs/fr/) for GitHub Pages.

Usage (from the repository root):
    python site/build_site.py

Reads   site/data/*.json         results and pitch content (English) + pitches_fr.json (French fields)
        site/content/{en,fr}/    hand-written pages in Markdown (about, journal, methodology, research notes, checklist)
        site/static/             site.css and site.js, copied to docs/assets/
Writes every page in both languages.
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
ETF = json.loads((DATA / "etf_strategies.json").read_text())
RCLS = {"Overweight": "r-ow", "Neutral": "r-n", "Underweight": "r-uw", "Sell": "r-uw", "Buy": "r-ow"}
REGION = {"France": "europe", "United States": "americas", "Japan": "asia", "Hong Kong": "asia"}
for s in PITCHES:
    s["slug"] = slugify(f"{s['ticker']}-{s['name']}")
    stem = f"{s['code']}_{re.sub(r'[^A-Za-z0-9]+', '_', s['name']).strip('_')}"
    s["files"] = {k: f"assets/pitches/{stem}{suf}" for k, suf in [("pptx", "_pitch.pptx"), ("pdf", "_pitch.pdf"),
                                                                  ("pptx_fr", "_pitch_FR.pptx"), ("pdf_fr", "_pitch_FR.pdf")]
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
  <h1>{L(lang, "Rules written before results. <em>Every number traceable.</em>", "Des règles écrites avant les résultats. <em>Chaque chiffre traçable.</em>")}</h1>
  <p class="lede">{L(lang, "I am Noah Doose, an MSc Financial Markets & Investments student at SKEMA and a CFA Level II candidate. Thoth Ledger is my research ledger: strategies anyone can replicate with ETFs, stock pitches that test them name by name, and the data behind every result.",
                     "Je suis Noah Doose, étudiant en MSc Financial Markets & Investments à SKEMA et candidat au CFA niveau II. Thoth Ledger est mon carnet de recherche : des stratégies réplicables par tous avec des ETF, des stock pitches qui les testent titre par titre, et les données derrière chaque résultat.")}</p>
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
 <div class="shead"><h2>{L(lang, "Two strategies, one discipline", "Deux stratégies, une même discipline")}</h2>
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
    v = ETF["value"]
    return f"""<div class="grid" style="grid-template-columns:repeat(auto-fit,minmax(320px,1fr))">
 <article class="card"><div class="tags"><span class="tag green">{L(lang, "Equities · ETF", "Actions · ETF")}</span><span class="tag">{L(lang, "Monthly · 8 ETF", "Mensuel · 8 ETF")}</span></div>
  <h3><a href="{lr}strategies/value-rotation/">{L(lang, "Global Value Rotation", "Rotation Value mondiale")}</a></h3>
  <p>{L(lang, "Value decides what to hold: the cheapest developed countries and sectors against their own history. A risk rule decides how much: 100%, or 50% when the market turns. ETF core of a core-satellite value strategy.", "Le value décide quoi détenir : les pays et secteurs développés les moins chers par rapport à leur propre historique. Une règle de risque décide combien : 100 %, ou 50 % quand le marché se retourne. Cœur ETF d’une stratégie value cœur-satellite.")}</p>
  <div class="mini"><div><span>CAGR</span><b>{pct(v["stats"]["cagr"], 1, lang=lang)}</b></div><div><span>Sharpe</span><b>{num(v["stats"]["sharpe"], 2, lang)}</b></div><div><span>Max DD</span><b>{pct(v["stats"]["mdd"], 0, lang=lang)}</b></div></div>
  <div class="foot"><span>{esc(v["bench_name"].replace(" Net EUR", ""))}{L(lang, ":", " :")} {pct(v["bench_stats"]["cagr"], 1, lang=lang)} · {num(v["bench_stats"]["sharpe"], 2, lang)} · {pct(v["bench_stats"]["mdd"], 0, lang=lang)} · 2006-2026</span><b>→</b></div></article>
 <article class="card"><div class="tags"><span class="tag gold">Horus AM</span><span class="tag">{L(lang, "Yearly · 4 ETF", "Annuel · 4 ETF")}</span></div>
  <h3><a href="{lr}strategies/horus-smart-beta/">Horus Smart Beta 60/40</a></h3>
  <p>{L(lang, "A permanent 60/40 whose equity half holds the two ETFs most exposed to size, growth and momentum, chosen each January.", "Un 60/40 permanent dont la poche actions détient les deux ETF les plus exposés à la taille, la croissance et le momentum, choisis chaque janvier.")}</p>
  <div class="mini"><div><span>CAGR</span><b>{pct(hp["cagr"], 1, lang=lang)}</b></div><div><span>Sharpe</span><b>{num(hp["sharpe"], 2, lang)}</b></div><div><span>Max DD</span><b>{pct(hp["mdd"], 0, lang=lang)}</b></div></div>
  <div class="foot"><span>60/40{L(lang, ":", " :")} {pct(HS["b"]["cagr"], 1, lang=lang)} · 2007-2026 · USD</span><b>→</b></div></article>
</div>"""


# ---------------------------------------------------------------- STRATEGIES INDEX
def build_strategies(lang):
    body = phead(t(lang, "strategies"), L(lang, "Strategies you can hold with ETFs", "Des stratégies que l'on peut détenir avec des ETF"),
                 L(lang, "Two rules-based strategies, each implementable with UCITS ETFs and rebalanced on a fixed calendar, plus the stock-level research engine that feeds the pitches.",
                   "Deux stratégies systématiques, chacune réplicable avec des ETF UCITS et rebalancée à date fixe, plus le moteur de recherche titre par titre qui alimente les pitches."))
    body += f'<section class="sec"><div class="wrap">{strategy_cards(lang, "../")}<p class="cap" style="margin-top:16px"><a href="../factsheets/">' + L(lang, "Monthly factsheets, all issues", "Factsheets mensuelles, tous les numéros") + ' →</a></p></div></section>'
    body += f"""<section class="sec alt"><div class="wrap"><div class="shead"><h2>{L(lang, "Research behind the strategies", "La recherche derrière les stratégies")}</h2></div>
<div class="grid">
 <article class="card"><div class="meta">{L(lang, "Stock level · 1,990 developed-market stocks · 2021-2026", "Titres · 1 990 actions de pays développés · 2021-2026")}</div>
  <h3><a href="value-developed/">{L(lang, "Stock-level value screen", "Screen value titre par titre")}</a></h3>
  <p>{L(lang, "The research engine behind the value rotation and the pitches: sector-neutral value composite, 50 names, three weighting schemes.", "Le moteur de recherche derrière la rotation value et les pitches : composite value neutre par secteur, 50 titres, trois pondérations.")}</p>
  <div class="foot"><span>{L(lang, "Equal weight", "Équipondéré")} {pct(H["EW"]["ann_return"], 1, lang=lang)} · IC {num(IC_MEAN, 3, lang)}</span><b>→</b></div></article>
</div></div></section>"""
    page("strategies/index.html", lang, t(lang, "strategies"), body, "strategies",
         L(lang, "ETF-replicable strategies by Noah Doose.", "Stratégies réplicables en ETF de Noah Doose."))



VAR_FR = {
    "V1 Rules (validated 30 Oct)": "V1 Règles (validées le 30/10)", "V6 Rules + market trend filter": "V6 Règles + filtre de tendance du marché",
    "VB 50% MSCI World + 50% V6": "VB 50 % MSCI World + 50 % V6", "V3 Cap-weighted world, value tilt": "V3 Monde pondéré par les capi, incliné value",
    "V4b Per-line trend filter": "V4b Filtre de tendance ligne par ligne", "V4c Buffer + market trend filter (official)": "V4c Tampon + filtre de tendance du marché (officielle)",
    "V4d 12 tranches + market trend filter": "V4d 12 tranches + filtre de tendance", "V4e 12 tranches + filter, bonds risk-off": "V4e 12 tranches + filtre, refuge obligataire", "V4c Buffer + 100% cash trend filter": "V4c Tampon + filtre de tendance 100 % cash", "V5 3 sectors, 50% de-risking, fast re-entry": "V5 3 secteurs, réduction à 50 %, retour rapide", "V7 ETF core: V4c selection + 50% de-risking (official)": "V7 Cœur ETF : sélection V4c + réduction à 50 % (officielle)", "MSCI World Value Net EUR": "MSCI World Value Net EUR",
    "MSCI World Net EUR": "MSCI World Net EUR", "MSCI World Value Net EUR": "MSCI World Value Net EUR"}
LINE_NAMES = {**{"C_" + c: nm for c, nm, *_ in COUNTRIES}, **{"S_" + c: nm for c, nm, _ in SECTORS}}
TREND_NAMES = {"EQ_US": ("US equities", "Actions américaines"), "EQ_EMU": ("Euro area equities", "Actions zone euro"), "EQ_JP": ("Japanese equities", "Actions japonaises"),
               "EQ_EM": ("Emerging equities", "Actions émergentes"), "BD_UST": ("US Treasuries", "Trésor américain"), "BD_EGB": ("Euro government bonds", "Obligations d'État zone euro"),
               "BD_GAGG": ("Global aggregate bonds", "Obligations mondiales"), "BD_UCRP": ("US IG credit", "Crédit IG américain"), "CM_GOLD": ("Gold", "Or"),
               "CM_SILV": ("Silver", "Argent"), "CM_BCOM": ("Broad commodities", "Matières premières"), "CM_WTI": ("Crude oil", "Pétrole"),
               "CM_CU": ("Copper", "Cuivre"), "CM_AGRI": ("Agriculture", "Agriculture")}


def variants_table(lang, keys):
    rows = []
    for v in ETF["variants"]:
        hl = "official" in v["name"]
        nm = VAR_FR.get(v["name"], v["name"]) if lang == "fr" else v["name"]
        tag = "" if v.get("kind") != "post" else L(lang, " · tested after the data", " · testée après les données")
        rows.append([(("<b>" + esc(nm) + "</b>") if hl else esc(nm)) + (f"<small>{tag}</small>" if tag else ""), pct(v["cagr"], 1, lang=lang), num(v["sharpe"], 2, lang), pct(v["mdd"], 0, lang=lang),
                     f'{pct(v["design_cagr"], 1, lang=lang)} · {num(v["design_sharpe"], 2, lang)}', f'{pct(v["valid_cagr"], 1, lang=lang)} · {num(v["valid_sharpe"], 2, lang)}'])
    return tbl([L(lang, "Version", "Version"), "CAGR", "Sharpe", "Max DD", L(lang, "2006-2015 (CAGR · Sharpe)", "2006-2015 (CAGR · Sharpe)"),
                L(lang, "2016-2026 (CAGR · Sharpe)", "2016-2026 (CAGR · Sharpe)")], rows, num_cols=(1, 2, 3, 4, 5),
               row_cls=lambda i, r: "hl" if "<b>" in r[0] else ("bench" if r[0].startswith("MSCI") else ""))


def results_block(kind, lang):
    d = ETF[kind]
    st, bs = d["stats"], d["bench_stats"]
    main = L(lang, "Global Value Rotation", "Rotation Value mondiale") if kind == "value" else L(lang, "Multi-Asset Trend", "Trend multi-actifs")
    bn = d.get("bench_name", "MSCI World Net EUR")
    b2n = d.get("bench2_name", "60/40 EUR")
    series = {main: d["nav"], bn: d["bench"]}
    colors = {main: "--accent", bn: "--bench"}
    bench_names = [bn]
    if "bench2" in d:
        series[b2n] = d["bench2"]
        colors[b2n] = "--s2"
        bench_names.append(b2n)
    nav = {"dates": d["dates"], "series": series, "colors": colors, "bench": bench_names, "main": main}
    chart = nav_chart("navchart", L(lang, "Growth of 100 euros", "Croissance de 100 euros"), L(lang, "monthly, EUR, net of costs and ETF fees", "mensuel, EUR, net de frais et de frais d'ETF"),
                      [("5", "5Y" if lang == "en" else "5A"), ("10", "10Y" if lang == "en" else "10A"), ("all", L(lang, "All", "Tout"))],
                      [("nav", L(lang, "Growth", "Croissance")), ("dd", "Drawdown")], list(series))
    cards = f"""<div class="stats" style="margin-bottom:18px">
 {stat("CAGR", pct(st["cagr"], 1, lang=lang), bn.replace(" Net EUR", "") + " " + pct(bs["cagr"], 1, lang=lang))}
 {stat(L(lang, "Volatility", "Volatilité"), pct(st["vol"], 1, lang=lang), bn.replace(" Net EUR", "") + " " + pct(bs["vol"], 1, lang=lang))}
 {stat("Sharpe", num(st["sharpe"], 2, lang), bn.replace(" Net EUR", "") + " " + num(bs["sharpe"], 2, lang))}
 {stat(L(lang, "Max drawdown", "Perte maximale"), pct(st["mdd"], 1, lang=lang), bn.replace(" Net EUR", "") + " " + pct(bs["mdd"], 1, lang=lang))}
</div>"""
    srow = [[L(lang, "Annual return (CAGR)", "Rendement annuel (CAGR)"), pct(st["cagr"], 1, lang=lang), pct(bs["cagr"], 1, lang=lang)],
            [L(lang, "Volatility", "Volatilité"), pct(st["vol"], 1, lang=lang), pct(bs["vol"], 1, lang=lang)],
            ["Sharpe", num(st["sharpe"], 2, lang), num(bs["sharpe"], 2, lang)],
            [L(lang, "Maximum drawdown", "Perte maximale"), f'{pct(st["mdd"], 1, lang=lang)} ({st["mdd_date"]})', f'{pct(bs["mdd"], 1, lang=lang)} ({bs["mdd_date"]})'],
            [L(lang, "Beta / correlation vs benchmark", "Bêta / corrélation vs indice"), f'{num(st["beta"], 2, lang)} / {num(st["corr"], 2, lang)}', "1 / 1"],
            [L(lang, "Tracking error", "Tracking error"), pct(st["te"], 1, lang=lang), "—"],
            [L(lang, "Positive months", "Mois positifs"), pct(st["pos_months"], 0, lang=lang), pct(bs["pos_months"], 0, lang=lang)],
            [L(lang, "Turnover (two-way, a year)", "Rotation (aller-retour, par an)"), pct(d["turnover"], 0, lang=lang), "—"]]
    head = [L(lang, "Statistic", "Statistique"), main, bn]
    if "bench2" in d:
        b2 = d["bench2_stats"]
        extra = [pct(b2["cagr"], 1, lang=lang), pct(b2["vol"], 1, lang=lang), num(b2["sharpe"], 2, lang), f'{pct(b2["mdd"], 1, lang=lang)} ({b2["mdd_date"]})', "—", "—", pct(b2["pos_months"], 0, lang=lang), "—"]
        srow = [r + [x] for r, x in zip(srow, extra)]
        head.append(b2n)
    stats_tbl = tbl(head, srow, num_cols=tuple(range(1, len(head))))
    years = sorted(d["calendar"], key=int)
    cal = svg_columns(years, [d["calendar"][y] * 100 for y in years], lambda v: num(v, 0, lang), w=980, h=260,
                      series2=[d["bench_calendar"][y] * 100 for y in years], names=[main, bn])
    period = f'{month_name(d["dates"][0], lang)} – {month_name(d["dates"][-1], lang)}'
    html = (cards + chart + f'<h3>{L(lang, "Statistics", "Statistiques")}, {period}</h3>' + stats_tbl +
            f'<p class="cap">{L(lang, "Backtest on index total returns in EUR (ETF proxies), unhedged, net of costs: 0.10% per unit of turnover and 0.25% a year of ETF fees, deducted monthly. Cash earns the euro money-market rate. Sharpe: (CAGR − average cash rate) / volatility. Hypothetical results.", "Backtest sur les rendements totaux des indices en EUR (proxys des ETF), non couvert, net de frais : 0,10 % par unité de rotation et 0,25 % par an de frais d’ETF, déduits chaque mois. Le cash rapporte le taux monétaire en euro. Sharpe : (CAGR − taux monétaire moyen) / volatilité. Résultats hypothétiques.")}</p>'
            f'<h3>{L(lang, "Year by year", "Année par année")}</h3><figure class="ch"><figcaption><span>{L(lang, "Calendar-year returns", "Rendements par année civile")} <small>· %</small></span></figcaption>{cal}</figure>')
    nav_json = json.dumps(nav).replace("</", "<\\/")
    return html, "<script>window.NAV=" + nav_json + ";</script>"


# ---------------------------------------------------------------- VALUE ROTATION
def status_block(lang):
    return f"""<div class="status"><span class="dot"></span><div><b>{L(lang, "Backtest in progress", "Backtest en cours")}</b>
<p>{L(lang, "The rules below were fixed on 30 October 2026, before the data were extracted. Monthly index data (2000-2026) are being extracted from the Bloomberg terminal; results will be published here with every variant tested.",
      "Les règles ci-dessous ont été fixées le 30 octobre 2026, avant l'extraction des données. Les données mensuelles d'indices (2000-2026) sont en cours d'extraction sur le terminal Bloomberg ; les résultats seront publiés ici avec toutes les variantes testées.")}</p></div></div>"""


def current_value(lang):
    h = ETF["value"]["holdings"]
    lr = "../../"
    rows = []
    for ln in h["selection"]:
        nm = LINE_NAMES.get(ln, ln)
        kind = L(lang, "Country", "Pays") if ln.startswith("C_") else L(lang, "Sector", "Secteur")
        ps = [p for p in PITCHES if (ln.startswith("C_") and COUNTRY_CODE.get(p["country"]) == ln[2:]) or (ln.startswith("S_") and SECTOR_CODE.get(p["sector"]) == ln[2:])]
        rows.append([kind, f"<b>{esc(tr(lang, nm))}</b>", pct(0.125 * h.get("exposure", 1.0), 1, lang=lang), pitch_links(ps, lang, lr)])
    ind = h.get("indicators", {}); nred = sum(ind.values())
    names = {"trend": L(lang, "trend", "tendance"), "credit": L(lang, "credit", "crédit"), "breadth": L(lang, "breadth", "largeur")}
    reds = ", ".join(names[k] for k, x in ind.items() if x) or L(lang, "none", "aucun")
    expo = h.get("exposure", 1.0)
    state = L(lang, f"Risk rule: <b>{pct(expo, 0, lang=lang)} invested</b>. Red indicators: {reds} ({nred} of 3); fast re-entry signal {'on' if h.get('fast') else 'off'}. The portfolio is cut to 50% only when at least two indicators are red and the fast signal is off.",
                    f"Règle de risque : <b>investi à {pct(expo, 0, lang=lang)}</b>. Indicateurs rouges : {reds} ({nred} sur 3) ; signal de retour rapide {'actif' if h.get('fast') else 'inactif'}. Le portefeuille n’est réduit à 50 % que si au moins deux indicateurs sont rouges et que le signal rapide est inactif.")
    return (f'<div class="callout">{state}</div>' + tbl([L(lang, "Sleeve", "Poche"), L(lang, "Line", "Ligne"), L(lang, "Weight", "Poids"), L(lang, "Our pitches inside", "Nos pitches à l'intérieur")], rows, num_cols=(2,)) +
            f'<p class="cap">{L(lang, "Signal at the end of", "Signal à fin")} {month_name(h["date"], lang)}, {L(lang, "held over the following month. Renault, BNP Paribas and Carrefour sit in the France sleeve, Carrefour also in Consumer Staples: the rotation and the pitches point to the same place.", "détenu le mois suivant. Renault, BNP Paribas et Carrefour sont dans la poche France, Carrefour aussi dans la Consommation de base : la rotation et les pitches pointent au même endroit.")}</p>')


def value_reading(lang):
    v = ETF["value"]; st, bs = v["stats"], v["bench_stats"]; d, va = v["halves"]["design"], v["halves"]["valid"]
    bd, bv = v["halves"]["bench_design"], v["halves"]["bench_valid"]; bn = v["bench_name"].replace(" Net EUR", "")
    P = lambda x, n=1: pct(x, n, lang=lang)
    cal, bcal = v["calendar"], v["bench_calendar"]
    ahead = sum(cal[y] > bcal[y] for y in cal); ny = len(cal)
    ex08 = [y for y in cal if y != "2008"]
    def geo(c): 
        g = 1.0
        for y in ex08: g *= 1 + c[y]
        return g ** (1 / len(ex08)) - 1
    w2 = v.get("bench2_stats")
    pending = "" if "Value" in v["bench_name"] else f"""<div class="status" style="margin:18px 0"><span class="dot"></span><div><b>{L(lang, "Benchmark update pending", "Mise à jour de l’indice en attente")}</b><p>{L(lang, "The official benchmark is now MSCI World Value Net EUR. Its monthly series is being extracted from the Bloomberg terminal; until then, results are shown against MSCI World Net EUR.", "L’indice officiel est désormais le MSCI World Value Net EUR. Sa série mensuelle est en cours d’extraction sur le terminal Bloomberg ; en attendant, les résultats sont présentés face au MSCI World Net EUR.")}</p></div></div>"""
    world = "" if not w2 else L(lang, f" MSCI World, the investor's alternative, earned {P(w2['cagr'])} with a {P(w2['mdd'], 0)} worst loss.",
                                 f" Le MSCI World, l’alternative de l’investisseur, a rapporté {P(w2['cagr'])} avec une perte maximale de {P(w2['mdd'], 0)}.")
    xs, xb = geo(cal), geo(bcal)
    lead_en = (f"The lead does not rest on 2008 alone: excluding that year, the core earned {P(xs)} a year against {P(xb)}." if xs > xb else
               f"The lead is concentrated: excluding 2008, the core earned {P(xs)} a year against {P(xb)}.")
    lead_fr = (f"L’avance ne repose pas sur la seule année 2008 : hors 2008, le cœur a rapporté {P(xs)} par an contre {P(xb)}." if xs > xb else
               f"L’avance est concentrée : hors 2008, le cœur a rapporté {P(xs)} par an contre {P(xb)}.")
    return pending + f"""<div class="callout amber"><b>{L(lang, "What the backtest says.", "Ce que dit le backtest.")}</b> {L(lang,
        f"Over 2006-2026 the ETF core earned {P(st['cagr'])} a year against {P(bs['cagr'])} for {bn}, with a volatility of {P(st['vol'])} against {P(bs['vol'])} and a worst loss of {P(st['mdd'], 0)} against {P(bs['mdd'], 0)}.{world} It led {bn} in both halves: {P(d['cagr'])} against {P(bd['cagr'])} over 2006-2015, {P(va['cagr'])} against {P(bv['cagr'])} over 2016-2026, and in {ahead} calendar years out of {ny}. {lead_en} The risk rule cut the portfolio to 50% in {v['risk_off_months']} months out of {v['months']}, in {v['switches']} switches; in 2008 it lost {P(abs(cal['2008']))} against {P(abs(bcal['2008']))}. None of these gaps is statistically significant on twenty years of data: the core is best read as diversified value exposure with a brake, and the clean test is the live record.",
        f"Sur 2006-2026, le cœur ETF a rapporté {P(st['cagr'])} par an contre {P(bs['cagr'])} pour le {bn}, avec une volatilité de {P(st['vol'])} contre {P(bs['vol'])} et une perte maximale de {P(st['mdd'], 0)} contre {P(bs['mdd'], 0)}.{world} Il a devancé le {bn} sur les deux moitiés : {P(d['cagr'])} contre {P(bd['cagr'])} sur 2006-2015, {P(va['cagr'])} contre {P(bv['cagr'])} sur 2016-2026, et {ahead} années civiles sur {ny}. {lead_fr} La règle de risque a ramené le portefeuille à 50 % pendant {v['risk_off_months']} mois sur {v['months']}, en {v['switches']} bascules ; en 2008, il a perdu {P(abs(cal['2008']))} contre {P(abs(bcal['2008']))}. Aucun de ces écarts n’est statistiquement significatif sur vingt ans de données : le cœur se lit comme une exposition value diversifiée avec un frein, et le test propre est le suivi réel.")}</div>"""


def factsheet_section(kind, lang):
    idx = json.loads((HERE / "static/factsheets/index.json").read_text()).get(kind, [])
    if not idx:
        return None
    base = "../../" if lang == "en" else "../../../"
    last = idx[0]
    btn = lambda e, lg, cls: f'<a class="btn {cls}" href="{base}assets/factsheets/{e[lg]}" download>{ICON_DL} {"English" if lg == "en" else "Français"} · PDF</a>'
    arch = "".join(f'<li>{month_name(e["month"], lang)} · <a href="{base}assets/factsheets/{e["en"]}">EN</a> · <a href="{base}assets/factsheets/{e["fr"]}">FR</a></li>' for e in idx[1:])
    who = L(lang, "Thoth Ledger", "Thoth Ledger") if kind == "value" else "Horus AM"
    body = (f'<div class="box accent" style="display:flex;justify-content:space-between;align-items:center;gap:18px;flex-wrap:wrap">'
            f'<div><div class="k">{L(lang, "Latest", "Dernière")} · {month_name(last["month"], lang)} · {who}</div>'
            f'<h4 style="margin-top:6px">{L(lang, "Two-page monthly factsheet", "Factsheet mensuelle de deux pages")}</h4>'
            f'<p>{L(lang, "Performance, risk, calendar years, current portfolio and a short comment, updated each month with the new data.", "Performances, risque, années civiles, portefeuille actuel et un court commentaire, mis à jour chaque mois avec les nouvelles données.")}</p></div>'
            f'<div class="btns">{btn(last, "en", "primary")}{btn(last, "fr", "")}</div></div>')
    if arch:
        body += f'<h3>{L(lang, "Archive", "Archives")}</h3><ul>{arch}</ul>'
    body += '<p class="cap"><a href="../../factsheets/">' + L(lang, 'All factsheets, every month, both strategies', 'Toutes les factsheets, chaque mois, pour les deux stratégies') + ' →</a></p>'
    return section("factsheet", L(lang, "Monthly factsheet", "Factsheet mensuelle"), body)


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
        [L(lang, "Value signal (what)", "Signal value (quoi)"), L(lang, "Average of three z-scores: earnings yield (E/P), book yield (B/P) and dividend yield, each measured against the line's own trailing 10-year history (at least 5 years). A market is cheap when it is cheap versus its own past.", "Moyenne de trois z-scores : rendement bénéficiaire (E/P), rendement comptable (B/P) et rendement du dividende, chacun mesuré par rapport à l'historique propre de la ligne sur 10 ans glissants (5 ans minimum). Un marché est bon marché quand il l'est par rapport à son propre passé.")],
        [L(lang, "Selection", "Sélection"), L(lang, "Two sleeves of equal size: the 4 cheapest countries and the 4 cheapest sectors.", "Deux poches de même taille : les 4 pays et les 4 secteurs les moins chers.")],
        [L(lang, "Holding buffer", "Tampon de détention"), L(lang, "A line already held is kept until it leaves the 6 cheapest of its sleeve. Value pays over years, not months: the buffer stops the strategy from selling a cheap market just because another became marginally cheaper.", "Une ligne déjà détenue est conservée tant qu'elle reste parmi les 6 moins chères de sa poche. Le value paie sur des années, pas des mois : le tampon évite de vendre un marché bon marché simplement parce qu'un autre l'est devenu un peu plus.")],
        [L(lang, "Risk rule (how much)", "Règle de risque (combien)"), L(lang, "Three indicators are checked at each month end: trend (MSCI World Net EUR below its 10-month average), credit (euro high yield behind short euro government bonds over 3 months) and breadth (fewer than half of the 25 lines above their own 10-month average). When at least two are red, the portfolio is cut to 50% equities and 50% euro money market, never to zero.", "Trois indicateurs sont vérifiés à chaque fin de mois : tendance (MSCI World Net EUR sous sa moyenne de 10 mois), crédit (high yield euro en retard sur les obligations d’État euro courtes sur 3 mois) et largeur (moins de la moitié des 25 lignes au-dessus de leur propre moyenne de 10 mois). Quand au moins deux sont rouges, le portefeuille est ramené à 50 % d’actions et 50 % de monétaire euro, jamais à zéro.")],
        [L(lang, "Fast re-entry", "Retour rapide"), L(lang, "Back to 100% as soon as MSCI World has a positive 3-month return or closes above its 5-month average, even if the slower indicators are still red: the rule accepts a few false starts to catch rebounds.", "Retour à 100 % dès que le MSCI World a un rendement positif sur 3 mois ou repasse au-dessus de sa moyenne de 5 mois, même si les indicateurs plus lents sont encore rouges : la règle accepte quelques faux départs pour prendre les rebonds.")],
        [L(lang, "Weighting", "Pondération"), L(lang, "Equal weight, 12.5% per ETF at full exposure (6.25% when cut to 50%); long only, no leverage.", "Équipondération, 12,5 % par ETF à pleine exposition (6,25 % quand le portefeuille est réduit à 50 %) ; long uniquement, sans levier.")],
        [L(lang, "Rebalancing", "Rebalancement"), L(lang, "Monthly: signals at the last trading day of the month, trades on the first trading day of the next month.", "Mensuel : signaux au dernier jour de bourse du mois, ordres le premier jour de bourse du mois suivant.")],
        [L(lang, "Costs", "Frais"), L(lang, "0.10% per unit of turnover and 0.25% a year of ETF fees.", "0,10 % par unité de rotation et 0,25 % par an de frais d'ETF.")],
        [L(lang, "Benchmark", "Indice de référence"), L(lang, "MSCI World Value Net EUR (style benchmark, chosen 4 Nov 2026 because the strategy is a value strategy); MSCI World Net EUR is also shown as the investor's alternative.", "MSCI World Value Net EUR (indice de style, retenu le 4/11/2026 parce que la stratégie est une stratégie value) ; le MSCI World Net EUR est aussi affiché comme alternative de l'investisseur.")],
        [L(lang, "Structure", "Structure"), L(lang, "This ETF core is 70% of the value strategy. The other 30% will be a satellite of single stocks from the stock-level value screen (in construction).", "Ce cœur ETF représente 70 % de la stratégie value. Les 30 % restants seront un satellite d’actions issues du screen value titre par titre (en construction).")],
        [L(lang, "History", "Historique"), L(lang, "Rules V1 fixed on 30 Oct 2026 before the data; five further rounds, each pre-registered before it was run. The current core (V7, 4 Nov 2026) keeps the V4c selection and replaces its all-or-nothing cash switch with the 50% risk rule. 2006-2015 is the design half, 2016-2026 the validation half; the live record starts in November 2026.", "Règles V1 fixées le 30/10/2026 avant les données ; cinq séries de tests ensuite, chacune pré-enregistrée avant d’être lancée. Le cœur actuel (V7, 4/11/2026) garde la sélection de V4c et remplace sa sortie tout-ou-rien en cash par la règle de risque à 50 %. 2006-2015 est la période de conception, 2016-2026 la période de validation ; le suivi réel commence en novembre 2026.")],
    ])
    toc = [("idea", L(lang, "The idea", "L'idée")), ("rules", L(lang, "Rules", "Règles")), ("results", L(lang, "Results", "Résultats")),
           ("variants", L(lang, "Variants", "Variantes")), ("now", L(lang, "Current portfolio", "Portefeuille actuel")),
           ("universe", L(lang, "Universe", "Univers")), ("pitches", L(lang, "Link with the pitches", "Lien avec les pitches")),
           ("risks", L(lang, "Risks", "Risques"))]
    vres, vscript = results_block("value", lang)
    secs = [
        section("idea", L(lang, "The idea", "L'idée"), f"""<div class="prose"><p>{L(lang,
            "Value works across markets, not only across stocks: countries and sectors that are cheap relative to their own history have tended to outperform over the following years (Asness, Moskowitz and Pedersen, 2013, <i>Value and Momentum Everywhere</i>). Countries and sectors are also easy to hold: one ETF each, cheap, liquid, available to any European investor.",
            "Le value fonctionne entre marchés, pas seulement entre actions : les pays et secteurs bon marché par rapport à leur propre historique ont eu tendance à surperformer les années suivantes (Asness, Moskowitz et Pedersen, 2013, <i>Value and Momentum Everywhere</i>). Pays et secteurs sont aussi faciles à détenir : un ETF chacun, peu coûteux, liquide, accessible à tout investisseur européen.")}</p>
<p>{L(lang, "Value alone has a weakness: cheap markets are often cheap because they are falling, and they can keep falling with the rest of the market (2008). So the strategy splits the two questions. <b>Value decides what to hold; a risk rule decides how much of it to hold.</b> The value signal is slow and is given time to work; the risk rule is checked every month and never takes the portfolio below 50% equities, as a real fund would not either.", "Le value seul a une faiblesse : les marchés bon marché le sont souvent parce qu'ils baissent, et ils peuvent continuer à baisser avec le reste du marché (2008). La stratégie sépare donc les deux questions. <b>Le value décide quoi détenir ; une règle de risque décide quelle part en détenir.</b> Le signal value est lent et on lui laisse le temps d'agir ; la règle de risque est vérifiée chaque mois et ne descend jamais sous 50 % d’actions, comme un vrai fonds.")}</p>
<p>{L(lang, "This ETF rotation is the top-down core (70%) of my value strategy. The stock-level screen and the pitches are its bottom-up satellite (30%), where the value signal is strongest: at stock level, within sectors.", "Cette rotation en ETF est le cœur top-down (70 %) de ma stratégie value. Le screen titres et les pitches en sont le satellite bottom-up (30 %), là où le signal value est le plus fort : au niveau des titres, à l’intérieur des secteurs.")}</p></div>
<div class="steps" style="margin-top:22px">
 <div class="box"><h4>{L(lang, "Measure", "Mesurer")}</h4><p>{L(lang, "E/P, B/P and dividend yield of 25 indices at each month end.", "E/P, B/P et rendement du dividende de 25 indices à chaque fin de mois.")}</p></div>
 <div class="box"><h4>{L(lang, "Score", "Noter")}</h4><p>{L(lang, "Each ratio versus the line's own 10-year history, averaged.", "Chaque ratio rapporté à l'historique propre de la ligne sur 10 ans, puis moyenné.")}</p></div>
 <div class="box"><h4>{L(lang, "Select and keep", "Choisir et garder")}</h4><p>{L(lang, "Buy the 4 cheapest countries and sectors; keep a line while it stays in the 6 cheapest.", "Acheter les 4 pays et secteurs les moins chers ; garder une ligne tant qu'elle reste parmi les 6 moins chères.")}</p></div>
 <div class="box"><h4>{L(lang, "Dose the risk", "Doser le risque")}</h4><p>{L(lang, "100% invested, or 50% when two of three risk indicators are red; fast return to 100% on a rebound.", "Investi à 100 %, ou à 50 % quand deux indicateurs de risque sur trois sont rouges ; retour rapide à 100 % au rebond.")}</p></div>
</div>"""),
        section("rules", L(lang, "Rules", "Règles"), rules, L(lang, "Each version was written down before it was run; every version tried is published under Variants.", "Chaque version a été écrite avant d'être lancée ; toutes les versions essayées sont publiées dans Variantes.")),
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
        section("results", L(lang, "Results", "Résultats"), vres + value_reading(lang)),
        section("variants", L(lang, "Variants", "Variantes"), variants_table(lang, ()) +
                f'<p class="cap">{L(lang, "Every version was written down before it was run, except V6, found while studying V1 and marked as such. Six rounds and about twenty value versions in all; the main ones are shown. V7 was chosen after seeing both halves, so 2016-2026 is not a clean out-of-sample test of that choice. The same risk rule was checked on the 11 S&P 500 sectors, a universe never used before, where it also cut the drawdown from −45% to −26% without losing return. The clean test is the live record from November 2026.", "Chaque version a été écrite avant d’être lancée, sauf V6, trouvée en étudiant V1 et signalée comme telle. Six séries et une vingtaine de versions value au total ; les principales sont montrées. V7 a été choisie après avoir vu les deux moitiés : 2016-2026 n’est donc pas un test hors échantillon propre de ce choix. La même règle de risque a été vérifiée sur les 11 secteurs du S&P 500, un univers jamais utilisé auparavant, où elle a aussi ramené la perte maximale de −45 % à −26 % sans perdre de rendement. Le test propre est le suivi réel à partir de novembre 2026.")}</p>',
                L(lang, "Every version tested, including the ones that did worse.", "Toutes les versions testées, y compris celles qui ont fait moins bien.")),
        section("now", L(lang, "Current portfolio", "Portefeuille actuel"), current_value(lang)),
        section("risks", L(lang, "Risks", "Risques"), f"""<div class="cols2">
 <div class="box"><h4>{L(lang, "Value traps at market level", "Pièges à valeur à l’échelle d’un marché")}</h4><p>{L(lang, "A country can stay cheap for years (Italy, Hong Kong). Measuring cheapness against its own history limits this, but does not remove it.", "Un pays peut rester bon marché des années (Italie, Hong Kong). Mesurer la décote par rapport à son propre historique limite ce risque sans le supprimer.")}</p></div>
 <div class="box"><h4>{L(lang, "Concentration", "Concentration")}</h4><p>{L(lang, "Eight lines can overlap: a cheap Financials sector and a cheap Italy are partly the same bet.", "Huit lignes peuvent se recouper : un secteur Finance bon marché et une Italie bon marché sont en partie le même pari.")}</p></div>
 <div class="box"><h4>{L(lang, "False signals", "Faux signaux")}</h4><p>{L(lang, "The risk rule cuts after a fall and adds back on a rebound. It halves the damage of long bear markets (2008: −24% against −38%) but costs money in short corrections that reverse quickly.", "La règle de risque réduit après une baisse et remet du risque au rebond. Elle divise par deux les dégâts des longs marchés baissiers (2008 : −24 % contre −38 %) mais coûte dans les corrections courtes qui se retournent vite.")}</p></div>
 <div class="box"><h4>{L(lang, "Growth markets", "Marchés de croissance")}</h4><p>{L(lang, "When expensive growth leads, as in 2023-24, a value rotation lags the benchmark.", "Quand la croissance chère mène, comme en 2023-24, une rotation value fait moins bien que le benchmark.")}</p></div>
</div>"""),
    ]
    _fs = factsheet_section("value", lang)
    if _fs:
        toc.insert(1, ("factsheet", L(lang, "Monthly factsheet", "Factsheet mensuelle")))
        secs.insert(1, _fs)
    body = phead(L(lang, "Strategy · Equities · ETF", "Stratégie · Actions · ETF"), L(lang, "Global Value Rotation", "Rotation Value mondiale"),
                 L(lang, "The ETF core (70%) of the value strategy. Value decides what to hold: the four cheapest developed countries and sectors against their own history. A risk rule decides how much: 100%, or 50% when the market turns. Eight UCITS ETFs, monthly.",
                   "Le cœur ETF (70 %) de la stratégie value. Le value décide quoi détenir : les quatre pays et les quatre secteurs développés les moins chers par rapport à leur propre historique. Une règle de risque décide combien : 100 %, ou 50 % quand le marché se retourne. Huit ETF UCITS, mensuel."),
                 f'<a href="../">{t(lang, "strategies")}</a> / value-rotation')
    body += doc_layout(lang, toc, secs)
    page("strategies/value-rotation/index.html", lang, L(lang, "Global Value Rotation", "Rotation Value mondiale"), body, "strategies",
         L(lang, "Monthly value rotation across developed countries and sectors with UCITS ETFs.", "Rotation value mensuelle entre pays et secteurs développés avec des ETF UCITS."),
         scripts=vscript)


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
    _fs = factsheet_section("horus", lang)
    if _fs:
        toc.insert(1, ("factsheet", L(lang, "Monthly factsheet", "Factsheet mensuelle")))
        secs.insert(1, _fs)
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
def deck_links(f, root, small=True, lang="en"):
    """Download buttons for the English and French decks (PowerPoint and PDF)."""
    out = []
    for code, keys in (("EN", ("pptx", "pdf")), ("FR", ("pptx_fr", "pdf_fr"))):
        if keys[0] not in f:
            continue
        primary = (code == "EN") == (lang == "en") and not small
        out.append(f'<a class="btn {"sm" if small else ""} {"primary" if primary else ""}" href="{root}{f[keys[0]]}" hreflang="{code.lower()}">{ICON_DL} {code} · PowerPoint</a>')
        if keys[1] in f:
            out.append(f'<a class="btn {"sm" if small else ""}" href="{root}{f[keys[1]]}" hreflang="{code.lower()}">{code} · PDF</a>')
    return "".join(out)


def build_pitch_index(lang):
    cards = []
    for s in PITCHES:
        f = s["files"]
        root = "../" if lang == "en" else "../../"
        dl = deck_links(f, root, small=True)
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
                 L(lang, "Holdings of the December 2025 value portfolio, researched from company filings in October 2026. Each pitch has a twelve-slide deck in a buy-side format, in English and French.",
                   "Des titres du portefeuille value de décembre 2025, étudiés à partir des publications des sociétés en octobre 2026. Chaque pitch a un deck de douze slides au format buy-side, en anglais et en français."))
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
    dl = deck_links(f, lr if lang == "en" else "../../../", small=False, lang=lang)
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
        section("deck", "Deck", f'<div class="box" style="display:flex;justify-content:space-between;align-items:center;gap:18px;flex-wrap:wrap"><div><h4>{L(lang, "The full pitch", "Le pitch complet")}</h4><p>{L(lang, "Twelve slides: summary, company, macro, why the screen picked it, track record, financials, variant perception, valuation, catalysts, risks and sources. Available in English and French.", "Douze slides : synthèse, société, macro, pourquoi le screen l’a choisi, historique, financiers, variant perception, valorisation, catalyseurs, risques et sources. Disponible en anglais et en français.")}</p></div><div class="btns">{dl}</div></div>'),
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
    for d in ["fr", "pitches", "research", "strategies", "tracker", "factsheets", "trend-following", "downloads", "database", "journal", "methodology", "about", "static"]:
        if (DOCS / d).exists():
            shutil.rmtree(DOCS / d)
    for f in ["home_template.html"]:
        if (DOCS / f).exists():
            (DOCS / f).unlink()


# ---------------------------------------------------------------- TRACKER
def tracker_data():
    """Monthly net returns of the three strategies and their benchmarks (aggregated results only, no raw data)."""
    d = json.loads((DATA / "etf_strategies.json").read_text())
    h = json.loads((DATA / "horus_smart_beta.json").read_text())

    def rets(nav):
        out, prev = [], 1.0
        for x in nav:
            out.append(round(x / prev - 1, 6)); prev = x
        return out
    y, m = map(int, h["start"].split("-"))
    hd = []
    for _ in h["r_p3"]:
        hd.append(f"{y:04d}-{m:02d}"); m += 1
        if m == 13: y, m = y + 1, 1
    return {
        "value": dict(dates=d["value"]["dates"], r=rets(d["value"]["nav"]), b=rets(d["value"]["bench"]), ccy="EUR",
                      name=["Global Value Rotation", "Rotation Value mondiale"], bench=d["value"]["bench_name"]),
        "horus": dict(dates=hd, r=[round(x, 6) for x in h["r_p3"]], b=[round(x, 6) for x in h["r_bench"]], ccy="USD",
                      name=["Horus Smart Beta 60/40", "Horus Smart Beta 60/40"], bench="60/40 (MSCI ACWI / US Agg)"),
        "mix": mix_data(d),
    }


def mix_data(d):
    """Both strategies in EUR on their common months; the JS mixes them at the chosen weights, rebalanced monthly."""
    v, he = d["value"], d["horus_eur"]
    rv = dict(zip(v["dates"], [v["nav"][0] - 1] + [v["nav"][i] / v["nav"][i - 1] - 1 for i in range(1, len(v["nav"]))]))
    bv = dict(zip(v["dates"], [v["bench"][0] - 1] + [v["bench"][i] / v["bench"][i - 1] - 1 for i in range(1, len(v["bench"]))]))
    rh, bh = dict(zip(he["dates"], he["r"])), dict(zip(he["dates"], he["b"]))
    ds = [x for x in v["dates"] if x in rh]
    return dict(dates=ds, rv=[round(rv[x], 6) for x in ds], bv=[round(bv[x], 6) for x in ds], rh=[rh[x] for x in ds], bh=[bh[x] for x in ds],
                r=[round(rv[x], 6) for x in ds], b=[round(bv[x], 6) for x in ds], ccy="EUR",
                name=["Both strategies (mix)", "Les deux stratégies (mix)"], bench="Mix of benchmarks")


def build_tracker(lang):
    data = tracker_data()
    opts = "".join(f'<option value="{k}">{esc(v["name"][0 if lang == "en" else 1])} · {v["ccy"]} · {L(lang, "from", "depuis")} {v["dates"][0]}</option>' for k, v in data.items())
    mixrow = (f'<div class="fgroup" id="trk-mixg" style="display:none"><span>{L(lang, "Value / Horus", "Value / Horus")}</span>'
              f'<input id="trk-w" type="range" min="0" max="100" step="10" value="50" style="accent-color:var(--gold);width:160px">'
              f'<b id="trk-wl" style="font:600 14px var(--f);min-width:90px">50 / 50</b></div>')
    body = phead(L(lang, "Simulation · net of costs", "Simulation · nette de frais"),
                 L(lang, "Portfolio tracker", "Simulateur de portefeuille"),
                 L(lang, "Pick a strategy, a start month and an amount: see what the position would be worth today, month by month, against its benchmark.",
                   "Choisissez une stratégie, un mois de départ et un montant : voyez ce que vaudrait la position aujourd’hui, mois par mois, face à son indice de référence."))
    body += f"""
<section class="sec"><div class="wrap">
 <div class="filters" id="trk-form">
  <div class="fgroup"><span>{L(lang, "Strategy", "Stratégie")}</span><select id="trk-s" class="search" style="min-width:300px">{opts}</select></div>
  <div class="fgroup"><span>{L(lang, "Start", "Départ")}</span><input id="trk-d" class="search" type="month" style="min-width:150px;flex:none"></div>
  <div class="fgroup"><span>{L(lang, "Amount", "Montant")}</span><input id="trk-a" class="search" type="number" min="100" step="100" value="10000" style="min-width:130px;flex:none"></div>
  <div class="fgroup"><span>{L(lang, "Monthly top-up", "Versement mensuel")}</span><input id="trk-m" class="search" type="number" min="0" step="50" value="0" style="min-width:110px;flex:none"></div>
  {mixrow}
 </div>
 <p class="cap" id="trk-mixnote" style="display:none;margin:-12px 0 18px">{L(lang, "Mix: both strategies in euros (Horus converted from US dollars at the month-end EUR/USD rate), brought back to the chosen weights every month. Benchmark: the same mix of MSCI World Value and the Horus 60/40 benchmark.", "Mix : les deux stratégies en euros (Horus converti depuis le dollar au cours EUR/USD de fin de mois), ramenées aux poids choisis chaque mois. Indice : le même mélange du MSCI World Value et de l’indice 60/40 d’Horus.")}</p>
 <div class="stats" id="trk-stats"></div>
 <figure class="ch" style="margin-top:20px"><figcaption><span id="trk-title"></span><span class="legend"><span><i style="background:var(--navy)"></i><span id="trk-l1"></span></span><span><i style="background:var(--bench)"></i><span id="trk-l2"></span></span><span><i style="background:var(--gold)"></i>{L(lang, "Amount invested", "Montant investi")}</span></span></figcaption>
  <div class="chartbox"><svg id="trk-svg" viewBox="0 0 900 340" role="img"></svg><div class="tip" id="trk-tip"></div></div></figure>
 <h3>{L(lang, "Year by year", "Année par année")}</h3>
 <div class="tbl-wrap"><table class="t" id="trk-tbl"></table></div>
 <p class="cap">{L(lang, "Hypothetical backtests, net of trading costs and ETF fees, before taxes. Past performance does not guarantee future returns. The value series is the official ETF core (V7), benchmark MSCI World Value; Horus Smart Beta is in US dollars (Horus AM data), converted to euros only in the mix. Not investment advice.",
   "Backtests hypothétiques, nets de frais de transaction et de frais d’ETF, avant impôts. Les performances passées ne préjugent pas des performances futures. La série value est le cœur ETF officiel (V7), indice MSCI World Value ; Horus Smart Beta est en dollars (données Horus AM), converti en euros seulement dans le mix. Ceci n’est pas un conseil en investissement.")}</p>
</div></section>"""
    T = json.dumps(data, separators=(",", ":"))
    js = """<script>(function(){
var D=__DATA__,LANG="__LANG__",FR=LANG==="fr";
var $=function(i){return document.getElementById(i)};
function money(v,c){return new Intl.NumberFormat(FR?"fr-FR":"en-GB",{style:"currency",currency:c,maximumFractionDigits:0}).format(v)}
function pc(v,s){var x=(v*100).toFixed(1);if(FR)x=x.replace(".",",");return (s&&v>0?"+":"")+x+(FR?"\u00a0%":"%")}
function stat(k,v,s){return '<div class="stat"><div class="k">'+k+'</div><div class="v">'+v+'</div><div class="s">'+(s||"")+'</div></div>'}
function sim(r,i0,amt,top){var v=amt,inv=amt,out=[],pk=0,dd=0;for(var i=i0;i<r.length;i++){if(i>i0){v+=top;inv+=top}v*=1+r[i];out.push([v,inv]);}return out}
function mdd(r,i0){var n=1,pk=1,dd=0;for(var i=i0;i<r.length;i++){n*=1+r[i];pk=Math.max(pk,n);dd=Math.min(dd,n/pk-1)}return dd}
function draw(){
 var k=$("trk-s").value,S=D[k],d0=$("trk-d").value||S.dates[0];
 var mix=k==="mix";$("trk-mixg").style.display=mix?"":"none";$("trk-mixnote").style.display=mix?"":"none";
 if(mix){var w=(+$("trk-w").value)/100;$("trk-wl").textContent=Math.round(w*100)+" / "+Math.round(100-w*100);S.r=S.rv.map(function(x,i){return w*x+(1-w)*S.rh[i]});S.b=S.bv.map(function(x,i){return w*x+(1-w)*S.bh[i]});
  S.name=FR?["","Mix "+Math.round(w*100)+" % value / "+Math.round(100-w*100)+" % Horus"]:["Mix "+Math.round(w*100)+"% value / "+Math.round(100-w*100)+"% Horus",""];S.bench=FR?"Mix des indices":"Benchmark mix"}
 var _=0,amt=+$("trk-a").value||0,top=+$("trk-m").value||0;
 var i0=S.dates.indexOf(d0);if(i0<0){i0=d0<S.dates[0]?0:S.dates.length-1}$("trk-d").value=S.dates[i0];
 $("trk-d").min=S.dates[0];$("trk-d").max=S.dates[S.dates.length-1];
 var P=sim(S.r,i0,amt,top),B=sim(S.b,i0,amt,top),n=P.length,yrs=n/12;
 var fv=P[n-1][0],bv=B[n-1][0],inv=P[n-1][1];
 var cP=1,cB=1;for(var i=i0;i<S.r.length;i++){cP*=1+S.r[i];cB*=1+S.b[i]}
 var cagr=Math.pow(cP,1/yrs)-1,bc=Math.pow(cB,1/yrs)-1;
 $("trk-stats").innerHTML=stat(FR?"Valeur finale":"Final value",money(fv,S.ccy),(FR?"investi ":"invested ")+money(inv,S.ccy))
  +stat(FR?"Plus-value":"Gain",money(fv-inv,S.ccy),pc(fv/inv-1,1))
  +stat(FR?"Rendement annualisé":"Annual return",pc(cagr),(FR?"indice ":"benchmark ")+pc(bc))
  +stat(FR?"Pire baisse":"Max drawdown",pc(mdd(S.r,i0)),(FR?"indice ":"benchmark ")+pc(mdd(S.b,i0)))
  +stat(FR?"Face à l’indice":"Vs benchmark",money(fv-bv,S.ccy),(FR?"valeur finale indice ":"benchmark ends at ")+money(bv,S.ccy));
 $("trk-title").textContent=(FR?"Valeur de la position, ":"Position value, ")+S.ccy+" · "+S.dates[i0]+" → "+S.dates[S.dates.length-1];
 $("trk-l1").textContent=S.name[FR?1:0];$("trk-l2").textContent=S.bench;
 var W=900,H=340,l=70,r=16,t=14,b=30,mx=0,mn=1e18;P.forEach(function(p,i){mx=Math.max(mx,p[0],B[i][0],p[1]);mn=Math.min(mn,p[0],B[i][0],p[1])});
 mn*=.95;mx*=1.03;var X=function(i){return l+(W-l-r)*(n<2?0:i/(n-1))},Y=function(v){return t+(H-t-b)*(1-(v-mn)/(mx-mn))};
 var g="";for(var j=0;j<=4;j++){var v=mn+(mx-mn)*j/4;g+='<line x1="'+l+'" x2="'+(W-r)+'" y1="'+Y(v)+'" y2="'+Y(v)+'" stroke="var(--line)"/><text x="'+(l-8)+'" y="'+(Y(v)+4)+'" text-anchor="end">'+money(v,S.ccy)+'</text>'}
 var yr=null;for(var i=0;i<n;i++){var y=S.dates[i0+i].slice(0,4);if(y!==yr&&(+y)%(n>120?5:n>36?2:1)===0&&S.dates[i0+i].slice(5)==="01"){g+='<text x="'+X(i)+'" y="'+(H-8)+'" text-anchor="middle">'+y+'</text>'}yr=y}
 function path(A,c,w,dash){return '<path d="'+A.map(function(v,i){return(i?"L":"M")+X(i).toFixed(1)+" "+Y(v).toFixed(1)}).join("")+'" fill="none" stroke="'+c+'" stroke-width="'+w+'"'+(dash?' stroke-dasharray="4 4"':'')+'/>'}
 g+=path(P.map(function(p){return p[1]}),"var(--gold)",1.5,1)+path(B.map(function(p){return p[0]}),"var(--bench)",1.8)+path(P.map(function(p){return p[0]}),"var(--navy)",2.4);
 g+='<line id="trk-x" y1="'+t+'" y2="'+(H-b)+'" stroke="var(--line2)" style="display:none"/><rect x="'+l+'" y="'+t+'" width="'+(W-l-r)+'" height="'+(H-t-b)+'" fill="transparent" id="trk-hit"/>';
 var svg=$("trk-svg");svg.innerHTML=g;var tip=$("trk-tip");
 $("trk-hit").onmousemove=function(e){var bb=svg.getBoundingClientRect(),xx=(e.clientX-bb.left)*W/bb.width,i=Math.max(0,Math.min(n-1,Math.round((xx-l)/(W-l-r)*(n-1))));
  var ln=$("trk-x");ln.style.display="";ln.setAttribute("x1",X(i));ln.setAttribute("x2",X(i));
  tip.innerHTML="<b>"+S.dates[i0+i]+"</b><br>"+S.name[FR?1:0]+": "+money(P[i][0],S.ccy)+"<br>"+S.bench+": "+money(B[i][0],S.ccy)+"<br>"+(FR?"Investi":"Invested")+": "+money(P[i][1],S.ccy);
  tip.style.opacity=1;tip.style.left=Math.min(bb.width-220,X(i)*bb.width/W+12)+"px";tip.style.top="20px"};
 $("trk-hit").onmouseleave=function(){tip.style.opacity=0;$("trk-x").style.display="none"};
 var rows='<tr><th>'+(FR?"Année":"Year")+'</th><th class="n">'+S.name[FR?1:0]+'</th><th class="n">'+S.bench+'</th><th class="n">'+(FR?"Écart":"Difference")+'</th><th class="n">'+(FR?"Valeur fin d’année":"Year-end value")+'</th></tr>';
 var ys={};for(var i=i0;i<S.r.length;i++){var y=S.dates[i].slice(0,4);ys[y]=ys[y]||{p:1,b:1,last:0};ys[y].p*=1+S.r[i];ys[y].b*=1+S.b[i];ys[y].last=i-i0}
 Object.keys(ys).sort().reverse().forEach(function(y){var o=ys[y],dp=o.p-1,db=o.b-1;rows+='<tr><td>'+y+'</td><td class="n '+(dp<0?"neg":"")+'">'+pc(dp,1)+'</td><td class="n">'+pc(db,1)+'</td><td class="n '+(dp-db<0?"neg":"pos")+'">'+pc(dp-db,1)+'</td><td class="n">'+money(P[o.last][0],S.ccy)+'</td></tr>'});
 $("trk-tbl").innerHTML=rows;
}
["trk-s","trk-d","trk-a","trk-m","trk-w"].forEach(function(i){$(i).addEventListener("input",draw);$(i).addEventListener("change",draw)});
$("trk-s").addEventListener("change",function(){$("trk-d").value=""; draw()});
draw();})();</script>""".replace("__DATA__", T).replace("__LANG__", lang)
    page("tracker/index.html", lang, L(lang, "Portfolio tracker", "Simulateur de portefeuille"), body, "tracker",
         L(lang, "Simulate an investment in one of the three strategies from any start month.", "Simulez un investissement dans l’une des trois stratégies à partir de n’importe quel mois."), js)


# ---------------------------------------------------------------- FACTSHEETS ARCHIVE
def build_factsheets(lang):
    idx = json.loads((HERE / "static/factsheets/index.json").read_text())
    base = "../" if lang == "en" else "../../"
    strat = [("value", L(lang, "Global Value Rotation", "Rotation Value mondiale"), "Thoth Ledger", "../strategies/value-rotation/"),
             ("horus", "Horus Smart Beta 60/40", "Horus AM", "../strategies/horus-smart-beta/")]
    months = sorted({e["month"] for k, _, _, _ in strat for e in idx.get(k, [])}, reverse=True)
    link = lambda e, lg: f'<a class="btn sm" href="{base}assets/factsheets/{e[lg]}" download>{ICON_DL} {lg.upper()}</a>'
    rows = []
    for m in months:
        for k, nm, who, href in strat:
            e = next((x for x in idx.get(k, []) if x["month"] == m), None)
            if e:
                rows.append([f"<b>{month_name(m, lang)}</b>", f'<a href="{href}">{esc(nm)}</a> <small>· {who}</small>', f'<div class="btns">{link(e, "en")}{link(e, "fr")}</div>'])
    cards = []
    for k, nm, who, href in strat:
        if not idx.get(k):
            continue
        e = idx[k][0]
        cards.append(f'<article class="card"><div class="meta">{who} · {L(lang, "latest", "dernière")} : {month_name(e["month"], lang)}</div>'
                     f'<h3><a href="{href}">{esc(nm)}</a></h3>'
                     f'<p>{L(lang, "Two pages: performance against the benchmark, risk, calendar years, current portfolio and the comment of the month.", "Deux pages : performances face à l’indice, risque, années civiles, portefeuille actuel et commentaire du mois.")}</p>'
                     f'<div class="foot links"><div class="btns">{link(e, "en")}{link(e, "fr")}</div></div></article>')
    body = phead(L(lang, "Monthly reporting", "Reporting mensuel"), "Factsheets",
                 L(lang, "Every monthly factsheet published for the two strategies, in English and French. A new issue is added at the start of each month once the month-end data are in; past issues are never rewritten.",
                   "Toutes les factsheets mensuelles publiées pour les deux stratégies, en anglais et en français. Un nouveau numéro est ajouté au début de chaque mois, une fois les données de fin de mois disponibles ; les numéros passés ne sont jamais réécrits."))
    body += '<section class="sec"><div class="wrap"><div class="grid" style="grid-template-columns:repeat(auto-fit,minmax(320px,1fr))">' + "".join(cards) + '</div></div></section>'
    body += ('<section class="sec alt"><div class="wrap"><div class="shead"><h2>' + L(lang, "Archive", "Archives") + '</h2><p>'
             + L(lang, "Newest first. The value factsheets start with September 2026; the live record of the strategy starts in November 2026.",
                 "Les plus récentes d’abord. Les factsheets value commencent en septembre 2026 ; le suivi réel de la stratégie commence en novembre 2026.")
             + '</p></div>' + tbl([L(lang, "Month", "Mois"), L(lang, "Strategy", "Stratégie"), L(lang, "Download", "Télécharger")], rows) + '</div></section>')
    page("factsheets/index.html", lang, "Factsheets", body, "strategies",
         L(lang, "Monthly factsheets of the Thoth Ledger strategies, English and French.", "Factsheets mensuelles des stratégies Thoth Ledger, en anglais et en français."))


def main():
    clean_docs()
    (DOCS / "assets").mkdir(parents=True, exist_ok=True)
    for f in ("site.css", "site.js"):
        shutil.copy(HERE / "static" / f, DOCS / "assets" / f)
    shutil.copytree(HERE / "static" / "brand", DOCS / "assets" / "brand", dirs_exist_ok=True)
    shutil.copytree(HERE / "static" / "factsheets", DOCS / "assets" / "factsheets", dirs_exist_ok=True)
    (DOCS / ".nojekyll").touch()
    for lang in LANGS:
        build_home(lang)
        build_strategies(lang)
        build_value_rotation(lang)
        build_horus(lang)
        build_value_screen(lang)
        build_pitch_index(lang)
        for s in PITCHES:
            build_pitch(s, lang)
        build_research(lang)
        build_database(lang)
        build_tracker(lang)
        build_factsheets(lang)
        simple_page("journal", lang, "", t(lang, "journal"), L(lang, "Decisions and milestones, dated.", "Décisions et étapes, datées."))
        simple_page("methodology", lang, "", t(lang, "methodology"), L(lang, "Where the data come from and the rules every result respects.", "D’où viennent les données et les règles que chaque résultat respecte."))
        simple_page("about", lang, "about", t(lang, "about"), L(lang, "Who is behind this ledger and why it exists.", "Qui tient ce carnet et pourquoi il existe."))
    print("site built in", DOCS)


if __name__ == "__main__":
    main()
