#!/usr/bin/env bash
set -euo pipefail

host="192.168.3.115"
adb_target="${host}:5555"
controller="/home/guosq/workspace/raspclaw-workspace/scripts/z10pro-download.py"

if timeout 8 "$controller" version >/dev/null 2>&1; then
  exit 0
fi

timeout 3 ping -c 1 "$host" >/dev/null
adb connect "$adb_target" >/dev/null
adb -s "$adb_target" shell am start -n com.termux/.app.TermuxActivity >/dev/null
sleep 2
adb -s "$adb_target" shell am startservice \
  -n com.termux/.app.RunCommandService \
  -a com.termux.RUN_COMMAND \
  --es com.termux.RUN_COMMAND_PATH /data/data/com.termux/files/usr/bin/service-daemon \
  --esa com.termux.RUN_COMMAND_ARGUMENTS start \
  --es com.termux.RUN_COMMAND_WORKDIR /data/data/com.termux/files/home \
  --ez com.termux.RUN_COMMAND_BACKGROUND true >/dev/null

for _ in $(seq 1 10); do
  if timeout 8 "$controller" version >/dev/null 2>&1; then
    exit 0
  fi
  sleep 2
done

echo "Zidoo aria2 did not recover" >&2
exit 1
