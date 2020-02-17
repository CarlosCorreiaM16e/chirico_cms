# -*- coding: utf-8 -*-
from belmiro.app.k import CFG_IMG_SIZE_SMALL
from gluon import current, DIV, H1, IMG, URL, A
from gluon.storage import Storage
from m16e import term
from m16e.db import attach_factory
from m16e.kommon import KQV_OFFSET, KQV_NEXT_C, KQV_NEXT_F
from m16e.ui import elements


def get_image_list( offset=0,
                    cols=6,
                    rows=2,
                    url_c=None,
                    url_f=None,
                    db=None ):
    if not db:
        db = current.db
    if not url_c:
        url_c = 'gallery'
    if not url_f:
        url_f = 'edit'
    T = current.T
    col_class = 'col-md-%d' % (12 / cols)
    sql = '''
        select count( * )
        from attach a
            join attach_type at on at.id = a.attach_type_id
        where
            at.meta_name in ( 'company-logo', 'images', 'webshop' )
    '''
    records = db.executesql( sql )
    rec_count = records[0][0]
    sql = '''
        select
            a.*,
            at.meta_name
        from attach a
            join attach_type at on at.id = a.attach_type_id
        where
            at.meta_name in ( 'company-logo', 'images', 'webshop' )
        order by a.path, a.filename
        offset %(ofs)s limit %(lim)s
    ''' % dict( ofs=offset,
                lim=cols * rows )
    records = db.executesql( sql, as_dict=True )
    content_panel = DIV( _class='col-md-12' )
    content_panel.append( H1( T( 'Image gallery' ) ) )
    content_panel.append( DIV( DIV( T( 'Image count' ),
                                    ': ',
                                    str( rec_count ),
                                    _class='col-md-6' ),
                               DIV( A( 'Add image',
                                       _href=URL( c='gallery',
                                                  f='edit',
                                                  args=[0] ),
                                       _class='btn btn-success' ),
                                    _class='col-md-6 text-right' ),
                               _class='row' ) )
    idx_limit = len( records )
    for row in range( rows ):
        row_panel = DIV( _class='row' )
        for col in range( cols ):
            idx = cols * row + col
            if idx >= idx_limit:
                break
            record = Storage( records[ idx ] )
            width = current.app_config.take( CFG_IMG_SIZE_SMALL )
            row_panel.append( DIV( A( IMG( _src=URL( c='default',
                                                      f='download',
                                                      args=[ record.attached ] ),
                                           _width=int( width ) ),
                                      DIV( record.filename ),
                                      DIV( '(%(w)sx%(h)s)' % dict( w=record.img_width, h=record.img_height) ),
                                      _href=URL( c= url_c, f=url_f, args=[ record.id ],
                                                 vars={ KQV_NEXT_C: 'gallery',
                                                        KQV_NEXT_F: 'list_images' } ) ),
                                   _class=col_class + ' text-center') )
        content_panel.append( row_panel )
    outer_div = DIV( content_panel, _class='row' )
    nav_panel = DIV( _class='row' )
    nav_prev = ''
    if offset > 0:
        ofs = offset - (cols * rows)
        if ofs < 0:
            ofs = 0
        nav_prev = elements.get_link_icon( elements.ICON_CHEVRON_LEFT,
                                           URL( c='gallery', f='list_images', vars={ KQV_OFFSET: ofs } ) )
    nav_panel.append( DIV( nav_prev, _class='col-md-6' ) )
    nav_next = ''
    ofs = offset + (cols * rows)
    if ofs < rec_count:
        nav_next = elements.get_link_icon( elements.ICON_CHEVRON_RIGHT,
                                           URL( c='gallery', f='list_images', vars={ KQV_OFFSET: ofs } ) )
    nav_panel.append( DIV( nav_next, _class='col-md-6 text-right' ) )
    outer_div.append( nav_panel )
    return outer_div


def get_image_list_comps( offset=0,
                          limit=100,
                          url_c=None,
                          url_f=None,
                          db=None ):
    if not db:
        db = current.db
    if not url_c:
        url_c = 'gallery'
    if not url_f:
        url_f = 'edit'
    T = current.T
    sql = '''
        select count( * )
        from attach a
            join attach_type at on at.id = a.attach_type_id
        where
            at.meta_name in ( 'company-logo', 'images', 'webshop' )
    '''
    records = db.executesql( sql )
    data = Storage()
    data.rec_count = records[0][0]
    sql = '''
        select
            a.*,
            at.meta_name
        from attach a
            join attach_type at on at.id = a.attach_type_id
        where
            at.meta_name in ( 'company-logo', 'images', 'webshop' )
        order by a.path, a.filename
        offset %(ofs)s limit %(lim)s
    ''' % dict( ofs=offset,
                lim=limit )
    term.printDebug( 'sql: %s' % sql )
    data.records = []
    rows = db.executesql( sql, as_dict=True )
    for row in rows:
        r = Storage( row )
        r.is_file_in_static = attach_factory.is_file_in_static( r.id, db=db )
        data.records.append( r )

    term.printDebug( 'len( records ): %d' % len( data.records ) )
    data.nav_prev = ''
    if offset > 0:
        ofs = offset - limit
        if ofs < 0:
            ofs = 0
        data.nav_prev = elements.get_link_icon( elements.ICON_CHEVRON_LEFT,
                                                URL( c='gallery', f='list_images', vars={ KQV_OFFSET: ofs } ) )
    data.nav_next = ''
    ofs = offset + limit
    if ofs < data.rec_count:
        data.nav_next = elements.get_link_icon( elements.ICON_CHEVRON_RIGHT,
                                                URL( c='gallery', f='list_images', vars={ KQV_OFFSET: ofs } ) )
    return data
