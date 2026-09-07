# Resume claim boundary

## Claims supported by the verified local baseline

- Built a Python/PySWMM prototype on EPA SWMM 5.2.4 for synthetic construction-site stormwater scenario comparison.
- Implemented five real-engine scenarios (S0–S4) using controlled mutation manifests and immutable base-model checksums.
- Implemented rainfall validation, flood metrics, risk heuristics, cost-assumption comparison, continuity QA, Rational Method comparison/warning and rainfall sensitivity.
- Added a reproducible batch CLI, Streamlit dashboard, unit tests and real-engine integration tests.
- The original local audit on Windows/Python 3.11.12 reported **18 passed** and **85% coverage** before the independent post-audit patch.
- The independently audited heavy synthetic result supports the statement that S4 reduced total flood volume from **3,338.20 m³ to 2,730.55 m³ (18.20%)** in the bundled model.
- The S4 effect is traceable to the C05–ST01–P01 bottleneck chain; the retained report evidence shows J05 flood volume falling from about **1,065 m³ to 466 m³**.

## Claims to update only after hosted CI

- Do not state a post-review test count or Linux CI result until the strengthened GitHub Actions workflow has actually run green.
- After hosted CI passes, update the test count/coverage from that run rather than copying the old local number automatically.

## Claims not supported

- No enterprise deployment, real construction-site validation, field calibration, code compliance or engineering accuracy percentage.
- No real cost savings, incident reduction, users, customers or performance guarantee.
- No claim that the dashboard replaces an engineer or produces a design approval.
- Do not describe the Rational Method comparison as calibration or proof of model correctness.
