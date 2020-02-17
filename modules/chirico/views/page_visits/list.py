# -*- coding: utf-8 -*-

from m16e.db import db_tables
from gluon import current
from m16e.kommon import KDT_INT, KDT_CHAR, KQV_SHOW_ALL, KDT_BOOLEAN, \
    KDT_TIMESTAMP, ACT_SUBMIT, ACT_NEW_RECORD
from m16e.ktfact import KTF_COL_ORDER, KTF_SORTABLE_COLS, KTF_CELL_CLASS, KTF_COLS, KTF_TITLE, KTF_TYPE, KTF_BUTTONS, KTF_NAME, KTF_VALUE
from m16e.views.plastic_view import BaseListPlasticView


#----------------------------------------------------------------------
class PageVisitsListView( BaseListPlasticView ):
    controller_name = 'page_visits'

    #----------------------------------------------------------------------
    def __init__( self, db ):
        super( PageVisitsListView, self ).__init__( db )

        T = current.T
        self.table_model = db_tables.get_table_model( 'page_visit', db=db )

        self.list_title = T( 'PageVisits list' )
#        term.printDebug( 'query_vars: %s' % repr( self.query_vars ) )

#----------------------------------------------------------------------
    def get_table_view_dict( self ):
        T = current.T
        tdef = {
            KTF_COL_ORDER: [ 'id', 'site_visit_id', 'page_visit_ts', 'path_info', 'query_string' ],
            KTF_SORTABLE_COLS: [ 'id', 'site_visit_id', 'page_visit_ts', 'path_info', 'query_string' ],
            KTF_CELL_CLASS: 'table_border',
            KTF_COLS: {
                 'id': {
                    KTF_TITLE: T( 'Id' ),
                    KTF_TYPE: KDT_INT,
                    KTF_CELL_CLASS: 'table_border',
                 },
                 'site_visit_id': {
                    KTF_TITLE: T( 'Site_visit_id' ),
                    KTF_TYPE: KDT_INT,
                    KTF_CELL_CLASS: 'table_border',
                 },
                 'page_visit_ts': {
                    KTF_TITLE: T( 'Page_visit_ts' ),
                    KTF_TYPE: KDT_TIMESTAMP,
                    KTF_CELL_CLASS: 'table_border',
                 },
                 'path_info': {
                    KTF_TITLE: T( 'Path_info' ),
                    KTF_TYPE: KDT_CHAR,
                    KTF_CELL_CLASS: 'table_border',
                 },
                 'query_string': {
                    KTF_TITLE: T( 'Query_string' ),
                    KTF_TYPE: KDT_CHAR,
                    KTF_CELL_CLASS: 'table_border',
                 },
            }
        }
        return tdef


#----------------------------------------------------------------------
    def get_table_qdata_dict( self, extra_buttons={} ):
        T = current.T
        qdata = {
            KTF_BUTTONS: [
                { KTF_NAME: 'action', KTF_TITLE: T( 'Submit' ), KTF_VALUE: ACT_SUBMIT },
                { KTF_NAME: 'action', KTF_TITLE: T( 'New record.' ), KTF_VALUE: ACT_NEW_RECORD },
                ],
            KTF_COL_ORDER: [ KQV_SHOW_ALL ],
            KTF_COLS: {
                KQV_SHOW_ALL: { KTF_TITLE: T( 'Show all' ), KTF_TYPE: KDT_BOOLEAN, },
            },
        }
        return qdata

    #----------------------------------------------------------------------

