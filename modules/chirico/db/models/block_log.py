# -*- coding: utf-8 -*-

from app import db_sets
from gluon.tools import Field, IS_IN_DB
from m16e import term
from m16e.db.database import DbBaseTable
from m16e.kommon import DT


class BlockLogModel( DbBaseTable ):
    table_name = 'block_log'


    def __init__( self, db ):
        super( BlockLogModel, self ).__init__( db )


    def get_fields( self ):
        from m16e.db import db_tables
        db_tables.get_table_model( 'block', db=self.db )
        self.fields = [
            Field( 'block_id', 'reference block', notnull=True ),
            Field( 'auth_user_id', 'reference auth_user', notnull=True ),
            Field( 'ts', 'datetime' ),
            Field( 'old_body', 'text', default='', notnull=True ),
            Field( 'old_body_en', 'text', default='', notnull=True ),
            Field( 'diff_body', 'text', default='', notnull=True ),
            Field( 'diff_body_en', 'text', default='', notnull=True ),
        ]
        return self.fields


    def get_validators( self ):
        from m16e.db import db_tables
        db_tables.get_table_model( 'block', db=self.db )
        self.validators = { 'block_id': IS_IN_DB( self.db, 'block.id', '%(name)s' ),
                            'auth_user_id': IS_IN_DB( self.db, 'auth_user.id', '%(first_name)s <%(email)s>' )
        }
        return self.validators

