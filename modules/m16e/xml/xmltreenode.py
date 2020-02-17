#! /usr/bin/python

__author__="carlos"
__date__ ="$22/Jun/2011 18:45:03$"

from lxml import etree

#----------------------------------------------------------------------
CDATA_START = "<![CDATA["
CDATA_STOP = "]]>"

INVALID_XML_CHARS = '''<>'"&'''

def stringContainsValidXmlValue( s ):
    if not s:
        return True

    for c in INVALID_XML_CHARS:
        if c in s:
            return False

    return True

#----------------------------------------------------------------------
class XmlTreeNode( object ):
    #----------------------------------------------------------------------
    def __init__( self, tag_name = None, parent = None, value = None, attribs = {} ):
        self.tag_name = tag_name
        self.parent = parent
        self.children = []
        self.attribs = attribs
        self.value = value
        if value:
            self.value = str( value )

        if parent is not None:
            parent.addChild( self )

    #----------------------------------------------------------------------
    def __str__( self ):
        return '%s: %s' % ( self.tag_name, repr( self.attribs ) )

    #----------------------------------------------------------------------
    def addChild( self, child, at = -1 ):
        child.parent = self
        if at < 0:
            self.children.append( child )
        else:
            self.children.insert( at, child )

    #----------------------------------------------------------------------
    def addChildren( self, children ):
        for child in children:
            child.parent = self
            self.children.append( child )

    #----------------------------------------------------------------------
    def getAttribute( self, name ):
        return self.attribs.get( name, None )

    #----------------------------------------------------------------------
    def setAttribute( self, name, value ):
        self.attribs[ name ] = value

    #----------------------------------------------------------------------
    def getChildByTag( self, tag ):
#        print ">>> getChildByTag: " + str( tag )
        children = self.getChildrenByTag( tag )
        if not children:
            return None
        else:
            return children[0]

    #----------------------------------------------------------------------
    def getChildrenByTag( self, tag ):
        '''
        data =
        <a>
            <a1>
                <a1a name="a1a-name">
                    <a1a1>1</a1a1>
                    <a1a2>A</a1a2>
                </a1a>
            </a1>
            <a2>
                <a2a name="a2a-name">
                    <a2a1>2</a2a1>
                    <a2a2>B</a2a2>
                </a1a>
            </a1>
        </a>
        '''
#         term.printDebug( "tag: " + str( tag ) )
        attribs = {}
        childList = []
        el_value = None
        parts = tag.rsplit( ':', 1 )
#         term.printDebug( 'parts: %s' % ( repr( parts ) ) )
        if len( parts ) > 1:
            el_value = parts[1]
            tag = parts[0]
        idx = tag.find( "(" )
        if idx >= 0:
            attrStr = tag[ idx + 1 : len(tag) - 1 ]
            tag = tag[:idx]
            al = attrStr.split( ";" )

            for a in al:
                idx = a.find( "=" )
                name = a[0:idx]
                value = a[ idx + 1:]
                attribs[ name ] = value
        found = False
        for child in self.children:
            if child.tag_name == tag:
                found = True

                for attrib in attribs:
                    childVal = child.getAttribute( attrib )
                    matchVal = attribs.get( attrib, None )

                    if childVal != matchVal:
                        found = False
                        break
                if el_value:
                    if child.value != el_value:
                        found = False
            if found:
                childList.append( child )

        return childList


    #----------------------------------------------------------------------
    def getChildByTags( self, *tags ):
#        print ">>> getChildByTags: " + str( tags )
        xtn = self
        for tag in tags:
            xtn = xtn.getChildByTag( tag )

        if xtn == self:
            xtn = None
        return xtn

    #----------------------------------------------------------------------
    def getChildByTagList( self, tags ):
#        print ">>> getChildByTags: " + str( tags ) + " (self: " + self.tag_name + ")"
        parts = tags[0].rsplit( ':', 1 )
        tag = parts[0]
        el_value = None
        if len( parts ) > 1:
            el_value = parts[1]
        for x in self.children:
#             print( x.toXml() )
            if tag == x.tag_name:
                if len( tags )==1:
                    if not el_value or el_value==x.value:
                        return x
                elif tags[1:]:
                    x_ret = x.getChildByTagList( tags[1:] )
                    if x_ret:
                        return x_ret

        return None

    #----------------------------------------------------------------------
    def getChildByPath( self, path ):
        pathList = path.split( "/" )
        return self.getChildByTagList( pathList )

    #----------------------------------------------------------------------
    def getChildrenByTagList( self, tags ):
#        print ">>> getChildByTags: " + str( tags ) + " (self: " + self.tag_name + ")"
        childList = []
        xtn = self
        parts = tags[0].rsplit( ':', 1 )
        tag = parts[0]
        el_value = None
        if len( parts ) > 1:
            el_value = parts[1]
        for x in xtn.children:
            if tag == x.tag_name:
                if len( tags ) == 1:
                    if not el_value or  el_value == x.value:
                        childList.append( x )
                elif tags[1:]:
                    childList.extend( x.getChildrenByTagList( tags[1:] ) )
        
        return childList

    #----------------------------------------------------------------------
    def getChildrenByTagList0( self, tags ):
