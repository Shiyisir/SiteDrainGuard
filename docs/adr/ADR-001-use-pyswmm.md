# ADR-001: Use EPA SWMM through PySWMM

Status: accepted

SiteDrainGuard delegates hydrologic-hydraulic solving to the mature EPA SWMM engine through PySWMM instead of implementing a solver. This keeps v0.1 focused on transparent scenario workflows, metrics and QA.
