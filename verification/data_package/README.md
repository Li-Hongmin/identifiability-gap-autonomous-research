# The Identifiability Gap in Autonomous Research: public release candidate

This local candidate supports the ARDA evidence map, finite-design identified sets, MLReplicate rankability reconstruction, the 15-evaluation cross-benchmark rankability audit, and the complete 44-paper blind-recoding and source-adjudication sensitivity analysis.

## Reproduction

From the package root, run the standard-library numerical reconstruction and validation:

```bash
python3 analysis/compare_arda_identification_secondcoding.py
python3 analysis/adjudicate_arda_identification_coding.py
python3 analysis/analyze_arda_validator_endpoint_reach.py
python3 analysis/make_identification_bounds.py
python3 analysis/build_cross_benchmark_rankability_audit.py
python3 analysis/validate_public_data_package.py
```

The two optional figure-rendering scripts (`analysis/make_identification_bounds_figure.py` and `analysis/make_rankability_audit_figure.py`) require NumPy and Matplotlib and are not needed to reproduce or validate any reported number.

The strict joint-identification result is intentionally reported under three matrices: first coding `3 papers / 35 units`, blind second coding `7 / 2267`, and cross-adjudication `8 / 2287`. A nested construct stress test fixes each paper's primary output claim before classifying its metric: four designs (`1930` heterogeneous units) combine claim-complete measurement with procedural separation, and none combines claim-complete measurement with institutional externality. These are sensitivity results in a purposive evidence map, not field prevalence or pooled capability estimates.

The rankability screen covers all 44 ARDA papers plus one flagged current update. Fifteen endpoint-specific evaluations contain 100 configurations and 376 within-evaluation pairs. In four selected- or missing-output evaluations, 119 of 134 displayed strict relations are same-direction certified, six reverse, and nine remain unresolved. Eleven all-run or near-complete positive controls retain all 214 displayed strict relations; complete-run display and target intervals coincide by construction as an algebraic control rather than independent evidence of scientific validity. Certified orders hold only for the realized endpoint (which may be a proxy), and finite-sample strict orders may be practically small or statistically uncertain. MLReplicate remains the extreme `0/15` case. Pair counts are dependent and endpoints are heterogeneous; neither `15/134` nor any all-audit total estimates field prevalence. `data/derived/cross_benchmark_rankability_certificate.json` freezes these design-specific results, while `data/derived/mlreplicate_rankability_certificate.json` remains the worked single-evaluation certificate.

No third-party PDFs, extracted full texts, external repository snapshots, or absolute local paths are included. `data/source_index/paper_sources.csv` links to original arXiv records.
