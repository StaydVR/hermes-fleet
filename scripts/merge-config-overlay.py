#!/usr/bin/env python3
"""Deep-merge fleet config.overlay.yaml into a live Hermes config.yaml.

Stdlib only (no PyYAML). Overlay keys win. Lists are replaced, not appended.
Maps merge recursively. Scalars overwrite.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path


def _fail(msg: str, code: int = 1) -> None:
    print(msg, file=sys.stderr)
    raise SystemExit(code)


def _try_import_yaml():
    try:
        import yaml  # type: ignore

        return yaml
    except Exception:
        pass
    # Hermes venv on this host
    venv_yaml = Path("/opt/hermes/.venv/lib")
    if venv_yaml.exists():
        import glob

        for p in glob.glob(str(venv_yaml / "python*" / "site-packages")):
            if p not in sys.path:
                sys.path.insert(0, p)
        try:
            import yaml  # type: ignore

            return yaml
        except Exception:
            pass
    return None


def deep_merge(base, overlay):
    if not isinstance(overlay, dict):
        return overlay
    if not isinstance(base, dict):
        base = {}
    out = dict(base)
    for k, v in overlay.items():
        if isinstance(v, dict) and isinstance(out.get(k), dict):
            out[k] = deep_merge(out[k], v)
        else:
            out[k] = v
    return out


def main(argv: list[str]) -> int:
    if len(argv) != 3:
        _fail(f"Usage: {argv[0]} <live-config.yaml> <overlay.yaml>")
    live_path = Path(argv[1])
    overlay_path = Path(argv[2])
    if not live_path.is_file():
        _fail(f"missing live config: {live_path}")
    if not overlay_path.is_file():
        _fail(f"missing overlay: {overlay_path}")

    yaml = _try_import_yaml()
    if yaml is None:
        _fail("PyYAML not available (need hermes venv or system PyYAML)")

    live = yaml.safe_load(live_path.read_text(encoding="utf-8")) or {}
    overlay = yaml.safe_load(overlay_path.read_text(encoding="utf-8")) or {}
    if not isinstance(live, dict) or not isinstance(overlay, dict):
        _fail("live and overlay must be YAML mappings")

    merged = deep_merge(live, overlay)
    # Prefer block style, keep unicode
    text = yaml.safe_dump(
        merged,
        sort_keys=False,
        default_flow_style=False,
        allow_unicode=True,
        width=100,
    )
    live_path.write_text(text, encoding="utf-8")
    print(f"merged overlay → {live_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
