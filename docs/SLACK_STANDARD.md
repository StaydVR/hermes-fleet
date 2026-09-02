# Slack operating standard

This standard applies to every fleet profile. It is both a user-experience contract and a completion-integrity control.

## Required behavior

1. Do not expose chain-of-thought, hidden reasoning, thought summaries, or thought streaming.
2. Do not stream tokens, tool progress, live status, native task cards, long-running notices, heartbeat updates, or interim assistant messages into Slack.
3. Send exactly one concise final receipt. Never double-message a final answer.
4. Add `:eyes:` automatically when processing begins.
5. Remove `:eyes:` only when processing ends.
6. Add `:white_check_mark:` only after the agent has independently verified the requested outcome.
7. A failed, blocked, partial, timed-out, or unverified run must not receive a check reaction. Runtime failure may use `:x:`; the final receipt must state the blocker plainly.
8. Channel messages require an initial explicit mention of the bot.
9. DMs work normally for authorized users.
10. Once a valid channel thread begins, reasonable continuation in that thread does not require a repeated mention.
11. Ignore channel messages addressed to other humans or bots.
12. Channel replies live in threads and never broadcast back into the channel.
13. Bot-to-bot messages are accepted only when the receiving bot is explicitly mentioned. Avoid loops and do not respond to ambient bot traffic.

The agent must not return a success outcome or finalize its receipt until domain-specific verification completes. Reaction correctness depends on truthful processing outcomes.

## Required Hermes overlay

Every `runtime-config.yaml` must include:

```yaml
agent:
  gateway_notify_interval: 0

display:
  interim_assistant_messages: false
  tool_progress: "off"
  thinking_progress: false
  live_status: "off"
  platforms:
    slack:
      interim_assistant_messages: false
      tool_progress: "off"
      thinking_progress: false
      streaming: false
      long_running_notifications: false
      busy_ack_detail: false
      live_status: "off"

gateway:
  streaming:
    enabled: false

platforms:
  slack:
    reply_to_mode: first
    extra:
      reply_in_thread: true
      reply_broadcast: false
      native_task_cards: false
      allow_bots: mentions

slack:
  require_mention: true
  strict_mention: false
  thread_require_mention: false
  ignore_other_user_mentions: true
```

The non-secret runtime default is:

```text
SLACK_REACTIONS=true
```

Hermes adds `eyes` at processing start, removes it at completion, then adds `white_check_mark` only for a successful processing outcome and `x` for failure. The Slack app therefore needs `reactions:write` in its installed OAuth grant.

## Receipt format

Keep the final message proportional to the task. For implementation work, include:

- outcome;
- meaningful files or systems changed;
- verification performed and result;
- blocker or rollback note only when relevant.

Do not narrate tools, token usage, internal reasoning, or every intermediate step.

## Acceptance cases

- DM receives one response.
- Initial channel mention starts one thread.
- Unmentioned new channel message gets no response.
- Thread continuation receives one in-thread response without a new mention.
- A message mentioning another human is ignored unless the bot is also clearly addressed.
- A bot message without an explicit mention is ignored.
- Start reaction appears once.
- Verified success replaces start state with a check.
- Forced failure has no check.
- No interim text, live status, task card, or channel broadcast appears.
