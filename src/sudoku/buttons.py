#!/usr/bin/env python3

#required for the Button definition
from tkinter import Button 
from tkinter import StringVar

class SudokuButton(Button):
    def __init__(self, row, column, master=None, **options):
        super().__init__(master, options)
        self.row = row
        self.column = column
        self.value = 0 #the zero value is used to indicate that this is an invalid square to the backtracker.
        self.textvariable = StringVar()
        self.hard_set = False #used to indicate that this is part of the initial condition and should not be reset when backtracking/solving.
        self.available_choices = set() 
        self.configure(textvariable = self.textvariable, width=2, height=2)

    def set_init(self, value):
        self.set_value(value)
        self.hard_set = True
        self.configure(bg = "gray")

    def unset_init(self):
        self.hard_set = False
        self.set_value(0)
        self.configure(bg = "light grey")

    def set_value(self, value):
        self.value = value
        if (value != 0):
            self.textvariable.set(str(value)) 
        else:
            self.textvariable.set("")
   
    def __repr__(self):
        return 'SudokuButton(row=%s, column=%s, value=%s, textvariable=%s, hard_set=%s)' % (self.row, self.column, self.value, self.textvariable.get(), self.hard_set)

    def __str__(self):
        return self.__repr__()

#boilerplate
def main():
    raise Exception("do not directly call this module.")
if __name__ == '__main__':
    main
