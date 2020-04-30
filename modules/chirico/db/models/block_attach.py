# -*- coding: utf-8 -*-

from gluon import current, Field, IS_NULL_OR, IS_IN_DB
from m16e.db.database import DbBaseTable


class BlockAttachModel( DbBaseTable ):
    table_name = 'block_attach'


    def __init__( self, db ):
        super( BlockAttachModel, self ).__init__( db )


    def get_fields( self ):
        from m16e.db import db_tables
        db_tables.get_table_model( 'attach', db=self.db )
        db_tables.get_table_model( 'block', db=self.db )
        self.fields = [ Field( 'block_id', 'reference block', ondelete='NO ACTION' ),
                        Field( 'attach_id', 'reference attach', ondelete='NO ACTION' ),
        ]
        return self.fields


    def get_validators( self ):
        T = current.T
        from m16e.db import db_tables
        db_tables.get_table_model( 'attach', db=self.db )
        db_tables.get_table_model( 'block', db=self.db )
        self.validators = { 'attach_id': IS_NULL_OR( IS_IN_DB( self.db, 'attach.id', '%(id)s' ) ),
                            'block_id': IS_NULL_OR( IS_IN_DB( self.db, 'block.id', '%(name)s' ) ),
        }
        return self.validators

