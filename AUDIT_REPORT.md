# SiteDrainGuard v0.1 Audit Report

## 1. Executive result

**Final status: READY for v0.1.0 release. Local validation: PASS. Hosted CI: PASS.**

The reviewed implementation, real Heavy simulation, 19 tests, 85% coverage and Hybrid audit passed both locally and in hosted GitHub Actions. The bilingual README, real dashboard screenshot and confirmed author/repository fields are complete. The earlier OAuth push blocker was resolved by the user-authorized addition of workflow scope only.

Hosted evidence: [CI run 34111256789](https://github.com/Shiyisir/SiteDrainGuard/actions/runs/34111256789), tested commit `fd3cf67319c151759fffc5ee42905969cf6f9623`. Both lint and test jobs completed successfully. Machine-readable job/step evidence is retained in `docs/evidence/hosted_ci.json`. A subsequent documentation-only release commit must also pass CI before tagging; its exact SHA is resolved by the v0.1.0 Git tag.

## 2. Environment actually tested

- OS: Windows 11 Home China, build 26200
- Python: 3.11.12, reusing the original project archive environment against the updated project source
- PySWMM: 2.1.0
- swmm-toolkit: 0.17.0
- EPA SWMM engine: 5.2.4
- Streamlit: 1.63.0
- pandas: 2.3.3
- NumPy: 2.4.6
- Pydantic: 2.13.5
- Plotly: 6.9.0
- Ruff: 0.16.6

Hosted environment: Ubuntu 24.04, Python 3.11.16, PySWMM 2.1.0, swmm-toolkit 0.17.0, SWMM 5.2.4, Streamlit 1.63.0, pandas 2.3.3, Pydantic 2.13.5. [Actual run logs](https://github.com/Shiyisir/SiteDrainGuard/actions/runs/34111256789).

Evidence: the final seven command logs under ignored `artifacts/release/`, `uv lock --check --offline`, and `docs/environment.md`.

## 3. Requirement traceability

| ID | Requirement | Status | Evidence |
|---|---|---|---|
| P0-01 | Real EPA SWMM/PySWMM engine | PASS | `test_real_swmm_smoke.py`; engine version 5.2.4 printed by environment validation |
| P0-02 | Synthetic construction-site model and rainfall | PASS | `data/demo_site/base_model.inp`, rainfall CSVs and demo README |
| P0-03 | S0–S4 real scenarios | PASS | `test_scenario_effects.py`; moderate and heavy batch outputs |
| P0-04 | Base model isolation and mutation manifest | PASS | SHA-256 assertion, `manifest.json`, controlled whitelist writer |
| P0-05 | Rainfall validation and safe CSV upload | PASS | `tests/unit/test_rainfall.py`, app 2 MB CSV limit |
| P0-06 | Hydraulic/flood metrics | PASS | Node statistics extraction and dashboard KPI table |
| P0-07 | Risk classification | PASS | `validation/risk.py` and unit tests |
| P0-08 | Cost-effectiveness comparison | PASS | `metrics/economics.py`, CLI CSV/JSON and dashboard table |
| P0-09 | Runoff/routing continuity QA | PASS | `.rpt`/SystemStats extraction and thresholds in `validation/continuity.py` |
| P0-10 | Rational Method sanity check | PASS | `validation/rational_method.py` and dashboard QA section |
| P0-11 | Rainfall sensitivity | PASS | S0 runs at 0.8/1.0/1.2 intensity scales |
| P0-12 | Reproducible batch CLI | PASS | `python scripts/run_demo_batch.py --rainfall moderate/heavy` |
| P0-13 | Streamlit dashboard | PASS locally | HTTP health endpoint returned 200; dashboard code contains network, KPI, comparison, time series and QA sections |
| P0-14 | Unit/integration tests and Ruff | PASS locally | 19 passed; coverage 85%; Ruff check and format check pass |
| P0-15 | CI workflow | PASS hosted | [Run 34111256789](https://github.com/Shiyisir/SiteDrainGuard/actions/runs/34111256789); all required steps passed |
| P0-16 | Open-source docs and audit | PASS | README, methodology, validation, limitations, citation, notices and this report |

## 4. Commands executed

The post-review session reused the original project's existing Python environment against the current updated source. It did not claim a fresh installation. Commands were invoked using that interpreter (including `python -m ruff` and `python -m pytest`). Every command below returned exit code 0 in the final run; individual logs are retained under ignored `artifacts/release/`.

| Command | Result |
|---|---|
| `ruff check .` | PASS |
| `ruff format --check .` | PASS; 72 files formatted |
| `pytest --cov=src/sitedrainguard --cov-report=term-missing` | PASS; 19 passed, 85% coverage |
| `python scripts/validate_environment.py` | PASS; real SWMM 5.2.4, CMS/SI |
| `python scripts/run_demo_batch.py --rainfall moderate` | PASS; S0–S4 |
| `python scripts/run_demo_batch.py --rainfall heavy` | PASS; S0–S4 |
| `python scripts/audit_hybrid_synergy.py` | PASS; exact union, extra=0, missing=0, rainfall identical, semantic changes match manifest |
| `uv lock --check --offline` | PASS |
| Streamlit headless and real Heavy browser analysis | PASS; screenshot in assets/dashboard.png |
| `git diff --cached --check` and staged-file hygiene | PASS; no environment/cache/SWMM temporary outputs or detected secret values |
| `git push -u origin main` | PASS after user-authorized workflow scope refresh; initial rejection retained in development history |

Ruff initially found two formatting-only differences in app.py and scripts/audit_hybrid_synergy.py. These were formatted and the full seven-command validation passed again. No hydraulic logic or input changed.

## 5. Real SWMM verification

The local heavy batch produced these real values:

| Scenario | Flood volume (m³) | Flood reduction | Routing continuity |
|---|---:|---:|---:|
| S0 | 3338.20 | 0.00% | 0.009% |
| S1 | 3320.33 | 0.54% | -0.301% |
| S2 | 3321.33 | 0.51% | 0.235% |
| S3 | 3306.33 | 0.95% | -0.151% |
| S4 | 2730.55 | 18.20% | -0.276% |

All five scenarios used engine version 5.2.4, CMS/SI units, the same rainfall and the same base model. Retained run artifacts are under ignored `artifacts/runs/`; the base model was not changed.

## 6. Scientific QA

- Runoff continuity: -0.060% for the heavy S0–S4 batch; PASS.
- Routing continuity: -0.301% to 0.235%; all are under the project PASS threshold of 2%.
- Units: `test_units_and_stats.py` compares PySWMM node flooding aggregates with the SWMM `.rpt` `10^6 ltr` label and checks positive flooding duration in hours.
- Rational Method: `Q = 0.00278 C i A`, C=0.82 and area=9.45 ha; extreme ratios are surfaced as warnings, not presented as calibration.
- Sensitivity: heavy S0 total flood volume increased from 2,576.53 m³ at 0.8x rainfall to 4,100.95 m³ at 1.2x rainfall.
- Cleanup: intentional post-start failure followed by a successful next simulation passes.

## 7. Automated tests

- Total: 19
- Passed: 19
- Failed: 0
- Coverage: 85% total; core source paths are covered without excluding the real runner.
- Unit tests include rainfall, mutation, economics/risk/rational checks and INP writer behavior.
- Integration tests include real smoke, S0–S4, report/API unit cross-check and cleanup-after-failure.

## 8. UI smoke

- Startup: PASS.
- HTTP health: PASS, status 200.
- Import exception: none observed.
- Interactive browser click-through: PASS on 2026-09-07. Selected Heavy with S0–S4, clicked Run analysis, waited for Analysis complete, and verified the real result table and QA. Screenshot saved as `assets/dashboard.png` and referenced in README.

## 9. Security / repository hygiene

- Only CSV uploads are accepted; upload size is limited to 2 MB.
- Arbitrary INP upload is not exposed.
- Uploaded data is parsed as tabular text; no pickle/eval path exists.
- No `.env` file, API key, token, password or private project data found in application/docs scan.
- Base model is copied per run and checksummed.
- Runtime artifacts and coverage/cache directories are ignored by `.gitignore`.
- A project-local Git repository was initialized on main; the parent workspace repository was not staged or committed. main was successfully pushed to the confirmed public repository after the authorized workflow-scope refresh.

## 10. Known limitations

- Synthetic site, rainfall, facilities and costs only.
- No field calibration, survey DEM, local design-storm generator or live monitoring.
- Risk thresholds are internal display heuristics.
- Rational Method is a sanity check, not proof of model correctness.
- v0.1 is single-process/sequential and not a production multi-user service.
- No hosted dashboard deployment is included. Hosted CI passed; the README screenshot is a real local dashboard capture.

## 11. Release gates

No unresolved v0.1 implementation or hosted-CI blocker remains. Author and repository fields are confirmed, all local commands pass, the real screenshot is included, and hosted CI is green. Final publication is gated on a clean tree and a green CI run for the documentation release commit. Release identity: Shiyisir/SiteDrainGuard, v0.1.0.

The hosted runner emitted a non-failing Node.js runtime deprecation notice for existing upstream Actions. No workflow steps were removed or disabled; all required checks passed.

## 12. Claims allowed in README/resume

The project supports claims about Python/PySWMM/SWMM implementation, five real synthetic scenarios, controlled mutation manifests, metrics, continuity QA, Rational Method sanity checking, rainfall sensitivity, local test counts and reproducible CLI/dashboard workflow. See `docs/resume_claims.md`.

## 13. Claims NOT supported

Do not claim real enterprise use, field validation, calibration, design-code compliance, engineering accuracy, customer/user adoption or real cost savings.

## 14. Final recommendation

**READY for v0.1.0. Preserve the synthetic/no-calibration/no-engineering-design boundaries in the release notes.**
