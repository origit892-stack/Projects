#!/bin/zsh
cd /Users/Ori/Documents/Projects/BunkerGame
/Users/Ori/.npm-global/bin/cn -p --config ~/.continue/config.yaml --auto --format json 'Reply with exactly: PONG' > /tmp/cn_test.out 2>/tmp/cn_test.err &
CNPID=$!
echo "CNPID=$CNPID"
sleep 45
echo "---OUT---"
cat /tmp/cn_test.out 2>&1 | head -40
echo "---ERR---"
cat /tmp/cn_test.err 2>&1 | head -40
echo "---ALIVE---"
ps -o pid=,stat= -p $CNPID 2>&1 || echo "process gone"
kill $CNPID 2>/dev/null || true