#!/bin/sh

. /usr/lib/tuned/functions

pp=/usr/lib/tuned/realtime-virt-guest/

start() {
    python $pp/defirqaffinity.py "remove" "$pp/isolated-cpus" &&
    python $pp/isolate-cpus.py "-i" "$pp/isolated-cpus" &&
    cp -f $pp/isolated-cpus $pp/isolated-cpus-ineffect
    return "$?"
}

stop() {
    python $pp/isolate-cpus.py "-I" "$pp/isolated-cpus-ineffect" &&
    python $pp/defirqaffinity.py "add" "$pp/isolated-cpus-ineffect"
    return "$?"
}

verify() {
    python $pp/defirqaffinity.py "verify" "$pp/isolated-cpus-ineffect"
    return "$?"
}

process $@
