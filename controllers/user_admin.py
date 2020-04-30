# -*- coding: utf-8 -*-
# this file is released under public domain and you can use without limitations
#########################################################################

import sys
import traceback

from psycopg2._psycopg import IntegrityError

from chirico.views.user_admin.edit import CmsUserEditView
from chirico.views.user_admin.list import CmsUserListView
from m16e.db import db_tables
from gluon.storage import Storage
from m16e import htmlcommon, user_factory
from m16e import term
from m16e.kommon import KQV_LIMIT, \
    KQV_OFFSET, KQV_ORDER, ACT_SUBMIT, DT, K_ROLE_ADMIN

if 0:
    import gluon
    import gluon.languages.translator as T
    from gluon.html import URL
    from gluon.tools import Mail, SQLFORM
    mail = Mail()
    global auth; auth = gluon.tools.Auth()
    global cache; cache = gluon.cache.Cache()
    global crud; crud = gluon.tools.Crud()
    global db; db = gluon.sql.DAL()
    global request; request = gluon.globals.Request()
    global response; response = gluon.globals.Response()
    global service; service = gluon.tools.Service()
    global session; session = gluon.globals.Session()

    from gluon.http import redirect


ACT_DELETE_GROUP = 'act_delete_group'

#------------------------------------------------------------------
@auth.requires_membership( K_ROLE_ADMIN )
def index():
    term.printLog( 'request.vars: %s' % repr( request.vars ) )
    query_vars = Storage()
    query_vars[ KQV_LIMIT ] = 100
    query_vars[ KQV_OFFSET ] = 0
    query_vars[ KQV_ORDER ] = 0

    term.printLog( 'query_vars: %s' % ( repr( query_vars ) ) )
    redirect( URL( r = request, f = 'list', vars=query_vars ) )

#------------------------------------------------------------------
@auth.requires_membership( K_ROLE_ADMIN )
def send_mail():
    term.printLog( 'request.args: %s\n' % ( repr( request.args ) ) )
    term.printLog( 'request.vars: %s\n' % ( repr( request.vars ) ) )
    
    view = CmsUserListView( db )
    result = view.send_mail()
    if result.redirect:
        redirect( result.redirect )

    return result.dict


@auth.requires_membership( K_ROLE_ADMIN )
def send_message():
    term.printLog( 'request.args: %s\n' % (repr( request.args )) )
    term.printLog( 'request.vars: %s\n' % (repr( request.vars )) )

    view = CmsUserListView( db )
    result = view.send_message()
    if result.redirect:
        redirect( result.redirect )

    return result.dict


@auth.requires_membership( K_ROLE_ADMIN )
def list():
    term.printLog( 'request.args: %s\n' % ( repr( request.args ) ) )
    term.printLog( 'request.vars: %s\n' % ( repr( request.vars ) ) )
    term.printLog( 'request.get_vars: %s\n' % ( repr( request.get_vars ) ) )
    term.printLog( 'request.post_vars: %s\n' % ( repr( request.post_vars ) ) )

    view = CmsUserListView( db )
    result = view.process()
    if result.redirect:
        redirect( result.redirect )

    return result.dict

#------------------------------------------------------------------
@auth.requires_membership( K_ROLE_ADMIN )
def edit():
    term.printLog( 'request.args: %s' % ( repr( request.args ) ) )
    term.printLog( 'request.vars: %s' % ( repr( request.vars ) ) )

    view = CmsUserEditView( db )
    result = view.process()
    if result.redirect:
        redirect( result.redirect )

    return result.dict

