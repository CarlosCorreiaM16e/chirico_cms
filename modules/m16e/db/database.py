# -*- coding: utf-8 -*-


import datetime
import sys
import traceback
from psycopg2 import Error, errorcodes

from gluon import current, Field
from gluon.storage import Storage
from m16e import term
from m16e.kommon import format_exception

DEFAULT_CACHE_TIME = 0 # no cache
AUX_TABLES_CACHE_TIME = 30 # 30 seconds
DEFAULT_CACHEABLE = True

DBERR_FK_EXISTS = errorcodes.FOREIGN_KEY_VIOLATION
DBERR_UNIQUE_VIOLATION = errorcodes.UNIQUE_VIOLATION

#------------------------------------------------------------------
class DatabaseException( Exception):
    pass


def database_exists( db_name, db=None ):
    if not db:
        db = current.db
    sql = '''
        SELECT count( * ) FROM pg_database
            WHERE datname = '%s' and datistemplate = false
            ''' % db_name
    # term.printDebug( 'sql: %s' % sql )
    rows = db.executesql( sql )
    # term.printDebug( 'rows: %s' % repr( rows ) )
    count = 0
    if rows:
        # term.printDebug( 'rows[0]: %s' % repr( rows[0] ) )
        count = rows[0][0]
        # term.printDebug( 'table: %s; count: %d' % (table, count ) )
    return (count > 0)


def table_exists( table, db=None ):
    if not db:
        db = current.db
    sql = '''
        SELECT count( * ) FROM information_schema.tables
            WHERE
                table_schema='public' AND
                table_name like( '%(table)s' )
    ''' % { 'table': table }
    # term.printDebug( 'sql: %s' % sql )
    rows = db.executesql( sql )
    # term.printDebug( 'rows: %s' % repr( rows ) )
    count = 0
    if rows:
        # term.printDebug( 'rows[0]: %s' % repr( rows[0] ) )
        count = rows[0][0]
        # term.printDebug( 'table: %s; count: %d' % (table, count ) )
    return (count > 0)


def get_table_names( db=None ):
    if not db:
        db = current.db
    sql = '''
        SELECT table_name 
        FROM information_schema.tables 
        WHERE table_type = 'BASE TABLE' AND table_schema = 'public' 
        ORDER BY table_type, table_name'''
    rows = db.executesql( sql, as_dict = True )
    table_names = [row[ 'table_name' ] for row in rows]
    return table_names


def column_exists( table, column, db=None ):
    if not db:
        db = current.db
    sql = '''
        SELECT count(*) from information_schema.columns
        where table_name='%(table)s' and column_name='%(column)s'
    ''' % { 'table': table, 'column': column }
#    term.printDebug( 'sql: %s' % repr( sql ) )
    rows = db.executesql( sql )
#    term.printDebug( 'rows: %s' % repr( rows ) )
    count = 0
    if rows:
#        term.printDebug( 'rows[0]: %s' % repr( rows[0] ) )
        count = rows[0][0]
#    term.printDebug( 'table: %s; col: %s; count: %d' % (table, column, count ) )
    return (count > 0)


def index_exists( table, idx_name, db=None ):
    if not db:
        db = current.db
    sql = '''
        select
            t.relname as table_name,
            i.relname as index_name,
            a.attname as column_name
        from
            pg_class t,
            pg_class i,
            pg_index ix,
            pg_attribute a
        where
            t.oid = ix.indrelid
            and i.oid = ix.indexrelid
            and a.attrelid = t.oid
            and a.attnum = ANY(ix.indkey)
            and t.relkind = 'r'
            and t.relname like ( %(table)s )
            and i.relname like ( %(idx_name)s )
        order by
            t.relname,
            i.relname;

    '''
    d = { 'table': table, 'idx_name': idx_name }
    rows = db.executesql( sql, placeholders=d  )
    return rows


def sequence_exists( seq_name, db=None ):
    if not db:
        db = current.db
    sql = 'select count( * ) from pg_class where relname like( %(seq_name)s )'
    rows = db.executesql( sql, placeholders={ 'seq_name': seq_name } )
    # term.printDebug( 'rows: %s' % repr( rows ) )
    count = 0
    if rows:
        # term.printDebug( 'rows[0]: %s' % repr( rows[0] ) )
        count = rows[0][0]
        # term.printDebug( 'table: %s; count: %d' % (seq_name, count ) )
    return (count > 0)


