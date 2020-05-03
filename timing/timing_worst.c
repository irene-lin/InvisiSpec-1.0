/** @file timing_worst.c
 *  @author Irene Lin (iwl)
 *  @brief  Timing analysis for indirect branch that always misses
 */

#define ITERATIONS 1000
int arr[ITERATIONS];

typedef void fn_t(int);

void indirect1(int a) {
    arr[a] = a;
}

void indirect2(int a) {
    arr[a] = a*2;
}

int main()
{
    int i;
    fn_t *func;
    for (i=0; i<ITERATIONS; i++) {
        func = (i%2) ? &indirect1 : &indirect2;
        (*func)(i);
    }

    return 0;
}
