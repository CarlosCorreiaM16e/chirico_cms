# -*- coding: utf-8 -*-

from m16e import term
from m16e.db.database import DbBaseTable
from gluon import current, Field, IS_IN_DB


#----------------------------------------------------------------------
class CountryRegionModel( DbBaseTable ):
    table_name = 'country_region'

    #----------------------------------------------------------------------
    def __init__( self, db ):
        super( CountryRegionModel, self ).__init__( db )

    #----------------------------------------------------------------------
    def get_fields( self ):
        T = current.T
        from m16e.db import db_tables
        db_tables.get_table_model( 'country', db=self.db )
        self.fields = [ Field( 'country_id', 'reference country', ondelete='NO ACTION', notnull=True ),
                        Field( 'name', 'string', notnull=True, unique=True ),
                        Field( 'nuts_code', 'string', unique=True ),
                        Field( 'preferred_order', 'integer', notnull=True ),
        ]
        return self.fields

    #----------------------------------------------------------------------
    def get_validators( self ):
        T = current.T
        from m16e.db import db_tables
        db_tables.get_table_model( 'country', db=self.db )
        self.validators = { 'country_id': IS_IN_DB( self.db, 'country.id', '%(name)s' ),
        }
        return self.validators
    #----------------------------------------------------------------------

