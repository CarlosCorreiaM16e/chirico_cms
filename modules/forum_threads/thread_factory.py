# -*- coding: utf-8 -*-
from app import db_sets
from forum_threads.db import forum_events
from m16e.db import db_tables
from gluon import current, URL, UL, LI, DIV, SPAN, A, H4, XML, IS_NOT_EMPTY, B, BUTTON, LABEL, MARKMIN, H3
from gluon.storage import Storage
from m16e import mpmail, htmlcommon, user_factory
from m16e import term
from m16e.kommon import DT, K_ROLE_SUPPORT, to_utf8, K_ROLE_ADMIN, K_ROLE_DEVELOPER
from m16e.ui import elements
from m16e.user_factory import is_in_group
from gluon.tools import prettydate


CMT_ANCHOR_MASK = 'c%d'

TSTATUS_OPEN = 1
TSTATUS_SUSPENDED = 2
TSTATUS_CLOSED = 100

TTYPE_OPEN_DISCUSSION = 1
TTYPE_RESTRICTED_DISCUSSION = 1


def get_thread_messages( thread_id, db=None ):
    if not db:
        db = current.db
    tm_model = db_tables.get_table_model( 'thread_msg', db=db )
    q_sql = (db.thread_msg.thread_id == thread_id)
    tm_list = tm_model.select( q_sql, orderby='msg_ts' )
    return tm_list


def get_thread_status_list( db=None ):
    if not db:
        db = current.db
    rs_model = db_tables.get_table_model( 'thread_status', db=db )
    rs_list = rs_model.select( orderby='preferred_order' )
    return rs_list


def get_thread_type_list( db=None ):
    if not db:
        db = current.db
    rt_model = db_tables.get_table_model( 'thread_type', db=db )
    rt_list = rt_model.select( orderby='preferred_order' )
    return rt_list


def is_visible_by_user( auth, thread_tuple, db=None ):
    if not db:
        db = current.db
    if not auth.user:
#         term.printDebug( 'NO USER' )
        return False
    if is_in_group( 'admin' ):
#         term.printDebug( 'USER (%d-%s) IS ADMIN' % (auth.user.id, auth.user.email ) )
        return True
    if auth.user.id == thread_tuple['auth_user_id']:
#         term.printDebug( 'REQUEST USER' )
        return True
    if is_user_in_subscribers( auth.user.id, thread_tuple[ 'id' ], db=db ):
#         term.printDebug( 'SUBSCRIBER USER' )
        return True
    return False


def is_user_in_subscribers( auth_user_id, thread_id, db=None ):
    if not db:
        db = current.db
    ts_model = db_tables.get_table_model( 'thread_subscriber', db=db )
    q_sql = (db.thread_subscriber.thread_id == thread_id)
    q_sql &= (db.thread_subscriber.auth_user_id == auth_user_id)
    req_subs = ts_model.count( q_sql )
    term.printDebug( 'sql: %s' % str( db._lastsql ) )
    return req_subs > 0


def get_last_msg_time( thread_id, db=None ):
    if not db:
        db = current.db
    query = '''
        select max(msg_ts) from thread_msg where thread_id = %(thread_id)s
      '''
    args = { 'thread_id': thread_id }
    time = db.executesql( query, placeholders = args )
    return time[0][0]


def has_user_voted_thread( auth_user_id, thread_id, db=None ):
    '''
    <auth_user_id> has voted <thread_id>?
    '''
    if not db:
        db = current.db
    rv_model = db_tables.get_table_model( 'thread_vote', db=db )
    q_sql = (db.thread_vote.thread_id == thread_id)
    q_sql &= (db.thread_vote.auth_user_id == auth_user_id)
    count = rv_model.count( q_sql )
    return (count > 0)


def get_thread_subscribers( thread_id, db=None ):
    if not db:
        db = current.db
    query = '''
        select u.*
        from auth_user u
        join thread_subscriber s on s.auth_user_id = u.id
        where s.thread_id = %(thread_id)s
        order by first_name
    '''
    args = { 'thread_id': thread_id }
    rows = db.executesql( query, placeholders = args, as_dict=True )
    row_list = []
    for r in rows:
        row_list.append( Storage( r ) )
    return row_list

def get_thread_voters( thread_id, db=None ):
    if not db:
        db = current.db
    query = '''
        select v.*, u.email
        from thread_vote v join auth_user u on v.auth_user_id = u.id
        where thread_id = %(thread_id)s
    '''
    args = { 'thread_id': thread_id }
    votes = db.executesql( query, placeholders=args, as_dict=True )
    row_list = []
    for r in votes:
        row_list.append( Storage( r ) )
    return row_list

def get_thread_vote_count( thread_id, db=None ):
    if not db:
        db = current.db
    query = '''
        select count(*)
        from thread_vote
        where thread_id = %s
    '''
    args = [thread_id]
    votes = db.executesql( query, placeholders=args )
