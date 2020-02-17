# -*- coding: utf-8 -*-

import Image
import StringIO
import magic
import os
import shutil
import sys
import tempfile
from gluon import current, URL
from gluon.storage import Storage
from m16e import term, user_factory
from m16e.db import db_tables
from m16e.files import fileutils, media
from m16e.kommon import DT

THUMBS_EXT = [
    'bmp',
    'gif',
    'jpeg',
    'jpg',
    'pcx',
    'pbm',
    'pgm',
    'png',
    'ppm',
    'tiff',
    'tif',
    'xbm',
    'xmp'
]

WIDTH_MARGIN = 1.3


def rebuild_mime_types( db=None ):
    if not db:
        db = current.db
    a_model = db_tables.get_table_model( 'attach', db=db )
    mte_model = db_tables.get_table_model( 'mime_type_ext', db=db )
    
    a_list = a_model.select()
    for a in a_list:
        term.printLog( 'id: %d; filename: %s' % (a.id, a.filename) )
        filename = a.filename
        ext = filename.split( '.' )[-1]
        q_sql = (db.mime_type_ext.extension == ext)
        mte = mte_model.select( q_sql ).first()
        if mte:
            term.printLog( 'mte: %s' % (repr( mte ) ) )
            if a.mime_type_id != mte.mime_type_id:
                db( db.attach.id == a.id ).update( mime_type_id=mte.mime_type_id )


def is_image( attach, db=None ):
    if not db:
        db = current.db
    mt_model = db_tables.get_table_model( 'mime_type', db=db )
    mt = mt_model[ attach.mime_type_id ]
    ret = mt.mt_name.startswith( 'image/' )
    return ret


def is_file_in_static( attach_id, db=None ):
    if not db:
        db = current.db
    a_model = db_tables.get_table_model( 'attach', db=db )
    request = current.request
    attach = a_model[ attach_id ]
    if not attach:
        raise Exception( 'Failed to find attach #%s' % repr( attach_id ) )

#     term.printDebug( 'attach: %s' % ( attach.filename ) )

    path = get_abs_path_from_server( attach )

    # filename = os.path.join( 'images',
    #                          path,
    #                          attach.filename )
    filename = os.path.join( path,
                             attach.filename )
    # term.printDebug( 'filename: %s' % ( filename ) )
    if os.path.isfile( filename ):
        # term.printDebug( 'filename: %s' % ( filename ) )
        return filename
    return None

def get_attach_pathname( attach_id, dump_folder='images', db=None ):
    if not db:
        db = current.db
    request = current.request
    a_model = db_tables.get_table_model( 'attach', db=db )
    attach = a_model[ attach_id ]
    # term.printDebug( 'attach: %s' % ( attach.filename ) )
    path = get_rel_path_from_server_app( attach )
    pathname = os.path.join( path,
                             attach.filename )
    return pathname


def rename_static_file( attach_id,
                        new_path=None,
                        new_filename=None,
                        db=None ):
    if not db:
        db = current.db
    old_filename = file_dump( attach_id, db=db )
    load_file( old_filename,
               path=new_path,
               filename=new_filename,
               attach_id=attach_id,
               db=db )
    os.unlink( old_filename )
    # pathname = get_rel_path_from_server( attach_id=attach_id, db=db )
    # # if old_pathname:
    # #     old_path, old_filename = old_pathname.rsplit( '/', 1 )
    # #     old_path = os.path.join( pathname, old_path )
    # # else:
    # #     old_path = os.path.join( pathname, old_path )
    # #     old_pathname = os.path.join( old_path, old_filename )
    # # if new_pathname:
    # #     new_path, new_filename = new_pathname.rsplit( '/', 1 )
    # #     new_path = os.path.join( pathname, new_path )
    # # else:
    # #     new_path = os.path.join( pathname, new_path )
    # #     new_pathname = os.path.join( new_path, new_filename )
    # #
    # # fileutils.move_file( old_pathname, new_pathname )
    #
    # a_model = db_tables.get_table_model( 'attach', db=db )
    # attach = a_model[ attach_id ]
    # data = Storage()
    # if new_path != attach.path:
    #     data.path = new_path[ len( pathname ) + 1 : ]
    # if new_filename != old_filename:
    #     data.filename = new_filename
    # a_model.update_by_id( attach_id, data )


