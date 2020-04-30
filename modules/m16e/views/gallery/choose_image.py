# -*- coding: utf-8 -*-
# this file is released under public domain and you can use without limitations
import os
from cgi import FieldStorage

from chirico.app import app_factory
from m16e.db import db_tables
from gluon import current
from gluon.html import URL, TR, TD, TH
from m16e import term, htmlcommon
from m16e.db import attach_factory
from m16e.db.querydata import QueryData
from m16e.kommon import KDT_INT, KDT_CHAR, KDT_BLOB_IMG, KQV_PREFIX, KDT_FILE, ACT_NEW_IMAGE, ACT_SUBMIT, \
    KDT_BOOLEAN, ACT_NEW_RECORD, ACT_CLEAR, storagize, KQV_UPLOAD_FILE, KQV_PAGE_SIZE, KQV_BLOCK_SIZE, KQV_THUMB_SIZE, \
    KQV_IS_SITE_IMAGE
from m16e.ktfact import KTF_BUTTONS, KTF_NAME, KTF_TITLE, KTF_ID, KTF_VALUE, \
    KTF_CSS_CLASS, KTF_COL_ORDER, KTF_COLS, KTF_TYPE, KTF_SORTABLE_COLS, KTF_CELL_CLASS, KTF_CELL_LINK, KTF_LINK_C, \
    KTF_LINK_F, \
    KTF_WIDTH, KTF_ARGS_V, KTF_VARS_F, KTF_VARS_V, KTF_ARGS, KTF_TARGET
from m16e.views.plastic_view import BaseListPlasticView


class GalleryChooseImageView( BaseListPlasticView ):
    controller_name = 'gallery'
    function_name = 'choose_image'

    accepted_exts = ( 'gif',
                      'ico',
                      'jpe',
                      'jpeg',
                      'jpg',
                      'pbm',
                      'pgm',
                      'png',
                      'pnm',
                      'ppm',
                      'tif',
                      'tiff' )


    def __init__( self, db ):
        super( GalleryChooseImageView, self ).__init__( db,
                                                        order_type=KDT_CHAR,
                                                        order_value='filename' )
        T = current.T
        self.table_model = db_tables.get_table_model( 'attach', db=db )

