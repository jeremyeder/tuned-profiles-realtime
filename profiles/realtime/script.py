#!/usr/bin/python -tt

# worker script for realtime tuned profile

import os
import sys
import subprocess
import argparse
import procfs

class CpuList(object):

    def __init__(self, cpurange):
        self.online = self.cpus()
        self.range = self.expand(cpurange)

    def __repr__(self):
        return ",".join(self.contract())

    def __str__(self):
        return str(",".join(self.contract()))

    # return the number of cpus online
    def cpus(self):
        p = subprocess.Popen(['getconf', '_NPROCESSORS_ONLN'],
                             stdout=subprocess.PIPE, shell=False)
        return int(p.stdout.readline());

    # expand a string cpu range into a flat array of integers
    # '2,4-7' -> [2, 4, 5, 6, 7 ]
    def expand(self, cpurange):
        result = []
        for part in cpurange.split(','):
            if '-' in part:
                a, b = part.split('-')
                a, b = int(a), int(b)
                if a >= self.online:
                    raise ValueError, "invalid cpu value: %d >= %d (max)" % (a, max)
                if b >= self.online:
                    raise ValueError, "invalid cpu value: %d >= %d (max)" % (b, max)
                result.extend(range(a, b + 1))
            else:
                a = int(part)
                if a >= self.online:
                    raise ValueError, "invalid cpu value: %d >= %d (max)" % (a, max)
                result.append(a)
        return result

    # return the compliment of our array of cpu numbers
    def compliment(self):
        return self.contract([ x for x in range(0, self.online) if x not in self.range ])

    # return true if the value x is the next consecutive number from the last entry
    # of array a
    def _consecutive (self, a, x):
        if a == []:
            return False
        last = a[-1:][0]
        if '-' in last:
            last = int(last.split('-')[1])
        else:
            last = int(last)
        if x == (last+1):
            return True
        return False

    # extend the range r by one
    def _extend_range(self, r):
        if '-' in r:
            a,b = r.split('-')
            return "%s-%s" % (a, str(int(b)+1))
        else:
            return "%s-%s" % (r, str(int(r)+1))

    # given a list of cpus 'l', return a compressed array of strings
    # [ 2, 4, 5, 6, 7 ] -> ['2', '4-7']
    def contract(self, array=None):
        result = []
        if array:
            l = array
        else:
            l = self.range
        while (l):
            if self._consecutive(result, l[0]):
                r = self._extend_range(result.pop())
            else:
                r = str(l[0])
            result.extend([r])
            l = l[1:]
        return result

######################################################################
# start of script logic

# activate this tuned profile
def start(cpulist):
    # move threads off the selected cpu cores
    cmd = ['tuna', '-c', str(cpulist), '-i']
    subprocess.call(cmd, shell=False)

    # move the interrupts to non-isolated cores
    cmd = ['tuna', '--c', ",".join(cpulist.compliment()), '-q', '*', '-x', '-m' ]
    subprocess.call(cmd, shell=False)

# deactivate the tuned profile
def stop(cpulist):
    pass

# verify the tuned profile conditions are met
def verify(cpulist):
    cmd = ['tuna', '-c', str(cpulist), '-P' ]
    subprocess.call(cmd, shell=False)

if __name__ == "__main__":

    parser = argparse.ArgumentParser(description='process tuned profile script argument')
    parser.add_argument('command', nargs=1, choices=['start', 'stop', 'verify'])

    ns = parser.parse_args()

    command = ns.command[0]

    try:
        isolated_cores = os.environ['TUNED_isolated_cores']
    except:
        print "no isolated cores set, realtime profile not activating"
        sys.exit(0)

    cpulist = CpuList(isolated_cores)

    if command == 'start':
        start(cpulist)
    elif command == 'stop':
        stop(cpulist)
    elif command == 'verify':
        verify(cpulist)
    else:
        raise ValueError, "Invalid command: %s" % command
