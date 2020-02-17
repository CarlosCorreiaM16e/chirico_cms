# -*- coding: utf-8 -*-

import sys
import traceback

from gluon import current
import m16e.term as term
import m16e.val_multi as vmulti


class is_valid_nif( object ):
    def __init__( self,
                  allowBlank=False,
                  error_message=None ):
        self.allowBlank = allowBlank
        self.error_message = error_message

    def __call__( self, value ):
        db = current.db
        T = current.T
        auth = current.auth

        try:
            # term.printLog( 'nif: %s' % ( repr( value ) ) )
            valid = False
            blank = not value
            if self.allowBlank and blank:
                return ( value, None )
            if value:
                valid = vmulti.controlNIF( value )
            # term.printLog( 'valid: %s' % ( repr( valid ) ) )
            if valid:
                q_sql = (db.auth_user.fiscal_id == value)
                if auth.user:
                    q_sql &= (db.auth_user.id != auth.user.id)
                count = db( q_sql ).count()
                # term.printDebug( 'sql: %s' % str( db._lastsql ) )
                # term.printDebug( 'count: %s' % repr( count ) )
                if db( q_sql ).count() > 0:
                    # term.printDebug( 'sql: %s' % str( db._lastsql ) )
                    self.error_message = T( 'Fiscal ID already in database' )
                    valid = False
                    # term.printDebug( 'error: %s' % repr( self.error_message ) )

            if not valid and not self.error_message:
                self.error_message = T( 'must be a valid NIF format (ex.: 123456789)' )

            # term.printDebug( 'error: %s' % repr( self.error_message ) )
            return ( value, self.error_message )
        except Exception as err:
            t, v, tb = sys.exc_info()
            traceback.print_exception( t, v, tb )
            term.printLog( 'error: %s' % ( str( err ) ) )
            return ( value, self.error_message )

    def formatter( self, value ):
        return value

