# -*- coding: utf-8 -*-

import datetime

from gluon.dal import Field
from m16e.db.database import DbBaseTable

DT=datetime.datetime
DATE=datetime.date

#----------------------------------------------------------------------
class LongTaskModel( DbBaseTable ):
    table_name = 'long_task'

    #----------------------------------------------------------------------
    def __init__( self, db ):
        super( LongTaskModel, self ).__init__( db )

    #----------------------------------------------------------------------
    def get_fields( self ):
        self.fields = [ Field( 'task_name', 'string', unique=True ),
                        Field( 'force_single_instance', 'boolean', default=True, notnull=True ),
        ]
        return self.fields

    #----------------------------------------------------------------------
    def get_validators( self ):
        self.validators = {}
        return self.validators
    #----------------------------------------------------------------------

