---
name: stayd-slack-standard
description: "Use for every Stayd Hermes Slack interaction and when configuring or testing mentions, threads, lifecycle reactions, quiet-mode, bot traffic, and final receipts."
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
- In a channel, require the bot's initial explicit mention.
- Continue reasonably inside a thread the bot validly joined; do not require a repeated mention.
- Ignore ambient channel traffic and messages addressed to other humans.
- Ignore bot messages unless this bot is explicitly mentioned. Never create a bot-to-bot response loop.

## While working

- Let Hermes add `:eyes:` when processing begins.
- Do not send reasoning, thoughts, token streams, tool progress, interim assistant text, live status, native task cards, long-running notices, or heartbeat updates.
- Keep channel work inside the source thread and never broadcast the reply to the channel.
- If blocked, finish with one concise blocker receipt; do not drip repeated status messages.

## Finish honestly

1. Complete the requested work.
2. Run the real domain verification gate.
3. Read the authoritative result or final artifact.
4. Return success only when verification passed.
5. Send exactly one concise final receipt.

Hermes removes `:eyes:` at completion and adds `:white_check_mark:` only for a successful processing outcome. A failed run may receive `:x:` and must never receive a check. Do not return success early merely to improve the Slack reaction.

## Final receipt

Lead with the outcome. Include the material change and verification result. Add a blocker or rollback note only when relevant. Do not repeat the request, narrate every tool, expose hidden reasoning, or send a second follow-up message.

## Configuration source

The full required overlay, env default, OAuth requirement, and acceptance cases live in `docs/SLACK_STANDARD.md`. If runtime behavior differs from that document, treat it as a configuration or gateway defect and route it through the fleet change process.
