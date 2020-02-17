# -*- coding: utf-8 -*-
# this file is released under public domain and you can use without limitations

# from chirico.views.page_block.add_block_to_page import AddBlockToPageView
from chirico.k import KQV_PAGE_ID
from gluon import current, H4, SQLFORM
from gluon.html import DIV, H5, URL
from gluon.storage import Storage

from m16e.db import db_tables
from m16e import term, htmlcommon
from m16e.kommon import KDT_INT, KDT_CHAR, KDT_TIMESTAMP, DT, ACT_DELETE_RECORD, ACT_SUBMIT
from m16e.ktfact import KTF_COL_ORDER, KTF_CELL_CLASS, KTF_COLS, KTF_TITLE, \
    KTF_TYPE, KTF_CELL_LINK, KTF_LINK_C, KTF_LINK_F, KTF_ARGS, KTF_BUTTON
import m16e.table_factory_with_session as tfact
from m16e.user_factory import is_in_group
from m16e.views.edit_base_view import BaseFormView
from chirico.db import page_factory, block_factory
from pydal import Field

ACT_CLONE_PAGE = 'clone_page'
ACT_DELETE_PAGE = 'delete_page'
ACT_NEW_BLOCK = 'new_block'
ACT_ADD_BLOCK = 'add_block'
ACT_NEW_PAGE = 'new_page'
ACT_SUBMIT_PAGE = 'submit_page'


class PageEditView( BaseFormView ):
    controller_name = 'page'
    function_name = 'edit'


    def __init__( self, db ):
        super( PageEditView, self ).__init__( db )
        self.table_model = db_tables.get_table_model( 'page', db=db )
        self.submit_action = ACT_SUBMIT


    def pre_del( self ):
        super( PageEditView, self ).pre_del()
        # request = current.request
        db = self.db
        b_model = db_tables.get_table_model( 'block', db=db )
        q_sql = (db.block.page_id == self.record_id)
        b_model.delete( q_sql )
        #
        # pb_model = db_tables.get_table_model( 'page_block', db=db )
        # q_sql = (pb_model.db_table.page_id == self.record_id)
        # pb_list = pb_model.select( q_sql )
        # pb_model.delete( q_sql )
        # if request.post_vars.chk_del_blocks:
        #     b_model = db_tables.get_table_model( 'block', db=db )
        #     q_sql = (b_model.db_table.id.belongs( [ pb.block_id for pb in pb_list ] ) )
        #     b_model.delete( q_sql )


    def process_pre_validation_actions( self ):
        super( PageEditView, self ).process_pre_validation_actions()
        request = current.request
        T = current.T
        db = self.db
        if self.action == ACT_NEW_PAGE:
            return self.set_result( redirect=URL( c=self.controller_name,
                                                  f=self.function_name,
                                                  args=[ 0 ] ) )

        if self.action == ACT_NEW_BLOCK:
            d = { 'qv_page_id': self.record_id }
            return self.set_result( redirect=URL( c='block',
                                                  f='edit',
                                                  args=[ 0 ],
                                                  vars=d ) )

        if self.action == ACT_ADD_BLOCK:
            d = { KQV_PAGE_ID: self.record_id }
            return self.set_result( redirect=URL( c='block',
                                                  f='compose',
                                                  vars=d ) )

        if self.action == ACT_CLONE_PAGE:
            inc_blocks = request.post_vars.chk_inc_blocks
            new_page_id = page_factory.clone( self.record_id, inc_blocks )
            return self.set_result( redirect=URL( c=self.controller_name,
                                                  f=self.function_name,
                                                  args=[ new_page_id ] ),
                                    message=T( 'Page cloned' ) )


    def get_readonly_fields( self ):
        return [ 'page_timestamp' ]


    def get_form_fields( self ):
        self.form_fields = [ 'id',
                             'name',
                             'tagname',
                             'parent_page_id',
                             'hide',
                             'title',
                             'url_c',
                             'url_f',
                             'url_args',
                             'colspan',
                             'rowspan',
                             'menu_order',
                             'is_news',
                             'page_timestamp',
                             'aside_position',
                             'aside_title',
                             'main_panel_cols',
                             'aside_panel_cols' ]


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
        term.printDebug( 'form_validators: %s' % repr( form_validators ) )
        if deletable is None and self.record_id:
            deletable = True
        form = super( PageEditView, self ).get_form( form_fields=form_fields,
                                                     form_validators=form_validators,
                                                     deletable=deletable )
        return form


    def process_form_action( self, form ):
        request = current.request
        auth = current.auth
        db = self.db
        # super( PageEditView, self ).process_form_action( form )
        if self.action == self.submit_action:
            upd = htmlcommon.get_changed_fields( form.vars,
                                                 request.post_vars,
                                                 db.page )
            upd[ 'last_modified_by' ] = auth.user.id
            upd[ 'page_timestamp' ] = DT.now()
            # term.printDebug( 'upd: ' + repr( upd ) )
            if upd:
                if self.record_id:
                    self.update_record( upd )
                else:
                    self.insert_record( upd )
            else:
                self.set_result( message=self.msg_nothing_to_update )
                # response.flash = self.msg_nothing_to_update


    def post_process_form( self, form ):
        super( PageEditView, self ).post_process_form( form )
        db = self.db
        block_list = None
        if self.record_id:
            block_list = block_factory.get_page_blocks( page_id=self.record_id, db=db )

        # history = self.get_history( self.record_id or 0 )
        is_dev = is_in_group( 'dev' )
    #    term.printLog( 'form: ' + repr( form.xml() ) )
        self.set_result( dict( page=self.record,
                               form=form,
                               block_list=block_list,
                               # page_history=history,
                               is_dev=is_dev ) )


