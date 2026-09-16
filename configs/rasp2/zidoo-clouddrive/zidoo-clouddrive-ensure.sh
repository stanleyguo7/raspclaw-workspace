#!/bin/sh
set -eu

ADB=/usr/bin/adb
ZIDOO=192.168.3.115:5555
PACKAGE=com.clouddrive2.clouddrive2
APP_HOME=/data/data/com.clouddrive2.clouddrive2/files
CD_HOME="$APP_HOME/CloudDrive2"
MOUNT=/storage/emulated/0/mnt/CloudDrive
APP_MOUNT=/mnt/runtime/default/emulated/0/mnt/CloudDrive
POLICY_HOST=/usr/local/lib/zidoo-clouddrive/magiskpolicy-armv7
POLICY_DEVICE=/data/local/tmp/magiskpolicy-cloud
POLICY_STAMP=/data/local/tmp/magiskpolicy-cloud.boot-id

"$ADB" connect "$ZIDOO" >/dev/null 2>&1 || exit 0
"$ADB" -s "$ZIDOO" get-state 2>/dev/null | grep -q '^device$' || exit 0

if ! "$ADB" -s "$ZIDOO" shell "grep -q ' $MOUNT .* - fuse CloudFS ' /proc/1/mountinfo"; then
  "$ADB" -s "$ZIDOO" shell "
    am force-stop $PACKAGE
    export CLOUDDRIVE_HOME=$CD_HOME
    export PATH=$APP_HOME:\$PATH
    cd $APP_HOME
    nohup ./clouddrive >/data/local/tmp/clouddrive-root.log 2>&1 </dev/null &
  " >/dev/null
  sleep 8
fi

# Zidoo's DvdPlayer SELinux domain cannot read generic FUSE mounts by default.
# Add only the read permissions required for CloudDrive playback; SELinux stays enforcing.
if [ -f "$POLICY_HOST" ] && ! "$ADB" -s "$ZIDOO" shell \
  "test -s '$POLICY_STAMP' && cmp -s /proc/sys/kernel/random/boot_id '$POLICY_STAMP'"; then
  if ! "$ADB" -s "$ZIDOO" shell "test -x '$POLICY_DEVICE'"; then
    "$ADB" -s "$ZIDOO" push "$POLICY_HOST" "$POLICY_DEVICE" >/dev/null
    "$ADB" -s "$ZIDOO" shell "chmod 755 '$POLICY_DEVICE'"
  fi
  "$ADB" -s "$ZIDOO" shell "
    $POLICY_DEVICE --live \
      'allow DvdPlayer fuse dir { search read open getattr }' \
      'allow DvdPlayer fuse file { open read getattr ioctl lock map }' \
      'allow DvdPlayer fuse filesystem getattr' &&
    cp /proc/sys/kernel/random/boot_id $POLICY_STAMP
  " >/dev/null
fi

# Android 9 keeps app-visible emulated storage in a separate mount namespace.
# A single bind into the default runtime view propagates to read/write views.
if ! "$ADB" -s "$ZIDOO" shell "test -r '$APP_MOUNT/movie'"; then
  "$ADB" -s "$ZIDOO" shell "
    umount -l $APP_MOUNT 2>/dev/null || true
    mkdir -p $APP_MOUNT
    mount --bind $MOUNT $APP_MOUNT
    kill -9 \$(pidof com.android.gallery3d) 2>/dev/null || true
    kill -9 \$(pidof com.zidoo.poster) 2>/dev/null || true
  " >/dev/null
fi
