"""French version of the final Intel course deck (Doose & Endrizzi, Nov 2026).

Keeps the layout of the final English file and replaces the text run by run.

    python3 tools/pitch_intc/intc_final_fr.py <final_en.pptx> <out_fr.pptx>
"""
import re
import sys

from pptx import Presentation

NB = " "

T = {
    "INITIATING COVERAGE  ·  INTEL CORPORATION (NASDAQ: INTC)": "INITIATION DE COUVERTURE  ·  INTEL CORPORATION (NASDAQ : INTC)",
    "The 2026 margin peak is behind us": "Le pic de marge 2026 est passé",
    "The Street still prices a shortage windfall as if it were permanent": "Le consensus valorise encore une aubaine de pénurie comme si elle était durable",
    "SELL": "VENDRE",
    "Rating": "Recommandation",
    "12–18m price target": "Objectif de cours 12-18 mois",
    "Price, 6 Nov 2026": "Cours, 6 nov. 2026",
    "Downside": "Baisse",
    "Noah Doose & Victor Endrizzi  ·  Equity Research, SKEMA MSc FMI (Paul Wuh)  ·  9–10 November 2026":
        "Noah Doose & Victor Endrizzi  ·  Equity Research, SKEMA MSc FMI (Paul Wuh)  ·  9-10 novembre 2026",
    "Sell: 2026 margins were a shortage windfall – EPS 25% below the Street":
        "Vendre : les marges 2026 étaient une aubaine de pénurie – BPA 25 % sous le consensus",
    "OUR CALL": "NOTRE AVIS",
    "Target (12–18m)": "Objectif (12-18 mois)",
    "Price": "Cours",
    "2027E EPS vs Street": "BPA 2027E vs consensus",
    "Peak margins, not a new base": "Un pic, pas une nouvelle base",
    "Q4 guide 38% vs 42.5% in 2027 consensus → EPS → P/E": "Guidance T4 38 % vs 42,5 % dans le consensus 2027 → BPA → PER",
    "2027E EPS $1.33 vs\xa0$1.78": "BPA 2027E 1,33 $ vs\xa01,78 $",
    "Servers capped, PCs shrink": "Serveurs plafonnés, PC en recul",
    "Servers Intel can't supply; PCs (~half of revenue) fall → revenue → EPS":
        "Serveurs non livrables ; les PC (~la moitié du CA) reculent → CA → BPA",
    "Client revenue –9% in 2027E": "CA Client –9 % en 2027E",
    "Capex and dilution eat the cash": "Capex et dilution pèsent",
    "Capex up strongly; shares +29% since 2023 → FCF and EPS → multiple":
        "Capex en forte hausse ; actions +29 % depuis 2023 → FCF et BPA → multiple",
    "2027E free cash flow –$5.7bn": "Free cash flow 2027E –5,7 Md$",
    "Fixed-cost fabs, a shrinking PC market and data centres under political risk":
        "Des usines à coûts fixes, un marché du PC en recul et des data centers sous risque politique",
    "Q4 26E = guidance. Sources: Intel 10-Qs, Q3 2026 call; Goldman Sachs (Nov 2026).":
        "T4 26E = guidance. Sources : 10-Q d'Intel, conférence du T3 2026 ; Goldman Sachs (nov. 2026).",
    "Catalyst 1 · Fixed-cost fabs": "Catalyseur 1 · Usines à coûts fixes",
    "Factory costs the same, full or half empty · PC lines half empty → gross margin 44% (Q3) → 38% (Q4 guide)":
        "Une usine coûte autant pleine qu'à moitié vide · Lignes PC à moitié vides → marge brute 44 % (T3) → 38 % (T4)",
    "Catalyst 2 · PC market shrinking": "Catalyseur 2 · PC en recul",
    "Memory expensive → fewer PCs bought · PC units –12% (2026), –10% (2027) · PCs ≈ half of Intel revenue":
        "Mémoire chère → moins de PC achetés · Unités PC –12 % (2026), –10 % (2027) · PC ≈ la moitié du CA d'Intel",
    "Catalyst 3 · Data centers at risk": "Catalyseur 3 · Data centers à risque",
    "Intel's only growth engine: +78% y/y (Q3) · After midterms: ~45% of planned US capacity at risk (Goldman)":
        "Seul moteur de croissance : +78 % sur un an (T3) · Après les midterms : ~45 % des capacités US prévues à risque (Goldman)",
    "Where we differ: the Street needs margins back above 42% – Intel just guided 38%":
        "Notre écart : le consensus a besoin d'une marge revenue au-dessus de 42 % – Intel vient d'annoncer 38 %",
    "1 · MARGINS (GM 2027E)": "1 · MARGES (MB 2027E)",
    "STREET (BLOOMBERG)": "CONSENSUS (BLOOMBERG)",
    "OUR VIEW": "NOTRE VUE",
    "Q4 guide 38%; Q1 26 flattered by reserved inventory sold; underused PC fabs":
        "Guidance T4 38 % ; T1 26 flatté par la vente de stocks dépréciés ; usines PC sous-utilisées",
    "2 · SERVERS & PCs (REVENUE)": "2 · SERVEURS & PC (CA)",
    "Servers supply-capped (AMD gains share); PC units –10% in 2027":
        "Serveurs limités par l'offre (AMD gagne des parts) ; unités PC –10 % en 2027",
    "3 · CASH & DILUTION (EPS)": "3 · CASH & DILUTION (BPA)",
    "D&A $14.2bn as capex rises; shares +29% since 2023. Q4 guide $0.25 × 4 = $1.00":
        "D&A 14,2 Md$ avec la hausse du capex ; actions +29 % depuis 2023. Guidance T4 0,25 $ × 4 = 1,00 $",
    "Four catalysts in 12 months – the January guide is the one that resets the Street":
        "Quatre catalyseurs en 12 mois – la guidance de janvier est celle qui recale le consensus",
    "Late Jan 2027": "Fin janv. 2027",
    "HARD": "FERME",
    "SOFT": "INCERTAIN",
    "Q4 results + 2027 guide": "Résultats T4 + guidance 2027",
    "Street: FY27 EPS $1.78, GM back > 42%": "Consensus : BPA 2027 1,78 $, MB de retour > 42 %",
    "Us: GM ~39.7%, EPS $1.33 · Impact:\xa0–⁠$22.93/share": "Nous : MB ~39,7 %, BPA 1,33 $ · Impact :\xa0–22,93\xa0$/action",
    "Jan 2027": "Janv. 2027",
    "PC data + CES Las\xa0Vegas": "Données PC + CES Las\xa0Vegas",
    "Street: H2 2027 PC recovery": "Consensus : reprise du PC au S2 2027",
    "Us: PC units –10% → client –9% · Impact: each –5% client ≈ –$0.09 EPS":
        "Nous : unités PC –10 % → Client –9 % · Impact : chaque –5 % de Client ≈ –0,09 $ de BPA",
    "H1 2027": "S1 2027",
    "Data-centre policy after midterms": "Politique des data centers après les midterms",
    "Street: AI build-out intact": "Consensus : investissements IA intacts",
    "Us: moratoria slow server builds · Impact: bear case $19.80": "Nous : les moratoires ralentissent les serveurs · Impact : scénario baissier 19,80 $",
    "Q2–Q3 2027": "T2-T3 2027",
    "First Apple chips on 18A-P": "Premières puces Apple en 18A-P",
    "Street: foundry inflection": "Consensus : point d'inflexion de la fonderie",
    "Us: low-end chips; TSMC keeps >90% · Impact: ~$1.2bn foundry revenue, no EPS change":
        "Nous : puces d'entrée de gamme ; TSMC garde >90 % · Impact : ~1,2 Md$ de CA fonderie, BPA inchangé",
    "Risk to our call: server supply fixed early (+$0.19 EPS per +10% DCAI) or a large 14A customer → bull $71.04.":
        "Risque pour notre avis : offre serveurs résolue tôt (+0,19 $ de BPA par +10 % de DCAI) ou un gros client 14A → haussier 71,04 $.",
    "January's Q4 print should cut 2027 EPS by a quarter: the Street needs $0.44 a quarter, Intel guides $0.25":
        "Le T4 de janvier devrait couper le BPA 2027 d'un quart : 0,44 $ attendus par trimestre, 0,25 $ annoncés",
    "What": "Quoi",
    "Q4 2026 results + first 2027 outlook (Q1 guide, gross margin, capex)":
        "Résultats T4 2026 + perspectives 2027 (T1, marge, capex)",
    "When": "Quand",
    "Late January 2027 – hard, dated": "Fin janvier 2027 – ferme, daté",
    "Street expects": "Le consensus attend",
    "2027 EPS $1.78; gross margin back to 42.5%": "BPA 2027 1,78 $ ; marge brute revenue à 42,5 %",
    "We expect – why": "Nous attendons – pourquoi",
    "$1.33: PC –10%, supply-capped servers, depreciation up with capex": "1,33 $ : PC –10 %, serveurs limités par l'offre, amortissements en hausse avec le capex",
    "Impact": "Impact",
    "–$22.93 per share if the Street moves to our EPS at its 51.2x P/E": "–22,93 $ par action si le consensus passe à notre BPA à son PER de 51,2x",
    "Source: Intel Q1–Q3 2026 remarks; Bloomberg consensus 6 Nov 2026; our model.":
        "Source : commentaires d'Intel T1-T3 2026 ; consensus Bloomberg du 6 nov. 2026 ; notre modèle.",
    "Our forecast: 2027E EPS $1.33, 25% below consensus – the gap is margins":
        "Notre prévision : BPA 2027E 1,33 $, 25 % sous le consensus – l'écart vient des marges",
    "2027E Street": "2027E cons.",
    "2027E ours": "2027E nous",
    "Gap": "Écart",
    "2028E Street": "2028E cons.",
    "2028E ours": "2028E nous",
    "Revenue ($bn)": "CA (Md$)",
    "Revenue growth": "Croissance du CA",
    "Gross margin (non-GAAP)": "Marge brute (non-GAAP)",
    "Adjusted EPS": "BPA ajusté",
    "Key drivers  ": "Moteurs clés  ",
    "Revenue growth driven by data center (+26%) · Gross margin 39.7%: PC lines half empty + rising depreciation with capex. Source: Bloomberg BEst, 6 Nov 2026.":
        "Croissance tirée par les data centers (+26 %) · Marge brute 39,7 % : lignes PC à moitié vides + amortissements en hausse avec le capex. Source : Bloomberg BEst, 6 nov. 2026.",
    "On Street NTM numbers Intel trades at 32.5x vs a peer median of 16.8x – with lower margins":
        "Intel cote 32,5x le BPA consensus contre 16,8x pour ses pairs – avec des marges plus faibles",
    "Company": "Société",
    "EV ($bn)": "VE (Md$)",
    "EBITDA margin": "Marge d'EBITDA",
    "EV / Sales": "VE / CA",
    "EV / EBITDA": "VE / EBITDA",
    "P / E": "PER",
    "Peer median": "Médiane des pairs",
    "Intel (Street NTM)": "Intel (consensus 12 m)",
    "Intel P/E on Street NTM EPS": "PER sur le BPA consensus 12 m",
    "~2× the peer median, after a 60% fall": "~2× la médiane, après –60 %",
    "Intel P/E on our 2027E EPS": "PER sur notre BPA 2027E",
    "2.5× the peer median": "2,5× la médiane des pairs",
    "Intel EBITDA margin (Street NTM)": "Marge d'EBITDA (consensus 12 m)",
    "vs 53% for the median peer": "vs 53 % pour le pair médian",
    "Source: Bloomberg NTM consensus (BEst, 6 Nov 2026), same basis for all; prices 6 Nov (TXN, GFS: 5 Nov). Median: Arm (64x) is an outlier.":
        "Source : consensus Bloomberg à 12 mois (BEst, 6 nov. 2026), même base pour tous ; cours du 6 nov. (TXN, GFS : 5 nov.). Médiane : Arm (64x) est un point aberrant.",
    "Our $32 target vs the Street's $90.91: lower EPS, and a multiple the Street has not cut yet":
        "Notre objectif de 32 $ vs 90,91 $ pour le consensus : BPA plus bas et multiple pas encore réduit",
    "From the consensus target to ours ($ per share)": "De l'objectif du consensus au nôtre ($ par action)",
    "From today's price to ours: 58% from lower EPS": "Du cours actuel à notre objectif : 58 % viennent du BPA plus bas",
    "Street PT": "Objectif consensus",
    "Price, 6 Nov": "Cours, 6 nov.",
    "Lower EPS": "BPA plus bas",
    "Lower multiple": "Multiple plus bas",
    "Our PT": "Notre objectif",
    "HOW WE GET THERE": "COMMENT ON Y ARRIVE",
    "$1.33 × 24x = $32": "1,33 $ × 24x = 32 $",
    "2027E EPS × target multiple (blend: DCF $21 · EV/EBITDA $49 · P/E $22)":
        "BPA 2027E × multiple cible (mélange : DCF 21 $ · VE/EBITDA 49 $ · PER 22 $)",
    "24x > peers (16.8x)": "24x > pairs (16,8x)",
    "2027 = Intel's worst year → on 2028E EPS ($1.70): only ~19x": "2027 = la pire année d'Intel → sur le BPA 2028E (1,70 $) : seulement ~19x",
    "–43% vs $56.28 → SELL": "–43 % vs 56,28 $ → VENDRE",
    "Sell threshold: below –10%": "Seuil de vente : sous –10 %",
    "Street PT $91: not cut after the fall": "Objectif consensus 91 $ : pas réduit après la chute",
    "vs today's price (lower chart): 58% of our gap = lower EPS": "vs le cours actuel (graphique du bas) : 58 % de notre écart = BPA plus bas",
    "Risks: the bull case is $71, the bear $20 – the skew still favours a Sell":
        "Risques : 71 $ en haussier, 20 $ en baissier – l'asymétrie reste en faveur de la vente",
    "Server supply fixed early": "Offre serveurs résolue tôt",
    "Each +10% data-center revenue ≈ +$0.19 EPS. Signpost: DCAI > $9bn a quarter at GM > 42%.":
        "Chaque +10 % de CA data centers ≈ +0,19 $ de BPA. Signal : DCAI > 9 Md$ par trimestre avec MB > 42 %.",
    "Apple + a 14A anchor customer": "Apple + un client de référence en 14A",
    "Foundry re-rated before profits → bull case $71 (+26%). Signpost: confirmed volumes, 14A prepayments.":
        "Fonderie revalorisée avant les profits → scénario haussier 71 $ (+26 %). Signal : volumes confirmés, prépaiements 14A.",
    "Early PC recovery": "Reprise précoce du PC",
    "Memory prices fall → PCs back in H2 2027 ≈ +$0.19 EPS (revenue at Street level). Signpost: DRAM prices, IDC PC data.":
        "Prix de la mémoire en baisse → PC de retour au S2 2027 ≈ +0,19 $ de BPA (CA au niveau du consensus). Signal : prix de la DRAM, données PC d'IDC.",
    "Bull: Street EPS × 40x. Bear: $0.90 × 22x (moratoria, PC –15%). Weighted: $36.76 (–35%).":
        "Haussier : BPA consensus × 40x. Baissier : 0,90 $ × 22x (moratoires, PC –15 %). Pondéré : 36,76 $ (–35 %).",
    "Price target $32  ·  –43.1%": "Objectif de cours 32 $  ·  –43,1 %",
    "Intel's 2026 margins were a shortage windfall – the stock still prices them as permanent":
        "Les marges 2026 d'Intel étaient une aubaine de pénurie – le titre les valorise encore comme durables",
    "2027E EPS $1.33 vs Street $1.78 (–25%): PC downturn, capped servers, higher D&A":
        "BPA 2027E 1,33 $ vs 1,78 $ pour le consensus (–25 %) : recul du PC, serveurs plafonnés, D&A en hausse",
    "Key catalyst: Q4 results and the 2027 guide, late January 2027": "Catalyseur clé : résultats du T4 et guidance 2027, fin janvier 2027",
    "32.5x Street EPS today vs 16.8x for peers – our $32 equals 18.8x our 2028E EPS":
        "32,5x le BPA consensus aujourd'hui vs 16,8x pour les pairs – nos 32 $ valent 18,8x notre BPA 2028E",
    "Questions?": "Questions ?",
    "AI footnote: how we used AI in this analysis": "Note sur l'IA : comment nous l'avons utilisée dans cette analyse",
    "Tools and tasks": "Outils et tâches",
    "Claude (Anthropic): extracting figures from Intel's 10-K and three 2026 10-Qs, first drafts of the Excel model, this deck and a study note; formatting charts.":
        "Claude (Anthropic) : chiffres extraits du 10-K et des trois 10-Q 2026, premières versions du modèle Excel, de ce deck et d'une note d'étude ; graphiques.",
    "Questions asked": "Questions posées",
    "'Which 2026 items in Intel's results are one-offs?' · 'What does the Escrowed Shares derivative do to GAAP EPS?' · 'Argue the Buy case against our Sell.'":
        "« Quels éléments 2026 sont non récurrents ? » · « Effet du dérivé Escrowed Shares sur le BPA GAAP ? » · « Défends l'achat contre notre vente. »",
    "Verification": "Vérification",
    "Key historical figures (revenue, margins, EPS) checked against the 10-Qs. AI first used a GAAP-mixed 2026 consensus EPS ($0.34); we replaced it with Bloomberg BEst ($1.49).":
        "CA, marges et BPA historiques vérifiés dans les 10-Q. L'IA a d'abord pris un BPA consensus 2026 mêlant GAAP (0,34 $) ; remplacé par Bloomberg BEst (1,49 $).",
    "Our conclusions": "Nos conclusions",
    "Rating, $32 target, 39.7% gross margin, weights, multiple and scenarios are our own judgements; AI saved us time on research and building the model.":
        "Recommandation, objectif de 32 $, marge brute de 39,7 %, pondérations, multiple et scénarios : nos jugements ; l'IA a fait gagner du temps sur la recherche et le modèle.",
    "Open questions": "Questions ouvertes",
    "How much of 2026's margin was one-off pricing? Apple volumes on 18A-P? Effect of data-centre moratoria on 2027 server units?":
        "Part ponctuelle de la marge 2026 ? Volumes d'Apple en 18A-P ? Effet des moratoires sur les serveurs 2027 ?",
    "BEFORE WE SUBMIT": "AVANT DE RENDRE",
    "In the file, not presented.": "Dans le fichier, non présenté.",
    "Tools, tasks and real prompts.": "Outils, tâches et vraies questions.",
    "One AI error and the source used instead.": "Une erreur de l'IA et la source utilisée à la place.",
    "Rating, target and thesis are our own.": "Recommandation, objectif et thèse sont les nôtres.",
    "Same content as the report's AI page.": "Même contenu que la page IA du rapport.",
    # layout footer
    "Intel Corporation (INTC)  ·  Noah Doose & Victor Endrizzi  ·  SKEMA MSc FMI  ·  For educational purposes only  ·  Prices as of 6 Nov 2026":
        "Intel Corporation (INTC)  ·  Noah Doose & Victor Endrizzi  ·  SKEMA MSc FMI  ·  À but pédagogique uniquement  ·  Cours au 6 nov. 2026",
}
T.update({"Quarterly revenue ($bn)": "CA trimestriel (Md$)", "Non-GAAP EPS per quarter ($)": "BPA non-GAAP par trimestre ($)",
          "Adjusted EPS ($)": "BPA ajusté ($)", "Value per share ($)": "Valeur par action ($)"})
