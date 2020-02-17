import inspect
import json
import os
import sys

from gluon import current
from m16e import w2p_logger


# moved to m16e.system.env
# DEV_SERVERS = [ 'zappa' ]

#----------------------------------------------------------------------
class AnsiPrint( object ):
    FG_BLACK = "\033[30m"
    FG_BLUE = "\033[34m"
    FG_GREEN = "\033[32m"
    FG_CYAN = "\033[36m"
    FG_RED = "\033[31m"
    FG_MAGENTA = "\033[35m"
    FG_YELLOW = "\033[33m"
    FG_DARK_GRAY = "\033[1;30m"

    RESET = "\033[0m"

    def __init__( self, color ):
        self.color = color

    #----------------------------------------------------------------------
    def getColoredText( self, text ):
        return self.color + text + self.RESET


def get_formated_error_message( remote_ip, pathname, line_no, msg ):
    err_msg = "%s - *** in %s:%d:\n%s\n" % (remote_ip, pathname, line_no, msg)
    return err_msg

def format_dict( d ):
    return json.dumps( d, indent=4 )


def getTerminalSize():
    rows, columns = os.popen( 'stty size', 'r' ).read().split()
    return ( int( rows ), int( columns ) )

def printLine( text, color = None ):
    if color:
        text = color + text + AnsiPrint.RESET
    print text

def printLog( text, print_trace=False ):
    from m16e.system import env
    if '/download/attach.attached' in env.get_path_info():
        return

    cwd = os.getcwd()
    stack = inspect.stack()[1]
    dir = stack[1]
    if dir.startswith( os.getenv( 'HOME' ) ):
        dir = dir[ len( cwd ) + 1 : ]
    text = get_formated_error_message( current.remote_ip, dir, stack[ 2 ], text )
    if print_trace:
        text += ' -- called by:'
        for st in inspect.stack():
            if 'gluon' in st[1]:
                text += '\n - (...)'
                break
            text += '\n - %s:%d' % ( st[1], st[2] )
    try:
        logger = w2p_logger.get_logger()
        logger.info( text )
    except AttributeError:
        print( text )
#     print text

#----------------------------------------------------------------------
def printError( text, print_trace=False ):
    cwd = os.getcwd()
    stack = inspect.stack()[1]
    dir = stack[1]
    if dir.startswith( os.getenv( 'HOME' ) ):
        dir = dir[ len( cwd ) + 1 : ]
    text = get_formated_error_message( current.remote_ip, dir, stack[ 2 ], text )
    logger = w2p_logger.get_logger()
    if print_trace:
        text += ' -- called by:'
        for st in inspect.stack():
            if 'gluon' in st[1]:
                text += '\n - (...)'
                break
            text += '\n - %s:%d' % ( st[1], st[2] )
    logger.error( text )
#     print text


def printDebug( text,
                print_trace=False,
                prompt_continue=False ):
    from m16e.system import env
    if not env.is_dev_server():
        return
    if '/download/attach.attached' in env.get_path_info():
        return

    cwd = os.getcwd()
    stack = inspect.stack()[1]
    # print( 'DEBUG:\n  stack:' )
    # for st in inspect.stack():
    #     print( 'st: %s' % repr( st[1] ) )
    dir = stack[1]
    if dir.startswith( os.getenv( 'HOME' ) ):
        dir = dir[ len( cwd ) + 1 : ]
    logger = w2p_logger.get_logger()
    text = get_formated_error_message( current.remote_ip, dir, stack[2], text )
    # text += 'server_name: %s' % current.server_name
    if print_trace:
        text += ' -- called by:'
        for st in inspect.stack():
            if 'gluon' in st[1]:
                text += '\n - (...)'
                break
            text += '\n - %s:%d' % ( st[1], st[2] )

    logger.info( text + '\n' )
    # logger.debug( 'prompt_continue: %s, current.server_name: %s' %
    #               (repr( prompt_continue ), repr( current.server_name )) )
    if prompt_continue:
        c = raw_input( 'continue (Y/n)?' )
        if c and c[0] not in 'yY':
            raise Exception( 'aborted by user' )

