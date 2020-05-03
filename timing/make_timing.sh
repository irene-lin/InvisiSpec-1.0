# compile without retpoline enabled
gcc -ggdb3 -std=c99 -static -O0 -Wall -Wextra -Werror -g -o timing_best timing_best.c
gcc -ggdb3 -std=c99 -static -O0 -Wall -Wextra -Werror -g -o timing_worst timing_worst.c
# compile with retpoline enabled
gcc -mindirect-branch=thunk -ggdb3 -std=c99 -static -O0 -Wall -Wextra -Werror -g -o timing_best_ret timing_best.c
gcc -mindirect-branch=thunk -ggdb3 -std=c99 -static -O0 -Wall -Wextra -Werror -g -o timing_worst_ret timing_worst.c

# Disassemble
objdump -d timing_best > timing_best.disas
objdump -d timing_worst > timing_worst.disas
objdump -d timing_best_ret > timing_best_ret.disas
objdump -d timing_worst_ret > timing_worst_ret.disas
