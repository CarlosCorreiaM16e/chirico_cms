# -*- coding: utf-8 -*-


from gluon.dal import Field
from gluon.validators import IS_NULL_OR, IS_IN_DB
from m16e.db.database import DbBaseTable
from m16e.kommon import DT


class AttachModel( DbBaseTable ):
    table_name = 'attach'


    def __init__( self, db ):
        super( AttachModel, self ).__init__( db )


    def get_fields( self ):
        from m16e.db import db_tables
        db_tables.get_table_model( 'mime_type', db=self.db )
        db_tables.get_table_model( 'unit_type', db=self.db )
        db_tables.get_table_model( 'attach_type', db=self.db )
        self.fields = [ Field( 'path', 'string' ),
                        Field( 'filename', 'string' ),
                        Field( 'short_description', 'string' ),
                        Field( 'long_description', 'text' ),
                        Field( 'attached', 'upload', uploadfield='attached_file' ),
                        Field( 'attached_file', 'blob' ),
                        Field( 'created_on', 'datetime', default=DT.now(), notnull=True ),
                        Field( 'created_by', 'reference auth_user' ),
                        Field( 'unit_type_id', 'reference unit_type', ondelete='NO ACTION' ),
                        Field( 'mime_type_id', 'reference mime_type', ondelete='NO ACTION' ),
                        Field( 'is_site_image', 'boolean', default=False, notnull=True ),
                        Field( 'img_width', 'integer' ),
                        Field( 'img_height', 'integer' ),
                        Field( 'attach_type_id', 'reference attach_type' ),
                        Field( 'org_attach_id', 'reference attach' ),
        ]
        return self.fields


    def get_validators( self ):
        from m16e.db import db_tables
        db = self.db
        db_tables.get_table_model( 'mime_type', db=self.db )
        db_tables.get_table_model( 'unit_type', db=self.db )
        db_tables.get_table_model( 'attach_type', db=self.db )
        self.validators = { 'mime_type_id': IS_NULL_OR( IS_IN_DB( db,
                                                        'mime_type.id',
                                                        '%(mt_name)s' ) ),
                            'created_by': IS_NULL_OR( IS_IN_DB( db,
                                                      'auth_user.id',
                                                      '%(first_name)s (%(email)s)' ) ),
                            'unit_type_id': IS_NULL_OR( IS_IN_DB( db,
                                                        'unit_type.id',
                                                        '%(name)s' ) ),
                            'attach_type_id': IS_IN_DB( db,
                                                        'attach_type.id',
                                                        'attach_type.name',
                                                        zero=None ),
                            'org_attach_id': IS_NULL_OR( IS_IN_DB( db( db.attach.org_attach_id == None ),
                                                                   'attach.id',
                                                                   'attach.filename' ) )
        }
        return self.validators

