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
ACT_ADD_TO_GROUP = 'act_add_to_group'
ACT_DELETE_GROUP = 'act_delete_group'
ACT_DELETE_USER = 'act_delete_user'
ACT_IMPERSONATE_USER = 'act_impersonate_user'


class CmsUserEditView( BaseFormView ):
    controller_name = 'user_admin'
    function_name = 'edit'


    def __init__( self, db ):
        super( CmsUserEditView, self ).__init__( db )
        self.auth_user = None


    def do_process( self ):
        return super( CmsUserEditView, self ).do_process()


    def get_table_name( self ):
        return 'auth_user'


    def get_db_table( self ):
        db = self.db
        return db.auth_user


    def get_form_fields( self ):
        self.form_fields = [ 'first_name',
                             'email',
                             'registration_key',
                             'reset_password_key' ]
        return self.form_fields


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
            return self.set_result( redirect=URL( c=self.controller_name,
                                                  f='list' ) )

        if self.action == ACT_DELETE_USER and request.vars.chk_del_user:
            ud_model = db_tables.get_table_model( 'user_data', db=db )
            q_sql = (db.user_data.auth_user_id == self.record_id)
            ud_model.delete( q_sql )
            db( db.auth_event.user_id == self.record_id ).delete()
            db( db.auth_membership.user_id == self.record_id ).delete()
            db( db.auth_user.id == self.record_id ).delete()
            session.flash = T( 'User removed' )
            return self.set_result( redirect=URL( c=self.controller_name,
                                                  f='list' ),
                                    message=T( 'User removed' ) )


    def post_process_form( self, form ):
        auth = current.auth
        T = current.T
        db = self.db
        super( CmsUserEditView, self ).post_process_form( form )
        may_impersonate = auth.has_permission( 'impersonate',
                                               db.auth_user,
                                               self.record_id )
        grp_list = [ ]
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

        q_sql = (db.auth_group.role != 'dev' )
        new_grp_list = db( q_sql ).select( orderby='description' )

        ud_model = db_tables.get_table_model( 'user_data', db=db )
        q_sql = (db.user_data.auth_user_id == self.record_id)
        ud = ud_model.select( q_sql ).first()
        delete_user_msg = T( 'Confirm remove user?' )
        is_dev = is_in_group( 'dev' )
        res = self.set_result( data=dict( auth_user=db.auth_user[ self.record_id ],
                                          grp_list=grp_list,
                                          new_grp_list=new_grp_list,
                                          is_dev=is_dev,
                                          delete_user_msg=delete_user_msg,
                                          user_data=ud ) )
        term.printDebug( 'res: %s' % repr( res ) )

