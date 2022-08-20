"""Module for gridding out lists of elements"""
from collections import namedtuple
from itertools import accumulate
import itertools
from math import floor
from tkinter import Widget
from typing import Any, Dict, Generator, Iterator, Mapping, NamedTuple, Tuple, Sequence, Optional
import warnings


class Autogrid(object):
    """
    Class for getting grid coordinates based on an enumeration
    """

    def __init__(self, row_lengths: 'Sequence[int]', group_size: 'int'=1):
        """
        Creates the gridder object

        Arguments:
            row_lengths {Sequence[int]} -- Tells how long each row should be. The last row length is used if there are more widgets than row lengths.

        Keyword Arguments:
            group_size {int} -- DEPRECATED (default: {1})
        """
        self.group_size = group_size
        self.row_lengths = [*row_lengths]
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
        warnings.warn("grid_tuples is deprecated", DeprecationWarning)
        for index in range(element_count):
            items_per_row = self._get_divisor(index)
            x_val = (index - self._get_x_offset(index)) % items_per_row
            y_val = self._get_row_index(index) + self._get_y_offset(index)
            yield (x_val, y_val)

    def grid_dicts(self, element_count, keynames: Sequence[str] = ('column', 'row')):
        """Yields grid coordinates as a dict using keynames as keys"""
        warnings.warn("grid_dicts is deprecated", DeprecationWarning)
        if len(tuple(iter(keynames))) != 2:
            raise ValueError("'keynames' must be of length %s" %
                             (2))
        return (
            dict(zip(iter(keynames), coords))
            for coords in self.grid_tuples(element_count)
        )

    def zip_dicts(self,
                  elements: Sequence[Widget],
                  keynames: Sequence[str] = ('column', 'row'),
                  grid_kwargs_list: Sequence[Mapping] = [],
                  fill_grid_kwargs: Mapping = {},
                  all_grid_kwargs: Mapping = {}) -> Iterator[Tuple[Widget, Dict]]:
        """
        Generate a tuple containing each widget and a dict containing coordinate and
        all_grid_kwargs mappings, optionally merged with a each dict in
        grid_kwargs_list. If there are less elements in the grid_kwargs_list than in the
        elements list, then the fill_grid_kwargs will be used after kwargs_list is consumed.
        """
        warnings.warn("zip_dicts is deprecated", DeprecationWarning)
        length = len(elements)
        for (index, coords), widget in zip(enumerate(self.grid_dicts(length, keynames=keynames)), elements):
            grid_kwargs = coords.copy()
            grid_kwargs.update(all_grid_kwargs)
            try:
                grid_kwargs.update(grid_kwargs_list[index])
            except IndexError:
                grid_kwargs.update(fill_grid_kwargs)
            yield (widget, grid_kwargs)

    def __call__(self,
        elements: 'Sequence[Widget]',
        grid_kwargs: Optional[Sequence[Mapping[str, Any]]] = None,
        all_kwargs: Optional[Mapping[str, Any]] = None,
        fill_kwargs: Optional[Mapping[str, Any]] = None,
    ) -> Generator['GridArgs', None, None]:
        if grid_kwargs is None: grid_kwargs = []
        if all_kwargs is None: all_kwargs = {}
        if fill_kwargs is None: fill_kwargs = {}

        def element_group(elements):
            start = 0
            elements = list(elements)
            _gd_kw = list(itertools.chain(grid_kwargs, itertools.repeat(fill_kwargs, len(elements))))
            for row, row_length in enumerate(self.row_lengths):
                yield GridArgs(
                    tuple(itertools.islice(elements, start, start + row_length)),
                    tuple(itertools.islice(_gd_kw, start, start + row_length)),
                    tuple({'row': row, 'column': col} for col in range(row_length)),
                    all_kwargs,)
                start += row_length
            while (True):
                row += 1
                slc = [*itertools.islice(elements, start, start + row_length)]
                if slc == []: break
                yield GridArgs(
                    tuple(slc),
                    tuple(itertools.islice(_gd_kw, start, start + row_length)),
                    tuple({'row': row, 'column': col} for col in range(row_length)),
                all_kwargs,)
                start += row_length
        for widgets, grid_kw, pos_kw, all_kw in element_group(elements):
            for w, gkw, pkw in zip(widgets, grid_kw, pos_kw):
                yield w, {**pkw, **gkw, **all_kw}

class GridArgs(NamedTuple):
    widgets: Tuple[Widget]
    grid_kwargs: Tuple[Mapping[str, Any]]
    pos_kwargs: Tuple[Mapping[str, Any]]
    all_kwargs: Mapping[str, Any]