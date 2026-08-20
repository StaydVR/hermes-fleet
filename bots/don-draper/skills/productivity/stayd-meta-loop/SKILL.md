---
name: stayd-meta-loop
description: "Use when auditing or operating Stayd OS Meta Loop."
version: 2.0.0
metadata:
  hermes:
    tags: [stayd, meta-loop, marketing, meta-ads, staydos, supabase, loop-contract]
    related_skills: [staydos-ops, stayd-hermes-fleet]
---

# Stayd Meta Loop ops

Operate and diagnose the **Meta Loop** using the **product contract first**.

**Contract (source of truth):** in `StaydVR/stayd-os`:
`docs/loops/meta-loop/CONTRACT.md`  
**Registry:** `docs/LOOP_REGISTRY.md`  
**Template (all loops):** `docs/loops/_TEMPLATE.md`

**Conflict rule:** Contract > this skill > chat. If this skill drifts, patch it and fleet-apply — do not freestyle scoreboard rules.

Not for Tuesday sales scorecards (`staydos-ops`) or Hermes fleet secrets (`stayd-hermes-fleet`).

## When to use

- Reid / Mr. Stayd asks to review, audit, or improve the Meta Loop
- Active run health, pre-judge checks, attribution mysteries
- Before crowning winners, killing a run, or claiming “0 leads” / “ads don’t convert”

## Identity map

| Resource | Value |
|----------|--------|
| Product | Stayd OS · `https://os.stayd.co` |
| Code | `StaydVR/stayd-os` · `src/lib/meta-loop/*` |
| Contract | `docs/loops/meta-loop/CONTRACT.md` |
| Live DB | `yvlsclsqeadtuzchywad` |
| Cron | `/api/cron/meta-loop`, `/api/cron/meta-loop-health` |

## Access

Same as `staydos-ops`: management token → project API keys → service_role. Browser-like `User-Agent`. Never print tokens. Never store service_role in git/fleet.

## Settled scoreboard (Reid 2026-08-20) — memorize

1. **Commercial truth = qualified CRM leads only**
   - `meta_loop_lp` (or clear loop LP)
   - **In brand service area** (Renjoy = CO area)
   - Not spam
   - Blank `property_state` → **not qualified** for commercial score (fail-open hole is In flight)
2. **Meta Insights “lead” actions = health only** — trial snapshots
3. **Never dual-count** Insights + CRM into one number
4. **OOA no Pixel Lead is by design** (`LeadForm` + inbound) — not a counting bug when Insights = 0 for HI/NC
5. Always report a table: `commercial_qualified_crm | insights_health | delta_note`

### Do not

- Say “3 CRM leads” without qualification filter
- Propose dual-count Meta+CRM as the fix
- Claim `utm_id` join works without checking payload keys on live rows
- Treat `raw_payload.run_id` as `meta_loop_runs.id` (often campaign **name**)
- Crown/kill on starved creatives without calling delivery unfair
- Trust snapshot spend without filtering prior-run creatives

## Join keys (verify live)

| Key | Typical state | Use |
|-----|---------------|-----|
| `leads.meta_ad_id` | Column **exists**, often **null** | Target join when filled |
| `raw_payload.utm_id` | Often **absent** | Do not assume |
| `utm_content` | Present | Best current creative crumb |
| LP URL / slug | Present | Match creatives |
| Campaign UTM | Harness name | Context only |

**In flight:** form → intake must persist ad id into `meta_ad_id` (and campaign/adset if available). Read `LeadForm.tsx` + `api/leads/inbound` before proposing schema work.

## Live diagnosis sequence

1. **Re-read contract** Settled / In flight / Open calls (or latest on main after merge).
2. **Active runs** — `meta_loop_runs.stage` not in (`done`,`entropy`,`killed`); prefer dashboard views.
3. **Brand config** — harness + **winners_*** ids, gates, `daily_cap_cents` vs real Meta budget (flag contradictions).
4. **Creatives** — `meta_ad_id`, status vs `meta_ads.status` (staged DB + ACTIVE Meta is common).
5. **Snapshots** — by `creative_id`; **no run_id** on snapshots; watch prior-run bleed.
6. **Commercial CRM** — qualify in-area / not spam / blank-state; per-creative via `utm_content` / LP until `meta_ad_id` works.
7. **Insights health** — snapshot leads; explain delta vs CRM (OOA suppression vs tracking gap).
8. **Delivery skew** — spend/impr share; starve callout before ranking.
9. **Learning** — any `writeback`/`done`? pains `won`/`lost`/`times_used`?
10. **Decisions / approvals / events**

## Code still In flight vs Settled

| Area | Today (verify) | Settled target |
|------|----------------|----------------|
| Judge | Insights + can crown 0-lead CTR past impr floor | Commercial CRM; two-tier winner (open call) |
| Trial-reader | Insights lead actions | Keep as health; add CRM qualified |
| Attribution | meta_ad_* null on many loop LPs | Intake writes ids |
| Delivery | ABO skew | Prefer 1 ad set / creative (ops) |
| `daily_cap_cents` | Config decoration risk | Enforce or delete |
| Haven | No full winners path | Hold until Renjoy `done` |

## Agent DoD (before performance claims)

From contract §11 — all boxes. Especially: qualification, join-key proof, no dual-count, delivery fairness, learning status, L3 separation.

## Operator output shape

1. Verdict (one line)  
2. Live board: run, stage, window, spend, **commercial CRM**, **insights health**  
3. Per-creative delivery + qualified CRM  
4. Good / not-great (P0–P2) aligned to contract  
5. Actions + owners; mark Open calls for Reid  
6. Explicit L3 items  

## After audits

- If **product truth** changed → PR to `docs/loops/meta-loop/CONTRACT.md` + registry `last_verified` (same PR as code when code changes).
- If **operator method** changed → update this skill → Mr. Stayd fleet commit + `apply-bot.sh don-draper`.
- Optional: dated line in profile `memories/MEMORY.md` under Settled calls.

## Pitfalls

1. Snapshot leads ≠ commercial truth  
2. Raw `meta_loop_lp` count includes OOA  
3. `meta_ad_id` column empty ≠ “column missing”  
4. Learning never closes without writeback→done  
5. Winners ad set required per brand for promotion  
6. Human enables ads after trial_start  
7. ABO skew invalidates ranking  
8. Three competing budget numbers  
9. Wrong Supabase project  
10. Tokens in Slack / service_role in git  

## References

- Contract: stayd-os `docs/loops/meta-loop/CONTRACT.md`
- Checklist: `references/diagnosis-checklist.md`
- Repo docs: `META_LOOP_*.md`, `meta-loop-audit-2026-08-13.md`
- `staydos-ops` for Supabase access pattern
