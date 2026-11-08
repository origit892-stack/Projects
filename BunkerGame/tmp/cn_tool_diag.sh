#!/bin/zsh
cd /Users/Ori/Documents/Projects/BunkerGame
PROMPT='Read the file /Users/Ori/Documents/Projects/BunkerGame/src/Workspace/SpawnRoot.model.json using your file tool, then reply with exactly: DONE'
/Users/Ori/.npm-global/bin/cn -p --config ~/.continue/config.yaml --auto --format json "$PROMPT" > /tmp/cn_tool.out 2>/tmp/cn_tool.err &
CNPID=$!
echo "CNPID=$CNPID"
for i in 1 2 3 4 5; do
  sleep 20
  OB=$(wc -c < /tmp/cn_tool.out 2>/dev/null)
  EB=$(wc -c < /tmp/cn_tool.err 2>/dev/null)
  echo "t=$((i*20))s out=$OB err=$EB"
  if ! ps -p $CNPID >/dev/null 2>&1; then
    echo "exited at t=$((i*20))s"
    break
  fi
done
echo "---OUT---"
cat /tmp/cn_tool.out 2>&1
echo "---ERR---"
cat /tmp/cn_tool.err 2>&1
echo "---ALIVE---"
ps -o pid=,stat= -p $CNPID 2>&1 || echo gone
kill $CNPID 2>/dev/null || true