# ADR-002: Sequential SWMM execution

Status: accepted

PySWMM protects a single simulation state and the native engine is not treated as a freely parallel pure-Python function. The service runs scenarios sequentially under a process-local lock, prioritizing correctness and cleanup over premature parallelism.
