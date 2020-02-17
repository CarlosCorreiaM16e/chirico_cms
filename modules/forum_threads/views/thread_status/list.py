# -*- coding: utf-8 -*-

from m16e.db import db_tables
from gluon import current
from m16e import term
from m16e.kommon import KQV_SHOW_ALL, KQV_PREFIX, KDT_CHAR, KDT_BLOB_IMG, \
    KDT_BOOLEAN, KDT_INT, KDT_DATE, KDT_DEC, KDT_FILE, KDT_TIME, KDT_TIMESTAMP, \
    KDT_SELECT_INT, KDT_SELECT_CHAR
from m16e.ktfact import KTF_COL_ORDER, KTF_SORTABLE_COLS, KTF_CELL_CLASS, \
    KTF_COLS, KTF_TITLE, KTF_TYPE, \
    KTF_CELL_LINK, KTF_LINK_C, KTF_LINK_F, KTF_ARGS, KTF_ARGS_F, \
    KTF_BUTTONS, KTF_NAME, KTF_VALUE, KTF_OPTIONS
from m16e.views.plastic_view import BaseListPlasticView


class ThreadStatusListView( BaseListPlasticView ):
    controller_name = 'thread_status'
    function_name = 'list'


    def __init__( self, db ):
        super( ThreadStatusListView, self ).__init__( db )

        T = current.T
        self.table_model = db_tables.get_table_model( 'thread_status', db=db )

        self.list_title = T( 'Thread status list' )

#        term.printDebug( 'query_vars: %s' % repr( self.query_vars ) )


    def get_table_view_dict( self ):
        T = current.T
        tdef = { KTF_COL_ORDER: [ 'id', 'thread_status_name', 'meta_name', 'is_closed', 'preferred_order' ],
                 KTF_SORTABLE_COLS: [ 'id', 'thread_status_name', 'meta_name', 'is_closed', 'preferred_order' ],
                 KTF_CELL_CLASS: 'table_border',
                 KTF_COLS: { 'id': { KTF_TITLE: T( 'Id' ),
                                     KTF_TYPE: KDT_INT,
                                     KTF_CELL_CLASS: 'table_border',
                                     KTF_CELL_LINK: { KTF_LINK_C: self.controller_name,
                                                      KTF_LINK_F: 'edit',
                                                      KTF_ARGS_F: [ 'id' ]
                                                      }
                                     },

                             'thread_status_name': { KTF_TITLE: T( 'thread status name' ),
                                                      KTF_TYPE: KDT_CHAR,
                                                      KTF_CELL_CLASS: 'table_border',
                                                      },

                             'meta_name': { KTF_TITLE: T( 'Meta name' ),
                                       KTF_TYPE: KDT_CHAR,
                                       KTF_CELL_CLASS: 'table_border',
                                       },

                             'is_closed': { KTF_TITLE: T( 'Is closed' ),
                                            KTF_TYPE: KDT_BOOLEAN,
                                            KTF_CELL_CLASS: 'table_border',
                                            },

                             'preferred_order': { KTF_TITLE: T( 'Preferred order' ),
                                                  KTF_TYPE: KDT_INT,
                                                  KTF_CELL_CLASS: 'table_border',
                                                  },
                             },
               }
        self.tdef = tdef
        return self.tdef


    def get_table_qdata_dict( self, extra_buttons={} ):
        T = current.T
        qdata = { KTF_BUTTONS: [],
                  KTF_COL_ORDER: [ KQV_SHOW_ALL ],
                  KTF_COLS: { KQV_SHOW_ALL: { KTF_TITLE: T( 'Show all' ), KTF_TYPE: KDT_BOOLEAN, },
                             },
                 }
        self.qdata = qdata
        return self.qdata
    

