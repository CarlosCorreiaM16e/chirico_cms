# -*- coding: utf-8 -*-

import datetime

from gluon import current
from gluon.dal import Field
from gluon.validators import IS_IN_DB
from m16e.db.database import DbBaseTable

DT=datetime.datetime
DATE=datetime.date

#----------------------------------------------------------------------
class MimeTypeExtModel( DbBaseTable ):
    table_name = 'mime_type_ext'

    #----------------------------------------------------------------------
    def __init__( self, db ):
        super( MimeTypeExtModel, self ).__init__( db )

    #----------------------------------------------------------------------
    def get_fields( self ):
        from m16e.db import db_tables
        db_tables.get_table_model( 'mime_type', db=self.db )
        self.fields = [ Field( 'mime_type_id', 'reference mime_type', ondelete='NO ACTION', notnull=True ),
                        Field( 'extension', 'string', notnull=True, unique=True ),
        ]
        return self.fields

    #----------------------------------------------------------------------
    def get_validators( self ):
        from m16e.db import db_tables
        T = current.T
        db_tables.get_table_model( 'mime_type', db=self.db )
        self.validators = { 'mime_type_id': IS_IN_DB( self.db, 'mime_type.id', '%(id)s' ),
        }
        return self.validators
    #----------------------------------------------------------------------

