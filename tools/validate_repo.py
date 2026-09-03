#!/usr/bin/env python3
"""Validate Hermes skills, privacy rules, env safety, and Slack overlays."""

from __future__ import annotations

import argparse
import re
import sys
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

import yaml


SKIP_DIRS = {".git", ".venv", "__pycache__", "node_modules"}
NAME_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
SAFE_EMAIL_DOMAINS = {"example.com", "example.org", "example.net", "example.invalid"}


@dataclass(frozen=True)
class Finding:
    path: Path
    message: str
    line: int | None = None

    def render(self, root: Path) -> str:
        try:
            display = self.path.relative_to(root)
        except ValueError:
            display = self.path
        location = f"{display}:{self.line}" if self.line else str(display)
        return f"{location}: {self.message}"


@dataclass(frozen=True)
class ScanPattern:
    label: str
    regex: re.Pattern[str]


PATTERNS = (
    ScanPattern(
        "Slack credential",
        re.compile(r"\bxox[baprs]-[A-Za-z0-9-]{8,}|\bxapp-[A-Za-z0-9-]{8,}"),
    ),
    ScanPattern(
        "provider credential",
        re.compile(r"\b(?:gh[pousr]_[A-Za-z0-9]{12,}|sk-[A-Za-z0-9_-]{16,})"),
    ),
    ScanPattern(
        "JWT credential",
        re.compile(r"\beyJ[A-Za-z0-9_-]{8,}\.[A-Za-z0-9_-]{8,}\.[A-Za-z0-9_-]{8,}"),
    ),
    ScanPattern(
        "private key material",
        re.compile(r"-----BEGIN(?: [A-Z0-9]+)? PRIVATE KEY-----"),
    ),
    ScanPattern(
        "secret-shaped assignment",
        re.compile(
            r"(?i)\b(?:api[_-]?key|secret|token|password|passwd|private[_-]?key)"
            r"\s*[:=]\s*['\"]?(?!\s*(?:$|<|\$|\{|\[))[A-Za-z0-9+/_.=-]{12,}"
        ),
    ),
    ScanPattern(
        "home-directory path",
        re.compile(r"/(?:Users|home)/[A-Za-z0-9._-]+(?:/|\b)"),
    ),
    ScanPattern(
        "Slack workspace identifier",
        re.compile(r"\b[CGDUW](?=[A-Z0-9]{8,}\b)(?=[A-Z0-9]*\d)[A-Z0-9]+\b"),
    ),
    ScanPattern(
        "production infrastructure identifier",
        re.compile(r"\b(?:prj|team|dpl)_[A-Za-z0-9]{8,}\b"),
    ),
    ScanPattern(
        "production Supabase host",
        re.compile(r"https://[a-z0-9]{20}\.supabase\.co\b"),
    ),
    ScanPattern(
        "production Supabase project reference",
        re.compile(
            r"(?i)\b(?:supabase\s+(?:project|ref)|project[_ -]?ref|live\s+db)"
            r"\s*(?:[:=|]\s*)[`'\"]?[a-z0-9]{20}\b"
        ),
    ),
    ScanPattern(
        "phone number",
        re.compile(r"(?<![A-Za-z0-9])(?:\+\d{1,3}[ .-]?)?(?:\(?\d{3}\)?[ .-])\d{3}[ .-]\d{4}(?!\d)"),
    ),
)

PERSON_FIELD_RE = re.compile(
    r"(?im)^\s*(?:[-*]\s*)?(?:\*\*)?"
    r"(?:owner|operator|maintainer|reviewer|requester|contact|approved by|requested by)"
    r"(?:\*\*)?\s*[:=]\s*(?!<|(?:the|company|department|security|repository|fleet)\b)"
    r"[A-Z][a-z]+(?:\s+[A-Z][a-z]+)+\s*$"
)

