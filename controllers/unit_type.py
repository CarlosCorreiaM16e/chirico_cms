# -*- coding: utf-8 -*-
# this file is released under public domain and you can use without limitations

from gluon.storage import Storage
from m16e.kommon import KQV_LIMIT, KQV_OFFSET, KQV_ORDER
from m16e.views.unit_type.edit import UnitTypeEditView
from m16e.views.unit_type.index import UnitTypeIndexView

import datetime
import m16e.term as term

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

ACT_DELETE_ATTACH = 'delete_attach'
ACT_NEW_ATTACH = 'new_attach'
ACT_SUBMIT_ATTACH = 'submit_attach'


@auth.requires_membership( 'manager' )
def index():
    term.printLog( 'request.args: %s\n' % ( repr( request.args ) ) )
    term.printLog( 'request.vars: %s\n' % ( repr( request.vars ) ) )
    view = UnitTypeIndexView( db )
    result = view.process()
    if result.redirect:
        redirect( result.redirect )
    return result.dict


@auth.requires_membership( 'manager' )
def edit():
    term.printLog( 'request.args: ' + repr( request.args ) )
    term.printLog( 'request.vars: ' + repr( request.vars ) )
    if request.post_vars:
        term.printLog( 'request.post_vars: ' + repr( request.post_vars ) )

    view = UnitTypeEditView( db )
    result = view.process()
    if result.redirect:
        redirect( result.redirect )

    return result.dict

