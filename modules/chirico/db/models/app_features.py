# -*- coding: utf-8 -*-

from gluon import IS_NOT_IN_DB
from gluon.dal import Field
from m16e.db.database import DbBaseTable


#----------------------------------------------------------------------
class AppFeaturesModel( DbBaseTable ):
    table_name = 'app_features'

    #----------------------------------------------------------------------
    def __init__( self, db ):
        super( AppFeaturesModel, self ).__init__( db )


    #----------------------------------------------------------------------
    def get_fields( self ):
        self.fields = [ Field( 'name', 'string' ),
                        Field( 'max_products', 'integer', default=0, notnull=True ),
                        Field( 'max_entities', 'integer', default=0, notnull=True ),
                        Field( 'max_monthly_docs', 'integer', default=0, notnull=True ),
                        Field( 'max_users', 'integer', default=0, notnull=True ),
                        Field( 'use_transport_docs', 'boolean', default=False ),
                        Field( 'use_templates', 'boolean', default=False ),
                        Field( 'anual_fee', 'decimal(15,2)', default=0.0 ),
                        Field( 'max_resolution_days', 'decimal(15,2)', default=0.0 ),
                        ]
        return self.fields


    #----------------------------------------------------------------------
    def get_validators( self ):
        self.validators = { 'name': IS_NOT_IN_DB( self.db, 'app_features.name' ),
        }
        return self.validators


    #----------------------------------------------------------------------

