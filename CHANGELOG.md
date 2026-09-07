# Changelog

## 0.1.0 - 2026-09-07

- Added a synthetic EPA SWMM construction-site model.
- Added validated rainfall events and S0-S4 scenario mutation.
- Added real PySWMM simulation, hydraulic metrics, economics and engineering QA.
- Added reproducible batch CLI, Streamlit dashboard, tests and CI configuration.
- Added an independent S4 structural audit that checks exact mutation union, identical rainfall and semantic INP isolation.
- Documented the C05-ST01-P01 bottleneck mechanism behind the heavy-event Hybrid result using retained SWMM report evidence.
- Added a Streamlit stale-result guard for rainfall/scenario changes.
- Strengthened GitHub Actions to reproduce the heavy demo and run the S4 audit before release.

Limitations: synthetic demo only; no field calibration; not an engineering design tool.
