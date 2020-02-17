# -*- coding: utf-8 -*-

from gluon import BR
from gluon.storage import Storage
from m16e import term
from m16e.ui.elements import get_bootstrap_icon, ICON_WARNING_SIGN

#----------------------------------------------------------------------
class ValidationResultItem():

    #----------------------------------------------------------------------
    def __init__( self,
                  success,
                  item_name,
                  val_tag=None,
                  target_id=None,
                  message=None,
                  val_type=None ):
        self.success = success
        self.item_name = item_name
        self.val_tag = val_tag
        self.message = message
        self.val_type = val_type
        self.target_id = target_id

    #----------------------------------------------------------------------
    def __repr__( self ):
        s = 'ValidationResultItem { '
        for a in self.__dict__:
            s += '\n  %s: %s' % (repr( a ), repr( self.__dict__[a] ) )
        s += '\n}'
        return s

    #----------------------------------------------------------------------
    def __str__( self ):
        s = '\tValidationResultItem { '
        for a in self.__dict__:
            s += '\n\t  %s: %s' % (repr( a ), repr( self.__dict__[a] ) )
        s += '\n\t}'
        return s

#----------------------------------------------------------------------
class ValidationResult():

    #----------------------------------------------------------------------
    def __init__( self, operation_name ):
        self.operation_name = operation_name
        self.items = Storage()

    #----------------------------------------------------------------------
    def __str__( self ):
        msg = 'operation_name: %s\n' % ( self.operation_name )
        for k in self.items:
            vi = self.items[ k ]
            if not vi.success:
                msg += '%s: %s\n' % ( vi.item_name, vi.message )
        return msg

    #----------------------------------------------------------------------
    def get_items_by_tagname( self, tagname ):
        i_list = [ vi for vi in self.items
                   if vi.val_tag == tagname ]
        return i_list

    #----------------------------------------------------------------------
    def get_items_by_target_id( self, target_id ):
        i_list = [ self.items[k] for k in self.items
                   if self.items[k].target_id == target_id ]
        return i_list

    #----------------------------------------------------------------------
    def set_item( self, key, vri, line_id=-1 ):
        self.items[ key ] = vri

    #----------------------------------------------------------------------
    def get_message( self, val_type ):
        msg = ''
        for k in self.items:
            vi = self.items[ k ]
            if vi.val_type == val_type:
                msg = vi.message
                break
        return msg


    def get_err_list( self, target_id=None ):
        err_list = []
        if target_id:
            target_list = [ self.items.get( target_id ) ]
        else:
            target_list = self.items

        for target in target_list:
            if not target:
                continue

            for t in target:
                vi = target[ t ]
                if not vi.success:
                    term.printLog( 'vi: %s' % ( repr( vi ) ) )
                    if err_list:
                        err_list.append( BR() )
                    else:
                        err_list.append( get_bootstrap_icon( ICON_WARNING_SIGN,
                                                             dark_background=False,
                                                             html_style='margin-right: 0.5em;' ) )
                    err_list.append( vi.message )
                    break
        term.printDebug( 'err_list: %s' % (repr( err_list ) ) )
        return err_list


    def get_full_err_list( self ):
        err_list = []

        for target in self.items:
            term.printDebug( 'target: %s' % repr( target ) )
            if not target:
                continue
            vi = self.items[ target ]
            if not vi.success:
                term.printLog( 'vi: %s' % ( repr( vi ) ) )
                if err_list:
                    err_list.append( BR() )
                else:
                    err_list.append( get_bootstrap_icon( ICON_WARNING_SIGN,
                                                         dark_background=False,
                                                         html_style='margin-right: 0.5em;' ) )
                err_list.append( vi.message )
                break
        term.printDebug( 'err_list: %s' % (repr( err_list ) ) )
        return err_list


    def get_success( self ):
        for k in self.items:
            for t in self.items[ k ]:
                vi = self.items[ k ][ t ]
                if not vi.success:
                    term.printLog( 'vi: %s' % ( repr( vi ) ) )
                    term.printDebug( 'vi: %s' % ( repr( vi ) ) ) #,
                                     # prompt_continue=True,
                                     # print_trace=True )
                    return False
        return True
