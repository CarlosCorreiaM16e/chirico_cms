# -*- coding: utf-8 -*-

# from cgi import FieldStorage
#
# from forum import thread_factory
from m16e.db import db_tables, db_sets
from gluon import current
from gluon.html import A, DIV, SPAN, URL
from gluon.storage import Storage
from m16e import term
# from m16e.db import attach_factory
from m16e.kommon import DATE, DT, KDT_BOOLEAN, ACT_SUBMIT
from m16e.views.edit_base_view import BaseFormView


class ThreadNewView( BaseFormView ):
    controller_name = 'forum'
    function_name = 'new'


    def __init__( self, db ):
        super( ThreadNewView, self ).__init__( db )
        self.table_model = db_tables.get_table_model( 'thread', db=db )


    def get_exclude_fields( self ):
        return ('created_on',
                'created_by',
                'thread_status_id',
                'closed_time',
                'markup' )


    def pre_ins( self, upd ):
        super( ThreadNewView, self ).pre_ins( upd )
        term.printDebug( 'upd: %s' % repr( upd ) )
        db = self.db
        auth = current.auth
        ts_model = db_tables.get_table_model( 'thread_status', db=db )
        ts_new = ts_model.select( orderby='preferred_order' ).first()
        upd.created_on = DT.now()
        upd.created_by = auth.user.id
        upd.thread_status_id = ts_new.id


    def post_ins( self, upd ):
        super( ThreadNewView, self ).post_ins( upd )
        db = self.db
        auth = current.auth
        ts_model = db_tables.get_table_model( 'thread_subscriber', db=db )
        ts_model.insert( dict( thread_id=self.record_id,
                               auth_user_id=auth.user.id ) )


    # def ins_attach( self, thread_msg_id ):
    #     db = self.db
    #     request = current.request
    #     T = current.T
    #     auth = current.auth
    #     term.printDebug( 'request.vars.tma_attach_1: %s' % request.vars.tma_attach_1 )
    #     if not isinstance( request.vars.tma_attach_1, FieldStorage ):
    #         return None
    #
    #     at_model = db_tables.get_table_model( 'attach_type', db=db )
    #     tma_model = db_tables.get_table_model( 'thread_msg_attach', db=db )
    #     q_sql = (db.attach_type.meta_name == 'gps')
    #     at = at_model.select( q_sql ).first()
    #     if at:
    #         at_id = at.id
    #     else:
    #         at_id = at_model.insert( dict( name=T( 'Support' ),
    #                                        meta_name='gps' ) )
    #
    #     attach_id = attach_factory.add_attach( request.vars.tma_attach_1,
    #                                            attach_type_id=at_id,
    #                                            created_by=auth.user.id,
    #                                            short_description=request.vars.tma_short_description )
    #     tma_id = tma_model.insert( dict( attach_id=attach_id,
    #                                      thread_msg_id=thread_msg_id ) )
    #     return tma_id
    #
    #
    # def add_subscriber( self ):
    #     db = self.db
    #     auth = current.auth
    #     rs_model = db_tables.get_table_model( 'thread_subscriber', db=db )
    #     upd = dict( thread_id=self.record_id,
    #                 user_id=auth.user.id )
    #     return rs_model.insert( upd )
    #
    #
    # def send_mail( self ):
    #     db = self.db
    #     T = current.T
    #     rt_model = db_tables.get_table_model( 'thread_type', db=db )
    #     rt = rt_model[ self.record.thread_type_id ]
    #     subject = '[%s]: %s' % (rt.thread_type_name.upper( ),
    #                             self.record.short_description)
    #     message = '%s: %s' % (T( 'New thread' ),
    #                           URL( c=self.controller_name,
    #                                f='edit',
    #                                args=[ self.record_id ] ) )
    #     thread_factory.do_send_mail( self.record_id,
    #                            subject=subject,
    #                            message=message )
    #
    #
    def process_form_action( self, form ):
        term.printDebug( 'form.vars: ' + repr( form.vars ) )
        if self.action == self.submit_action:
            upd = self.get_changed_fields( form )
            term.printDebug( 'upd: ' + repr( upd ) )
            if upd:
                self.insert_record( upd )
                self.set_result( message=self.msg_record_created )
            else:
                self.set_result( message=self.msg_nothing_to_update )


    # ------------------------------------------------------------------
    def get_redirect_on_insert( self ):
        return URL( c=self.controller_name,
                    f='view',
                    args=[ self.record_id ] )


