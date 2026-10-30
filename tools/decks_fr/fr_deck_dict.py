"""English -> French text for the pitch decks. Exact strings first, then patterns, then French number formatting."""
import re

T = {
 # ---------------------------------------------------------------- recurring slide furniture
 "STOCK PITCH  ·  SYSTEMATIC VALUE PORTFOLIO  ·  29 OCTOBER 2026": "STOCK PITCH  ·  PORTEFEUILLE VALUE SYSTÉMATIQUE  ·  29 OCTOBRE 2026",
 "Price": "Cours", "Target (base case)": "Objectif (scénario central)", "Upside / downside": "Potentiel", "Horizon": "Horizon",
 "Market cap": "Capitalisation", "Dividend yield": "Rendement du dividende",
 "Noah Doose  ·  MSc Financial Markets & Investments, SKEMA Business School  ·  Student research for educational purposes, not investment advice":
     "Noah Doose  ·  MSc Financial Markets & Investments, SKEMA Business School  ·  Travail étudiant à visée pédagogique, pas un conseil en investissement",
 "01  EXECUTIVE SUMMARY": "01  SYNTHÈSE", "02  COMPANY SNAPSHOT": "02  LA SOCIÉTÉ", "03  INDUSTRY AND MACRO BACKDROP": "03  SECTEUR ET MACRO",
 "04  WHY THE SYSTEMATIC SCREEN PICKED IT": "04  POURQUOI LE SCREEN L'A CHOISI", "05  TRACK RECORD IN THE PORTFOLIO": "05  HISTORIQUE DANS LE PORTEFEUILLE",
 "06  FINANCIAL SNAPSHOT": "06  CHIFFRES CLÉS", "07  VARIANT PERCEPTION": "07  VARIANT PERCEPTION", "08  VALUATION": "08  VALORISATION",
 "09  CATALYSTS": "09  CATALYSEURS", "10  RISKS AND SELL DISCIPLINE": "10  RISQUES ET DISCIPLINE DE VENTE", "11  SOURCES AND DISCLOSURES": "11  SOURCES ET AVERTISSEMENTS",
 "What moves the stock beyond the company": "Ce qui fait bouger le titre au-delà de la société",
 "Source: company releases and research brief (see Sources slide)": "Source : communiqués de la société et note de recherche (voir la slide Sources)",
 "H1 2026 return (EUR)": "Performance S1 2026 (EUR)", "MSCI World Net EUR, H1 2026": "MSCI World Net EUR, S1 2026",
 "Weight, equal weight": "Poids, équipondéré", "Min-variance / mean-variance": "Variance minimale / moyenne-variance",
 "Source: pipeline weekly total returns (EUR, net of withholding tax) and portfolio weights at the 31 Dec 2025 rebalance":
     "Source : rendements totaux hebdomadaires du pipeline (EUR, nets de retenue à la source) et poids du portefeuille au rebalancement du 31 déc. 2025",
 "Reported numbers and guidance": "Chiffres publiés et guidance", "Trend": "Tendance",
 "Where we differ from the market": "Là où nous divergeons du marché", "WHAT THE MARKET BELIEVES": "CE QUE CROIT LE MARCHÉ", "OUR VIEW": "NOTRE LECTURE",
 "What the bulls say, and what the evidence says": "Ce que disent les optimistes, et ce que montrent les faits",
 "THE BULL ARGUMENT": "L'ARGUMENT OPTIMISTE", "WHAT THE EVIDENCE SAYS": "CE QUE MONTRENT LES FAITS",
 "Scenario": "Scénario", "Key inputs": "Hypothèses", "Value / share": "Valeur / action", "vs price": "vs cours",
 "Bear": "Pessimiste", "Base": "Central", "Bull": "Optimiste", "Valuation range": "Fourchette de valorisation",
 "52-week range": "Plage 52 semaines", "Scenario range (bear - bull)": "Scénarios (pessimiste - optimiste)",
 "Consensus target (third-party)": "Objectif du consensus (tiers)",
 "Source: own valuation; 52-week range and consensus from third-party data (29 Oct 2026)": "Source : valorisation propre ; plage 52 semaines et consensus issus de données tierces (29 oct. 2026)",
 "What could move the stock in the next 12-18 months": "Ce qui peut faire bouger le titre dans les 12-18 prochains mois",
 "What could move the stock in the next 12 months": "Ce qui peut faire bouger le titre dans les 12 prochains mois",
 "What could move the stock in the next 18-24 months": "Ce qui peut faire bouger le titre dans les 18-24 prochains mois",
 "What could move the stock in the next 2-3 years": "Ce qui peut faire bouger le titre dans les 2-3 prochaines années",
 "The number to watch: ": "Le chiffre à suivre : ", "Risk": "Risque", "Mitigant": "Atténuation",
 "Risks, mitigants and what would make us sell": "Risques, atténuations et ce qui nous ferait vendre",
 "What would change our view": "Ce qui nous ferait changer d'avis",
 "WE SELL IF": "NOUS VENDONS SI", "WE CHANGE THE CALL IF": "NOUS CHANGEONS D'AVIS SI", "WE WOULD CHANGE OUR VIEW IF": "NOUS CHANGERIONS D'AVIS SI",
 "Sources": "Sources",
 "Portfolio Project pipeline: scores, multiples, weights and returns computed from Bloomberg data extracted on the SKEMA terminal (Oct 2026).":
     "Pipeline du Portfolio Project : scores, multiples, poids et rendements calculés à partir de données Bloomberg extraites sur le terminal de SKEMA (oct. 2026).",
 "OVERWEIGHT": "SURPONDÉRER", "NEUTRAL": "NEUTRE", "UNDERWEIGHT": "SOUS-PONDÉRER",
 "Medium conviction": "Conviction moyenne", "Medium-high conviction": "Conviction moyenne-forte", "Case study": "Cas d'école",
 "12 months": "12 mois", "12-18 months": "12-18 mois", "18-24 months": "18-24 mois", "2-3 years": "2-3 ans",
 "Price: close, 29 Oct 2026": "Cours : clôture, 29 oct. 2026", "Price: intraday, 29 Oct 2026": "Cours : en séance, 29 oct. 2026",
 "Price: close, 29 Oct 2026, before H1 results": "Cours : clôture, 29 oct. 2026, avant les résultats S1",
 "Revenue": "Chiffre d'affaires", "Operating profit": "Résultat opérationnel", "Operating margin": "Marge opérationnelle",
 "Profit attributable": "Résultat part du groupe", "EPS": "BPA", "DPS": "Dividende par action", "Free cash flow": "Free cash flow",
 "Net sales": "Chiffre d'affaires", "Ordinary profit": "Résultat ordinaire", "Net profit": "Résultat net", "Net debt / EBITDA": "Dette nette / EBITDA",
 "Total revenues": "Chiffre d'affaires total", "Adjusted diluted EPS": "BPA dilué ajusté", "GAAP diluted EPS": "BPA dilué GAAP",
 "Total debt": "Dette totale", "Debt / capital": "Dette / capitaux", "Net revenue": "Chiffre d'affaires net",
 "Personal Systems margin": "Marge Personal Systems", "Printing margin": "Marge Impression", "Non-GAAP diluted EPS": "BPA dilué non-GAAP",
 "Group revenue": "Chiffre d'affaires du groupe", "Group operating margin": "Marge opérationnelle du groupe",
 "Automotive free cash flow": "Free cash flow automobile", "Automotive net cash (period end)": "Trésorerie nette automobile (fin de période)",
 "Net income, group share": "Résultat net part du groupe", "Revenues (NBI)": "Revenus (PNB)", "Cost / income": "Coefficient d'exploitation",
 "Return on tangible equity": "Rentabilité des fonds propres tangibles", "CET1 ratio": "Ratio CET1", "Dividend per share": "Dividende par action",
 "Cost of risk": "Coût du risque", "Sales incl. VAT (pre-IAS 29)": "Ventes TTC (avant IAS 29)", "Recurring operating income": "Résultat opérationnel courant",
 "ROI margin": "Marge opérationnelle courante", "Adjusted EPS": "BPA ajusté", "Net free cash flow": "Free cash flow net", "Net financial debt": "Dette financière nette",
 "Underlying business profit": "Profit opérationnel sous-jacent", "of which U.S. Steel": "dont U.S. Steel", "Profit to owners": "Résultat part du groupe",
 "EPS (post-split)": "BPA (après division)", "DPS (post-split)": "Dividende (après division)",
 "Q1 FY2026": "T1 ex. 2026", "FY2026 guide": "Guidance ex. 2026", "H1 FY2026": "S1 ex. 2026", "9M 2026": "9 mois 2026", "2026 target": "Objectif 2026",
 "2026 guide (Oct)": "Guidance 2026 (oct.)", "2026 guide": "Guidance 2026", "Q3 FY2026": "T3 ex. 2026", "Q3 2026": "T3 2026", "H1 2026": "S1 2026",
 "FY26 guide": "Guidance ex. 2026", "FY2026 guide (Aug)": "Guidance ex. 2026 (août)",
 "growth": "croissance", "stable to slightly up": "stable à légère hausse", "slight decline": "légère baisse",
 "payout ~50%": "distribution ~50 %", "payout 60%": "distribution 60 %", "payout 50-60%": "distribution 50-60 %",
 "Q3 liner rev. +45%": "CA maritime T3 +45 %", "Net cash (cash − leases)": "Trésorerie nette (cash − loyers)",
 "> 5% CAGR": "> 5 % TCAC", "> 7% CAGR": "> 7 % TCAC", "> 13% (end-2026)": "> 13 % (fin 2026)", "39 bp (Q3)": "39 pb (T3)", "+0 to +15 bp": "+0 à +15 pb",
 "¥24 (minimum)": "24 ¥ (minimum)", "~5x (plan)": "~5x (plan)", "US$0.55 interim": "0,55 US$ acompte", "€3.23 interim": "3,23 € acompte", "¥40 interim": "40 ¥ acompte",
 "Other": "Autres", "Other countries": "Autres pays", "Energy": "Énergie", "Real estate": "Immobilier", "Capital": "Capital", "Control": "Contrôle",
 "Balance sheet": "Bilan", "Geography": "Géographie", "Mix": "Mix", "Currencies": "Devises", "Regulation": "Réglementation", "Yen": "Yen",
 "Crude oil": "Pétrole brut", "Middle East": "Moyen-Orient", "Input costs": "Coûts des intrants", "EV transition": "Transition électrique",
 "Rates and credit": "Taux et crédit", "European car demand": "Demande automobile européenne", "Memory prices": "Prix des mémoires",
 "Windows 10 end of support": "Fin du support de Windows 10", "AI PCs": "PC IA", "Growth areas": "Relais de croissance",
 "Printing": "Impression", "Personal Systems": "Personal Systems",
 # ---------------------------------------------------------------- chart labels
 "Peer median": "Médiane des pairs", "Sector median": "Médiane du secteur", "z-score": "z-score", "EBIT / EV": "EBIT / VE", "Book / price": "Valeur comptable / cours",
 "FCF yield": "Rendement FCF", "Sales / EV": "CA / VE", "Earnings / price": "Bénéfices / cours", "EV/EBIT": "VE/EBIT", "EV/Sales": "VE/CA", "P/E": "PER", "P/B": "P/B", "P/FCF": "P/FCF",
 "Liner revenue by trade lane, FY2025": "CA maritime par route commerciale, 2025", "Trans-Pacific": "Transpacifique", "Intra-Asia / Australasia": "Intra-Asie / Australasie",
 "Asia-Europe": "Asie-Europe", "Trans-Atlantic": "Transatlantique", "Domestic": "Japon", "Overseas incl. raw materials": "Étranger, matières premières incluses",
 "FY2026f": "Ex. 2026 prév.", "Own generation mix, FY2025 (94.2 TWh)": "Mix de production propre, ex. 2025 (94,2 TWh)", "Nuclear": "Nucléaire", "Thermal": "Thermique", "Hydro": "Hydraulique",
 "Division revenues (NBI), 9M 2026": "PNB par pôle, 9 mois 2026", "Commercial, Personal Banking & Services": "Banque commerciale et services",
 "Corporate & Institutional Banking": "Banque de financement et d'investissement", "Investment & Protection Services": "Épargne, assurance et gestion",
 "Sales incl. VAT by country, H1 2026": "Ventes TTC par pays, S1 2026", "France": "France", "Brazil": "Brésil", "Spain": "Espagne",
 "Members by product, Sep 2026": "Adhérents par produit, sept. 2026", "Marketplace": "Marketplace", "Medicare Part D (PDP)": "Medicare partie D (PDP)",
 "Medicare Advantage & supplement": "Medicare Advantage et complémentaire", "Revenue by segment, FY2025": "Chiffre d'affaires par activité, ex. 2025",
 "Revenue split, 9M 2026": "Répartition du CA, 9 mois 2026", "Automotive": "Automobile", "Mobilize Financial Services": "Mobilize Financial Services",
 "Total return in EUR, rebased to 100 (Jun 2021 - Jun 2026, weekly)": "Rendement total en EUR, base 100 (juin 2021 - juin 2026, hebdo)",
 "Multiples at 31 Dec 2025 (last usable fiscal year)": "Multiples au 31 déc. 2025 (dernier exercice utilisable)",
 "Value z-scores within the sector (Dec 2025)": "Z-scores value dans le secteur (déc. 2025)",
 # ---------------------------------------------------------------- OOIL
 "Case study: The highest value score in our universe, on peak-cycle earnings": "Cas d'école : le meilleur score value de notre univers, sur des bénéfices de haut de cycle",
 "Container shipping (OOCL)": "Transport de conteneurs (OOCL)",
 "A pure-play liner: 139 vessels and 1.15m TEU of capacity at end-2025, member of the Ocean Alliance.": "Un armateur pur : 139 navires et 1,15 M EVP de capacité fin 2025, membre de l'Ocean Alliance.",
 "Trade lanes": "Routes commerciales",
 "Trans-Pacific (most US policy exposure), Asia-Europe, Trans-Atlantic and Intra-Asia (most volume).": "Transpacifique (la plus exposée à la politique américaine), Asie-Europe, Transatlantique et Intra-Asie (le plus gros volume).",
 "COSCO Shipping holds 71.07% and Shanghai International Port Group 9.06%: the free float is about 20%.": "COSCO Shipping détient 71,07 % et Shanghai International Port Group 9,06 % : le flottant est d'environ 20 %.",
 "No bank debt; US$5.8bn of cash against US$1.3bn of lease liabilities at June 2026.": "Aucune dette bancaire ; 5,8 Md US$ de trésorerie contre 1,3 Md US$ de dettes locatives à juin 2026.",
 "Freight rates": "Taux de fret", "Asia-US spot rates by early June 2026 after the Hormuz disruption (Cape routing again).": "Taux spot Asie-États-Unis début juin 2026 après la perturbation d'Ormuz (retour par le Cap).",
 "Fleet vs demand": "Flotte vs demande", "2026 fleet growth ahead of demand growth: the structural pressure on rates.": "Croissance de la flotte 2026 supérieure à celle de la demande : la pression structurelle sur les taux.",
 "US port fees": "Taxes portuaires US", "Section 301 fees on Chinese operators (US$50 per net ton) resume unless extended.": "Les taxes Section 301 sur les armateurs chinois (50 US$ par tonne nette) reprennent sauf prolongation.",
 "Bunker fuel": "Carburant de soute", "Average H1 2026 cost (+8%): the largest variable cost.": "Coût moyen S1 2026 (+8 %) : le premier coût variable.",
 "No numeric guidance. FCF after lease payments was about −US$0.69bn in 2025 and −US$0.35bn in H1 2026 (derived). Sources: OOIL annual report 2025 and interim report 2026.":
     "Pas de guidance chiffrée. FCF après loyers d'environ −0,69 Md US$ en 2025 et −0,35 Md US$ au S1 2026 (calculé). Sources : rapport annuel 2025 et rapport semestriel 2026 d'OOIL.",
 "“Net cash of US$4.5bn makes it safe”": "« 4,5 Md US$ de trésorerie nette le rendent sûr »",
 "Yard and charter commitments (~US$7.5bn) exceed net cash; FCF after leases was negative in 2025 and H1 2026.": "Les engagements de chantiers et d'affrètement (~7,5 Md US$) dépassent la trésorerie nette ; le FCF après loyers était négatif en 2025 et au S1 2026.",
 "“The dividend yield is attractive”": "« Le rendement du dividende est attractif »",
 "Dividends follow profits: US$10.56 per share in 2022, US$1.14 in 2025. A trailing yield overstates future income.": "Les dividendes suivent les profits : 10,56 US$ par action en 2022, 1,14 US$ en 2025. Un rendement passé surestime les revenus futurs.",
 "“Q3 2026 shows a new up-cycle”": "« Le T3 2026 montre un nouveau cycle haussier »",
 "The spike is geopolitical. Port fees on Chinese operators may return on 10 November 2026.": "Le pic est géopolitique. Les taxes portuaires sur les armateurs chinois peuvent revenir le 10 novembre 2026.",
 "Disruption lasts longer (Hormuz, Cape routing)": "La perturbation dure (Ormuz, route du Cap)", "Underweight, not short: we hold the model weight": "Sous-pondérer, pas vendre à découvert : nous gardons le poids du modèle",
 "Special dividend from the cash pile": "Dividende exceptionnel financé par la trésorerie", "Possible under the payout policy; would narrow the gap": "Possible selon la politique de distribution ; réduirait l'écart",
 "COSCO-related capital allocation": "Allocation du capital liée à COSCO", "Governance set by the parent; thin float": "Gouvernance fixée par la maison mère ; flottant étroit",
 "US-China policy swings": "Revirements de la politique sino-américaine", "Fees and tariffs cut both ways": "Taxes et droits de douane jouent dans les deux sens",
 # ---------------------------------------------------------------- Nippon Steel
 "Domestic steel": "Acier au Japon", "Japan's largest integrated steelmaker: ¥528bn of underlying business profit in FY2025, restructured.": "Premier sidérurgiste intégré du Japon : 528 Md¥ de profit sous-jacent sur l'ex. 2025, restructuré.",
 "U.S. Steel": "U.S. Steel", "100% owned since June 2025 (~$14.9bn), under a National Security Agreement with a US golden share.": "Détenue à 100 % depuis juin 2025 (~14,9 Md$), sous un accord de sécurité nationale avec une golden share américaine.",
 "India and other overseas": "Inde et autres pays", "AM/NS India JV with ArcelorMittal (capacity 9 to 15 Mt/yr), Thai and ASEAN operations, Ovako, Nippon Steel Slovakia.": "Coentreprise AM/NS India avec ArcelorMittal (capacité de 9 à 15 Mt/an), activités en Thaïlande et en ASEAN, Ovako, Nippon Steel Slovakia.",
 "Raw materials": "Matières premières", "Coking coal interests: a partial hedge on input costs.": "Participations dans le charbon à coke : une couverture partielle du coût des intrants.",
 "Source: company filings; Underlying business profit (¥bn): FY2025 actual vs FY2026 forecast (FY2026 domestic derived as total guide minus overseas guide)":
     "Source : publications de la société ; profit sous-jacent (Md¥) : ex. 2025 réel vs ex. 2026 prévu (Japon 2026 calculé comme guidance totale moins guidance étranger)",
 "Chinese steel exports": "Exportations chinoises d'acier", "Record in 2025 per the company: the main pressure on Asian spreads.": "Record en 2025 selon la société : la principale pression sur les marges asiatiques.",
 "Section 232": "Section 232", "US steel tariffs": "Droits de douane US sur l'acier", "Protect U.S. Steel's pricing; the investment case leans on them.": "Ils protègent les prix d'U.S. Steel ; la thèse s'appuie dessus.",
 "FY2026 assumption: a weak yen lifts overseas profits in yen and inventory valuation gains (¥80bn).": "Hypothèse ex. 2026 : un yen faible gonfle les profits étrangers en yens et les gains de valorisation des stocks (80 Md¥).",
 "Middle East costs": "Coûts liés au Moyen-Orient", "FY2026 impact from raw materials, fuel, logistics and lost exports, absorbed in the guide.": "Impact ex. 2026 des matières premières, du carburant, de la logistique et des exportations perdues, intégré à la guidance.",
 "*After ¥271bn of impairments and transfer losses (AM/NS Calvert, Usiminas). Fiscal year ends 31 March (FY2025 = Apr 2025-Mar 2026). Per-share data after the five-for-one split. Sources: Nippon Steel FY2025 and Q1 FY2026 materials.":
     "*Après 271 Md¥ de dépréciations et de pertes de cession (AM/NS Calvert, Usiminas). Exercice clos le 31 mars (ex. 2025 = avr. 2025-mars 2026). Données par action après la division par cinq. Sources : documents Nippon Steel ex. 2025 et T1 ex. 2026.",
 "“Chinese steel exports will keep crushing spreads”": "« Les exportations chinoises vont continuer d'écraser les marges »",
 "They hit the domestic business, which is why we focus on overseas: U.S. Steel sells behind Section 232 tariffs and India grows with local demand.": "Elles frappent l'activité au Japon, d'où notre focus sur l'étranger : U.S. Steel vend derrière les droits Section 232 et l'Inde croît avec la demande locale.",
 "“U.S. Steel was overpriced and is politically constrained”": "« U.S. Steel a été payée trop cher et reste sous contrainte politique »",
 "The golden share limits closures, but FY2026 guidance already assumes U.S. Steel at ≥ ¥180bn after the Gary relining.": "La golden share limite les fermetures, mais la guidance ex. 2026 suppose déjà U.S. Steel à ≥ 180 Md¥ après la réfection de Gary.",
 "“The balance sheet is stretched”": "« Le bilan est tendu »",
 "Adjusted D/E is 0.71 and the debt is now long-dated; the CEO calls ~1.0 acceptable during heavy investment.": "Le D/E ajusté est de 0,71 et la dette est désormais longue ; le PDG juge ~1,0 acceptable en période d'investissement lourd.",
 "U.S. Steel execution and capex overrun": "Exécution chez U.S. Steel et dépassement des investissements", "Tariff protection; $0.3bn synergies in FY2026": "Protection douanière ; 0,3 Md$ de synergies sur l'ex. 2026",
 "Leverage and convertible dilution": "Levier et dilution des convertibles", "Long-dated financing; ¥730+ conversion prices": "Financement long ; prix de conversion de 730 ¥ et plus",
 "Chinese oversupply": "Surcapacités chinoises", "Domestic cost base reset": "Base de coûts au Japon remise à plat",
 "Profit flattered by yen and inventory gains": "Profit flatté par le yen et les gains sur stocks", "Base case on operating run-rate": "Scénario central sur le rythme opérationnel",
 # ---------------------------------------------------------------- Kansai
 "Generation, retail and gas: ¥377bn of the ¥519bn FY2025 ordinary profit. Generation mix 49% nuclear, 37% thermal, 14% hydro.": "Production, vente et gaz : 377 Md¥ sur les 519 Md¥ de résultat ordinaire 2025. Mix : 49 % nucléaire, 37 % thermique, 14 % hydraulique.",
 "Transmission & distribution": "Transport et distribution", "Regulated network (Kansai T&D): ¥63bn. Revenue cap raised by ¥149.6bn from November 2026.": "Réseau régulé (Kansai T&D) : 63 Md¥. Plafond de revenus relevé de 149,6 Md¥ à partir de novembre 2026.",
 "ICT": "Télécoms et numérique", "Optage fibre and data centres: ¥47bn.": "Fibre Optage et data centers : 47 Md¥.",
 "Kanden Realty: ¥36bn; more than ¥550bn of property to be recycled under the 2026 plan.": "Kanden Realty : 36 Md¥ ; plus de 550 Md¥ d'immobilier à céder dans le cadre du plan 2026.",
 "Nuclear availability": "Disponibilité nucléaire", "H1 FY2026 capacity factor (77.2% a year earlier): outages are the main swing factor.": "Taux de disponibilité S1 ex. 2026 (77,2 % un an plus tôt) : les arrêts sont le principal facteur de variation.",
 "H1 FY2026 average versus an $80 plan assumption; fuel costs pass through with a 3-5 month lag.": "Moyenne S1 ex. 2026 contre 80 $ dans le plan ; les coûts du combustible sont répercutés avec 3 à 5 mois de décalage.",
 "Each ¥1 move against the dollar is worth about −¥1.2bn of profit.": "Chaque yen de variation contre le dollar vaut environ −1,2 Md¥ de profit.",
 "New T&D wheeling tariffs apply after the revenue-cap approval.": "Nouveaux tarifs d'acheminement après l'approbation du plafond de revenus.",
 "*Includes a ¥105bn gain on Kinden shares. Fiscal year ends 31 March (FY2025 = Apr 2025-Mar 2026). Sources: Kansai Electric FY2025 and H1 FY2026 results.":
     "*Inclut une plus-value de 105 Md¥ sur les actions Kinden. Exercice clos le 31 mars (ex. 2025 = avr. 2025-mars 2026). Sources : résultats Kansai Electric ex. 2025 et S1 ex. 2026.",
 "“Data centres will drive a demand boom”": "« Les data centers vont faire exploser la demande »",
 "Kansai-area demand is flat: 133.7 TWh in FY2025 and 133.1 TWh forecast for FY2026.": "La demande de la région du Kansai est stable : 133,7 TWh en 2025 et 133,1 TWh prévus en 2026.",
 "“The H1 collapse is temporary”": "« La chute du S1 est temporaire »",
 "Partly: the −¥87bn fuel time lag should reverse. But outages (62.7% capacity factor) and ¥2.5tn of capex are structural.": "En partie : le décalage de −87 Md¥ sur le combustible devrait s'inverser. Mais les arrêts (62,7 % de disponibilité) et 2 500 Md¥ d'investissements sont structurels.",
 "“At 0.85x book it must be cheap”": "« À 0,85x les fonds propres, c'est forcément bon marché »",
 "Only if ROE holds near 9%; the plan itself guides ROE down to about 8.7%, and normalised ROE is closer to 6-7%.": "Seulement si le ROE reste proche de 9 % ; le plan lui-même vise environ 8,7 %, et le ROE normalisé est plus proche de 6-7 %.",
 "Extended outages or court injunctions": "Arrêts prolongés ou injonctions judiciaires", "Largest fleet in Japan: diversified across 3 sites": "Plus grand parc du Japon : réparti sur 3 sites",
 "Fuel and yen": "Combustible et yen", "Pass-through with a lag": "Répercussion avec décalage",
 "¥2.5tn capex and possible equity raise": "2 500 Md¥ d'investissements et augmentation de capital possible", "Asset recycling > ¥550bn": "Cessions d'actifs > 550 Md¥",
 "Regulated tariffs": "Tarifs régulés", "T&D cap just raised": "Plafond T&D tout juste relevé",
 # ---------------------------------------------------------------- BNP
 "Retail networks in France, Belgium, Italy and Luxembourg, Europe-Mediterranean, plus Personal Finance, Arval (car leasing, Athlon acquired July 2026) and Nickel.":
     "Réseaux de détail en France, Belgique, Italie et Luxembourg, Europe-Méditerranée, plus Personal Finance, Arval (location automobile, Athlon acquis en juillet 2026) et Nickel.",
 "Global Banking, Global Markets and Securities Services; the bank describes itself as the leading EMEA investment bank.": "Global Banking, Global Markets et Securities Services ; la banque se présente comme la première banque d'investissement de la zone EMEA.",
 "Insurance, Wealth Management and Asset Management, including AXA IM, consolidated since July 2025.": "Assurance, banque privée et gestion d'actifs, dont AXA IM, consolidé depuis juillet 2025.",
 "CET1 12.9% at September 2026, against a 10.45% requirement; guided above 13% at end-2026.": "CET1 de 12,9 % à fin septembre 2026, contre une exigence de 10,45 % ; visé au-dessus de 13 % fin 2026.",
 "French 10-year yield": "Taux français à 10 ans", "Political and budget uncertainty pushed French yields up in 2026; French banks trade as a proxy for the sovereign.": "L'incertitude politique et budgétaire a fait monter les taux français en 2026 ; les banques françaises servent de proxy du souverain.",
 "OAT-Bund spread": "Écart OAT-Bund", "A wider spread raises funding costs and the discount investors apply to French financials.": "Un écart plus large renchérit le refinancement et la décote appliquée aux financières françaises.",
 "Oil and inflation": "Pétrole et inflation", "Brent around $115 a barrel with the Middle East conflict: a risk to credit quality and to rate expectations.": "Brent autour de 115 $ le baril avec le conflit au Moyen-Orient : un risque pour la qualité du crédit et les anticipations de taux.",
 "Q3 2026, at the top of the <40 bp guide. Arval used-car prices are the visible pressure point.": "T3 2026, en haut de la guidance < 40 pb. Les prix des véhicules d'occasion d'Arval sont le point de pression visible.",
 "The score averages the z-scores above (financials use book and earnings only). Accounts are used only from fiscal year end + 6 months, so in December 2025 the screen read the accounts for the fiscal year ended December 2024.":
     "Le score fait la moyenne des z-scores ci-dessus (les financières n'utilisent que fonds propres et bénéfices). Les comptes ne sont utilisés qu'à partir de la clôture + 6 mois : en décembre 2025, le screen lisait les comptes de l'exercice clos en décembre 2024.",
 "FY2024 figures derived from the 2025 growth rates reported by the bank. RoTE methodology changed in Q4 2025. Sources: BNP Paribas FY2025 and Q3 2026 releases.":
     "Chiffres 2024 déduits des taux de croissance 2025 publiés par la banque. Méthode de calcul du RoTE modifiée au T4 2025. Sources : communiqués BNP Paribas 2025 et T3 2026.",
 "“BNP is a leveraged bet on France”": "« BNP est un pari à levier sur la France »",
 "Three of its four retail home markets are outside France, CIB is the leading EMEA investment bank, and IPS adds fee income. Earnings are more diversified than the share price implies.":
     "Trois de ses quatre marchés domestiques sont hors de France, la BFI est la première de la zone EMEA, et IPS apporte des commissions. Les bénéfices sont plus diversifiés que ne le suggère le cours.",
 "“Trading revenue is at a peak”": "« Les revenus de marché sont au plus haut »",
 "Global Markets is strong (+21.9% in Q3), but the RoTE target was beaten even after €408m of restructuring costs.": "Global Markets est solide (+21,9 % au T3), mais l'objectif de RoTE a été battu même après 408 M€ de coûts de restructuration.",
 "“The Sudan litigation is an open-ended liability”": "« Le litige Soudan est un passif sans limite »",
 "It is real and unprovisioned; we treat it as a tail risk that the appeal (2027) will clarify, and keep the position sized accordingly.": "Il est réel et non provisionné ; nous le traitons comme un risque extrême que l'appel (2027) clarifiera, et dimensionnons la position en conséquence.",
 "French sovereign and political stress": "Tensions souveraines et politiques en France", "Diversified earnings; French bonds held mostly at amortised cost (€16bn of €19bn)": "Bénéfices diversifiés ; obligations françaises surtout au coût amorti (16 Md€ sur 19 Md€)",
 "Sudan litigation, no provision booked": "Litige Soudan, sans provision", "Appeal pending; position sized below the 4% cap": "Appel en cours ; position sous le plafond de 4 %",
 "Normalisation of trading revenue": "Normalisation des revenus de marché", "Targets beaten even after restructuring costs": "Objectifs battus même après les coûts de restructuration",
 "Cost of risk above 40 bp": "Coût du risque au-dessus de 40 pb", "Stage 3 ratio 1.6% with 67% coverage": "Ratio stage 3 de 1,6 % avec 67 % de couverture",
 # ---------------------------------------------------------------- Carrefour
 "France (No. 2)": "France (n° 2)", "About half of sales: hypermarkets, supermarkets, convenience and e-commerce, moving toward franchise and location-gérance. ROI margin 1.5% in H1 2026.":
     "Environ la moitié des ventes : hypermarchés, supermarchés, proximité et e-commerce, en transition vers la franchise et la location-gérance. Marge opérationnelle courante de 1,5 % au S1 2026.",
 "Brazil (No. 1)": "Brésil (n° 1)", "Atacadão cash & carry and retail; highest margin (4.0% in H1 2026) but exposed to rates near 15% and the real.": "Cash & carry Atacadão et distribution ; la meilleure marge (4,0 % au S1 2026) mais exposée à des taux proches de 15 % et au réal.",
 "Spain (No. 2)": "Espagne (n° 2)", "Steady growth and a 3.3% margin in H1 2026.": "Croissance régulière et marge de 3,3 % au S1 2026.",
 "Belgium, Poland and Argentina: loss-making in H1 2026 (−€34m) and under strategic review.": "Belgique, Pologne et Argentine : en perte au S1 2026 (−34 M€) et en revue stratégique.",
 "French unrest": "Troubles en France", "Estimated hit to 2026 recurring operating income from the October riots, looting and curfews.": "Impact estimé sur le résultat opérationnel courant 2026 des émeutes, pillages et couvre-feux d'octobre.",
 "Food price war": "Guerre des prix alimentaire", "Private-label products sold at cost to loyalty members under the 2030 plan: price investment caps margins.": "Produits à marque propre vendus à prix coûtant aux clients fidèles dans le plan 2030 : l'investissement prix plafonne les marges.",
 "Brazil policy rate": "Taux directeur brésilien", "High rates hit cash & carry volumes in 2025; rate cuts would help Atacadão.": "Les taux élevés ont pesé sur les volumes du cash & carry en 2025 ; des baisses aideraient Atacadão.",
 "FX drag on 2025 operating income from the Brazilian real and the Argentine peso.": "Effet de change négatif sur le résultat 2025 lié au réal brésilien et au peso argentin.",
 "*Seasonal: working capital reverses in H2. FY2024 ROI derived from the −5.4% reported for 2025. Sources: Carrefour FY2025, H1 2026 and Q3 2026 releases.":
     "*Saisonnier : le BFR s'inverse au S2. ROC 2024 déduit du −5,4 % publié pour 2025. Sources : communiqués Carrefour 2025, S1 2026 et T3 2026.",
 "“The French market is structurally broken”": "« Le marché français est structurellement cassé »",
 "France is a low-margin, price-war market, but Carrefour is No. 2 and the plan already prices €1bn a year of savings, half of them delivered by mid-2026.": "La France est un marché à faibles marges et en guerre des prix, mais Carrefour est n° 2 et le plan intègre déjà 1 Md€ d'économies par an, dont la moitié réalisée mi-2026.",
 "“The riots are a lasting hit”": "« Les émeutes sont un choc durable »",
 "Management estimates €80-200m of recurring operating income at risk in 2026. That is a one-year shock on a €2.2bn profit base, not a change in earning power.": "La direction estime 80 à 200 M€ de résultat opérationnel courant à risque en 2026. C'est un choc d'un an sur 2,2 Md€ de profit, pas un changement de capacité bénéficiaire.",
 "“The dividend will be cut”": "« Le dividende va baisser »",
 "This is the real risk: a 50-60% payout on flat EPS implies €0.80-0.96 against €0.97 paid. We assume a cut in the base case.": "C'est le vrai risque : 50-60 % de distribution sur un BPA stable implique 0,80-0,96 € contre 0,97 € versé. Nous supposons une baisse dans le scénario central.",
 "French unrest persisting into 2027": "Troubles en France jusqu'en 2027", "Store base diversified; security costs one-off": "Parc de magasins diversifié ; coûts de sécurité ponctuels",
 "Price investment erodes margins": "L'investissement prix érode les marges", "€1bn a year of savings; franchise model lowers costs": "1 Md€ d'économies par an ; la franchise réduit les coûts",
 "Dividend reset": "Baisse du dividende", "Already assumed in our base case": "Déjà intégrée dans notre scénario central",
 "Brazil macro and currency translation": "Macro et change brésiliens", "Fully owned Brazil, No. 1 position": "Brésil détenu à 100 %, position de n° 1",
 # ---------------------------------------------------------------- Centene
 "Case study: Cheap for the wrong reason": "Cas d'école : bon marché pour la mauvaise raison",
 "Largest US Medicaid managed-care organisation: 11.9m members at September 2026, down from 12.7m.": "Premier gestionnaire de Medicaid aux États-Unis : 11,9 M d'adhérents à fin septembre 2026, contre 12,7 M.",
 "Marketplace (ACA)": "Marketplace (ACA)", "Ambetter plans: 3.4m members versus 5.8m a year earlier after enhanced premium tax credits expired.": "Contrats Ambetter : 3,4 M d'adhérents contre 5,8 M un an plus tôt, après la fin des crédits d'impôt renforcés.",
 "Medicare": "Medicare", "Wellcare: 0.95m Medicare Advantage and supplement members plus 8.9m stand-alone Part D members.": "Wellcare : 0,95 M d'adhérents Medicare Advantage et complémentaire, plus 8,9 M en partie D seule.",
 "Remaining Magellan Health businesses held for sale ($513m impairment, December 2025).": "Activités restantes de Magellan Health en cours de cession (dépréciation de 513 M$, décembre 2025).",
 "ACA subsidies": "Subventions ACA", "Marketplace membership y/y after enhanced premium tax credits expired on 31 Dec 2025.": "Adhérents Marketplace sur un an après la fin des crédits d'impôt renforcés le 31 déc. 2025.",
 "Medicaid reform": "Réforme de Medicaid", "OBBBA work requirements and more frequent eligibility checks phase in from end-2026.": "Obligations de travail de l'OBBBA et contrôles d'éligibilité plus fréquents à partir de fin 2026.",
 "Medicare rates": "Tarifs Medicare", "CMS final 2027 Medicare Advantage rate notice (April 2026), versus +0.09% proposed.": "Avis définitif CMS des tarifs Medicare Advantage 2027 (avril 2026), contre +0,09 % proposé.",
 "Medical cost trend": "Dérive des coûts médicaux", "Medicaid benefits ratio in Q3 2026: behavioural health, home health and high-cost drugs.": "Ratio de sinistralité Medicaid au T3 2026 : santé mentale, soins à domicile et médicaments coûteux.",
 "*Includes a $6.7bn non-cash goodwill impairment (Q3 2025). No dividend. Sources: Centene FY2025 and Q3 2026 releases.": "*Inclut une dépréciation de goodwill sans impact cash de 6,7 Md$ (T3 2025). Pas de dividende. Sources : communiqués Centene 2025 et T3 2026.",
 "“The stock has doubled, so the model was right”": "« Le titre a doublé, donc le modèle avait raison »",
 "The 2026 rebound came from repricing and policy, not from the cheapness the model measured. The signal had no defence against a fast fundamental break.": "Le rebond de 2026 vient des hausses de tarifs et de la politique, pas de la décote mesurée par le modèle. Le signal n'avait aucune défense contre une rupture rapide des fondamentaux.",
 "“Managed care is a stable compounder”": "« L'assurance santé est une valeur de croissance régulière »",
 "Margins are thin: each 10 bp of benefits ratio on ~$175bn of premiums is about $175m of pre-tax profit.": "Les marges sont minces : chaque 10 pb de ratio de sinistralité sur ~175 Md$ de primes vaut environ 175 M$ de résultat avant impôt.",
 "“Guidance raises mean upside”": "« Les relèvements de guidance signifient du potentiel »",
 "The floor format ('greater than $5.20') and ~$0.50 of non-recurring items flatter 2026; FY2027 guidance in February is the real test.": "Le format plancher (« plus de 5,20 $ ») et ~0,50 $ d'éléments non récurrents flattent 2026 ; la guidance 2027 de février sera le vrai test.",
 "Marketplace risk pool worsens as healthier members lapse": "Le risque Marketplace se dégrade à mesure que les adhérents en bonne santé partent", "Repricing already filed; membership smaller": "Hausses de tarifs déjà déposées ; portefeuille plus petit",
 "Medicaid rate adequacy versus acuity": "Adéquation des tarifs Medicaid à la gravité des cas", "State rate increases in 2026": "Hausses de tarifs des États en 2026",
 "Low Medicare Star ratings limit bonuses": "Des notes Medicare Star faibles limitent les bonus", "Small MA book (0.95m members)": "Petit portefeuille MA (0,95 M d'adhérents)",
 "Little unregulated cash ($175m)": "Peu de trésorerie non régulée (175 M$)", "Debt reduced from $17.4bn to $15.5bn": "Dette réduite de 17,4 à 15,5 Md$",
 # ---------------------------------------------------------------- HP
 "PCs, workstations and peripherals: $38.5bn of FY2025 revenue at a 5.3% operating margin.": "PC, stations de travail et périphériques : 38,5 Md$ de CA sur l'ex. 2025 à 5,3 % de marge opérationnelle.",
 "Supplies (ink and toner), hardware and industrial graphics: $16.7bn at an 18.7% margin.": "Consommables (encre et toner), matériel et impression industrielle : 16,7 Md$ à 18,7 % de marge.",
 "AI PCs with dedicated neural processors, workstations and services.": "PC IA avec processeurs neuronaux dédiés, stations de travail et services.",
 "Negative book equity after years of buybacks; net debt about $5bn (own calculation).": "Fonds propres comptables négatifs après des années de rachats ; dette nette d'environ 5 Md$ (calcul propre).",
 "DRAM and NAND inflation squeezes PC margins; management expects the peak in Aug-Oct 2026.": "L'inflation des DRAM et NAND comprime les marges PC ; la direction attend le pic en août-octobre 2026.",
 "Drove a commercial refresh: Personal Systems revenue +18% in Q3 FY2026.": "A déclenché un renouvellement du parc professionnel : CA Personal Systems +18 % au T3 ex. 2026.",
 "IEEPA tariffs struck down in February 2026; FY26 EPS includes $0.19 of one-off refunds.": "Droits IEEPA annulés en février 2026 ; le BPA 2026 inclut 0,19 $ de remboursements ponctuels.",
 "Higher-spec machines lift average selling prices as the installed base renews.": "Des machines mieux équipées relèvent les prix moyens à mesure que le parc se renouvelle.",
 "*Includes $0.19 of one-off tariff refunds. Fiscal year ends 31 October. FY2024 revenue derived from the +3.2% reported for FY2025. Sources: HP Q4 FY2025 and Q3 FY2026 releases.":
     "*Inclut 0,19 $ de remboursements douaniers ponctuels. Exercice clos le 31 octobre. CA 2024 déduit du +3,2 % publié pour 2025. Sources : communiqués HP T4 ex. 2025 et T3 ex. 2026.",
 "“Printing is in terminal decline”": "« L'impression est en déclin terminal »",
 "Revenue falls about 2% a year and the margin holds above 18%. A slow decline is priced as a fast one.": "Le CA baisse d'environ 2 % par an et la marge tient au-dessus de 18 %. Un déclin lent est valorisé comme un déclin rapide.",
 "“FY2026 PC demand was pulled forward by Windows 10”": "« La demande de PC 2026 a été avancée par Windows 10 »",
 "Partly true. We use a base FCF of $3.0bn, below the guided midpoint, and exclude tariff refunds.": "En partie vrai. Nous retenons un FCF de 3,0 Md$, sous le milieu de la guidance, hors remboursements douaniers.",
 "“An interim CEO means strategic risk”": "« Un PDG intérimaire, c'est un risque stratégique »",
 "A permanent appointment, expected in the coming months, is more likely a catalyst than a threat.": "Une nomination définitive, attendue dans les prochains mois, est plus probablement un catalyseur qu'une menace.",
 "Printing decline speeds up": "Le déclin de l'impression s'accélère", "Supplies are recurring; margin held above 18%": "Consommables récurrents ; marge tenue au-dessus de 18 %",
 "PC demand pulled forward into FY2026": "Demande PC avancée sur l'ex. 2026", "Base case below the guide": "Scénario central sous la guidance",
 "Memory costs do not peak as guided": "Le coût des mémoires ne culmine pas comme prévu", "Pricing passed through in Q3": "Hausses de prix répercutées au T3",
 "Negative equity and ~$5bn net debt": "Fonds propres négatifs et ~5 Md$ de dette nette", "Payout flexible; buybacks can be cut first": "Distribution flexible ; les rachats peuvent être réduits en premier",
 # ---------------------------------------------------------------- Renault
 "Automotive (~88% of revenue)": "Automobile (~88 % du CA)",
 "Renault, Dacia and Alpine brands; a volume player in European B and C segments, with Dacia as the low-cost brand. 52% of European sales were electrified in H1 2026.":
     "Marques Renault, Dacia et Alpine ; un généraliste des segments B et C en Europe, avec Dacia comme marque low-cost. 52 % des ventes européennes étaient électrifiées au S1 2026.",
 "Mobilize Financial Services (~12%)": "Mobilize Financial Services (~12 %)",
 "Captive car finance and leasing. Contributed €753m of operating margin in H1 2026 and pays dividends up to the car business (€250m in H1 2026, about €500m a year targeted).":
     "Financement et location automobile captifs. 753 M€ de marge opérationnelle au S1 2026 et dividendes versés à la branche auto (250 M€ au S1 2026, environ 500 M€ par an visés).",
 "Nissan stake": "Participation Nissan",
 "About 35% after the 2023-2025 Alliance restructuring, according to press reports. Carried at fair value through equity since June 2025.": "Environ 35 % après la refonte de l'Alliance 2023-2025, selon la presse. Comptabilisée à la juste valeur par capitaux propres depuis juin 2025.",
 "No US sales, so US tariffs are a second-order risk. Growth markets are India, Turkey, Morocco and Brazil (Geely partnership in Brazil since September 2026).": "Aucune vente aux États-Unis : les droits de douane américains sont un risque de second ordre. Marchés de croissance : Inde, Turquie, Maroc et Brésil (partenariat Geely au Brésil depuis septembre 2026).",
 "Group volumes in Q3 2026. European demand is flat and Chinese brands are gaining share in the low-cost segment where Dacia plays.": "Volumes du groupe au T3 2026. La demande européenne est stable et les marques chinoises gagnent des parts sur le low-cost, le terrain de Dacia.",
 "The 2026 Middle East conflict lifted raw-material, energy and logistics costs; management expects H2 margin only slightly above H1.": "Le conflit au Moyen-Orient de 2026 a relevé les coûts des matières premières, de l'énergie et de la logistique ; la direction attend une marge S2 à peine supérieure au S1.",
 "Share of electric cars in Q3 2026 passenger-car sales. EU CO2 rules force the mix shift and compress pricing.": "Part des voitures électriques dans les ventes VP au T3 2026. Les règles CO2 de l'UE imposent le changement de mix et compriment les prix.",
 "Investment-grade rating (S&P, Dec 2025) lowers funding cost for Mobilize, whose margin depends on rates and used-car prices.": "La note investment grade (S&P, déc. 2025) réduit le coût de financement de Mobilize, dont la marge dépend des taux et des prix de l'occasion.",
 "*Includes a €9.3bn non-cash loss on the Nissan stake. FY2024 revenue derived from the +3.0% growth reported for 2025. Sources: Renault FY2025 and H1 2026 releases.":
     "*Inclut une perte sans impact cash de 9,3 Md€ sur la participation Nissan. CA 2024 déduit de la croissance de +3,0 % publiée pour 2025. Sources : communiqués Renault 2025 et S1 2026.",
 "“Chinese competition will crush margins”": "« La concurrence chinoise va écraser les marges »",
 "Volumes are under pressure, but pricing and mix held. The plan cuts variable cost by about €400 per car a year and development time to two years.": "Les volumes sont sous pression, mais prix et mix ont tenu. Le plan réduit le coût variable d'environ 400 € par voiture et par an, et le temps de développement à deux ans.",
 "“The cash is trapped and will be burnt”": "« La trésorerie est bloquée et sera brûlée »",
 "The car business generated €1.5bn of free cash flow in 2025, S&P upgraded Renault to investment grade (BBB−) in December 2025, and the €2.20 dividend was paid from that cash.":
     "La branche auto a généré 1,5 Md€ de free cash flow en 2025, S&P a relevé Renault en investment grade (BBB−) en décembre 2025, et le dividende de 2,20 € a été payé avec ce cash.",
 "“Management keeps cutting guidance”": "« La direction ne cesse d'abaisser la guidance »",
 "The new CEO reset targets once, in July 2025. The 2026 guide has since been confirmed three times.": "Le nouveau PDG a remis les objectifs à zéro une fois, en juillet 2025. La guidance 2026 a depuis été confirmée trois fois.",
 "“Nissan is a black hole”": "« Nissan est un trou noir »",
 "The stake was written down by €9.3bn in 2025. Our valuation gives it no value, so any monetisation is upside.": "La participation a été dépréciée de 9,3 Md€ en 2025. Notre valorisation ne lui donne aucune valeur : toute monétisation est un bonus.",
 "European price war with Chinese brands": "Guerre des prix en Europe avec les marques chinoises", "Dacia's cost position; plan cuts €400 of variable cost per car a year": "Position de coûts de Dacia ; le plan réduit le coût variable de 400 € par voiture et par an",
 "Raw-material and energy inflation": "Inflation des matières premières et de l'énergie", "Pricing power held in 2026; costs partly passed through": "Pouvoir de prix maintenu en 2026 ; coûts partiellement répercutés",
 "Execution of futuREady": "Exécution de futuREady", "Two-year development cycle already used on 2026 launches": "Cycle de développement de deux ans déjà appliqué aux lancements 2026",
 "Mobilize credit risk if used-car prices fall": "Risque de crédit de Mobilize si les prix de l'occasion baissent", "Investment-grade funding; diversified retail book": "Financement investment grade ; portefeuille de détail diversifié",
}

