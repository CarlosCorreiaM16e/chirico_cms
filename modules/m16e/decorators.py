## {{{ http://code.activestate.com/recipes/577819/ (r2)
#!/usr/bin/env python

"""
Deprecated decorator.

Author: Giampaolo Rodola' <g.rodola [AT] gmail [DOT] com>
License: MIT
"""

from m16e import term
import sys
import traceback
import warnings

#------------------------------------------------------------------
def try_wrapper( w_function ):
    def wrapper():
        try:
            w_function()
        except:
            t, v, tb = sys.exc_info()
            traceback.print_exception( t, v, tb )
    return wrapper

#------------------------------------------------------------------
def deprecated( replacement=None ):
    """A decorator which can be used to mark functions as deprecated.
    replacement is a message with the action to take.

    >>> @deprecated()
    ... def foo(x):
    ...     return x
    ...
    >>> ret = foo(1)
    DeprecationWarning: foo is deprecated
    >>> ret
    1
    >>>
    >>>
    >>> def newfun(x):
    ...     return 0
    ...
    >>> @deprecated(newfun)
    ... def foo(x):
    ...     return x
    ...
    >>> ret = foo(1)
    DeprecationWarning: foo is deprecated; use newfun instead
    >>> ret
    0
    >>>
    """

    def outer(oldfun):
        def inner(*args, **kwargs):
            msg = "%s is deprecated" % oldfun.__name__
            if replacement:
                if hasattr( replacement, '__call__' ):
                    repl = replacement.__name__
                else:
                    repl = replacement
                msg += "; use %s instead" % (repl)
            term.printDeprecated( '%s' % ( msg ) )
            return oldfun(*args, **kwargs)
        return inner
    return outer


if __name__ == '__main__':

    # --- new function
    def sum_many(*args):
        return sum(args)

    # --- old / deprecated function
    @deprecated(sum_many)
    def sum_couple(a, b):
        return a + b

    print sum_couple(2, 2)
## end of http://code.activestate.com/recipes/577819/ }}}