#     term.printDebug( 'sql: %s' % (db._lastsql) )
#     term.printDebug( repr(args) )
    return votes[0][0]

#   return len( reqSubs )

def get_mails_for_thread( thread_id, db=None ):
    if not db:
        db = current.db
    query = '''
        select email
        from auth_user u
            join thread_subscriber s on s.auth_user_id = u.id
        where
            s.thread_id = %d
    ''' % (thread_id)
    u_list = db.executesql( query, as_dict=True )
    mails = [ u[ 'email' ] for u in u_list ]
    return mails

# def do_send_mail( thread_id, subject, message='', db=None ):

def notify_subscribers( thread_id, subject, message='', db=None ):
    if not db:
        db = current.db
    mail = current.mail
    subscribers = get_mails_for_thread( thread_id, db=db )
    user_factory.notify_users( subscribers, subject, message, db=db )
    # for s in subscribers:
    #     mpmail.queue_mail( s,
    #                        cc=[mail.settings.sender],
    #                        subject=subject,
    #                        text_body=message,
    #                        db=db )


def update_thread_status( thread_id, new_status_id, send_mail=True, db=None ):
    T = current.T
    if not db:
        db = current.db
    t_model = db_tables.get_table_model( 'thread', db=db )
    upd = Storage( thread_status_id=new_status_id )
    t = t_model[ thread_id ]
    closed = False
    if not t.closed_time \
      and new_status_id == TSTATUS_CLOSED:
        upd.closed_time = DT.now()
        closed = True
    t_model.update_by_id( thread_id, upd )
    if send_mail:
        link = URL( c='forum',
                    f='view',
                    args=[ thread_id ],
                    scheme=True,
                    host=True )
        message = '%s: %s\n\n' % (T( 'Thread changed' ), link)
        # term.printDebug( 'upd: ' + repr( upd ) )
        message += '\n' + T( 'Status changed to' ) + ': '
        rs_model = db_tables.get_table_model( 'thread_status' )
        rs = rs_model[ new_status_id ]
        message += rs.thread_status_name
        term.printLog( 'send_mail: %s' % (repr( send_mail )) )
        rt_model = db_tables.get_table_model( 'thread_type', db=db )
        rt = rt_model[ t.thread_type_id ]
        subject = '[%s]: %s' % (rt.thread_type_name,
                                t.short_description)
        if closed:
            subject += ' (' + T( 'closed' ) + ')'
        notify_subscribers( thread_id,
                            subject,
                            message=message,
                            db=db )

def add_comment( thread_id, msg_text, parent_thread_msg_id=None, send_mail=True, db=None ):
    T = current.T
    if not db:
        db = current.db
    t_model = db_tables.get_table_model( 'thread', db=db )
    tm_model = db_tables.get_table_model( 'thread_msg', db=db )
    thread = t_model[ thread_id ]
    data = Storage( thread_id=thread_id,
                    auth_user_id=user_factory.get_auth_user_id( db=db ),
                    msg_text=msg_text,
                    markup='M' )
    if parent_thread_msg_id:
        data.parent_thread_msg_id = parent_thread_msg_id
    tm_id = tm_model.insert( data )
    forum_events.store_comment_created( tm_id, db=db )
    if send_mail:
        args = [ thread_id, tm_id ]
        if parent_thread_msg_id:
            args.append( parent_thread_msg_id )
        link = URL( c='forum',
                    f='view',
                    args=args,
                    scheme=True,
                    host=True )
        user = user_factory.get_auth_user( db=db )
        message = '%s: \n\n%s' % (T( 'Comment added to thread "%(t)s" by %(user)s',
                                     dict( user=user.first_name,
                                           t=thread.thread_title ) ),
                                  link)
        # term.printDebug( 'upd: ' + repr( upd ) )
        rt_model = db_tables.get_table_model( 'thread_type', db=db )
        rt = rt_model[ thread.thread_type_id ]
        term.printDebug( 'thread: %s' % repr( thread ) )
        subject = '[%s][NEW-CMT]: %s' % (rt.thread_type_name,
                                         thread.thread_title)
        notify_subscribers( thread_id,
                            subject,
                            message=message,
                            db=db )

    return tm_id


