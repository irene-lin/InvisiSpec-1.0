import sys
import argparse
import subprocess
import os
import shutil

irene_list = ["blackscholes", "bodytrack", "canneal", "dedup"]
maxwell_list = ["facesim", "ferret", "fluidanimate", "freqmine"]
jen_list = ["raytrace", "streamcluster", "swaptions", "vips", "x264"]


parsec_path = "/home/ulsi/18742/parsec-3.0"

parser = argparse.ArgumentParser(description='Run benchmarks.')
parser.add_argument('--arm', action="store_true",
  help="For running an ARM benchmark. Assumes you have ARM set up for GEM5")
parser.add_argument('--output', '-o', action="store_true",
  help="Will output a compressed log file named after exe if set")
parser.add_argument('--fs', action="store_true",
  help="If you want to use full system instead of syscall emulation");
parser.add_argument('--exe', default="attack_code/spectre_full.out",
  help="The program you want to benchmark")
parser.add_argument('--flags', default="",
  help="Debug flags you want set - use one string, comma separated")
parser.add_argument('--setup', default="",
  help="Usage: '--setup <Jen, Irene, Maxwell> (choose your name)'")
parser.add_argument('--runparsec', default="",
  help="""Usage: '--runparsec <Jen, Irene, Maxwell> (choose your name).
  Assumes the correct setup has been run already.'""")
parser.add_argument('--cpu', default="DerivO3CPU",
  help="The CPU model for GEM5. Default iS Deriv03CPU")
parser.add_argument('--start', default="",
  help="CPU ticks to start logging at")


def setup_command_line(args):
    arch = "X86"
    flags = ""
    output = ""
    start = ""
    cpu = "DerivO3CPU"
    extra = ""
    if args.fs:
        config="fs"
        exe = "--script="
        extra = "--kernel=vmlinux --disk-image=amd64-linux.img"
    else:
        exe = "--cmd="
        config = "se"
    if args.arm:
        arch = "ARM"
    if args.exe:
        exe += args.exe
    else:
        exe +="spectre_full.out"
    if args.output:
        output = "--debug-file=" + exe.split("/")[-1].split(".")[0]+".out.gz"
    if args.flags:
        flags = "--debug-flags=%s"%(args.flags)
    if args.start:
        start = "--debug-start=%s"(args.start)

    s = """build/{arch}/gem5.opt {flags} {output} {start} \
    configs/example/{config}.py \
    {exe} --cpu-type={cpu} --caches --l1d_size=64kB --l1i_size=16kB \
    --needsTSO=0 --scheme=UnsafeBaseline {extra}""".format(
    arch=arch, config=config, exe=exe, flags=flags, output=output,
    cpu=cpu, start=start, extra=extra)
    return s

def setup_parsec():
    os.environ["M5_PATH"] = "/home/ulsi/18742/InvisiSpec-1.0/x86-system"
    gcc_bldconf = os.path.join(parsec_path, "config", "gcc.bldconf")
    ret_bldconf = os.path.join(parsec_path, "config", "ret.bldconf")


    # Replace -O3 with -O so the case statements don't get optimized
    with open(gcc_bldconf, 'r') as file :
      filedata = file.read()

    # Replace the target string
    filedata = filedata.replace('-O3', '-O')

    # Write the file out again
    with open(gcc_bldconf, 'w') as file:
        file.write(filedata)


    # Create the ret_bldconf by copying gcc bldconf
    shutil.copyfile(gcc_bldconf, ret_bldconf)

    # Add the -mindirect-branch=thunk flag
    with open(ret_bldconf, 'r') as file :
      filedata = file.read()

    # Replace the target string
    filedata = filedata.replace('-fprefetch-loop-arrays ',
        '-fprefetch-loop-arrays -mindirect-branch=thunk ')

    # Write the file out again
    with open(ret_bldconf, 'w') as file:
        file.write(filedata)

    # Set up the config files

    pkg_dir =  os.path.join(parsec_path, "pkgs")
    # For all the apps and dependencies, we need to copy local gcc.bldconf
    # files to ret.bldconf
    for dirs in os.listdir(pkg_dir):
        app_dir = os.path.join(pkg_dir, dirs)
        for apps in os.listdir(app_dir):
            cfg_dir = os.path.join(app_dir, apps)
            current_cfg = os.path.join(cfg_dir, "parsec", "gcc.bldconf")
            new_cfg = os.path.join(cfg_dir, "parsec", "ret.bldconf")
            if os.path.exists(current_cfg):
                shutil.copyfile(current_cfg, new_cfg)


