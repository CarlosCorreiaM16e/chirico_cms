# -*- coding: utf-8 -*-

from gluon import current
from m16e import term
from gluon.storage import Storage

_db_dict = Storage()


def get_db( db=None ):
    return db or current.db


def get_db_name( db=None ):
    db = get_db( db )
    return db._uri.split( '/' )[ -1 ]


def register_table_list( db, table_list ):
    global _db_dict
    db_name = get_db_name( db )
    if not db_name in _db_dict:
        _db_dict[ db_name ] = []
    for t in table_list:
        if not t in _db_dict[ db_name ]:
            _db_dict[ db_name ].append( t )
    current.table_models[ db_name ] = Storage()


def define_all_tables( db=None ):
    db = get_db( db )
    term.printLog( 'define_all' )
    db_name = get_db_name( db )
    t_list = _db_dict[ db_name ]
    for t in t_list:
        print( t.table_name )
        get_table_model( t.table_name, db=db )


def get_table_model( table_name, db=None ):
    db = get_db( db )
    table_model = None
    db_name = get_db_name( db )
    if db_name in current.table_models:
        dbt_list = current.table_models[ db_name ]
        if table_name in dbt_list:
            table_model = dbt_list[ table_name ]
            # term.printDebug( 'table_model: %s' % repr( table_model ) )

    if not table_model:
        t_list = _db_dict[ db_name ]
        for t in t_list:
            # term.printDebug( 't.table_name: %s' % repr( t.table_name ) )
            if t.table_name == table_name:
                table_model = t( db )
                current.table_models[ db_name ][ table_name ] = table_model
                # term.printDebug( 'table_model: %s' % repr( table_model ) )
    if not table_model:
        term.printError( 'table not found: %s (%s)' % (table_name, db._uri ),
                         print_trace=True )
    return table_model