#        print ">>> getChildByTags: " + str( tags ) + " (self: " + self.tag_name + ")"
        childList = []
        xtn = self
        for tag in tags:
            l = xtn.getChildrenByTag( tag )
            for x in l:
                if tag == tags[-1]:
                    childList.append( x )
                else:
                    lc = x.getChildrenByTagList( )
                
            childList.extend( l )

        return childList

    #----------------------------------------------------------------------
    def getChildrenByPath( self, path ):
        pathList = path.split( "/" )
        return self.getChildrenByTagList( pathList )

    #----------------------------------------------------------------------
    def parse( self, element ):
        self.tag_name = element.tag
        self.attribs = element.attrib
        self.value = element.text

        for el in element:
            treeNode = XmlTreeNode( el.tag, self )
#            self.children.append( treeNode )
            treeNode.parse( el )

    #----------------------------------------------------------------------
    def printTree( self, indent = "" ):
        print indent + "Tag: " + str( self.tag_name )
        for attr in self.attribs:
            print indent + "    + " + attr + ": " + str( self.attribs.get( attr ) )
        for child in self.children:
            child.printTree( indent + "    " )

    #----------------------------------------------------------------------
    def toXml( self, indent = "" ):
        xml = indent + "<" + str( self.tag_name )
        for attr in self.attribs:
            xml += " " + attr + "=\"" + str( self.attribs.get( attr ) ) + "\""
        xml += ">"
        if self.children:
            xml += "\n"
            for child in self.children:
                xml += child.toXml( indent + "    " )
            xml += indent
        elif self.value:
            if stringContainsValidXmlValue( self.value ):
                xml += self.value
            else:
                xml += CDATA_START + self.value + CDATA_STOP
        xml += "</" + str( self.tag_name ) + ">\n"
        return xml

    #----------------------------------------------------------------------
    def remove( self, child ):
        child.parent = None
        self.children.remove( child )

    #----------------------------------------------------------------------
    def removeFromParent( self ):
        self.parent.remove( self )

    #----------------------------------------------------------------------
    def findChildByTagAndAttribs( self, tag, attribs = {} ):
#        term.printLog( 'self: %s: %s' % (self.tag_name, repr( self.attribs ) ) )
#        term.printLog( 'find: %s: %s' % (tag, repr( attribs ) ) )
        found = None
        for c in self.children:
            if c.tag_name == tag:
                match = True
                for k in attribs.keys():
                    if attribs[ k ] != c.getAttribute( k ):
                        match = False
                        break
                if match:
                    return c
                if c.children:
                    found = c.findChildByTagAndAttribs( tag, attribs )
                    if found:
                        break
#        term.printLog( 'found: %s' % (repr( found ) ) )
        return found

#----------------------------------------------------------------------
if __name__ == "__main__":
#     file = sys.argv[1]
#     file = '/home/carlos/tmp/inidesign/install/data/tab_moeda.xml'
#     context = etree.parse( file )
#     root = context.getroot()
#     xtn = XmlTreeNode()
#     xtn.parse( root )
#     l = xtn.getChildrenByPath( 'data/row/tab_moeda.moeda_id:2' )
# #     x = xtn.getChildByTagList( [ 'data' ] )
#     
#     for x in l: 
#         print( '%s: %s' % ( x.tag_name, repr( x.value ) ) )

    file = '/home/carlos/tmp/inidesign/install/data/ent_fin.xml'
    context = etree.parse( file )
    root = context.getroot()
    xtn = XmlTreeNode()
    xtn.parse( root )
    l = xtn.getChildrenByPath( 'data/row/ent_fin.ent_id:832' )
#     x = xtn.getChildByTagList( [ 'data' ] )
    
    for x in l: 
        print( '%s: %s' % ( x.tag_name, repr( x.value ) ) )

    file = '/home/carlos/tmp/inidesign/install/data/prod_alfa_code.xml'
    context = etree.parse( file )
    root = context.getroot()
    xtn = XmlTreeNode()
    xtn.parse( root )
    l = xtn.getChildrenByPath( 'data/row/prod_alfa_code.prod_id:1' )
#     x = xtn.getChildByTagList( [ 'data' ] )
    
    for x in l: 
        print( '%s: %s' % ( x.tag_name, repr( x.value ) ) )
        xp = x.parent
        print( xp.toXml() )

    x = xtn.getChildByPath( 'data/row/prod_alfa_code.prod_id:1' )
    print( '%s: %s' % ( x.tag_name, repr( x.value ) ) )
    xp = x.parent
    print( xp.toXml() )

    """
    xtn = treeNode.getChildByTags( "book", "author" )
    if xtn != None:
        print xtn.tag_name
    else:
        print xtn
    xtn = treeNode.getChildByTag( "book(id=bk102)" )
    if xtn != None:
        print xtn.tag_name
    else:
        print xtn
    xtn = treeNode.getChildByPath( "book(id=bk102)/title" )
    if xtn != None:
        print xtn.value
    else:
        print xtn
        """
