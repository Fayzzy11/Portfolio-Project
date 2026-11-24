def _tbl(head, rows, hl=()):
    h = "".join(f"<th{' class=n' if i else ''}>{c}</th>" for i, c in enumerate(head))
    b = "".join(f"<tr{' class=hl' if i in hl else ''}>" + "".join(f"<td{' class=n' if j else ''}>{'<b>' if j == 0 else ''}{c}{'</b>' if j == 0 else ''}</td>" for j, c in enumerate(r)) + "</tr>" for i, r in enumerate(rows))
    return f"<table class=t><thead><tr>{h}</tr></thead><tbody>{b}</tbody></table>"


_FIN_EN = _tbl(["", "2024A", "2025A", "2026E", "2027E ours", "2027E Street", "2028E ours", "2028E Street"], [
    ["Revenue ($bn)", "53.1", "52.9", "61.7", "66.1", "69.3", "73.2", "84.7"],
    ["Growth", "−2.1%", "−0.5%", "+16.8%", "+7.2%", "+12.1%", "+10.7%", "+22.2%"],
    ["Gross margin, non-GAAP", "—", "—", "—", "39.7%", "42.5%", "41.7%", "45.8%"],
    ["Gross margin, GAAP", "32.7%", "34.8%", "40.0%", "38.5%", "—", "40.5%", "—"],
    ["Adjusted EPS ($)", "—", "—", "1.48", "1.33", "1.78", "1.70", "3.00"],
    ["Free cash flow ($bn)", "−14.9", "−6.4", "0.3", "−5.7", "−2.7", "−0.7", "—"],
    ["Diluted shares (m)", "4,280", "4,530", "5,218", "5,480", "—", "5,525", "—"]], hl=(4,))
_FIN_FR = _tbl(["", "2024R", "2025R", "2026E", "2027E nous", "2027E consensus", "2028E nous", "2028E consensus"], [
    ["CA (Md$)", "53,1", "52,9", "61,7", "66,1", "69,3", "73,2", "84,7"],
    ["Croissance", "−2,1 %", "−0,5 %", "+16,8 %", "+7,2 %", "+12,1 %", "+10,7 %", "+22,2 %"],
    ["Marge brute non-GAAP", "—", "—", "—", "39,7 %", "42,5 %", "41,7 %", "45,8 %"],
    ["Marge brute GAAP", "32,7 %", "34,8 %", "40,0 %", "38,5 %", "—", "40,5 %", "—"],
    ["BPA ajusté ($)", "—", "—", "1,48", "1,33", "1,78", "1,70", "3,00"],
    ["Free cash flow (Md$)", "−14,9", "−6,4", "0,3", "−5,7", "−2,7", "−0,7", "—"],
    ["Actions diluées (M)", "4 280", "4 530", "5 218", "5 480", "—", "5 525", "—"]], hl=(4,))
_PEERS_EN = _tbl(["Company (Street NTM)", "EV ($bn)", "EBITDA margin", "EV/Sales", "EV/EBITDA", "P/E"], [
    ["AMD", "728", "35%", "8.2x", "23.6x", "28.0x"], ["Qualcomm", "186", "29%", "4.0x", "14.1x", "16.5x"], ["Arm Holdings", "183", "48%", "24.5x", "51.4x", "63.7x"],
    ["Nvidia", "4,524", "65%", "7.1x", "10.8x", "13.0x"], ["Broadcom", "1,476", "67%", "8.4x", "12.6x", "15.1x"], ["TSMC", "1,876", "73%", "8.0x", "11.1x", "17.1x"],
    ["GlobalFoundries", "18", "37%", "2.2x", "6.0x", "14.9x"], ["Texas Instruments", "264", "58%", "10.3x", "17.8x", "24.5x"],
    ["Peer median", "496", "53%", "8.1x", "13.3x", "16.8x"], ["Intel (Street NTM)", "319", "35%", "4.7x", "13.3x", "32.5x"]], hl=(9,))
_PEERS_FR = _tbl(["Société (consensus 12 mois)", "VE (Md$)", "Marge d’EBITDA", "VE/CA", "VE/EBITDA", "PER"], [
    ["AMD", "728", "35 %", "8,2x", "23,6x", "28,0x"], ["Qualcomm", "186", "29 %", "4,0x", "14,1x", "16,5x"], ["Arm Holdings", "183", "48 %", "24,5x", "51,4x", "63,7x"],
    ["Nvidia", "4 524", "65 %", "7,1x", "10,8x", "13,0x"], ["Broadcom", "1 476", "67 %", "8,4x", "12,6x", "15,1x"], ["TSMC", "1 876", "73 %", "8,0x", "11,1x", "17,1x"],
    ["GlobalFoundries", "18", "37 %", "2,2x", "6,0x", "14,9x"], ["Texas Instruments", "264", "58 %", "10,3x", "17,8x", "24,5x"],
    ["Médiane des pairs", "496", "53 %", "8,1x", "13,3x", "16,8x"], ["Intel (consensus 12 mois)", "319", "35 %", "4,7x", "13,3x", "32,5x"]], hl=(9,))
_CAP_EN = "<p class=cap>2026E = nine months reported + Q4 guidance. FCF 2024A-2025A = operating cash flow − net capex; 2027E-2028E = unlevered FCF from the DCF. Sources: Intel 10-K FY2025, 10-Qs 2026; Bloomberg BEst consensus (6 Nov 2026); our model. Peers: Bloomberg NTM consensus, 6 Nov 2026.</p>"
_CAP_FR = "<p class=cap>2026E = neuf mois publiés + guidance du T4. FCF 2024R-2025R = flux d’exploitation − investissements nets ; 2027E-2028E = FCF non endetté du DCF. Sources : 10-K 2025 et 10-Q 2026 d’Intel ; consensus Bloomberg BEst (6 nov. 2026) ; notre modèle. Pairs : consensus Bloomberg à 12 mois, 6 nov. 2026.</p>"

