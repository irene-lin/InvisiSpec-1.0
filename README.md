
# Retpoline

## Files
* cmd.sh - Makefile to build and run gem5 and exploits
* demoRet.log - Log file for attackv2/demoRet
* demo.log - Log file for attackv2/demo

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

* ./timing:
    * make\_timing.sh - Build the timing benchmarks
    * timing\_best.c - Makes many indirect jumps to the same function
    * timing\_best.disas - timing\_best.c benchmark compiled without Retpoline
    * timing\_best\_ret.disas - timing\_best.c benchmark compiled with Retpoline
    * timing\_worst.c - Makes many indirect jumps to alternating functions
    * timing\_worst.disas - timing\_worst.c benchmark compiled with Retpoline
    * timing\_worst\_ret.disas - timing\_worst.c benchmark compiled with Retpoline
    
## Major changes in the simulator.

We made following major changes in gem5:

## How to compile the exploit
Run without retpoline enabled. This will generate demo and demo.disas
```
./cmd.sh makeDemo
```
Run with retpoline enabled. This will generate demoRet and demoRet.disas
```
./cmd.sh makeDemoRet
```
The above two commands will also output the gadget target address, benign comparison function target address, and the addresses of the indirect branch instructions.
## How to run the simulator
Recompile GEM5 if you haven't already.
```
./cmd.sh make
```
Simulate execution for demo without Retpoline enabled. Run with debug flags Exec,Indirect,Cache and pipe output to a file.
```
./cmd.sh sim Exec,Indirect,Cache attackv2/demo > demo.log
```
Simulate execution for demo with Retpoline enabled. Use same debug flags
```
./cmd.sh sim Exec,Indirect,Cache attackv2/demoRet > demoRet.log
```
## How to run timing benchmarks
This command will simulate in gem5 timing\_best.c without Repoline and with Repoline, and then simulate in gem5 timing\_worst.c without Retpoline and with Retpoline.
```
./cmd.sh timing
```
