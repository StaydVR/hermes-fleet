---
name: stayd-meta-loop
description: "Use when auditing or operating the StaydOS Meta Loop under its current product contract."
version: 3.0.0
metadata:
  hermes:
    tags: [stayd, meta-loop, marketing, meta-ads, staydos, supabase, loop-contract]
    related_skills: [staydos-platform-architecture, staydos-agent-api]
---

# Stayd Meta Loop operations

Operate and diagnose the Meta Loop from its current product contract. This skill describes method; it does not replace live product truth or grant campaign write authority.

## Source order

1. Read the Meta Loop contract and loop registry in the StaydOS repository.
2. Read current implementation and migrations for the affected stage.
3. Query the registered live StaydOS views or bounded APIs.
4. Use this skill for the diagnosis sequence and output shape.

Contract beats skill; skill beats chat. If the contract and live behavior diverge, report the gap and route a product decision rather than inventing a new rule.

## When to use

- active-run health and stage progression;
- tracking, attribution, or delivery diagnosis;
- pre-judge review before ranking or stopping a creative;
- writeback and learning-cycle completion;
- a claim that leads are absent or ads are not converting.

## Authority

- Read approved campaign, run, snapshot, and qualified CRM evidence.
- Diagnose and draft recommendations.
- Do not activate, pause, publish, change spend, modify audiences, or perform external writes without the exact approved bounded pathway.
- Treat task acceptance as permission to investigate and draft, not to go live.

## Commercial and health evidence

Keep two measures separate:

1. **Commercial outcome:** CRM records that meet the current contract's source, service-area, spam, and required-field qualification rules.
2. **Platform health:** provider-reported lead actions and delivery signals from trial snapshots.

Never add the two into one lead count. Report both with a delta note. A raw CRM row count is not a qualified commercial count.

Read the current contract for exact qualification rules. Blank or uncertain qualification fields do not become positive outcomes by assumption.

## Attribution

- Prefer explicit provider entity ids when they are populated and verified.
- Inspect a bounded sample of live payload keys before relying on a join.
- Use approved UTM or landing-page crumbs only as documented fallback evidence.
- Do not treat a campaign label as a run UUID.
- Distinguish a missing column from a present but null value.
- State confidence and unmatched rows.

## Diagnosis sequence

1. Re-read settled, in-flight, and open sections of the current contract.
2. Load active runs and the registered dashboard or stalled-run views.
3. Resolve the exact leaf brand and its current config, gates, caps, and promotion prerequisites.
4. Load creatives and compare recorded state with current provider state through an approved read path.
5. Load snapshots by the documented join key and exclude prior-run bleed.
6. Qualify CRM outcomes under the contract and map them to creatives only with proven keys.
7. Report provider health beside commercial outcomes without dual-counting.
8. Calculate delivery share and flag material starvation before ranking.
9. Check whether writeback and learning completed.
10. Review decisions, approvals, and events before recommending a state change.

## Fairness and decision safety

- Do not crown or stop a creative whose delivery was materially starved without calling out the unfair comparison.
- Do not infer commercial failure from click-through or impression data alone.
- Do not trust stored budget fields without comparing them to the authoritative provider read.
- Keep open product calls with the product owner role.
- Separate recommendations from actions requiring human approval.

## Output

1. One-line verdict.
2. Run, stage, window, spend, qualified commercial outcomes, and platform health.
3. Per-creative delivery share and qualified outcomes.
4. Proven data-quality or contract gaps, ranked by severity.
5. Actions with owner roles and verification gates.
6. Explicit approvals required.

Before finalizing, confirm scope, qualification, join proof, no dual-counting, delivery fairness, learning status, and the applicable approval boundary. Use `references/diagnosis-checklist.md` for the working checklist.
