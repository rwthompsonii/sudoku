#!/usr/bin/env python3

import sys, logging, argparse, pprint, random, math, os
from  tkinter import *
import tkinter.messagebox as messagebox
from functools import partial
from operator import attrgetter

#my own libraries
import sudoku.utils as utils
from sudoku.utils import debug_print
import sudoku.buttons as buttons
import sudoku.structs as structs
from sudoku.constants import DEBUG
from sudoku.constants import MAX_ROWS_COLUMNS
import sudoku.globals as globals

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

def isqrt(n, raiseOnError = True):
    #from https://stackoverflow.com/questions/15390807/integer-square-root-in-python/17495624
    #i don't really care that it overflows on large values because the input size is sanitized
    #much earlier.
    i = int(math.sqrt(n) + 0.5)
    if i**2 == n:
        return i
    if raiseOnError == True:
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

    #end row/column are not inclusive, that's actually the start of the next block
    end_row = start_row + block_size
    end_column = start_column + block_size

    return utils.lambda_find_first(lambda b: b.row >= start_row and \
                                       b.row < end_row and \
                                       b.column >= start_column and \
                                       b.column < end_column and \
                                       b.value == pot_value.value, \
                             button_array) \
                                is not None
    
def isValueInRowOrColumn(button_array, pot_value):
    row_check = lambda b: b.column != pot_value.column and b.row == pot_value.row and b.value == pot_value.value
    column_check = lambda b: b.row != pot_value.row and b.column == pot_value.column and b.value == pot_value.value

    return utils.lambda_find_first(lambda b: row_check(b) or column_check(b), button_array) is not None

def isNewValueValid(button_array, pot_value):
    return not isValueInSameBlock(button_array, pot_value) and not isValueInRowOrColumn(button_array, pot_value) 

def clear_button_func(full_clear, button):
    if button.hard_set == False:
        button.set_value(0)
    elif full_clear == True:
        button.unset_init()
    return button

def clear_action(full_clear, button_array):
    debug_print("Clear action.")
    reset_guesses_count_action()
    utils.map_in_place(partial(clear_button_func, full_clear), button_array)

def solve_action(button_array):
    debug_print("Solve action.")
   
    solved = guess(button_array)
    if solved == True:
        debug_print("All done.")
    else:
        debug_print("cannot be solved.")
        isYes = messagebox.askyesno("Sudoku Solver", "No solution found.  Full clear the board?")
        if (isYes): 
            clear_action(True, button_array)

def reset_guesses_count_action():
    globals.total_guesses.set(0)
     
def guess(button_array):
    first_empty = utils.lambda_find_first(lambda i: i.value == 0 and i.hard_set == False, button_array)
    debug_print("working on first_empty: %s" % (first_empty))
    if first_empty is not None:
        randoms = list(range(1,10))
        random.shuffle(randoms)
        
        for r in randoms:
            globals.total_guesses.set(globals.total_guesses.get() + 1)
            pot_value = structs.PotentialValue(first_empty.row, first_empty.column, r)
            if isNewValueValid(button_array, pot_value):
                update_button = utils.lambda_find_first(lambda i: i.row == first_empty.row and i.column == first_empty.column, button_array)
                assert update_button is not None

                update_button.set_value(pot_value.value)

                if guess(button_array):
                   return True #start unwinding
                else:
                    update_button.set_value(0)

        #if we make it here then none of the random values were valid.  start unwinding.
        return False
    else:
        return True #all done, the remaining values are filled.

def startup_ui(rows, columns):
    root = Tk()
    root.wm_title("Sudoku Solver")   
    #remove the maximize button.
    root.resizable(0,0)

    globals.total_guesses = IntVar()
    button_array = []
    init_values = get_initial_values()

    for r in range(rows):
        for c in range(columns):
            button = buttons.SudokuButton(r, c, root, borderwidth = 1)
            
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
    clear_button = Button(root, text="Clear", command=partial(clear_action, False, button_array)).grid(row=rows+2, columnspan=columns, sticky=E+W+N+S)
    full_clear_button = Button(root, text="Full Clear", command=partial(clear_action, True, button_array)).grid(row=rows+3, columnspan=columns, sticky=E+W+N+S)
    reset_guesses_button = Button(root, textvariable=globals.total_guesses, command=reset_guesses_count_action).grid(row=rows+4, columnspan=columns, sticky=E+W+N+S)
    reset_guesses_label = Label(root, text="Total Guesses:").grid(row=rows+4, columnspan=int(columns/2), sticky=E+W+N+S)
    root.mainloop()

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
