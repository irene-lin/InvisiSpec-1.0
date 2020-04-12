# Overview:

This is a highly-edited version of the README from SpectreGuard with
their instructions for installing a full system image for use with
Gem5.

# Unpacking the system image:

gem5 requires a system image to run on. One has been provided. To unpack it:
```
    cd BASE_DIR/x86-system-parts/
    ./restore_system.pl
```

This system is ready to run the synthetic benchmark right out of the box,
    but you will need to mount it if you would like to build it yourself,
    or you would like to add the spec2006 benchmark files.

To mount the system simply:
```
    cd BASE_DIR/x86-system/disks/
    sudo mount -o loop,offset=$((2048*512)) amd64-linux.img tempdir
```

tempdir will now contain the system files.
The OS utilizes busybox.
On boot, the init script creates a checkpoint and then loads and runs a script
    that is passed in on the gem5 command line. There is also an init script in
    /etc for booting to a terminal.

# Building spec2006:

We cannot provide spec2006 as it is licensed. To add this benchmark, you must
    first build spec2006 statically, and then copy the desired tests into the
    following tree structure:

```
    BASE_DIR/x86-system/disks/tempdir/usr/bin/spec/
        astar/
            astar_base.gcc43-64bit
            BigLakes2048.bin
            BigLakes2048.cfg
            rivers.bin
            rivers.cfg
        bwaves/
            bwaves_base.gcc43-64bit
            bwaves.in
        bzip2/
            ......
        .......
```

A complete list of benchmarks and files required can be found in the script
    for running the benchmarks, along as in the scripts folder which contains
    the individual scripts for each benchmark.

# Building the Linux Kernel:

A pre-built linux kernel has been included in x86-system/binaries/.
See the original SpectreGuard project for instructions for generating it.

# Viewing output:

When the system is run, its output is directed to a directory (see
OUTPUT_DIR in cmd.sh). stdout can be found in a file like
system.pc.com_1.device in that directory. gem5 also ships with a
terminal for connecting to the simulated system (though I believe any
serial terminal will do). To use the terminal:

```
cd util/term/
make
./m5term localhost 3456
```

The port can be found when the simulator begins and prints a line like
"Listening for com_1 connection on port 3456".