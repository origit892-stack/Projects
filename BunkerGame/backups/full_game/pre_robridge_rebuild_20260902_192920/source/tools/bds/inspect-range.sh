#!/bin/bash
set -euo pipefail

FILE="${1:-}"
START="${2:-}"
END="${3:-}"

if [ -z "$FILE" ] || [ -z "$START" ] || [ -z "$END" ]; then
  echo "Usage: tools/bds/inspect-range.sh <file> <start-line> <end-line>"
  exit 1
fi

if [ ! -f "$FILE" ]; then
  echo "FILE_NOT_FOUND: $FILE"
  exit 1
fi

if ! [[ "$START" =~ ^[0-9]+$ && "$END" =~ ^[0-9]+$ ]]; then
  echo "ERROR: line numbers must be integers"
  exit 1
fi

if [ "$START" -gt "$END" ]; then
  echo "ERROR: start line must not exceed end line"
  exit 1
fi

echo "FILE: $FILE"
echo "RANGE: $START-$END"
echo

nl -ba "$FILE" | sed -n "${START},${END}p"