#     text = "%s*** in %s:%d:\n%s%s" % (
#         AnsiPrint.FG_MAGENTA, dir, stack[2], text, AnsiPrint.RESET )
#     print text

#----------------------------------------------------------------------
def printWarn( text ):
    cwd = os.getcwd()
    stack = inspect.stack()[2]
    dir = stack[1]
    if dir.startswith( os.getenv( 'HOME' ) ):
        dir = dir[ len( cwd ) + 1 : ]
    text = "%s*** in %s:%d:\n%s%s" % (
        AnsiPrint.FG_RED, dir, stack[2], text, AnsiPrint.RESET )
    print text

#----------------------------------------------------------------------
def printDeprecated( text ):
    cwd = os.getcwd()
    stack = inspect.stack()[2]
    dir = stack[1]
    if dir.startswith( os.getenv( 'HOME' ) ):
        dir = dir[ len( cwd ) + 1 : ]
    text = "%s!!! DEPRECATION in %s:%d: %s%s" % (
        AnsiPrint.FG_RED, dir, stack[2], text, AnsiPrint.RESET )
    print text

#----------------------------------------------------------------------
def formatStorage( st, indent = '' ):
    if isinstance( st, dict ):
        text = indent + '{\n'
        indent += '    '
        first = True
        for k in st.keys():
            v = st[k]
#            printLog( 'v:' + repr( v ) )
            if v and repr( v ).startswith( '<' ):
                continue
            if first:
                first = False
            else:
                text += ',\n'
            text += indent + k + ': ' + formatStorage( v, indent )
        text += '\n'
        text += indent + '}\n'
        return text
    else:
        print 'not dict'
    return str( st )

#----------------------------------------------------------------------
def printLogStorage( storage ):
    text = formatStorage( storage )
    stack = inspect.stack()[1]
    text = "*** in %s:%d:\n%s" % (stack[1], stack[2], text)
    print text

#----------------------------------------------------------------------
def printLogDict( d, indent = 0, dictName = '' ):
    cwd = os.getcwd()
    stack = inspect.stack()[1]
    dir = stack[1]
    if dir.startswith( os.getenv( 'HOME' ) ):
        dir = dir[ len( cwd ) + 1 : ]
    text = "*** in %s:%d:" % (dir, stack[2] )
    print text
    print( 'dictName: %s' % dictName )
    printDict( d, indent )

#----------------------------------------------------------------------
def printDict( d, indent = 0 ):
    iStr = '    ' * indent
    kList = d.keys()
    for k in kList:
        print k
        val = d[k]
        if isinstance( val, dict ):
            print '%s%s:' % (iStr, k, )
            printDict( val, indent + 1 )
        else:
            print '%s%s: %s' % (iStr, k, repr( val ))


def printChars( text, color = None ):
    if color:
        text = color + text + AnsiPrint.RESET
    sys.stdout.write( text )
    sys.stdout.flush()


def fg_black( text ):
    return AnsiPrint.FG_BLACK + text + AnsiPrint.RESET


def fg_blue( text ):
    return AnsiPrint.FG_BLUE + text + AnsiPrint.RESET


def fg_green( text ):
    return AnsiPrint.FG_GREEN + text + AnsiPrint.RESET


def fg_magenta( text ):
    return AnsiPrint.FG_MAGENTA + text + AnsiPrint.RESET


def fg_red( text ):
    return AnsiPrint.FG_RED + text + AnsiPrint.RESET


def fg_cyan( text ):
    return AnsiPrint.FG_CYAN + text + AnsiPrint.RESET


def fg_light_blue( text ):
    return AnsiPrint.FG_LIGHT_BLUE + text + AnsiPrint.RESET

