import sys
import argparse
import subprocess
import os
import shutil
import glob

irene_list = ["blackscholes", "bodytrack", "canneal", "dedup"]
maxwell_list = ["facesim", "ferret", "fluidanimate", "freqmine"]
jen_list = ["raytrace", "streamcluster", "swaptions", "vips", "x264"]

suite = {
    "Maxwell":"intrate",
    "Irene":"core4fprate",
    "Jen":"fprate",
    "Last": "intspeed"
}

suite_benchmarks = {
    "intrate" : ["xalancbmk_r", "deepsjeng_r", "leela_r", "xz_r"],
    "intspeed" : ["mcf_s", "omnetpp_s","xalancbmk_s", "deepsjeng_s",
                 "leela_s", "xz_s"],
    "fpspeed"  : ["cactuBSSN_s", "lbm_s", "wrf_s", "cam4_s", "pop2_s",
                  "imagick_s", "nab_s"],
    "fprate"  : ["namd_r", "parest_r", "povray_r",
                 "lbm_r", "wrf_r"],
    "core4fprate" : ["blender_r", "cam4_r", "imagick_r", "nab_r"]
}
parsec_path = "/home/ulsi/18742/parsec-3.0"
spec_dir = "/home/ulsi/18742/spec"
gem5_path="/home/ulsi/18742/InvisiSpec-1.0"

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
parser.add_argument('--setupparsec', default="",
  help="Usage: '--setup <Jen, Irene, Maxwell> (choose your name)'")
parser.add_argument('--setupspec', default="",
  help="Usage: '--setup <Jen, Irene, Maxwell> (choose your name)'")
parser.add_argument('--runparsec', default="",
  help="""Usage: '--runparsec <Jen, Irene, Maxwell> (choose your name).
  Assumes the correct setup has been run already.'""")
parser.add_argument('--runspec', default="",
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


    # Add "-case-values-threshold 1" so the case statements don't get optimized
    with open(gcc_bldconf, 'r') as file :
      filedata = file.read()

    # Replace the target string
    filedata = filedata.replace('-fprefetch-loop-arrays ',
        '-fprefetch-loop-arrays -case-values-threshold 1 ')

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
        '-fprefetch-loop-arrays \
        -mindirect-branch=thunk \
        --param case-values-threshold 1')

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


def setup_spec(person):


    # doing extremely secure things with sudo password to mount the SPEC CD
    command_line = "echo 18664 | sudo -S \
                    mount -t iso9660 /dev/cdrom /media/cdrom"
    subprocess.call(command_line, shell=True)

    # update gcc while we're doing this
    command_line = "sudo apt -y update && \
                    sudo add-apt-repository -y ppa:ubuntu-toolchain-r/test && \
                    sudo apt -y install gcc-9 g++-9"

    subprocess.call(command_line, shell = True)

    # Install SPEC
    command_line = "sudo /media/cdrom/install.sh -d \
                    {dir} -f".format(dir = spec_dir)
    subprocess.call(command_line, shell = True)

    orig_bldconf = "{dir}/config/Example-gcc-linux-x86.cfg".format(
                                                            dir = spec_dir)

    gcc_bldconf = "{dir}/config/baseline.cfg".format(dir = spec_dir)

    ret_bldconf = "{dir}/config/retpoline.cfg".format(dir = spec_dir)

    shutil.copyfile(orig_bldconf, gcc_bldconf)

    with open(gcc_bldconf, 'r') as file :
      filedata = file.read()

    # Update label
    filedata = filedata.replace("label mytest ",
        'label baseline')

    # Update number of cores to build with
    filedata = filedata.replace("build_ncpus 8", "build_ncpus 2")
    filedata = filedata.replace("CC                      = $(SPECLANG)gcc ",
                                "CC                      = $(SPECLANG)gcc-9 ")
    filedata = filedata.replace("CXX                     = $(SPECLANG)g++",
                                "CXX                     = $(SPECLANG)g++-9")
    filedata = filedata.replace("FC                      = $(SPECLANG)fortran",
                            "FC                      = $(SPECLANG)fortran-9")

    filedata = filedata.replace("gcc_dir        /opt/rh/devtoolset-7/root/usr",
                                "gcc_dir        /usr")

    # Add -case-values-threshold 1 to not optimize out indirect jumps
    # (do we want this?)
    filedata = filedata.replace("-O3 -march=native ",
        "-O3 -march=native --param case-values-threshold=1 ")

    # Write the file out again
    with open(gcc_bldconf, 'w') as file:
        file.write(filedata)

    shutil.copyfile(gcc_bldconf, ret_bldconf)

    with open(ret_bldconf, 'r') as file :
      filedata = file.read()

    # Update label and add flags
    filedata = filedata.replace("label baseline ",
        'label ret')
    filedata = filedata.replace("-O3 -march=native ",
        "-O3 -march=native -mindirect-branch=thunk ")

    # Write the file out again
    with open(ret_bldconf, 'w') as file:
        file.write(filedata)

    # Source the shrc and test the build
    subprocess.call("cd {dir} && chmod +x shrc && ./shrc \
                    && runcpu --config=baseline.cfg \
                    --action=runsetup --threads=1 \
                    --size=ref \
                    {suite}".format(suite=suite[person],
                                    dir = spec_dir), shell=True)

    # Source the shrc and test the build
    subprocess.call("cd {dir} && ./shrc \
                    && runcpu --config=ret.cfg \
                    --action=runsetup --threads=1 \
                    --size=ref \
                    {suite}".format(suite=suite[person], dir=spec_dir),
                    shell=True)

