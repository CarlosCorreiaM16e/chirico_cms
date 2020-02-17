# coding=utf-8
import math

from gluon import current
from gluon.storage import Storage
from m16e import term
from m16e.kommon import KDT_DEC, DATE, DECIMAL_0
from m16e.printing.report_data import ReportData
from m16e.printing.reports.base_report import BaseReport, POSITION_TOP, PDF_ORIENTATION_PORTRAIT, UNIT_MM, \
    PAGE_FORMAT_A4, FONT_FAMILY_HELVETICA, FONT_STYLE_PLAIN, FONT_STYLE_BOLD, POSITION_BOTTOM, TEXT_ALIGN_RIGHT, \
    PAGE_FORMAT_A4_WIDTH, PAGE_FORMAT_A4_HEIGHT, TEXT_ALIGN_CENTER, strT

HEADER_TEXT_IDX = 0
HEADER_FAMILY_IDX = 1
HEADER_STYLE_IDX = 2
HEADER_SIZE_IDX = 3
HEADER_ALIGN_IDX = 4
HEADER_HEIGHT_IDX = 5

# COL_NAME_IDX = 0
# COL_LABEL_IDX = 1
# COL_TYPE_IDX = 2
# COL_WIDTH_IDX = 3
# COL_DEC_IDX = 4
# COL_ALIGN_IDX = 5


