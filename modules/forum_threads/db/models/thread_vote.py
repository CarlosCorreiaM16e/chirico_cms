# -*- coding: utf-8 -*-
from app import db_sets
from gluon.dal import Field
from gluon.validators import IS_IN_DB, IS_IN_SET
from m16e import term
from m16e.db.database import DbBaseTable
from m16e.kommon import DT


class ThreadVoteModel( DbBaseTable ):
    table_name = 'thread_vote'


    def __init__( self, db ):
        super( ThreadVoteModel, self ).__init__( db )


    def get_fields( self ):
        from m16e.db import db_tables
        db_tables.get_table_model( 'thread', db=self.db )
        db_tables.get_table_model( 'thread_msg', db=self.db )
        self.fields = [ Field( 'thread_id', 'reference thread', ondelete='NO ACTION', notnull=True ),
                        Field( 'thread_msg_id', 'reference thread_msg', ondelete='NO ACTION', notnull=True ),
                        Field( 'auth_user_id', 'reference auth_user', ondelete='NO ACTION', notnull=True ),
                        Field( 'vote_ts', 'datetime', default=DT.now(), notnull=True ),
                        Field( 'vote', 'integer', notnull=True )
                        ]
        return self.fields


    def get_validators( self ):
        from m16e.db import db_tables
        db_tables.get_table_model( 'thread', db=self.db )
        db_tables.get_table_model( 'thread_msg', db=self.db )
        self.validators = { 'auth_user_id': IS_IN_DB( self.db, 'auth_user.id', '%(first_name)s (%(email)s)' ),
                            'thread_id': IS_IN_DB( self.db, 'thread.id', '%(thread_title)s' ),
                            'thread_msg_id': IS_IN_DB( self.db, 'thread_msg.id', '%(msg_ts)s' ),
                            'vote': IS_IN_SET( db_sets.VOTE_SET )
                            }
        return self.validators

