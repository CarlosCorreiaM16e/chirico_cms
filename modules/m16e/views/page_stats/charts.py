# -*- coding: utf-8 -*-
# this file is released under public domain and you can use without limitations
from chirico.db import page_factory, page_stats
from gluon.storage import Storage
from m16e import term
from m16e.db import db_tables
from gluon import current, DIV, A, URL
from m16e.kommon import ACT_NEW_RECORD, KQV_PREFIX, KDT_INT, KDT_CHAR, KDT_TIMESTAMP, KDT_RAW, to_utf8, DT
from m16e.ui import elements
from m16e.views.plastic_view import BaseListPlasticView

CT_SHOW_DAILY = 'show_daily'
CT_SHOW_MONTHLY = 'show_monthly'
CT_SHOW_TOTALS = 'show_totals'
CT_SHOW_YEARLY = 'show_yearly'

QV_DATE = 'date'
# QV_TYPE = 'type' -> args( 0 )
QV_URL = 'url'

MAX_TOP = 10
MAX_DAYS = 15

class PageStatsChartsView( BaseListPlasticView ):
    controller_name = 'page_stats'
    function_name = 'charts'


    def __init__( self, db ):
        super( PageStatsChartsView, self ).__init__( db )
        self.table_model = db_tables.get_table_model( 'page_log', db=db )
        T = current.T
        self.list_title = T( 'Page charts' )
        self.print_query = True
        self.chart_type = CT_SHOW_TOTALS
        self.chart_date = DT.now()
        self.url = None
        # self.nav_prev = None
        # self.nav_next = None
        self.pv_list = None


    def get_inhibit_actions( self ):
        return [ ACT_NEW_RECORD ]


    def get_plastic_table( self, reload=False ):
        pass


    def get_table_div_element( self ):
        return DIV()


    def parse_request_vars( self, post_vars=None, get_vars=None ):
        super( PageStatsChartsView, self ).parse_request_vars( post_vars, get_vars )
        request = current.request
        db = self.db
        self.chart_type = request.args( 0 ) or CT_SHOW_TOTALS
        self.chart_date = request.vars.get( QV_DATE, DT.now() )
        self.url = request.vars.get( QV_URL )
        if self.chart_type == CT_SHOW_DAILY:
            self.pv_list = page_stats.get_page_views_daily( self.url,
                                                            self.chart_date,
                                                            limit=MAX_DAYS, db=db )
        else:
            self.pv_list = page_stats.get_page_views( limit=MAX_TOP, db=db )


    def get_prev_url( self ):
        db = self.db
        q_sql = (db.page_log.path_info == self.url)
        pv = self.pv_list[0]
        q_sql &= (db.page_log.ts < pv.min_ts)
        pl = self.table_model.select( q_sql, orderby='id desc' ).first()
        if pl:
            url = URL( c=self.controller_name,
                       f=self.function_name,
                       args=self.chart_type,
                       vars={ QV_URL: self.url,
                              QV_DATE: pl.ts } )
            return url
        return ''


    def get_next_url( self ):
        db = self.db
        q_sql = (db.page_log.path_info == self.url)
        q_sql &= (db.page_log.ts > self.pv_list[-1].max_ts)
        pl = self.table_model.select( q_sql, orderby='id' ).first()
        if pl:
            url = URL( c=self.controller_name,
                       f=self.function_name,
                       args=self.chart_type,
                       vars={ QV_URL: self.url,
                              QV_DATE: pl.ts } )
            return url
        return ''


    def post_process( self, div_content ):
        super( PageStatsChartsView, self ).post_process( div_content )
        db = self.db
        data = Storage( chart_type=self.chart_type )
        if self.chart_type == CT_SHOW_DAILY:
            prev_url = self.get_prev_url()
            if prev_url:
                data.nav_prev = A( elements.get_bootstrap_icon( elements.ICON_NAV_PREV, dark_background=False ),
                                   _href=prev_url, )
            next_url = self.get_next_url()
            if next_url:
                data.nav_next = A( elements.get_bootstrap_icon( elements.ICON_NAV_NEXT, dark_background=False ),
                                   _href=next_url )

        return self.set_result( data )


    def get_chart_show_daily( self ):
        request = current.request
        T = current.T
        db = self.db
        js = '''
            window.barChart = new Chart( document.getElementById( 'chart_canvas' ), {
                type: 'bar',
                data: {
                  labels: %(day_list)s,
                  datasets: [ { label: '%(label)s',
                                data: %(count_list)s } ]
                },
                options: {
                  title: {
                    display: true,
                    text: '%(title)s'
                  }
                }
            });
            jQuery( "#chart_canvas" ).click(
                function( evt ) {
                    console.log( evt );
                    var point = window.barChart.getElementAtEvent( evt )[0];
                    var point_label = encodeURIComponent( point._model.label );
                    console.log( point );
                    if( point ) {
                        var page = '/%(app)s/page_stats/index?qv_path_info=%(url)s&' +
                            'qv_start_ts=' + point_label + 
                            '&qv_stop_ts=' + point_label + ' 23:59:59';
                        console.log( page );
                        window.location.href = page;
                    }
                }
            );
        ''' % dict( label=T( 'Daily page views for page: %(page)s', dict( page=self.url ) ),
                    day_list=[ '%d-%02d-%02d' % (pv.year, pv.month, pv.day) for pv in self.pv_list ],
                    count_list=[ int( pv.total ) for pv in self.pv_list ],
                    title=T( 'Daily page views (since %(date)s)',
                             dict( date=self.pv_list[0].min_ts.strftime( '%Y-%m-%d' ) ) ),
                    app=current.app_name,
                    url=self.url )
        return js


    def get_chart_show_totals( self ):
        T = current.T
        db = self.db
        self.pv_list = page_stats.get_page_views( limit=MAX_TOP, db=db )
        js = '''
            window.barChart = new Chart( document.getElementById( 'chart_canvas' ), {
                type: 'horizontalBar',
                data: {
                  labels: %(page_list)s,
                  datasets: [ { label: '%(label)s',
                                data: %(count_list)s } ]
                },
                options: {
                  title: {
                    display: true,
                    text: '%(title)s'
                  }
                }
            });
            jQuery( "#chart_canvas" ).click(
                function( evt ) {
                    console.log( evt );
                    var point = window.barChart.getElementAtEvent( evt )[0];
                    console.log( point );
                    if( point ) {
                        var page = '/%(app)s/page_stats/charts/show_daily?url=' + 
                            encodeURIComponent( point._model.label );
                        console.log( page );
                        window.location.href = page;
                    }
                }
            );
            
        ''' % dict( label=T( 'Page views' ),
                    page_list=[ pv.path_info for pv in self.pv_list ],
                    count_list=[ int( pv.total ) for pv in self.pv_list ],
                    title=T( 'Total page views (since 2020-01-27)' ),
                    app=current.app_name )
        return js


    def get_chart_js( self ):
        js = ''
        if self.chart_type == CT_SHOW_TOTALS:
            js = self.get_chart_show_totals()
        elif self.chart_type == CT_SHOW_DAILY:
            js = self.get_chart_show_daily()
        return js


    def get_page_js( self ):
        js = super( PageStatsChartsView, self ).get_page_js()
        js += self.get_chart_js()
        return js


    def do_process( self ):
        request = current.request
        session = current.session

        term.printLog( 'request.args: ' + repr( request.args ) )
        term.printLog( 'request.vars.keys: ' + repr( request.vars.keys() ) )

        self.parse_request_args()
        # term.printDebug( 'request.vars: %s' % repr( request.vars ) )
        if self.result.redirect:
            return self.result
#         action = request.post_vars.action
#         term.printDebug( 'query_vars: %s' % repr( self.query_vars ),
#                          prompt_continue=True )

        self.parse_request_vars( request.post_vars, request.get_vars )
        # term.printLog( 'self.action: ' + repr( self.action ) )
        term.printDebug( 'query_vars: %s' % repr( self.query_vars ) )

        if self.result.redirect:
            return self.result

        self.process_pre_validation_actions()
        if self.result.redirect:
            return self.result

        self.get_plastic_table()

        div = self.get_table_div_element()
        if self.invoke_process_form:
            self.process_form()
        if self.result.redirect:
            return self.result

        self.post_process( div )
        # term.printDebug( 'result: %s' % ( repr( self.result ) ) )
        return self.result