def get_sequence_names( db ):
    sql = '''
        select c.relname
        from pg_catalog.pg_class c
            LEFT JOIN pg_catalog.pg_namespace n ON n.oid = c.relnamespace
        where c.relkind = 'S' and n.nspname like( 'public' )
    '''
    rows = db.executesql( sql, as_dict = True )
    seq_names = [row[ 'relname' ] for row in rows]
    return seq_names


def constraint_exists( constraint_name, db=None ):
    if not db:
        db = current.db
    sql = '''
        SELECT count(*) from pg_constraint WHERE conname = %(conname)s
    '''
    rows = db.executesql( sql, placeholders={ 'conname': constraint_name } )
    count = 0
    if rows:
        count = rows[0][0]
    return (count > 0)


def fetch_record_by_id( table_name, record_id, db=None ):
    if not db:
        db = current.db
    sql = '''
        select * from %(table_name)s
        where id = %(id)s
    ''' % { 'table_name': table_name,
            'id': record_id }
    rows = db.executesql( sql, as_dict=True )
    record = None
    if rows:
        record = Storage( rows[0] )
    return record


class DbBaseTable( object ):
    table_name = '???'
    default_result_limit = 200
    primarykey = None

    def __init__( self, db, track_history=False, print_query=False ):
        self.T = current.T
        self.db = db
        self.db_table = None
        self.fields = None
        self.validators = None
        self.labels = None
        self.widgets = None
        self.visibility = None
        self.track_history = track_history
        self.define_table()
        self.print_query = print_query


    def define_table( self ):
#         term.printDebug( repr( self.db.tables ) )
        if self.table_name in self.db.tables:
            return

#        term.printDebug( repr( self.db.tables ) )
        if not self.fields:
            self.fields = self.get_fields()

#        term.printDebug( repr( self.db.tables ) )
#        term.printDebug( repr( self.fields ) )
        if self.primarykey:
            self.db.define_table( self.table_name,
                                  *self.fields,
                                  primarykey=self.primarykey,
                                  migrate=False )
        else:
            self.db.define_table( self.table_name, *self.fields, migrate=False )
        self.db_table = self.db[ self.table_name ]
#        term.printDebug( repr( self.db.tables ) )
#         term.printDebug( 'track_history: %s' % self.track_history )
        if self.track_history:
            h_fields = [
                Field( 'auth_user_id', 'reference auth_user', ondelete = 'NO ACTION' ),
                Field( 'when_happened', 'datetime', default = datetime.datetime.now() ),
                Field( 'operation', 'string', notnull=True ),
                Field( '%s_id' % self.table_name, 'reference %s' % self.table_name, notnull=True ) ]
            for f in self.fields:
                f_name = 'o_%s' % f.name
                if f.type.startswith( 'reference ' ):
                    field = Field( f_name,
                                   f.type,
                                   default=f.default,
                                   notnull=f.notnull,
                                   ondelete = 'NO ACTION' )
                else:
                    field = Field( f_name,
                                   f.type,
                                   default=f.default,
                                   notnull=f.notnull )
                h_fields.append( field )
            self.db.define_table( '%s_history' % self.table_name, *h_fields,
                                  migrate=False )
#         term.printDebug( repr( self.db.tables ) )


    def get_fields( self ): return []
    def get_validators( self ): return {}
    def get_labels( self ): return {}
    def get_widgets( self ): return {}
    def get_visibility( self ): return {}


    def get_field_names( self ):
        return [ f.name for f in self.fields ]


    def get_default_attribute( self, attr_name ):
        if attr_name == 'fields':
            if not self.fields:
                self.fields = self.get_fields()
            return self.fields

        if attr_name == 'validators':
            if not self.validators:
                self.validators = self.get_validators()
            return self.validators

        if attr_name == 'labels':
            if not self.labels:
                self.labels = self.get_labels()
            return self.labels

        if attr_name == 'widgets':
            if not self.widgets:
                self.widgets = self.get_widgets()
            return self.widgets

        if attr_name == 'visibility':
            if not self.visibility:
                self.visibility = self.get_visibility()
            return self.visibility


    def get_orderby( self, orderby ):
        return orderby


    def __getitem__( self, o_id ):
        # term.printDebug( 'o_id: %s (type: %s)' % ( repr( o_id ), type( o_id ) ) )
        try:
            i_id = int( o_id or 0)
            item = self.select_by_id( i_id ) #, print_query=True )
            # term.printDebug( 'item: %s' % repr( item ) )
            return item
        except:
            t, v, tb = sys.exc_info()
            traceback.print_exception( t, v, tb )
            raise TypeError( 'Bad type (%s) for data: %s' %
                             (type( o_id ), repr( o_id )) )
