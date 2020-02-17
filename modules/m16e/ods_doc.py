# -*- coding: utf-8 -*-

import sys
import traceback

from m16e.kommon import KDT_CHAR, KDT_INT, KDT_DEC, KDT_PERCENT
from m16e.odslib import odslib


#----------------------------------------------------------------------
class OdsDoc( object ):

    #----------------------------------------------------------------------
    def __init__(self):
        self.doc = odslib.ODS()
        
    #----------------------------------------------------------------------
    def set_cell( self,
                  row,
                  col,
                  value,
                  val_type=KDT_CHAR,
                  row_span=1,
                  col_span=1,
                  font_size=None,
                  font_bold=False,
                  h_align=None,
                  v_align=None ):
#         term.printDebug( 'row: %d, col: %d' % (row, col) )
        for i in range( 6 ):
            try:
                cell = self.doc.content.getCell( col, row )
                if val_type in (KDT_INT, KDT_DEC, KDT_PERCENT):
                    cell.floatValue( value )
                else:
                    cell.stringValue( str( value ) )
                if font_size:
                    cell.setFontSize( "%dpt" % font_size )
                if font_bold:
                    cell.setBold( True )
                if v_align:
                    cell.setAlignVertical( v_align )
                if h_align:
                    cell.setAlignHorizontal( h_align )
                if row_span > 1 or col_span > 1:
                    self.doc.content.mergeCells( col, row, col_span, row_span )
                # if completed successfuly
                break
            except:
                t, v, tb = sys.exc_info()
                traceback.print_exception( t, v, tb )
        
    #----------------------------------------------------------------------
    def save( self, filename ):
        self.doc.save( filename )
        
        
