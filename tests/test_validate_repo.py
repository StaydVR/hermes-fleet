from __future__ import annotations

import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from tools.validate_repo import validate_privacy, validate_repository, validate_skills, write_skill


REPO_ROOT = Path(__file__).resolve().parents[1]
COMPOSE_SCRIPT = REPO_ROOT / "scripts/compose-skills.py"


class SkillValidatorTests(unittest.TestCase):
    def test_valid_skill_passes(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            write_skill(root, "skills/reporting", "reporting-skill")
            findings, count = validate_skills(root)
            self.assertEqual(1, count)
            self.assertEqual([], findings)

    def test_duplicate_name_fails(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            write_skill(root, "skills/reporting", "reporting-skill")
            write_skill(root, "bots/example/skills/local", "reporting-skill")
            findings, _ = validate_skills(root)
            self.assertTrue(any("duplicate skill name" in finding.message for finding in findings))

    def test_empty_body_fails(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            write_skill(root, "skills/reporting", "reporting-skill", body="")
            findings, _ = validate_skills(root)
            self.assertTrue(any("body" in finding.message for finding in findings))

    def test_backup_skill_fails(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            write_skill(root, "skills/archive/reporting", "reporting-skill")
            findings, _ = validate_skills(root)
            self.assertTrue(any("backup/archive" in finding.message for finding in findings))


class PrivacyValidatorTests(unittest.TestCase):
    def test_secret_token_fails(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "unsafe.txt").write_text("xoxb-" + "A" * 24, encoding="utf-8")
            findings, _ = validate_privacy(root)
            self.assertTrue(any("credential" in finding.message.lower() for finding in findings))

    def test_personal_email_fails(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "unsafe.txt").write_text("person" + "@company.test", encoding="utf-8")
            findings, _ = validate_privacy(root)
            self.assertTrue(any("email" in finding.message for finding in findings))

    def test_safe_env_names_and_placeholders_pass(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "safe.env.example").write_text(
                "SERVICE_API_TOKEN=\nSECOND_TOKEN=<runtime-secret>\n",
                encoding="utf-8",
            )
            findings, _ = validate_privacy(root)
            self.assertEqual([], findings)

    def test_role_field_with_personal_name_fails(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "unsafe.txt").write_text("Owner: Avery Exampleton\n", encoding="utf-8")
            findings, _ = validate_privacy(root)
            self.assertTrue(any("personal name" in finding.message for finding in findings))

    def test_home_path_and_phone_fail(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "unsafe.txt").write_text(
                "/Users/" + "operator/work\n" + "+1 " + "212-" + "555-" + "0199",
                encoding="utf-8",
            )
            findings, _ = validate_privacy(root)
            messages = {finding.message for finding in findings}
            self.assertIn("home-directory path is not allowed", messages)
            self.assertIn("phone number is not allowed", messages)

    def test_production_project_reference_fails(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "unsafe.txt").write_text("project_ref=" + "a" * 20, encoding="utf-8")
            findings, _ = validate_privacy(root)
            self.assertTrue(any("project reference" in finding.message for finding in findings))


class CompositionTests(unittest.TestCase):
    def test_shared_and_local_skills_compose(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            shared = root / "shared"
            local = root / "local"
            destination = root / "output"
            write_skill(root, "shared/core", "core-skill")
            write_skill(root, "local/productivity/report", "report-skill")
            result = subprocess.run(
                [
                    sys.executable,
                    str(COMPOSE_SCRIPT),
                    "--shared",
                    str(shared),
                    "--bot",
                    str(local),
                    "--destination",
                    str(destination),
                ],
                check=False,
                capture_output=True,
                text=True,
            )
            self.assertEqual(0, result.returncode, result.stderr)
            self.assertTrue((destination / "core/SKILL.md").is_file())
            self.assertTrue((destination / "productivity/report/SKILL.md").is_file())

    def test_composition_rejects_duplicate_names(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            shared = root / "shared"
            local = root / "local"
            write_skill(root, "shared/core", "same-skill")
            write_skill(root, "local/core", "same-skill")
            result = subprocess.run(
                [
                    sys.executable,
                    str(COMPOSE_SCRIPT),
                    "--shared",
                    str(shared),
                    "--bot",
                    str(local),
                    "--check-only",
                ],
                check=False,
                capture_output=True,
                text=True,
            )
            self.assertNotEqual(0, result.returncode)
            self.assertIn("duplicate skill name", result.stderr)


class RepositoryValidatorTests(unittest.TestCase):
    def test_minimal_repository_passes(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            write_skill(root, "skills/core", "core-skill")
            findings, skill_count, scanned_count = validate_repository(root)
            self.assertEqual([], findings)
            self.assertEqual(1, skill_count)
            self.assertGreater(scanned_count, 0)


if __name__ == "__main__":
    unittest.main()