def rename_static_file2( attach_id,
                        old_path=None,
                        old_filename=None,
                        old_pathname=None,
                        new_path=None,
                        new_filename=None,
                        new_pathname=None,
                        db=None ):
    if not db:
        db = current.db
    pathname = get_rel_path_from_server_app( attach_id=attach_id, db=db )
    if old_pathname:
        old_path, old_filename = old_pathname.rsplit( '/', 1 )
        old_path = os.path.join( pathname, old_path )
    else:
        old_path = os.path.join( pathname, old_path )
        old_pathname = os.path.join( old_path, old_filename )
    if new_pathname:
        new_path, new_filename = new_pathname.rsplit( '/', 1 )
        new_path = os.path.join( pathname, new_path )
    else:
        new_path = os.path.join( pathname, new_path )
        new_pathname = os.path.join( new_path, new_filename )
    file_dump_to_static( attach_id, db=db )
    fileutils.move_file( old_pathname, new_pathname )

    a_model = db_tables.get_table_model( 'attach', db=db )
    data = Storage()
    if new_path != old_path:
        data.path = new_path[ len( pathname ) + 1 : ]
    if new_filename != old_filename:
        data.filename = new_filename
    a_model.update_by_id( attach_id, data )


def delete_attach( attach_id, purge_static=True, db=None ):
    if not db:
        db = current.db
    a_model = db_tables.get_table_model( 'attach', db=db )
    if purge_static:
        delete_from_static( attach_id, db=db )
    a_model.delete_by_id( attach_id )


#------------------------------------------------------------------
def delete_from_static( attach_id, db=None ):
    if not db:
        db = current.db
    a_model = db_tables.get_table_model( 'attach', db=db )
    request = current.request
    attach = a_model[ attach_id ]
    # term.printDebug( 'attach: %s' % ( attach.filename ) )

    path = get_rel_path_from_server_app( attach )

    filename = os.path.join( request.folder,
                             'static',
                             'images',
                             path,
                             attach.filename )
    # term.printDebug( 'filename: %s' % ( filename ) )
    if os.path.isfile( filename ):
        os.remove( filename )

#------------------------------------------------------------------
def copy_image( auth_user_id,
                attach_id,
                new_attach_filename=None,
                new_attach_path=None,
                new_width=None,
                new_height=None,
                new_short_description=None,
                prefix='',
                insert_dim_in_name=False,
                dump_to_static=False,
                db=None ):
    if not db:
        db = current.db
    a_model = db_tables.get_table_model( 'attach', db=db )
    attach = a_model[ attach_id ]
    parts = attach.filename.rsplit( '.', 1 )
    ext = '.%s' % parts[1]
    # term.printDebug( 'attach.filename: %s' % repr( attach.filename ) )
    # term.printDebug( 'parts: %s' % repr( parts ) )
#         term.printDebug( 'attach: %s' % repr( attach ) )
    img_path = file_dump( attach_id, tmp=True, db=db )
    # term.printDebug( 'img_path: %s' % repr( img_path ) )
    img = Image.open( img_path )
    attach.update_record( img_width=img.size[ 0 ],
                          img_height=img.size[ 1 ] )

