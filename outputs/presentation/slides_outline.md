# 8-Slide Presentation Outline (8–10 minutes)

## Speaker allocation
- Nikhil Balaji: Data, dependence, and regimes (Slides 2 and 6)
- Jaanvi Bajaj: EDA, CLT/bootstrap, and Monte Carlo (Slides 3–4)
- Aryan Singh: Estimation, tests, synthesis, and limitations (Slides 5, 7–8)

## Slide 1 — Title and research question
- Title, Aryan Singh, Jaanvi Bajaj, Nikhil Balaji
- Motivation: systemically important Singapore banking pillars; tail-risk under Normal assumptions affects capital and limits.
- One-sentence research question.

## Slide 2 — Repository and reproducibility
- Repository map and workflow: raw Yahoo adjusted closes → cleaning → pipeline → tables/figures/notebooks.
- Pre-committed dates, alpha, seeds, resamples, regimes, and worst-10% definition.
- Extreme dates are listed in the cleaning log; some bank-specific annotations are not independently verified.

## Slide 3 — Exploratory diagnostics
- Summary statistics, return-series volatility clustering, histogram/KDE and Normal Q-Q.
- Emphasise excess kurtosis, extreme realisations about -7σ (actual range -6.9σ to -7.4σ), and lower-tail log-CDF evidence.

## Slide 4 — CLT vs. bootstrap intervals
- Merged presentation of Steps 5–6.
- Mean intervals agree; Normal-theory volatility intervals understate uncertainty.
- Delta-method and bootstrap recover 92.5% (Delta) and 92.6% (Efron bootstrap) Monte Carlo coverage under Student-t nu=5; Normal-theory coverage is 70.1% (Normal-theory).

## Slide 5 — Normal vs. Student-t estimation and fit
- MM nu≈5.1 vs MLE nu≈4.1, because fourth moments are noisy and barely exist near nu=4.
- Parametric LRT p<0.001; Student-t KS accepted for DBS (p≈0.066), rejected for OCBC/UOB (p<0.05).
- Lower-tail log-CDF shows Normal understates left-tail probabilities.

## Slide 6 — Co-movement and regime shifts
- Pearson Fisher-z vs Pearson bootstrap vs Kendall tau; heavy tails widen bootstrap correlation uncertainty.
- COVID dispersion ratios ≈2.22–2.23, permutation p<0.0001.
- OCBC rate-hike ratio 0.86; p=0.0143 does not survive Bonferroni across six tests.
- Worst-10% contingency chi-square rejects independence.

## Slide 7 — Risk-manager takeaways and limitations
- Normal-based tail-risk numbers are materially deficient; Student-t is better but still imperfect.
- Volatility clustering, clustered worst days, single-market scope, external validity, and multiple testing limitations.

## Slide 8 — Appendix / Bayesian stretch and feedback
- Three unordered pairs only (DBS–OCBC, DBS–UOB, OCBC–UOB).
- Flat Beta-Binomial agrees closely with Wald and bootstrap; skeptical prior demonstrates sensitivity.