#         return db( db[ self.table_name ].id.belongs( o_id ) ).select()

    #------------------------------------------------------------------
    def get_record_by( self,
                       field_name,
                       value,
                       orderby=None,
                       print_query=None ):
        db = self.db
        q = (db[ self.table_name ][ field_name ] == value)
        return self.select( q,
                            orderby=orderby,
                            print_query=print_query ).first()

    #------------------------------------------------------------------
    def select_by_id( self,
                      fld_id,
                      cache_results=-1,
                      offset=0,
                      limit=1,
                      cacheable=False,
                      print_query=None ):
        db = self.db
        q = (db[ self.table_name ].id == fld_id)
        item = self.select( q,
                            cache_results=cache_results,
                            offset=offset,
                            limit=limit,
                            cacheable=cacheable,
                            print_query=print_query ).first()
#         term.printDebug( 'item: %s' % repr( item ) )
        return item

    #------------------------------------------------------------------
    def select( self,
                query=None,
                cache_results=-1,
                offset=0,
                limit=0,
                distinct=None,
                cacheable=False,
                orderby=None,
                raw_orderby=None,
                deleted=False,
                print_query=None ):
        '''
        cache results by default for DEFAULT_CACHE_TIME (0 seconds) if table not in
        current.AUX_TABLES or
        for AUX_TABLES_CACHE_TIME (30 seconds) in case of an auxilliary table,
        call with cache_results=False|None|0
        to force DB read
        limit:
           0: no limit
          -1: default limit
        '''
        db = self.db
        db_table = db[ self.table_name ]
        aux_tables = None
        if print_query is None:
            print_query = self.print_query
        try:
            aux_tables = current.AUX_TABLES
        except:
            pass
        if limit < 0:
            limit = self.default_result_limit
        if not query:
            if self.primarykey:
                fld = self.primarykey[0]
            else:
                fld = 'id'

            query = (db_table[ fld ] > 0)
        cache = current.cache
#         term.printDebug( 'cache_results: %s' % ( repr( cache_results ) ) )
        if cache_results < 0:
            if aux_tables and (aux_tables == '*' or self.table_name in aux_tables):
                cache_results = AUX_TABLES_CACHE_TIME
            else:
                cache_results = DEFAULT_CACHE_TIME
#         term.printDebug( 'cache_results: %s' % ( repr( cache_results ) ) )
        if 'is_deleted' in db_table.fields:
            query &= (db_table.is_deleted == deleted)

        cache_cfg = (cache.ram, cache_results)
        limitby = False
        if offset or limit:
            limitby = (offset, limit)
        if not orderby:
            if self.primarykey:
                orderby = ', '.join( self.primarykey )
            else:
                orderby = 'id'
        if raw_orderby:
            orderby_str = raw_orderby
        else:
            orderby_str = self.get_orderby( orderby )
        if print_query:
            term.printDebug( self.db( query )._select( db_table.ALL,
                                                       cache=cache_cfg,
                                                       cacheable=cacheable,
                                                       limitby=limitby,
                                                       orderby=orderby_str,
                                                       distinct=distinct ),
                             print_trace=True )
#         term.printDebug( 'orderby_str: %s' % ( repr( orderby_str ) ) )
        result = self.db( query ).select( db_table.ALL,
                                          cache=cache_cfg,
                                          cacheable=cacheable,
                                          limitby=limitby,
                                          orderby=orderby_str,
                                          distinct=distinct )
