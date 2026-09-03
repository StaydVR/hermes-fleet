---
name: stayd-slack-standard
description: "Use for every Stayd Hermes Slack interaction and when configuring or testing exact-message mentions, threads, lifecycle reactions, working status, bot traffic, and final receipts."
version: 1.0.0
author: Stayd Fleet
license: MIT
metadata:
  hermes:
    tags: [stayd, hermes, slack, reactions, threads]
---

# Stayd Slack standard

Apply this behavior to every Slack turn. It does not expand the agent's audience, tools, permissions, or authority.

## Decide whether to respond

- Respond normally to an authorized DM.
- In every shared Slack surface—channels, existing threads, and group DMs—require this bot's explicit mention on that exact message.
- Do not treat an earlier mention, a prior bot reply, or participation in the thread as admission for a later unmentioned message.
- Ignore ambient shared-surface traffic and messages that open with another person's mention.
- Ignore bot messages unless this bot is explicitly mentioned on that exact message. Never create a bot-to-bot response loop.

## While working

- For an eligible message, let Hermes add `:eyes:` once when processing begins. Ignored shared-surface messages get no reply and no reaction.
- Use only the normal `is thinking...` indicator and compact verb footer for working state. Never expose command or path arguments.
- Do not send reasoning, thoughts, token streams, tool progress, interim assistant text, native task cards, long-running notices, busy-ack detail, or heartbeat updates.
- Keep shared-surface work inside the source thread and never broadcast the reply to the channel.
- If blocked, finish with one concise blocker receipt; do not drip repeated status messages.

## Finish honestly

1. Complete the requested work.
2. Run the real domain verification gate.
3. Read the authoritative result or final artifact.
4. Return success only when verification passed.
5. Send exactly one concise final receipt.

Hermes removes `:eyes:` at completion and adds `:white_check_mark:` for `SUCCESS` or `:x:` for `FAILURE`. The reaction reflects the processing outcome and never replaces independent verification. Do not return success early merely to improve the Slack reaction.

## Final receipt

Lead with the outcome. Include the material change and verification result. Add a blocker or rollback note only when relevant. Do not repeat the request, narrate every tool, expose hidden reasoning, or send a second follow-up message.

## Configuration source

The full required overlay, env default, OAuth requirement, and acceptance cases live in `docs/SLACK_STANDARD.md`. If runtime behavior differs from that document, treat it as a configuration or gateway defect and route it through the fleet change process.
