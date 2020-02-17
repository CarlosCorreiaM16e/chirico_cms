# -*- coding: utf-8 -*-

import datetime

from gluon.dal import Field
from m16e.db.database import DbBaseTable

DT = datetime.datetime
DATE = datetime.date

#------------------------------------------------------------------
class WdayModel( DbBaseTable ):
    table_name = 'wday'

    #------------------------------------------------------------------
    def __init__( self, db ):
        super( WdayModel, self ).__init__( db )

    #------------------------------------------------------------------
    def get_fields( self ):
        self.fields = [ Field( 'name', 'string', notnull = 'True' ),
                       ]
        return self.fields

    #------------------------------------------------------------------
    def get_validators( self ):
        self.validators = {}
        return self.validators

