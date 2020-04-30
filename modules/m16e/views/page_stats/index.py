# -*- coding: utf-8 -*-
# this file is released under public domain and you can use without limitations

from m16e.db import db_tables
from gluon import current
from gluon.html import DIV, H3, TABLE, TR, TD, INPUT, A, URL, SPAN, BUTTON, FORM, LABEL
from gluon.storage import Storage
from m16e import term, htmlcommon, user_factory
from m16e.db.querydata import QueryData
from m16e.kommon import ACT_NEW_RECORD, KQV_PREFIX, KDT_INT, KDT_CHAR, KDT_TIMESTAMP, KDT_BOOLEAN, KDT_SELECT_INT
from m16e.ktfact import KTF_COL_ORDER, KTF_SORTABLE_COLS, KTF_CELL_CLASS, KTF_COLS, KTF_TITLE, KTF_TYPE, KTF_BUTTONS, \
    KTF_CELL_LINK, KTF_LINK_C, KTF_LINK_F, KTF_ARGS_F, KTF_FILTER_PANEL, KTF_NAME, KTF_ID, KTF_VALUE, KTF_CSS_CLASS
from m16e.views.plastic_view import BaseListPlasticView

KQV_PATH_INFO = KQV_PREFIX + 'path_info'
KQV_START_TS = KQV_PREFIX + 'start_ts'
KQV_STOP_TS = KQV_PREFIX + 'stop_ts'
KQV_AUTH_USER_ID = KQV_PREFIX + 'auth_user_id'
KQV_AUTH_USER_ID_OP = KQV_PREFIX + 'auth_user_id_op'

ACT_DAILY_TOTALS = 'act_daily_totals'


