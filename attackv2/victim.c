#include "victim.h"
#include <unistd.h>

/* Compile with -ffixed-ebx to turn ebx into your own private
 * variable, reducing interference from the rest of the code */

/* We should never read this variable in normal program operation */
char *secret = "foobar";

void gadget(void) {
    /* The purpose of the gadget is to access the secret to get it
     * into the cache. We generally can't execute the gadget directly;
     * instead, the point of Spectre v2 is to speculatively execute
     * this function. In general, there isn't a gadget in the program
     * that will directly access the secret, so a gadget will use some
     * value given by the attacker to perform the memory access (here,
     * a register)
     */

    /* ebx = *ebx */
    __asm("mov (%rbx),%rbx");
}

int example_cmp(int a, int b) {
    return a < b;
}

int victim_entry(cmp_func_t *cmp) {
    PRINT("Begin victim_entry\n");

    /* We need an indirect branch, which the attacker will poison so
     * we speculatively execute the gadget. This function calls cmp, a
     * function pointer, which will compilie to an indirect branch.
     * An attacker could cause this function to directly call the
     * gadget, but in the general case it may not be possible, or may
     * not return cleanly.
     */

    int array[5] = {5, 4, 3, 2, 1};
    int sorted = 1;
    for (size_t i = 1; i < sizeof(array) / sizeof(int); i++) {
        sorted &= (*cmp)(array[i-1], array[i]);
    }

    PRINT("End victim_entry\n");
    return sorted;
}
