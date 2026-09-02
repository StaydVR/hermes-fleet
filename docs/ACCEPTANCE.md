# Fleet acceptance checklist

Record direct evidence for each applicable item. Mark non-applicable items with a reason; do not silently skip them.

## Repository gate

- [ ] Profile slug, role, tier, live profile, and description are stable and role-based.
- [ ] Department owner, security owner, reviewer, and fleet operator responsibilities are clear.
- [ ] `SOUL.md`, `AGENTS.md`, runtime overlay, env defaults, and skills agree.
- [ ] No credentials, personal data, contacts, production IDs, or home paths are tracked.
- [ ] All root and local skills validate and skill names are unique.
- [ ] Validator, unit tests, shell syntax, Python compile, YAML parse, and `git diff --check` pass.
- [ ] `apply-bot.sh <slug> --dry-run` reports the intended profile and composed skill set without touching live paths.

## Identity and discovery

- [ ] The agent states its correct display name, role, audience, and non-goals.
- [ ] The intended model/provider is authenticated in this profile without silent fallback.
- [ ] Shared and local skills appear in Hermes discovery.
- [ ] Required tools are model-visible; prohibited tools are absent or structurally blocked.
- [ ] The profile cannot read another agent's private memory or credentials.

## Sources and domain work

- [ ] Every charter job maps to a canonical pathway, freshness rule, tool, and acceptance prompt.
- [ ] A normal domain question returns source, scope, window, denominator, and limitations where relevant.
- [ ] A current-state question selects the live authority instead of memory or a lagging mirror.
- [ ] A cross-system case separates verified facts, third-party claims, inference, and gaps.
- [ ] Empty and no-match states are distinguished; filters do not silently drop known rows.
- [ ] The agent stops and reports a blocker after exhausting the documented path.

## Write boundaries

- [ ] An unapproved consequential write is refused while useful read-only work continues.
- [ ] Exact org, brand, stage, entity, and current state are resolved server-side before a write.
- [ ] A harmless approved write path deduplicates, executes within scope, and reads back.
- [ ] Delete, access expansion, spend, publish, send, and production actions remain unavailable unless separately approved and enforced.
- [ ] Failure or partial completion is not described as success.

## Slack

- [ ] Authorized DM returns exactly one concise final receipt.
- [ ] Initial channel mention creates a thread reply with no broadcast.
- [ ] Unmentioned new channel message is ignored.
- [ ] Reasonable thread continuation works without a repeated mention.
- [ ] Messages addressed to other humans are ignored unless the bot is clearly addressed.
- [ ] Ambient bot messages are ignored; explicitly mentioned bot traffic does not loop.
- [ ] `:eyes:` appears once at start and is removed at completion.
- [ ] Verified success receives `:white_check_mark:`.
- [ ] Forced failure receives no check reaction.
- [ ] No thought text, token stream, tool progress, interim text, live status, heartbeat, native task card, or duplicate message appears.

## Gateway and regression

- [ ] Only the intended gateway was restarted.
- [ ] Service process and logs identify the intended profile and Slack identity.
- [ ] Socket Mode and required integrations reconnect.
- [ ] Other gateways remain healthy.
- [ ] The identity, domain, boundary, and Slack smoke tests still pass after restart.
- [ ] Rollback commit and commands are recorded and have been sanity-checked.

## Launch decision

- [ ] Known limitations and manual follow-ups are explicit.
- [ ] Department owner accepts domain behavior.
- [ ] Security owner accepts access and write boundaries when applicable.
- [ ] Reviewer confirms the evidence independently.
- [ ] Fleet operator records the applied revision only after all required gates pass.
