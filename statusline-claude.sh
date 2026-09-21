#!/bin/sh
input=$(cat)

# auto-research cost governor: persist rate limits for scripts/cost-check.sh (best-effort, never blocks the status line)
printf '%s' "$input" | jq -c '{five_hour: .rate_limits.five_hour, seven_day: .rate_limits.seven_day, ts: now}' > "$HOME/.claude/rate_limits.json" 2>/dev/null || true

ESC=$(printf '\033')
RED="${ESC}[31m"
YELLOW="${ESC}[33m"
GREEN="${ESC}[32m"
DIM="${ESC}[2m"
RESET="${ESC}[0m"
SEP=" ${DIM}·${RESET} "

# Return color as an integer percentage: >80 Red / >60 Yellow / Otherwise Green
pct_color() {
  if [ "$1" -gt 80 ]; then
    printf '%s' "$RED"
  elif [ "$1" -gt 60 ]; then
    printf '%s' "$YELLOW"
  else
    printf '%s' "$GREEN"
  fi
}

# Starting section: Model name
out=$(echo "$input" | jq -r '.model.display_name // "Claude"')

# Context Progress bar (colored according to usage)
used=$(echo "$input" | jq -r '.context_window.used_percentage // empty')
if [ -z "$used" ]; then
  used="0"
fi
if [ -n "$used" ]; then
  used_int=$(printf '%.0f' "$used")
  bar_filled=$(( used_int / 5 ))
  [ "$bar_filled" -gt 20 ] && bar_filled=20
  bar_empty=$(( 20 - bar_filled ))
  bar=""
  i=0
  while [ $i -lt $bar_filled ]; do bar="${bar}█"; i=$(( i + 1 )); done
  i=0
  while [ $i -lt $bar_empty ]; do bar="${bar}░"; i=$(( i + 1 )); done
  color=$(pct_color "$used_int")
  out="${out}${SEP}${color}[${bar}] ${used_int}%${RESET}"
fi

# Detect a third-party proxy backend (e.g. Zhipu glm-*): cost is priced via Anthropic's rate card and is meaningless there
is_glm=$(echo "$input" | jq -r '(.model.id // .model.display_name // "") | test("glm"; "i")')

# Cost (only meaningful on the official Claude backend)
if [ "$is_glm" != "true" ]; then
  cost=$(echo "$input" | jq -r '.cost.total_cost_usd // empty')
  if [ -n "$cost" ]; then
    out="${out}${SEP}$(printf '$%.2f' "$cost")"
  fi
fi

# Duration (Total Wall Clock Time)
dur_ms=$(echo "$input" | jq -r '(.cost.total_duration_ms // empty) | floor')
if [ -n "$dur_ms" ]; then
  dur_s=$(( dur_ms / 1000 ))
  h=$(( dur_s / 3600 ))
  m=$(( (dur_s % 3600) / 60 ))
  s=$(( dur_s % 60 ))
  if [ "$h" -gt 0 ]; then
    dur=$(printf '%dh%dm' "$h" "$m")
  elif [ "$m" -gt 0 ]; then
    dur=$(printf '%dm%ds' "$m" "$s")
  else
    dur=$(printf '%ds' "$s")
  fi
  out="${out}${SEP}${dur}"
fi

# Rate limit (Only appears in Claude.ai Pro/Max and only after an API response has been received in this session; it will be hidden if missing)
five_h=$(echo "$input" | jq -r '.rate_limits.five_hour.used_percentage // empty')
if [ -n "$five_h" ]; then
  fh_int=$(printf '%.0f' "$five_h")
  color=$(pct_color "$fh_int")
  out="${out}${SEP}${DIM}5h${RESET} ${color}${fh_int}%${RESET}"
fi
seven_d=$(echo "$input" | jq -r '.rate_limits.seven_day.used_percentage // empty')
if [ -n "$seven_d" ]; then
  sd_int=$(printf '%.0f' "$seven_d")
  color=$(pct_color "$sd_int")
  out="${out}${SEP}${DIM}7d${RESET} ${color}${sd_int}%${RESET}"
fi

printf '%s' "$out"