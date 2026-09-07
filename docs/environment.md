# Tested environment

The following versions were used in the original audit and reverified during post-review local validation on 2026-09-07. The final local run reused the original project's Python 3.11.12 environment against the updated source tree; this is not a clean-install or hosted-CI claim.

| Component | Version |
|---|---|
| OS | Windows |
| Python | 3.11.12 |
| PySWMM | 2.1.0 |
| swmm-toolkit | 0.17.0 |
| EPA SWMM engine | 5.2.4 |
| Streamlit | 1.63.0 |
| pandas | 2.3.3 |
| NumPy | 2.4.6 |
| Pydantic | 2.13.5 |
| Plotly | 6.9.0 |
| pytest | 8.4.2 |
| pytest-cov | 7.1.0 |
| Ruff | 0.16.6 |

The project uses `pyproject.toml` and `uv.lock`. A standard `venv` + pip installation is also supported. The native engine is never replaced by a mock in application or integration code.
