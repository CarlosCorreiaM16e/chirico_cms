# -*- coding: utf-8 -*-
import sys
import traceback

from forum_threads import thread_factory
from m16e.db import db_tables
from gluon import SQLFORM, IS_NOT_EMPTY, IS_NOT_IN_DB, IS_IN_DB, TABLE, TR, INPUT, TEXTAREA, TD, BUTTON
from gluon import current, FORM
from m16e import term
from m16e.kommon import DT
from m16e.views.edit_base_view import BaseFormView
from gluon.html import A, DIV, SPAN, URL

ACT_ADD_ATTACH = 'act_add_attach'

#----------------------------------------------------------------------
class ThreadMsgEditView( BaseFormView ):
    controller_name = 'thread'
    function_name = 'edit_thread_msg'

    #----------------------------------------------------------------------
    def __init__( self, db ):
        super( ThreadMsgEditView, self ).__init__( db )
        self.table_model = db_tables.get_table_model( 'thread_msg', db=db )


    def get_redirect_on_insert( self ):
        self.fetch_record()
        return URL( c=self.controller_name,
                    f='edit',
                    args=[ self.record.thread_id ] )


    def get_form_fields( self ):
        return [ 'msg_text' ]


    def update_record( self, upd ):
        db = self.db
        if 'is_waiting_reply' in upd:
            sr_model = db_tables.get_table_model( 'thread', db=db )
            sr_model.update_by_id( self.record.thread_id,
                                   dict( is_waiting_reply= upd[ 'is_waiting_reply' ] ) )
            del( upd[ 'is_waiting_reply' ] )
        super( ThreadMsgEditView, self ).update_record( upd )


    def insert_record( self, upd ):
        auth = current.auth
        upd[ 'user_id' ] = auth.user.id
        upd[ 'msg_ts' ] = DT.now()
        super( ThreadMsgEditView, self ).insert_record( upd )


    def process_form_action( self, form ):
        db = self.db
        T = current.T
        term.printDebug( 'form.vars: ' + repr( form.vars ) )
        if self.action == self.submit_action:
            if form.deleted:
                self.try_to_delete_record()
            else:
                upd = self.get_changed_fields( form )
                term.printDebug( 'upd: ' + repr( upd ) )
                is_waiting_reply = bool( form.vars.is_waiting_reply )
                if is_waiting_reply:
                    sr_model = db_tables.get_table_model( 'thread', db=db )
                    sr_model.update_by_id( self.record.thread_id,
                                           dict( is_waiting_reply=is_waiting_reply ) )

                if upd:
                    if self.record_id:
                        self.update_record( upd )
                    else:
                        self.insert_record( upd )
                else:
                    self.set_result( message=self.msg_nothing_to_update )
                send_mail = form.vars.send_mail
                if send_mail:
                    rt_model = db_tables.get_table_model( 'thread_type', db=db )
                    rt = rt_model[ self.record.thread_type_id ]
                    link = URL( c=self.controller_name,
                                f='edit',
                                args=[ self.record.thread_id ],
                                scheme=True,
                                host=True )
                    message = '%s: %s' % (T( 'Thread message updated' ), link)
                    thread_factory.notify_subscribers( self.record.thread_id,
                                                       subject='Re: [%s]' % rt.thread_type_name,
                                                       message=message )
                # self.set_result( redirect=URL( c=self.controller_name,
                #                                f='edit',
                #                                args=[ self.record.thread_id ] ) )

    # # ------------------------------------------------------------------
    # def process_form_action( self, form ):
    #     db = self.db
    #     auth = current.auth
    #     T = current.T
    #     term.printDebug( 'form.vars: ' + repr( form.vars ) )
    #     if self.action == self.submit_action:
    #         upd = self.get_changed_fields( form,
    #                                        db_table=db[ self.rm_model.table_name ] )
    #         term.printDebug( 'upd: ' + repr( upd ) )
    #         if upd:
    #             self.rm_model.insert( dict( request_id=self.record_id,
    #                                         msg_text=form.vars.msg_text,
    #                                         msg_ts=DT.now(),
    #                                         time_consumed=form.vars.time_consumed or 0,
    #                                         time_consumed_period_id=form.vars.time_consumed_period_id or 1,
    #                                         user_id=auth.user.id ) )
    #             self.set_result( message=self.msg_record_created )
    #         else:
    #             self.set_result( message=self.msg_nothing_to_update )
    #             # response.flash = self.msg_nothing_to_update
    #
    #----------------------------------------------------------------------
    def post_process_form( self, form ):
        super( ThreadMsgEditView, self ).post_process_form( form )
        T = current.T
        req_link = A( T( 'View thread # ' ) + str( self.record.thread_id ),
            _href = URL( c=self.controller_name,
                         f='edit',
                         args=[ self.record.thread_id ] ) )
        term.printDebug( 'req_link: %s' % repr( req_link ) )
        term.printDebug( 'self.record: %s' % repr( self.record ) )
        self.set_result( data=dict( message=T( 'Thread # ' ) + self.record_id,
                                    req_link=req_link ) )


    # ------------------------------------------------------------------
    def ajax_show_add_attach( self ):
        request = current.request
        response = current.response
        session = current.session
        T = current.T
        db = self.db
        auth = current.auth

        try:
            thread_id = int( request.args( 0 ) )
            table = TABLE()
            tr = TR()
            inp = INPUT( _type='hidden', _name='rm_id', _value=thread_id )
            ta = TEXTAREA( _name='short_description', _rows=3, _style='width: 260px;' )
            tr.append( TD( inp, ta, _rowspan=2 ) )
            inp = INPUT( _type='file', _name='attached', _id='rma_add_file_%d' % thread_id, _style='width: 360px;' )
            tr.append( TD( inp ) )
            table.append( tr )
            table.append( TR( TD( BUTTON( T( 'Add' ),
                                          _name='action',
                                          _title=T( 'Add attach to thread' ),
                                          _type='submit',
                                          _value='act_add_attach' ) ) ) )
            div = DIV( table,
                       _id='thread_messages_table_%d' % thread_id )
            td = TD( div,
                     _colspan=3,
                     _class='table_border' )
            return td.xml()
        except:
            t, v, tb = sys.exc_info( )
            traceback.print_exception( t, v, tb )
            raise
        return ''


    #----------------------------------------------------------------------



