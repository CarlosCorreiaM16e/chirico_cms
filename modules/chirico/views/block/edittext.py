# -*- coding: utf-8 -*-
# this file is released under public domain and you can use without limitations
from m16e.db import db_tables
from gluon import current
from gluon.html import URL
from gluon.storage import Storage
from m16e import term, htmlcommon
from m16e.views.edit_base_view import BaseFormView


class BlockEdittextView( BaseFormView ):
    controller_name = 'block'
    function_name = 'edittext'


    def __init__( self, db ):
        super( BlockEdittextView, self ).__init__( db )
        T = current.T
        self.table_model = db_tables.get_table_model( 'block', db=db )
        self.page_id = None
        self.msg_record_updated = T( 'Block updated' )
        self.msg_record_created = T( 'Block created' )
        self.msg_record_deleted = T( 'Block deleted' )


    def fetch_vars( self ):
        super( BlockEdittextView, self ).fetch_vars()
        request = current.request
        self.page_id = int( request.vars.qv_page_id or 0 )


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
        if not form_fields:
            form_fields = [ 'content_type', 'body' ]
        form = super( BlockEdittextView, self ).get_form( form_fields, form_validators )
        for el in form.elements( 'textarea' ):
            el['_rows'] = 25
        form.vars.page_id = self.page_id
        return form


    def process_form_action( self, form ):
        request = current.request
        auth = current.auth
        db = self.db
        if self.action == self.submit_action:
            upd = htmlcommon.get_changed_fields( form.vars,
                                                 request.post_vars,
                                                 db.block )
            # term.printDebug( 'upd: ' + repr( upd ) )
            if upd:
                if self.record_id:
                    upd[ 'last_modified_by' ] = auth.user.id
                    self.update_record( upd )
                else:
                    self.insert_record( upd )
            else:
                self.set_result( message=self.msg_nothing_to_update )
                # response.flash = self.msg_nothing_to_update


    # def process( self ):
    #     ACT_SUBMIT_BLOCK = 'submit_block'
    #
    #     request = current.request
    #     response = current.response
    #     session = current.session
    #     T = current.T
    #     db = self.db
    #     auth = session.auth
    #     redirect = None
    #
    #     term.printLog( 'request.args: ' + repr( request.args ) )
    #     term.printLog( 'request.vars: ' + repr( request.vars ) )
    #
    #     BlockModel( db ).define_table()
    #     block_id = 0
    #     block = None
    #     if request.args:                    # block
    #         block_id = int( request.args( 0 ) )
    #         if block_id:
    #             block = db.block[ block_id ]
    #
    #     pageId = int( request.vars.qv_page_id or 0 )
    #     term.printLog( 'block_id: ' + repr( block_id ) )
    #
    #     form = self.get_form( block )
    #     if pageId:
    #         form.vars.page_id = pageId
    #
    #     action = request.post_vars.action
    #     term.printLog( 'action: ' + repr( action ) )
    #
    #     if form.accepts( request.vars, session, dbio=False ):
    #         term.printLog( 'form.vars: ' + repr( form.vars ) )
    #         if action == ACT_SUBMIT_BLOCK:
    #             upd = html.getChangedFields( form.vars, request.post_vars, db.block )
    #             if upd:
    #                 upd[ 'last_modified_by' ] = auth.user.id
    #                 block_id = block['id']
    #                 term.printLog( 'updating: ' + repr( upd ) )
    #                 db( db.block.id == block_id ).update( **upd )
    #                 session.flash = T( 'Block updated' )
    #                 redirect = URL( c='pageviewer', f='view', args = [ block.page_id or 1 ] )
    #             else:
    #                 response.flash = T( 'Nothing to update' )
    #
    #     elif form.errors:
    #         term.printLog( 'form.errors: ' + repr( form.errors ) )
    #         response.flash=T( 'Form has errors' )
    #
    #     return Storage( dict=dict( block=block,
    #                                form=form  ),
    #                    redirect=redirect )
    #
    #
