# -*- coding: utf-8 -*-
# Published under GPL v. 3 
# see: http://www.gnu.org/licenses/gpl-3.0.en.html

from gluon.html import A, I, SPAN
# from m16e import htmlcommon
from m16e.ui.actions import get_action_name

__author__ = 'carlos@memoriapersistente.pt'

# bootstrap
BTN_DEFAULT = 'default'
BTN_PRIMARY = 'primary'
BTN_SUCCESS = 'success'
BTN_INFO = 'info'
BTN_WARNING = 'warning'
BTN_DANGER = 'danger'
BTN_LINK = 'link'
# extra
BTN_SUBMIT = 'submit'
BTN_PURGE = 'purge'

BTN_STYLES = [ BTN_DEFAULT,
               BTN_PRIMARY,
               BTN_SUCCESS,
               BTN_INFO,
               BTN_WARNING,
               BTN_DANGER,
               BTN_LINK,
               BTN_SUBMIT,
               BTN_PURGE
               ]

BT_SIZE_LARGE = 'btn-lg'
BT_SIZE_SMALL = 'btn-sm'
BT_SIZE_XSMALL = 'btn-xs'
BT_SIZES = [ BT_SIZE_LARGE,
             BT_SIZE_SMALL,
             BT_SIZE_XSMALL ]

ICON_BAN_CIRCLE = 'ban-circle'
ICON_CAMERA = 'camera'
ICON_CHEVRON_LEFT = 'chevron-left'
ICON_CHEVRON_RIGHT = 'chevron-right'
ICON_CHECK = 'check'
ICON_CLEAR = 'unchecked'
ICON_DELETE = 'remove'
ICON_DOWN = 'circle-arrow-down'
ICON_EDIT = 'edit'
ICON_ENVELOPE = 'envelope'
ICON_ERASE = 'erase'
ICON_EURO = 'euro'
ICON_EXPORT = 'export'
ICON_EYE_CLOSE = 'eye-close'
ICON_EYE_OPEN = 'eye-open'
ICON_FAST_BACKWARD = 'fast-backward'
ICON_FAST_FORWARD = 'fast-forward'
ICON_FILE = 'file'
ICON_FILM = 'film'
ICON_GIFT = 'gift'
ICON_IMPORT = 'import'
ICON_LIST = 'list'
ICON_LIST_ALT = 'list-alt'
ICON_MENU_HAMBURGER = 'menu-hamburger'
ICON_MINUS = 'minus'
ICON_MINUS_SIGN = 'minus-sign'
ICON_MOVE = 'resize-vertical'
ICON_OK = 'ok'
ICON_PENCIL = 'pencil'
ICON_PICTURE = 'picture'
ICON_PLAY = 'play'
ICON_PLUS = 'plus'
ICON_PLUS_SIGN = 'plus-sign'
ICON_PRINT = 'print'
ICON_REFRESH = 'refresh'
ICON_REMOVE = 'remove'
ICON_RETWEET ='retweet'
ICON_SAVE = 'save'
ICON_SEARCH = 'search'
ICON_SHARE = 'share'
ICON_SHARE_ALT = 'share-alt'
ICON_SHOPPING_CART = 'shopping-cart'
ICON_STAR = 'star'
ICON_STAR_EMPTY = 'star-empty'
ICON_STEP_BACKWARD = 'step-backward'
ICON_STEP_FORWARD = 'step-forward'
ICON_TASKS = 'tasks'
ICON_TRASH = 'trash'
ICON_THUMBS_DOWN = 'thumbs-down'
ICON_THUMBS_UP = 'thumbs-up'
ICON_UNCHECK = 'unchecked'
ICON_USER = 'user'
ICON_UP = 'circle-arrow-up'
ICON_WARNING_SIGN = 'warning-sign'

