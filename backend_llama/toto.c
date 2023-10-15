#include <stdio.h>
#include <stdlib.h>

int main(void)
{
    while (1) {
        char *addr = malloc(1);
        printf("%x  Running in interactive mode.\n", addr);
    }
}
