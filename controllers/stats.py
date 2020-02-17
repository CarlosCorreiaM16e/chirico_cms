# -*- coding: utf-8 -*-

import datetime


import m16e.term as term

from m16e.kommon import *
from m16e.ktfact import *

from m16e.db.querydata import QueryData

import m16e.table_factory_with_session as tfact

DT = datetime.datetime
DATE = datetime.date

ACT_BACK = 'back'
ACT_CLEAR = 'clear'

KQV_VISIT_ID = 'qv_visit_id'
KQV_IP = 'qv_ip'
KQV_SHOW_MOBILE = 'qv_show_mobile'
KQV_SHOW_ME = 'qv_show_me'

tdef = {
    KTF_COL_ORDER: [
        'sv_id', 'pv_id', 'ip', 'visit_ts', 'page_visit_ts',
        'auth_user_id',
        'client_os_name', 'client_os_version',
        'client_flavor_name', 'client_flavor_version',
        'client_browser_name', 'client_browser_version',
        'client_is_mobile', 'client_is_tablet',
        'client_user_agent',
        'path_info', 'query_string' ],
    KTF_SORTABLE_COLS: [
        'sv_id', 'pv_id', 'ip', 'visit_ts', 'page_visit_ts',
        'auth_user_id',
        'client_os_name', 'client_os_version',
        'client_flavor_name', 'client_flavor_version',
        'client_browser_name', 'client_browser_version',
        'client_is_mobile', 'client_is_tablet',
        'client_user_agent',
        'path_info', 'query_string' ],
    KTF_CELL_CLASS: 'table_border small',
    KTF_COLS: {
        'sv_id': { KTF_TITLE: T( 'Visit #' ), KTF_TYPE: KDT_INT },
        'pv_id': { KTF_TITLE: T( 'Page vis. #' ), KTF_TYPE: KDT_INT },
        'ip': { KTF_TITLE: T( 'IP' ), KTF_TYPE: KDT_CHAR },
        'visit_ts': { KTF_TITLE: T( 'Site ts' ), KTF_TYPE: KDT_TIMESTAMP },
        'page_visit_ts': { KTF_TITLE: T( 'Page ts' ), KTF_TYPE: KDT_TIMESTAMP },
        'auth_user_id': { KTF_TITLE: T( 'User Id' ), KTF_TYPE: KDT_INT },
        'path_info': { KTF_TITLE: T( 'Path' ), KTF_TYPE: KDT_CHAR },
        'query_string': { KTF_TITLE: T( 'Query' ), KTF_TYPE: KDT_CHAR },
        'client_os_name': { KTF_TITLE: T( 'OS name' ), KTF_TYPE: KDT_CHAR },
        'client_os_version': { KTF_TITLE: T( 'OS version' ), KTF_TYPE: KDT_CHAR },
        'client_flavor_name': { KTF_TITLE: T( 'Flavor name' ), KTF_TYPE: KDT_CHAR },
        'client_flavor_version': { KTF_TITLE: T( 'Flavor version' ), KTF_TYPE: KDT_CHAR },
        'client_browser_name': { KTF_TITLE: T( 'Browser name' ), KTF_TYPE: KDT_CHAR },
        'client_browser_version': { KTF_TITLE: T( 'Browser version' ), KTF_TYPE: KDT_CHAR },
        'client_user_agent': { KTF_TITLE: T( 'User agent string' ), KTF_TYPE: KDT_CHAR },
        'client_is_mobile': { KTF_TITLE: T( 'Mobile' ), KTF_TYPE: KDT_BOOLEAN },
        'client_is_tablet': { KTF_TITLE: T( 'Mobile' ), KTF_TYPE: KDT_BOOLEAN },
    }
}

qdata = {
    KTF_BUTTONS: [
        { KTF_NAME: 'action', KTF_TITLE: T( 'Clear' ), KTF_VALUE: 'clear',
            KTF_CSS_CLASS: 'sel_bt' },
        { KTF_NAME: 'action', KTF_TITLE: T( 'Submit' ), KTF_VALUE: 'submit' } ],
    KTF_COL_ORDER: [ KQV_IP, KQV_DATE_SINCE, KQV_DATE_UNTILL, KQV_SHOW_MOBILE,
                     KQV_SHOW_ME ],
    KTF_COLS: {
        KQV_IP: { KTF_TITLE: T( 'IP' ), KTF_TYPE: KDT_CHAR },
        KQV_DATE_SINCE: { KTF_TITLE: T( 'Since' ), KTF_TYPE: KDT_TIMESTAMP, },
        KQV_DATE_UNTILL: { KTF_TITLE: T( 'Untill' ), KTF_TYPE: KDT_TIMESTAMP, },
        KQV_SHOW_MOBILE: { KTF_TITLE: T( 'Show mobile' ), KTF_TYPE: KDT_BOOLEAN, },
        KQV_SHOW_ME: { KTF_TITLE: T( 'Show me' ), KTF_TYPE: KDT_BOOLEAN, },
    },
}

