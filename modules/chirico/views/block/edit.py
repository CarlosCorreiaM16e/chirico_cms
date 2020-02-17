# -*- coding: utf-8 -*-
# this file is released under public domain and you can use without limitations
from app import db_sets
from chirico.k import KQV_PAGE_ID, KQV_BLK_ORDER, KQV_CONTAINER
from m16e.db import db_tables, attach_factory
from gluon import current, IS_NULL_OR, IS_IN_DB, IS_IN_SET, SCRIPT, XML, IMG
from gluon.html import URL, DIV, H5
from gluon.storage import Storage
from m16e import term, markmin_factory
# from m16e.kommon import KDT_INT, KDT_CHAR, KDT_TIMESTAMP, KQR_SELECTED_ID, DT, KQV_PREFIX
# from m16e.ktfact import KTF_COL_ORDER, KTF_CELL_CLASS, KTF_COLS, KTF_TITLE, KTF_TYPE, KTF_BUTTON, KTF_CELL_LINK, \
#     KTF_LINK_C, KTF_LINK_F, KTF_ARGS
from m16e.kommon import DT
from m16e.user_factory import is_in_group
from m16e.views.edit_base_view import BaseFormView
from chirico.db import block_factory, page_factory

# from chirico.wikiviewer import TAG_PREFIX, WT_BLOCK, WT_IMAGE, TAG_SUFFIX
# import m16e.table_factory_with_session as tfact

ACT_CREATE_PAGE_FROM_BLOCK = 'create_page_from_block'
ACT_CLONE_BLOCK = 'clone_block'
ACT_DELETE_BLOCK = 'delete_block'
ACT_NEW_BLOCK = 'new_block'
ACT_NEW_IMAGE = 'act_new_image'
ACT_NEW_PAGE = 'new_page'
ACT_SUBMIT_BLOCK = 'submit_block'

CHK_DEL_BLOCK = 'chk_del_block'
# CHK_DEL_PAGE_BLOCK = 'chk_del_page_block'


