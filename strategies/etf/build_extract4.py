"""Bloomberg workbook #4 (5 Nov 2026), satellite history step 2: for the union of the top-350 developed-market names
(2005-2020, from workbook #3) and the top-300 of 2021-2025: static data, monthly total return and market cap in EUR
(Dec 2005 -> Jun 2026), annual fundamentals 2004-2025 with the locked settings (original figures, EUR)."""
import openpyxl, pandas as pd, sys
from openpyxl.styles import Font, PatternFill, Alignment
from openpyxl.workbook.defined_name import DefinedName
from openpyxl.utils import get_column_letter as L
from openpyxl.formatting.rule import CellIsRule

UNION = pd.read_csv("strategies/etf/satellite_lists/union_tickers.csv", header=None)[0].tolist()
FUND = pd.read_csv("strategies/etf/satellite_lists/fund_tickers.csv", header=None)[0].tolist()     # 2021-25-only names reuse the 29/10 fundamentals
NAVY, GOLD, GREY, OKF, KOF, AMB = "0B1F3A", "B08D57", "F1EFEA", "DDEBDD", "F6E3E0", "F6EDD9"
H = Font(bold=True, color="FFFFFF"); B = Font(bold=True); FH = PatternFill("solid", fgColor=NAVY); FG = PatternFill("solid", fgColor=GREY)
FIELDS = [("SALES_REV_TURN", "Chiffre d'affaires"), ("EBIT", "EBIT"), ("NET_INCOME", "Résultat net"), ("CF_FREE_CASH_FLOW", "Free cash flow"),
          ("TOT_COMMON_EQY", "Fonds propres"), ("NET_DEBT", "Dette nette"), ("MINORITY_NONCONTROLLING_INTEREST", "Minoritaires"),
          ("BS_SH_OUT", "Actions en circulation"), ("ANNOUNCEMENT_DT", "Date de publication")]
wb = openpyxl.Workbook(); wb.calculation.fullCalcOnLoad = True
def name(n, ref): wb.defined_names[n] = DefinedName(n, attr_text=ref)
def head(ws, r, vals):
    for i, v in enumerate(vals, 1):
        c = ws.cell(r, i, v); c.fill = FH; c.font = H; c.alignment = Alignment(wrap_text=True, vertical="center")

def fund_formula(t, f, start="F_START", end="F_END"):
    a = f'BDH("{t}","{f}",{start},{end},"Per","Y","FILING_STATUS","OR","EQY_FUND_CRNCY","EUR")'
    b = f'BDH("{t}","{f}",{start},{end},"Per","Y","Days","A","FILING_STATUS","OR","Currency","EUR")'
    return a, b

# ---------------- Mode d'emploi
ws = wb.active; ws.title = "Mode d'emploi"
lines = [("Extraction n°4 — historique du satellite, étape 2 : prix mensuels et fondamentaux de " + str(len(UNION)) + " titres", "t"), ("", None),
 ("Ce que c'est : les 350 plus grosses capitalisations des pays développés à chaque date 2005-2020 (tirées de ton extraction n°3) + les 300 plus grosses de 2021-2025. Pour chacune : pays, secteur, rendement total mensuel et capitalisation mensuelle en EUR (déc. 2005 → juin 2026), et fondamentaux annuels 2004-2025 (mêmes réglages que le 29/10 : chiffres d'origine, EUR).", None), ("", None),
 ("Prévu sur 3 sessions pour ménager la limite du poste (une par jour). Chaque étape : passer l'interrupteur à OUI dans Config, attendre la fin du chargement (plus de « #N/A Requesting »), Ctrl+A, Ctrl+C, Ctrl+Alt+V, V, Entrée dans chaque onglet concerné, puis enregistrer.", "b"),
 ("JOUR 1", "b"),
 ("1. Ouvre, ENREGISTRE SOUS dans ton dossier. Onglet Tests : attends 1 minute.", None),
 ("2. Tests F1 à F3 (fondamentaux) : deux formules candidates, A et B. Regarde laquelle donne OK sur les trois tests et écris A ou B dans Config!C2 (FUND_MODE). Si aucune n'est OK partout : ARRÊTE-TOI et envoie-moi le fichier.", None),
 ("3. Test C1 (capitalisation) : note s'il est OK. Ne change rien.", None),
 ("4. RUN_Tickers = OUI → onglet Tickers rempli → colle en valeurs.", None),
 ("5. RUN_TR_A = OUI (onglets TR_01 à TR_05) → colle en valeurs chaque onglet. Si pas de message de limite, enchaîne RUN_TR_B (TR_06 à TR_09). Enregistre.", None),
 ("JOUR 2", "b"),
 ("6. RUN_CAP_A puis RUN_CAP_B (onglets CAP_01 à CAP_09), même méthode.", None),
 ("JOUR 3", "b"),
 ("7. RUN_FUND (onglets FUND_01 à FUND_04), même méthode. Colle aussi l'onglet Tests en valeurs. Enregistre sous SAT_DATA_AAAAMMJJ.xlsx et envoie-le à Claude.", None), ("", None),
 ("Si une cellule affiche #N/A Review ou un message de limite : arrête-toi, colle en valeurs ce qui est rempli, enregistre, et reprends le lendemain à l'interrupteur suivant.", None),
 ("Leçon Bloomberg : FILING_STATUS = OR demande les chiffres tels que publiés à l'époque (pas les chiffres retraités ensuite). Sans ce réglage, le backtest utiliserait des données corrigées après coup : c'est un biais d'anticipation (look-ahead).", None),
 ("Rappel : données Bloomberg brutes — ni site, ni GitHub.", None)]
