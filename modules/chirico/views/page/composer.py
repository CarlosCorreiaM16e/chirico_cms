# -*- coding: utf-8 -*-
# this file is released under public domain and you can use without limitations
from app import db_sets
from chirico.app import app_factory
from chirico.db import block_factory
from chirico.k import ARCHIVE_CONTROLLER, ARCHIVE_FUNCTION, IMG_SIZE_BLOCK, IMG_SIZE_PAGE, IMG_SIZE_THUMB
from gluon import current, H4, SQLFORM, IS_NOT_EMPTY, IMG, SCRIPT, IS_NOT_IN_DB
from gluon.html import DIV, H5, URL
from gluon.storage import Storage

from m16e.db import db_tables, attach_factory
from m16e import term, htmlcommon, markmin_factory
from m16e.files import fileutils
from m16e.kommon import KDT_INT, KDT_CHAR, KDT_TIMESTAMP, DT, ACT_NEW_IMAGE
from m16e.ktfact import KTF_ACTION
from m16e.user_factory import is_in_group
from m16e.views.edit_base_view import BaseFormView

ACT_NEW_MAIN_BLOCK = 'new_main_block'
ACT_NEW_SIDE_BLOCK = 'new_side_block'


class PageComposerView( BaseFormView ):
    controller_name = 'page'
    function_name = 'composer'


    def __init__( self, db ):
        super( PageComposerView, self ).__init__( db )
        self.table_model = db_tables.get_table_model( 'page', db=db )
        # self.page = None
        self.b_list = []
        self.textarea_rows = 16


    def fetch_record( self, fetch_id=False ):
        super( PageComposerView, self ).fetch_record( fetch_id )
        self.b_list = block_factory.get_page_blocks( page_id=self.record_id, db=self.db )
        return self.record


    def append_image( self ):
        request = current.request
        T = current.T
        auth = current.auth
        attach_id = int( request.vars.attach_id )
        block_id = int( request.args( 1 ) )
        target = request.vars.target
        size = request.vars.size
        db = self.db
        a_model = db_tables.get_table_model( 'attach', db=db )
        attach = a_model[ attach_id ]
        aid = None
        if size != db_sets.IMG_SIZE_ORIGINAL:
            ac = app_factory.get_app_config_data( db=db )
            isizes = Storage( { db_sets.IMG_SIZE_ORIGINAL: ac[ IMG_SIZE_PAGE ],
                                db_sets.IMG_SIZE_MEDIUM: ac[ IMG_SIZE_BLOCK ],
                                db_sets.IMG_SIZE_SMALL: ac[ IMG_SIZE_THUMB ] } )
            resize_options = attach_factory.get_resize_options( attach, isizes )
            if size in resize_options:
                w = isizes[ size ]
                aid = attach_factory.get_child_by_width( attach_id, w, db=db )
                if not aid:
                    aid = attach_factory.copy_image( auth.user.id,
                                                     attach_id,
                                                     new_width=w,
                                                     insert_dim_in_name=True,
                                                     dump_to_static=True )
                attach = a_model[ aid ]
        else:
            aid = attach_id

        if not attach_factory.is_file_in_static( aid, db=db ):
            upd = dict( filename=fileutils.filename_sanitize( attach.filename ) )
            a_model.update_by_id( aid, upd )
            attach_factory.file_dump_to_static( aid, db=db )

        b_model = db_tables.get_table_model( 'block', db=db )
        # attach = a_model[ attach_id ]
        b = b_model[ block_id ]
        if b.body_markup == db_sets.MARKUP_MARKMIN:
            img = markmin_factory.mk_wt_image( aid,
                                               align='center',
                                               width=attach.img_width,
                                               caption=attach.short_description,
                                               db=db )
        else:
            img = IMG( _src=attach_factory.get_url( aid, db=db ) ).xml()
        b_model.update_by_id( block_id,
                              { target: b[ target ] + '\n' + img + '\n' } )
        return self.set_result( redirect=URL( c=self.controller_name,
                                              f=self.function_name,
                                              args=[ self.record_id ] ),
                                message=T( 'Image added' ) )


    def process_pre_validation_actions( self ):
        super( PageComposerView, self ).process_pre_validation_actions()
        # request = current.request
        # T = current.T
        if self.action == ACT_NEW_IMAGE:
            return self.append_image()


    def get_exclude_fields( self ):
        self.exclude_fields = [ 'tagname',
                                'colspan',
                                'rowspan',
                                'parent_page_id',
                                'menu_order',
                                'last_modified_by',
                                'is_news',
                                'page_timestamp',
                                'aside_position',
                                'aside_title',
                                'main_panel_cols',
                                'aside_panel_cols',
                                'title_en',
                                'aside_title_en',
                                'hide' ]
        return self.exclude_fields


    # def get_form_fields( self ):
    #     super( PageComposerView, self ).get_form_fields()
    #     # db = self.db
    #     # self.form_fields.append( Field( 'page_id', type='integer', writable=False,
    #     #                                 default=self.record.id if self.record else '' ) )
    #     # self.form_fields.append( Field( 'name', type='string',
    #     #                                 requires=[ IS_NOT_EMPTY(),
    #     #                                            IS_NOT_IN_DB( db, 'page.name') ],
    #     #                                 default=self.record.name if self.record else '' ) )
    #     # self.form_fields.append( Field( 'title', type='string',
    #     #                                 requires=[ IS_NOT_EMPTY(),
    #     #                                            IS_NOT_IN_DB( db, 'page.title') ],
    #     #                                 default=self.record.title if self.record else '' ) )
    #     # for b in self.b_list:
    #     #     self.form_fields.append( Field( 'body_%d' % b.id, 'text', notnull='True',
    #     #                                     default=b.body ) )
    #     # self.form_fields.append( Field( 'body_0', 'text', notnull='True' ) )
    #     return self.form_fields


    # def get_form( self,
    #               form_fields=None,
    #               form_validators=None,
    #               deletable=None,
    #               textarea_rows=None,
    #               readonly_fields=None,
    #               exclude_fields=None,
    #               upload=None,
    #               showid=None,
    #               buttons=None,
    #               extra_fields=None,
    #               form_id=None ):
    #     form = super( PageComposerView, self ).get_form( form_fields=form_fields,
    #                                                      form_validators=form_validators,
    #                                                      deletable=deletable,
    #                                                      textarea_rows=textarea_rows,
    #                                                      readonly_fields=readonly_fields,
    #                                                      exclude_fields=exclude_fields,
    #                                                      upload=upload,
    #                                                      showid=showid,
    #                                                      buttons=buttons,
    #                                                      extra_fields=extra_fields,
    #                                                      form_id=form_id )
    #     # for b in self.b_list:
    #     #     self.form_fields.append( Field( 'body_%d' % b.id, 'text', notnull='True',
    #     #                                     default=b.body ) )
    #     # self.form_fields.append( Field( 'body_0', 'text', notnull='True' ) )
    #
    #     return form


    # def get_form( self,
    #               form_fields=None,
    #               form_validators=None,
    #               deletable=None,
    #               textarea_rows=None,
    #               readonly_fields=None,
    #               exclude_fields=None,
    #               upload=None,
    #               showid=None,
    #               buttons=None,
    #               extra_fields=None,
    #               form_id=None ):
    #     term.printDebug( 'form_validators: %s' % repr( form_validators ) )
    #     if form_fields is None:
    #         form_fields = self.get_form_fields()
    #     form = SQLFORM.factory( *form_fields )
    #     return form


    def upd_page( self, form ):
        db = self.db
        auth = current.auth
        upd = self.get_changed_fields( form, db_table=self.table_model.db_table )
        if upd:
            if self.record:
                self.table_model.update_by_id( self.record.id, upd )
            else:
                upd.url_c = ARCHIVE_CONTROLLER
                upd.url_f = ARCHIVE_FUNCTION
                upd.last_modified_by = auth.user.id
                upd.page_timestamp = DT.now()
                self.record_id = self.table_model.insert( upd )
                self.table_model.update_by_id( self.record_id, dict( url_args=self.record_id ) )
                self.record = self.table_model[ self.record_id ]
        return upd


    def upd_blocks( self, form ):
        term.printDebug( 'form.vars: ' + repr( form.vars ) )
        db = self.db
        auth = current.auth
        request = current.request
        b_model = db_tables.get_table_model( 'block', db=db )
        # pb_model = db_tables.get_table_model( 'page_block', db=db )
        ts = DT.now()
        upd = False
        for fld in request.post_vars:
            if fld.startswith( 'body_' ):
                val = request.post_vars[ fld ]
                db_value = request.post_vars[ 'org__' + fld ] or ''
                if val == db_value:
                    continue

                b_id = int( fld[ 5: ] )
                block = None
                for b in self.b_list:
                    if b.id == b_id:
                        block = b
                        break

                if block and block.id:
                    b_model.update_by_id( block.id,
                                          dict( body=val,
                                                last_modified_by=auth.user.id,
                                                last_modified_on=ts ) )
                else:
                    blk_order = 1
                    if self.b_list:
                        blk_order = self.b_list[ -1 ].blk_order + 1
                    data = Storage( page_id=self.record_id,
                                    title=self.record.title,
                                    name=self.record.name,
                                    created_on=ts,
                                    created_by=auth.user.id,
                                    body=val,
                                    blk_order=blk_order,
                                    last_modified_by=auth.user.id,
                                    last_modified_on=ts )
                    block_id = b_model.insert( data )
                upd = True
        return upd


    def process_form_action( self, form ):
        term.printDebug( 'form.vars: ' + repr( form.vars ) )
        if self.action == self.submit_action:
            ins = (self.record is None)
            upd_p = self.upd_page( form )
            upd_b = self.upd_blocks( form )
            if ins:
                msg = self.msg_record_created
            elif upd_p or upd_b:
                msg = self.msg_record_updated
            else:
                msg = self.msg_nothing_to_update
            self.set_result( message=msg,
                             redirect=URL( c=self.controller_name,
                                           f=self.function_name,
                                           args=[ self.record_id ] ) )


    # def get_page_js( self ):
    #     if self.block and self.page_block and self.page_block.display_type == db_sets.BLOCK_DISPLAY_SUMMARY:
    #         page_js = '''
    #             jQuery( '#block_body_row' ).hide();
    #         '''
    #     else:
    #         page_js = '''
    #             jQuery( '#block_summary_row' ).hide();
    #         '''
    #     js = SCRIPT( '''
    #         jQuery( function() {
    #             %(js)s
    #         } );
    #         ''' % dict( js=page_js ) )
    #     return js
    #
    #
    def post_process_form( self, form ):
        super( PageComposerView, self ).post_process_form( form )
        is_dev = is_in_group( 'dev' )
        #    term.printLog( 'form: ' + repr( form.xml() ) )
        self.set_result( dict( b_list=self.b_list,
                               is_dev=is_dev ) )


