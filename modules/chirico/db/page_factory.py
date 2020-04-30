# -*- coding: utf-8 -*-
'''
Created on 11/09/2014

@author: carlos
'''
from chirico.db import chirico_events
from m16e.db import db_tables
from gluon.globals import current
from gluon.storage import Storage
from m16e import term, user_factory
from m16e.kommon import DT


NON_PAGE_LIST = [ 'forum',
                  'support',
                  'user' ]

def get_page( page_id=None, url=None, db=None ):
    if not db:
        db = current.db
    p_model = db_tables.get_table_model( 'page', db=db )
    if page_id:
        page = p_model[ page_id ]
    else:
        parts = url.split( '/' )[ 1 : ]
        if parts and parts[0] in NON_PAGE_LIST:
            return Storage( name='[%s]' % parts[0] )

        if parts and not parts[ -1 ]:
            del parts[ -1 ]
        plen = len( parts )
        if not plen:
            q_sql = (p_model.db_table.url_c == 'default')
            q_sql &= (p_model.db_table.url_f == 'index')
        else:
            q_sql = (p_model.db_table.url_c == parts[0])
        if plen > 1:
            q_sql &= (p_model.db_table.url_f == parts[ 1 ])
        if plen > 2:
            q_sql &= (p_model.db_table.url_args == ','.join( parts[ 2 : ] ))
        if plen > 0 and parts[ 0 ] == 'page' and parts[ 1 ] == 'view':
            page = p_model[ parts[ 2 ] ]
        else:
            page = p_model.select( q_sql, print_query=True ).first()
        if not page:
            term.printLog( 'Page not found: %s' % str( url ) )
            page = Storage( name='[%s]' % url )
    return page


def clone( page_id, inc_blocks=True, db=None ):
    if not db:
        db = current.db
    p_model = db_tables.get_table_model( 'page', db=db )
    page = p_model[ page_id ]
    upd_page = {}
    for f in p_model.db_table.fields:
        if not f == 'id':
            upd_page[f] = page[f]
    new_page_id = p_model.insert( upd_page )
    p_model.update_by_id( new_page_id,
                          dict( name=upd_page[ 'name' ] + ' (%d)' % int( new_page_id ) ) )
    if inc_blocks:
        b_model = db_tables.get_table_model( 'block', db=db )
        q_sql = (db.block.page_id == page_id)
        b_list = b_model.select( q_sql, orderby='container, blk_order' )
        for b in b_list:
            upd_block = { f: b[f]
                          for f in b_model.db_table.fields
                          if not f == 'id' }
            upd_block[ 'page_id' ] = new_page_id
            b_model.insert( upd_block )

    return new_page_id


def get_page_children( page_id, db=None ):
    if not db:
        db = current.db
    sql = '''
        select * from page
        where parent_page_id = %(page_id)s
        order by menu_order nulls last
    '''
    args = { 'page_id': page_id }
    rows = db.executesql( sql, placeholders=args, as_dict=True )
    pages = []
    for r in rows:
        pages.append( Storage( r ) )
    return pages


def get_top_pages( db=None ):
    if not db:
        db = current.db
    sql = '''
        select * from page
        where parent_page_id = 0 or parent_page_id is null
        order by menu_order
    '''
    rows = db.executesql( sql, as_dict=True )
    pages = []
    for r in rows:
        pages.append( Storage( r ) )
    return pages


# def add_blocks_to_page( page_id, block_ids, db=None ):
#     if not db:
#         db = current.db
#     pb_model = db_tables.get_table_model( 'page_block', db=db )
#     for b_id in block_ids:
#         pb_model.insert( dict( page_id=page_id,
#                                block_id=b_id ) )


def create_page( upd, db=None ):
    if not db:
        db = current.db
    p_model = db_tables.get_table_model( 'page', db=db )
    ts = DT.now()
    user_id = user_factory.get_auth_user_id( db=db )
    upd.last_modified_by = user_id
    upd.last_modified_on = ts
    upd.created_on = ts
    upd.created_by = user_id
    page_id = p_model.insert( upd )
    chirico_events.store_page_created( page_id, db=db )
    return page_id


def update_page( page_id, upd, db=None ):
    if not db:
        db = current.db
    p_model = db_tables.get_table_model( 'page', db=db )
    ts = DT.now()
    upd.last_modified_by = user_factory.get_auth_user_id( db=db )
    upd.last_modified_on = ts
    p_model.update_by_id( page_id, upd )
    chirico_events.store_page_updated( page_id, db=db )


def get_last_modification_time( page_id, db=None ):
    if not db:
        db = current.db
    p_model = db_tables.get_table_model( 'page', db=db )
    page = p_model[ page_id ]
    last_modification_time = page.page_timestamp
    b_model = db_tables.get_table_model( 'block', db=db )
    q_sql = (db.block.page_id == page_id)
    b_list = b_model.select( q_sql )
    for b in b_list:
        if last_modification_time < b.created_on:
            last_modification_time = b.created_on
        if last_modification_time < b.last_modified_on:
            last_modification_time = b.last_modified_on
    return last_modification_time