#         term.printDebug( 'attach: %s' % repr( attach ) )
    h = new_height
    w = new_width
    ratio = 1.0
    if new_width:
        ratio = float(new_width / float( img.size[0] ) )
        h = int( (float( img.size[1]) * ratio ) )
    elif new_height:
        ratio = new_height / float( img.size[1] )
        w = int( (float( img.size[0]) * ratio ) )
    if ratio < 1.0:
        thumb = img.resize( (w, h), Image.ANTIALIAS )
    else:
        thumb = img
    
    if not new_attach_filename:
        new_attach_filename = ''
        if prefix:
            new_attach_filename = prefix
        new_attach_filename += parts[0]
        if insert_dim_in_name:
            new_attach_filename += '-%dx%d' % ( w, h )
        new_attach_filename += '.' + parts[1]
    if not new_short_description:
        new_short_description = attach.short_description
    fd, thumb_path = tempfile.mkstemp( suffix=ext )
    f = os.fdopen( fd )
    f.close()
    # term.printDebug( 'thumb_path: %s' % repr( thumb_path ) )
    thumb.save( thumb_path )
    # term.printDebug( 'thumb_path: %s' % repr( thumb_path ) )
    if not new_attach_path:
        new_attach_path = attach.path
    # term.printDebug( 'thumb_path: %s' % repr( thumb_path ) )
    new_id = load_file( thumb_path,
                        path=new_attach_path,
                        filename=new_attach_filename,
                        created_on=DT.now(),
                        created_by=auth_user_id,
                        unit_type_id=attach.unit_type_id,
                        mime_type_id=attach.mime_type_id,
                        attach_type_id=attach.attach_type_id,
                        is_site_image=attach.is_site_image,
                        img_width=w,
                        img_height=h,
                        org_attach_id=attach_id,
                        short_description=new_short_description,
                        db=db )
    if dump_to_static:
        file_dump_to_static( new_id, db=db )
    os.remove( img_path )
    os.remove( thumb_path )
    
    # term.printDebug( 'new_id: %s' % repr( new_id ) )
    return new_id


def load_file( file_to_load,
               path=None,
               filename=None,
               created_on=DT.now(),
               created_by=None,
               unit_type_id=None,
               mime_type_id=None,
               attach_type_id=None,
               is_site_image=False,
               img_width=None,
               img_height=None,
               org_attach_id=None,
               attach_id=None,
               short_description=None,
               db=None ):
    # term.printDebug( 'loading: %s' % file_to_load )
    if not db:
        db = current.db
    auth = current.auth
    a_model = db_tables.get_table_model( 'attach', db=db )
    stream = open( file_to_load, 'rb' )
    if attach_id:
        attach = a_model[ attach_id ]
        filename = filename or attach.filename
        path = path or attach.path
        d = dict( path=path,
                  filename=filename,
                  short_description=short_description,
                  attached=db.attach.attached.store( stream,
                                                     filename ),
                  attached_file=stream.read() )
        a_model.update_by_id( attach_id, d )
        return attach_id

    if not created_by:
        created_by = auth.user.id
    if not mime_type_id:
        mime_type_id = get_mime_type_id_from_name( filename )
    if not mime_type_id:
        mime_type_id = get_mime_type_id_from_file( filename )
    d = dict( path=path,
              filename=filename,
              attached=db.attach.attached.store( stream,
                                                 filename ),
              attached_file=stream.read(),
              created_on=created_on,
              created_by=created_by,
              unit_type_id=unit_type_id,
              mime_type_id=mime_type_id,
              attach_type_id=attach_type_id,
              is_site_image=is_site_image,
              img_width=img_width,
              img_height=img_height,
              org_attach_id=org_attach_id,
              short_description=short_description )
    q_sql = (db.attach.filename == filename)
    a = a_model.select( q_sql ).first()
    if a:
        a_model.update_by_id( a.id, d )
        new_id = a.id
    else:
        new_id = a_model.insert( d )
#     term.printDebug( 'new_id: %s' % repr( new_id ) )
    return new_id


#------------------------------------------------------------------
# def clone( attach_id, filename=None, path=None, db=None ):
#     if not db:
#         db = current.db
#     a_model = db_tables.get_table_model( 'attach', db=db )
#     attach = a_model[ attach_id ]
#     if not filename:
#         filename = attach.filename
#         f_parts = filename.rsplit( '.', 1 )
#         filename = f_parts[0] + ('-clone-%d.' % attach_id) + f_parts[1]
#     if not path:
#         path = attach.path
#     # term.printDebug( 'filename: %s' % filename )
#     new_attach_id = db.attach.insert( attach_type_id=attach.attach_type_id,
#                                       path=path,
#                                       filename=filename,
#                                       short_description=attach.short_description,
#                                       long_description=attach.long_description,
#                                       attached=attach.attached,
#                                       attached_file=attach.attached_file,
#                                       created_on=DT.now(),
#                                       created_by=attach.created_by,
#                                       unit_type_id=attach.unit_type_id,
#                                       mime_type_id=attach.mime_type_id,
#                                       is_site_image=attach.is_site_image,
#                                       img_width=attach.img_width,
#                                       img_height=attach.img_height,
#                                       org_attach_id=attach.id )
#     return new_attach_id

