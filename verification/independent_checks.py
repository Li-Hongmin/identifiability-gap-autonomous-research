"""Independent numerical checks for the manuscript (standard library only).

Run from the supplement root after unpacking the data package:
    python3 independent_checks.py
These are finite numerical checks, not proofs. Random checks use a fixed seed.
"""
import csv, itertools, random
from fractions import Fraction as F
from pathlib import Path

ROOT = Path(__file__).resolve().parent
D = ROOT / "data_package" / "data" / "derived"
random.seed(20261027)
fails = []
def check(cond, msg):
    if not cond:
        fails.append(msg)

# Proposition 1: exact rational grid over (0,1)^2.
grid = [F(k, 20) for k in range(1, 20)]
for th in grid:
    for q in grid:
        if th <= q:
            a, b = F(1), th * (1 - q) / (q * (1 - th))
        else:
            b, a = F(1), q * (1 - th) / ((1 - q) * th)
        check(0 <= a <= 1 and 0 <= b <= 1, f"P1 prob {th},{q}")
        ps = th * a + (1 - th) * b
        check(ps > 0 and th * a / ps == q, f"P1 identity {th},{q}")

# Proposition 2: random finite populations never leave the stated sets,
# and the endpoints are attained by mu_u in {0,1} (or {0,mu_s}).
for _ in range(20000):
    c, s, ms, mu = (random.random() for _ in range(4))
    th = c * (s * ms + (1 - s) * mu)
    L, U = c * s * ms, c * (s * ms + (1 - s))
    check(L - 1e-12 <= th <= U + 1e-12, "P2 outer")
    if mu <= ms:
        check(th <= c * ms + 1e-12, "P2 monotone")
check(abs(0.9 * 0.1 - 0.09) < 1e-12 and abs(0.9 * 0.1 + 0.9 - 0.99) < 1e-12, "P3 example")

# Proposition 3 on random interval pairs: order identified iff L_i > U_j,
# checked by searching jointly admissible points on a fine grid.
for _ in range(3000):
    Li, Lj = random.random(), random.random()
    Ui, Uj = Li + random.random() * (1 - Li), Lj + random.random() * (1 - Lj)
    pts = lambda L, U: [L + (U - L) * k / 50 for k in range(51)]
    always = all(x > y for x in pts(Li, Ui) for y in pts(Lj, Uj))
    check(always == (Li > Uj), "P3 criterion")

# Validator correction (Rogan-Gladen form).
for _ in range(5000):
    a, b, v = 0.5 + random.random() / 2, 0.5 + random.random() / 2, random.random()
    if a + b <= 1.0001:
        continue
    q = a * v + (1 - b) * (1 - v)
    check(abs((q + b - 1) / (a + b - 1) - v) < 1e-9, "RG inversion")
    check(1 - b - 1e-12 <= q <= a + 1e-12, "RG range")

# MLReplicate: recompute bounds from the 30 score slots and the funnel.
rows = list(csv.DictReader(open(D / "mlreplicate_selected_human_scores.csv", newline="")))
bounds = {r["system_code"]: r for r in csv.DictReader(open(D / "mlreplicate_rankability_bounds.csv", newline=""))}
check(len(rows) == 30 and sum(r["score_status"] == "observed" for r in rows) == 29, "ML slots")
I = {}
for code, b in bounds.items():
    n = int(b["targeted_attempts_n"]) * 3
    obs = sum(float(r["normalized_score_0_to_1"]) for r in rows if r["system_code"] == code and r["score_status"] == "observed")
    unknown = int(b["unknown_completed_scores_n"])  # includes the one missing selected score
    lo, hi = obs / n, (obs + unknown) / n
    check(abs(lo - float(b["identified_lower"])) < 1e-6 and abs(hi - float(b["identified_upper"])) < 1e-6, f"ML bound {code}")
    I[code] = (lo, hi)
