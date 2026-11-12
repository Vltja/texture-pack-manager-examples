#!/usr/bin/env python3
"""Generate Common-relative PNG entries without changing Hytale's directory layout."""
from pathlib import Path


def write_index(resources: Path) -> list[str]:
    common = resources / "Common"
    if not common.is_dir():
        raise ValueError("Missing resources/Common directory")
    paths = []
    for path in sorted(common.rglob("*")):
        if path.is_symlink():
            raise ValueError(f"Symlinks are not supported: {path}")
        if path.is_file():
            relative = path.relative_to(common).as_posix()
            if not relative.endswith(".png") or any(c in relative for c in ("\n", "\r", "\\")) or ".." in relative:
                raise ValueError(f"Expected a canonical PNG path: {relative}")
            paths.append(relative)
    if not paths:
        raise ValueError("Empty texture pack")
    (resources / "textures.list").write_text("\n".join(paths) + "\n", encoding="utf-8")
    return paths


if __name__ == "__main__":
    root = Path(__file__).resolve().parents[1]
    print(f"Indexed {len(write_index(root / 'resources'))} Common PNGs")
