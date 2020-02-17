# -*- coding: utf-8 -*-

import datetime

from gluon import current
from gluon.dal import Field
from m16e.db.database import DbBaseTable

DT=datetime.datetime
DATE=datetime.date

#----------------------------------------------------------------------
class AppLoggerModel( DbBaseTable ):
    table_name = 'app_logger'

    #----------------------------------------------------------------------
    def __init__( self, db ):
        super( AppLoggerModel, self ).__init__( db )

    #----------------------------------------------------------------------
    def get_fields( self ):
        self.fields = [ Field( 'when_happened', 'datetime', default=DT.now(), notnull=True ),
                        Field( 'short_description', 'string', notnull=True ),
                        Field( 'long_description', 'string', notnull=True ),
                        Field( 'user_id', 'integer', notnull=True ),
                        Field( 'table_name', 'string', notnull=True ),
                        Field( 'crud_action', 'string' ),
                        Field( 'client_ip', 'string' ),
                        ]
        return self.fields

    #----------------------------------------------------------------------
    def get_validators( self ):
        T = current.T
        self.validators = {}
        return self.validators

#     #----------------------------------------------------------------------
#     def get_data( self,
#                   app_logger_id=None,
#                   offset=0,
#                   limit=200,
#                   cache_results=30,
#                   orderby='id',
#                   return_first=False ):
#         '''cache results by default for 30 seconds,
#         call with cache_results=False|None|0
#         to force DB read
#         '''
#         cache = current.cache
#         cache_cfg = (cache.ram, cache_results or 0)
#         db = self.db
#         q = (db.app_logger.id > 0)
#         rec_list = db( q ).select( cache=cache_cfg,
#                                    limitby=(offset, limit),
#                                    orderby=self.get_orderby( orderby ) )
#
# #         term.printDebug( 'sql: %s' % ( db._lastsql ) )
# #         term.printDebug( 'orderby: %s' % ( self.get_orderby( orderby ) ) )
# #         term.printDebug( 'rec_list: %s' % ( repr( rec_list ) ) )
#
#         if app_logger_id:
#             for r in rec_list:
#                 if r.id == app_logger_id:
#                     return r
#             return None
#
#         if return_first:
#             if rec_list:
#                 return rec_list[0]
#             return None
#
#         return rec_list
#
#     #----------------------------------------------------------------------
#
