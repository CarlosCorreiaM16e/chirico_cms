# -*- coding: utf-8 -*-

from chirico.views.app_config.app_config import ConfigAppConfigView
from m16e import term


if 0:
    import gluon
    import gluon.languages.translator as T
    from gluon.html import LI, UL, A, DIV, TABLE, TR, TH, TD, INPUT, BUTTON, FORM, \
        SELECT, OPTION, URL
    from gluon.sqlhtml import SQLFORM
    global auth; auth = gluon.tools.Auth()
    global cache; cache = gluon.cache.Cache()
    global crud; crud = gluon.tools.Crud()
    global db; db = gluon.sql.DAL()
    global request; request = gluon.globals.Request()
    global response; response = gluon.globals.Response()
    global service; service = gluon.tools.Service()
    global session; session = gluon.globals.Session()

    from gluon.http import redirect

#------------------------------------------------------------------
@auth.requires_membership( 'manager' )
def edit():
    term.printLog( 'request.args: %s' % repr( request.args ) )
    term.printLog( 'request.vars: %s' % repr( request.vars ) )

    view = ConfigAppConfigView( db )
    result = view.process()
    if result.redirect:
        redirect( result.redirect )

    return result.dict

