"""Replace weak third-party sources in the pitch data with company documents (Noah, 10 Nov 2026) and correct the figures they changed.
Market data (prices, consensus, multiples) stays third-party until the Bloomberg refresh at the end of December 2026."""
import json, re
from pathlib import Path
D = Path(__file__).resolve().parents[2] / "site/data"
P = json.loads((D / "pitches.json").read_text(encoding="utf-8")); F = json.loads((D / "pitches_fr.json").read_text(encoding="utf-8"))
G = {p["code"]: p for p in P}
MKT = " (third-party market data; to be replaced by Bloomberg, Dec 2026)"

def rep(obj, a, b):
    s = json.dumps(obj, ensure_ascii=False); assert a in s, a; return json.loads(s.replace(a, b))

def src(code, drop, add):
    s = G[code]; keep = [x for x in s["sources"] if not any(d in x["label"] for d in drop)]
    keep += [{"tag": "", "label": l, "url": u} for l, u in add]
    for i, x in enumerate(keep, 1): x["tag"] = str(i)
    s["sources"] = keep

def mark_market(code, names):
    for x in G[code]["sources"]:
        if any(n in x["label"] for n in names) and "Bloomberg, Dec 2026" not in x["label"]: x["label"] += MKT

# ---------------- BNP Paribas: official tangible book (URD 2025) rolled forward, instead of KoalaGains
b = G["BNP_FP"]; v = b["valuation"]
tnbv25, eps26 = 93.50, round(9.36 / 0.75, 2)                 # URD 2025 p.152; 9M 2026 EPS €9.36 (Q3 2026 release) annualised
tnbv = round(tnbv25 + 0.40 * eps26, 1)                         # 60% distribution -> 40% retained
v["tbvps"] = tnbv
v["explain"] = (f"A bank is worth (RoTE − g) / (cost of equity − g) times its tangible book. We start from the bank's revalued tangible net book value of €93.50 per share at 31 December 2025 (Universal Registration Document 2025) and add 40% of 2026E EPS (9M EPS of €9.36 annualised, 60% distributed): €{tnbv} at end-2026. Long-term growth 2%; the cost of equity falls as the French risk premium normalises.")
outs = []
for name, rote, coe, story in v["scenarios"]:
    val = round(tnbv * (rote - v["g"]) / (coe - v["g"]), 2)
    outs.append({"name": name, "inputs": f"RoTE {rote:.1%}, CoE {coe:.1%} → {((rote - v['g']) / (coe - v['g'])):.2f}x TBV", "value": val, "upside": round(val / b["price"] - 1, 4), "story": story})
b["scenarios_out"] = outs; b["target"] = outs[1]["value"]; b["upside"] = outs[1]["upside"]
F["BNP_FP"]["explain"] = (f"Une banque vaut (RoTE − g) / (coût des fonds propres − g) fois son actif net tangible. Nous partons de l’actif net tangible réévalué publié par la banque, 93,50 € par action au 31 décembre 2025 (Document d’enregistrement universel 2025), auquel nous ajoutons 40 % du BPA 2026E (BPA 9 mois de 9,36 € annualisé, 60 % distribués) : {str(tnbv).replace('.', ',')} € fin 2026. Croissance de long terme 2 % ; le coût des fonds propres baisse à mesure que la prime de risque française se normalise.")
src("BNP_FP", ["KoalaGains", "Teleborsa"], [("BNP Paribas, 2025 Universal Registration Document and annual financial report (revalued tangible net book value per share €93.50 at 31 Dec 2025)", "https://invest.bnpparibas/en/document/universal-registration-document-and-annual-financial-report-2025"),
                                               ("BNP Paribas, second quarter 2026 results, conference call transcript, 23 Jul 2026", "https://invest.bnpparibas/")])
mark_market("BNP_FP", ["MarketScreener", "StockAnalysis", "Ideal Investisseur", "Trading Economics"])

# ---------------- Renault: FY2025 release, presentation and URD instead of press summaries
r = G["RNO_FP"]
r_txt = json.dumps(r, ensure_ascii=False)
for a, bb in [("Renault trades at about €7.7bn", "Renault trades at about €8.1bn"), ('"€7.7bn"', '"€8.1bn"'),
              ("equals about 86% of the market value", "equals about 80% of the market value"),
              ('"€7.3bn"', '"€7.4bn"'),
              ("About 35% after the 2023-2025 Alliance restructuring, according to press reports.", "About 34% of Nissan at end-2025: 15% held directly (lock-up at 10%) and 18.7% in a French trust free to sell (URD 2025)."),
              ("a stake of roughly 35% in Nissan, according to press reports", "a stake of about 34% in Nissan (15% direct, 18.7% in a French trust, URD 2025)")]:
    if a in r_txt: r_txt = r_txt.replace(a, bb)
    else: print("Renault: not found", a[:50])
