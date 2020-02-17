# -*- coding: utf-8 -*-
# this file is released under public domain and you can use without limitations

import datetime

from gluon.storage import Storage
from m16e.kommon import KQV_LIMIT, KQV_OFFSET, KQV_ORDER, K_ROLE_MANAGER
import m16e.term as term
from m16e.views.mail_queue.edit import MailQueueEditView
from m16e.views.mail_queue.list import MailQueueListView


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


@auth.requires_membership( K_ROLE_MANAGER )
def index():
    term.printLog( 'request.args: %s\n' % ( repr( request.args ) ) )
    term.printLog( 'request.vars: %s\n' % ( repr( request.vars ) ) )
    session.svars = Storage()
    session.svars[ KQV_LIMIT ] = 20
    session.svars[ KQV_OFFSET ] = 0
    session.svars[ KQV_ORDER ] = 1

    view = MailQueueListView( db )
    result = view.process()
    if result.redirect:
        redirect( result.redirect )

    return result.dict


@auth.requires_membership( K_ROLE_MANAGER )
def edit():
    term.printLog( 'request.args: ' + repr( request.args ) )
    term.printLog( 'request.vars: ' + repr( request.vars ) )
    if request.post_vars:
        term.printLog( 'request.post_vars: ' + repr( request.post_vars ) )

    view = MailQueueEditView( db )
    result = view.process()
    if result.redirect:
        redirect( result.redirect )

    return result.dict


@auth.requires_membership( K_ROLE_MANAGER )
def resend():
    term.printLog( 'request.args: ' + repr( request.args ) )
    term.printLog( 'request.vars: ' + repr( request.vars ) )
    if request.post_vars:
        term.printLog( 'request.post_vars: ' + repr( request.post_vars ) )

    view = MailQueueEditView( db )
    result = view.resend()
    if result.redirect:
        redirect( result.redirect )

    return result.dict

