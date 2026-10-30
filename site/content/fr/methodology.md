---
title: Méthodologie
---
# Données et méthodologie

## Sources
- **Terminal Bloomberg** (salle SKEMA, extractions d'octobre 2026) : compositions d'indices, prix, dividendes, fondamentaux standardisés tels que publiés à l'origine, capitalisations, change, MSCI World Net EUR, €STR ; indices pays, secteurs, obligataires et matières premières pour les stratégies ETF. Les données sous licence **ne sont pas** publiées ici : le site montre la méthode et des résultats agrégés.
- **Kenneth French Data Library** : facteurs Developed (5 facteurs + momentum).
- **OCDE via FRED** : taux interbancaires 3 mois par devise, pour le coût de couverture de change.

## Règles d'intégrité
1. **Pas de biais du survivant :** l'univers à chaque date est la composition de l'indice à cette date, y compris les titres radiés ensuite.
2. **Pas de look-ahead :** un exercice comptable n'est utilisé qu'à partir de la clôture + 6 mois et jamais avant sa publication ; chiffres d'origine (non retraités) ; les ordres sont exécutés après la date de décision.
3. **Unités vérifiées :** capitalisation vs prix × actions, réplique du benchmark à partir des rendements des titres (corrélation 0,996 avec le MSCI World Net), étude d'événement sur les dates de détachement.
4. **Net vs brut :** rendements nets de retenue à la source, comme le benchmark.
5. **Reproductible :** une commande reconstruit chaque chiffre depuis le fichier brut ; des tests unitaires vérifient le décalage, les rendements et chaque contrainte.
6. **Chaque arbitrage consigné** avec ses alternatives dans un journal de décisions.

## Outils
Python (pandas, NumPy, SciPy/HiGHS pour la sélection en nombres entiers, cvxpy pour les optimiseurs, scikit-learn pour le shrinkage de Ledoit-Wolf, statsmodels pour les régressions factorielles), PowerPoint pour les decks.