r = json.loads(r_txt); r["mcap_bn"] = round(r["price"] * 289.29 / 1000, 2)   # 295.72m shares less 6.43m treasury (URD 2025)
r["financials"]["rows"][0][1] = "€56.2bn"; r["financials"]["note"] = r["financials"]["note"].replace("FY2024 revenue derived from the +3.0% growth reported for 2025. ", "")
G["RNO_FP"] = r
for k in ("one_liner", "key_stats", "thesis"):
    F["RNO_FP"][k] = json.loads(json.dumps(F["RNO_FP"][k], ensure_ascii=False).replace("7,7 Md€", "8,1 Md€").replace("environ 86 %", "environ 80 %"))
src("RNO_FP", ["Ideal Investisseur", "NewMobility", "Invezz", "ad-hoc-news"], [
    ("Renault Group, 2025 full-year results press release, 19 Feb 2026", "https://www.renaultgroup.com/en/finance/"),
    ("Renault Group, 2025 FY financial results presentation, 19 Feb 2026", "https://www.renaultgroup.com/en/finance/"),
    ("Renault Group, Document d'enregistrement universel 2025 (filed with the AMF on 18 Mar 2026): Nissan shareholding, share count, July 2025 guidance revision", "https://www.renaultgroup.com/en/finance/")])
mark_market("RNO_FP", ["MarketScreener", "StockAnalysis", "Investing.com"])

# ---------------- Carrefour: company releases and accounts instead of secondary sites
c = G["CA_FP"]
src("CA_FP", ["Rallies.ai", "ESM Magazine"], [
    ("Carrefour, \"First-quarter 2026 sales\" press release, 22 Apr 2026 (sales €21.1bn, +2.2% LFL)", "https://www.carrefour.com/en/finance"),
    ("Carrefour, 2026 Interim Financial Report (H1 2026)", "https://www.carrefour.com/en/finance"),
    ("Carrefour, consolidated financial statements at 31 Dec 2025 with the auditors' report (Note 4: disposal of Carrefour Italy to NewPrinces, effective 1 Dec 2025)", "https://www.carrefour.com/en/finance")])
mark_market("CA_FP", ["stockanalysis"])

# ---------------- Nippon Steel: Integrated Report 2026 and results instead of trade press
n = G["5401_JP"]
src("5401_JP", ["SteelOrbis", "GMK Center", "Hunton", "BusinessDay"], [
    ("Nippon Steel, Integrated Report 2026 (U. S. Steel acquisition; ¥500bn hybrid loan Sep 2025, ¥600bn convertible bonds Mar 2026, ¥900bn JBIC syndicated loan Mar 2026)", "https://www.nipponsteel.com/en/ir/library/"),
    ("Nippon Steel, Consolidated Financial Results for the Nine Months Ended 31 Dec 2025 (IFRS), 24 Feb 2026", "https://www.nipponsteel.com/en/ir/library/")])
mark_market("5401_JP", ["MarketScreener"])

# ---------------- OOIL: results announcements opened
src("316_HK", ["2024 Annual Results Announcement"], [("OOIL, 2024 Annual Results Announcement, HKEX, 13 Mar 2025", "https://www.ooilgroup.com/investor-relations")])

# ---------------- HP: SEC filings instead of blogs
h = json.loads(json.dumps(G["HPQ_US"], ensure_ascii=False).replace("CEO Enrique Lores leaves for PayPal; Bruce Broussard interim CEO", "CEO Enrique Lores steps down; board member Bruce Broussard named interim CEO"))
G["HPQ_US"] = h
src("HPQ_US", ["Action-Intell", "Futurum", "investingLive"], [
    ("HP Inc., Form 8-K Exh. 99.1, \"HP Inc. Announces Leadership Transition\", 3 Feb 2026", "https://www.sec.gov/Archives/edgar/data/47217/000114036126003514/ef20064653_ex99-1.htm"),
    ("HP Inc., Form 8-K Exh. 99.1, \"HP Inc. Reports Fiscal 2026 Second Quarter Results\", 27 May 2026", "https://www.sec.gov/Archives/edgar/data/0000047217/000004721726000027/hp43026exhibit991q226.htm")])
mark_market("HPQ_US", ["Massive", "Earnings Whispers"])

# ---------------- Centene: full Q1 2026 release instead of a search excerpt
cn = G["CNC_US"]
cn["sources"] = [x for x in cn["sources"] if "First Quarter 2026" not in x["label"]]
src("CNC_US", [], [("Centene, \"Centene Corporation Reports First Quarter 2026 Results\", 8-K Ex. 99.1, 28 Apr 2026", "https://www.sec.gov/Archives/edgar/data/0001071739/000107173926000099/a20260428ex991pressrelease.htm")])
mark_market("CNC_US", ["stockanalysis"])
mark_market("9503_JP", ["StockAnalysis"])

P = [G[p["code"]] for p in P]
(D / "pitches.json").write_text(json.dumps(P, ensure_ascii=False, indent=1), encoding="utf-8")
(D / "pitches_fr.json").write_text(json.dumps(F, ensure_ascii=False, indent=1), encoding="utf-8")
print("BNP TBV", tnbv, [(o["name"], o["value"], o["upside"]) for o in outs]); print("Renault mcap", r["mcap_bn"])