#------------------------------------------------------------------
def get_mime_type_id_from_name( name ):
    db = current.db

    mte_model = db_tables.get_table_model( 'mime_type_ext', db=db )
    term.printDebug( 'name: %s' % repr( name ) )
    if '.' in name:
        ext = name.rsplit( '.', 1 )[1]
        term.printDebug( 'ext: %s' % repr( ext ) )
        q_sql = (db.mime_type_ext.extension == ext.lower())
        mte = mte_model.select( q_sql ).first()
        if mte:
            return mte.mime_type_id
    return None


#------------------------------------------------------------------
def get_mime_type_ext_from_name( name ):
    db = current.db

    mte_model = db_tables.get_table_model( 'mime_type_ext', db=db )

    if '.' in name:
        ext = name.rsplit( '.', 1 )[1]
        q_sql = (db.mime_type_ext.extension == ext)
        mte = mte_model.select( q_sql ).first()
        return mte
    return None


def get_mime_type_id_from_file( filename ):
    db = current.db
    mt_model = db_tables.get_table_model( 'mime_type', db=db )
    mg = magic.open( magic.MAGIC_MIME )
    mg.load()
    mtype = mg.file( filename )
    if mtype:
        mt_name = mtype.split( ';' )[0]
        q_sql = (db.mime_type.mt_name == mt_name)
        mt = mt_model.select( q_sql ).first()
        mime_type_id = mt.id
        return mime_type_id
    return None


def get_mime_type_from_name( name ):
    db = current.db

    mt_model = db_tables.get_table_model( 'mime_type', db=db )
    mt_id = get_mime_type_id_from_name( name )
    if mt_id:
        return mt_model[ mt_id ]
    return None


def get_mime_type_list( filter_types=None, db=None ):
    if not db:
        db = current.db
    if filter_types is None:
        filter_types = []
    mt_model = db_tables.get_table_model( 'mime_type', db=db )
    q_sql = None
    for f in filter_types:
        if q_sql:
            q_sql |= (db.mime_type.mt_name.like( f ))
        else:
            q_sql = (db.mime_type.mt_name.like( f ))
    rows = mt_model.select( q_sql, orderby='mt_name' )
    term.printDebug( 'sql: %s' % str( db._lastsql ) )
    return rows


def get_mime_type_ext_list( filter_types=[], db=None ):
    if not db:
        db = current.db
    mt_list = get_mime_type_list( filter_types=filter_types, db=db )
    mte_model = db_tables.get_table_model( 'mime_type_ext', db=db )
    q_sql = (db.mime_type_ext.mime_type_id.belongs( [mt.id for mt in mt_list ] ) )
    rows = mte_model.select( q_sql, orderby='extension' )
    return rows


def get_media_mime_type_list( db=None ):
    if not db:
        db = current.db
    filter_types = ('audio/%', 'video/%')
    mt_list = get_mime_type_list( filter_types=filter_types, db=db )
    return mt_list


def get_unit_type( meta_name, db=None ):
    if not db:
        db = current.db
    ut_model = db_tables.get_table_model( 'unit_type', db=db )
    q_sql = (db.unit_type.meta_name == meta_name)
    ut = ut_model.select( q_sql ).first()
    return ut


def get_attach_type( meta_name, db=None ):
    if not db:
        db = current.db
    at_model = db_tables.get_table_model( 'attach_type', db=db )
    q_sql = (db.attach_type.meta_name == meta_name)
    at = at_model.select( q_sql ).first()
    return at


