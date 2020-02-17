# # -*- coding: utf-8 -*-
# from app import db_sets
# from gluon.dal import Field
# from gluon.validators import IS_IN_DB, IS_NOT_IN_DB, IS_NULL_OR, IS_IN_SET
# from m16e import term
# from m16e.db.database import DbBaseTable
#
#
# class PageBlockModel( DbBaseTable ):
#     table_name = 'page_block'
#
#
#     def __init__( self, db ):
#         super( PageBlockModel, self ).__init__( db )
#
#
#     def get_fields( self ):
#         from m16e.db import db_tables
#         db_tables.get_table_model( 'page', db=self.db )
#         db_tables.get_table_model( 'block', db=self.db )
#         self.fields = [ Field( 'page_id', 'reference page' ),
#                         Field( 'block_id', 'reference block' ),
#                         Field( 'blk_order', 'integer', notnull=True, default=1 ),
#                         Field( 'container', 'string', notnull=True, default='M' ),
#                         Field( 'colspan', 'integer', notnull=True, default=1 ),
#                         Field( 'rowspan', 'integer', notnull=True, default=1 ),
#                         Field( 'css_class', 'string' ),
#                         Field( 'css_style', 'string' ),
#                         ]
#         return self.fields
#
#
#     def get_validators( self ):
#         from m16e.db import db_tables
#         db_tables.get_table_model( 'page', db=self.db )
#         db_tables.get_table_model( 'block', db=self.db )
#         self.validators = { 'page_id': IS_IN_DB( self.db,
#                                                  'page.id', '%(name)s' ),
#                             'block_id': IS_IN_DB( self.db,
#                                                   'block.id', '%(name)s' ),
#                             'container': IS_IN_SET( db_sets.BLOCK_CONTAINER_SET ),
#                             }
#         return self.validators
#
