# -*- coding: utf-8 -*-

from forum_threads import thread_factory
from m16e.db import db_tables
from gluon import current, URL
from m16e import term
from m16e import user_factory
from m16e.db.querydata import QueryData
from m16e.kommon import KQV_PREFIX, KDT_CHAR, KDT_BOOLEAN, KDT_INT, KDT_TIMESTAMP, \
    KDT_SELECT_INT, ACT_CHECK_ALL, ACT_UNCHECK_ALL, K_ROLE_SUPPORT, storagize, K_ROLE_ADMIN, K_ROLE_DEVELOPER
from m16e.ktfact import KTF_COL_ORDER, KTF_SORTABLE_COLS, KTF_CELL_CLASS, \
    KTF_COLS, KTF_TITLE, KTF_TYPE, \
    KTF_CELL_LINK, KTF_LINK_C, KTF_LINK_F, KTF_ARGS, KTF_ARGS_F, \
    KTF_BUTTONS, KTF_NAME, KTF_VALUE, KTF_OPTIONS, KTF_CHECKBOXES, K_CHK_ID_PREFIX, KTF_CHECKBOX_ID, KTF_ONCLICK, \
    KTF_CSS_CLASS
from m16e.ui.elements import UiButton, UiIcon, BTN_SUCCESS
from m16e.user_factory import is_in_group
from m16e.views.plastic_table import extract_ids_from_vars
from m16e.views.plastic_view import BaseListPlasticView, BT_NEW_RECORD_ID

KQV_AUTH_USER_ID = KQV_PREFIX + 'auth_user_id'
KQV_THREAD_STATUS_ID = KQV_PREFIX + 'thread_status_id'
KQV_THREAD_TYPE_ID = KQV_PREFIX + 'thread_type_id'
KQV_SHOW_CLOSED = KQV_PREFIX + 'show_closed'
FORUM_DIV_ID = 'forum_div'

ACT_DELETE_THREADS = 'act_delete_threads'


