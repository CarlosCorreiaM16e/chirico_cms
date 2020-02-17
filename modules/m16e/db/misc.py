# -*- coding: utf-8 -*-

#----------------------------------------------------------------------
def getSequenceNames( db ):
    sql = '''
        select c.relname
        from pg_catalog.pg_class c
            LEFT JOIN pg_catalog.pg_namespace n ON n.oid = c.relnamespace
        where c.relkind = 'S' and n.nspname like( 'public' )
    '''
    rows = db.executesql( sql, as_dict = True )
    seqNames = []
    for row in rows:
        seqNames.append( row[ 'relname' ] )
    return seqNames

#------------------------------------------------------------------
def replace_alias( query, a_list ):
    # term.printDebug( query )
    # term.printDebug( a_list )
    for k in a_list:
        # term.printDebug( 'k: %s - %s' % ( k, query ) )
        query = query.replace( ' ' + k + '_', ' ' + k + '.' )
        query = query.replace( '(' + k + '_', '(' + k + '.' )
        # term.printDebug( query )
    for k in a_list:
        query = query.replace( '%(' + k + '.', '%(' + k + '_' )
    # term.printDebug( query )
    return query

