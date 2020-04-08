#ifndef VICTIM_H
#define VICTIM_H

/* Print using a syscall for cases where we don't want to add a ton of cycles */
#define PRINT(s) write(STDOUT_FILENO, s, sizeof(s) - 1)

extern char *secret;

void gadget(void);

typedef int cmp_func_t(int, int);

int example_cmp(int a, int b);
int victim_entry(cmp_func_t *cmp);

#endif /* VICTIM_H */
