'''
Created on 11/09/2014

@author: carlos
'''
import difflib
import os

from app import db_sets
from chirico.db import chirico_events
from chirico.k import ARCHIVE_FUNCTION, ARCHIVE_CONTROLLER
from gluon import URL
from m16e.db import db_tables
from gluon.globals import current
from gluon.storage import Storage
from m16e import term, user_factory, markmin_factory
from m16e.kommon import DT, NAV_DIR_PREV, NAV_DIR_NEXT
from m16e.ui import elements


def get_page_blocks( page_id=None, block_id=None, db=None ):
    if not db:
        db = current.db
    b_model = db_tables.get_table_model( 'block', db=db )
    if page_id:
        q_sql = (db.block.page_id == page_id)
    elif block_id:
        b = b_model[ block_id ]
        q_sql = (db.block.page_id == b.page_id)
    else:
        return []
    b_list = b_model.select( q_sql, orderby='container desc, blk_order' )
    return b_list

    # if page_id:
    #     sql = '''
    #         select *
    #         from block
    #         where page_id = %(page_id)s
    #     ''' % dict( page_id=page_id )
    # elif block_id:
    #     sql = '''
    #         select
    #             pb.*,
    #             p.name
    #         from page_block pb
    #             join page p on pb.page_id = p.id
    #         where pb.block_id = %(block_id)s
    #     ''' % dict( block_id=block_id )
    # else:
    #     raise AttributeError( 'Must supply a page or a block' )
    # rows = []
    # for r in db.executesql( sql, as_dict=True ):
    #     for container in db_sets.BLOCK_CONTAINER_SET:
    #         if container[0] == r[ 'container' ]:
    #             r[ 'container_name' ] = container[1]
    #             break
    #     rows.append( Storage( r ) )
    # return rows


def purge( block_id, db=None ):
    if not db:
        db = current.db
    b_model = db_tables.get_table_model( 'block', db=db )
    # # bh_model = db_tables.get_table_model( 'block_history', db=db )
    # pb_model = db_tables.get_table_model( 'page_block', db=db )
    # pb_model.delete( (db.page_block.block_id == block_id) )
    # # bh_model.delete( (db.block_history.block_id == block_id) )
    b_model.delete( (db.block.id == block_id) )


def clone( block_id, db=None ):
    if not db:
        db = current.db
    session = current.session
    auth = session.auth
    b_model = db_tables.get_table_model( 'block', db=db )
    block = b_model[ block_id ]
    upd = {}
    for f in db.block.fields:
        if not f == 'id':
            upd[f] = block[f]
    upd[ 'created_on' ] = DT.now()
    upd[ 'created_by' ] = auth.user.id
    new_block = b_model.insert( upd )
    return new_block


def create_page_from_block( block_id, post_vars, db=None ):
    if not db:
        db = current.db
    session = current.session
    auth = session.auth
    T = current.T

    title = post_vars.title
    tag_name = post_vars.p_tagname or ''
    css_class = post_vars.pb_css_class or 'main_panel'
    description = post_vars.title
    term.printDebug( 'title: ' + repr( title ) )
    term.printDebug( 'tag_name: ' + repr( tag_name ) )
    term.printDebug( 'css_class: ' + repr( css_class ) )
    term.printDebug( 'description: ' + repr( description ) )
    page_id = None
    if not title or not description:
        fields = []
        term.printLog( 'empty fields' )
        if not title:
            fields.append( str( T( 'Title' ) ) )
        if not description:
            fields.append( str( T( 'Description' ) ) )
        msg = ', '.join( fields )
        msg += str( T( ' must not be empty' ) )
    else:
        term.printLog( 'creating page...' )
        b_model = db_tables.get_table_model( 'block', db=db )
        p_model = db_tables.get_table_model( 'page', db=db )
        page_id = p_model.insert( dict( tagname=tag_name,
                                        url_c='page',
                                        url_f='view',
                                        title=title,
                                        name=title,
                                        colspan=1,
                                        rowspan=1,
                                        last_modified_by=auth.user.id,
                                        aside_position=db_sets.PANEL_RIGHT,
                                        main_panel_cols=1,
                                        aside_panel_cols=0 ) )
        p_model.update_by_id( page_id, dict( url_args=str( page_id ) ) )
        term.printLog( 'created page: ' + repr( page_id ) )
        b_model.update_by_id( block_id, dict( page_id=page_id ) )
        msg = T( 'Page created' )

    return page_id, msg


def get_articles( article_type='M', order='created_on', limit=None, db=None ):
    if not db:
        db = current.db
    sql = '''
        select b.*
            from block b
                join category c on b.category_id = c.id'''
    if article_type:
        sql += '''
            where category_type = '%(t)s' '''  % dict( t=article_type )
    sql += '''
            order by ''' + order
    if limit:
        sql += '''
            limit ''' + str( limit )
    rows = db.executesql( sql, as_dict=True )
    a_list = []
    for r in rows:
        a_list.append( Storage( r ) )
    return a_list


def get_blocks_with_image( url, db=None ):
    if not db:
        db = current.db
    b_model = db_tables.get_table_model( 'block', db=db )
    q_sql = (db.block.body.like( '%' + str( url ) + '%' ))
    q_sql |= (db.block.body_en.like( '%' + str( url ) + '%' ))
    rows = b_model.select( q_sql, distinct=True, print_query=True )
    return rows


