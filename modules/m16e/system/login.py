# -*- coding: utf-8 -*-
'''
Created on 06/06/2015

@author: carlos
'''

import os
import sys
import traceback

from gluon import URL
from gluon.globals import current
from m16e import term
from m16e.files import fileutils


def prepare_user_login( app_name, next_url=None ):
    '''
    Prepare auto login in <app_name>

    Returns: app url
    '''
    auth = current.auth
    parent_folder = '%s/applications/%s/private/login' % (fileutils.get_w2p_full_path(),
                                                          app_name)
    term.printDebug( 'parent_folder: %s' % parent_folder )
    if not os.path.isdir( parent_folder ):
        os.makedirs( parent_folder )
    path = '%s/%s' % (parent_folder, auth.user.email)
    term.printLog( 'path: %s\n  next_url: %s' % (path, repr( next_url )) )
    if not os.path.isfile( path ):
        if next_url:
            fileutils.write_file( path, next_url )
        else:
            os.mknod( path )
    url = URL( a=app_name,
               c='admin',
               f='login_user',
               args=[ auth.user.email ] )
    term.printDebug( 'url: %s' % repr( url ) )
    return url


def auto_user_login( email, db=None ):
    '''
    Auto login user
    Args:
        email:
        db:

    Returns:
        main url
    '''
    if not db:
        db = current.db
    request = current.request
    next_url = None
    try:
        q_sql = (db.auth_user.email == email)
        user = db( q_sql ).select().first()
#        term.printDebug( 'sql: %s' % db._lastsql )
#        term.printDebug( 'user: %s' % repr( user ) )
        path = '%sprivate/login/%s' % (request.folder, email)
        term.printDebug( 'path: %s' % path )
        term.printDebug( 'user: %s' % repr( user ) )
        if os.path.isfile( path ):
            current.auth.login_user( user )
            next_url = fileutils.read_file( path )
            term.printDebug( 'user logged in: %s' % repr( user.id ) )
            os.remove( path )
    except:
        t, v, tb = sys.exc_info( )
        traceback.print_exception( t, v, tb )
        raise
    if not next_url:
        next_url = URL( c='default', f='index' )
    return next_url


def request_authentication( email, db=None ):
    if not db:
        db = current.db
    request = current.request
    next_url = None
    try:
        q_sql = (db.auth_user.email == email)
        user = db( q_sql ).select().first()
        #        term.printDebug( 'sql: %s' % db._lastsql )
        #        term.printDebug( 'user: %s' % repr( user ) )
        path = '%sprivate/login/%s' % (request.folder, email)
        term.printDebug( 'path: %s' % path )
        term.printDebug( 'user: %s' % repr( user ) )
        if os.path.isfile( path ):
            current.auth.login_user( user )
            next_url = fileutils.read_file( path )
            term.printDebug( 'user logged in: %s' % repr( user.id ) )
            os.remove( path )
    except:
        t, v, tb = sys.exc_info()
        traceback.print_exception( t, v, tb )
        raise
    if not next_url:
        next_url = URL( c='default', f='index' )
    return next_url

