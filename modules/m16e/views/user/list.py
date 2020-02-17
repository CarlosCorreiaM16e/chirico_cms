# -*- coding: utf-8 -*-
# this file is released under public domain and you can use without limitations

import m16e.table_factory_with_session as tfact
from gluon import current
from gluon.dal import Field
from gluon.html import URL, DIV, H3, FORM
from gluon.sqlhtml import SQLFORM
from gluon.storage import Storage
from gluon.validators import IS_NOT_EMPTY
from m16e import term, mpmail
from m16e.db.querydata import QueryData
from m16e.kommon import KDT_INT, KDT_CHAR, KQV_OFFSET, \
    KQV_LIMIT, KQV_NAME, ACT_NEW_RECORD, KQV_EMAIL
from m16e.ktfact import KTF_COL_ORDER, KTF_SORTABLE_COLS, KTF_CELL_CLASS, \
    KTF_COLS, KTF_TITLE, KTF_TYPE, KTF_CELL_LINK, KTF_LINK_C, KTF_LINK_F, KTF_ARGS, \
    KTF_BUTTONS, KTF_NAME, KTF_USE_ICON, KTF_CHECKBOXES, KTF_CHECKBOX_ID
from m16e.views.plastic_view import BaseListPlasticView

K_CHK_ID_PREFIX = 'chk_q_id_'

# ACT_NEW_RECORD = 'act_new_record'
ACT_SEND_MAIL = 'act_send_mail'
# KQV_EMAIL = KQV_PREFIX + 'email'

#------------------------------------------------------------------
class UserListView( BaseListPlasticView ):
    controller_name = 'users'

    #------------------------------------------------------------------
    def __init__( self, db ):
        super( UserListView, self ).__init__( db )

        T = current.T
        self.query_vars.qv_limit = 40
        self.append_var( KQV_NAME,
                         fld_type=KDT_CHAR )
        self.append_var( KQV_EMAIL,
                         fld_type=KDT_CHAR )

        self.new_record_action = ACT_NEW_RECORD
        self.list_title = T( 'Users' )
        term.printDebug( 'query_vars: %s' % repr( self.query_vars ) )

    #------------------------------------------------------------------
    def get_table_view_dict( self ):
        T = current.T
        tdef = {
            KTF_COL_ORDER: [ 'id', 'username', 'email', 'groups' ],
            KTF_SORTABLE_COLS: [ 'id', 'username', 'email', 'groups' ],
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
                        'username': { KTF_TITLE: T( 'Name' ), KTF_TYPE: KDT_CHAR },
                        'email': { KTF_TITLE: T( 'Email' ), KTF_TYPE: KDT_CHAR },
                        'groups': { KTF_TITLE: T( 'Groups' ), KTF_TYPE: KDT_CHAR },
            },
            KTF_CHECKBOXES: [
                { KTF_NAME: K_CHK_ID_PREFIX + '%d', KTF_CHECKBOX_ID: 'id', KTF_TITLE: T( 'Select' ) },
            ],
        }
        return tdef

    #------------------------------------------------------------------
    def get_table_qdata_dict( self, extra_buttons={} ):
        T = current.T
        qdata = {
            KTF_BUTTONS: [ { KTF_NAME: 'submit',
                             KTF_TITLE: T( 'Submit' ),
                             KTF_TYPE: 'submit' } ],
            KTF_COL_ORDER: [ KQV_NAME, KQV_EMAIL ],
            KTF_COLS: { KQV_NAME: { KTF_TITLE: T( 'Name' ),
                                    KTF_TYPE: KDT_CHAR, },
                        KQV_EMAIL: { KTF_TITLE: T( 'Email' ),
                                     KTF_TYPE: KDT_CHAR, } }
        }

        return qdata

    #------------------------------------------------------------------
    def get_query_data( self, orderby=None ):
        qd = super( UserListView, self ).get_query_data( orderby )
        if self.query_vars.qv_name:
            qd.addAnd( QueryData( 'username ilike( %(name)s )',
                                  { 'name': '%%' + self.query_vars[ KQV_NAME ] + '%%' } ) )
        if self.query_vars.qv_email:
            qd.addAnd( QueryData( 'email ilike( %(email)s )',
                                  { 'email': '%%' + self.query_vars[ KQV_EMAIL ] + '%%' } ) )
        term.printDebug( repr( qd ) )
        return qd

    #------------------------------------------------------------------
    def get_query_select( self ):
        query = '''
            select *
        '''
        return query

    #------------------------------------------------------------------
    def get_query_from( self ):
        query_form = '''
            from auth_user
        '''
        return query_form

    #------------------------------------------------------------------
    def get_record_list( self, qd ):
        db = self.db
        super( UserListView,
               self ).get_record_list( qd=qd )
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

