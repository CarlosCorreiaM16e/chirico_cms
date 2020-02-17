# -*- coding: utf-8 -*-

import os

import m16e.files.fileutils as futils
import m16e.term as term
from gluon import current


#----------------------------------------------------------------------
# users
#----------------------------------------------------------------------
def addUser( db, T, user, grpList ):
    has_username = 'username' in db.auth_user.fields
    has_full_name = 'full_name' in db.auth_user.fields
    has_fiscal_id = 'fiscal_id' in db.auth_user.fields
    user[ 'password' ] = db.auth_user.password.validate( user[ 'password' ] )[0]
    d = { 'first_name': user[ 'fname' ],
          'last_name': user[ 'lname' ],
          'email': user[ 'email' ],
          'password': db.auth_user.password.validate( user[ 'password' ] )[0],
          'registration_key': '',
          'reset_password_key': '',
          'registration_id': '' }
    if has_full_name:
        d[ 'full_name' ] = user[ 'full_name' ]
    if has_username:
        d[ 'username' ] = user[ 'username' ]
    if has_fiscal_id:
        d[ 'fiscal_id' ] = '?'
    uid = db.auth_user.insert( **d )
    for g in grpList:
        grp = db( db.auth_group.role == g[ 'name' ] ).select().first()
        if grp:
            db.auth_membership.insert(
                user_id = uid,
                group_id = grp.id )
        else:
            gid = db.auth_group.insert(
                role = g[ 'name' ],
                description = T( g[ 'desc' ] ) )
            db.auth_membership.insert(
                user_id = uid,
                group_id = gid )

#----------------------------------------------------------------------
def upd_permissions( permissions ):
    db = current.db
    if permissions:
        for p in permissions:
            if p == 'impersonate':
                group_name = permissions[ p ]
                q = (db.auth_group.role == group_name )
                group = db( q ).select().first()
                q = (db.auth_permission.group_id == group.id)
                q &= (db.auth_permission.name == p)
                q &= (db.auth_permission.table_name == 'auth_user')
                ap = db( q ).select().first()
                if not ap:
                    db.auth_permission.insert( group_id=group.id,
                                               name=p,
                                               table_name='auth_user',
                                               record_id=0 )

            else:
                raise Exception( 'Bad perm: %s' % p )
    else:
        term.printLog( 'no permissions defined!' )

#----------------------------------------------------------------------
def init_users( userList ):
    db = current.db
    T = current.T

    has_username = 'username' in db.auth_user.fields
    has_full_name = 'full_name' in db.auth_user.fields
    has_fiscal_id = 'fiscal_id' in db.auth_user.fields
    for u in userList:
        term.printLog( 'u: %s' % ( repr( u ) ) )
        d = { 'first_name': u[ 'fname' ],
              'last_name': u[ 'lname' ],
              'email': u[ 'email' ],
              'password': db.auth_user.password.validate( u[ 'password' ] )[0],
              'registration_key': '',
              'reset_password_key': '',
              'registration_id': '' }
        if has_full_name:
            d[ 'full_name' ] = u[ 'fname' ]
        if has_username:
            d[ 'username' ] = u[ 'username' ]
            q = (db.auth_user.username == u[ 'username' ])
        else:
            q = (db.auth_user.email == u[ 'email' ])
        if has_fiscal_id:
            d[ 'fiscal_id' ] = '?'
        user = db( q ).select().first()
        if user:
            db( q ).update( **d )
            for g in u[ 'groups' ]:
                grp = db( db.auth_group.role == g[ 'name' ] ).select().first()
                if grp:
                    am = db(
                        (db.auth_membership.user_id == user.id) &
                        (db.auth_membership.group_id == grp.id) ).select().first()
                    if not am:
                        db.auth_membership.insert(
                            user_id = user.id,
                            group_id = grp.id )
                else:
                    gid = db.auth_group.insert(
                        role = g[ 'name' ],
                        description = T( g[ 'desc' ] ) )
                    db.auth_membership.insert(
                        user_id = user.id,
                        group_id = gid )
        else:
            uid = db.auth_user.insert( **d )
            for g in u[ 'groups' ]:
                grp = db( db.auth_group.role == g[ 'name' ] ).select().first()
                if grp:
                    db.auth_membership.insert(
                        user_id = uid,
                        group_id = grp.id )
                else:
                    gid = db.auth_group.insert(
                        role = g[ 'name' ],
                        description = T( g[ 'desc' ] ) )
                    db.auth_membership.insert(
                        user_id = uid,
                        group_id = gid )

#------------------------------------------------------------------
def load_mime_types( db, folder ):
    mts = os.path.join(
        folder,
        'private', 'resources', 'install', 'mime_type.txt' )

    sql = '''
    insert into mime_type values(
        %(id)s, %(mt_name)s, %(description)s,
        %(edit_command)s, %(view_command)s, %(preferred_order)s )
    '''
    lines = futils.readFilelines( mts )
    for mt in lines[2:]:
        term.printLog( mt )
        if mt.startswith( '(' ):
            break
        line = mt.split( '|' )
        t = {}
        t[ 'id' ] = int( line[0].strip() ) + 1
        t[ 'mt_name' ] = line[1].strip()
        t[ 'description' ] = line[2].strip()
        t[ 'edit_command' ] = line[3].strip()
        t[ 'view_command' ] = line[4].strip()
        t[ 'preferred_order' ] = int( line[5].strip() )
        db.executesql( sql, placeholders = t )

    mtExts = os.path.join(
        folder,
        'private', 'resources', 'install', 'mime_type_ext.txt' )
    sql = '''
    insert into mime_type_ext ( mime_type_id, extension )
    values( %(mime_type_id)s, %(extension)s )
    '''
    lines = futils.readFilelines( mtExts )
    for mt in lines[2:]:
        if mt.startswith( '(' ):
            break
        line = mt.split( '|' )
        t = {}
        t[ 'mime_type_id' ] = int( line[0].strip() ) + 1
        t[ 'extension' ] = line[2].strip()
        db.executesql( sql, placeholders = t )

    db.commit()

#----------------------------------------------------------------------


