# -*- coding: utf-8 -*-
# this file is released under public domain and you can use without limitations
import sys
import traceback

from m16e.db import db_tables
from gluon import current, URL, IS_IN_SET
from gluon.dal import Field
from gluon.sqlhtml import SQLFORM
from gluon.storage import Storage
from gluon.validators import IS_NOT_EMPTY
from m16e import term, mpmail, user_factory
from m16e.db.querydata import QueryData
from m16e.kommon import KDT_INT, KDT_CHAR, KQV_NAME, KQV_EMAIL, KDT_TIMESTAMP, KDT_TIMESTAMP_PRETTY, ACT_SEND_MAIL, \
    ACT_SEND_MESSAGE, K_ROLE_SUPPORT
from m16e.ktfact import KTF_COL_ORDER, KTF_SORTABLE_COLS, KTF_CELL_CLASS, \
    KTF_COLS, KTF_TITLE, KTF_TYPE, KTF_CELL_LINK, KTF_LINK_C, KTF_LINK_F, KTF_ARGS, \
    KTF_BUTTONS, KTF_NAME, KTF_USE_ICON, KTF_CHECKBOXES, KTF_CHECKBOX_ID, KTF_VALUE, KTF_CSS_CLASS
from m16e.user_factory import is_in_group
from m16e.views.plastic_view import BaseListPlasticView

K_CHK_ID_PREFIX = 'chk_id_'


