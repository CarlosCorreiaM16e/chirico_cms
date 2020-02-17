# -*- coding: utf-8 -*-
# this file is released under public domain and you can use without limitations

import datetime

from m16e.db import db_tables
from gluon import current
from gluon.html import URL
from gluon.sqlhtml import SQLFORM
from gluon.storage import Storage
from m16e import term
from m16e.user_factory import is_in_group
from m16e.views.edit_base_view import BaseFormView

DT = datetime.datetime

ACT_ACTIVATE_USER = 'act_activate_user'
ACT_DELETE_USER = 'act_delete_user'
ACT_IMPERSONATE_USER = 'act_impersonate_user'

#------------------------------------------------------------------
class UserEditView( BaseFormView ):
    controller_name = 'users'

    #------------------------------------------------------------------
    def __init__( self, db ):
        super( UserEditView, self ).__init__( db )
        self.auth_user = None


    #------------------------------------------------------------------
    def do_process( self ):
        return super( UserEditView, self ).do_process()


    #------------------------------------------------------------------
    def get_table_name( self ):
        return 'auth_user'


    #------------------------------------------------------------------
    def fetch_vars( self ):
        """
        auth_user_id       = request.args( 0 )
        """
        super( UserEditView, self ).fetch_vars()
        db = self.db
        self.auth_user = db.auth_user[ self.record_id ]


    #------------------------------------------------------------------
    def process_pre_validation_actions( self ):
        db = self.db
        T = current.T
        auth = current.auth
        session = current.session
        request = current.request
        if self.action == ACT_IMPERSONATE_USER:
            return self.set_result( redirect=URL( c='default',
                                                  f='user',
                                                  args=[ 'impersonate',
                                                         self.record_id ] ) )

        if self.action == ACT_ACTIVATE_USER:
            db( db.auth_user.id == self.record_id ).update( registration_key='' )
            user = db.auth_user[ self.record_id ]
            auth.email_reset_password( user )
            session.flash = T( 'E-mail sent' )
            return self.set_result( redirect=URL( c='users',
                                                  f='list' ) )

        if self.action == ACT_DELETE_USER and request.vars.chk_del_user:
            rm_model = db_tables.get_table_model( 'request_msg', db=db )
            rs_model = db_tables.get_table_model( 'request_subscribers', db=db )
            rv_model = db_tables.get_table_model( 'request_vote', db=db )
            sr_model = db_tables.get_table_model( 'support_request', db=db )
            eq_sql = (db.request_subscribers.user_id == self.record_id)
            rs_model.delete( eq_sql )
            eq_sql = (db.request_msg.user_id == self.record_id)
            rm_model.delete( eq_sql )
            eq_sql = (db.request_vote.auth_user_id == self.record_id)
            rv_model.delete( eq_sql )
            eq_sql = (db.support_request.auth_user_id == self.record_id)
            sr_model.delete( eq_sql )
            db( db.auth_event.user_id == self.record_id ).delete()
            db( db.auth_membership.user_id == self.record_id ).delete()
            db( db.auth_user.id == self.record_id ).delete()
            return self.set_result( redirect=URL( c='users',
                                                  f='list' ),
                                    message=T( 'User removed' ) )


    #------------------------------------------------------------------
    def get_form_fields( self ):
        self.form_fields = [ 'first_name',
                             'email',
                             'registration_key',
                             'reset_password_key' ]
        return self.form_fields


    #------------------------------------------------------------------
    def get_form( self,
                  form_fields=None,
                  form_validators=None,
                  deletable=None,
                  textarea_rows=None,
                  readonly_fields=None,
                  exclude_fields=None,
                  upload=None,
                  showid=None,
                  buttons=None):

        db = self.db
        if self.record_id:
            self.auth_user = db.auth_user[ self.record_id ]
#         term.printDebug( 'record: %s' % repr( record ) )
        form = SQLFORM( db.auth_user,
                        self.auth_user,
                        fields=self.get_form_fields(),
                        deletable=deletable,
                        showid=True )
#         term.printDebug( 'form: %s' % form.xml() )
        return form


    # #------------------------------------------------------------------
    # def pre_upd_ins( self, upd ):
    #     db = self.db
    #     T = current.T
    #     af = app_factory.get_app_features( db=db )
    #     if af:
    #         uc = db( db.auth_user.id > 0).count()
    #         if af.max_users and uc > af.max_users:
    #             self.set_result( message=T( 'User limit reached' ),
    #                              stop_execution=True )
    #
    #
    #------------------------------------------------------------------
    def post_process_form( self, form ):
        auth = current.auth
        T = current.T
        db = self.db
        super( UserEditView, self ).post_process_form( form )
        may_impersonate = auth.has_permission( 'impersonate',
                                               db.auth_user,
                                               self.record_id )
        title = T( 'Edit user' )
        grp_list = []
        sql = '''
            select ag.*
                from auth_group ag
                    join auth_membership am on am.group_id = ag.id
                where
                    user_id = %(user_id)s
        ''' % { 'user_id': self.record_id }
        rows = db.executesql( sql, as_dict=True )
        for r in rows:
            grp_list.append( Storage( r ) )

        g_list = []
        sql = 'select * from auth_group'
        if not is_in_group( 'dev' ):
            sql += ' where '
            g_list = [ 'dev' ]
            if not is_in_group( 'support' ):
                g_list.append( 'support' )
            if not is_in_group( 'admin' ):
                g_list.append( 'admin' )
            if not is_in_group( 'manager' ):
                g_list.append( 'manager' )
            sql += ' role not in ( %s )'
        sql += ' order by description'
        if g_list:
            exec_sql = sql % (', '.join( [ "'%s'" % g for g in g_list ] ) )
        else:
            exec_sql = sql
        # term.printDebug( 'exec_sql: %s' % exec_sql )
        rows = db.executesql( exec_sql, as_dict=True )
        new_grp_list = [ Storage( r ) for r in rows ]
        # if is_in_group( 'dev' ):
        #     q_sql = (db.auth_group.id > 0)
        # elif is_in_group( 'admin' ):
        #     q_sql = ~(db.auth_group.role.belongs( 'dev' ))
        # else:
        #     q_sql = ~(db.auth_group.role.belongs( 'dev', 'admin' ))
        #
        # term.printDebug( 'sql: %s' % db( q_sql )._select( orderby='description' ) )
        # new_grp_list = db( q_sql ).select( orderby='description' )

        res = self.set_result( data=dict( form=form,
                                          page_title=title,
                                          auth_user=self.auth_user,
                                          may_impersonate=may_impersonate,
                                          grp_list=grp_list,
                                          new_grp_list=new_grp_list ) )
        term.printDebug( 'res: %s' % repr( res ) )