#         term.printDebug( 'result: %s' % ( repr( result ) ) )
#         if result:
#             term.printDebug( 'result[0]: %s' % ( repr( result[0] ) ) )
        return result

    #------------------------------------------------------------------
    def update_and_reload_by_id( self,
                                 fld_id,
                                 upd,
                                 track_history=True,
                                 print_query=None ):
        db = self.db
        q = (db[ self.table_name ].id == fld_id)
        return self.update_and_reload( q,
                                       upd,
                                       track_history=track_history,
                                       print_query=print_query ).first()

    #------------------------------------------------------------------
    def update_and_reload( self,
                           query,
                           upd,
                           track_history=True,
                           print_query=None ):
        db = self.db
        try:
            self.update( query,
                         upd,
                         track_history=track_history,
                         print_query=print_query )
        except Error as e:
            t, v, tb = sys.exc_info()
            traceback.print_exception( t, v, tb )
            term.printLog( '\nexception type: %s\n  exception: %s\n    pgerror: %s\n    pgcode: %s\n    args: %s' %
                           ( type( e ),
                             repr( e ),
                             e.pgerror,
                             e.pgcode,
                             e.args ) )
            term.printLog( 'EXCEPTION:\n%s' % format_exception( e ) )
            raise
#         term.printDebug( 'sql: %s' % db._lastsql )
#         term.printDebug( 'update record: %s\n--> with: %s' %
#                          ( repr( query ), repr( upd ) ) )
        return self.select( query, cache_results=0, limit=0 )

    #------------------------------------------------------------------
    def update_by_id( self,
                      fld_id,
                      upd,
                      print_query=None,
                      track_history=True ):
        db = self.db
        q = (db[ self.table_name ].id == fld_id)
        result = self.update( q,
                              upd,
                              print_query=print_query,
                              track_history=track_history )
        return result


    def insert_or_update( self, upd, print_query=None ):
        u_id = upd.get( 'id' )
        if not u_id:
            u_id = self.insert( upd, print_query=print_query )
        else:
            del u_id[ 'id' ]
            self.update_by_id( u_id, upd )
        record = self.select_by_id( u_id )
        return record


    def update_history( self, query, operation ):
        db = self.db
        session = current.session
        auth = session.auth
        try:
            if self.track_history:
                rows = db( query ).select()
                for r in rows:
                    htable = self.table_name + '_history'
                    h_upd = { 'auth_user_id': auth.user.id,
                              'when_happened': datetime.datetime.now(),
                              'operation': operation,
                              '%s_id' % self.table_name: r.id }
                    for f in self.fields:
                        if f == 'id':
                            continue
                        f_name = 'o_%s' % f.name
                        h_upd[ f_name ] = r[ f ]
                    db[ htable ].insert( **h_upd )

        except Error as e:
            t, v, tb = sys.exc_info()
            traceback.print_exception( t, v, tb )
            term.printLog( '\nexception type: %s\n  exception: %s\n    pgerror: %s\n    pgcode: %s\n    args: %s' %
                           ( type( e ),
                             repr( e ),
                             e.pgerror,
                             e.pgcode,
                             e.args ) )
            term.printLog( 'EXCEPTION:\n%s' % format_exception( e ) )
            raise

    #------------------------------------------------------------------
    def update( self,
                query,
                upd,
                print_query=None,
                track_history=True ):
        db = self.db
        if print_query is None:
            print_query = self.print_query
        if print_query:
            term.printDebug( 'query: %s\nupd: %s' % (str( query ), upd ) )
            term.printDebug( 'sql: ' + db( query )._update( **upd ), print_trace=True )
        result = None
        try:
            if self.track_history and track_history:
                self.update_history( query, 'u' )
            result = db( query ).update( **upd )

        except Error as e:
            t, v, tb = sys.exc_info()
            traceback.print_exception( t, v, tb )
            term.printLog( '\nexception type: %s\n  exception: %s\n    pgerror: %s\n    pgcode: %s\n    args: %s' %
                             ( type( e ),
                               repr( e ),
                               e.pgerror,
                               e.pgcode,
                               e.args ) )
            term.printLog( 'EXCEPTION:\n%s' % format_exception( e ) )
            raise
        return result

    #------------------------------------------------------------------
    def delete_by_id( self,
                      fld_id,
                      print_query=None,
                      track_history=True,
                      purge_history=False ):
        db = self.db
        q = (db[ self.table_name ].id == fld_id)
        result = None
        try:
            result = self.delete( q,
                                  print_query=print_query,
                                  track_history=track_history,
                                  purge_history=purge_history )
        except Error as e:
            t, v, tb = sys.exc_info()
            traceback.print_exception( t, v, tb )
            term.printLog( '\nexception type: %s\n  exception: %s\n    pgerror: %s\n    pgcode: %s\n    args: %s' %
                             ( type( e ),
                               repr( e ),
                               e.pgerror,
                               e.pgcode,
                               e.args ) )
            term.printLog( 'EXCEPTION:\n%s' % format_exception( e ) )
            raise
        return result

    #------------------------------------------------------------------
    def delete( self,
                query,
                print_query=None,
                print_trace=False,
                track_history=True,
                purge_history=False ):
        upd = {}
        db = self.db
        if print_query is None:
            print_query = self.print_query
        if 'is_deleted' in self.db[ self.table_name ].fields and not purge_history:
