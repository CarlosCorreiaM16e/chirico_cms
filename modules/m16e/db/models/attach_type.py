# -*- coding: utf-8 -*-


from gluon import current, Field
from m16e.db.database import DbBaseTable


class AttachTypeModel( DbBaseTable ):
    table_name = 'attach_type'


    def __init__( self, db ):
        super( AttachTypeModel, self ).__init__( db )


    def get_fields( self ):
        self.fields = [ Field( 'name', 'string', notnull=True ),
                        Field( 'meta_name', 'string', notnull=True, unique=True ),
        ]
        return self.fields


    def get_validators( self ):
        T = current.T
        self.validators = {}
        return self.validators

