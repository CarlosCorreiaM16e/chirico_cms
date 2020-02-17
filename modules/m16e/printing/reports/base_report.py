# coding=utf-8

from gluon import current
from gluon.contrib.fpdf import FPDF
from m16e import term
from m16e.kommon import KDT_DEC, KDT_MONEY, KDT_PERCENT


PDF_ORIENTATION_PORTRAIT = 'P'
PDF_ORIENTATION_LANDSCAPE = 'L'

UNIT_MM = 'mm'

PAGE_FORMAT_A4 = 'A4'
PAGE_FORMAT_A4_WIDTH = 210
PAGE_FORMAT_A4_HEIGHT = 297

# FONT_FAMILY_ARIAL = 'Arial'
FONT_FAMILY_HELVETICA = 'Helvetica'

FONT_STYLE_BOLD = 'B'
FONT_STYLE_PLAIN = ''

TEXT_ALIGN_LEFT = 'L'
TEXT_ALIGN_RIGHT = 'R'
TEXT_ALIGN_CENTER = 'C'
TEXT_ALIGN_JUSTIFY = 'J'

POSITION_BOTTOM = 'B'
POSITION_LEFT = 'L'
POSITION_RIGHT = 'R'
POSITION_TOP = 'T'


def strT( txt, symbols={} ):
    T = current.T
    return str( T( txt, symbols=symbols ) )


def convert_2_windows1252( txt ):
    enc_from = 'utf-8'
    try:
        return txt.decode( enc_from ).encode( 'Windows-1252' )
    except UnicodeDecodeError:
        pass
    return txt


class BaseReport( FPDF ):
    def __init__( self,
                  orientation=PDF_ORIENTATION_PORTRAIT,
                  unit=UNIT_MM,
                  format=PAGE_FORMAT_A4,
                  body_font=None,
                  header_font=None,
                  footer_font=None,
                  company_name='',
                  app_name='',
                  margins_ltrb=(20, 10, 10, 10) ):
        if body_font is None:
            body_font = (FONT_FAMILY_HELVETICA, FONT_STYLE_PLAIN, 10)
        if header_font is None:
            header_font = (FONT_FAMILY_HELVETICA, FONT_STYLE_PLAIN, 8)
        if footer_font is None:
            footer_font = (FONT_FAMILY_HELVETICA, FONT_STYLE_PLAIN, 8)
        super( BaseReport, self ).__init__( orientation=orientation,
                                            unit=unit,
                                            format=format )
        self.set_display_mode( 'fullpage' )
        self.body_font = body_font
        self.header_font = header_font
        self.footer_font = footer_font
        self.company_name = company_name
        self.app_name = app_name
        self.margins_ltrb = margins_ltrb

        self.set_font( *self.body_font )
        self.set_margins( margins_ltrb[ 0 ], margins_ltrb[ 1 ], margins_ltrb[ 2 ] )
        self.set_auto_page_break( 1, margins_ltrb[3] )
        self.line_height = 6


    def split_lines( self, w, txt, align ):
        cell_lines = self.multi_cell( w, self.line_height, txt=txt, align=align,
                                      split_only=True )
        return cell_lines


    def format_text( self, value, col_type, decimal_places=2, hide_zeros=False ):
#         term.printDebug( 'value(%s): %s' % (type( value ), repr( value )) )
        if hide_zeros and not value:
            return ''
        if col_type == KDT_DEC:
            txt = '%.*f' % (decimal_places, value)
        elif col_type == KDT_MONEY:
            txt = '%.*f %s' % (decimal_places, value, chr( 128 ))
        elif col_type == KDT_PERCENT:
            # term.printDebug( 'value(%s): %s' % (type( value ), repr( value )) )
            txt = '%.*f' % (decimal_places, value) + ' %'
        else:
            txt = self.normalize_text( str( value ) )
        return txt


    def get_body_width( self ):
        bw = self.fw - self.l_margin - self.r_margin
        return bw


    def get_body_height( self ):
        bh = self.fh - self.t_margin - self.b_margin
        return bh


    def normalize_text( self, txt ):
        # term.printDebug( 'txt (%s): %s' %
        #                  (type( txt ), repr( txt ) ),
        #                  print_trace=True )
        if isinstance( txt, basestring ):
            txt = convert_2_windows1252( txt )
        return super( BaseReport, self ).normalize_text( txt )


    def pdf_render( self, data ):
        self.write_pdf( data )


    def write_pdf( self, data ):
        pass