def subscribe_user( thread_id, user_id, db=None ):
    if not db:
        db = current.db
    T = current.T
    ts_model = db_tables.get_table_model( 'thread_subscriber', db=db )
    t_model = db_tables.get_table_model( 'thread', db=db )
    thread = t_model[ thread_id ]
    q_sql = (db.thread_subscriber.thread_id == thread_id)
    q_sql &= (db.thread_subscriber.auth_user_id == user_id)
    ts = ts_model.select( q_sql ).first()
    if ts:
        return -1

    ts_id = ts_model.insert( dict( thread_id=thread_id,
                                   auth_user_id=user_id ) )
    au = db.auth_user[ user_id ]
    subject = '[%s][SUBSCRIBE]: %s' % (thread.thread_type_id.thread_type_name,
                                       thread.thread_title)
    link = URL( c='forum',
                f='view',
                args=[ thread_id ],
                scheme=True,
                host=True )
    user = user_factory.get_auth_user( db=db )
    message = T( 'You have been subscribed to thread "%(t)s" (%(url)s) by user %(u)s',
                 dict( t=thread.thread_title,
                       url=link,
                       u=user.first_name ) )
    user_factory.notify_users( user.email, subject, message, db=db )
    return ts_id


def subscribe_group( thread_id, group_id, db=None ):
    if not db:
        db = current.db
    T = current.T
    sql = '''
        select au.*
        from auth_membership am
            join auth_user au on am.user_id = au.id
        where 
            am.group_id = %(g)s and
            au.id not in ( select auth_user_id from thread_subscriber where thread_id = %(t)s )
    ''' % dict( g=group_id, t=thread_id )
    au_list = [ Storage( au ) for au in user_factory.get_user_list( group_id=group_id, db=db ) ]
    t_model = db_tables.get_table_model( 'thread', db=db )
    ts_model = db_tables.get_table_model( 'thread_subscriber', db=db )
    thread = t_model[ thread_id ]
    subject = '[%s][SUBSCRIBE]: %s' % (thread.thread_type_id.thread_type_name,
                                       thread.thread_title)
    link = URL( c='forum',
                f='view',
                args=[ thread_id ],
                scheme=True,
                host=True )
    user = user_factory.get_auth_user( db=db )
    message = T( 'You have been subscribed to thread "%(t)s" (%(url)s) by user %(u)s',
                 dict( t=thread.thread_title,
                       url=link,
                       u=user.first_name ) )
    for au in au_list:
        ts_model.insert( dict( thread_id=thread_id,
                               auth_user_id=au.id ) )

    user_factory.notify_users( [ au.email for au in au_list ], subject, message, db=db )


def alter_post( thread_id, thread_title=None, thread_msg=None, send_mail=True, db=None ):
    T = current.T
    if not db:
        db = current.db
    t_model = db_tables.get_table_model( 'thread', db=db )
    data = Storage()
    if thread_title:
        data.thread_title = thread_title
    if thread_msg:
        data.thread_msg = thread_msg
    if not data:
        return

    t_model.update_by_id( thread_id, data, print_query=True )
    forum_events.store_thread_updated( thread_id, db=db )
    if send_mail:
        t = t_model[ thread_id ]
        subject = '[%s][POST-UPD]: %s' % (t.thread_type_id.thread_type_name,
                                          t.thread_title)
        args = [ thread_id ]
        link = URL( c='forum',
                    f='view',
                    args=args,
                    scheme=True,
                    host=True )
        user = user_factory.get_auth_user( db=db )
        message = '%s: \n\n%s' % (T( 'Post "%(thread_title)s" changed by %(user)s',
                                        dict( thread_title=t.thread_title,
                                              user=user.first_name ) ),
                                     link)
        notify_subscribers( thread_id,
                            subject,
                            message=message,
                            db=db )


def alter_comment( thread_msg_id, msg_text, send_mail=True, db=None ):
    T = current.T
    if not db:
        db = current.db
    tm_model = db_tables.get_table_model( 'thread_msg', db=db )
    upd = Storage( msg_text=msg_text )
    tm_model.update_by_id( thread_msg_id, upd )
    forum_events.store_comment_updated( thread_msg_id, db=db )
    if send_mail:
        tm = tm_model[ thread_msg_id ]
        subject = '[%s][COMMENT-UPD]: %s' % (tm.thread_id.thread_type_id.thread_type_name,
                                             tm.thread_id.thread_title)
        link = URL( c='forum',
                    f='view',
                    args=[ tm.thread_id ],
                    scheme=True,
                    host=True,
                    anchor=CMT_ANCHOR_MASK % thread_msg_id )
        user = user_factory.get_auth_user( db=db )
        message = '%s %s: \n\n%s' % (T( 'Comment changed by' ),
                                     user.first_name,
                                     link)
        notify_subscribers( tm.thread_id,
                            subject,
                            message=message,
                            db=db )


