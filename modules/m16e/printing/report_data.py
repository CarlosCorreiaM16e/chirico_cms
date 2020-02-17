# coding=utf-8

from gluon.storage import Storage
from m16e import term


class ReportData( object ):

    def __init__( self, report, list_rows ):
        '''
        :param report: instance of BaseListReport
        :param list_rows: array of rows
        '''
        self.report = report
        self.data_rows = []
        for r in list_rows:
            self.data_rows.append( ReportDataRow( self, r ) )


class ReportDataRow( object ):

    def __init__( self, report_data, row ):
        self.report_data = report_data
        self.row_lines = []
        self.tuple = row
        self.build_lines( row )


    def build_lines( self, row ):
        self.row_lines = []
        report = self.report_data.report
        cdef = Storage()
        width = report.get_body_width()
        max_lines = 0
        for col in report.report_col_def:
            w = width * col.col_width / 100.0
            # term.printDebug( 'row[ %s ]: %s' % (col.field_name, repr( row[ col.field_name ] ) ) )
            txt = report.format_text( row[ col.field_name ],
                                      col.field_type,
                                      col.col_dec )
            lines = report.split_lines( w,
                                        txt,
                                        col.align )
            max_lines = max( max_lines, len( lines ) )
            cdef[ col.field_name ] = Storage( col_def=col,
                                              lines=lines )
        for idx in range( 0, max_lines ):
            line = Storage()
            for col in report.report_col_def:
                if len( cdef[ col.field_name ].lines ) > idx:
                    v = cdef[ col.field_name ].lines[ idx ]
                else:
                    v = ''
                line[ col.field_name ] = v
            self.row_lines.append( line )


    def get_no_lines( self ):
        return len( self.row_lines )
