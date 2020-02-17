# -*- coding: utf-8 -*-
from app import db_sets
from chirico.k import IMG_SIZE_PAGE, IMG_SIZE_BLOCK, IMG_SIZE_THUMB
from chirico.app import app_factory
from gluon.storage import Storage
from m16e import term, user_factory
from m16e.db import db_tables, attach_factory

if 0:
    import gluon
    from gluon.html import DIV
    from gluon.html import FORM
    from gluon.html import INPUT
    from gluon.html import TABLE
    from gluon.html import TD
    from gluon.html import TR
    from gluon.html import URL
    from gluon.dal import GQLDB, SQLDB
    from gluon.html import PRE, P, TAG, B
    from gluon.http import HTTP
    from gluon.sqlhtml import SQLFORM
    from gluon.validators import IS_NOT_EMPTY

    import gluon.languages.translator as T

    global auth; auth = gluon.tools.Auth()
    global cache; cache = gluon.cache.Cache()
    global crud; crud = gluon.tools.Crud()
    global db; db = gluon.sql.DAL()
    global request; request = gluon.globals.Request()
    global response; response = gluon.globals.Response()
    global service; service = gluon.tools.Service()
    global session; session = gluon.globals.Session()

    from gluon.http import redirect


def img2disk():
    a_model = db_tables.get_table_model( 'attach', db=db )
    at_model = db_tables.get_table_model( 'attach_type', db=db )
    ut_model = db_tables.get_table_model( 'unit_type', db=db )
    q_sql = (db.attach_type.meta_name == 'images')
    at = at_model.select( q_sql ).first()
    q_sql = (db.unit_type.meta_name == 'site_objects')
    ut = ut_model.select( q_sql ).first()
    q_sql = (db.attach.attach_type_id == at.id)
    q_sql &= (db.attach.unit_type_id == ut.id)
    q_sql &= (db.attach.org_attach_id == None)
    a_list = a_model.select( q_sql, orderby='filename' )
    ac = app_factory.get_app_config_data( db=db )
    small_size = ac[ IMG_SIZE_THUMB ]
    user_id = user_factory.get_auth_user_id( include_dummy=True, db=db )
    for a in a_list:
        if not attach_factory.is_file_in_static( a.id, db=db ):
            attach_factory.file_dump_to_static( a.id, db=db )
        child = attach_factory.get_child_by_width( a.id, small_size, db=db )
        if not child:
            attach_factory.copy_image( user_id,
                                       a.id,
                                       new_width=small_size,
                                       insert_dim_in_name=True,
                                       dump_to_static=True )


img2disk()
