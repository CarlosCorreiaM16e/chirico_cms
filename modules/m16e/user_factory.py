# -*- coding: utf-8 -*-
# this file is released under GPL Licence v.3
# author: carlos@memoriapersistente.pt

from dateutil import relativedelta

from m16e.db import db_tables
from gluon.globals import current
from gluon.html import DIV, TABLE, TR, TD, XML, URL, INPUT, B
from gluon.storage import Storage
from m16e import term, mpmail
from m16e.kommon import HTML_PERMITED_TAGS, HTML_ALLOWED_ATTRIBUTES, K_ROLE_ADMIN, K_ROLE_DEVELOPER, K_ROLE_EDITOR, \
    K_ROLE_MANAGER, K_ROLE_SUPPORT, DT, is_sequence, K_ROLE_USER

DUMMY_USER = 'dummy@m16e.com'

# UMT_EMBBED_TOP = 'embbed_top'

def get_dummy_user( db=None ):
    if not db:
        db = current.db
    u = db( db.auth_user.email == DUMMY_USER ).select().first()
    return u


def get_auth_user( include_dummy=False, db=None ):
    if not db:
        db = current.db
    auth = current.auth
    if auth.user:
        return auth.user
    if include_dummy:
        return get_dummy_user( db=db )
    return None


def get_auth_user_id( include_dummy=False, db=None ):
    if not db:
        db = current.db
    try:
        auth = current.auth
    except:
        pass
    if auth and auth.user:
        return auth.user.id
    if include_dummy:
        u = get_dummy_user( db=db )
        return u.id
    return None


def get_dev_user( db=None ):
    if not db:
        db = current.db
    sql = '''
        select 
            au.* 
        from auth_user au 
            join auth_membership am on au.id = am.user_id 
            join auth_group ag on am.group_id = ag.id 
        where ag.role = '%s' 
        order by au.id, ag.id
    ''' % K_ROLE_DEVELOPER
    rows = db.executesql( sql, as_dict=True )
    if rows:
        return Storage( rows[0] )
    return None


def get_user_message_board():
    T = current.T
    auth = current.auth
    db = current.db
    user_message_board = ''
    if auth and auth.user:
        um_model = db_tables.get_table_model( 'user_message', db=db )
        q_sql = (db.user_message.notify_user_id == auth.user.id)
        q_sql &= (db.user_message.period_start <= DT.now())
        q_sql &= ( (db.user_message.period_stop == None) | (db.user_message.period_stop >= DT.now()))
        q_sql &= (db.user_message.ack_when == None)
        user_message_board = um_model.select( q_sql, orderby='period_start, id')

#     if auth and auth.user:
#         user_message_board = DIV()
#         um_model = db_tables.get_table_model( 'user_message', db=db )
#         q_sql = (db.user_message.notify_user_id == auth.user.id)
#         q_sql &= (db.user_message.period_start <= DT.now())
#         q_sql &= ( (db.user_message.period_stop == None) | (db.user_message.period_stop >= DT.now()))
#         q_sql &= (db.user_message.ack_when == None)
#         um_list = um_model.select( q_sql, orderby='period_start, id')
# #         term.printDebug( 'sql: %s' % db._lastsql )
#         table = TABLE()
#         for um in um_list:
#             tr = TR( _id='um_%d' % um.id )
#             tr.append( TD( B( um.msg_title ) ) )
#             tr.append( TD( XML( um.msg_text,
#                                 sanitize=False,
#                                 permitted_tags=HTML_PERMITED_TAGS,
#                                 allowed_attributes=HTML_ALLOWED_ATTRIBUTES ) ) )
#             onclick = '''
#                 ajax( '%(url)s', [], ':eval' );
#             ''' % { 'url': URL( c='users',
#                                 f='ajax_ack_message',
#                                 args=[ um.id ] ) }
#             inp = INPUT( _value=T( 'Acknowledge' ),
#                          _type='button',
#                          _class='btn btn-mini btn-info',
#                          _onclick=onclick )
#             tr.append( TD( inp ) )
#             table.append( tr )
#         user_message_board.append( table )
    return user_message_board


# def get_user_list( role, orderby='first_name', db=None ):
#     if not db:
#         db = current.db
#     sql = '''
#         select au.*
#         from auth_user au
#             join auth_membership am on am.user_id = au.id
#             join auth_group ag on am.group_id = ag.id
#         where
#             role = '%(role)s'
#         order by %(orderby)s
#     ''' % dict( role=role, orderby=orderby )
#     rows = db.executesql( sql, as_dict=True )
#

