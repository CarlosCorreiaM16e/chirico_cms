# -*- coding: utf-8 -*-
# this file is released under public domain and you can use without limitations

from m16e.db import db_tables
from gluon import current, A, URL, SPAN
from gluon.storage import Storage

from m16e import term
from m16e.db.querydata import QueryData
from m16e.kommon import KDT_INT, KDT_CHAR, KQV_SHOW_ALL, KDT_BOOLEAN, storagize, KDT_RAW, KDT_XML
from m16e.ktfact import KTF_COL_ORDER, KTF_SORTABLE_COLS, KTF_CELL_CLASS, \
    KTF_COLS, KTF_TITLE, KTF_TYPE, KTF_CELL_LINK, KTF_LINK_C, KTF_LINK_F, KTF_ARGS, \
    KTF_MAX_LENGTH, KTF_BUTTONS, KTF_NAME, KTF_VALUE
from m16e.views.plastic_view import BaseListPlasticView

ACT_NEW_BLOCK = 'new_block'


class BlockListView( BaseListPlasticView ):
    controller_name = 'block'
    function_name = 'list'


    def __init__( self, db ):
        super( BlockListView, self ).__init__( db )
        self.table_model = db_tables.get_table_model( 'block', db )
        self.append_var( KQV_SHOW_ALL, fld_type=KDT_BOOLEAN )
        self.new_record_action = ACT_NEW_BLOCK


    def do_process( self ):
        return super( BlockListView, self ).do_process()


    def get_table_view_dict( self ):
        T = current.T
        tdef = {
            KTF_COL_ORDER: [
                'id', 'name', 'description', 'blk_order', 'page_id', 'page_name' ],
            KTF_SORTABLE_COLS: [
                'id', 'name', 'description', 'blk_order', 'page_id' ],
            KTF_CELL_CLASS: 'table_border',
            KTF_COLS: {
                'id': {
                    KTF_TITLE: T( 'Id' ),
                    KTF_TYPE: KDT_INT,
                    KTF_CELL_LINK: {
                        KTF_LINK_C: 'block',
                        KTF_LINK_F: 'composer',
                        KTF_ARGS: [ 'id' ]
                    },
                    KTF_CELL_CLASS: 'table_border w10pct'
                },
                'page_id': {
                    KTF_TITLE: T( 'Page' ),
                    KTF_TYPE: KDT_INT,
                    KTF_CELL_LINK: {
                        KTF_LINK_C: 'page',
                        KTF_LINK_F: 'composer',
                        KTF_ARGS: [ 'page_id' ]
                    },
                    KTF_CELL_CLASS: 'table_border w10pct'
                },
                'description': {
                    KTF_TITLE: T( 'Description' ),
                    KTF_TYPE: KDT_CHAR,
                    KTF_CELL_CLASS: 'table_border w40pct',
                },
                'name': {
                    KTF_TITLE: T( 'Name' ),
                    KTF_TYPE: KDT_CHAR,
                    KTF_CELL_CLASS: 'table_border w20pct',
                },
                'page_name': {
                    KTF_TITLE: T( 'Page' ),
                    KTF_TYPE: KDT_XML,
                    KTF_CELL_CLASS: 'table_border w30pct',
                },
                'blk_order': {
                    KTF_TITLE: T( 'Order' ),
                    KTF_TYPE: KDT_INT,
                },
            }
        }
        self.tdef = storagize( tdef )
        return self.tdef


    def get_table_qdata_dict( self, extra_buttons={} ):
        T = current.T
        qdata = {
            KTF_BUTTONS: [],
            KTF_COL_ORDER: [ KQV_SHOW_ALL ],
            KTF_COLS: {
                KQV_SHOW_ALL: { KTF_TITLE: T( 'Show all' ), KTF_TYPE: KDT_BOOLEAN, },
            },
        }
        self.qdata = storagize( qdata )
        return self.qdata


    def get_query_data( self, orderby=None ):
        qd = super( BlockListView, self ).get_query_data( orderby )
        # show_all = self.query_vars.get( KQV_SHOW_ALL )
        # if not show_all:
        #     qd.addAnd( QueryData( 'b.is_deleted = false' ) )
        return qd


    def get_query_select( self ):
        q_select = '''
            select
                id,
                name,
                description,
                blk_order,
                page_id
        '''
        return q_select


    def get_query_from( self ):
        q_from = '''
            from block b
        '''
        return q_from


    def get_record_list( self, qd=None, alias=None, print_query=None, force_refresh=False ):
        super( BlockListView, self ).get_record_list( qd=qd,
                                                      alias=alias,
                                                      print_query=print_query,
                                                      force_refresh=force_refresh )
        db = self.db
        # p_model = db_tables.get_table_model( 'page', db=db )
        # pb_model = db_tables.get_table_model( 'page_block', db=db )
        for r in self.list_rows:
            p_model = db_tables.get_table_model( 'page', db=db )
            if r.page_id:
                page = p_model[ r.page_id ]
                r.page_name = SPAN( A( page.name,
                                       _href=URL( c='page',
                                                  f='composer',
                                                  args=[ r.page_id ] ) ) )
            else:
                r.page_name = ''
            # q_sql = (db.page_block.block_id == r.id)
            # pb_list = pb_model.select( q_sql )
            # q_sql = (db.page.id.belongs( [ pb.page_id for pb in pb_list ] ) )
            # pages = p_model.select( q_sql, orderby='name' )
            # p_list = []
            # l = len( pages ) - 1
            # for idx, p in enumerate( pages ):
            #     p_list.append( A( p.name,
            #                       _href=URL( c='page', f='edit', args= [ p.id ] ) ) )
            #     if idx < l:
            #         p_list.append( ', ' )
            #
            # r.page_name = SPAN( *p_list )
        return self.list_rows


