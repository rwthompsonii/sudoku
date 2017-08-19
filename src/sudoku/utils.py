#!/usr/bin/env python3

from sudoku.constants import DEBUG

#really, this doesn't exist??
def map_in_place(fn, l):
    for i in range(len(l)):
        l[i] = fn(l[i])

#or this?!
#this likely should assert that its arguments are callable and iterable.
#TODO: define a debug_assert function to use here.
def lambda_find_first(function, iterable, default_value=None):
    return next(filter(function, iterable), default_value)

#TODO: this can be done more effectively with Logging, but i'll deal with that in a bit
def debug_print(printme, pretty=False):
    if DEBUG:
        if pretty:
            pprint.pprint(printme)
        else:
            print(printme)

#boilerplate
def main():
    raise Exception("do not directly call this module.")
if __name__ == '__main__':
    main()
