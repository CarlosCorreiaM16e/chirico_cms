# -*- coding: utf-8 -*-

from gluon import current
from gluon.dal import Field
from gluon.validators import IS_NULL_OR, IS_IN_DB, IS_IN_SET
from m16e import term
from m16e.db.database import DbBaseTable


class ThreadVisibilityModel( DbBaseTable ):
    table_name = 'thread_visibility'


    def __init__( self, db ):
        super( ThreadVisibilityModel, self ).__init__( db )


    def get_fields( self ):
        T = current.T
        from m16e.db import db_tables
        db_tables.get_table_model( 'thread', db=self.db )
        self.fields = [ Field( 'thread_id', 'reference thread', ondelete='NO ACTION', notnull=True ),
                        Field( 'group_id', 'reference auth_group', ondelete='NO ACTION', notnull=True ),
                        ]
        return self.fields


    def get_validators( self ):
        from m16e.db import db_tables
        db_tables.get_table_model( 'thread', db=self.db )
        self.validators = { 'group_id': IS_IN_DB( self.db, 'auth_group.id', '%(role)s' ),
                            'thread_id': IS_IN_DB( self.db, 'thread.id', '%(first_name)s (%(email)s)' ),
                            }
        return self.validators

