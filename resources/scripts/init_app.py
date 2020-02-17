# -*- coding: utf-8 -*-
# import ast

if 0:
    import gluon
    from gluon.html import DIV
    from gluon.html import FORM
    from gluon.html import INPUT
    from gluon.html import TABLE
    from gluon.html import TD
    from gluon.html import TR
    from gluon.html import URL
    from gluon.dal import GQLDB, SQLDB
    from gluon.html import PRE, P, TAG, B
    from gluon.http import HTTP
    from gluon.sqlhtml import SQLFORM
    from gluon.validators import IS_NOT_EMPTY

    import gluon.languages.translator as T

    global auth; auth = gluon.tools.Auth()
    global cache; cache = gluon.cache.Cache()
    global crud; crud = gluon.tools.Crud()
    global db; db = gluon.sql.DAL()
    global request; request = gluon.globals.Request()
    global response; response = gluon.globals.Response()
    global service; service = gluon.tools.Service()
    global session; session = gluon.globals.Session()

    from gluon.http import redirect


# class Config( object ):
#     def __init__( self, config_filename ):
#         super( Config, self ).__init__()
#         f = open( config_filename )
#         text = f.read()
#         f.close()
#         self.config_data = ast.literal_eval( text )
#
#
#     def get( self, key ):
#         return self.config_data.get( key )
#
#
# def init_app( cfg_file=None ):
#     if not cfg_file:
#         cfg_file = 'applications/%(app)s/resources/config/init/cfg_%(app)s' % request.app_name
#     cfg = Config( cfg_file )
#     for k in cfg.config_data:
#


from app import initdb
initdb.initdb()
