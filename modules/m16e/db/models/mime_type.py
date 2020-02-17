# -*- coding: utf-8 -*-

import datetime

from gluon import current
from gluon.dal import Field
from m16e.db.database import DbBaseTable

DT=datetime.datetime
DATE=datetime.date

#----------------------------------------------------------------------
class MimeTypeModel( DbBaseTable ):
    table_name = 'mime_type'

    #----------------------------------------------------------------------
    def __init__( self, db ):
        super( MimeTypeModel, self ).__init__( db )

    #----------------------------------------------------------------------
    def get_fields( self ):
        self.fields = [ Field( 'mt_name', 'string', notnull=True, unique=True ),
                        Field( 'description', 'string' ),
                        Field( 'edit_command', 'string' ),
                        Field( 'view_command', 'string' ),
                        Field( 'preferred_order', 'integer', default=0, notnull=True ),
        ]
        return self.fields

    #----------------------------------------------------------------------
    def get_validators( self ):
        T = current.T
        self.validators = {}
        return self.validators
    #----------------------------------------------------------------------

