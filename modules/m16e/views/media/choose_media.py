# -*- coding: utf-8 -*-
# this file is released under public domain and you can use without limitations

from cgi import FieldStorage

from m16e.db import db_tables
from gluon import current
from gluon.html import URL, TR, TD, TH
from m16e import term, htmlcommon
from m16e.db import attach_factory
from m16e.db.querydata import QueryData
from m16e.kommon import KDT_INT, KDT_CHAR, KQV_PREFIX, KDT_FILE, ACT_SUBMIT, \
    KDT_BOOLEAN, ACT_NEW_RECORD, ACT_CLEAR, KDT_BLOB_MEDIA, ACT_NEW_MEDIA
from m16e.ktfact import KTF_BUTTONS, KTF_NAME, KTF_TITLE, KTF_ID, KTF_VALUE, \
    KTF_CSS_CLASS, KTF_COL_ORDER, KTF_COLS, KTF_TYPE, KTF_SORTABLE_COLS, \
    KTF_CELL_CLASS, KTF_CELL_LINK, KTF_LINK_C, KTF_LINK_F, \
    KTF_WIDTH, KTF_ARGS_V, KTF_VARS_F, KTF_VARS_V
from m16e.views.plastic_view import BaseListPlasticView


KQV_UPLOAD_FILE = KQV_PREFIX + 'upload_file'
KQV_IS_SITE_IMAGE = KQV_PREFIX + 'is_site_image'

#------------------------------------------------------------------
class MediaChooseView( BaseListPlasticView ):
    controller_name = 'gallery'
    function_name = 'choose_image'

    # accepted_exts = ( 'gif',
    #                   'ico',
    #                   'jpe',
    #                   'jpeg',
    #                   'jpg',
    #                   'pbm',
    #                   'pgm',
    #                   'png',
    #                   'pnm',
    #                   'ppm',
    #                   'tif',
    #                   'tiff' )

    #------------------------------------------------------------------
    def __init__( self, db ):
        super( MediaChooseView, self ).__init__( db,
                                                 order_type=KDT_CHAR,
                                                 order_value='filename' )
        T = current.T
        self.table_model = db_tables.get_table_model( 'attach', db=db )

