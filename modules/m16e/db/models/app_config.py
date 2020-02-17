# -*- coding: utf-8 -*-

from gluon import current
from gluon.dal import Field
from gluon.validators import IS_NULL_OR, IS_IN_DB, IS_IN_SET
from m16e import term
from m16e.db.database import DbBaseTable
from m16e.kommon import DATE, DT


#----------------------------------------------------------------------
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

