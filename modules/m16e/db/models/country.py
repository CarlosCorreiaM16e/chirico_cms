# -*- coding: utf-8 -*-

import datetime

from gluon import current
from gluon.dal import Field
from m16e.db.database import DbBaseTable

DT=datetime.datetime
DATE=datetime.date

#----------------------------------------------------------------------
class CountryModel( DbBaseTable ):
    table_name = 'country'

    #----------------------------------------------------------------------
    def __init__( self, db ):
        super( CountryModel, self ).__init__( db )

    #----------------------------------------------------------------------
    def get_fields( self ):
        self.fields = [ Field( 'iso3166_1_alpha_2', 'string', notnull=True ),
                        Field( 'name', 'string', notnull=True ),
                        Field( 'preferred_order', 'integer', notnull=True, default=0 )
                        ]
        return self.fields

    #----------------------------------------------------------------------
    def get_validators( self ):
        T = current.T
        self.validators = {}
        return self.validators
    #----------------------------------------------------------------------

