#!/usr/bin/env python3

import sys, logging, argparse, pprint, random, math, os, time
from  tkinter import *
import tkinter.messagebox as messagebox
import tkinter.simpledialog as simpledialog
from functools import partial, reduce
from operator import attrgetter
from threading import Timer

#my own libraries
import sudoku.utils as utils
import sudoku.buttons as buttons
import sudoku.structs as structs
from sudoku.constants import DEBUG
from sudoku.constants import MAX_ROWS_COLUMNS
import sudoku.globals as globals

#TODO: this can be done more effectively with Logging, but i'll deal with that in a bit
def debug_print(printme, pretty=False):
    if pretty:
        printme = pprint.pformat(printme)
    
    logger = logging.getLogger(__name__)
    logger.debug(printme)

def debug_print_button_array(button_array):
    debug_print(list(button_array), True)

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

def get_harder_initial_values():
    return [[0,0,0,0,0,0,0,0,0],
            [0,0,0,0,0,3,0,8,5],
            [0,0,1,0,2,0,0,0,0],
            [0,0,0,5,0,7,0,0,0],
            [0,0,4,0,0,0,1,0,0],
            [0,9,0,0,0,0,0,0,0],
            [5,0,0,0,0,0,0,7,3],
            [0,0,2,0,1,0,0,0,0],
            [0,0,0,0,4,0,0,0,9]] 

def isqrt(n, raiseOnError = True):
    #from https://stackoverflow.com/questions/15390807/integer-square-root-in-python/17495624
    #i don't really care that it overflows on large values because the input size is sanitized
    #much earlier.
    i = int(math.sqrt(n) + 0.5)
    if i**2 == n:
        return i
    if raiseOnError == True:
        raise ValueError('input rows/columns were not a perfect square')
    else:
        return -1 #clearly not possible

def isButtonInBlock(b, pot_value, block_size):
    #the modulus will be zero if i'm already on the starting row/column.
    start_row = pot_value.row - (pot_value.row % block_size)
    start_column = pot_value.column - (pot_value.column % block_size)

    #end row/column are not inclusive, that's actually the start of the next block
    end_row = start_row + block_size
    end_column = start_column + block_size

    return b.row >= start_row and \
           b.row < end_row and \
           b.column >= start_column and \
           b.column < end_column

#this function is the only one that actually requires a perfect square input.
def get_block_size(button_array):
    max_row = max(button_array, key=attrgetter('row')).row
    max_column = max(button_array, key=attrgetter('column')).column
    
    #these two statements ensure that the given inputs make nice blocks.
    assert max_row == max_column
    block_size = isqrt(max_row + 1)

    return block_size

def isValueInSameBlock(button_array, pot_value):
    block_size = get_block_size(button_array)

    return utils.find(lambda b: isButtonInBlock(b, pot_value, block_size) and b.value == pot_value.value, button_array) \
                        is not None
    
def isValueInRowOrColumn(button_array, pot_value):
    row_check = lambda b: b.column != pot_value.column and b.row == pot_value.row and b.value == pot_value.value
    column_check = lambda b: b.row != pot_value.row and b.column == pot_value.column and b.value == pot_value.value

    return utils.find(lambda b: row_check(b) or column_check(b), button_array) is not None

def isNewValueValid(button_array, pot_value):
    return not isValueInSameBlock(button_array, pot_value) and not isValueInRowOrColumn(button_array, pot_value) 

def set_choices_for_button(button_array, empty_button):
    pot_value = structs.PotentialValue(empty_button.row, empty_button.column, empty_button.value)
    block_size = get_block_size(button_array)    
    
    #function defined to look at the choice set defined by 
    #   1) row peers
    #   2) column peers
    #   3) block peers
    is_peer = lambda b : b.row == empty_button.row or b.column == empty_button.column or isButtonInBlock(b, pot_value, block_size)
    is_empty = lambda b : b.value == 0
    is_relevant = lambda b: is_peer(b) and not is_empty(b)
    relevant_peer_list = list(filter(is_relevant, button_array))
    currently_valid_choices = set(range(1,10))

    #remove any choice that's aleady present in the peer group, and you're left with the only valid choices for this button.
    #entirely possible to be left with the empty set, which should be noticed by other code as an impossibility for a valid empty button.
    for p in relevant_peer_list:
        currently_valid_choices.discard(p.value)

    empty_button.available_choices = currently_valid_choices
    return empty_button

def calculate_optimal_choice(button_array, all_empties):
    #given a set of empty choices, find the one with the minimum number of available choices.
    #this is somewhat of a heuristic, as it's typically how a human would solve it.

    #map a function over all the empties which then sets the number of available choices it finds onto the button 
    utils.map_in_place(partial(set_choices_for_button, button_array), all_empties)
    
    #next, min the entire empties list with available choices as the determinant.
    #and return the result of that operation
    return min(all_empties, key=lambda e: len(e.available_choices))

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
   
    logger = logging.getLogger(__name__)
   
    start_time = time.perf_counter()
    solved = guess(button_array)
    end_time = time.perf_counter()
    if solved == True:
        logger.info("All done. Time to solve: %s" % float('%.3g' % (end_time - start_time)))
    else:
        logger.info("Cannot be solved. Time for attempt: %s" % float('%.3g' % (end_time - start_time)))
        isYes = messagebox.askyesno("Sudoku Solver", "No solution found.  Full clear the board?")
        if (isYes): 
            clear_action(True, button_array)

def reset_guesses_count_action():
    globals.total_guesses.set(0)
     
def update_ui():
    #debug_print('update_ui')
    global root
    root.update()

def maybe_update_ui():
    now_time = time.perf_counter()
    if (now_time - globals.refresh_ui_time) > 1.0:
        globals.refresh_ui_time = now_time
        update_ui()

