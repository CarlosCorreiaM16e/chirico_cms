# -*- coding: utf-8 -*-

from forum_threads import thread_factory
from forum_threads.views.thread.edit import ThreadEditView
from forum_threads.views.thread.edit_thread import ThreadEditThreadView
from forum_threads.views.thread.edit_thread_message import ThreadMsgEditView
from forum_threads.views.thread.new import ThreadNewView
from forum_threads.views.thread.open_discussions import ForumDiscussionView
from forum_threads.views.thread.view import ThreadDisplayView
from forum_threads.views.thread.list import ForumListView
from gluon.html import URL
from gluon.storage import Storage
import m16e.term as term
from m16e import user_factory
from m16e.kommon import K_ROLE_DEVELOPER, K_ROLE_ADMIN

if 0:
    import gluon
    import gluon.languages.translator as T
    global auth; auth = gluon.tools.Auth()
    global cache; cache = gluon.cache.Cache()
    global crud; crud = gluon.tools.Crud()
    global db; db = gluon.sql.DAL()
    global request; request = gluon.globals.Request()
    global response; response = gluon.globals.Response()
    global service; service = gluon.tools.Service()
    global session; session = gluon.globals.Session()

    from gluon import current
    from gluon.http import redirect


@auth.requires_membership( K_ROLE_ADMIN )
def index():
    session.forget( response )
    term.printLog( 'request.args: ' + repr( request.args ) )
    # term.printLog( 'request.vars: ' + repr( request.vars ) )
    # if is_in_group( 'dev' ):
    #     redirect( URL( c='thread_mng', f='index', args=request.args, vars=request.vars ) )
    redirect( URL( r=request, f='list', args=request.args, vars=request.vars ) )


@auth.requires_membership( K_ROLE_ADMIN )
def list():
    session.forget( response )
    term.printLog( 'request.args: ' + repr( request.args ) )
    # term.printLog( 'request.vars: ' + repr( request.vars ) )
    # if is_in_group( 'dev' ):
    #     redirect( URL( c='thread_mng', f='list',
    #                    args=request.args, vars=request.vars ) )

    view = ForumListView( db )
    result = view.process()
    if result.redirect:
        redirect( result.redirect )

    return result.dict


@auth.requires_login()
def open_discussions():
    session.forget( response )
    term.printLog( 'request.args: ' + repr( request.args ) )
    # term.printLog( 'request.vars: ' + repr( request.vars ) )
    # if is_in_group( 'dev' ):
    #     redirect( URL( c='thread_mng', f='list',
    #                    args=request.args, vars=request.vars ) )

    view = ForumDiscussionView( db )
    result = view.process()
    if result.redirect:
        redirect( result.redirect )

    return result.dict


@auth.requires_login()
def edit():
    """
    record_id = int( request.args( 0 ) )
    """
    term.printLog( 'request.args: ' + repr( request.args ) )
    # if is_in_group( 'dev' ):
    #     redirect( URL( c='thread_mng', f='edit', args=request.args, vars=request.vars ) )
    # term.printLog( 'request.vars: ' + repr( request.vars ) )
    thread_id = int( request.args( 0 ) )
    if not thread_factory.user_may_edit_thread( thread_id, db=db ):
        user_factory.login_event( user_factory.EVT_ORIGIN_PERMISSIONS,
                                  'Bad permissions for [edit] #%d' % thread_id )
        redirect( URL( c='thread', f='index' ) )
    view = ThreadEditView( db )

    result = view.process()
    if result.redirect:
        redirect( result.redirect )

    return result.dict


@auth.requires_login()
def view():
    """
    thread_id = int( request.args( 0 ) )
    """
    term.printLog( 'request.args: ' + repr( request.args ) )
    term.printLog( 'request.vars: ' + repr( request.vars ) )
    view = ThreadDisplayView( db )
    result = view.process()
    if result.redirect:
        redirect( result.redirect )

    return result.dict


@auth.requires_login()
def ajax_vote_comment():
    term.printLog( 'request.args: ' + repr( request.args ) )
    term.printLog( 'request.vars: ' + repr( request.vars ) )
    view = ThreadDisplayView( db )
    return view.ajax_vote_comment()


@auth.requires_login()
def ajax_show_add_attach( ):
    term.printDebug( 'request.args: %s' % repr( request.args ) )
    term.printLog( 'request.args: ' + repr( request.args ) )
    #     term.printLog( 'request.vars: ' + repr( request.vars ) )

    thread_msg_id = int( request.args( 0 ) )
    if not thread_factory.user_may_edit_thread( thread_msg_id=thread_msg_id, db=db ):
        user_factory.login_event( user_factory.EVT_ORIGIN_PERMISSIONS,
                                  'Bad permissions for [forum_threads.ajax_show_add_attach] #%d' % thread_msg_id )
        redirect( URL( c='thread', f='index' ) )
    view = ThreadEditView( db )
    result = view.ajax_show_add_attach( )
    return result


