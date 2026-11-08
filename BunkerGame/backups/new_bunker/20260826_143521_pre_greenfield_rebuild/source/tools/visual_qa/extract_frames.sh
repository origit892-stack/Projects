#!/bin/bash
set -eu

VIDEO="${1:?Usage: extract_frames.sh VIDEO [INTERVAL_SECONDS]}"
INTERVAL="${2:-5}"

ROOT="/Users/Ori/Documents/Projects/BunkerGame"
NAME="$(basename "$VIDEO" .mp4)"
OUT="$ROOT/visual-qa/frames/$NAME"

mkdir -p "$OUT"

ffmpeg \
    -hide_banner \
    -loglevel warning \
    -i "$VIDEO" \
    -vf "fps=1/$INTERVAL,scale=-2:720" \
    -q:v 3 \
    -y "$OUT/frame_%04d.jpg"

echo "VISUAL_QA_FRAMES_COMPLETE"
echo "PATH=$OUT"
find "$OUT" -type f -name '*.jpg' | wc -l | awk '{print "FRAMES=" $1}'