def get_user_list( group=None,
                   group_id=None,
                   company_id=None,
                   orderby='first_name',
                   db=None ):
    if not db:
        db = current.db
    if company_id:
        auth = current.auth
        if is_in_group( 'support' ):
            sql = '''
                select *
                from auth_user
                order by
                    %s
            ''' % orderby
        else:
            sql = '''
                select * 
                from auth_user 
                where registation_key == ''
            ''' % auth.user.id
    elif group:
        sql = '''
            select au.*
            from auth_user au
                join auth_membership am on au.id = am.user_id
                join auth_group ag on ag.id = am.group_id
        '''
        if is_sequence( group ):
            sql += '''
            where
                ag.role in ( %s )
            ''' % str( group )[ 1 : -1 ]
        else:
            sql += '''
            where
                ag.role like( '%s' )
            ''' % group
        sql += '''
            order by
                %s
        ''' % orderby
    elif group_id:
        sql = '''
            select au.*
            from auth_user au
                join auth_membership am on au.id = am.user_id
            where
                am.group_id = %d
        ''' % group_id
        sql += '''
                order by
                    %s
            ''' % orderby
    else:
        sql = '''
            select *
            from auth_user
            where 
                registration_key = ''
            order by
                %s
        ''' % orderby
    # term.printDebug( 'sql: %s' % sql )
    rows = db.executesql( sql, as_dict=True )
    u_list = [ Storage( r ) for r in rows ]
    return u_list


def get_user_list_as_options( group=None,
                              company_id=None,
                              orderby='first_name',
                              insert_blank=False,
                              db=None ):
    if not db:
        db = current.db
    u_list = get_user_list( group=group, company_id=company_id, orderby=orderby, db=db )
    user_list = [ (r.id, '%s <%s>' % (r.first_name, r.email)) for r in u_list ]
    if insert_blank:
        user_list.insert( 0, ('', '') )
    return user_list


_group_hierarchy_list = [ K_ROLE_DEVELOPER,
                          K_ROLE_ADMIN,
                          K_ROLE_EDITOR,
                          K_ROLE_MANAGER,
                          K_ROLE_SUPPORT,
                          K_ROLE_USER
                          ]


def get_group_list( role=None, db=None ):
    '''

    :param role: if None, use user highest role
    :param db:
    :return: list of ROW
    '''
#     term.printDebug( 'role: %s' % role )
    if not db:
        db = current.db
    if role is None:
        auth = current.auth
        sql = '''
            select ag.*
            from auth_user au
                join auth_membership am on au.id = am.user_id
                join auth_group ag on ag.id = am.group_id
        '''
        rows = db.executesql( sql, as_dict=True )
        high_role = len( _group_hierarchy_list ) - 1
        for r in rows:
            idx = _group_hierarchy_list.index( r[ 'role' ] )
            if idx < high_role:
                high_role = idx
        # idx = _group_hierarchy_list.index( r[ 'role' ] )
        role = _group_hierarchy_list[ high_role ]
    ag_list = db( db.auth_group.id > 0 ).select( orderby='role' )
    if role:
        h = _group_hierarchy_list[ _group_hierarchy_list.index( role ) : ]
    else:
        h = _group_hierarchy_list
    g_list = []
    for ag in ag_list:
        if ag.role in h:
            g_list.append( ag )
    return g_list


def get_group_list_as_options( role=None, insert_blank=False, db=None ):
#     term.printDebug( 'role: %s' % role )
    if not db:
        db = current.db
    g_list = get_group_list( role=role, db=db )
    group_list = [ (g.id, g.role) for g in g_list ]
    if insert_blank:
        group_list.insert( 0, ('', '') )
    return group_list


def is_in_group( group_name=None, group_id=None, auth_user_id=None, db=None ):
    '''
    Group hierarchy:
    + dev
    +-- support
        +-- admin
            +-- manager
                +-- (others)
    '''
#     term.printDebug( 'group: %s' % group )
    if not db:
        db = current.db
    auth = current.auth
    if auth_user_id is None and auth.user:
        auth_user_id = auth.user.id

    if not auth_user_id:
        return False

    if group_name:
        sql = '''
            select count( * )
                from auth_membership am
                    join auth_group ag on am.group_id = ag.id
                where
                    ag.role = '%(role)s' and
                    am.user_id = %(uid)s
        ''' % { 'role': group_name,
                'uid': auth_user_id }
    else:
        sql = '''
            select count( * )
                from auth_membership
                where
                    am.group_id = '%(gid)s' and
                    am.user_id = %(uid)s
        ''' % { 'gid': group_id,
                'uid': auth_user_id }
    # term.printDebug( 'sql: %s' % sql )
    rows = db.executesql( sql )
    in_grp = bool( rows[0][0] > 0 )
    # term.printDebug( 'auth_user_id: %s; in_grp: %s; rows: %s' %
    #                  ( repr( auth_user_id ), repr( in_grp ), repr( rows[0][0] ) ) )
    return in_grp

    # q = (db.auth_group.role == group)
    # grp = db( q ).select().first()
    # q = (db.auth_membership.user_id == auth_user_id)
    # q &= (db.auth_membership.group_id == grp.id)
    # return bool( db( q ).count() )

    # auth = current.auth
    # if auth.user and auth.user.id > 0:
    #     if auth.has_membership( group ):
    #         return True
        # if auth.has_membership( 'dev' ):
        #     return True
        # master_grps = [ 'dev' ]
        # if group not in master_grps and auth.has_membership( 'support' ):
        #     return True
        # master_grps.append( 'support' )
        # if group not in master_grps and auth.has_membership( 'admin' ):
        #     return True
        # master_grps.append( 'admin' )
        # if group not in master_grps and auth.has_membership( 'manager' ):
        #     return True

    # return False


