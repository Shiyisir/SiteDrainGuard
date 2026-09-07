# Third-party notices

SiteDrainGuard is an independent prototype and is not endorsed by any upstream project. The exact versions used for the verified local v0.1 baseline are recorded in `docs/environment.md`.

The table below is based on the installed package metadata/license files from that verified environment. Package versions and license metadata were rechecked locally on 2026-09-07 during release preparation.

| Component | Role | License in verified environment |
|---|---|---|
| EPA SWMM / solver material distributed via `swmm-toolkit` | Hydrologic and hydraulic engine | U.S. Government work / CC0 notice in the toolkit distribution |
| PySWMM 2.1.0 | Python simulation API | BSD-2-Clause |
| swmm-toolkit 0.17.0 | Native SWMM toolkit bindings/runtime | Package metadata: `CC0-1.0 AND (MIT OR Apache-2.0)`; bundled third-party components retain their own notices |
| Streamlit 1.63.0 | Local dashboard runtime | Apache-2.0 |
| Plotly 6.9.0 | Interactive charts | MIT |
| pandas 2.3.3 | Tabular data handling | BSD-3-Clause |
| NumPy 2.4.6 | Numeric dependency | Package metadata includes BSD-3-Clause plus licenses for bundled components |
| Pydantic 2.13.5 | Input/result models | MIT |
| PyYAML 6.0.3 | Synthetic configuration files | MIT |

This file is a project-level attribution summary, not a substitute for upstream license files. When redistributing dependency binaries, retain all notices required by those distributions.
