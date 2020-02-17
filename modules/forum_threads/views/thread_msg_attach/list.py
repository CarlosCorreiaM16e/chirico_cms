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


KQV_ATTACH_ID = 'KQV_PREFIX + attach_id' 
KQV_REQUEST_MSG_ID = 'KQV_PREFIX + request_msg_id' 

#----------------------------------------------------------------------
class RequestMsgAttachListView( BaseListPlasticView ):
    controller_name = 'request_msg_attachs'
    function_name = 'list'

    #----------------------------------------------------------------------
    def __init__( self, db ):
        super( RequestMsgAttachListView, self ).__init__( db )

        T = current.T
        self.table_model = db_tables.get_table_model( 'request_msg_attach', db=db )

        self.list_title = T( 'RequestMsgAttach list' )

        self.append_var( KQV_ATTACH_ID, fld_type=KDT_INT )
        self.append_var( KQV_REQUEST_MSG_ID, fld_type=KDT_INT )
#        term.printDebug( 'query_vars: %s' % repr( self.query_vars ) )



#----------------------------------------------------------------------
    def get_table_view_dict( self ):
        T = current.T
        tdef = { KTF_COL_ORDER: [ 'id', 'attach_id', 'request_msg_id' ],
                 KTF_SORTABLE_COLS: [ 'id', 'attach_id', 'request_msg_id' ],
                 KTF_CELL_CLASS: 'table_border',
                 KTF_COLS: { 'id': { KTF_TITLE: T( 'Id' ),
                                     KTF_TYPE: KDT_INT,
                                     KTF_CELL_CLASS: 'table_border',
                                     KTF_CELL_LINK: { KTF_LINK_C: self.controller_name,
                                                      KTF_LINK_F: 'edit',
                                                      KTF_ARGS_F: [ 'id' ]
                                                      }
                                     },

                             'attach_id': { KTF_TITLE: T( 'Attach id' ),
                                            KTF_TYPE: KDT_INT,
                                            KTF_CELL_CLASS: 'table_border',
                                            },

                             'request_msg_id': { KTF_TITLE: T( 'Request msg id' ),
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
        attach_model = db_tables.get_table_model( 'attach', db=db )
        request_msg_model = db_tables.get_table_model( 'request_msg', db=db )
        attach_list = attach_model.select( orderby='id' )
        attach_options = [ (r.id, r.name) for r in attach_list ]
        attach_options.insert( 0, ('', '') )
        request_msg_list = request_msg_model.select( orderby='id' )
        request_msg_options = [ (r.id, r.name) for r in request_msg_list ]
        request_msg_options.insert( 0, ('', '') )
        qdata = { KTF_BUTTONS: [],
                  KTF_COL_ORDER: [ KQV_ATTACH_ID, KQV_REQUEST_MSG_ID, KQV_SHOW_ALL ],
                  KTF_COLS: { KQV_SHOW_ALL: { KTF_TITLE: T( 'Show all' ), KTF_TYPE: KDT_BOOLEAN, },
                              KQV_ATTACH_ID: {
                                  KTF_TITLE: T( 'Attach id' ),
                                  KTF_TYPE: KDT_SELECT_INT,
                                  KTF_OPTIONS: attach_options },
                              KQV_REQUEST_MSG_ID: {
                                  KTF_TITLE: T( 'Request msg id' ),
                                  KTF_TYPE: KDT_SELECT_INT,
                                  KTF_OPTIONS: request_msg_options },
                             },
                 }
        self.qdata = qdata
        return self.qdata
    
#----------------------------------------------------------------------
    def get_query_data( self, orderby=None ):
        qd = super( RequestMsgAttachListView, self ).get_query_data( orderby )
        qv_attach_id =  self.query_vars.get( KQV_ATTACH_ID )
        if qv_attach_id:
            qd.addAnd( QueryData( 'attach_id = %(qv_attach_id)s',
                                  { 'qv_attach_id': qv_attach_id } ) )
        qv_request_msg_id =  self.query_vars.get( KQV_REQUEST_MSG_ID )
        if qv_request_msg_id:
            qd.addAnd( QueryData( 'request_msg_id = %(qv_request_msg_id)s',
                                  { 'qv_request_msg_id': qv_request_msg_id } ) )
        term.printDebug( repr( qd ) )
        return qd

    #----------------------------------------------------------------------

