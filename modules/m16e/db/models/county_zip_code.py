# -*- coding: utf-8 -*-

import datetime

from gluon import current, IS_IN_DB
from gluon.dal import Field
from m16e.db.database import DbBaseTable

DT=datetime.datetime
DATE=datetime.date


class CountyZipCodeModel( DbBaseTable ):
    table_name = 'county_zip_code'


    def __init__( self, db ):
        super( CountyZipCodeModel, self ).__init__( db )


    def get_fields( self ):
        db = self.db
        from m16e.db import db_tables
        db_tables.get_table_model( 'county', db=db )
        self.fields = [ Field( 'county_id', 'reference county', notnull=True ),
                        Field( 'zip_part_1', 'string', notnull=True ),
                        Field( 'zip_part_2', 'string', notnull=True ),
                        Field( 'zip_city', 'string', notnull=True ),
        ]
        return self.fields


    def get_validators( self ):
        T = current.T
        db = self.db
        from m16e.db import db_tables
        db_tables.get_table_model( 'county', db=db )
        self.validators = { 'county_id': IS_IN_DB( self.db, 'county.id', 'county.name' ) }
        return self.validators


