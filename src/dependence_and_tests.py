from pathlib import Path
from itertools import combinations
import numpy as np, pandas as pd
from scipy import stats
import matplotlib.pyplot as plt
from .config import SEED, B_BOOT, B_PERM, ALPHA, CALM_WINDOW, COVID_WINDOW, RATE_HIKE_WINDOW, EXTREME_QUANTILE
ROOT=Path(__file__).resolve().parents[1]
FIG=ROOT/'outputs/figures'; TAB=ROOT/'outputs/tables'

def load_returns(): return pd.read_csv(ROOT/'data/processed/bank_log_returns.csv',index_col=0,parse_dates=True)

def step9():
    r=load_returns(); rng=np.random.default_rng(SEED); rows=[]; n=len(r)
    for a,b in combinations(r.columns,2):
        x=r[a].to_numpy(); y=r[b].to_numpy(); rho=stats.pearsonr(x,y).statistic; tau=stats.kendalltau(x,y).statistic
        rhos=[]; taus=[]
        for _ in range(B_BOOT):
            ids=rng.integers(0,n,n); rhos.append(stats.pearsonr(x[ids],y[ids]).statistic); taus.append(stats.kendalltau(x[ids],y[ids]).statistic)
        z = np.arctanh(rho)
        fisher_half_width = stats.norm.ppf(1 - ALPHA / 2) / np.sqrt(max(n - 3, 1))
        fisher_low = np.tanh(z - fisher_half_width)
        fisher_high = np.tanh(z + fisher_half_width)
        rows.append({'Pair':f'{a}-{b}','Pearson rho':rho,'Pearson low':np.quantile(rhos,.025),'Pearson high':np.quantile(rhos,.975),
                     'Pearson Fisher-z low':fisher_low,'Pearson Fisher-z high':fisher_high,
                     'Pearson Fisher-z width':fisher_high-fisher_low,
                     'Kendall tau':tau,'Kendall low':np.quantile(taus,.025),'Kendall high':np.quantile(taus,.975)})
    pd.DataFrame(rows).to_csv(TAB/'step9_pearson_vs_kendall.csv',index=False)
    d=pd.read_csv(TAB/'step9_pearson_vs_kendall.csv'); fig,ax=plt.subplots(figsize=(11,5)); yy=[]; labs=[]; ls=[]; hs=[]; cs=[]
    for i,row in d.iterrows():
        for key,lo,hi,c in [('Pearson (Bootstrap)','Pearson low','Pearson high','C0'),('Pearson (Fisher-z CLT)','Pearson Fisher-z low','Pearson Fisher-z high','C1'),("Kendall's tau (Bootstrap)",'Kendall low','Kendall high','C2')]:
            labs.append(row['Pair']+' '+key); ls.append(row[lo]); hs.append(row[hi]); cs.append(c)
    yy=np.arange(len(labs)); ax.hlines(yy,ls,hs,color=cs,lw=3); ax.scatter([(a+b)/2 for a,b in zip(ls,hs)],yy,c=cs)
    ax.set_yticks(yy,labs); ax.invert_yaxis(); ax.set_xlabel('Correlation')
    from matplotlib.lines import Line2D
    ax.legend(handles=[Line2D([0],[0],color=c,lw=3,label=n) for n,c in [('Pearson (Bootstrap)','C0'),('Pearson (Fisher-z CLT)','C1'),("Kendall's tau (Bootstrap)",'C2')]],title='Interval method',loc='best')
    fig.tight_layout(); fig.savefig(FIG/'step9_correlation_cis.png',dpi=300); plt.close(fig)
    return d

def perm_test(calm,stress,rng):
    obs=stress.std(ddof=1)/calm.std(ddof=1); pooled=np.r_[calm,stress]; n=len(calm); null=[]
    for _ in range(B_PERM):
        p=rng.permutation(pooled); null.append(p[n:].std(ddof=1)/p[:n].std(ddof=1))
    null=np.array(null)
    two=(1+np.sum(np.abs(np.log(null))>=abs(np.log(obs))))/(B_PERM+1)
    # One-sided direction is stress dispersion greater than calm dispersion.
    one=(1+np.sum(null>=obs))/(B_PERM+1)
    return obs,two,one,null

