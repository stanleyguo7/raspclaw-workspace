#!/bin/sh
set -eu

ADB=/usr/bin/adb
ZIDOO=192.168.3.115:5555
PACKAGE=com.clouddrive2.clouddrive2
APP_HOME=/data/data/com.clouddrive2.clouddrive2/files
CD_HOME="$APP_HOME/CloudDrive2"
MOUNT=/storage/emulated/0/mnt/CloudDrive
APP_MOUNT=/mnt/runtime/default/emulated/0/mnt/CloudDrive

"$ADB" connect "$ZIDOO" >/dev/null 2>&1 || exit 0
"$ADB" -s "$ZIDOO" get-state 2>/dev/null | grep -q '^device$' || exit 0

if ! "$ADB" -s "$ZIDOO" shell "mount | grep -q 'CloudFS on $MOUNT '"; then
  "$ADB" -s "$ZIDOO" shell "
    am force-stop $PACKAGE
    export CLOUDDRIVE_HOME=$CD_HOME
    export PATH=$APP_HOME:\$PATH
    cd $APP_HOME
    nohup ./clouddrive >/data/local/tmp/clouddrive-root.log 2>&1 </dev/null &
  " >/dev/null
  sleep 8
fi

# Android 9 keeps app-visible emulated storage in a separate mount namespace.
# A single bind into the default runtime view propagates to read/write views.
if ! "$ADB" -s "$ZIDOO" shell "test -d '$APP_MOUNT/movie'"; then
  "$ADB" -s "$ZIDOO" shell "
    mkdir -p $APP_MOUNT
    mount --bind $MOUNT $APP_MOUNT
  " >/dev/null
fi
