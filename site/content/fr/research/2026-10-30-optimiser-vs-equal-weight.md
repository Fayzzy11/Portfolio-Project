---
title: Pourquoi l'optimiseur a perdu contre le 1/N dans un portefeuille value
date: 30 oct. 2026
summary: Mêmes 50 titres, trois pondérations. La variance minimale et la moyenne-variance font environ 2,3 points par an de moins que l'équipondération, et la raison tient au style, pas seulement à l'erreur d'estimation.
---
## L'expérience
À chacune des dix dates semestrielles, les mêmes 50 titres bon marché ont été pondérés de trois façons : à parts égales, par variance minimale (covariance de Ledoit-Wolf, 250 semaines) et par moyenne-variance classique, sous les mêmes contraintes (0,5 %-4 % par ligne, ±10 points par secteur et par pays).

## Le résultat
| Pondération | Rendement annuel | Actif vs MSCI World Net |
|---|---|---|
| Équipondéré | 11,6 % | −0,1 % |
| Variance minimale | 9,4 % | −2,3 % |
| Moyenne-variance | 9,4 % | −2,4 % |
| Proportionnelle au score | 11,5 % | −0,2 % |

## Pourquoi
- **Dérive de style.** La variance minimale surpondère les titres bon marché les moins volatils (consommation de base, services aux collectivités, santé défensive) et ajoute un biais qualité/investissement (RMW +0,12, CMA +0,23) avec un bêta plus faible. Sur 2021-2026, ce sont les *cycliques* bon marché qui ont payé.
- **Erreur d'estimation.** La moyenne-variance utilise les rendements moyens historiques, très bruités ; elle se concentre sur les gagnants passés au sein d'un portefeuille value, ce qui annule en partie le signal (DeMiguel, Garlappi et Uppal, 2009).
- **Rotation.** Les poids optimisés bougent davantage : 70 % par an contre 57 % pour l'équipondération.

## Ce que j'en retiens
L'équipondération est un benchmark difficile pour un optimiseur quand l'estimation des rendements attendus contient peu d'information. Si j'utilisais un optimiseur, je lui donnerais le score comme alpha (à la Grinold) et je contrôlerais explicitement les expositions factorielles plutôt que de minimiser la variance brute.
