# -*- coding: utf-8 -*-
# this file is released under public domain and you can use without limitations

from gluon import current
from gluon.html import URL, DIV, H3, FORM, TABLE, TR, TD, A, IMG, TH
from gluon.storage import Storage
from m16e import term
from m16e.db import db_tables
from m16e.kommon import ACT_CLEAR, KDT_INT, KDT_CHAR, storagize
from m16e.ktfact import KTF_COL_ORDER, KTF_SORTABLE_COLS, KTF_CELL_CLASS, KTF_COLS, KTF_TITLE, KTF_TYPE, KTF_CELL_LINK, \
    KTF_LINK_C, KTF_LINK_F, KTF_ARGS_F, KTF_BUTTONS
from m16e.views.plastic_view import BaseListPlasticView


class UnitTypeIndexView( BaseListPlasticView ):
    controller_name = 'unit_type'
    function_name = 'index'


    def __init__( self, db ):
        super( UnitTypeIndexView, self ).__init__( db )
        self.table_model = db_tables.get_table_model( 'unit_type', db=db )


    def get_inhibit_actions( self ):
        return [ ACT_CLEAR ]


    def get_table_view_dict( self ):
        T = current.T
        tdef = { KTF_COL_ORDER: [ 'id', 'name', 'path' ],
                 KTF_SORTABLE_COLS: [ 'id', 'name', 'path' ],
                 KTF_CELL_CLASS: 'table_border',
                 KTF_COLS: { 'id': { KTF_TITLE: T( 'Unit type Id' ),
                                     KTF_TYPE: KDT_INT,
                                     KTF_CELL_LINK: { KTF_LINK_C: self.controller_name,
                                                      KTF_LINK_F: 'edit',
                                                      KTF_ARGS_F: [ 'id' ],
                                                      KTF_TITLE: T( 'Edit attach type' ) },
                                  },
                             'name': { KTF_TITLE: T( 'Name' ),
                                       KTF_TYPE: KDT_CHAR },
                             'path': { KTF_TITLE: T( 'Path' ),
                                       KTF_TYPE: KDT_CHAR },
                             },
                 }
        self.tdef = storagize( tdef )
        # term.printDebug( 'tdef: %s' % repr( self.tdef ) )
        return self.tdef


    def get_table_qdata_dict( self, extra_buttons={} ):
        T = current.T
        db = self.db
        qdata = { KTF_BUTTONS: [],
                  KTF_COL_ORDER: [],
                  KTF_COLS: {},
                 }
        # term.printDebug( 'qdata: %s' % repr( qdata ) )
        self.qdata = storagize( qdata )
        return self.qdata



#     #------------------------------------------------------------------
#     def process( self ):
#         #------------------------------------------------------------------
#         def getQueryData():
#             #------------------------------------------------------------------
#             def get_user_query_data():
#                 return QueryData()
#             #------------------------------------------------------------------
#             def get_dyn_query_data():
# #                term.printLog( 'session.svars: ' + repr( session.svars ) )
#                 qd = QueryData()
#                 term.printLog( repr( qd ) )
#                 return qd
#             #------------------------------------------------------------------
#             qd = get_user_query_data()
#             qd.addAnd( get_dyn_query_data() )
#             term.printDebug( repr( qd ) )
#             return qd
#
#         #------------------------------------------------------------------
#         def getRecordList( qd ):
#             query = '''
#                 select
#                     id,
#                     name,
#                     path,
#                     parent_unit_type_id
#                 from unit_type
#             '''
#             args = {}
#             if qd:
#                 if qd.where:
#                     query += ' where ' + qd.where
#                 if qd.order:
#                     order = qd.order
#                     query += ' order by ' + order
#                 if qd.limit:
#                     query += ' limit %d ' % (qd.limit)
#                 if qd.offset:
#                     query += ' offset %d ' % (qd.offset)
#                 if qd.args:
#                     args = qd.args
#             term.printLog( 'query: %s\nargs: %s' % ( query, repr( args ) ) )
#             res = db.executesql( query, placeholders = args, as_dict = True )
# #            term.printLog( 'sql: ' + db._lastsql )
#             rows = []
#             for r in res:
#                 rows.append( Storage( r ) )
#             return rows
#
#         #------------------------------------------------------------------
#         def getRecordListCount( qd ):
#             query = '''
#                 select count( * )
#                 from unit_type
#             '''
#             args = {}
#             if qd:
#                 if qd.where:
#                     query += ' where ' + qd.where
#                 if qd.args:
#                     args = qd.args
#             term.printLog( 'query: %s\nargs: %s' % ( query, repr( args ) ) )
#             recCount = db.executesql( query, placeholders = args )
#             term.printDebug( 'sql: %s' % str( db._lastsql ) )
#             return recCount[0][0]
#
#         #------------------------------------------------------------------
#         request = current.request
#         response = current.response
#         term.printLog( 'request.args: %s\n' % ( repr( request.args ) ) )
#         term.printLog( 'request.vars: %s\n' % ( repr( request.vars ) ) )
#
#         session = current.session
#         T = current.T
#         db = self.db
#         auth = session.auth
#         redirect = None
#
#         next_c = request.vars.next_c or ''
#         next_f = request.vars.next_f or ''
#         next_args = request.vars.next_args or []
#
#         action = request.post_vars.action
#         term.printLog( 'action: ' + repr( action ) )
#
#         if action == ACT_NEW_UNIT_TYPE:
#             redirect = URL( c='unit_type', f='edit', args=[ 0 ] )
#
#         qd = getQueryData()
#
#         recCount = getRecordListCount( qd )
#         term.printDebug( 'count: %d' % ( recCount ) )
#         data_rows = getRecordList( qd )
#         main_panel = DIV()
#         main_panel.append( H3( T( 'Unit type list' ) ) )
#         table = TABLE()
#         tr = TR()
#         tr.append( TH( T( 'Id' ) ) )
#         tr.append( TH( T( 'Path' ) ) )
#         tr.append( TH( T( 'Name' ) ) )
#         if next_c:
#             tr.append( TH( T( 'Action' ) ) )
#         table.append( tr )
#         for r in data_rows:
#             tr = TR()
#             d_vars = {}
#             if next_c:
#                 d_vars = { 'next_c': next_c,
#                            'next:f': next_f,
#                            'next_args': next_args }
#             url = URL( c='unit_type', f='edit', args=[ r.id ], vars=d_vars )
#             tr.append( TD( A( str( r.id ), _href=url ) ) )
#             tr.append( TD( r.path ) )
#             tr.append( TD( r.name ) )
#             if next_c:
#                 d_vars[ KQR_SELECTED_ID ] = r.id
#                 url = URL( c=next_c, f=next_f, args=next_args, vars=d_vars )
#                 tr.append( TD( A( T( 'Select' ), _href=url, _class='btn' ) ) )
#             table.append( tr )
#         form = FORM()
#         form.append( table )
#         main_panel.append( form )
#
#         return Storage( dict=dict( main_panel=main_panel ),
#                         redirect=redirect )
#
#     #------------------------------------------------------------------
