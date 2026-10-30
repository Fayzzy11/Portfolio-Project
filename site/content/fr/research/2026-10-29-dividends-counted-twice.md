---
title: Le bug à 2 % par an — des prix qui incluent déjà les dividendes
date: 29 oct. 2026
summary: En reconstruisant le benchmark à partir de mes propres rendements, j'ai découvert un double comptage des dividendes. Une étude d'événement sur 38 000 détachements l'a prouvé.
---
## Le symptôme
Avant de tester une stratégie, j'ai reconstruit le benchmark : tous les membres de l'indice dans les pays développés, pondérés par la capitalisation à chaque date, à partir de mes propres rendements totaux hebdomadaires (prix plus dividendes réinvestis). La réplique battait le MSCI World Net de **deux points par an**, chaque année, avec une corrélation de 0,996. Systématique, faible et beaucoup trop beau : le signe classique d'une erreur de données plutôt que d'un talent.

## Le test
Si les prix ne sont pas ajustés des dividendes, une action doit baisser à peu près du montant du dividende le jour du détachement. J'ai régressé le rendement hebdomadaire de chaque action sur le rendement du dividende versé cette semaine-là, en contrôlant par le marché, sur environ 38 000 semaines de détachement. La pente aurait dû être proche de −1. Elle était proche de **0** dans toutes les tranches de rendement, dividendes exceptionnels compris.

Même une réplique « prix seuls » battait le benchmark *net*. Conclusion : les prix extraits du terminal étaient déjà ajustés des dividendes. Une vérification antérieure sur une seule action montrait prix et indice de rendement total progressant ensemble ; je l'avais lue comme « le champ total return ne fonctionne pas », alors qu'elle voulait dire « le prix est déjà une série de rendement total ».

## La correction et ce qu'elle change
Le rendement total est désormais le rendement du prix ajusté ; l'historique des dividendes sert seulement à déduire la retenue à la source pour que les rendements soient comparables au benchmark net. La réplique fait maintenant 0,3 % par an de moins que le MSCI World Net, l'écart venant des différences entre fournisseurs d'indices et d'une retenue prudente. Sans cette correction, chaque résultat aurait été gonflé d'environ 2 % par an.

## La leçon
Reconstruire le benchmark avant de croire la stratégie. Si un backtest bat le marché d'une marge constante, soupçonner d'abord les unités, le biais du survivant et le look-ahead.
