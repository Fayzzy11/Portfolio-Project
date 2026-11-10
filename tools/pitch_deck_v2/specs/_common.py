"""Shared fields for the pitch specs."""
RATINGS = {"Overweight": ("OVERWEIGHT", "SURPONDÉRER"), "Neutral": ("NEUTRAL", "NEUTRE"), "Underweight": ("UNDERWEIGHT", "SOUS-PONDÉRER"), "Sell": ("SELL", "VENDRE")}
BYLINE = ("Noah Doose  ·  MSc Financial Markets & Investments, SKEMA Business School  ·  Student research, not investment advice",
          "Noah Doose  ·  MSc Financial Markets & Investments, SKEMA Business School  ·  Travail étudiant, pas un conseil en investissement")


def base(code, stem, company, rating, listing, headline, target, price, upside, date=("29 Oct 2026", "29 oct. 2026"),
         kicker=("Stock pitch · Systematic value portfolio · 29 October 2026", "Stock pitch · Portefeuille value systématique · 29 octobre 2026"),
         authors="Noah Doose", byline=BYLINE, horizon=("12 months", "12 mois"), conviction=("Medium", "Moyenne")):
    return {"code": code, "stem": stem, "company": company, "rating": rating, "rating_label": RATINGS[rating], "kicker": kicker,
            "ticker_line": listing, "headline": headline, "target_s": target, "price_s": price, "upside_s": upside,
            "target_cap": ("Base-case value", "Valeur centrale"), "price_cap": (f"Price, {date[0]}", f"Cours, {date[1]}"), "upside_cap": ("Upside, 12 months", "Potentiel, 12 mois") if not upside[0].startswith("−") else ("Downside, 12 months", "Baisse, 12 mois"),
            "byline": byline,
            "footer": (f"{company} ({listing[0].split('  ·')[0]})  ·  {authors}  ·  Student research, not investment advice  ·  Prices as of {date[0]}",
                       f"{company} ({listing[1].split('  ·')[0]})  ·  {authors}  ·  Travail étudiant, pas un conseil en investissement  ·  Cours au {date[1]}"),
            "_panel": [(("Target", "Objectif"), target), (("Price", "Cours"), price), (("Upside", "Potentiel") if not upside[0].startswith("−") else ("Downside", "Baisse"), upside),
                       (("Horizon", "Horizon"), horizon), (("Conviction", "Conviction"), conviction)]}


CORE_JUN26 = ("ETF core, June 2026: Health Care, Consumer Staples, Energy, Real Estate; Germany, France, Denmark, Hong Kong.",
              "Cœur ETF, juin 2026 : Santé, Consommation de base, Énergie, Immobilier ; Allemagne, France, Danemark, Hong Kong.")
