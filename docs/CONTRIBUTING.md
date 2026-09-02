# Contribution and change process

## Change classes

| Change | Required review |
|---|---|
| Documentation wording with no policy effect | repository maintainer |
| Profile lens, sources, or domain skill | repository maintainer + department owner |
| Runtime, apply tooling, shared skills, or fleet policy | repository maintainer + fleet operator |
| Credentials, permissions, channels, write powers, or security controls | repository maintainer + security owner |
| External audience, spend, publish/send, deletion, or production authority | security owner + department owner with an explicit rollout plan |

## Workflow

1. Start from current `main` and inspect the working tree. Preserve unrelated work.
2. State the intended outcome, affected profile, risk, owner roles, and rollback.
3. Read the relevant durable standard, profile files, local skills, and source contract.
4. Make the smallest coherent change. Put shared behavior in root `skills/`; keep exceptional behavior bot-local.
5. Never include credentials, contacts, personal data, production IDs, sessions, memories, or home paths.
6. Run repository validation and the profile dry run.
7. Review the full diff, including generated or copied files.
8. Obtain the reviews required by the change class.
9. Commit the reviewed source. Do not apply uncommitted normal changes.
10. Apply the exact commit, restart only the target gateway, and run acceptance.
11. If verification fails, do not finalize success or add a check reaction. Repair or roll back.
12. Record durable lessons in the relevant standard or skill, not in transient chat.

## Required local verification

```bash
python3 tools/validate_repo.py .
python3 -m unittest discover -s tests -v
find . -type f -name '*.sh' -not -path './.git/*' -exec bash -n {} +
python3 -m compileall -q scripts tools tests
git diff --check
./scripts/apply-bot.sh <agent-slug> --dry-run
```

Parse every tracked YAML file with a real YAML parser before review. CI repeats the validator and unit tests on pushes to `main` and pull requests.

## Skill rules

- Every `SKILL.md` starts at byte one with YAML frontmatter.
- `name` and `description` are required.
- Names are unique lowercase hyphenated identifiers.
- Descriptions are concise and at most 1024 characters.
- Bodies contain actionable operating guidance.
- Do not keep backup, archive, copy, or disabled skill files in the tree.
- Keep class-level rules reusable. Move bulky checklists or protocol details into `references/` when that improves navigation.

## Rollout evidence

The reviewer should be able to answer:

- What changed and why?
- Which profile and live path will change?
- Which sources or permissions are affected?
- What proves positive behavior?
- What proves the negative boundary?
- What proves Slack quiet-mode and reaction correctness?
- What exact commit and gateway command restore the previous accepted state?

## Emergency changes

Containment can precede normal review when a credential, external action, or unsafe permission is active. Prefer revocation, disabling the narrow integration, or stopping the exact profile gateway. Do not delete evidence. Capture or revert any manual runtime drift, then follow the normal review and acceptance path before restoration.
