# -*- coding: utf-8 -*-
# this file is released under GPL Licence v.3
# author: carlos@memoriapersistente.pt

from gluon import current
from m16e.decorators import deprecated
from m16e.kommon import KDT_BOOLEAN, KDT_INT, KDT_CHAR, KDT_DATE


#------------------------------------------------------------------
def get_value_type_by_data_type_id( db_tables, data_type_id, db=None ):
    if not db:
        db = current.db
    # from m16e.db import db_tables
    dt_model = db_tables.get_table_model( 'data_type', db=db )
    data_type = dt_model[ data_type_id ]
    if data_type.is_boolean:
        return KDT_BOOLEAN
    if data_type.is_integer:
        return KDT_INT
    if data_type.is_text:
        return KDT_CHAR
    if data_type.is_date:
        return KDT_DATE
    return None


#------------------------------------------------------------------
def get_data_type_by_type_name( data_type_name, db=None ):
    if not db:
        db = current.db
    from m16e.db import db_tables
    dt_model = db_tables.get_table_model( 'data_type', db=db )
    q = (db.data_type.dt_name == data_type_name)
    dataType = dt_model.select( q ).first()
    return dataType


# #------------------------------------------------------------------
# @deprecated( 'use get_value_type_by_data_type_id( data_type_id, db=None )')
# def getValueTypeByDataTypeId( db, dataTypeId ):
#     dataType = db.data_type[ dataTypeId ]
#     if dataType.is_boolean:
#         return KDT_BOOLEAN
#     if dataType.is_integer:
#         return KDT_INT
#     if dataType.is_text:
#         return KDT_CHAR
#     if dataType.is_date:
#         return KDT_DATE
#     return None
#
# #------------------------------------------------------------------
# @deprecated( 'use get_data_type_by_type_name( data_type_name, db=None )' )
# def getDataTypeByTypeName( db, dataTypeName ):
#     from m16e.db import db_tables
#     dt_model = db_tables.get_table_model( 'data_type' )
#     q = (db.data_type.dt_name == dataTypeName)
#     dataType = dt_model.select( q ).first()
#     return dataType
#
