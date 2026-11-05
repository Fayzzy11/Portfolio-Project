"""Strategy note in a Financial Times-like layout (English and French) for the Global Value Rotation (70% ETF core + 30% stock satellite).
Reads site/data/etf_strategies.json (aggregated results) and data/etf/official.pkl (private, for the 50%-exposure shading).
    python3 tools/note/build_value_note.py <out_dir>
"""
import json, sys, base64, math
from pathlib import Path
import pandas as pd
ROOT = Path(__file__).resolve().parents[2]
D = json.loads((ROOT / "site/data/etf_strategies.json").read_text())["value"]
_J = json.loads((ROOT / "site/data/etf_strategies.json").read_text())
VAR, COMB = _J["variants"], _J["combination"]
_O = pd.read_pickle(ROOT / "data/etf/official.pkl")
_e = _O["expo"].copy(); _e.index = pd.to_datetime(_e.index)
on = (_e.shift(1) >= 0.999).reindex(pd.to_datetime([x + "-01" for x in D["dates"]]) + pd.offsets.MonthEnd(0)).fillna(True)   # exposure during each month
OUT = Path(sys.argv[1] if len(sys.argv) > 1 else ".")
FONTS = Path("/home/claude/work/fonts/node_modules/@fontsource")
dates, nav, bnav = D["dates"], D["nav"], D["bench"]
st, bs, hv = D["stats"], D["bench_stats"], D["halves"]
w2 = D.get("bench2_stats", bs)
AHEAD = sum(D['calendar'][y] > D['bench_calendar'][y] for y in D['calendar'])
_ex = [y for y in D['calendar'] if y != '2008']
EX08 = lambda c: (math.prod(1 + c[y] for y in _ex)) ** (1 / len(_ex)) - 1
cal, bcal = D["calendar"], D["bench_calendar"]
_i = D['dates'].index('2015-12'); _b2 = D['bench2']; W2V = (_b2[-1] / _b2[_i]) ** (12 / (len(_b2) - 1 - _i)) - 1
wcal = D.get("bench2_calendar", bcal)


def font_css():
    css = []
    for fam, d, specs in (("Cormorant Garamond", "cormorant-garamond", [(500, "normal"), (600, "normal"), (700, "normal"), (500, "italic")]),
                          ("Source Sans 3", "source-sans-3", [(400, "normal"), (600, "normal"), (700, "normal")])):
        for w, s in specs:
            f = FONTS / d / "files" / f"{d}-latin-{w}-{s}.woff2"
            if f.exists():
                css.append(f"@font-face{{font-family:'{fam}';font-weight:{w};font-style:{s};src:url(data:font/woff2;base64,{base64.b64encode(f.read_bytes()).decode()}) format('woff2')}}")
    return "\n".join(css)


def pc(x, lang, d=1, sign=False):
    s = (f"{x * 100:+.{d}f}" if sign else f"{x * 100:.{d}f}").replace("-", "−")
    return s.replace(".", ",") + " %" if lang == "fr" else s + "%"


def nm(x, lang, d=2):
    s = f"{x:.{d}f}".replace("-", "−"); return s.replace(".", ",") if lang == "fr" else s


SALMON, INK, CLARET, BLUE, GRID = "#FFF1E5", "#33302E", "#990F3D", "#0F5499", "#E6D9CE"


def growth_svg(lang):
    W, H, l, r, t, b = 640, 250, 40, 10, 10, 24
    s = [100.0] + [100 * x for x in nav]; q = [100.0] + [100 * x for x in bnav]; w = [100.0] + [100 * x for x in D.get("bench2", bnav)]
    lo, hi = math.log(min(min(s), min(q)) * 0.92), math.log(max(max(s), max(q)) * 1.05)
    n = len(s)
    X = lambda i: l + (W - l - r) * i / (n - 1); Y = lambda v: t + (H - t - b) * (1 - (math.log(v) - lo) / (hi - lo))
    g = ""
    flags = [True] + list(on.values)
    i = 1
    while i < n:
        if not flags[i]:
            j = i
            while j < n and not flags[j]: j += 1
            g += f'<rect x="{X(i - 1):.1f}" y="{t}" width="{X(j - 1) - X(i - 1) + (W - l - r) / (n - 1):.1f}" height="{H - t - b}" fill="#F2DFCE"/>'
            i = j
        else:
            i += 1
    for v in (60, 100, 150, 200, 300, 400, 600):
        if math.log(v) < lo or math.log(v) > hi: continue
        g += f'<line x1="{l}" x2="{W - r}" y1="{Y(v):.1f}" y2="{Y(v):.1f}" stroke="{GRID}" stroke-width=".8"/><text x="{l - 5}" y="{Y(v) + 3:.1f}" text-anchor="end">{v}</text>'
    for i, d in enumerate(["2006-01"] + dates):
        if d.endswith("-12") and (int(d[:4]) + 1) % 4 == 2:
            g += f'<text x="{X(i):.1f}" y="{H - 7}" text-anchor="middle">{int(d[:4]) + 1}</text>'
    p = lambda a: "M" + " L".join(f"{X(i):.1f} {Y(v):.1f}" for i, v in enumerate(a))
    g += f'<path d="{p(w)}" fill="none" stroke="#8C8279" stroke-width="1.1" stroke-dasharray="3 2"/><path d="{p(q)}" fill="none" stroke="{BLUE}" stroke-width="1.6"/><path d="{p(s)}" fill="none" stroke="{CLARET}" stroke-width="2.1"/>'
    return f'<svg viewBox="0 0 {W} {H}">{g}</svg>'