def guess(button_array):
    chosen_empty = None
    all_empties = list(filter(lambda i: i.value == 0 and i.hard_set == False, button_array))
    
    if len(all_empties) > 0:
        chosen_empty = calculate_optimal_choice(button_array, all_empties) 

    if chosen_empty is not None:
        debug_print("working on chosen_empty: %s" % (chosen_empty))
        #some puzzles are built to mess with us if we don't introduce at least a small 
        #amount of randomness.  we're working with the optimal button, but it has 1-9 choices
        #and you can construct sudokus that really like to mess with solvers that start with 1.
        available_choices = list(chosen_empty.available_choices)
        random.shuffle(available_choices)
        
        update_button = utils.find(lambda i: i.row == chosen_empty.row and i.column == chosen_empty.column, button_array)
        assert update_button is not None
        
        for c in available_choices:
            globals.total_guesses.set(globals.total_guesses.get() + 1)
            
            maybe_update_ui()   

            update_button.set_value(c)

            if guess(button_array):
                return True #start unwinding
            else:
                update_button.set_value(0)

        #if we make it here then one of the previous values was invalid.  start unwinding.
        return False
    else:
        return True #all done, the remaining values are filled.

def on_button_clicked(button_array, button):
    if not button.hard_set:
        new_value = simpledialog.askinteger("Enter a value.", "Number between 1-9, 0 to clear", minvalue=0, maxvalue=9)
        if new_value is not None and new_value != 0:
            pot_value = structs.PotentialValue(button.row, button.column, new_value)
            if isNewValueValid(button_array, pot_value):
                button.set_value(new_value)
            else:
                #calculate why.
                conflict = utils.find(lambda b: b.row == button.row and b.value == new_value, button_array)
                if conflict is None:
                    conflict = utils.find(lambda b: b.column == button.column and b.value == new_value, button_array)
                if conflict is None:
                    conflict = utils.find(lambda b: isButtonInBlock(b, pot_value, get_block_size(button_array)) and b.value == new_value, button_array)
                assert conflict is not None#there's a major issue in the logic if this hits.
                messagebox.showwarning("Value is not valid.", "The value: " + str(new_value) + " is not a valid value for this location, it conflicts with the button's value at (row:" + str(conflict.row+1) + ", column:" + str(conflict.column+1) + ").  Please try again.")
        elif new_value == 0:
            button.set_value(new_value)
    else:
        messagebox.showerror("Sudoku Solver", "May not unset initial condition.")

def startup_ui(rows, columns):
    #hack global to update the UI?
    global root
    root = Tk()
    root.wm_title("Sudoku Solver")   
    #remove the maximize button.
    root.resizable(0,0)

    globals.total_guesses = IntVar()
    button_array = []

    #TODO: this needs to be initializable from somewhere besides this code.
    #init_values = get_initial_values()
    init_values = get_harder_initial_values()

    assert isqrt(rows) != -1
    assert rows == columns
    block_size = isqrt(rows)
    
    frame_array = []
    for r in range(rows):
        for c in range(columns):
            if r % block_size == 0 and c % block_size == 0:
                frame = Frame(root, borderwidth=2, background="black")
                frame.grid(row = (r // block_size), column = (c // block_size))
                frame_array.append(frame)
    
    for r in range(rows):
        for c in range(columns):
            correct_frame_index = (r // block_size) * block_size + (c // block_size)      
            correct_frame = frame_array[correct_frame_index]

            button = buttons.SudokuButton(r, c, correct_frame, borderwidth = 1)
            button.configure(command=partial(on_button_clicked, button_array, button))
            
            #TODO: all this init code is just to write the solver.  Need to init smarter.
            init_value = init_values[r][c]
            if not init_value == 0:
                button.set_init(init_values[r][c])
                button.hard_set = True
            
            button.grid(row = (r % block_size), column = (c % block_size))
            button_array.append(button)

    #the tkinter framework really wants a no argument function as the callback,
    #so we give it one by partially applying the argument here.
    solve_button = Button(root, text="Solve", command=partial(solve_action, button_array)).grid(row=rows+1, columnspan=columns, sticky=E+W+N+S)
    clear_button = Button(root, text="Clear", command=partial(clear_action, False, button_array)).grid(row=rows+2, columnspan=columns, sticky=E+W+N+S)
    full_clear_button = Button(root, text="Full Clear", command=partial(clear_action, True, button_array)).grid(row=rows+3, columnspan=columns, sticky=E+W+N+S)
    reset_guesses_button = Button(root, textvariable=globals.total_guesses, command=reset_guesses_count_action).grid(row=rows+4, columnspan=columns, sticky=E+N+S)
    reset_guesses_label = Label(root, text="Total Guesses:").grid(row=rows+4, columnspan=columns//2, sticky=W+N+S)
    
    #and go into the main loop
    root.mainloop()

"""
function used to make argparse reject values of rows or columns that cannot be used.
"""
def row_or_column_type(x):
    x = int(x)
    if x > MAX_ROWS_COLUMNS:
        raise argparse.ArgumentTypeError("Maximum rows/columns is " + str(MAX_ROWS_COLUMNS) + ".")
    elif isqrt(x, raiseOnError=False) == -1: 
        raise argparse.ArgumentTypeError("Input is required to be a perfect square.")        
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
    if (args.debug == True):
        logging_level = logging.DEBUG
    else:
        logging_level = logging.INFO
    logging.basicConfig(level=logging_level)

    debug_print("Debugging information is turned on")
    return (args.rows,args.columns)

#boilerplate
def main():
    random.seed()
    rows,columns = setup_args()
    startup_ui(rows, columns) 
if __name__ == '__main__':
    main()
