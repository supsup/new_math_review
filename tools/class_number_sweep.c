/* Confluence (data for crew_visuals/class_numbers_band.html). h(-d) for every d <= D in one sweep over reduced
   forms (a, b, c): b^2 - 4ac = -d, |b| <= a <= c, b >= 0 when |b| = a or a = c. At a FUNDAMENTAL discriminant -d
   every form is primitive, so the tally is the class number there. L(1, chi_-d) = 2 pi h / (w sqrt d), with
   w = 6, 4, 2 for d = 3, 4, > 4 (the class number formula). Prints JSON: log-spaced bins with their smallest and
   largest L (and where), and the running records of new largest and new smallest L.
   Build and run:  cc -O2 -o class_number_sweep tools/class_number_sweep.c -lm && ./class_number_sweep 4000000 */
#include <stdio.h>
#include <stdlib.h>
#include <math.h>
static int squarefree(long m) { for (long p = 2; p * p <= m; p++) if (m % (p * p) == 0) return 0; return 1; }
static int fundamental(long d) {
    if (d % 4 == 3) return squarefree(d);
    if (d % 4 == 0) { long m = d / 4; return (m % 4 == 1 || m % 4 == 2) && squarefree(m); }
    return 0;
}
int main(int argc, char **argv) {
    long D = atol(argv[1]); int NB = 96;
    int *h = calloc(D + 1, sizeof(int));
    for (long a = 1; 3 * a * a <= D; a++)
        for (long b = -a + 1; b <= a; b++)
            for (long c = a; ; c++) {
                long d = 4 * a * c - b * b; if (d > D) break;
                if (b < 0 && a == c) continue;
                h[d]++;
            }
    double *lo = malloc(NB * sizeof(double)), *hi = malloc(NB * sizeof(double));
    long *dlo = calloc(NB, sizeof(long)), *dhi = calloc(NB, sizeof(long)), *cnt = calloc(NB, sizeof(long));
    for (int i = 0; i < NB; i++) { lo[i] = 1e9; hi[i] = -1; }
    double best = -1, worst = 1e9, L1 = log(3.0), L2 = log((double) D); long nf = 0;
    printf("{\"D\": %ld, \"records\": [", D);
    int firstrec = 1;
    for (long d = 3; d <= D; d++) {
        if (!fundamental(d)) continue;
        nf++;
        double w = d == 3 ? 6 : d == 4 ? 4 : 2, L = 2 * M_PI * h[d] / (w * sqrt((double) d));
        int k = (int) floor(NB * (log((double) d) - L1) / (L2 - L1 + 1e-12)); if (k >= NB) k = NB - 1;
        cnt[k]++;
        if (L < lo[k]) { lo[k] = L; dlo[k] = d; }
        if (L > hi[k]) { hi[k] = L; dhi[k] = d; }
        if (L > best) { best = L; printf("%s[\"max\", %ld, %d]", firstrec ? "" : ", ", d, h[d]); firstrec = 0; }
        if (L < worst) { worst = L; printf("%s[\"min\", %ld, %d]", firstrec ? "" : ", ", d, h[d]); firstrec = 0; }
    }
    printf("], \"fundamental\": %ld, \"bins\": [", nf);
    int first = 1;
    for (int i = 0; i < NB; i++) if (cnt[i]) {
        printf("%s[%ld, %d, %ld, %d, %ld]", first ? "" : ", ", dlo[i], h[dlo[i]], dhi[i], h[dhi[i]], cnt[i]); first = 0;
    }
    long ones[16]; int no = 0; for (long d = 3; d <= D && no < 16; d++) if (fundamental(d) && h[d] == 1) ones[no++] = d;
    printf("], \"class_number_one\": [");
    for (int i = 0; i < no; i++) printf("%s%ld", i ? ", " : "", ones[i]);
    printf("]}\n");
    return 0;
}
