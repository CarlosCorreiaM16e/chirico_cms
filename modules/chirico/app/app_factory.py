# -*- coding: utf-8 -*-
'''
Created on 06/06/2015

@author: carlos
'''

import os

from chirico.k import SES_MODE_ANON
from m16e.db import db_tables
from gluon.globals import current


def is_demo():
    request = current.request
    test_file = '%(w)s/applications/%(a)s/DEMO' % { 'w': request.env.web2py_path,
                                                    'a': request.application }
    testing = os.path.isfile( test_file )
    return testing


def is_demo_version():
    request = current.request
    demo = request.application.endswith( '_test' ) or is_testing() or is_demo()
    return demo


def is_testing():
    request = current.request
    test_file = '%(w)s/applications/%(a)s/TESTING' % { 'w': request.env.web2py_path,
                                                       'a': request.application }
    testing = os.path.isfile( test_file )
    return testing


def set_testing( testing ):
    request = current.request
    test_file = '%(w)s/applications/%(a)s/TESTING' % { 'w': request.env.web2py_path,
                                                       'a': request.application }
    if testing:
        f = open( test_file, 'w' )
        f.close()
        # os.utime( test_file )
    elif os.path.isfile( test_file ):
        os.unlink( test_file )


def get_app_config_data( force_reload=False, db=None ):
    if not db:
        db = current.db
    if not current.app_config_data or force_reload:
        ac_model = db_tables.get_table_model( 'app_config', db=db )
        current.app_config_data = ac_model.select().first()
    return current.app_config_data


def get_flash_msg_delay( db=None ):
    if not db:
        db = current.db
    ac = get_app_config_data( db=db )
    if ac:
        return ac.flash_msg_delay
    return 4000


def get_app_theme( db=None ):
    if not db:
        db = current.db
    ac_model = db_tables.get_table_model( 'app_config', db=db )
    at_model = db_tables.get_table_model( 'app_theme', db=db )
    ac = ac_model.select().first()
    # term.printDebug( 'ac: %s' % repr( ac ) )
    if ac.app_theme_id:
        return at_model[ ac.app_theme_id ]
    return None


def get_session_mode():
    session = current.session
    if not session.session_mode:
        session.session_mode = SES_MODE_ANON
    return session.session_mode


def set_session_mode( session_mode ):
    session = current.session
    session.session_mode = session_mode