class ForumListView( BaseListPlasticView ):
    controller_name = 'forum'
    function_name = 'list'


    def __init__( self, db ):
        super( ForumListView, self ).__init__( db )

        T = current.T
        self.table_model = db_tables.get_table_model( 'thread', db=db )
        term.printDebug( 'table_model: %s' % repr( self.table_model ) )

        self.new_record_title = T( 'New Thread' )
        self.list_title = T( 'Forum list' )
        self.nav.width = 3
        self.content_div_id = FORUM_DIV_ID

        self.append_var( KQV_AUTH_USER_ID, fld_type=KDT_INT )
        self.append_var( KQV_THREAD_STATUS_ID, fld_type=KDT_INT )
        self.append_var( KQV_THREAD_TYPE_ID, fld_type=KDT_INT )
        self.append_var( KQV_SHOW_CLOSED, fld_type=KDT_BOOLEAN )

        #         self.print_query = True
        #        term.printDebug( 'query_vars: %s' % repr( self.query_vars ) )


    def do_process( self ):
        return super( ForumListView, self ).do_process()


    def get_new_record_function(self):
        return 'new'


    def get_new_record_button( self ):
        T = current.T
        nr_bt = UiButton( text=self.new_record_title,
                          ui_icon=UiIcon( 'plus' ),
                          tip=T( 'Create new record' ),
                          action=self.new_record_action,
                          input_id=BT_NEW_RECORD_ID,
                          button_style=BTN_SUCCESS,
                          css_class='btn-lg')
        return nr_bt


    def get_table_view_dict( self ):
        if not self.tdef:
            T = current.T
            edit_f = 'view'
            tdef = { KTF_COL_ORDER: [ 't_id', 'created_on', 'created_by_name',
                                      'thread_title', 'thread_status_name', 'thread_type_name',
                                      'closed_time' ],
                     KTF_SORTABLE_COLS: [ 't_id', 'created_on', 'created_by_name',
                                          'thread_title', 'thread_status_name', 'thread_type_name',
                                          'closed_time' ],
                     KTF_CELL_CLASS: 'table_border',
                     KTF_COLS: { 't_id': { KTF_TITLE: T( 'Id' ),
                                           KTF_TYPE: KDT_INT,
                                           KTF_CELL_CLASS: 'table_border',
                                           KTF_CELL_LINK: { KTF_LINK_C: self.controller_name,
                                                            KTF_LINK_F: edit_f,
                                                            KTF_ARGS_F: [ 't_id' ]
                                                            }
                                           },
                                 'created_by_name': { KTF_TITLE: T( 'Author' ),
                                               KTF_TYPE: KDT_CHAR,
                                               KTF_CELL_CLASS: 'table_border',
                                               },
                                 'created_on': { KTF_TITLE: T( 'Date/time' ),
                                                KTF_TYPE: KDT_TIMESTAMP,
                                                KTF_CELL_CLASS: 'table_border',
                                                },
                                 'thread_title': { KTF_TITLE: T( 'Title' ),
                                                   KTF_TYPE: KDT_CHAR,
                                                   KTF_CELL_CLASS: 'table_border',
                                                   },
                                 'thread_status_id': { KTF_TITLE: T( 'Thread status id' ),
                                                        KTF_TYPE: KDT_INT,
                                                        KTF_CELL_CLASS: 'table_border',
                                                        },
                                 'thread_status_name': { KTF_TITLE: T( 'Status' ),
                                                          KTF_TYPE: KDT_CHAR,
                                                          KTF_CELL_CLASS: 'table_border',
                                                          },
                                 'thread_type_id': { KTF_TITLE: T( 'thread type id' ),
                                                      KTF_TYPE: KDT_INT,
                                                      KTF_CELL_CLASS: 'table_border',
                                                      },
                                 'thread_type_name': { KTF_TITLE: T( 'Type' ),
                                                        KTF_TYPE: KDT_CHAR,
                                                        KTF_CELL_CLASS: 'table_border',
                                                        },
                                 'closed_time': { KTF_TITLE: T( 'Closed time' ),
                                                  KTF_TYPE: KDT_TIMESTAMP,
                                                  KTF_CELL_CLASS: 'table_border',
                                                  },
                                 },
                     KTF_CHECKBOXES: [ { KTF_NAME: K_CHK_ID_PREFIX + '%d',
                                         KTF_CHECKBOX_ID: 't_id',
                                         KTF_TITLE: T( 'Select' ) },
                                       ],
                     }
            self.register_tdef( tdef )
        return self.tdef


    def get_table_qdata_dict( self, extra_buttons={} ):
        if not self.qdata:
            T = current.T
            db = self.db
            jq_check_all = '''
                jQuery( '#%s input[name^="%s"]' ).prop( 'checked', true ); return false;
                ''' % (FORUM_DIV_ID, K_CHK_ID_PREFIX)
            jq_uncheck_all = '''
                jQuery( '#%s input[name^="%s"]' ).prop( 'checked', false ); return false;
                ''' % (FORUM_DIV_ID, K_CHK_ID_PREFIX)
            term.printDebug( 'jq_check_all: %s' % jq_check_all )

            thread_status_model = db_tables.get_table_model( 'thread_status', db=db )
            thread_type_model = db_tables.get_table_model( 'thread_type', db=db )

            if is_in_group( K_ROLE_DEVELOPER ):
                auth_user_list = db( db.auth_user.id > 0 ).select( orderby='first_name' )
            else:
                auth_user_list = db( db.auth_user.registration_key == '' ).select( orderby='first_name' )
            auth_user_options = [ (r.id, '%s (%s)' % (r.first_name, r.email)) for r in auth_user_list ]
            auth_user_options.insert( 0, ('', '') )

            thread_status_list = thread_status_model.select( orderby='id' )
            thread_status_options = [ (r.id, r.thread_status_name) for r in thread_status_list ]
            thread_status_options.insert( 0, ('', '') )

            thread_type_list = thread_type_model.select( orderby='id' )
            thread_type_options = [ (r.id, r.thread_type_name) for r in thread_type_list ]
            thread_type_options.insert( 0, ('', '') )

            assigned_user_list = user_factory.get_user_list( group=['dev', 'tec'],
                                                             db=db )
            assigned_user_options = [ (r.id, '%s (%s)' % (r.first_name, r.email)) for r in assigned_user_list ]
            assigned_user_options.insert( 0, ('', '') )

            qdata = { KTF_BUTTONS: [ { KTF_NAME: 'action',
                                       KTF_TITLE: T( 'Check all' ),
                                       KTF_VALUE: ACT_CHECK_ALL,
                                       KTF_ONCLICK: jq_check_all,
                                       KTF_CSS_CLASS: 'btn btn-info' },
                                     { KTF_NAME: 'action',
                                       KTF_TITLE: T( 'Uncheck all' ),
                                       KTF_VALUE: ACT_UNCHECK_ALL,
                                       KTF_ONCLICK: jq_uncheck_all,
                                       KTF_CSS_CLASS: 'btn btn-info' }
                                     ],
                      KTF_COL_ORDER: [ KQV_THREAD_STATUS_ID,
                                       KQV_THREAD_TYPE_ID, KQV_SHOW_CLOSED ],
                      KTF_COLS: { KQV_THREAD_STATUS_ID: { KTF_TITLE: T( 'Status' ),
                                                          KTF_TYPE: KDT_SELECT_INT,
                                                          KTF_OPTIONS: thread_status_options },
                                  KQV_THREAD_TYPE_ID: { KTF_TITLE: T( 'Type' ),
                                                        KTF_TYPE: KDT_SELECT_INT,
                                                        KTF_OPTIONS: thread_type_options },
                                  KQV_SHOW_CLOSED: { KTF_TITLE: T( 'Show closed' ),
                                                     KTF_TYPE: KDT_BOOLEAN }
                                  },
                     }
            if is_in_group( K_ROLE_ADMIN ):
                qdata[ KTF_COLS ][ KQV_AUTH_USER_ID ] = { KTF_TITLE: T( 'User' ),
                                                          KTF_TYPE: KDT_SELECT_INT,
                                                          KTF_OPTIONS: auth_user_options }
                qdata[ KTF_COL_ORDER ].append( KQV_AUTH_USER_ID )
            if is_in_group( K_ROLE_SUPPORT ):
                jq_confirm_delete = '''return confirm( "%s" );'''
                qdata[ KTF_BUTTONS ].append( { KTF_NAME: 'action',
                                               KTF_TITLE: T( 'Delete threads' ),
                                               KTF_VALUE: ACT_DELETE_THREADS,
                                               KTF_ONCLICK: jq_confirm_delete % T( 'Confirm delete threads?' ),
                                               KTF_CSS_CLASS: 'btn btn-danger' } )

            self.register_qdata( qdata )
        return self.qdata


    def get_alias( self ):
        return [ 'au', 't', 'ts', 'tt' ]


    def get_query_select( self ):
        return '''
            select
                t.id as t_id,
                au.id as au_id,
                au.email as au_email,
                au.first_name as created_by_name,
                t.created_on,
                t.thread_title,
                t.thread_status_id,
                ts.thread_status_name,
                ts.is_closed,
                t.thread_type_id,
                tt.thread_type_name,
                tt.meta_name,
                t.closed_time 
            '''


    def get_query_from( self ):
        return '''
            from thread t
                join thread_status ts on t.thread_status_id = ts.id 
                join thread_type tt on t.thread_type_id = tt.id 
                join auth_user au on au.id = t.created_by
            '''


    def get_query_data( self, orderby=None ):
        qd = super( ForumListView, self ).get_query_data( orderby )
        auth = current.auth
        qdu = QueryData( "tt.meta_name = 'open-discussion'" )
        qdu.addOr( QueryData( '''
            %(uid)s in ( select auth_user_id 
                            from thread_subscriber
                            where thread_id = t.id )''' % dict( uid=auth.user_id ) ) )
        qd.addAnd( qdu )
        qv_auth_user_id =  self.query_vars.get( KQV_AUTH_USER_ID )
        if qv_auth_user_id:
            qd.addAnd( QueryData( 't.created_by = %(qv_auth_user_id)s',
                                  { 'qv_auth_user_id': qv_auth_user_id } ) )

        qv_thread_status_id =  self.query_vars.get( KQV_THREAD_STATUS_ID )
        if qv_thread_status_id:
            qd.addAnd( QueryData( 't.thread_status_id = %(qv_thread_status_id)s',
                                  { 'qv_thread_status_id': qv_thread_status_id } ) )
        qv_show_closed = self.query_vars.get( KQV_SHOW_CLOSED )
        if not qv_show_closed:
            qd.addAnd( QueryData( 'ts.is_closed = false' ) )

        qv_thread_type_id =  self.query_vars.get( KQV_THREAD_TYPE_ID )
        if qv_thread_type_id:
            qd.addAnd( QueryData( 't.thread_type_id = %(qv_thread_type_id)s',
                                  { 'qv_thread_type_id': qv_thread_type_id } ) )
        term.printDebug( repr( qd ) )
        return qd


    def process_pre_validation_actions( self ):
        super( ForumListView, self ).process_pre_validation_actions()
        request = current.request
        response = current.response
        session = current.session
        T = current.T
        db = self.db
        action = request.post_vars.action
        if action == ACT_DELETE_THREADS:
            ids = extract_ids_from_vars( request.vars )
            for t_id in ids:
                thread_factory.delete_thread( t_id, db=db )
            return self.set_result( redirect=URL( c=self.controller_name,
                                                  f=self.function_name ) )


