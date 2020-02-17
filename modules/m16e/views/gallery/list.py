# -*- coding: utf-8 -*-
# this file is released under public domain and you can use without limitations

from m16e.db import db_tables
from gluon import current
from gluon.html import URL
from gluon.storage import Storage
from m16e import term
from m16e.db.querydata import QueryData
from m16e.kommon import KQV_PREFIX, KDT_BOOLEAN, KDT_INT, KQV_SHOW_ALL, \
    KDT_SELECT_INT, KDT_CHAR, KDT_BLOB_IMG
from m16e.ktfact import KTF_COL_ORDER, KTF_SORTABLE_COLS, KTF_CELL_CLASS, \
    KTF_COLS, KTF_TITLE, KTF_TYPE, KTF_CELL_LINK, KTF_LINK_C, KTF_LINK_F, KTF_ARGS, \
    KTF_BUTTONS, KTF_NAME, KTF_VALUE, KTF_OPTIONS, KTF_WIDTH
from m16e.views.plastic_view import BaseListPlasticView

ACT_NEW_ATTACH = 'act_new_attach'
ACT_DUMP_TO_STATIC = 'act_dump_to_static'

KQV_SITE_IMAGE = KQV_PREFIX + 'site_image'
KQV_UNIT_TYPE = KQV_PREFIX + 'unit_type'

#------------------------------------------------------------------
class GalleryListView( BaseListPlasticView ):
    controller_name = 'gallery'
    function_name = 'list'

    #------------------------------------------------------------------
    def __init__( self, db ):
        super( GalleryListView, self ).__init__( db )
        self.table_model = db_tables.get_table_model( 'attach', db=db )

        self.append_var( KQV_SITE_IMAGE, fld_type=KDT_BOOLEAN )
        self.append_var( KQV_UNIT_TYPE, fld_type=KDT_INT )

    #------------------------------------------------------------------
    def get_query_data( self, orderby=None ):
        db = self.db
        term.printLog( 'self.query_vars: ' + repr( self.query_vars ) )
        qd = super( GalleryListView, self ).get_query_data( orderby )
        qd.addAnd( QueryData( '''at.meta_name in ('images', 'webshop') ''' ) )
        is_site_image = self.query_vars.get( KQV_SITE_IMAGE )
        if is_site_image:
            qd.addAnd( QueryData( '''is_site_image = 't' ''' ) )
        ut_id = self.query_vars.get( KQV_UNIT_TYPE )
        if ut_id:
            qd.addAnd( QueryData( 'unit_type_id = %(ut_id)s', dict( ut_id=ut_id ) ) )
        return qd

    #------------------------------------------------------------------
    def get_query_select( self ):
        query = '''
            select
                a.id,
                a.attach_type_id,
                a.path,
                a.filename,
                a.attached,
                a.short_description,
                a.long_description,
                a.created_on,
                a.created_by,
                a.mime_type_id,
                a.is_site_image,
                a.img_width,
                a.img_height,
                mt.mt_name,
                at.meta_name
        '''
        return query

    #------------------------------------------------------------------
    def get_query_from( self ):
        query_form = '''
            from attach a
            join attach_type at on a.attach_type_id = at.id
            left outer join mime_type mt on a.mime_type_id = mt.id
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
                                 { KTF_NAME: 'action', KTF_TITLE: T( 'New image' ),
                                   KTF_VALUE: ACT_NEW_ATTACH },
                                 { KTF_NAME: 'action', KTF_TITLE: T( 'Dump to disk' ),
                                   KTF_VALUE: ACT_DUMP_TO_STATIC },
                                 ],
                  KTF_COL_ORDER: [ KQV_SITE_IMAGE, KQV_UNIT_TYPE, KQV_SHOW_ALL ],
                  KTF_COLS: { KQV_SHOW_ALL: { KTF_TITLE: T( 'Show all' ), KTF_TYPE: KDT_BOOLEAN, },
                              KQV_SITE_IMAGE: { KTF_TITLE: T( 'Site image' ), KTF_TYPE: KDT_BOOLEAN },
                              KQV_UNIT_TYPE: { KTF_TITLE: T( 'Unit' ), KTF_TYPE: KDT_SELECT_INT,
                                               KTF_OPTIONS: ut_list },
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
                                     KTF_CELL_LINK: { KTF_LINK_C: 'gallery',
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
                             'attached': { KTF_TITLE: T( 'Image' ), KTF_TYPE: KDT_BLOB_IMG, KTF_WIDTH: 120,
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
        super(GalleryListView, self).process_pre_validation_actions()
        request = current.request
        db = self.db
        action = request.post_vars.action
        redirect = None

        if action == ACT_NEW_ATTACH:
            redirect = URL( c='gallery', f='edit', args=[ 0 ] )

        if action == ACT_DUMP_TO_STATIC:
            redirect = URL( c='gallery', f='dump_to_disk' )
        self.set_result( redirect=redirect )

