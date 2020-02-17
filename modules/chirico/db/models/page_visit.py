# -*- coding: utf-8 -*-

from gluon.dal import Field
from gluon.globals import current
from gluon.storage import Storage
from gluon.validators import IS_NOT_IN_DB, IS_IN_DB
from m16e import term
from m16e.db.database import DbBaseTable

#------------------------------------------------------------------
class PageVisitModel( DbBaseTable ):
    table_name = 'page_visit'

    #------------------------------------------------------------------
    def __init__( self, db ):
        super( PageVisitModel, self ).__init__( db )

    #------------------------------------------------------------------
    def get_fields( self ):
        self.fields = [ Field( 'site_visit_id', 'reference site_visit', ondelete = 'NO ACTION', notnull = 'True' ),
                        Field( 'page_visit_ts', 'datetime' ),
                        Field( 'path_info', 'string' ),
                        Field( 'query_string', 'string' ),
        ]
        return self.fields

    #------------------------------------------------------------------
    def get_validators( self ):
        self.validators = {
            'site_visit_id': IS_IN_DB( self.db, 'site_visit.id', 'site_visit.ip' ) }
        return self.validators