NOTE = {
 "authors": ("Noah Doose & Victor Endrizzi", "Noah Doose & Victor Endrizzi"),
 "cover": {"stem": "INTC_US_Intel", "company": "Intel", "rating": "Sell", "rating_label": ("SELL", "VENDRE"),
           "kicker": ("Initiating coverage · Equity Research, SKEMA MSc FMI · 9-10 November 2026", "Initiation de couverture · Equity Research, SKEMA MSc FMI · 9-10 novembre 2026"),
           "claim": ("The 2026 margin peak is behind us", "Le pic de marge 2026 est passé"),
           "sub": ("The Street still prices a shortage windfall as if it were permanent", "Le consensus valorise encore une aubaine de pénurie comme si elle était durable"),
           "target_s": ("$32", "32 $"), "target_cap": ("Price target, 12-18 months", "Objectif de cours, 12-18 mois"),
           "price_s": ("$56.28", "56,28 $"), "price_cap": ("Price, 6 Nov 2026", "Cours, 6 nov. 2026"),
           "upside_s": ("−43.1%", "−43,1 %"), "upside_cap": ("Downside", "Baisse")},
 "pitch60": [
  ("We initiate coverage of **Intel with a Sell** and a 12-to-18-month price target of **$32**, 43% below the $56.28 close of 6 November 2026.",
   "Nous initions la couverture d’**Intel à Vendre** avec un objectif de cours à 12-18 mois de **32 $**, 43 % sous la clôture de 56,28 $ du 6 novembre 2026."),
  ("Intel's 2026 recovery came from a **shortage**: reserved inventory sold in Q1, price rises, and a server boom it could only partly supply. Gross margin went from 41% in Q1 to 44% in Q3, and then Intel guided **38% for Q4** and EPS of **$0.25**. "
   "The Street still models 42.5% and **$1.78 of EPS for 2027**. We have **$1.33**: PCs shrink, servers are supply-capped, and depreciation rises with capex.",
   "La reprise d’Intel en 2026 vient d’une **pénurie** : des stocks réservés vendus au T1, des hausses de prix et un boom des serveurs qu’Intel n’a pu servir qu’en partie. La marge brute est passée de 41 % au T1 à 44 % au T3, puis Intel a annoncé **38 % pour le T4** et un BPA de **0,25 $**. "
   "Le consensus modélise encore 42,5 % et **1,78 $ de BPA en 2027**. Nous avons **1,33 $** : les PC reculent, les serveurs sont limités par l’offre, et l’amortissement monte avec les investissements."),
  ("At $56 the stock trades at **32.5x Street earnings** against 16.8x for peers, after a 60% fall from its June high. Our $32 is $1.33 × 24x, cross-checked by a blend of DCF, EV/EBITDA and P/E comparables. "
   "The catalyst is the **Q4 results and 2027 guide in late January 2027**. We would change our mind if server supply were fixed early or if a large 14A foundry customer signed.",
   "À 56 $ le titre cote **32,5x les bénéfices du consensus** contre 16,8x pour les pairs, après une chute de 60 % depuis son plus haut de juin. Nos 32 $, c’est 1,33 $ × 24x, recoupé par un mélange de DCF, de VE/EBITDA et de PER comparables. "
   "Le catalyseur est la **publication du T4 et de la guidance 2027 fin janvier 2027**. Nous changerions d’avis si l’offre de serveurs était débloquée tôt ou si un grand client fonderie signait sur le 14A."),
 ],
 "killer": ("Four quarters at Intel's Q4 guide of 25 cents is one dollar. The Street needs $1.78 – 44 cents a quarter, back to the peak. We have $1.33.",
            "Quatre trimestres au rythme de la guidance du T4, 25 cents, font un dollar. Le consensus a besoin de 1,78 $ – 44 cents par trimestre, retour au pic. Nous avons 1,33 $."),
 "memorise": [
  (("Price (6 Nov 2026)", "Cours (6 nov. 2026)"), ("$56.28", "56,28 $")), (("Price target", "Objectif de cours"), ("$32 (−43%)", "32 $ (−43 %)")),
  (("Our 2027E EPS / Street", "Notre BPA 2027E / consensus"), ("$1.33 / $1.78", "1,33 $ / 1,78 $")), (("2028E EPS ours / Street", "BPA 2028E nous / consensus"), ("$1.70 / $3.00", "1,70 $ / 3,00 $")),
  (("Gross margin 2027E (non-GAAP) ours / Street", "Marge brute 2027E (non-GAAP) nous / consensus"), ("39.7% / 42.5%", "39,7 % / 42,5 %")), (("Q4 2026 guide", "Guidance T4 2026"), ("Rev $15-16bn, GM 38%, EPS $0.25", "CA 15-16 Md$, MB 38 %, BPA 0,25 $")),
  (("Target P/E / peer median", "PER cible / médiane des pairs"), ("24.1x / 16.8x", "24,1x / 16,8x")), (("P/E on Street NTM / on our 2027E", "PER sur consensus / sur notre 2027E"), ("32.5x / 42.4x", "32,5x / 42,4x")),
  (("Street target / implied P/E", "Objectif du consensus / PER implicite"), ("$90.91 / 51.2x", "90,91 $ / 51,2x")), (("Bridge from Street PT: EPS / multiple", "Pont depuis l’objectif consensus : BPA / multiple"), ("−$22.93 / −$35.98", "−22,93 $ / −35,98 $")),
  (("DCF (30%) / EV/EBITDA (40%) / P/E (30%)", "DCF (30 %) / VE/EBITDA (40 %) / PER (30 %)"), ("$20.96 / $48.68 / $22.31", "20,96 $ / 48,68 $ / 22,31 $")), (("WACC / terminal growth", "CMPC / croissance terminale"), ("11.5% / 2.5%", "11,5 % / 2,5 %")),
  (("Bull / bear / weighted", "Optimiste / pessimiste / pondéré"), ("$71.04 / $19.80 / $36.76", "71,04 $ / 19,80 $ / 36,76 $")), (("FCF 2027E ours / Street", "FCF 2027E nous / consensus"), ("−$5.7bn / −$2.7bn", "−5,7 / −2,7 Md$")),
  (("Diluted shares since 2023", "Actions diluées depuis 2023"), ("+29%", "+29 %")), (("52-week range", "Plus bas / plus haut 52 sem."), ("$32.89 – $142.35", "32,89 $ – 142,35 $")),
  (("Each 1 pt of gross margin", "Chaque point de marge brute"), ("≈ $0.10 of EPS", "≈ 0,10 $ de BPA")), (("Key date", "Date clé"), ("Late Jan 2027: Q4 + 2027 guide", "Fin janv. 2027 : T4 + guidance 2027")),
 ],
 "company": [
  ("Intel designs and manufactures x86 processors. **Client Computing (CCPG)** sells PC processors: $32.2bn of revenue in 2025, 61% of the total, at a 28.9% operating margin, and most of the profit. "
   "**Data Center & AI (DCAI)** sells server CPUs and custom chips: $16.9bn (32%), growing 53% in the first nine months of 2026, but supply-constrained into 2028.",
   "Intel conçoit et fabrique des processeurs x86. **Client Computing (CCPG)** vend les processeurs pour PC : 32,2 Md$ de CA en 2025, 61 % du total, à 28,9 % de marge opérationnelle, et l’essentiel du profit. "
   "**Data Center & AI (DCAI)** vend des processeurs pour serveurs et des puces sur mesure : 16,9 Md$ (32 %), en hausse de 53 % sur les neuf premiers mois de 2026, mais limité par l’offre jusqu’en 2028."),
  ("**Intel Foundry** makes almost all of Intel's own chips and is trying to win outside customers. It sells wafers mostly to Intel Products and lost $10.3bn in 2025 and $6.4bn in the first nine months of 2026: **the products earn, the factories lose**.",
   "**Intel Foundry** fabrique presque toutes les puces d’Intel et cherche des clients externes. Elle vend surtout des plaquettes à Intel Products et a perdu 10,3 Md$ en 2025 et 6,4 Md$ sur les neuf premiers mois de 2026 : **les produits gagnent, les usines perdent**."),
  ("Under CEO Lip-Bu Tan, capital goes to manufacturing: about $20bn of gross capex in 2026 and 'up strongly' in 2027. The balance sheet was rebuilt with equity from the US government, SoftBank and Nvidia and a $20bn share offering in August 2026: "
   "diluted shares are up 29% since 2023, and about $1.1bn of profit a year goes to minority partners in the fabs.",
   "Sous la direction de Lip-Bu Tan, le capital va à la fabrication : environ 20 Md$ d’investissements bruts en 2026 et « en forte hausse » en 2027. Le bilan a été reconstitué avec des fonds propres de l’État américain, de SoftBank et de Nvidia et une émission de 20 Md$ en août 2026 : "
   "les actions diluées ont augmenté de 29 % depuis 2023, et environ 1,1 Md$ de profit par an revient aux partenaires minoritaires des usines."),
 ],
 "money": ("Owning the fabs makes Intel the extreme case of **operating leverage**. A fab costs the same whether it runs full or half empty, so when volumes and prices rose in 2026 margins jumped, and when PC lines empty again margins fall fast. "
           "For Q4 Intel guided gross margin down about six points on 'lower overall revenue against our fixed-cost base'. Each point of gross margin is about $0.10 of EPS.",
           "Posséder ses usines fait d’Intel le cas extrême de **levier opérationnel**. Une usine coûte autant pleine qu’à moitié vide : quand volumes et prix ont monté en 2026, les marges ont bondi, et quand les lignes PC se vident, elles chutent vite. "
           "Pour le T4, Intel a annoncé une marge brute en baisse d’environ six points du fait d’un « chiffre d’affaires global plus faible face à notre base de coûts fixes ». Chaque point de marge brute vaut environ 0,10 $ de BPA."),
 "segments": [[("Segment (2025)", "Segment (2025)"), ("Revenue", "CA"), ("Share", "Part"), ("Profitability", "Rentabilité")],
              [("Client Computing (PCs)", "Client Computing (PC)"), ("$32.2bn", "32,2 Md$"), ("61%", "61 %"), ("28.9% operating margin", "28,9 % de marge opérationnelle")],
              [("Data Center & AI", "Data Center & AI"), ("$16.9bn", "16,9 Md$"), ("32%", "32 %"), ("+53% in 9M 2026", "+53 % sur 9 mois 2026")],
              [("Intel Foundry", "Intel Foundry"), ("mostly internal", "surtout interne"), ("—", "—"), ("−$10.3bn (2025)", "−10,3 Md$ (2025)")]],
 "industry": [
  ("Intel competes with AMD in x86 processors for PCs and servers, and with Arm-based designs (Apple, Qualcomm, cloud providers' own chips). As a manufacturer it competes with TSMC, which makes chips for AMD, Nvidia and Apple and keeps more than 90% of Apple's volume. "
   "Peers that only design chips (fabless) earn much higher margins because they do not carry factories.",
   "Intel affronte AMD sur les processeurs x86 pour PC et serveurs, ainsi que les conceptions Arm (Apple, Qualcomm, puces maison des fournisseurs de cloud). Comme fabricant, il affronte TSMC, qui produit pour AMD, Nvidia et Apple et garde plus de 90 % des volumes d’Apple. "
   "Les pairs qui ne font que concevoir (fabless) ont des marges bien plus élevées car ils ne portent pas d’usines."),
  ("2026 had two opposite forces. A **memory shortage** raised PC prices while IT budgets were tight, so PC units fall about 12% in 2026 and 10% in 2027. At the same time **AI agents** need more server CPUs (>30% unit growth), but Intel is short of substrates and Intel 3 output, and lost Fab 28 in October.",
   "2026 a connu deux forces opposées. Une **pénurie de mémoire** a fait monter le prix des PC alors que les budgets informatiques étaient serrés : les unités PC reculent d’environ 12 % en 2026 et 10 % en 2027. Dans le même temps, les **agents d’IA** demandent plus de processeurs serveurs (>30 % de croissance en unités), mais Intel manque de substrats et de production Intel 3, et a perdu la Fab 28 en octobre."),
 ],
 "drivers": [
  (("Fixed-cost fabs", "Des usines à coûts fixes"), ("A factory costs the same full or half empty. PC lines half empty → gross margin 44% (Q3) → 38% (Q4 guide).", "Une usine coûte autant pleine qu’à moitié vide. Lignes PC à moitié vides → marge brute 44 % (T3) → 38 % (guidance T4).")),
  (("A shrinking PC market", "Un marché du PC en recul"), ("Expensive memory → fewer PCs bought. Units −12% in 2026 and −10% in 2027; PCs are about half of Intel's revenue.", "Mémoire chère → moins de PC achetés. Unités −12 % en 2026 et −10 % en 2027 ; les PC font environ la moitié du CA d’Intel.")),
  (("Data centres at political risk", "Des data centers sous risque politique"), ("Intel's only growth engine (+78% y/y in Q3). After the 3 November midterms, Goldman sees ~45% of planned US capacity at risk from local moratoria.", "Le seul moteur de croissance d’Intel (+78 % sur un an au T3). Après les midterms du 3 novembre, Goldman voit ~45 % des capacités US prévues menacées par des moratoires locaux.")),
 ],
 "history": [
  (("2025", "2025"), ("Lip-Bu Tan becomes CEO; US government, SoftBank and Nvidia take equity stakes", "Lip-Bu Tan devient DG ; l’État américain, SoftBank et Nvidia entrent au capital")),
  (("Q1 2026", "T1 2026"), ("Reserved inventory sold at high prices; stock +24% on the print", "Stocks réservés vendus à prix élevés ; titre +24 % à la publication")),
  (("Jun 2026", "Juin 2026"), ("Stock peaks at $142.35", "Le titre culmine à 142,35 $")),
  (("May-Jun 2026", "Mai-juin 2026"), ("Reports of an Apple-Intel foundry agreement (WSJ), unconfirmed", "Informations sur un accord de fonderie Apple-Intel (WSJ), non confirmé")),
  (("11 Aug 2026", "11 août 2026"), ("$20bn share offering", "Augmentation de capital de 20 Md$")),
  (("Oct 2026", "Oct. 2026"), ("Fab 28 lost; server supply tighter", "Perte de la Fab 28 ; offre de serveurs plus tendue")),
  (("29 Oct 2026", "29 oct. 2026"), ("Q3: EPS $0.52 vs $0.41 expected, but Q4 guided to $0.25 vs $0.43; stock −28.6%", "T3 : BPA 0,52 $ contre 0,41 $ attendu, mais T4 annoncé à 0,25 $ contre 0,43 $ ; titre −28,6 %")),
  (("3 Nov 2026", "3 nov. 2026"), ("US midterms; data-centre moratoria become a risk", "Midterms américaines ; les moratoires sur les data centers deviennent un risque")),
 ],
 "history_read": ("The guide matters more than the beat: Intel beat Q3 and fell 28.6% because Q4 showed the windfall ending.", "La guidance compte plus que le résultat : Intel a battu le consensus au T3 et chuté de 28,6 % parce que le T4 montrait la fin de l’aubaine."),
 "screen": [
  ("Intel is **not a holding of the value strategy**. It was assigned by the instructor of the SKEMA Equity Research course (Paul Wuh), where Victor Endrizzi and I had to initiate coverage and defend a call. "
   "It is in this set because it is the mirror image of the value pitches: the stock has fallen 60% and looks cheap on price, but it is still **expensive on earnings**.",
   "Intel **n’est pas une ligne de la stratégie value**. Il a été attribué par l’enseignant du cours d’Equity Research de SKEMA (Paul Wuh), où Victor Endrizzi et moi devions initier la couverture et défendre un avis. "
   "Il figure dans cet ensemble car c’est l’image inverse des pitches value : le titre a chuté de 60 % et paraît bon marché sur le prix, mais reste **cher sur les bénéfices**."),
  ("This is the opposite lesson to Centene and OOIL: a large fall in price is not the same as a low multiple. Price fell, but so did earnings expectations, and they still have further to fall.",
   "C’est la leçon inverse de Centene et d’OOIL : une forte baisse du cours n’est pas un multiple bas. Le cours a baissé, mais les attentes de bénéfices aussi, et elles doivent encore baisser."),
 ],
 "pillars": [
  (("Peak margins, not a new base", "Un pic, pas une nouvelle base"), ("Q4 guide 38% vs 42.5% in 2027 consensus → EPS → P/E", "Guidance T4 38 % vs 42,5 % dans le consensus 2027 → BPA → PER")),
  (("Servers capped, PCs shrink", "Serveurs plafonnés, PC en recul"), ("Servers Intel can't supply; PCs (~half of revenue) fall → revenue → EPS", "Serveurs non livrables ; les PC (~la moitié du CA) reculent → CA → BPA")),
  (("Capex and dilution eat the cash", "Capex et dilution pèsent"), ("Capex up strongly; shares +29% since 2023 → FCF and EPS → multiple", "Capex en forte hausse ; actions +29 % depuis 2023 → FCF et BPA → multiple")),
 ],
 "thesis": [
  [("Non-GAAP gross margin rose from 41.0% in Q1 to 44.1% in Q3, helped by reserved inventory sold at high prices and by price rises, then Intel guided 38% for Q4 'against our fixed-cost base'. We keep 2027 near that run-rate: 39.7% non-GAAP (38.5% GAAP) against 42.5% for consensus.",
    "La marge brute non-GAAP est passée de 41,0 % au T1 à 44,1 % au T3, aidée par des stocks réservés vendus cher et des hausses de prix, puis Intel a annoncé 38 % pour le T4 « face à notre base de coûts fixes ». Nous gardons 2027 près de ce rythme : 39,7 % non-GAAP (38,5 % GAAP) contre 42,5 % pour le consensus."),
   ("Compare like with like: the course report first compared a GAAP margin with a non-GAAP consensus. On the same non-GAAP basis our figure is 39.7%. Each point of gross margin is about $0.10 of EPS.",
    "Comparer ce qui est comparable : le rapport du cours comparait d’abord une marge GAAP à un consensus non-GAAP. Sur la même base non-GAAP notre chiffre est de 39,7 %. Chaque point de marge brute vaut environ 0,10 $ de BPA.")],
  [("Server CPU demand grows more than 30%, but Intel is short of substrates and Intel 3 output and lost Fab 28: we model data center +26% while AMD takes share. PC units fall about 10% in 2027 and client revenue −9%.",
    "La demande de processeurs serveurs croît de plus de 30 %, mais Intel manque de substrats et de production Intel 3 et a perdu la Fab 28 : nous modélisons +26 % pour le data center pendant qu’AMD prend des parts. Les unités PC reculent d’environ 10 % en 2027 et le CA client de 9 %."),
   ("Revenue ends only 4.5% below consensus ($66.1bn vs $69.3bn): the EPS gap is margins, not volumes.", "Le CA ne finit que 4,5 % sous le consensus (66,1 Md$ contre 69,3 Md$) : l’écart de BPA vient des marges, pas des volumes.")],
  [("Capex rises 'strongly' in 2027 and depreciation reaches about $14.2bn; free cash flow is negative (−$5.7bn in 2027E vs −$2.7bn for the Street). Diluted shares are up 29% since 2023 and about $1.1bn of profit a year goes to fab partners.",
    "Les investissements montent « fortement » en 2027 et l’amortissement atteint environ 14,2 Md$ ; le free cash flow est négatif (−5,7 Md$ en 2027E contre −2,7 Md$ pour le consensus). Les actions diluées ont augmenté de 29 % depuis 2023 et environ 1,1 Md$ de profit par an revient aux partenaires des usines."),
   ("At 32.5x Street EPS the stock prices none of this.", "À 32,5x le BPA du consensus, le titre n’en intègre rien.")],
 ],
 "differ_intro": [("Unlike the value pitches, here we compare our forecast with the Bloomberg consensus (BEst, 6 November 2026), as in the course deck. The gap is margins first, then dilution.",
                   "Contrairement aux pitches value, nous comparons ici nos prévisions au consensus Bloomberg (BEst, 6 novembre 2026), comme dans le deck du cours. L’écart vient d’abord des marges, puis de la dilution.")],
 "differ_cols": [
  (("1 · Margins (GM 2027E)", "1 · Marges (MB 2027E)"), ("Street (Bloomberg)", "Consensus (Bloomberg)"), ("42.5%", "42,5 %"), ("Our view", "Notre vue"), ("39.7%", "39,7 %"),
   ("Q4 guide 38%; Q1 26 flattered by reserved inventory sold; underused PC fabs", "Guidance T4 38 % ; T1 26 flatté par les stocks réservés ; usines PC sous-utilisées")),
  (("2 · Servers & PCs (revenue)", "2 · Serveurs et PC (CA)"), ("Street (Bloomberg)", "Consensus (Bloomberg)"), ("$69.3bn", "69,3 Md$"), ("Our view", "Notre vue"), ("$66.1bn", "66,1 Md$"),
   ("Servers supply-capped (AMD gains share); PC units −10% in 2027", "Serveurs limités par l’offre (AMD gagne des parts) ; unités PC −10 % en 2027")),
  (("3 · Cash & dilution (EPS)", "3 · Cash et dilution (BPA)"), ("Street (Bloomberg)", "Consensus (Bloomberg)"), ("$1.78", "1,78 $"), ("Our view", "Notre vue"), ("$1.33", "1,33 $"),
   ("D&A $14.2bn as capex rises; shares +29% since 2023. Q4 guide $0.25 × 4 = $1.00", "Amortissements 14,2 Md$ avec la hausse des capex ; actions +29 % depuis 2023. Guidance T4 0,25 $ × 4 = 1,00 $")),
 ],
 "variant": [
  (("“2026 margins are the new base: 42.5% in 2027, $3.00 of EPS in 2028.”", "« Les marges 2026 sont la nouvelle base : 42,5 % en 2027, 3,00 $ de BPA en 2028. »"),
   ("They came from reserved inventory, price rises and a shortage; Intel itself guides 38% for Q4 'against our fixed-cost base'.", "Elles venaient de stocks réservés, de hausses de prix et d’une pénurie ; Intel annonce elle-même 38 % pour le T4 « face à notre base de coûts fixes ».")),
  (("“Intel is an AI winner: server CPUs are booming.”", "« Intel est un gagnant de l’IA : les processeurs serveurs explosent. »"),
   ("Demand is not the problem, supply is: substrates, Intel 3 and Fab 28 cap shipments and AMD takes the share.", "La demande n’est pas le problème, l’offre l’est : substrats, Intel 3 et Fab 28 limitent les livraisons et AMD prend les parts.")),
  (("“After a 60% fall it is priced in.”", "« Après une chute de 60 %, tout est dans le cours. »"),
   ("Not on earnings: 32.5x Street NTM EPS and 42.4x ours, against a peer median of 16.8x.", "Pas sur les bénéfices : 32,5x le BPA du consensus et 42,4x le nôtre, contre une médiane des pairs de 16,8x.")),
  (("“The Apple deal makes the foundry a business.”", "« L’accord Apple fait de la fonderie une vraie activité. »"),
   ("Unconfirmed, low-end chips from mid-2027, TSMC keeps >90% of Apple's volume: ~$1.2bn of external revenue in 2027E, no change to EPS.", "Non confirmé, des puces d’entrée de gamme à partir de mi-2027, TSMC garde >90 % des volumes d’Apple : ~1,2 Md$ de CA externe en 2027E, sans effet sur le BPA.")),
 ],
 "numbers_html": (_FIN_EN + _CAP_EN + "<h3>Peers on the same basis (Street NTM)</h3>" + _PEERS_EN, _FIN_FR + _CAP_FR + "<h3>Les pairs sur la même base (consensus à 12 mois)</h3>" + _PEERS_FR),
 "numbers_extra": [("On Street NTM numbers Intel trades at 32.5x earnings against a 16.8x peer median, with a 35% EBITDA margin against 53%: it is a more expensive, less profitable chip company. On our 2027E EPS the P/E is 42.4x.",
                    "Sur les chiffres du consensus à 12 mois, Intel cote 32,5x ses bénéfices contre une médiane des pairs de 16,8x, avec 35 % de marge d’EBITDA contre 53 % : une société de semi-conducteurs plus chère et moins rentable. Sur notre BPA 2027E, le PER est de 42,4x.")],
 "valuation": {
  "why": [("No single method is reliable for Intel in 2027. GAAP EPS is distorted by one-offs and by the escrowed-shares derivative; the DCF depends heavily on a terminal value because free cash flow is negative for two years; EV/EBITDA ignores the heavy depreciation. "
           "We therefore **blend three methods** and cross-check the result with a simple P/E on our 2027 EPS.",
           "Aucune méthode n’est fiable seule pour Intel en 2027. Le BPA GAAP est faussé par des éléments ponctuels et par le dérivé lié aux actions séquestrées ; le DCF dépend beaucoup de la valeur terminale car le free cash flow est négatif deux ans ; le VE/EBITDA ignore l’amortissement élevé. "
           "Nous **combinons donc trois méthodes** et recoupons le résultat par un PER simple sur notre BPA 2027."),
          ("Weights: **EV/EBITDA 40%** (least distorted by one-offs), **DCF 30%** (only 30% because 59% of its value is terminal value), **P/E comparables 30%**.",
           "Pondérations : **VE/EBITDA 40 %** (le moins faussé par les éléments ponctuels), **DCF 30 %** (seulement 30 % car 59 % de sa valeur est terminale), **PER comparables 30 %**.")],
  "formula": ("Target = 30% × DCF + 40% × EV/EBITDA comps + 30% × P/E comps ≈ 2027E EPS × target P/E", "Objectif = 30 % × DCF + 40 % × VE/EBITDA comparables + 30 % × PER comparables ≈ BPA 2027E × PER cible"),
  "inputs": [
   [("DCF value", "Valeur DCF"), ("$20.96", "20,96 $"), ("WACC 11.5%, terminal growth 2.5%; unlevered FCF negative in 2027-28", "CMPC 11,5 %, croissance terminale 2,5 % ; FCF non endetté négatif en 2027-28"),
    ("Implied exit multiple only 5x EBITDA; at 10x the DCF is $27-44, still below the price", "Multiple de sortie implicite de 5x l’EBITDA seulement ; à 10x, le DCF donne 27-44 $, toujours sous le cours")],
   [("EV/EBITDA comparables", "VE/EBITDA comparables"), ("$48.68", "48,68 $"), ("Peer median EV/EBITDA on our EBITDA, less net debt and minorities", "Médiane VE/EBITDA des pairs sur notre EBITDA, moins dette nette et minoritaires"),
    ("The highest of the three: it ignores Intel's heavy depreciation", "La plus haute des trois : elle ignore l’amortissement élevé d’Intel")],
   [("P/E comparables", "PER comparables"), ("$22.31", "22,31 $"), ("Peer-based P/E on our 2027E EPS of $1.33", "PER issu des pairs sur notre BPA 2027E de 1,33 $"), ("Close to the DCF", "Proche du DCF")],
   [("Cross-check: target P/E", "Contrôle : PER cible"), ("24.1x", "24,1x"), ("$32 / $1.33", "32 $ / 1,33 $"),
    ("Above the 16.8x peer median because 2027 is a trough year; on 2028E EPS ($1.70) it is only ~19x", "Au-dessus de la médiane des pairs (16,8x) car 2027 est une année creuse ; sur le BPA 2028E (1,70 $) cela ne fait que ~19x")],
  ],
  "walk": [("**Step 1.** 30% × $20.96 + 40% × $48.68 + 30% × $22.31 = $6.29 + $19.47 + $6.69 = **$32.45**, rounded to **$32**.",
            "**Étape 1.** 30 % × 20,96 $ + 40 % × 48,68 $ + 30 % × 22,31 $ = 6,29 $ + 19,47 $ + 6,69 $ = **32,45 $**, arrondi à **32 $**."),
           ("**Step 2.** Cross-check: $1.33 × 24.1x = $32.05. Against $56.28: −43%, below the −10% sell threshold, so **Sell**.", "**Étape 2.** Contrôle : 1,33 $ × 24,1x = 32,05 $. Contre 56,28 $ : −43 %, sous le seuil de vente de −10 %, donc **Vendre**."),
           ("**Step 3.** Scenarios: bull = Street EPS $1.78 × 40x = $71.04 (+26%); bear = $0.90 × 22x = $19.80 (−65%). Weighted 20% bull, 55% base, 25% bear: **$36.76** (−35%), still a Sell.",
            "**Étape 3.** Scénarios : optimiste = BPA du consensus 1,78 $ × 40x = 71,04 $ (+26 %) ; pessimiste = 0,90 $ × 22x = 19,80 $ (−65 %). Pondéré 20 % optimiste, 55 % central, 25 % pessimiste : **36,76 $** (−35 %), toujours Vendre.")],
  "implied": [("The Street's $90.91 target is **51.2x** 2027 EPS of $1.78, while the market pays 32.5x NTM today. The bridge from the Street's target to ours: **−$22.93** from lower EPS (the Street's multiple on our EPS) and **−$35.98** from a lower multiple.",
               "L’objectif du consensus de 90,91 $ représente **51,2x** le BPA 2027 de 1,78 $, alors que le marché paie aujourd’hui 32,5x à 12 mois. Le pont de l’objectif du consensus au nôtre : **−22,93 $** dus au BPA plus bas (multiple du consensus sur notre BPA) et **−35,98 $** dus au multiple plus bas."),
              ("From today's price: −$14.20 from lower EPS and −$10.08 from a lower multiple; **58% of our gap to the price is earnings**, not just a multiple call.",
               "Depuis le cours actuel : −14,20 $ dus au BPA et −10,08 $ dus au multiple ; **58 % de notre écart avec le cours vient des bénéfices**, pas seulement d’un jugement sur le multiple.")],
  "cross": [("**Peers:** at 16.8x (peer median) our $1.33 would give $22. **2028:** our $32 is 18.8x our 2028E EPS of $1.70. **History:** the stock started 2026 around $39 and the 52-week low is $32.89.",
             "**Pairs :** à 16,8x (médiane des pairs), nos 1,33 $ donneraient 22 $. **2028 :** nos 32 $ représentent 18,8x notre BPA 2028E de 1,70 $. **Historique :** le titre a commencé 2026 vers 39 $ et le plus bas sur 52 semaines est de 32,89 $.")],
  "limits": [("The blend weights are our judgement. The DCF is fragile (59% terminal value, negative near-term cash flow). EV/EBITDA comps flatter a capital-heavy business. And a Sell into a heavily shorted, volatile stock can hurt: Intel rose 24% on its Q1 print.",
              "Les pondérations sont notre jugement. Le DCF est fragile (59 % de valeur terminale, cash-flow négatif à court terme). Les comparables VE/EBITDA flattent une activité très capitalistique. Et vendre un titre très shorté et volatil peut coûter cher : Intel a pris 24 % à la publication du T1.")],
 },
 "events": [
  (("Late Jan 2027", "Fin janv. 2027"), ("Hard", "Ferme"), ("Q4 results + 2027 guide", "Résultats T4 + guidance 2027"),
   ("Street: FY27 EPS $1.78, GM back above 42%", "Consensus : BPA 2027 de 1,78 $, MB revenue au-dessus de 42 %"),
   ("Us: GM ~39.7%, EPS $1.33 · Impact: −$22.93/share", "Nous : MB ~39,7 %, BPA 1,33 $ · Impact : −22,93 $/action")),
  (("Jan 2027", "Janv. 2027"), ("Soft", "Incertain"), ("PC data + CES Las Vegas", "Données PC + CES Las Vegas"),
   ("Street: PC recovery in H2 2027", "Consensus : reprise des PC au S2 2027"), ("Us: PC units −10% → client −9% · Impact: each −5% client ≈ −$0.09 EPS", "Nous : unités PC −10 % → client −9 % · Impact : chaque −5 % client ≈ −0,09 $ de BPA")),
  (("H1 2027", "S1 2027"), ("Soft", "Incertain"), ("Data-centre policy after the midterms", "Politique des data centers après les midterms"),
   ("Street: AI build-out intact", "Consensus : la construction IA continue"), ("Us: moratoria slow server builds · Impact: bear case $19.80", "Nous : les moratoires freinent les serveurs · Impact : pessimiste 19,80 $")),
  (("Q2-Q3 2027", "T2-T3 2027"), ("Hard", "Ferme"), ("First Apple chips on 18A-P", "Premières puces Apple en 18A-P"),
   ("Street: foundry inflection", "Consensus : tournant de la fonderie"), ("Us: low-end chips; TSMC keeps >90% · Impact: ~$1.2bn foundry revenue, no EPS change", "Nous : puces d’entrée de gamme ; TSMC garde >90 % · Impact : ~1,2 Md$ de CA fonderie, BPA inchangé")),
 ],
 "key": 0,
 "key_catalyst": [("**Late January 2027: Q4 2026 results and the first 2027 outlook** (Q1 guide, gross margin, capex). The Street needs $0.44 of EPS a quarter in 2027; Intel guides $0.25 for Q4. If consensus moves to our $1.33 at its own 51.2x multiple, that is **−$22.93 a share**.",
                   "**Fin janvier 2027 : résultats du T4 2026 et premières perspectives 2027** (guidance du T1, marge brute, capex). Le consensus a besoin de 0,44 $ de BPA par trimestre en 2027 ; Intel annonce 0,25 $ pour le T4. Si le consensus passe à nos 1,33 $ à son propre multiple de 51,2x, c’est **−22,93 $ par action**.")],
 "risks": [
  (("Server supply fixed early", "Offre de serveurs débloquée tôt"), ("Each +10% of data-centre revenue ≈ +$0.19 of EPS. Signpost: DCAI above $9bn a quarter at gross margin above 42%.", "Chaque +10 % de CA data center ≈ +0,19 $ de BPA. Signal : DCAI au-dessus de 9 Md$ par trimestre avec une marge brute au-dessus de 42 %.")),
  (("Apple + a 14A anchor customer", "Apple + un client de référence sur le 14A"), ("The foundry is re-rated before profits → bull case $71 (+26%). Signpost: confirmed volumes, 14A prepayments.", "La fonderie est revalorisée avant les profits → optimiste 71 $ (+26 %). Signal : volumes confirmés, prépaiements sur le 14A.")),
  (("Early PC recovery", "Reprise précoce des PC"), ("Memory prices fall → PCs back in H2 2027 ≈ +$0.19 of EPS. Signpost: DRAM contract prices, IDC PC data.", "Baisse du prix de la mémoire → PC de retour au S2 2027 ≈ +0,19 $ de BPA. Signal : prix contractuels de la DRAM, données IDC.")),
  (("Short squeeze", "Rachat forcé des vendeurs à découvert"), ("After a 60% fall, short interest is high and the stock rose 24% on its Q1 print. No short into January without a stop.", "Après une chute de 60 %, les positions vendeuses sont élevées et le titre a pris 24 % sur le T1. Pas de vente à découvert avant janvier sans stop.")),
 ],
 "triggers": ("Data-centre revenue above $9bn a quarter at gross margin above 42%; Apple volumes confirmed together with a 14A anchor customer and prepayments; DRAM prices falling early with IDC data showing PCs recovering in H1 2027.",
              "un CA data center au-dessus de 9 Md$ par trimestre avec une marge brute au-dessus de 42 % ; des volumes Apple confirmés avec un client de référence 14A et des prépaiements ; une baisse précoce de la DRAM avec des données IDC montrant une reprise des PC au S1 2027."),
 "qa": [
  (("Isn't all of this priced in after a 60% fall?", "Tout n’est-il pas dans le cours après une chute de 60 % ?"),
   ("No: at $56.28 the stock trades at 32.5x Street EPS and 42.4x ours, against 16.8x for peers; the price still assumes margins back above 42%.", "Non : à 56,28 $ le titre cote 32,5x le BPA du consensus et 42,4x le nôtre, contre 16,8x pour les pairs ; le cours suppose encore des marges revenues au-dessus de 42 %.")),
  (("Why is your target so far from the Street's?", "Pourquoi ton objectif est-il si loin de celui du consensus ?"),
   ("Two parts: −$22.93 from lower EPS and −$35.98 from the multiple. The Street's $90.91 implies 51.2x 2027 EPS while the market pays 32.5x today.", "Deux parties : −22,93 $ dus au BPA et −35,98 $ dus au multiple. Les 90,91 $ du consensus impliquent 51,2x le BPA 2027 quand le marché paie 32,5x aujourd’hui.")),
  (("What is the single most important assumption?", "Quelle est l’hypothèse la plus importante ?"),
   ("2027 gross margin: 39.7% non-GAAP (38.5% GAAP) against 42.5% for consensus. Each point is about $0.10 of EPS.", "La marge brute 2027 : 39,7 % non-GAAP (38,5 % GAAP) contre 42,5 % pour le consensus. Chaque point vaut environ 0,10 $ de BPA.")),
  (("Intel beat Q3. Why didn't you raise numbers?", "Intel a battu le consensus au T3. Pourquoi ne pas relever les chiffres ?"),
   ("Because the guide matters more than the beat: Q3 EPS $0.52 vs $0.41 expected, but Q4 guided to $0.25 vs $0.43 and the stock fell 28.6%.", "Parce que la guidance compte plus que le résultat : BPA T3 de 0,52 $ contre 0,41 $ attendu, mais T4 annoncé à 0,25 $ contre 0,43 $ et le titre a chuté de 28,6 %.")),
  (("Why is your target P/E (24x) above the peer median (17x)?", "Pourquoi ton PER cible (24x) dépasse-t-il la médiane des pairs (17x) ?"),
   ("2027 is a trough year for Intel's margins, so the peer multiple on trough EPS would be too harsh; 24x is still far below the 51x in the Street's target, and only ~19x our 2028E.", "2027 est une année creuse pour les marges d’Intel, le multiple des pairs sur un BPA de creux serait trop sévère ; 24x reste très loin des 51x de l’objectif du consensus, et ne fait que ~19x notre 2028E.")),
  (("Why is the DCF so low ($21)?", "Pourquoi le DCF est-il si bas (21 $) ?"),
   ("FCF is negative in 2027-28 and capex converges to depreciation only slowly; the implied exit multiple is 5x EBITDA. With 10x the DCF is $27-44, still below the price.", "Le FCF est négatif en 2027-28 et les capex ne convergent que lentement vers l’amortissement ; le multiple de sortie implicite est de 5x l’EBITDA. À 10x, le DCF donne 27-44 $, toujours sous le cours.")),
  (("Explain GAAP vs non-GAAP gross margin.", "Explique la marge brute GAAP et non-GAAP."),
   ("Non-GAAP excludes stock-based pay and amortisation of acquired intangibles, so it is about 1.2 points higher. Always compare like with like: our 39.7% non-GAAP against the Street's 42.5% non-GAAP.", "Le non-GAAP exclut la rémunération en actions et l’amortissement des incorporels acquis, il est donc environ 1,2 point plus haut. Toujours comparer ce qui est comparable : nos 39,7 % non-GAAP contre 42,5 % non-GAAP pour le consensus.")),
  (("What would make you change your rating?", "Qu’est-ce qui te ferait changer d’avis ?"),
   ("Data-centre revenue above $9bn a quarter at gross margin above 42%, or confirmed Apple volumes together with a 14A anchor customer.", "Un CA data center au-dessus de 9 Md$ par trimestre avec une marge brute au-dessus de 42 %, ou des volumes Apple confirmés avec un client de référence sur le 14A.")),
  (("Would you short it today?", "Le vendrais-tu à découvert aujourd’hui ?"),
   ("Not into the January print without a stop: Intel rose 24% on its Q1 print and short interest can make a squeeze violent.", "Pas avant la publication de janvier sans stop : Intel a pris 24 % sur le T1 et les positions vendeuses peuvent rendre un rachat forcé violent.")),
  (("How did you use AI in this work?", "Comment as-tu utilisé l’IA dans ce travail ?"),
   ("To extract figures from the 10-K and 10-Qs, draft the model and the deck, and argue the Buy case against us. We checked key numbers against the filings and replaced one AI error (a GAAP-mixed consensus EPS) with Bloomberg data. Rating, target and thesis are ours.",
    "Pour extraire des chiffres du 10-K et des 10-Q, rédiger des premières versions du modèle et du deck, et plaider l’achat contre nous. Nous avons vérifié les chiffres clés dans les publications et remplacé une erreur de l’IA (un BPA de consensus mélangeant GAAP et non-GAAP) par les données Bloomberg. Avis, objectif et thèse sont les nôtres.")),
 ],
 "glossary": [
  (("IDM", "IDM"), ("Integrated device manufacturer: designs and makes its own chips (Intel), unlike fabless designers (AMD, Nvidia) or pure foundries (TSMC).", "Fabricant intégré : conçoit et fabrique ses puces (Intel), contrairement aux concepteurs sans usine (AMD, Nvidia) ou aux fonderies pures (TSMC).")),
  (("Gross margin (GAAP vs non-GAAP)", "Marge brute (GAAP vs non-GAAP)"), ("Non-GAAP excludes stock pay and acquired-intangible amortisation; compare like with like.", "Le non-GAAP exclut la rémunération en actions et l’amortissement des incorporels acquis ; comparer ce qui est comparable.")),
  (("NTM", "12 mois glissants (NTM)"), ("Next twelve months: consensus estimates for the coming four quarters.", "Les douze prochains mois : estimations du consensus pour les quatre trimestres à venir.")),
  (("WACC", "CMPC (WACC)"), ("Weighted average cost of capital: the discount rate of the DCF (11.5% for Intel).", "Coût moyen pondéré du capital : le taux d’actualisation du DCF (11,5 % pour Intel).")),
  (("Terminal value", "Valeur terminale"), ("The value of all cash flows after the forecast period; 59% of Intel's DCF.", "La valeur de tous les flux après la période de prévision ; 59 % du DCF d’Intel.")),
  (("18A / 14A", "18A / 14A"), ("Intel's most advanced manufacturing processes; 14A needs an outside anchor customer to be worth building.", "Les procédés de fabrication les plus avancés d’Intel ; le 14A a besoin d’un client externe de référence pour être rentable.")),
  (("Short squeeze", "Rachat forcé (short squeeze)"), ("A sharp rise forcing short sellers to buy back, which pushes the price higher still.", "Une forte hausse qui oblige les vendeurs à découvert à racheter, ce qui fait encore monter le cours.")),
 ],
 "data_note": ("Company figures come from Intel's 10-K and 10-Qs; consensus, peers and prices from Bloomberg (6 November 2026); forecasts and valuation from our course model (Intel_INTC_Sell_Model_FINAL_v2.xlsx). Written with Victor Endrizzi for the SKEMA Equity Research course (Paul Wuh).",
               "Les chiffres de la société viennent du 10-K et des 10-Q d’Intel ; consensus, pairs et cours de Bloomberg (6 novembre 2026) ; prévisions et valorisation de notre modèle du cours (Intel_INTC_Sell_Model_FINAL_v2.xlsx). Rédigé avec Victor Endrizzi pour le cours d’Equity Research de SKEMA (Paul Wuh)."),
}
