# -*- coding: utf-8 -*-
# Published under GPL v. 3 
# see: http://www.gnu.org/licenses/gpl-3.0.en.html

__author__ = 'carlos@memoriapersistente.pt'

def get_action_name( action ):
    if isinstance( action, UiAction ):
        action_name = action.action_name
    else:
        action_name = action
    return action_name


#------------------------------------------------------------------
class UiAction( object ):

    #------------------------------------------------------------------
    def __init__( self,
                  action_name=None,
                  url=None,
                  js=None ):
        self.action_name = action_name
        self.url = url
        self.js = js



