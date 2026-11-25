#include <array>
#include <cstdlib>
#include <iostream>
#include <utility>

namespace {
constexpr int size = 6;
constexpr int first_support = 12;
constexpr int last_support = 16;
using Board = std::array<unsigned, size>;

constexpr std::array<int, 7> inverse7{0, 1, 4, 5, 2, 3, 6};
constexpr std::array<int, 11> inverse11{0, 1, 6, 4, 3, 9, 2, 8, 7, 5, 10};

template<int dimension, int modulus>
bool has_full_rank(const std::array<unsigned, dimension>& rows, const std::array<int, modulus>& inverses) {
    int cells[dimension][dimension];
    for (int i = 0; i < dimension; ++i)
        for (int j = 0; j < dimension; ++j)
            cells[i][j] = (rows[i] >> j) & 1u;

    for (int j = 0; j < dimension; ++j) {
        int pivot = j;
        while (pivot < dimension && cells[pivot][j] == 0) ++pivot;
        if (pivot == dimension) return false;
        for (int c = j; c < dimension; ++c) std::swap(cells[pivot][c], cells[j][c]);

        for (int i = j + 1; i < dimension; ++i) {
            if (cells[i][j] == 0) continue;
            const int factor = inverses[cells[j][j]] * cells[i][j] % modulus;
            for (int c = j; c < dimension; ++c)
                cells[i][c] = (cells[i][c] - factor * cells[j][c] + modulus * modulus) % modulus;
        }
    }
    return true;
}

template<int dimension>
bool loses_rank_mod7(const std::array<unsigned, dimension>& rows) {
    // For the boards in this search, |det| is below 77. A multiple of 7
    // is therefore nonzero over the integers exactly when nonzero mod 11.
    return !has_full_rank<dimension, 7>(rows, inverse7) && has_full_rank<dimension, 11>(rows, inverse11);
}

bool no_smaller_obstruction(std::array<unsigned, 5>& rows, int depth, unsigned first_row, long& checked) {
    if (depth == 5) {
        ++checked;
        // A 5 × 5 binary matrix satisfies |det| ≤ 5^(5/2) < 77 by Hadamard.
        return !loses_rank_mod7<5>(rows);
    }
    for (unsigned row = first_row; row < 32; ++row) {
        rows[depth] = row;
        if (!no_smaller_obstruction(rows, depth + 1, row + 1, checked)) return false;
    }
    return true;
}

struct Counts {
    std::array<long, last_support + 1> checked{};
    std::array<long, last_support + 1> drops{};
};

void enumerate(Board& rows, Counts& counts, int depth, unsigned first_row, int support) {
    if (depth == size) {
        for (int col = 0; col < size; ++col) {
            int column_support = 0;
            for (const unsigned row : rows) column_support += (row >> col) & 1u;
            if (column_support < 2) return;
        }
        ++counts.checked[support];

        // Hadamard and AM–GM give |det| ≤ (16/6)^3 < 77 here.
        if (loses_rank_mod7<size>(rows)) ++counts.drops[support];
        return;
    }

    for (unsigned row = first_row; row < (1u << size); ++row) {
        const int row_support = __builtin_popcount(row);
        if (row_support < 2) continue;
        if (support + row_support + 2 * (size - depth - 1) > last_support) continue;
        rows[depth] = row;
        enumerate(rows, counts, depth + 1, row + 1, support + row_support);
    }
}
} // namespace

int main() {
    std::array<unsigned, 5> smaller{};
    long smaller_checked = 0;
    if (!no_smaller_obstruction(smaller, 0, 1, smaller_checked) || smaller_checked != 169911)
        return EXIT_FAILURE;
    std::cout << smaller_checked << " five-row boards: no nonzero determinant divisible by 7\n";

    Board rows{};
    Counts counts;
    enumerate(rows, counts, 0, 1, 0);

    constexpr std::array<long, 5> expected_boards{70, 2760, 31320, 176406, 615486};
    for (int support = first_support; support <= last_support; ++support) {
        std::cout << support << " ones: " << counts.checked[support]
                  << " boards, " << counts.drops[support] << " rank drops\n";
        if (counts.checked[support] != expected_boards[support - first_support] ||
            counts.drops[support] != (support == last_support ? 720 : 0)) {
            return EXIT_FAILURE;
        }
    }
    return EXIT_SUCCESS;
}