CHART = {"Quarterly revenue ($bn)": "CA trimestriel (Md$)", "Client (PC)": "Client (PC)", "Data center": "Data centers",
         "Non-GAAP EPS per quarter ($)": "BPA non-GAAP par trimestre ($)", "EPS": "BPA", "Adjusted EPS ($)": "BPA ajusté ($)",
         "Street": "Consensus", "Ours": "Nous", "Value per share ($)": "Valeur par action ($)", "Bear": "Baissier", "Our PT": "Notre objectif",
         "Price": "Cours", "Bull": "Haussier", "Value": "Valeur",
         "Q4 26E guide": "T4 26E guidance", "2027E/qtr Street": "2027E/trim. consensus", "2027E/qtr ours": "2027E/trim. nous"}
CAT_Q = re.compile(r"^Q(\d) (\d\d)(E?)$")

NUM = re.compile(r"^[–\-+~]?\$?[\d,]+(\.\d+)?(%|x|pt|bn)?$")


def fr_num(s):
    """Pure-number runs: decimal comma, $ after the number, non-breaking space before %."""
    if not NUM.match(s):
        return None
    neg = s[0] in "–-"
    sign = s[0] if s[0] in "–-+~" else ""
    body = s[len(sign):]
    dollar = body.startswith("$")
    body = body.lstrip("$")
    body = body.replace(",", NB) if re.match(r"^\d{1,3}(,\d{3})+$", body) else body
    body = re.sub(r"(\d)\.(\d)", r"\1,\2", body)
    body = body.replace("%", NB + "%").replace("bn", NB + "Md")
    if dollar:
        body += NB + "$"
    return sign + ("\u2060" if sign in "–-" and sign else "") + body


