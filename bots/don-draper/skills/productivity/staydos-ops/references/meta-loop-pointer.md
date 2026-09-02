# Meta Loop pointer

Meta Loop is StaydOS's multi-brand paid-media test state machine. It is separate from recurring sales scorecards and general CRM funnel reporting.

## Source order

1. StaydOS Meta Loop product contract.
2. StaydOS loop registry.
3. `stayd-meta-loop` skill.

Contract beats skill; skill beats chat.

## Shared rules

1. Commercial outcomes are CRM rows qualified under the current contract.
2. Provider-reported lead actions are health evidence; never dual-count them with CRM outcomes.
3. Verify live payload keys before claiming an attribution join.
4. Distinguish present-but-null fields from missing schema.
5. Check delivery fairness and learning completion before a performance judgment.

Use the general StaydOS operations pathway for recurring sales scorecards and CRM reporting. Use `stayd-meta-loop` for run health, trial evidence, attribution, judge readiness, and writeback.
