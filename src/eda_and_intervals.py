from pathlib import Path
import numpy as np, pandas as pd
from scipy import stats
import matplotlib.pyplot as plt
import seaborn as sns
from .config import ANNUALISATION, SEED, B_BOOT, CALM_WINDOW, COVID_WINDOW, RATE_HIKE_WINDOW
ROOT=Path(__file__).resolve().parents[1]; FIG=ROOT/'outputs/figures'; TAB=ROOT/'outputs/tables'
FIG.mkdir(parents=True,exist_ok=True); TAB.mkdir(parents=True,exist_ok=True)
sns.set_theme(style='whitegrid')

def load_returns(): return pd.read_csv(ROOT/'data/processed/bank_log_returns.csv', index_col=0, parse_dates=True)

def step4():
    r=load_returns(); rows=[]
    for b in r:
        x=r[b].dropna()
        rows.append({'Bank':b,'N':len(x),'Mean':x.mean(),'Standard Deviation':x.std(ddof=1),
                     'Annualised Volatility':x.std(ddof=1)*np.sqrt(ANNUALISATION),'Skewness':stats.skew(x,bias=False),
                     'Excess Kurtosis':stats.kurtosis(x,fisher=True,bias=False),'Minimum':x.min(),'Q01':x.quantile(.01),
                     '10% Quantile':x.quantile(.10),'Maximum':x.max()})
    pd.DataFrame(rows).to_csv(TAB/'step4_summary_statistics.csv',index=False)
    fig,axs=plt.subplots(3,1,figsize=(12,10),sharex=True)
    for ax,b in zip(axs,r.columns):
        ax.plot(r.index,r[b],lw=.55,label=b)
        ax.axvspan(pd.Timestamp(COVID_WINDOW[0]),pd.Timestamp(COVID_WINDOW[1]),color='red',alpha=.15,label='COVID-19 shock')
        ax.axvspan(pd.Timestamp(RATE_HIKE_WINDOW[0]),pd.Timestamp(RATE_HIKE_WINDOW[1]),color='orange',alpha=.12,label='Rate-hike regime')
        ax.set_ylabel('Log return'); ax.legend(loc='upper right')
    axs[-1].set_xlabel('Date'); fig.tight_layout(); fig.savefig(FIG/'step4_return_series_regimes.png',dpi=300); plt.close(fig)
    fig,axs=plt.subplots(1,3,figsize=(15,4))
    xs=np.linspace(-.12,.12,500)
    for ax,b in zip(axs.ravel(),r.columns):
        x=r[b]; sns.histplot(x,ax=ax,stat='density',bins=70,color='steelblue',alpha=.45); sns.kdeplot(x,ax=ax,color='black',lw=1.5,label='KDE')
        ax.plot(xs,stats.norm.pdf(xs,x.mean(),x.std(ddof=1)),color='red',lw=1.8,label='Normal'); ax.set_title(b); ax.legend()
    fig.tight_layout(); fig.savefig(FIG/'step4_hist_kde_normal.png',dpi=300); plt.close(fig)
    fig,axs=plt.subplots(3,2,figsize=(10,10)); xx=np.linspace(0,1,1000)
    for i,b in enumerate(r.columns):
        x=r[b].sort_values().values; mu=x.mean(); sig=x.std(ddof=1)
        ax=axs[i,0]; ecdf=np.arange(1,len(x)+1)/len(x); ax.plot(x,ecdf,lw=1,label='ECDF'); ax.plot(x,stats.norm.cdf(x,mu,sig),'r--',label='Normal CDF'); ax.set_title(f'{b} ECDF'); ax.legend()
        stats.probplot(x,dist='norm',plot=axs[i,1]); axs[i,1].set_title(f'{b} Normal Q-Q'); axs[i,1].get_lines()[1].set_color('red')
    fig.tight_layout(); fig.savefig(FIG/'step4_ecdf_and_qq.png',dpi=300); plt.close(fig)
    return pd.DataFrame(rows)

def step5():
    r=load_returns(); out=[]; z=stats.norm.ppf(.975)
    for b,x in r.items():
        x=x.dropna(); n=len(x); mean=x.mean(); s=x.std(ddof=1); se=s/np.sqrt(n); cm=mean-z*se; cp=mean+z*se
        w=mean/se; p=2*stats.norm.sf(abs(w)); vann=s*np.sqrt(ANNUALISATION); se_text=vann/np.sqrt(2*n); se_delta=vann*np.sqrt((stats.kurtosis(x,fisher=True,bias=False)+2)/(4*n))
        out.append({'Bank':b,'Mean':mean,'Mean_CLT_low':cm,'Mean_CLT_high':cp,'Wald_z':w,'Wald_p':p,
                    'Annualised Volatility':vann,'Normal_theory_low':vann-z*se_text,'Normal_theory_high':vann+z*se_text,
                    'Delta_method_low':vann-z*se_delta,'Delta_method_high':vann+z*se_delta,'Excess Kurtosis':stats.kurtosis(x,fisher=True,bias=False)})
    pd.DataFrame(out).to_csv(TAB/'step5_clt_intervals_wald.csv',index=False)
    return pd.DataFrame(out)

