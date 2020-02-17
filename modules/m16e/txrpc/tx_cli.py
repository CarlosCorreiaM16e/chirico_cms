# -*- coding: utf-8 -*-

import fileutils
from m16e import term
from m16e.txrpc.tx_base import TxRPC


class TxRPCCli( TxRPC ):
    suffix = '.request'

    def __init__( self, app_name ):
        super( TxRPCCli, self ).__init__( app_name )


    def write_file( self, file_tag, data ):
        lines = []
        for k in data:
            lines.append( self.compose_line( k, data[ k ] ) )
        lines.append( '' ) # ends with \n
        term.printDebug( 'file_tag: %s; lines:\n%s' % (file_tag, str( lines )) )
        path = self.get_app_folder()
        fileutils.mkdirs( path, throwError=True )
        filename = fileutils.write_tmp_file( '\n'.join( lines ),
                                             suffix=self.suffix,
                                             prefix=file_tag + '-',
                                             dir=path )
        return filename.rsplit( '/', 1 )[1]