#         self.append_var( # from survey.k import KQV_SURVEY_ID, fld_type=KDT_INT )
        self.list_title = T( 'Choose media file' )

        self.next_c = None
        self.next_f = None
        self.next_args = None

        self.extra_rows = []
        sql = '''
            select mte.extension 
                from mime_type mt 
                    join mime_type_ext mte on mte.mime_type_id = mt.id 
                where 
                    mt.mt_name like( 'audio/%' ) or 
                    mt.mt_name like( 'video/%' ) 
                order by mte.extension
        '''
        rows = db.executesql( sql )
        self.accepted_exts = [ r[0] for r in rows ]
        self.mt_list = attach_factory.get_media_mime_type_list( db=db )

        self.print_query = True


    def do_process( self ):
        return super( MediaChooseView, self ).do_process()


    def get_inhibit_actions( self ):
        return [ ACT_NEW_RECORD, ACT_CLEAR ]


    def get_query_data( self, orderby=None ):
        # term.printLog( 'self.query_vars: ' + repr( self.query_vars ) )
        qd = super( MediaChooseView, self ).get_query_data( orderby )
        sql = 'mime_type_id in ( %s )' % ', '.join( [ str( mt.id )
                                                      for mt in self.mt_list ] )
        term.printDebug( 'sql: %s' % sql )
        qd.addAnd( QueryData( sql ) )
        # qd.addAnd( QueryData( 'mime_type_id in ( %(mt)s )',
        #                       dict( mt=', '.join( [ str( mt.id ) for mt in self.mt_list ] ) ) ) )
        term.printDebug( repr( qd ) )
        return qd

    #------------------------------------------------------------------
    def get_query_select( self ):
        query = '''
            select
                id,
                attach_type_id,
                path,
                filename,
                attached,
                short_description,
                long_description,
                created_on,
                created_by,
                mime_type_id,
                is_site_image,
                img_width,
                img_height
        '''
        return query

    #------------------------------------------------------------------
    def get_query_from( self ):
        query_form = '''
            from attach
        '''
        return query_form

    #------------------------------------------------------------------
    def get_table_qdata_dict( self, extra_buttons={} ):
        T = current.T
        qdata = { KTF_BUTTONS: [ { KTF_NAME: 'action',
                                   KTF_TITLE: T( 'Submit' ),
                                   KTF_ID: 'bt_submit',
                                   KTF_VALUE: ACT_SUBMIT,
                                   KTF_CSS_CLASS: 'btn btn-primary' },
                                ],
                  KTF_COL_ORDER: [],
                  KTF_COLS: {},
                 }
        self.qdata = qdata
        return self.qdata


    def get_extra_rows( self ):
        T = current.T
        if not self.extra_rows:
            self.extra_rows = []
            inp = htmlcommon.get_input_field( KQV_UPLOAD_FILE,
                                              input_type=KDT_FILE,
                                              input_id=KQV_UPLOAD_FILE )
            self.extra_rows.append( TR( TH( T( 'Add new media' ) ) ) )
            tr = TR( TH( T( 'File to add' ), ': ' ),
                     TD( inp ),
                     TD( htmlcommon.get_button( bt_text=T( 'Add media file' ),
                                                name='action',
                                                value=KQV_UPLOAD_FILE,
                                                css_class='btn btn-success' ) ) )
            self.extra_rows.append( tr )
        return self.extra_rows


    def get_extra_rows_style( self ):
        return 'background-color: #e1e3ff; border: 1px solid #ccb;'


    def get_table_view_dict( self ):
        T = current.T
        tdef = { KTF_COL_ORDER: [ 'id', 'path', 'filename', 'attached' ],
                 KTF_SORTABLE_COLS: [ 'id', 'path', 'filename', 'attached' ],
                 KTF_CELL_CLASS: 'table_border',
                 KTF_COLS: { 'id': { KTF_TITLE: T( 'Id' ), KTF_TYPE: KDT_INT,
                                     KTF_CELL_CLASS: 'table_border w10pct'
                                     },
                             'path': { KTF_TITLE: T( 'Path' ), KTF_TYPE: KDT_CHAR,
                                       KTF_CELL_CLASS: 'table_border w20pct',
                                      },
                             'filename': { KTF_TITLE: T( 'Filename' ),
                                           KTF_TYPE: KDT_CHAR,
                                           KTF_CELL_CLASS: 'table_border w20pct',
                                          },
                             'attached': { KTF_TITLE: T( 'Media' ),
                                           KTF_TYPE: KDT_BLOB_MEDIA,
                                           KTF_WIDTH: 120,
                                           KTF_CELL_LINK: { KTF_LINK_C: self.next_c,
                                                            KTF_LINK_F: self.next_f,
                                                            KTF_ARGS_V: self.next_args,
                                                            KTF_VARS_V: { 'action': ACT_NEW_MEDIA },
                                                            KTF_VARS_F: { 'attach_id': 'id' },
                                                            },
                                           KTF_CELL_CLASS: 'table_border w30pct',
                                          },
                            },
                }
        self.tdef = tdef
        return self.tdef

    #------------------------------------------------------------------
    def parse_request_vars( self, post_vars=None, get_vars=None ):
        T = current.T
        super( MediaChooseView, self ).parse_request_vars( post_vars,
                                                                  get_vars )
        response = current.response
        request = current.request
        db = self.db

        self.next_c = request.vars.next_c
        self.next_f = request.vars.next_f
        self.next_args = request.vars.next_args or []

        term.printLog( 'request.args: ' + repr( request.args ) )
        term.printLog( 'request.vars.keys(): ' + repr( request.vars.keys() ) )
        for rv in request.vars:
            if rv != KQV_UPLOAD_FILE:
                print( '%s: %s' % (rv, request.vars[ rv ] ) )
        new_file = request.vars.get( KQV_UPLOAD_FILE )
        term.printDebug( 'new_file: %s' % repr( new_file ) )
        if new_file is not None and isinstance( new_file, FieldStorage ):
            term.printDebug( 'new_file.filename: %s' % repr( new_file.filename ) )
            ext = new_file.filename.split( '.' )[-1]
            term.printDebug( 'ext: %s' % repr( ext ) )
            if not ext in self.accepted_exts:
                response.flash = T( 'Unsupported extension' )
                return

            mte_model = db_tables.get_table_model( 'mime_type_ext', db=db )
            mt_model = db_tables.get_table_model( 'mime_type', db=db )
            q_sql = (db.mime_type_ext.extension.like( ext ))
            mte = mte_model.select( q_sql ).first()
            term.printDebug( 'mte: %s' % repr( mte ) )
            if not mte:
                response.flash = T( 'Unknown extension' )
                return
            mt = mt_model[ mte.mime_type_id ]
            attach_id = attach_factory.add_attach( attached=new_file,
                                                   path='/',
                                                   filename=new_file.filename )
            if self.next_c:
                url = URL( c=self.next_c,
                           f=self.next_f,
                           args=self.next_args,
                           vars=dict( action=ACT_NEW_MEDIA,
                                      attach_id=attach_id ) )
                term.printDebug( 'url: %s' % str( url ), prompt_continue=True )
                return self.set_result( redirect=url )

