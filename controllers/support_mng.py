# -*- coding: utf-8 -*-


from gluon.html import URL
from gluon.storage import Storage
import m16e.term as term
from gps.views.support_request.edit_mng import RequestEditMngView
from gps.views.support_request.edit_request_message_mng import RequestMsgEditMngView
from gps.views.support_request.edit_request_mng import ReqmngEditRequestMngView
from gps.views.support_request.list_mng import RequestListMngView
from gps.views.support_request.new_mng import RequestNewMngView

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


@auth.requires_membership( 'support' )
def index():
    session.forget( response )
    term.printLog( 'request.args: ' + repr( request.args ) )
    # term.printLog( 'request.vars: ' + repr( request.vars ) )
    redirect( URL( r=request, f='list' ) )


@auth.requires_membership( 'support' )
def list():
    session.forget( response )
    term.printLog( 'request.args: ' + repr( request.args ) )
    # term.printLog( 'request.vars: ' + repr( request.vars ) )

    view = RequestListMngView( db )
    result = view.process()
    if result.redirect:
        redirect( result.redirect )

    return result.dict


@auth.requires_membership( 'support' )
def edit():
    """
    record_id = int( request.args( 0 ) )
    """
    term.printLog( 'request.args: ' + repr( request.args ) )
    # term.printLog( 'request.vars: ' + repr( request.vars ) )
    view = RequestEditMngView( db )

    result = view.process()
    if result.redirect:
        redirect( result.redirect )

    return result.dict


@auth.requires_login()
def subscribe():
    if not request.args:
        redirect( URL( 'index' ) )
    view = RequestEditMngView( db )
    result = view.subscribe()
    if result.redirect:
        redirect( result.redirect )

    return result.dict


@auth.requires_login()
def unsubscribe():
    if not request.args:
        redirect( URL( 'index' ) )
    view = RequestEditMngView( db )
    result = view.unsubscribe()
    if result.redirect:
        redirect( result.redirect )

    return result.dict


@auth.requires_membership( K_ROLE_DEVELOPER )
def unsubscribe_user():
    if not request.args:
        redirect( URL( 'index' ) )
    view = RequestEditMngView( db )
    result = view.unsubscribe_user()
    if result.redirect:
        redirect( result.redirect )

    return result.dict


@auth.requires_membership( 'support' )
def ajax_change_request_status():
    term.printLog( 'request.args: %s\n' % ( repr( request.args ) ) )
    term.printLog( 'request.vars: %s\n' % ( repr( request.vars ) ) )
    view = RequestEditMngView( db )
    result = view.ajax_change_request_status()
    return result


@auth.requires_membership( 'support' )
def delete_request( ):
    term.printLog( 'request.args: ' + repr( request.args ) )
    # term.printLog( 'request.vars: ' + repr( request.vars ) )
    view = RequestEditMngView( db )

    result = view.delete_request()
    if result.redirect:
        redirect( result.redirect )

    return result.dict


@auth.requires_membership( 'support' )
def manage_subscriptions( ):
    term.printLog( 'request.args: ' + repr( request.args ) )
    # term.printLog( 'request.vars: ' + repr( request.vars ) )
    view = RequestEditMngView( db )

    result = view.manage_subscriptions()
    if result.redirect:
        redirect( result.redirect )

    return result.dict


@auth.requires_membership( 'support' )
def ajax_show_add_attach( ):
    term.printLog( 'request.args: ' + repr( request.args ) )
    #     term.printLog( 'request.vars: ' + repr( request.vars ) )

    view = RequestEditMngView( db )
    result = view.ajax_show_add_attach( )
    return result


@auth.requires_membership( 'support' )
def edit_request_msg( ):
    if not request.args:
        session.flash = T( 'Session lost' )
        redirect( URL( 'index' ) )
    term.printLog( 'request.args: %s' % repr( request.args ) )
    #     term.printLog( 'request.vars: %s' % repr( request.vars ) )

    view = RequestMsgEditMngView( db )
    result = view.process( )
    if result.redirect:
        redirect( result.redirect )

    return result.dict


@auth.requires_membership( 'support' )
def new():
    """
    record_id = int( request.args( 0 ) )
    """
    term.printLog( 'request.args: ' + repr( request.args ) )
    # term.printLog( 'request.vars: ' + repr( request.vars ) )
    view = RequestNewMngView( db )

    result = view.process( )
    if result.redirect:
        redirect( result.redirect )

    return result.dict


@auth.requires_membership( 'support' )
def delete_req_msg_attach():
    """
    record_id = int( request.args( 0 ) )
    """
    term.printLog( 'request.args: ' + repr( request.args ) )
    # term.printLog( 'request.vars: ' + repr( request.vars ) )
    view = RequestEditMngView( db )

    result = view.delete_req_msg_attach()
    if result.redirect:
        redirect( result.redirect )

    return result.dict


@auth.requires_membership( 'support' )
def delete_request_msg():
    """
    record_id = int( request.args( 0 ) )
    """
    term.printLog( 'request.args: ' + repr( request.args ) )
    # term.printLog( 'request.vars: ' + repr( request.vars ) )
    view = RequestEditMngView( db )

    result = view.delete_request_msg()
    if result.redirect:
        redirect( result.redirect )

    return result.dict


@auth.requires_membership( 'support' )
def vote():
    """
    record_id = int( request.args( 0 ) )
    """
    term.printLog( 'request.args: ' + repr( request.args ) )
    # term.printLog( 'request.vars: ' + repr( request.vars ) )
    view = RequestEditMngView( db )

    result = view.vote()
    if result.redirect:
        redirect( result.redirect )

    return result.dict


@auth.requires_membership( 'support' )
def edit_request( ):
    if not request.args:
        session.flash = T( 'Session lost' )
        redirect( URL( 'index' ) )
    term.printLog( 'request.args: %s' % repr( request.args ) )
    term.printLog( 'request.vars: %s' % repr( request.vars ) )

    view = ReqmngEditRequestMngView( db )
    result = view.process( )
    if result.redirect:
        redirect( result.redirect )

    return result.dict