def add_attach( attached,
                path=None,
                filename=None,
                created_by=None,
                attach_type_id=None,
                unit_type_id=None,
                mime_type_id=None,
                is_site_image=False,
                short_description=None,
                long_description=None,
                created_on=DT.now(),
                img_width=None,
                img_height=None,
                org_attach_id=None,
                dump_to_static=False,
                db=None ):
    if not db:
        db = current.db
    auth = current.auth

    term.printDebug( 'filename: %s' % filename )
    a_model = db_tables.get_table_model( 'attach', db=db )
    # at_model = db_tables.get_table_model( 'attach_type', db=db )
    mt_model = db_tables.get_table_model( 'mime_type', db=db )
    # ut_model = db_tables.get_table_model( 'unit_type', db=db )

    if not created_by:
        created_by = auth.user.id
    if not filename:
        filename = attached.filename
    filename = fileutils.filename_sanitize( filename )
    if not mime_type_id:
        mime_type_id = get_mime_type_id_from_name( filename )
    # ut = ut_model[ unit_type_id ]
    if not path:
        path = ''
    new_attach_id = db.attach.insert( attach_type_id=attach_type_id,
                                      path=path,
                                      filename=filename,
                                      attached=db.attach.attached.store( attached,
                                                                         attached.filename ),
                                      attached_file=attached.file.read(),
                                      created_on=created_on,
                                      created_by=created_by,
                                      unit_type_id=unit_type_id,
                                      mime_type_id=mime_type_id,
                                      is_site_image=bool( is_site_image ),
                                      short_description=short_description or filename,
                                      long_description=long_description,
                                      img_width=img_width,
                                      img_height=img_height,
                                      org_attach_id=org_attach_id )
    mt = mt_model[ mime_type_id ]
    if mt.mt_name.startswith( 'image/' ):
        a = a_model[ new_attach_id ]
        img = Image.open( StringIO.StringIO( a.attached_file ) )
        if not img_width and not img_height:
            a_model.update_by_id( new_attach_id,
                                  dict( img_width=img.size[0],
                                        img_height=img.size[1] ) )
        elif img_width or img_height:
            if img_width:
                ratio = float( img_width ) / img.size[0]
            else:
                ratio = float( img_height ) / img.size[1]
            if ratio < 1.0:
                a_model.update_by_id( new_attach_id,
                                      dict( img_width=img.size[0] * ratio,
                                            img_height=img.size[1] * ratio ) )
                resize_image( new_attach_id, img_width, db=db )
    if dump_to_static:
        file_dump_to_static( new_attach_id, db=db )
    return new_attach_id


# def get_full_path( attach_id, db=None ):
#     if not db:
#         db = current.db
#     request = current.request
#     a_model = db_tables.get_table_model( 'attach', db=db )
#     attach = a_model[ attach_id ]
#     if attach.mime_type_id.mt_name.startswith( 'image/' ):
#         dump_folder = 'images'
#     else:
#         dump_folder = 'data'
#     pathname = os.path.join( request.folder,
#                              'static',
#                              dump_folder,
#                              attach.path,
#                              attach.filename )
#     return pathname


def get_webshop_image_unit_type( db=None ):
    if not db:
        db = current.db
    ut_model = db_tables.get_table_model( 'unit_type', db=db )
    q_sql = (db.unit_type.meta_name == 'webshop')
    ut = ut_model.select( q_sql ).first()
    return ut

def get_webshop_image_folder( db=None ):
    if not db:
        db = current.db
    ut = get_webshop_image_unit_type( db=db )
    folder = 'images/' + ut.path
    return folder


def get_rel_path_from_app_static( attach=None, attach_id=None, db=None ):
    if not db:
        db = current.db
    if not attach:
        a_model = db_tables.get_table_model( 'attach', db=db )
        attach = a_model[ attach_id ]
    if attach.unit_type_id:
        if attach.mime_type_id.mt_name.startswith( 'image/' ):
            dump_folder = 'images'
        else:
            dump_folder = 'data'
    if attach.path:
        pathname = os.path.join( dump_folder, attach.path )
    elif attach.unit_type_id:
        pathname = dump_folder
        ut_model = db_tables.get_table_model( 'unit_type', db=db )
        ut = ut_model[ attach.unit_type_id ]
        if ut.path:
            pathname = os.path.join( dump_folder, ut.path )
    return pathname


