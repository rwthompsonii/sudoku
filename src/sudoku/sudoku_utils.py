#really, this doesn't exist??
def map_in_place(fn, l):
    for i in range(len(l)):
        l[i] = fn(l[i])

#or this?!
#this likely should assert that its arguments are callable and iterable.
#TODO: define a debug_assert function to use here.
def lambda_find_first(function, iterable, default_value=None):
    return next(filter(function, iterable), default_value)

