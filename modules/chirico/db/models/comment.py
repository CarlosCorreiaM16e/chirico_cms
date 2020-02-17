# -*- coding: utf-8 -*-

from gluon.dal import Field
from gluon.validators import IS_IN_DB
from gluon.validators import IS_IN_SET

from m16e import term
from m16e.db.database import DbBaseTable

import datetime


class CommentModel( DbBaseTable ):
    table_name = 'comment'

    #------------------------------------------------------------------
    def __init__( self, db ):
        super( CommentModel, self ).__init__( db )

    #------------------------------------------------------------------
    def get_fields( self ):
        db = self.db
        from m16e.db import db_tables
        db_tables.get_table_model( 'block', db=db )
        fields = [ Field( 'block_id', 'reference block', ondelete = 'NO ACTION' ),
                   Field( 'body', 'string' ),
                   Field( 'created_on', 'datetime' ),
                   Field( 'created_by', 'reference auth_user', ondelete = 'NO ACTION' ),
                   Field( 'parent_comment_id', 'reference comment', ondelete = 'NO ACTION' ),
        ]
        return fields
    
    #------------------------------------------------------------------
    def get_validators( self ): 
        from m16e.db import db_tables
        db_tables.get_table_model( 'article' )
        self.validators = {
            'block_id': IS_IN_DB( self.db, 'block.id', 'block.title' ),
            'parent_comment_id': IS_IN_DB( self.db, 'comment.id', 'comment.created_on')
        }
        return self.validators

    # #------------------------------------------------------------------
    # def get_comment_list( self, article_id ):
    #     db = self.db
    #     #------------------------------------------------------------------
    #     def getCommentTree( xParent ):
    #         q = ( db.comment.parent_comment_id == xParent.getAttribute( 'tuple' ).id )
    #         commentList = db( q ).select( orderby = 'comment.created_on' )
    #         for c in commentList:
    #             x = xtn.XmlTreeNode( 'node', xParent, attribs = { 'tuple': c } )
    #             getCommentTree( db, x )
    #         return xParent
    #
    #     cList = []
    #     q = ( db.comment.article_id ==article_id )
    #     q &= ( db.comment.parent_comment_id == None )
    #     commentList = db( q ).select( orderby = 'comment.created_on' )
    #     x = None
    #     for c in commentList:
    #         x = xtn.XmlTreeNode( 'node', x, attribs = { 'tuple': c } )
    #         getCommentTree( db, x )
    #         cList.append( x )
    #     return cList
    #
    # #------------------------------------------------------------------