def build_parsec(list):
    os.chdir(parsec_path)
    for workload in list:
        subprocess.call(["bin/parsecmgmt", "-a", "build", "-c", "ret", "-p",
                        workload])
        subprocess.call(["bin/parsecmgmt", "-a", "build", "-c", "gcc", "-p",
                        workload])

def run_parsec(list):
    arch = "X86"
    flags = ""
    output = ""
    start = ""
    cpu = "DerivO3CPU"
    extra = "--kernel=vmlinux --disk-image=amd64-linux.img"
    if args.arm:
        arch = "ARM"
    if args.flags:
        flags = "--debug-flags=%s"%(args.flags)
    if args.start:
        start = "--debug-start=%s"(args.start)

    for workload in list:

        # Set up and run the normal gcc version
        script_name = workload + "_gcc"

        if args.output:
            output = "--debug-file=" + script_name +".out.gz"

        s = """build/{arch}/gem5.opt {flags} {output} {start} \
            configs/example/fs.py {extra} \
            --script={exe} --cpu-type={cpu} --caches --l1d_size=64kB \
            --l1i_size=16kB --needsTSO=0 --scheme=UnsafeBaseline \
            """.format(
            arch=arch, exe=script_name, flags=flags,
            output=output, cpu=cpu, start=start, extra=extra)
        subprocess.call(s.split())
        print("\nDone running %s \n", script_name)

        # Move the stats file so that running other files doesn't clobber it
        old_stats_file = "/home/ulsi/18742/InvisiSpec-1.0/m5out/stats.txt"
        new_stats_file = "/home/ulsi/18742/InvisiSpec-1.0/m5out/" + \
                            "{sname}_stats.txt".format(sname = script_name)
        shutil.copyfile(old_stats_file, new_stats_file)

        # Set up and run the retpoline compiled version
        script_name = workload + "_ret"

        if args.output:
            output = "--debug-file=" + script_name +".out.gz"

        s = """build/{arch}/gem5.opt {flags} {output} {start} \
            configs/example/fs.py {extra} \
            --script=runparsec/{exe} --cpu-type={cpu} --caches \
            --l1d_size=64kB \
            --l1i_size=16kB --needsTSO=0 --scheme=UnsafeBaseline \
            """.format(
            arch=arch, exe=script_name, flags=flags,
            output=output, cpu=cpu, start=start, extra=extra)
        subprocess.call(s.split())
        print("\nDone running %s \n", script_name)

# Just used this to copy the gcc shell scripts so a ret version existed too
def copy_gcc_ret():
    workloads = jen_list + irene_list + maxwell_list
    for workload in workloads:
        gcc_file = os.path.join("/home/ulsi/18742/InvisiSpec-1.0/runparsec",
                                workload + "_gcc")
        ret_file = os.path.join("/home/ulsi/18742/InvisiSpec-1.0/runparsec",
                                workload + "_ret")
        if (not os.path.exists(ret_file)):
            shutil.copyfile(gcc_file, ret_file)

            # Replace the "gcc" with "ret"
            with open(ret_file, 'r') as file :
              filedata = file.read()

            # Replace the target string
            filedata = filedata.replace('gcc', 'ret')

            # Write the file out again
            with open(ret_file, 'w') as file:
                file.write(filedata)

            #Make it executable
            os.chmod(ret_file, 777)


if __name__ == "__main__":
    os.environ["M5_PATH"] = "/home/ulsi/18742/InvisiSpec-1.0/x86-system"
    args = parser.parse_args()

    if (args.setup == "Jen"):
        setup_parsec()
        build_parsec(jen_list)

    if (args.setup == "Irene"):
        setup_parsec()
        build_parsec(irene_list)
    if (args.setup == "Maxwell"):
        setup_parsec()
        build_parsec(maxwell_list)

    if (args.runparsec == "Jen"):
        run_parsec(jen_list)
    if (args.runparsec == "Irene"):
        run_parsec(irene_list)
    if (args.runparsec == "Maxwell"):
        run_parsec(maxwell_list)

    elif (args.runparsec == "" and args.setup == ""):
        command_line = setup_command_line(args).split()
        print(command_line)
        subprocess.call(command_line)
