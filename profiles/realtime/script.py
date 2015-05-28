#!/usr/bin/python -tt

import os
import sys
import subprocess
import argparse

class CpuList(object):

    def __init__(self, cpurange):
        self.online = self.cpus()
        self.range = self.expand(cpurange)
        
    # return the number of cpus online
    def cpus(self):
        p = subprocess.Popen(['lscpu'], stdout=subprocess.PIPE, shell=False)
        for l in p.stdout.readlines():
            if l.startswith("CPU(s)"):
                return int(l.split()[1])
        return 0

    # expand a string cpu range into a flat array of integers
    # ['2','4-7'] -> [2, 4, 5, 6, 7 ]
    def expand(self):
        result = []
        for part in self.range.split(','):
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

    # return the compliment of an array of cpu numbers
    def compliment(self):
        return [ x for x in range(0, self.online) if x not in self.range ]

    # return true if the value x is the next consecutive number from the last entry
    # of array a
    def consecutive (self, a, x):
        #print a, x
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
    def extend_range(self, r):
        if '-' in r:
            a,b = r.split('-')
            return "%s-%s" % (a, str(int(b)+1))
        else:
            return "%s-%s" % (r, str(int(r)+1))

    # given a list of cpus 'l', return a compressed array of strings
    # [ 2, 4, 5, 6, 7 ] -> ['2', '4-7']
    def contract(self):
        result = []
        l = self.range
        while (len(l)):
            end = len(l) - 1
            if consecutive(result, l[0]):
                r = extend_range(result.pop())
                #print "new range: ", r
            else:
                r = str(l[0])
            result.extend([r])
            l = l[1:]
            return result
######################################################################
# start of script logic

def start(cpulist):
    pass

def stop(cpulist):
    pass

def verify(cpulist):
    pass

def read_variables(path):
    variables = {}
    f = open(path)
    for l in f.readline():
        if l.startswith('#'): continue
        if '=' in l:
            n,v  = l.split('=')
            variables[n] = v
    close f
    return variables


if __name__ == "__main__":

    parser = argparse.ArgumentParser(description='process tuned profile script argument')
    parser.add_argument('command', nargs=1, choices=['start', 'stop', 'verify'])

    ns = parser.parse_args()

    command = ns.command[0]

    try:
        isolated_list = sys.environ['ISOLATED_CORES']
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
