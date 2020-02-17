# coding=utf-8

from m16e.kommon import KDT_CHAR
from m16e.printing.reports.base_report import TEXT_ALIGN_LEFT


class ReportColDef( object ):

    def __init__( self,
                  field_name,
                  col_label=None,
                  field_type=KDT_CHAR,
                  col_width=100,
                  col_dec=2,
                  align=TEXT_ALIGN_LEFT ):
        self.field_name = field_name
        self.col_label = col_label
        self.field_type = field_type
        self.col_width = col_width
        self.col_dec = col_dec
        self.align = align

