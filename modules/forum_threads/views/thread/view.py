# -*- coding: utf-8 -*-
import sys
import traceback

from app import db_sets
from forum_threads import thread_factory
from gluon import current, SQLFORM, IS_NOT_EMPTY, URL, FORM
from gluon.storage import Storage
from m16e import term, htmlcommon, mpmail, user_factory
from m16e.db import db_tables, event_factory
from m16e.kommon import DT, K_ROLE_USER, K_ROLE_ADMIN
from m16e.user_factory import is_in_group
from m16e.views.edit_base_view import BaseFormView
from pydal import Field

ACT_ADD_COMMENT = 'act_add_comment'
ACT_ALTER_COMMENT = 'act_alter_comment'
ACT_DEL_COMMENT = 'act_del_comment'
ACT_SUBSCRIBE_USER = 'act_subscribe_user'
ACT_SUBSCRIBE_GROUP = 'act_subscribe_group'


class ThreadDisplayView( BaseFormView ):
    controller_name = 'forum'
    function_name = 'view'


    def __init__( self, db ):
        super( ThreadDisplayView, self ).__init__( db )
        self.table_model = db_tables.get_table_model( 'thread', db=db )
        # self.thread_id = None
        # self.thread = None
        self.tm_list = []


    def do_process( self ):
        return super( ThreadDisplayView, self ).do_process()


    def get_redirect_on_insert( self ):
        return URL( c=self.controller_name,
                    f='view',
                    args=[ self.record_id ] )


    def process_pre_validation_actions( self ):
        super( ThreadDisplayView, self ).process_pre_validation_actions()
        request = current.request
        auth = current.auth
        T = current.T
        db = self.db
        term.printDebug( 'vars: %s' % repr( request.vars ) )
        if not is_in_group( K_ROLE_ADMIN ) \
            and self.record.thread_type_id != thread_factory.TTYPE_OPEN_DISCUSSION:
            self.tm_list = []
            event_factory.store_event( user_factory.EVT_ORIGIN_PERMISSIONS,
                                       T( 'Wrong thread (%(t)s)', dict( t=self.record_id ) ),
                                       user_id=auth.user.id )
            return self.set_result( redirect=URL( c=self.controller_name,
                                                  f='open_discussions' ),
                                    message=T( 'Thread doesn\'t exist' ) )
        if self.action and self.action.startswith( ACT_ADD_COMMENT + '_' ):
            parent_thread_msg_id = int( self.action[ len( ACT_ADD_COMMENT ) + 1 : ] )
            msg_text = request.vars[ 'cmt_msg_text_%d' % parent_thread_msg_id ]
            tm_id = thread_factory.add_comment( self.record_id,
                                                msg_text,
                                                parent_thread_msg_id=parent_thread_msg_id,
                                                db=db )
            return self.set_result( redirect=URL( c=self.controller_name,
                                                  f=self.function_name,
                                                  args=[ self.record_id ],
                                                  anchor=thread_factory.CMT_ANCHOR_MASK % tm_id),
                                    message=T( 'Comment added' ) )

        if self.action and self.action.startswith( ACT_ALTER_COMMENT + '_' ):
            thread_msg_id = int( self.action[ len( ACT_ALTER_COMMENT ) + 1 : ] )
            msg_text = request.vars[ 'edt_msg_text_%d' % thread_msg_id ]
            send_mail = bool( request.vars[ 'ta_edt_send_mail_%d' % thread_msg_id ] )
            # markup = request.vars[ 'edt_markup_%d' % thread_msg_id ]
            if thread_msg_id > 0:
                thread_factory.alter_comment( thread_msg_id,
                                              msg_text,
                                              send_mail=send_mail,
                                              db=db )
                return self.set_result( redirect=URL( c=self.controller_name,
                                                      f=self.function_name,
                                                      args=[ self.record_id ],
                                                      anchor=thread_factory.CMT_ANCHOR_MASK % thread_msg_id ),
                                        message=T( 'Comment changed' ) )
            msg_title = request.vars[ 'edt_msg_title_%d' % thread_msg_id ]
            thread_factory.alter_post( self.record_id,
                                       thread_title=msg_title,
                                       thread_msg=msg_text,
                                       send_mail=send_mail,
                                       db=db )
            return self.set_result( redirect=URL( c=self.controller_name,
                                                  f=self.function_name,
                                                  args=[ self.record_id ] ),
                                    message=T( 'Post changed' ) )

        if self.action and self.action.startswith( ACT_DEL_COMMENT + '_' ):
            thread_msg_id = int( self.action[ len( ACT_DEL_COMMENT ) + 1 : ] )
            thread_factory.delete_thread_msg( thread_msg_id, db=db )
            return self.set_result( redirect=URL( c=self.controller_name,
                                                  f=self.function_name,
                                                  args=[ self.record_id ] ),
                                    message=T( 'Comment removed' ) )


        if self.action and self.action == ACT_SUBSCRIBE_USER:
            user_id = request.vars.selected_user
            ts_id = thread_factory.subscribe_user( self.record_id, user_id, db=db )
            if ts_id < 0:
                return self.set_result( message=T( 'Already subscribed' ) )
            # au = db.auth_user[ user_id ]
            # mpmail.queue_mail( au.email,
            #                    subject=T( 'You were added to thread #%(t)s',
            #                               dict( t=self.record_id ) ),
            #                    text_body=T( 'You were added to thread #%(t)s by user %(u)s. View thread here: %(url)s',
            #                                 dict( t='%d (%s)' % (self.record_id, self.record.thread_title),
            #                                       u=auth.user.first_name,
            #                                       url=URL( c=self.controller_name,
            #                                                f=self.function_name,
            #                                                args=[ self.record_id ],
            #                                                host=True ) ) ) )
            return self.set_result( redirect=URL( c=self.controller_name,
                                                  f=self.function_name,
                                                  args=[ self.record_id ] ),
                                    message=T( 'Suscribed' ) )

        if self.action and self.action == ACT_SUBSCRIBE_GROUP:
            group_id = request.vars.selected_group
            ts_id = thread_factory.subscribe_group( self.record_id, group_id, db=db )
            if ts_id < 0:
                return self.set_result( message=T( 'Already subscribed' ) )
            return self.set_result( redirect=URL( c=self.controller_name,
                                                  f=self.function_name,
                                                  args=[ self.record_id ] ),
                                    message=T( 'Suscribed' ) )


    def fetch_record( self, fetch_id=False ):
        super( ThreadDisplayView, self ).fetch_record( fetch_id=fetch_id )
        if self.record_id:
            self.tm_list = thread_factory.get_thread_messages( self.record_id )
        return self.record


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
        form = SQLFORM.factory()
        return form


    def pre_ins( self, upd ):
        super( ThreadDisplayView, self ).pre_ins( upd )
        auth = current.auth
        upd.msg_ts = DT.now()
        upd.auth_user_id = auth.user.id
        upd.thread_id = self.record_id


    def do_insert_record( self, upd ):
        db = self.db
        tm_model = db_tables.get_table_model( 'thread_msg', db=db )
        tm_model.insert( upd )


    def process_form( self, form ):
        # super( ThreadDisplayView, self ).process_form( form )
        self.errors = []


    def post_process_form( self, form ):
        super( ThreadDisplayView, self ).post_process_form( form )
        auth = current.auth
        db = self.db
        t_model = db_tables.get_table_model( 'thread', db=db )
        ts_model = db_tables.get_table_model( 'thread_subscriber', db=db )
        thread = t_model[ self.record_id ]
        tm_model = db_tables.get_table_model( 'thread_msg', db=db )
        q_sql = (db.thread_msg.thread_id == self.record_id)
        cmt_list = tm_model.select( q_sql, orderby='msg_ts' )
        thread_list = thread_factory.get_thread_as_UL( self.record_id, db=db )
        thread_cmd_row = thread_factory.get_thread_command_row_div( self.record_id, db=db )
        active_thread_list = thread_factory.get_thread_list( active=True, db=db )
        subscriber_list = thread_factory.get_subscriber_list( self.record_id, db=db )
        has_subscribed = False
        for s in subscriber_list:
            if s.auth_user_id == auth.user.id:
                has_subscribed = True
                break
        # q_sql = (db.auth_user.registration_key == '')
        # q_sql &= (db.auth_user.id != auth.user.id)
        # rows = db( q_sql ).select( orderby='first_name' )

        # user_list = [ (r.id, '%s <%s>' % (r.first_name, r.email)) for r in rows ]
        user_list = user_factory.get_user_list_as_options( insert_blank=True,
                                                           db=db )
        group_list = user_factory.get_group_list_as_options( insert_blank=True,
                                                             db=db )
        # q_sql = (db.auth_group.id > 0)
        # rows = db( q_sql ).select( orderby='description' )
        # group_list = [ (r.id, r.description) for r in rows ]
        # group_list.insert( 0, ('', '') )

        user_sel = htmlcommon.get_selection_field( 'selected_user', options=user_list, use_bootstrap_live_search=True )
        group_sel = htmlcommon.get_selection_field( 'selected_group', options=group_list, use_bootstrap_live_search=True )
        self.set_result( data=dict( thread=thread,
                                    cmt_list=cmt_list,
                                    thread_list=thread_list,
                                    thread_cmd_row=thread_cmd_row,
                                    active_thread_list=active_thread_list,
                                    subscriber_list=subscriber_list,
                                    has_subscribed=has_subscribed,
                                    user_sel=user_sel,
                                    group_sel=group_sel ) )


    def subscribe( self ):
        request = current.request
        T = current.T
        auth = current.auth
        db = self.db
        thread_id = int( request.args( 0 ) )
        auth_user_id = auth.user.id
        ts_model = db_tables.get_table_model( 'thread_subscriber', db=db )
        q_sql = (db.thread_subscriber.thread_id == thread_id)
        q_sql &= (db.thread_subscriber.auth_user_id == auth.user.id)
        ts = ts_model.select( q_sql ).first()
        if ts:
            return self.set_result( message=T( 'Already subscribed' ) )

        ts_model.insert( dict( thread_id=thread_id,
                               auth_user_id=auth_user_id ) )

        return self.set_result( redirect=URL( c=self.controller_name,
                                              f=self.function_name,
                                              args=[ thread_id ] ),
                                message=T( 'Suscribed' ) )


    def unsubscribe( self ):
        request = current.request
        T = current.T
        auth = current.auth
        db = self.db
        thread_id = int( request.args( 0 ) )
        auth_user_id = auth.user.id
        ts_model = db_tables.get_table_model( 'thread_subscriber', db=db )
        q_sql = (db.thread_subscriber.thread_id == thread_id)
        q_sql &= (db.thread_subscriber.auth_user_id == auth_user_id)
        ts_model.delete( q_sql )
        return self.set_result( redirect=URL( c=self.controller_name,
                                              f=self.function_name,
                                              args=[ thread_id ] ),
                                message=T( 'Unsubscribed' ) )


    def unsubscribe_user( self ):
        request = current.request
        T = current.T
        auth = current.auth
        db = self.db
        thread_id = int( request.args( 0 ) )
        auth_user_id = int( request.args( 1 ) )
        ts_model = db_tables.get_table_model( 'thread_subscriber', db=db )
        q_sql = (db.thread_subscriber.thread_id == thread_id)
        q_sql &= (db.thread_subscriber.auth_user_id == auth_user_id)
        ts_model.delete( q_sql )
        return self.set_result( redirect=URL( c=self.controller_name,
                                              f=self.function_name,
                                              args=[ thread_id ] ),
                                message=T( 'Unsubscribed' ) )


    def ajax_vote_comment( self ):
        '''
        args[0]: thread_id
        args[1]: thread_msg_id
        args[2]: vote
        :return:
        '''
        request = current.request
        T = current.T
        db = self.db
        auth = current.auth

        try:
            thread_id = int( request.args( 0 ) )
            thread_msg_id = int( request.args( 1 ) )
            vote = int( request.args( 2 ) )
            thread_factory.vote_thread( thread_id,
                                        thread_msg_id,
                                        vote,
                                        auth_user_id=auth.user.id,
                                        db=db )
            # if thread_msg_id:
            #     tm_id = thread_msg_id
            # else:
            #     tm_id = None
            # tv_model = db_tables.get_table_model( 'thread_vote', db=db )
            # q_sql = (db.thread_vote.thread_id == thread_id)
            # q_sql &= (db.thread_vote.thread_msg_id == tm_id)
            # q_sql &= (db.thread_vote.auth_user_id == auth.user.id)
            # tv = tv_model.select( q_sql ).first()
            # if tv:
            #     if vote:
            #         tv_model.update_by_id( tv.id,
            #                                dict( vote=vote ) )
            #     else:   # vote was cancelled, delete it
            #         tv_model.delete( q_sql )
            # else:
            #     data = dict( auth_user_id=auth.user.id,
            #                  thread_id=thread_id,
            #                  vote=vote,
            #                  vote_ts=DT.now() )
            #     if thread_msg_id:
            #         data[ 'thread_msg_id' ] = thread_msg_id
            #     tv_model.insert( data )
            css_class_up = css_class_down = 'vote_display has_not_voted'
            if vote > 0:
                css_class_up = 'vote_display has_voted_up'
            elif vote < 0:
                css_class_down = 'vote_display has_voted_down'

            up_count, down_count = thread_factory.get_vote_count( thread_id=thread_id,
                                                                  thread_msg_id=thread_msg_id,
                                                                  db=db )
            data = dict( vote_count_up='vote_count_up_%d_%d' % (thread_id, thread_msg_id),
                         span_vote_count_up='span_vote_count_up_%d_%d' % (thread_id, thread_msg_id),
                         vote_count_down='vote_count_down_%d_%d' % (thread_id, thread_msg_id),
                         span_vote_count_down='span_vote_count_down_%d_%d' % (thread_id, thread_msg_id),
                         u=up_count,
                         d=down_count,
                         css_class_up=css_class_up,
                         css_class_down=css_class_down )
            js = '''
                jQuery( '#%(vote_count_up)s' ).html( '(%(u)s)' );
                jQuery( '#%(span_vote_count_up)s' ).removeClass( 'has_voted_up has_voted_down has_not_voted' );
                jQuery( '#%(span_vote_count_up)s' ).addClass( '%(css_class_up)s' );
                jQuery( '#%(vote_count_down)s' ).html( '(%(d)s)' );
                jQuery( '#%(span_vote_count_down)s' ).removeClass( 'has_voted_up has_voted_down has_not_voted' );
                jQuery( '#%(span_vote_count_down)s' ).addClass( '%(css_class_down)s' );
            ''' % data

            term.printLog( 'jq: %s' % (js) )
            return js
        except:
            t, v, tb = sys.exc_info( )
            traceback.print_exception( t, v, tb )
            raise
        return ''




