# -*- coding: utf-8 -*-

from gluon import current
from gluon.dal import Field
from gluon.validators import IS_NULL_OR, IS_IN_DB, IS_IN_SET
from m16e import term
from m16e.db.database import DbBaseTable


class ThreadStatusModel( DbBaseTable ):
    table_name = 'thread_status'


    def __init__( self, db ):
        super( ThreadStatusModel, self ).__init__( db )


    def get_fields( self ):
        self.fields = [ Field( 'thread_status_name', 'string', notnull=True ),
                        Field( 'meta_name', 'string' ),
                        Field( 'is_closed', 'boolean', default=False, notnull=True ),
                        Field( 'preferred_order', 'integer', default=0, notnull=True ),
        ]
        return self.fields


    def get_validators( self ):
        self.validators = {}
        return self.validators

