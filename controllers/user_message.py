# -*- coding: utf-8 -*-
# this file is released under public domain and you can use without limitations
#########################################################################
from gluon.storage import Storage
from m16e import term
from m16e.kommon import KQV_LIMIT, KQV_OFFSET, KQV_ORDER, K_ROLE_ADMIN
from m16e.views.user_message.edit import UserMsgEditView
from m16e.views.user_message.list import UserMsgListView

if 0:
    import gluon
    import gluon.languages.translator as T


    from gluon.html import \
        URL
    from gluon.tools import Mail, SQLFORM

    mail = Mail()

    global auth; auth = gluon.tools.Auth()
    global cache; cache = gluon.cache.Cache()
    global crud; crud = gluon.tools.Crud()
    global db; db = gluon.sql.DAL()
    global dbErp; dbErp = gluon.sql.DAL()
    global request; request = gluon.globals.Request()
    global response; response = gluon.globals.Response()
    global service; service = gluon.tools.Service()
    global session; session = gluon.globals.Session()

    from gluon.http import redirect


@auth.requires_membership( K_ROLE_ADMIN )
def index():
    term.printLog( 'request.vars: %s' % repr( request.vars ) )
    query_vars = Storage()
    query_vars[ KQV_LIMIT ] = 100
    query_vars[ KQV_OFFSET ] = 0
    query_vars[ KQV_ORDER ] = 0

    term.printLog( 'query_vars: %s' % (repr( query_vars )) )
    redirect( URL( r=request, f='list', vars=query_vars ) )


@auth.requires_membership( K_ROLE_ADMIN )
def send_mail():
    term.printLog( 'request.args: %s\n' % (repr( request.args )) )
    term.printLog( 'request.vars: %s\n' % (repr( request.vars )) )

    view = UserMsgListView( db )
    result = view.send_mail()
    if result.redirect:
        redirect( result.redirect )

    return result.dict


@auth.requires_membership( K_ROLE_ADMIN )
def send_message():
    term.printLog( 'request.args: %s\n' % (repr( request.args )) )
    term.printLog( 'request.vars: %s\n' % (repr( request.vars )) )

    view = UserMsgListView( db )
    result = view.send_message()
    if result.redirect:
        redirect( result.redirect )

    return result.dict


@auth.requires_membership( K_ROLE_ADMIN )
def list():
    term.printLog( 'request.args: %s\n' % (repr( request.args )) )
    term.printLog( 'request.vars: %s\n' % (repr( request.vars )) )
    term.printLog( 'request.get_vars: %s\n' % (repr( request.get_vars )) )
    term.printLog( 'request.post_vars: %s\n' % (repr( request.post_vars )) )

    view = UserMsgListView( db )
    result = view.process()
    if result.redirect:
        redirect( result.redirect )

    return result.dict


@auth.requires_membership( K_ROLE_ADMIN )
def edit():
    term.printLog( 'request.args: %s\n' % (repr( request.args )) )
    term.printLog( 'request.vars: %s\n' % (repr( request.vars )) )
    term.printLog( 'request.get_vars: %s\n' % (repr( request.get_vars )) )
    term.printLog( 'request.post_vars: %s\n' % (repr( request.post_vars )) )

    view = UserMsgEditView( db )
    result = view.process()
    if result.redirect:
        redirect( result.redirect )

    return result.dict
