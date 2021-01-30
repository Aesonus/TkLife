"""Module for gridding out lists of elements"""
from itertools import accumulate
from math import floor
from typing import Mapping, Sequence


class Autogrid:
    """
    Class for getting grid coordinates based on an enumeration
    """

    def __init__(self, row_lengths, group_size=2):
        """
        Sets the row lengths and group size for generators
        """
        self.group_size = group_size
        self.__divisors = tuple(
            [length * group_size for length in row_lengths])
        self.__row_boundaries = tuple(accumulate(self.__divisors))

    def _get_row_index(self, index):
        """Gets the row that the index is in"""
        for bound_index, boundary in enumerate(self.__row_boundaries):
            if index < boundary:
                return bound_index
        return len(self.__row_boundaries) - 1

    def _get_divisor(self, index):
        return self.__divisors[self._get_row_index(index)]

    def _get_x_offset(self, index):
        row_index = self._get_row_index(index)
        first = self.__row_boundaries[row_index]
        return first % self._get_divisor(index)

    def _get_y_offset(self, index):
        row_index = self._get_row_index(index)
        last = self.__row_boundaries[row_index]
        if index < last:
            return 0
        return floor((index - last) / self._get_divisor(index)) + 1

    def grid_tuples(self, element_count):
        """Yield grid coordinates as a 2-tuples (x, y)"""
        for index in range(element_count):
            items_per_row = self._get_divisor(index)
            x_val = (index - self._get_x_offset(index)) % items_per_row
            y_val = self._get_row_index(index) + self._get_y_offset(index)
            yield (x_val, y_val)

    def grid_dicts(self, element_count, keynames: Sequence[str] = ('column', 'row')):
        """Yields grid coordinates as a dict using keynames as keys"""
        if len(tuple(iter(keynames))) != 2:
            raise ValueError("'keynames' must be of length %s" %
                             (2))
        return (
            dict(zip(iter(keynames), coords))
            for coords in self.grid_tuples(element_count)
        )

    def zip_dicts(self, elements, keynames: Sequence[str] = ('column', 'row'), grid_kwargs: Sequence[Mapping] = None, default_grid_kwargs: Mapping = {}):
        length = len(elements)
        grid_coords = self.grid_dicts(length, keynames=keynames)
        if grid_kwargs is None:
            return (
                zip(elements, grid_coords)
            )
        else:
            grid_kwargs = list(grid_kwargs)
            while len(grid_kwargs) < length:
                grid_kwargs.append(default_grid_kwargs)
            return zip(elements, grid_coords, tuple(grid_kwargs))
