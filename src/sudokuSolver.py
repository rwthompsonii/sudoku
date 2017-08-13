#!/usr/bin/env python3

import sys, logging, argparse, pprint
from  tkinter import *
DEBUG = False
MAX_ROWS_COLUMNS=15

class SudokuButton(Button):
    def __init__(self, row, column, master=None, **options):
        self.row = row
        self.column = column
        self.value = 0 #the zero value is used to indicate that this is an invalid square to the backtracker.
        self.hard_set = False #used to indicate that this is part of the initial condition and should not be reset when backtracking/solving.
        super().__init__(master, options)

    def __repr__(self):
        return 'SudokuButton(row=%s, column=%s, value=%s, hard_set=%s)' % (self.row, self.column, self.value, self.hard_set)

def debug_print_button_array(button_array):
    debug_print(list(button_array), True)

def startup_ui(rows, columns):
    root = Tk()
    button_array = []
    for r in range(rows):
        for c in range(columns):
            button = SudokuButton(r, c, root, text = "("+str(r+1)+","+str(c+1)+")", borderwidth = 1)
            button.grid(row = r,column = c)
            button_array.append(button)

    debug_print_button_array(button_array)
    
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
    rows,columns = setup_args()
    startup_ui(rows, columns) 
if __name__ == '__main__':
    main()
