#!/bin/zsh
cd /Users/Ori/Documents/Projects/BunkerGame
PROMPT=$(cat /Users/Ori/Documents/Projects/BunkerGame/.director/runs/impl-bunker-ground-placement-f1e592bfaad9.prompt.txt)
/Users/Ori/.npm-global/bin/cn -p --config ~/.continue/config.yaml --auto --format json "$PROMPT" > /tmp/cn_worker.out 2>/tmp/cn_worker.err &
CNPID=$!
echo "CNPID=$CNPID"
for i in 1 2 3 4 5 6; do
  sleep 20
  echo "=== t=$((i*20))s out_bytes=$(wc -c < /tmp/cn_worker.out 2>/dev/null) err_bytes=$(wc -c < /tmp/cn_worker.err 2>/dev/null) ==="
  if ! ps -p $CNPID >/dev/null 2>&1; then
    echo "process exited at t=$((i*20))s"
    break
  fi
done
echo "---OUT tail---"
tail -30 /tmp/cn_worker.out 2>&1
echo "---ERR tail---"
tail -30 /tmp/cn_worker.err 2>&1
echo "---ALIVE---"
ps -o pid=,stat= -p $CNPID 2>&1 || echo "process gone"
kill $CNPID 2>/dev/null || true