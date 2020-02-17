# -*- coding: utf-8 -*-

import xlrd
from gluon import current


class SpreadSheetLoader( object ):
    def __init__( self, filename, db=None ):
        self.filename = filename
        if db:
            self.db = db
        else:
            self.db = current.db
        self.fld_list = None
        self.field_separator = '\t'
        self.delimier = ''


    def add_item_from_row( self, row ):
        raise Exception( 'Not implemented')


    def load_spreadsheet_from_xls( self ):
        wb = xlrd.open_workbook( self.filename )
        ws = wb.sheet_by_index( 0 )
        h_row = ws.row( 0 )
        for row_idx in range( ws.nrows ):
            if row_idx == 0:
                self.fld_list = [ c.value for c in h_row ]
            else:
                row = ws.row( row_idx )
                self.add_item_from_row( row )


    def load_spreadsheet_from_csv( self ):
        row0 = True
        with open( self.filename ) as infile:
            for line in infile:
                if row0:
                    row0 = False
                    self.fld_list = line.split( self.field_separator )
                    continue
                row = line.split( self.field_separator )
                if self.delimier:
                    row = [ r.replace( self.delimier, '' ) for r in row ]
                self.add_item_from_row( row )


    def load_spreadsheet( self ):
        ext = self.filename.rsplit( '.', 1 )[ 1 ].lower()
        if ext in ('xls', 'xlsx'):
            self.load_spreadsheet_from_xls()
        elif ext == 'csv':
            self.load_spreadsheet_from_csv()

