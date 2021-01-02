from functools import reduce
from typing import Dict, Iterable, Tuple

from tkinter.ttk import Label, Entry

from tkinter import Widget


def labelled_entry(master, entry_kwargs={}, label_kwargs={}, **label_groups):
    """
    Creates an entry widget with a label

    master - tkinter.Widget The parent widget
    label_groups - 2-tuples containing label text and textvariable
    entry_kwargs - keyword arguments passed to each entry
    label_kwargs - keyword arguments passed to each label

    returns a dict of 2-tuples containing the Label and Entry under the kwarg keyword key
    """
    returnval = {}
    for dict_key, (label_text, textvar) in label_groups.items():
        returnval[dict_key] = (Label(master, text=label_text, **label_kwargs),
                               Entry(master, textvariable=textvar, **entry_kwargs),)
    return returnval


def labelled_widgets(master: Widget, labels: Iterable[str], widgets: Iterable[Widget], kwargs: Iterable[Dict], widget_kwargs: Dict = {}, label_kwargs: Dict = {},):
    args = (labels, widgets, kwargs)
    size = sum(map(len, args))
    if size % 3 != 0:
        raise ValueError("'{}', '{}', and '{}' must be of same length".format('labels', 'widgets', 'kwargs'))
    return_ = []
    for (label, widget, kwarg) in zip(*args):
        return_.append(
            Label(master, text=label, **label_kwargs),
        )
        return_.append(
            widget(master, **kwarg, **widget_kwargs)
        )
    return return_
