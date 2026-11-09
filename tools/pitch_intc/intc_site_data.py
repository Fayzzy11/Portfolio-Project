"""Adds the Intel (INTC) pitch to site/data/pitches.json and site/data/pitches_fr.json (idempotent).
Content: Noah Doose & Victor Endrizzi, Intel initiation (SKEMA Equity Research, Nov 2026); figures from their model."""
import json
from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]
D = ROOT / "site/data"
PRICE = 56.28

def sc(name, inputs, value, story):
    return {"name": name, "inputs": inputs, "value": value, "upside": round(value / PRICE - 1, 4), "story": story}

EN = {
 "code": "INTC_US", "bbg": "INTC US Equity", "name": "Intel", "legal": "Intel Corporation", "exchange": "Nasdaq", "ticker": "INTC",
 "country": "United States", "ccy": "USD", "sym": "$", "sector": "Information Technology", "industry": "Semiconductors",
 "price": PRICE, "price_note": "close, 6 Nov 2026", "shares_m": 5440, "high52": 142.35, "low52": 32.89,
 "rating": "Sell", "conviction": "Initiation", "horizon": "12-18 months", "role": "Short idea (course project, with Victor Endrizzi)",
 "headline": "The 2026 margin peak is behind us: the Street still prices a shortage windfall as if it were permanent",
 "one_liner": "Intel's 2026 recovery came from a shortage: reserved inventory sold in Q1, price rises and a server boom it could only partly supply. The Q4 guide (gross margin 38%, EPS $0.25) shows the peak has passed, yet consensus still models 42.5% and $1.78 of EPS for 2027. We have $1.33 and a $32 target, 43% below the price.",
 "key_stats": [["Market cap (diluted)", "$306bn"], ["2027E EPS, ours / Street", "$1.33 / $1.78"], ["P/E on Street NTM EPS", "32.5x"], ["Free cash flow 2027E", "−$5.7bn"]],
 "thesis": [["2026 margins were a windfall, not a new base", "Non-GAAP gross margin rose from 41.0% in Q1 to 44.1% in Q3, helped by reserved inventory and price rises, then Intel guided 38% for Q4. We keep 2027 near that run-rate (39.7% non-GAAP) against 42.5% for consensus: 2027E EPS $1.33 vs $1.78."],
            ["Supply-capped servers, shrinking PCs", "Server CPU demand grows >30% but Intel is short of substrates and Intel 3 output: we model data center +26%. PC units fall ~10% in 2027 and client revenue −9%. Revenue is only 5% below consensus; the EPS gap is margins."],
            ["Capex, dilution and minorities absorb the cash", "Capex rises 'strongly' in 2027 and free cash flow is negative (−$5.7bn); diluted shares are up 29% since 2023 and ~$1.1bn of profit a year goes to fab partners. At 32.5x Street EPS the stock prices none of this."]],
 "variant": [["2026 margins are the new base: 42.5% in 2027, $3.00 of EPS in 2028.", "They came from reserved inventory, price rises and a shortage; Intel itself guides 38% for Q4 'against our fixed-cost base'."],
             ["Intel is an AI winner: server CPUs are booming.", "Demand is not the problem, supply is: substrates, Intel 3 and Fab 28 cap shipments and AMD takes the share."],
             ["After a 60% fall it is priced in.", "Not on earnings: 32.5x Street NTM EPS and 42.4x ours, against a peer median of 16.8x."],
             ["The Apple deal makes the foundry a business.", "Unconfirmed, low-end chips from mid-2027, TSMC keeps >90% of Apple's volume: ~$1.2bn of external revenue in 2027E."]],
 "business": [["Client Computing (CCPG)", "x86 processors for PCs: $32.2bn of revenue in 2025 (61%) at a 28.9% operating margin."],
              ["Data Center & AI (DCAI)", "Server CPUs and custom chips: $16.9bn (32%), +53% in 9M 2026; supply-constrained into 2028."],
              ["Intel Foundry", "Makes almost all of Intel's own chips and seeks outside customers; lost $10.3bn in 2025 and $6.4bn in 9M 2026."],
              ["Capital", "CEO Lip-Bu Tan prioritises manufacturing: $20bn gross capex in 2026, more in 2027; equity from the US government, SoftBank, Nvidia and a $20bn offering (Aug 2026)."]],
 "segments": {"title": "Revenue by segment, 2025", "unit": "$bn", "labels": ["Client (CCPG)", "Intel Foundry (mostly internal)", "Data Center & AI", "All other"], "values": [32.2, 17.8, 16.9, 3.6]},
 "macro": [["PC units, 2027", "−10%", "A memory shortage raises PC prices while IT budgets are tight; Intel expects −12% in 2026 and −10% in 2027."],
           ["Server CPU units", ">30%", "AI agents need more CPUs, but Intel is short of substrates and Intel 3 output, and lost Fab 28 in October."],
           ["US data-centre capacity at risk", "~45%", "After the 3 Nov midterms, Goldman flags that moratoria could affect ~45% of planned US capacity."],
           ["TSMC's share of Apple", ">90%", "The reported Apple-Intel deal is unconfirmed and covers low-end chips from mid-2027."]],
 "financials": {"cols": ["", "2024A", "2025A", "2026E", "2027E", "2028E"],
                "rows": [["Revenue ($m)", "53,101", "52,853", "61,718", "66,132", "73,223"], ["Growth", "−2.1%", "−0.5%", "+16.8%", "+7.2%", "+10.7%"],
                         ["Gross margin (GAAP)", "32.7%", "34.8%", "40.0%", "38.5%", "40.5%"], ["EBITDA margin", "−0.6%", "18.0%", "24.2%", "31.5%", "35.0%"],
                         ["Adjusted EPS ($)", "–", "–", "1.48", "1.33", "1.70"], ["Consensus EPS ($)", "–", "–", "1.49", "1.78", "3.00"],
                         ["Free cash flow ($m)", "−14,898", "−6,398", "298", "−5,690", "−730"], ["Diluted shares (m)", "4,280", "4,530", "5,218", "5,480", "5,525"]],
                "note": "2026E = nine months reported + Q4 guidance. 2024A-2025A FCF = operating cash flow − net capex; 2027E-2028E = unlevered FCF (DCF). Sources: Intel 10-K FY2025, 10-Qs 2026; Bloomberg BEst consensus (6 Nov 2026); own estimates."},
 "valuation": {"method": "Blend of DCF, EV/EBITDA and P/E comparables",
               "explain": "Price target $32 = DCF $20.96 (30%), EV/EBITDA comps $48.68 (40%), P/E comps $22.31 (30%), rounded; cross-check $1.33 × 24.1x. EV/EBITDA gets most weight because GAAP EPS is distorted by one-offs; the DCF only 30% because 59% of its value is terminal value. The Street's $90.91 target implies 51.2x 2027 EPS.",
               "kind": "blend", "scenarios": [["Bear", 0.90, 22.0, "Data-centre moratoria, PC −15%, AMD gains, 14A slips"],
                                               ["Base", 1.33, 24.1, "PC −10%, supply-capped servers, gross margin 38.5%"],
                                               ["Bull", 1.78, 40.0, "Supply fixed, Apple ramps, 14A anchor customer, PCs back in H2 2027"]],
               "consensus_target": 90.91},
 "catalysts": [["Late Jan 2027", "Q4 2026 results and first 2027 outlook: if consensus moves to $1.33 at its own 51.2x, −$22.93 a share"],
               ["Jan 2027", "IDC/Gartner PC data and CES: confirm a 2027 PC decline (~−10% units)"],
               ["H1 2027", "Data-centre policy after the midterms: each −10% of data center revenue ≈ −$0.19 of EPS"],
               ["Q2-Q3 2027", "First Apple chips on 18A-P: ~$1.2bn of external foundry revenue, too small to change margins"]],
 "risks": [["Server supply fixed early (substrates, Intel 3, Fab 28)", "Signpost: data center revenue above $9bn a quarter at gross margin above 42%"],
           ["Apple confirmed plus a 14A anchor customer", "Would re-rate Intel Foundry before profits; bull case $71"],
           ["Early PC recovery or new state support", "Signposts: DRAM contract prices, IDC data, CHIPS funding"],
           ["Short squeeze after a 60% fall (+24% on the Q1 print)", "Watch short interest and estimate revisions; no short into January without a stop"]],
 "triggers": ["Data center revenue above $9bn a quarter at gross margin above 42%", "Apple volumes confirmed together with a 14A anchor customer and prepayments",
              "DRAM contract prices falling early and IDC data showing PCs recovering in H1 2027"],
 "peers_text": "AMD, Nvidia, Qualcomm, Arm, TSMC, GlobalFoundries, Texas Instruments, Broadcom (Bloomberg NTM consensus; median used, Arm is an outlier).",
 "target": 32.0, "upside": round(32 / PRICE - 1, 4),
 "scenarios_out": [sc("Bear", "EPS $0.90 × 22x", 19.80, "Data-centre moratoria, PC −15%, AMD gains, 14A slips"),
                   sc("Base", "EPS $1.33 × 24.1x", 32.0, "PC −10%, supply-capped servers, gross margin 38.5%"),
                   sc("Bull", "EPS $1.78 × 40x", 71.04, "Supply fixed, Apple ramps, 14A anchor customer, PCs back in H2 2027")],
 "rating_consistent": True, "mcap_bn": 306.2, "facts": None,
 "authors": "Noah Doose & Victor Endrizzi",
 "differ": [["Gross margin 2027E (non-GAAP)", "42.5%", "39.7%"], ["Revenue 2027E", "$69.3bn (+12%)", "$66.1bn (+7%)"], ["Adjusted EPS 2027E", "$1.78", "$1.33"],
            ["Free cash flow 2027E", "−$2.7bn", "−$5.7bn"], ["Adjusted EPS 2028E", "$3.00", "$1.70"]],
 "sources": [{"tag": "1", "label": "Intel Corporation, Form 10-K for the fiscal year ended 27 December 2025", "url": "https://www.sec.gov/cgi-bin/browse-edgar?action=getcompany&CIK=0000050863&type=10-K"},
             {"tag": "2", "label": "Intel Corporation, Forms 10-Q, Q1-Q3 2026", "url": "https://www.sec.gov/cgi-bin/browse-edgar?action=getcompany&CIK=0000050863&type=10-Q"},
             {"tag": "3", "label": "Intel Corporation, CEO/CFO prepared remarks, Q1-Q3 2026 earnings (Q3: 29 Oct 2026)", "url": "https://www.intc.com/"},
             {"tag": "4", "label": "Intel, \"Intel announces upsize and pricing of $20 billion common stock offering\", 11 Aug 2026", "url": "https://www.intc.com/news-events/press-releases"},
             {"tag": "5", "label": "Bloomberg L.P., INTC US Equity: BEst consensus, ANR, beta, peers (NTM), weekly prices, 6 Nov 2026", "url": ""},
             {"tag": "6", "label": "StockTitan (6 Nov 2026) and Forbes (5 Nov 2026): chip stocks after the midterms", "url": ""},
             {"tag": "7", "label": "Tech Times (20 Jun 2026), Gadget Hacks (2026): reports on the Apple-Intel agreement (WSJ, May 2026)", "url": ""},
             {"tag": "8", "label": "Damodaran, A., implied equity risk premium, NYU Stern (1 Nov 2026)", "url": "https://pages.stern.nyu.edu/~adamodar/"},
             {"tag": "9", "label": "SKEMA Business School, Equity Research course materials, Sessions 1-4 (Paul Wuh)", "url": ""}],
 "note": {
  "intro": "Intel is not a holding of the value strategy: it was assigned by the instructor of the SKEMA Equity Research course, where Victor Endrizzi and I had to initiate coverage and defend a Sell. It is in this set because it is the opposite exercise to the value pitches: here the stock has already fallen 60%, looks cheap on price, and is still expensive on earnings. This note explains how Intel makes money, why its margins move so much, and why we think the Street's 2027 numbers are too high.",
  "business_long": ["Intel designs and manufactures x86 processors. Client Computing (CCPG) sells PC processors: $32.2bn of revenue in 2025, 61% of the total, and most of the profit. Data Center & AI (DCAI) sells server CPUs and custom chips: $16.9bn, growing 53% in the first nine months of 2026.",
                    "Intel Foundry makes almost all of Intel's own chips and is trying to win outside customers. It sells wafers mostly to Intel Products and lost $6.4bn in the first nine months of 2026: the products earn, the factories lose.",
                    "Owning the fabs makes Intel the extreme case of operating leverage. A fab costs the same whether it runs full or half empty, so when volumes and prices rose in 2026 margins jumped, and when PC lines empty again margins fall fast. For Q4 Intel guided gross margin down about six points on 'lower overall revenue against our fixed-cost base'.",
                    "Capital allocation goes to manufacturing: $20bn of gross capex in 2026 and 'up strongly' in 2027. The balance sheet was rebuilt with equity — the US government (2025), SoftBank, Nvidia and a $20bn offering at $95 in August 2026 — so diluted shares are up 29% since 2023. There has been no dividend since 2024 and no buybacks."],
  "macro_long": ["Memory prices are breaking PC demand: a shortage pushed PC prices up while IT budgets are tight. Intel expects the PC market to fall about 12% in 2026 and 10% in 2027, with no recovery until memory prices normalise. AMD and Arm-based PCs gain share while Intel prioritises server wafers.",
                 "In servers, demand is not the problem: AI agents need more CPUs, and Intel sees industry server CPU units growing more than 30% in 2026 and 2027. Supply is the problem: Intel is short of substrates for its EMIB packaging, Intel 3 output is still ramping, and the October shutdown of Fab 28 in Israel costs about $300m of Q4 revenue. When Intel cannot ship, AMD takes the share.",
                 "Politics added a new risk after the 3 November midterms: Democrats won both chambers after campaigning on data-centre power use, and Goldman flags that local moratoria could affect about 45% of planned US capacity. Intel sells into new data centres, so it sits on the losing side; we keep this in the bear case only."],
  "history": [["2025", "Lip-Bu Tan becomes CEO; US government takes a ~10% stake"], ["Q1 2026", "Margins helped by previously reserved inventory; shares +24% on the print"],
              ["Jun 2026", "Share price peaks at $141"], ["11 Aug 2026", "$20bn equity offering at $95"], ["Oct 2026", "Fab 28 (Israel) shut down"],
              ["29 Oct 2026", "Q3 beat (EPS $0.52 vs $0.41) but Q4 guide of $0.25 vs $0.43: −28.6% the next day, worst since 1974"],
              ["3-6 Nov 2026", "Midterms: −10.3% on 5 Nov, +7.7% on 6 Nov to $56.28"]],
  "model_long": "We forecast by segment. Client revenue = PC units × Intel share × price: for 2027E, units −10%, share −3%, price +4%, so client revenue −9%. Data center = server CPU units × share/supply × price: +30%, −8%, +5%, so +26%. Total revenue grows 7% to $66.1bn, only 4.5% below consensus. GAAP gross margin is 38.5% in 2027E (about 39.7% non-GAAP), recovering to 46% by 2033E as 18A/14A costs fall; depreciation rises from $13.0bn to $16.1bn by 2028E with the capex wave. Tax 12%, minorities ~$1.1bn a year, diluted shares 5.48bn. Non-GAAP EPS adds back stock pay and acquired-intangible amortisation, like consensus: $1.33 in 2027E against $1.78. Each point of gross margin is worth about $0.10-0.11 of EPS.",
  "bear_long": "The bull case is $71 (+26%): Intel fixes its supply problems in H1 2027, data center grows well above 26%, Apple ramps on 18A-P, a 14A anchor customer signs with prepayments, and PCs recover in H2 2027 as memory prices fall. Consensus EPS of $1.78 at 40x gets there. It needs several things to go right at once, which is why we give it 20%; the probability-weighted value is $36.76, 35% below the price.",
  "glossary": [["IDM", "Integrated device manufacturer: designs and makes its own chips (Intel), unlike fabless designers (AMD, Nvidia) or pure foundries (TSMC)."],
               ["Gross margin (GAAP vs non-GAAP)", "Non-GAAP excludes stock pay and acquired-intangible amortisation; Intel's non-GAAP is about one point higher."],
               ["Escrowed Shares derivative", "A $13.7bn liability settled in shares, marked to market through GAAP results; non-cash, so excluded from adjusted EPS and EV."],
               ["18A / 14A", "Intel's leading-edge process nodes; 14A is the node that needs an external anchor customer."],
               ["EMIB", "Intel's packaging technology that links chips on a substrate; substrate shortages cap server output."],
               ["NTM", "Next twelve months: consensus estimates rolled forward over the coming year."]],
  "interview": [["Isn't all of this priced in after a 60% fall?", "No: at $56.28 the stock trades at 32.5x Street EPS and 42.4x ours, against 16.8x for peers; the price still assumes margins back above 42%."],
                ["Why is your target so far from the Street's?", "Two parts: −$22.93 from lower EPS and −$35.98 from the multiple. The Street's $90.91 implies 51.2x 2027 EPS while the market pays 32.5x today."],
                ["What is the single most important assumption?", "2027 gross margin: 39.7% non-GAAP (38.5% GAAP) against 42.5% for consensus. Each point is about $0.10 of EPS."],
                ["Intel beat Q3. Why didn't you raise numbers?", "Because the guide matters more than the beat: Q3 EPS $0.52 vs $0.41 expected, but Q4 guided to $0.25 vs $0.43 and the stock fell 28.6%."],
                ["Why is your target P/E (24x) above the peer median (17x)?", "2027 is a trough year for Intel's margins, so the peer multiple on trough EPS would be too harsh; 24x is still far below the 51x in the Street's target."],
                ["Why is the DCF so low ($21)?", "FCF is negative in 2027-28 and capex converges to depreciation only slowly; the implied exit multiple is 5x EBITDA. With 10x the DCF is $27-44, still below the price."],
                ["What would make you change your rating?", "Data center revenue above $9bn a quarter at gross margin above 42%, or confirmed Apple volumes together with a 14A anchor customer."],
                ["Would you short it today?", "Not into the January print without a stop: Intel rose 24% on its Q1 print and short interest can make the squeeze violent."]]}
}

