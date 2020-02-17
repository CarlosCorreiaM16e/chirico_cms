# -*- coding: utf-8 -*-

from gluon import current
from gluon.dal import Field
from m16e.db.database import DbBaseTable


class PageCounterModel( DbBaseTable ):
    table_name = 'page_counter'


    def __init__( self, db ):
        super( PageCounterModel, self ).__init__( db )


    def get_fields( self ):
        self.fields = [ Field( 'path_info', 'string', notnull=True ),
                        Field( 'year', 'integer', notnull=True ),
                        Field( 'month', 'integer', notnull=True ),
                        Field( 'day', 'integer', notnull=True ),
                        Field( 'hour', 'integer', notnull=True ),
                        Field( 'views', 'integer', notnull=True, default=1 ),
                        ]
        return self.fields


    def get_validators( self ):
        T = current.T
        self.validators = {}
        return self.validators


