#!/bin/sh

. /usr/lib/tuned/functions

pp=/usr/lib/tuned/realtime-virtual-host/

ltanfile=/sys/module/kvm/parameters/lapic_timer_advance_ns

start() {
    python $pp/expandisolcpus.py $TUNED_isolated_cores > $pp/isolated-cpus
    python $pp/defirqaffinity.py "remove" "$pp/isolated-cpus" &&
    python $pp/isolate-cpus.py "-i" "$pp/isolated-cpus" &&
    cp -f $pp/isolated-cpus $pp/isolated-cpus-ineffect
    retval = "$?"

    if [ ! $retval -eq 0 ]; then
        return $retval
    fi

    modinfo -p kvm | grep -q kvmclock_periodic_sync
    if [ "$?" -eq 0 ]; then
        echo "options kvm kvmclock_periodic_sync=0" > /etc/modprobe.d/kvm.rt.tuned.conf
    fi

    if [ -f lapic_timer_adv_ns.cpumodel ]; then
        curmodel=`cat /proc/cpuinfo | grep "model name" | cut -f 2 -d ":" | uniq`
        genmodel=`cat lapic_timer_adv_ns.cpumodel`

        if [ "$cpumodel" != "$genmodel" ]; then
            rm -f lapic_timer_adv_ns
            rm -f lapic_timer_adv_ns.cpumodel
        fi
    fi


    if [ -f $ltanfile -a ! -f $pp/lapic_timer_adv_ns ]; then
        if [ -f $pp/tscdeadline_latency.flat ]; then
             tempdir=`mktemp -d`
             cd $pp
             isolatedcpu=`cat isolated-cpus | cut -f 1 -d ","`
             sh $pp/run-tscdeadline-latency.sh $isolatedcpu > $tempdir/lat.out
             sh $pp/find-lapictscdeadline-optimal.sh $tempdir/lat.out > $tempdir/opt.out
             cd -
             if [ $? -eq 0 ]; then
                  echo `cat $tempdir/opt.out | cut -f 2 -d ":"` > $pp/lapic_timer_adv_ns
                  curmodel=`cat /proc/cpuinfo | grep "model name" | cut -f 2 -d ":" | uniq`
                  echo $curmodel > lapic_timer_adv_ns.cpumodel
             fi
        fi
    fi
    if [ -f $ltanfile -a -f $pp/lapic_timer_adv_ns ]; then
        echo `cat $pp/lapic_timer_adv_ns` > $ltanfile
    fi

    return $retval
}

stop() {
    rm -f /etc/modprobe.d/kvm.rt.tuned.conf
    python $pp/isolate-cpus.py "-I" "$pp/isolated-cpus-ineffect" &&
    python $pp/defirqaffinity.py "add" "$pp/isolated-cpus-ineffect"
    return "$?"
}

verify() {
    python $pp/defirqaffinity.py "verify" "$pp/isolated-cpus-ineffect"
    retval = "$?"
    if [ $retval -eq 0 -a -f /sys/module/kvm/parameters/kvmclock_periodic_sync ]; then
        retval = `cat /sys/module/kvm/parameters/kvmclock_periodic_sync`
    fi
    return $retval
}

process $@
