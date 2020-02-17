# -*- coding: utf-8 -*-
from app.db_sets import PANEL_POSITION_SET
from gluon.dal import Field
from gluon.globals import current
from gluon.storage import Storage
from gluon.validators import IS_NOT_IN_DB, IS_IN_DB, IS_NULL_OR, IS_IN_SET
from m16e import term
from m16e.db.database import DbBaseTable

#------------------------------------------------------------------
class PageModel( DbBaseTable ):
    table_name = 'page'

    #------------------------------------------------------------------
    def __init__( self, db ):
        super( PageModel, self ).__init__( db )

    #------------------------------------------------------------------
    def get_fields( self ):
        self.fields = [
            Field( 'name', 'string', unique=True, notnull=True ),
            Field( 'tagname', 'string' ),
            Field( 'url_c', 'string' ),
            Field( 'url_f', 'string' ),
            Field( 'url_args', 'string' ),
            Field( 'title', 'string', notnull='True' ),
            Field( 'title_en', 'string', notnull='True' ),
            Field( 'colspan', 'integer', default=1, notnull='True' ),
            Field( 'rowspan', 'integer', default=1, notnull='True' ),
            Field( 'hide', 'boolean', default=False, notnull=True ),
            Field( 'menu_order', 'integer' ),
            Field( 'aside_position', 'string' ),
            Field( 'aside_title', 'string' ),
            Field( 'aside_title_en', 'string' ),
            Field( 'main_panel_cols', 'integer', default=1, notnull='True' ),
            Field( 'aside_panel_cols', 'integer', default=0, notnull='True' ),
            Field( 'parent_page_id', 'integer' ),
            Field( 'last_modified_by', 'reference auth_user', ondelete='NO ACTION' ),
            # Field( 'is_deleted', 'boolean', default=False, notnull='True' ),
            Field( 'is_news', 'boolean', default=False, notnull='True' ),
            Field( 'page_timestamp', 'datetime' )
        ]
        return self.fields

    #------------------------------------------------------------------
    def get_validators( self ):
        self.validators = { 'name': IS_NOT_IN_DB( self.db, 'page.name' ),
                            'parent_page_id': IS_NULL_OR( IS_IN_DB( self.db, 'page.id', '%(name)s' ) ),
                            'aside_position': IS_NULL_OR( IS_IN_SET( PANEL_POSITION_SET ) ) }
        return self.validators

#     #------------------------------------------------------------------
#     def get_data( self,
#                   cache_results=300,
#                   page_id=None,
#                   name=None,
#                   hide_deleted=True,
#                   orderby='name' ):
#         '''
#         cache results by default for 300 seconds,
#         call with cache_results=False|None|0
#         to force DB read
#         '''
#         cache = current.cache
#         cache_cfg = (cache.ram, cache_results or 0)
#         q = (self.db.page.id > 0)
#         if hide_deleted:
#             q &= (self.db.page.is_deleted == False)
#
#         rec_list = self.db( q ).select( cache=cache_cfg,
#                                         orderby=self.get_orderby( orderby ) )
#         if page_id:
#             for r in rec_list:
#                 if r.id == page_id:
#                     return r
#         if name:
#             for r in rec_list:
#                 if r.name == name:
#                     return r
#         return rec_list
#
#     #------------------------------------------------------------------
#     def restore( self, page_history_id ):
#         session = current.session
#         auth = session.auth
#         upd = Storage()
#         ph = self.db.page_history[ page_history_id ]
#         upd.tagname = ph.o_tagname
#         upd.url_c = ph.o_url_c
#         upd.url_f = ph.o_url_f
#         upd.title = ph.o_title
#         upd.colspan = ph.o_colspan
#         upd.rowspan = ph.o_rowspan
#         upd.menu_order = ph.o_menu_order
#         upd.parent_page_id = ph.o_parent_page_id
#         upd.last_modified_by = auth.user.id
#         term.printLog( 'restoring: ' + repr( upd ) )
#         self.db( self.db.page.id == ph.page_id ).update( **upd )
# #         term.printDebug( 'sql: %s' % ( self.db._lastsql ) )
#         return ph.page_id
#
#     #------------------------------------------------------------------
#     def set_deleted( self, page_id, delete_blocks=False ):
#         db = self.db
#         if delete_blocks:
#             from chirico.db.models.block import BlockModel
#             BlockModel( self.db ).define_table()
#             blockList = db( db.block.page_id == page_id )
#             for b in blockList:
#                 db( db.block.id == b.id ).update( is_deleted=True )
#
#         db( db.page.id == page_id ).update( is_deleted=True )
#
#     #------------------------------------------------------------------
#     def purge( self, page_id, delete_blocks=False ):
#         db = self.db
#         if delete_blocks:
#             from chirico.db.models.block import BlockModel
#             BlockModel( self.db ).define_table()
#             blockList = db( db.block.page_id == page_id )
#             for b in blockList:
#                 db( db.block_history.block_id == b.id ).delete()
#                 db( db.block.id == b.id ).delete()
#
#         db( db.page_history.page_id == page_id ).delete()
#         db( db.page.id == page_id ).delete()
#
#     #------------------------------------------------------------------
#     def clone( self, page_id, inc_blocks=True ):
#         db = self.db
#         page = db.page[ page_id ]
#         upd_page = {}
#         for f in db.page.fields:
#             if not f == 'id':
#                 upd_page[f] = page[f]
#         new_page_id = db.page.insert( **upd_page )
#         if inc_blocks:
#             from chirico.db.models.block import BlockModel
#             BlockModel( self.db ).define_table()
#             blocks = db( db.block.page_id == page.id ).select()
#             for b in blocks:
#                 updBlock = {}
#                 for f in db.block.fields:
#                     if not f == 'id':
#                         updBlock[f] = b[f]
#                 updBlock[ 'page_id' ] = new_page_id.id
#                 db.block.insert( **updBlock )
#
#         return new_page_id
#
#     #------------------------------------------------------------------
