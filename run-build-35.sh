#!/usr/bin/env bash
# Build gta6-twitch-ccu-forecast-01 via Gemini CLI (gemini-3.5-flash-lite).
# Desain: unlock-aligned log-ratio comparables forecaster + kalibrasi per-jam (geseran pola LB 1-5).
set -uo pipefail
cd /home/hatch/workspace/makefun/entry-gta6-01
PROMPT_FILE=/home/hatch/workspace/makefun/gemini-cli/gta6-twitch-ccu-forecast-01-prompt.txt
LOG=/home/hatch/workspace/makefun/entry-gta6-01/build-35flash-lite.log
PREAMBLE='SESI BUILD gta6-twitch-ccu-forecast-01 — "Forecast GTA VI launch-day Twitch viewers" ($250 top 20). Jam sekarang ~19:05 WIB 17 Nov 2026, deadline submit 19 Nov 08:00 WIB. Target: main.py forecaster + skor practice SENDIRI vs house baseline + SHIP-READY.md. Pola LB 1-5: log-ratio + comparables + kernel/local-linear + kalibrasi per-jam — CONTEK lalu GESER, jangan copy persis. Kalau kuota habis di tengah, tulis SHIP-READY.md + keadaan terakhir lalu BERHENTI. JANGAN buat repo GitHub, JANGAN push, JANGAN bundle transcript, JANGAN submit — parent yang menangani setelah kamu selesai. Ikuti build prompt di bawah ini persis.'
/home/hatch/workspace/makefun/gemini-cli/run-gemini.sh -p "$PREAMBLE

$(cat "$PROMPT_FILE")" --model gemini-3.5-flash-lite --yolo 2>&1 | tee "$LOG"
echo "GEMINI_EXIT=${PIPESTATUS[0]}" | tee -a "$LOG"
