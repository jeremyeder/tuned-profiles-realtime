from procfs import procfs
import os, sys
from os import listdir
from os.path import isdir, join

def bitmasklist(line):
        fields = line.strip().split(",")
        bitmasklist = []
        entry = 0
        for i in range(len(fields) - 1, -1, -1):
                mask = int(fields[i], 16)
                while mask != 0:
                        if mask & 1:
                                bitmasklist.append(entry)
                        mask >>= 1
                        entry += 1
        return bitmasklist

def get_cpumask(mask):
	groups = list()
	comma = 0
	while mask:
		cpumaskstr = ''
		m = mask & 0xffffffff
		cpumaskstr += ('%x' % m)
		if comma:
			cpumaskstr += ','
		comma = 1
		mask >>= 32
		groups.append(cpumaskstr)
	string = ''
	for i in reversed(groups):
		string += i
	return string

def parse_def_affinity(self, fname):
	if os.getuid() != 0:
		return
	try:
                f = file(fname)
                line = f.readline()
                f.close()
                return bitmasklist(line)
        except IOError:
                return [ 0, ]

def verify(shouldbemask):
	inplacemask = 0
	fname = "/proc/irq/default_smp_affinity";
	cpulist = parse_def_affinity(ints, fname)
	for i in cpulist:
		inplacemask = inplacemask | 1 << i;
	if (inplacemask & ~shouldbemask):
		sys.stderr.write("verify: failed: irqaffinity (%s) inplacemask=%x shouldbemask=%x\n" % (fname, inplacemask, shouldbemask))
		sys.exit(1)

	# now verify each /proc/irq/$num/smp_affinity
	interruptdirs = [ f for f in listdir(irqpath) if isdir(join(irqpath,f)) ]
	# IRQ 2 - cascaded signals from IRQs 8-15 (any devices configured to use IRQ 2 will actually be using IRQ 9)
	interruptdirs.remove("2")
	# IRQ 0 - system timer (cannot be changed)
	interruptdirs.remove("0")

	for i in interruptdirs:
		inplacemask = 0
		fname = "/proc/irq/" + i + "/smp_affinity"
		cpulist = parse_def_affinity(ints, fname)
		for i in cpulist:
			inplacemask = inplacemask | 1 << i;
		if (inplacemask & ~shouldbemask):
			sys.stderr.write("verify: failed: irqaffinity (%s) inplacemask=%x shouldbemask=%x\n" % (fname, inplacemask, shouldbemask))
		sys.exit(1)

	sys.exit(0)


irqpath = "/proc/irq/"
isolcpulist = open(sys.argv[2])

ints = procfs.interrupts()

# adjust default_smp_affinity
cpulist = parse_def_affinity(ints, "default_smp_affinity")
mask = 0
for i in cpulist:
	mask = mask | 1 << i;

line = isolcpulist.readline()
fields = line.strip().split(",")

for i in fields:
	if sys.argv[1] == "add":
		mask = mask | 1 << int(i);
	elif sys.argv[1] == "remove" or sys.argv[1] == "verify":
		mask = mask & ~(1 << int(i));
		
if sys.argv[1] == "verify":
	verify(mask)

string = get_cpumask(mask)

fo = open("/proc/irq/default_smp_affinity", "wb")
fo.write(string)
fo.close()

# now adjust each /proc/irq/$num/smp_affinity

interruptdirs = [ f for f in listdir(irqpath) if isdir(join(irqpath,f)) ]

# IRQ 2 - cascaded signals from IRQs 8-15 (any devices configured to use IRQ 2 will actually be using IRQ 9)
interruptdirs.remove("2")
# IRQ 0 - system timer (cannot be changed)
interruptdirs.remove("0")

for i in interruptdirs:
	fname = "/proc/irq/" + i + "/smp_affinity"
	cpulist = parse_def_affinity(ints, fname)
	mask = 0
	for i in cpulist:
		mask = mask | 1 << i;
	for i in fields:
		if sys.argv[1] == "add":
			mask = mask | 1 << int(i);
		elif sys.argv[1] == "remove":
			mask = mask & ~(1 << int(i));
	string = get_cpumask(mask)
	fo = open(fname, "wb")
	fo.write(string)
	fo.close()

