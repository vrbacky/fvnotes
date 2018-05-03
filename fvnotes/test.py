from itertools import zip_longest
import time


def find_greater(sorted_numbers, key):

    index, number = next((index, number)
                         for index, number in enumerate(sorted_numbers)
                         if number > key)

    return index, number


def combine_positions(positions_1, positions_2, fillvalue=None):
    """Create non-overlapping ranges containing limits from the same iterator

    Combine two iterators and return tuples of non-overlapping positions limited
    by the positions from the same iterator. It can be used for example to find
    docstrings surrounded by triple single- or double-quotes.

    Parameters
    ----------
    positions1 : iter
        Positions of the limits of the first type (e.g. triple single-quotes)
    positions2 : iter
        Positions of the limits of the second type (e.g. triple double-quotes)
    fillvalue : str
        This value will be used if the last range is open (default: None).

    Returns
    -------
    iter
        Iterator of tuples containing opening and closing positions
        of the intervals.
    """
    pos1 = [(i, 1) for i in positions_1]
    pos2 = [(i, 2) for i in positions_2]

    positions = sorted(pos1 + pos2, key=lambda x: x[0])
    starts = []
    ends = []

    active_docstring = 0

    for position in positions:
        if active_docstring == 0:
            active_docstring = position[1]
            starts.append(position[0])
        elif active_docstring == position[1]:
            ends.append(position[0])
            active_docstring = 0
    print('ac', active_docstring)
    return zip_longest(starts, ends, fillvalue=fillvalue)

x = time.time()

p1 = [0, 0, 20, 30, 54, 78, 98, 102]
p2 = [10, 35, 58, 105]
print(list(combine_positions(p1, p2, fillvalue=150)))

print(time.time()-x)

