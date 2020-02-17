# -*- coding: utf-8 -*-

from gluon import current, Field
from m16e.db.database import DbBaseTable


class AppThemeModel( DbBaseTable ):
    table_name = 'app_theme'


    def __init__( self, db ):
        super( AppThemeModel, self ).__init__( db )


    def get_fields( self ):
        self.fields = [ Field( 'name', 'string', notnull=True ),
                        Field( 'title', 'string', notnull=True ),
                        Field( 'subtitle', 'string', notnull=True ),
                        Field( 'logo_header', 'string', notnull=True ),
                        Field( 'login_button_position', 'string', notnull=True ),
                        Field( 'meta_name', 'string' ),
                        Field( 'stylesheet', 'string' ),
        ]
        return self.fields


    def get_validators( self ):
        T = current.T
        self.validators = {}
        return self.validators

