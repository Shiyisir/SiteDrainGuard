# Data dictionary and unit audit

| Field | Meaning | Source | Raw unit | Display unit | Notes |
|---|---|---|---|---|---|
| `intensity_mm_h` | rainfall intensity | validated CSV / SWMM TIMESERIES | mm/h | mm/h | non-negative, ≤500 in P0 |
| `total_depth_mm` | event rainfall depth | validated points | mm | mm | interval intensity × minutes / 60 |
| `Node.statistics["max_depth"]` | maximum node water depth | PySWMM Node statistics | m in SI model | m | cross-checked with SWMM report depth column |
| `Node.statistics["flooding_volume"]` | total node overflow | PySWMM Node statistics | m³ in SI model | m³ | agrees with report `10^6 ltr` after ×1000 |
| `Node.statistics["flooding_duration"]` | time node flooded | PySWMM Node statistics | h | h | agrees with report `Hours Flooded` |
| `Node.statistics["peak_flooding_rate"]` | peak overflow rate | PySWMM Node statistics | m³/s | m³/s | SI `CMS` |
| `SystemStats.runoff_stats["routing_error"]` | runoff continuity | PySWMM SystemStats / `.rpt` | percent | % | project QA thresholds apply |
| `SystemStats.routing_stats["routing_error"]` | flow-routing continuity | PySWMM SystemStats / `.rpt` | percent | % | project QA thresholds apply |
| `SystemStats.routing_stats["outflow"]` | total outfall routing volume | PySWMM SystemStats | m³ | m³ | not used as a primary KPI |
| `Link.flow` | current link flow | PySWMM Link | m³/s | m³/s | SI `CMS` |

If a future model changes flow units or engine version, this table and the integration cross-check must be revisited before labelling a new KPI.
