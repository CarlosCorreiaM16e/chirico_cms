# -*- coding: utf-8 -*-

from gluon import current
from m16e import term
from m16e.db.querydata import QueryData
from m16e.kommon import KDT_INT, KDT_CHAR, KDT_TIMESTAMP, \
    KQV_SHOW_ALL, KQV_ORDER, KQV_PREFIX, ACT_NEW_RECORD, TEST_MATCH_EQ, TEST_MATCH_DIFF, KDT_SELECT_CHAR, \
    KDT_SELECT_INT, TEST_MATCH_LIST
from m16e.ktfact import KTF_COL_ORDER, KTF_SORTABLE_COLS, KTF_CELL_CLASS, \
    KTF_COLS, KTF_TITLE, KTF_TYPE, KTF_BUTTONS, KTF_OPTIONS
from m16e.views.plastic_view import BaseListPlasticView


KQV_CLIENT_IP = KQV_PREFIX + 'client_ip'
KQV_CLIENT_IP_OP = KQV_PREFIX + 'client_ip_op'
KQV_EMAIL = KQV_PREFIX + 'email'
KQV_TIME_STAMP = KQV_PREFIX + 'time_stamp'
KQV_TIME_STAMP_START = KQV_TIME_STAMP + '_start'
KQV_TIME_STAMP_END = KQV_TIME_STAMP + '_end'

#----------------------------------------------------------------------
class AuthEventViewerListView( BaseListPlasticView ):
    controller_name = 'auth_event_viewer'

    #----------------------------------------------------------------------
    def __init__( self, db ):
        super( AuthEventViewerListView, self ).__init__( db )

        if KQV_SHOW_ALL in self.query_vars:
            del( self.query_vars[ KQV_SHOW_ALL ] )
        T = current.T

        self.append_var( KQV_CLIENT_IP, fld_type=KDT_CHAR )
        self.append_var( KQV_CLIENT_IP_OP, fld_type=KDT_INT )
        self.append_var( KQV_EMAIL, fld_type=KDT_CHAR )
        self.append_var( KQV_TIME_STAMP_START, fld_type=KDT_TIMESTAMP )
        self.append_var( KQV_TIME_STAMP_END, fld_type=KDT_TIMESTAMP )

        self.list_title = T( 'Event list' )

        self.nav.width = 3

        self.query_vars[ KQV_ORDER ] = -1

#        term.printDebug( 'query_vars: %s' % repr( self.query_vars ) )

    #------------------------------------------------------------------
    def get_table_name( self ):
        return 'auth_event'


    def get_inhibit_actions( self ):
        return [ ACT_NEW_RECORD ]


    def get_query_data( self, orderby=None ):
        term.printLog( 'self.query_vars: ' + repr( self.query_vars ) )
        qd = super( AuthEventViewerListView, self ).get_query_data( orderby )
        # client_ip
        client_ip = self.query_vars.get( KQV_CLIENT_IP )
        if client_ip:
            client_ip_op = int( self.query_vars.get( KQV_CLIENT_IP_OP ) )
            term.printDebug( 'client_ip_op (%s): %s' % (type( client_ip_op ), repr( client_ip_op )) )
            client_ip = '%%' + client_ip.replace( ' ', '%%' ) + '%%'
            if client_ip_op == TEST_MATCH_EQ:
                query = 'ae.client_ip ilike( %(client_ip)s )'
            elif client_ip_op == TEST_MATCH_DIFF:
                query = 'ae.client_ip not ilike( %(client_ip)s )'
            qd.addAnd( QueryData( query, { 'client_ip': client_ip } ) )
        # email
        email = self.query_vars.get( KQV_EMAIL )
        if email:
            email = '%%' + email.replace( ' ', '%%' ) + '%%'
            qd.addAnd( QueryData( 'au.email ilike( %(email)s )',
                                  { 'email': email } ) )
        # time_stamp_start
        time_stamp_start = self.query_vars.get( KQV_TIME_STAMP_START )
        if time_stamp_start:
            qd.addAnd( QueryData( 'ae.time_stamp >= %(time_stamp_start)s',
                                  { 'time_stamp_start': time_stamp_start } ) )
        # time_stamp_end
        time_stamp_end = self.query_vars.get( KQV_TIME_STAMP_END )
        if time_stamp_end:
            qd.addAnd( QueryData( 'ae.time_stamp <= %(time_stamp_end)s',
                                  { 'time_stamp_end': time_stamp_end } ) )
        return qd

    #------------------------------------------------------------------
    def get_query_from( self ):
        return 'from auth_event ae join auth_user au on au.id = ae.user_id'

    #------------------------------------------------------------------
    def get_query_select( self ):
        return '''
            select
                ae.id,
                time_stamp,
                client_ip,
                user_id,
                email,
                origin,
                description
                '''

