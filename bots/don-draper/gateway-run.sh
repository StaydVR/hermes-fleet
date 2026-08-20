#!/command/with-contenv sh
# shellcheck shell=sh
# Fleet source of truth for Don's s6 gateway run script.
# Applied by apply-bot.sh → /run/service/gateway-don-draper/run (best-effort).
set -e
export HOME=/opt/data
cd /opt/data
. /opt/hermes/.venv/bin/activate
export HERMES_S6_SUPERVISED_CHILD=1
export HERMES_HOME=/opt/data/profiles/don-draper
export HERMES_CODEX_EVENT_STALE_TIMEOUT_SECONDS=900
export HERMES_CODEX_TTFB_TIMEOUT_SECONDS=300
export HERMES_CODEX_TTFB_MAX_SECONDS=300
[ "$(id -u)" = 0 ] || exec hermes -p don-draper gateway run --replace
exec s6-setuidgid hermes hermes -p don-draper gateway run --replace