SLACK_CONFIG = {
    ("agent", "gateway_notify_interval"): 0,
    ("display", "interim_assistant_messages"): False,
    ("display", "tool_progress"): "off",
    ("display", "thinking_progress"): False,
    ("display", "live_status"): "off",
    ("display", "platforms", "slack", "interim_assistant_messages"): False,
    ("display", "platforms", "slack", "tool_progress"): "off",
    ("display", "platforms", "slack", "thinking_progress"): False,
    ("display", "platforms", "slack", "streaming"): False,
    ("display", "platforms", "slack", "long_running_notifications"): False,
    ("display", "platforms", "slack", "busy_ack_detail"): False,
    ("display", "platforms", "slack", "live_status"): "verb",
    ("gateway", "streaming", "enabled"): False,
    ("gateway", "platforms", "slack", "typing_indicator"): True,
    ("gateway", "platforms", "slack", "typing_status_text"): "is thinking...",
    ("platforms", "slack", "reply_to_mode"): "first",
    ("platforms", "slack", "extra", "reply_in_thread"): True,
    ("platforms", "slack", "extra", "reply_broadcast"): False,
    ("platforms", "slack", "extra", "native_task_cards"): False,
    ("platforms", "slack", "extra", "allow_bots"): "mentions",
    ("slack", "require_mention"): True,
    ("slack", "strict_mention"): True,
    ("slack", "thread_require_mention"): True,
    ("slack", "ignore_other_user_mentions"): True,
}

REQUIRED_SLACK_BOT_SCOPES = {"assistant:write", "reactions:write"}

SAFE_ENV_VALUES = {
    "SLACK_REACTIONS": re.compile(r"true"),
    "HERMES_CODEX_EVENT_STALE_TIMEOUT_SECONDS": re.compile(r"\d+|<[^>]+>"),
    "HERMES_CODEX_TTFB_TIMEOUT_SECONDS": re.compile(r"\d+|<[^>]+>"),
    "HERMES_CODEX_TTFB_MAX_SECONDS": re.compile(r"\d+|<[^>]+>"),
}


def iter_files(root: Path) -> Iterable[Path]:
    for path in sorted(root.rglob("*")):
        if not path.is_file():
            continue
        if any(part in SKIP_DIRS for part in path.relative_to(root).parts):
            continue
        yield path


def read_text(path: Path) -> str | None:
    try:
        data = path.read_bytes()
    except OSError:
        return None
    if b"\x00" in data:
        return None
    try:
        return data.decode("utf-8")
    except UnicodeDecodeError:
        return None


def line_number(text: str, index: int) -> int:
    return text.count("\n", 0, index) + 1


def validate_skill(path: Path) -> tuple[dict[str, object] | None, list[Finding]]:
    findings: list[Finding] = []
    text = read_text(path)
    if text is None:
        return None, [Finding(path, "SKILL.md must be UTF-8 text")]
    if not text.startswith("---\n"):
        return None, [Finding(path, "SKILL.md must start at byte one with YAML frontmatter")]

    closing = text.find("\n---\n", 4)
    if closing == -1:
        return None, [Finding(path, "SKILL.md is missing a closing frontmatter delimiter")]

    raw_frontmatter = text[4:closing]
    body = text[closing + 5 :].strip()
    try:
        frontmatter = yaml.safe_load(raw_frontmatter)
    except yaml.YAMLError as exc:
        return None, [Finding(path, f"invalid YAML frontmatter: {exc}")]

    if not isinstance(frontmatter, dict):
        return None, [Finding(path, "frontmatter must be a YAML mapping")]

    name = frontmatter.get("name")
    description = frontmatter.get("description")
    if not isinstance(name, str) or not name.strip():
        findings.append(Finding(path, "frontmatter requires a non-empty string name"))
    elif not NAME_RE.fullmatch(name):
        findings.append(Finding(path, f"skill name must be lowercase hyphenated: {name!r}"))

    if not isinstance(description, str) or not description.strip():
        findings.append(Finding(path, "frontmatter requires a non-empty string description"))
    elif len(description) > 1024:
        findings.append(Finding(path, "skill description exceeds 1024 characters"))

    if not body:
        findings.append(Finding(path, "skill body must contain actionable content"))
    return frontmatter, findings


