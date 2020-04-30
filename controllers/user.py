# -*- coding: utf-8 -*-
# this file is released under GPL Licence v.3
# author: carlos@memoriapersistente.pt

from chirico.views.user.mydata import CmsUserMydataView
from m16e.db import db_tables
from gluon.sqlhtml import SQLFORM
from gluon.storage import Storage
import m16e.htmlcommon as html
from m16e.kommon import ACT_SUBMIT, DT
import m16e.term as term
from m16e.views.user.list import UserListView

if 0:
    import gluon
    global auth; auth = gluon.tools.Auth()
    global cache; cache = gluon.cache.Cache()
    global crud; crud = gluon.tools.Crud()
    global db; db = gluon.sql.DAL()
    global request; request = gluon.globals.Request()
    global response; response = gluon.globals.Response()
    global service; service = gluon.tools.Service()
    global session; session = gluon.globals.Session()

    from gluon import current
    T = current.T

    from gluon.http import redirect

    from gluon.html import URL, SPAN, A, BR, DIV, H3, H4, FORM


@auth.requires_membership( 'editor' )
def index():
    term.printLog( 'request.args: %s\n' % ( repr( request.args ) ) )
    term.printLog( 'request.vars: %s' % repr( request.vars ) )
    session.svars = Storage()
    redirect( URL( r=request, f='list' ) )


@auth.requires_membership( 'editor' )
def list():
    term.printLog( 'request.args: %s\n' % ( repr( request.args ) ) )
    term.printLog( 'request.vars: %s\n' % ( repr( request.vars ) ) )
    term.printLog( 'request.get_vars: %s\n' % ( repr( request.get_vars ) ) )
    term.printLog( 'request.post_vars: %s\n' % ( repr( request.post_vars ) ) )
    term.printLog( 'session.vars: %s\n' % ( repr( session.svars ) ) )

    view = UserListView( db )

    result = view.process()
    if result.redirect:
        redirect( result.redirect )

    return result.dict

@auth.requires_membership( 'manager' )
def edit():
    """
    userId = int( request.args( 0 ) )
    """
    term.printLog( 'request.args: ' + repr( request.args ) )
    term.printLog( 'request.vars: ' + repr( request.vars ) )

    userId = 0
    authUser = None
    if request.args:                    # user
        userId = int( request.args( 0 ) )
        if userId:
            authUser = db.auth_user[ userId ]

    term.printLog( 'userId: ' + repr( userId ) )

    userFields = [
        'id',
        'email',
        'first_name',
        'last_name',
        'registration_key' ]

    form = SQLFORM( db.auth_user, authUser, fields = userFields )

    action = request.post_vars.action
    term.printLog( 'action: ' + repr( action ) )

    if form.accepts( request.vars, session, dbio = False ):
        term.printLog( 'form.vars: ' + repr( form.vars ) )
        if action == ACT_SUBMIT:
            changed = False
            upd = html.getChangedFields( form.vars, request.post_vars, db.auth_user )
            if upd:
                changed = True
            term.printLog( 'upd: ' + repr( upd ) )
            userId = None
            if authUser:
                userId = authUser['id']
                if upd:
                    term.printLog( 'updating: ' + repr( upd ) )
                    db( db.auth_user.id == userId ).update( **upd )
            else:
                userId = db.auth_user.insert( **upd )

            if changed:
                if authUser:
                    session.flash = T( 'User updated' )
                else:
                    session.flash = T( 'User created' )
                redirect( URL( r = request, f = 'edit', args = [ userId ] ) )
            else:
                response.flash = T( 'Nothing to update' )

    elif form.errors:
        term.printLog( 'form.errors: ' + repr( form.errors ) )
        response.flash = T( 'Form has errors' )

    grpList = []
    if authUser:
        sql = '''
            select ag.*
                from auth_group ag
                    join auth_membership am on am.group_id = ag.id
                where
                    user_id = %(user_id)s
        '''
        rows = db.executesql(
            sql, placeholders = { 'user_id': authUser.id }, as_dict = True )
        for r in rows:
            grpList.append( Storage( r ) )
    return dict( authUser = authUser, grpList = grpList, form = form )

@auth.requires_login()
def mydata():
    term.printLog( 'request.args: ' + repr( request.args ) )
    term.printLog( 'request.vars: ' + repr( request.vars ) )

    ud_model = db_tables.get_table_model( 'user_data', db=db )
    q_sql = (db.user_data.auth_user_id == auth.user.id)
    ud = ud_model.select( q_sql ).first()
    if not ud:
        ud_model.insert( dict( name=auth.user.first_name,
                              auth_user_id=auth.user.id ) )

    view = CmsUserMydataView( db )
    result = view.process()
    if result.redirect:
        redirect( result.redirect )

    return result.dict


