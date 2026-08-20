# Meta Loop diagnosis checklist

**Always open first:** stayd-os `docs/loops/meta-loop/CONTRACT.md`  
Registry: `docs/LOOP_REGISTRY.md`

## PostgREST pulls (service_role)

Prefer `select=*` on one row when columns are uncertain.

| Check | Table / filter |
|-------|----------------|
| Active runs | `meta_loop_runs` stage not in done/entropy/killed |
| Dashboard | `meta_loop_run_dashboard` |
| Stalled | `meta_loop_stalled_runs` |
| Config | `meta_loop_brand_configs` |
| Creatives | `meta_loop_creatives?run_id=eq.<uuid>` |
| Snapshots | `meta_loop_trial_snapshots?creative_id=in.(…)` — **no run_id** |
| Decisions / approvals / events | by `run_id` |
| Pains | `meta_loop_pains` brand order rank |
| Harness ads | `meta_ads?adset_id=eq.<harness>` |
| CRM loop leads | `leads` brand + trial window + `meta_loop_lp` / LP |

### Known columns (2026-08)

**meta_loop_runs:** `id, brand_config_id, brand_id, objective, stage, trial_start_at, trial_end_at, notes, created_at, updated_at, hidden, leased_until`  
**snapshots:** `creative_id, brand_id, snapshot_date, spend_cents, impressions, link_clicks, link_ctr, cpc_cents, leads, cpl_cents, raw`  
**leads:** includes `meta_ad_id`, `meta_adset_id`, `meta_campaign_id`, utm_*, `raw_payload` — **ids often null** on loop LPs

## Commercial qualification (mandatory)

For each CRM loop lead:

1. `lead_source` / payload `lead_source` = `meta_loop_lp`
2. Property state in **service area** (Renjoy → CO). HI/NC/etc. = **not commercial**
3. Not spam
4. Blank state = **not commercial** until fail-closed
5. Map to creative via `utm_content` / LP until `meta_ad_id` populated

**Commercial count ≠ row count.**

## Health (Insights)

Snapshot `leads` column = Insights-derived. Report beside commercial; **do not add them together**.

OOA → no Pixel Lead is **intentional** (`LeadForm.tsx`).

## Join keys

| Prefer | Avoid assuming |
|--------|----------------|
| `utm_content`, LP slug | `utm_id` always present |
| `creatives.meta_ad_id` when set | `raw_payload.run_id` as UUID |
| Check payload keys on 1–3 sample rows first | “column missing” when value is null |

## Delivery skew

Per creative: spend %, impr, clicks, insights leads, **qualified CRM**.  
Flag >~60–70% spend concentration or creatives under impression floors.

## Learning health

| Symptom | Meaning |
|---------|---------|
| pains untested, times_used=0 | No writeback learning |
| never writeback/done | Cycle incomplete |
| winners_*=null | Cannot promote that brand |

## Report shape

1. Verdict  
2. Board: commercial CRM + insights health  
3. Per-creative delivery  
4. P0–P2 vs contract  
5. Actions / Open calls / L3  

## Code map

| Concern | Path |
|---------|------|
| Contract | `docs/loops/meta-loop/CONTRACT.md` |
| Form | `src/app/lp/[slug]/LeadForm.tsx` |
| Intake | `src/app/api/leads/inbound/route.ts` |
| Trial | `src/lib/meta-loop/trial-reader.ts` |
| Judge | `judge.ts`, `judge-rules.ts` |
| Writeback | `writeback.ts` |
