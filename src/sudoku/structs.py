#!/usr/bin/env python3

class PotentialValue():
    def __init__(self, row, column, block, value):
        self.row = row
        self.column = column
        self.block = block
        self.value = value

    def __repr__(self):
        #return 'PotentialValue(row = %s, column = %s, block = %s, value = %s)' % str(self.row), str(self.column), str(self.block), str(self.value)
        return "row = '{0}', column = '{1}', block = '{2}', value = '{3}'\n".format(self.row, self.column, self.block, self.value)

#boilerplate
def main():
    raise Exception("do not directly call this module.")
if __name__ == '__main__':
    main()