def validate_skills(root: Path) -> tuple[list[Finding], int]:
    findings: list[Finding] = []
    names: dict[str, Path] = {}
    count = 0
    for path in iter_files(root):
        relative = path.relative_to(root)
        lowered_parts = {part.lower() for part in relative.parts}
        looks_like_skill_copy = path.name != "SKILL.md" and path.name.lower().startswith("skill.md")
        archived_skill = path.name == "SKILL.md" and lowered_parts.intersection(
            {"backup", "backups", "archive", "archives", "archived", "old"}
        )
        if looks_like_skill_copy or archived_skill:
            findings.append(Finding(path, "backup/archive skill copies are not allowed"))
        if path.name != "SKILL.md":
            continue

        count += 1
        frontmatter, skill_findings = validate_skill(path)
        findings.extend(skill_findings)
        if frontmatter and isinstance(frontmatter.get("name"), str):
            name = str(frontmatter["name"])
            if name in names:
                findings.append(
                    Finding(path, f"duplicate skill name {name!r}; first declared in {names[name].relative_to(root)}")
                )
            else:
                names[name] = path
    return findings, count


def is_safe_email(value: str) -> bool:
    domain = value.rsplit("@", 1)[-1].lower()
    return domain in SAFE_EMAIL_DOMAINS


def validate_privacy(root: Path) -> tuple[list[Finding], int]:
    findings: list[Finding] = []
    scanned = 0
    email_regex = re.compile(r"\b[A-Za-z0-9.!#$%&'*+/=?^_`{|}~-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b")
    for path in iter_files(root):
        text = read_text(path)
        if text is None:
            continue
        scanned += 1
        for match in email_regex.finditer(text):
            if not is_safe_email(match.group(0)):
                findings.append(
                    Finding(path, "personal or non-example email address is not allowed", line_number(text, match.start()))
                )
        match = PERSON_FIELD_RE.search(text)
        if match:
            findings.append(Finding(path, "role field contains a personal name", line_number(text, match.start())))
        for scan_pattern in PATTERNS:
            match = scan_pattern.regex.search(text)
            if match:
                findings.append(
                    Finding(path, f"{scan_pattern.label} is not allowed", line_number(text, match.start()))
                )
    return findings, scanned


def nested_value(document: object, path: tuple[str, ...]) -> object:
    value = document
    for part in path:
        if not isinstance(value, dict) or part not in value:
            raise KeyError(".".join(path))
        value = value[part]
    return value


def validate_runtime_overlays(root: Path) -> list[Finding]:
    findings: list[Finding] = []
    overlays = sorted((root / "bots").glob("*/runtime-config.yaml"))
    template = root / "templates/new-agent/runtime-config.yaml"
    if template.is_file():
        overlays.append(template)

    for path in overlays:
        try:
            data = yaml.safe_load(path.read_text(encoding="utf-8"))
        except (OSError, UnicodeError, yaml.YAMLError) as exc:
            findings.append(Finding(path, f"runtime overlay is not valid YAML: {exc}"))
            continue
        for key_path, expected in SLACK_CONFIG.items():
            try:
                actual = nested_value(data, key_path)
            except KeyError:
                findings.append(Finding(path, f"missing Slack contract key {'.'.join(key_path)}"))
                continue
            if actual != expected or type(actual) is not type(expected):
                findings.append(
                    Finding(
                        path,
                        f"Slack contract key {'.'.join(key_path)} must be {expected!r}, got {actual!r}",
                    )
                )
    return findings


def validate_slack_manifest(root: Path) -> list[Finding]:
    path = root / "templates/new-agent/slack-app-manifest.yaml"
    if not path.is_file():
        return []

    try:
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, yaml.YAMLError) as exc:
        return [Finding(path, f"Slack app manifest is not valid YAML: {exc}")]

    try:
        scopes = nested_value(data, ("oauth_config", "scopes", "bot"))
    except KeyError:
        return [Finding(path, "Slack app manifest is missing oauth_config.scopes.bot")]
    if not isinstance(scopes, list) or any(not isinstance(scope, str) for scope in scopes):
        return [Finding(path, "Slack app manifest oauth_config.scopes.bot must be a list of scope names")]

    missing = sorted(REQUIRED_SLACK_BOT_SCOPES.difference(scopes))
    if missing:
        return [Finding(path, f"Slack app manifest is missing required bot scope(s): {', '.join(missing)}")]
    return []


