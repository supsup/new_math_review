// A second, independent replay for the rank-drop notes: plain brute force, no reduction.
//
//   c++ -O3 -std=c++17 tools/check_rank_drop_brute.cpp -o check_rank_drop_brute
//   ./check_rank_drop_brute                 the five-row and six-row checks (a few seconds)
//   ./check_rank_drop_brute 7 2 21          every seven-row board up to 21 ones (several minutes)
//   ./check_rank_drop_brute N MINW W        another search: N rows (1 to 7), at least MINW ones per row (1 to N),
//                                           at most W ones in the board (0 to N*N)
//
// The notes crew_visuals/mod7_rank_card.txt, mod11_rank_card.txt and mod13_rank_card.txt prove their "fewest ones"
// claims by reducing a board to a small system of signed equations, and their replays in tools/ check that reduction.
// This file shares nothing with them. It walks through every choice of N DISTINCT rows of an N-column board of zeros
// and ones (row order does not matter, so each board is visited once), and takes the determinant of each.
//
// Determinant, exactly: elimination modulo the prime Q = 65521, done row by row as the board is built. This is exact
// for the following reason. A square 0/1 matrix of size k has absolute determinant at most (k+1)^((k+1)/2) / 2^k
// (Hadamard's bound for the matching +1/-1 matrix of size k+1), which is at most 32 for k up to 7. So:
//   - a determinant is recovered from its residue modulo Q, because 2 * 32 < Q;
//   - rows that are independent over the fractions stay independent modulo Q, because some square block of them
//     has a nonzero determinant of absolute value at most 32, which Q cannot divide.
// The program stops with an error if a recovered determinant exceeds the bound for its size.
//
// Why "at least two ones per row" is enough for seven rows: a row with a single 1 reduces the determinant to one of
// size six, and the six-row run here finds that those never exceed 9. So a seven-row determinant of 10 or more has at
// least two ones in every row. Below 10 the seven-row table of this program is NOT the full story.
//
// What the built-in runs must find, or the program exits with an error:
//   five rows, all 169,911 boards: largest determinant 5
//   six rows, all 67,945,521 boards: largest determinant 9; boards with AT LEAST two ones in every row and every
//     column at 12, 13, 14, 15, 16 ones: 70, 2,760, 31,320, 176,406, 615,486; determinant 7 first at 16 ones, on 720
//   seven rows up to 21 ones (4,614,501,284 boards): determinant 11 first at 20 ones on 37,800 boards; determinant 13
//     first at 21 ones on 21,420 boards; no 22 or 26; determinant 24 at 21 ones on 30 boards (the Fano planes)
//
// Author: Fixpoint, for Marginalia, 24 November 2026. Reviewed by Lattice (strict arguments, exact arithmetic).
#include <cerrno>
#include <cmath>
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <vector>

static const unsigned Q = 65521;       // prime; (Q-1)^2 + (Q-1) < 2^32, so the arithmetic below fits in 32 bits
static std::vector<unsigned> inv;      // inverses modulo Q

static int n, MINW, W, bound;
static std::vector<int> rows;          // row bitmasks, each with at least MINW ones
static unsigned red[8][8];             // reduced rows of the rows chosen so far, modulo Q
static int pivcol[8];
static unsigned pivinv[8];
static int chosen[8];
static long long boards[64], hist[64][40], filt[64], singular, maxdet;
static bool outOfRange;

static void record(int weight, unsigned detmod, bool dependent) {
  int d = dependent ? 0 : (int)(detmod <= Q / 2 ? detmod : Q - detmod);       // the absolute determinant
  if (d > bound) { outOfRange = true; return; }
  boards[weight]++;
  if (d == 0) singular++;
  if (d > maxdet) maxdet = d;
  hist[weight][d]++;
  int once = 0, twice = 0; bool rows2 = true;
  for (int i = 0; i < n; i++) { twice |= once & chosen[i]; once |= chosen[i]; if (__builtin_popcount(chosen[i]) < 2) rows2 = false; }
  if (rows2 && twice == (1 << n) - 1) filt[weight]++;        // at least two ones in every row and every column
}

// dependent: the rows chosen so far are already linearly dependent, so every completion has determinant 0
static void dfs(int depth, int start, int weight, unsigned det, bool dependent) {
  int left = n - depth;
  for (int idx = start; idx + left <= (int)rows.size(); idx++) {
    int r = rows[idx], w = weight + __builtin_popcount(r);
    if (w + MINW * (left - 1) > W) continue;
    chosen[depth] = r;
    bool dep = dependent; unsigned d = det;
    if (!dep) {
      unsigned v[8];
      for (int c = 0; c < n; c++) v[c] = (r >> c) & 1;
      for (int k = 0; k < depth; k++) {
        unsigned f = v[pivcol[k]];
        if (f) { unsigned neg = Q - (unsigned)((unsigned long long)f * pivinv[k] % Q); for (int c = 0; c < n; c++) v[c] = (v[c] + neg * red[k][c]) % Q; }
      }
      int pc = -1;
      for (int c = 0; c < n; c++) if (v[c]) { pc = c; break; }
      if (pc < 0) { dep = true; d = 0; }
      else { for (int c = 0; c < n; c++) red[depth][c] = v[c]; pivcol[depth] = pc; pivinv[depth] = inv[v[pc]]; d = (unsigned)((unsigned long long)det * v[pc] % Q); }
    }
    if (depth + 1 == n) record(w, d, dep); else dfs(depth + 1, idx + 1, w, d, dep);
  }
}

