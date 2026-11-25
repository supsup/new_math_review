// Exact determinant searches for the seven-row spectrum and sparse larger boards.
// The column-prefix argument is in crew_visuals/seven_row_spectrum.txt.
#include <array>
#include <cstdlib>
#include <iostream>
#include <stdexcept>
#include <string_view>
#include <vector>

namespace {
constexpr unsigned max_dimension = 9;
constexpr unsigned mask_count = 1 << max_dimension;
constexpr unsigned max_determinant = 195;  // Bordered Hadamard bound through size nine.
using Masks = std::vector<unsigned>;
using ByMask = std::array<int, mask_count>;
using Board = std::array<unsigned, max_dimension>;

struct Search {
    unsigned dimension;
    int support_cap;
    unsigned min_degree;
    bool sorted_only;
    bool show_mod17;
    bool mixed_primes = false;

    unsigned all_columns() const { return (1u << dimension) - 1; }
};

ByMask weight;
std::array<Masks, max_dimension + 1> subsets;
std::array<unsigned long long, max_dimension + 1> visits{};
Board board{};
std::array<int, max_determinant + 1> fewest_ones{};
std::array<Board, max_determinant + 1> witnesses{};
unsigned mod17_hits = 0;

unsigned least_positions(unsigned group, int count) {
    unsigned result = 0;
    for (int i = 0; i < count; ++i) {
        const unsigned position = group & -group;
        result |= position;
        group ^= position;
    }
    return result;
}

ByMask append_row(const ByMask &minors, unsigned row, unsigned size) {
    ByMask result{};
    for (unsigned columns : subsets[size]) {
        // Expand these minors along the new row, starting at the last column.
        int sign = 1;
        for (unsigned remaining = columns; remaining; sign = -sign) {
            const unsigned last = remaining & -remaining;
            if (row & last) result[columns] += sign * minors[columns ^ last];
            remaining ^= last;
        }
    }
    return result;
}

void enumerate(unsigned depth, int support, const Masks &groups,
               const Masks &eligible, const ByMask &minors, const Search &search,
               unsigned once = 0, unsigned twice = 0) {
    ++visits[depth];
    std::array<unsigned, mask_count> normalized{};
    for (unsigned row : eligible) {
        for (unsigned group : groups) normalized[row] |= least_positions(group, weight[group & row]);
    }

    for (unsigned row : eligible) {
        // Put the zeros first within columns having an identical prefix.
        if (row != normalized[row]) continue;
        board[depth] = row;
        const int total = support + weight[row];
        const unsigned remaining = search.dimension - depth - 1;
        if (total + static_cast<int>(search.min_degree * remaining) > search.support_cap) continue;
        unsigned next_once = once;
        unsigned next_twice = twice;
        if (search.mixed_primes) {
            // Every column needs two entries by the end. Each missing entry consumes one mark,
            // and a column can gain only one mark in each remaining row.
            next_twice |= once & row;
            next_once |= row;
            const int empty = search.dimension - __builtin_popcount(next_once);
            const int deficit = 2 * empty + __builtin_popcount(next_once & ~next_twice);
            if (total + deficit > search.support_cap || (remaining < 2 && empty) || (!remaining && deficit)) {
                continue;
            }
        } else if (!remaining && search.min_degree > 1) {
            bool low_degree = false;
            for (unsigned col = 0; col < search.dimension; ++col) {
                unsigned degree = 0;
                for (unsigned i = 0; i < search.dimension; ++i) degree += (board[i] >> col) & 1;
                low_degree |= degree < search.min_degree;
            }
            if (low_degree) continue;
        }
        const ByMask next_minors = append_row(minors, row, depth + 1);
        bool independent = false;
        for (unsigned columns : subsets[depth + 1]) independent |= next_minors[columns] != 0;
        if (!independent) continue;

        if (!remaining) {
            ++visits[search.dimension];
            const auto value = static_cast<unsigned>(std::abs(next_minors[search.all_columns()]));
            if (value > max_determinant) throw std::logic_error("Hadamard bound exceeded");
            if (value % 17 == 0) ++mod17_hits;
            const int mod17_minimum = search.dimension == 7 ? 24 : 23;
            if (search.show_mod17 && value == 17 && total == mod17_minimum) {
                std::cout << "mod17:";
                for (unsigned i = 0; i < search.dimension; ++i) std::cout << ' ' << board[i];
                std::cout << '\n';
            }
            if (!fewest_ones[value] || total < fewest_ones[value]) {
                fewest_ones[value] = total;
                witnesses[value] = board;
            }
            continue;
        }

        Masks next_groups;
        for (unsigned group : groups) {
            if (group & ~row) next_groups.push_back(group & ~row);
            if (group & row) next_groups.push_back(group & row);
        }

        Masks next_eligible;
        for (unsigned other : eligible) {
            // A smaller normalized row would have been chosen in this position.
            const unsigned comparison = search.sorted_only ? other : normalized[other];
            if (other != row && comparison >= row) next_eligible.push_back(other);
        }
        enumerate(depth + 1, total, next_groups, next_eligible, next_minors, search, next_once, next_twice);
    }
}
}  // namespace

