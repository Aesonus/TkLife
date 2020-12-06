from tkinter.ttk import Label, Entry

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
        returnval[dict_key] = (Label(master, text=label_text, **label_kwargs), Entry(master, textvariable=textvar, **entry_kwargs),)
    return returnval