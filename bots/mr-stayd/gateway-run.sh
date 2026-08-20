#!/command/with-contenv sh
# shellcheck shell=sh
# Fleet source of truth for Mr Stayd (default) s6 gateway run script.
set -e
export HOME=/opt/data
cd /opt/data
. /opt/hermes/.venv/bin/activate
export HERMES_S6_SUPERVISED_CHILD=1
export HERMES_HOME=/opt/data
export HERMES_CODEX_EVENT_STALE_TIMEOUT_SECONDS=900
export HERMES_CODEX_TTFB_TIMEOUT_SECONDS=300
export HERMES_CODEX_TTFB_MAX_SECONDS=300
# default slot: no -p (root HERMES_HOME profile)
[ "$(id -u)" = 0 ] || exec hermes gateway run --replace
exec s6-setuidgid hermes hermes gateway run --replace
