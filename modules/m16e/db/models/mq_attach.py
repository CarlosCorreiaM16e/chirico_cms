# -*- coding: utf-8 -*-

from gluon.dal import Field
from gluon.validators import IS_IN_DB
from m16e.db.database import DbBaseTable


#------------------------------------------------------------------
class MqAttachModel( DbBaseTable ):
    table_name = 'mq_attach'

    #------------------------------------------------------------------
    def __init__( self, db ):
        super( MqAttachModel, self ).__init__( db )

    #------------------------------------------------------------------
    def get_fields( self ):
        from m16e.db import db_tables
        db_tables.get_table_model( 'attach', db=self.db )
        db_tables.get_table_model( 'mail_queue', db=self.db )
        self.fields = [ Field( 'mail_queue_id', 'reference mail_queue' ),
                        Field( 'attach_id', 'reference attach' ),
                        ]
        return self.fields

    #------------------------------------------------------------------
    def get_validators( self ):
        from m16e.db import db_tables
        db_tables.get_table_model( 'attach', db=self.db )
        db_tables.get_table_model( 'mail_queue', db=self.db )
        self.validators = { 'mail_queue_id': IS_IN_DB( self.db, 'mail_queue.id', '%(subject)s [%(id)s]', zero=None ),
                            'attach_id': IS_IN_DB( self.db, 'attach.id', '%(filename)s', zero=None ),
                            }
        return self.validators

