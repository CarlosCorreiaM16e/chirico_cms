# -*- coding: utf-8 -*-

from gluon import current, Field
from m16e import term
from m16e.db.database import DbBaseTable


class AppConfigModel( DbBaseTable ):
    table_name = 'app_config'

    #----------------------------------------------------------------------
    def __init__( self, db ):
        super( AppConfigModel, self ).__init__( db )


    #----------------------------------------------------------------------
    def get_fields( self ):
        self.fields = [ Field( 'flash_msg_delay', 'integer', default=2000, notnull=True ),
                        Field( 'app_theme_id', 'integer', default=1, notnull=True ),
        ]
        return self.fields


    #----------------------------------------------------------------------
    def get_validators( self ):
        T = current.T
        self.validators = {}
        return self.validators
    #----------------------------------------------------------------------

