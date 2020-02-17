# -*- coding: utf-8 -*-

from m16e.db import db_tables
from gluon import current, URL
from m16e import term
from m16e.kommon import DT
from m16e.views.edit_base_view import BaseFormView


ACT_SEND_TO_ALL = 'act_send_to_all'


class MailQueueEditView( BaseFormView ):
    controller_name = 'mail_queue'
    function_name = 'edit'

    def __init__( self, db ):
        super( MailQueueEditView, self ).__init__( db )
        self.table_model = db_tables.get_table_model( 'mail_queue', db=db )


    def get_form_fields( self ):
        self.form_fields = [ 'id', 'when_to_send', 'subject', 'text_body',
                             'html_body', 'mail_cc', 'mail_bcc', 'status',
                             'sent', 'auth_user_id', 'percent_done', 'progress_message' ]
        if self.record:
            self.form_fields.append( 'status' )
        return super( MailQueueEditView, self ).get_form_fields()


    def do_insert_record( self, upd ):
        auth = current.auth
        if not upd.get( 'status' ):
            upd[ 'status'] = 'pending'
        if not upd.get( 'auth_user_id' ):
            upd[ 'auth_user_id' ] = auth.user.id
        if not upd.get( 'when_to_send' ):
            upd[ 'when_to_send' ] = DT.now()
        super( MailQueueEditView, self ).do_insert_record( upd )


    def process_form_action( self, form ):
        request = current.request
        response = current.response
        session = current.session
        T = current.T
        term.printDebug( 'form.vars: ' + repr( form.vars ) )
        if self.action == self.submit_action or self.action == ACT_SEND_TO_ALL:
            if form.deleted:
                self.try_to_delete_record()
            else:
                upd = self.get_changed_fields( form )
                term.printDebug( 'upd: ' + repr( upd ) )
                if upd:
                    if self.record_id:
                        self.update_record( upd )
                    else:
                        self.insert_record( upd )
                else:
                    self.set_result( message=self.msg_nothing_to_update )
                    # response.flash = self.msg_nothing_to_update
                if self.action == ACT_SEND_TO_ALL:
                    self.send()

        # super( MailQueueEditView, self ).process_form_action( form )


    def post_process_form( self, form ):
        super( MailQueueEditView, self ).post_process_form( form )
        mr_list = None
        if self.record_id:
            db = self.db
            mr_model = db_tables.get_table_model( 'mail_recipient', db=db )
            q_sql = (db.mail_recipient.mail_queue_id == self.record_id)
            mr_list = mr_model.select( q_sql, orderby='email' )
        self.set_result( data=dict( mr_list=mr_list ) )


    def resend( self ):
        request = current.request
        db = self.db
        mr_id = int( request.args( 0 ) )
        mr_model = db_tables.get_table_model( 'mail_recipient', db=db )
        mr_model.update_by_id( mr_id, dict( sent=None, status='resend' ) )
        mr = mr_model[ mr_id ]
        self.table_model.update_by_id( mr.mail_queue_id,
                                       dict( status='resend' ) )
        return self.set_result( redirect=URL( c=self.controller_name,
                                              f=self.function_name,
                                              args=[ mr.mail_queue_id ] ) )
