# -*- coding: utf-8 -*-
# this file is released under public domain and you can use without limitations
from forum_threads import thread_factory
from m16e.db import db_tables
from gluon import current, IS_IN_SET, A
from gluon.html import URL
from gluon.storage import Storage
from m16e import term, htmlcommon
from m16e.kommon import DT, to_utf8
from m16e.views.edit_base_view import BaseFormView


SEND_MAIL_FLD = 'send_mail'


class ThreadEditThreadView( BaseFormView ):
    controller_name = 'forum'
    function_name = 'edit_thread'


    def __init__( self, db ):
        super( ThreadEditThreadView, self ).__init__( db )
        self.table_model = db_tables.get_table_model( 'thread', db=db )


    def get_exclude_fields( self ):
        self.exclude_fields = [ 'created_on', 'closed_time' ]
        return self.exclude_fields


    def process_pre_validation_actions( self ):
        super( ThreadEditThreadView, self ).process_pre_validation_actions()
        request = current.request
        T = current.T
        if not request.args:
            return self.set_result( redirect=URL( c=self.controller_name,
                                                  f='index' ),
                                    message=T( 'An error has occurred' ),
                                    stop_execution=True )


    def send_mail( self, message, closed ):
        db = self.db
        T = current.T
        rt_model = db_tables.get_table_model( 'thread_type', db=db )
        rt = rt_model[ self.record.thread_type_id ]
        subject = '[%s]: %s' % (to_utf8( rt.thread_type_name ).upper(),
                                self.record.short_description)
        if closed:
            subject += ' (' + T( 'closed' ) + ')'
        thread_factory.notify_subscribers( self.record_id,
                                           subject,
                                           message=message )


    def process_form_action( self, form ):
        request = current.request
        response = current.response
        session = current.session
        T = current.T
        term.printDebug( 'form.vars: ' + repr( form.vars ) )
        if self.action == self.submit_action:
            send_mail = bool( request.vars[ SEND_MAIL_FLD ] )
            term.printLog( 'send_mail: %s' % (repr( send_mail )) )

            if form.deleted:
                self.try_to_delete_record()
            else:
                upd = self.get_changed_fields( form )
                if upd:
                    link = URL( c=self.controller_name,
                                f='edit',
                                args=[ self.record_id ],
                                scheme=True,
                                host=True )
                    message = '%s: %s\n\n' % (T( 'Thread changed' ), link)
                    # term.printDebug( 'upd: ' + repr( upd ) )
                    closed = False
                    status_id = int( upd.get( 'thread_status_id' ) or 0 )
                    if status_id:
                        message += '\n' + T( 'Status changed to' ) + ': '
                        rs_model = db_tables.get_table_model( 'thread_status' )
                        rs = rs_model[ status_id ]
                        message += rs.thread_status_name

                    self.update_record( upd )

                    term.printLog( 'send_mail: %s' % (repr( send_mail )) )
                    if send_mail:
                        self.send_mail( message, closed )
                    else:
                        term.printLog( 'Skipped mail send' )
                else:
                    response.flash = T( 'Nothing to update' )


    def post_process_form( self, form ):
        super( ThreadEditThreadView, self ).post_process_form( form )
        T = current.T
        req_link = A( T( 'View thread # ' ) + str( self.record_id ),
                      _href = URL( c=self.controller_name,
                                   f='view',
                                   args=[ self.record_id ] ) )
        term.printDebug( 'req_link: %s' % repr( req_link ) )
        term.printDebug( 'self.record: %s' % repr( self.record ) )
        self.set_result( data=dict( message=T( 'Thread # ' ) + self.record_id,
                                    req_link=req_link ) )
