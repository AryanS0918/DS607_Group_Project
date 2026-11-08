# Contributions

This project was equally divided among the three members. Aryan Singh originated the project idea and led the distribution-fitting work, while Jaanvi Bajaj led descriptive and interval analysis and Nikhil Balaji led data preparation and dependence analysis.


## Aryan Singh — project conception, distribution modeling, and tail diagnostics (approximately one-third)
* Originated the project concept, empirical research direction, and the Normal-versus-Student-t analytical framework.
* Implemented and validated Student-t method-of-moments (MoM) and maximum-likelihood estimation (MLE) fitting routines in `src/distribution_fitting.py` (and the corresponding distribution-fitting notebook).
* Derived and reconciled the Student-t scale parameterization and degrees-of-freedom tail-heaviness interpretation across the codebase, README, and presentation.
* Generated the parametric goodness-of-fit comparison tables and empirical tail diagnostic figures comparing Gaussian vs. heavy-tailed return assumptions.
* Structured the presentation build workflow, standardized slide layouts, and documented Quarto/revealjs rendering instructions in the repository map.

## Jaanvi Bajaj — description and intervals (approximately one-third)
- Produced summary statistics, histograms, ECDF, KDE, and Q-Q exploratory figures in the notebooks and pipeline.
- Implemented CLT, Wald, bootstrap, and Monte Carlo interval analysis in `src/eda_and_intervals.py` and `02_clt_vs_bootstrap.ipynb`.
- Corrected the Student-t coverage numbers and extreme-return interpretation in the README and slides.
- Completed the descriptive EDA narrative and coefficient comparison tables across the five notebooks.
- Checked the course-week mapping and presentation figures against the committed analysis outputs.

## Nikhil Balaji — data and dependence (approximately one-third)
- Prepared raw SGX price handling, aligned returns, cleaning checks, and the processed return dataset in `src/data_loader.py`.
- Maintained the cleaning log, extreme-date annotations, and reproducible output tables.
- Implemented Pearson/Kendall dependence, permutation, contingency, and regime analysis in `src/dependence_and_tests.py`.
- Updated the README reproducibility instructions, pinned environment, FAST_MODE documentation, and course mapping.
- Ran the pipeline and checked that committed tables and figures are reproducible from the documented environment.