#------------------------------------------------------------------
def getUserQueryData():
    return QueryData()

#------------------------------------------------------------------
def getDynQueryData():
    term.printLog( 'session.svars: ' + repr( session.svars ) )
    qd = QueryData()

    if session.svars[ KQV_VISIT_ID ]:
        qd.addAnd( QueryData( 's.id = %(visit_id)s',
                              { 'visit_id': session.svars[ KQV_VISIT_ID ] } ) )
    term.printLog( repr( qd ) )

    ip = session.svars[ KQV_IP ]
    if ip:
        term.printLog( repr( ip ) )
        ip = ip.replace( '*', '%%' )
        if ip.startswith( '!' ):
            qd.addAnd( QueryData( 'ip not like( %(ip)s )', { 'ip': ip[1:] } ) )
        else:
            qd.addAnd( QueryData( 'ip like( %(ip)s )', { 'ip': ip } ) )

    showMobile = session.svars[ KQV_SHOW_MOBILE ]
    if showMobile:
        qd.addAnd( QueryData( 'client_is_mobile or client_is_tablet' ) )

    showMe = session.svars[ KQV_SHOW_ME ]
    if not showMe:
        qdShow = QueryData( 'auth_user_id != 1 or auth_user_id is null' )
        qdShow.addAnd( QueryData( "ip not like( '192.%%') " ) )
        qd.addAnd( qdShow )

    if session.svars[ KQV_DATE_SINCE ]:
        qd.addAnd(
            QueryData(
                'visit_ts >= %(start_date)s',
                { 'start_date': session.svars[ KQV_DATE_SINCE ] } ) )

    if session.svars[ KQV_DATE_UNTILL ]:
        qd.addAnd(
            QueryData(
                'visit_ts <= %(stop_date)s',
                { 'stop_date': session.svars[ KQV_DATE_UNTILL ] } ) )

    term.printLog( repr( qd ) )
    return qd

#------------------------------------------------------------------
def getQueryData():
    qd = getDynQueryData()
    qd.addAnd( getUserQueryData() )
#    term.printDebug( repr( qd ) )
    return qd

#------------------------------------------------------------------
def getList( qd ):
    query = '''
        select
            s.id as sv_id,
            p.id as pv_id,
            page_visit_ts,
            path_info,
            query_string,
            visit_ts,
            ip,
            auth_user_id,
            client_os_name,
            client_browser_name,
            client_browser_version,
            client_is_mobile,
            client_is_tablet,
            client_os_version,
            client_flavor_name,
            client_flavor_version,
            client_user_agent
            from page_visit p
                join site_visit s on p.site_visit_id = s.id
    '''
    if qd.where:
        query += ' where (' + qd.where + ')'
    if qd.order:
        query += ' order by ' + qd.order
    if qd.limit:
        query += ' limit %d ' % (qd.limit)
    if qd.offset:
        query += ' offset %d ' % (qd.offset)

    rows = db.executesql( query, placeholders = qd.args, as_dict = True )
    term.printDebug( 'sql: ' + db._lastsql )
    return rows

#------------------------------------------------------------------
def getListCount( qd ):
    term.printLog( 'qd: %s' % ( repr( qd ) ) )
    query = '''
        select
            count( * )
            from page_visit p
                join site_visit s on p.site_visit_id = s.id
    '''
    if qd.where:
        query += ' where (' + qd.where + ')'
    term.printLog( 'query: ' + query )
    term.printLog( 'args: ' + repr( qd.args ) )
    recCount = db.executesql( query, placeholders = qd.args )
    term.printLog( 'sql: ' + db._lastsql )
    return recCount[0][0]

#------------------------------------------------------------------
@auth.requires_membership( 'admin' )
def index():
    term.printLog( 'request.args: %s\n' % ( repr( request.args ) ) )
    term.printLog( 'request.vars: %s\n' % ( repr( request.vars ) ) )
    session.svars = Storage()
    session.svars[ KQV_LIMIT ] = 20
    session.svars[ KQV_OFFSET ] = 0
    orderBy = (tdef[ KTF_SORTABLE_COLS ].index( 'pv_id' ) + 1) * (-1)
    visitId = request.args( 0 )
    if visitId:
        session.svars[ KQV_VISIT_ID ] = int( visitId )
    redirect( URL( r = request, f = 'list', vars = { KQV_ORDER: orderBy } ) )

