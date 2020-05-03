/** @file timing_best.c
 *  @author Irene Lin (iwl)
 *  @brief  Timing analysis for indirect branch that doesnt miss
 */

#define ITERATIONS 1000
int arr[ITERATIONS];

typedef void fn_t(int);

void indirect(int a) {
    arr[a] = a;
}

int main()
{
    int i;
    fn_t *func = &indirect;
    for (i=0; i<ITERATIONS; i++) {
        (*func)(i);
    }

    return 0;
}
