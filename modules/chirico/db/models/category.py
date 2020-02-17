# -*- coding: utf-8 -*-

import datetime

from gluon import current
from gluon.dal import Field
from m16e.db.database import DbBaseTable

DT=datetime.datetime
DATE=datetime.date

#----------------------------------------------------------------------
class CategoryModel( DbBaseTable ):
    table_name = 'category'

    #----------------------------------------------------------------------
    def __init__( self, db ):
        super( CategoryModel, self ).__init__( db )

    #----------------------------------------------------------------------
    def get_fields( self ):
        self.fields = [ Field( 'name', 'string', notnull=True ),
                        Field( 'description', 'string' ),
                        Field( 'parent_category_id', 'integer' ),
                        Field( 'category_type', 'string', default='A', notnull=True ),
        ]
        return self.fields

    #----------------------------------------------------------------------
    def get_validators( self ):
        T = current.T
        self.validators = {}
        return self.validators
    #----------------------------------------------------------------------

