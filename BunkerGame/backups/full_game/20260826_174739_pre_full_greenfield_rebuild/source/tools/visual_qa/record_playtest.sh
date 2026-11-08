#!/bin/bash
set -eu

DURATION="${1:-120}"
LABEL="${2:-playtest}"

ROOT="/Users/Ori/Documents/Projects/BunkerGame"
RAW_DIR="$ROOT/visual-qa/raw"
OUT_DIR="$ROOT/visual-qa/captures"

mkdir -p "$RAW_DIR" "$OUT_DIR"

STAMP="$(date '+%Y-%m-%d_%H-%M-%S')"
RAW="$RAW_DIR/${STAMP}_${LABEL}_raw.mp4"
OUT="$OUT_DIR/${STAMP}_${LABEL}.mp4"

echo "VISUAL_QA_LABEL=$LABEL"
echo "VISUAL_QA_DURATION=$DURATION"
echo "VISUAL_QA_RAW=$RAW"
echo "VISUAL_QA_OUTPUT=$OUT"

# Bring Roblox Studio to the foreground.
osascript <<'APPLESCRIPT'
tell application "System Events"
    set frontmost of first process whose name contains "RobloxStudio" to true
end tell
APPLESCRIPT

sleep 2

# Screen 0 was verified as AVFoundation device 2 on this Mac.
ffmpeg \
    -hide_banner \
    -loglevel warning \
    -f avfoundation \
    -framerate 30 \
    -i "2:none" \
    -t "$DURATION" \
    -c:v libx264 \
    -preset veryfast \
    -crf 28 \
    -pix_fmt yuv420p \
    -y "$RAW"

# Produce a compact review copy.
ffmpeg \
    -hide_banner \
    -loglevel warning \
    -i "$RAW" \
    -vf "scale=-2:720" \
    -c:v libx264 \
    -preset fast \
    -crf 29 \
    -an \
    -movflags +faststart \
    -y "$OUT"

SIZE="$(stat -f%z "$OUT")"

echo "VISUAL_QA_CAPTURE_COMPLETE"
echo "PATH=$OUT"
echo "BYTES=$SIZE"
