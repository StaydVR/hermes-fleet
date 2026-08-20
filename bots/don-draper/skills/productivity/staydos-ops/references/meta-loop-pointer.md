# Meta Loop (pointer from staydos-ops)

Meta Loop is **not** the Tuesday sales scorecard. It is Stayd OS’s multi-brand Meta ads test state machine.

**Product contract (source of truth):**  
`StaydVR/stayd-os` → `docs/loops/meta-loop/CONTRACT.md`  
**Registry:** `docs/LOOP_REGISTRY.md`  
**Load skill:** `stayd-meta-loop`

## Shared hard rules (Settled 2026-08-20)

1. **Commercial scoreboard = qualified CRM** (in-area, not spam; blank state not qualified).
2. **Meta Insights leads = health only** — never dual-count with CRM.
3. **OOA no Pixel Lead is by design** — not automatically a tracking bug.
4. Before claiming joins: verify payload keys; `leads.meta_ad_id` exists but is often null; `utm_id` often absent from payload.
5. Contract > skill > chat.

## When to hand off

| Task | Skill |
|------|--------|
| Brian/Renjoy Tue scorecard, RevMaaS, CRM funnel | `staydos-ops` |
| Meta Loop run audit, trial health, judge, writeback | `stayd-meta-loop` |