class ListReport( BaseReport ):

    def __init__( self,
                  orientation=PDF_ORIENTATION_PORTRAIT,
                  unit=UNIT_MM,
                  format=PAGE_FORMAT_A4,
                  body_font=None,
                  header_font=None,
                  footer_font=None,
                  company_name='',
                  app_name='',
                  margins_ltrb=(20, 0, 10, 0),
                  body_line_height=10,
                  # body_cols_nlwa=[],
                  report_col_def=[],
                  report_title=(),
                  report_subtitle=(),
                  report_description=(),
                  list_font=None,
                  totalizer=None,
                  groupby=None ):
        self.row_list = None
        if body_font is None:
            body_font = (FONT_FAMILY_HELVETICA, FONT_STYLE_PLAIN, 10)
        if header_font is None:
            header_font = (FONT_FAMILY_HELVETICA, FONT_STYLE_PLAIN, 8)
        if footer_font is None:
            footer_font = (FONT_FAMILY_HELVETICA, FONT_STYLE_PLAIN, 8)
        if list_font is None:
            list_font = (FONT_FAMILY_HELVETICA, FONT_STYLE_PLAIN, 9)
        super( ListReport, self ).__init__( orientation=orientation,
                                            unit=unit,
                                            format=format,
                                            body_font=body_font,
                                            header_font=header_font,
                                            footer_font=footer_font,
                                            company_name=company_name,
                                            app_name=app_name,
                                            margins_ltrb=margins_ltrb )
        term.printDebug('margins: %s' % repr(margins_ltrb))
        self.body_line_height = body_line_height
        self.report_col_def = report_col_def            # ReportColDef(field_name, col_label, field_type, col_width, col_dec, align)
        self.report_title = report_title                # (text, font_family, font_style, font_size, align, line_height)
        self.report_subtitle = report_subtitle          # (text, font_family, font_style, font_size, align, line_height)
        self.report_description = report_description    # (text, font_family, font_style, font_size, align, line_height)
        self.list_font = list_font
        self.totalizer = totalizer  # instance of ListTotalizer
        term.printDebug( 'totalizer: %s' % repr( self.totalizer ) )
        self.groupby = groupby      # ListGroupBy(label, field_name, .write())
        self.need_list_header = True
        self.need_group_header = False
        self.current_line = 0
        self.first_page = True
        self.first_page_in_group = True


    def add_page( self, orientation='' ):
        super( ListReport, self ).add_page( orientation )
        # if self.page_no() == 1:
        if self.report_title:
            self.set_font( *self.report_title[  HEADER_FAMILY_IDX: HEADER_SIZE_IDX ] )
            self.multi_cell( 0,
                             self.report_title[ HEADER_HEIGHT_IDX ],
                             self.report_title[ HEADER_TEXT_IDX ],
                             align=self.report_title[ HEADER_ALIGN_IDX ] )
            if self.report_subtitle:
                self.set_font( *self.report_subtitle[ HEADER_FAMILY_IDX: HEADER_SIZE_IDX ] )
                self.multi_cell( 0,
                                 self.report_subtitle[ HEADER_HEIGHT_IDX ],
                                 self.report_subtitle[ HEADER_TEXT_IDX ],
                                 align=self.report_subtitle[ HEADER_ALIGN_IDX ] )
                self.ln( self.report_subtitle[ HEADER_HEIGHT_IDX ] )
            if self.report_description:
                self.set_font( *self.report_description[ HEADER_FAMILY_IDX: HEADER_SIZE_IDX ] )
                self.multi_cell( 0,
                                 self.report_description[ HEADER_HEIGHT_IDX ],
                                 self.report_description[ HEADER_TEXT_IDX ],
                                 align=self.report_description[ HEADER_ALIGN_IDX ] )
                self.ln( self.report_description[ HEADER_TEXT_IDX ] )
        # term.printDebug( 'add_page: %d' % self.page_no() )
        self.need_list_header = True


    def header( self ):
        # term.printDebug( 'y: %s' % repr( self.y ) )
        self.set_font( *self.header_font )
        w = self.get_body_width() / 2
        self.set_y( self.header_font[2] / 2 )
        h = self.header_font[2] / 1.5
        self.cell( w, h, self.company_name )
        self.cell( w, h, self.app_name, align=TEXT_ALIGN_RIGHT )
        self.line( self.l_margin,
                   self.t_margin,
                   PAGE_FORMAT_A4_WIDTH - self.r_margin,
                   self.t_margin )
        self.ln( self.t_margin )
        # term.printDebug( '[header] y: %s' % repr( self.y ) )


    def footer( self ):
        T = current.T
        self.line( self.l_margin,
                   PAGE_FORMAT_A4_HEIGHT - self.b_margin,
                   PAGE_FORMAT_A4_WIDTH - self.r_margin,
                   PAGE_FORMAT_A4_HEIGHT - self.b_margin )
        # term.printDebug( 'x1: %d; y1: %d; x2: %d; y2: %d'%
        #                  (self.l_margin,
        #                   PAGE_FORMAT_A4_HEIGHT - self.b_margin,
        #                   PAGE_FORMAT_A4_WIDTH - self.r_margin,
        #                   PAGE_FORMAT_A4_HEIGHT - self.b_margin))
        self.set_y( -self.b_margin )
        w = self.get_body_width() / 3
        h = self.footer_font[ 2 ] / 1.5
        # term.printDebug('w: %d' % w )
        self.set_font( *self.footer_font )
        # term.printDebug( 'w: %s; page_break_trigger: %s' %
        #                  (str( w ), repr( self.page_break_trigger )) )
        # term.printDebug('y: %d; x: %d' % (self.y, self.x), prompt_continue=True)
        self.cell( w, h=h, txt='http://memoriapersistente.pt' )
        txt = strT( 'Page %(page_no)s of %(pages)s',
                    dict( page_no=self.page_no(),
                          pages=self.alias_nb_pages() ) )
        self.cell( w, h=h, txt=txt, align=TEXT_ALIGN_CENTER )
        self.cell( w, h=h, txt=DATE.today().isoformat(), align=TEXT_ALIGN_RIGHT )
        # term.printDebug( '[footer] y: %s' % repr( self.y ) )


    def write_group_footer_totalizers( self ):
        if not self.groupby or not self.groupby.totalizers:
            return
        T = current.T
        self.ln( 1 )
        self.set_font( self.list_font[0],
                       FONT_STYLE_BOLD,
                       self.list_font[2] )
        # term.printDebug( 'totals: %s' % repr( totals ), prompt_continue=True )
        for idx, col in enumerate( self.report_col_def ):
            if idx == 0:
                txt = T( self.groupby.totals_label )
            elif col.field_name in self.groupby.totalizers.keys():
                txt = self.format_text( self.groupby.totalizers[ col.field_name ],
                                        col.field_type,
                                        col.col_dec )
            else:
                txt = ''
            w = self.get_body_width() * col.col_width / 100
            self.cell( w,
                       h=self.body_line_height,
                       txt=txt,
                       border=POSITION_TOP,
                       align=col.align )
        self.ln( self.body_line_height )


    def write_report_header( self ):
        term.printDebug( 'y: %s' % repr( self.y ) )
        self.ln( 1 )
        self.set_font( self.list_font[0],
                       FONT_STYLE_BOLD,
                       self.list_font[2] )
        for col in self.report_col_def:
            w = self.get_body_width() * col.col_width / 100
            if col.field_type == KDT_DEC:
                txt = '%.*f' % (col.col_dec, col.col_label )
            else:
                txt = strT( col.col_label )

            self.cell( w,
                       h=self.body_line_height,
                       txt=self.normalize_text( txt ),
                       border=POSITION_BOTTOM,
                       align=col.align )
        self.need_list_header = False


    def write_header_totalizers( self ):
        T = current.T
        totals = self.totalizer.totalize_rows( self.current_line, self.row_list, include_last=False )
        # term.printDebug( 'self.current_line: %d; totals: %s' % (self.current_line, repr( totals ) ), prompt_continue=True )
        show = False
        for f in totals:
            if totals[f] != DECIMAL_0:
                show = True
                break
        # term.printDebug( 'self.current_line: %d; show: %s' % (self.current_line, repr( show ) ) )
        if not show:
            return

        self.ln( 1 )
        self.set_font( self.list_font[0],
                       FONT_STYLE_BOLD,
                       self.list_font[2] )
        for idx, col in enumerate( self.report_col_def ):
            if idx == 0:
                txt = T( 'Transport' )
            elif col.field_name in self.totalizer.cols:
                txt = self.format_text( totals[ col.field_name ],
                                        col.field_type,
                                        col.col_dec,
                                        hide_zeros=False )
            else:
                txt = ''
            w = self.get_body_width() * col.col_width / 100
            self.cell( w,
                       h=self.body_line_height,
                       txt=txt,
                       border=POSITION_BOTTOM,
                       align=col.align )
        self.ln( self.body_line_height )


    def write_footer_totalizers( self ):
        T = current.T
        self.ln( 1 )
        self.set_font( self.list_font[0],
                       FONT_STYLE_BOLD,
                       self.list_font[2] )

        totals = self.totalizer.totalize_rows( self.current_line, self.row_list )
        # totals = self.totalizer.totalize_footer( self.current_line )
        # term.printDebug( 'totals: %s' % repr( totals ), print_trace=True, prompt_continue=True )
        for idx, col in enumerate( self.report_col_def ):
            if idx == 0:
                txt = T( 'Totals' )
            elif col.field_name in self.totalizer.cols:
                txt = self.format_text( totals[ col.field_name ],
                                        col.field_type,
                                        col.col_dec )
            else:
                txt = ''
            w = self.get_body_width() * col.col_width / 100
            self.cell( w,
                       h=self.body_line_height,
                       txt=txt,
                       border=POSITION_TOP,
                       align=col.align )
        self.ln( self.body_line_height )


    def check_group( self, row ):
        if self.groupby:
            # term.printDebug( 'page: %d; current_group: %s' % (self.page_no(), repr( self.groupby.current_group ) ) )
            # term.printDebug( '; '.join( [ '%s: %s' % (f, row[f]) for f in row ] ) )
            if not self.groupby.current_group or not self.groupby.is_row_in_group( row ):
                self.groupby.set_current_group( row )
                self.first_page_in_group = True
                self.need_group_header = True
                self.need_list_header = True
                # term.printDebug( 'need_group_header: %s' % repr( self.need_group_header ), prompt_continue=True )
                # term.printDebug( '; '.join( [ '%s: %s' % (f, row[f]) for f in row ] ), prompt_continue=True )


    def write_group_header( self ):
        if self.groupby:
            self.ln( 1 )
            w = self.get_body_width() / (self.groupby.groups_per_line * 2.0)
            # term.printDebug( 'current_group: %s' % repr( self.groupby.current_group ) )
            for idx, gb in enumerate( self.groupby.field_order ):
                # term.printDebug( 'idx: %d, gb: %s' % (idx, repr( gb )) )
                remain = idx % self.groupby.groups_per_line
                if idx > 0 and remain == 0:
                    # term.printDebug( 'remain: %s; h: %s; y: %s; gb: %s' %
                    #                  (repr( remain ), repr( self.body_line_height ),
                    #                   repr( self.get_y()), repr( gb )) )
                    self.ln( self.body_line_height + 1 )
                self.set_font( self.header_font[ 0 ],
                               FONT_STYLE_BOLD,
                               self.groupby.font_size or self.header_font[ 2 ] )
                self.cell( w,
                           self.body_line_height,
                           strT( self.groupby.labels[ gb ] ) + ':' )
                # self.set_font( self.header_font[0],
                #                self.header_font[1],
                #                self.groupby.font_size or self.header_font[ 2 ] )
                self.cell( w,
                           self.body_line_height,
                           self.groupby.current_group[ gb ] )
                # remain = idx % self.groupby.groups_per_line

                # term.printDebug( 'remain: %s; y: %s; x: %s' %
                #                  (repr( remain ), repr( self.get_y() ), repr( self.get_x() )),
                #                  prompt_continue=True )
            self.need_group_header = False


    def write_report_line( self, row ):
        '''
        :param row:  ReportDataRow instance
        '''
        # term.printDebug( 'doc_id: %s; y: %s' %
        #                  (repr( row[ 'doc_id' ] ), repr( self.y ) ) )
        # term.printDebug( 'totalizer: %s' % repr( self.totalizer ) )
        self.check_group( row.tuple )
        may_append_line = self.may_append_report_line( row )
        # term.printDebug( 'may_append_line: %s' % repr( may_append_line ) )
        if not may_append_line or self.need_list_header or self.need_group_header:
            # term.printDebug( '\n  may_append_line: %s\n  need_list_header: %s\n  need_group_header: %s'
            #                  % (repr( may_append_line ), self.need_list_header, self.need_group_header) )
            # term.printDebug( 'self.totalizer: %s' % repr( self.totalizer ), prompt_continue=True )
            # if self.need_list_header or self.need_group_header:
                # term.printDebug( 'page: %d' % self.page, prompt_continue=True )
            if self.first_page:
                self.first_page = False
            else:
                if self.totalizer:
                    self.write_footer_totalizers()
                self.write_group_footer_totalizers()
                self.add_page()
            if self.first_page_in_group:
                self.first_page_in_group = False
                if self.groupby:
                    self.groupby.reset_totalizers()

            if self.groupby:
                self.write_group_header()
                self.ln( self.body_line_height )

            self.write_report_header()
            # term.printDebug( 'self.body_line_height: %s' % repr( self.body_line_height ) )
            self.ln( self.body_line_height )
            if self.totalizer:
                self.write_header_totalizers()

        # term.printDebug( 'doc: %s' % repr( row ) )
        # term.printDebug( 'body_width: %s' % repr( self.get_body_width() ) )
        # term.printDebug( 'page_width: %s; t_margin: %s; l_margin: %s; r_margin: %s' %
        #                  (repr( self.fw ), repr( self.t_margin ), repr( self.l_margin ), repr( self.r_margin )),
        #                  prompt_continue=True )
        self.set_font( *self.list_font )
        bw = self.get_body_width()
        for rline in row.row_lines:
            for col in self.report_col_def:
                w = bw * col.col_width / 100
                # term.printDebug( 'field: %s; value: %s; type: %s; dec: %s' %
                #                  (repr( col.field_name ),
                #                   repr( row[ col.field_name ] ),
                #                   repr( col.field_type ),
                #                   repr( col.col_dec )) )
                self.cell( w,
                           h=self.body_line_height,
                           txt=rline[ col.field_name ],
                           align=col.align )
            self.ln( self.body_line_height )
        # if self.totalizer:
        #     self.totalizer.totalize_row( row.tuple )
        if self.groupby and self.groupby.totalizers:
            self.groupby.totalize_groups( row.tuple )
        self.current_line += 1


    def may_append_report_line( self, row ):
        '''
        :param row:  ReportDataRow instance
        '''
        footer_top = self.fh - self.b_margin
        # term.printDebug( 'footer_top: %s' % repr( footer_top ) )
        if self.totalizer:
            footer_top -= self.body_line_height
        y = self.get_y()
        # term.printDebug( 'y: %s; footer_top: %s' % ( str( y ), repr( footer_top ) ) )
        factor = row.get_no_lines() + 1
        if self.groupby:
            factor += math.ceil( len( self.groupby.field_order ) / self.groupby.groups_per_line )
            # if self.groupby.totalizers:
            #     factor += 2
        new_y = y + (self.body_line_height * factor)
        if new_y < footer_top:
            return True
        # term.printDebug( 'new_y: %s; footer_top: %s; body_line_height: %d' %
        #                  (str( new_y ), repr( footer_top ), self.body_line_height) )
        return False


    def write_pdf( self, row_list ):
        term.printDebug( 'len( row_list ): %d' % len( row_list ) )
        self.row_list = row_list
        report_data = ReportData( self, row_list )
        self.add_page()
        for row in report_data.data_rows:
            self.write_report_line( row )
        # row_len = len( row_list )
        # for row_no in range( row_len ):
        #     self.write_report_line( row_list[ row_no ] )
        # term.printDebug( 'totalizer: %s' % repr( self.totalizer ) )
        if self.totalizer:
            self.write_footer_totalizers()
        if self.groupby and self.groupby.totalizers:
            self.write_group_footer_totalizers()


