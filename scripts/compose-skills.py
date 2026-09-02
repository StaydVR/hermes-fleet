#!/usr/bin/env python3
"""Validate and compose shared and bot-local Hermes skill trees."""

from __future__ import annotations

import argparse
import re
import shutil
import sys
from dataclasses import dataclass
from pathlib import Path


NAME_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")


@dataclass(frozen=True)
class Skill:
    name: str
    path: Path
    layer: str


def frontmatter_name(path: Path) -> str:
    text = path.read_text(encoding="utf-8")
    lines = text.splitlines()
    if not lines or lines[0] != "---":
        raise ValueError(f"{path}: missing opening YAML frontmatter")
    try:
        end = lines.index("---", 1)
    except ValueError as exc:
        raise ValueError(f"{path}: missing closing YAML frontmatter") from exc

    for line in lines[1:end]:
        match = re.match(r"^name:\s*['\"]?([^'\"#]+?)['\"]?\s*$", line)
        if match:
            name = match.group(1).strip()
            if not NAME_RE.fullmatch(name):
                raise ValueError(f"{path}: invalid skill name {name!r}")
            return name
    raise ValueError(f"{path}: frontmatter is missing name")


def discover(root: Path, layer: str) -> list[Skill]:
    if not root.is_dir():
        return []
    return [
        Skill(frontmatter_name(path), path, layer)
        for path in sorted(root.rglob("SKILL.md"))
    ]


def validate_unique(skills: list[Skill]) -> None:
    by_name: dict[str, Skill] = {}
    for skill in skills:
        prior = by_name.get(skill.name)
        if prior is not None:
            raise ValueError(
                f"duplicate skill name {skill.name!r}: {prior.path} ({prior.layer}) "
                f"and {skill.path} ({skill.layer})"
            )
        by_name[skill.name] = skill


def copy_layer(source: Path, destination: Path) -> None:
    if source.is_dir():
        shutil.copytree(source, destination, dirs_exist_ok=True)


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Compose root shared skills followed by a bot-local overlay."
    )
    parser.add_argument("--shared", required=True, type=Path)
    parser.add_argument("--bot", required=True, type=Path)
    parser.add_argument("--destination", type=Path)
    parser.add_argument("--check-only", action="store_true")
    args = parser.parse_args(argv)
    if not args.check_only and args.destination is None:
        parser.error("--destination is required unless --check-only is used")
    return args


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv or sys.argv[1:])
    try:
        shared = args.shared.resolve()
        bot = args.bot.resolve()
        skills = discover(shared, "shared") + discover(bot, "bot")
        validate_unique(skills)

        if args.destination is not None and not args.check_only:
            destination = args.destination.resolve()
            if destination == shared or destination == bot:
                raise ValueError("destination must differ from source skill trees")
            destination.mkdir(parents=True, exist_ok=True)
            copy_layer(shared, destination)
            copy_layer(bot, destination)

        print(f"skill composition OK: {len(skills)} unique skills")
        for skill in skills:
            print(f"  {skill.layer}: {skill.name}")
        return 0
    except (OSError, UnicodeError, ValueError) as exc:
        print(f"skill composition failed: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
