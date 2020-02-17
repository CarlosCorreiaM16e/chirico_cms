# -*- coding: utf-8 -*-

import datetime
import sys
import traceback

from gluon import current
import m16e.term as term

DT = datetime.datetime
DATE = datetime.date

#------------------------------------------------------------------
class is_valid_wday_list( object ):
    def __init__( self,
                  allow_blank=False,
                  error_message='' ):
        self.allow_blank = allow_blank
        self.error_message = error_message

    def __call__( self, value ):
        db = current.db
        T = current.T
        auth = current.auth

        try:
            term.printLog( 'nif: %s' % ( repr( value ) ) )
            valid = False
            blank = not value
            if self.allow_blank and blank:
                return ( value, None )
            if value:
                valid = True
                d_list = sorted( list( value ) )
                last = None
                for d in d_list:
                    if not last:
                        last = d
                    elif last == d:
                        self.error_message = T( 'Day (%s) referred more then once',
                                                d )
                        valid = False
                        break
                    else:
                        i = int( d )
                        if i < 0 or i > 6:
                            self.error_message = T( 'Invalid day (%s)',
                                                    d )
                            valid = False
                            break
                value = ''.join( d_list )

            if not valid and not self.error_message:
                self.error_message = T( 'Unknown error for input: %s', value )

            term.printDebug( 'error: %s' % repr( self.error_message ) )
            return ( value, self.error_message )
        except Exception, err:
            t, v, tb = sys.exc_info()
            traceback.print_exception( t, v, tb )
            term.printLog( 'error: %s' % ( str( err ) ) )
            return ( value, self.error_message )

    def formatter( self, value ):
        return value

