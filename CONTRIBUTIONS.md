# Contributions

This project was equally divided among the three members. Aryan Singh originated the project idea and led the distribution-fitting work, while Jaanvi Bajaj led descriptive and interval analysis and Nikhil Balaji led data preparation and dependence analysis.

## Aryan Singh — distribution fitting and presentation (approximately one-third)
- Defined the project idea, research direction, and Normal-versus-Student-t analysis plan.
- Implemented and reviewed Student-t method-of-moments and maximum-likelihood fitting in `src/distribution_fitting.py`.
- Explained and corrected the Student-t scale formula and degrees-of-freedom interpretation in the README and presentation.
- Produced the Normal-versus-Student-t fit tables and tail diagnostic figures.
- Fixed slide layout, removed the presentation placeholder, and added render instructions to the repository map.

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
