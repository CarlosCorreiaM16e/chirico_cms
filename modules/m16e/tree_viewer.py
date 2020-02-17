# To change this template, choose Tools | Templates
# and open the template in the editor.

import datetime
import sys

from gluon.html import *
from gluon.sqlhtml import *
from gluon.validators import *

import m16e.term as term

from m16e.xml.xmltreenode import XmlTreeNode

#------------------------------------------------------------------
def getXRefCategoryTree(
  db, xtnParent, parentCategoryId, categoryTable, parentFieldName ):
  kSql = '''
    select
      m.%(parentFieldName)s as m_parent_id,
      m.id as m_id,
      p.name as p_name,
      p.description as p_description,
      m.name as m_name,
      m.description  as m_description
    from
      %(categoryTable)s m
      left outer join %(categoryTable)s p on p.id = m.%(parentFieldName)s
  ''' % {
    'categoryTable': categoryTable,
    'parentFieldName': parentFieldName }
  sql = kSql + ' where '
  args = {}
  if parentCategoryId:
    sql += 'm.' + parentFieldName + ' = %(parent_category_id)s'
    args = { 'parent_category_id': parentCategoryId }
  else:
    sql += 'm.' + parentFieldName + ' is null'
  sql += ' order by m_name'
#  term.printLog( 'sql: %s' % ( sql ) )
#  term.printLog( 'args: %s' % (repr( args ) ) )
  xrefList = db.executesql( sql, placeholders = args, as_dict = True )
  for xref in xrefList:
    attribs = {
      'parent_category_id' : xref[ 'm_parent_id' ],
      parentFieldName: xref[ 'm_id' ],
      'm_name': xref[ 'm_name' ]
    }
    x = XmlTreeNode( 'tree_node', xtnParent, attribs = attribs )
    getXRefCategoryTree( db, x, xref[ 'm_id' ], categoryTable, parentFieldName )

#  term.printLog( repr(xtnParent ) )
#  xtnParent.printTree()

#------------------------------------------------------------------
def getTreeChooserTable(
  T, xtnParent, fieldId, selCategoryId, isIndex, categoryTable, parentFieldName ):
#  term.printLog(
#    'get chooser for: %s; selCategoryId: %s, isIndex: %s' %
#    ( xtnParent.tag_name, repr( selCategoryId ), repr( isIndex ) ) )
  tableList = []
  for x in xtnParent.children:
#    term.printLog( 'x: %s' % ( x.toXml( '  ' ) ) )
    sName = x.getAttribute( 'm_name' )
#    term.printLog( 'name: %s' % ( sName ) )
    sId = x.getAttribute( parentFieldName )
#    term.printLog( 'id: %s (%s), name: %s' % ( repr( sId ), type( sId ), repr( sName ) ) )
    table = TABLE( _class = 'w100pct tree_view' )
    tr = TR()
    td = TD()
    cssClass = 'ajax_link'
    catNameStyle = None
    if sId == selCategoryId:
      cssClass += ' red'
      catNameStyle = 'color: magenta; font-weight: bold;'

    cssStyle = None
    divCssStyle = 'display: none;'
    if isIndex:
      selLink = SPAN(
        ' [',
        A(
          T( 'select' ),
          _href = URL( c = categoryTable, f = 'edit', args = [ sId ] ),
          _id = parentFieldName + '-%d' % ( sId ),
          _title = T( 'Edit this category' ),
          _class = cssClass ),
        ']' )
    else:
      if sId == selCategoryId:
        ajax = '''
          window.console && console.log( 'remove category' );
          jQuery( '#category_tree_div' ).hide();
          jQuery( '#category_name_span' ).html( '' );
          jQuery( '#%s' ).val( '' );
          jQuery( '#category_element_div' ).show();
        ''' % ( fieldId )
        linkText = T( 'remove' )
        linkTitle = T( 'Remove this category' )
        cssStyle = 'color:red;'
      else:
        ajax = '''
          window.console && console.log( 'select category' );
          jQuery( '#category_tree_div' ).hide();
          jQuery( '#category_name_span' ).html( '%s' );
          jQuery( '#%s' ).val( '%s' );
          jQuery( '#category_element_div' ).show();
        ''' % ( sName, fieldId, sId )
        linkText = T( 'select' )
        linkTitle = T( 'Select this category' )

      fldId = parentFieldName + '-%d' % ( sId )
      selLink = SPAN(
        ' [' + linkText + ']',
        _id = fldId,
        _title = linkTitle,
        _class = cssClass,
        _style = cssStyle,
        _onclick = ajax )
#    term.printLog( 'selLink: %s' % (selLink.xml() ) )

      attribs = { parentFieldName: selCategoryId }
      xSel = x.findChildByTagAndAttribs( 'tree_node', attribs )
      if xSel:
#        term.printLog( 'xSel(%d): %s' % (selCategoryId, str( xSel ) ) )
        divCssStyle = 'display: block;'


    if x.children:
      img = IMG( _src = URL( 'static', 'images/plus.gif' ), _class = 'tree_view' )
      a = A( img, _class = 'ajax_link', _onclick = 'Toggle(this);' )
      td.append( a )
      td.append( SPAN( sName, _style = catNameStyle ) )
      td.append( selLink )
      childDiv = DIV( _style = divCssStyle )
      tlist = getTreeChooserTable(
        T, x, fieldId, selCategoryId, isIndex, categoryTable, parentFieldName )
      for t in tlist:
        childDiv.append( t)
      td.append( childDiv )
    else:
      img = IMG( _src = URL( 'static', 'images/leaf.gif' ), _class = 'tree_view' )
      td.append( img )
      td.append( sName )
      td.append( selLink )
      childDiv = DIV( _style = divCssStyle )
      td.append( childDiv )
    tr.append( td )
    table.append( tr )
    tableList.append( table )

  return tableList

#------------------------------------------------------------------
def getCategoryTreeChooserTable(
  db, T, fieldId, selCategoryId, isIndex, categoryTable, parentFieldName ):
  table = TABLE( _class = 'w100pct tree_view' )
  xRoot = XmlTreeNode( T( 'Categories' ) )
  getXRefCategoryTree( db, xRoot, None, categoryTable, parentFieldName )

#  term.printLog( repr(xRoot) )
#  xRoot.printTree()
  if xRoot.children:
    tlist = getTreeChooserTable(
      T, xRoot, fieldId, selCategoryId, isIndex, categoryTable, parentFieldName )
    for t in tlist:
      table.append( TR( TD( t ) ) )
  else:
    table.append( TR( TD( '' ) ) )

  return table