for i, (t, f) in enumerate(lines, 1):
    c = ws.cell(i, 1, t); c.alignment = Alignment(wrap_text=True, vertical="top")
    if f == "t": c.font = Font(bold=True, size=14, color=NAVY)
    if f == "b": c.font = Font(bold=True, color=GOLD)
ws.column_dimensions["A"].width = 130; ws.sheet_view.showGridLines = False

# ---------------- Config
ws = wb.create_sheet("Config"); head(ws, 1, ["Nom", "Rôle", "Valeur", "Note"])
cfg = [("FUND_MODE", "Formule des fondamentaux (A ou B)", "A", "À fixer d'après les tests F1-F3"),
       ("P_START", "Début prix", "20051130", "Pour avoir le rendement de décembre 2005"), ("P_END", "Fin prix", "20260630", ""),
       ("F_START", "Début fondamentaux", "20040101", "Exercice 2004 : publié en 2005, utilisable en 2006"), ("F_END", "Fin fondamentaux", "20251231", ""),
       ("RUN_Tickers", "Interrupteur Tickers", "NON", "Jour 1"), ("RUN_TR_A", "Rendement total, onglets 1-5", "NON", "Jour 1"),
       ("RUN_TR_B", "Rendement total, onglets 6-9", "NON", "Jour 1"), ("RUN_CAP_A", "Capitalisation, onglets 1-5", "NON", "Jour 2"),
       ("RUN_CAP_B", "Capitalisation, onglets 6-9", "NON", "Jour 2"), ("RUN_FUND", "Fondamentaux, onglets 1-4", "NON", "Jour 3")]
for i, row in enumerate(cfg, 2):
    for j, v in enumerate(row, 1): ws.cell(i, j, v)
    name(row[0], f"Config!$C${i}")
ws.cell(2, 3).fill = PatternFill("solid", fgColor=AMB)
for c, w in zip("ABCD", [14, 36, 12, 50]): ws.column_dimensions[c].width = w

# ---------------- Tests
ws = wb.create_sheet("Tests", 1)
ws.cell(1, 1, "Tests — à lire avant tout. Valeur de référence = extraction du 29/10 (même titre, même exercice).").font = Font(bold=True, color=NAVY)
head(ws, 3, ["Test", "Ce qui est testé", "Référence 29/10", "Formule A", "Formule B", "Statut A", "Statut B"])
tests = [("F1", "Siemens, chiffre d'affaires exercice clos le 30/09/2024 (M EUR)", "SIE GY Equity", "SALES_REV_TURN", "20240101", "20241231", 75930.0),
         ("F2", "Ricoh, chiffre d'affaires exercice clos le 31/03/2024 (M EUR)", "7752 JT Equity", "SALES_REV_TURN", "20240101", "20241231", 14998.0459),
         ("F3", "Apple, EBIT exercice clos le 28/09/2024 (M EUR)", "AAPL UW Equity", "EBIT", "20240101", "20241231", 113686.096)]
col = 10
for i, (n, what, t, f, s0, e0, ref) in enumerate(tests, 4):
    ws.cell(i, 1, n); ws.cell(i, 2, what); ws.cell(i, 3, ref)
    a, b = fund_formula(t, f, f'"{s0}"', f'"{e0}"')
    for k, frm in enumerate((a, b)):
        c0 = col + 3 * k
        ws.cell(3, c0, "Formule A" if k == 0 else "Formule B").font = B
        ws.cell(5 + (i - 4) * 4, c0, "=" + frm)
        ws.cell(i, 4 + k, f"=IFERROR(INDEX({L(c0 + 1)}{5 + (i - 4) * 4}:{L(c0 + 1)}{8 + (i - 4) * 4},1),\"\")")
        ws.cell(i, 6 + k, f'=IF(N({L(4 + k)}{i})=0,"KO",IF(ABS({L(4 + k)}{i}/C{i}-1)<0.01,"OK","KO"))')
