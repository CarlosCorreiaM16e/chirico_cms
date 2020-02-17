# -*- coding: utf-8 -*-
# this file is released under public domain and you can use without limitations

from m16e.db import db_tables
from gluon import current
from gluon.html import URL, DIV, H3, FORM, TABLE, TR, TD, A, IMG
from gluon.storage import Storage
from m16e import term
from m16e.db.querydata import QueryData
from m16e.views.plastic_view import BaseListPlasticView

ACT_NEW_ATTACH = 'new_attach'

#------------------------------------------------------------------
class GalleryIndexView( BaseListPlasticView ):
    def __init__( self, db ):
        super( GalleryIndexView, self ).__init__( db )
        self.table_model = db_tables.get_table_model( 'attach', db=db )

    #------------------------------------------------------------------
    def process( self ):
        #------------------------------------------------------------------
        def getQueryData( cols, rows, page ):
            #------------------------------------------------------------------
            def get_user_query_data():
                return QueryData()
            #------------------------------------------------------------------
            def get_dyn_query_data( cols, rows, page ):
#                term.printLog( 'session.svars: ' + repr( session.svars ) )
#                 qd = QueryData( 'is_site_image = true' )
                qd = QueryData( "mt.mt_name like( 'image/%' )" )
                qd.limit = cols * rows
                qd.offset = (page - 1) * qd.limit

                term.printLog( repr( qd ) )
                return qd
            #------------------------------------------------------------------
            qd = get_user_query_data()
            qd.addAnd( get_dyn_query_data( cols, rows, page ) )
            qd.order = 'filename'
            term.printDebug( repr( qd ) )
            return qd

        #------------------------------------------------------------------
        def getRecordList( qd ):
            query = '''
                select
                    a.id,
                    attach_type_id,
                    path,
                    filename,
                    attached,
                    short_description,
                    long_description,
                    created_on,
                    created_by,
                    mime_type_id,
                    is_site_image,
                    img_width,
                    img_height
                from attach a
                    join mime_type mt on a.mime_type_id = mt.id
            '''
            args = {}
            if qd:
                if qd.where:
                    query += ' where ' + qd.where
                if qd.order:
                    query += ' order by ' + qd.order
                if qd.limit:
                    query += ' limit %d' % (qd.limit)
                if qd.offset:
                    query += ' offset %d' % (qd.offset)
                if qd.args:
                    args = qd.args
            term.printLog( 'query: %s\nargs: %s' % ( query, repr( args ) ) )
            res = db.executesql( query, placeholders = args, as_dict = True )
#            term.printLog( 'sql: ' + db._lastsql )
            rows = []
            for r in res:
                rows.append( Storage( r ) )
            return rows

        #------------------------------------------------------------------
        def getRecordListCount( qd ):
            query = '''
                select count( * )
                from attach a
                    join mime_type mt on a.mime_type_id = mt.id
            '''
            args = {}
            if qd:
                if qd.where:
                    query += ' where ' + qd.where
                if qd.args:
                    args = qd.args
            term.printLog( 'query: %s\nargs: %s' % ( query, repr( args ) ) )
            rec_count = db.executesql( query, placeholders = args )
            term.printDebug( 'sql: %s' % str( db._lastsql ) )
            return rec_count[0][0]

        #------------------------------------------------------------------
        request = current.request
        response = current.response
        term.printLog( 'request.args: %s\n' % ( repr( request.args ) ) )
        term.printLog( 'request.vars: %s\n' % ( repr( request.vars ) ) )

        session = current.session
        T = current.T
        db = self.db
        auth = session.auth
        redirect = None

        page = 0
        cols = 6
        rows = 10
        if request.args:                    # page
            page = int( request.args( 0 ) )
        if request.vars:
            if request.vars.cols:
                cols = int( request.vars.cols )
            if request.vars.rows:
                rows = int( request.vars.rows )

        action = request.post_vars.action
        term.printLog( 'action: ' + repr( action ) )

        if action == ACT_NEW_ATTACH:
            redirect = URL( c = 'gallery', f = 'edit', args = [ 0 ] )

        qd = getQueryData( cols, rows, page )

        main_panel = ''
        rec_count = getRecordListCount( qd )
        term.printDebug( 'count: %d' % ( rec_count ) )
        if cols * rows * page > rec_count:
            redirect = URL( r=request, f='index', args=[page - 1] )
        else:
            data_rows = getRecordList( qd )
            main_panel = DIV()
            main_panel.append( H3( T( 'Gallery' ) ) )
            table = TABLE()
            for r in range( rows ):
                tr = TR()
                for c in range( cols ):
                    it = TABLE()
                    itr = TR()
                    ofs = (r * cols) + c
                    attached = ''
                    if ofs < len( data_rows ):
                        url = URL( c='default', f='download',
                                   args=[ data_rows[ ofs ].attached ] )
                        attached = IMG( _src=url )
                    itr.append( attached )
                    it.append( itr )
                    itr = TR()
                    cell = ''
                    if ofs < len( data_rows ):
                        url = URL( c='gallery', f='edit',
                                   args=[ data_rows[ ofs ].id ] )

                        cell = A( data_rows[ ofs ].filename, _href=url )
                    itr.append( TD( cell ) )
                    it.append( itr )
                    tr.append( TD( it ) )
                table.append( tr )

            bt_prev = ''
            if page:
                bt_prev = A( '<<', _class='btn',
                             _href=URL( c='gallery', f='index', args=[ page - 1 ] ) )
            bt_next = ''
            if rec_count > (page + 1) * rows * cols:
                bt_next = A( '>>', _class='btn',
                             _href=URL( c='gallery', f='index', args=[ page + 1 ] ) )
            bt_new = A( T( 'Add image' ), _class='btn',
                        _href=URL( c='gallery', f='edit', args=[0] ) )
            it = TABLE( _class='w100pct' )
            itr = TR()
            itr.append( TD( bt_prev, _class='w33pct text-left' ) )
            itr.append( TD( bt_new, _class='w33pct text-center' ) )
            itr.append( TD( bt_next, _class='w33pct text-right' ) )
            it.append( itr )
            table.append( TR( TD( it, _colspan=cols ) ) )

            form = FORM()
            form.append( table )
            main_panel.append( form )

        return Storage( dict=dict( main_panel=main_panel ),
                        redirect=redirect )

    #------------------------------------------------------------------