def vote_thread( thread_id, thread_msg_id, vote, auth_user_id=None, db=None ):
    T = current.T
    if not db:
        db = current.db
    if auth_user_id:
        user = db.auth_user[ auth_user_id ]
    else:
        user = user_factory.get_auth_user( db=db )
        auth_user_id = user.id
    t_model = db_tables.get_table_model( 'thread', db=db )
    tv_model = db_tables.get_table_model( 'thread_vote', db=db )
    q_sql = (db.thread_vote.thread_id == thread_id)
    q_sql &= (db.thread_vote.thread_msg_id == thread_msg_id)
    q_sql &= (db.thread_vote.auth_user_id == auth_user_id)
    tv = tv_model.select( q_sql ).first()
    if tv:
        if vote:
            tv_model.update_by_id( tv.id,
                                   dict( vote=vote ) )
        else:  # vote was cancelled, delete it
            tv_model.delete( q_sql )
    else:
        data = dict( auth_user_id=auth_user_id,
                     thread_id=thread_id,
                     vote=vote,
                     vote_ts=DT.now() )
        if thread_msg_id:
            data[ 'thread_msg_id' ] = thread_msg_id
        tv_model.insert( data )
    t = t_model[ thread_id ]
    d = dict( user=user.first_name )
    if vote > 0:
        s_vote = 'VOTE_UP'
        v_msg = T( 'User %(user)s has voted up message', d )
    elif vote < 0:
        s_vote = 'VOTE_DOWN'
        v_msg = T( 'User %(user)s has voted down message', d )
    else:
        s_vote = 'DEL_VOTE'
        v_msg = T( 'User %(user)s removed vote from message', d )
    subject = '[%s][%s]: %s' % (t.thread_type_id.thread_type_name,
                                s_vote,
                                t.thread_title)
    link = URL( c='forum',
                f='view',
                args=[ thread_id ],
                scheme=True,
                host=True,
                anchor=CMT_ANCHOR_MASK % thread_msg_id )
    message = '%s: \n\n%s' % (v_msg, link)
    notify_subscribers( thread_id,
                        subject,
                        message=message,
                        db=db )


def get_thread_status_css_class( thread_status_id ):
    css_class = 'req_status_solving'
    if thread_status_id in (TSTATUS_OPEN,):
        css_class = 'req_status_new'
    elif thread_status_id == TSTATUS_SUSPENDED:
        css_class = 'req_status_reopened'
    elif thread_status_id == TSTATUS_CLOSED:
        css_class = 'req_status_closed'
    return css_class


def user_may_edit_thread( thread_id=None,
                           thread_msg_id=None,
                           thread_msg_attach_id=None,
                           db=None ):
    if is_in_group( K_ROLE_SUPPORT ):
        return True
    term.printDebug( 'thread_id: %s' % repr( thread_id ) )
    if not db:
        db = current.db
    auth = current.auth
    t_model = db_tables.get_table_model( 'thread', db=db )
    if not thread_id:
        if thread_msg_id is not None:
            rm_model = db_tables.get_table_model( 'thread_msg', db=db )
            rm = rm_model[ thread_msg_id ]
            thread_id = rm.thread_id
        elif thread_msg_attach_id is not None:
            rma_model = db_tables.get_table_model( 'thread_msg_attach', db=db )
            rma = rma_model[ thread_msg_attach_id ]
            thread_id = rma.thread_msg_id.thread_id
    term.printDebug( 'thread_id: %s' % repr( thread_id ) )

    t = t_model[ thread_id ]
    term.printDebug( 't: %s' % repr( t ) )
    if t.auth_user_id == auth.user.id or not t.private_thread:
        return True
    return False


def get_support_user_list( db=None ):
    if not db:
        db = current.db
    sql = '''
        select au.*
        from auth_user au
            join auth_membership am on au.id = am.user_id
            join auth_group ag on ag.id = am.group_id
        where
             ag.role = 'support'
    '''
    rows = db.executesql( sql, as_dict=True )
    return [ Storage( r ) for r in rows ]


def delete_thread( thread_id, db=None ):
    if not db:
        db = current.db
    t_model = db_tables.get_table_model( 'thread', db=db )
    rm_model = db_tables.get_table_model( 'thread_msg', db=db )
    rs_model = db_tables.get_table_model( 'thread_subscriber', db=db )
    rv_model = db_tables.get_table_model( 'thread_vote', db=db )
    # delete thread_msg
    q = (db.thread_msg.thread_id == thread_id)
    rm_model.delete( q )
    # delete thread_subscriber
    q = (db.thread_subscriber.thread_id == thread_id)
    rs_model.delete( q )
    # delete thread_vote
    q = (db.thread_vote.thread_id == thread_id)
    rv_model.delete( q )
    # delete thread
    q = (db.thread.id == thread_id)
    t_model.delete( q )


