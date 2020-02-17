# -*- coding: utf-8 -*-

import json
from m16e import term
from m16e.kommon import storagize


#------------------------------------------------------------------
class JsonData( object ):
    #------------------------------------------------------------------
    def __init__( self, filename=None, data=None ):
        self.data = None
        if filename:
            self.load( filename )
        if data:
            self.data = json.dumps( data )
            
    #------------------------------------------------------------------
    def load( self, filename ):
        f = open( filename )
        c = f.read()
        f.close()
        self.loads( c )

    #------------------------------------------------------------------
    def loads( self, data ):
        self.data = json.loads( data )

    #------------------------------------------------------------------
    def dump( self, filename, data, sort_keys=False ):
        f = open( filename, 'w' )
        s = self.dumps( data, sort_keys=sort_keys )
        term.printDebug( 's: %s' % s )
        f.write( s + '\n' )
        f.close()
        
    #------------------------------------------------------------------
    def dumps( self, data, sort_keys=False ):
        json_data = json.dumps( data, 
                                sort_keys=sort_keys,
                                indent=4,
                                ensure_ascii=False )
        return json_data
        
    #------------------------------------------------------------------
    def as_dict( self, encoding='utf-8' ):
        #----------------------------------------------------------------------
        def u_to_utf8( value ):
            if isinstance( value, dict ):
                return { u_to_utf8( k ): u_to_utf8( v ) 
                         for k, v in value.iteritems() }
            elif isinstance( value, list ):
                return [ u_to_utf8( v ) for v in value ]
            elif isinstance( value, unicode ):
                return value.encode( 'utf-8' )
            return value
        #----------------------------------------------------------------------
        return storagize( u_to_utf8( self.data ) )
    
