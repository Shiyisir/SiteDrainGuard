# Architecture

The application follows a thin-UI, thick-domain boundary:

```text
Streamlit / CLI
      |
AnalysisService
      |
rainfall validation -> controlled INP mutation -> sequential PySWMM runner
      |                                      |
metrics / economics / QA <------------------+
```

The base INP is copied before every run. `replace_timeseries` and `scenario.mutations` are intentionally narrow writers: they know the target section/object/row/token and reject an unexpected base value. This was chosen over a broad string replacement because curve rows and timeseries have different SWMM token shapes.

`Simulation` objects never enter Streamlit session state. A process-wide re-entrant lock and a context manager protect the non-reentrant engine; the analysis service calls scenarios sequentially. The dashboard stores only Pydantic result data.

The runner uses an ASCII-only runtime directory under `artifacts/.runtime` before copying retained artifacts to the requested output directory. This matters on Windows because the native SWMM toolkit can reject a temporary path containing a non-ASCII user name.
