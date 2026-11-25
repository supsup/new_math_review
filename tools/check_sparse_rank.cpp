// Exhaustive determinant check for 3- through 6-square binary tables.
// Build with: c++ -O3 -std=c++20 tools/check_sparse_rank.cpp -o /tmp/check_sparse_rank
// Run with: /tmp/check_sparse_rank

#include <algorithm>
#include <array>
#include <bit>
#include <cstdint>
#include <cstdlib>
#include <iostream>
#include <limits>
#include <map>
#include <numeric>
#include <utility>
#include <vector>

using Mask = unsigned;
constexpr unsigned largestDimension = 6;

struct RowBlock {
    std::vector<Mask> rows;
    std::vector<int> minors;
    int ones = 0;
};

struct Finding {
    std::uint64_t count = 0;
    std::vector<Mask> example;
    int determinant = 0;
};

struct Sparsest {
    int ones = std::numeric_limits<int>::max();
    std::vector<std::vector<Mask>> tables;
};

std::uint64_t canonicalTable(const std::vector<Mask>& rows,
                             const std::vector<std::vector<Mask>>& columnMaps) {
    std::uint64_t best = std::numeric_limits<std::uint64_t>::max();
    for (const auto& map : columnMaps) {
        std::array<Mask, largestDimension> reordered{};
        for (unsigned row = 0; row < rows.size(); row++) reordered[row] = map[rows[row]];
        std::sort(reordered.begin(), reordered.begin() + rows.size());
        std::uint64_t key = 0;
        for (unsigned row = 0; row < rows.size(); row++) key = (key << rows.size()) | reordered[row];
        best = std::min(best, key);
    }
    return best;
}

std::vector<std::vector<Mask>> columnPermutations(unsigned dimension) {
    std::vector<unsigned> order(dimension);
    std::iota(order.begin(), order.end(), 0u);
    const Mask limit = 1u << dimension;
    std::vector<std::vector<Mask>> maps;
    do {
        std::vector<Mask> map(limit);
        for (Mask row = 1; row < limit; row++) {
            const Mask first = row & -row;
            map[row] = map[row ^ first] | (1u << order[std::countr_zero(first)]);
        }
        maps.push_back(std::move(map));
    } while (std::next_permutation(order.begin(), order.end()));
    return maps;
}

int determinant(const std::vector<Mask>& rows, unsigned row, Mask columns) {
    if (!columns) return 1;
    int total = 0;
    int sign = 1;
    for (Mask remaining = columns; remaining; remaining &= remaining - 1) {
        const Mask first = remaining & -remaining;
        if (first & rows[row]) {
            total += sign * determinant(rows, row + 1, columns ^ first);
        }
        sign = -sign;
    }
    return total;
}

void blocks(std::vector<RowBlock>& result, const std::vector<Mask>& columnSets,
            unsigned length, Mask limit, std::vector<Mask>& selected) {
    if (selected.size() == length) {
        RowBlock block;
        block.rows = selected;
        for (Mask row : selected) block.ones += std::popcount(row);
        for (Mask columns : columnSets) block.minors.push_back(determinant(selected, 0, columns));
        result.push_back(std::move(block));
        return;
    }
    const Mask start = selected.empty() ? 1 : selected.back() + 1;
    for (Mask row = start; row + length - selected.size() <= limit; row++) {
        selected.push_back(row);
        blocks(result, columnSets, length, limit, selected);
        selected.pop_back();
    }
}

