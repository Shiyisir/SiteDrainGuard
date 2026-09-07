# Development log

## 2026-09-07 — Final release preparation

- Restored project rules, business context and development specifications from the original project archive; retained the independently reviewed code and review text.
- Reused Python 3.11.12 / PySWMM 2.1.0 / SWMM 5.2.4 and reran all seven release validation commands. Results: 19 tests, 85% coverage, moderate/heavy S0–S4 PASS, exact Hybrid union, identical rainfall, no extra/missing mutations.
- Applied Ruff formatting to two expressions only; repeated all seven validations successfully. No hydraulic logic or input data changed.
- Captured the real Heavy result table after clicking Run analysis in Streamlit. Added assets/dashboard.png and a Chinese/English README.
- Confirmed author Shiyisir and created the authorized public repository Shiyisir/SiteDrainGuard. Initialized a project-local main branch, isolated from the parent workspace repository.
- GitHub rejected the first push because the active CLI OAuth authorization lacks workflow scope. No hosted Actions run, tag or Release is claimed. The existing CI workflow remains intact.

## 2026-09-07

- Read the full project prompt and development specification before implementation.
- Created a Python 3.11.12 isolated environment with PySWMM 2.1.0, swmm-toolkit 0.17.0 and real EPA SWMM 5.2.4.
- The installed PySWMM 2.1.0 distribution reported no `swmm5` extra; its dependency set installed `swmm-toolkit` directly. The runtime smoke test confirmed the real engine, so the project pins the observed package rather than inventing an extra name.
- The first synthetic INP attempts exposed actual SWMM syntax constraints: no `[END]` section, curve type is present on the first row only, pump curves use `PUMP1`, and one outfall cannot have multiple inlet links. The final model was corrected and verified through the engine.
- Windows native SWMM rejected pytest temporary paths containing the local non-ASCII user name. The runner now executes in an ASCII project-local runtime directory and copies closed artifacts to the requested output path.
- PySWMM node statistics were cross-checked against `.rpt`: flooding volume is m³ under the SI model and duration is hours. The report uses `10^6 ltr` for aggregate flow-routing volumes.
- Verified both moderate and heavy real batches; no scenario uses mock output or hard-coded KPI values.

## 2026-09-07 — Independent second review

- Audited the uploaded retained heavy-run artifacts independently of the original self-audit.
- Verified S4's mutation manifest is exactly the set union of S1, S2 and S3, with zero extra or missing mutations, identical rainfall bytes, and no undeclared semantic INP token changes.
- Localized the S4 improvement to the serial C05–ST01–P01–O01 bottleneck. J05 accounts for about 98.6% of the S0→S4 flood-volume reduction in the retained heavy reports.
- Added `scripts/audit_hybrid_synergy.py` so the structural/mechanism audit can run after the heavy real-engine batch in GitHub Actions.
- Strengthened GitHub Actions to lint, validate the environment, run the full test suite, reproduce the heavy batch, run the S4 audit, and retain failure diagnostics.
- Added a Streamlit hydraulic-input signature guard so changed rainfall/scenario selections cannot silently display stale SWMM results; cost-only changes still reuse hydraulic results.
- Added report-derived evidence plots and `docs/hybrid_synergy.md`; no generated/mock dashboard screenshot was created.
- Clarified that the current Rational Method comparison is a quantity warning against the constrained outfall peak, not calibration or proof of SWMM correctness.
- Hosted GitHub Actions could not be triggered in this review environment because no authenticated repository write/push action or remote repository was available. The review therefore preserves `PARTIAL` for the external CI gate.

## 2026-09-07 — Hosted CI passed

- Added only the user-authorized workflow scope and successfully pushed main to Shiyisir/SiteDrainGuard. Existing scopes were preserved.
- Hosted run 34111256789 passed all lint/test steps on Ubuntu 24.04 / Python 3.11.16. Real SWMM 5.2.4, 19 tests, 85% coverage, Heavy S0–S4 and Hybrid audit matched the verified baseline.
- Updated bilingual README badge and release status, audit, environment, resume claims and machine-readable CI evidence. No simulation code or workflow changed.

## 2026-09-07 — Dashboard screenshot correction

- Replaced the narrow, mid-label screenshot with a fresh Chrome capture after a real Heavy S0–S4 analysis. The full baseline KPI labels and all five comparison rows are visible.
- Captured a 1100 × 450 result region at native browser size. The screenshot transport returned JPEG bytes, so the file was encoded as an actual PNG without resizing, sharpening, or changing any displayed data.
- Visually checked the saved image, verified PNG chunk checksums and the existing README reference. No application code or hydraulic input changed; the published v0.1.0 tag remains immutable.
