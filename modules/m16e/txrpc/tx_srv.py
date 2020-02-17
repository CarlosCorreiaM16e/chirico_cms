# -*- coding: utf-8 -*-

import fileutils
from m16e import term
from m16e.txrpc.tx_base import TxRPC


class TxRPCSrv( TxRPC ):
    suffix = '.response'

    def __init__( self, app_name ):
        super( TxRPCSrv, self ).__init__( app_name )


    def get_response_filename( self, filename ):
        outpath = filename.rsplit( '.', 1 )[0]
        return outpath


    def write_file( self, filename, data=None, lines=None ):
        term.printDebug( 'data: %s' % repr( data ) )
        if lines is None:
            lines = []
            for k in data:
                lines.append( self.compose_line( k, data[ k ] ) )
        term.printDebug( 'filename: %s; lines:\n%s' % (filename, str( lines )) )
        filename = self.get_response_filename( filename )
        fileutils.write_file( filename, '\n'.join( lines ) + '\n' )
        term.printDebug( 'filename: %s' % filename )
        return filename


