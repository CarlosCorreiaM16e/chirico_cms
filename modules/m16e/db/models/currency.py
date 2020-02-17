# -*- coding: utf-8 -*-

from gluon import current
from gluon.dal import Field
from m16e.db.database import DbBaseTable
from m16e.decorators import deprecated


class CurrencyModel( DbBaseTable ):
    table_name = 'currency'


    def __init__( self, db ):
        super( CurrencyModel, self ).__init__( db )


    def get_fields( self ):
        self.fields = [ Field( 'name', 'string', notnull=True ),
                        Field( 'currency_code_iso_4217', 'string', notnull=True ),
                        Field( 'currency_symbol', 'string', notnull=True ),
                        Field( 'quotation', 'double', default=0.0, notnull=True ),
                        Field( 'preferred_order', 'integer', default=(-1), notnull=True ),
                        Field( 'doc_totals_decimals', 'integer', default=2, notnull=True ),
                        Field( 'currency_mask', 'string', notnull=True ),
        ]
        return self.fields


    def get_validators( self ):
        T = current.T
        self.validators = {}
        return self.validators

