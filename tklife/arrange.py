"""Module for gridding out lists of elements"""
import itertools
from itertools import accumulate
from tkinter import Widget
from typing import (Any, Generator, Mapping, NamedTuple, Optional, Sequence,
                    Tuple)


class Autogrid(object):
    """
    Class for getting grid coordinates based on an enumeration
    """

    def __init__(self, row_lengths: 'Sequence[int]'):
        """
        Creates the gridder object

        Arguments:
            row_lengths {Sequence[int]} -- Tells how long each row should be. The last row length is used if there are more widgets than row lengths.
        """
        self.row_lengths = [*row_lengths]

    def __call__(self,
                 elements: 'Sequence[Widget]',
                 grid_kwargs: Optional[Sequence[Mapping[str, Any]]] = None,
                 all_kwargs: Optional[Mapping[str, Any]] = None,
                 fill_kwargs: Optional[Mapping[str, Any]] = None,
                 ) -> Generator[tuple[Widget, Mapping[str, Any]], None, None]:
        if grid_kwargs is None:
            grid_kwargs = []
        if all_kwargs is None:
            all_kwargs = {}
        if fill_kwargs is None:
            fill_kwargs = {}

        def element_group(elements):
            start = 0
            elements = list(elements)
            _gd_kw = list(itertools.chain(
                grid_kwargs, itertools.repeat(fill_kwargs, len(elements))))
            for row, row_length in enumerate(self.row_lengths):
                yield GridArgs(
                    tuple(itertools.islice(elements, start, start + row_length)),
                    tuple(itertools.islice(_gd_kw, start, start + row_length)),
                    tuple({'row': row, 'column': col}
                          for col in range(row_length)),
                    all_kwargs,)
                start += row_length
            while (True):
                row += 1
                slc = [*itertools.islice(elements, start, start + row_length)]
                if slc == []:
                    break
                yield GridArgs(
                    tuple(slc),
                    tuple(itertools.islice(_gd_kw, start, start + row_length)),
                    tuple({'row': row, 'column': col}
                          for col in range(row_length)),
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