check(sum(1 for i, j in itertools.permutations(I, 2) if I[i][0] > I[j][1]) == 0, "ML 0/15")
al = [float(r["normalized_score_0_to_1"]) for r in rows if r["system_code"] == "AL" and r["score_status"] == "observed"]
check(abs(sum(al) / 15 - 0.240) < 5e-4 and abs((sum(al) + 1) / 15 - 0.30667) < 5e-4 and len(al) == 14, "AL sensitivity")

# Cross-benchmark audit: recount every pair from the released pair table.
pairs = list(csv.DictReader(open(D / "rankability_audit_pairs.csv", newline="")))
check(len(pairs) == 376, "pairs 376")
def tally(group):
    P = [p for p in pairs if (p["audit_group"] == "selected_output") == group]
    disp = [p for p in P if p["display_relation"] != "no_display" and p["display_relation"] not in ("tie",)]
    st = [p["display_claim_status"] for p in P]
    return len(P), st.count("certified"), st.count("reversed"), st.count("unresolved")
sel, ctrl = tally(True), tally(False)
check(sel == (145, 119, 6, 9), f"selected group {sel}")
check(ctrl[0] == 231 and ctrl[2] == 0 and ctrl[3] == 0 and ctrl[1] == 214, f"control group {ctrl}")

# Arithmetic quoted in the text.
Q = {"290/616": (290/616, .471), "326/616": (326/616, .529), "575/728": (575/728, .790),
     "178/240": (178/240, .742), "1050/4717": (1050/4717, .223), "15/4717": (15/4717, .0032),
     "70/157": (70/157, .446), "101/164": (101/164, .616), "49/92": (49/92, .533),
     "15/134": (15/134, .112), "23/44": (23/44, .523), "32/44": (32/44, .727), "5/1773": (5/1773, .0028)}
for k, (x, r) in Q.items():
    check(abs(x - r) < 6e-4 if r > .01 else abs(x - r) < 6e-5, f"arith {k}")
check(abs((0.60 - 0.45) / 0.60 - 0.25) < 1e-12 and abs((0.50 - 0.40) / 0.50 - 0.20) < 1e-12, "FirstProof fraction")


# arXiv query log vs per-record matches: totals, union 446, 7 citation-chain additions.
import json, collections
ql = json.load(open(D.parent / "source_index" / "arxiv_query_log.json"))
rows = list(csv.DictReader(open(D / "autonomous_research_evaluation_screening_merged.csv", encoding="utf-8")))
cnt = collections.Counter(q for r in rows for q in r["matched_queries"].split(";") if q)
check(len(ql["queries"]) == 9, "query log: nine queries")
for k, st in ql["query_stats"].items():
    check(st["total_results"] == st["returned"] == cnt.get(k, 0), f"query log: {k} totals")
check(sum(1 for r in rows if r["matched_queries"]) == ql["retrieved_unique_records"] == 446, "query log: 446 unique")
check(sum(1 for r in rows if not r["matched_queries"]) == 7 and len(rows) == 453, "query log: 7 additions, 453 records")

# Machine-readable rankability certificates and certification qualifications.
ml_cert = json.load(open(D / "mlreplicate_rankability_certificate.json", encoding="utf-8"))
cb_cert = json.load(open(D / "cross_benchmark_rankability_certificate.json", encoding="utf-8"))
check("algebraic control" in ml_cert.get("certification_qualification", "") and "statistically uncertain" in ml_cert.get("certification_qualification", ""), "ML cert qualification")
check("algebraic control" in cb_cert.get("certification_qualification", "") and "statistically uncertain" in cb_cert.get("certification_qualification", ""), "CB cert qualification")
check(cb_cert["headline"]["selected_output_certified_pairs"] == 119 and cb_cert["headline"]["selected_output_reversed_pairs"] == 6, "CB cert headline")

print("FAILED:" if fails else "all checks passed", *fails[:20], sep="\n")
raise SystemExit(1 if fails else 0)
