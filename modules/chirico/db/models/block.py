# -*- coding: utf-8 -*-

from app import db_sets
from gluon.tools import Field
from gluon.validators import IS_IN_DB, IS_NOT_IN_DB, IS_NULL_OR, IS_IN_SET
from m16e import term
from m16e.db.database import DbBaseTable
from m16e.kommon import DT


class BlockModel( DbBaseTable ):
    table_name = 'block'


    def __init__( self, db ):
        super( BlockModel, self ).__init__( db )


    def get_fields( self ):
        from m16e.db import db_tables
        db_tables.get_table_model( 'page', db=self.db )
        self.fields = [
            Field( 'name', 'string' ),
            Field( 'description', 'string' ),
            Field( 'page_id', 'reference page', ondelete='NO ACTION', notnull=True ),
            Field( 'container', 'string', notnull=True, default='M' ),
            Field( 'blk_order', 'integer', notnull=True, default=1 ),
            Field( 'body', 'text', notnull='True', default='' ),
            Field( 'body_en', 'text', notnull='True', default='' ),
            Field( 'body_markup', 'string', default=db_sets.MARKUP_SET[0][0], notnull=True ),
            Field( 'created_on', 'datetime', default=DT.now(), notnull='True' ),
            Field( 'created_by', 'reference auth_user', ondelete='NO ACTION', notnull='True' ),
            Field( 'last_modified_by', 'reference auth_user', ondelete='NO ACTION', notnull='True' ),
            Field( 'last_modified_on', 'datetime', default=DT.now(), notnull='True' ), # NEW
            Field( 'colspan', 'integer', notnull=True, default=1 ),
            Field( 'rowspan', 'integer', notnull=True, default=1 ),
            Field( 'css_class', 'string' ),
            Field( 'css_style', 'string' ),
            Field( 'html_element_id', 'string' ),
        ]
        return self.fields


    def get_validators( self ):
        from m16e.db import db_tables
        db_tables.get_table_model( 'page', db=self.db )
        self.validators = { 'name': IS_NOT_IN_DB( self.db, 'block.name' ),
                            'body_markup': IS_IN_SET( db_sets.MARKUP_SET ),
                            'page_id': IS_IN_DB( self.db, 'page.id', '%(name)s' ),
                            'container': IS_IN_SET( db_sets.BLOCK_CONTAINER_SET )
        }
        return self.validators

