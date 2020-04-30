# -*- coding: utf-8 -*-
# this file is released under public domain and you can use without limitations

import m16e.term as term
from chirico.views import page_viewer
from chirico.views.page.composer import PageComposerView
from chirico.views.page.edit import PageEditView
from chirico.views.page.index import PageIndexView
from m16e import user_factory
from m16e.db import db_tables

if 0:
    from gluon.html import URL

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


ACT_CHECK_ALL = 'check_all'
ACT_CLONE_PAGE = 'clone_page'
ACT_DELETE_ALL_CHECKED = 'delete_all_checked'
ACT_DELETE_PAGE = 'delete_page'
ACT_NEW_BLOCK = 'new_block'
ACT_NEW_PAGE = 'new_page'
ACT_SUBMIT_PAGE = 'submit_page'
ACT_UNCHECK_ALL = 'uncheck_all'

#------------------------------------------------------------------
@auth.requires_membership( 'editor' )
def index():
    view = PageIndexView( db )
    result = view.process()
    if result.redirect:
        redirect( result.redirect )

    return result.dict

#------------------------------------------------------------------
@auth.requires_membership( 'editor' )
def edit():
    term.printLog( 'request.args: ' + repr( request.args ) )
    term.printLog( 'request.vars: ' + repr( request.vars ) )
    if request.post_vars:
        term.printLog( 'request.post_vars: ' + repr( request.post_vars ) )

    page_edit_view = PageEditView( db )

    result = page_edit_view.process()
    if result.redirect:
        redirect( result.redirect )

    return result.dict


@auth.requires_membership( 'editor' )
def composer():
    term.printLog( 'request.args: ' + repr( request.args ) )
    term.printLog( 'request.vars: ' + repr( request.vars ) )
    if request.post_vars:
        term.printLog( 'request.post_vars: ' + repr( request.post_vars ) )

    page_edit_view = PageComposerView( db )

    result = page_edit_view.process()
    if result.redirect:
        redirect( result.redirect )

    return result.dict


def view():
    term.printLog( 'request.args: %s' % repr( request.args ) )
    term.printLog( 'request.vars: %s' % repr( request.vars ) )
    page_args = request.args( 0 )
    try:
        page_id = int( page_args )
        p_model = db_tables.get_table_model( 'page', db=db )
        page = p_model[ page_id ]
        if page.url_c:
            redirect( URL( c=page.url_c,
                           f=page.url_f,
                           args=page.url_args ) )
        content = page_viewer.get_page( page_id=page_id,
                                        db=db )
    except ValueError:
        content = page_viewer.get_page( url_c='page',
                                        url_f='view',
                                        url_args=page_args,
                                        db=db )
    return dict( content=content,
                 user_message_board=user_factory.get_user_message_board() )





