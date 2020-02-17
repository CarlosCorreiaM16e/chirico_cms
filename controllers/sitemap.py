# -*- coding: utf-8 -*-
# this file is released under public domain and you can use without limitations

from m16e import term

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


@service.xml
def index():
    term.printLog( 'request.args: %s' % repr( request.args ) )
    term.printLog( 'request.vars: %s' % repr( request.vars ) )
    return dict()

