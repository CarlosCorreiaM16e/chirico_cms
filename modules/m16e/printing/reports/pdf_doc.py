# coding=utf-8

'''
pdf_metadata
{
    orientation, unit, format,
    font_family, font_style, font_size,
    header: { title: { text, font_family, font_style, font_size, align, line_height },
              sub_title: { text, font_family, font_style, font_size, align, line_height },
              description: { text, font_family, font_style, font_size, align, line_height },
              },
    footer: { height,
              line_height,
              left: { field, text_mask, font_family, font_style, font_size, align },
              center: { field, text_mask, font_family, font_style, font_size, align },
              right: { field, text_mask, font_family, font_style, font_size, align },
              }
    cols: [(name, label, width, align)]
}

# footer.*.fields: app_name | page_no | author_sign | datetime | date



'''
from gluon import THEAD, TR, TH, current, TD, TBODY, TABLE, XML
from gluon.contrib.fpdf import FPDF, HTMLMixin
from gluon.storage import Storage
from m16e import term

COL_NAME_IDX = 0
COL_LABEL_IDX = 1
COL_WIDTH_IDX = 2
COL_ALIGN_IDX = 3

PDF_ORIENTATION_PORTRAIT = 'P'
PDF_ORIENTATION_LANDSCAPE = 'L'

UNIT_MM = 'mm'

PAGE_FORMAT_A4 = 'A4'
PAGE_FORMAT_A4_WIDTH = 210
PAGE_FORMAT_A4_HEIGHT = 297

FONT_FAMILY_ARIAL = 'Arial'
FONT_FAMILY_HELVETICA = 'Helvetica'

FONT_STYLE_BOLD = 'B'
FONT_STYLE_PLAIN = ''

TEXT_ALIGN_LEFT = 'L'
TEXT_ALIGN_RIGHT = 'R'
TEXT_ALIGN_CENTER = 'C'
TEXT_ALIGN_JUSTIFY = 'J'


def parse_font( metadata=Storage(),
                default_data=Storage() ):
    # term.printDebug( 'metadata: %s' % repr( metadata ) )
    if metadata.font_family:
        ffamily = metadata.font_family
    else:
        ffamily = default_data.font_family or FONT_FAMILY_HELVETICA
    if metadata.font_style:
        fstyle = metadata.font_style
    else:
        fstyle = default_data.font_style or FONT_STYLE_PLAIN
    if metadata.font_size:
        fsize = metadata.font_size
    else:
        fsize = default_data.font_size or 12
    return (ffamily, fstyle, fsize)


def get_align_class( align_type ):
    if align_type == TEXT_ALIGN_CENTER:
        return 'text-center'
    if align_type == TEXT_ALIGN_RIGHT:
        return 'text-right'
    if align_type == TEXT_ALIGN_JUSTIFY:
        return 'text-justify'
    return 'text-left'

class ReportFPDF( FPDF, HTMLMixin ):

    def __init__( self,
                  orientation=PDF_ORIENTATION_PORTRAIT,
                  unit=UNIT_MM,
                  format=PAGE_FORMAT_A4,
                  metadata=None ):
        super( ReportFPDF, self ).__init__( orientation=orientation,
                                            unit=unit,
                                            format=format )
        self.metadata = metadata
        self.report_font = parse_font( metadata )
        self.set_font( *self.report_font )


    def header( self ):
        for f in ('title', 'sub_title', 'description'):
            fdata = self.metadata.header.get( f )
            if fdata:
                font = parse_font( fdata, self.metadata )
                self.set_font( *font )
                self.multi_cell(0, h=10, txt=fdata.text,
                                border=0, align=fdata.align)
        self.ln( 10 )


    def footer( self ):
        T = current.T
        request = current.request
        self.set_y( -self.metadata.footer.height )
        term.printDebug('y: %d; x: %d' % (self.get_y(), self.get_x()))
        fdata = self.metadata.footer.get( 'left' )
        if fdata:
            w = (PAGE_FORMAT_A4_WIDTH - 30) / 3
            term.printDebug('w: %d' % w )
            font = parse_font( fdata, self.metadata )
            self.set_font( *font )
            txt = (fdata.text + ' ') * 3
            sw = self.get_string_width( txt )
            term.printDebug('sw: %d' % sw)
            lines = self.multi_cell( w, h=10, txt=txt, border=0, align=fdata.align,
                                     split_only=True )
            term.printDebug( 'lines: %s' % repr( lines ) )
            for idx, l in enumerate( lines ):
                self.set_y( -self.metadata.footer.height + (idx * 10) )
                self.cell( w, h=10, txt=l, align=fdata.align )

        else:
            w = 0
        fdata = self.metadata.footer.get( 'center' )
        font = parse_font( fdata, self.metadata )
        self.set_font( *font )
        txt = T( 'Page %(page_no)s of %(pages)s',
                 dict( page_no=self.page_no(),
                       pages=self.alias_nb_pages() ) )
        self.set_y( -self.metadata.footer.height )
        self.set_x( w )
        self.multi_cell( w, h=10, txt=txt, border=0, align='C' )
        term.printDebug('y: %d; x: %d' % (self.get_y(), self.get_x()))
        fdata = self.metadata.footer.get( 'right' )
        if fdata:
            w = (PAGE_FORMAT_A4_WIDTH - 30) / 3
            font = parse_font( fdata, self.metadata )
            self.set_font( *font )
            self.set_y(-self.metadata.footer.height)
            self.set_x( w * 2 )
            self.multi_cell( w, h=10, txt=fdata.text, border=0, align=fdata.align )
            term.printDebug('y: %d; x: %d' % (self.get_y(), self.get_x()))

class PdfReport( object ):
    def __init__( self ):
        self.metadata = None
        self.data = None

    def set_metadata( self, metadata ):
        term.printDebug( 'metadata: %s' % repr( metadata ) )
        self.metadata = metadata


    def set_data( self, data ):
        self.data = data


    def html_render( self ):
        tr = TR()
        for c in self.metadata.cols:
            tr.append( TH( c[ COL_LABEL_IDX ], _width=str( c[ COL_WIDTH_IDX ] ) + '%' ) )
        head = THEAD( tr, _bgcolor='#A0A0A0' )
        rows = []
        for row in self.data:
            tr = TR()
            for c in self.metadata.cols:
                tr.append( TD( row[ c[ COL_NAME_IDX ] ],
                               _class=get_align_class( c[ COL_ALIGN_IDX ] ) ) )
            rows.append( tr )
        body = TBODY( *rows )
        table = TABLE( *[ head, body ] )
        pdf = ReportFPDF( orientation=self.metadata.orientation,
                          unit=self.metadata.unit,
                          format=self.metadata.format,
                          metadata=self.metadata )
        pdf.add_page()
        pdf.write_html( str( XML( table, sanitize=False ) ) )
        return pdf