# was get_path()
def get_rel_path_from_server_app( attach=None, attach_id=None, db=None ):
    '''

    Args:
        attach:
        attach_id:
        db:

    Returns:
        'static/' + <path_from_app_static>
    '''
    if not db:
        db = current.db
    if not attach:
        a_model = db_tables.get_table_model( 'attach', db=db )
        attach = a_model[ attach_id ]
    pathname = os.path.join( 'static',
                             get_rel_path_from_app_static( attach=attach, db=db ) )
    return pathname


def get_rel_path_from_server( attach=None, attach_id=None, db=None ):
    if not db:
        db = current.db
    request = current.request
    if not attach:
        a_model = db_tables.get_table_model( 'attach', db=db )
        attach = a_model[ attach_id ]
    path = request.folder
    if path.endswith( '/' ):
        path = path[ : -1 ]
    folder = '/'.join( path.split( '/' )[ -2 : ] )
    pathname = os.path.join( folder,
                             get_rel_path_from_server_app( attach=attach, db=db ) )
    return pathname


def get_abs_path_from_server( attach=None, attach_id=None, db=None ):
    if not db:
        db = current.db
    request = current.request
    if not attach:
        a_model = db_tables.get_table_model( 'attach', db=db )
        attach = a_model[ attach_id ]
    pathname = os.path.join( request.folder,
                             get_rel_path_from_server_app( attach=attach, db=db ) )
    return pathname


# def dump_all_attaches_to_static( db=None ):
#     if not db:
#         db = current.db
#     sql = '''
#         select a.*
#         from attach a
#         join unit_type ut on a.unit_type_id = ut.id
#         where ut.meta_name in ( 'site_objects', 'webshop' )
#     '''
#     rows = db.executesql( sql, as_dict=True )
#     for row in rows:
#         r = Storage( row )
#         file_dump_to_static( r.id, db=db )


def get_url( attach_id, db=None ):
    if not db:
        db = current.db
    request = current.request
    a_model = db_tables.get_table_model( 'attach', db=db )
    attach = a_model[ attach_id ]
    if is_file_in_static( attach_id, db=db ):
        pathname = os.path.join( get_rel_path_from_app_static( attach, db=db ),
                                 attach.filename )
        url = URL( 'static', pathname )
    else:
        url = URL( c='default', f='download', args=[ attach.attached ] )
    return url


# def resize_image_file( pathname, width=None, height=None ):
#     return media.resize_image( pathname, width=width, height=height )
    # img = Image.open( pathname )
    # img_width = img.size[ 0 ]
    # img_height = img.size[ 1 ]
    # if width:
    #     ratio = float( width ) / img_width
    # elif height:
    #     ratio = float( height ) / img_height
    # if ratio < 1.0:
    #     w = int( img_width * ratio )
    #     h = int( img_height * ratio )
    #     img_resized = img.resize( (w, h), Image.ANTIALIAS )
    #     img_resized.save( pathname )
    #     return w, h
    # return None, None


def image_dump( attach_id, filename=None, width=None, db=None ):
    if not db:
        db = current.db
    # term.printDebug( 'attach_id: %s' % ( attach_id ) )
    a_model = db_tables.get_table_model( 'attach', db=db )
    attach = a_model[ attach_id ]
    # term.printDebug( 'attach: %s' % ( attach.filename ) )
    parts = attach.filename.rsplit( '.', 1 )
    ext = '.%s' % parts[1]
    if not filename:
        fd, filename = tempfile.mkstemp( suffix=ext )
        f = os.fdopen( fd, 'wb' )
