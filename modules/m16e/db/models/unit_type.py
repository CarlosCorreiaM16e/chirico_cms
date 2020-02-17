# -*- coding: utf-8 -*-

from gluon import current
from gluon.dal import Field
from m16e.db.database import DbBaseTable


class UnitTypeModel( DbBaseTable ):
    table_name = 'unit_type'


    def __init__( self, db ):
        super( UnitTypeModel, self ).__init__( db )


    def get_fields( self ):
        self.fields = [ Field( 'name', 'string', notnull=True, unique=True ),
                        Field( 'path', 'string', notnull=True ),
                        Field( 'meta_name', 'string', notnull=True ),
                        Field( 'preferred_order', 'integer', default=0 ),
                        Field( 'parent_unit_type_id', 'integer' ),
                        ]
        return self.fields


    def get_validators( self ):
        T = current.T
        self.validators = {}
        return self.validators

