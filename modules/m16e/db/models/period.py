# -*- coding: utf-8 -*-

import datetime

from gluon import current
from gluon.dal import Field
from gluon.validators import IS_IN_SET
from m16e.db.database import DbBaseTable

DT = datetime.datetime
DATE = datetime.date

#------------------------------------------------------------------
class PeriodModel( DbBaseTable ):
    table_name = 'period'

    #------------------------------------------------------------------
    def __init__( self, db ):
        super( PeriodModel, self ).__init__( db )
        self.track_history = True

    #------------------------------------------------------------------
    def get_fields( self ):
        from m16e.db import db_tables
        db_tables.get_table_model( 'uom', db=self.db )
        self.fields = [
             Field( 'uom_id', 'reference uom', notnull = 'True' ),
             Field( 'units', 'integer', notnull = 'True' ),
             Field( 'name', 'string', notnull = 'True' ),
             Field( 'period_type', 'string', notnull = 'True' ),
        ]
        return self.fields

    #------------------------------------------------------------------
    def get_validators( self ):
        T = current.T
        self.validators = { 'period_type': IS_IN_SET( { 'minute': T( 'Minute' ),
                                                        'hour': T( 'Hour' ),
                                                        'day': T( 'Day' ),
                                                        'month': T( 'Month' ),
                                                        'year': T( 'Year' ) } )}
        return self.validators

