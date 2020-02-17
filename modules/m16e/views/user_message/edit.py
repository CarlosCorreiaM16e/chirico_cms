# -*- coding: utf-8 -*-
from m16e.db import db_tables
from gluon import current
from m16e.views.edit_base_view import BaseFormView
from gluon.html import A, DIV, SPAN, URL


class UserMsgEditView( BaseFormView ):
    controller_name = 'user_message'
    function_name = 'edit'


    def __init__( self, db ):
        super( UserMsgEditView, self ).__init__( db )
        self.table_model = db_tables.get_table_model( 'user_message', db=db )


    def get_exclude_fields( self ):
        return [ 'msg_org',
                 'msg_type',
                 'answer',
                 'delete_if_past' ]


    def post_process_form( self, form ):
        T = current.T
        super(   UserMsgEditView, self ).post_process_form( form )
        menu_path = DIV( _id='menu_path_div', _class='menu_path' )
        menu_path.append( A( T( 'User messages' ),
                             _href=URL( c='user_message',
                                        f='index' ) ) )
        self.set_result( data=dict( menu_path=menu_path ) )



