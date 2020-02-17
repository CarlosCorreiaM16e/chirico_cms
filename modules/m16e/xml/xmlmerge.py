#! /usr/bin/python
from lxml import etree
from xmltreenode import XmlTreeNode
import m16e.term as term
import sys

__author__="carlos"
__date__ ="$22/Jun/2011 18:46:47$"



__author__="carlos"
__date__ ="$1/Jun/2011 23:34:59$"

ACT_REPLACE_ALL = "replace-all"
ACT_REPLACE_ATTRIB = "replace-attrib"
ACT_REPLACE_EL = "replace-el"

ATTR_ACTION = "action"
ATTR_EL = "el"
ATTR_NAME = "name"
ATTR_VALUE = "value"

TAG_ADD = " add"
TAG_ATTRIB = "attrib"
TAG_FIND = "find"

def add( xtnSrc, xtnMerge ):
    el = xtnMerge.getAttribute( ATTR_EL )
    if el is None or el == "":
        xtnSrc.addChildren( xtnMerge.children )
    else:
        child = xtnSrc.getChildByTag( el )
        child.addChildren( xtnMerge.children )

def replaceAll( xtnSrc, xtnMerge ):
    el = xtnMerge.getAttribute( ATTR_EL )
    children = xtnSrc.getChildrenByTag( el )
    parent = children[0].parent
    for child in children:
        child.removeFromParent()
    parent.addChildren( xtnMerge.children )

def replaceAttrib( xtnSrc, xtnMerge ):
    el = xtnMerge.getAttribute( ATTR_EL )
    children = xtnSrc.getChildrenByTag( el )
    for child in children:
        attribs = xtnMerge.getChildrenByTag( TAG_ATTRIB )
        for attrib in attribs:
            name = attrib.getAttribute( ATTR_NAME )
            value = attrib.getAttribute( ATTR_VALUE )
            child.setAttribute( name, value )

def replaceEl( xtnSrc, xtnMerge ):
    el = xtnMerge.getAttribute( ATTR_EL )
    child = xtnSrc.getChildByTag( el )
    if not child:
        error = '''
            failed to find el (%s) in:\n
            %s
        ''' % (el, xtnSrc.toXml() )
        path = el.split( '/' )
        term.printDebug( repr( path ) )
        c = xtnSrc.getChildByTag( '/'.join( path[:-1] ) )
        term.printDebug( repr( c ) )
        if c:
            x = XmlTreeNode( path[-1] )
            x.addChildren( xtnMerge.children )
            c.addChild( x )
            term.printDebug( c.toXml() )
#            raise Exception( c.toXml() )
#            term.printDebug( c.toXml() )
        else:
            raise Exception( error )
    else:
        parent = child.parent
        child.removeFromParent()
        parent.addChildren( xtnMerge.children )

def mergeFind( xtnSrc, xtnMerge ):
    if xtnMerge.tag_name == TAG_ADD:
        add( xtnSrc, xtnMerge )
    elif xtnMerge.tag_name == TAG_FIND:
        action = xtnMerge.getAttribute( ATTR_ACTION )
        if action == ACT_REPLACE_EL:
            replaceEl( xtnSrc, xtnMerge )
        elif action == ACT_REPLACE_ALL:
            replaceEl( xtnSrc, xtnMerge )
        elif action == ACT_REPLACE_ATTRIB:
            replaceAttrib( xtnSrc, xtnMerge )

def merge( xtnSrc, xtnMerge ):
    for child in xtnMerge.children:
        mergeFind( xtnSrc, child )

def usage():
    print sys.argv[0] + " <xml-file> <xml-merge>"

def execute():
    context = etree.parse( sys.argv[1] )
    root = context.getroot()
    xtnSrc = XmlTreeNode()
    xtnSrc.parse( root )
    context = etree.parse( sys.argv[2] )
    root = context.getroot()
    xtnMerge = XmlTreeNode()
    xtnMerge.parse( root )
    merge( xtnSrc, xtnMerge )

def runApp():
    if len( sys.argv ) < 3 or sys.argv[1] == "-h":
        usage()
    else:
        execute()

if __name__ == "__main__":
    runApp()

