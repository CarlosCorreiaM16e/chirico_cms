# -*- coding: utf-8 -*-

import datetime

from gluon import current
from gluon.dal import Field
from m16e.db.database import DbBaseTable

DT=datetime.datetime
DATE=datetime.date

#------------------------------------------------------------------
class UomTypeModel( DbBaseTable ):
    table_name='uom_type'

    #------------------------------------------------------------------
    def __init__( self, db ):
        super( UomTypeModel, self ).__init__( db )

    #------------------------------------------------------------------
    def get_fields( self ):
        T = current.T
        self.fields = [ Field( 'name', 'string', notnull = 'True' ),
                        Field( 'is_date', 'boolean', default = False, notnull = 'True' ),
                        Field( 'is_time', 'boolean', default = False, notnull = 'True' ),
                        Field( 'is_weight', 'boolean', default = False, notnull = 'True' ),
                        Field( 'is_length', 'boolean', default = False, notnull = 'True' ),
                        Field( 'is_volume', 'boolean', default = False, notnull = 'True' ),
        ]
        return self.fields

    #------------------------------------------------------------------
    def get_validators( self ):
        self.validators = {}
        return self.validators

    #------------------------------------------------------------------

