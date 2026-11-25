"""Classify all minimum-support mod-17 boards, up to rows and columns."""

from argparse import ArgumentParser
from pathlib import Path
from subprocess import check_output

from check_mod11_minimum import check_lower_bound, determinant
from check_mod17_shapes import column_orbit, column_permutations, from_masks, to_masks


def eight_row_classes(binary):
    output = check_output([str(binary.resolve()), '--eight-row-mod17-boards'], text=True)
    boards = {tuple(map(int, line.split()[1:])) for line in output.splitlines() if line.startswith('mod17:')}
    assert len(boards) == 40
    transforms = list(column_permutations(8))
    classes = {}
    while boards:
        rows = min(boards)
        decoded = from_masks(rows)
        assert sum(map(sum, decoded)) == 23 and abs(determinant(decoded)) == 17
        orbit = column_orbit(rows, transforms)
        classes[min(orbit)] = len(orbit)
        boards.difference_update(orbit)

    forms = sorted(classes)
    transpose_ids = []
    for i, form in enumerate(forms, start=1):
        transpose = to_masks(zip(*from_masks(form)))
        partner = forms.index(min(column_orbit(transpose, transforms))) + 1
        transpose_ids.append(partner)
        print(i, ' '.join(f'{row:08b}' for row in form), classes[form], partner)
    assert len(forms) == 13 and sum(classes.values()) == 372_960
    assert transpose_ids == [1,13,5,9,3,10,8,7,4,6,11,12,2]
    print('13 shapes, eight if transposes are identified.')


if __name__ == '__main__':
    parser = ArgumentParser(description=__doc__)
    parser.add_argument('binary', type=Path, help='compiled seven-row spectrum checker')
    args = parser.parse_args()
    eight_row_classes(args.binary)
    # At 23 ones, twelve or more rows would require a removable weight-one row.
    cases = [
        (9, [75, 4_011, 170_008, 2_661_970, 13_727_939]),
        (10, [100, 4_720, 52_854]),
        (11, [91]),
    ]
    for dimension, counts in cases:
        print(f'Checking size {dimension} at 23 ones.', flush=True)
        check_lower_bound(prime=17, cap=23, dimension=dimension, expected_counts=counts)
