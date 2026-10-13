// Shared rendering script for the trend-following report (English and French pages).
// Reads the results JSON embedded in the page and the language table T defined by each template.
(function(){
const D = JSON.parse(document.getElementById('report-data').textContent);
const REF = D.meta.reference, ETF = D.meta.etf, VAL = 'MSCI World Value (EUR)', WLD = 'MSCI World (EUR)';
const H = T.h;
const css = n => getComputedStyle(document.documentElement).getPropertyValue(n).trim();
const nf = (x,d=2) => x==null||isNaN(x) ? '–' : x.toLocaleString(T.locale,{minimumFractionDigits:d,maximumFractionDigits:d});
const pct = (x,d=1) => x==null||isNaN(x) ? '–' : (x*100).toLocaleString(T.locale,{minimumFractionDigits:d,maximumFractionDigits:d})+T.pctSep+'%';
const spct = (x,d=1) => x==null||isNaN(x) ? '–' : `<span class="${x>0?'pos':x<0?'neg':''}">${x>0?'+':''}${pct(x,d)}</span>`;
const eur = x => (LANG==='en' ? '€'+Math.round(x).toLocaleString(T.locale) : Math.round(x).toLocaleString(T.locale)+' €');
const short = n => T.names[n] || n;
const cls = c => T.classes[c] || c;
const lab = (t, l) => T.labels[t] || l;
const fmtDate = s => { const [y,m,d] = s.split('-'); return `${+d} ${T.months[+m-1]} ${y}`; };
const F = {nf, pct};

// ---------- KPI
const st = D.stats, CM = D.monthly_correlation, CB = D.combinations;
const kv = [nf(st.full[REF].sharpe), nf(CM.full[REF][VAL]), pct(st.full[VAL].max_drawdown,1), nf(st.full[ETF].sharpe)];
const ks = H.kpiSub(st, CM, CB, REF, ETF, VAL, F);
document.getElementById('kpis').innerHTML = H.kpi.map((k,i)=>`<div class="kpi"><div class="k">${k}</div><div class="v">${kv[i]}</div><div class="s">${ks[i]}</div></div>`).join('');
document.getElementById('cost-fut').textContent = pct(D.attribution[REF].annual_costs,2);

// ---------- tables
const isText = c => typeof c==='string' && /^[A-Za-zÀ-ÿ<]/.test(c) && !/^<(span|b)[ >]/.test(c) && c!==H.notTraded;
function table(id, head, rows, hl){
  const el = document.getElementById(id);
  el.innerHTML = `<thead><tr>${head.map((h,i)=>`<th${i===0?' class="l"':''}>${h}</th>`).join('')}</tr></thead><tbody>${rows.map(r=>`<tr${hl&&hl(r)?' class="hl"':''}>${r.cells.map((c,i)=>`<td${i===0||isText(c)?' class="l"':''}>${c}</td>`).join('')}</tr>`).join('')}</tbody>`;
}
function tabs(target, opts, render){
  const g = document.querySelector(`.tabs[data-target="${target}"]`);
  g.innerHTML = opts.map((o,i)=>`<button type="button" aria-pressed="${i===0}" data-v="${o[0]}">${o[1]}</button>`).join('');
  g.addEventListener('click', e=>{ const b=e.target.closest('button'); if(!b) return;
    g.querySelectorAll('button').forEach(x=>x.setAttribute('aria-pressed', x===b)); render(b.dataset.v); });
  render(opts[0][0]);
}
const PER = T.periods;

table('t-universe', H.universe, D.universe.map(u=>({cells:[lab(u.ticker,u.label), `<code>${u.ticker}</code>`, cls(u.asset_class), fmtDate(u.start), u.n_points.toLocaleString(T.locale)]})));

const EX = D.worked_example;
const sg = v => v==null?'–':(v>0?'+1':'−1');
const frac = v => v==null?'–':({'1':'+1','-1':'−1','0.333333':'+⅓','-0.333333':'−⅓'})[String(Math.round(v*1e6)/1e6)] || nf(v,2);
table('t-example', H.example, Object.entries(EX.markets).map(([t,m])=>({cells:[lab(t,m.label), sg(m.s3), sg(m.s6), sg(m.s12), frac(m.signal), pct(m.vol,1), nf(m.raw_weight,3), spct(m.final_weight,1)]})));
document.getElementById('example-cap').innerHTML = H.exampleCap(EX, F);

const SER = ['TSMOM 3m','TSMOM 6m','TSMOM 12m',REF,ETF,VAL,WLD];
tabs('stats', PER, p=>{
  table('t-stats', H.stats, SER.map(k=>{const s=st[p][k]; return {k, cells:[short(k), spct(s.annual_return), pct(s.volatility), `<b>${nf(s.sharpe)}</b>`, `[${nf(s.sharpe_ci95_low)} ; ${nf(s.sharpe_ci95_high)}]`, nf(s.sortino), spct(s.max_drawdown,1), nf(s.calmar), pct(s.pct_positive_months,0), nf(s.monthly_skew)]};}), r=>r.k===REF);
});

const A = D.annual, AK = [REF, ETF, VAL, WLD, '70/30 value/trend', '70/30 value/ETF'];
table('t-annual', [H.year, ...AK.map(short)], A.years.map((y,i)=>({cells:[y, ...AK.map(k=>spct(A.series[k][i]))]})));

const AT = D.attribution[REF];
table('t-classes', H.classes, Object.entries(AT.classes).map(([c,v])=>({cells:[cls(c), spct(v.annual_contribution,2), nf(v.sharpe), spct(v.annual_contribution_validation,2)]})));
table('t-markets', H.markets, Object.entries(AT.markets).map(([t,m])=>({cells:[lab(t,m.label), cls(m.asset_class), pct(m.avg_abs_weight,1), pct(m.pct_time_long,0), pct(m.pct_time_short,0), spct(m.annual_contribution,2), nf(m.contribution_sharpe)]})));
const SC = D.cost_sensitivity;
table('t-costs', H.costs, ['x0','x1','x2','x3'].map((k,i)=>({k, cells:[H.costRows[i], nf(SC[k].full), nf(SC[k].design), nf(SC[k].validation)]})), r=>r.k==='x1');

const CK = [REF,'TSMOM 12m',ETF,VAL,WLD];
tabs('corr', PER, p=>{ const C = CM[p];
  table('t-corr', ['', ...CK.map(short)], CK.map(a=>({cells:[short(a), ...CK.map(b=>a===b?'1':nf(C[a][b]))]})));
});
const CO = D.conditional;
const condKeys = [['beta_vs_value',x=>nf(x)],['avg_ret_value_worst_10pct',spct],['avg_ret_value_best_10pct',spct],['avg_ret_value_down',spct],['avg_ret_value_up',spct],['corr_value_down',x=>nf(x)],['corr_value_up',x=>nf(x)]];
const condLabels = H.condRows(pct(CO[REF].value_avg_worst_10pct));
table('t-cond', [H.cond[0], short(REF), short(ETF)], condKeys.map(([k,f],i)=>({cells:[condLabels[i], f(CO[REF][k],2), f(CO[ETF][k],2)]})));
const CR = D.crises, CRK = [REF, ETF, VAL, WLD];
table('t-crises', [...H.crises, ...CRK.map(short)], Object.entries(CR).map(([c,v])=>({cells:[T.crises[c]||c, v.period.split(' → ').map(fmtDate).join(' → '), ...CRK.map(k=>spct(v[k]))]})));

tabs('combo', [[REF,T.versions[0]],[ETF,T.versions[1]]], k=>{
  table('t-combo', H.combo, CB[k].map(r=>({w:r.value_weight, cells:[`${Math.round(r.value_weight*100)}${T.pctSep}% / ${Math.round((1-r.value_weight)*100)}${T.pctSep}%`, nf(r.full.sharpe), spct(r.full.annual_return), pct(r.full.volatility), spct(r.full.max_drawdown,0), nf(r.validation.sharpe), spct(r.validation.max_drawdown,0)]})), r=>Math.abs(r.w-0.7)<1e-9);
});

table('t-contracts', H.contracts, Object.entries(D.contracts.markets).map(([t,c])=>({cells:[lab(t,c.label), T.contracts[t]||c.contract, eur(c.notional_eur), eur(c.target_position_eur), `× ${nf(c.ratio,1)}`]})));

const EK = [REF, ETF, VAL];
table('t-etf', H.etf, PER.flatMap(([p,l])=>EK.map(k=>({k, cells:[l, short(k), nf(st[p][k].sharpe), spct(st[p][k].annual_return), pct(st[p][k].volatility), spct(st[p][k].max_drawdown,0), k===VAL?'1':nf(CM[p][k][VAL])]}))), r=>r.k===ETF);

const PF = D.latest_positions[REF].positions, PE = D.latest_positions[ETF].positions, cap = D.contracts.capital;
table('t-pos', H.pos, Object.keys(PF).map(t=>{const f=PF[t], e=PE[t]; return {cells:[lab(t,f.label), cls(f.asset_class), frac(f.signal), spct(f.weight,1), eur(f.weight*cap), e?pct(e.weight,1):H.notTraded, e?eur(e.weight*cap):'–']};}));

// ---------- SVG charts
const NS='http://www.w3.org/2000/svg';
function el(tag, attrs, parent){ const e=document.createElementNS(NS,tag); for(const k in attrs) e.setAttribute(k,attrs[k]); if(parent) parent.appendChild(e); return e; }
function legend(id, series){ document.getElementById(id).innerHTML = series.map(s=>`<span><i style="background:${s.dash?'repeating-linear-gradient(90deg,'+css(s.c)+' 0 4px,transparent 4px 7px)':css(s.c)}"></i>${s.name}</span>`).join(''); }
function niceTicks(lo, hi, n){ const span=hi-lo, step0=span/n, mag=Math.pow(10,Math.floor(Math.log10(step0))); const err=step0/mag; const step=(err>=7.5?10:err>=3.5?5:err>=1.5?2:1)*mag; const t=[]; for(let v=Math.ceil(lo/step)*step; v<=hi+1e-12; v+=step) t.push(+v.toFixed(10)); return t; }

function lineChart(id, opt){
  const host=document.getElementById(id); host.innerHTML='';
  const W=Math.max(320, host.clientWidth||720), Hh0=opt.h||300, m={l:52,r:14,t:10,b:28};
  const svg=el('svg',{viewBox:`0 0 ${W} ${Hh0}`,role:'img','aria-label':opt.label||''},host);
  const X=opt.x, n=X.length, S=opt.series;
  const vals=S.flatMap(s=>s.v.filter(v=>v!=null&&isFinite(v)));
  let lo=Math.min(...vals), hi=Math.max(...vals);
  if(opt.zero){lo=Math.min(lo,0);hi=Math.max(hi,0);}
  const log=!!opt.log; const f=v=>log?Math.log10(v):v;
  let L=f(lo), U=f(hi); const pad=(U-L)*0.05; L-=pad; U+=pad;
  const xs=i=>m.l+(W-m.l-m.r)*(opt.xNum? (X[i]-X[0])/(X[n-1]-X[0]) : i/(n-1));
  const ys=v=>m.t+(Hh0-m.t-m.b)*(1-(f(v)-L)/(U-L));
  const g=el('g',{},svg);
  const ticks = log ? [10,20,50,100,200,500,1000,2000,5000].filter(t=>t>=lo*0.9&&t<=hi*1.1) : niceTicks(lo,hi,5);
  ticks.forEach(t=>{ const y=ys(t); el('line',{x1:m.l,x2:W-m.r,y1:y,y2:y,stroke:css('--grid'),'stroke-width':1},g);
    const tx=el('text',{x:m.l-8,y:y+4,'text-anchor':'end'},g); tx.textContent=opt.yFmt?opt.yFmt(t):t; });
  if(opt.zero&&!log){ const y=ys(0); el('line',{x1:m.l,x2:W-m.r,y1:y,y2:y,stroke:css('--axis'),'stroke-width':1},g); }
  if(opt.xNum){ X.forEach((x,i)=>{ if(i%2) return; const t=el('text',{x:xs(i),y:Hh0-8,'text-anchor':'middle'},g); t.textContent=opt.xFmt?opt.xFmt(x):x; }); }
  else { let last=-1; X.forEach((d,i)=>{ const y=+d.slice(0,4); if(d.slice(5,7)==='01'&&y%(W<560?5:3)===0&&y!==last){ last=y; const xx=xs(i); el('line',{x1:xx,x2:xx,y1:Hh0-m.b,y2:Hh0-m.b+4,stroke:css('--axis')},g); const t=el('text',{x:xx,y:Hh0-8,'text-anchor':'middle'},g); t.textContent=y; } }); }
  el('line',{x1:m.l,x2:W-m.r,y1:Hh0-m.b,y2:Hh0-m.b,stroke:css('--axis')},g);
  S.forEach(s=>{ let d='', pen=false; s.v.forEach((v,i)=>{ if(v==null||!isFinite(v)){pen=false;return;} d+=(pen?'L':'M')+xs(i).toFixed(1)+' '+ys(v).toFixed(1); pen=true; });
    el('path',{d,fill:'none',stroke:css(s.c),'stroke-width':2,'stroke-linejoin':'round','stroke-linecap':'round','stroke-dasharray':s.dash?'5 4':'none'},svg);
    if(opt.dots) s.v.forEach((v,i)=>{ if(v!=null) el('circle',{cx:xs(i),cy:ys(v),r:3.5,fill:css(s.c),stroke:css('--surface'),'stroke-width':2},svg); });
  });
  const tip=document.createElement('div'); tip.className='tip'; tip.hidden=true; host.appendChild(tip);
  const cross=el('line',{y1:m.t,y2:Hh0-m.b,stroke:css('--axis'),'stroke-dasharray':'3 3',visibility:'hidden'},svg);
  const dots=S.map(s=>el('circle',{r:4.5,fill:css(s.c),stroke:css('--surface'),'stroke-width':2,visibility:'hidden'},svg));
  const ov=el('rect',{x:m.l,y:m.t,width:W-m.l-m.r,height:Hh0-m.t-m.b,fill:'transparent'},svg);
  function move(ev){ const r=svg.getBoundingClientRect(); const px=(ev.clientX-r.left)*W/r.width;
    let i; if(opt.xNum){ i=0; let best=1e9; X.forEach((x,j)=>{const dd=Math.abs(xs(j)-px); if(dd<best){best=dd;i=j;}}); } else i=Math.round((px-m.l)/(W-m.l-m.r)*(n-1));
    i=Math.max(0,Math.min(n-1,i)); const xx=xs(i);
    cross.setAttribute('x1',xx); cross.setAttribute('x2',xx); cross.setAttribute('visibility','visible');
    S.forEach((s,k)=>{ const v=s.v[i]; if(v==null){dots[k].setAttribute('visibility','hidden');return;} dots[k].setAttribute('cx',xx); dots[k].setAttribute('cy',ys(v)); dots[k].setAttribute('visibility','visible'); });
    tip.innerHTML=`<div class="d">${opt.xNum?(opt.xFmt?opt.xFmt(X[i]):X[i]):fmtDate(X[i])}</div>`+S.map(s=>`<div class="r"><span>${s.name}</span><b>${s.v[i]==null?'–':(opt.tFmt||opt.yFmt||(v=>nf(v)))(s.v[i])}</b></div>`).join('');
    tip.hidden=false; const hw=host.clientWidth, tx=(xx/W)*hw; tip.style.left=(tx>hw*0.6? tx-tip.offsetWidth-12 : tx+12)+'px'; tip.style.top='8px'; }
  ov.addEventListener('pointermove',move); ov.addEventListener('pointerdown',move);
  ov.addEventListener('pointerleave',()=>{tip.hidden=true;cross.setAttribute('visibility','hidden');dots.forEach(d=>d.setAttribute('visibility','hidden'));});
}

function barChart(id, opt){
  const host=document.getElementById(id); host.innerHTML='';
  const W=Math.max(320, host.clientWidth||720), cats=opt.cats, S=opt.series;
  if(opt.horizontal){
    const rowH=22, m={l:Math.min(150,W*0.34),r:48,t:6,b:24}, Hh0=m.t+m.b+cats.length*rowH;
    const svg=el('svg',{viewBox:`0 0 ${W} ${Hh0}`,role:'img','aria-label':opt.label||''},host);
    const vals=S[0].v; const mx=Math.max(...vals.map(Math.abs))*1.05;
    const xs=v=>m.l+(W-m.l-m.r)*(v+mx)/(2*mx);
    niceTicks(-mx,mx,4).forEach(t=>{ const x=xs(t); el('line',{x1:x,x2:x,y1:m.t,y2:Hh0-m.b,stroke:css('--grid')},svg); const tx=el('text',{x,y:Hh0-6,'text-anchor':'middle'},svg); tx.textContent=pct(t,0); });
    el('line',{x1:xs(0),x2:xs(0),y1:m.t,y2:Hh0-m.b,stroke:css('--axis')},svg);
    cats.forEach((c,i)=>{ const v=vals[i], y=m.t+i*rowH+4, h=rowH-8; const x0=xs(0), x1=xs(v);
      el('rect',{x:Math.min(x0,x1),y,width:Math.max(1,Math.abs(x1-x0)),height:h,rx:2,fill:css(v>=0?'--s1':'--neg')},svg);
      const t=el('text',{x:m.l-8,y:y+h-2,'text-anchor':'end'},svg); t.textContent=c; t.style.fill=css('--fg2');
      const lv=el('text',{x:v>=0?x1+4:x1-4,y:y+h-2,'text-anchor':v>=0?'start':'end'},svg); lv.textContent=pct(v,1); });
    return;
  }
  const Hh0=opt.h||280, m={l:52,r:10,t:10,b:30};
  const svg=el('svg',{viewBox:`0 0 ${W} ${Hh0}`,role:'img','aria-label':opt.label||''},host);
  const vals=S.flatMap(s=>s.v); const lo=Math.min(0,...vals), hi=Math.max(0,...vals);
  const pad=(hi-lo)*0.08; const L=lo-(lo<0?pad:0), U=hi+pad;
  const ys=v=>m.t+(Hh0-m.t-m.b)*(1-(v-L)/(U-L));
  niceTicks(L,U,5).forEach(t=>{ const y=ys(t); el('line',{x1:m.l,x2:W-m.r,y1:y,y2:y,stroke:css('--grid')},svg); const tx=el('text',{x:m.l-8,y:y+4,'text-anchor':'end'},svg); tx.textContent=pct(t,0); });
  el('line',{x1:m.l,x2:W-m.r,y1:ys(0),y2:ys(0),stroke:css('--axis')},svg);
  const gw=(W-m.l-m.r)/cats.length, bw=Math.min(22,(gw-10)/S.length-2);
  const tip=document.createElement('div'); tip.className='tip'; tip.hidden=true; host.appendChild(tip);
  cats.forEach((c,i)=>{ const gx=m.l+i*gw+(gw-(bw+2)*S.length)/2;
    S.forEach((s,k)=>{ const v=s.v[i], x=gx+k*(bw+2), y0=ys(0), y1=ys(v);
      const r=el('rect',{x,y:Math.min(y0,y1),width:bw,height:Math.max(1,Math.abs(y1-y0)),rx:2,fill:css(s.c)},svg);
      r.addEventListener('pointerenter',()=>{ tip.innerHTML=`<div class="d">${c}</div><div class="r"><span>${s.name}</span><b>${pct(v,1)}</b></div>`; tip.hidden=false; const hw=host.clientWidth; const tx=(x/W)*hw; tip.style.left=Math.min(hw-170,Math.max(0,tx))+'px'; tip.style.top='6px'; });
      r.addEventListener('pointerleave',()=>tip.hidden=true); });
    const tx=el('text',{x:m.l+i*gw+gw/2,y:Hh0-m.b+16,'text-anchor':'middle'},svg); tx.textContent=c; });
}

function drawAll(){
  const N=D.nav;
  const s1=[{name:short(REF),c:'--s1',v:N.series[REF]},{name:short(VAL),c:'--s2',v:N.series[VAL]},{name:short(ETF),c:'--s3',v:N.series[ETF]},{name:short(WLD),c:'--s4',v:N.series[WLD],dash:true}];
  legend('lg-nav',s1); lineChart('c-nav',{x:N.dates,series:s1,log:true,h:320,yFmt:v=>Math.round(v),tFmt:v=>nf(v,1),label:'NAV'});
  const Dd=D.drawdown; const s2=[{name:short(REF),c:'--s1',v:Dd.series[REF]},{name:short(VAL),c:'--s2',v:Dd.series[VAL]},{name:short(ETF),c:'--s3',v:Dd.series[ETF]}];
  legend('lg-dd',s2); lineChart('c-dd',{x:Dd.dates,series:s2,zero:true,h:260,yFmt:v=>pct(v,0),tFmt:v=>pct(v,1),label:'Drawdown'});
  const G=D.rolling_36m;
  const s3=[{name:short(REF),c:'--s1',v:G.sharpe[REF]},{name:short(VAL),c:'--s2',v:G.sharpe[VAL]},{name:short(ETF),c:'--s3',v:G.sharpe[ETF]}];
  legend('lg-rsr',s3); lineChart('c-rsr',{x:G.dates,series:s3,zero:true,h:260,yFmt:v=>nf(v,1),tFmt:v=>nf(v,2),label:'Rolling Sharpe'});
  const s4=[{name:short(REF),c:'--s1',v:G.correlation[REF]},{name:short(ETF),c:'--s3',v:G.correlation[ETF]}];
  legend('lg-rc',s4); lineChart('c-rc',{x:G.dates,series:s4,zero:true,h:240,yFmt:v=>nf(v,1),tFmt:v=>nf(v,2),label:'Rolling correlation'});
  const crs=Object.keys(D.crises); const s5=[{name:short(REF),c:'--s1',v:crs.map(c=>D.crises[c][REF])},{name:short(ETF),c:'--s3',v:crs.map(c=>D.crises[c][ETF])},{name:short(VAL),c:'--s2',v:crs.map(c=>D.crises[c][VAL])}];
  legend('lg-cr',s5); barChart('c-cr',{cats:crs.map(c=>T.crisisShort[c]||c),series:s5,h:280,label:'Crises'});
  const wv=CB[REF].map(r=>r.value_weight*100), Lb=H.lines;
  const s6=[{name:`${H.futures}, ${Lb[0]}`,c:'--s1',v:CB[REF].map(r=>r.full.sharpe)},{name:`${H.futures}, ${Lb[1]}`,c:'--s1',dash:true,v:CB[REF].map(r=>r.validation.sharpe)},{name:`${H.etfShort}, ${Lb[0]}`,c:'--s3',v:CB[ETF].map(r=>r.full.sharpe)},{name:`${H.etfShort}, ${Lb[1]}`,c:'--s3',dash:true,v:CB[ETF].map(r=>r.validation.sharpe)}];
  legend('lg-fs',s6); lineChart('c-fs',{x:wv,xNum:true,xFmt:v=>v+T.pctSep+'%',series:s6,h:240,dots:true,yFmt:v=>nf(v,1),tFmt:v=>nf(v,2),label:'Sharpe'});
  const s7=[{name:`${H.futures}, ${Lb[0]}`,c:'--s1',v:CB[REF].map(r=>r.full.max_drawdown)},{name:`${H.futures}, ${Lb[1]}`,c:'--s1',dash:true,v:CB[REF].map(r=>r.validation.max_drawdown)},{name:`${H.etfShort}, ${Lb[0]}`,c:'--s3',v:CB[ETF].map(r=>r.full.max_drawdown)},{name:`${H.etfShort}, ${Lb[1]}`,c:'--s3',dash:true,v:CB[ETF].map(r=>r.validation.max_drawdown)}];
  legend('lg-fd',s7); lineChart('c-fd',{x:wv,xNum:true,xFmt:v=>v+T.pctSep+'%',series:s7,h:240,dots:true,yFmt:v=>pct(v,0),tFmt:v=>pct(v,1),label:'Max drawdown'});
  const s8=[{name:short(VAL),c:'--s2',v:N.series[VAL]},{name:short('70/30 value/trend'),c:'--s1',v:N.series['70/30 value/trend']},{name:short('70/30 value/ETF'),c:'--s3',v:N.series['70/30 value/ETF']}];
  legend('lg-cmb',s8); lineChart('c-cmb',{x:N.dates,series:s8,log:true,h:280,yFmt:v=>Math.round(v),tFmt:v=>nf(v,1),label:'Combinations'});
  const P=Object.entries(D.latest_positions[REF].positions);
  barChart('c-pos',{horizontal:true,cats:P.map(([t,p])=>lab(t,p.label)),series:[{v:P.map(([t,p])=>p.weight)}],label:'Positions'});
}
drawAll();
let rt; window.addEventListener('resize',()=>{clearTimeout(rt); rt=setTimeout(drawAll,150);});
if(window.matchMedia){ const mq=matchMedia('(prefers-color-scheme: dark)'); if(mq.addEventListener) mq.addEventListener('change',drawAll); }
new MutationObserver(drawAll).observe(document.documentElement,{attributes:true,attributeFilter:['data-theme']});
})();

