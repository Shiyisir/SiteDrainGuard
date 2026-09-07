from __future__ import annotations

from pathlib import Path

import yaml

from ..domain.models import LinkMetadata, ModelMetadata, NodeMetadata


def _rows(path: Path, section_name: str) -> list[list[str]]:
    lines = path.read_text(encoding="utf-8").splitlines()
    start = next(i for i, line in enumerate(lines) if line.strip().upper() == f"[{section_name}]")
    rows: list[list[str]] = []
    for line in lines[start + 1 :]:
        stripped = line.strip()
        if stripped.startswith("["):
            break
        if not stripped or stripped.startswith(";"):
            continue
        rows.append(stripped.split())
    return rows


def load_model_metadata(inp_path: Path, metadata_path: Path) -> ModelMetadata:
    source = yaml.safe_load(metadata_path.read_text(encoding="utf-8")) or {}
    node_rows = {row[0]: row for row in _rows(inp_path, "JUNCTIONS")}
    node_rows.update({row[0]: row for row in _rows(inp_path, "STORAGE")})
    node_rows.update({row[0]: row for row in _rows(inp_path, "OUTFALLS")})
    coords = {row[0]: row for row in _rows(inp_path, "COORDINATES")}
    nodes: list[NodeMetadata] = []
    for node_id, row in node_rows.items():
        kind = "JUNCTION"
        full_depth = 1.0
        elevation = float(row[1])
        if node_id in {storage[0] for storage in _rows(inp_path, "STORAGE")}:
            kind = "STORAGE"
            full_depth = float(row[2])
        elif node_id in {outfall[0] for outfall in _rows(inp_path, "OUTFALLS")}:
            kind = "OUTFALL"
            full_depth = 0.45
        else:
            full_depth = float(row[2])
        coordinate = coords.get(node_id, [node_id, 0, 0])
        nodes.append(
            NodeMetadata(
                node_id=node_id,
                kind=kind,
                x=float(coordinate[1]),
                y=float(coordinate[2]),
                elevation_m=elevation,
                full_depth_m=full_depth,
            )
        )
    links: list[LinkMetadata] = []
    for row in _rows(inp_path, "CONDUITS"):
        links.append(
            LinkMetadata(link_id=row[0], from_node=row[1], to_node=row[2], length_m=float(row[3]))
        )
    for row in _rows(inp_path, "PUMPS"):
        links.append(LinkMetadata(link_id=row[0], from_node=row[1], to_node=row[2], kind="PUMP"))
    return ModelMetadata(nodes=nodes, links=links, **source)