def delete_thread_msg( thread_msg_id, db=None ):
    if not db:
        db = current.db
    auth = current.auth
    tm_model = db_tables.get_table_model( 'thread_msg', db=db )
    tm = tm_model[ thread_msg_id ]
    if not is_in_group( K_ROLE_DEVELOPER ) and auth.user.id != tm.auth_user_id:
        raise Exception( 'Thread #%d has comments' % tm.id )
    tv_model = db_tables.get_table_model( 'thread_vote', db=db )
    q_sql = (db.thread_msg.parent_thread_msg_id == thread_msg_id)
    rows = tm_model.select( q_sql, orderby='id desc' )
    for r in rows:
        delete_thread_msg( r.id, db=db )
    q_sql = (db.thread_vote.thread_msg_id == thread_msg_id)
    tv_model.delete( q_sql )
    q_sql = (db.thread_msg.id == thread_msg_id)
    tm_model.delete( q_sql )


def get_thread_msg_comments( thread_msg_id, db=None ):
    if not db:
        db = current.db
    tm_model = db_tables.get_table_model( 'thread_msg', db=db )
    q_sql = (db.thread_msg.parent_thread_msg_id == thread_msg_id)
    tm_list = tm_model.select( q_sql, orderby='msg_ts' )
    thread_msg_list = []
    for tm in tm_list:
        thread_msg_list.append( Storage( tm=tm,
                                         children=get_thread_msg_comments( tm.id, db=db ) ) )
    return thread_msg_list


def get_thread_as_tree( thread_id, db=None ):
    '''
    :param thread_id:
    :param db:
    :return: [ { 'tm': {}, 'children': [ ] }, ]
    '''
    if not db:
        db = current.db
    t_model = db_tables.get_table_model( 'thread', db=db )
    tm_model = db_tables.get_table_model( 'thread_msg', db=db )
    thread = t_model[ thread_id ]
    q_sql = (db.thread_msg.thread_id == thread_id)
    q_sql &= (db.thread_msg.parent_thread_msg_id == None)
    thread_list = []
    tm_list = tm_model.select( q_sql, orderby='msg_ts' )
    for tm in tm_list:
        thread_list.append( Storage( tm=tm,
                                     children=get_thread_msg_comments( tm.id, db=db ) ) )
    return thread_list


def _get_cmt_user_div( tm ):
    user_div = DIV( _class='col-md-6' )
    user_div.append( A( _name=CMT_ANCHOR_MASK % tm.tm.id ) )
    if is_in_group( K_ROLE_SUPPORT ):
        user_div.append( SPAN( '#%d: ' % tm.tm.id ) )
    user_div.append( SPAN( tm.tm.auth_user_id.first_name,
                           _class='tm_header_user' ) )
    return user_div


def user_has_voted( tm, db=None ):
    if not db:
        db = current.db
    auth = current.auth
    tv_model = db_tables.get_table_model( 'thread_vote', db=db )
    q_sql = (db.thread_vote.thread_id == tm.tm.thread_id)
    q_sql &= (db.thread_vote.thread_msg_id == tm.tm.id)
    q_sql &= (db.thread_vote.auth_user_id == auth.user.id)
    tv = tv_model.select( q_sql ).first()
    if tv:
        return tv.vote
    return 0


def get_vote_count( thread_id, thread_msg_id=None, db=None ):
    if not db:
        db = current.db
    tv_model = db_tables.get_table_model( 'thread_vote', db=db )
    def get_count( vote ):
        q_sql = (db.thread_vote.vote == vote)
        q_sql &= (db.thread_vote.thread_id == thread_id)
        tm_id = thread_msg_id
        if not tm_id:
            tm_id = None
        q_sql &= (db.thread_vote.thread_msg_id == tm_id)
        tv_count = tv_model.count( q_sql ) #, print_query=True )
        return tv_count

    up_count = get_count( 1 )
    down_count = get_count( -1 )
    return (up_count, down_count)


def _get_vote_comment_button( tm, vote, db=None ):
    if not db:
        db = current.db
    T = current.T
    v = user_has_voted( tm, db=db )
    vote_val = vote
    if v:
        if v == vote and vote > 0:
            css_class = 'has_voted_up'
            vote_val = 0
        elif v == vote and vote < 0:
            css_class = 'has_voted_down'
            vote_val = 0
        else:
            css_class = 'has_not_voted'
    else:
        css_class = 'has_not_voted'
    url = URL( c='forum',
               f='ajax_vote_comment',
               args=[ tm.tm.thread_id,
                      tm.tm.id,
                      vote_val ] )
    onclick = "ajax( '%(url)s', [], ':eval' ) " % dict( url=url )
    if vote > 0:    # vote UP
        icon = elements.ICON_THUMBS_UP
        direction = 'up'
    elif vote < 0:  # vote DOWN
        icon = elements.ICON_THUMBS_DOWN
        direction = 'down'
    else:
        raise ValueError( 'Illegal value for "vote": ' + repr( vote ) )
    tip = T( 'Vote ' + direction )
    if not vote_val:
        tip = T( 'Cancel vote' )
    bt = A( elements.get_bootstrap_icon( icon,
                                         dark_background=False,
                                         tip=tip ),
            _href='#',
            _onclick=onclick )
    # tv_model = db_tables.get_table_model( 'thread_vote', db=db )
    # q_sql = (db.thread_vote.thread_msg_id == tm.tm.id)
    # q_sql &= (db.thread_vote.vote > 0)
    # tv_count = tv_model.count( q_sql )
    return (bt, css_class)
    # return (bt, tv_count, css_class)


