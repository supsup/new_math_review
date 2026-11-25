/* Confluence (data for crew_visuals/robin_and_nicolas.html).
   (a) sigma(n) for every n <= N1 by a divisor sieve: every n >= 3 with sigma(n) >= e^gamma n log log n (Robin's
       exceptions), the largest sigma(n)/(n log log n) over 5040 < n <= N1, and the largest
       sigma(n)/(H_n + exp(H_n) log H_n) over 2 <= n <= N1 (Lagarias's criterion), with where each occurs.
   (b) Every primorial N_k with p_k <= N2, by a segmented sieve: S = log(N_k/phi(N_k)) = sum -log(1 - 1/p) and
       theta = log N_k = sum log p, both with compensated (Kahan) summation; reports [k, p_k,
       N_k/(phi(N_k) log log N_k), c(N_k), log N_k] at log-spaced k, where Nicolas's c(N_k) = (N_k/phi(N_k) - e^gamma log log N_k) sqrt(log N_k), and its smallest and largest values over all k, its value at k = 66, and its largest value for k >= 120569.
   Build and run:  cc -O2 -o robin_nicolas tools/robin_nicolas.c -lm && ./robin_nicolas 10000000 100000000 */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <math.h>
static const double EG = 1.7810724179901979852;           /* e^gamma */
int main(int argc, char **argv) {
    long N1 = atol(argv[1]); long long N2 = atoll(argv[2]);
    unsigned long long *sg = calloc(N1 + 1, sizeof(unsigned long long));
    for (long d = 1; d <= N1; d++) for (long m = d; m <= N1; m += d) sg[m] += d;
    printf("{\"N1\": %ld, \"exceptions\": [", N1); int first = 1; double best = 0; long best_n = 0; double H = 1.0, cH = 0, lag = 0; long lag_n = 0;
    for (long n = 3; n <= N1; n++) {
        double r = (double) sg[n] / ((double) n * log(log((double) n)));
        if (r >= EG) { printf("%s%ld", first ? "" : ", ", n); first = 0; }
        if (n > 5040 && r > best) { best = r; best_n = n; }
    }
    for (long n = 2; n <= N1; n++) { double y = 1.0 / (double) n - cH, t = H + y; cH = (t - H) - y; H = t;
        double q = (double) sg[n] / (H + exp(H) * log(H)); if (q > lag) { lag = q; lag_n = n; } }
    printf("], \"robin_max_after_5040\": [%ld, %llu, %.12f], \"lagarias_max\": [%ld, %llu, %.12f], ", best_n, sg[best_n], best, lag_n, sg[lag_n], lag);
    free(sg);
    /* primorials */
    long long root = (long long) sqrt((double) N2) + 1; char *sm = calloc(root + 1, 1); long long *bp = malloc(sizeof(long long) * root); long nb = 0;
    for (long long i = 2; i <= root; i++) if (!sm[i]) { if (i > 2) bp[nb++] = i; for (long long j = i * i; j <= root; j += i) sm[j] = 1; }
    const long long SEG = 1LL << 24; unsigned char *seg = malloc(SEG);
    double S = 0, cS = 0, T = 0, cT = 0; long long k = 0; double next = 1; double cmin = 1e9; long long cmin_k = 0, cmin_p = 0; double cmax = -1e9; long long cmax_k = 0, cmax_p = 0; double tailmax = -1e9; long long tail_k = 0; double c66 = 0, c120568 = 0;
    printf("\"primorials\": ["); first = 1;
    #define ADD(sum, comp, x) do { double y_ = (x) - comp; double t_ = sum + y_; comp = (t_ - sum) - y_; sum = t_; } while (0)
    for (long long lo = 1; lo <= N2; lo += 2 * SEG) {             /* odd numbers lo, lo+2, ... (lo odd) */
        long long hi = lo + 2 * (SEG - 1); if (hi > N2) hi = N2;
        memset(seg, 0, SEG);
        for (long q = 0; q < nb; q++) { long long p = bp[q]; if (p * p > hi) break; long long s = p * p; if (s < lo) { s = ((lo + p - 1) / p) * p; if (s % 2 == 0) s += p; } for (long long m = s; m <= hi; m += 2 * p) seg[(m - lo) / 2] = 1; }
        for (long long m = lo; m <= hi; m += 2) {
            long long p = m;
            if (lo == 1 && m == 1) { p = 2; }                       /* insert 2 before 3 */
            else if (seg[(m - lo) / 2]) continue;
            ADD(S, cS, -log1p(-1.0 / (double) p)); ADD(T, cT, log((double) p)); k++;
            double ratio = exp(S), c = (ratio - EG * log(T)) * sqrt(T);
            if (c < cmin) { cmin = c; cmin_k = k; cmin_p = p; }
            if (c > cmax) { cmax = c; cmax_k = k; cmax_p = p; }
            if (k == 66) c66 = c;
            if (k == 120568) c120568 = c;
            if (k >= 120569 && c > tailmax) { tailmax = c; tail_k = k; }
            if ((double) k >= next || p == 3) { printf("%s[%lld, %lld, %.10f, %.10f, %.6f]", first ? "" : ", ", k, p, ratio / log(T), c, T); first = 0; next *= 1.25; }
        }
    }
    printf("], \"primorial_count\": %lld, \"nicolas_cmin\": [%lld, %lld, %.10f], \"nicolas_cmax\": [%lld, %lld, %.10f], \"c66\": %.10f, \"c120568\": %.10f, \"tail_max_from_120569\": [%lld, %.10f]}\n", k, cmin_k, cmin_p, cmin, cmax_k, cmax_p, cmax, c66, c120568, tail_k, tailmax);
    return 0;
}
