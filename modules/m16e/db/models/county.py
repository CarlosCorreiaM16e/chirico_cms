# -*- coding: utf-8 -*-


from gluon import current
from gluon.dal import Field
from gluon.validators import IS_IN_DB
from m16e.db.database import DbBaseTable


#----------------------------------------------------------------------
class CountyModel( DbBaseTable ):
    table_name = 'county'

    #----------------------------------------------------------------------
    def __init__( self, db ):
        super( CountyModel, self ).__init__( db )

    #----------------------------------------------------------------------
    def get_fields( self ):
        from m16e.db import db_tables
        db_tables.get_table_model( 'district', db=self.db )
        self.fields = [ Field( 'name', 'string', notnull=True ),
                        Field( 'district_id', 'reference district', notnull=True ),
        ]
        return self.fields

    #----------------------------------------------------------------------
    def get_validators( self ):
        from m16e.db import db_tables
        T = current.T
        db_tables.get_table_model( 'district', db=self.db )
        self.validators = { 'district_id': IS_IN_DB( self.db,
                                                     'district.id',
                                                     '%(name)s' ) }
        return self.validators
    #----------------------------------------------------------------------

