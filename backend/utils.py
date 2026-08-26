"""Small file helpers shared by backend modules."""

import json
from pathlib import Path
from typing import Any


def read_json(path: Path) -> Any:
    """Read UTF-8 JSON config or output files."""
    with path.open("r", encoding="utf-8") as file:
        return json.load(file)


def write_json(path: Path, data: Any) -> None:
    """Write readable UTF-8 JSON and create the output folder when needed."""
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as file:
        json.dump(data, file, indent=2, ensure_ascii=False)
        file.write("\n")
