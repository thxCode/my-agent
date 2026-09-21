#!/bin/sh
# Kimi Code custom status line.
# Receives a JSON snapshot on stdin from the TUI:
#   {model, cwd, gitBranch, permissionMode, planMode, contextUsage,
#    contextTokens, maxContextTokens, sessionId, version}
# Prints one line: model · context bar · 5h quota · 7d quota · cwd · git
#
# 5h/7d quota comes from the managed Kimi Code usage endpoint
# (GET <base_url>/usages -> .usages.limit_5h/limit_7d.used_ratio).
# The endpoint is polled in a detached background job at most once per
# minute; the foreground path only reads the cache, so rendering stays
# well under the 300ms budget the TUI gives this command.

input=$(cat)

KC_HOME="${KIMI_CODE_HOME:-$HOME/.kimi-code}"
CACHE="$KC_HOME/cache/statusline-usage.json"
CACHE_TTL=60
USAGE_URL="${KIMI_CODE_BASE_URL:-https://api.kimi.com/coding/v1}/usages"
CRED="$KC_HOME/credentials/kimi-code.json"

ESC=$(printf '\033')
RED="${ESC}[31m"
YELLOW="${ESC}[33m"
GREEN="${ESC}[32m"
DIM="${ESC}[2m"
RESET="${ESC}[0m"
SEP=" ${DIM}·${RESET} "

# >80 red / >60 yellow / else green; $1 = integer percent
pct_color() {
  if [ "$1" -gt 80 ]; then
    printf '%s' "$RED"
  elif [ "$1" -gt 60 ]; then
    printf '%s' "$YELLOW"
  else
    printf '%s' "$GREEN"
  fi
}

# Fetch quota into the cache. Runs detached; never blocks the status line.
refresh_quota() {
  command -v jq >/dev/null 2>&1 || exit 0
  command -v curl >/dev/null 2>&1 || exit 0
  [ -f "$CRED" ] || exit 0
  token=$(jq -r '.access_token // empty' "$CRED" 2>/dev/null)
  [ -n "$token" ] || exit 0
  tmp="$CACHE.tmp.$$"
  if curl -fsS --max-time 5 -H "Authorization: Bearer $token" -H "Accept: application/json" \
      "$USAGE_URL" > "$tmp" 2>/dev/null \
    && jq -e '.usages' "$tmp" >/dev/null 2>&1; then
    mv "$tmp" "$CACHE"
  else
    rm -f "$tmp"
  fi
}

# Trigger a background refresh when the cache is missing or stale.
now=$(date +%s)
mtime=$(stat -f %m "$CACHE" 2>/dev/null || stat -c %Y "$CACHE" 2>/dev/null || echo 0)
if [ $((now - mtime)) -ge "$CACHE_TTL" ]; then
  ( refresh_quota ) </dev/null >/dev/null 2>&1 &
fi

if ! command -v jq >/dev/null 2>&1; then
  printf '%s' "kimi"
  exit 0
fi

# Extract every field in one jq pass; @sh makes the values shell-safe.
eval "$(printf '%s' "$input" | jq -r '
  "MODEL=" + ((.model // "") | @sh),
  "CWD=" + ((.cwd // "") | @sh),
  "BRANCH=" + ((.gitBranch // "") | @sh),
  "CTX_PCT=" + ((
    if (.maxContextTokens // 0) > 0
    then (((.contextTokens // 0) * 100 / .maxContextTokens) | floor)
    else (((.contextUsage // 0) * 100) | floor)
    end) | tostring)
' 2>/dev/null)"

out="${MODEL:-kimi}"

# Context usage progress bar (20 cells)
pct="${CTX_PCT:-0}"
case "$pct" in ''|*[!0-9]*) pct=0 ;; esac
filled=$(( pct / 5 ))
[ "$filled" -gt 20 ] && filled=20
empty=$(( 20 - filled ))
bar=""
i=0
while [ $i -lt $filled ]; do bar="${bar}█"; i=$(( i + 1 )); done
i=0
while [ $i -lt $empty ]; do bar="${bar}░"; i=$(( i + 1 )); done
color=$(pct_color "$pct")
out="${out}${SEP}${color}[${bar}] ${pct}%${RESET}"

# 5h / 7d quota from the cache (may be absent until the first refresh lands)
if [ -f "$CACHE" ]; then
  eval "$(jq -r '
    "FH=" + ((((.usages.limit_5h.used_ratio // .usages.limit5h.usedRatio) // -1) * 100 | floor) | tostring),
    "SD=" + ((((.usages.limit_7d.used_ratio // .usages.limit7d.usedRatio) // -1) * 100 | floor) | tostring)
  ' "$CACHE" 2>/dev/null)"
  case "${FH:--1}" in ''|*[!0-9]*) FH=-1 ;; esac
  case "${SD:--1}" in ''|*[!0-9]*) SD=-1 ;; esac
  if [ "$FH" -ge 0 ] 2>/dev/null; then
    out="${out}${SEP}${DIM}5h${RESET} $(pct_color "$FH")${FH}%${RESET}"
  fi
  if [ "$SD" -ge 0 ] 2>/dev/null; then
    out="${out}${SEP}${DIM}7d${RESET} $(pct_color "$SD")${SD}%${RESET}"
  fi
fi

# Working directory, shortened to ~ and the last 3 segments
if [ -n "$CWD" ]; then
  short="$CWD"
  case "$short" in
    "$HOME") short="~" ;;
    "$HOME"/*) short="~/${short#"$HOME"/}" ;;
  esac
  segs=$(printf '%s' "$short" | awk -F/ 'NF>3 {print "…/" $(NF-2) "/" $(NF-1) "/" $NF; next} {print}')
  out="${out}${SEP}${DIM}${segs}${RESET}"
fi

# Git branch
if [ -n "$BRANCH" ]; then
  out="${out}${SEP}${DIM}${BRANCH}${RESET}"
fi

printf '%s' "$out"
