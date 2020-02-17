# -*- coding: utf-8 -*-
# this file is released under public domain and you can use without limitations
from m16e.db import db_tables
from gluon import current
from gluon.html import DIV, H3, TABLE, TR, TD, INPUT, A, URL, SPAN, BUTTON, FORM
from gluon.storage import Storage

from m16e import term
import m16e.tree_viewer as tview

#------------------------------------------------------------------
from m16e.views.plastic_view import BaseListPlasticView


class CategoryIndexView( BaseListPlasticView ):
    def __init__( self, db ):
        super( CategoryIndexView, self ).__init__( db )
        self.table_model = db_tables.get_table_model( 'article', db=db )

    
    #------------------------------------------------------------------
    def process( self ):
        request = current.request
        response = current.response
        session = current.session
        T = current.T
        db = self.db
        auth = session.auth
        redirect = None
        
        ACT_EDIT_CATEGORY = 'edit_category'
        ACT_NEW_CATEGORY = 'new_category'
        
        mainPanel = DIV()
        mainPanel.append( H3( T( 'Categories' ) ) )

        parent_tree_chooser = DIV()
        parent_tree_chooser.append( tview.getCategoryTreeChooserTable(
            db, T, 'parent_category_id', 0, False,
            'category', 'parent_category_id' ) )
    
        mainPanel.append( parent_tree_chooser )
    
        btNew = BUTTON( T( 'New category' ), _name = 'action', _type = 'submit',
                        _value = ACT_NEW_CATEGORY, _title = T( 'New category' ) )
        form = FORM( btNew )
        mainPanel.append( form )
        if form.accepts( request.vars, session ):
            term.printLog( 'form.vars: ' + repr( form.vars ) )
            term.printLog( 'post_vars: ' + repr( request.post_vars ) )
            action = request.post_vars.action
            if action == ACT_NEW_CATEGORY:
                redirect = URL( c = 'category', f = 'edit', args = [ 0 ] )
            elif action.startswith( ACT_EDIT_CATEGORY ):
                imgId = int( action.split( '-' )[1] )
                redirect = URL( r = request, f = 'edit', args = [ imgId ] )
    
        return Storage( dict=dict( main_panel = mainPanel ), redirect=redirect )
        
    