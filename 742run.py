import sys
import argparse
import subprocess

parser = argparse.ArgumentParser(description='Run benchmarks.')
parser.add_argument('--arm', action="store_true",
  help="For running an ARM benchmark. Assumes you have ARM set up for GEM5")
parser.add_argument('--output', '-o', action="store_true",
  help="Will output a compressed log file named after exe if set")
parser.add_argument('--exe', default="attack_code/spectre_full.out",
  help="The program you want to benchmark")
parser.add_argument('--flags', default="",
  help="Debug flags you want set - use one string, comma separated")
parser.add_argument('--cpu', default="DerivO3CPU",
  help="The CPU model for GEM5. Default iS Deriv03CPU")
parser.add_argument('--start', default="",
  help="CPU ticks to start logging at")
# arch: arm or x86
# output file: default to exe.split(".")[0].out
# debug flags: autoset to nothing
# defaults
#
def setup_command_line(args):
    arch = "X86"
    flags = ""
    exe = "spectre_full.out"
    output = ""
    cpu = "DerivO3CPU"
    start = ""
    if args.arm:
        arch = "ARM"
    if args.exe:
        exe = args.exe
    if args.output:
        output = "--debug-file=" + exe.split("/")[-1].split(".")[0]+".out.gz"
    if args.flags:
        flags = "--debug-flags=%s"%(args.flags)
    if args.start:
        start = "--debug-start=%s"(args.start)

    s = """build/{arch}/gem5.opt {flags} configs/example/se.py \
    --cmd={exe} --cpu-type={cpu} --caches --l1d_size=64kB --l1i_size=16kB \
    --needsTSO=0 --scheme=UnsafeBaseline {output} {start}""".format(
    arch=arch, exe=exe, flags=flags, output=output, cpu=cpu, start=start)
    return s

if __name__ == "__main__":
    args = parser.parse_args()
    command_line = setup_command_line(args).split()
    print(command_line)
    subprocess.call(command_line)
