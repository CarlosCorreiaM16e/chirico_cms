# -*- coding: utf-8 -*-

#----------------------------------------------------------------------
class QueryData( object ):

    #----------------------------------------------------------------------
    def __init__( self,
                  where='',
                  args={},
                  order=None,
                  limit=20,
                  offset=None,
                  dict={} ):
        '''
        >>> QueryData( 'a = %(a)s', { 'a': 2 }, 'b', 20, 0, 50 )
        ('a = %(a)s', "{'a': 2}", 'b')

        '''
        if isinstance( where, str ):
            self.where = where
        else:
            raise Exception( 'Bad type for <where>: %s\nvalue: %s' % (type( where ), repr( where ) ) )
#        term.printLog( 'args: %s (%s)' % (repr( args ), type( args )) )
        if type( args ) == type( {} ):
            self.args = args
        else:
            raise Exception( 'Bad type for <args>: %s\nvalue: %s' % (type( args ), repr( args ) ) )

        self.order = order
        self.limit = limit
        self.offset = offset
        self.dict = dict

    #----------------------------------------------------------------------
    def __str__( self ):
        where = self.where % self.args
        return 'where ' + where


    #----------------------------------------------------------------------
    def __repr__( self ):
        return '''where: %(where)s
args. %(args)s
ofs: %(ofs)s; lim: %(lim)s; order: %(order)s
''' % { 'where': repr( self.where ),
        'args': str( self.args ),
        'order': repr( self.order ),
        'ofs': repr( self.offset ),
        'lim': self.limit }


    #----------------------------------------------------------------------
    def clone( self ):
        return QueryData(
            self.where, self.args,
            self.order, self.limit,
            self.offset, self.dict )

    #----------------------------------------------------------------------
    def addAnd( self, queryData ):
        self.addQuery( queryData, 'and' )

    #----------------------------------------------------------------------
    def addOr( self, queryData ):
        self.addQuery( queryData, 'or' )

    #----------------------------------------------------------------------
    def addQuery( self, queryData, op ):
        '''
        >>> q1 = QueryData( 'a = %(a)s', { 'a': 2 }, 'b', 20, 0, 50 )
        >>> q2 = QueryData( 'c = %(c)s or b = %(b)s', { 'c': 1, 'b': 'xxx' } )
        >>> q1.addAnd( q2 )
        >>> print repr( q1 )
        ('(a = %s) and (c = %s or b = %)', "{'a': 2, 'c': 1, 'b': 'xxx'}", 'b')
        '''
#        term.printLog( 'thisArgs: %s\notherArgs: %s' % (repr( self.args ), repr( queryData.args )) )
        if self.where:
            if queryData.where:
                self.where = '(%s) %s (%s)' % (self.where, op, queryData.where )
            if self.args:
                if queryData.args:
                    for arg in queryData.args:
                        self.args[ arg ] = queryData.args[ arg ]
            else:
                self.args = queryData.args
        else:
            self.where = queryData.where
            self.args = queryData.args

# #----------------------------------------------------------------------
# class FromListItem( object ):
#     def __init__( self, relName, joinCondition = None, leftJoin = False ):
#         """
#         relName: name of table or view plus (optional) alias
#         joinCondition: join condition ('using(...)' or 'on ...')
#         leftJoin: boolean indicating whether to execute a left outer join
#         """
#         names = relName.split( ' ' )
#         self.relName = names[0]
#         self.alias = None
#         if len( names ) > 1:
#             self.alias = names[2]
#         self.joinCondition = joinCondition
#         self.leftJoin = leftJoin
#
# #----------------------------------------------------------------------
# class SelectQuery( object ):
#     def __init__( self,
#                   fieldList,
#                   fromList,
#                   queryData ):
#         self.fromList = fromList
#         self.fieldList = fieldList
#         if isinstance( fieldList, str ):
#             self.fieldList = []
#             a = fieldList.split( ',' )
#             for f in a:
#                 els = f.split( ' as ' )
#                 fEls = (els[0],)
#                 if len( els ) > 1:
#                     fEls = (els[0], els[1])
#                 self.fieldList.append( els )
#                 print 'els:'
#                 print els
#         elif isinstance( fieldList, list ):
#             self.fieldList = []
#             for f in fieldList:
#                 if isinstance( f, tuple ):
#                     self.fieldList.append( f )
#                 else:
#                     self.fieldList.append( (f, ) )
#         else:
#             raise Exception( 'bad type: (%s)' % (type( f )) )
#         self.queryData = queryData
#
    #----------------------------------------------------------------------
    def getFieldNames( self ):
        names = []
        for f in self.fieldList:
            names.append( f[-1] )
        return names

    #----------------------------------------------------------------------
    def getDict( self, tuple ):
        dict = {}
        ofs = 0
        for f in self.getFieldNames():
            dict[f] = tuple[ ofs ]
            ofs += 1
        return dict

    #----------------------------------------------------------------------
    def reprTuple( self, tuple ):
        text = '{ '
        for n in self.getFieldNames():
            text += n + ': '
            text += repr( tuple[n] ) + ', '
        text += ' }'
        return text

    #----------------------------------------------------------------------
    def getStatement( self ):
        stmt = "select "
        first = True
#        print 'querydata.getStatement() fieldList:'
#        print self.fieldList
        for f in self.fieldList:
            print f
            if first:
                first = False
            else:
                stmt += ', '
            stmt += f[0]
            if len( f ) > 1:
                stmt += ' as ' + f[1]
        stmt += " from "
        first = True
        for f in self.fromList:
            if first:
                first = False
                stmt += f.relName
            else:
                if f.leftJoin:
                    stmt += " left outer"
                stmt += " join "
                stmt += f.relName + " " + f.joinCondition
        if self.queryData:
            stmt += " where " + self.queryData.where
            if self.queryData.order:
                stmt += " order by " + self.queryData.order
            if self.queryData.offset:
                stmt += " offset %d" % (self.queryData.offset)
            if self.queryData.limit:
                stmt += " limit %d" % (self.queryData.limit)
        return stmt

#----------------------------------------------------------------------
def test():
    where = "tipo_ent_id = %s and tipo_doc_id = %s"
    args = [ 1, 2 ]
    order = "doc_id desc"
    qd = QueryData( where, args, order, 10 )
    sq = SelectQuery( '*', [FromListItem( 'mpbv_get_doc_total' )], qd )
    print sq.getStatement()

#----------------------------------------------------------------------
if __name__ == "__main__":
    import doctest
    doctest.testmod()
