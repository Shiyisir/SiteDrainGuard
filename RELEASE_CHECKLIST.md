# SiteDrainGuard v0.1 public-release checklist

v0.1 is functionally frozen. Do not add P1 features before the items below are closed.

- [x] Real EPA SWMM 5.2.4 / PySWMM 2.1.0 local run verified on Windows/Python 3.11.
- [x] S0–S4 real runs completed for moderate and heavy synthetic rainfall.
- [x] S4 manifest independently verified as exactly S1 ∪ S2 ∪ S3.
- [x] S4 mechanism documented from SWMM `.rpt` evidence.
- [x] UI stale-result guard added so rainfall/scenario changes cannot silently display an old hydraulic run.
- [x] GitHub Actions workflow includes heavy-demo reproduction and S4 structural audit.
- [x] Push to Shiyisir/SiteDrainGuard and obtain a green hosted GitHub Actions run: [34111256789](https://github.com/Shiyisir/SiteDrainGuard/actions/runs/34111256789).
- [x] Confirm public author Shiyisir and repository Shiyisir/SiteDrainGuard in `pyproject.toml`, `LICENSE`, and `CITATION.cff`.
- [x] Capture a **real** dashboard screenshot/GIF from the running Streamlit app and add it to README. `assets/dashboard.png` shows the real Heavy S0–S4 result table captured on 2026-09-07.
- [x] Confirm the v0.1.0 tagging gate: hosted CI, identity fields, real screenshot and local validation are complete. Tagging must target the clean release commit after its CI passes.

All release prerequisites above have evidence. The published tag and Release are verified directly on GitHub; no generated screenshot or synthetic CI status is used.
