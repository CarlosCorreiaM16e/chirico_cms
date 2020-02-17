# -*- coding: utf-8 -*-

import datetime

from gluon import current
from gluon.dal import Field
from m16e.db.database import DbBaseTable

DT = datetime.datetime
DATE = datetime.date

#------------------------------------------------------------------
class MimeTypeModel( DbBaseTable ):
    table_name = 'mime_type'

    #------------------------------------------------------------------
    def __init__( self, db ):
        super( MimeTypeModel, self ).__init__( db )
        self.track_history = True

    #------------------------------------------------------------------
    def get_fields( self ):
        self.fields = [
            Field( 'mt_name', 'string', notnull = 'True' ),
            Field( 'description', 'string' ),
            Field( 'edit_command', 'string' ),
            Field( 'view_command', 'string' ),
            Field( 'preferred_order', 'integer', default = 0, notnull = 'True' )
        ]
        return self.fields
    
    #------------------------------------------------------------------
    def define_table( self ):
        if self.table_name not in self.db.tables:
            super( MimeTypeModel, self ).define_table()

    #------------------------------------------------------------------
    def get_validators( self ): 
        self.validators = {}
        return self.validators

    #------------------------------------------------------------------
    def get_data( self, 
                  mime_type_id=None, 
                  cache_results=300, 
                  orderby='mt_name' ):
        '''
        cache results by default for 300 seconds,
        call with cache_results=False|None|0
        to force DB read
        if given <ent_doc_type_id> or (<ent_type_id> and <doc_type_id>)
        a single record is returned, else returns a list
        '''
        cache = current.cache
        cache_cfg = (cache.ram, cache_results or 0)
        db = self.db
        rec_list = db( db.mime_type.id > 0 ).select( cache=cache_cfg,
                                                     orderby=self.get_orderby( orderby ) )
        if mime_type_id:
            for r in rec_list:
                if r.id == mime_type_id:
                    return r
            return None
        
        return rec_list

#------------------------------------------------------------------
class MimeTypeExtModel( DbBaseTable ):
    table_name = 'mime_type_ext'

    #------------------------------------------------------------------
    def __init__( self, db ):
        super( MimeTypeExtModel, self ).__init__( db )
        self.track_history = True

    #------------------------------------------------------------------
    def get_fields( self ):
        MimeTypeModel( self.db ).define_table()
        self.fields = [
            Field( 'mime_type_id', 'reference mime_type', notnull = 'True', ondelete = 'NO ACTION' ),
            Field( 'extension', 'string' )
        ]
        return self.fields
    
    #------------------------------------------------------------------
    def get_validators( self ): 
        self.validators = {}
        return self.validators

    # #------------------------------------------------------------------
    # def get_data( self,
    #               mime_type_ext_id=None,
    #               mime_type_id=None,
    #               extension=None,
    #               cache_results=30,
    #               orderby='extension' ):
    #     '''
    #     cache results by default for 300 seconds,
    #     call with cache_results=False|None|0
    #     to force DB read
    #     if given <ent_doc_type_id> or (<ent_type_id> and <doc_type_id>)
    #     a single record is returned, else returns a list
    #     '''
    #     cache = current.cache
    #     cache_cfg = (cache.ram, cache_results or 0)
    #     db = self.db
    #     rec_list = db( db.mime_type_ext.id > 0 ).select( cache=cache_cfg,
    #                                                      orderby=self.get_orderby( orderby ) )
    #     if mime_type_ext_id:
    #         for r in rec_list:
    #             if r.id == mime_type_ext_id:
    #                 return r
    #         return None
    #
    #     if mime_type_id:
    #         q_list = []
    #         for r in rec_list:
    #             if r.mime_type_id == mime_type_id:
    #                 q_list.append( r )
    #         return q_list
    #
    #     if extension:
    #         q_list = []
    #         for r in rec_list:
    #             if extension.lower() == r.extension:
    #                 q_list.append( r )
    #         return q_list
    #
    #     return rec_list
    #
    #