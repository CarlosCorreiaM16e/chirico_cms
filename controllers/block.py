# -*- coding: utf-8 -*-
# this file is released under public domain and you can use without limitations
from chirico.views.block.composer import BlockComposerView
from chirico.views.block.list import BlockListView
from chirico.views.block.edit import BlockEditView
from chirico.views.block.edittext import BlockEdittextView
from gluon.storage import Storage
from m16e.kommon import KQV_LIMIT, KQV_OFFSET, KQV_ORDER, KQV_SHOW_ALL, K_ROLE_EDITOR
import m16e.term as term

if 0:
    import gluon
    from gluon.html import URL
    global auth; auth = gluon.tools.Auth()
    global cache; cache = gluon.cache.Cache()
    global crud; crud = gluon.tools.Crud()
    global db; db = gluon.sql.DAL()
    global request; request = gluon.globals.Request()
    global response; response = gluon.globals.Response()
    global service; service = gluon.tools.Service()
    global session; session = gluon.globals.Session()

    from gluon.http import redirect


@auth.requires_membership( K_ROLE_EDITOR )
def index():
    term.printLog( 'request.vars: %s' % repr( request.vars ) )
    session.svars = Storage()
    session.svars[ KQV_LIMIT ] = 200
    session.svars[ KQV_OFFSET ] = 0
    session.svars[ KQV_ORDER ] = 1

    session.svars[ KQV_SHOW_ALL ] = False

    term.printLog( 'session.svars: %s' % ( repr( session.svars ) ) )
    redirect( URL( r = request, f = 'list' ) )


@auth.requires_membership( K_ROLE_EDITOR )
def list():
    term.printLog( 'request.args: %s\n' % ( repr( request.args ) ) )
    term.printLog( 'request.vars: %s\n' % ( repr( request.vars ) ) )
    term.printLog( 'request.get_vars: %s\n' % ( repr( request.get_vars ) ) )
    term.printLog( 'request.post_vars: %s\n' % ( repr( request.post_vars ) ) )
    term.printLog( 'session.vars: %s\n' % ( repr( session.svars ) ) )

    view = BlockListView( db )
    result = view.process()
    if result.redirect:
        redirect( result.redirect )

    return result.dict


@auth.requires_membership( K_ROLE_EDITOR )
def edit():
    """
    blockId = int( request.args( 0 ) )
    pageId = int( request.vars.qv_page_id )
    """
    term.printLog( 'request.args: ' + repr( request.args ) )
    term.printLog( 'request.vars: ' + repr( request.vars ) )
    if request.post_vars:
        term.printLog( 'request.post_vars: ' + repr( request.post_vars ) )

#     term.printDebug( 'env: %s' % ( request.env ) )
    view = BlockEditView( db )

    result = view.process()
    if result.redirect:
        redirect( result.redirect )

    return result.dict


@auth.requires_membership( K_ROLE_EDITOR )
def edittext():
    """
    blockId = int( request.args( 0 ) )
    """
    term.printLog( 'request.args: ' + repr( request.args ) )
    term.printLog( 'request.vars: ' + repr( request.vars ) )
    if request.post_vars:
        term.printLog( 'request.post_vars: ' + repr( request.post_vars ) )

    view = BlockEdittextView( db )
    result = view.process()
    if result.redirect:
        redirect( result.redirect )

    return result.dict


@auth.requires_membership( K_ROLE_EDITOR )
def composer():
    term.printLog( 'request.args: ' + repr( request.args ) )
    term.printLog( 'request.vars: ' + repr( request.vars ) )
    if request.post_vars:
        term.printLog( 'request.post_vars: ' + repr( request.post_vars ) )

    page_edit_view = BlockComposerView( db )

    result = page_edit_view.process()
    if result.redirect:
        redirect( result.redirect )

    return result.dict


@auth.requires_membership( K_ROLE_EDITOR )
def ajax_add_link():
    term.printLog( 'request.args: ' + repr( request.args ) )
    term.printLog( 'request.vars: ' + repr( request.vars ) )
    if request.post_vars:
        term.printLog( 'request.post_vars: ' + repr( request.post_vars ) )

    page_edit_view = BlockComposerView( db )

    return page_edit_view.ajax_add_link()


@auth.requires_membership( K_ROLE_EDITOR )
def ajax_add_embed():
    term.printLog( 'request.args: ' + repr( request.args ) )
    term.printLog( 'request.vars: ' + repr( request.vars ) )
    if request.post_vars:
        term.printLog( 'request.post_vars: ' + repr( request.post_vars ) )

    page_edit_view = BlockComposerView( db )

    return page_edit_view.ajax_add_embed()
