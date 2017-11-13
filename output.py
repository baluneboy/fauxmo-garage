#!/usr/bin/env python


def get_print_fun(verbosity):
    """return function that does printing that depends on verbosity level"""

    if verbosity is None:
        # this is like verbosity = 0
        return lambda *args: None  # do nothing; no op
    else:
        def _print_fcn(*args):
            """print vcount args one per line"""
            # Print each argument separately so caller doesn't need to
            # stuff everything to be printed into a single string
            upper = verbosity
            if verbosity >= 3:
                upper = len(args)
            for arg in args[0:upper]:
                print arg,
            print
        return _print_fcn


if __name__ == '__main__':

    for v in range(1, 9):
        print 'verbosity', v,
        vprint = get_print_fun(v)
        #                        V-- saturation starts at 3rd arg
        vprint('hello', 'there', 'big', 'guy', 'how', 'is', 'it', 'going')

    v = None
    vprint = get_print_fun(v)
    print 'verbosity', v,
    vprint('hello', 'there')