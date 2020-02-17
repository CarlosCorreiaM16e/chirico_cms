# -*- coding: utf-8 -*-
from app import db_sets
from gluon import current
from gluon.dal import Field
from gluon.validators import IS_NULL_OR, IS_IN_DB, IS_IN_SET
from m16e import term
from m16e.db.database import DbBaseTable
from m16e.kommon import DATE, DT


class ThreadModel( DbBaseTable ):
    table_name = 'thread'


    def __init__( self, db ):
        super( ThreadModel, self ).__init__( db )


    def get_fields( self ):
        T = current.T
        from m16e.db import db_tables
        db_tables.get_table_model( 'thread_status', db=self.db )
        db_tables.get_table_model( 'thread_type', db=self.db )
        self.fields = [ Field( 'created_on', 'datetime', notnull=True ),
                        Field( 'created_by', 'reference auth_user', ondelete='NO ACTION' ),
                        Field( 'thread_title', 'string', notnull=True ),
                        Field( 'thread_msg', 'text', notnull=True ),
                        Field( 'thread_status_id', 'reference thread_status', ondelete='NO ACTION', default=1, notnull=True ),
                        Field( 'thread_type_id', 'reference thread_type', ondelete='NO ACTION', default=1, notnull=True ),
                        Field( 'markup', 'string', default='M', notnull=True ),
                        Field( 'closed_time', 'datetime' ),
                        ]
        return self.fields


    def get_validators( self ):
        T = current.T
        from m16e.db import db_tables
        db_tables.get_table_model( 'thread_status', db=self.db )
        db_tables.get_table_model( 'thread_type', db=self.db )
        self.validators = { 'created_by': IS_IN_DB( self.db( self.db.auth_user.registration_key == '' ),
                                                    'auth_user.id',
                                                    '%(first_name)s (%(email)s)' ),
                            'thread_status_id': IS_IN_DB( self.db,
                                                           'thread_status.id',
                                                           '%(thread_status_name)s',
                                                           orderby='preferred_order' ),
                            'thread_type_id': IS_IN_DB( self.db,
                                                         'thread_type.id',
                                                         '%(thread_type_name)s',
                                                         orderby='preferred_order' ),
                            'markup': IS_IN_SET( db_sets.MARKUP_SET ),
                            }
        return self.validators