ws.cell(7, 1, "C1"); ws.cell(7, 2, "Ricoh, capitalisation au 31/12/2021 (référence en M EUR)"); ws.cell(7, 3, 6121.5705)
ws.cell(3, 16, "C1").font = B; ws.cell(5, 16, '=BDH("7752 JT Equity","CUR_MKT_CAP","20211231","20211231","Currency","EUR")')
ws.cell(7, 4, "=IFERROR(INDEX(Q5:Q6,1),\"\")")
ws.cell(7, 6, '=IF(N(D7)=0,"KO",IF(OR(ABS(D7/C7-1)<0.03,ABS(D7/C7/1000000-1)<0.03),"OK","KO"))')
ws.cell(9, 1, "Formule A : \"Per\",\"Y\",\"FILING_STATUS\",\"OR\",\"EQY_FUND_CRNCY\",\"EUR\"   ·   Formule B : \"Per\",\"Y\",\"Days\",\"A\",\"FILING_STATUS\",\"OR\",\"Currency\",\"EUR\"").font = Font(size=9, italic=True)
for c, w in zip("ABCDEFG", [6, 58, 14, 14, 14, 10, 10]): ws.column_dimensions[c].width = w
for rng in ("F4:G7",):
    for v, fill in (("OK", OKF), ("KO", KOF)):
        ws.conditional_formatting.add(rng, CellIsRule(operator="equal", formula=[f'"{v}"'], fill=PatternFill("solid", fgColor=fill)))

# ---------------- Tickers
ws = wb.create_sheet("Tickers")
STAT = ["NAME", "CRNCY", "GICS_SECTOR_NAME", "GICS_INDUSTRY_GROUP_NAME", "CNTRY_OF_RISK", "CNTRY_OF_DOMICILE", "ID_BB_GLOBAL"]
head(ws, 1, ["Ticker"] + STAT)
for i, t in enumerate(UNION, 2):
    ws.cell(i, 1, t)
    for j, f in enumerate(STAT, 2):
        ws.cell(i, j, f'=IF(RUN_Tickers="OUI",BDP($A{i},"{f}"),"")')
for c, w in zip("ABCDEFGH", [20, 34, 7, 24, 30, 8, 8, 16]): ws.column_dimensions[c].width = w
ws.freeze_panes = "B2"

# ---------------- TR and CAP (100 tickers per sheet)
def block_sheets(prefix, field, label, sw_a, sw_b, ccy=True):
    for k in range(0, len(UNION), 100):
        n = k // 100 + 1; sw = sw_a if n <= 5 else sw_b
        ws = wb.create_sheet(f"{prefix}_{n:02d}")
        ws.cell(1, 1, f"{label} — titres {k + 1} à {min(k + 100, len(UNION))}").font = Font(bold=True, color=NAVY)
        for j, t in enumerate(UNION[k:k + 100]):
            c = 1 + 2 * j
            ws.cell(2, c, t).font = B; ws.cell(3, c, "Date").fill = FG; ws.cell(3, c + 1, field).fill = FG
            ws.cell(4, c, f'=IF({sw}="OUI",BDH("{t}","{field}",P_START,P_END,"Per","M","Days","A","Fill","P","Currency","EUR"),"")')
            ws.column_dimensions[L(c)].width = 11; ws.column_dimensions[L(c + 1)].width = 11
        ws.freeze_panes = "A4"
block_sheets("TR", "TOT_RETURN_INDEX_GROSS_DVDS", "Rendement total mensuel (indice, dividendes bruts réinvestis), EUR", "RUN_TR_A", "RUN_TR_B")
block_sheets("CAP", "CUR_MKT_CAP", "Capitalisation boursière mensuelle, EUR", "RUN_CAP_A", "RUN_CAP_B")

# ---------------- FUND (250 tickers per sheet, 23 rows per ticker)
for k in range(0, len(FUND), 250):
    n = k // 250 + 1
    ws = wb.create_sheet(f"FUND_{n:02d}")
    ws.cell(1, 1, f"Fondamentaux annuels EUR, chiffres d'origine — titres {k + 1} à {min(k + 250, len(FUND))}").font = Font(bold=True, color=NAVY)
    for j, (f, lab) in enumerate(FIELDS):
        c = 3 + 2 * j
        ws.cell(2, c, lab).font = B; ws.cell(3, c, "Date").fill = FG; ws.cell(3, c + 1, f).fill = FG
        ws.column_dimensions[L(c)].width = 11; ws.column_dimensions[L(c + 1)].width = 12
    ws.cell(3, 1, "N°").fill = FG; ws.cell(3, 2, "Ticker").fill = FG; ws.column_dimensions["B"].width = 18
    for i, t in enumerate(FUND[k:k + 250]):
        r = 4 + 23 * i
        ws.cell(r, 1, k + i + 1); ws.cell(r, 2, t)
        for j, (f, lab) in enumerate(FIELDS):
            a, b = fund_formula(t, f)
            ws.cell(r, 3 + 2 * j, f'=IF(RUN_FUND="OUI",IF(FUND_MODE="B",{b},{a}),"")')
    ws.freeze_panes = "C4"

out = "/home/claude/work/deliv/SAT_Extraction_2_Data.xlsx"; wb.save(out)
print(out, "| union", len(UNION), "| fund", len(FUND), "| sheets", wb.sheetnames)
