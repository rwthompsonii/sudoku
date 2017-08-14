#!/usr/bin/env python3

import sys, logging, argparse, pprint, random
from  tkinter import *
from functools import partial
DEBUG = False
MAX_ROWS_COLUMNS=15

class SudokuButton(Button):
    def __init__(self, row, column, master=None, **options):
        super().__init__(master, options)
        self.row = row
        self.column = column
        self.value = 0 #the zero value is used to indicate that this is an invalid square to the backtracker.
        self.textvariable = StringVar()
        self.configure(textvariable = self.textvariable, width=2, height=2)
        self.hard_set = False #used to indicate that this is part of the initial condition and should not be reset when backtracking/solving.

    def set_value(self, value):
        self.value = value
        if (value != 0):
            self.textvariable.set(str(value)) 
        else:
            self.textvariable.set("")

    def __repr__(self):
        return 'SudokuButton(row=%s, column=%s, value=%s, textvariable=%s, hard_set=%s)' % (self.row, self.column, self.value, self.textvariable.get(), self.hard_set)

#TODO: these need to come from user input or at least a .conf file
def get_initial_values():
    return [[5,3,0,0,7,0,0,0,0],
            [6,0,0,1,9,5,0,0,0],
            [0,9,8,0,0,0,0,6,0],
            [8,0,0,0,6,0,0,0,3],
            [4,0,0,8,0,3,0,0,1],
            [7,0,0,0,2,0,0,0,6],
            [0,6,0,0,0,0,2,8,0],
            [0,0,0,4,1,9,0,0,5],
            [0,0,0,0,8,0,0,7,9]]

def debug_print_button_array(button_array):
    debug_print(list(button_array), True)

def solve_action(button_array):
    debug_print("Solve button clicked.")
    debug_print_button_array(button_array)

def startup_ui(rows, columns):
    root = Tk()
    root.wm_title("Sudoku Solver")   
    #remove the maximize button.
    root.resizable(0,0)

    button_array = []
    init_values = get_initial_values()

    for r in range(rows):
        for c in range(columns):
            button = SudokuButton(r, c, root, borderwidth = 1)
            button.set_value(init_values[r][c])
            button.grid(row = r,column = c)
            button_array.append(button)

    #the tkinter framework really wants a no argument function as the callback,
    #so we give it one by partially applying the argument here.
    solve_button = Button(root, text="Solve", command=partial(solve_action, button_array)).grid(row=rows+1, columnspan=columns, sticky=E+W+N+S)

    root.mainloop()

#TODO: this can be done more effectively with Logging, but i'll deal with that in a bit
def debug_print(printme, pretty=False):
    if DEBUG:
        if pretty:
            pprint.pprint(printme)
        else:
            print(printme)

def row_or_column_type(x):
    x = int(x)
    if x > MAX_ROWS_COLUMNS:
        raise argparse.ArgumentTypeError("Maximum rows/columns is " + str(MAX_ROWS_COLUMNS) + ".")
    return x

def setup_args():
    default_row_column=9
    arg_parser = argparse.ArgumentParser(description='Solve a sudoku.')
    arg_parser.add_argument('name', metavar='name',
                            help='the name of the thing')
    arg_parser.add_argument('--debug', help='turn on debugging information', action='store_true')
    arg_parser.add_argument('--rows', help='number of rows in the sudoku, default: ' + str(default_row_column) + ", max: " + str(MAX_ROWS_COLUMNS) + ".", type=row_or_column_type, default=default_row_column)
    arg_parser.add_argument('--columns', help='number of columns in the sudoku, default: ' + str(default_row_column) + ", max: " + str(MAX_ROWS_COLUMNS) + ".", type=row_or_column_type, default=default_row_column)
    
    
    #arg_parser.add_argument('--sum', dest='accumulate', action='store_const',
    #                        const=sum, default=max,
    #                        help='sum the integers (default: find the max)')

    args = arg_parser.parse_args()
    print("Hello, welcome to sudoku solver: ", args.name)
    global DEBUG
    DEBUG = args.debug
    debug_print("Debugging information is turned on")
    return (args.rows,args.columns)
#boilerplate
def main():
    random.seed()
    rows,columns = setup_args()
    startup_ui(rows, columns) 
if __name__ == '__main__':
    main()
