#!/usr/bin/env bash
# Mikro gta6: edit main.py (revisi kedua, kit gate thinking_revised) via Gemini CLI 3.5-flash-lite.
set -uo pipefail
cd /home/hatch/workspace/makefun/entry-gta6-01
PROMPT_FILE=/home/hatch/workspace/makefun/gemini-cli/gta6-twitch-ccu-forecast-01-micro-prompt.txt
LOG=/home/hatch/workspace/makefun/entry-gta6-01/build-35flash-lite-micro.log
PREAMBLE='SESI MIKRO gta6-twitch-ccu-forecast-01: EDIT main.py saja (kit gate thinking_revised menuntut file final dari >=2 pesan tulis/edit). Jam ~19:10 WIB 17 Nov 2026, deadline submit 19 Nov 08:00 WIB. Ikuti micro prompt di bawah ini persis. JANGAN buat repo/push/bundle/submit.'
/home/hatch/workspace/makefun/gemini-cli/run-gemini.sh -p "$PREAMBLE

$(cat "$PROMPT_FILE")" --model gemini-3.5-flash-lite --yolo 2>&1 | tee "$LOG"
echo "GEMINI_EXIT=${PIPESTATUS[0]}" | tee -a "$LOG"