def dd_svg(lang):
    W, H, l, r, t, b = 640, 150, 40, 10, 8, 22
    def dd(a):
        out, pk = [], 1
        for v in a: pk = max(pk, v); out.append(v / pk - 1)
        return out
    s, q = dd([1] + nav), dd([1] + bnav); n = len(s); lo = min(min(s), min(q)) * 1.08
    X = lambda i: l + (W - l - r) * i / (n - 1); Y = lambda v: t + (H - t - b) * (v / lo)
    g = ""
    for v in (0, -0.1, -0.2, -0.3, -0.4, -0.5):
        if v < lo: continue
        g += f'<line x1="{l}" x2="{W - r}" y1="{Y(v):.1f}" y2="{Y(v):.1f}" stroke="{GRID}" stroke-width=".8"/><text x="{l - 5}" y="{Y(v) + 3:.1f}" text-anchor="end">{int(round(v * 100))}</text>'
    for i, d in enumerate(["2006-01"] + dates):
        if d.endswith("-12") and (int(d[:4]) + 1) % 4 == 2:
            g += f'<text x="{X(i):.1f}" y="{H - 6}" text-anchor="middle">{int(d[:4]) + 1}</text>'
    area = lambda a, col, op: f'<path d="M{X(0):.1f} {Y(0):.1f} ' + " ".join(f"L{X(i):.1f} {Y(v):.1f}" for i, v in enumerate(a)) + f' L{X(n - 1):.1f} {Y(0):.1f} Z" fill="{col}" fill-opacity="{op}" stroke="{col}" stroke-width="1"/>'
    g += area(q, BLUE, .18) + area(s, CLARET, .35)
    return f'<svg viewBox="0 0 {W} {H}">{g}</svg>'


def cal_svg(lang):
    ys = sorted(cal, key=int)
    W, H, l, t, b = 640, 170, 30, 10, 20
    m = max(max(abs(cal[y]), abs(bcal[y])) for y in ys) * 1.08
    Y = lambda v: t + (H - t - b) * (0.5 - v / (2 * m)); bw = (W - l) / len(ys)
    g = ""
    for v in (-0.3, -0.15, 0, 0.15, 0.3):
        g += f'<line x1="{l}" x2="{W}" y1="{Y(v):.1f}" y2="{Y(v):.1f}" stroke="{GRID if v else "#B9A898"}" stroke-width=".8"/><text x="{l - 4}" y="{Y(v) + 3:.1f}" text-anchor="end">{int(v * 100)}</text>'
    for i, y in enumerate(ys):
        x = l + i * bw + bw * .12
        for j, (v, c) in enumerate(((cal[y], CLARET), (bcal[y], BLUE))):
            y0, y1 = sorted((Y(0), Y(v))); g += f'<rect x="{x + j * bw * .38:.1f}" y="{y0:.1f}" width="{bw * .36:.1f}" height="{max(y1 - y0, .6):.1f}" fill="{c}" fill-opacity="{1 if j == 0 else .55}"/>'
        g += f'<text x="{x + bw * .37:.1f}" y="{H - 6}" text-anchor="middle">{y[2:]}</text>'
    return f'<svg viewBox="0 0 {W} {H}">{g}</svg>'


def versions_table(lang):
    names_fr = {"V1 Rules of 30 Oct: 4 cheapest countries + 4 sectors": "V1 Règles du 30/10 : 4 pays + 4 secteurs",
                "V4c + holding buffer and 100% cash trend filter": "V4c Tampon + filtre de tendance 100 % cash",
                "V5 3 sectors only, 50% de-risking": "V5 3 secteurs, réduction à 50 %",
                "V7 ETF core: V4c selection, 50% de-risking": "V7 Cœur ETF : V4c, réduction à 50 %",
                "Satellite: 8 cheapest stocks in the core's countries and sectors": "Satellite : 8 actions les moins chères",
                "Strategy: 70% core + 30% satellite (official)": "Stratégie 70/30 (officielle)"}
    short_en = {"V1 Rules of 30 Oct: 4 cheapest countries + 4 sectors": "V1 Rules of 30 Oct: 4 countries + 4 sectors",
                "V4c + holding buffer and 100% cash trend filter": "V4c Buffer + 100% cash trend filter",
                "V7 ETF core: V4c selection, 50% de-risking": "V7 ETF core: V4c, cut to 50%",
                "Satellite: 8 cheapest stocks in the core's countries and sectors": "Satellite: 8 cheapest stocks",
                "Strategy: 70% core + 30% satellite (official)": "Strategy 70/30 (official)"}
    rows = ""
    for v in VAR:
        n = names_fr.get(v["name"], v["name"]) if lang == "fr" else short_en.get(v["name"], v["name"])
        cls = ' class="hl"' if "official" in v["name"] else (' class="b"' if v["name"].startswith("MSCI") else "")
        rows += f'<tr{cls}><td>{n}</td><td>{pc(v["cagr"], lang)}</td><td>{nm(v["sharpe"], lang)}</td><td>{pc(v["mdd"], lang, 0)}</td><td>{pc(v["design_cagr"], lang)}</td><td>{pc(v["valid_cagr"], lang)}</td></tr>'
    h = ["Version", "CAGR", "Sharpe", "Max DD", "2006-15", "2016-26"]
    return "<table class='vt'><tr>" + "".join(f"<th>{x}</th>" for x in h) + "</tr>" + rows + "</table>"