#------------------------------------------------------------------
@auth.requires_membership( 'admin' )
def list():
    term.printLog( 'request.args: %s\n' % ( repr( request.args ) ) )
    term.printLog( 'request.vars: %s\n' % ( repr( request.vars ) ) )
    term.printLog( 'request.get_vars: %s\n' % ( repr( request.get_vars ) ) )
    term.printLog( 'request.post_vars: %s\n' % ( repr( request.post_vars ) ) )
    term.printLog( 'session.svars: %s\n' % ( repr( session.svars ) ) )
    term.printLog( 'session.kvars: %s\n' % ( repr( session.kvars ) ) )

    vars = tfact.requestToSession(
        qdata, session.svars,
        request.args, request.get_vars, request.post_vars )

    session.svars = vars
    term.printLog( 'session.svars: %s' % ( repr( session.svars ) ) )
    if not session.svars[ KQV_ORDER ]:
        session.svars[ KQV_ORDER ] = tdef[ KTF_SORTABLE_COLS ].index( 'doc_date' ) + 1
    term.printLog( 'session.svars: %s' % ( repr( session.svars ) ) )

    action = request.post_vars.action
    term.printLog( 'action: ' + repr( action ) )

    if action == ACT_CLEAR:
        for n in qdata[ KTF_COL_ORDER ]:
            session.svars[ n ] = None

    opvars = Storage()
    opvars[ KQV_IP ] = session.svars[ KQV_IP ]
    opvars[ KQV_DATE_SINCE ] = session.svars[ KQV_DATE_SINCE ]
    opvars[ KQV_DATE_UNTILL ] = session.svars[ KQV_DATE_UNTILL ]
    opvars[ KQV_SHOW_MOBILE ] = session.svars[ KQV_SHOW_MOBILE ]
    opvars[ KQV_SHOW_ME ] = session.svars[ KQV_SHOW_ME ]

    term.printLog( 'opvars: %s' % ( repr( opvars ) ) )

#    term.printLog( 'session.svars: %s' % ( repr( session.svars ) ) )
    qd = getQueryData()

    qd.offset = session.svars[ KQV_OFFSET ]
    qd.limit = session.svars[ KQV_LIMIT ]

#    term.printLog( 'qd: %s' % ( repr( qd ) ) )
    qd.order = tfact.getOrderBy( tdef, session.svars[ KQV_ORDER ], 'pv_id' )
#    term.printLog( 'qd: %s' % ( repr( qd ) ) )

    term.printLog( 'session.svars: %s' % ( repr( session.svars ) ) )
    recCount = getListCount( qd )

    term.printLog(
        'recCount: %s \nqd: %s' %
        (repr(recCount), repr( qd )) )
    if session.svars[ KQV_OFFSET ] > recCount:
        session.svars[ KQV_OFFSET ] = 0
    rows = getList( qd )
    for row in rows:
        if row[ 'path_info' ].startswith( '/%s/default/user' % APP_NAME ):
            row[ KTF_ROW_CLASS ] = 'possible_break_in'

    div = DIV()
    div.append( H5( T( 'Detailed stats' ) ) )
    form = FORM()
    table = tfact.getTable(
        tdef, rows,
        controller = 'stats', function = 'list',
        order = session.svars[ KQV_ORDER ] )
    term.printDebug( 'qdata: %s' % ( repr( qdata ) ) )
    optTable = tfact.getNavOptions(
        T, recCount, qdata, opvars,
        session.svars[ KQV_OFFSET ] or 0,
        session.svars[ KQV_LIMIT ] or 20,
        width = 4,
        functionName = 'list',
        titleCssClass = 'small w10pct',
        cellCssClass = 'small w15pct' )
#    term.printLog( 'optTable: %s' % ( optTable.xml() ) )
    form.append( optTable )
    form.append( table )
#    term.printLog( 'form: %s' % ( form.xml() ) )
    div.append( form )

#    term.printLog( 'div: %s' % ( div.xml() ) )
#    if form.accepts( request.vars, session, dbio = False ):
#        term.printLog( 'form.vars: %s' % repr( form.vars ) )
#        redirect( URL( r = request, f = 'list', args = page, vars = upd ) )

#    term.printLog( 'div: %s' % ( div.xml() ) )
    return dict( statlist = div )