// ---------- navigation: active section in the contents, previous / next buttons, back to top
(function(){
  const H2 = T.h;
  const secs = [...document.querySelectorAll('main section[id]')];
  const links = new Map([...document.querySelectorAll('nav.toc a[href^="#"]')].map(a=>[a.getAttribute('href').slice(1), a]));
  const title = s => { const h=s.querySelector('h2'); if(!h) return s.id; const c=h.cloneNode(true); const n=c.querySelector('.n'); if(n) n.remove(); return c.textContent.trim(); };
  secs.forEach((s,i)=>{
    const nav=document.createElement('div'); nav.className='secnav';
    if(i>0) nav.insertAdjacentHTML('beforeend', `<a class="prev" href="#${secs[i-1].id}"><small>← ${H2.prev}</small>${title(secs[i-1])}</a>`);
    if(i<secs.length-1) nav.insertAdjacentHTML('beforeend', `<a class="next" href="#${secs[i+1].id}"><small>${H2.next} →</small>${title(secs[i+1])}</a>`);
    s.appendChild(nav);
  });
  const top=document.createElement('a'); top.className='totop'; top.href='#top'; top.setAttribute('aria-label',H2.top); top.title=H2.top; top.textContent='↑'; top.hidden=true;
  document.body.appendChild(top);
  window.addEventListener('scroll',()=>{ top.hidden = window.scrollY < 700; },{passive:true});
  if('IntersectionObserver' in window){
    let current=null;
    const io=new IntersectionObserver(entries=>{
      entries.forEach(e=>{ if(e.isIntersecting){ current=e.target.id; } });
      links.forEach((a,id)=>a.classList.toggle('active', id===current));
    },{rootMargin:'-80px 0px -70% 0px'});
    secs.forEach(s=>io.observe(s));
  }
})();
