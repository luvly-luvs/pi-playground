#!/usr/bin/env bash

#? WM8960 Controls (* is some number):
#?
#? Playback: pcm*p
#? Capture : pcm*c

#? WM8960 Playback/Capture Closed State:
#?
#? closed

#? WM8960 Playback Open State:
#?
#? state: OPEN

CARD='card0'
CONTROL='pcm0p'
DEVICE='hw:0'

# Unused utility function
function log_playback_state() {
  while true; do
    sudo cat /proc/asound/"$CARD"/pcm0p/sub0/status
    sleep 0.5
  done
}

function get_state() {
  sudo grep -P -ie '^(closed|.*open)$' "/proc/asound/$CARD/$CONTROL/sub0/status"
}

# Change depending on target ALSA Control
function on_open() {
  amixer -D"$DEVICE" sset Capture 0%
}

# Change depending on target ALSA Control
function on_closed() {
  amixer -D"$DEVICE" sset Capture 18%
}

CURRENT_STATE=$(get_state)

while true; do
  NEXT_STATE=$(get_state)

  if [[ "$CURRENT_STATE" != "$NEXT_STATE" ]]; then
    CURRENT_STATE="$NEXT_STATE"

    if grep -qie "open" <<<"$CURRENT_STATE"; then
      on_open &
    elif grep -qie "closed" <<<"$CURRENT_STATE"; then
      on_closed &
    fi

    wait
  fi
done
