#!/bin/zsh
TOKEN=$(security find-generic-password -a "$USER" -s BunkerGame-Figma-API -w 2>/dev/null)
if [ -z "$TOKEN" ]; then
  echo "TOKEN_MISSING"
  exit 1
fi
CODE=$(curl -s -o /tmp/figma-check.json -w '%{http_code}' --max-time 20 -H "X-Figma-Token: $TOKEN" "https://api.figma.com/v1/files/rzVdCT73aztDRPsAWTdgrM?depth=1")
echo "HTTP_CODE=$CODE"
head -c 300 /tmp/figma-check.json
echo ""