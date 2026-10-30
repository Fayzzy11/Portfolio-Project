# Checklist anti-biais (écrite avant d'interpréter le backtest)

| # | Risque | Contrôle | Preuve | Statut |
|---|---|---|---|---|
| 1 | **Biais du survivant** | Univers à chaque date = composition de WORLD à cette date (10 listes datées), jamais les membres actuels ni l'union | `src/universe.py::point_in_time_universe` ; le nombre de membres passe de 3 332 à 2 248, les titres radiés (suffixe `…D`) sont présents | OK |
| 2 | Survivant (période de détention) | Une ligne qui cesse de coter rapporte 0 % après son dernier cours ; aucun gain prolongé artificiellement | `src/returns.py::total_returns` et son test unitaire | OK — limite : une faillite sans dernier cours passerait inaperçue (aucune observée en portefeuille) |
| 3 | **Look-ahead (comptable)** | Exercice utilisable à partir de la clôture + 6 mois, et pas avant sa publication | `src/signals.py` ; un test d'intégration échoue si un score utilise un exercice trop tôt | OK |
| 4 | Look-ahead (retraitements) | Chiffres publiés à l'origine (`FILING_STATUS = OR`) à l'extraction | Paramètres d'extraction (journal 26/10) | OK (à confirmer au terminal) |
| 5 | Look-ahead (prix et exécution) | Les décisions utilisent l'information jusqu'à D ; les ordres passent à la clôture du premier vendredi après D | `src/backtest.py`, fonction `trade_date` | OK |
| 6 | Look-ahead (classification) | Secteur GICS **actuel** appliqué à tout l'historique | Limite connue de l'extraction | Ouvert — impact limité (peu de reclassements, surtout la réforme GICS 2023 : paiements, Visa et Mastercard vers la Finance) |
| 7 | **Unités : dividendes comptés deux fois** | Une étude d'événement prouve que `PX_LAST` inclut déjà les dividendes : rendement total = rendement du prix ajusté | Rapport qualité des données §3 ; réplique du benchmark −0,3 %/an vs MSCI World Net | **Corrigé** (était +2 %/an) |
| 8 | Unités : pence et sous-unités | Prix en EUR à la source ; devise des dividendes déduite pour GBp/ILs (sert seulement à la retenue) | `src/returns.py::clean_dividends` | OK |
| 9 | Unités : millions et EUR | Fondamentaux et capitalisation en millions d'EUR ; ratios calculés sur des totaux société | Capitalisation vs prix × actions : médiane 1,07 | OK |
| 10 | **Dividendes bruts vs nets** | Résultat principal net de retenue (convention MSCI net) ; brut donné en sensibilité (+0,9 %/an en équipondéré) | `outputs/backtest/robustness.csv` | OK |
| 11 | Écart de fournisseur d'indice | Univers Bloomberg World DM vs benchmark MSCI World | Corrélation de la réplique 0,996, tracking error 1,2 % | Signalé |
| 12 | Coûts de transaction | 15 pb × rotation, construction initiale incluse ; pas d'impact de marché | `outputs/backtest/performance_summary.csv` (avant et après coûts) | Signalé (impact sous-estimé pour les titres moins liquides) |
| 13 | Coût de couverture de change | Portage à partir des écarts de taux interbancaires 3 mois (parité couverte), couverture recalée chaque semaine | `src/backtest.py` | Signalé (pas de fourchette sur les forwards, recalage hebdomadaire idéalisé) |
| 14 | Data snooping dans la construction | Tampon de rotation fixé avant de voir les résultats corrigés (cible < 60 %/an) ; un tampon plus large faisait mieux mais n'a **pas** été retenu | Journal des décisions, C3 | OK |
| 15 | Petit échantillon | 5 ans, 10 rebalancements, un seul régime | t-stat de l'IC ≈ 2,1 ; ratio d'information non significatif | Signalé |
