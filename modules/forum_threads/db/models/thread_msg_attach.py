# -*- coding: utf-8 -*-

from gluon.dal import Field
from gluon.validators import IS_NULL_OR, IS_IN_DB, IS_IN_SET
from m16e import term
from m16e.db.database import DbBaseTable


class ThreadMsgAttachModel( DbBaseTable ):
    table_name = 'thread_msg_attach'


    def __init__( self, db ):
        super( ThreadMsgAttachModel, self ).__init__( db )


    def get_fields( self ):
        from m16e.db import db_tables
        db_tables.get_table_model( 'attach', db=self.db )
        db_tables.get_table_model( 'thread_msg', db=self.db )
        self.fields = [ Field( 'attach_id', 'reference attach', ondelete='NO ACTION' ),
                        Field( 'thread_msg_id', 'reference thread_msg', ondelete='NO ACTION' ),
                        ]
        return self.fields


    def get_validators( self ):
        from m16e.db import db_tables
        db_tables.get_table_model( 'attach', db=self.db )
        db_tables.get_table_model( 'thread_msg', db=self.db )
        self.validators = { 'attach_id': IS_NULL_OR( IS_IN_DB( self.db, 'attach.id', '%(id)s' ) ),
                            'thread_msg_id': IS_NULL_OR( IS_IN_DB( self.db, 'thread_msg.id', '%(id)s' ) ),
                            }
        return self.validators