def validate_env_defaults(root: Path) -> list[Finding]:
    findings: list[Finding] = []
    paths = sorted((root / "bots").glob("*/env.defaults"))
    paths.extend(sorted((root / "templates").glob("**/env.defaults")))
    example = root / "shared/env.keys.example"
    if example.is_file():
        paths.append(example)

    for path in paths:
        text = path.read_text(encoding="utf-8")
        values: dict[str, str] = {}
        for number, raw in enumerate(text.splitlines(), 1):
            line = raw.strip()
            if not line or line.startswith("#"):
                continue
            if "=" not in line:
                findings.append(Finding(path, "env line must be NAME=VALUE", number))
                continue
            key, value = line.split("=", 1)
            values[key] = value
            if value == "" or re.fullmatch(r"<[^>]+>", value):
                continue
            allowed = SAFE_ENV_VALUES.get(key)
            if allowed is None or not allowed.fullmatch(value):
                findings.append(Finding(path, f"non-secret env value is not allowlisted for {key}", number))
        if path.name == "env.defaults" and values.get("SLACK_REACTIONS") != "true":
            findings.append(Finding(path, "env.defaults must set SLACK_REACTIONS=true"))
    return findings


def validate_repository(root: Path) -> tuple[list[Finding], int, int]:
    root = root.resolve()
    skill_findings, skill_count = validate_skills(root)
    privacy_findings, scanned_count = validate_privacy(root)
    findings = skill_findings + privacy_findings
    findings.extend(validate_runtime_overlays(root))
    findings.extend(validate_slack_manifest(root))
    findings.extend(validate_env_defaults(root))
    return findings, skill_count, scanned_count


def write_skill(root: Path, relative: str, name: str, body: str = "# Work\n\nDo the bounded task.\n") -> None:
    path = root / relative / "SKILL.md"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        f'---\nname: {name}\ndescription: "Actionable test skill."\n---\n\n{body}',
        encoding="utf-8",
    )


def run_self_tests() -> int:
    cases = 0
    with tempfile.TemporaryDirectory() as directory:
        root = Path(directory)
        write_skill(root, "skills/good", "good-skill")
        findings, _, _ = validate_repository(root)
        assert not findings, findings
        cases += 1

    with tempfile.TemporaryDirectory() as directory:
        root = Path(directory)
        write_skill(root, "skills/bad", "Bad_Name")
        findings, _ = validate_skills(root)
        assert any("lowercase hyphenated" in finding.message for finding in findings)
        cases += 1

    with tempfile.TemporaryDirectory() as directory:
        root = Path(directory)
        write_skill(root, "skills/one", "same-name")
        write_skill(root, "bots/example/skills/two", "same-name")
        findings, _ = validate_skills(root)
        assert any("duplicate skill name" in finding.message for finding in findings)
        cases += 1

    with tempfile.TemporaryDirectory() as directory:
        root = Path(directory)
        source = root / "unsafe.txt"
        source.write_text("credential=" + "xoxb-" + "A" * 24, encoding="utf-8")
        findings, _ = validate_privacy(root)
        assert any("credential" in finding.message.lower() for finding in findings)
        cases += 1

    with tempfile.TemporaryDirectory() as directory:
        root = Path(directory)
        source = root / "safe.env.example"
        source.write_text("SERVICE_API_TOKEN=\nSECOND_TOKEN=<runtime-secret>\n", encoding="utf-8")
        findings, _ = validate_privacy(root)
        assert not findings, findings
        cases += 1

    with tempfile.TemporaryDirectory() as directory:
        root = Path(directory)
        source = root / "contact.txt"
        source.write_text("person" + "@company.test", encoding="utf-8")
        findings, _ = validate_privacy(root)
        assert any("email" in finding.message for finding in findings)
        cases += 1

    with tempfile.TemporaryDirectory() as directory:
        root = Path(directory)
        source = root / "identity.txt"
        source.write_text("Owner: Avery Exampleton\n", encoding="utf-8")
        findings, _ = validate_privacy(root)
        assert any("personal name" in finding.message for finding in findings)
        cases += 1

    print(f"validator self-test OK: {cases} cases")
    return 0


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("root", nargs="?", default=".", type=Path)
    parser.add_argument("--self-test", action="store_true")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv or sys.argv[1:])
    if args.self_test:
        return run_self_tests()

    root = args.root.resolve()
    findings, skill_count, scanned_count = validate_repository(root)
    if findings:
        for finding in findings:
            print(finding.render(root), file=sys.stderr)
        print(f"repository validation failed: {len(findings)} finding(s)", file=sys.stderr)
        return 1
    print(f"repository validation OK: {skill_count} skills, {scanned_count} text files scanned")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
