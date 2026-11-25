/* Confluence (replay for crew_visuals/euler_convenient_numbers.html): n is idoneal (Euler's convenient numbers) iff the form class group of discriminant -4n has exponent <= 2,
   i.e. iff there is NO primitive reduced form a x^2 + 2b xy + c y^2 (ac - b^2 = n) with 0 < 2b < a < c
   (such a form and its opposite (a, -2b, c) are distinct classes, inverse to each other). Prints every idoneal n <= N.
   Build and run:  cc -O2 -o idoneal_search tools/idoneal_search.c -lm && ./idoneal_search 5000000
   Output recorded 2026-11-25: 65 idoneal numbers up to 5,000,000, the largest 1848, in 0.09 s. */
#include <stdio.h>
#include <stdlib.h>
#include <math.h>
static long long g(long long x, long long y) { while (y) { long long t = x % y; x = y; y = t; } return x; }
int main(int argc, char **argv) {
    long long N = atoll(argv[1]), count = 0, last = 0;
    for (long long n = 1; n <= N; n++) {
        int idoneal = 1;
        long long amax = (long long) sqrt(4.0 * n / 3.0) + 2;          /* reduced: 2|b| <= a <= c and ac - b^2 = n give a <= sqrt(4n/3) */
        for (long long a = 3; a <= amax && idoneal; a++)
            for (long long b = 1; 2 * b < a; b++) {
                long long m = n + b * b;
                if (m % a) continue;
                long long c = m / a;
                if (c > a && g(g(a, 2 * b), c) == 1) { idoneal = 0; break; }
            }
        if (idoneal) { count++; last = n; if (n <= 100000) printf("%lld ", n); }
    }
    printf("\nidoneal numbers up to %lld: %lld; largest %lld\n", N, count, last);
    return 0;
}
