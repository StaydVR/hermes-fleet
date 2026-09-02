# Meta Loop diagnosis checklist

Open the current StaydOS Meta Loop contract and loop registry first.

## Pulls

Use the registered live views or bounded APIs for:

- active runs and stalled runs;
- leaf-brand config and promotion prerequisites;
- creatives for the exact run;
- trial snapshots by the documented creative key;
- qualified CRM outcomes;
- decisions, approvals, events, and learning records.

Prefer a minimal field list once schema is known. When schema is uncertain, inspect one bounded row without printing confidential fields or raw credentials.

## Commercial qualification

For each candidate CRM outcome:

1. Confirm the current contract's accepted source.
2. Confirm it is inside the leaf brand's approved service scope.
3. Exclude spam and invalid rows.
4. Treat missing required qualification fields according to the contract; do not guess.
5. Map to creative only through a verified provider id or documented fallback key.

Commercial count is not raw row count.

## Platform health

Provider-derived lead actions are health evidence. Report them beside qualified CRM outcomes and explain the delta. Never add them together.

## Join proof

- Inspect current payload keys on a bounded sample.
- Prefer populated explicit ids.
- State when a field exists but is null.
- Never assume a label is the internal run id.
- Report unmatched rows and join confidence.

## Delivery fairness

For each creative report spend share, impressions, clicks, provider health actions, and qualified CRM outcomes. Flag material concentration and creatives below the contract's decision floor before ranking.

## Learning health

Check whether the run reached writeback and completion, whether learning records changed, and whether the leaf brand has the promotion prerequisites required by contract.

## Report shape

1. Verdict.
2. Commercial outcome and platform-health board.
3. Per-creative delivery and qualified outcomes.
4. Data-quality, fairness, and contract gaps.
5. Actions, owner roles, open product calls, and explicit approvals.

## Verification

Before marking success, read back the current run state and any internal write. Campaign activation, spend, publishing, pausing, or external provider mutation requires a separately approved bounded path.
