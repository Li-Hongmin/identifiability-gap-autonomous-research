# Supplement: The Identifiability Gap in Autonomous Research

Contents

- `data_package/` — the data and reconstruction code for the manuscript: the 44-paper evidence map (first coding, blind second coding, source-based adjudication of all 62 disagreements), the 54-row estimand table and computability check, the nine finite-design identified sets, the MLReplicate score reconstruction (30 intended score slots, 29 observed), the 45-record rankability screen, the 15-evaluation pair table (376 pairs), machine-readable rankability certificates, and source links (`data/source_index/paper_sources.csv`). No third-party full texts are included. See `data_package/README.md` for the reproduction order; all scripts use relative paths. Dependencies: the numerical reconstruction, validation, and `independent_checks.py` use only the Python standard library; the two plotting scripts (`analysis/make_identification_bounds_figure.py` and `analysis/make_rankability_audit_figure.py`) additionally require NumPy and Matplotlib and are not needed to reproduce any reported number. `analysis/collect_autonomous_research_evaluation_frame.py` is not included; the nine query strings, retrieval settings, and per-query totals are in `data/source_index/arxiv_query_log.json` (also listed in Section 4.1), and per-record matches are in `data/derived/autonomous_research_evaluation_screening_merged.csv`.
- `independent_checks.py` — a separate script written for this submission that re-derives, from the released tables, every count reported in the manuscript and checks the propositions numerically.
- `CONTENTS.sha256` — SHA-256 checksums for every file in the supplement (with package-level checksums in `data_package/MANIFEST.sha256`).

What `independent_checks.py` checks

1. Proposition 1: the construction gives valid probabilities and reproduces $q$ exactly, on a 19×19 rational grid in $(0,1)^2$ (exact rational arithmetic).
2. Proposition 2: 20,000 random $(c,s,\mu_s,\mu_u)$ draws never leave the stated sets (outer and monotone).
3. Proposition 3: on 3,000 random interval pairs, "every admissible pair satisfies $\theta_i>\theta_j$" (grid search) coincides with $L_i>U_j$; the worked example $[0.09,0.99]$.
4. The sensitivity–specificity inversion and its admissible range for $q$.
5. MLReplicate: all six identified sets recomputed from the 29 observed scores; zero of 15 orders identified; the Agent Laboratory missing-score interval $[0.240,0.307]$.
6. The audit: 376 pairs; selected group 145 pairs with 119 certified, 6 reversed, 9 unresolved; control group 231 pairs with 214 certified and no losses.
7. Every quoted ratio in the text (e.g. 290/616, 1050/4717, 70/157, 101/164, 15/134).
8. The arXiv query log (`data/source_index/arxiv_query_log.json`, nine queries, 446 unique records, 7 citation-chain additions) and the machine-readable rankability certificates (`mlreplicate_rankability_certificate.json` and `cross_benchmark_rankability_certificate.json`, including their certification qualifications).

Run `python3 independent_checks.py` from this directory; it prints `all checks passed`. Random checks use a fixed seed. These are numerical checks, not proofs; the propositions are proved in the manuscript. The checks confirm internal consistency with the released tables; they do not re-extract numbers from the source papers, whose transcription is documented by the source anchors in the data package.

Coding provenance: second coders and adjudicators appear only as pseudonymous labels (`arda_second_a`–`c`, `arda_adjudicator_a`–`c`); the records do not state whether each was a person or an AI agent, and blinding was by file omission and instruction, not verified. The codings are not independent expert assessments.

Licence: manuscript text and data annotations CC BY 4.0; code MIT.
