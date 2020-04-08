#!/bin/bash
#list all commands
if [ "$1" = "help" ]; then
    echo "attack path/file.c: compile and run file.c without retpoline flags"
    echo "attack_ret path/file.c: compile and run file.c with retpoline flags"
    echo "sim debugFlag path/executable: run gem5 using debugFlag on executable"
    echo "makesim debugFlag path/executable: same as sim, but also recompiles gem5"
    echo "make: recompiles gem5"
    
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
    build/X86/gem5.opt --debug-flags="$2" configs/example/se.py \
    --cmd="$3" --cpu-type=DerivO3CPU --caches \
    --l1d_size=64kB --l1i_size=16kB --needsTSO=0 --scheme=UnsafeBaseline
#recompile and run gem5 using debugFlag on executable
elif [ "$1" = "makesim" ]; then
    scons build/X86/gem5.opt;
    build/X86/gem5.opt --debug-flags="$2" configs/example/se.py \
    --cmd="$3" --cpu-type=DerivO3CPU --caches \
    --l1d_size=64kB --l1i_size=16kB --needsTSO=0 --scheme=UnsafeBaseline

#recompile gem5
elif [ "$1" = "sim" ]; then
    scons build/X86/gem5.opt;
    
else
    echo "invalid command"
fi