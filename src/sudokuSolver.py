#!/usr/bin/env python3

import sys, logging, argparse, pprint, random, math
from  tkinter import *
from functools import partial
from operator import attrgetter

#constants
DEBUG = False
MAX_ROWS_COLUMNS=15

class PotentialValue():
    def __init__(self, row, column, value):
        self.row = row
        self.column = column
        self.value = value

    def __repr__():
        return 'PotentialValue(row = %s, column = %s, value = %s) % self.row, self.column, self.value'

class SudokuButton(Button):
    def __init__(self, row, column, master=None, **options):
        super().__init__(master, options)
        self.row = row
        self.column = column
        self.value = 0 #the zero value is used to indicate that this is an invalid square to the backtracker.
        self.textvariable = StringVar()
        self.hard_set = False #used to indicate that this is part of the initial condition and should not be reset when backtracking/solving.
        self.configure(textvariable = self.textvariable, width=2, height=2, command=self.on_button_clicked)

    def set_init(self, value):
        self.set_value(value)
        self.hard_set = True
        self.configure(bg = "gray")

    def unset_init(self):
        self.hard_set = False
        self.set_value(0)
        self.configure(bg = "white")

    def set_value(self, value):
        self.value = value
        if (value != 0):
            self.textvariable.set(str(value)) 
        else:
            self.textvariable.set("")
    
    def on_button_clicked(self):
        debug_print("button clicked, location: [{0.row},{0.column}]".format(self))
        debug_print(self.__repr__())

    def __repr__(self):
        return 'SudokuButton(row=%s, column=%s, value=%s, textvariable=%s, hard_set=%s)' % (self.row, self.column, self.value, self.textvariable.get(), self.hard_set)

    def __str__(self):
        return self.__repr__()

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

def isqrt(n):
    #from https://stackoverflow.com/questions/15390807/integer-square-root-in-python/17495624
    #i don't really care that it overflows on large values because the input size is sanitized
    #much earlier.
    i = int(math.sqrt(n) + 0.5)
    if i**2 == n:
        return i
    raise ValueError('input rows/columns were not a perfect square')

#this function is the only one that actually requires a perfect square input.
def isValueInSameBlock(button_array, pot_value):
    max_row = max(button_array, key=attrgetter('row')).row
    max_column = max(button_array, key=attrgetter('column')).column
    
    #these two statements ensure that the given inputs make nice blocks.
    assert max_row == max_column
    block_size = isqrt(max_row + 1)

    #the modulus will be zero if i'm already on the starting row/column.
    start_row = pot_value.row - (pot_value.row % block_size)
    start_column = pot_value.column - (pot_value.column % block_size)

    #end row is not inclusive, it's actually the start of the next block
    end_row = start_row + block_size
    end_column = start_column + block_size

    for button in button_array:
        if button.row >= start_row and button.row < end_row and button.column >= start_column and button.column < end_column and button.value == pot_value.value:
            return True

    return False

def isValueInRowOrColumn(button_array, pot_value):
    for button in button_array:
        if button.column != pot_value.column and button.row == pot_value.row and button.value == pot_value.value: #don't check the same button...
            return True
        if button.row != pot_value.row and button.column == pot_value.column and button.value == pot_value.value: #don't check the same button... 
            return True

    return False

def isNewValueValid(button_array, pot_value):
    return not isValueInSameBlock(button_array, pot_value) and not isValueInRowOrColumn(button_array, pot_value) 

def solve_action(button_array):
    debug_print("Solve button clicked.")
    #debug_print_button_array(button_array)
    solved = guess(button_array)
    if solved == True:
        debug_print("All done.")

def guess(button_array):
    first_empty = next(filter(lambda i: i.value == 0 and i.hard_set == False, button_array), None)
    debug_print("working on first_empty: %s" % (first_empty))
    if first_empty is not None:
        #debug_print(first_empty.__repr__())
        randoms = list(range(1,10))
        random.shuffle(randoms)
        #debug_print(randoms)
        
        for r in randoms:
            pot_value = PotentialValue(first_empty.row, first_empty.column, r)
            if isNewValueValid(button_array, pot_value):
                for button in button_array:
                    if button.row == first_empty.row and button.column == first_empty.column:
                        button.set_value(pot_value.value)
                if guess(button_array):
                   return True #start unwinding
                else:
                    for button in button_array:
                        if button.row == first_empty.row and button.column == first_empty.column:
                            button.set_value(0)
        
        #if we make it here then none of the random values were valid.  start unwinding.
        return False
    else:
        return True #all done, the remaining values are filled.

    

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
            
            #TODO: all this init code is just to debug the solver.  Need to init smarter.
            init_value = init_values[r][c]
            if not init_value == 0:
                button.set_init(init_values[r][c])
                button.hard_set = True
            
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
