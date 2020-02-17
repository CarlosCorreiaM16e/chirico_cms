# -*- coding: utf-8 -*-

from gluon.dal import Field
from m16e import term
from m16e.db.database import DbBaseTable


class ThreadTypeModel( DbBaseTable ):
    table_name = 'thread_type'


    def __init__( self, db ):
        super( ThreadTypeModel, self ).__init__( db )


    def get_fields( self ):
        self.fields = [ Field( 'thread_type_name', 'string', notnull=True ),
                        Field( 'meta_name', 'string' ),
                        Field( 'preferred_order', 'integer', default=0, notnull=True ),
        ]
        return self.fields


    def get_validators( self ):
        self.validators = {}
        return self.validators