def tr(s):
    if s in T:
        return T[s]
    n = fr_num(s.strip())
    if n is not None:
        return s.replace(s.strip(), n)
    return s


def tr_frame(tf, missing):
    for p in tf.paragraphs:
        for r in p.runs:
            if r.text.strip():
                new = tr(r.text)
                if new == r.text and not re.match(r"^[\d\s·•|]+$|^(AMD|Qualcomm|Arm Holdings|Nvidia|Broadcom|TSMC|GlobalFoundries|Texas Instruments|\d+)$", r.text.strip()):
                    missing.add(r.text)
                r.text = new


def main(src, dst):
    prs = Presentation(src)
    missing = set()
    for lay in prs.slide_layouts:
        for sh in lay.shapes:
            if sh.has_text_frame:
                tr_frame(sh.text_frame, missing)
    for s in prs.slides:
        for sh in s.shapes:
            if sh.has_text_frame:
                tr_frame(sh.text_frame, missing)
            if getattr(sh, "has_table", False) and sh.has_table:
                for row in sh.table.rows:
                    for c in row.cells:
                        tr_frame(c.text_frame, missing)
            if getattr(sh, "has_chart", False) and sh.has_chart:
                ch = sh.chart
                if ch.has_title:
                    tr_frame(ch.chart_title.text_frame, missing)
                plot = ch.plots[0]
                cats = []
                for c in plot.categories:
                    c = str(c)
                    m = CAT_Q.match(c)
                    cats.append(f"T{m.group(1)} {m.group(2)}{m.group(3)}" if m else CHART.get(c, c))
                from pptx.chart.data import CategoryChartData
                cd = CategoryChartData()
                cd.categories = cats
                for se in plot.series:
                    cd.add_series(CHART.get(se.name, se.name), list(se.values))
                ch.replace_data(cd)
    for s in prs.slides:          # the closing slide's big rating word is wider in French
        for sh in s.shapes:
            if sh.name == "a1_sell":
                sh.width = sh.width * 2
    prs.save(dst)
    if missing:
        print("UNTRANSLATED:", *sorted(missing), sep="\n  ")


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
