# -*- coding: utf-8 -*-
# this file is released under public domain and you can use without limitations
from chirico.app.app_factory import set_session_mode
from chirico.db import lang_factory
from chirico.k import SES_MODE_ERP, SES_MODE_SHOP, SES_MODE_ANON
from chirico.views import page_viewer
from m16e.db import db_tables
from m16e import term, htmlcommon, mpmail, user_factory
from m16e.kommon import DATE
from m16e.ui import elements
from gluon.storage import Storage

# Dummy code to enable code completion in IDE's.
if 0:
    from gluon.globals import Request, Response, Session
    from gluon.cache import Cache
    from gluon.languages import translator
    from gluon.tools import Auth, Crud, Mail, Service, PluginManager, A, URL, DIV, P, H2
    from gluon.http import redirect

    # API objects
    request = Request()
    response = Response()
    session = Session()
    cache = Cache( request )
    T = translator( request )

    # Objects commonly defined in application model files
    # (names are conventions only -- not part of API)
    db = DAL()
    auth = Auth( db )
    crud = Crud( db )
    mail = Mail()
    service = Service()
    plugins = PluginManager()

    # import gluon
    # global auth; auth = gluon.tools.Auth()
    # global cache; cache = gluon.cache.Cache()
    # global crud; crud = gluon.tools.Crud()
    # global db; db = gluon.sql.DAL()
    # global request; request = gluon.globals.Request()
    # global response; response = gluon.globals.Response()
    # global service; service = gluon.tools.Service()
    # global session; session = gluon.globals.Session()
    #
    # from gluon import current
    # T = current.T
    #
    # from gluon.http import redirect
    # from gluon.html import P, XML, H2, TABLE, TR, TH, TD, I, SELECT, OPTION, IMG, INPUT, \
    #     SCRIPT, URL, SPAN, A, BR, DIV, H3, H4, FORM
    # from gluon.sqlhtml import SQLFORM
    # from gluon.validators import IS_NULL_OR, IS_IN_DB

def index():
    term.printLog( 'request.args: %s' % repr( request.args ) )
    term.printLog( 'request.vars: %s' % repr( request.vars ) )
    p_model = db_tables.get_table_model( 'page', db=db )
    q_sql = (p_model.db_table.url_c == 'default')
    q_sql &= (p_model.db_table.url_f == 'index')
    page = p_model.select( q_sql ).first()
    content = page_viewer.get_page( page.id, db=db )
    return dict( content=content,
                 user_message_board=user_factory.get_user_message_board() )


def set_session_anon():
    set_session_mode( SES_MODE_ANON )
    redirect( URL( c='default', f='index' ) )


def set_session_shop():
    set_session_mode( SES_MODE_SHOP )
    redirect( URL( c='shop', f='index' ) )


def set_session_erp():
    set_session_mode( SES_MODE_ERP )
    redirect( URL( c='default', f='shop_erp' ) )


def user():
    """
    exposes:
    http://..../[app]/default/user/login
    http://..../[app]/default/user/logout
    http://..../[app]/default/user/register
    http://..../[app]/default/user/profile
    http://..../[app]/default/user/retrieve_password
    http://..../[app]/default/user/change_password
    http://..../[app]/default/user/manage_users (requires membership in
    http://..../[app]/default/user/bulk_register
    use @auth.requires_login()
        @auth.requires_membership('group name')
        @auth.requires_permission('read','table name',record_id)
    to decorate functions that need access control
    """
    term.printLog( 'request.args: %s' % repr( request.args ) )
    term.printDebug( 'request.vars: %s' % repr( request.vars ) )
    term.printDebug( 'auth.settings.register_next: %s' %
                     repr( auth.settings.register_next ) )

    term.printLog( 'request.vars.keys(): %s' % repr( request.vars.keys() ) )
    form = auth()
    if request.args(0)=='impersonate':
        term.printDebug( 'impersonating: %s' % repr( auth.is_impersonating() ) )
        redirect( URL( c='default', f='index' ) )
        # redirect( URL( c='default', f='index' ) )
    return dict( form=form )

@cache.action()
def download():
    """
    allows downloading of uploaded files
    http://..../[app]/default/download/[filename]
    """
    db_tables.get_table_model( 'attach', db=db )
    return response.download(request, db)


def call():
    """
    exposes services. for example:
    http://..../[app]/default/call/jsonrpc
    decorate with @services.jsonrpc the functions to expose
    supports xml, json, xmlrpc, jsonrpc, amfrpc, rss, csv
    """
    return service()


def error():
    term.printDebug( 'request.args: %s' % request.args )
    term.printDebug( 'request.vars: %s' % request.vars )
    """ Custom error handler that returns correct status codes."""

    code = request.vars.code
    request_url = request.vars.request_url
    ticket = request.vars.ticket

    if code is not None and request_url != request.url:  # Make sure error url is not current url to avoid infinite loop.
        response.status = int(code)  # Assign the error status code to the current response. (Must be integer to work.)
    content = DIV()
    app = None
    user_msg = T( '''Click on the button below to return to application''' )
    if code == '403':
        title = T( "Not authorized" )
    elif code == '404':
        title = T( "Page not found" )
    elif code == '500':
        app = ticket.split( '/', 1 )[0]
        # Get ticket URL:
        ticket_url = '%(scheme)s://%(host)s/admin/default/ticket/%(ticket)s' % {
            'scheme': 'https' if request.is_https else 'http',
            'host': request.env.http_host,
            'ticket': ticket }

        # Email a notice, etc:
        au = user_factory.get_dev_user( db=db )
        mpmail.do_send_mail( to=au.email,
                             subject="[%s][Error]" % app.upper(),
                             message="Error Ticket:  %s" % ticket_url)

        title = T( "Internal error" )
        user_msg = (P( T( 'An unexpected error has occurred. The system administrator has been mailed on this issue.' ) ),
                    P( T( 'Click on the button below to return to application' ) ))
    else:
        title = T( "Unexpected error" )
    content.append( H2( title ) )
    content.append( DIV( DIV( user_msg,
                              _class='col-md-12' ),
                         _class='row' ) )
    bt_msg = T( 'Return to application' )

    content.append( DIV( DIV( elements.UiButton( text=bt_msg,
                                                 ui_icon=elements.UiIcon( elements.ICON_NAV_NEXT ),
                                                 button_style=elements.BTN_SUBMIT,
                                                 button_size=elements.BT_SIZE_LARGE,
                                                 url=URL( a=app,
                                                          c='default',
                                                          f='index' ) ).get_html_button(),
                              _class='col-md-12 text-center' ),
                         _class='row' ) )
    return dict( content=content )


def bang():
    a = 1 / 0
    return dict()


def lang():
    l = request.args( 0 )
    if l in lang_factory.ACCEPTED_LANGUAGES:
        session.lang = l
    url = request.vars.url
    if url:
        redirect( url )


@service.xml
def sitemap():
    return dict()

