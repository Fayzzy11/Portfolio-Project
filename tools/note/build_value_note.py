"""Strategy note in a Financial Times-like layout (English and French) for the Global Value Rotation (V4c).
Reads site/data/etf_strategies.json (aggregated results) and data/etf/v4c_full.pkl (private, for the risk-off shading).
    python3 tools/note/build_value_note.py <out_dir>
"""
import json, sys, base64, math
from pathlib import Path
import pandas as pd
ROOT = Path(__file__).resolve().parents[2]
D = json.loads((ROOT / "site/data/etf_strategies.json").read_text())["value"]
VAR = json.loads((ROOT / "site/data/etf_strategies.json").read_text())["variants"]
P = pd.read_pickle(ROOT / "data/etf/v4c_full.pkl")
on = P["on"].shift(1).reindex(P["r"].index).fillna(True)          # state during each month
OUT = Path(sys.argv[1] if len(sys.argv) > 1 else ".")
FONTS = Path("/home/claude/work/fonts/node_modules/@fontsource")
dates, nav, bnav = D["dates"], D["nav"], D["bench"]
st, bs, hv = D["stats"], D["bench_stats"], D["halves"]
cal, bcal = D["calendar"], D["bench_calendar"]


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
    s = [100.0] + [100 * x for x in nav]; q = [100.0] + [100 * x for x in bnav]
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
    for i, d in enumerate(["2005-12"] + dates):
        if d.endswith("-12") and (int(d[:4]) + 1) % 4 == 2:
            g += f'<text x="{X(i):.1f}" y="{H - 7}" text-anchor="middle">{int(d[:4]) + 1}</text>'
    p = lambda a: "M" + " L".join(f"{X(i):.1f} {Y(v):.1f}" for i, v in enumerate(a))
    g += f'<path d="{p(q)}" fill="none" stroke="{BLUE}" stroke-width="1.6"/><path d="{p(s)}" fill="none" stroke="{CLARET}" stroke-width="2.1"/>'
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
    for i, d in enumerate(["2005-12"] + dates):
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
    names_fr = {"V1 Rules (validated 30 Oct)": "V1 Règles (validées le 30/10)", "V6 Rules + market trend filter": "V6 Règles + filtre de tendance",
                "VB 50% MSCI World + 50% V6": "VB 50 % MSCI World + 50 % V6", "V3 Cap-weighted world, value tilt": "V3 Monde pondéré, incliné value",
                "V4b Per-line trend filter": "V4b Filtre ligne par ligne", "V4c Buffer + market trend filter (official)": "V4c Tampon + filtre de tendance (officielle)",
                "V4d 12 tranches + market trend filter": "V4d 12 tranches + filtre", "V4e 12 tranches + filter, bonds risk-off": "V4e 12 tranches + filtre, refuge obligataire",
                "MSCI World Net EUR": "MSCI World Net EUR"}
    rows = ""
    for v in VAR:
        n = names_fr.get(v["name"], v["name"]) if lang == "fr" else v["name"]
        cls = ' class="hl"' if "official" in v["name"] else (' class="b"' if v["name"].startswith("MSCI") else "")
        rows += f'<tr{cls}><td>{n}</td><td>{pc(v["cagr"], lang)}</td><td>{nm(v["sharpe"], lang)}</td><td>{pc(v["mdd"], lang, 0)}</td><td>{pc(v["design_cagr"], lang)}</td><td>{pc(v["valid_cagr"], lang)}</td></tr>'
    h = ["Version", "CAGR", "Sharpe", "Max DD", "2006-15", "2016-26"]
    return "<table class='vt'><tr>" + "".join(f"<th>{x}</th>" for x in h) + "</tr>" + rows + "</table>"


