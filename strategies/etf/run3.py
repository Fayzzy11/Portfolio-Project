import pandas as pd, numpy as np, json
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import engine as E
pd.set_option("display.width",220)
rc,rs=E.country_returns(),E.sector_returns()
TS_c=E.value_score(E.VP,{k:v[0] for k,v in E.COUNTRIES.items()}); TS_s=E.value_score(E.VS,E.SECTORS)
XS_c=E.xs_value(E.VP,{k:v[0] for k,v in E.COUNTRIES.items()}).where(TS_c.notna()); XS_s=E.xs_value(E.VS,E.SECTORS).where(TS_s.notna())
M_c=E.xs_z(E.momentum(rc,12).shift(1)); M_s=E.xs_z(E.momentum(rs,12).shift(1))   # 12-1 momentum
cands={}
def add(name,W,R,ter=0.0025,start="2006-01-31"):
    r,to,_=E.run(W,R,cost=0.001,ter=ter,start=start); cands[name]=(r,to)
W,R=E.value_rotation(); add('V1 Rules (validated)',W,R)
W,R=E.value_rotation(mom_filter=True); add('V2 Rules + momentum filter (pre-registered variant)',W,R)
W,R=E.value_rotation_custom(XS_c,XS_s,rc,rs); add('V3 Cross-sectional value',W,R)
W,R=E.value_rotation_custom((E.xs_z(TS_c)+M_c)/2,(E.xs_z(TS_s)+M_s)/2,rc,rs); add('V4 Value + momentum composite',W,R)
W,R=E.value_rotation_custom((XS_c+M_c)/2,(XS_s+M_s)/2,rc,rs); add('V5 Cross-sectional value + momentum',W,R)
W,R=E.value_rotation(); add('V6 Rules + market trend overlay (10m SMA)',E.overlay_sma(W),R)
W,R=E.value_rotation(mom_filter=True); add('V7 Momentum filter + trend overlay',E.overlay_sma(W),R)
WT,RT=E.trend(); add('T1 Trend rules (validated)',WT,RT,ter=0.003,start="2001-01-31")
WT2,_=E.trend(target_vol=0.12); add('T2 Trend, 12% vol target',WT2,RT,ter=0.003,start="2001-01-31")
WT3,_=E.trend(lookbacks=(12,)); add('T3 Trend, 12-month signal only',WT3,RT,ter=0.003,start="2001-01-31")
WT4,_=E.trend(lookbacks=(1,3,6,12)); add('T4 Trend, 1/3/6/12 blend',WT4,RT,ter=0.003,start="2001-01-31")
v1=cands['V1 Rules (validated)'][0]; t1=cands['T1 Trend rules (validated)'][0]; v2=cands['V2 Rules + momentum filter (pre-registered variant)'][0]
for nm,a,b in [('C1 50% value rules + 50% trend',v1,t1),('C2 50% value mom.filter + 50% trend',v2,t1)]:
    r=(0.5*a+0.5*b).dropna(); cands[nm]=(r,None)
cands['MSCI World Net EUR']=(E.BENCH.loc["2006-01-31":"2026-09-30"],None)
cands['60/40 EUR']=(E.sixty_forty().loc["2006-01-31":"2026-09-30"],None)
rows=[]
for nm,(r,to) in cands.items():
    r=r.loc["2006-01-31":"2026-09-30"]
    full=E.stats(r); d=E.stats(r.loc[:"2015-12-31"]); v=E.stats(r.loc["2016-01-31":])
    rows.append(dict(name=nm,cagr=full['cagr'],vol=full['vol'],sharpe=full['sharpe'],mdd=full['mdd'],
      design_cagr=d['cagr'],design_sharpe=d['sharpe'],valid_cagr=v['cagr'],valid_sharpe=v['sharpe'],valid_mdd=v['mdd'],
      turnover=(to.loc["2006-01-31":].mean()*12 if to is not None else np.nan)))
df=pd.DataFrame(rows).set_index('name')
print(df.to_string(float_format=lambda x:f"{x:.3f}"))
pd.to_pickle(cands,os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'data', 'etf', 'cands.pkl'))