class BlockEditView( BaseFormView ):
    def __init__( self, db ):
        super( BlockEditView, self ).__init__( db )
        self.table_model = db_tables.get_table_model( 'block', db=db )
        self.submit_action = ACT_SUBMIT_BLOCK
        self.textarea_rows = 10
        self.page_id = None


    def fetch_vars( self ):
        super( BlockEditView, self ).fetch_vars()
        request = current.request
        self.page_id = request.vars.get( KQV_PAGE_ID )
        self.blk_order = request.get_vars.get( KQV_BLK_ORDER )
        self.container = request.get_vars.get( KQV_CONTAINER )


    def get_form_validators( self ):
        super( BlockEditView, self ).get_form_validators()
        db = self.db
        return self.form_validators


    def get_form_fields( self ):
        self.form_fields = [ 'page_id',
                             'name',
                             'body',
                             'body_en',
                             'body_markup',
                             'description',
                             'colspan',
                             'rowspan',
                             'css_class',
                             'css_style',
                             'html_element_id',
                             'container',
                             'blk_order'
                             ]
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
        form = super( BlockEditView, self ).get_form( form_fields=form_fields,
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
        if not self.record_id and self.page_id:
            form.vars.page_id = self.page_id
        form.element( '#block_body_en' )[ '_rows' ] = 4
        return form


    def append_image( self ):
        request = current.request
        T = current.T
        target = request.vars.target
        attach_id = int( request.vars.attach_id )
        db = self.db
        # a_model = db_tables.get_table_model( 'attach', db=db )
        # attach = a_model[ attach_id ]
        if self.record.body_markup == db_sets.MARKUP_MARKMIN:
            img = markmin_factory.mk_wt_image( attach_id, db=db )
        else:
            img = IMG( _src=attach_factory.get_url( attach_id, db=db ) ).xml()
        self.table_model.update_by_id( self.record_id,
                                       { target: self.record[ target ] + '\n' + img + '\n' })
        return self.set_result( redirect=URL( c='block', f='edit', args=[ self.record_id ] ),
                                message=T( 'Image added' ) )



    # def delete_record( self ):
    #     db = self.db
    #     request = current.request
    #     if request.vars.get( CHK_DEL_PAGE_BLOCK ) == 'on':
    #         pb_model = db_tables.get_table_model( 'page_block', db=db )
    #         q_sql = (pb_model.db_table.block_id == self.record_id)
    #         pb_model.delete( q_sql )
    #     super( BlockEditView, self ).delete_record()


    def process_pre_validation_actions( self ):
        request = current.request
        super( BlockEditView, self ).process_pre_validation_actions()
        if self.action == ACT_NEW_PAGE:
            return self.set_result( redirect=URL( c='page', f='edit', args=[ 0 ] ) )

        if self.action == ACT_NEW_BLOCK:
            return self.set_result( redirect=URL( c='block', f='edit', args=[ 0 ] ) )

        if self.action == ACT_CLONE_BLOCK:
            if self.record_id:
                block_id = block_factory.clone( self.record_id, db=self.db )
                return self.set_result( redirect=URL( c='block', f='edit', args=[ block_id ] ) )

        if self.action == ACT_NEW_IMAGE:
            return self.append_image()

        if self.action == ACT_DELETE_BLOCK and self.record_id:
            if request.vars.get( CHK_DEL_BLOCK ) == 'on':
                return self.try_to_delete_record()


    def process_form_action( self, form ):
        request = current.request
        db = self.db
        term.printDebug( 'form.vars: ' + repr( form.vars ) )
        if self.action in (self.submit_action, ACT_CREATE_PAGE_FROM_BLOCK):
            upd = self.get_changed_fields( form )
            T = current.T
            if upd:
                auth = current.auth
                # upd[ 'last_modified_by' ] = auth.user.id
                term.printLog( 'upd: ' + repr( upd ) )
                if self.record_id:
                    term.printLog( 'updating: ' + repr( upd ) )
                    block_factory.update_block( self.record_id, upd, db=db )
                    # self.table_model.update_by_id( self.record_id, upd )
                    msg = T( 'Block updated' )
                else:
                    # upd[ 'created_on' ] = DT.now()
                    # upd[ 'created_by' ] = auth.user.id
                    # self.record_id = self.table_model.insert( upd )
                    self.record_id = block_factory.create_block( upd, db=db )
                    msg = T( 'Block created' )
                self.set_result( redirect=URL( c=self.controller_name,
                                               f=self.function_name,
                                               args=[ self.record_id ] ),
                                 message=msg )
            else:
                self.set_result( message=T( 'Nothing to update' ) )
            if self.action == ACT_CREATE_PAGE_FROM_BLOCK:
                page_id, msg = block_factory.create_page_from_block( self.record_id, request.post_vars )
                if page_id:
                    self.set_result( redirect=URL( c='page', f='edit', args=[ page_id ] ),
                                     message=msg )

    # def process_form_action( self, form ):
    #     super( BlockEditView, self ).process_form_action()
    #     request = current.request
    #     db = self.db
    #     term.printDebug( 'form.vars: ' + repr( form.vars ) )
    #     a_model = db_tables.get_table_model( 'attach', db=db )
    #     # pb_model = db_tables.get_table_model( 'page_block', db=self.db )
    #     # if KQR_SELECTED_ID in request.vars:
    #     #     attach = a_model[ request.vars[ KQR_SELECTED_ID ] ]
    #     #     body = self.record.body + '''
    #     # %(prefix)s%(wt_image)s %(id)s:%(title)s+++{ 'link': True, 'width': '200px' }%(suffix)s''' % {
    #     #         'prefix': TAG_PREFIX,
    #     #         'wt_image': WT_IMAGE,
    #     #         'id': attach.id,
    #     #         'title': attach.filename,
    #     #         'suffix': TAG_SUFFIX }
    #     #     self.table_model.update_by_id( self.record_id, dict( body=body ) )
    #     #     return self.set_result( redirect=URL( c='block', f='edit', args=[ self.record_id ] ) )
    #
    #     if self.action in (ACT_SUBMIT_BLOCK, ACT_CREATE_PAGE_FROM_BLOCK):
    #         upd = self.get_changed_fields( form )
    #         msg = None
    #         T = current.T
    #         if upd:
    #             auth = current.auth
    #             upd[ 'last_modified_by' ] = auth.user.id
    #             term.printLog( 'upd: ' + repr( upd ) )
    #             if self.record_id:
    #                 term.printLog( 'updating: ' + repr( upd ) )
    #                 self.table_model.update_by_id( self.record_id, upd )
    #                 msg = T( 'Block updated' )
    #             else:
    #                 upd[ 'created_on' ] = DT.now()
    #                 upd[ 'created_by' ] = auth.user.id
    #                 # upd[ 'group_id' ] = 0
    #                 self.record_id = self.table_model.insert( upd )
    #                 # pb_model.insert( dict( page_id=upd[ 'page_id' ],
    #                 #                        block_id=self.record_id ) )
    #                 msg = T( 'Block created' )
    #             self.set_result( redirect=URL( r=request, f='edit', args=[ self.record_id ] ), message=msg )
    #         else:
    #             self.set_result( message=T( 'Nothing to update' ) )
    #
    #         if self.action == ACT_CREATE_PAGE_FROM_BLOCK:
    #             page_id, msg = self.table_model.create_page_from_block( self.record_id, request.post_vars )
    #             if page_id:
    #                 self.set_result( redirect=URL( c='page', f='edit', args=[ page_id ] ) )


    # def post_process_form( self, form ):
    #     request = current.request
    #     super( BlockEditView, self ).post_process_form( form )
    #     # history = self.get_history()
    #     # history = ''
    #     children_blocks = []
    #     # if request.args:                    # block
    #     #     if self.record_id:
    #     #         # block = db.block[ block_id ]
    #     #         blk_prefix = '%s%s' % (TAG_PREFIX, WT_BLOCK)
    #     #         if blk_prefix in self.record.body:
    #     #             chl_ids = [ int( s.split( ':', 1 )[0] )
    #     #                         for s in self.record.body.split( blk_prefix )[1:] ]
    #     #             for chl_id in chl_ids:
    #     #                 children_blocks.append( self.table_model[ chl_id ] )
    #     #
    #     # block_list = self.table_model.select( (self.table_model.db_table.page_id == None), orderby='block.name' )
    #     block_list = []
    #     #         for b in block_list:
    #     #             print( '%s, %s, %s' % ( b.id, b.name, b.title ) )
    #     is_dev = is_in_group( 'dev' )
    #     return self.set_result( dict( block=self.record,
    #                                   form=form,
    #                                   block_list=block_list,
    #                                   # block_history=history,
    #                                   children_blocks=children_blocks,
    #                                   is_dev=is_dev ) )
    #


    def post_process_form( self, form ):
        super( BlockEditView, self ).post_process_form( form )
        is_dev = is_in_group( 'dev' )
        # block_list = None
        # if self.record_id:
        #     block_list = block_factory.get_page_blocks( block_id=self.record_id, db=self.db )
        return self.set_result( dict( block=self.record,
                                      form=form,
                                      # block_list=block_list,
                                      is_dev=is_dev ) )


    # def get_page_js( self ):
    #     js = '''
    #         jQuery( function() {'''
    #     if not self.record or self.record.summary_markup == db_sets.MARKUP_HTML:
    #         js += '''
    #             jQuery( #block_summary' ).jqte();'''
    #     if not self.record or self.record.body_markup == db_sets.MARKUP_HTML:
    #         js += '''
    #             jQuery( '#block_body' ).jqte();'''
    #     js += '''
    #         } );
    #         '''
    #     return XML( '<script>' + js + '</script>' )
    #
    #

