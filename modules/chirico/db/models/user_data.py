# -*- coding: utf-8 -*-

from gluon import current, Field, IS_IN_DB, IS_NULL_OR
from m16e.db import db_tables
from m16e.db.database import DbBaseTable


class UserDataModel( DbBaseTable ):
    table_name = 'user_data'


    def __init__( self, db ):
        super( UserDataModel, self ).__init__( db )


    def get_fields( self ):
        db_tables.get_table_model( 'country', db=self.db )
        self.fields = [ Field( 'auth_user_id', 'reference auth_user', notnull=True ),
                        Field( 'address_1', 'string' ),
                        Field( 'address_2', 'string' ),
                        Field( 'zip_code', 'string' ),
                        Field( 'city', 'string' ),
                        Field( 'country_id', 'reference country' ),
                        Field( 'phone_1', 'string' ),
                        Field( 'url', 'string' ),
                        Field( 'obs', 'text' ),
                        ]
        return self.fields


    def get_validators( self ):
        T = current.T
        db_tables.get_table_model( 'country', db=self.db )
        self.validators = { 'auth_user_id': IS_IN_DB( self.db, 'auth_user.id', '%(first_name)s <%(email)s>' ),
                            'country_id': IS_NULL_OR( IS_IN_DB( self.db, 'country.id', '%(name)s', orderby='preferred_order' ) ),
                            }
        return self.validators

