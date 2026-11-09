# The Identifiability Gap in Autonomous Research: When Can Systems Be Ranked?

[![verify](https://github.com/Li-Hongmin/identifiability-gap-autonomous-research/actions/workflows/verify.yml/badge.svg)](https://github.com/Li-Hongmin/identifiability-gap-autonomous-research/actions/workflows/verify.yml) [![DOI](https://img.shields.io/badge/DOI-10.5281%2Fzenodo.24054527-blue)](https://doi.org/10.5281/zenodo.24054527)

**Hongmin Li** (Institute of Science Tokyo; The University of Tokyo) · ORCID [0000-0003-0228-0600](https://orcid.org/0000-0003-0228-0600)

Main result of the manuscript: selected success rates of autonomous-research systems identify neither per-attempt reliability nor a system order; the paper gives sharp missing-outcome bounds, an order-identification criterion for separable identified sets, and an audit of published comparisons, with all data and reconstruction code released.

- Manuscript on rStation: <https://rstation.ai/problems/ai_agent/papers/2/v2> (version 2)
- Archived on Zenodo: concept DOI [10.5281/zenodo.24054527](https://doi.org/10.5281/zenodo.24054527) (all versions); this repository mirrors version 2, DOI [10.5281/zenodo.24054530](https://doi.org/10.5281/zenodo.24054530)

## Contents

- `paper/paper.md`, `paper/identifiability-gap-autonomous-research.pdf` — the manuscript (version 2).
- `verification/` — the supplement of that version, unpacked unchanged (except as noted below); its own README describes each file.
- `.github/workflows/verify.yml` — reruns every check below on each push.

## What the programs check

| Check | Command (run inside `verification/`) |
|---|---|
| Re-derives every reported count and checks Propositions 1-3 numerically | `python independent_checks.py \| tee out.txt && grep -q 'all checks passed' out.txt` |
| Second-coding comparison | `cd data_package && python analysis/compare_arda_identification_secondcoding.py` |
| Adjudication of coding disagreements | `cd data_package && python analysis/adjudicate_arda_identification_coding.py` |
| Validator endpoint reach | `cd data_package && python analysis/analyze_arda_validator_endpoint_reach.py` |
| Finite-design identified sets | `cd data_package && python analysis/make_identification_bounds.py` |
| Cross-benchmark rankability audit | `cd data_package && python analysis/build_cross_benchmark_rankability_audit.py` |
| Validation of the public data package | `cd data_package && python analysis/validate_public_data_package.py` |

The programs check the finite and exact computations used in the manuscript; the mathematical arguments are those written in the paper.

The `decision_reason` column of `data_package/data/derived/autonomous_research_evaluation_screening_merged.csv` is rendered here in English. That file is covered by the supplement hashes, so the CI restores the archived original from the Zenodo record before running the checks.

## Reproducing

```sh
cd verification
sha256sum -c CONTENTS.sha256      # or: shasum -a 256 -c CONTENTS.sha256
pip install numpy==2.5.4 matplotlib==3.10.3
python independent_checks.py | tee out.txt && grep -q 'all checks passed' out.txt
cd data_package && python analysis/compare_arda_identification_secondcoding.py
cd data_package && python analysis/adjudicate_arda_identification_coding.py
cd data_package && python analysis/analyze_arda_validator_endpoint_reach.py
cd data_package && python analysis/make_identification_bounds.py
cd data_package && python analysis/build_cross_benchmark_rankability_audit.py
cd data_package && python analysis/validate_public_data_package.py
```

Requirements: Python 3.9+. Run the commands from a copy if you want to keep the recorded outputs untouched.

## Cite

```bibtex
@misc{li2026identifiabilitygapautono,
  author    = {Li, Hongmin},
  title     = {The Identifiability Gap in Autonomous Research: When Can Systems Be Ranked?},
  year      = {2026},
  publisher = {Zenodo},
  doi       = {10.5281/zenodo.24054527},
  url       = {https://doi.org/10.5281/zenodo.24054527}
}
```

## License

Manuscript and data: [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/). Code: MIT (see `LICENSE`).
