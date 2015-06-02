#!/bin/sh

. /usr/lib/tuned/functions

pp=/usr/lib/tuned/realtime-virtual-host/

ltanfile=/sys/module/kvm/parameters/lapic_timer_advance_ns

start() {
    if [ -f $ltanfile -a ! -f $pp/lapic_timer_adv_ns ]; then
        if [ -f $pp/tscdeadline_latency.flat ]; then
             tempdir=`mktemp -d`
             sh $pp/run-tscdeadline-latency.sh > $tempdir/lat.out
             sh $pp/find-lapictscdeadline-optimal.sh $tempdir/lat.out > $tempdir/opt.out
             if [ $? -eq 0 ]; then
                  echo `cat $tempdir/opt.out | cut -f 2 -d ":"` > $pp/lapic_timer_adv_ns
             fi
        fi
    fi
    if [ -f $ltanfile -a -f $pp/lapic_timer_adv_ns ]; then
        echo `cat $pp/lapic_timer_adv_ns` > $ltanfile
    fi
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
