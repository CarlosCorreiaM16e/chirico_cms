# -*- coding: utf-8 -*-
# this file is released under public domain and you can use without limitations
from m16e.db import db_tables
from gluon.globals import current
from gluon.html import URL, DIV, H5
from gluon.sqlhtml import SQLFORM
from gluon.storage import Storage
from m16e import term
import m16e.htmlcommon as html
import m16e.tree_viewer as tview

#------------------------------------------------------------------
from m16e.views.edit_base_view import BaseFormView


class CategoryEditView( BaseFormView ):
    def __init__( self, db ):
        super( CategoryEditView, self ).__init__( db )
        self.table_model = db_tables.get_table_model( 'article', db=db )


    def get_form( self,
                  db_record=None, 
                  form_fields=[], 
                  form_validators={},
                  deletable=False ):
        if not form_fields:
            form_fields = [ 'name', 'description', 
                            'parent_category_id', 'category_type' ]
        form = super( CategoryEditView, self ).get_form( self,
                                                         db_record,
                                                         form_fields,
                                                         form_validators,
                                                         deletable=deletable )
        return form
        
    #------------------------------------------------------------------
    def process( self ):
        request = current.request
        response = current.response
        session = current.session
        T = current.T
        db = self.db
        auth = session.auth
        redirect = None
        
        ACT_SUBMIT_CATEGORY = 'submit_category'
        
        term.printLog( 'request.args: ' + repr( request.args ) )
        term.printLog( 'request.vars: ' + repr( request.vars ) )
        
        category = db.article_category( request.args( 0 ) )
        form = self.get_form( category, deletable=True )
        
        action = request.post_vars.action
    
        if form.validate():
            term.printLog( 'form.vars: ' + repr( form.vars ) )
            term.printLog( 'post_vars: ' + repr( request.post_vars ) )
            if action == ACT_SUBMIT_CATEGORY:
                if form.deleted:
                    db( db.article_category.id == category.id ).delete()
                    session.flash = T( 'Category deleted' )
                    redirect = URL( r = request, f = 'index' )
    
                changed = False
                upd = html.getChangedFields( 
                    form.vars, request.post_vars, db.article_category )
                if upd:
                    changed = True
    
                categoryId = None
                if category:
                    categoryId = category.id
                    if upd:
                        term.printLog( 'updating: ' + repr( upd ) )
                        db( db.article_category.id == categoryId ).update( **upd )
                        term.printLog( 'sql: ' + db._lastsql )
                else:
                    categoryId = db.article_category.insert( **upd )
    
                if changed:
                    category = db.article_category[ categoryId ]
                    if category:
                        session.flash = T( 'Category updated' )
                    else:
                        session.flash = T( 'Category created' )
                    redirect = URL( c = 'category', f = 'index' )
                else:
                    response.flash = T( 'Nothing to update' )
        elif form.errors:
            term.printLog( 'errors: %s' % ( repr( form.errors ) ) )
            response.flash = T( 'Form has errors' )
    
        parent_tree_chooser = DIV()
        parent_tree_chooser.append( tview.getCategoryTreeChooserTable(
            db, T, 'parent_category_id', category and category.id or 0, False,
            'category', 'parent_category_id' ) )
    
        parent_name = T( 'None' )
        title = T( 'Create category' )
        if category:
            title = T( 'Edit category' )
            if category.parent_category_id:
                parent = db.article_category[ category.parent_category_id ]
                parent_name = parent.name
    #    term.printLog( 'form: ' + repr( form.xml() ) )
        return Storage( dict=dict( title = title, 
                                   form = form,
                                   category = category,
                                   parent_name = parent_name,
                                   parent_tree_chooser = parent_tree_chooser ),
                        redirect=redirect )
        
    
    