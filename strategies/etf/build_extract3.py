"""Bloomberg workbook #3 (4 Nov 2026), satellite history step 1: tests + point-in-time compositions of WORLD Index,
semi-annual, Dec 2005 -> Dec 2020 (the 10 dates of 2021-2025 already exist in the Claude Code project).
Step 2 (prices + fundamentals of the top 300 developed-market names at each date) is built from this file's output."""
import openpyxl, pandas as pd
from openpyxl.styles import Font, PatternFill, Alignment
from openpyxl.workbook.defined_name import DefinedName
from openpyxl.utils import get_column_letter as L
from openpyxl.formatting.rule import CellIsRule

NAVY, GOLD, GREY, OKF, KOF, AMB = "0B1F3A", "B08D57", "F1EFEA", "DDEBDD", "F6E3E0", "F6EDD9"
H = Font(bold=True, color="FFFFFF"); B = Font(bold=True); FH = PatternFill("solid", fgColor=NAVY); FG = PatternFill("solid", fgColor=GREY)
DATES = [d for d in pd.bdate_range("2005-12-01", "2020-12-31", freq="BME") if d.month in (6, 12)]
wb = openpyxl.Workbook(); wb.calculation.fullCalcOnLoad = True
def name(n, ref): wb.defined_names[n] = DefinedName(n, attr_text=ref)
def head(ws, r, vals):
    for i, v in enumerate(vals, 1):
        c = ws.cell(r, i, v); c.fill = FH; c.font = H; c.alignment = Alignment(wrap_text=True, vertical="center")

ws = wb.active; ws.title = "Mode d'emploi"
lines = [("Extraction n°3 — historique du satellite, étape 1 : compositions de WORLD Index 2005-2020", "t"), ("", None),
 ("Pourquoi : le satellite (8 titres) n'a des scores que depuis 2021. Pour le tester sur 20 ans, il faut savoir quels titres étaient dans l'univers à chaque date passée (sinon biais du survivant). Cette étape récupère ces compositions ; l'étape 2 (prix mensuels + fondamentaux des 300 plus grosses capitalisations des pays développés) sera construite à partir de ce fichier.", None), ("", None),
 ("Étapes (environ 20 minutes, une seule session) :", "b"),
 ("1. Ouvre le fichier sur le terminal, ENREGISTRE SOUS dans ton dossier, attends 1 minute.", None),
 ("2. Onglet Tests : regarde la colonne Statut.", None),
 ("   • Test 1 et 2 (compositions 2006 et 2011) : si KO, WORLD Index n'a pas d'historique aussi ancien. ARRÊTE-TOI et dis-le-moi : on choisira un autre indice ensemble. Ne lance pas la suite.", None),
 ("   • Tests 3 et 4 (rendement total mensuel, titre vivant et titre radié) : notent seulement si Bloomberg garde l'historique des sociétés disparues. KO = à me signaler, mais tu peux continuer.", None),
 ("3. Onglet Config : passe RUN_Compo_A à OUI (dates 2005-2012). Attends que l'onglet Compositions soit rempli pour ces dates (plus de « #N/A Requesting »), puis Ctrl+A, Ctrl+C, Ctrl+Alt+V, V, Entrée (collage en valeurs).", None),
 ("4. Même chose avec RUN_Compo_B (dates 2013-2020). Colle aussi l'onglet Tests en valeurs.", None),
 ("5. Enregistre sous SAT_COMPO_AAAAMMJJ.xlsx et envoie-le à Claude.", None), ("", None),
 ("Leçon Bloomberg : la formule utilisée est BDS(\"WORLD Index\",\"INDX_MWEIGHT_HIST\",\"END_DATE_OVERRIDE\",date). C'est l'équivalent Excel de MEMB <GO> avec une date passée. Piège classique : sans END_DATE_OVERRIDE, Bloomberg renvoie la composition d'AUJOURD'HUI, ce qui crée un biais du survivant.", None),
 ("Si une cellule affiche #N/A Review : plafond Bloomberg. Arrête-toi, enregistre, envoie le fichier tel quel.", None),
 ("Rappel : données Bloomberg brutes — ni site, ni GitHub.", None)]
for i, (t, f) in enumerate(lines, 1):
    c = ws.cell(i, 1, t); c.alignment = Alignment(wrap_text=True, vertical="top")
    if f == "t": c.font = Font(bold=True, size=14, color=NAVY)
    if f == "b": c.font = Font(bold=True, color=GOLD)
ws.column_dimensions["A"].width = 130; ws.sheet_view.showGridLines = False

