# -*- coding: utf-8 -*-

from m16e.db import db_tables
from gluon import current
from m16e import term
from m16e.db.querydata import QueryData
from m16e.kommon import KQV_SHOW_ALL, KQV_PREFIX, KDT_CHAR, KDT_BLOB_IMG, \
    KDT_BOOLEAN, KDT_INT, KDT_DATE, KDT_DEC, KDT_FILE, KDT_TIME, KDT_TIMESTAMP, \
    KDT_SELECT_INT, KDT_SELECT_CHAR
from m16e.ktfact import KTF_COL_ORDER, KTF_SORTABLE_COLS, KTF_CELL_CLASS, \
    KTF_COLS, KTF_TITLE, KTF_TYPE, \
    KTF_CELL_LINK, KTF_LINK_C, KTF_LINK_F, KTF_ARGS, KTF_ARGS_F, \
    KTF_BUTTONS, KTF_NAME, KTF_VALUE, KTF_OPTIONS
from m16e.views.plastic_view import BaseListPlasticView


KQV_AUTH_USER_ID = 'KQV_PREFIX + auth_user_id' 
KQV_REQUEST_ID = 'KQV_PREFIX + request_id' 

#----------------------------------------------------------------------
class RequestVoteListView( BaseListPlasticView ):
    controller_name = 'request_votes'
    function_name = 'list'

    #----------------------------------------------------------------------
    def __init__( self, db ):
        super( RequestVoteListView, self ).__init__( db )

        T = current.T
        self.table_model = db_tables.get_table_model( 'request_vote', db=db )

        self.list_title = T( 'RequestVote list' )

        self.append_var( KQV_AUTH_USER_ID, fld_type=KDT_INT )
        self.append_var( KQV_REQUEST_ID, fld_type=KDT_INT )
#        term.printDebug( 'query_vars: %s' % repr( self.query_vars ) )



#----------------------------------------------------------------------
    def get_table_view_dict( self ):
        T = current.T
        tdef = { KTF_COL_ORDER: [ 'id', 'request_id', 'auth_user_id' ],
                 KTF_SORTABLE_COLS: [ 'id', 'request_id', 'auth_user_id' ],
                 KTF_CELL_CLASS: 'table_border',
                 KTF_COLS: { 'id': { KTF_TITLE: T( 'Id' ),
                                     KTF_TYPE: KDT_INT,
                                     KTF_CELL_CLASS: 'table_border',
                                     KTF_CELL_LINK: { KTF_LINK_C: self.controller_name,
                                                      KTF_LINK_F: 'edit',
                                                      KTF_ARGS_F: [ 'id' ]
                                                      }
                                     },

                             'request_id': { KTF_TITLE: T( 'Request id' ),
                                             KTF_TYPE: KDT_INT,
                                             KTF_CELL_CLASS: 'table_border',
                                             },

                             'auth_user_id': { KTF_TITLE: T( 'Auth user id' ),
                                               KTF_TYPE: KDT_INT,
                                               KTF_CELL_CLASS: 'table_border',
                                               },
                             },
               }
        self.tdef = tdef
        return self.tdef


#----------------------------------------------------------------------
    def get_table_qdata_dict( self, extra_buttons={} ):
        T = current.T
        db = self.db
        auth_user_model = db_tables.get_table_model( 'auth_user', db=db )
        request_model = db_tables.get_table_model( 'request', db=db )
        auth_user_list = auth_user_model.select( orderby='id' )
        auth_user_options = [ (r.id, r.name) for r in auth_user_list ]
        auth_user_options.insert( 0, ('', '') )
        request_list = request_model.select( orderby='id' )
        request_options = [ (r.id, r.name) for r in request_list ]
        request_options.insert( 0, ('', '') )
        qdata = { KTF_BUTTONS: [],
                  KTF_COL_ORDER: [ KQV_AUTH_USER_ID, KQV_REQUEST_ID, KQV_SHOW_ALL ],
                  KTF_COLS: { KQV_SHOW_ALL: { KTF_TITLE: T( 'Show all' ), KTF_TYPE: KDT_BOOLEAN, },
                              KQV_AUTH_USER_ID: {
                                  KTF_TITLE: T( 'Auth user id' ),
                                  KTF_TYPE: KDT_SELECT_INT,
                                  KTF_OPTIONS: auth_user_options },
                              KQV_REQUEST_ID: {
                                  KTF_TITLE: T( 'Request id' ),
                                  KTF_TYPE: KDT_SELECT_INT,
                                  KTF_OPTIONS: request_options },
                             },
                 }
        self.qdata = qdata
        return self.qdata
    
#----------------------------------------------------------------------
    def get_query_data( self, orderby=None ):
        qd = super( RequestVoteListView, self ).get_query_data( orderby )
        qv_auth_user_id =  self.query_vars.get( KQV_AUTH_USER_ID )
        if qv_auth_user_id:
            qd.addAnd( QueryData( 'auth_user_id = %(qv_auth_user_id)s',
                                  { 'qv_auth_user_id': qv_auth_user_id } ) )
        qv_request_id =  self.query_vars.get( KQV_REQUEST_ID )
        if qv_request_id:
            qd.addAnd( QueryData( 'request_id = %(qv_request_id)s',
                                  { 'qv_request_id': qv_request_id } ) )
        term.printDebug( repr( qd ) )
        return qd

    #----------------------------------------------------------------------

