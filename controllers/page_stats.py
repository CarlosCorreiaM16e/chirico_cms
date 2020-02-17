# -*- coding: utf-8 -*-

from m16e import term
from m16e.kommon import K_ROLE_ADMIN
from m16e.views.page_stats.charts import PageStatsChartsView
from m16e.views.page_stats.index import PageStatsIndexView
from m16e.views.page_stats.totals import PageStatsTotalsView

if 0:
    from gluon.html import URL
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


@auth.requires_membership( K_ROLE_ADMIN )
def index():
    term.printLog( 'request.args: %s\n' % ( repr( request.args ) ) )
    term.printLog( 'request.vars: %s\n' % ( repr( request.vars ) ) )
    view = PageStatsIndexView( db )
    result = view.process()
    if result.redirect:
        redirect( result.redirect )
    return result.dict


@auth.requires_membership( K_ROLE_ADMIN )
def totals():
    term.printLog( 'request.args: %s\n' % ( repr( request.args ) ) )
    term.printLog( 'request.vars: %s\n' % ( repr( request.vars ) ) )
    view = PageStatsTotalsView( db )
    result = view.process()
    if result.redirect:
        redirect( result.redirect )
    return result.dict


@auth.requires_membership( K_ROLE_ADMIN )
def charts():
    term.printLog( 'request.args: %s\n' % ( repr( request.args ) ) )
    term.printLog( 'request.vars: %s\n' % ( repr( request.vars ) ) )
    view = PageStatsChartsView( db )
    result = view.process()
    if result.redirect:
        redirect( result.redirect )
    return result.dict


