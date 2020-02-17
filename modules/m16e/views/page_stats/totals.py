# -*- coding: utf-8 -*-
# this file is released under public domain and you can use without limitations
from chirico.db import page_factory
from m16e.db import db_tables
from gluon import current
from gluon.html import DIV, H3, TABLE, TR, TD, INPUT, A, URL, SPAN, BUTTON, FORM, LABEL
from gluon.storage import Storage
from m16e import term, htmlcommon
from m16e.db.misc import replace_alias
from m16e.db.querydata import QueryData
from m16e.kommon import ACT_NEW_RECORD, KQV_PREFIX, KDT_INT, KDT_CHAR, KDT_TIMESTAMP, KDT_RAW
from m16e.ktfact import KTF_COL_ORDER, KTF_SORTABLE_COLS, KTF_CELL_CLASS, KTF_COLS, KTF_TITLE, KTF_TYPE, KTF_BUTTONS, \
    KTF_CELL_LINK, KTF_LINK_C, KTF_LINK_F, KTF_ARGS_F, KTF_FILTER_PANEL, KTF_NAME, KTF_ID, KTF_VALUE, KTF_CSS_CLASS
from m16e.views.page_stats.index import PageStatsIndexView, KQV_PATH_INFO, KQV_START_TS, KQV_STOP_TS
from m16e.views.plastic_view import BaseListPlasticView

ACT_SHOW_DAILY = 'act_show_daily'
ACT_SHOW_HOURLY = 'act_show_hourly'
ACT_SHOW_MONTHLY = 'act_show_monthly'


class PageStatsTotalsView( PageStatsIndexView ):
    def __init__( self, db ):
        super( PageStatsTotalsView, self ).__init__( db, order_value=-6 )
        T = current.T
        self.list_title = T( 'Page stats (totals)' )
        self.print_query = True


    def get_inhibit_actions( self ):
        return [ ACT_NEW_RECORD ]


    def get_table_view_dict( self ):
        T = current.T
        tdef = { KTF_COL_ORDER: [ 'path_info', 'page_name', 'year', 'month', 'day', 'total' ],
                 KTF_SORTABLE_COLS: [ 'path_info', 'total' ],
                 KTF_CELL_CLASS: 'table_border',
                 KTF_COLS: { 'path_info': { KTF_TITLE: T( 'Page' ),
                                            KTF_TYPE: KDT_CHAR },
                             'page_name': { KTF_TITLE: T( 'Name' ),
                                            KTF_TYPE: KDT_CHAR },
                             'year': { KTF_TITLE: T( 'Year' ),
                                        KTF_TYPE: KDT_INT },
                             'month': { KTF_TITLE: T( 'Month' ),
                                        KTF_TYPE: KDT_INT },
                             'day': { KTF_TITLE: T( 'Day' ),
                                      KTF_TYPE: KDT_INT },
                             'total': { KTF_TITLE: T( 'Total' ),
                                        KTF_TYPE: KDT_INT },
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

        # filter_panel.append( rdiv )
        #
        # rdiv = DIV(_class='row')
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
        bt_list = []
        bt_list.append( htmlcommon.get_button( T( 'Hourly' ),
                                               value=ACT_SHOW_HOURLY,
                                               css_class='btn btn-info' ) )
        bt_list.append( htmlcommon.get_button( T( 'Daily' ),
                                               value=ACT_SHOW_DAILY,
                                               css_class='btn btn-info' ) )
        bt_list.append( htmlcommon.get_button( T( 'Monthly' ),
                                               value=ACT_SHOW_MONTHLY,
                                               css_class='btn btn-info' ) )

        filter_panel.append( DIV( DIV( ),
                                  _class='row' ) )

        return filter_panel


    def get_query_select( self ):
        s = '''
            select 
                path_info, 
                extract( year from ts ) as year, 
                extract( month from ts ) as month, 
                extract( day from ts ) as day, 
                count( distinct client_ip) as total 
        '''
        return s


    def get_query_from( self ):
        s = '''
            from page_log
            '''
        return s


    def get_query_group_by( self ):
        return 'path_info, year, month, day'


    # def get_record_count( self,
    #                       qd=None,
    #                       alias=None,
    #                       print_query=None,
    #                       force_refresh=False ):
    #     term.printDebug( 'self.row_count: %s' % repr( self.row_count ) )
    #     if self.row_count is None \
    #       or force_refresh \
    #       or str( self.prev_query_data ) != str( qd ):
    #         if print_query is None:
    #             print_query = self.print_query
    #         if alias is None:
    #             alias = self.get_alias()
    #         query = 'select count( * ) %s' % (self.get_query_from())
    #         group = self.get_query_group_by()
    #         args = { }
    #         if qd:
    #             if qd.where:
    #                 q = replace_alias( qd.where, alias )
    #                 query += ' where (' + q + ')'
    #                 # term.printDebug( 'query: %s' % ( query ) )
    #             if qd.args:
    #                 args = qd.args
    #             if group:
    #                 query += ' group by ' + group
    #         if print_query:
    #             term.printLog( 'query: %s\nargs: %s' % (query, repr( args )) )
    #         query = 'select count( * ) from ( %s ) as temp' % query
    #         term.printDebug( 'query: %s' % query )
    #         res = self.db.executesql( query, placeholders=args )
    #         if group:
    #             self.row_count = len( res )
    #         else:
    #             self.row_count = res[ 0 ][ 0 ]
    #     #             term.printLog( 'sql: ' + db._lastsql )
    #
    #     return self.row_count
    #

    sql_query = '''
        select
            path_info,
            extract( year from ts ) as year,
            extract( month from ts ) as month,
            extract( day from ts ) as day,
            count( distinct client_ip) as total
        from page_log
        group by path_info, year, month, day
    '''

    def get_record_count( self, qd=None, alias=None, print_query=None, force_refresh=False ):
        db = self.db
        sql = 'select count( * ) from (%s) as temp' % self.sql_query
        self.row_count = db.executesql( sql )[0][0]
        return self.row_count


    def get_record_list( self, qd=None, alias=None, print_query=None, force_refresh=False ):
        super( PageStatsTotalsView, self ).get_record_list( qd, alias, print_query, force_refresh )
        for r in self.list_rows:
            page = page_factory.get_page( url=r.path_info )
            r.page_name = page.name
        return self.list_rows

