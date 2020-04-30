# -*- coding: utf-8 -*-


from gluon import current, Field, IS_NULL_OR, IS_IN_DB
from m16e.db.database import DbBaseTable


class DistrictModel( DbBaseTable ):
    table_name = 'district'


    def __init__( self, db ):
        super( DistrictModel, self ).__init__( db )


    def get_fields( self ):
        from m16e.db import db_tables
        db_tables.get_table_model( 'country', db=self.db )
        db_tables.get_table_model( 'country_region', db=self.db )
        self.fields = [ Field( 'name', 'string', notnull=True ),
                        Field( 'country_id', 'reference country', notnull=True ),
                        Field( 'country_region_id', 'reference country_region', notnull=True ),
                        Field( 'tax_zone_id', 'integer' ),
        ]
        return self.fields


    def get_validators( self ):
        T = current.T
        from m16e.db import db_tables
        db_tables.get_table_model( 'country', db=self.db )
        db_tables.get_table_model( 'country_region', db=self.db )
        self.validators = { 'country_id': IS_NULL_OR( IS_IN_DB( self.db,
                                                                'country.id',
                                                                '%(name)s [%(id)s]' ) ),
                            'country_region_id': IS_NULL_OR( IS_IN_DB( self.db,
                                                                'country_region.id',
                                                                '%(name)s [%(id)s]' ) ),

                            }
        return self.validators
