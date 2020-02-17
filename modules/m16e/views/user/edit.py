# -*- coding: utf-8 -*-
# this file is released under public domain and you can use without limitations

import datetime
from decimal import Decimal
import sys
import traceback

from gluon import current
from gluon.dal import Field
from gluon.html import URL, DIV, H5, I, H6, TABLE, TR, TH, TD, UL, LI, A
from gluon.sqlhtml import SQLFORM
from gluon.storage import Storage
from gluon.validators import IS_IN_SET, IS_IN_DB, IS_NULL_OR
from m16e import term
from m16e.htmlcommon import getChangedFields, formatDecimal
from m16e.kommon import ACT_SUBMIT
from m16e.views.edit_base_view import BaseFormView

DT = datetime.datetime

ACT_IMPERSONATE_USER = 'act_impersonate_user'

#------------------------------------------------------------------
class UserEditView( BaseFormView ):
    controller_name = 'users'
    
    #------------------------------------------------------------------
    def __init__( self, db ):
        super( UserEditView, self ).__init__( db )
        self.table_model = db.auth_user

    #------------------------------------------------------------------
    def process( self ):
        ret = None
        try:
            ret = self._process()
        except:
            t, v, tb = sys.exc_info()
            traceback.print_exception( t, v, tb )
        return ret

    #------------------------------------------------------------------
    def _process( self ):
        request = current.request
        response = current.response
        session = current.session
        T = current.T
        db = self.db
        auth = current.auth
        redirect = None

        term.printLog( 'request.args: ' + repr( request.args ) )
        term.printLog( 'request.vars: ' + repr( request.vars ) )

        user_id = int( request.args( 0 ) )
        user = db.auth_user[ user_id ]
                
        action = request.post_vars.action
        term.printLog( 'action: ' + repr( action ) )

        if action == ACT_IMPERSONATE_USER:
            return Storage( dict=dict(),
                            redirect=URL( c='default',
                                          f='user',
                                          args=[ 'impersonate', user_id ] ) )

        has_username = 'username' in db.auth_user.fields
        has_full_name = 'full_name' in db.auth_user.fields
        fields = [ 'first_name','last_name', 'email' ]
        if has_username:
            fields.append( 'username' )
        if has_full_name:
            fields.append( 'full_name' )
        form = SQLFORM( db.auth_user, user, fields=fields )
#         term.printDebug( form.xml() )
        if form.accepts( request.vars, session, dbio=False ):
            term.printLog( 'form.vars: ' + repr( form.vars ) )
            if action == ACT_SUBMIT:
                upd = getChangedFields( form.vars,
                                        request.post_vars,
                                        db.auth_user )
                if upd:
                    term.printLog( 'upd: ' + repr( upd ) )
                    db( db.auth_user.id == user.id ).update( **upd )
                    session.flash = T( 'User updated' )

                    redirect = URL( c=self.controller_name,
                                    f='index' )
                    term.printDebug( 'redirect: %s' % ( repr( redirect ) ) )
                else:
                    response.flash = T( 'Nothing to update' )

        elif form.errors:
            term.printLog( 'form.errors: ' + repr( form.errors ) )
            response.flash=T( 'Form has errors' )

        term.printDebug( 'table: %s\nuser: %s' % ( repr( db.auth_user ), repr( user_id ) ) )
        term.printDebug( 'auth: %s' % ( repr( auth ) ) )
        may_impersonate = auth.has_permission( 'impersonate',
                                               db.auth_user,
                                               user_id )
        title = T( 'Edit user' )
        return Storage( dict=dict( form=form,
                                   page_title=title,
                                   auth_user=user,
                                   may_impersonate=may_impersonate ),
                        redirect=redirect )