def text(lang):
    d, v, bd, bv = hv["design"], hv["valid"], hv["bench_design"], hv["bench_valid"]
    P = lambda x, k=1, s=False: pc(x, lang, k, s)
    if lang == "en":
        return dict(
            mast="Strategy note", date="4 November 2026", sec="SYSTEMATIC STRATEGIES · VALUE",
            head="Buy what is cheap, but not in a crash",
            stand=f"A two-rule rotation across developed countries and sectors kept most of world equities' return over twenty years with less than half of their worst loss. It still trailed the index over the past decade — and the clean test only starts now.",
            by="Noah Doose", byline="MSc Financial Markets & Investments, SKEMA Business School · CFA Level II candidate",
            lead=[f"Value investing has a timing problem. Markets become cheap because they are falling, and in a crash they can keep falling together. A country-and-sector value rotation that held on through 2008 lost half its value; one that simply waited for world equities to recover their trend lost {P(abs(st['mdd']), 0)} at worst.",
                  f"That is the idea behind the Global Value Rotation, the official version of the value strategy published on Thoth Ledger: <b>value decides what to hold, trend decides when to hold it.</b> Over January 2006 to September 2026 it returned {P(st['cagr'])} a year net of costs, against {P(bs['cagr'])} for MSCI World in euros, with a volatility of {P(st['vol'])} instead of {P(bs['vol'])} and a worst drawdown of {P(st['mdd'], 0)} instead of {P(bs['mdd'], 0)}. Its Sharpe ratio was {nm(st['sharpe'], lang)}, against {nm(bs['sharpe'], lang)}.",
                  "Those numbers deserve as much suspicion as interest. This note explains how the strategy works, where its return comes from, where it fails, and why the only test that really counts started this month."],
            how_h="Two rules, one ETF per line",
            how=[("What to hold", "At each month end, 25 indices are scored: 14 developed countries and the 11 sectors of MSCI World. The score averages three z-scores — earnings yield, book yield and dividend yield — each measured against the index's own ten-year history. A market is cheap when it is cheap against its own past, so structurally cheap markets are not bought forever."),
                 ("Which lines", "The four cheapest countries and the four cheapest sectors are bought at 12.5% each. A line already held stays until it drops out of the six cheapest: value pays over years, and selling a cheap market because another became marginally cheaper only adds trading."),
                 ("When to hold", "If MSCI World ends the month below its ten-month moving average, the whole portfolio moves to the euro money market until the index closes back above it. The rule is old (Faber, 2007) and deliberately crude: it is meant to sidestep long bear markets, not to time corrections."),
                 ("How to hold", "Each line is a UCITS ETF listed in euros. The backtest charges 0.10% per unit of turnover and 0.25% a year of ETF fees; turnover was " + P(D['turnover'], 0) + " a year, two-way.")],
            g1_h="Growth of 100 invested in December 2005", g1_s="Log scale, EUR, net of costs. Shaded: months spent in cash.",
            leg=("Global Value Rotation", "MSCI World Net EUR"),
            p2_h="Where the return comes from",
            p2=[f"The trend filter does most of the work. It kept the portfolio in cash for {D['risk_off_months']} of {D['months']} months, in {D['switches']} switches. In 2008 the strategy made {P(cal['2008'], 1, True)} while world equities lost {P(abs(bcal['2008']))}; in 2022 it lost {P(abs(cal['2022']))} against {P(abs(bcal['2022']))}. Those two years alone explain most of the gap in drawdown.",
                 f"The filter also has a cost, paid in quick rebounds. It sold near the bottom in March 2020 and bought back late: {P(cal['2020'], 1, True)} that year against {P(bcal['2020'], 1, True)} for the index. In 2023 the market recovered from a correction that the filter had treated as the start of a bear market ({P(cal['2023'], 1, True)} against {P(bcal['2023'], 1, True)}).",
                 "The value score contributes less than the name suggests. At country and sector level its twelve-month rank information coefficient was close to zero (−0.05 for countries, −0.03 for sectors). Where it does help is in what it avoids: the strategy almost never held the most expensive markets, which kept it away from the US technology sector at its peaks — a protection in 2022, a heavy cost in 2023-24."],
            g2_h="Drawdown from previous peak (%)", g3_h="Calendar-year returns (%)", g3_s="20-26 = 2020-2026; 2026 to September.",
            p3_h="Two halves, two stories",
            p3=[f"The research was organised around a design half (2006-2015) and a validation half (2016-2026). In the first, the strategy earned {P(d['cagr'])} a year against {P(bd['cagr'])} for MSCI World. In the second, {P(v['cagr'])} against {P(bv['cagr'])}. The decade of US mega-cap leadership is exactly the environment in which an equal-weighted value rotation, which under-owns the US by construction, should lag — and it did.",
                 "That is why the benchmark is now MSCI World Value, chosen because the strategy is a value strategy rather than because it is easier to beat. MSCI World Value itself trailed MSCI World by about 2.5 points a year over the ten years to September 2026 (10.85% against 13.37% gross in USD, MSCI factsheet). MSCI World remains on every page as the investor's real alternative."],
            p4_h="How it was built — and why that matters",
            p4=["Every version was written down before it was run. The first rules were fixed on 30 October 2026, before any data were extracted. They lost to the index with the same drawdown. Three further rounds followed, each pre-registered and committed to the code repository before the first result: a fifty-fifty mix with an index fund, a capitalisation-weighted tilt, a per-line trend filter, overlapping twelve-month tranches and a bond refuge. Eleven value versions in all; the main ones are below.",
                 "V4c was chosen among four candidates after seeing both halves. Its 2016-2026 numbers are therefore not a clean out-of-sample test of that choice, and a reader should haircut the Sharpe ratio for the number of trials (Bailey and López de Prado, 2014). The clean test is the live record that starts in November 2026; the monthly factsheet will report it without restating the backtest."],
            vt_h="Every value version tested, 2006-2026",
            risk_h="What could go wrong",
            risks=["A long period of expensive-growth leadership: the strategy will lag, as in 2016-2026.", "Sharp V-shaped recoveries: the filter sells low and buys back higher.", "Overlap: a cheap sector and a cheap country can be the same bet (Financials and Italy).", "Model risk: rules chosen after eleven trials look better on paper than they will live."],
            now_h="The portfolio for November 2026",
            now="The trend filter is invested. The value selection holds Germany, France, Denmark and Hong Kong, and the Consumer Staples, Energy, Utilities and Real Estate sectors. France is where three of the Thoth Ledger stock pitches sit (Renault, BNP Paribas, Carrefour), and Carrefour is also in Consumer Staples: the top-down rotation and the bottom-up research point to the same place.",
            facts=[("Universe", "14 MSCI countries, 11 MSCI World sectors"), ("Holdings", "8 ETFs at 12.5%, or cash"), ("Rebalancing", "Monthly"), ("Benchmark", "MSCI World Value Net EUR (MSCI World shown)"), ("Backtest", "Jan 2006 – Sep 2026, EUR"), ("CAGR", P(st['cagr'])), ("Volatility", P(st['vol'])), ("Sharpe", nm(st['sharpe'], lang)), ("Max drawdown", P(st['mdd'], 0)), ("Months in cash", f"{D['risk_off_months']} / {D['months']}")],
            facts_h="The numbers",
            refs="References: Asness, Moskowitz & Pedersen (2013), “Value and Momentum Everywhere”, Journal of Finance 68(3), 929-985 · Faber (2007), “A Quantitative Approach to Tactical Asset Allocation”, Journal of Wealth Management 9(4), 69-79 · Bailey & López de Prado (2014), “The Deflated Sharpe Ratio”, Journal of Portfolio Management 40(5), 94-107 · MSCI World Value Index factsheet, 30 September 2026.",
            disc="Student research by Noah Doose. Thoth Ledger is not an investment firm and offers no product or service. Hypothetical backtest of a model portfolio on monthly index total returns in EUR (ETFs as proxies), net of the costs stated, before taxes. Data: Bloomberg (MSCI indices, valuation ratios, euro money-market rates). Past performance does not guarantee future returns. Not investment advice.",
            page="Page")
    return dict(
        mast="Note de stratégie", date="4 novembre 2026", sec="STRATÉGIES SYSTÉMATIQUES · VALUE",
        head="Acheter bon marché, mais pas pendant un krach",
        stand="Une rotation à deux règles entre pays et secteurs développés a conservé l’essentiel du rendement des actions mondiales sur vingt ans, avec moins de la moitié de leur pire perte. Elle reste distancée par l’indice sur la dernière décennie — et le vrai test commence seulement maintenant.",
        by="Noah Doose", byline="MSc Financial Markets & Investments, SKEMA Business School · candidat au CFA niveau II",
        lead=[f"Le value a un problème de calendrier. Les marchés deviennent bon marché parce qu’ils baissent, et dans un krach ils peuvent continuer à baisser ensemble. Une rotation value entre pays et secteurs qui serait restée investie en 2008 aurait perdu la moitié de sa valeur ; celle qui a simplement attendu que les actions mondiales retrouvent leur tendance a perdu au pire {P(abs(st['mdd']), 0)}.",
              f"C’est l’idée de la Rotation Value mondiale, version officielle de la stratégie value publiée sur Thoth Ledger : <b>le value décide quoi détenir, la tendance décide quand le détenir.</b> De janvier 2006 à septembre 2026, elle a rapporté {P(st['cagr'])} par an net de frais, contre {P(bs['cagr'])} pour le MSCI World en euros, avec une volatilité de {P(st['vol'])} au lieu de {P(bs['vol'])} et une perte maximale de {P(st['mdd'], 0)} au lieu de {P(bs['mdd'], 0)}. Son ratio de Sharpe a été de {nm(st['sharpe'], lang)}, contre {nm(bs['sharpe'], lang)}.",
              "Ces chiffres méritent autant de méfiance que d’intérêt. Cette note explique comment la stratégie fonctionne, d’où vient son rendement, où elle échoue, et pourquoi le seul test qui compte vraiment a commencé ce mois-ci."],
        how_h="Deux règles, un ETF par ligne",
        how=[("Quoi détenir", "À chaque fin de mois, 25 indices sont notés : 14 pays développés et les 11 secteurs du MSCI World. La note moyenne trois z-scores — rendement bénéficiaire, rendement comptable et rendement du dividende — chacun mesuré par rapport à l’historique propre de l’indice sur dix ans. Un marché est bon marché quand il l’est par rapport à son propre passé : les marchés structurellement peu chers ne sont pas achetés éternellement."),
             ("Quelles lignes", "Les quatre pays et les quatre secteurs les moins chers sont achetés à 12,5 % chacun. Une ligne déjà détenue reste en portefeuille tant qu’elle figure parmi les six moins chères : le value paie sur des années, et vendre un marché bon marché parce qu’un autre l’est devenu un peu plus ne fait qu’ajouter des transactions."),
             ("Quand détenir", "Si le MSCI World termine le mois sous sa moyenne mobile de dix mois, tout le portefeuille passe en monétaire euro jusqu’à ce que l’indice repasse au-dessus. La règle est ancienne (Faber, 2007) et volontairement rudimentaire : elle sert à éviter les longs marchés baissiers, pas à anticiper les corrections."),
             ("Comment détenir", "Chaque ligne est un ETF UCITS coté en euros. Le backtest compte 0,10 % par unité de rotation et 0,25 % par an de frais d’ETF ; la rotation a été de " + P(D['turnover'], 0) + " par an, achats et ventes cumulés.")],
        g1_h="Croissance de 100 investis en décembre 2005", g1_s="Échelle logarithmique, EUR, net de frais. En grisé : mois passés en cash.",
        leg=("Rotation Value mondiale", "MSCI World Net EUR"),
        p2_h="D’où vient le rendement",
        p2=[f"Le filtre de tendance fait l’essentiel du travail. Il a laissé le portefeuille en cash {D['risk_off_months']} mois sur {D['months']}, en {D['switches']} bascules. En 2008, la stratégie a gagné {P(cal['2008'], 1, True)} quand les actions mondiales perdaient {P(abs(bcal['2008']))} ; en 2022, elle a perdu {P(abs(cal['2022']))} contre {P(abs(bcal['2022']))}. Ces deux années expliquent à elles seules la plus grande partie de l’écart de perte maximale.",
             f"Le filtre a aussi un coût, payé dans les rebonds rapides. Il a vendu près du point bas en mars 2020 et racheté tard : {P(cal['2020'], 1, True)} cette année-là contre {P(bcal['2020'], 1, True)} pour l’indice. En 2023, le marché s’est repris après une correction que le filtre avait traitée comme le début d’un marché baissier ({P(cal['2023'], 1, True)} contre {P(bcal['2023'], 1, True)}).",
             "Le score value apporte moins que son nom ne le laisse penser. Au niveau des pays et des secteurs, son coefficient d’information de rang à douze mois a été proche de zéro (−0,05 pour les pays, −0,03 pour les secteurs). Son apport tient surtout à ce qu’il évite : la stratégie n’a presque jamais détenu les marchés les plus chers, ce qui l’a tenue à l’écart de la technologie américaine à ses sommets — une protection en 2022, un coût lourd en 2023-24."],
        g2_h="Baisse depuis le précédent sommet (%)", g3_h="Rendements par année civile (%)", g3_s="20-26 = 2020-2026 ; 2026 jusqu’à septembre.",
        p3_h="Deux moitiés, deux histoires",
        p3=[f"La recherche a été organisée autour d’une période de conception (2006-2015) et d’une période de validation (2016-2026). Dans la première, la stratégie a rapporté {P(d['cagr'])} par an contre {P(bd['cagr'])} pour le MSCI World. Dans la seconde, {P(v['cagr'])} contre {P(bv['cagr'])}. La décennie des mégacaps américaines est précisément l’environnement où une rotation value équipondérée, qui sous-pondère les États-Unis par construction, devait être distancée — et elle l’a été.",
             "C’est pourquoi l’indice de référence est désormais le MSCI World Value, retenu parce que la stratégie est une stratégie value, et non parce qu’il serait plus facile à battre. Le MSCI World Value a lui-même été distancé par le MSCI World d’environ 2,5 points par an sur les dix ans à fin septembre 2026 (10,85 % contre 13,37 % brut en USD, factsheet MSCI). Le MSCI World reste affiché partout comme la véritable alternative de l’investisseur."],
        p4_h="Comment elle a été construite — et pourquoi c’est important",
        p4=["Chaque version a été écrite avant d’être lancée. Les premières règles ont été fixées le 30 octobre 2026, avant toute extraction de données. Elles ont fait moins bien que l’indice, avec la même perte maximale. Trois autres séries ont suivi, chacune pré-enregistrée et déposée dans le dépôt de code avant le premier résultat : un mélange à parts égales avec un fonds indiciel, une inclinaison sur les poids du marché, un filtre de tendance ligne par ligne, des tranches de douze mois et un refuge obligataire. Onze versions value au total ; les principales figurent ci-dessous.",
             "V4c a été choisie parmi quatre candidates après avoir vu les deux moitiés. Ses chiffres 2016-2026 ne sont donc pas un test hors échantillon propre de ce choix, et le lecteur doit décoter le ratio de Sharpe du nombre d’essais (Bailey et López de Prado, 2014). Le test propre est le suivi réel qui commence en novembre 2026 ; la factsheet mensuelle le publiera sans réécrire le backtest."],
        vt_h="Toutes les versions value testées, 2006-2026",
        risk_h="Ce qui peut mal tourner",
        risks=["Une longue domination de la croissance chère : la stratégie sera distancée, comme en 2016-2026.", "Les reprises rapides en V : le filtre vend bas et rachète plus haut.", "Les recoupements : un secteur et un pays bon marché peuvent être le même pari (Finance et Italie).", "Le risque de modèle : des règles choisies après onze essais paraissent meilleures sur le papier qu’elles ne le seront en réel."],
        now_h="Le portefeuille de novembre 2026",
        now="Le filtre de tendance est investi. La sélection value détient l’Allemagne, la France, le Danemark et Hong Kong, ainsi que les secteurs Consommation de base, Énergie, Services aux collectivités et Immobilier. La France est le pays de trois stock pitches de Thoth Ledger (Renault, BNP Paribas, Carrefour), et Carrefour est aussi dans la Consommation de base : la rotation top-down et la recherche bottom-up pointent au même endroit.",
        facts=[("Univers", "14 pays MSCI, 11 secteurs MSCI World"), ("Positions", "8 ETF à 12,5 %, ou cash"), ("Rebalancement", "Mensuel"), ("Indice", "MSCI World Value Net EUR (MSCI World affiché)"), ("Backtest", "janv. 2006 – sept. 2026, EUR"), ("CAGR", P(st['cagr'])), ("Volatilité", P(st['vol'])), ("Sharpe", nm(st['sharpe'], lang)), ("Perte maximale", P(st['mdd'], 0)), ("Mois en cash", f"{D['risk_off_months']} / {D['months']}")],
        facts_h="Les chiffres",
        refs="Références : Asness, Moskowitz et Pedersen (2013), « Value and Momentum Everywhere », Journal of Finance 68(3), 929-985 · Faber (2007), « A Quantitative Approach to Tactical Asset Allocation », Journal of Wealth Management 9(4), 69-79 · Bailey et López de Prado (2014), « The Deflated Sharpe Ratio », Journal of Portfolio Management 40(5), 94-107 · Factsheet MSCI World Value Index, 30 septembre 2026.",
        disc="Travail de recherche étudiant de Noah Doose. Thoth Ledger n’est pas une société de gestion et ne propose aucun produit ni service. Backtest hypothétique d’un portefeuille modèle sur les rendements totaux mensuels d’indices en EUR (ETF comme proxys), net des frais indiqués, avant impôts. Données : Bloomberg (indices MSCI, ratios de valorisation, taux monétaires euro). Les performances passées ne préjugent pas des performances futures. Ceci n’est pas un conseil en investissement.",
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
  <div class="fig"><div class="t">{T['g1_h']}</div><div class="s">{T['g1_s']}</div>{growth_svg(lang)}{leg}<div class="src">Source: Bloomberg, Thoth Ledger</div></div>
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