SECT = {"Industrials": "Industrie", "Materials": "Matériaux", "Utilities": "Services aux collectivités", "Financials": "Finance",
        "Consumer Staples": "Consommation de base", "Health Care": "Santé", "Information Technology": "Technologies de l'information",
        "Consumer Discretionary": "Consommation discrétionnaire"}
IND = {"Container shipping": "Transport de conteneurs", "Steel": "Sidérurgie", "Electric utilities": "Électricité", "Banks": "Banques",
       "Food retail": "Distribution alimentaire", "Managed care": "Assurance santé", "Technology hardware": "Matériel informatique", "Automobiles": "Automobile"}
CTRY = {"Hong Kong": "Hong Kong", "Japan": "Japon", "France": "France", "United States": "États-Unis"}
MONTH = {"January": "janvier", "February": "février", "March": "mars", "April": "avril", "May": "mai", "June": "juin", "July": "juillet",
         "August": "août", "September": "septembre", "October": "octobre", "November": "novembre", "December": "décembre"}
FIRSTS = {"first": "1er"}


def patterns(s):
    m = re.match(r"^Ranked (\d+) of (\d+) in (.+) on our value score$", s)
    if m:
        return f"Classé {m.group(1)} sur {m.group(2)} en {SECT.get(m.group(3), m.group(3))} sur notre score value"
    m = re.match(r"^Composite score ([\d.]+), (first|rank \d+) of (\d+) in its sector\. $", s)
    if m:
        rk = "1er" if m.group(2) == "first" else m.group(2).replace("rank ", "") + "e"
        return f"Score composite {m.group(1)}, {rk} sur {m.group(3)} dans son secteur. "
    m = re.match(r"^The score averages the z-scores above \(four ratios as yields\)\. Accounts are used only from fiscal year end \+ 6 months, so in December 2025 the screen read the accounts for the fiscal year ended (\w+) (\d{4})\.$", s)
    if m:
        return (f"Le score fait la moyenne des z-scores ci-dessus (quatre ratios exprimés en rendements). Les comptes ne sont utilisés qu'à partir de la clôture + 6 mois : "
                f"en décembre 2025, le screen lisait les comptes de l'exercice clos en {MONTH[m.group(1)]} {m.group(2)}.")
    m = re.match(r"^Held at (\d+) of 10 rebalances since (\w+) (\d{4})$", s)
    if m:
        return f"Détenu à {m.group(1)} rebalancement{'s' if m.group(1) != '1' else ''} sur 10 depuis {MONTH[m.group(2)]} {m.group(3)}"
    m = re.match(r"^base-case value, (.+) vs (.+)$", s)
    if m:
        return f"valeur centrale, {m.group(1)} vs {m.group(2)}"
    m = re.match(r"^Base-case value (.+) per share, (.+) vs today$", s)
    if m:
        return f"Valeur centrale {m.group(1)} par action, {m.group(2)} vs aujourd'hui"
    m = re.match(r"^Method: (.+)$", s)
    if m:
        return "Méthode : " + METHODS.get(m.group(1), m.group(1))
    m = re.match(r"^│ Price (.+)$", s)
    if m:
        return f"│ Cours {m.group(1)}"
    m = re.match(r"^┆ Base case (.+)$", s)
    if m:
        return f"┆ Scénario central {m.group(1)}"
    m = re.match(r"^(.+) at a glance$", s)
    if m:
        return f"{m.group(1)} en bref"
    m = re.match(r"^Source: company filings; (.+)$", s)
    if m:
        return "Source : publications de la société ; " + T.get(m.group(1), m.group(1))
    m = re.match(r"^Source: Portfolio Project pipeline \(Bloomberg data\); peers: (.+)$", s)
    if m:
        p = m.group(1).replace("(pipeline peer set, December 2025)", "(pairs du pipeline, décembre 2025)").replace("(pipeline peer set)", "(pairs du pipeline)")
        p = p.replace(" for regional context", " pour le contexte régional").replace(" for context", " pour le contexte").replace(" for Japan", " pour le Japon")
        return "Source : pipeline du Portfolio Project (données Bloomberg) ; pairs : " + p
    m = re.match(r"^(.+): (\S+)  ·  (.+) / (.+)  ·  (.+)$", s)
    if m and m.group(4) in IND:
        ex = {"Tokyo Stock Exchange": "Bourse de Tokyo"}.get(m.group(1), m.group(1))
        return f"{ex} : {m.group(2)}  ·  {SECT.get(m.group(3), m.group(3))} / {IND[m.group(4)]}  ·  {CTRY.get(m.group(5), m.group(5))}"
    m = re.match(r"^(EPS|FCF|RoTE|ROE|US\$[\d.]+ EPS)(.*)$", s)
    if m:
        x = s.replace("EPS", "BPA").replace(" at ", " à ").replace(" yield", " de rendement").replace("x TBV", "x l'ANCT").replace("x book", "x les fonds propres")
        x = re.sub(r"^US\$([\d.]+) BPA", r"BPA US$\1", x)
        return x
    m = re.match(r"^([\d.]+)x book \((.+) BVPS\)$", s)
    if m:
        return f"{m.group(1)}x les fonds propres ({m.group(2)} par action)"
    return None


