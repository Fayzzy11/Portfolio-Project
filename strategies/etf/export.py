import pandas as pd, numpy as np, json
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import engine as E
cands=pd.read_pickle(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'data', 'etf', 'cands.pkl'))
def nav(r): return [round(x,5) for x in (1+r).cumprod()]
def pack(r,bench_r,b2=None,start=None):
    r=r.loc[start:]; b=bench_r.reindex(r.index); 
    st=E.stats(r,b); stb=E.stats(b)
    out=dict(dates=[d.strftime("%Y-%m") for d in r.index], nav=nav(r), bench=nav(b),
             stats={k:(float(v) if isinstance(v,(float,np.floating)) else v) for k,v in st.items() if v is not None},
             bench_stats={k:(float(v) if isinstance(v,(float,np.floating)) else v) for k,v in stb.items()},
             calendar={int(k):float(v) for k,v in E.calendar(r).items()}, bench_calendar={int(k):float(v) for k,v in E.calendar(b).items()})
    if b2 is not None:
        b2=b2.reindex(r.index); out['bench2']=nav(b2); out['bench2_stats']={k:(float(v) if isinstance(v,(float,np.floating)) else v) for k,v in E.stats(b2).items()}
        out['bench2_calendar']={int(k):float(v) for k,v in E.calendar(b2).items()}
    return out
sf=E.sixty_forty()
res={'value':pack(cands['V1 Rules (validated)'][0],E.BENCH,start="2006-01-31"),
     'trend':pack(cands['T1 Trend rules (validated)'][0],E.BENCH,sf,start="2001-01-31")}
res['value']['turnover']=float(cands['V1 Rules (validated)'][1].loc["2006":].mean()*12)
res['trend']['turnover']=float(cands['T1 Trend rules (validated)'][1].loc["2001":].mean()*12)
rows=[]
for nm,(r,to) in cands.items():
    r=r.loc["2006-01-31":"2026-09-30"]; f=E.stats(r); d=E.stats(r.loc[:"2015-12-31"]); v=E.stats(r.loc["2016-01-31":])
    rows.append(dict(name=nm,cagr=f['cagr'],vol=f['vol'],sharpe=f['sharpe'],mdd=f['mdd'],design_cagr=d['cagr'],design_sharpe=d['sharpe'],valid_cagr=v['cagr'],valid_sharpe=v['sharpe']))
res['variants']=[{k:(float(x) if isinstance(x,(float,np.floating)) else x) for k,x in r.items()} for r in rows]
W,_=E.value_rotation(); last=W.iloc[-1]; res['value']['holdings']={'date':W.index[-1].strftime('%Y-%m'),'lines':[k for k,v in last.items() if v>0]}
WT,_=E.trend(); lt=WT.iloc[-1]; res['trend']['holdings']={'date':WT.index[-1].strftime('%Y-%m'),'weights':{k:float(round(v,4)) for k,v in lt.items() if v>0.001}}
res['signal']={'ic12_countries':-0.046,'ic12_sectors':-0.026,'spread_countries':-0.006,'spread_sectors':-0.011,'ew_countries_cagr':0.076,'ew_sectors_cagr':0.088}
json.dump(res,open(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'site', 'data', 'etf_strategies.json'),'w'))
print('ok', res['value']['holdings'], res['trend']['stats']['cagr'], res['trend']['bench2_stats']['cagr'])
