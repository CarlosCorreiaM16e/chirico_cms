# -*- coding: utf-8 -*-
from chirico.db import page_factory
from gluon import current
from gluon.storage import Storage
from m16e import user_factory, term
from m16e.db import db_tables
from m16e.kommon import DT
from m16e.system import env


def update_page_stats( path_info, db=None ):
    if not db:
        db = current.db
    pc_model = db_tables.get_table_model( 'page_counter', db=db )
    ts = DT.now()
    q_sql = (db.page_counter.path_info == path_info)
    q_sql &= (db.page_counter.year == ts.year)
    q_sql &= (db.page_counter.month == ts.month)
    q_sql &= (db.page_counter.day == ts.day)
    q_sql &= (db.page_counter.hour == ts.hour)
    pc = pc_model.select( q_sql ).first()
    if pc:
        sql = 'update page_counter set views = views + 1 where id = %d' % pc.id
        db.executesql( sql )
    else:
        pc_model.insert( dict( path_info=path_info,
                               year=ts.year,
                               month=ts.month,
                               day=ts.day,
                               hour=ts.hour ) )


_SKIP_LIST = [ '/auth_event_viewer',
               '/bang',
               '/block/',
               '/cronjobs/',
               '/default/error/',
               '/default/bang/',
               '/default/download/',
               '/default/set_session_anon/',
               '/default/user/',
               '/download/',
               '/lang/',
               '/page/',
               '/page_stats/',
               '/set_session_',
               '/user_admin',
               ]

def update_page_log( db=None ):
    if not current.remote_ip:
        return

    if not db:
        db = current.db
    request = current.request
    user_agent = request.user_agent()
    if user_agent.bot:
        term.printLog( 'Skipping bot: %s' % repr( request.env.http_user_agent ))
        return

    pl_model = db_tables.get_table_model( 'page_log', db=db )
    path_info = env.get_path_info()
    if path_info.startswith( '/' + current.app_name ):
        path_info = path_info[ 4 : ]
    if not path_info:
        term.printLog( 'empty path_info', print_trace=True )
        path_info = '/'
    if path_info.startswith( '/default/index' ):
        path_info = '/'

    for s in _SKIP_LIST:
        if path_info.startswith( s ) or path_info == s[ : -1 ]:
            return

    auth_user_id = user_factory.get_auth_user_id( db=db )
    data = Storage( path_info=path_info,
                    ts=DT.now(),
                    client_ip=current.remote_ip,
                    auth_user_id=auth_user_id,
                    is_tablet=user_agent.is_tablet,
                    is_mobile=user_agent.is_mobile )
    if user_agent.os:
        data.os_name = user_agent.os.name
    if user_agent.browser:
        data.browser_name = user_agent.browser.name
        data.browser_version = user_agent.browser.version
    pl_model.insert( data )


def get_page_views( limit=None, db=None ):
    '''

    :param db:
    :return: [ (path_info, count(*) ]
    '''
    if not db:
        db = current.db
    sql = '''
        select 
            path_info, 
            count( distinct client_ip) as total
        from page_log 
        group by path_info 
        order by total desc'''
    if limit:
        sql += '''
        limit %(l)s
        ''' % dict( l=limit )
    rows = db.executesql( sql, as_dict=True )
    pv_list = []
    for row in rows:
        r = Storage( row )
        page = page_factory.get_page( url=r.path_info )
        r.page_name = page.name
        pv_list.append( r )

    return pv_list


def get_page_views_daily( path_info, ts, limit=None, db=None ):
    '''

    :param db:
    :return: [ (path_info, count(*) ]
    '''
    if not db:
        db = current.db
    sql = '''
        select 
            min( ts ) as min_ts,
            max( ts ) as max_ts,
            extract( year from ts ) as year, 
            extract( month from ts ) as month, 
            extract( day from ts ) as day, 
            count( distinct client_ip ) as total 
        from page_log 
        where 
            path_info = '%(path_info)s' and
            ts < '%(ts)s' 
        group by year, month, day 
        order by year desc, month desc, day desc''' % dict( path_info=path_info, ts=str( ts ) )
    if limit:
        sql += '''
        limit %(l)s''' % dict( l=limit )
    term.printDebug( 'sql: %s' % sql )
    rows = db.executesql( sql, as_dict=True )
    pv_list = [ Storage( r ) for r in rows ]
    pv_list.reverse()
    return pv_list

