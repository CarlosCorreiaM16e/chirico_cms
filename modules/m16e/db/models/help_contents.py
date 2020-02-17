# -*- coding: utf-8 -*-

from gluon import current
from gluon.dal import Field
from m16e.db.database import DbBaseTable


class HelpContentsModel( DbBaseTable ):
    table_name='help_contents'


    def __init__( self, db ):
        super( HelpContentsModel, self ).__init__( db )


    def get_fields( self ):
        T = current.T
        from m16e.db import db_tables
        db_tables.get_table_model( 'help_contents', db=self.db )
        self.fields = [ Field( 'contents', 'text', notnull = 'True' ),
                        Field( 'title', 'string' ),
                        Field( 'parent_id', 'reference help_contents' ),
        ]
        return self.fields


    def get_validators( self ):
        self.validators = {}
        return self.validators


