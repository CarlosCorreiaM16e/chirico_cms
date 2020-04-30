# -*- coding: utf-8 -*-

from gluon import current
from gluon.dal import Field
from m16e.db.database import DbBaseTable
from m16e.kommon import DT


class PageLogModel( DbBaseTable ):
    table_name = 'page_log'


    def __init__( self, db ):
        super( PageLogModel, self ).__init__( db )


    def get_fields( self ):
        self.fields = [ Field( 'path_info', 'string', notnull=True ),
                        Field( 'ts', 'datetime', default=DT.now, notnull=True ),
                        Field( 'client_ip', 'string' ),
                        Field( 'auth_user_id', 'referne auth_user' ),
                        Field( 'is_tablet', 'boolean', default=False ),
                        Field( 'is_mobile', 'boolean', default=False ),
                        Field( 'os_name', 'string' ),
                        Field( 'browser_name', 'string' ),
                        Field( 'browser_version', 'string' ),
                        ]
        return self.fields


    def get_validators( self ):
        T = current.T
        self.validators = {}
        return self.validators