#------------------------------------------------------------------
@auth.requires_membership( K_ROLE_ADMIN )
def ajax_add_user_to_group():
    '''
        auth_user_id = int( request.args( 0 ) )
        group_id = int( request.vars.add_to_group_id )
    '''
    term.printLog( 'request.args: %s\n' % ( repr( request.args ) ) )
    term.printLog( 'request.vars: %s\n' % ( repr( request.vars ) ) )
    try:
        auth_user_id = int( request.args( 0 ) )
        group_id = int( request.vars.add_to_group_id )
        user_factory.add_user_to_group( group_id=group_id, auth_user_id=auth_user_id, db=db )
        # db.auth_membership.insert( user_id=auth_user_id,
        #                            group_id=group_id )

        url = URL( c='user_admin',
                   f='edit',
                   args=[ auth_user_id ] )
        js = '''
            window.location.replace("%(url)s");
        ''' % { 'url': url }
        term.printDebug( 'js: %s' % js )
    except IntegrityError as e:
        t, v, tb = sys.exc_info()
        traceback.print_exception( t, v, tb )
        print( '\nexception type: %s\n  exception: %s\n    pgerror: %s\n    pgcode: %s\n    args: %s' %
               ( type( e ),
                 repr( e ),
                 e.pgerror,
                 e.pgcode,
                 e.args ) )
        url = URL( c='user_admin',
                   f='list' )
        js = '''
            jQuery( '.flash' ).html( '%(msg)s' ).show();
        ''' % { 'url': url,
                'msg': T( 'There is already a user with that email' ) }
        term.printDebug( 'js: %s' % js )
        db.rollback()
        return js

    except:
        t, v, tb = sys.exc_info()
        traceback.print_exception( t, v, tb )
        url = URL( c='user_admin',
                   f='list' )
        js = '''
            jQuery( '.flash' ).html( '%(msg)s' ).show();
            window.location.replace("%(url)s");
        ''' % { 'url': url, 'msg': T( 'An error has occurred' ) }
        term.printDebug( 'js: %s' % js )
        db.rollback()
        response.flash = T( 'An error has occurred' )
    return js


@auth.requires_login()
def ajax_ack_message():
    """
    msg_id = int( request.args( 0 ) )
    """
    try:
        msg_id = int( request.args( 0 ) )
        um_model = db_tables.get_table_model( 'user_message', db=db )
        um_model.update_by_id( msg_id,
                               dict( ack_when=DT.now() ) )
        js = '''
            jQuery( '#um_%d' ).hide();
        ''' % msg_id
        return js
    except:
        t, v, tb = sys.exc_info()
        traceback.print_exception( t, v, tb )
    return ''


@auth.requires_membership( K_ROLE_ADMIN )
def remove_from_group():
    '''
    auth_user.id = request.args( 0 )
    group_id =  = request.args( 1 )
    '''
    term.printLog( 'request.args: ' + repr( request.args ) )
    term.printLog( 'request.vars: ' + repr( request.vars ) )

    user_id = int( request.args( 0 ) )
    q_sql = (db.auth_membership.user_id == user_id)
    q_sql &= (db.auth_membership.group_id == int( request.args( 1 ) ))
    db( q_sql ).delete()
    redirect( URL( c='user_admin',
                   f='edit',
                   args=[ user_id ] ) )


#------------------------------------------------------------------
@auth.requires_membership( 'editor' )
def edit_group():
    """
    group_id = int( request.args( 0 ) )
    """
    term.printLog( 'request.args: ' + repr( request.args ) )
    term.printLog( 'request.vars: ' + repr( request.vars ) )

    group_id = 0
    group = None
    if request.args:                    # user
        group_id = int( request.args( 0 ) )
        if group_id:
            group = db.auth_group[ group_id ]

    term.printLog( 'group_id: ' + repr( group_id ) )
    db.auth_group.description.type = 'string'
    form = SQLFORM( db.auth_group,
                    group )

    action = request.post_vars.action
    term.printLog( 'action: ' + repr( action ) )

    if action == ACT_DELETE_GROUP and request.vars.chk_del_group == 'on':
        db( db.auth_membership.group_id == group_id ).delete()
        db( db.auth_group.id == group_id ).delete()
        session.flash = T( 'Group deleted' )
        redirect( URL( c='user_admin',
                       f='list' ) )

    if form.accepts( request.vars, session, dbio = False ):
        term.printLog( 'form.vars: ' + repr( form.vars ) )
        if action == ACT_SUBMIT:
            changed = False
            upd = htmlcommon.getChangedFields( form.vars, request.post_vars, db.auth_group )
            if upd:
                changed = True
            term.printLog( 'upd: ' + repr( upd ) )
            group_id = None
            if group:
                group_id = group['id']
                if upd:
                    term.printLog( 'updating: ' + repr( upd ) )
                    db( db.auth_group.id == group_id ).update( **upd )
            else:
                group_id = db.auth_group.insert( **upd )

            if changed:
                if group:
                    session.flash = T( 'Group updated' )
                else:
                    session.flash = T( 'Group created' )
                redirect( URL( r=request,
                               f='edit_group',
                               args=[ group_id ] ) )
            else:
                response.flash = T( 'Nothing to update' )

    elif form.errors:
        term.printLog( 'form.errors: ' + repr( form.errors ) )
        response.flash = T( 'Form has errors' )

    delete_group_msg = T( 'Confirm remove group?' )
    return dict( auth_group=group,
                 form=form,
                 delete_group_msg=delete_group_msg )

#------------------------------------------------------------------
def verify_email():
    return dict()


#------------------------------------------------------------------