class PageStatsIndexView( BaseListPlasticView ):
    def __init__( self,
                  db,
                  order_type=KDT_INT,
                  order_value=1,
                  invoke_process_form=False,
                  order_hidden=True
                  ):
        super( PageStatsIndexView, self ).__init__( db,
                                                    order_type=order_type,
                                                    order_value=order_value,
                                                    invoke_process_form=invoke_process_form,
                                                    order_hidden=order_hidden )
        T = current.T
        self.table_model = db_tables.get_table_model( 'page_log', db=db )
        # self.nav.width = 4
        self.append_var( KQV_PATH_INFO, fld_type=KDT_CHAR )
        self.append_var( KQV_START_TS, fld_type=KDT_TIMESTAMP )
        self.append_var( KQV_STOP_TS, fld_type=KDT_TIMESTAMP )
        self.append_var( KQV_AUTH_USER_ID, fld_type=KDT_SELECT_INT )
        self.append_var( KQV_AUTH_USER_ID_OP, fld_type=KDT_BOOLEAN )
        self.list_title = T( 'Page stats' )
        self.print_query = True


    def get_inhibit_actions( self ):
        return [ ACT_NEW_RECORD ]


    def get_query_data( self, orderby=None ):
        term.printLog( 'self.query_vars: ' + repr( self.query_vars ) )
        qd = super( PageStatsIndexView, self ).get_query_data( orderby )
        # path_info
        path_info = self.query_vars.get( KQV_PATH_INFO )
        if path_info:
            qd.addAnd( QueryData( 'path_info = %(path_info)s',
                                  { 'path_info': path_info } ) )
        # start_ts
        start_ts = self.query_vars.get( KQV_START_TS )
        if start_ts:
            qd.addAnd( QueryData( 'ts >= %(start_ts)s',
                                  { 'start_ts': start_ts } ) )
        # stop_ts
        stop_ts = self.query_vars.get( KQV_STOP_TS )
        if stop_ts:
            qd.addAnd( QueryData( 'ts <= %(stop_ts)s',
                                  { 'stop_ts': stop_ts } ) )
        # auth_user_id_op
        auth_user_id_op = self.query_vars.get( KQV_AUTH_USER_ID_OP )
        if auth_user_id_op:
            op = '!='
        else:
            op = '='
        # auth_user_id
        auth_user_id = self.query_vars.get( KQV_AUTH_USER_ID )
        if auth_user_id:
            qd.addAnd( QueryData( 'auth_user_id ' + op + ' %(auth_user_id)s',
                                  { 'auth_user_id': auth_user_id } ) )
        return qd


    def get_table_view_dict( self ):
        T = current.T
        tdef = { KTF_COL_ORDER: [ 'id', 'path_info', 'client_ip', 'ts', 'auth_user_id',
                                  'is_tablet', 'is_mobile', 'os_name', 'browser_name', 'browser_version' ],
                 KTF_SORTABLE_COLS: [ 'id', 'path_info', 'client_ip', 'ts', 'auth_user_id',
                                      'is_tablet', 'is_mobile', 'os_name', 'browser_name', 'browser_version' ],
                 KTF_CELL_CLASS: 'table_border',
                 KTF_COLS: { 'id': { KTF_TITLE: T( 'Page access Id' ),
                                     KTF_TYPE: KDT_INT
                                     },
                             'path_info': { KTF_TITLE: T( 'Page' ),
                                            KTF_TYPE: KDT_CHAR },
                             'client_ip': { KTF_TITLE: T( 'Client IP' ),
                                            KTF_TYPE: KDT_CHAR },
                             'ts': { KTF_TITLE: T( 'When' ),
                                     KTF_TYPE: KDT_TIMESTAMP },
                             'is_tablet': { KTF_TITLE: T( 'Tablet' ),
                                            KTF_TYPE: KDT_BOOLEAN },
                             'is_mobile': { KTF_TITLE: T( 'Mobile' ),
                                            KTF_TYPE: KDT_BOOLEAN },
                             'os_name': { KTF_TITLE: T( 'OS' ),
                                          KTF_TYPE: KDT_CHAR },
                             'browser_name': { KTF_TITLE: T( 'Browser' ),
                                               KTF_TYPE: KDT_CHAR },
                             'browser_version': { KTF_TITLE: T( 'Version' ),
                                                  KTF_TYPE: KDT_CHAR },
                             'auth_user_id': { KTF_TITLE: T( 'User ID' ),
                                               KTF_TYPE: KDT_INT,
                                               KTF_CELL_LINK: { KTF_LINK_C: 'user_admin',
                                                                KTF_LINK_F: 'edit',
                                                                KTF_ARGS_F: [ 'auth_user_id' ],
                                                                KTF_TITLE: T( 'Edit user' ) },
                                               },
                             },
                 }
        self.register_tdef( tdef )
        return self.tdef


    def get_table_qdata_dict( self, extra_buttons={ } ):
        T = current.T
        qdata = { KTF_BUTTONS: [],
                  KTF_COL_ORDER: [],
                  KTF_COLS: {},
                  KTF_FILTER_PANEL: True
                  }
        self.register_qdata( qdata )
        return self.qdata


    def get_filter_panel( self ):
        T = current.T
        db = self.db
        filter_panel = DIV()
        rdiv = DIV(_class='row')
        # KQV_PATH_INFO
        rdiv.append( DIV( LABEL( T( 'Page' ) + ':' ),
                          _class='col-md-2 text-right' ) )
        path_info = self.query_vars.get( KQV_PATH_INFO )
        inp_path_info = htmlcommon.get_input_field( KQV_PATH_INFO,
                                                    value=path_info,
                                                    input_id=KQV_PATH_INFO,
                                                    value_type=KDT_CHAR,
                                                    css_class='small' )
        rdiv.append( DIV( inp_path_info,
                          _class='col-md-2' ) )

        # KQV_START_TS
        rdiv.append( DIV( LABEL( T( 'Since' ) + ':' ),
                          _class='col-md-2 text-right' ) )
        dt_since = self.query_vars.get( KQV_START_TS )
        inp_dt_since = htmlcommon.get_input_field( KQV_START_TS,
                                                   value=dt_since,
                                                   input_id=KQV_START_TS,
                                                   value_type=KDT_TIMESTAMP,
                                                   css_class='small' )
        rdiv.append( DIV( inp_dt_since,
                          _class='col-md-2' ) )
        # KQV_STOP_TS
        rdiv.append( DIV( LABEL( T( 'Until' ) + ':' ),
                          _class='col-md-2 text-right' ) )
        dt_until = self.query_vars.get( KQV_STOP_TS )
        inp_dt_until = htmlcommon.get_input_field( KQV_STOP_TS,
                                                    value=dt_until,
                                                    input_id=KQV_STOP_TS,
                                                    value_type=KDT_TIMESTAMP,
                                                    css_class='small' )
        rdiv.append( DIV( inp_dt_until,
                          _class='col-md-2' ) )
        filter_panel.append( rdiv )
        rdiv = DIV( _class='row' )
        # KQV_AUTH_USER_ID
        rdiv.append( DIV( LABEL( T( 'User' ) + ':' ),
                          _class='col-md-2 text-right' ) )
        auth_user_id = self.query_vars.get( KQV_AUTH_USER_ID )
        u_list = user_factory.get_user_list_as_options( insert_blank=True,
                                                        db=db )
        inp_auth_user_id = htmlcommon.get_selection_field( KQV_AUTH_USER_ID,
                                                           input_id=KQV_AUTH_USER_ID,
                                                           options=u_list,
                                                           selected=auth_user_id )
        rdiv.append( DIV( inp_auth_user_id,
                          _class='col-md-3' ) )
        auth_user_id_op = self.query_vars.get( KQV_AUTH_USER_ID_OP )
        rdiv.append( DIV( LABEL( '!=:' ),
                          htmlcommon.get_checkbox( KQV_AUTH_USER_ID_OP,
                                                   value=auth_user_id_op,
                                                   input_id=KQV_AUTH_USER_ID_OP,
                                                   title=T( 'Different' ) ),
                          _class='col-md-1 text-right' ) )
        filter_panel.append( rdiv )

        return filter_panel






