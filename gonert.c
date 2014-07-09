#include <stdio.h>

void _print_int(int x) {
  printf("%i\n", x);
}

void _print_float(double x) {
  printf("%f\n", x);
}

void _print_bool(int x) {
  if (x == 1) {
    printf("true\n");
  } else if (x == 0) {
    printf("false\n");
  }
}