ICON_BACK = ICON_CHEVRON_LEFT
ICON_CLEAR = ICON_UNCHECK
ICON_DELETE = ICON_REMOVE
ICON_DISABLE = ICON_BAN_CIRCLE
ICON_DOC = ICON_FILE
ICON_ENABLED = ICON_EYE_OPEN
ICON_MAIL = ICON_ENVELOPE
ICON_MENU = ICON_MENU_HAMBURGER
ICON_PURGE = ICON_ERASE
ICON_READ_ONLY = ICON_EYE_CLOSE
ICON_REPORT = ICON_LIST_ALT

ICON_NAV_END = ICON_FAST_FORWARD
ICON_NAV_NEXT = ICON_STEP_FORWARD
ICON_NAV_PREV = ICON_STEP_BACKWARD
ICON_NAV_START = ICON_FAST_BACKWARD

#------------------------------------------------------------------
def get_bootstrap_icon( icon_name,
                        dark_background=True,
                        html_style=None,
                        append_css_class=None,
                        tip=None ):
    # if html_style is None:
    #     html_style='padding-right: 0.5em;'
    if dark_background:
        css_class = 'glyphicon glyphicon-%s glyphicon-white' % icon_name
    else:
        css_class = 'glyphicon glyphicon-%s' % icon_name
    if append_css_class:
        css_class += ' ' + append_css_class
    icon = I( _class=css_class )
    if html_style:
        icon[ '_style' ] = html_style
    if tip:
        icon[ '_title' ] = tip
    return icon


#------------------------------------------------------------------
def get_link_icon( icon_name,
                   url=None,
                   bt_text='',
                   text_before_icon=False,
                   dark_background=True,
                   html_style=None,
                   tip=None,
                   on_click=None,
                   modal_data_target=None,
                   link_style=None,
                   blank_target=False ):

    """
    Args:
        icon_name: icon name
        url: if None, on_click must be given
        bt_text:
        text_before_icon:
        dark_background:
        html_style:
        tip:
        on_click:

    Returns:
        an <A> element (gluon.html.A)
    """
    i = get_bootstrap_icon( icon_name,
                            dark_background=dark_background,
                            html_style=html_style )
    a = None
    if not url:
        url = '#'
    if bt_text:
        if text_before_icon:
            a = A( bt_text + ' ',
                   i,
                   # _style='margin-left: 0.5em;',
                   _href=url )
        else:
            a = A( i,
                   ' ' + bt_text,
                   # _style='margin-left: 0.5em;',
                   _href=url )
    else:
        a = A( i,
               # _style='margin-left: 0.5em;',
               _href=url )
    if dark_background:
        a[ '_class' ] = 'dark_bg'
    if tip:
        a[ '_title' ] = tip
    if on_click:
        a[ '_onclick' ] = on_click
    if modal_data_target:
        a[ '_data-toggle' ] = 'modal'
        a[ '_data-target' ] = modal_data_target
    if blank_target:
        a[ '_target' ] = '_blank'
    if link_style:
        a[ '_style' ] = link_style
    return a


#------------------------------------------------------------------
class UiIcon( object ):

    def __init__( self,
                  icon_type,
                  dark_background=True ):
        self.icon_type = icon_type
        if dark_background:
            self.css_class = 'glyphicon glyphicon-%s glyphicon-white' % icon_type
        else:
            self.css_class = 'glyphicon glyphicon-%s' % icon_type


    def get_html_icon( self ):
        icon = SPAN( _class=self.css_class )
        return icon

