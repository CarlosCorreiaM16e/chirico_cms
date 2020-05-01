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


from app import initdb
initdb.initdb()
