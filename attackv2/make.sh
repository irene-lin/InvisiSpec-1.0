#!/bin/bash

# make.sh compiles the exploit code without repoline 
# and prints important addresses
# produces the binaries and asm

# Listen, Makefiles are hard, ok?

# Flags common to both files
FLAGS="-ffixed-ebx \
-ggdb3 -std=c99 -static -O0 -Wall -Wextra -Werror -g"

# Here's where you'd add retpoline
VICTIM_FLAGS=$FLAGS
ATTACK_FLAGS=$FLAGS

# Compile and assembly, but don't link
gcc -c $VICTIM_FLAGS victim.c -o victim.o
gcc -c $ATTACK_FLAGS attack.c -o attack.o

# Link
gcc $FLAGS victim.o attack.o -o demo

# Link
# ld /usr/lib/x86_64-linux-gnu/crti.o            \
#    /usr/lib/x86_64-linux-gnu/crtn.o            \
#    /usr/lib/x86_64-linux-gnu/crt1.o            \
#    -lc                                         \
#    victim.o attack.o                           \
#    -dynamic-linker /lib64/ld-linux-x86-64.so.2 \
#    -o main_ELF_executable

# Disassemble
# Change -d to -D to get a disassembly of everything statically linked in
objdump -d demo > demo.disas

# Get relevant addresses
grep -e '<example_cmp>' -e '<gadget>' -e '<victim_entry>' -e '4010ab:' -e '4014ab:' \
demo.disas

# print secret 
gdb demo  < gdb_commands.txt
