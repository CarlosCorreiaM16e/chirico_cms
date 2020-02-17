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
KQV_THREAD_TYPE_ID = KQV_PREFIX + 'thread_type_id'
FORUM_DIV_ID = 'forum_div'

ACT_DELETE_THREADS = 'act_delete_threads'


class ForumDiscussionView( BaseListPlasticView ):
    controller_name = 'forum'
    function_name = 'list'


    def __init__( self, db ):
        super( ForumDiscussionView, self ).__init__( db )

        T = current.T
        self.table_model = db_tables.get_table_model( 'thread', db=db )
        term.printDebug( 'table_model: %s' % repr( self.table_model ) )

        self.new_record_title = T( 'New Thread' )
        self.list_title = T( 'Forum list' )
        self.nav.width = 3
        self.content_div_id = FORUM_DIV_ID

        self.append_var( KQV_AUTH_USER_ID, fld_type=KDT_INT )
        self.append_var( KQV_THREAD_TYPE_ID, fld_type=KDT_INT )

        #         self.print_query = True
        #        term.printDebug( 'query_vars: %s' % repr( self.query_vars ) )


    def do_process( self ):
        return super( ForumDiscussionView, self ).do_process()


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
                                      'thread_title', 'thread_type_name' ],
                     KTF_SORTABLE_COLS: [ 't_id', 'created_on', 'created_by_name',
                                          'thread_title', 'thread_type_name' ],
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
                                 'thread_type_id': { KTF_TITLE: T( 'thread type id' ),
                                                      KTF_TYPE: KDT_INT,
                                                      KTF_CELL_CLASS: 'table_border',
                                                      },
                                 'thread_type_name': { KTF_TITLE: T( 'Type' ),
                                                        KTF_TYPE: KDT_CHAR,
                                                        KTF_CELL_CLASS: 'table_border',
                                                        },
                                 },
                     }
            self.register_tdef( tdef )
        return self.tdef


    def get_table_qdata_dict( self, extra_buttons={} ):
        if not self.qdata:
            qdata = { KTF_BUTTONS: [],
                      KTF_COL_ORDER: [],
                      KTF_COLS: {},
                     }
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
                ts.is_closed,
                t.thread_type_id,
                tt.thread_type_name,
                tt.meta_name
            '''


    def get_query_from( self ):
        return '''
            from thread t
                join thread_status ts on t.thread_status_id = ts.id 
                join thread_type tt on t.thread_type_id = tt.id 
                join auth_user au on au.id = t.created_by
            '''


    def get_query_data( self, orderby=None ):
        qd = super( ForumDiscussionView, self ).get_query_data( orderby )
        auth = current.auth
        qd.addAnd( QueryData( 'ts.is_closed = false' ) )
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

        qv_thread_type_id =  self.query_vars.get( KQV_THREAD_TYPE_ID )
        if qv_thread_type_id:
            qd.addAnd( QueryData( 't.thread_type_id = %(qv_thread_type_id)s',
                                  { 'qv_thread_type_id': qv_thread_type_id } ) )
        term.printDebug( repr( qd ) )
        return qd



