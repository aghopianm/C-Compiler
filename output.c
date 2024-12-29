#include <stdio.h>

int main() {
    float x = 5.2;
    float y = 10.11;
    float result = x / y;
    if (x < 10) {
        printf("%f\n", x);
    }
    while (x < 10) {
        x = x + 1;
    }
    for (int i = 0; i < 10; i++) {
        printf("%d\n", i);
    }
    return 0;
}