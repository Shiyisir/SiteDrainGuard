from pathlib import Path


def require_base_model(path: Path) -> None:
    if not path.is_file():
        raise FileNotFoundError(f"base model not found: {path}")
    text = path.read_text(encoding="utf-8")
    for section in ("[OPTIONS]", "[RAINGAGES]", "[SUBCATCHMENTS]", "[JUNCTIONS]", "[TIMESERIES]"):
        if section not in text:
            raise ValueError(f"base model missing required section {section}")