def get_vote_panel( tm, db=None ):
    if not db:
        db = current.db
    up_count, down_count = get_vote_count( tm.tm.thread_id, tm.tm.id, db=db )
    bt, css_class = _get_vote_comment_button( tm, 1, db=db )
    v_div = DIV( SPAN( bt,
                       SPAN( '(%d)' % up_count,
                             _class='vote_display_count',
                             _id='vote_count_up_%d_%d' % (tm.tm.thread_id, tm.tm.id) ),
                       _class='vote_display ' + css_class,
                       _id='span_vote_count_up_%d_%d' % (tm.tm.thread_id, tm.tm.id) ),
                 _class='col-md-6' )
    bt, css_class = _get_vote_comment_button( tm, -1, db=db )
    v_div.append( SPAN( bt,
                        SPAN( '(%d)' % down_count,
                              _class='vote_display_count',
                              _id='vote_count_down_%d_%d' % (tm.tm.thread_id, tm.tm.id) ),
                        _class='vote_display ' + css_class,
                        _id='span_vote_count_down_%d_%d' % (tm.tm.thread_id, tm.tm.id) ) )
    return v_div


def _get_cmt_ts( tm ):
    T = current.T
    ts_div = DIV( DIV( prettydate( tm.tm.msg_ts.replace( tzinfo=None), T ),
                        _class='tm_header_time',
                        _title=tm.tm.msg_ts.strftime( '%Y-%m-%d %H:%M' ) ),
                  _class='col-md-6 text-right' )
    return ts_div


def _get_header_div( tm, db=None ):
    if not db:
        db = current.db
    header_div = DIV( DIV( _get_cmt_user_div( tm ),
                           _get_cmt_ts( tm ),
                           _class='row' ),
                      _class='col-md-12' )
    return header_div


def _get_body_div( tm ):
    # if tm.tm.markup == db_sets.MARKUP_HTML:
    #     msg_text = XML( tm.tm.msg_text )
    # else:
    msg_text = MARKMIN( tm.tm.msg_text )
    body_div = DIV( DIV( DIV( SPAN( msg_text, _class='tm_body-msg' ),
                              _class='col-md-12 forum_comment' ),
                         _class='row' ),
                    _class='col-md-12' )
    return body_div


