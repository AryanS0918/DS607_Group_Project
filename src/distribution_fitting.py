from pathlib import Path
import numpy as np, pandas as pd
from scipy import stats, optimize
import matplotlib.pyplot as plt
from .config import SEED, B_PARAM
ROOT=Path(__file__).resolve().parents[1]; FIG=ROOT/'outputs/figures'; TAB=ROOT/'outputs/tables'

def load_returns(): return pd.read_csv(ROOT/'data/processed/bank_log_returns.csv', index_col=0, parse_dates=True)
def norm_mle(x):
    mu=x.mean(); sig=np.sqrt(np.mean((x-mu)**2)); ll=np.sum(stats.norm.logpdf(x,mu,sig)) if sig>0 else -np.inf
    return mu,sig,ll
def t_mle(x):
    x=np.asarray(x)
    x=x[np.isfinite(x)]
    mu0,s0,_=norm_mle(x)
    def nll(th):
        mu,sq,nu=th[0],th[1],th[2]
        if sq<=0 or nu<=2.0001: return 1e100
        return -np.sum(stats.t.logpdf(x,nu,mu,sq))
    # scipy fit as starting point, bounded free optimization
    try:
        nu,s_fit_mu,s_fit=stats.t.fit(x,floc=mu0)
        mu=mu0
        s=s_fit
    except Exception:
        mu, s, nu = mu0, max(np.std(x,ddof=1)*np.sqrt(2/4), 1e-8), 4.0
    # ensure scale
    res=optimize.minimize(nll,[mu,s,nu],method='Nelder-Mead',options={'maxiter':3000,'xatol':1e-8,'fatol':1e-8})
    mu,s,nu=res.x
    if not np.all(np.isfinite([mu,s,nu])) or s<=0 or nu<=2.0001:
        nu, fit_loc, fit_scale=stats.t.fit(x,floc=mu)
        mu, s = fit_loc, fit_scale
    ll=np.sum(stats.t.logpdf(x,nu,mu,s))
    return mu,s,nu,ll

def step7():
    r=load_returns(); rows=[]
    for b,xs in r.items():
        x=xs.to_numpy(); mu=x.mean(); s=x.std(ddof=1); k=np.mean(((x-mu)/s)**4)-3
        nu_mm=4+6/k if k>0 else np.nan
        s_mm=s*np.sqrt((nu_mm-2)/nu_mm) if np.isfinite(nu_mm) else np.nan
        mu_ml,s_ml,nu_ml,ll=t_mle(x)
        rows.append({'Bank':b,'Normal MM mu':mu,'Normal MM sigma':s,'Student-t MM mu':mu,'Student-t MM scale':s_mm,'Student-t MM nu':nu_mm,
                    'Student-t MLE mu':mu_ml,'Student-t MLE scale':s_ml,'Student-t MLE nu':nu_ml})
    pd.DataFrame(rows).to_csv(TAB/'step7_mm_vs_mle_fits.csv',index=False)
    return pd.DataFrame(rows)

def step8():
    r=load_returns(); rng=np.random.default_rng(SEED); rows=[]
    for b,xs in r.items():
        x=xs.to_numpy(); n=len(x); mn,sn,lln=norm_mle(x); mt,st,nt,ll=t_mle(x); lob=2*(ll-lln)
        lrt_stats=[]; ks_norm_null=[]; ks_t_null=[]
        for _ in range(B_PARAM):
            xb=rng.normal(mn,sn,n); lrt_stats.append(max(0,2*(t_mle(xb)[3]-norm_mle(xb)[2])))
            xn=rng.normal(mn,sn,n); mn_b,sn_b,_=norm_mle(xn); ks_norm_null.append(stats.kstest(xn, lambda z: stats.norm.cdf(z, mn_b, sn_b)).statistic)
            xt=stats.t.rvs(nt,mt,st,size=n,random_state=rng); mt_b,st_b,nt_b,_=t_mle(xt); ks_t_null.append(stats.kstest(xt, lambda z, nt=nt_b, mt=mt_b, st=st_b: stats.t.cdf(z, nt, mt, st)).statistic)
        # observed parametric D with estimated parameters
        dn=stats.kstest(x, lambda z: stats.norm.cdf(z, mn, sn)).statistic; dt=stats.kstest(x, lambda z: stats.t.cdf(z, nt, mt, st)).statistic
        rows.append({'Bank':b,'LRT_Lambda':lob,'LRT_parametric_bootstrap_p':(1+sum(v>=lob for v in lrt_stats))/(B_PARAM+1),
                     'Normal KS D':dn,'Normal KS bootstrap p':(1+sum(v>=dn for v in ks_norm_null))/(B_PARAM+1),
                     'Student-t KS D':dt,'Student-t KS bootstrap p':(1+sum(v>=dt for v in ks_t_null))/(B_PARAM+1)})
        negative = np.sort(x[x < 0])
        empirical_tail = np.arange(1, len(negative) + 1) / n
        fig, axs = plt.subplots(1, 3, figsize=(14, 4))
        stats.probplot(x, dist='norm', sparams=(mn, sn), plot=axs[0])
        axs[0].set_title(f'{b}: Normal Q-Q')
        stats.probplot(x, dist='t', sparams=(nt, mt, st), plot=axs[1])
        axs[1].set_title(f'{b}: Student-t Q-Q')
        axs[2].plot(negative, empirical_tail, lw=1.5, label='Negative-return ECDF')
        axs[2].plot(negative, stats.norm.cdf(negative, mn, sn), lw=1.5, label='Fitted Normal CDF')
        axs[2].plot(negative, stats.t.cdf(negative, nt, mt, st), lw=1.5, label='Fitted Student-t CDF')
        axs[2].set_yscale('log')
        axs[2].set_xlabel('Negative log return')
        axs[2].set_ylabel('Probability (log scale)')
        axs[2].set_title(f'{b}: lower-tail empirical vs fitted CDF')
        axs[2].legend(fontsize='small')
        fig.tight_layout()
        fig.savefig(FIG / f'step8_normal_vs_t_qq_ecdf_{b}.png', dpi=300)
        plt.close(fig)
    pd.DataFrame(rows).to_csv(TAB/'step8_lrt_and_ks_tests.csv',index=False)
    fig,axs=plt.subplots(3,3,figsize=(15,12));
    for i,(b,xs) in enumerate(r.items()):
        x=xs.to_numpy(); mn,sn,_=norm_mle(x); mt,st,nt,_=t_mle(x); n=len(x)
        stats.probplot(x,dist='norm',sparams=(mn,sn),plot=axs[i,0]); axs[i,0].set_title(f'{b} Normal Q-Q')
        stats.probplot(x,dist='t',sparams=(nt,mt,st),plot=axs[i,1]); axs[i,1].set_title(f'{b} Student-t Q-Q')
        negative=np.sort(x[x < 0])
        empirical_tail=np.arange(1,len(negative)+1)/n
        axs[i,2].plot(negative,empirical_tail,lw=1,label='Empirical negative-tail ECDF')
        axs[i,2].plot(negative,stats.norm.cdf(negative,mn,sn),label='Fitted Normal')
        axs[i,2].plot(negative,stats.t.cdf(negative,nt,mt,st),label='Fitted Student-t')
        axs[i,2].set_yscale('log'); axs[i,2].legend(); axs[i,2].set_title(f'{b} lower-tail log-CDF')
    fig.tight_layout(); fig.savefig(FIG/'step8_normal_vs_t_qq_ecdf.png',dpi=300); plt.close(fig)
    return pd.DataFrame(rows)
