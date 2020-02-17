# -*- coding: utf-8 -*-

import sys
import traceback

from gluon import current
import m16e.term as term


class is_valid_zip( object ):

    def __init__( self,
                  allowBlank=False,
                  error_message=None ):
        self.allowBlank = allowBlank
        self.error_message = error_message


    def __call__( self, value ):
        return self.validate( value )


    def formatter( self, value ):
        return value


    def get_county_zip_code( self, value ):
        db = current.db
        T = current.T
        from m16e.db import db_tables
        czc_model = db_tables.get_table_model( 'county_zip_code', db=db )
        parts = value.split( '-' )
        if len( parts ) < 2:
            return None
        p1 = parts[0].strip()
        p2 = parts[1].strip()
        if len( p1 ) == 4 and len( p2 ) == 3:
            q_sql = (db.county_zip_code.zip_part_1 == p1)
            q_sql &= (db.county_zip_code.zip_part_2 == p2)
            czc = czc_model.select( q_sql ).first()
            return czc
        return None


    def validate( self, value ):
        db = current.db
        T = current.T

        try:
#             term.printLog( 'zip: %s' % ( repr( value ) ) )
            valid = False
            blank = not value
            if self.allowBlank and blank:
                return ( value, None )
            if value:
                czc = self.get_county_zip_code( value )
                if czc:
                    valid = True

#             term.printLog( 'valid: %s' % ( repr( valid ) ) )
            if valid:
                msg = None
            else:
                msg = self.error_message
                if not msg:
                    msg = T( 'must be a valid zip code (ex.: 1000-001)' )

#             term.printDebug( 'msg: %s' % repr( msg ) )
            return ( value, msg )
        except Exception, err:
            t, v, tb = sys.exc_info()
            traceback.print_exception( t, v, tb )
            term.printLog( 'error: %s' % ( str( err ) ) )
            return ( value, self.error_message )
