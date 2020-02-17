# -*- coding: utf-8 -*-

import sys
import traceback

from forum_threads import thread_factory
from m16e.db import db_tables
from gluon import SQLFORM, IS_IN_DB, TABLE, TR, INPUT, TEXTAREA, TD, BUTTON, H2, H3, P
from gluon import current, FORM
from m16e import mpmail
from m16e import term
from m16e.db import attach_factory
from m16e.kommon import DT, K_ROLE_ADMIN, to_utf8
from m16e.user_factory import is_in_group
from m16e.views.edit_base_view import BaseFormView
from gluon.html import A, DIV, SPAN, URL

class ThreadEditView( BaseFormView ):
    controller_name = 'forum'
    function_name = 'edit'


    def __init__( self, db ):
        super( ThreadEditView, self ).__init__( db )
        self.table_model = db_tables.get_table_model( 'thread', db=db )
        self.tm_model = db_tables.get_table_model( 'thread_msg', db=db )


    def do_process( self ):
        return super( ThreadEditView, self ).do_process()


    def pre_del( self ):
        super( ThreadEditView, self ).pre_del()
        db = self.db
        request = current.request
        term.printLog( 'deleting thread #%s' % self.record_id )

        tm_model = db_tables.get_table_model( 'thread_msg', db=db )
        ts_model = db_tables.get_table_model( 'thread_subscriber', db=db )
        tv_model = db_tables.get_table_model( 'thread_vote', db=db )
        q_sql = (db.thread_msg.thread_id == self.record_id)
        tm_model.delete( q_sql )

        q_sql = (db.thread_subscriber.thread_id == self.record_id)
        ts_model.delete( q_sql )

        q_sql = (db.thread_vote.thread_id == self.record_id)
        tv_model.delete( q_sql )

        return  self.set_result( redirect=URL( c=self.controller_name,
                                               f='index' ) )


    def post_process_form( self, form ):
        super( ThreadEditView, self ).post_process_form( form )
        T = current.T
        db = self.db
        menu_path = DIV( _id='menu_path_div', _class='menu_path' )
        menu_path.append( A( T( 'Threads' ),
                             _href=URL( c=self.controller_name,
                                        f='index' ) ) )

        self.set_result( data=dict( menu_path=menu_path,
                                    message=T( 'Thread # ' ) + self.record_id ) )


    def reopen( self ):
        T = current.T
        try:
            self.fetch_record( fetch_id=True )
            self.update_record( dict( thread_status_id=thread_factory.TSTATUS_OPEN ) )
            link = URL( c=self.controller_name,
                        f=self.function_name,
                        args=self.record_id,
                        scheme=True,
                        host=True )
            message = '%s: %s' % (T( 'Ticket reopened' ), link)
            u_list = thread_factory.get_support_user_list( db=self.db )
            prefix = 'Re: [%s][Reopened] ' % (to_utf8( self.record.thread_type_id.thread_type_name ).upper())
            mpmail.queue_mail( mpmail.DEFAULT_BCC,
                               cc=[ u.email for u in u_list ],
                               subject=prefix + self.record.short_description,
                               text_body=message )

            return self.set_result( redirect=URL( c=self.controller_name,
                                                  f=self.function_name,
                                                  args=[ self.record_id ] ),
                                    force_redirect=True,
                                    message=T( 'Please, fill a comment describing the motive for reopening' ) )
        except:
            t, v, tb = sys.exc_info()
            traceback.print_exception( t, v, tb )
            raise


