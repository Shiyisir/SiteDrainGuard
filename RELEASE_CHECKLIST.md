# SiteDrainGuard v0.1 public-release checklist

v0.1 is functionally frozen. Do not add P1 features before the items below are closed.

- [x] Real EPA SWMM 5.2.4 / PySWMM 2.1.0 local run verified on Windows/Python 3.11.
- [x] S0–S4 real runs completed for moderate and heavy synthetic rainfall.
- [x] S4 manifest independently verified as exactly S1 ∪ S2 ∪ S3.
- [x] S4 mechanism documented from SWMM `.rpt` evidence.
- [x] UI stale-result guard added so rainfall/scenario changes cannot silently display an old hydraulic run.
- [x] GitHub Actions workflow includes heavy-demo reproduction and S4 structural audit.
- [ ] Push to the intended GitHub repository and obtain a green hosted GitHub Actions run.
- [x] Confirm public author Shiyisir and repository Shiyisir/SiteDrainGuard in `pyproject.toml`, `LICENSE`, and `CITATION.cff`.
- [x] Capture a **real** dashboard screenshot/GIF from the running Streamlit app and add it to README. `assets/dashboard.png` shows the real Heavy S0–S4 result table captured on 2026-09-07.
- [ ] Tag `v0.1.0` only after the hosted CI and identity fields above are complete.

The remaining unchecked items require the repository owner's confirmed GitHub destination/identity and an actual hosted CI run; they are deliberately not fabricated.
