#!/bin/bash
set -euo pipefail

FILE="${1:-}"

if [ -z "$FILE" ]; then
  echo "Usage: tools/bds/inspect-file.sh <file>"
  exit 1
fi

if [ ! -f "$FILE" ]; then
  echo "FILE_NOT_FOUND: $FILE"
  exit 1
fi

echo "============================================================"
echo "BDS FILE INSPECTION"
echo "============================================================"
echo "FILE: $FILE"
echo

echo "=== FILE METADATA ==="
wc -l -c "$FILE"
file "$FILE"
echo

echo "=== FUNCTION DECLARATIONS ==="
grep -nE '^[[:space:]]*(local[[:space:]]+)?function[[:space:]]+|^[[:space:]]*[A-Za-z_][A-Za-z0-9_.:]*[[:space:]]*=[[:space:]]*function' "$FILE" || true
echo

echo "=== REQUIRE CALLS ==="
grep -n 'require(' "$FILE" || true
echo

echo "=== ROBLOX SERVICES ==="
grep -nE 'game:GetService\(|game\.[A-Za-z]+' "$FILE" || true
echo

echo "=== REMOTES AND BINDABLES ==="
grep -nE 'RemoteEvent|RemoteFunction|BindableEvent|BindableFunction|OnServerEvent|OnClientEvent|OnServerInvoke|OnClientInvoke|FireClient|FireAllClients|FireServer|InvokeClient|InvokeServer' "$FILE" || true
echo

echo "=== DATASTORE USAGE ==="
grep -nE 'DataStoreService|GetDataStore|GetOrderedDataStore|GetAsync|SetAsync|UpdateAsync|RemoveAsync|IncrementAsync' "$FILE" || true
echo

echo "=== PLAYER LIFECYCLE ==="
grep -nE 'PlayerAdded|PlayerRemoving|CharacterAdded|CharacterRemoving|Players:GetPlayers' "$FILE" || true
echo

echo "=== INSTANCE CREATION ==="
grep -n 'Instance.new(' "$FILE" || true
echo

echo "=== ATTRIBUTES AND TAGS ==="
grep -nE 'GetAttribute|SetAttribute|GetAttributes|CollectionService|AddTag|RemoveTag|HasTag|GetTagged' "$FILE" || true
echo

echo "=== EVENT CONNECTIONS ==="
grep -nE ':Connect\(|:Once\(' "$FILE" || true
echo

echo "=== LOOPS AND TASKS ==="
grep -nE 'while[[:space:]]|repeat[[:space:]]|for[[:space:]].*[[:space:]]do|task\.spawn|task\.defer|task\.delay|task\.wait' "$FILE" || true
