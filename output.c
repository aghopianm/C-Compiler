#include <stdio.h>

int main() {
    double x = 5.2;
    double y = 10.11;
    int a = 22;
    int z = 5;
    int azres = a + z;
    double result = x / y;
    if (x < 10) {
        printf("%d\n", x);
    }
    while (x < 10) {
        x = x + 1;
    }
    for (int i = 0; i < 10; i++) {
        printf("%d\n", i);
    }
    return 0;
}