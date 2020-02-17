# -*- coding: utf-8 -*-

from gluon import current, Field
from gluon.validators import IS_NULL_OR, IS_IN_DB
from m16e.db.database import DbBaseTable


#----------------------------------------------------------------------
class AppConfigModel( DbBaseTable ):
    table_name = 'app_config'

    #----------------------------------------------------------------------
    def __init__( self, db ):
        super( AppConfigModel, self ).__init__( db )


    #----------------------------------------------------------------------
    def get_fields( self ):
        T = current.T
        from m16e.db import db_tables
        db_tables.get_table_model( 'app_theme', db=self.db )
        db_tables.get_table_model( 'country', db=self.db )
        self.fields = [ Field( 'qt_decimals', 'integer', default=2, notnull=True ),
                        Field( 'currency_decimals', 'integer', default=2, notnull=True ),
                        Field( 'server_timezone', 'string', default='UTC', notnull=True ),
                        Field( 'client_timezone', 'string', default='UTC', notnull=True ),
                        Field( 'app_theme_id', 'reference app_theme', ondelete='NO ACTION', default=1, notnull=True ),
                        Field( 'flash_msg_delay', 'integer', default=3000, notnull=True ),
                        Field( 'max_img_page_width', 'integer' ),
                        Field( 'max_img_block_width', 'integer' ),
                        Field( 'max_img_thumb_width', 'integer' ),
                        ]
        return self.fields


    #----------------------------------------------------------------------
    def get_validators( self ):
        T = current.T
        from m16e.db import db_tables
        db_tables.get_table_model( 'app_theme', db=self.db )
        db_tables.get_table_model( 'country', db=self.db )
        db_tables.get_table_model( 'currency', db=self.db )
        db_tables.get_table_model( 'tax_exempt_type', db=self.db )
        db_tables.get_table_model( 'tax_zone', db=self.db )
        self.validators = { 'app_theme_id': IS_IN_DB( self.db, 'app_theme.id', '%(name)s' ),
                            'default_country_id': IS_IN_DB( self.db,
                                                            'country.id',
                                                            '%(name)s',
                                                            orderby='preferred_order' ),
                            'default_currency_id': IS_IN_DB( self.db, 'currency.id', '%(name)s' ),
                            # 'tax_exempt_type_id': IS_NULL_OR( IS_IN_DB( self.db, 'tax_exempt_type.id', '%(name)s' ) ),
                            # 'tax_zone_id': IS_NULL_OR( IS_IN_DB( self.db, 'tax_zone.id', '%(name)s' ) ),
        }
        return self.validators
    #----------------------------------------------------------------------