def get_auth_group( group_name=None,
                    group_id=None,
                    create_group=False,
                    db=None ):
    '''
    Get group and (optionally), create it
    Args:
        group_name: group role 
        group_id: group id
        create_group: if True creates group if doesn't exist
        db: 

    Returns:
        group row
    '''
    if not db:
        db = current.db
    if group_name:
        q = (db.auth_group.role == group_name)
    else:
        q = (db.auth_group.id == group_id)
    group = db( q ).select().first()
    if not group and create_group:
        gid = db.auth_group.insert( role=group_name )
        group = db.auth_group[ gid ]
    return group


def add_user_to_group( group_name=None,
                       group_id=None,
                       auth_user_id=None,
                       create_groups=False,
                       db=None ):
    if not db:
        db = current.db
    if auth_user_id is None:
        auth = current.auth
        auth_user_id = auth.user.id
    group = get_auth_group( group_name=group_name, group_id=group_id, db=db )
    d = { 'uid': auth_user_id }
    sql = '''
        insert into auth_membership( user_id, group_id )
            values( %(uid)s, %(gid)s )
    '''
    for grp in _group_hierarchy_list[ _group_hierarchy_list.index( group.role ): ]:
        # term.printDebug( 'grp: %s' % repr( grp ) )
        if not is_in_group( group_name=grp,
                            auth_user_id=auth_user_id,
                            db=db ):
            aux_group = get_auth_group( group_name=grp, create_group=create_groups, db=db )
            term.printLog( 'sql: %s' % str( db._lastsql ) )
            term.printLog( 'added user %s to group: %s' % (repr( auth_user_id ), repr( aux_group ) ) )
            d[ 'gid' ] = aux_group.id
            db.executesql( sql % d )


def touch_login_event( db=None ):
    if not db:
        db = current.db
    auth = current.auth
    now = DT.now()
    start = now - relativedelta.relativedelta( hours=8 )
    q_sql = (db.auth_event.user_id == auth.user.id)
    q_sql &= (db.auth_event.time_stamp > start)
    count = db( q_sql ).count()
    # term.printDebug( 'sql: %s' % db._lastsql )
    if not count:
        db.auth_event.insert( time_stamp=now,
                              client_ip=current.request.client,
                              user_id=auth.user.id,
                              origin='auth',
                              description='User %(id)s is logged-in' % dict( id=auth.user.id ) )


EVT_ORIGIN_AUTH = 'auth'
EVT_ORIGIN_PERMISSIONS = 'permissions'
EVT_ORIGIN_CMS = 'cms'
EVT_ORIGIN_FORUM = 'forum'

_evt_origin_list = [ EVT_ORIGIN_AUTH,
                     EVT_ORIGIN_PERMISSIONS,
                     EVT_ORIGIN_CMS,
                     EVT_ORIGIN_FORUM ]

def login_event( origin, description, db=None ):
    if not db:
        db = current.db
    auth = current.auth
    now = DT.now()
    if origin not in _evt_origin_list:
        term.printLog( 'UNKNOWN ORIGIN: ' + origin, print_trace=True )
    db.auth_event.insert( time_stamp=now,
                          client_ip=current.request.client,
                          user_id=auth.user.id,
                          origin=origin,
                          description=description )


def add_user_message( data, db=None ):
    auth = current.auth
    if not db:
        db = current.db
    ut_model = db_tables.get_table_model( 'user_message', db=db )
    if not 'notify_user_id' in data:
        q = (db.auth_user.email == auth.user.email)
        au = db( q ).select().first()
        data[ 'notify_user_id' ] = au.id
    ui_id = ut_model.insert( data )
    return ui_id


def notify_users( to_list, subject, message, db=None ):
    if not db:
        db = current.db
    mail = current.mail
    app_name = '[%s]' % current.meta_name
    if not subject.startswith( app_name ):
        subject = app_name + subject
    mpmail.queue_mail( to_list,
                       bcc=[mail.settings.sender],
                       subject=subject,
                       text_body=message,
                       db=db )
