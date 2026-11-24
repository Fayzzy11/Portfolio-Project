"""Shared fields for the v3 pitch specs (English, French)."""
RATINGS = {"Overweight": ("OVERWEIGHT", "SURPONDÉRER"), "Neutral": ("NEUTRAL", "NEUTRE"), "Underweight": ("UNDERWEIGHT", "SOUS-PONDÉRER"), "Sell": ("SELL", "VENDRE")}
BYLINE = ("Noah Doose  ·  MSc Financial Markets & Investments, SKEMA Business School  ·  Student research, not investment advice",
          "Noah Doose  ·  MSc Financial Markets & Investments, SKEMA Business School  ·  Travail étudiant, pas un conseil en investissement")
KICKER = ("Stock pitch  ·  Global Value Rotation, stock satellite  ·  29 October 2026",
          "Stock pitch  ·  Rotation Value mondiale, satellite actions  ·  29 octobre 2026")
DATA_NOTE = ("Company figures come from the filings listed on the left. Prices, consensus and 52-week ranges are third-party (29 Oct 2026) "
             "and will be replaced by Bloomberg in December 2026. Screen multiples use the 31 Dec 2025 rebalance, on accounts lagged six months.",
             "Les chiffres de la société viennent des publications listées à gauche. Cours, consensus et plus haut/plus bas 52 semaines sont de source tierce (29 oct. 2026) "
             "et seront remplacés par Bloomberg en décembre 2026. Les multiples du screen sont ceux du rebalancement du 31 déc. 2025, sur des comptes décalés de six mois.")


def base(code, stem, company, short, rating, listing, claim, sub, target, price, upside, date=("29 Oct 2026", "29 oct. 2026"), kicker=KICKER,
         horizon=("12 months", "12 mois")):
    down = upside[0].startswith("−")
    return {"code": code, "stem": stem, "company": company, "short": short, "rating": rating, "rating_label": RATINGS[rating], "kicker": kicker,
            "claim": claim, "sub": sub, "target_s": target, "price_s": price, "upside_s": upside,
            "target_cap": (f"Base-case value, {horizon[0]}", f"Valeur centrale, {horizon[1]}"), "price_cap": (f"Price, {date[0]}", f"Cours, {date[1]}"),
            "upside_cap": ("Downside" if down else "Upside", "Baisse" if down else "Potentiel"),
            "byline": BYLINE,
            "footer": (f"{company} ({listing[0]})  ·  Noah Doose  ·  Student research, not investment advice  ·  Prices as of {date[0]}",
                       f"{company} ({listing[1]})  ·  Noah Doose  ·  Travail étudiant, pas un conseil en investissement  ·  Cours au {date[1]}")}


def pct_fmt(d=1):
    def f(x, lg):
        s = f"{x * 100:.{d}f}"
        return (s + "%") if lg == "en" else (s.replace(".", ",") + " %")
    return f


def mult_fmt(d=1, suffix="x"):
    def f(x, lg):
        s = f"{x:.{d}f}"
        return (s if lg == "en" else s.replace(".", ",")) + suffix
    return f


def money_fmt(sym, d=2, unit=""):
    def f(x, lg):
        s = f"{x:,.{d}f}"
        if lg == "fr":
            s = s.replace(",", " ").replace(".", ",")
            return f"{s}{unit} {sym}"
        return f"{sym}{s}{unit}"
    return f
