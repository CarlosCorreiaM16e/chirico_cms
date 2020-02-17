# -*- coding: utf-8 -*-
from chirico.views import page_viewer
from m16e.db import db_tables

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


def index():
    p_model = db_tables.get_table_model( 'page', db=db )
    q_sql = (db.page.url_c == 'contacts')
    q_sql &= (db.page.url_f == 'index')
    page = p_model.select( q_sql, print_query=True ).first()
    content = page_viewer.get_page( page.id, db=db )
    return dict( content=content )
