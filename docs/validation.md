# Validation record

## Real engine

On a local Windows environment, Python 3.11.12, PySWMM 2.1.0 and swmm-toolkit 0.17.0 loaded EPA SWMM 5.2.4. `scripts/validate_environment.py` runs the real S0 model. `tests/integration/test_real_swmm_smoke.py` checks engine version, CMS/SI units, non-empty output and positive synthetic flooding.

## Scenarios and cleanup

`tests/integration/test_scenario_effects.py` runs S0–S4 with heavy rainfall, checks all five real runs and verifies the base-model SHA-256 is unchanged. `test_cleanup_after_failure.py` raises after the real engine has started, then immediately runs S0 again to verify context cleanup and lock release.

## Unit cross-check

`test_units_and_stats.py` reads the SWMM `.rpt` Flow Routing section. The report's Flooding Loss is labelled in `10^6 ltr`; the aggregate from PySWMM node statistics is treated as m³ and agrees with that report value within the report's three-decimal rounding tolerance. Node flooding duration is checked as a positive value and documented as hours.

## Continuity and sensitivity

The internal QA threshold is absolute continuity error ≤2% PASS, 2–5% WARNING and >5% invalid for ranking. The verified heavy batch had runoff continuity -0.060% for S0–S4 and routing continuity from -0.301% to 0.235%, all PASS. Sensitivity increased total flood volume from 2,576.53 m³ at 0.8x to 4,100.95 m³ at 1.2x in the verified heavy run.

## Not performed

There is no field calibration, measured rainfall validation, survey DEM validation, local-code compliance review or real-project validation. These are explicitly outside v0.1.

## Independent S4 structural audit

A second review added `scripts/audit_hybrid_synergy.py`. After a heavy batch it verifies that S4 is exactly the union of S1/S2/S3 at both manifest and semantic INP-token level, confirms identical rainfall across scenarios, and extracts C05/P01/ST01/O01/J05 report evidence. The retained uploaded heavy artifacts passed this audit with zero extra and zero missing S4 mutations. See `docs/hybrid_synergy.md`.
