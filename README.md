# Heavy Tails & Inference in DBS, OCBC and UOB

**MDSE DS607 group coursework — Master of Science in Data Science in Economics.**

**Members:** Aryan Singh, Jaanvi Bajaj, Nikhil Balaji.

## Motivation
DBS, OCBC, and UOB are systemically important pillars of Singapore's financial system and components of the STI. Mis-specifying their return tails with a Normal model can systematically understate extreme losses, distort capital reserves and Value-at-Risk estimates, and lead to overly loose or tight risk limits. This project tests those tail assumptions using daily SGX equity returns from 2014–2024.

## Research question
Are daily returns of DBS, OCBC and UOB from 2014 to 2024 well described by a Normal distribution, and do CLT-based confidence intervals agree with bootstrap intervals for their mean, volatility and co-movement?

## Pre-committed definitions and experimental design
- Tickers: DBS = `D05.SI`, OCBC = `O39.SI`, UOB = `U11.SI`.
- Dates: 2014-01-02 through 2024-12-31; Yahoo's exclusive end date is 2025-01-01.
- Return: $R_t=\ln(P_t/P_{t-1})$, where $P_t$ is daily Adjusted Close.
- Significance: α = 0.05; bootstrap $B=10,000$; permutation $B_{perm}=10,000$; parametric bootstrap default $B_{param}=1,000$; seed 42.
- Annualisation: 252 trading days.
- Extreme day: $R_{i,t}\leq q_{i,0.10}$.
- Calm: 2017-01-01 to 2019-12-31; COVID stress: 2020-02-01 to 2020-06-30; rate-hike: 2022-01-01 to 2023-12-31.

The 10% threshold was fixed before analysis to create a comparable worst-decile co-crash indicator while retaining enough observations for contingency inference.

## Methods & Course Mapping

| Project method | DS607 course week / lab |
|---|---|
| Summary statistics, ECDF, KDE, Q-Q, KS and permutation tests | Week 4 / Lab 4 |
| MM, LLN/CLT and delta method | Week 2 / Lab 2 |
| Wald and CLT tests | Week 3 / Lab 3 |
| Efron bootstrap and Monte Carlo coverage | Week 5 / Lab 5 |
| MLE | Week 6 / Lab 6 |
| Likelihood ratio test and numerical optimisation | Week 8 / Lab 7 |
| χ² tests | Week 9 / Lab 8 |
| Bayesian inference | Weeks 10–11 / Labs 9–10 |

## Data sources and reproducibility
All analysis uses Yahoo Finance daily Adjusted Close data. The SGX adjusted-close series have been independently checked against documented macroeconomic events on extreme move days; several event annotations remain not independently verified. No LSEG Workspace cross-check was performed. Raw downloads are retained under `data/raw/`; cleaned returns are under `data/processed/`. If raw files exist, the pipeline runs offline.

Tested environment: Python 3.14.6. Full pipeline runtime is measured at approximately 14 minutes on the current full-size development machine (including Step 8 parametric-bootstrap MLE optimisation). Run:

```bash
python -m pip install -r requirements.txt
python -m src.pipeline
# Development-only; FAST_MODE=1 changes only Step 8 replicates from 1,000 to 100: FAST_MODE=1 python -m src.pipeline
jupyter nbconvert --to notebook --execute --inplace notebooks/00_master_analysis.ipynb notebooks/01_data_and_eda.ipynb notebooks/02_clt_vs_bootstrap.ipynb notebooks/03_normal_vs_student_t.ipynb notebooks/04_dependence_regimes_bayesian.ipynb
```

## Repository map
- [00 master analysis](notebooks/00_master_analysis.ipynb)
- [01 data and EDA](notebooks/01_data_and_eda.ipynb)
- [02 CLT and bootstrap](notebooks/02_clt_vs_bootstrap.ipynb)
- [03 Normal and Student-t](notebooks/03_normal_vs_student_t.ipynb)
- [04 dependence, regimes and Bayesian analysis](notebooks/04_dependence_regimes_bayesian.ipynb)
- [src/](src/) — configuration, cleaning, inference, distribution fitting, and dependence modules.
- [data/raw/](data/raw/) · [data/interim/](data/interim/) · [data/processed/](data/processed/)
- [outputs/figures/](outputs/figures/) · [outputs/tables/](outputs/tables/) · [outputs/presentation/](outputs/presentation/)
- [render_slides.py](outputs/presentation/render_slides.py) and [slides_outline.md](outputs/presentation/slides_outline.md) define and render the presentation; [AI_USAGE.md](AI_USAGE.md) documents tool use.

