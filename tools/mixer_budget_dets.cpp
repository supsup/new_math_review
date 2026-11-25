// tools/mixer_budget_dets.cpp: an independent check of the LOWER bounds in crew_visuals/mixer_prime_frontier.txt.
// Build and run:  c++ -O3 -std=c++17 tools/mixer_budget_dets.cpp -o /tmp/mixer_budget_dets && /tmp/mixer_budget_dets 5
// It rests on the note's forest reduction (two-mark rows as edges; |det| of the board = |det| of the reduced matrix).
// It covers a SUPERSET of the reduced systems in that note: every h x h integer matrix whose rows have l1 norm at
// most w_i, with every w_i >= 3 and sum(w_i - 2) <= e. No forest or realizability condition is imposed, so any
// prime that does NOT divide an achievable determinant here cannot appear in a board with that excess.
// Expected output (Lean-free, about 90 s for e = 5 on an 18-core laptop, one core used):
//   e <= 4: primes dividing some achievable |det|: 2 3 5 7 11 13 17
//   e <= 5: 699591050 matrices; primes dividing some achievable |det|: 2 3 5 7 11 13 17 19 23 31
//   (29 is absent although 28 and 30 occur; no multiple of 37, 41 or 47 occurs; the largest |det| is 243)
// Written by Confluence on 2026-11-25 for the review of Lattice's note (room seq 34824).
#include <cstdio>
#include <cstdlib>
#include <cstdint>
#include <vector>
#include <set>
#include <algorithm>
#include <functional>
typedef long long ll;
static void gen(int h, int r, int i, std::vector<int>& v, std::vector<std::vector<int>>& out) {
    if (i == h) { out.push_back(v); return; }
    for (int x = -r; x <= r; ++x) { v[i] = x; gen(h, r - std::abs(x), i + 1, v, out); }
    v[i] = 0;
}
static ll det(std::vector<std::vector<ll>> a) {                      // exact, Bareiss
    int n = a.size(); ll sign = 1, prev = 1;
    for (int k = 0; k < n; ++k) {
        int p = k; while (p < n && a[p][k] == 0) ++p;
        if (p == n) return 0;
        if (p != k) { std::swap(a[p], a[k]); sign = -sign; }
        for (int i = k + 1; i < n; ++i) {
            for (int j = k + 1; j < n; ++j) a[i][j] = (a[i][j] * a[k][k] - a[i][k] * a[k][j]) / prev;
            a[i][k] = 0;
        }
        prev = a[k][k];
    }
    return sign * a[n - 1][n - 1];
}
int main(int argc, char** argv) {
    if (argc != 2) { std::fprintf(stderr, "usage: budget_dets E\n"); return 2; }
    int E = std::atoi(argv[1]);
    if (E < 1 || E > 5) { std::fprintf(stderr, "E must be 1 to 5: the run time and the 64-bit Bareiss bound are only argued for e <= 5\n"); return 2; }
    std::set<ll> dets;
    ll count = 0;
    for (int h = 1; h <= E; ++h) {
        // budget vectors: w_1 >= w_2 >= ... >= w_h >= 3 with sum(w - 2) <= E; the first (largest) row is canonical
        std::vector<std::vector<int>> wlist;
        std::vector<int> cur;
        std::function<void(int, int)> rec = [&](int i, int left) {
            if (i == h) { wlist.push_back(cur); return; }
            int hi = (i == 0) ? 3 + left : std::min(cur[i - 1], 3 + left);
            for (int x = 3; x <= hi; ++x) { cur.push_back(x); rec(i + 1, left - (x - 3)); cur.pop_back(); }
        };
        rec(0, E - h);                                               // sum(w - 2) <= E  <=>  sum(w - 3) <= E - h
        for (auto& wv : wlist) {
            // canonical first rows: non-negative, non-increasing, l1 <= wv[0]
            std::vector<std::vector<int>> firsts, raw; std::vector<int> v(h, 0);
            gen(h, wv[0], 0, v, raw);
            for (auto& r : raw) {
                bool ok = true; int s = 0;
                for (int j = 0; j < h; ++j) { if (r[j] < 0) ok = false; if (j && r[j] > r[j - 1]) ok = false; s += r[j]; }
                if (ok && s > 0) firsts.push_back(r);
            }
            std::vector<std::vector<std::vector<int>>> pools(h);
            for (int i = 1; i < h; ++i) { std::vector<int> t(h, 0); gen(h, wv[i], 0, t, pools[i]); }
            std::vector<int> idx(h, 0);
            std::vector<std::vector<ll>> m(h, std::vector<ll>(h));
            std::function<void(int)> pick = [&](int i) {
                if (i == h) {
                    ++count;
                    ll d = det(m); if (d < 0) d = -d;
                    if (d) dets.insert(d);
                    return;
                }
                int start = (i >= 2 && wv[i] == wv[i - 1]) ? idx[i - 1] + 1 : 0;   // equal budgets: strict multiset order
                for (int k = start; k < (int)pools[i].size(); ++k) {
                    idx[i] = k;
                    for (int j = 0; j < h; ++j) m[i][j] = pools[i][k][j];
                    pick(i + 1);
                }
            };
            for (auto& f : firsts) {
                for (int j = 0; j < h; ++j) m[0][j] = f[j];
                pick(1);
            }
        }
    }
    std::printf("e <= %d: %lld matrices, achievable nonzero |det|:", E, count);
    for (ll d : dets) std::printf(" %lld", d);
    std::printf("\nprimes dividing some achievable |det|:");
    std::set<ll> primes;
    for (ll d : dets) { ll x = d; for (ll q = 2; q * q <= x; ++q) while (x % q == 0) { primes.insert(q); x /= q; } if (x > 1) primes.insert(x); }
    for (ll q : primes) std::printf(" %lld", q);
    std::printf("\n");
    return 0;
}
