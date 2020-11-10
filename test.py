import tklife
from tkinter import StringVar, Entry, Button
from tklife.shortcuts import *
from tklife.simpledialog import *

class Test(tklife.Main):
    def _create_widgets(self):
        self.b = Button(self, text='woo', command=self.foo)
        self.x = StringVar()
        self.x.set('Hello')
        e = labelled_entry(self, test=('Test', self.x))
        self.c, self.d = e['test']

    def _layout_widgets(self):
        self.b.pack()
        self.c.pack()
        self.d.pack()

    def foo(self):
        print(AskInteger.show(self, title='Test', prompt="Test dialog"))

Test().mainloop()