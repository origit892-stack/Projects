#!/bin/bash
set -eu

ROOT="/Users/Ori/Documents/Projects/BunkerGame"
OBS="$ROOT/tools/visual_qa/obs_capture.py"

COMMAND="${1:-}"

case "$COMMAND" in
    verify)
        "$OBS" verify
        ;;

    start)
        LABEL="${2:?Usage: visual_qa.sh start LABEL}"
        "$OBS" start "$LABEL"
        ;;

    stop)
        "$OBS" stop
        ;;

    status)
        "$OBS" status
        ;;

    latest)
        "$OBS" latest
        ;;

    list)
        "$ROOT/tools/visual_qa/list_captures.sh"
        ;;

    frames)
        VIDEO="${2:?Usage: visual_qa.sh frames VIDEO [INTERVAL]}"
        INTERVAL="${3:-5}"
        "$ROOT/tools/visual_qa/extract_frames.sh" "$VIDEO" "$INTERVAL"
        ;;

    *)
        echo "BunkerGame Visual QA"
        echo
        echo "Commands:"
        echo "  verify"
        echo "  start LABEL"
        echo "  status"
        echo "  stop"
        echo "  latest"
        echo "  list"
        echo "  frames VIDEO [INTERVAL]"
        exit 2
        ;;
esac
