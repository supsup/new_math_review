/* Confluence (data for crew_visuals/prime_gaps_rh.html): every maximal prime gap up to N by a segmented
   sieve of Eratosthenes over odd numbers, and, over ALL consecutive primes p > 3 (not only the records), the
   largest value of gap / (sqrt(p) log p), the quantity Carneiro-Milinovich-Soundararajan bound by 22/25 on RH.
   Prints JSON: the records [p, gap] and the overall maximum of the ratio with where it occurs.
   Build and run:  cc -O2 -o prime_gap_records tools/prime_gap_records.c -lm && ./prime_gap_records 10000000000 */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <math.h>
int main(int argc, char **argv) {
    unsigned long long N = strtoull(argv[1], 0, 10);
    unsigned long long root = (unsigned long long) sqrtl((long double) N) + 1;
    char *small = calloc(root + 1, 1); unsigned long long *bp = malloc(sizeof(unsigned long long) * (root / 2 + 10)); size_t nb = 0;
    for (unsigned long long i = 2; i <= root; i++) if (!small[i]) { if (i > 2) bp[nb++] = i; for (unsigned long long j = i * i; j <= root; j += i) small[j] = 1; }
    const unsigned long long SEG = 1ULL << 24;                 /* odd numbers per segment */
    unsigned char *seg = malloc(SEG);
    unsigned long long prev = 2, maxgap = 0, count = 1; double best = 0; unsigned long long best_p = 0, best_g = 0;
    printf("{\"N\": %llu, \"records\": [", N); int first = 1;
    for (unsigned long long lo = 3; lo <= N; lo += 2 * SEG) {            /* segment covers odd lo, lo+2, ..., lo+2(SEG-1) */
        unsigned long long hi = lo + 2 * (SEG - 1); if (hi > N) hi = N;
        memset(seg, 0, SEG);
        for (size_t k = 0; k < nb; k++) {
            unsigned long long p = bp[k]; if (p * p > hi) break;
            unsigned long long s = p * p; if (s < lo) { s = ((lo + p - 1) / p) * p; if (s % 2 == 0) s += p; }
            for (unsigned long long m = s; m <= hi; m += 2 * p) seg[(m - lo) / 2] = 1;
        }
        for (unsigned long long m = lo; m <= hi; m += 2) {
            if (seg[(m - lo) / 2]) continue;
            unsigned long long g = m - prev;
            if (g > maxgap) { maxgap = g; printf("%s[%llu, %llu]", first ? "" : ", ", prev, g); first = 0; }
            if (prev > 3) { double r = g / (sqrt((double) prev) * log((double) prev)); if (r > best) { best = r; best_p = prev; best_g = g; } }
            prev = m; count++;
        }
    }
    printf("], \"primes\": %llu, \"max_ratio\": [%llu, %llu, %.9f]}\n", count, best_p, best_g, best);
    return 0;
}
