
# Retpoline

## Files
* cmd.sh - Makefile to build and run gem5 and exploits
* no\_ret.log - Log file for attackv2/demoRet
* ret.log - Log file for attackv2/demo

* ./attackv2:
    * attack.c - Code to mistrain the btb
    * demo - Executable for the attack compiled without Retpoline
    * demo.disas - Assembly for the attack compiled without Retpoline
    * demoRet - Executable for the attack compiled with Retpoline
    * demoRet.disas - Assembly for the attack compiled with Retpoline
    * gdb\_commands.txt - Used by Makefiles to print the address of the secret
    * makeRet.sh - Build and link the exploit code with Retpoline
    * make.sh - Build and link the exploit code without Retpoline
    * victim.c - Code that makes an indirect jump

## Major changes in the simulator.

We made following major changes in gem5:

## How to run the exploit
Run without retpoline enabled
```
./cmd.sh makeDemo
```
Run with retpoline enabled
```
./cmd.sh makeDemoRet
```
## How to run the simulator