METHODS = {
    "P/E on normalised earnings": "PER sur bénéfices normalisés", "Price to book against the return path": "Multiple des fonds propres selon la trajectoire de rentabilité",
    "Justified price to book (Gordon growth)": "Multiple justifié des fonds propres (Gordon)", "Justified price to tangible book (Gordon growth)": "Multiple justifié de l'actif net tangible (Gordon)",
    "Free-cash-flow yield on normalised net free cash flow": "Rendement de free cash flow sur un FCF net normalisé", "P/E on 2027 adjusted EPS": "PER sur le BPA ajusté 2027",
    "Free-cash-flow yield": "Rendement de free cash flow", "P/E on 2027 earnings, cross-checked with a sum of the parts": "PER sur les bénéfices 2027, recoupé par une somme des parties",
}


def fr_numbers(s):
    """French number formatting: decimal comma, thin-space thousands, currency after the amount, bn/tn/m to Md/M."""
    nb = "\u00a0"

    def amount(cur, val, unit):
        v = val.replace(",", "")
        if unit == "tn":
            v = f"{float(v) * 1000:,.0f}"
            unit = "bn"
        v = v.replace(",", "\u202f").replace(".", ",")
        u = {"bn": "Md", "m": "M", "": ""}[unit]
        cur = {"€": "€", "$": "$", "¥": "¥", "US$": "US$", "HK$": "HK$"}[cur]
        if u:
            return f"{v}{nb}{u}{cur}" if cur in ("€", "$", "¥") else f"{v}{nb}{u} {cur}"
        return f"{v}{nb}{cur}"

    s = re.sub(r"(US\$|HK\$|€|\$|¥)(\d[\d,]*(?:\.\d+)?)-(\d[\d,]*(?:\.\d+)?)(bn|m)\b",
               lambda m: f"{m.group(2).replace('.', ',')}-{m.group(3).replace('.', ',')}{nb}{ {'bn': 'Md', 'm': 'M'}[m.group(4)] }{m.group(1)}", s)
    s = re.sub(r"(US\$|HK\$|€|\$|¥)(\d[\d,]*(?:\.\d+)?)(bn|tn|m)?(?![\w])", lambda m: amount(m.group(1), m.group(2), m.group(3) or ""), s)
    s = re.sub(r"(?<![\d\w])(\d{1,3}(?:,\d{3})+)(?![\d])", lambda m: m.group(1).replace(",", "\u202f"), s)
    s = re.sub(r"(\d)\.(\d)", r"\1,\2", s)
    s = re.sub(r"(\d)%", "\\1\u00a0%", s)
    s = re.sub(r"(\d) bp\b", "\\1 pb", s)
    s = s.replace("H1 ", "S1 ").replace("H2 ", "S2 ").replace("Q1 ", "T1 ").replace("Q2 ", "T2 ").replace("Q3 ", "T3 ").replace("Q4 ", "T4 ")
    return s


