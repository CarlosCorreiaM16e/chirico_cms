# -*- coding: utf-8 -*-

from gluon.dal import Field
from gluon.globals import current
from gluon.storage import Storage
from gluon.validators import IS_NOT_IN_DB, IS_IN_DB
from m16e import term
from m16e.db.database import DbBaseTable

#------------------------------------------------------------------
class SiteVisitModel( DbBaseTable ):
    table_name = 'site_visit'

    #------------------------------------------------------------------
    def __init__( self, db ):
        super( SiteVisitModel, self ).__init__( db )

    #------------------------------------------------------------------
    def get_fields( self ):
        self.fields = [ Field( 'visit_ts', 'datetime' ),
                        Field( 'ip', 'string' ),
                        Field( 'auth_user_id', 'reference auth_user', ondelete = 'NO ACTION' ),
                        Field( 'client_os_name', 'string' ),
                        Field( 'client_os_version', 'string' ),
                        Field( 'client_flavor_name', 'string' ),
                        Field( 'client_flavor_version', 'string' ),
                        Field( 'client_is_mobile', 'boolean' ),
                        Field( 'client_is_tablet', 'boolean' ),
                        Field( 'client_browser_name', 'string' ),
                        Field( 'client_browser_version', 'string' ),
                        Field( 'client_user_agent', 'string' ),
        ]
        return self.fields

    #------------------------------------------------------------------
    def get_validators( self ):
        self.validators = {
            'auth_user_id': IS_IN_DB( self.db, 'auth_user.id', 'auth_user.email' ) }
        return self.validators

