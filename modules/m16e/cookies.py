# coding=utf-8
from gluon import current
from m16e import term


def set_cookie( name, value, expires=68400, path='/' ):
    '''
    Sets a cookie on browser
    Args:
        name:
        value:
        expires: if integer parse as seconds, if string the last
            digit must be a letter (d,m,y)
        path:

    Returns:

    '''
    response = current.response
    response.cookies[ name ] = value
    if not isinstance( expires, int ):
        un = expires[ -1 ]
        v = int( expires[ : -1 ] )
        if un == 'd':
            expires = v * 3600 * 24
        elif un == 'm':
            expires = v * 3600 * 24 * 30
        elif un == 'y':
            expires = v * 3600 * 24 * 365
    response.cookies[ name ][ 'expires' ] = expires
    response.cookies[ name ][ 'path' ] = '/'
    response.cookies[ name ][ 'secure' ] = True


def get_cookie( name ):
    request = current.request
#     term.printDebug( 'cookies: %s' % repr( request.cookies ) ) #, prompt_continue=True )
    if request.cookies.has_key( name ):
        return request.cookies[ name ].value
    return None

