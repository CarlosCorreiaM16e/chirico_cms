# -*- coding: utf-8 -*-

from m16e import term
from m16e.db.querydata import QueryData
from m16e.kommon import KDT_INT, KDT_CHAR, KDT_TIMESTAMP_PRETTY, KQV_EMAIL, KQV_NAME, KQV_GROUP_ID, KDT_TIMESTAMP, \
    KDT_SELECT_INT, ACT_EDIT_GROUP, K_ROLE_DEVELOPER
from m16e.ktfact import KTF_COL_ORDER, KTF_SORTABLE_COLS, KTF_CELL_CLASS, KTF_COLS, KTF_TITLE, KTF_TYPE, KTF_CELL_LINK, \
    KTF_LINK_C, KTF_LINK_F, KTF_ARGS, KTF_USE_ICON, KTF_CHECKBOXES, KTF_NAME, K_CHK_ID_PREFIX, KTF_CHECKBOX_ID, \
    KTF_BUTTONS, KTF_OPTIONS
from m16e.user_factory import is_in_group
from m16e.views.users.list import UserListView
from gluon import current, URL
from gluon.storage import Storage


class CmsUserListView( UserListView ):
    controller_name = 'user_admin'
    function_name = 'list'


    def __init__( self, db ):
        super( CmsUserListView, self ).__init__( db )
        T = current.T
        self.append_var( KQV_EMAIL, fld_type=KDT_CHAR )
        self.append_var( KQV_NAME, fld_type=KDT_CHAR )
        self.append_var( KQV_GROUP_ID, fld_type=KDT_INT )
        self.list_title = T( 'User list' )


    def do_process( self ):
        return super( CmsUserListView, self ).do_process()


    def get_table_name( self ):
        return 'auth_user'


    def get_query_data( self, orderby=None ):
        db = self.db
        term.printDebug( 'self.query_vars: ' + repr( self.query_vars ) )
        qd = super( CmsUserListView, self ).get_query_data( orderby )
        if not is_in_group( K_ROLE_DEVELOPER ):
            qd.addAnd( QueryData( '''au.registration_key not like( 'dummy' )''' ) )
        no_test = '''au.id not in (
                        select am.user_id
                            from auth_membership am
                                join auth_group ag on am.group_id = ag.id
                            where
                                role = 'test' )
                             '''
        qd.addAnd( QueryData( no_test ) )
        group_id = self.query_vars.get( KQV_GROUP_ID )
        if group_id:
            qd.addAnd( QueryData( 'am.group_id = %(group_id)s',
                                  { 'group_id': group_id } ) )

        name = self.query_vars.get( KQV_NAME )
        if name:
            name = '%%' + name.replace( ' ', '%%' ) + '%%'
            qd.addAnd( QueryData( 'au.first_name ilike( %(name)s )',
                                  { 'name': name } ) )
        email = self.query_vars.get( KQV_EMAIL )
        if email:
            email = '%%' + email.replace( ' ', '%%' ) + '%%'
            qd.addAnd( QueryData( 'au.email ilike( %(email)s )',
                                  { 'email': email } ) )

        term.printDebug( str( qd ) )
        return qd


    def get_query_select( self ):
        query = '''
            select
                au.id,
                au.email,
                au.first_name,
                au.registration_key,
                au.ctime,
                (select time_stamp 
                 from auth_event 
                 where 
                    user_id = au.id and 
                    description ilike( 'User %% Logged-in') 
                 order by id desc limit 1) as last_login
        '''
        return query


    def get_query_from( self ):
        query_form = '''
            from auth_user au
            '''
        group_id = self.query_vars.get( KQV_GROUP_ID )
        if group_id:
            query_form += '''left outer join auth_membership am on am.user_id = au.id
            '''
        return query_form


    def get_record_list( self, qd ):
        db = self.db
        a_list = []
        super( UserListView,
               self ).get_record_list( qd=qd,
                                       alias=a_list )
        q_grp = '''
            select ag.id, ag.role
            from auth_membership am
                join auth_group ag on ag.id = am.group_id
            where
                am.user_id = %s
            order by
                ag.role
        '''
        for row in self.list_rows:
            grp_list = db.executesql( q_grp,
                                      placeholders=[ row.id ],
                                      as_dict=True )
            row.group_list = ', '.join( [ '%s (%d)' % (r[ 'role' ], r[ 'id' ])
                                          for r in grp_list ] )
            # term.printDebug( 'row: %s' % repr( row ) )

        return self.list_rows


    def get_table_view_dict( self ):
        T = current.T
        tdef = { KTF_COL_ORDER: [ 'id', 'email', 'first_name', 'ctime',
                                  'last_login', 'registration_key', 'group_list' ],
                 KTF_SORTABLE_COLS: [ 'id', 'email', 'first_name', 'ctime', 'last_login' ],
                 KTF_CELL_CLASS: 'table_border',
                 KTF_COLS: { 'id': { KTF_TITLE: T( 'Id' ),
                                     KTF_TYPE: KDT_INT,
                                     KTF_CELL_LINK: { KTF_LINK_C: 'user_admin',
                                                      KTF_LINK_F: 'edit',
                                                      KTF_ARGS: [ 'id' ] },
                                     KTF_CELL_CLASS: 'table_border' },
                             'email': { KTF_TITLE: T( 'E-mail' ),
                                        KTF_TYPE: KDT_CHAR,
                                        KTF_CELL_CLASS: 'table_border', },
                             'first_name': { KTF_TITLE: T( 'Name' ),
                                             KTF_TYPE: KDT_CHAR,
                                             KTF_CELL_CLASS: 'table_border', },
                             'registration_key': { KTF_TITLE: T( 'Status' ),
                                                   KTF_TYPE: KDT_CHAR,
                                                   KTF_CELL_CLASS: 'table_border', },
                             'ctime': { KTF_TITLE: T( 'Since' ),
                                        KTF_TYPE: KDT_TIMESTAMP_PRETTY,
                                        KTF_CELL_CLASS: 'table_border', },
                             'last_login': { KTF_TITLE: T( 'Last login' ),
                                             KTF_TYPE: KDT_TIMESTAMP_PRETTY },
                             'group_list': { KTF_TITLE: T( 'Groups' ),
                                             KTF_TYPE: KDT_CHAR,
                                             KTF_CELL_CLASS: 'table_border' }
                             },
                 KTF_CHECKBOXES: [ { KTF_NAME: K_CHK_ID_PREFIX + '%d',
                                     KTF_CHECKBOX_ID: 'id',
                                     KTF_TITLE: T( 'Select' ) },
                                   ],
                 }
        self.register_tdef( tdef )
        # term.printDebug( 'self.tdef: %s' % repr( self.tdef ) )
        return self.tdef


    def get_table_qdata_dict( self, extra_buttons={} ):
        T = current.T
        db = self.db
        group_list = db( db.auth_group.role != 'dev' ).select( orderby='description')
        g_options = [ (g.id, g.description) for g in group_list ]
        g_options.insert( 0, ( '', '') )
        qdata = { KTF_BUTTONS: [],
                  KTF_COL_ORDER: [ KQV_EMAIL, KQV_NAME, KQV_GROUP_ID ],
                  KTF_COLS: { KQV_EMAIL: { KTF_TITLE: T( 'E-mail' ),
                                           KTF_TYPE: KDT_CHAR, },
                              KQV_NAME: { KTF_TITLE: T( 'Name' ),
                                          KTF_TYPE: KDT_CHAR, },
                              KQV_GROUP_ID: { KTF_TITLE: T( 'Group' ),
                                              KTF_TYPE: KDT_SELECT_INT,
                                              KTF_OPTIONS: g_options },
                             },
                }
        self.register_qdata( qdata )
        return self.qdata


    def process_pre_validation_actions( self ):
        super( CmsUserListView, self ).process_pre_validation_actions()
        request = current.request
        db = self.db
        action = request.post_vars.action
        group_id = self.query_vars.get( KQV_GROUP_ID )
        term.printDebug( 'action: ' + repr( action ) )
        if group_id and action == ACT_EDIT_GROUP:
            return Storage( dict=dict(),
                            redirect=URL( c='user_admin',
                                          f='edit_group',
                                          args=[ self.query_vars[ KQV_GROUP_ID ] ] ) )
        return None


    def post_process( self, div_content ):
        db = self.db
        super( CmsUserListView, self ).post_process( div_content )
        self.result.dict[ 'group' ] = db.auth_group[ self.query_vars.get( KQV_GROUP_ID ) ]
