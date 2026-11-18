#!/usr/bin/env bash
set -eu

usage() {
  cat >&2 <<EOF
Использование: collect.sh [--last | --session <ses_id> | --window <Nd>] [--log <path>]

  --last       последняя сессия текущей директории (по умолчанию)
  --session    конкретная сессия по её id (ses_...)
  --window     все события за последние N дней (без привязки к сессии)
  --log        путь к логу (по умолчанию ~/.local/share/opencode/log/opencode.log)
EOF
  exit 1
}

LOG="$HOME/.local/share/opencode/log/opencode.log"
MODE="last"
SESSION_ID=""
WINDOW=""

while [ $# -gt 0 ]; do
  case "$1" in
    --last) MODE="last"; shift ;;
    --session) [ -n "${2:-}" ] || usage; MODE="session"; SESSION_ID="$2"; shift 2 ;;
    --window) [ -n "${2:-}" ] || usage; MODE="window"; WINDOW="$2"; shift 2 ;;
    --log) [ -n "${2:-}" ] || usage; LOG="$2"; shift 2 ;;
    -h|--help) usage ;;
    *) echo "Неизвестный аргумент: $1" >&2; usage ;;
  esac
done

[ -f "$LOG" ] || { echo "Лог не найден: $LOG" >&2; exit 1; }

section() { printf '\n===== %s =====\n' "$1"; }

SRC="$LOG"
TMP=""

if [ "$MODE" = "window" ]; then
  case "$WINDOW" in
    ''|*[!0-9]*) echo "--window требует число дней" >&2; exit 1 ;;
  esac
  SINCE=$(date -u -d "-${WINDOW} days" +%Y-%m-%dT%H:%M:%S)
  TMP=$(mktemp)
  awk -v since="$SINCE" 'substr($0,11,19) >= since' "$LOG" > "$TMP"
  SRC="$TMP"
fi

cleanup() { [ -n "$TMP" ] && [ -f "$TMP" ] && rm -f "$TMP"; }
trap cleanup EXIT

RUN=""
if [ "$MODE" = "last" ]; then
  LINE=$(grep 'message=created id=ses_' "$SRC" | grep -F "directory=$PWD" | tail -1 || true)
  [ -n "$LINE" ] || { echo "Сессий для директории $PWD в логе не найдено" >&2; exit 1; }
  RUN=$(printf '%s\n' "$LINE" | grep -oE 'run=[a-f0-9]+' | head -1 | cut -d= -f2)
  SESSION_ID=$(printf '%s\n' "$LINE" | grep -oE 'id=ses_[A-Za-z0-9]+' | head -1 | cut -d= -f2)
elif [ "$MODE" = "session" ]; then
  LINE=$(grep -F "message=created id=$SESSION_ID" "$SRC" | tail -1 || true)
  [ -n "$LINE" ] || { echo "Сессия $SESSION_ID в логе не найдена" >&2; exit 1; }
  RUN=$(printf '%s\n' "$LINE" | grep -oE 'run=[a-f0-9]+' | head -1 | cut -d= -f2)
fi

echo "Цель: mode=$MODE session=${SESSION_ID:--} run=${RUN:--} ${WINDOW:+window=$WINDOW дней}"
if [ -n "$RUN" ]; then
  echo "Гранулярность: run=$RUN (процесс opencode со всеми сессиями и субагентами)"
  RF=(grep -F "run=$RUN")
else
  RF=(cat)
fi

section "SESSIONS"
"${RF[@]}" "$SRC" | grep 'message=created id=ses_' | while read -r l; do
  fld() { printf '%s\n' "$l" | grep -oE "$1=[^ ]*" | head -1 | cut -d= -f2-; }
  printf '%s  agent=%s  parent=%s  cost=%s  in=%s out=%s reason=%s cache_r=%s  title=%s\n' \
    "$(fld id)" "$(fld agent)" "$(fld parentID)" "$(fld cost)" \
    "$(fld 'tokens.input')" "$(fld 'tokens.output')" "$(fld 'tokens.reasoning')" "$(fld 'tokens.cache.read')" \
    "$(printf '%s\n' "$l" | grep -oE 'title="[^"]*"' | head -1 | cut -d'"' -f2)"
done

section "TOOL_CALLS: частоты по инструментам"
"${RF[@]}" "$SRC" | grep 'message=evaluated permission=' | grep -oE 'permission=[a-zA-Z0-9._-]+' | sort | uniq -c | sort -rn

section "TOOL_CALLS: точные дубли bash-команд (>=2 раз)"
"${RF[@]}" "$SRC" | grep 'message=evaluated permission=bash' | grep -oE 'pattern="([^"\\]|\\.)*"' | sort | uniq -c | sort -rn | awk '$1>=2 {print}' | head -20

section "TOOL_CALLS: топ-20 длиннейших bash-команд"
"${RF[@]}" "$SRC" | grep 'message=evaluated permission=bash' | grep -oE 'pattern="([^"\\]|\\.)*"' | awk '{print length($0), $0}' | sort -rn | head -20 | cut -d' ' -f2-

section "LLM: вызовы по модель/агент"
"${RF[@]}" "$SRC" | grep 'message=stream providerID=' | grep -oE 'providerID=[^ ]* modelID=[^ ]*' | sort | uniq -c | sort -rn
echo "-- agent:"
"${RF[@]}" "$SRC" | grep 'message=stream providerID=' | grep -oE 'agent=[^ ]*' | sort | uniq -c | sort -rn

section "ERRORS"
printf 'level=ERROR: '; "${RF[@]}" "$SRC" | grep -c 'level=ERROR' || true
printf 'stream error: '; "${RF[@]}" "$SRC" | grep -c 'message="stream error"' || true
echo "-- последние level=ERROR:"
"${RF[@]}" "$SRC" | grep 'level=ERROR' | tail -10 | sed 's/^timestamp=\([^ ]*\).*message=/\1  /'

section "SKILL_CONFLICTS (глобально, весь лог)"
grep 'message="duplicate skill name"' "$LOG" | grep -oE 'name=[^ ]*' | sort -u | while read -r n; do
  nm="${n#name=}"
  cnt=$(grep "message=\"duplicate skill name\" name=$nm " "$LOG" | grep -oE '(existing|duplicate)=[^ ]*' | cut -d= -f2- | sort -u | wc -l)
  printf '%s — %s копий:\n' "$nm" "$cnt"
  grep "message=\"duplicate skill name\" name=$nm " "$LOG" | grep -oE '(existing|duplicate)=[^ ]*' | cut -d= -f2- | sort -u | sed 's/^/    /'
done

section "FILES: частоты правок"
"${RF[@]}" "$SRC" | grep 'message="touching file"' | grep -oE 'file=[^ ]*' | sort | uniq -c | sort -rn | head -15
echo "-- formatting:"
"${RF[@]}" "$SRC" | grep 'message="formatting file"' | grep -oE 'file=[^ ]*' | sort | uniq -c | sort -rn | head -10

section "ASKING: затыки на разрешениях"
printf 'asking: '; "${RF[@]}" "$SRC" | grep -c 'message=asking id' || true
printf '\nГотово. Источник: %s\n' "$LOG"
