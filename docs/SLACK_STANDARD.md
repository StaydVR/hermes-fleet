# Slack operating standard

This standard applies to every fleet profile. It is both a user-experience contract and a completion-integrity control.

## Required behavior

1. Do not expose chain-of-thought, hidden reasoning, thought summaries, or thought streaming.
2. Do not stream tokens, thoughts, tool progress, native task cards, long-running notices, heartbeat updates, or interim assistant messages into Slack. The only working signals beyond reactions are Slack's normal typing indicator and compact footer status.
3. Send exactly one concise final receipt. Never double-message a final answer.
4. Add `:eyes:` automatically when processing begins.
5. Remove `:eyes:` only when processing ends.
6. Add `:white_check_mark:` only after the agent has independently verified the requested outcome.
7. A failed, blocked, partial, timed-out, or unverified run must not receive a check reaction. A `FAILURE` outcome receives `:x:`; the final receipt must state the blocker plainly.
8. Authorized 1:1 DMs work normally without requiring a mention.
9. Every message in a shared Slack surface requires an explicit mention of the bot on that exact message. Shared surfaces include channels, existing threads, and group DMs.
10. An earlier mention, prior bot reply, or bot participation in a thread does not admit later unmentioned replies.
11. With `ignore_other_user_mentions: true`, skip messages that open with another person's mention.
12. Shared-surface replies stay in the source thread and never broadcast back into the channel.
13. Bot-to-bot messages are accepted only when the receiving bot is explicitly mentioned on that exact message. Keep `allow_bots: mentions`, avoid loops, and ignore ambient bot traffic.

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
      live_status: verb

gateway:
  streaming:
    enabled: false
  platforms:
    slack:
      typing_indicator: true
      typing_status_text: "is thinking..."

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
  strict_mention: true
  thread_require_mention: true
  ignore_other_user_mentions: true
```

The non-secret runtime default is:

```text
SLACK_REACTIONS=true
```

For every eligible message—an authorized 1:1 DM or a shared-surface message that passes the exact-message mention gate—Hermes adds `eyes` once at processing start, removes it at completion, then adds `white_check_mark` for `SUCCESS` or `x` for `FAILURE`. Ignored or unmentioned shared-surface messages receive neither a reply nor a reaction. The Slack app therefore needs `reactions:write` in its installed OAuth grant.

A success reaction reports Hermes's processing outcome; it does not replace independent verification. The agent must verify the requested result from the authoritative source before returning `SUCCESS`.

## Working status

`gateway.platforms.slack.typing_indicator: true` with `typing_status_text: "is thinking..."` enables Slack's normal thinking indicator. `display.platforms.slack.live_status: verb` uses `assistant.threads.setStatus` to show a compact footer such as `thinking`, `reading`, or `searching`, without command or path arguments. The Slack app needs `assistant:write` for this footer status.

Keep interim assistant messages, thinking progress, tool progress, response streaming, long-running notifications, busy-ack detail, native task cards, and gateway streaming disabled. The typing indicator and footer are working-state UI, not extra assistant messages; Slack must still receive one final reply rather than streamed thoughts or status messages. Slack's generic inline AI placeholders are separate from Hermes's footer status and are not controlled by `assistant:write`.

## OAuth rollout

Apply the `assistant:write` scope to one profile at a time:

1. In the Slack app, open **OAuth & Permissions** → **Bot Token Scopes** and add `assistant:write`. Confirm `reactions:write` is also present.
2. Reinstall the app to the workspace and confirm Slack shows the **Success** state.
3. If and only if Slack rotates the bot token, securely replace that profile's `SLACK_BOT_TOKEN` in its protected runtime secret store. Never put the token in this repository.
4. Restart only that profile's gateway because Hermes runtime configuration is loaded at startup.
5. Verify Socket Mode reconnects as the intended app identity.
6. Send an explicit mention in a shared surface and confirm the in-thread reply, lifecycle reactions, and footer status while it works.

## Receipt format

Keep the final message proportional to the task. For implementation work, include:

- outcome;
- meaningful files or systems changed;
- verification performed and result;
- blocker or rollback note only when relevant.

Do not narrate tools, token usage, internal reasoning, or every intermediate step.

## Acceptance cases

- DM receives one response.
- Explicit channel mention starts one thread.
- Unmentioned channel, thread, and group-DM messages get no response or reaction, including after prior bot participation.
- A fresh explicit mention in an existing thread or group DM receives one in-thread response.
- A message opening with another human's mention is ignored.
- A bot message without an explicit mention is ignored.
- Start reaction appears once for an eligible message.
- Verified success replaces start state with a check.
- Forced failure removes `:eyes:`, adds `:x:`, and has no check.
- The normal thinking indicator and argument-free verb footer appear while work is active.
- No interim text, thought stream, tool progress, task card, duplicate final, or channel broadcast appears.