FR = {
 "role": "Idée de vente (projet de cours, avec Victor Endrizzi)", "conviction": "Initiation", "industry": "Semi-conducteurs", "horizon": "12-18 mois",
 "headline": "Le pic de marge de 2026 est derrière nous : le marché valorise encore une aubaine de pénurie comme si elle était durable",
 "one_liner": "La reprise d’Intel en 2026 vient d’une pénurie : stocks réservés vendus au T1, hausses de prix et un boom des serveurs qu’Intel n’a pu servir qu’en partie. La guidance du T4 (marge brute 38 %, BPA 0,25 $) montre que le pic est passé, mais le consensus table encore sur 42,5 % et 1,78 $ de BPA en 2027. Nous avons 1,33 $ et un objectif de 32 $, 43 % sous le cours.",
 "key_stats": [["Capitalisation (diluée)", "306 Md$"], ["BPA 2027E, nous / consensus", "1,33 $ / 1,78 $"], ["PER sur BPA 12 mois consensus", "32,5x"], ["Free cash flow 2027E", "−5,7 Md$"]],
 "thesis": [["Les marges de 2026 sont une aubaine, pas une nouvelle base", "La marge brute non-GAAP est passée de 41,0 % au T1 à 44,1 % au T3, aidée par des stocks réservés et des hausses de prix, puis Intel a annoncé 38 % pour le T4. Nous restons près de ce rythme en 2027 (39,7 % non-GAAP) contre 42,5 % pour le consensus : BPA 2027E de 1,33 $ contre 1,78 $."],
            ["Serveurs plafonnés, PC en recul", "La demande de CPU serveurs croît de plus de 30 % mais Intel manque de substrats et de production Intel 3 : nous modélisons +26 % en data center. Les PC reculent d’environ 10 % en 2027 et le CA client de 9 %. Le CA n’est que 5 % sous le consensus ; l’écart de BPA vient des marges."],
            ["Capex, dilution et minoritaires absorbent le cash", "Le capex monte « fortement » en 2027 et le free cash flow est négatif (−5,7 Md$) ; les actions diluées ont augmenté de 29 % depuis 2023 et ~1,1 Md$ de bénéfice par an revient aux partenaires des usines. À 32,5x le BPA du consensus, le titre n’intègre rien de tout cela."]],
 "method": "Combinaison DCF, comparables VE/EBITDA et PER",
 "explain": "Objectif de 32 $ = DCF 20,96 $ (30 %), comparables VE/EBITDA 48,68 $ (40 %), comparables PER 22,31 $ (30 %), arrondi ; contrôle 1,33 $ × 24,1x. VE/EBITDA pèse le plus car le BPA GAAP est faussé par des éléments ponctuels ; le DCF seulement 30 % car 59 % de sa valeur est terminale. L’objectif du consensus à 90,91 $ suppose 51,2x le BPA 2027.",
 "stories": ["Moratoires sur les data centers, PC −15 %, AMD gagne, 14A glisse", "PC −10 %, serveurs plafonnés, marge brute 38,5 %", "Offre rétablie, Apple monte en charge, client 14A, PC de retour au S2 2027"],
 "catalysts": [["Fin janv. 2027", "Résultats du T4 2026 et premières perspectives 2027 : si le consensus rejoint 1,33 $ à son propre 51,2x, −22,93 $ par action"],
               ["Janv. 2027", "Données PC IDC/Gartner et CES : confirmation d’un recul des PC en 2027 (~−10 % d’unités)"],
               ["S1 2027", "Politique des data centers après les élections : chaque −10 % de CA data center ≈ −0,19 $ de BPA"],
               ["T2-T3 2027", "Premières puces Apple sur 18A-P : ~1,2 Md$ de CA fonderie externe, trop peu pour changer les marges"]],
 "triggers": ["Le CA data center dépasse 9 Md$ par trimestre avec une marge brute au-dessus de 42 %", "Les volumes d’Apple sont confirmés avec un client de référence 14A et des prépaiements",
              "Les prix contractuels de la DRAM baissent tôt et les données IDC montrent une reprise des PC dès le S1 2027"],
}

for path, key, val in ((D / "pitches.json", None, EN), (D / "pitches_fr.json", "INTC_US", FR)):
    data = json.loads(path.read_text(encoding="utf-8"))
    if key is None:
        data = [p for p in data if p["code"] != "INTC_US"] + [val]
    else:
        data[key] = val
    path.write_text(json.dumps(data, ensure_ascii=False, indent=1), encoding="utf-8")
print("Intel added")
