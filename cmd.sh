#!/bin/bash

GEM5="build/X86/gem5.opt"

#list all commands
if [ "$1" = "help" ]; then
    echo ""
    echo "attack path/file.c                : compile and run file.c without retpoline flags"
    echo "attack_ret path/file.c            : compile and run file.c with retpoline flags"
    echo "sim debugFlag path/executable     : run gem5 using debugFlag on executable"
    echo "makesim debugFlag path/executable : same as sim, but also recompiles gem5"
    echo "make                              : recompiles gem5"
    echo "fs path/script                    : Run script on the full system (examples in scripts/)"
    echo ""

#compile and run attack code with retpoline flags
elif [ "$1" = "attack" ]; then
    gcc -O0 -ggdb3 -std=c99 \
        -static -o attack_code/a.out "$2";
    ./attack_code/a.out;
elif [ "$1" = "attack_ret" ]; then
    gcc -mindirect-branch=thunk -mfunction-return=thunk -O0 -ggdb3 -std=c99 \
        -static -o attack_code/a.out "$2";
    ./attack_code/a.out;

#run gem5 using debugFlag on executable
elif [ "$1" = "sim" ]; then
    $GEM5 --debug-flags="$2" configs/example/se.py \
    --cmd="$3" --cpu-type=DerivO3CPU --caches \
    --l1d_size=64kB --l1i_size=16kB --needsTSO=0 --scheme=UnsafeBaseline
#recompile and run gem5 using debugFlag on executable
elif [ "$1" = "makesim" ]; then
    scons $GEM5;
    $GEM5 --debug-flags="$2" configs/example/se.py \
    --cmd="$3" --cpu-type=DerivO3CPU --caches \
    --l1d_size=64kB --l1i_size=16kB --needsTSO=0 --scheme=UnsafeBaseline

#recompile gem5
elif [ "$1" = "make" ]; then
    scons $GEM5;

#run using the full system
elif [ "$1" = "fs" ]; then
    # Where to find the kernel (in binaries/) and the disk image (in disks/)
    M5_PATH=$M5_PATH:./x86-system

    # Location of checkpoints and stats
    # Change this to create a new checkpoint, necessary if you change parameters
    OUTPUT_DIR="checkpoints/vmlinux"

    # Check for a checkpoint file (cpt*) in the directory
    if ls $OUTPUT_DIR/cpt* > /dev/null 2>&1; then
        # If a checkpoint exists, use it
        CHECKPOINT_FLAGS="--checkpoint-restore=1 --checkpoint-dir=$CHECKPOINT_DIR --restore-with-cpu=AtomicSimpleCPU"
    else
        # Otherwise, we need to specify the kernel
        CHECKPOINT_FLAGS="--kernel=vmlinux"
    fi

    $GEM5 -d $OUTPUT_DIR                                                   \
          configs/example/fs.py                                            \
          --num-cpus=1 --sys-clock=2GHz                                    \
          --mem-type=DDR3_1600_8x8 --mem-size=100MB                        \
          --caches --l2cache --l1d_size=64kB --l1i_size=32kB --l2_size=2MB \
          --cpu-type=DerivO3CPU --cpu-clock=2GHz                           \
          --network=simple --topology=Mesh_XY --mesh-rows=1                \
          --ruby --l1d_assoc=8 --l2_assoc=16 --l1i_assoc=4                 \
          --needsTSO=0 --scheme=UnsafeBaseline                             \
          --disk-image=amd64-linux.img                                     \
          $CHECKPOINT_FLAGS                                                \
          --script=$2
else
    echo "invalid command"
fi