def step10():
    r=load_returns(); rng=np.random.default_rng(SEED); calm=r.loc[CALM_WINDOW[0]:CALM_WINDOW[1]]; cov=r.loc[COVID_WINDOW[0]:COVID_WINDOW[1]]; rate=r.loc[RATE_HIKE_WINDOW[0]:RATE_HIKE_WINDOW[1]]
    perms=[]; all_null={}
    for b in r:
        for comp,stress in [('Calm vs COVID',cov),('Calm vs Rate Hike',rate)]:
            c=calm[b].dropna(); s=stress[b].dropna(); tval,two,one,null=perm_test(c,s,rng)
            perms.append({'Bank':b,'Comparison':comp,'Calm N':len(c),'Stress N':len(s),'Observed ratio':tval,'Two-sided empirical p':two,'One-sided stress>calm p':one})
            all_null[f'{b}|{comp}']=null
    pd.DataFrame(perms).to_csv(TAB/'step10_permutation_tests.csv',index=False)
    fig,axs=plt.subplots(3,2,figsize=(12,10))
    for i,b in enumerate(r):
        for j,comp in enumerate(['Calm vs COVID','Calm vs Rate Hike']):
            null=all_null[f'{b}|{comp}']; obs=pd.DataFrame(perms).query("Bank == @b and Comparison == @comp")['Observed ratio'].iloc[0]
            axs[i,j].hist(null,bins=50,density=True,color='steelblue',alpha=.7,label='Permutation null')
            axs[i,j].axvline(obs,color='red',lw=2,label='Observed stress/calm ratio')
            axs[i,j].axvline(1/obs,color='orange',ls='--',label='Reciprocal two-sided mirror')
            axs[i,j].set_title(f'{b}: {comp}')
            axs[i,j].set_xlabel('Permutation Ratio (s_stress / s_calm)')
            axs[i,j].set_ylabel('Density')
            axs[i,j].set_title(f'{b}: {comp}\nReciprocal mirror marks the two-sided threshold')
            axs[i,j].legend(loc='upper right',fontsize='small')
    fig.tight_layout(); fig.savefig(FIG/'step10_permutation_nulls.png',dpi=300); plt.close(fig)
    # chi-square extreme-day table
    q=r.quantile(EXTREME_QUANTILE); extreme=r.le(q); chis=[]
    for a,b in combinations(r.columns,2):
        tab=pd.crosstab(extreme[a],extreme[b])
        # orientation may omit false/true; force all four
        tab=tab.reindex(index=[False,True],columns=[False,True],fill_value=0)
        expected=stats.contingency.expected_freq(tab)
        chi,p,dof,_=stats.chi2_contingency(tab,correction=False)
        chis.append({'Pair':f'{a}-{b}','00':tab.iloc[0,0],'01':tab.iloc[0,1],'10':tab.iloc[1,0],'11':tab.iloc[1,1],
                     'Minimum expected count':expected.min(),'All expected >= 5':bool(expected.min()>=5),'Chi-square':chi,'p-value':p,'Degrees of freedom':dof})
    pd.DataFrame(chis).to_csv(TAB/'step10_chisq_extreme_days.csv',index=False)
    return pd.DataFrame(perms), pd.DataFrame(chis)

def step11():
    r=load_returns(); rng=np.random.default_rng(SEED); q=r.quantile(EXTREME_QUANTILE); ex=r.le(q); rows=[]
    for a,b in combinations(r.columns,2):
        n=int(ex[a].sum()); k=int((ex[a]&ex[b]).sum()); p=k/n; z=stats.norm.ppf(.975); se=np.sqrt(p*(1-p)/n)
        posts=[]
        for label,prior in [('Flat Beta(1,1)',(1,1)),('Skeptical Beta(2,18)',(2,18)),('Jeffreys Beta(.5,.5)',(.5,.5))]:
            aa=prior[0]+k; bb=prior[1]+n-k
            lo,hi=stats.beta.ppf([.025,.975],aa,bb)
            posts.append((label,lo,hi,aa,bb))
        inds=rng.choice(np.where(ex[a])[0],size=(B_BOOT,n),replace=True)
        vals=np.array([ex[b].iloc[ii].mean() for ii in inds])
        blo,bhi=np.quantile(vals,[.025,.975])
        flat=posts[0]
        rows.append({'Pair A':a,'Pair B':b,'n_extreme_A':n,'k_joint':k,'Observed proportion':p,
                     'Wald low':max(0,p-z*se),'Wald high':min(1,p+z*se),'Bootstrap low':blo,'Bootstrap high':bhi,
                     'Beta flat low':flat[1],'Beta flat high':flat[2],'Skeptical low':posts[1][1],'Skeptical high':posts[1][2],
                     'Jeffreys low':posts[2][1],'Jeffreys high':posts[2][2]})
    pd.DataFrame(rows).to_csv(TAB/'step11_bayesian_vs_frequentist_cis.csv',index=False)
    d=pd.read_csv(TAB/'step11_bayesian_vs_frequentist_cis.csv'); fig,ax=plt.subplots(figsize=(12,7)); labs=[]; low=[]; high=[]; cols=[]
    for i,row in d.iterrows():
        for off,name,l,h,c in [(0,'Wald','Wald low','Wald high','gray'),(1,'Bootstrap','Bootstrap low','Bootstrap high','C0'),(2,'Flat Beta','Beta flat low','Beta flat high','C1'),(3,'Skeptical Beta','Skeptical low','Skeptical high','C2'),(4,'Jeffreys Beta','Jeffreys low','Jeffreys high','C3')]:
            labs.append(f"{row['Pair A']}->{row['Pair B']} {name}"); low.append(row[l]); high.append(row[h]); cols.append(c)
    yy=np.arange(len(labs)); ax.hlines(yy,low,high,color=cols,lw=3); ax.scatter([(a+b)/2 for a,b in zip(low,high)],yy,c=cols,s=20)
    ax.set_yticks(yy,labs); ax.invert_yaxis(); ax.set_xlim(0,1); ax.set_xlabel('Conditional extreme-day probability')
    from matplotlib.lines import Line2D
    ax.legend(handles=[Line2D([0],[0],color=c,lw=3,label=n) for n,c in [('Wald','gray'),('Bootstrap','C0'),('Flat Beta','C1'),('Skeptical Beta','C2'),('Jeffreys Beta','C3')]],title='Interval method',loc='upper right')
    fig.tight_layout(); fig.savefig(FIG/'step11_bayesian_credible_intervals.png',dpi=300); plt.close(fig)
    return d
