# -*- coding: utf-8 -*-
# this file is released under public domain and you can use without limitations

from m16e.db import db_tables
from gluon import current
from gluon.html import URL
from gluon.storage import Storage
from m16e import term
from m16e.db import attach_factory
from m16e.db.querydata import QueryData
from m16e.kommon import KQV_PREFIX, KDT_BOOLEAN, KDT_INT, KQV_SHOW_ALL, \
    KDT_SELECT_INT, KDT_CHAR, KDT_BLOB_IMG, KDT_BLOB_MEDIA
from m16e.ktfact import KTF_COL_ORDER, KTF_SORTABLE_COLS, KTF_CELL_CLASS, \
    KTF_COLS, KTF_TITLE, KTF_TYPE, KTF_CELL_LINK, KTF_LINK_C, KTF_LINK_F, KTF_ARGS, \
    KTF_BUTTONS, KTF_NAME, KTF_VALUE, KTF_OPTIONS, KTF_WIDTH
from m16e.views.plastic_view import BaseListPlasticView

ACT_NEW_ATTACH = 'act_new_attach'
ACT_DUMP_TO_STATIC = 'act_dump_to_static'


class MediaListView( BaseListPlasticView ):
    controller_name = 'media'
    function_name = 'list'


    def __init__( self, db ):
        super( MediaListView, self ).__init__( db )
        self.table_model = db_tables.get_table_model( 'attach', db=db )
        self.mt_list = attach_factory.get_media_mime_type_list( db=db )


    def get_query_data( self, orderby=None ):
        db = self.db
        term.printLog( 'self.query_vars: ' + repr( self.query_vars ) )
        qd = super( MediaListView, self ).get_query_data( orderby )
        sql = 'mime_type_id in ( %s )' % ', '.join( [ str( mt.id )
                                                      for mt in self.mt_list ] )
        term.printDebug( 'sql: %s' % sql )
        qd.addAnd( QueryData( sql ) )
        return qd

    #------------------------------------------------------------------
    def get_query_select( self ):
        query = '''
            select
                id,
                attach_type_id,
                path,
                filename,
                attached,
                short_description,
                long_description,
                created_on,
                created_by,
                mime_type_id,
                img_width,
                img_height
        '''
        return query

    #------------------------------------------------------------------
    def get_query_from( self ):
        query_form = '''
            from attach
        '''
        return query_form

    #------------------------------------------------------------------
    def get_table_qdata_dict( self, extra_buttons={} ):
        T = current.T
        db = self.db
        ut_model = db_tables.get_table_model( 'unit_type', db=db )
        ut_rows = ut_model.select( orderby='name')
        ut_list = [ ('', '') ]
        for ut in ut_rows:
            ut_list.append( (ut.id, ut.name) )
        qdata = { KTF_BUTTONS: [ { KTF_NAME: 'action', KTF_TITLE: T( 'Submit' ),
                                   KTF_VALUE: 'submit' },
                                 { KTF_NAME: 'action', KTF_TITLE: T( 'New media' ),
                                   KTF_VALUE: ACT_NEW_ATTACH },
                                 { KTF_NAME: 'action', KTF_TITLE: T( 'Dump to disk' ),
                                   KTF_VALUE: ACT_DUMP_TO_STATIC },
                                 ],
                  KTF_COL_ORDER: [ KQV_SHOW_ALL ],
                  KTF_COLS: { KQV_SHOW_ALL: { KTF_TITLE: T( 'Show all' ), KTF_TYPE: KDT_BOOLEAN, },
                              },
        }
        self.qdata = qdata
        return self.qdata

    #------------------------------------------------------------------
    def get_table_view_dict( self ):
        T = current.T
        tdef = { KTF_COL_ORDER: [ 'id', 'path', 'filename', 'short_description', 'attached' ],
                 KTF_SORTABLE_COLS: [ 'id', 'path', 'filename', 'short_description', 'attached' ],
                 KTF_CELL_CLASS: 'table_border',
                 KTF_COLS: { 'id': { KTF_TITLE: T( 'Id' ), KTF_TYPE: KDT_INT,
                                     KTF_CELL_LINK: { KTF_LINK_C: 'media',
                                                      KTF_LINK_F: 'edit',
                                                      KTF_ARGS: [ 'id' ]
                                                     },
                                     KTF_CELL_CLASS: 'table_border w10pct'
                                     },
                             'path': { KTF_TITLE: T( 'Path' ), KTF_TYPE: KDT_CHAR,
                                       KTF_CELL_CLASS: 'table_border w20pct',
                                      },
                             'filename': { KTF_TITLE: T( 'Filename' ), KTF_TYPE: KDT_CHAR,
                                           KTF_CELL_CLASS: 'table_border w20pct',
                                          },
                             'attached': { KTF_TITLE: T( 'Media' ), KTF_TYPE: KDT_BLOB_MEDIA, KTF_WIDTH: 120,
                                           KTF_CELL_CLASS: 'table_border w30pct',
                                           },
                             'short_description': { KTF_TITLE: T( 'Description' ), KTF_TYPE: KDT_CHAR,
                                                    KTF_CELL_CLASS: 'table_border w20pct',
                },
            }
        }
        self.tdef = tdef
        return self.tdef

    #------------------------------------------------------------------
    def process_pre_validation_actions( self ):
        super(MediaListView, self).process_pre_validation_actions()
        request = current.request
        db = self.db
        action = request.post_vars.action
        redirect = None

        if action == ACT_NEW_ATTACH:
            redirect = URL( c='media', f='edit', args=[ 0 ] )

        if action == ACT_DUMP_TO_STATIC:
            redirect = URL( c='media', f='dump_to_disk' )
        return Storage( dict=dict(), redirect=redirect )