#         self.append_var( # from survey.k import KQV_SURVEY_ID, fld_type=KDT_INT )
        self.append_var( KQV_IS_SITE_IMAGE, fld_type=KDT_BOOLEAN )

        self.list_title = T( 'Choose image' )

        self.target = None

        self.extra_rows = []


    def do_process( self ):
        return super( GalleryChooseImageView, self ).do_process()


    def get_inhibit_actions( self ):
        return [ ACT_NEW_RECORD, ACT_CLEAR ]


    def get_extra_rows( self ):
        T = current.T
        db = self.db
        if not self.extra_rows:
            self.extra_rows = []
            inp = htmlcommon.get_input_field( KQV_UPLOAD_FILE,
                                              input_type=KDT_FILE,
                                              input_id=KQV_UPLOAD_FILE )
            self.extra_rows.append( TR( TH( T( 'Add new image' ) ) ) )
            tr = TR( TH( T( 'Image to add' ), ': ' ),
                     TD( inp ),
                     TD( htmlcommon.get_button( bt_text=T( 'Add image' ),
                                                name='action',
                                                value=KQV_UPLOAD_FILE,
                                                css_class='btn btn-success text-right' ) ) )
            self.extra_rows.append( tr )
            tr = TR( TD( T( 'Large size' ), ': ',
                         htmlcommon.get_checkbox( KQV_PAGE_SIZE, input_id=KQV_PAGE_SIZE ) ),
                     TD( T( 'Medium size' ), ': ',
                         htmlcommon.get_checkbox( KQV_BLOCK_SIZE, input_id=KQV_BLOCK_SIZE ) ),
                     TH( T( 'Small size' ), ': ',
                         htmlcommon.get_checkbox( KQV_THUMB_SIZE, input_id=KQV_THUMB_SIZE ) ) )
            self.extra_rows.append( tr )
        return self.extra_rows


    def get_extra_rows_style( self ):
        return 'background-color: #e1e3ff; border: 1px solid #ccb;'



    def get_query_data( self, orderby=None ):
        term.printLog( 'self.query_vars: ' + repr( self.query_vars ) )
        qd = super( GalleryChooseImageView, self ).get_query_data( orderby )

        qd.addAnd( QueryData( '''at.meta_name in ( 'company-logo', 'images', 'webshop' )''' ) )

        term.printDebug( repr( qd ) )
        return qd


    def get_query_select( self ):
        query = '''
            select
                a.id as a_id,
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


    def get_query_from( self ):
        query_form = '''
            from attach a
                join attach_type at on at.id = a.attach_type_id
        '''
        return query_form


    def get_table_qdata_dict( self, extra_buttons={} ):
        T = current.T
        qdata = { KTF_BUTTONS: [ { KTF_NAME: 'action',
                                   KTF_TITLE: T( 'Submit' ),
                                   KTF_ID: 'bt_submit',
                                   KTF_VALUE: ACT_SUBMIT,
                                   KTF_CSS_CLASS: 'btn btn-primary' },
                                ],
                  KTF_COL_ORDER: [ KQV_IS_SITE_IMAGE ],
                  KTF_COLS: { KQV_IS_SITE_IMAGE: { KTF_TITLE: T( 'Site image' ),
                                                   KTF_TYPE: KDT_BOOLEAN },
                             },
                 }
        self.qdata = qdata
        return self.qdata


    def get_record_list( self, qd=None, alias=None, print_query=None, force_refresh=False ):
        rows = super( GalleryChooseImageView, self ).get_record_list( qd=qd,
                                                                      alias=alias,
                                                                      print_query=print_query,
                                                                      force_refresh=force_refresh )
        for r in rows:
            r.size = '%dx%d' % (r.img_width, r.img_height)
        return self.list_rows


    def get_table_view_dict( self ):
        T = current.T
        return_link = { KTF_LINK_C: self.next_c,
                        KTF_LINK_F: self.next_f,
                        KTF_ARGS_V: self.next_args,
                        KTF_VARS_V: { 'action': ACT_NEW_IMAGE },
                        KTF_VARS_F: { 'attach_id': 'a_id' },
                        }
        if self.target:
            return_link[ KTF_VARS_V ][ KTF_TARGET ] = self.target
        tdef = { KTF_COL_ORDER: [ 'a_id', 'path', 'filename', 'size', 'attached' ],
                 KTF_SORTABLE_COLS: [ 'a_id', 'path', 'filename' ],
                 KTF_CELL_CLASS: 'table_border',
                 KTF_COLS: { 'a_id': { KTF_TITLE: T( 'Id' ), KTF_TYPE: KDT_INT,
                                       KTF_CELL_CLASS: 'table_border w10pct',
                                       KTF_CELL_LINK: { KTF_LINK_C: self.controller_name,
                                                        KTF_LINK_F: 'edit',
                                                        KTF_ARGS: [ 'a_id' ] }
                                       },
                             'path': { KTF_TITLE: T( 'Path' ), KTF_TYPE: KDT_CHAR,
                                       KTF_CELL_CLASS: 'table_border w20pct',
                                      },
                             'filename': { KTF_TITLE: T( 'Filename' ),
                                           KTF_TYPE: KDT_CHAR,
                                           KTF_CELL_CLASS: 'table_border w20pct',
                                          },
                             'size': { KTF_TITLE: T( 'Size' ), KTF_TYPE: KDT_CHAR,
                                       KTF_CELL_CLASS: 'table_border w20pct',
                                      },
                             'attached': { KTF_TITLE: T( 'Image' ),
                                           KTF_TYPE: KDT_BLOB_IMG,
                                           KTF_WIDTH: 120,
                                           KTF_CELL_LINK: return_link,
                                           KTF_CELL_CLASS: 'table_border w30pct img_link',
                                          },
                            },
                }
        self.tdef = storagize( tdef )
        return self.tdef


    def parse_request_vars( self, post_vars=None, get_vars=None ):
        T = current.T
        super( GalleryChooseImageView, self ).parse_request_vars( post_vars,
                                                                  get_vars )
        response = current.response
        request = current.request
        db = self.db

        self.next_c = request.vars.next_c
        self.next_f = request.vars.next_f
        self.next_args = request.vars.next_args or []
        self.target = request.args( 0 )

        term.printLog( 'request.args: ' + repr( request.args ) )
        term.printLog( 'request.vars.keys(): ' + repr( request.vars.keys() ) )
        for rv in request.vars:
            if rv != KQV_UPLOAD_FILE:
                print( '%s: %s' % (rv, request.vars[ rv ] ) )
        new_image = request.vars.get( KQV_UPLOAD_FILE )
        if not new_image:
            return self.set_result( message=T( 'No image supplied' ) )
        term.printDebug( 'new_image: %s' % repr( new_image ) )
        term.printDebug( 'is FieldStorage: %s' %
                         str( isinstance( new_image, FieldStorage ) ) )
        if new_image is not None and isinstance( new_image, FieldStorage ):
            term.printDebug( 'new_image.filename: %s' % repr( new_image.filename ) )
            ext = new_image.filename.split( '.' )[-1]
            term.printDebug( 'ext: %s' % repr( ext ) )
            if not ext in self.accepted_exts:
                return self.set_result( message=T( 'Unsupported extension' ) )

            mte_model = db_tables.get_table_model( 'mime_type_ext', db=db )
            mt_model = db_tables.get_table_model( 'mime_type', db=db )
            a_model = db_tables.get_table_model( 'attach', db=db )
            q_sql = (db.mime_type_ext.extension.like( ext ))
            mte = mte_model.select( q_sql ).first()
            term.printDebug( 'mte: %s' % repr( mte ) )
            if not mte:
                return self.set_result( message=T( 'Unknown extension' ) )
            page_size = request.vars.get( KQV_PAGE_SIZE )
            block_size = request.vars.get( KQV_BLOCK_SIZE )
            thumb_size = request.vars.get( KQV_THUMB_SIZE )

            mt = mt_model[ mte.mime_type_id ]
            ac = app_factory.get_app_config_data( db=db )
            attach_id = attach_factory.add_attach( attached=new_image,
                                                   path='/',
                                                   filename=new_image.filename )
            attach = a_model[ attach_id ]
            if page_size:
                path = attach_factory.get_path( attach, db=db )
                filename = os.path.join( path,
                                         attach.filename )
                attach_factory.image_dump( attach_id, filename=filename, width=ac[ attach_factory.IMG_SIZE_PAGE ], db=db )
            if block_size:
                path = attach_factory.get_path( attach, db=db )
                filename = os.path.join( path,
                                         attach.filename )
                attach_factory.image_dump( attach_id, filename=filename, width=ac[ attach_factory.IMG_SIZE_BLOCK ], db=db )
            if thumb_size:
                path = attach_factory.get_path( attach, db=db )
                filename = os.path.join( path,
                                         attach.filename )
                attach_factory.image_dump( attach_id, filename=filename, width=ac[ attach_factory.IMG_SIZE_THUMB ], db=db )
            if self.next_c:
                data = dict( action=ACT_NEW_IMAGE,
                             attach_id=attach_id )
                if self.target:
                    data[ KTF_TARGET ] = self.target
                url = URL( c=self.next_c,
                           f=self.next_f,
                           args=self.next_args,
                           vars=data )
                return self.set_result( redirect=url )