def mix_table(lang):
    rows = ""
    for m in COMB["mixes"]:
        w = int(round(m["value"] * 100))
        lab = f"{w}% value / {100 - w}% Horus" if lang == "en" else f"{w} % value / {100 - w} % Horus"
        rows += f'<tr><td>{lab}</td><td>{pc(m["cagr"], lang)}</td><td>{nm(m["sharpe"], lang)}</td><td>{pc(m["mdd"], lang, 0)}</td></tr>'
    return "<table class='vt'><tr>" + "".join(f"<th>{x}</th>" for x in [("Mix" if lang == "en" else "Mélange"), "CAGR", "Sharpe", "Max DD"]) + "</tr>" + rows + "</table>"


def text(lang):
    d, v, bd, bv = hv["design"], hv["valid"], hv["bench_design"], hv["bench_valid"]
    P = lambda x, k=1, s=False: pc(x, lang, k, s)
    N = lambda x, k=2: nm(x, lang, k)
    SAT, CORE = D["parts"]["satellite"], D["parts"]["core"]
    c = COMB; best = max(c["mixes"], key=lambda m: m["sharpe"])
    H = D["holdings"]; sat_names = ", ".join(s["name"] for s in H["satellite"])
    if lang == "en":
        return dict(
            mast="Strategy note", date="5 November 2026", sec="SYSTEMATIC STRATEGIES · VALUE",
            head="Cheap markets, cheaper stocks",
            stand=f"A value strategy built at two levels — ETFs on cheap countries and sectors, then the cheapest stocks inside them — beat its value benchmark over twenty years with little more than half of its worst loss. The stocks did the heavy lifting, and the clean test only starts now.",
            by="Noah Doose", byline="MSc Financial Markets & Investments, SKEMA Business School · CFA Level II candidate",
            lead=[f"Value investing has two problems. The first is timing: markets become cheap because they are falling, and in a crash they keep falling together. The second is precision: a sector can be cheap while many of the companies inside it are not.",
                  f"The Global Value Rotation, the official value strategy published on Thoth Ledger, answers both. It holds 70% in ETFs on the cheapest developed countries and sectors, 30% in the eight cheapest stocks inside them, and halves the whole portfolio when the market turns. From February 2006 to June 2026 it returned {P(st['cagr'])} a year net of costs, against {P(bs['cagr'])} for its benchmark, MSCI World Value in euros, and {P(w2['cagr'])} for MSCI World. Its worst drawdown was {P(st['mdd'], 0)}, against {P(bs['mdd'], 0)} and {P(w2['mdd'], 0)}; its Sharpe ratio {N(st['sharpe'])}, against {N(bs['sharpe'])} and {N(w2['sharpe'])}.",
                  f"The lead holds in both halves of the period, but it is not statistically significant: the t-statistic of the monthly excess return is {N(D['t_vs_bench'])}. The strategy beat its benchmark in {AHEAD} calendar years out of {len(cal)}. It matches MSCI World on return over twenty years, not since 2016.",
                  "Those numbers deserve as much suspicion as interest. This note explains how the strategy works, where its return comes from, where it fails, and why the only test that really counts started this month."],
            how_h="Two levels, one risk rule",
            how=[("The core (70%)", "At each month end, 25 indices are scored: 14 developed countries and the 11 sectors of MSCI World. The score averages three z-scores — earnings yield, book yield and dividend yield — each measured against the index's own ten-year history. The four cheapest countries and four cheapest sectors are held through one UCITS ETF each; a line already held stays until it leaves the six cheapest."),
                 ("The satellite (30%)", "Among the 300 largest stocks of MSCI World at each date — including those later delisted or taken over — the satellite ranks each company within its sector on EV/EBIT, book-to-price, free-cash-flow yield and sales-to-EV. Accounts are used only six months after the year end. It holds the eight cheapest stocks in the countries or sectors held by the core, at most two per sector and three per country, and keeps a stock while it stays in the cheapest 40% of its sector."),
                 ("The risk rule", "Three indicators are checked at each month end: MSCI World below its ten-month average, euro high yield lagging short government bonds, fewer than half of the 25 lines in an uptrend. When at least two are red, the whole portfolio is cut to 50% equities, never to zero, until fewer than two are red."),
                 ("The costs", f"The backtest charges 0.10% per unit of turnover and 0.25% a year of fees on ETFs, 0.15% per unit of turnover and 0.40% a year of withholding tax on stocks.")],
            g1_h="Growth of 100 invested at the end of January 2006", g1_s="Log scale, EUR, net of costs. Shaded: months at 50% exposure.",
            leg=("Global Value Rotation", "MSCI World Value Net EUR"),
            p2_h="Where the return comes from",
            p2=[f"Mostly from the stocks. On its own, the satellite earned {P(SAT['stats']['cagr'])} a year (t = {N(SAT['t'])} against MSCI World Value); the ETF core earned {P(CORE['stats']['cagr'])} (t = {N(CORE['t'])}). At country and sector level, the value score's twelve-month rank information coefficient was close to zero (−0.05 for countries, −0.03 for sectors). A sector ETF holds hundreds of companies and they cannot all be cheap: ranking stocks within their sector is where the signal is sharp enough to pay.",
                 f"The core brings the risk control. The risk rule held the portfolio at 50% in {D['risk_off_months']} of {D['months']} months, in {D['switches']} switches. In 2008 the strategy lost {P(abs(cal['2008']))} while MSCI World Value lost {P(abs(bcal['2008']))}; in 2022 it gained {P(cal['2022'], 1, True)} while MSCI World lost {P(abs(wcal['2022']))}.",
                 f"The rule has a cost, paid in quick rebounds: {P(cal['2020'], 1, True)} in 2020 against {P(wcal['2020'], 1, True)} for MSCI World. And when expensive growth leads, value lags whatever the rule: {P(cal['2023'], 1, True)} in 2023 and {P(cal['2024'], 1, True)} in 2024, against {P(wcal['2023'], 1, True)} and {P(wcal['2024'], 1, True)}."],
            g2_h="Drawdown from previous peak (%)", g3_h="Calendar-year returns (%)", g3_s="06-26 = 2006-2026; 2026 to June.",
            p3_h="Two halves, two stories",
            p3=[f"The research was organised around a design half (2006-2015) and a validation half (2016-2026). In the first, the strategy earned {P(d['cagr'])} a year against {P(bd['cagr'])} for MSCI World Value, mostly by losing less in 2008. In the second, {P(v['cagr'])} against {P(bv['cagr'])}, with the satellite at {P(SAT['halves']['valid']['cagr'])}.",
                 f"The benchmark is MSCI World Value because the strategy is a value strategy. MSCI World earned the same {P(w2['cagr'])} a year over twenty years, but much more since 2016 ({P(W2V)} a year), so it stays on every page as the investor's real alternative. Against it the strategy offers about the same return with a worst loss of {P(st['mdd'], 0)} instead of {P(w2['mdd'], 0)}."],
            p4_h="How it was built — and why that matters",
            p4=["The first rules were fixed on 30 October 2026, before any data were extracted: four countries and four sectors, no risk rule. They earned more than the benchmark with almost the same 50% drawdown. Each later step was written down and committed to the code repository before it was run: a holding buffer and a trend filter (V4c), a three-sector version (V5), the 50% risk rule instead of all-or-nothing cash (V7), and finally the stock satellite, with its universe, score and rules fixed before the first result.",
                 "Each step was chosen after seeing earlier results over the whole period, so 2016-2026 is not a clean out-of-sample test, and a reader should haircut the Sharpe ratio for the number of trials (Bailey and López de Prado, 2014). The clean test is the live record from November 2026; the monthly factsheet will report it without restating the backtest."],
            vt_h="The main versions, Feb 2006 – Jun 2026",
            mix_h="Next to Horus Smart Beta", mix_s=f"Monthly returns in EUR, {c['start']} to {c['end']}, rebalanced monthly.",
            mix=f"The value strategy can sit next to Horus Smart Beta 60/40, the multi-asset strategy of Horus AM. In euros the two are correlated at {N(c['corr'])}, and only {N(c['corr_bear'])} in months when world equities fall, because Horus keeps 40% in bonds. A mix lifts the Sharpe ratio to about {N(best['sharpe'])}, from {N(c['mixes'][0]['sharpe'])} for value alone. Horus in euros benefited from a stronger dollar.",
            risk_h="What could go wrong",
            risks=["A long period of expensive-growth leadership: the strategy will lag MSCI World, as in 2023-24.", "Value traps: eight stocks at 3.75% each, some cheap for good reasons (tobacco, autos).", "Sharp V-shaped recoveries: the risk rule sells low and buys back higher.", "Model risk: rules chosen after several rounds look better on paper than they will live."],
            now_h="The portfolio for July 2026",
            now=f"The last data month is June 2026 and the risk rule is fully invested. The core holds Germany, France, Denmark and Hong Kong, and the Health Care, Consumer Staples, Energy and Real Estate sectors. The satellite holds {sat_names}. BNP Paribas is both in the satellite and one of the Thoth Ledger stock pitches: the screen found it, the pitch checks whether the discount is a mispricing.",
            facts=[("Holdings", "8 ETFs + 8 stocks"), ("Weights", "8.75% per ETF, 3.75% per stock"), ("Risk rule", "100% or 50% invested"), ("Rebalancing", "Monthly"), ("Benchmark", "MSCI World Value Net EUR"), ("Backtest", "Feb 2006 – Jun 2026, EUR"), ("CAGR", P(st['cagr'])), ("Volatility", P(st['vol'])), ("Sharpe", N(st['sharpe'])), ("Max drawdown", P(st['mdd'], 0)), ("t vs benchmark", N(D['t_vs_bench'])), ("Months at 50%", f"{D['risk_off_months']} / {D['months']}")],
            facts_h="The numbers",
            refs="References: Asness, Moskowitz & Pedersen (2013), “Value and Momentum Everywhere”, Journal of Finance 68(3), 929-985 · Faber (2007), “A Quantitative Approach to Tactical Asset Allocation”, Journal of Wealth Management 9(4), 69-79 · Bailey & López de Prado (2014), “The Deflated Sharpe Ratio”, Journal of Portfolio Management 40(5), 94-107.",
            disc="Student research by Noah Doose. Thoth Ledger is not an investment firm and offers no product or service. Hypothetical backtest of a model portfolio on monthly total returns in EUR (indices as ETF proxies, stocks with dividends), net of the costs stated, before taxes. Data: Bloomberg (MSCI indices and compositions, valuation ratios, stock returns and fundamentals, euro money-market rates). Past performance does not guarantee future returns. Not investment advice.",
            page="Page")
    return dict(
        mast="Note de stratégie", date="5 novembre 2026", sec="STRATÉGIES SYSTÉMATIQUES · VALUE",
        head="Des marchés bon marché, des actions encore moins chères",
        stand="Une stratégie value construite à deux niveaux — des ETF sur les pays et secteurs bon marché, puis les actions les moins chères à l’intérieur — a battu son indice value sur vingt ans avec à peine plus de la moitié de sa pire perte. Les actions ont fait l’essentiel du travail, et le vrai test commence seulement maintenant.",
        by="Noah Doose", byline="MSc Financial Markets & Investments, SKEMA Business School · candidat au CFA niveau II",
        lead=["Le value a deux problèmes. Le premier est le calendrier : les marchés deviennent bon marché parce qu’ils baissent, et dans un krach ils continuent à baisser ensemble. Le second est la précision : un secteur peut être bon marché alors que beaucoup de ses sociétés ne le sont pas.",
              f"La Rotation Value mondiale, stratégie value officielle publiée sur Thoth Ledger, répond aux deux. Elle détient 70 % en ETF sur les pays et secteurs développés les moins chers, 30 % sur les huit actions les moins chères à l’intérieur, et réduit tout le portefeuille de moitié quand le marché se retourne. De février 2006 à juin 2026, elle a rapporté {P(st['cagr'])} par an net de frais, contre {P(bs['cagr'])} pour son indice, le MSCI World Value en euros, et {P(w2['cagr'])} pour le MSCI World. Sa perte maximale a été de {P(st['mdd'], 0)}, contre {P(bs['mdd'], 0)} et {P(w2['mdd'], 0)} ; son ratio de Sharpe de {N(st['sharpe'])}, contre {N(bs['sharpe'])} et {N(w2['sharpe'])}.",
              f"L’avance tient sur les deux moitiés de la période, mais elle n’est pas statistiquement significative : la statistique t de la surperformance mensuelle est de {N(D['t_vs_bench'])}. La stratégie a battu son indice {AHEAD} années civiles sur {len(cal)}. Elle égale le MSCI World en rendement sur vingt ans, pas depuis 2016.",
              "Ces chiffres méritent autant de méfiance que d’intérêt. Cette note explique comment la stratégie fonctionne, d’où vient son rendement, où elle échoue, et pourquoi le seul test qui compte vraiment a commencé ce mois-ci."],
        how_h="Deux niveaux, une règle de risque",
        how=[("Le cœur (70 %)", "À chaque fin de mois, 25 indices sont notés : 14 pays développés et les 11 secteurs du MSCI World. La note moyenne trois z-scores — rendement bénéficiaire, rendement comptable et rendement du dividende — chacun mesuré par rapport à l’historique propre de l’indice sur dix ans. Les quatre pays et les quatre secteurs les moins chers sont détenus via un ETF UCITS chacun ; une ligne déjà détenue reste tant qu’elle figure parmi les six moins chères."),
             ("Le satellite (30 %)", "Parmi les 300 plus grandes actions du MSCI World à chaque date — y compris celles radiées ou rachetées depuis — le satellite classe chaque société à l’intérieur de son secteur sur l’EV/EBIT, le book-to-price, le rendement du free cash flow et le ratio ventes / EV. Les comptes ne sont utilisés que six mois après la clôture. Il détient les huit actions les moins chères dans les pays ou secteurs détenus par le cœur, deux au plus par secteur et trois par pays, et garde une action tant qu’elle reste parmi les 40 % les moins chères de son secteur."),
             ("La règle de risque", "Trois indicateurs sont vérifiés à chaque fin de mois : MSCI World sous sa moyenne de dix mois, high yield euro en retard sur les obligations d’État courtes, moins de la moitié des 25 lignes en tendance haussière. Quand au moins deux sont rouges, tout le portefeuille est ramené à 50 % d’actions, jamais à zéro, jusqu’à ce que moins de deux le soient."),
             ("Les frais", "Le backtest compte 0,10 % par unité de rotation et 0,25 % par an de frais sur les ETF, 0,15 % par unité de rotation et 0,40 % par an de retenue à la source sur les actions.")],
        g1_h="Croissance de 100 investis fin janvier 2006", g1_s="Échelle logarithmique, EUR, net de frais. En grisé : mois à 50 % d’exposition.",
        leg=("Rotation Value mondiale", "MSCI World Value Net EUR"),
        p2_h="D’où vient le rendement",
        p2=[f"Surtout des actions. Seul, le satellite a rapporté {P(SAT['stats']['cagr'])} par an (t = {N(SAT['t'])} face au MSCI World Value) ; le cœur ETF {P(CORE['stats']['cagr'])} (t = {N(CORE['t'])}). Au niveau des pays et des secteurs, le coefficient d’information de rang à douze mois du score value a été proche de zéro (−0,05 pour les pays, −0,03 pour les secteurs). Un ETF sectoriel détient des centaines de sociétés et elles ne peuvent pas toutes être bon marché : c’est en classant les actions à l’intérieur de leur secteur que le signal devient assez précis pour payer.",
             f"Le cœur apporte la maîtrise du risque. La règle a tenu le portefeuille à 50 % pendant {D['risk_off_months']} mois sur {D['months']}, en {D['switches']} bascules. En 2008, la stratégie a perdu {P(abs(cal['2008']))} quand le MSCI World Value perdait {P(abs(bcal['2008']))} ; en 2022, elle a gagné {P(cal['2022'], 1, True)} quand le MSCI World perdait {P(abs(wcal['2022']))}.",
             f"La règle a un coût, payé dans les rebonds rapides : {P(cal['2020'], 1, True)} en 2020 contre {P(wcal['2020'], 1, True)} pour le MSCI World. Et quand la croissance chère mène, le value est distancé quelle que soit la règle : {P(cal['2023'], 1, True)} en 2023 et {P(cal['2024'], 1, True)} en 2024, contre {P(wcal['2023'], 1, True)} et {P(wcal['2024'], 1, True)}."],
        g2_h="Baisse depuis le précédent sommet (%)", g3_h="Rendements par année civile (%)", g3_s="06-26 = 2006-2026 ; 2026 jusqu’à juin.",
        p3_h="Deux moitiés, deux histoires",
        p3=[f"La recherche a été organisée autour d’une période de conception (2006-2015) et d’une période de validation (2016-2026). Dans la première, la stratégie a rapporté {P(d['cagr'])} par an contre {P(bd['cagr'])} pour le MSCI World Value, surtout en perdant moins en 2008. Dans la seconde, {P(v['cagr'])} contre {P(bv['cagr'])}, avec un satellite à {P(SAT['halves']['valid']['cagr'])}.",
             f"L’indice de référence est le MSCI World Value parce que la stratégie est une stratégie value. Le MSCI World a rapporté le même {P(w2['cagr'])} par an sur vingt ans, mais bien plus depuis 2016 ({P(W2V)} par an) : il reste donc affiché partout comme la véritable alternative de l’investisseur. Face à lui, la stratégie offre à peu près le même rendement avec une perte maximale de {P(st['mdd'], 0)} au lieu de {P(w2['mdd'], 0)}."],
        p4_h="Comment elle a été construite — et pourquoi c’est important",
        p4=["Les premières règles ont été fixées le 30 octobre 2026, avant toute extraction de données : quatre pays et quatre secteurs, sans règle de risque. Elles ont fait mieux que l’indice, avec presque la même perte maximale de 50 %. Chaque étape suivante a été écrite et déposée dans le dépôt de code avant d’être lancée : un tampon de détention et un filtre de tendance (V4c), une version à trois secteurs (V5), la règle de risque à 50 % au lieu d’un passage tout-ou-rien en cash (V7), et enfin le satellite actions, dont l’univers, le score et les règles ont été fixés avant le premier résultat.",
             "Chaque étape a été choisie après avoir vu les résultats précédents sur toute la période : 2016-2026 n’est donc pas un test hors échantillon propre, et le lecteur doit décoter le ratio de Sharpe du nombre d’essais (Bailey et López de Prado, 2014). Le test propre est le suivi réel à partir de novembre 2026 ; la factsheet mensuelle le publiera sans réécrire le backtest."],
        vt_h="Les principales versions, fév. 2006 – juin 2026",
        mix_h="À côté d’Horus Smart Beta", mix_s=f"Rendements mensuels en EUR, {c['start']} à {c['end']}, rebalancés chaque mois.",
        mix=f"La stratégie value peut s’associer à Horus Smart Beta 60/40, la stratégie multi-actifs d’Horus AM. En euros, les deux sont corrélées à {N(c['corr'])}, et à seulement {N(c['corr_bear'])} les mois où les actions mondiales baissent, car Horus garde 40 % d’obligations. Un mélange porte le ratio de Sharpe à environ {N(best['sharpe'])}, contre {N(c['mixes'][0]['sharpe'])} pour la value seule. Horus en euros a profité de la hausse du dollar.",
        risk_h="Ce qui peut mal tourner",
        risks=["Une longue domination de la croissance chère : la stratégie sera distancée par le MSCI World, comme en 2023-24.", "Les pièges à valeur : huit actions à 3,75 % chacune, certaines bon marché pour de bonnes raisons (tabac, automobile).", "Les reprises rapides en V : la règle de risque vend bas et rachète plus haut.", "Le risque de modèle : des règles choisies après plusieurs séries d’essais paraissent meilleures sur le papier qu’elles ne le seront en réel."],
        now_h="Le portefeuille de juillet 2026",
        now=f"Le dernier mois de données est juin 2026 et la règle de risque est investie à 100 %. Le cœur détient l’Allemagne, la France, le Danemark et Hong Kong, ainsi que les secteurs Santé, Consommation de base, Énergie et Immobilier. Le satellite détient {sat_names}. BNP Paribas est à la fois dans le satellite et parmi les stock pitches de Thoth Ledger : le screen l’a trouvée, le pitch vérifie si la décote est une erreur de prix.",
        facts=[("Positions", "8 ETF + 8 actions"), ("Poids", "8,75 % par ETF, 3,75 % par action"), ("Règle de risque", "investi à 100 % ou 50 %"), ("Rebalancement", "Mensuel"), ("Indice", "MSCI World Value Net EUR"), ("Backtest", "fév. 2006 – juin 2026, EUR"), ("CAGR", P(st['cagr'])), ("Volatilité", P(st['vol'])), ("Sharpe", N(st['sharpe'])), ("Perte maximale", P(st['mdd'], 0)), ("t vs indice", N(D['t_vs_bench'])), ("Mois à 50 %", f"{D['risk_off_months']} / {D['months']}")],
        facts_h="Les chiffres",
        refs="Références : Asness, Moskowitz et Pedersen (2013), « Value and Momentum Everywhere », Journal of Finance 68(3), 929-985 · Faber (2007), « A Quantitative Approach to Tactical Asset Allocation », Journal of Wealth Management 9(4), 69-79 · Bailey et López de Prado (2014), « The Deflated Sharpe Ratio », Journal of Portfolio Management 40(5), 94-107.",
        disc="Travail de recherche étudiant de Noah Doose. Thoth Ledger n’est pas une société de gestion et ne propose aucun produit ni service. Backtest hypothétique d’un portefeuille modèle sur les rendements totaux mensuels en EUR (indices comme proxys des ETF, actions dividendes inclus), net des frais indiqués, avant impôts. Données : Bloomberg (indices et compositions MSCI, ratios de valorisation, rendements et comptes des actions, taux monétaires euro). Les performances passées ne préjugent pas des performances futures. Ceci n’est pas un conseil en investissement.",
        page="Page")