# def create_block( name, body, body_markup=None, db=None ):
#     if not db:
#         db = current.db
#     auth = current.auth
#     b_model = db_tables.get_table_model( 'block', db=db )
#     data = Storage( name=name,
#                     body=body,
#                     created_by=auth.user_id,
#                     last_modified_by=auth.user_id,
#                     body_markup=body_markup or db_sets.MARKUP_HTML )
#     return b_model.insert( data )


def create_block( upd, db=None ):
    if not db:
        db = current.db
    b_model = db_tables.get_table_model( 'block', db=db )
    ts = DT.now()
    user_id = user_factory.get_auth_user_id( db=db )
    upd = Storage( upd )
    upd.last_modified_by = user_id
    upd.last_modified_on = ts
    upd.created_on = ts
    upd.created_by = user_id
    if not upd.body_markup:
        upd.body_markup = db_sets.MARKUP_MARKMIN
    block_id = b_model.insert( upd )
    chirico_events.store_block_created( block_id, db=db )
    return block_id


def update_block( block_id, upd, db=None ):
    if not db:
        db = current.db
    upd = Storage( upd )
    b_model = db_tables.get_table_model( 'block', db=db )
    b = b_model[ block_id ]
    ts = DT.now()
    log_data = Storage()
    if 'body' in upd:
        log_data.old_body = b.body
        udiff = difflib.unified_diff( b.body.splitlines(),
                                      upd.body.splitlines(),
                                      'old',
                                      'new' )
        log_data.diff_body = '\n'.join( [ l for l in udiff ] )
    else:
        log_data.old_body = ''
        log_data.diff_body = ''

    if 'body_en' in upd:
        log_data.old_body_en = b.body_en
        udiff = difflib.unified_diff( b.body_en.splitlines(),
                                      upd.body_en.splitlines(),
                                      'old',
                                      'new' )
        log_data.diff_body_en = '\n'.join( [ l for l in udiff ] )
    else:
        log_data.old_body_en = ''
        log_data.diff_body_en = ''

    if log_data:
        log_data.block_id = block_id
        log_data.auth_user_id = user_factory.get_auth_user_id( db=db )
        log_data.ts = ts
        bl_model = db_tables.get_table_model( 'block_log', db=db )
        bl_model.insert( log_data )
    upd = Storage( upd )
    upd.last_modified_by = user_factory.get_auth_user_id( db=db )
    upd.last_modified_on = ts
    b_model.update_by_id( block_id, upd )
    chirico_events.store_block_updated( block_id, db=db )
    b = b_model[ block_id ]
    # append  or delete image to/from block_attach
    b_img_ids = markmin_factory.get_text_images_id( b.body )
    for i in markmin_factory.get_text_images_id( b.body_en ):
        if i not in b_img_ids:
            b_img_ids.append( i )
    ba_model = db_tables.get_table_model( 'block_attach', db=db )
    q_sql = (db.block_attach.block_id == block_id)
    ba_list = ba_model.select( q_sql )
    for ba in ba_list:
        if ba.attach_id not in b_img_ids:
            ba_model.delete_by_id( ba.id )
    if b_img_ids:
        for i in b_img_ids:
            q_sql = (db.block_attach.block_id == block_id)
            q_sql &= (db.block_attach.attach_id == i)
            ba = ba_model.select( q_sql ).first()
            if not ba:
                ba_model.insert( dict( attach_id=i,
                                       block_id=block_id ) )


def create_slot_before( block, db=None ):
    if not db:
        db = current.db
    block = Storage( block )
    sql = '''
        update block
            set blk_order = blk_order + 1
    where 
        page_id = %(page_id)s and
        container = '%(container)s' and
        blk_order >= %(blk_order)s
    ''' % dict( page_id=block.page_id,
                blk_order=block.blk_order,
                container=block.container )
    db.executesql( sql )


def get_nav_block_in_page( block, nav_dir, db=None ):
    if nav_dir not in (NAV_DIR_PREV, NAV_DIR_NEXT):
        raise AttributeError( 'Wrong nav_dir: %s' % str( nav_dir ) )

    if not db:
        db = current.db
    b_model = db_tables.get_table_model( 'block', db=db )
    q_sql = (db.block.page_id == block.page_id)
    if nav_dir == NAV_DIR_PREV:
        q_sql &= (db.block.blk_order < block.blk_order)
        orderby = 'blk_order desc'
    else:
        q_sql &= (db.block.blk_order > block.blk_order)
        orderby = 'blk_order'
    b = b_model.select( q_sql, orderby=orderby ).first()
    return b


def get_link_to_block_in_page( block, nav_dir, function_name='composer', db=None ):
    if nav_dir not in (NAV_DIR_PREV, NAV_DIR_NEXT):
        raise AttributeError( 'Wrong nav_dir: %s' % str( nav_dir ) )

    if not db:
        db = current.db
    T = current.T
    b = get_nav_block_in_page( block, nav_dir, db=db )
    nav_block = ''
    if b:
        if nav_dir == NAV_DIR_PREV:
            tip = T( 'Go to previous block' )
            icon = elements.ICON_NAV_PREV
            text_before_icon = False
        else:
            tip = T( 'Go to next block' )
            icon = elements.ICON_NAV_NEXT
            text_before_icon = True
        nav_block = elements.get_link_icon( icon,
                                            url=URL( c='block',
                                                     f=function_name,
                                                     args=b.id ),
                                            bt_text=b.name,
                                            text_before_icon=text_before_icon,
                                            dark_background=False,
                                            tip=tip )
    return nav_block