def run_spec(user):
    benchmarks = suite_benchmarks[suite[user]]

    rate_speed = "rate"
    if "speed" in suite[user]:
        rate_speed = "speed"

    base_dir = "run_base_ref{rs}_baseline-m64.0000".format(rs=rate_speed)
    ret_dir = "run_base_ref{rs}_ret-m64.0000".format(rs=rate_speed)

    for benchmark in benchmarks:
        bench_top_dir = glob.glob(
        "{spec_dir}/benchspec/CPU/*.{benchmark}/run".format(
        spec_dir=spec_dir, benchmark=benchmark))
        if not bench_top_dir:
            print (
            "ERROR: Could not locate benchmark top level directory for\
            {}".format(benchmark))
            continue

        bench_top_dir = bench_top_dir[0]

        bench_base_dir = os.path.join(bench_top_dir, base_dir)
        bench_ret_dir = os.path.join(bench_top_dir, ret_dir)

        print("Benchmark baseline: {}".format(bench_base_dir))
        print("Benchmark retpoline: {}".format(bench_ret_dir))

        specinvoke = subprocess.check_output(
        "{spec_dir}/bin/specinvoke -n {bench_dir}/speccmds.cmd | \
        grep -v '#'".format(
        spec_dir=spec_dir, bench_dir=bench_base_dir), shell=True)
        print(specinvoke)
        specinvoke = specinvoke.split("\n")[0]
        specinvoke = specinvoke.split()
        idx1 = specinvoke.index(">") if ">" in specinvoke else len(specinvoke)
        idx2 = specinvoke.index("<") if "<" in specinvoke else len(specinvoke)
        bench_bin = specinvoke[0]
        bench_opts = specinvoke[1:min(idx1, idx2)]
        print("\n--- Running simulation: {} {} ---".format(
        bench_bin, " ".join(bench_opts)))

        # From the exp_script
        run_cmd = ("{gem5_path}/build/X86/gem5.opt " +
            "{gem5_path}/configs/example/se.py --output=gem5_run.log " +
            "--cmd={bench_bin} --options=\'{bench_opts}\' " +
            "--num-cpus=1 --mem-size=2GB " +
            "--l1d_assoc=8 --l2_assoc=16 --l1i_assoc=4 " +
            "--cpu-type=DerivO3CPU --needsTSO=0 --scheme=UnsafeBaseline " +
            "--caches --maxinsts=2000000000 ").format(
                gem5_path=gem5_path,
                bench_bin=bench_bin, bench_opts=" ".join(bench_opts))

        print("\n--- GEM5 run_cmd: {} ---".format(run_cmd))

        try:
            print("\n--- GEM5 running baseline simulation: \
            {} > {} ---\n".format(
            bench_base_dir, os.path.join(bench_base_dir, "gem5_run.log")))

            subprocess.call("cd {} && {}".format(bench_base_dir,
            run_cmd), shell=True)
        except subprocess.CalledProcessError as e:
            print("ERROR: GEM5 baseline simulation returned errcode {}".format(
                e.returncode))

            continue

        # Run retpoline compiled code
        specinvoke = subprocess.check_output(
            "{spec_dir}/bin/specinvoke -n \
            {bench_dir}/speccmds.cmd | grep -v '#'".format(
            spec_dir=spec_dir, bench_dir=bench_ret_dir), shell=True)
        specinvoke = specinvoke.split("\n")[0]
        specinvoke = specinvoke.split()
        idx1 = specinvoke.index(">") if ">" in specinvoke else len(specinvoke)
        idx2 = specinvoke.index("<") if "<" in specinvoke else len(specinvoke)
        bench_bin = specinvoke[0]
        bench_opts = specinvoke[1:min(idx1, idx2)]
        print("\n--- Running simulation: {} \
        {} ---".format(bench_bin, " ".join(bench_opts)))

        # From the exp_script
        run_cmd = ("{gem5_path}/build/X86/gem5.opt " +
            "{gem5_path}/configs/example/se.py --output=gem5_run.log " +
            "--cmd={bench_bin} --options=\'{bench_opts}\' " +
            "--num-cpus=1 --mem-size=2GB " +
            "--l1d_assoc=8 --l2_assoc=16 --l1i_assoc=4 " +
            "--cpu-type=DerivO3CPU --needsTSO=0 --scheme=UnsafeBaseline " +
            "--caches --maxinsts=2000000000 ").format(
                gem5_path=gem5_path,
                bench_bin=bench_bin, bench_opts=" ".join(bench_opts))

        print("\n--- GEM5 run_cmd: {} ---".format(run_cmd))

        try:
            print("\n--- GEM5 running ret simulation: {} > {} ---\n".format(
                bench_ret_dir, os.path.join(bench_base_dir, "gem5_run.log")))

            subprocess.call("cd {} && {}".format(bench_ret_dir,
            run_cmd), shell=True)
        except subprocess.CalledProcessError as e:
            print("ERROR: GEM5 ret simulation returned errcode  {}".format(
                e.returncode))

            continue

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
    if (args.setupspec != ""):
        setup_spec(args.setupspec)

    if (args.runspec != ""):
        run_spec(args.runspec)

    if (args.setupparsec == "Jen"):
        setup_parsec()
        build_parsec(jen_list)

    if (args.setupparsec == "Irene"):
        setup_parsec()
        build_parsec(irene_list)
    if (args.setupparsec == "Maxwell"):
        setup_parsec()
        build_parsec(maxwell_list)

    if (args.runparsec == "Jen"):
        run_parsec(jen_list)
    if (args.runparsec == "Irene"):
        run_parsec(irene_list)
    if (args.runparsec == "Maxwell"):
        run_parsec(maxwell_list)

    elif (args.runparsec == ""
          and args.runspec == ""
          and args.setupparsec == ""
          and args.setupspec == ""):
        command_line = setup_command_line(args).split()
        print(command_line)
        subprocess.call(command_line)
