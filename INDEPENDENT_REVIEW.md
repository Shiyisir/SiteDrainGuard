# SiteDrainGuard v0.1 — Independent second review

Date: 2026-09-07

This review was performed against the uploaded project archive and retained SWMM run artifacts. It is independent of the original Codex self-audit in `AUDIT_REPORT.md`.

## Result

**Local scientific/software baseline: credible. Public-release state: still PARTIAL until hosted GitHub CI and owner identity fields are completed.**

The original audit reported a Windows/Python 3.11.12 environment with EPA SWMM 5.2.4, PySWMM 2.1.0, 18 passing tests, 85% coverage and a Streamlit HTTP 200 smoke check. This second review did not rerun the native SWMM engine because the review environment does not have a compatible Python 3.11/Linux PySWMM wheel available offline. Instead, it independently inspected code, mutation logic, retained `.inp`/`.rpt` artifacts and generated a structural S4 audit that can now run in CI after the real heavy batch.

## 1. S4 isolation — PASS

A new reproducible audit (`scripts/audit_hybrid_synergy.py`) checks the retained/generated batch artifacts and verifies:

- `S4 = S1 ∪ S2 ∪ S3`
- extra S4 mutations: 0
- missing S4 mutations: 0
- rainfall bytes identical across S0–S4
- semantic INP token changes exactly match each scenario manifest
- no hidden S4-only INP token changes

The audit was run against the uploaded retained heavy-run artifacts and returned PASS.

Observed structural result:

```text
S4 = S1 ∪ S2 ∪ S3
extra mutations = 0
missing mutations = 0
```

A stronger unit test was also added to assert that the S4 mutation plan is exactly the set union of S1, S2 and S3 rather than merely checking that S4 has four mutations.

## 2. Why S4 is much better — explained from SWMM report evidence

The heavy-run reports localize the mechanism to the serial path:

```text
upstream junctions -> C05 -> ST01 -> P01 -> O01
```

Key report values:

| Scenario | C05 max flow (m³/s) | P01 max flow (m³/s) | O01 volume (m³) | J05 flood volume (m³) | Total flood (m³) |
|---|---:|---:|---:|---:|---:|
| S0 | 0.040 | 0.000 | 1 | 1,065 | 3,338.20 |
| S1 | 0.028 | 0.028 | 197 | 1,047 | 3,320.33 |
| S2 | 0.283 | 0.000 | 1 | 1,060 | 3,321.33 |
| S3 | 0.040 | 0.000 | 1 | 1,033 | 3,306.33 |
| S4 | 0.323 | 0.180 | 786 | 466 | 2,730.55 |

Interpretation:

- S1 gives the pump capacity but leaves C05 narrow, so the pump is feed-limited.
- S2 increases conveyance but leaves the outlet pump effectively off, so the transferred water cannot leave the system.
- S3 adds storage but leaves both access (C05) and discharge constraints.
- S4 relieves all three serial constraints together, so C05 can feed ST01 and P01 can actually reach 0.18 m³/s.

The S0→S4 total flood reduction is 607.65 m³. J05 alone drops by about 599 m³, accounting for approximately 98.6% of that total reduction. The improvement is therefore hydraulically localized at the bottleneck immediately upstream of C05/ST01 rather than looking like an unexplained model-wide artifact.

The simple sum of individual reductions is 66.62 m³, while S4 reduces 607.65 m³. The 541.03 m³ difference is described only as an **observed nonlinear interaction in this synthetic model**, not a general synergy coefficient.

Full explanation: `docs/hybrid_synergy.md`.

## 3. CI gate — workflow strengthened, hosted run still external

`.github/workflows/ci.yml` was strengthened to:

- allow manual `workflow_dispatch`;
- retain read-only repository permissions;
- run lint/format checks on Python 3.11;
- run environment validation and the complete pytest suite;
- reproduce the **heavy** demo rather than only the default moderate event;
- immediately run `scripts/audit_hybrid_synergy.py` against the newly generated real-engine artifacts;
- upload SWMM reports/results on failure for debugging.

This means a hosted green run will now validate not just “tests pass,” but also the exact S4 isolation property and the advertised heavy mechanism.

A hosted GitHub Actions run could not be triggered from this review session because no authenticated GitHub write/push action is available to this environment and the uploaded archive is not connected to a remote repository. No green CI status is fabricated.

## 4. Release polish — completed where evidence permits

Completed:

- README now explains the S4 result using report-level evidence.
- Two report-derived evidence figures were added under `assets/`.
- `docs/hybrid_synergy.md` and a portable audit snapshot were added.
- A stale-result guard was added to the Streamlit UI: changing rainfall or scenario selection after a run now blocks display of stale hydraulic results until `Run analysis` is clicked again; cost-only edits still reuse hydraulic results.
- `RELEASE_CHECKLIST.md` freezes v0.1 and explicitly blocks P1 feature creep.
- The release checklist explicitly forbids a generated/mock dashboard image.

Not fabricated / still owner-external:

- hosted GitHub CI green status;
- GitHub repository URL;
- repository owner name in `LICENSE`, `CITATION.cff`, `pyproject.toml`;
- a real Streamlit dashboard screenshot/GIF.

Those items require the owner's GitHub destination/identity or a browser attached to the actual running app.

## 5. Additional review note: Rational Method wording

The existing v0.1 Rational Method implementation compares the formula result with the modeled outfall peak. In this synthetic model the outlet is intentionally constrained by the pump, so the comparison produces a large warning and should **not** be presented as calibration or as a proof that SWMM runoff is correct. The existing UI already surfaces it as a warning, which is acceptable for v0.1, but interview wording should remain conservative: “Rational Method quantity comparison / sanity warning,” not “model validation.”

A stronger future implementation would compare the Rational estimate with SWMM system lateral/runoff inflow rather than the constrained outfall discharge. This is intentionally not expanded into v0.1 feature work during this freeze.

## 6. Public-release recommendation

Do not add GIS, LID, Docker, optimization, AI, custom INP upload or other P1/P2 features now.

Tag `v0.1.0` only after:

1. the reviewed package is pushed to the intended GitHub repository;
2. the hosted CI workflow is green;
3. `YOUR_NAME` / repository URL placeholders are replaced;
4. one real dashboard screenshot or GIF is captured from the running application.
