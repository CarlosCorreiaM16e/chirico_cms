# -*- coding: utf-8 -*-
# this file is released under public domain and you can use without limitations

import datetime

from gluon.html import URL
from gluon.storage import Storage
from m16e.kommon import KQV_LIMIT, KQV_OFFSET, KQV_ORDER
import m16e.term as term
from m16e.views.auth_event_viewer.list import AuthEventViewerListView

if 0:
    from gluon.sqlhtml import SQLFORM
    import gluon.languages.translator as T

    import gluon
    global auth; auth = gluon.tools.Auth()
    global cache; cache = gluon.cache.Cache()
    global crud; crud = gluon.tools.Crud()
    global db; db = gluon.sql.DAL()
    global request; request = gluon.globals.Request()
    global response; response = gluon.globals.Response()
    global service; service = gluon.tools.Service()
    global session; session = gluon.globals.Session()

    from gluon.http import redirect


DT = datetime.datetime
DATE = datetime.date

#------------------------------------------------------------------
@auth.requires_membership( 'manager' )
def index():
    term.printLog( 'request.args: %s\n' % ( repr( request.args ) ) )
    term.printLog( 'request.vars: %s\n' % ( repr( request.vars ) ) )
    session.svars = Storage()
    session.svars[ KQV_LIMIT ] = 100
    session.svars[ KQV_OFFSET ] = 0
    session.svars[ KQV_ORDER ] = -1

    redirect( URL( f='list', args=request.args, vars=request.vars ) )

#------------------------------------------------------------------
@auth.requires_membership( 'manager' )
def list():
    term.printLog( 'request.args: %s\n' % ( repr( request.args ) ) )
    term.printLog( 'request.vars: %s\n' % ( repr( request.vars ) ) )
    session.svars = Storage()
    session.svars[ KQV_LIMIT ] = 100
    session.svars[ KQV_OFFSET ] = 0
    session.svars[ KQV_ORDER ] = -1

    view = AuthEventViewerListView( db )
    result = view.process()
    if result.redirect:
        redirect( result.redirect )

    return result.dict