int main(int argc, char **argv) {
    const bool sorted_only = argc == 2 && std::string_view(argv[1]) == "--sorted-only";
    const bool show_mod17 = argc == 2 && std::string_view(argv[1]) == "--mod17-boards";
    const bool eight_row_boards = argc == 2 && std::string_view(argv[1]) == "--eight-row-mod17-boards";
    const bool eight_row = eight_row_boards || (argc == 2 && std::string_view(argv[1]) == "--eight-row-mod17");
    const bool eight_mixed = argc == 2 && std::string_view(argv[1]) == "--eight-row-mod30";
    const bool nine_mixed = argc == 2 && std::string_view(argv[1]) == "--nine-row-mod30";
    if (argc != 1 && !sorted_only && !show_mod17 && !eight_row && !eight_mixed && !nine_mixed) {
        std::cerr << "Usage: check_seven_row_spectrum [--sorted-only | --mod17-boards | --eight-row-mod17"
                     " | --eight-row-mod17-boards | --eight-row-mod30 | --nine-row-mod30]\n";
        return EXIT_FAILURE;
    }
    Search search{7, 49, 1, sorted_only, show_mod17};
    if (eight_row) search = Search{8, 23, 2, false, eight_row_boards};
    if (eight_mixed) search = Search{8, 26, 2, false, false, true};
    if (nine_mixed) search = Search{9, 25, 2, false, false, true};
    Masks rows;
    for (unsigned mask = 0; mask <= search.all_columns(); ++mask) {
        const int count = __builtin_popcount(mask);
        weight[mask] = count;
        subsets[static_cast<unsigned>(count)].push_back(mask);
        if (count >= static_cast<int>(search.min_degree)) rows.push_back(mask);
    }
    ByMask empty_minor{};
    empty_minor[0] = 1;
    enumerate(0, 0, {search.all_columns()}, rows, empty_minor, search);

    std::cout << "Visited independent prefixes by size:";
    for (unsigned i = 0; i <= search.dimension; ++i) std::cout << ' ' << visits[i];
    if (search.mixed_primes) {
        std::cout << '\n' << search.dimension << " rows, support at most " << search.support_cap
                  << ", all row and column weights at least 2.\n";
        bool passed = visits[search.dimension] == (eight_mixed ? 301'717'646 : 390'738'028)
                      && fewest_ones[30] == (eight_mixed ? 26 : 0);
        for (unsigned value = 30; value <= max_determinant; value += 30) {
            if (!fewest_ones[value]) continue;
            std::cout << "Absolute determinant " << value << " first at " << fewest_ones[value] << " ones.\n";
            passed &= eight_mixed && fewest_ones[value] == 26;
        }
        return passed ? EXIT_SUCCESS : EXIT_FAILURE;
    }
    if (eight_row) {
        std::cout << "\nEight rows, support at most 23, all row and column weights at least 2.\n";
        std::cout << mod17_hits << " nonzero determinants divisible by 17; minimum support " << fewest_ones[17] << ".\n";
        std::cout << "Minimum support for determinant 19: " << fewest_ones[19] << ".\n";
        bool passed = fewest_ones[17] == 23 && fewest_ones[19] == 23 && mod17_hits == 40 && visits[8] == 22'027'239;
        for (unsigned prime : {17u, 19u}) {
            for (unsigned multiple = 2 * prime; multiple <= max_determinant; multiple += prime) {
                passed &= fewest_ones[multiple] == 0;
            }
        }
        return passed ? EXIT_SUCCESS : EXIT_FAILURE;
    }
    std::cout << "\n|det|  ones  witness rows\n";
    for (unsigned value = 1; value <= max_determinant; ++value) {
        if (!fewest_ones[value]) continue;
        std::cout << value << ' ' << fewest_ones[value];
        for (unsigned i = 0; i < search.dimension; ++i) {
            std::cout << ' ';
            for (unsigned col = search.dimension; col > 0; --col) {
                std::cout << ((witnesses[value][i] >> (col - 1)) & 1);
            }
        }
        std::cout << '\n';
    }

    const std::array<int, max_determinant + 1> expected = {
        0, 7, 10, 12, 13, 15, 15, 17, 17, 18, 19, 20, 19, 21, 21, 22, 20,
        24, 23, 0, 22, 0, 0, 0, 21, 0, 0, 0, 0, 0, 0, 0, 28,
    };
    const unsigned long long expected_visits = sorted_only ? 373'908'469 : 28'967'978;
    if (fewest_ones != expected || visits[search.dimension] != expected_visits) {
        std::cerr << "The supports or number of boards differ from the recorded run.\n";
        return EXIT_FAILURE;
    }
}