@auth.requires_login()
def edit_thread_msg( ):
    if not request.args:
        session.flash = T( 'Session lost' )
        redirect( URL( 'index' ) )
    term.printLog( 'request.args: %s' % repr( request.args ) )
    #     term.printLog( 'request.vars: %s' % repr( request.vars ) )

    thread_msg_id = int( request.args( 0 ) )
    if not thread_factory.user_may_edit_thread( thread_msg_id=thread_msg_id, db=db ):
        user_factory.login_event( user_factory.EVT_ORIGIN_PERMISSIONS,
                                  'Bad permissions for [forum_threads.edit_thread_msg] #%d' % thread_msg_id )
        redirect( URL( c='thread', f='index' ) )
    view = ThreadMsgEditView( db )
    result = view.process( )
    if result.redirect:
        redirect( result.redirect )

    return result.dict


@auth.requires_login()
def new():
    """
    record_id = int( request.args( 0 ) )
    """
    term.printLog( 'request.args: ' + repr( request.args ) )
    # term.printLog( 'request.vars: ' + repr( request.vars ) )
    view = ThreadNewView( db )

    result = view.process( )
    if result.redirect:
        redirect( result.redirect )

    return result.dict



#----------------------------------------------------------------------
@auth.requires_login()
def delete_thread_msg_attach():
    """
    record_id = int( request.args( 0 ) )
    """
    term.printLog( 'request.args: ' + repr( request.args ) )
    # term.printLog( 'request.vars: ' + repr( request.vars ) )
    thread_msg_attach_id = int( request.args( 0 ) )
    if not thread_factory.user_may_edit_thread( thread_msg_attach_id=thread_msg_attach_id, db=db ):
        user_factory.login_event( user_factory.EVT_ORIGIN_PERMISSIONS,
                                  'Bad permissions for [delete_thread_msg_attach] #%d' % thread_msg_attach_id )
        redirect( URL( c='thread', f='index' ) )

    view = ThreadEditView( db )

    result = view.delete_req_msg_attach()
    if result.redirect:
        redirect( result.redirect )

    return result.dict


#----------------------------------------------------------------------
@auth.requires_login()
def delete_thread_msg():
    """
    record_id = int( request.args( 0 ) )
    """
    term.printLog( 'request.args: ' + repr( request.args ) )
    # term.printLog( 'request.vars: ' + repr( request.vars ) )
    thread_msg_id = int( request.args( 0 ) )
    if not thread_factory.user_may_edit_thread( thread_msg_id=thread_msg_id, db=db ):
        user_factory.login_event( user_factory.EVT_ORIGIN_PERMISSIONS,
                                  'Bad permissions for [delete_thread_msg] #%d' % thread_msg_id )
        redirect( URL( c='thread', f='index' ) )

    view = ThreadEditView( db )

    result = view.delete_thread_msg()
    if result.redirect:
        redirect( result.redirect )

    return result.dict


@auth.requires_login()
def vote():
    """
    record_id = int( request.args( 0 ) )
    """
    term.printLog( 'request.args: ' + repr( request.args ) )
    # term.printLog( 'request.vars: ' + repr( request.vars ) )
    view = ThreadEditView( db )

    result = view.vote()
    if result.redirect:
        redirect( result.redirect )

    return result.dict


@auth.requires_login()
def subscribe():
    if not request.args:
        redirect( URL( 'index' ) )
    view = ThreadDisplayView( db )
    result = view.subscribe()
    if result.redirect:
        redirect( result.redirect )

    return result.dict


@auth.requires_login()
def unsubscribe():
    if not request.args:
        redirect( URL( 'index' ) )
    view = ThreadDisplayView( db )
    result = view.unsubscribe()
    if result.redirect:
        redirect( result.redirect )

    return result.dict


@auth.requires_membership( K_ROLE_DEVELOPER )
def unsubscribe_user():
    if not request.args:
        redirect( URL( 'index' ) )
    view = ThreadDisplayView( db )
    result = view.unsubscribe_user()
    if result.redirect:
        redirect( result.redirect )

    return result.dict


@auth.requires_login( )
def edit_thread():
    if not request.args:
        session.flash = T( 'Session lost' )
        redirect( URL( 'index' ) )
    term.printLog( 'request.args: %s' % repr( request.args ) )
    term.printLog( 'request.vars: %s' % repr( request.vars ) )

    thread_id = int( request.args( 0 ) )
    if not thread_factory.user_may_edit_thread( thread_id=thread_id, db=db ):
        user_factory.login_event( user_factory.EVT_ORIGIN_PERMISSIONS,
                                  'Bad permissions for [edit_thread] #%d' % thread_id )
        redirect( URL( c='thread', f='index' ) )

    view = ThreadEditThreadView( db )
    result = view.process( )
    if result.redirect:
        redirect( result.redirect )

    return result.dict


@auth.requires_login()
def reopen():
    if not request.args:
        session.flash = T( 'Session lost' )
        redirect( URL( 'index' ) )
    term.printLog( 'request.args: %s' % repr( request.args ) )
    term.printLog( 'request.vars: %s' % repr( request.vars ) )

    thread_id = int( request.args( 0 ) )
    if not thread_factory.user_may_edit_thread( thread_id=thread_id, db=db ):
        user_factory.login_event( user_factory.EVT_ORIGIN_PERMISSIONS,
                                  'Bad permissions for [reopen] #%d' % thread_id )
        redirect( URL( c='support', f='index' ) )

    view = ThreadEditView( db )
    result = view.reopen()
    if result.redirect:
        redirect( result.redirect )

    return result.dict


