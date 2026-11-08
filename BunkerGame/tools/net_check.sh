#!/bin/zsh
echo '=== Connectivity to Roblox endpoints (5s timeout each) ==='
for url in https://apis.roblox.com https://tracing.roblox.com https://ecsv2.roblox.com https://www.roblox.com; do
  code=$(curl -s -o /dev/null -m 5 -w '%{http_code}' "$url" 2>/dev/null)
  echo "$url -> HTTP $code"
done
echo '=== General internet (google) ==='
code=$(curl -s -o /dev/null -m 5 -w '%{http_code}' https://www.google.com 2>/dev/null)
echo "google -> HTTP $code"