# -*- coding: utf-8 -*-
from chirico.views import page_viewer
from m16e import term, user_factory
from m16e.db import db_tables
from m16e.ui import elements

if 0:
    from gluon.html import URL, DIV, A
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
    from gluon.http import redirect, HTTP


def view():
    term.printLog( 'request.args: %s' % repr( request.args ) )
    term.printLog( 'request.vars: %s' % repr( request.vars ) )
    page_id = request.args( 0 )
    content = page_viewer.get_page( page_id, db=db )
    return dict( content=content,
                 user_message_board=user_factory.get_user_message_board() )


def year():
    term.printLog( 'request.args: %s' % repr( request.args ) )
    term.printLog( 'request.vars: %s' % repr( request.vars ) )
    year = int( request.args( 0 ) or 0 )
    if not year or (year < 2010 or year > 2019):
        raise HTTP( 404 )
    content = page_viewer.get_page( url_c='arquivo',
                                    url_f='ano',
                                    url_args=year,
                                    db=db )
    nav_prev = DIV( _class='col-md-6' )
    nav_next = DIV( _class='col-md-6 text-right' )
    if year > 2010:
        nav_prev.append( A( elements.get_bootstrap_icon( elements.ICON_NAV_PREV, dark_background=False ),
                            str( year - 1 ),
                            _href=URL( c='arquive',
                                       f='year',
                                       args=year - 1 ) ) )
    if year < 2019:
        nav_next.append( A( str( year + 1 ),
                            elements.get_bootstrap_icon( elements.ICON_NAV_NEXT, dark_background=False ),
                            _href=URL( c='arquive',
                                       f='year',
                                       args=year + 1 ) ) )
    nav = DIV( nav_prev,
               nav_next,
               _class='row' )

    content.insert( 0, nav )

    return dict( content=content )


