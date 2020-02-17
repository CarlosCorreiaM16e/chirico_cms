# -*- coding: utf-8 -*-

from m16e.db import db_tables
from gluon import current
from m16e.kommon import KDT_INT, KDT_CHAR, KQV_SHOW_ALL, KDT_BOOLEAN, KDT_TIMESTAMP, \
    ACT_SUBMIT, ACT_NEW_RECORD, storagize
from m16e.ktfact import KTF_COL_ORDER, KTF_SORTABLE_COLS, KTF_CELL_CLASS, KTF_COLS, KTF_TITLE, KTF_TYPE, KTF_BUTTONS, \
    KTF_NAME, KTF_VALUE, KTF_CELL_LINK, KTF_LINK_C, KTF_LINK_F, KTF_ARGS, KTF_USE_ICON
from m16e.views.plastic_view import BaseListPlasticView


class MailQueueListView( BaseListPlasticView ):
    controller_name = 'mail_queue'

    def __init__( self, db ):
        super( MailQueueListView, self ).__init__( db, order_value=-1 )

        T = current.T
        self.table_model = db_tables.get_table_model( 'mail_queue', db=db )

        self.list_title = T( 'Mail queue list' )
#        term.printDebug( 'query_vars: %s' % repr( self.query_vars ) )


    def get_table_view_dict( self ):
        T = current.T
        if not self.tdef:
            tdef = { KTF_COL_ORDER: [ 'id', 'subject', 'when_to_send', 'sent', 'status', 'task_id', 'auth_user_id', 'percent_done', 'progress_message' ],
                     KTF_SORTABLE_COLS: [ 'id', 'subject', 'when_to_send', 'sent', 'status', 'task_id', 'auth_user_id', 'percent_done', 'progress_message' ],
                     KTF_CELL_CLASS: 'table_border',
                     KTF_COLS: { 'id': { KTF_TITLE: T( 'Id' ),
                                         KTF_TYPE: KDT_INT,
                                         KTF_CELL_LINK: { KTF_LINK_C: self.controller_name,
                                                          KTF_LINK_F: 'edit',
                                                          KTF_ARGS: [ 'id' ],
                                                          KTF_USE_ICON: True },
                                         KTF_CELL_CLASS: 'table_border',
                                         },
                                 'subject': { KTF_TITLE: T( 'Subject' ),
                                              KTF_TYPE: KDT_CHAR,
                                              KTF_CELL_CLASS: 'table_border',
                                              },
                                 'text_body': { KTF_TITLE: T( 'Text_body' ),
                                                KTF_TYPE: KDT_CHAR,
                                                KTF_CELL_CLASS: 'table_border',
                                                },
                                 'html_body': { KTF_TITLE: T( 'Html_body' ),
                                                KTF_TYPE: KDT_CHAR,
                                                KTF_CELL_CLASS: 'table_border',
                                                },
                                 'when_to_send': { KTF_TITLE: T( 'When_to_send' ),
                                                   KTF_TYPE: KDT_TIMESTAMP,
                                                   KTF_CELL_CLASS: 'table_border',
                                                   },
                                 'sent': { KTF_TITLE: T( 'Sent' ),
                                           KTF_TYPE: KDT_TIMESTAMP,
                                           KTF_CELL_CLASS: 'table_border',
                                           },
                                 'status': { KTF_TITLE: T( 'Status' ),
                                             KTF_TYPE: KDT_CHAR,
                                             KTF_CELL_CLASS: 'table_border',
                                             },
                                 'mail_cc': { KTF_TITLE: T( 'Mail_cc' ),
                                              KTF_TYPE: KDT_CHAR,
                                              KTF_CELL_CLASS: 'table_border',
                                              },
                                 'mail_bcc': { KTF_TITLE: T( 'Mail_bcc' ),
                                               KTF_TYPE: KDT_CHAR,
                                               KTF_CELL_CLASS: 'table_border',
                                               },
                                 'task_id': { KTF_TITLE: T( 'Task_id' ),
                                              KTF_TYPE: KDT_INT,
                                              KTF_CELL_CLASS: 'table_border',
                                              },
                                 'auth_user_id': { KTF_TITLE: T( 'Auth_user_id' ),
                                                   KTF_TYPE: KDT_INT,
                                                   KTF_CELL_CLASS: 'table_border',
                                                   },
                                 'percent_done': { KTF_TITLE: T( 'Percent_done' ),
                                                   KTF_TYPE: KDT_INT,
                                                   KTF_CELL_CLASS: 'table_border',
                                                   },
                                 'progress_message': { KTF_TITLE: T( 'Progress_message' ),
                                                       KTF_TYPE: KDT_CHAR,
                                                       KTF_CELL_CLASS: 'table_border',
                                                       },
                                 }
                     }
            self.tdef = storagize( tdef )
        return self.tdef


    def get_table_qdata_dict( self, extra_buttons={} ):
        T = current.T
        qdata = {
            KTF_BUTTONS: [],
            KTF_COL_ORDER: [  ],
            KTF_COLS: {
            },
        }
        self.qdata = storagize( qdata )
        return self.qdata