#------------------------------------------------------------------
class UserListView( BaseListPlasticView ):
    controller_name = 'users'
    function_name = 'list'


    #------------------------------------------------------------------
    def __init__( self, db ):
        super( UserListView, self ).__init__( db )

        T = current.T
        self.query_vars.qv_limit = 40
        self.append_var( KQV_NAME, fld_type=KDT_CHAR )
        self.append_var( KQV_EMAIL, fld_type=KDT_CHAR )

        self.list_title = T( 'User list' )
        # term.printDebug( 'query_vars: %s' % repr( self.query_vars ) )

    #------------------------------------------------------------------
    def get_table_name( self ):
        return 'auth_user'


    #------------------------------------------------------------------
    def do_process( self ):
        result = super( UserListView, self ).do_process()
        return result

    #------------------------------------------------------------------
    def get_table_view_dict( self ):
        T = current.T
        self.tdef = { KTF_COL_ORDER: [ 'id', 'first_name', 'email', 'groups', 'last_login' ],
                      KTF_SORTABLE_COLS: [ 'id', 'first_name', 'email', 'last_login' ],
                      KTF_CELL_CLASS: 'table_border',
                      KTF_COLS: { 'id': { KTF_TITLE: T( 'User Id' ),
                                          KTF_TYPE: KDT_INT,
                                          KTF_CELL_LINK: { KTF_LINK_C: 'users',
                                                           KTF_LINK_F: 'edit',
                                                           KTF_ARGS: [ 'id' ],
                                                           KTF_TITLE: T( 'Edit user data' ),
                                                           KTF_USE_ICON: True
                                                           }
                                          },
                                  'email': { KTF_TITLE: T( 'Email' ),
                                             KTF_TYPE: KDT_CHAR },
                                  'first_name': { KTF_TITLE: T( 'First name' ),
                                                  KTF_TYPE: KDT_CHAR },
                                  'last_name': { KTF_TITLE: T( 'Last name' ),
                                                 KTF_TYPE: KDT_CHAR },
                                  'groups': { KTF_TITLE: T( 'Groups' ),
                                              KTF_TYPE: KDT_CHAR },
                                  'last_login': { KTF_TITLE: T( 'Last login' ),
                                                  KTF_TYPE: KDT_TIMESTAMP_PRETTY },
                                  },
                      KTF_CHECKBOXES: [ { KTF_NAME: K_CHK_ID_PREFIX + '%d',
                                          KTF_CHECKBOX_ID: 'id',
                                          KTF_TITLE: T( 'Select' ) },
                                        ],
                      }
        # term.printDebug( 'self.tdef: %s' % repr( self.tdef ) )
        return self.tdef

    #------------------------------------------------------------------
    def get_table_qdata_dict( self, extra_buttons={} ):
        T = current.T
        self.qdata = { KTF_BUTTONS: [ { KTF_NAME: 'action',
                                        KTF_TITLE: T( 'Send mail' ),
                                        KTF_VALUE: ACT_SEND_MAIL,
                                        KTF_CSS_CLASS: 'btn btn-success' },
                                      { KTF_NAME: 'action',
                                        KTF_TITLE: T( 'Send message' ),
                                        KTF_VALUE: ACT_SEND_MESSAGE,
                                        KTF_CSS_CLASS: 'btn btn-success' }
                                      ],
                       KTF_COL_ORDER: [ KQV_NAME, KQV_EMAIL ],
                       KTF_COLS: { KQV_NAME: { KTF_TITLE: T( 'Name' ),
                                               KTF_TYPE: KDT_CHAR, },
                                   KQV_EMAIL: { KTF_TITLE: T( 'Email' ),
                                                KTF_TYPE: KDT_CHAR, } }
                       }

        return self.qdata

    #------------------------------------------------------------------
    def get_query_data( self, orderby=None ):
        db = self.db
        qd = super( UserListView, self ).get_query_data( orderby )

        if self.query_vars.get( KQV_NAME ):
            if current.login_field == 'username':
                qd.addAnd( QueryData( 'username ilike( %(name)s )',
                                      { 'name': '%%' + self.query_vars[ KQV_NAME ] + '%%' } ) )
            else:
                qd.addAnd( QueryData( 'first_name ilike( %(name)s )',
                                      { 'name': '%%' + self.query_vars[ KQV_NAME ] + '%%' } ) )
        if self.query_vars.get( KQV_EMAIL ):
            qd.addAnd( QueryData( 'email ilike( %(email)s )',
                                  { 'email': '%%' + self.query_vars[ KQV_EMAIL ] + '%%' } ) )
        if not is_in_group( K_ROLE_SUPPORT ):
            qd.addAnd( QueryData( '''au.id not in (
                select au2.id
                from auth_user au2
                    join auth_membership am2 on am2.user_id = au2.id
                    join auth_group ag2 on am2.group_id = ag2.id
                where
                    ag2.role in ( 'dev', 'support', 'admin' ) )''' ) )
        # term.printDebug( repr( qd ) )
        return qd

    #------------------------------------------------------------------
    def get_query_select( self ):
        query = '''
            select distinct( au.* ),                 
                (select time_stamp 
                 from auth_event 
                 where 
                    user_id = au.id and 
                    description ilike( 'User %% Logged-in') 
                 order by id desc limit 1) as last_login
        '''
        return query

    #------------------------------------------------------------------
    def get_query_from( self ):
        query_form = '''
            from auth_user au
            left outer join auth_membership am on am.user_id = au.id
            left outer join auth_group ag on am.group_id = ag.id
        '''
        return query_form

    #------------------------------------------------------------------
    def get_record_list( self, qd ):
        db = self.db
        a_list = []
        super( UserListView,
               self ).get_record_list( qd=qd,
                                       alias=a_list )
        grp_sql = '''
            SELECT role
                FROM auth_membership am
                    JOIN auth_group ag on am.group_id = ag.id
                WHERE am.user_id = %(user_id)s
                ORDER BY ag.role
        '''
        for row in self.list_rows:
            grp_list = db.executesql( grp_sql,
                                      placeholders={ 'user_id': row.id },
                                      as_dict=True )
            row.groups = ', '.join( [ g[ 'role' ] for g in grp_list ] )

        return self.list_rows


    #------------------------------------------------------------------
    def get_record_count( self, qd ):
        a_list = []
        return super( UserListView,
                      self ).get_record_count( qd=qd,
                                               alias=a_list )

    #------------------------------------------------------------------
    def send_mail( self ):
        request = current.request
        response = current.response
        mail = current.mail
        T = current.T

        term.printLog( 'request.args: %s\n' % ( repr( request.args ) ) )
        term.printLog( 'request.vars: %s\n' % ( repr( request.vars ) ) )

        uidList = request.args
        term.printLog( repr( uidList ) )

        qd = QueryData(
            'au.id in ( %(list)s )' % { 'list': ', '.join( uidList ) } )

        user_list = self.get_record_list( qd )
        form = SQLFORM.factory(
            Field( 'mail_subject', 'string', requires = IS_NOT_EMPTY() ),
            Field( 'mail_text', 'text', requires = IS_NOT_EMPTY() ) )
        if form.process().accepted:
            for u in user_list:
                mpmail.send_mail( u.email,
                                  subject=form.vars.mail_subject,
                                  plain_text_body=form.vars.mail_text )
            response.flash = T( 'Mail sent' )
        elif form.errors:
            response.flash = T( 'Errors in form' )
        return Storage( dict=dict( user_list=user_list, form=form ), redirect=None )


    def send_message( self ):
        request = current.request
        response = current.response
        T = current.T
        db = self.db
        term.printLog( 'request.args: %s\n' % (repr( request.args )) )
        term.printLog( 'request.vars: %s\n' % (repr( request.vars )) )
        try:
            uid_list = request.args
            term.printLog( repr( uid_list ) )

            qd = QueryData(
                'au.id in ( %(list)s )' % { 'list': ', '.join( uid_list ) } )

            user_list = self.get_record_list( qd )
            form = SQLFORM.factory(
                # Field( 'erp_blm_id', 'integer', requires=IS_IN_SET( ee_options ) ),
                Field( 'msg_title', 'string', requires=IS_NOT_EMPTY() ),
                Field( 'msg_text', 'text', requires=IS_NOT_EMPTY() ) )
            if form.process().accepted:
                # data = dict( notify_user_id=notify_user_id,
                #              msg_title=msg_title,
                #              msg_text=msg_text,
                #              msg_type=msg_type,
                #              delete_if_past=delete_if_past )
                data = dict( msg_title=form.vars.msg_title,
                             msg_text=form.vars.msg_text,
                             erp_blm_id=form.vars.erp_blm_id )
                for u in user_list:
                    term.printDebug( 'u (%s): %s' % (type( u ), repr( u )) )
                    data[ 'notify_user_id' ] = u.id
                    user_factory.add_user_message( data, db=db )
                self.set_result( message=T( 'Message created' ),
                                 redirect=URL( c=self.controller_name,
                                               f='list' ) )

            elif form.errors:
                response.flash = T( 'Errors in form' )
        except:
            t, v, tb = sys.exc_info()
            traceback.print_exception( t, v, tb )
            raise
        return Storage( dict=dict( user_list=user_list, form=form ), redirect=None )


    def process_pre_validation_actions( self ):
        super( UserListView, self ).process_pre_validation_actions()
        request = current.request
        term.printDebug( 'send mail: %s' % repr( request.post_vars ) )
        if self.result.stop_execution:
            return
        if self.action == ACT_SEND_MAIL:
            term.printDebug( 'send mail: %s' % repr( request.post_vars ) )
            userList = []
            for chk in request.post_vars:
                if not chk.startswith( K_CHK_ID_PREFIX ):
                    continue
                value = request.post_vars[ chk ]
                if value == 'on':
                    term.printLog( 'chk: ' + repr( chk ) )
                    userId = int( chk.split( '_' )[-1] )
                    userList.append( userId )
            if userList:
                self.set_result( redirect=URL( c=self.controller_name, f='send_mail', args = userList ) )

        elif self.action == ACT_SEND_MESSAGE:
            term.printDebug( 'send message: %s' % repr( request.post_vars ) )
            user_list = []
            for chk in request.post_vars:
                if not chk.startswith( K_CHK_ID_PREFIX ):
                    continue
                value = request.post_vars[ chk ]
                if value == 'on':
                    term.printLog( 'chk: ' + repr( chk ) )
                    user_id = int( chk.split( '_' )[-1] )
                    user_list.append( user_id )
            if user_list:
                self.set_result( redirect=URL( c=self.controller_name, f='send_message', args=user_list ) )


    #------------------------------------------------------------------
