---
title: The backtest bug worth 2% a year — prices that already include dividends
date: 29 Oct 2026
summary: Rebuilding the benchmark from my own security returns exposed a dividend double count. An event study on 38,000 ex-dates proved it.
---
## The symptom
Before testing any strategy I rebuilt the benchmark: all developed-market members of the index, cap-weighted at each date, from my own weekly total returns (price plus reinvested dividends). The replica beat MSCI World Net by **two points a year**, every year, with 0.996 correlation. Systematic, small, and far too good — the textbook sign of a data error rather than skill.

## The test
If prices are not adjusted for dividends, a stock should fall by roughly its dividend on the ex-date. I regressed each stock's weekly price return on the dividend yield paid that week, controlling for the market, over about 38,000 ex-date weeks. The slope should be close to −1. It was close to **0** in every yield bucket, including large special dividends.

Even a price-only replica beat the *net* benchmark. Conclusion: the price series extracted from the terminal were already adjusted for dividends. An earlier check on one stock had shown price and total-return index rising in lockstep — and been read as "the total-return field is broken", when it meant "the price already is a total-return series".

## The fix and what it changed
Total return is now the adjusted price return; the dividend history is used only to deduct withholding tax so that returns match the net benchmark. The replica now trails MSCI World Net by 0.3% a year — the residual being index-provider differences and a conservative tax haircut. Every strategy result would otherwise have been inflated by about 2% a year.

## Lesson
Rebuild the benchmark before you trust the strategy. If a backtest beats the market by a constant margin, suspect units, survivorship and look-ahead first.
