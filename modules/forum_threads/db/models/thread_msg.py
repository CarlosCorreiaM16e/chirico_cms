# -*- coding: utf-8 -*-
from app import db_sets
from gluon.dal import Field
from gluon.validators import IS_NULL_OR, IS_IN_DB, IS_IN_SET
from m16e import term
from m16e.db.database import DbBaseTable
from m16e.kommon import DT


class ThreadMsgModel( DbBaseTable ):
    table_name = 'thread_msg'


    def __init__( self, db ):
        super( ThreadMsgModel, self ).__init__( db )


    def get_fields( self ):
        from m16e.db import db_tables
        db_tables.get_table_model( 'thread', db=self.db )
        self.fields = [ Field( 'thread_id', 'reference thread', ondelete='NO ACTION' ),
                        Field( 'parent_thread_msg_id', 'integer' ),
                        Field( 'auth_user_id', 'reference auth_user', ondelete='NO ACTION' ),
                        Field( 'msg_text', 'text', notnull=True ),
                        Field( 'msg_ts', 'datetime', default=DT.now(), notnull=True ),
                        Field( 'markup', 'string', default='H', notnull=True ),
                        ]
        return self.fields


    def get_validators( self ):
        from m16e.db import db_tables
        db_tables.get_table_model( 'thread', db=self.db )
        self.validators = { 'user_id': IS_NULL_OR( IS_IN_DB( self.db, 'auth_user.id', '%(first_name)s' ) ),
                            'thread_id': IS_NULL_OR( IS_IN_DB( self.db, 'thread.id', '%(thread_title)s' ) ),
                            'markup': IS_IN_SET( db_sets.MARKUP_SET ),
                            }
        return self.validators

