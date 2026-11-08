#!/bin/zsh
cd /Users/Ori/Documents/Projects/BunkerGame
PROMPT=$(cat /Users/Ori/Documents/Projects/BunkerGame/.director/runs/impl-bunker-ground-placement-f1e592bfaad9.prompt.txt)
/Users/Ori/.npm-global/bin/cn -p --config ~/.continue/config.yaml --auto --format json "$PROMPT" > /tmp/cn_real.out 2>/tmp/cn_real.err &
CNPID=$!
echo "CNPID=$CNPID"
for i in $(seq 1 20); do
  sleep 30
  OB=$(wc -c < /tmp/cn_real.out 2>/dev/null)
  EB=$(wc -c < /tmp/cn_real.err 2>/dev/null)
  echo "t=$((i*30))s out=$OB err=$EB"
  if ! ps -p $CNPID >/dev/null 2>&1; then
    echo "exited at t=$((i*30))s"
    break
  fi
done
echo "---OUT (full)---"
cat /tmp/cn_real.out 2>&1
echo "---ERR (full)---"
cat /tmp/cn_real.err 2>&1
echo "---ALIVE---"
ps -o pid=,stat= -p $CNPID 2>&1 || echo gone
kill $CNPID 2>/dev/null || true