def step6():
    r=load_returns(); rng=np.random.default_rng(SEED); out=[]
    for b in r:
        x=r[b].to_numpy(); n=len(x); mu=x.mean(); se=x.std(ddof=1)/np.sqrt(n); z=stats.norm.ppf(.975)
        means=np.empty(B_BOOT); vols=np.empty(B_BOOT); q1=np.empty(B_BOOT)
        for i in range(B_BOOT):
            y=x[rng.integers(0,n,n)]; means[i]=y.mean(); vols[i]=y.std(ddof=1)*np.sqrt(ANNUALISATION); q1[i]=np.quantile(y,.01)
        q=lambda a:(np.quantile(a,.025),np.quantile(a,.975))
        m=q(means); v=q(vols); qci=q(q1); s=x.std(ddof=1); k=stats.kurtosis(x,fisher=True,bias=False)
        vann=s*np.sqrt(ANNUALISATION); se_delta=vann*np.sqrt((k+2)/(4*n)); se_norm=vann/np.sqrt(2*n)
        out.append({'Bank':b,'Mean_CLT_low':mu-z*se,'Mean_CLT_high':mu+z*se,'Mean_boot_low':m[0],'Mean_boot_high':m[1],
                    'Vol_normal_low':vann-z*se_norm,'Vol_normal_high':vann+z*se_norm,'Vol_delta_low':vann-z*se_delta,'Vol_delta_high':vann+z*se_delta,
                    'Vol_boot_low':v[0],'Vol_boot_high':v[1],'Q01_boot_low':qci[0],'Q01_boot_high':qci[1],'Q01_point':np.quantile(x,.01)})
    pd.DataFrame(out).to_csv(TAB/'step6_clt_vs_bootstrap_comparison.csv',index=False)
    # Student-t Monte Carlo coverage, nu=5 gives finite fourth moments.
    M = 1000
    B_MC = 1000
    rng = np.random.default_rng(SEED)
    n = 2750
    scale = 2
    nu_mc = 5
    true_vol = scale * np.sqrt(nu_mc / (nu_mc - 2)) * np.sqrt(ANNUALISATION)
    z = stats.norm.ppf(0.975)
    covered = {'Normal-theory CLT': 0, 'Delta-method CLT': 0, 'Efron Bootstrap': 0}
    for _ in range(M):
        y = stats.t.rvs(df=nu_mc, loc=0, scale=scale, size=n, random_state=rng)
        v = y.std(ddof=1) * np.sqrt(ANNUALISATION)
        excess_kurtosis = stats.kurtosis(y, fisher=True, bias=False)
        normal_se = v / np.sqrt(2 * n)
        delta_se = v * np.sqrt((excess_kurtosis + 2) / (4 * n))
        covered['Normal-theory CLT'] += v - z * normal_se <= true_vol <= v + z * normal_se
        covered['Delta-method CLT'] += v - z * delta_se <= true_vol <= v + z * delta_se
        idx = rng.integers(0, n, size=(B_MC, n))
        boot_vol = np.std(y[idx], axis=1, ddof=1) * np.sqrt(ANNUALISATION)
        boot_low, boot_high = np.percentile(boot_vol, [2.5, 97.5])
        covered['Efron Bootstrap'] += boot_low <= true_vol <= boot_high
    coverage = pd.DataFrame([
        {'Method': method, 'Coverage': hits / M}
        for method, hits in covered.items()
    ])
    coverage.to_csv(TAB/'step6_monte_carlo_coverage.csv', index=False)
    # interval plot
    d=pd.read_csv(TAB/'step6_clt_vs_bootstrap_comparison.csv'); fig,ax=plt.subplots(figsize=(11,5)); ypos=np.arange(len(d)*3)
    labels=[]; lows=[]; highs=[]; cols=[]
    for i,b in enumerate(d['Bank']):
        for name,lo,hi,c in [('Normal',d.loc[i,'Vol_normal_low'],d.loc[i,'Vol_normal_high'],'C0'),('Delta',d.loc[i,'Vol_delta_low'],d.loc[i,'Vol_delta_high'],'C1'),('Bootstrap',d.loc[i,'Vol_boot_low'],d.loc[i,'Vol_boot_high'],'C2')]:
            labels.append(f'{b} {name}'); lows.append(lo); highs.append(hi); cols.append(c)
    ypos=np.arange(len(labels)); ax.hlines(ypos,lows,highs,color=cols,lw=3); ax.scatter([(a+b)/2 for a,b in zip(lows,highs)],ypos,c=cols,s=25)
    ax.set_yticks(ypos,labels); ax.invert_yaxis(); ax.set_xlabel('Annualised volatility')
    from matplotlib.lines import Line2D
    ax.legend(handles=[Line2D([0],[0],color=c,lw=3,label=n) for n,c in [('Normal-Theory CLT','C0'),('Delta-Method CLT','C1'),('Efron Bootstrap','C2')]],title='Interval method',loc='best')
    fig.tight_layout(); fig.savefig(FIG/'step6_clt_vs_bootstrap_cis.png',dpi=300); plt.close(fig)
    return d
