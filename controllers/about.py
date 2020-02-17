# -*- coding: utf-8 -*-
from chirico.views import page_viewer
from m16e import term
from m16e.db import db_tables

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


def index():
    term.printLog( 'request.args: %s' % repr( request.args ) )
    term.printLog( 'request.vars: %s' % repr( request.vars ) )
    p_model = db_tables.get_table_model( 'page', db=db )
    q_sql = (db.page.url_c == 'about')
    q_sql &= (db.page.url_f == 'index')
    page = p_model.select( q_sql, print_query=True ).first()
    content = page_viewer.get_page( page.id, db=db )
    return dict( content=content )


def terms_of_use():
    p_model = db_tables.get_table_model( 'page', db=db )
    q_sql = (db.page.url_c == 'about')
    q_sql &= (db.page.url_f == 'terms_of_use')
    page = p_model.select( q_sql, print_query=True ).first()
    content = page_viewer.get_page( page.id, db=db )
    return dict( content=content )

