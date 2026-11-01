from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'outputs' / 'presentation'
TABLES = ROOT / 'outputs' / 'tables'
FIGURES = ROOT / 'outputs' / 'figures'

slides = [
    ('1', 'Heavy Tails & Inference in DBS, OCBC and UOB', [
        'Aryan Singh, Jaanvi, Nikhil — MDSE DS607 group coursework',
        'Singapore banking pillars: tail-risk choices affect capital reserves and risk limits.',
        'Research question: are 2014–2024 daily returns Normal, and do CLT intervals agree with bootstrap intervals?'
    ]),
    ('2', 'Repository, reproducibility & definitions', [
        'Yahoo Finance Adjusted Close; aligned SGX dates; raw files retained offline.',
        'Fixed: alpha=0.05, B=10,000, 10,000 permutations, seed 42, 252 annualisation.',
        'Calm 2017–2019; COVID 2020-02-01 to 2020-06-30; rate-hike 2022–2023.',
        'Extreme dates are annotated in the cleaning log and extreme observations are retained.'
    ]),
    ('3', 'Exploratory diagnostics: heavy tails', [
        'Daily return series exhibit volatility clustering and COVID/rate-hike regime shifts.',
        'Excess kurtosis is approximately 5; extreme minima are near -7σ to -9σ.',
        'Normal Q-Q and lower-tail log-CDF plots reveal departures in the extreme left tail.'
    ]),
    ('4', 'CLT vs bootstrap intervals', [
        'Mean CLT and bootstrap intervals agree closely.',
        'Normal-theory volatility intervals ignore excess kurtosis and understate uncertainty.',
        'Under Student-t nu=5: Delta and Efron bootstrap coverage are ~92–95%; Normal-theory coverage is ~59–80%.',
        'Q01 is reported as an empirical 1% quantile, not a complete VaR model.'
    ]),
    ('5', 'Normal vs Student-t estimation & fit', [
        'MM nu≈5.1; MLE nu≈4.1. Fourth moments are noisy near nu=4.',
        'Parametric-bootstrap LRT p < 0.001 for all banks.',
        'Student-t KS: not rejected for DBS (p≈0.066); rejected for OCBC and UOB (p<0.05).'
    ]),
    ('6', 'Co-movement and regime shifts', [
        'Pearson Fisher-z CLT ≈0.03 wide; Pearson bootstrap ≈0.05 wide; Kendall measures rank association.',
        'COVID dispersion ratios ≈2.22–2.23; permutation p<0.0001.',
        'OCBC rate-hike ratio 0.86; p=0.0143 does not survive Bonferroni at 0.05/6.',
        'Worst-10% chi-square rejects independence for all pairs.'
    ]),
    ('7', 'Takeaways and limitations', [
        'Normal risk numbers severely understate tail risk; Student-t is substantially better but imperfect.',
        'Volatility clustering and clustered extreme dates undermine independence assumptions.',
        'One market and 11-year period; multiple tests across pairs and regimes require multiplicity caution.'
    ]),
    ('8', 'Appendix: Bayesian extreme co-crashes', [
        'Three unordered pairs: DBS–OCBC, DBS–UOB, OCBC–UOB.',
        'Flat Beta-Binomial agrees closely with Wald and bootstrap intervals.',
        'Skeptical Beta(2,18) illustrates prior sensitivity.',
        'Discussant: 1 strength | 1 methodological concern | 1 concrete suggestion'
    ]),
]

with PdfPages(OUT / 'DS607 GP 01549747 slides.pdf') as pdf:
    for number, title, bullets in slides:
        fig = plt.figure(figsize=(13.333, 7.5))
        ax = fig.add_axes([0, 0, 1, 1]); ax.axis('off')
        ax.text(0.07, 0.91, title, fontsize=28, weight='bold', va='top')
        y = 0.78
        for bullet in bullets:
            ax.text(0.09, y, '• ' + bullet, fontsize=18, va='top', wrap=True)
            y -= 0.16
        ax.text(0.92, 0.04, number, fontsize=14, ha='right', color='gray')

        figure_candidates = {
            '3': 'step4_ecdf_and_qq.png',
            '4': 'step6_clt_vs_bootstrap_cis.png',
            '5': 'step8_normal_vs_t_qq_ecdf.png',
            '6': 'step9_correlation_cis.png',
            '8': 'step11_bayesian_credible_intervals.png',
        }
        image_name = figure_candidates.get(number)
        if image_name and (FIGURES / image_name).exists():
            im = plt.imread(FIGURES / image_name)
            iax = fig.add_axes([0.62, 0.12, 0.34, 0.48]); iax.imshow(im); iax.axis('off')
        pdf.savefig(fig, bbox_inches='tight'); plt.close(fig)
