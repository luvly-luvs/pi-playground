#!/usr/bin/env bash

export BAK_DIR=~/.audio
export BAK_FILE=wm8960-bk.state
export DBUS_SYSTEM_BUS_ADDRESS=unix:path=/host/run/dbus/system_bus_socket
export DBUS_SESSION_BUS_ADDRESS=$DBUS_SYSTEM_BUS_ADDRESS
export DEVICE=hw:0
export UDEV=1

[[ ! -d "$BAK_DIR" ]] && mkdir -p "$BAK_DIR"

alsactl --file "$BAK_DIR"/"$BAK_FILE" store

amixer -D"$DEVICE" sset Headphone 79%
amixer -D"$DEVICE" sset Playback 100%
amixer -D"$DEVICE" sset Capture 18%

alsactl store

xhost + >/dev/null &
unclutter &
xset s noblank &
xset s off &
xset -dpms &

exec sudo "$(which levelup-standalone-dmp-intercom-ui)" --no-sandbox
