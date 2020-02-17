# -*- coding: utf-8 -*-

from m16e.db import db_tables
from gluon import current
from m16e.views.edit_base_view import BaseFormView
from gluon.html import A, DIV, SPAN, URL


class ThreadStatusEditView( BaseFormView ):
    controller_name = 'thread_statuss'


    def __init__( self, db ):
        super( ThreadStatusEditView, self ).__init__( db )
        self.table_model = db_tables.get_table_model( 'thread_status', db=db )


    def post_process_form( self, form ):
        T = current.T
        super(   ThreadStatusEditView, self ).post_process_form( form )
        menu_path = DIV( _id='menu_path_div', _class='menu_path' )
        menu_path.append( A( T( 'Thread status' ),
                             _href=URL( c='thread_status',
                                        f='index' ) ) )
        self.set_result( data=dict( menu_path=menu_path ) )