def get_thread_msg_comments_as_UL( thread_msg_list, db=None ):
    if not db:
        db = current.db
    T = current.T
    auth = current.auth
    ul = []
    for tm in thread_msg_list:
        forum_comment_box = DIV( _class='row forum_comment_box' )
        # get user + timestamp
        forum_comment_box.append( _get_header_div( tm, db=db ) )
        # get body
        forum_comment_box.append( _get_body_div( tm ) )
        forum_comment_box.append( DIV( _get_command_row_div( tm, db=db ),
                                       _class='col-md-12' ) )

        if auth.user.id == tm.tm.auth_user_id or is_in_group( K_ROLE_SUPPORT ):
            edt_div = DIV( _id='edt_msg_text_%d_row' % tm.tm.id,
                           _class='row',
                           _style='display: none;' )
            out_col = DIV( _class='col-md-12' )
            d_row = DIV( _class='row' )
            d_row.append( H3( T( 'Edit comment' ),
                              _class='col-md-8' ) )
            d_row.append( DIV( LABEL( T( 'Send mail' ), ':' ),
                               htmlcommon.get_checkbox( 'ta_edt_send_mail_%d' % tm.tm.id,
                                                        value=True,
                                                        input_id='ta_edt_send_mail_%d' % tm.tm.id ),
                               _class='col-md-4 text-right' ) )
            out_col.append( d_row )
            d_row = DIV( _class='row' )
            d_row.append( DIV( htmlcommon.get_textarea( 'edt_msg_text_%d' % tm.tm.id,
                                                        input_id='ta_edt_msg_text_%d' % tm.tm.id,
                                                        requires=IS_NOT_EMPTY(),
                                                        rows=4 ),
                               _class='col-md-12' ) )
            out_col.append( d_row )
            d_row = DIV( _class='row' )
            d_row.append( DIV( htmlcommon.get_button( T( 'Alter comment' ),
                                                      value='act_alter_comment_%d' % tm.tm.id,
                                                      css_class='btn btn-submit' ),
                               htmlcommon.get_button( T( 'Cancel' ),
                                                      bt_link='#',
                                                      on_click="jQuery( '#edt_msg_text_%d_row' ).hide();" % tm.tm.id,
                                                      css_class='btn btn-warning' ),
                               _class='col-md-12 text-center') )
            out_col.append( d_row )
            edt_div.append( out_col )

            # edt_div = DIV( DIV( DIV( DIV( H3( T( 'Edit comment' ),
            #                                   _class='col-md-12' ),
            #                               _class='row'),
            #                          htmlcommon.get_textarea( 'edt_msg_text_%d' % tm.tm.id,
            #                                                   input_id='ta_edt_msg_text_%d' % tm.tm.id,
            #                                                   requires=IS_NOT_EMPTY(),
            #                                                   rows=4 ),
            #                          _class='col-md-12' ),
            #                     DIV( htmlcommon.get_button( T( 'Alter comment' ),
            #                                                 value='act_alter_comment_%d' % tm.tm.id,
            #                                                 css_class='btn btn-submit' ),
            #                          htmlcommon.get_button( T( 'Cancel' ),
            #                                                 bt_link='#',
            #                                                 on_click="jQuery( '#edt_msg_text_%d_row' ).hide();" % tm.tm.id,
            #                                                 css_class='btn btn-warning' ),
            #                          _class='col-md-12 text-center' ),
            #                     _id='edt_msg_text_%d_row' % tm.tm.id,
            #                     _class='row',
            #                     _style='display: none;' ),
            #                _class='col-md-12' )
            forum_comment_box.append( edt_div )

        # get add comment textarea
        cmt_div = DIV( DIV( DIV( H4( T( 'Add comment' ),
                                     _class='col-md-12' ),
                                 # DIV( LABEL( T( 'Markup' ) + ':' ),
                                 #      _class='col-md-2' ),
                                 # DIV( htmlcommon.get_selection_field( 'cmt_markup_%d' % tm.tm.id,
                                 #                                input_id='ta_cmt_markup_%d' % tm.tm.id,
                                 #                                options=db_sets.MARKUP_SET,
                                 #                                selected=tm.tm.markup ),
                                 #      _class='col-md-4' ),
                            htmlcommon.get_textarea( 'cmt_msg_text_%d' % tm.tm.id,
                                                         input_id='ta_cmt_msg_text_%d' % tm.tm.id,
                                                         requires=IS_NOT_EMPTY(),
                                                         rows=4 ),
                                _class='col-md-12' ),
                           DIV( htmlcommon.get_button( T( 'Add comment' ),
                                                       value='act_add_comment_%d' % tm.tm.id,
                                                       css_class='btn btn-submit' ),
                                htmlcommon.get_button( T( 'Cancel' ),
                                                       bt_link='#',
                                                       on_click="jQuery( '#cmt_msg_text_%d_row' ).hide();" % tm.tm.id,
                                                       css_class='btn btn-warning' ),

                                _class='col-md-12 text-center' ),
                           _id='cmt_msg_text_%d_row' % tm.tm.id,
                           _class='row',
                           _style='display: none;' ),
                           _class='col-md-12' )
        forum_comment_box.append( cmt_div )

        li = LI( forum_comment_box )
        # get children if any
        if tm.children:
            li.append( UL( get_thread_msg_comments_as_UL( tm.children ) ) )
        ul.append( li )
    return ul


def get_thread_as_UL( thread_id, db=None ):
    if not db:
        db = current.db
    thread_msg_list = get_thread_as_tree( thread_id, db=db )
    ul = UL( get_thread_msg_comments_as_UL( thread_msg_list, db=db ),
             _class='thread_tree' )
    return ul


def _get_add_comment_button( tm ):
    T = current.T
    edt_onclick = "jQuery( '#cmt_msg_text_%d_row' ).show();" % tm.tm.id
    edt_onclick += "jQuery( '#ta_cmt_msg_text_%(tm_id)s' ).focus();" \
                   "return false;" \
                   % dict( tm_id=tm.tm.id )
    bt = A( elements.get_bootstrap_icon( elements.ICON_PENCIL,
                                         dark_background=False,
                                         tip=T( 'Add comment' ) ),
            T( 'Add comment' ),
            href='#',
            _class='btn command_link',
            _onclick=edt_onclick )
    # bt = A( elements.get_bootstrap_icon( elements.ICON_PENCIL,
    #                                      dark_background=False,
    #                                      tip=T( 'Add comment' ) ),
    #         B( T( 'Add comment' ) ),
    #         _href='#',
    #         _class='command_link',
    #         _onclick=edt_onclick )
    return bt


