# -*- coding: utf-8 -*-

from gluon import current
from gluon.dal import Field
from gluon.validators import IS_NULL_OR, IS_IN_DB, IS_IN_SET
from m16e import term
from m16e.db.database import DbBaseTable


class ThreadSubscribersModel( DbBaseTable ):
    table_name = 'thread_subscriber'


    def __init__( self, db ):
        super( ThreadSubscribersModel, self ).__init__( db )


    def get_fields( self ):
        T = current.T
        from m16e.db import db_tables
        db_tables.get_table_model( 'thread', db=self.db )
        self.fields = [ Field( 'thread_id', 'reference thread', ondelete='NO ACTION', notnull=True ),
                        Field( 'auth_user_id', 'reference auth_user', ondelete='NO ACTION', notnull=True ),
                        Field( 'unsubscribed', 'datetime' ),
                        ]
        return self.fields


    def get_validators( self ):
        from m16e.db import db_tables
        db_tables.get_table_model( 'thread', db=self.db )
        self.validators = { 'auth_user_id': IS_IN_DB( self.db, 'auth_user.id', '%(email)s' ),
                            'thread_id': IS_IN_DB( self.db, 'thread.id', '%(title)s' ),
        }
        return self.validators