def html(lang):
    T = text(lang)
    logo = base64.b64encode((ROOT / "site/static/brand/mark_256.png").read_bytes()).decode()
    paras = lambda xs: "".join(f"<p>{x}</p>" for x in xs)
    how = "".join(f'<div class="how"><b>{a}.</b> {b}</div>' for a, b in T["how"])
    facts = "".join(f"<tr><td>{a}</td><td>{b}</td></tr>" for a, b in T["facts"])
    risks = "".join(f"<li>{x}</li>" for x in T["risks"])
    mast = lambda n: f'<div class="mast"><img src="data:image/png;base64,{logo}"><span class="brand">THOTH LEDGER</span><span class="m">{T["mast"]} · {T["date"]}</span><span class="pg">{T["page"]} {n}/3</span></div>'
    leg = f'<div class="leg"><i style="background:{CLARET}"></i>{T["leg"][0]}<i style="background:{BLUE}"></i>{T["leg"][1]}</div>'
    return f"""<!doctype html><html lang="{lang}"><head><meta charset="utf-8"><style>{font_css()}
@page{{size:A4;margin:0}}*{{box-sizing:border-box}}
body{{margin:0;background:{SALMON};color:{INK};font:400 9.2pt/1.45 'Source Sans 3',Georgia,serif}}
.page{{width:210mm;height:297mm;padding:11mm 14mm 10mm;position:relative;page-break-after:always;background:{SALMON}}}
.mast{{display:flex;align-items:center;gap:8px;border-bottom:2px solid {INK};padding-bottom:5px;font-size:7.5pt}}
.mast img{{width:22px;height:22px}}.brand{{font:700 13pt 'Cormorant Garamond';letter-spacing:.14em}}.mast .m{{margin-left:12px;color:#66605C}}.mast .pg{{margin-left:auto;color:#66605C}}
.sec{{font:700 7pt 'Source Sans 3';letter-spacing:.14em;color:{CLARET};margin:10px 0 2px}}
h1{{font:700 31pt/1.02 'Cormorant Garamond',serif;margin:2px 0 6px;color:#1A1817}}
.stand{{font:500 13pt/1.32 'Cormorant Garamond',serif;color:#4D4845;margin:0 0 8px}}
.by{{font-size:8pt;border-top:1px solid #CCC1B7;border-bottom:1px solid #CCC1B7;padding:4px 0;margin-bottom:9px}}.by b{{color:{CLARET}}}
.cols{{column-count:2;column-gap:7mm}}p{{margin:0 0 6px;text-align:left}}
.cols p:first-child::first-letter{{font:700 30pt/0.8 'Cormorant Garamond';float:left;padding:4px 5px 0 0;color:{CLARET}}}
h2{{font:700 13pt/1.15 'Cormorant Garamond';margin:9px 0 4px;color:#1A1817;break-after:avoid}}
.how{{margin:0 0 5px;padding-left:8px;border-left:2px solid {CLARET}}}
.fig{{border-top:3px solid {INK};margin:8px 0 6px;padding-top:4px;break-inside:avoid}}.fig .t{{font:700 9.5pt 'Source Sans 3'}}.fig .s{{font-size:7.3pt;color:#66605C}}
.fig svg{{width:100%;height:auto;display:block;margin-top:3px}}svg text{{font:6.8pt 'Source Sans 3';fill:#66605C}}
.leg{{font-size:7.3pt;color:#4D4845;margin-top:2px}}.leg i{{display:inline-block;width:12px;height:3px;vertical-align:middle;margin:0 4px 0 8px}}.leg i:first-child{{margin-left:0}}
.src{{font-size:6.6pt;color:#66605C;margin-top:2px}}
.box{{background:#F2DFCE;padding:7px 9px;margin:6px 0;break-inside:avoid}}.box h3{{font:700 10pt 'Cormorant Garamond';margin:0 0 3px;color:{CLARET};letter-spacing:.04em;text-transform:uppercase}}
table{{width:100%;border-collapse:collapse;font-size:7.6pt}}td,th{{padding:2.2px 3px;border-bottom:.5px solid #CCC1B7;text-align:left}}
.facts td:last-child{{text-align:right;font-weight:600}}.vt td:not(:first-child),.vt th:not(:first-child){{text-align:right;font-variant-numeric:tabular-nums}}
.vt th{{font-weight:700;border-bottom:1.2px solid {INK}}}.vt tr.hl td{{font-weight:700;color:{CLARET}}}.vt tr.b td{{color:#66605C;font-style:italic}}
ul{{margin:0;padding-left:13px}}li{{margin-bottom:3px}}
.foot{{position:absolute;left:14mm;right:14mm;bottom:7mm;font-size:6.5pt;color:#66605C;border-top:1px solid #CCC1B7;padding-top:4px}}
</style></head><body>
<div class="page">{mast(1)}
 <div class="sec">{T['sec']}</div><h1>{T['head']}</h1><p class="stand">{T['stand']}</p>
 <div class="by"><b>{T['by']}</b> · {T['byline']}</div>
 <div class="cols">{paras(T['lead'])}
  <div class="fig"><div class="t">{T['g1_h']}</div><div class="s">{T['g1_s']}</div>{growth_svg(lang)}{leg[:-6]}<i style="background:#8C8279"></i>MSCI World Net EUR</div><div class="src">Source: Bloomberg, Thoth Ledger</div></div>
  <h2>{T['how_h']}</h2>{how}
 </div>
 <div class="foot">{T['disc']}</div>
</div>
<div class="page">{mast(2)}
 <div class="cols" style="margin-top:8px">
  <h2 style="margin-top:0">{T['p2_h']}</h2>{paras(T['p2'])}
  <div class="fig"><div class="t">{T['g2_h']}</div>{dd_svg(lang)}{leg}</div>
  <div class="fig"><div class="t">{T['g3_h']}</div><div class="s">{T['g3_s']}</div>{cal_svg(lang)}{leg}</div>
  <h2>{T['p3_h']}</h2>{paras(T['p3'])}
  <div class="box"><h3>{T['facts_h']}</h3><table class="facts">{facts}</table></div>
  <div class="box"><h3>{T['mix_h']}</h3><p>{T['mix']}</p>{mix_table(lang)}<div class="src">{T['mix_s']}</div></div>
 </div>
 <div class="foot">{T['disc']}</div>
</div>
<div class="page">{mast(3)}
 <div class="cols" style="margin-top:8px">
  <h2 style="margin-top:0">{T['p4_h']}</h2>{paras(T['p4'])}
  <div class="fig"><div class="t">{T['vt_h']}</div>{versions_table(lang)}<div class="src">{'Net of costs, EUR. 2006-15 and 2016-26: CAGR of each half.' if lang == 'en' else 'Net de frais, EUR. 2006-15 et 2016-26 : CAGR de chaque moitié.'}</div></div>
  <h2>{T['risk_h']}</h2><ul>{risks}</ul>
  <h2>{T['now_h']}</h2><p>{T['now']}</p>
  <p class="src" style="margin-top:8px">{T['refs']}</p>
 </div>
 <div class="foot">{T['disc']}</div>
</div></body></html>"""


def main():
    from playwright.sync_api import sync_playwright
    OUT.mkdir(parents=True, exist_ok=True)
    with sync_playwright() as p:
        br = p.chromium.launch()
        for lang in ("en", "fr"):
            pg = br.new_page(); pg.set_content(html(lang), wait_until="networkidle")
            f = OUT / f"Thoth_GlobalValueRotation_StrategyNote_{lang.upper()}.pdf"
            pg.pdf(path=str(f), format="A4", print_background=True); print(f)
        br.close()


if __name__ == "__main__":
    main()