def translate(s):
    if s in T:
        out = T[s]
    else:
        out = patterns(s)
        if out is None:
            return fr_numbers(s) if re.search(r"\d", s) else s
    return fr_numbers(out) if re.search(r"[$€¥]|\d\.\d|\d%| bp\b", out) else out

T.update({
 "Disclosure: student research prepared for educational purposes and job interviews. It is not investment advice or a solicitation. Third-party market data (prices, consensus, forward multiples) is labelled and was accessed on 29 October 2026; third-party figures should be checked against company filings or a Bloomberg terminal before use. Backtest results are hypothetical.":
   "Avertissement : travail étudiant préparé à des fins pédagogiques et pour des entretiens. Ce n'est ni un conseil en investissement ni une sollicitation. Les données de marché tierces (cours, consensus, multiples prospectifs) sont signalées et ont été consultées le 29 octobre 2026 ; elles doivent être vérifiées dans les publications des sociétés ou sur un terminal Bloomberg avant usage. Les résultats de backtest sont hypothétiques.",
 "Health benefits ratio": "Ratio de sinistralité", "US tariffs": "Droits de douane US", "trough": "creux", "Shareholder returns": "Retour aux actionnaires",
 "Free cash flow": "Free cash flow",
})

_old_patterns = patterns


def patterns(s):  # noqa: F811  (extends the first definition)
    m = re.match(r"^(.+) \((.+): (\S+)\)  ·  Noah Doose  ·  Student research, not investment advice  ·  Data as of 29 Oct 2026$", s)
    if m:
        ex = {"Tokyo Stock Exchange": "Bourse de Tokyo"}.get(m.group(2), m.group(2))
        return f"{m.group(1)} ({ex} : {m.group(3)})  ·  Noah Doose  ·  Travail étudiant, pas un conseil en investissement  ·  Données au 29 oct. 2026"
    m = re.match(r"^(.+) \(share of total\)$", s)
    if m:
        return T.get(m.group(1), m.group(1)) + " (part du total)"
    m = re.match(r"^(.+) \(share of total, %\)$", s)
    if m:
        return T.get(m.group(1), m.group(1)) + " (part du total, %)"
    return _old_patterns(s)
T["Underlying business profit (¥bn): FY2025 actual vs FY2026 forecast"] = "Profit sous-jacent (Md¥) : ex. 2025 réel vs ex. 2026 prévu"
