# -*- coding: utf-8 -*-

from gps import gps_factory
from gps.views.support_request.edit import RequestEditView
from gps.views.support_request.edit_request import ReqmngEditRequestView
from gps.views.support_request.edit_request_message import RequestMsgEditView
from gps.views.support_request.list import RequestListView
from gps.views.support_request.new import RequestNewView
from gluon.html import URL
from gluon.storage import Storage
import m16e.term as term
from m16e import user_factory
from m16e.user_factory import is_in_group

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


@auth.requires_login()
def index():
    session.forget( response )
    term.printLog( 'request.args: ' + repr( request.args ) )
    # term.printLog( 'request.vars: ' + repr( request.vars ) )
    if is_in_group( 'dev' ):
        redirect( URL( c='support_mng', f='index', args=request.args, vars=request.vars ) )
    redirect( URL( r=request, f='list', args=request.args, vars=request.vars ) )


@auth.requires_login()
def list():
    session.forget( response )
    term.printLog( 'request.args: ' + repr( request.args ) )
    # term.printLog( 'request.vars: ' + repr( request.vars ) )
    if is_in_group( 'dev' ):
        redirect( URL( c='support_mng', f='list',
                       args=request.args, vars=request.vars ) )

    view = RequestListView( db )
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
    if is_in_group( 'dev' ):
        redirect( URL( c='support_mng', f='edit', args=request.args, vars=request.vars ) )
    # term.printLog( 'request.vars: ' + repr( request.vars ) )
    support_request_id = int( request.args( 0 ) )
    if not gps_factory.user_may_edit_request( support_request_id, db=db ):
        user_factory.login_event( user_factory.EVT_ORIGIN_PERMISSIONS,
                                  'Bad permissions for [edit] #%d' % support_request_id )
        redirect( URL( c='support', f='index' ) )
    view = RequestEditView( db )

    result = view.process()
    if result.redirect:
        redirect( result.redirect )

    return result.dict


def ajax_show_add_attach( ):
    term.printDebug( 'request.args: %s' % repr( request.args ) )
    term.printLog( 'request.args: ' + repr( request.args ) )
    #     term.printLog( 'request.vars: ' + repr( request.vars ) )

    request_msg_id = int( request.args( 0 ) )
    if not gps_factory.user_may_edit_request( request_msg_id=request_msg_id, db=db ):
        user_factory.login_event( user_factory.EVT_ORIGIN_PERMISSIONS,
                                  'Bad permissions for [ajax_show_add_attach] #%d' % request_msg_id )
        redirect( URL( c='support', f='index' ) )
    view = RequestEditView( db )
    result = view.ajax_show_add_attach( )
    return result


@auth.requires_login()
def edit_request_msg( ):
    if not request.args:
        session.flash = T( 'Session lost' )
        redirect( URL( 'index' ) )
    term.printLog( 'request.args: %s' % repr( request.args ) )
    #     term.printLog( 'request.vars: %s' % repr( request.vars ) )

    request_msg_id = int( request.args( 0 ) )
    if not gps_factory.user_may_edit_request( request_msg_id=request_msg_id, db=db ):
        user_factory.login_event( user_factory.EVT_ORIGIN_PERMISSIONS,
                                  'Bad permissions for [edit_request_msg] #%d' % request_msg_id )
        redirect( URL( c='support', f='index' ) )
    view = RequestMsgEditView( db )
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
    view = RequestNewView( db )

    result = view.process( )
    if result.redirect:
        redirect( result.redirect )

    return result.dict



#----------------------------------------------------------------------
@auth.requires_login()
def delete_req_msg_attach():
    """
    record_id = int( request.args( 0 ) )
    """
    term.printLog( 'request.args: ' + repr( request.args ) )
    # term.printLog( 'request.vars: ' + repr( request.vars ) )
    request_msg_attach_id = int( request.args( 0 ) )
    if not gps_factory.user_may_edit_request( request_msg_attach_id=request_msg_attach_id, db=db ):
        user_factory.login_event( user_factory.EVT_ORIGIN_PERMISSIONS,
                                  'Bad permissions for [delete_req_msg_attach] #%d' % request_msg_attach_id )
        redirect( URL( c='support', f='index' ) )

    view = RequestEditView( db )

    result = view.delete_req_msg_attach()
    if result.redirect:
        redirect( result.redirect )

    return result.dict


#----------------------------------------------------------------------
@auth.requires_login()
def delete_request_msg():
    """
    record_id = int( request.args( 0 ) )
    """
    term.printLog( 'request.args: ' + repr( request.args ) )
    # term.printLog( 'request.vars: ' + repr( request.vars ) )
    request_msg_id = int( request.args( 0 ) )
    if not gps_factory.user_may_edit_request( request_msg_id=request_msg_id, db=db ):
        user_factory.login_event( user_factory.EVT_ORIGIN_PERMISSIONS,
                                  'Bad permissions for [delete_request_msg] #%d' % request_msg_id )
        redirect( URL( c='support', f='index' ) )

    view = RequestEditView( db )

    result = view.delete_request_msg()
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
    view = RequestEditView( db )

    result = view.vote()
    if result.redirect:
        redirect( result.redirect )

    return result.dict


@auth.requires_login()
def subscribe():
    if not request.args:
        redirect( URL( 'index' ) )
    view = RequestEditView( db )
    result = view.subscribe()
    if result.redirect:
        redirect( result.redirect )

    return result.dict


@auth.requires_login()
def unsubscribe():
    if not request.args:
        redirect( URL( 'index' ) )
    view = RequestEditView( db )
    result = view.unsubscribe()
    if result.redirect:
        redirect( result.redirect )

    return result.dict


@auth.requires_login( )
def edit_request():
    if not request.args:
        session.flash = T( 'Session lost' )
        redirect( URL( 'index' ) )
    term.printLog( 'request.args: %s' % repr( request.args ) )
    term.printLog( 'request.vars: %s' % repr( request.vars ) )

    support_request_id = int( request.args( 0 ) )
    if not gps_factory.user_may_edit_request( support_request_id=support_request_id, db=db ):
        user_factory.login_event( user_factory.EVT_ORIGIN_PERMISSIONS,
                                  'Bad permissions for [edit_request] #%d' % support_request_id )
        redirect( URL( c='support', f='index' ) )

    view = ReqmngEditRequestView( db )
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

    support_request_id = int( request.args( 0 ) )
    if not gps_factory.user_may_edit_request( support_request_id=support_request_id, db=db ):
        user_factory.login_event( user_factory.EVT_ORIGIN_PERMISSIONS,
                                  'Bad permissions for [reopen] #%d' % support_request_id )
        redirect( URL( c='support', f='index' ) )

    view = RequestEditView( db )
    result = view.reopen()
    if result.redirect:
        redirect( result.redirect )

    return result.dict