#     #------------------------------------------------------------------
#     def process( self ):
#         result = super( UserListView, self ).process()
#         return result

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
                mpmail.sendMail(
                    mail, u.email,
                    subject = form.vars.mail_subject, message = form.vars.mail_text )
            response.flash = T( 'Mail sent' )
        elif form.errors:
            response.flash = T( 'Errors in form' )
        return Storage( dict=dict( user_list=user_list, form=form ), redirect=None )

    #------------------------------------------------------------------
    def do_process( self ):
        #------------------------------------------------------------------
        request = current.request
        response = current.response
        session = current.session
        T = current.T
        db = self.db
        auth = session.auth
        redirect = None

        term.printLog( 'request.args: ' + repr( request.args ) )
        term.printLog( 'request.vars: ' + repr( request.vars ) )

        qdata = self.get_table_qdata_dict()

#        term.printDebug( 'query_vars: %s' % repr( self.query_vars ) )
        self.parse_request_vars( request.post_vars, request.get_vars )
#        term.printDebug( 'query_vars: %s' % repr( self.query_vars ) )

        page = 0
        if request.args:                    # page
            page = int( request.args( 0 ) )
            self.query_vars.qv_offset = self.query_vars.qv_limit * page

        action = request.post_vars.action
        term.printDebug( 'action: ' + repr( action ) )

        if action == self.new_record_action:
#             term.printDebug( 'NEW' )
            redirect = URL( c=self.controller_name, f='edit', args=[ 0 ] )
            return Storage( dict=dict(), redirect=redirect )

        tdef = self.get_table_view_dict()

#         term.printDebug( 'order: %s' % ( repr( order ) ) )
        orderby = tfact.getOrderBy( tdef, self.query_vars.qv_order )
#         term.printDebug( 'orderby: %s' % ( repr( orderby ) ) )
        qd = self.get_query_data( orderby )

#         term.printLog( 'qd: %s' % ( repr( qd ) ) )
        recCount = self.get_record_count( qd )
#         term.printLog( 'recCount: %s \nqd: %s' % (repr(recCount), repr( qd )) )
        if qd.offset > recCount:
            qd.offset = 0
        rows = self.get_record_list( qd )
        div = DIV()
        if not self.list_title:
            self.list_title = T( 'List of %(table_name)s',
                                 dict( table_name=self.table_model.table_name ) )
        div.append( H3( self.list_title ) )
#        term.printDebug( 'self.query_vars: %s' % ( repr( self.query_vars ) ) )
        optTable = tfact.getNavOptions( T,
                                        recCount,
                                        qdata,
                                        self.query_vars,
                                        self.query_vars.qv_offset,
                                        self.query_vars.qv_limit,
                                        width=8,
                                        functionName='list',
                                        titleCssClass='small w10pct',
                                        cellCssClass='small w15pct' )
        table = tfact.getTable( tdef,
                                rows,
                                controller='users',
                                function='list',
                                order=self.query_vars.qv_order,
                                highlight_row_class='highlight_row',
                                query_vars=self.query_vars )

        form = FORM()
        form.append( optTable )
        form.append( table )
        div.append( form )

        if form.accepts( request.vars, session ):
            term.printLog( repr( form.vars ) )

            term.printLog( 'form.vars: ' + repr( form.vars ) )
            term.printLog( 'request.post_vars: ' + repr( request.post_vars ) )
            if action == ACT_SEND_MAIL:
                userList = []
                for chk in form.vars:
                    value = form.vars[ chk ]
                    if value == 'on':
                        term.printLog( 'chk: ' + repr( chk ) )
                        userId = int( chk.split( '_' )[-1] )
                        userList.append( userId )
                if userList:
                    redirect( URL( r=request, f='send_mail', args = userList ) )

            page = session.svars[ KQV_OFFSET ] / session.svars[ KQV_LIMIT ]
            redirect = URL( r=request, f='list', args=page )

        title = T( 'User list' )
        return Storage( dict=dict( contents=div, page_title=title ), redirect=redirect )

    #------------------------------------------------------------------
