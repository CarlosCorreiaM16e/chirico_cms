# -*- coding: utf-8 -*-
import struct

from gluon.globals import current


def use_bootstrap_select():
    if current.app_config:
        use_it = current.app_config.get( 'ui.bootstrap_select', default=False )
#        term.printDebug( 'use_it: %s' % repr( use_it ) )
#        term.printDebug( 'use_it: %s' % type( use_it ) )
        return use_it
        # return bool( use_it and use_it.lower() not in [ '0', 'no', 'false' ] )

    return False


def conv_hex_2_rgb( hex_str ):
    if hex_str.startswith( '#' ):
        hex_str = hex_str[ 1: ]
    return struct.unpack( 'BBB', hex_str.decode( 'hex' ) )