#         f.write( self.db.attach.attached.retrieve( attach.attached )[1].read() )
        f.close()
    # filename = fileutils.filename_sanitize( filename )
    f_name, stream = db.attach.attached.retrieve( attach.attached )
    # term.printDebug( 'filename: %s' % ( filename ) )
    if '/' in filename:
        parent = filename.rsplit( '/', 1 )[0]
        if not os.path.exists( parent ):
            os.makedirs( parent )
    import shutil
    # term.printDebug( 'filename: %s' % ( filename ) )
    shutil.copyfileobj( stream, open( filename, 'wb' ) )
    if width:
        media.resize_image( filename, width=width )
    return filename


def file_dump( attach_id, filename=None, tmp=False, db=None ):
    if not db:
        db = current.db
    # term.printDebug( 'attach_id: %s' % ( attach_id ) )
    a_model = db_tables.get_table_model( 'attach', db=db )
    attach = a_model[ attach_id ]
    # term.printDebug( 'attach: %s' % ( attach.filename ) )
    if not filename:
        filename = fileutils.filename_sanitize( attach.filename )
        if filename != attach.filename:
            a_model.update_by_id( attach_id, dict( filename=filename ) )
        if tmp:
            parts = attach.filename.rsplit( '.', 1 )
            ext = '.%s' % parts[ 1 ]
            fd, filename = tempfile.mkstemp( suffix=ext )
            f = os.fdopen( fd, 'wb' )
            f.close()
        else:
            pathname = get_rel_path_from_server( attach )
            filename = os.path.join( pathname, attach.path, attach.filename )
#     parts = attach.filename.rsplit( '.', 1 )
#     ext = '.%s' % parts[1]
#     if not filename:
#         fd, filename = tempfile.mkstemp( suffix=ext )
#         f = os.fdopen( fd, 'wb' )
# #         f.write( self.db.attach.attached.retrieve( attach.attached )[1].read() )
#         f.close()
    f_name, stream = db.attach.attached.retrieve( attach.attached )
    # term.printDebug( 'filename: %s' % ( filename ) )
    if '/' in filename:
        parent = filename.rsplit( '/', 1 )[0]
        if not os.path.exists( parent ):
            os.makedirs( parent )
    import shutil
    term.printDebug( 'filename: %s' % ( filename ) )
    shutil.copyfileobj( stream, open( filename, 'wb' ) )
    return filename


def file_dump_to_private( attach_id, dump_folder=None, db=None ):
    if not db:
        db = current.db
    a_model = db_tables.get_table_model( 'attach', db=db )
    request = current.request
    attach = db.attach[ attach_id ]
    # term.printDebug( 'attach: %s' % ( attach.filename ) )

    path = get_rel_path_from_server_app( attach )
    filename = os.path.join( request.folder,
                             'private' )
    if dump_folder:
        filename = os.path.join( filename, dump_folder, attach.filename )
    else:
        filename = os.path.join( filename, path, attach.filename )
    # term.printDebug( 'filename: %s' % ( filename ) )
    file_dump( attach.id, filename )
    # term.printDebug( 'attach copied to: %s' % ( filename ) )
    if is_image( attach, db=db ):
        img = Image.open( filename )
        a_model.update_by_id( attach_id,
                              dict( img_width=img.size[0],
                                    img_height=img.size[1] ) )
    return filename


def file_dump_to_static( attach_id, db=None ):
    if not db:
        db = current.db
    request = current.request
    a_model = db_tables.get_table_model( 'attach', db=db )
    attach = a_model[ attach_id ]
    term.printDebug( 'attach: %s' % ( attach.filename ) )
    # path = get_rel_path_from_server_app( attach )
    path = get_rel_path_from_server( attach, db=db )
    s_filename = fileutils.filename_sanitize( attach.filename )
    filename = os.path.join( path, s_filename )
    # filename = fileutils.filename_sanitize( attach.filename )
    if s_filename != attach.filename:
        a_model.update_by_id( attach_id, dict( filename=s_filename ) )

    # filename = fileutils.filename_sanitize( attach.filename )
    # term.printDebug( 'filename: %s' % ( filename ) )
    file_dump( attach.id, filename, db=db )
    term.printDebug( 'attach copied to: %s' % ( filename ) )
    if is_image( attach ):
        img = Image.open( filename )
        a_model.update_by_id( attach_id,
                              dict( img_width=img.size[0],
                                    img_height=img.size[1] ) )
    return filename


