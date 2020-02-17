# -*- coding: utf-8 -*-
# this file is released under public domain and you can use without limitations
import sys
import traceback

from app import db_sets
from chirico.app import app_factory
from chirico.db import block_factory
from chirico.k import KQV_PAGE_ID, ACT_DELETE_BLOCK, IMG_SIZE_PAGE, IMG_SIZE_BLOCK, IMG_SIZE_THUMB, KQV_BLK_ORDER, \
    KQV_CONTAINER
from gluon import current, H4, SQLFORM, IS_NOT_EMPTY, IMG, SCRIPT, A
from gluon.html import DIV, H5, URL
from gluon.storage import Storage

from m16e.db import db_tables, attach_factory
from m16e import term, markmin_factory
from m16e.files import fileutils
from m16e.kommon import KDT_INT, KDT_CHAR, KDT_TIMESTAMP, DT, ACT_NEW_IMAGE
from m16e.user_factory import is_in_group
from m16e.views.edit_base_view import BaseFormView

# ACT_NEW_MAIN_BLOCK = 'new_main_block'
# ACT_NEW_SIDE_BLOCK = 'new_side_block'


class BlockComposerView( BaseFormView ):
    controller_name = 'block'
    function_name = 'composer'


    def __init__( self, db ):
        super( BlockComposerView, self ).__init__( db )
        self.table_model = db_tables.get_table_model( 'block', db=db )
        self.textarea_rows = 18
        self.page_id = None
        self.blk_order = None
        self.container = None

    def fetch_vars( self ):
        super( BlockComposerView, self ).fetch_vars()
        request = current.request
        self.page_id = request.vars.get( KQV_PAGE_ID )
        self.blk_order = request.get_vars.get( KQV_BLK_ORDER )
        self.container = request.get_vars.get( KQV_CONTAINER )


    # def fetch_record( self, fetch_id=False ):
    #     super( BlockComposerView, self ).fetch_record( fetch_id )
    #     if not self.record:
    #         db = self.db
    #         block_factory.create_slot_before( dict( page_id=self.page_id,
    #                                                 container=self.container,
    #                                                 blk_order=self.blk_order ),
    #                                           db=db )
    #         self.record_id = block_factory.create_block( dict( page_id=self.page_id,
    #                                                            container=self.container,
    #                                                            blk_order=self.blk_order ),
    #                                                      db=db )
    #         self.record = self.table_model[ self.record_id ]


    def append_image( self ):
        request = current.request
        T = current.T
        auth = current.auth
        # block_id = int( request.args( 0 ) )
        attach_id = int( request.vars.attach_id )
        target = request.vars.target
        size = request.vars.size
        # block_id = int( request.args( 1 ) or 0 )
        db = self.db
        a_model = db_tables.get_table_model( 'attach', db=db )
        attach = a_model[ attach_id ]
        append_attach_id = None
        if size != db_sets.IMG_SIZE_ORIGINAL:
            ac = app_factory.get_app_config_data( db=db )
            isizes = Storage( { db_sets.IMG_SIZE_ORIGINAL: ac[ IMG_SIZE_PAGE ],
                                db_sets.IMG_SIZE_MEDIUM: ac[ IMG_SIZE_BLOCK ],
                                db_sets.IMG_SIZE_SMALL: ac[ IMG_SIZE_THUMB ] } )
            resize_options = attach_factory.get_resize_options( attach, isizes )
            if size in resize_options:
                w = isizes[ size ]
                att = attach_factory.get_child_by_width( attach_id, w, db=db )
                if att:
                    append_attach_id = att.id
                else:
                    append_attach_id = attach_factory.copy_image( auth.user.id,
                                                                  attach_id,
                                                                  new_width=w,
                                                                  insert_dim_in_name=True,
                                                                  dump_to_static=True )
                attach = a_model[ append_attach_id ]
        else:
            append_attach_id = attach_id

        if not attach_factory.is_file_in_static( append_attach_id, db=db ):
            upd = dict( filename=fileutils.filename_sanitize( attach.filename ) )
            a_model.update_by_id( append_attach_id, upd )
            attach_factory.file_dump_to_static( append_attach_id, db=db )
        # b = b_model[ block_id ]
        if self.record.body_markup == db_sets.MARKUP_MARKMIN:
            img = markmin_factory.mk_wt_image( append_attach_id,
                                               align='center',
                                               width=attach.img_width,
                                               caption=attach.short_description,
                                               db=db )
        else:
            img = IMG( _src=attach_factory.get_url( append_attach_id, db=db ) ).xml()
        self.table_model.update_by_id( self.record_id,
                                       { target: self.record[ target ] + '\n' + img + '\n' } )
        return self.set_result( redirect=URL( c=self.controller_name,
                                              f=self.function_name,
                                              args=[ self.record_id ] ),
                                message=T( 'Image added' ) )


    def process_pre_validation_actions( self ):
        super( BlockComposerView, self ).process_pre_validation_actions()
        # request = current.request
        T = current.T
        if self.action == ACT_NEW_IMAGE:
            return self.append_image()

        if self.action == ACT_DELETE_BLOCK:
            url = URL( c=self.record.page_id.url_c,
                       f=self.record.page_id.url_f,
                       args=self.record.page_id.url_args )
            self.delete_record()
            return self.set_result( redirect=url, message=T( 'Block deleted' ),
                                    force_redirect=True )


    def get_form_fields( self ):
        self.form_fields = [ 'page_id', 'name', 'body', 'body_en',
                             'body_markup', 'container', 'blk_order' ]
        return self.form_fields


    def get_form( self,
                  form_fields=None,
                  form_validators=None,
                  deletable=None,
                  textarea_rows=None,
                  readonly_fields=None,
                  exclude_fields=None,
                  upload=None,
                  showid=None,
                  buttons=None,
                  extra_fields=None,
                  form_id=None ):
        form =  super( BlockComposerView, self ).get_form( form_fields=form_fields,
                                                           form_validators=form_validators,
                                                           deletable=deletable,
                                                           textarea_rows=textarea_rows,
                                                           readonly_fields=readonly_fields,
                                                           exclude_fields=exclude_fields,
                                                           upload=upload,
                                                           showid=showid,
                                                           buttons=buttons,
                                                           extra_fields=extra_fields,
                                                           form_id=form_id )
        if not self.record_id:
            form.vars.page_id = self.page_id
            form.vars.blk_order = self.blk_order
            form.vars.container = self.container
        # form.element( '#block_body_en' )[ '_rows' ] = 4
        form.element( '#block_body' )[ '_class' ] += ' mono_font'
        form.element( '#block_body_en' )[ '_class' ] += ' mono_font'
        return form


    def upd_block( self, form ):
        db = self.db
        # auth = current.auth
        upd = self.get_changed_fields( form, db_table=self.table_model.db_table )
        if upd:
            if self.record_id:
                block_factory.update_block( self.record_id, upd, db=db )
            else:
                block_factory.create_slot_before( dict( page_id=self.page_id,
                                                        container=self.container,
                                                        blk_order=self.blk_order ),
                                                  db=db )
                self.record_id = block_factory.create_block( upd, db=db )
                self.record = self.table_model[ self.record_id ]
        return upd



    def process_form_action( self, form ):
        term.printDebug( 'form.vars: ' + repr( form.vars ) )
        if self.action == self.submit_action:
            ins = (self.record is None)
            upd_b = self.upd_block( form )
            if ins:
                msg = self.msg_record_created
            elif upd_b:
                msg = self.msg_record_updated
            else:
                msg = self.msg_nothing_to_update
            self.set_result( message=msg,
                             redirect=URL( c=self.controller_name,
                                           f=self.function_name,
                                           args=[ self.record_id ] ) )


    def post_process_form( self, form ):
        super( BlockComposerView, self ).post_process_form( form )
        T = current.T
        db = self.db
        is_dev = is_in_group( 'dev' )
        #    term.printLog( 'form: ' + repr( form.xml() ) )
        p_model = db_tables.get_table_model( 'page', db=db )
        pages = p_model.select( orderby='name' )
        self.set_result( dict( page_list=pages,
                               is_dev=is_dev ) )


    # def get_page_js( self ):
    #     js = super( BlockComposerView, self ).get_page_js()
    #     if self.record:
    #         T = current.T
    #         url_add_embed = URL( c="block", f="ajax_add_embed", args=[ self.record.id, 'body' ] )
    #         url_add_embed_en = URL( c="block", f="ajax_add_embed", args=[ self.record.id, 'body_en' ] )
    #         url_add_link = URL( c="block", f="ajax_add_link", args=[ self.record.id ] )
    #         bt_submit = T( 'Submit' )
    #         bt_cancel = T( 'Cancel' )
    #         pjs = '''
    #             jQuery(function() {
    #                 jQuery( '#act_add_embed' ).click( function() {
    #                     jQuery( '#add_embed_form_dialog' )
    #                         .data( 'url', '%(url_add_embed)s' )
    #                         .dialog( 'open' );
    #                     return false;
    #                 } );
    #                 jQuery( '#act_add_embed_en' ).click( function() {
    #                     jQuery( '#add_embed_form_dialog' )
    #                         .data( 'url', '%(url_add_embed_en)s' )
    #                         .dialog( 'open' );
    #                     return false;
    #                 } );
    #                 jQuery( '#add_embed_form_dialog' ).dialog( {
    #                     autoOpen: false,
    #                     modal: true,
    #                     width: 640,
    #                     buttons: {
    #                         "%(bt_submit)s": function() {
    #                             jQuery( this ).dialog( 'close' );
    #                             ajax( jQuery( this ).data( 'url' ), [ 'add_embed_text', 'add_embed_text_caption' ], ':eval' );
    #                         },
    #                         "%(bt_cancel)s": function() {
    #                             jQuery( this ).dialog( 'close' );
    #                         }
    #                     }
    #                 } );
    #                 jQuery( '#act_add_link' ).click( function() {
    #                     jQuery( '#add_link_form_dialog' ).dialog( 'open' );
    #                     return false;
    #                 } );
    #
    #                 jQuery( '#add_link_form_dialog' ).dialog( {
    #                     autoOpen: false,
    #                     modal: true,
    #                     buttons: {
    #                         "%(bt_submit)s": function() {
    #                             jQuery( this ).dialog( 'close' );
    #                             ajax( '%(url_add_link)s', [ 'add_link_id' ], ':eval' );
    #                         },
    #                         "%(bt_cancel)s": function() {
    #                             jQuery( this ).dialog( 'close' );
    #                         }
    #                     }
    #                 } );
    #             });
    #         ''' % dict( url_add_embed=url_add_embed,
    #                     url_add_embed_en=url_add_embed_en,
    #                     url_add_link=url_add_link,
    #                     bt_submit=bt_submit,
    #                     bt_cancel=bt_cancel )
    #         js += pjs
    #         if self.record.body_markup == db_sets.MARKUP_HTML:
    #             js += '''
    #                 jQuery(function(){
    #                     jQuery( '#block_body' ).css('min-height','400px').jqte();
    #                     jQuery( '#block_body_en' ).css('min-height','400px').jqte();
    #                 } );
    #             '''
    #     return js
    #


    def ajax_add_link( self ):
        request = current.request

        term.printLog( 'request.args: %s' % repr( request.args ) )
        term.printLog( 'request.vars: %s' % repr( request.vars ) )
        js = ''
        try:
            db = self.db
            self.fetch_record( fetch_id=True )
            add_link_id = request.vars.add_link_id
            p_model = db_tables.get_table_model( 'page', db=db )
            page = p_model[ add_link_id ]
            url = URL( c=page.url_c, f=page.url_f, args=page.url_args )
            if self.record.body_markup == db_sets.MARKUP_MARKMIN:
                lk = markmin_factory.mk_wt_link( url, text=page.title )
            else:
                lk = A( page.title, _href=url ).xml()
            js = '''
                jQuery( '#block_body' ).val( jQuery( '#block_body' ).val() + '%s' );
            ''' % lk
            term.printLog( 'js: %s' % js )
            return js

        except:
            t, v, tb = sys.exc_info( )
            traceback.print_exception( t, v, tb )
            # raise
        return ''


    def ajax_add_embed( self ):
        request = current.request

        term.printLog( 'request.args: %s' % repr( request.args ) )
        term.printLog( 'request.vars: %s' % repr( request.vars ) )
        # js = ''
        try:
            self.fetch_record( fetch_id=True )
            target = request.args( 1 )
            add_embed_text = request.vars.add_embed_text
            add_embed_text_caption = request.vars.add_embed_text_caption
            if self.record.body_markup == db_sets.MARKUP_MARKMIN:
                s = markmin_factory.mk_wt_embed( add_embed_text, add_embed_text_caption )
            else:
                if add_embed_text_caption:
                    s = '''
                        <figure>
                            %(e)s
                            <figcaption>%(c)s</figcaption>
                        </figure>
                    ''' % dict( e=add_embed_text, c=add_embed_text_caption )
                else:
                    s = add_embed_text
            js = '''
                jQuery( '#block_%(t)s' ).val( jQuery( '#block_%(t)s' ).val() + '%(s)s' );
            ''' % dict( t=target, s=s )
            term.printLog( 'js: %s' % js )
            return js

        except:
            t, v, tb = sys.exc_info( )
            traceback.print_exception( t, v, tb )
            # raise
        return ''