# @auth.requires_login()
# def invite_friends():
#     term.printLog( 'request.args: ' + repr( request.args ) )
#     term.printLog( 'request.vars: ' + repr( request.vars ) )
#     # return dict()
#     view = UserInviteFriendsView( db )
#     result = view.process()
#     if result.redirect:
#         redirect( result.redirect )
#
#     return result.dict
#
#
# @auth.requires_login()
# def ajax_add_mail():
#     term.printLog( 'request.args: ' + repr( request.args ) )
#     term.printLog( 'request.vars: ' + repr( request.vars ) )
#
#     view = UserInviteFriendsView( db )
#     result = view.ajax_add_mail()
#     return result
#
#
# @auth.requires_login()
# def ajax_resend_invitation():
#     term.printLog( 'request.args: ' + repr( request.args ) )
#     term.printLog( 'request.vars: ' + repr( request.vars ) )
#
#     view = UserInviteFriendsView( db )
#     result = view.ajax_resend_invitation()
#     return result
#
#
# @auth.requires_login()
# def delete_invitation():
#     term.printLog( 'request.args: ' + repr( request.args ) )
#     term.printLog( 'request.vars: ' + repr( request.vars ) )
#
#     view = UserInviteFriendsView( db )
#     result = view.delete_invitation()
#     if result.redirect:
#         redirect( result.redirect )
#
#     return result.dict


@auth.requires_login()
def ajax_zip_code_helper():
    term.printLog( 'request.args: %s\n' % ( repr( request.args ) ) )
    term.printLog( 'request.vars: %s\n' % ( repr( request.vars ) ) )

    view = CmsUserMydataView( db )
    result = view.ajax_zip_code_helper()
    return result


@auth.requires_login()
def ajax_zip_code_changed():
    term.printLog( 'request.args: %s\n' % ( repr( request.args ) ) )
    term.printLog( 'request.vars: %s\n' % ( repr( request.vars ) ) )

    view = CmsUserMydataView( db )
    result = view.ajax_zip_code_changed()
    return result


@auth.requires_login()
def ajax_validate_nif():
    term.printLog( 'request.args: %s\n' % ( repr( request.args ) ) )
    term.printLog( 'request.vars: %s\n' % ( repr( request.vars ) ) )

    view = CmsUserMydataView( db )
    result = view.ajax_validate_nif()
    return result


def verify_email():
    return dict()

@auth.requires_login()
def remove_me():
    term.printLog( 'request.args: ' + repr( request.args ) )
    term.printLog( 'request.vars: ' + repr( request.vars ) )

    gp_model = db_tables.get_table_model( 'global_panel', db=db )
    q_sql = (db.global_panel.auth_user_id == auth.user.id)
    gp = gp_model.select( q_sql ).first()
    gp_model.update_by_id( gp.id,
                           dict( deactivated_since=DT.now() ) )
    db( db.auth_user.id == auth.user.id ).update(registration_key='suspended' )
    redirect( URL( c='default', f='user', args=[ 'logout' ] ) )

@auth.requires_login()
def suspend_me():
    term.printLog( 'request.args: ' + repr( request.args ) )
    term.printLog( 'request.vars: ' + repr( request.vars ) )

    gp_model = db_tables.get_table_model( 'global_panel', db=db )
    q_sql = (db.global_panel.auth_user_id == auth.user.id)
    gp = gp_model.select( q_sql ).first()
    gp_model.update_by_id( gp.id,
                           dict( suspended_since=DT.now() ) )
    redirect( URL( c='user', f='mydata' ) )

@auth.requires_login()
def unsuspend_me():
    term.printLog( 'request.args: ' + repr( request.args ) )
    term.printLog( 'request.vars: ' + repr( request.vars ) )

    gp_model = db_tables.get_table_model( 'global_panel', db=db )
    q_sql = (db.global_panel.auth_user_id == auth.user.id)
    gp = gp_model.select( q_sql ).first()
    gp_model.update_by_id( gp.id,
                           dict( suspended_since=None ) )
    redirect( URL( c='user', f='mydata' ) )

@auth.requires_login()
def ajax_ack_message():
    """
    msg_id = int( request.args( 0 ) )
    """
    um_model = db_tables.get_table_model( 'user_message', db=db )
    msg_id = int( request.args( 0 ) )
    um_model.update_by_id( msg_id,
                           dict( ack_when=DT.now() ) )
    js = '''
        jQuery( '#um_%d' ).hide();
    ''' % msg_id
    return js