#             term.printDebug( 'set record deleted: %s' % ( repr( query ) ) )
            upd = { 'is_deleted': True }
            for fld in self.db[ self.table_name ].fields:
                if fld in [ 'id', 'is_deleted' ]:
                    continue
                upd[ fld ] = self.db[ self.table_name ][ fld ].default
            return self.update_and_reload( query, upd )
#         term.printDebug( 'delete record: %s' % ( repr( query ) ) )
        result = None
        try:
            if self.track_history and track_history and not purge_history:
                self.update_history( query, 'd' )
            if print_query:
                term.printDebug( self.db( query )._delete(), print_trace=print_trace )
            result = db( query ).delete()
        except Error as e:
            t, v, tb = sys.exc_info()
            traceback.print_exception( t, v, tb )
            term.printLog( '\nexception type: %s\n  exception: %s\n    pgerror: %s\n    pgcode: %s\n    args: %s' %
                           ( type( e ),
                             repr( e ),
                             e.pgerror,
                             e.pgcode,
                             e.args ) )
            term.printLog( 'EXCEPTION:\n%s' % format_exception( e ) )
            raise
        return result

    #------------------------------------------------------------------
    def insert( self, upd, print_query=None ):
        db = self.db
        if print_query is None:
            print_query = self.print_query
        if 'is_deleted' in self.db[ self.table_name ].fields:
            deleted = self.select( deleted=True ).first()
            if deleted:
#                 term.printDebug( 'updating: %s\nwith: %s' %
#                                  ( repr( deleted ), repr( upd ) ) )
                upd[ 'is_deleted' ] = False
                for fld in db[ self.table_name ].fields:
                    if fld not in [ 'id', 'is_deleted' ] \
                    and fld not in upd:
                        upd[ fld ] = db[ self.table_name ][ fld ].default
                q = (db[ self.table_name ].id == deleted.id)
                rec = self.update_and_reload( q, upd ).first()
                return rec.id
        # term.printDebug( 'inserting: %s' % ( repr( upd ) ) )
        result = None
        try:
            if print_query:
                term.printDebug( db[ self.table_name ]._insert( **upd ), print_trace=True )
            # term.printDebug( 'sql: %s' % ( repr( db[ self.table_name ]._insert( **upd ) ) ) )
            result = db[ self.table_name ].insert( **upd )
#         term.printDebug( 'sql: %s' % ( repr( db._lastsql ) ) )
        except Error as e:
            t, v, tb = sys.exc_info()
            traceback.print_exception( t, v, tb )
            term.printLog( '\nexception type: %s\n  exception: %s\n    pgerror: %s\n    pgcode: %s\n    args: %s' %
                           ( type( e ),
                             repr( e ),
                             e.pgerror,
                             e.pgcode,
                             e.args ) )
            term.printLog( 'EXCEPTION:\n%s' % format_exception( e ) )
            raise
        return result

    #------------------------------------------------------------------
    def count( self,
               query=None,
               deleted=False,
               print_query=None ):
        '''
        cache results by default for DEFAULT_CACHE_TIME (30) seconds,
        call with cache_results=False|None|0
        to force DB read
        '''
        db = self.db
        if print_query is None:
            print_query = self.print_query

        if not query:
            query = (db[ self.table_name ].id > 0)
        if 'is_deleted' in db[ self.table_name ].fields:
            query &= (db[ self.table_name ].is_deleted == deleted)

        if print_query:
            term.printDebug( db( query )._count(),
                             print_trace=True )
#         term.printDebug( 'orderby_str: %s' % ( repr( orderby_str ) ) )
        return db( query ).count()

    #------------------------------------------------------------------
    def to_dict( self, record_id=None, record=None ):
        db = self.db
        if not record:
            record = self.select_by_id( record_id )
        d = Storage()
        for fld in db[ self.table_name ].fields:
            d[ fld ] = str( record[ fld ] )
        return d

    #------------------------------------------------------------------