#------------------------------------------------------------------
class UiButton( object ):

    def __init__( self,
                  text=None,
                  icon=None,
                  ui_icon=None,
                  tip=None,
                  action=None,
                  bt_var_name='action',
                  input_id=None,
                  button_type='submit',
                  button_style=None,
                  button_size=None,
                  css_class=None,
                  append_css_class=True,
                  css_style=None,
                  on_click=None,
                  url=None,
                  confirm_msg=None,
                  disabled=None ):
        """

        :param text:              text to display in button face
        :param icon:              icon to place before text
        :param tip:               text to display in tooltip
        :param action:            value to send in POST vars (name='action') or an UiAction instance
        :param bt_var_name:       name to send in POST vars (name='action')
        :param input_id:          HTML element id
        :param button_type:       one of [ 'button', 'submit', 'reset' ]
        :param button_style:      one of BTN_STYLES[]
        :param css_class:         button's class
        :param append_css_class:  if false, replaces button's class
        :param css_style:         style to be applied
        :param on_click:          onclick function
        :param url:               if given, button is a link
        """
        if text is None and icon is None and ui_icon is None:
            raise Exception( 'Faceless button' )
        self.text = text
        self.icon = icon
        self.ui_icon = ui_icon
        self.tip = tip
        self.action = action
        self.bt_var_name = bt_var_name
        self.input_id = input_id
        self.button_type = button_type
        self.button_size = button_size
        self.button_style = button_style
        if css_class:
            if append_css_class:
                self.css_class = 'btn btn-%s %s' % (button_style, css_class)
            else:
                self.css_class = css_class
        else:
            self.css_class = 'btn btn-%s' % button_style
        self.css_style = css_style
        self.on_click = on_click
        self.url = url
        self.confirm_msg = confirm_msg
        self.disabled = disabled
        # term.printDebug( 'self.css_class: %s' % repr( self.css_class ) )


    #------------------------------------------------------------------
    def get_html_button( self,
                         action=None,
                         bt_var_name=None,
                         input_id=None,
                         tip=None,
                         button_type=None,
                         button_style=None,
                         button_size=None,
                         css_class=None,
                         css_style=None,
                         on_click=None,
                         url=None,
                         confirm_msg=None,
                         disabled=None ):
        '''
        :param css_class:       button's class
        :param css_style:       style to be applied
        :param input_id:        HTML element id
        :param button_type:     button|submit|reset
        :param action:          value to send in POST vars (name='action') or an UiAction instance
        :param button_style:    one of BTN_STYLES[]
        :param on_click:        onclick function
        :param url:             if given, button is a link
        :return:                A gluon.html.BUTTON or gluon.html.A (for button_type == 'link')
        '''
        if bt_var_name is None:
            bt_var_name = self.bt_var_name
        if input_id is None:
            input_id = self.input_id
        if button_type is None:
            button_type = self.button_type
        if button_size is None:
            button_size = self.button_size
        if action is None:
            action = self.action
        if css_class is None:
            css_class = self.css_class
        if css_style is None:
            css_style = self.css_style
        if on_click is None:
            on_click = self.on_click
        elif confirm_msg:
            on_click = '''return confirm( '%s' );''' % confirm_msg
        if url is None:
            url = self.url
        if tip is None:
            tip = self.tip
        if button_style:
            if css_style:
                if not 'btn' in css_style.split( ' ' ):
                    css_style += ' btn btn-%s' % button_style
            else:
                css_style = 'btn btn-%s' % button_style
            if button_style == 'reset' and on_click is None:
                on_click = '''jQuery('.selectpicker').selectpicker('refresh');'''
        if button_size in BT_SIZES:
            if css_class:
                css_class += ' ' + button_size
            else:
                css_class = button_size

        action_name = get_action_name( action )
        # if isinstance( action, UiAction ):
        #     action_name = self.action.action_name
        # else:
        #     action_name = action
        if disabled is None:
            disabled = self.disabled
        from m16e import htmlcommon
        bt = htmlcommon.get_button( self.text or '',
                                    name=bt_var_name,
                                    value=action_name,
                                    icon=self.icon or (self.ui_icon and self.ui_icon.get_html_icon()),
                                    tip=tip,
                                    input_id=input_id,
                                    button_type=button_type,
                                    css_class=css_class,
                                    css_style=css_style,
                                    on_click=on_click,
                                    bt_link=url,
                                    disabled=disabled )
        return bt
