#!/bin/sh

. /usr/lib/tuned/functions

start() {
    if [ -z "$TUNED_isolated_cores" ]; then
      echo "no isolated cores set, realtime profile not activating"
      exit 1
    fi

    # move threads off the selected cpu cores
    tuna -c "$TUNED_isolated_cores"

    # move the interrupts to non-isolated cores
    tuna -c "$TUNED_isolated_cores_complement" -q '*' -x -m
    return "$?"
}

stop() {
    return 0
}

verify() {
    return "$?"
}

process $@
