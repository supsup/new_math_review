// Filter eight-tap circulants using the factor tables sent by
// check_eight_tap_minimum.py. Emit candidate length, prime, and tap offsets.
#include <array>
#include <bit>
#include <cstdint>
#include <iostream>
#include <vector>

namespace {
using Mask = std::uint64_t;
using Taps = std::array<int, 8>;

struct Factor {
    int degree;
    std::array<std::array<int, 50>, 7> powers;
};

struct Field {
    int prime;
    std::vector<Factor> factors;
};

struct Search {
    int length;
    Mask circle;
    std::vector<Field> fields;
    Taps taps{};
    std::uint64_t shapes = 0;
    std::uint64_t passed = 0;

    Mask rotate(Mask support, int shift) const {
        return ((support << shift) & circle) | (support >> (length - shift));
    }

    bool possible(Mask support) {
        // The least rotation has an occupied origin. It suffices to
        // compare the rotations that put one tap at the origin.
        for (std::size_t i = 1; i < taps.size(); ++i) {
            if (rotate(support, length - taps[i]) < support) return false;
        }
        ++shapes;
        for (int shift = 1; shift <= length / 2; ++shift) {
            if (std::popcount(support & rotate(support, shift)) > 4) return false;
        }
        ++passed;
        return true;
    }

    bool vanishes(const Factor& factor, int prime) const {
        for (int coefficient = 0; coefficient < factor.degree; ++coefficient) {
            int value = 0;
            for (int position : taps) value += factor.powers[coefficient][position];
            if (value % prime != 0) return false;
        }
        return true;
    }

    void visit(Mask support) {
        if (!possible(support)) return;
        for (const Field& field : fields) {
            int defect = 0;
            for (const Factor& factor : field.factors) {
                if (vanishes(factor, field.prime)) defect += factor.degree;
                if (defect > 7) break;
            }
            // The Python checker recomputes the complete gcd and checks
            // ordinary invertibility on every candidate emitted here.
            if (defect == 7) {
                std::cout << length << ' ' << field.prime;
                for (int tap : taps) std::cout << ' ' << tap;
                std::cout << '\n';
            }
        }
    }

    void enumerate(int count, int start, Mask support) {
        const int remaining = static_cast<int>(taps.size()) - count;
        if (remaining == 0) {
            visit(support);
            return;
        }
        for (int position = start; position <= length - remaining; ++position) {
            taps[count] = position;
            enumerate(count + 1, position + 1, support | (Mask{1} << position));
        }
    }
};
}  // namespace

int main() {
    Search search;
    std::size_t fields;
    if (!(std::cin >> search.length >> fields) || search.length < 9 || search.length > 50) return 1;
    search.circle = (Mask{1} << search.length) - 1;
    search.fields.resize(fields);
    for (Field& field : search.fields) {
        std::size_t factors;
        if (!(std::cin >> field.prime >> factors)) return 1;
        field.factors.resize(factors);
        for (Factor& factor : field.factors) {
            if (!(std::cin >> factor.degree) || factor.degree < 1 || factor.degree > 7) return 1;
            for (int position = 0; position < search.length; ++position) {
                for (int coefficient = 0; coefficient < factor.degree; ++coefficient) {
                    if (!(std::cin >> factor.powers[coefficient][position])) return 1;
                }
            }
        }
    }
    if (!search.fields.empty()) search.enumerate(1, 1, 1);
    std::cerr << search.length << ": " << search.fields.size() << " candidate fields, "
              << search.shapes << " shapes, " << search.passed << " pass the overlap bound\n";
}