def resize_image( attach_id, width=None, height=None, new_filename=None, db=None ):
    if not db:
        db = current.db

    a_model = db_tables.get_table_model( 'attach', db=db )
    attach = a_model[ attach_id ]
    if not new_filename:
        new_filename = attach.filename

    f_name, stream = db.attach.attached.retrieve( attach.attached )
    img = Image.open( stream )
    img_width = img.size[ 0 ]
    img_height = img.size[ 1 ]
    w = h = 0
    if width and height:
        w = width
        h = height
    else:
        if width:
            ratio = float( width ) / img_width
        else:
            ratio = float( height ) / img_height
        if ratio < 1.0:
            w = int( img_width * ratio )
            h = int( img_height * ratio )
    if w:
        img_resized = img.resize( (w, h), Image.ANTIALIAS )
        pathname = os.path.join( get_rel_path_from_server_app( attach, db=db ),
                                 new_filename )
        img_resized.save( pathname )
        stream = open( pathname, 'rb' )
        d = dict( path=attach.path,
                  filename=new_filename,
                  attached=db.attach.attached.store( stream,
                                                     new_filename ),
                  attached_file=stream.read(),
                  img_width=w,
                  img_height=h )
        a_model.update_by_id( attach_id, d )
    else:
        d = dict( img_width=img_width,
                  img_height=img_height )
        a_model.update_by_id( attach_id, d )

    return w, h


def get_resize_options( attach, img_sizes ):
    '''
        ac = app_factory.get_app_config_data( db=db )
        img_sizes = Storage( large=ac[ IMG_SIZE_PAGE ],
                             medium=ac[ IMG_SIZE_BLOCK ],
                             small=ac[ IMG_SIZE_THUMB ])

    '''
    resize_options = []
    for k in img_sizes:
        if img_sizes[k] < attach.img_width:
            resize_options.append( k )
    return resize_options


def get_child_by_width( attach_id, width, db=None ):
    if not db:
        db = current.db

    a_model = db_tables.get_table_model( 'attach', db=db )
    q_sql = (db.attach.org_attach_id == attach_id)
    q_sql &= (db.attach.img_width < width * WIDTH_MARGIN)
    q_sql &= (db.attach.img_width >= width)
    child = a_model.select( q_sql, orderby='img_width' ).first()
    return child


def dump_all_files_to_disk( attach_type_id=None,
                            unit_type_id=None,
                            at_meta_name=None,
                            ut_meta_name=None,
                            thumb_size=0,
                            db=None ):
    if not db:
        db = current.db

    a_model = db_tables.get_table_model( 'attach', db=db )
    at_model = db_tables.get_table_model( 'attach_type', db=db )
    ut_model = db_tables.get_table_model( 'unit_type', db=db )
    if attach_type_id:
        at = at_model[ attach_type_id ]
    else:
        q_sql = (db.attach_type.meta_name == at_meta_name)
        at = at_model.select( q_sql ).first()
    if unit_type_id:
        ut = ut_model[ unit_type_id ]
    else:
        q_sql = (db.unit_type.meta_name == ut_meta_name)
        ut = ut_model.select( q_sql ).first()

    q_sql = (db.attach.attach_type_id == at.id)
    q_sql &= (db.attach.unit_type_id == ut.id)
    q_sql &= (db.attach.org_attach_id == None)
    a_list = a_model.select( q_sql, orderby='filename' )
    user_id = user_factory.get_auth_user_id( include_dummy=True, db=db )
    for a in a_list:
        if not is_file_in_static( a.id, db=db ):
            file_dump_to_static( a.id, db=db )
        if thumb_size:
            child = get_child_by_width( a.id, thumb_size, db=db )
            if not child:
                copy_image( user_id,
                            a.id,
                            new_width=thumb_size,
                            insert_dim_in_name=True,
                            dump_to_static=True,
                            db=db )