static long long total;
static void run(int N, int minw, int cap) {
  n = N; MINW = minw; W = cap; rows.clear();
  bound = (int)std::floor(std::pow((double)(n + 1), (n + 1) / 2.0) / std::pow(2.0, n) + 1e-9);
  std::memset(boards, 0, sizeof boards); std::memset(hist, 0, sizeof hist); std::memset(filt, 0, sizeof filt);
  singular = 0; maxdet = 0; total = 0; outOfRange = false;
  for (int r = 1; r < (1 << n); r++) if (__builtin_popcount(r) >= MINW) rows.push_back(r);
  dfs(0, 0, 0, 1, false);
  for (int w = 0; w < 64; w++) total += boards[w];
  std::printf("%d rows, at least %d ones per row, at most %d ones: %lld boards (%lld singular), largest determinant %lld (bound for this size: %d)\n", n, MINW, W, total, singular, maxdet, bound);
  for (int w = 0; w < 64; w++) if (boards[w]) {
    std::printf("  ones=%2d boards=%lld at-least-two-in-every-row-and-column=%lld  determinants:", w, boards[w], filt[w]);
    for (int d = 0; d < 40; d++) if (hist[w][d]) std::printf(" %d:%lld", d, hist[w][d]);
    std::printf("\n");
  }
}
static int firstAt(int d) { for (int w = 0; w < 64; w++) if (hist[w][d]) return w; return -1; }

static int failures = 0;
static void expect(bool ok, const char* what) { if (!ok) { failures++; std::printf("FAILED: %s\n", what); } }

// a whole number in [lo, hi], with nothing after it; anything else is refused
static bool whole(const char* s, int lo, int hi, int* out) {
  if (!s || !*s) return false;
  char* end = nullptr; errno = 0;
  long v = std::strtol(s, &end, 10);
  if (errno || *end || v < lo || v > hi) return false;
  *out = (int)v; return true;
}

int main(int argc, char** argv) {
  inv.assign(Q, 0); inv[1] = 1;
  for (unsigned i = 2; i < Q; i++) inv[i] = (unsigned)((unsigned long long)(Q - Q / i) * inv[Q % i] % Q);
  if (argc == 1) {
    run(5, 1, 25);
    expect(!outOfRange, "a determinant beyond the bound: the arithmetic is wrong"); expect(total == 169911, "five rows: 169,911 boards"); expect(maxdet == 5, "five rows: largest determinant 5");
    run(6, 1, 36);
    expect(!outOfRange, "a determinant beyond the bound: the arithmetic is wrong"); expect(total == 67945521, "six rows: 67,945,521 boards"); expect(maxdet == 9, "six rows: largest determinant 9");
    expect(filt[12] == 70 && filt[13] == 2760 && filt[14] == 31320 && filt[15] == 176406 && filt[16] == 615486, "six rows: boards with at least two ones in every row and column");
    expect(firstAt(7) == 16 && hist[16][7] == 720, "six rows: determinant 7 first at 16 ones, on 720 boards");
  } else if (argc == 4) {
    int N, minw, cap;
    if (!whole(argv[1], 1, 7, &N) || !whole(argv[2], 1, N, &minw) || !whole(argv[3], 0, N * N, &cap)) {
      std::fprintf(stderr, "refused: N must be 1 to 7, MINW 1 to N, W 0 to N*N, each a plain whole number\n"); return 2;
    }
    run(N, minw, cap);
    expect(!outOfRange, "a determinant beyond the bound: the arithmetic is wrong");
    if (n == 7 && MINW == 2 && W >= 21) {
      expect(firstAt(11) == 20 && hist[20][11] == 37800, "seven rows: determinant 11 first at 20 ones, on 37,800 boards");
      expect(firstAt(13) == 21 && hist[21][13] == 21420, "seven rows: determinant 13 first at 21 ones, on 21,420 boards");
      expect(firstAt(24) == 21 && hist[21][24] == 30, "seven rows: determinant 24 at 21 ones, on 30 boards");
      bool none = true; for (int w = 0; w <= 21; w++) if (hist[w][22] || hist[w][26]) none = false;
      expect(none, "seven rows: no determinant 22 or 26 up to 21 ones");
    }
  } else { std::fprintf(stderr, "usage: check_rank_drop_brute [N MINW W]\n"); return 2; }
  std::printf(failures ? "A CHECK FAILED\n" : "ALL CHECKS PASS\n");
  return failures ? 1 : 0;
}
