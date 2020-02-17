# -*- coding: utf-8 -*-

import datetime

from gluon import current, IS_IN_DB
from gluon.dal import Field
from m16e.db.database import DbBaseTable


DT=datetime.datetime
DATE=datetime.date

#------------------------------------------------------------------
class UomModel( DbBaseTable ):
    table_name='uom'

    #------------------------------------------------------------------
    def __init__( self, db ):
        super( UomModel, self ).__init__( db )

    #------------------------------------------------------------------
    def get_fields( self ):
        T = current.T
        from m16e.db import db_tables
        db_tables.get_table_model( 'uom_type', db=self.db )
        self.fields = [ Field( 'name', 'string', notnull = 'True' ),
                        Field( 'mnemonic', 'string', notnull = 'True' ),
                        Field( 'uom_type_id', 'reference uom_type', ondelete = 'NO ACTION', notnull = 'True' ),
                        Field( 'preferred_order', 'integer', default = 0, notnull = 'True' ),
        ]
        return self.fields

    #------------------------------------------------------------------
    def get_validators( self ):
        from m16e.db import db_tables
        db_tables.get_table_model( 'uom_type', db=self.db )
        self.validators = { 'uom_type_id': IS_IN_DB( self.db, 'uom_type.id', '%(name)s', zero=None ) }
        return self.validators


    #------------------------------------------------------------------

