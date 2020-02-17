# -*- coding: utf-8 -*-


from gluon import current
from gluon.validators import IS_IN_SET

# T = current.T

#------------------------------------------------------------------
# MARKUP_SET
MARKUP_SET = IS_IN_SET( { 'M': 'Markmin',
                          'D': 'Markdown',
                          'H': 'HTML',
                          'N': current.T( 'None' ) } )
# HTML_TAGNAME_SET
HTML_TAGNAME_SET = IS_IN_SET( { 'div': 'div', 'span': 'span', } )

