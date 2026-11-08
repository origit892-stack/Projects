#!/bin/zsh
LOG='/Users/Ori/Library/Logs/Roblox/0.740.19.7400003_20260928T184050Z_Studio_ce547_last.log'
echo '=== Log size / line count ==='
wc -l "$LOG"
echo '=== Non-telemetry lines (errors, crashes, place, session, client) ==='
grep -viE 'HttpTraceError|WebSocketTraceError|OtlpHttpExporter|CURLINFO|CURLOPT|ConnectFail|timespent|/studio"|tracing.roblox' "$LOG" 2>/dev/null | tail -40
echo '=== Any crash/fatal/exception mentions ==='
grep -iE 'crash|fatal|exception|abort|segfault|unhandled' "$LOG" 2>/dev/null | head -10