ws = wb.create_sheet("Config"); head(ws, 1, ["Nom", "Rôle", "Valeur", "Note"])
cfg = [("RUN_Compo_A", "Interrupteur compositions 2005-2012", "NON", "Passe à OUI, attends, colle en valeurs"),
       ("RUN_Compo_B", "Interrupteur compositions 2013-2020", "NON", "Seulement après A"),
       ("T_START", "Début test rendement total", "20051231", ""), ("T_END", "Fin test rendement total", "20260930", "")]
for i, row in enumerate(cfg, 2):
    for j, v in enumerate(row, 1): ws.cell(i, j, v)
    name(row[0], f"Config!$C${i}")
for c, w in zip("ABCD", [16, 36, 12, 50]): ws.column_dimensions[c].width = w

ws = wb.create_sheet("Tests", 1)
ws.cell(1, 1, "Tests — à regarder avant de lancer les compositions").font = Font(bold=True, color=NAVY)
head(ws, 3, ["Test", "Ce qui est testé", "Résultat", "Attendu", "Statut"])
tests = [("1", "Composition WORLD Index au 30/06/2006 : nombre de membres (colonnes H-I)", "H", 'BDS("WORLD Index","INDX_MWEIGHT_HIST","END_DATE_OVERRIDE","20060630")', 1000),
         ("2", "Composition WORLD Index au 30/12/2011 : nombre de membres (colonnes K-L)", "K", 'BDS("WORLD Index","INDX_MWEIGHT_HIST","END_DATE_OVERRIDE","20111230")', 1000),
         ("3", "Rendement total mensuel EUR, titre vivant (Shell) : nombre de mois (colonnes N-O)", "N", 'BDH("SHEL LN Equity","TOT_RETURN_INDEX_GROSS_DVDS",T_START,T_END,"Per","M","Currency","EUR")', 200),
         ("4", "Rendement total mensuel EUR, titre radié (Lehman) : nombre de mois (colonnes Q-R)", "Q", 'BDH("LEHMQ US Equity","TOT_RETURN_INDEX_GROSS_DVDS",T_START,"20081231","Per","M","Currency","EUR")', 20)]
for i, (n, what, col, f, thr) in enumerate(tests, 4):
    ws.cell(i, 1, n); ws.cell(i, 2, what); ws.cell(i, 4, f"> {thr}")
    from openpyxl.utils import column_index_from_string as CI
    c0 = CI(col); vcol = L(c0 + 1)
    ws.cell(3, c0, f"Test {n}").font = B
    ws.cell(4, c0, "=" + f)
    ws.cell(i, 3, f"=COUNT({vcol}4:{vcol}5000)")
    ws.cell(i, 5, f'=IF(C{i}>{thr},"OK","KO")')
ws.cell(9, 1, "Si le test 4 est KO, essaie à la main le ticker de Lehman avec LEHMQ US Equity <GO> puis HP <GO> : la leçon est de voir si l'historique d'une société radiée existe encore.").font = Font(italic=True, size=9)
for c, w in zip("ABCDE", [6, 70, 12, 10, 10]): ws.column_dimensions[c].width = w
for v, fill in (("OK", OKF), ("KO", KOF)):
    ws.conditional_formatting.add("E4:E7", CellIsRule(operator="equal", formula=[f'"{v}"'], fill=PatternFill("solid", fgColor=fill)))

ws = wb.create_sheet("Compositions")
ws.cell(1, 1, "Composition historique de WORLD Index (tous pays) — membres et poids à chaque date").font = Font(bold=True, color=NAVY)
for k, d in enumerate(DATES):
    c = 1 + 3 * k
    sw = "RUN_Compo_A" if d.year <= 2012 else "RUN_Compo_B"
    ws.cell(2, c, d.strftime("%d/%m/%Y")).font = B
    ws.cell(3, c, "Membre").fill = FG; ws.cell(3, c + 1, "Poids %").fill = FG
    ws.cell(4, c, f'=IF({sw}="OUI",BDS("WORLD Index","INDX_MWEIGHT_HIST","END_DATE_OVERRIDE","{d.strftime("%Y%m%d")}"),"")')
    ws.column_dimensions[L(c)].width = 14; ws.column_dimensions[L(c + 1)].width = 9; ws.column_dimensions[L(c + 2)].width = 2
ws.freeze_panes = "A4"
out = "/home/claude/work/deliv/SAT_Extraction_1_Compositions.xlsx"; wb.save(out); print(out, len(DATES), DATES[0].date(), DATES[-1].date())