def _get_edit_comment_button( tm ):
    T = current.T
    auth = current.auth
    if auth.user.id == tm.tm.auth_user_id or is_in_group( K_ROLE_SUPPORT ):
        msg_text = tm.tm.msg_text.replace( '\n', '\\n' ).replace( '\r', '' ).replace( "'", "\\'" )
        edt_onclick = "jQuery( '#edt_msg_text_%(tm_id)s_row' ).show(); " \
                      "jQuery( '#ta_edt_msg_text_%(tm_id)s' ).val( '%(val)s' );" \
                      % dict( tm_id=tm.tm.id,
                              val=msg_text )
        if tm.tm.id == 0:
            edt_onclick += "jQuery( '#ta_edt_msg_title_0' ).val( '%(val)s' );" % dict( val=tm.tm.msg_title )
        edt_onclick += "jQuery( '#ta_edt_msg_title_%(tm_id)s' ).focus();" \
                       "return false;" \
                       % dict( tm_id=tm.tm.id )
        bt = BUTTON( elements.get_bootstrap_icon( elements.ICON_EDIT,
                                                  dark_background=False,
                                                  tip=T( 'Edit comment' ) ),
                     T( 'Edit' ),
                     _class='command_link',
                     _onclick=edt_onclick )
        return bt
    return ''


def _get_delete_comment_button( tm, db=None ):
    if not db:
        db = current.db
    T = current.T
    auth = current.auth
    bt = ''
    if tm.tm.id > 0:
        tm_model = db_tables.get_table_model( 'thread_msg', db=db )
        q_sql = (db.thread_msg.parent_thread_msg_id == tm.tm.id)
        q_sql &= (db.thread_msg.auth_user_id != auth.user_id)
        count = tm_model.count( q_sql )
        if is_in_group( K_ROLE_DEVELOPER ) or ( auth.user.id == tm.tm.auth_user_id and
                                                count == 0 ):
            edt_onclick = "return confirm( '%(msg)s' );" \
                          % dict( msg=T( 'Confirm delete comment #%(id)s?',
                                         dict( id=tm.tm.id ) ) )
            bt = BUTTON( elements.get_bootstrap_icon( elements.ICON_DELETE,
                                                      dark_background=False,
                                                      tip=T( 'Delete this comment' ) ),
                         T( 'Delete' ),
                         _name='action',
                         _type='submit',
                         _value='act_del_comment_%d' % tm.tm.id,
                         _class='command_link',
                         _onclick=edt_onclick )
        # url = URL( c='forum', f='delete_comment', args=[ tm.tm.id ] )
        # bt = A( elements.get_bootstrap_icon( elements.ICON_DELETE,
        #                                      dark_background=False,
        #                                      tip=T( 'Delete this comment' ) ),
        #         T( 'Delete' ),
        #         _href=url,
        #         _class='btn command_link',
        #         _onclick=edt_onclick )
        return bt
    return ''


def _get_command_row_div( tm, db=None ):
    if not db:
        db = current.db
    cmd_div = DIV( _class='row' )
    v_div = get_vote_panel( tm, db=db )
    cmd_div.append( v_div )
    c_div = DIV( _get_add_comment_button( tm ),
                 _get_edit_comment_button( tm ),
                 _get_delete_comment_button( tm, db=db ),
                 _class='col-md-6 command_display text-right' )
    cmd_div.append( c_div )
    return cmd_div


def get_thread_command_row_div( thread_id, db=None ):
    if not db:
        db = current.db
    t_model = db_tables.get_table_model('thread', db=db )
    t = t_model[ thread_id ]
    div = _get_command_row_div( Storage( tm=Storage( id=0,
                                                     thread_id=thread_id,
                                                     msg_title=t.thread_title,
                                                     msg_text=t.thread_msg ) ),
                                db=db )
    return div


def get_thread_list( active=None, db=None ):
    '''

    :param active: [ False, True, 'all' ]
    :param db:
    :return:
    '''
    if not db:
        db = current.db
    t_model = db_tables.get_table_model( 'thread', db=db )
    q_sql = (db.thread.id > 0)
    if active != 'all':
        if active:
            q_sql &= (db.thread.closed_time == None)
        else:
            q_sql &= (db.thread.closed_time != None)
    if not is_in_group( K_ROLE_ADMIN ):
        q_sql &= (db.thread.thread_type_id == TTYPE_OPEN_DISCUSSION)
    t_list = t_model.select( q_sql, orderby='created_on' )
    return t_list


def get_subscriber_list( thread_id, db=None ):
    if not db:
        db = current.db
    ts_model = db_tables.get_table_model( 'thread_subscriber', db=db )
    q_sql = (db.thread_subscriber.thread_id == thread_id)
    ts_list = ts_model.select( q_sql )
    subscriber_list = [ Storage( auth_user_id=ts.auth_user_id,
                                 first_name=ts.auth_user_id.first_name,
                                 email=ts.auth_user_id.email )
                         for ts in ts_list ]
    return sorted( subscriber_list, key=lambda name: name[1] )