#     #------------------------------------------------------------------
#     def get_record_list( self,
#                          qd=None,
#                          alias=[],
#                          print_query=False ):
#         rows = super( AuthEventViewerListView, self ).get_record_list( qd=qd,
#                                                                        alias=alias,
#                                                                        print_query=print_query )
# #         db = current.db
# #         auth = current.auth
# #         ac_model = app.get_table_model( 'app_config', db=db )
# #         ac = ac_model[ 1 ]
# #         for row in rows:
# #             row.time_stamp = tz.convert_timestamp( row.time_stamp,
# #                                                    ac.server_timezone,
# #                                                    auth.user.user_timezone or 'Europe/Lisbon' )
#         return rows

    #----------------------------------------------------------------------
    def get_table_view_dict( self ):
        T = current.T
        tdef = {
            KTF_COL_ORDER: [ 'id', 'time_stamp', 'client_ip', 'user_id', 'email', 'origin', 'description' ],
            KTF_SORTABLE_COLS: [ 'id', 'time_stamp', 'client_ip', 'user_id', 'email', 'origin', 'description' ],
            KTF_CELL_CLASS: 'table_border',
            KTF_COLS: {
                 'id': {
                    KTF_TITLE: T( 'Id' ),
                    KTF_TYPE: KDT_INT,
                    KTF_CELL_CLASS: 'table_border',
                 },
                 'time_stamp': {
                    KTF_TITLE: T( 'Date/time' ),
                    KTF_TYPE: KDT_TIMESTAMP,
                    KTF_CELL_CLASS: 'table_border',
                 },
                 'client_ip': {
                    KTF_TITLE: T( 'Client IP' ),
                    KTF_TYPE: KDT_CHAR,
                    KTF_CELL_CLASS: 'table_border',
                 },
                 'user_id': {
                    KTF_TITLE: T( 'User ID' ),
                    KTF_TYPE: KDT_INT,
                    KTF_CELL_CLASS: 'table_border',
                 },
                 'email': {
                    KTF_TITLE: T( 'E-mail' ),
                    KTF_TYPE: KDT_CHAR,
                    KTF_CELL_CLASS: 'table_border',
                 },
                 'origin': {
                    KTF_TITLE: T( 'Origin' ),
                    KTF_TYPE: KDT_CHAR,
                    KTF_CELL_CLASS: 'table_border',
                 },
                 'description': {
                    KTF_TITLE: T( 'Description' ),
                    KTF_TYPE: KDT_CHAR,
                    KTF_CELL_CLASS: 'table_border',
                 },
            }
        }
        self.tdef = tdef
        return self.tdef


#----------------------------------------------------------------------
    def get_table_qdata_dict( self, extra_buttons={} ):
        T = current.T
        qdata = { KTF_BUTTONS: [],
                  KTF_COL_ORDER: [ KQV_CLIENT_IP, KQV_CLIENT_IP_OP, KQV_EMAIL,
                                   KQV_TIME_STAMP_START, KQV_TIME_STAMP_END ],
                  KTF_COLS: { KQV_CLIENT_IP: { KTF_TITLE: T( 'Client IP' ),
                                               KTF_TYPE: KDT_CHAR },
                              KQV_CLIENT_IP_OP: { KTF_TITLE: T( 'Test' ),
                                                  KTF_TYPE: KDT_SELECT_INT,
                                                  KTF_OPTIONS: TEST_MATCH_LIST },
                              KQV_EMAIL: { KTF_TITLE: T( 'Email' ),
                                           KTF_TYPE: KDT_CHAR },
                              KQV_TIME_STAMP_START: { KTF_TITLE: T( 'Since' ),
                                                      KTF_TYPE: KDT_TIMESTAMP },
                              KQV_TIME_STAMP_END: { KTF_TITLE: T( 'Until' ),
                                                    KTF_TYPE: KDT_TIMESTAMP },
            },
        }
        self.qdata = qdata
        return self.qdata

    #----------------------------------------------------------------------