## Empirical results
### Distribution and tail diagnostics
Aligned returns contain 2762 observations per bank. Excess kurtosis estimates are approximately 5.27 (DBS), 5.03 (OCBC), and 5.25 (UOB), so extreme returns are far heavier than a Gaussian benchmark. Minimum returns are about -7σ (the observed range is -6.9σ to -7.4σ). The Q-Q and lower-tail log-CDF diagnostics show Normal failure in the extremes; 1% quantiles alone are not evidence against Normality because variance inflation stretches Normal shoulders. Full values are in [step4_summary_statistics.csv](outputs/tables/step4_summary_statistics.csv).

Figures: [return series](outputs/figures/step4_return_series_regimes.png), [histograms and KDEs](outputs/figures/step4_hist_kde_normal.png), [ECDF and Q-Q](outputs/figures/step4_ecdf_and_qq.png).

### CLT versus bootstrap
Mean CLT and Efron bootstrap intervals agree closely. Volatility differs materially: textbook Normal-theory intervals ignore excess kurtosis, whereas fourth-moment delta and bootstrap intervals are wider and agree. Under simulated heavy-tailed Student-t returns ($\nu=5$), the Efron bootstrap and fourth-moment Delta-method intervals achieve coverage values of 92.5% for Delta, 92.6% for Efron bootstrap, and 70.1% for the textbook Normal-theory interval. See [Step 5](outputs/tables/step5_clt_intervals_wald.csv), [Step 6 comparison](outputs/tables/step6_clt_vs_bootstrap_comparison.csv), and [Monte Carlo coverage](outputs/tables/step6_monte_carlo_coverage.csv).

### Normal versus Student-t
MM degrees of freedom are near 5.1, while MLE estimates are near 4.1. MM relies on sample fourth moments, which are noisy in finite samples and barely exist theoretically when $\nu$ is near 4, so the MM estimates likely overstate $\nu$ relative to MLE. Student-t MLE estimates are approximately 4.14, 4.25, and 3.82. The Student-t MM scale is $s\sqrt{(\nu-2)/\nu}$; this formula gives the fitted distribution the same scale convention as MLE.

Parametric-bootstrap LRT p-values are p < 0.001 for all banks. The Student-t is not rejected for DBS (KS p ≈ 0.066), but is statistically rejected for OCBC and UOB (p < 0.05). Thus Student-t is vastly better than Normal yet remains imperfect. Tables: [fits](outputs/tables/step7_mm_vs_mle_fits.csv), [LRT/KS](outputs/tables/step8_lrt_and_ks_tests.csv); figure: [Normal vs. t](outputs/figures/step8_normal_vs_t_qq_ecdf.png).

### Dependence and regimes
For Pearson correlation, asymptotic Fisher-z CLT intervals are about 0.03 wide, e.g. DBS–OCBC [0.763, 0.793], whereas bootstrap intervals are about 0.05 wide, e.g. [0.753, 0.803]. This is consistent with joint heavy tails inflating sample correlation variability beyond Normal theory. Pearson and Kendall rank the pairs in the same order: DBS–OCBC highest, OCBC–UOB second, DBS–UOB third. See [correlation results](outputs/tables/step9_pearson_vs_kendall.csv) and [figure](outputs/figures/step9_correlation_cis.png).

COVID dispersion ratios are about 2.22–2.23 for all banks with p < 0.0001. The OCBC 2022–2023 rate-hike ratio is 0.86: dispersion was lower than calm, and $p=0.0143$ does not survive Bonferroni correction across six regime tests ($0.05/6 ≈ 0.0083$). Full [permutation tests](outputs/tables/step10_permutation_tests.csv) and [null distributions](outputs/figures/step10_permutation_nulls.png).

All expected worst-decile table counts exceed 5, and chi-square rejects independence for every pair. See [chi-square results](outputs/tables/step10_chisq_extreme_days.csv).

### Beta-Binomial stretch
Flat and Jeffreys intervals agree with frequentist intervals; the skeptical Beta(2,18) prior shifts estimates toward 10%. Estimates cover the three unordered pairs. See [Bayesian results](outputs/tables/step11_bayesian_vs_frequentist_cis.csv) and [figure](outputs/figures/step11_bayesian_credible_intervals.png).

## Limitations
1. Daily returns exhibit serial dependence and volatility clustering; ordinary bootstrap and permutation intervals are not i.i.d. intervals and may be too narrow.
2. In the Step 11 Beta-Binomial model, the 277 extreme days per bank cluster heavily in calendar time, such as March 2020, violating independent Bernoulli trials and making Bayesian and frequentist intervals overly narrow.
3. Results cover one market, three related banks, and a single 11-year period, limiting external validity.
4. Multiple tests span banks, pairs, and regimes without formal family-wise corrections, except where Bonferroni is explicitly discussed.
5. Data provenance: reliance on Yahoo Finance daily Adjusted Close data independently checked against documented macroeconomic events; no LSEG Workspace cross-check was performed, and some cleaning-log events remain not independently verified.

Cleaning records: [step3 cleaning log](outputs/tables/step3_cleaning_log.csv), [cleaning log narrative](data/interim/cleaning_log.md).
