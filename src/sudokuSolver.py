#!/usr/bin/env python3

import sys, logging, argparse
DEBUG = False














#this can be done more effectively with Logging, but i'll deal with that in a bit
def debug_print(printme):
    if DEBUG:
        print(printme)

#boilerplate
def main():
    arg_parser = argparse.ArgumentParser(description='Solve a sudoku.')
    arg_parser.add_argument('name', metavar='name',
                            help='the name of the thing')
    arg_parser.add_argument('--debug', help='turn on debugging information', action='store_true')
    
    #arg_parser.add_argument('--sum', dest='accumulate', action='store_const',
    #                        const=sum, default=max,
    #                        help='sum the integers (default: find the max)')

    args = arg_parser.parse_args()
    print("Hello, welcome to sudoku solver: ", args.name)
    global DEBUG
    DEBUG = args.debug
    debug_print("Debugging information is turned on")
    
if __name__ == '__main__':
    main()