void search(unsigned dimension) {
    const Mask limit = 1u << dimension;
    const Mask full = limit - 1;
    const unsigned firstRows = dimension / 2;
    std::vector<Mask> leftColumns;
    std::vector<Mask> rightColumns;
    std::vector<int> signs;
    for (Mask columns = 1; columns < limit; columns++) {
        if (std::popcount(columns) != static_cast<int>(firstRows)) continue;
        leftColumns.push_back(columns);
        rightColumns.push_back(full ^ columns);
        // Laplace expansion along the first rows, with zero-based indices.
        unsigned parity = firstRows * (firstRows - 1) / 2;
        for (Mask bits = columns; bits; bits &= bits - 1) parity += std::countr_zero(bits);
        signs.push_back(parity % 2 ? -1 : 1);
    }
    std::vector<RowBlock> left;
    std::vector<RowBlock> right;
    std::vector<Mask> selected;
    blocks(left, leftColumns, firstRows, limit, selected);
    blocks(right, rightColumns, dimension - firstRows, limit, selected);
    for (RowBlock& block : left) {
        for (unsigned index = 0; index < signs.size(); index++) block.minors[index] *= signs[index];
    }

    std::uint64_t checked = 0;
    int maximum = 0;
    std::map<std::pair<int, int>, Finding> findings;
    std::map<int, Sparsest> minima;
    for (const RowBlock& top : left) {
        const auto begin = std::upper_bound(right.begin(), right.end(), top.rows.back(),
            [](Mask last, const RowBlock& next) { return last < next.rows.front(); });
        for (auto bottom = begin; bottom != right.end(); ++bottom) {
            int value = 0;
            for (unsigned index = 0; index < signs.size(); index++) {
                value += top.minors[index] * bottom->minors[index];
            }
            checked++;
            maximum = std::max(maximum, std::abs(value));
            if (!value) continue;
            for (int prime : {2, 3, 5, 7}) {
                if (value % prime) continue;
                const int ones = top.ones + bottom->ones;
                Finding& match = findings[{prime, ones}];
                if (match.count++ == 0) {
                    match.determinant = value;
                    match.example = top.rows;
                    match.example.insert(match.example.end(), bottom->rows.begin(), bottom->rows.end());
                }
                Sparsest& minimum = minima[prime];
                if (ones <= minimum.ones) {
                    if (ones < minimum.ones) {
                        minimum.ones = ones;
                        minimum.tables.clear();
                    }
                    std::vector<Mask> rows = top.rows;
                    rows.insert(rows.end(), bottom->rows.begin(), bottom->rows.end());
                    minimum.tables.push_back(std::move(rows));
                }
            }
        }
    }

    std::uint64_t expected = 1;
    for (unsigned i = 0; i < dimension; i++) expected = expected * (full - i) / (i + 1);
    if (checked != expected) std::abort();
    std::cout << "dimension " << dimension << ", checked row sets " << checked
              << ", maximum absolute determinant " << maximum << '\n';
    for (const auto& [key, match] : findings) {
        // Recompute the witness by expanding the whole determinant from the top row.
        if (match.determinant != determinant(match.example, 0, full)) std::abort();
        std::cout << "  mod " << key.first << ", ones " << key.second << ", row sets "
                  << match.count << ", witness determinant " << match.determinant << ":";
        for (Mask row : match.example) {
            std::cout << ' ';
            for (unsigned column = 0; column < dimension; column++) std::cout << ((row >> column) & 1);
        }
        std::cout << '\n';
    }
    const auto columnMaps = columnPermutations(dimension);
    for (const auto& [prime, minimum] : minima) {
        std::map<std::uint64_t, unsigned> classes;
        for (const auto& table : minimum.tables) classes[canonicalTable(table, columnMaps)]++;
        std::cout << "  sparse mod " << prime << ": " << minimum.ones << " ones, "
                  << minimum.tables.size() << " row sets, " << classes.size()
                  << " classes after both row and column permutations\n";
        if (classes.size() <= 1) continue;
        for (const auto& [key, count] : classes) {
            std::cout << "    " << count << " row sets in class:";
            for (unsigned row = dimension; row > 0; row--) {
                const auto rowMask = (key >> ((row - 1) * dimension)) & full;
                std::cout << ' ';
                for (unsigned col = 0; col < dimension; col++) std::cout << ((rowMask >> col) & 1);
            }
            std::cout << '\n';
        }
    }
}

int main() {
    for (unsigned dimension = 3; dimension <= largestDimension; dimension++) search(dimension);
}
