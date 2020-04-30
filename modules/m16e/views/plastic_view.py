# -*- coding: utf-8 -*-

import copy
import sys
import traceback

from gluon.globals import current
from gluon.html import URL, DIV, H3, H4, FORM
from gluon.storage import Storage
from m16e import term, htmlcommon
from m16e.db.misc import replace_alias
from m16e.db.querydata import QueryData
from m16e.kommon import KQV_ORDER, KQV_OFFSET, KQV_LIMIT, \
    KQV_SHOW_ALL, KDT_INT, KDT_CHAR, KDT_BOOLEAN, storagize, ACT_NEW_RECORD, ACT_CLEAR, ACT_SUBMIT, KDT_SELECT_CHAR, \
    is_sequence, KDT_DATE, KDT_TIME, KDT_TIMESTAMP, KDT_SELECT_INT, KDT_INT_LIST, KQV_PREFIX
from m16e.ktfact import KTF_COL_ORDER, KTF_SORTABLE_COLS, KTF_TYPE, KTF_COLS, ACT_NAV_FIRST, ACT_NAV_PREV, ACT_NAV_NEXT, \
    ACT_NAV_LAST
from m16e.ui.actions import UiAction, get_action_name
from m16e.ui.elements import UiButton, BTN_SUBMIT, BTN_SUCCESS, BTN_WARNING, UiIcon, BT_SIZE_XSMALL
from m16e.user_factory import is_in_group
from m16e.views.base_view import BaseView, get_var_from_dict
from m16e.views.plastic_table import PlasticTable


LIST_TITLE_HEADER = 'list_title_div'
# BT_CREATE_RECORD = 'bt_create_record'
BT_SUBMIT_ID = 'bt_submit'
BT_NEW_RECORD_ID = 'bt_new_record'
BT_CLEAR_ID = 'bt_clear'
BT_PURGE_ID = 'bt_purge'
KQV_INVERT_ORDER = KQV_PREFIX + 'invert_order'


def remove_if_exists( list_items, value ):
    try:
        list_items.remove( value )
    except ValueError:
        pass
#--END remove_if_exists


class BaseListPlasticView( BaseView ):
    '''
    To use order in select:
    - Invoke __init__( order_hidden=False ) and add qv_order to self.qdata

    '''
    exclude_from_url = [ KQV_SHOW_ALL ]


    #------------------------------------------------------------------
    def __init__( self,
                  db,
                  order_type=KDT_INT,
                  order_value=1,
                  invoke_process_form=False,
                  order_hidden=True ):
        super( BaseListPlasticView, self ).__init__( db )
        T = current.T
        self.order_type = order_type
        self.order_value = order_value
        self.query_vars = Storage()
        self.default_vars = Storage()
        self.append_var( KQV_OFFSET,
                         fld_type=KDT_INT,
                         none_overwrites=False,
                         value=0,
                         hidden=True )
        self.append_var( KQV_LIMIT,
                         fld_type=KDT_INT,
                         none_overwrites=False,
                         value=100 )
        if order_hidden:
            self.append_var( KQV_ORDER,
                             fld_type=order_type,
                             none_overwrites=False,
                             value=order_value,
                             hidden=True )
        else:
            self.append_var( KQV_ORDER,
                             fld_type=order_type,
                             none_overwrites=False,
                             value=order_value )

        self.new_record_action = UiAction( action_name=ACT_NEW_RECORD )
        self.clear_qdata_action = ACT_CLEAR
        self.new_record_title = T( 'New record' )
        self.list_title = None
        self.list_subtitle = None
        self.list_subtitle_2 = None

        self.edit_function_name = 'edit'

        self.show_var_values = False

        self.qdata = {}
        self.tdef = {}
        self.extra_rows = []
        self.list_rows = None
        self.row_count = None
        self.prev_query_data = None

        self._plastic_table = None

        self.nav = Storage()
        self.nav.width = 3
        self.nav.function_name = self.function_name

        self.hide_columns = []

        self.form_id = None
        self.table_id = None
        self.content_div_id = None

        self.transport_text = T( 'Transport' )
        self.totals_text = T( 'Total' )
        self.highlight_row_class = 'highlight_row'

        self.next_c = None
        self.next_f = None
        self.next_args = None
        self.next_vars = None

        self.ui_buttons = Storage()
        self.inhibit_actions = []
        self.form = None

        self.invoke_process_form = invoke_process_form
        self.totalizers = Storage()
        # self.page = 0


        #         term.printDebug( 'query_vars: %s' % repr( self.query_vars ) )


    def get_inhibit_actions( self ):
        return self.inhibit_actions


    def append_var( self,
                    var_name,
                    def_tuple=None,
                    fld_type=None,
                    none_overwrites=True,
                    value=None,
                    hidden=False ):
        #         term.printDebug( 'var_name: %s' % ( repr( var_name ) ) )
        self.query_vars[ var_name ] = value
        if def_tuple:
            if isinstance( def_tuple, tuple ):
                var_name = def_tuple[ 0 ]
                fld_type = def_tuple[ 1 ]
                none_overwrites = def_tuple[ 2 ]
            else:
                raise Exception( 'Bad tuple: %s (type: %s)' %
                                 (repr( def_tuple ), type( def_tuple )) )
        self.default_vars[ var_name ] = Storage( fld_type=fld_type,
                                                 none_overwrites=none_overwrites,
                                                 value=value,
                                                 hidden=hidden )


#         term.printDebug( 'default_vars: %s' % ( repr( self.default_vars ) ) )

    def get_hidden_vars( self ):
        hv_set = { }
        for v in self.default_vars:
            if self.default_vars[ v ].hidden:
                hv_set[ v ] = self.query_vars[ v ]
        #         term.printDebug('hv_set: %s' % (repr(hv_set)))
        return hv_set


    def get_new_record_button( self ):
        T = current.T
        nr_bt = UiButton( text=self.new_record_title,
                          ui_icon=UiIcon( 'plus' ),
                          tip=T( 'Create new record' ),
                          action=self.new_record_action,
                          input_id=BT_NEW_RECORD_ID,
                          button_style=BTN_SUCCESS )
        return nr_bt


    def parse_request_args( self ):
        pass


    def parse_request_var( self, var_name, post_vars=None, get_vars=None ):
        request = current.request
        dv = self.default_vars[ var_name ]
        v = None
        try:
            # term.printDebug( '%s:\n>> post: %s\n>> get: %s' % (var_name,
            #                                                    repr( post_vars ),
            #                                                    repr( get_vars )) )
            var_type = dv.fld_type
            none_overwrites = dv.none_overwrites
            # 1st, get from constants
            (found, value) = self.get_constant_value( var_name )
            # term.printDebug( 'var_name: %s, found: %s; value: %s' %
            #                  (var_name, repr( found ), repr( value ) ) )
            if found:
                v = value
                self.set_constant_value( var_name, v )
            else:
                if request.env.request_method == 'GET':
                    (found, value) = get_var_from_dict( get_vars, var_name )
                    # term.printDebug( 'var_name: %s, found: %s; value: %s' %
                    #                  (var_name, repr( found ), repr( value )) )
                elif request.env.request_method == 'POST':
                    (found, value) = get_var_from_dict( post_vars, var_name )
                    # term.printDebug( 'var_name: %s, found: %s; value: %s' %
                    #                  (var_name, repr( found ), repr( value )) )
                    if not found and self.default_vars[ var_name ].hidden:
                        (found, value) = get_var_from_dict( get_vars, var_name )
                        # term.printDebug( 'var_name: %s, found: %s; value: %s' %
                        #                  (var_name, repr( found ), repr( value )) )
                if found:
                    v = value

            # term.printDebug( 'v: %s' % repr( v ) )
            # if v and var_name in (KQV_ORDER) and self.order_type != KDT_CHAR:
            # term.printDebug( 'v (%s): %s' % (type( v ), repr( v )) )  # , prompt_continue=True )
            #     # v = v[0]
            if v or none_overwrites:
                if var_type in (KDT_INT, KDT_SELECT_INT):
                    if v == 'None':
                        v = 0
                    v = int( v or 0 )
                elif var_type == KDT_INT_LIST:
                    # term.printDebug( 'v: %s' % repr( v ) )
                    if v == 'None' or v is None:
                        v = [ ]
                    elif is_sequence( v ):
                        v = [ int( e ) for e in v ]
                    else:
                        if '[' in v:
                            v = v[ 1: -1 ]
                        v = [ int( s.strip() ) for s in v.split( ',' ) ]
                elif var_type in (KDT_CHAR, KDT_SELECT_CHAR):
                    v = str( v or '' )
                elif var_type == KDT_BOOLEAN:
                    v = bool( v or False )
                elif var_type == KDT_DATE:
                    if v:
                        v = htmlcommon.parse_date( v )
                    else:
                        v = None
                elif var_type == KDT_TIME:
                    if v:
                        v = htmlcommon.parse_time( v )
                    else:
                        v = None
                elif var_type == KDT_TIMESTAMP:
                    if v:
                        v = htmlcommon.parse_timestamp( v )
                    else:
                        v = None
            if found:
                self.query_vars[ var_name ] = v
        except:
            term.printLog( 'var_name: %s; val: %s\npost_vars: %s\nget_vars: %s' %
                           (var_name, repr( v ), repr( post_vars ), repr( get_vars )) )
            t, v, tb = sys.exc_info()
            traceback.print_exception( t, v, tb )
            raise


    def parse_request_vars( self, post_vars=None, get_vars=None ):
        request = current.request

        #         term.printDebug( 'post_vars: %s' % repr( post_vars ) )
        #         term.printDebug( 'get_vars: %s' % repr( get_vars ) )
        #         term.printDebug( 'request.vars.keys: %s' % repr( request.vars.keys() ) )
        if self.show_var_values:
            term.printDebug( 'request.vars: %s' % repr( request.vars ) )
        #         term.printLog( 'query_vars: %s' % ( repr( self.query_vars ) ) )
        #         term.printLog( 'default_vars: %s' % ( repr( self.default_vars ) ) )
        if not post_vars:
            post_vars = request.post_vars
        if not get_vars:
            get_vars = request.get_vars
        #         changed = Storage()

        self.action = post_vars.action
        term.printDebug( 'action: ' + repr( self.action ) )
        # term.printDebug( 'print_query: %s' % ( repr( self.print_query ) ) )
        for var_name in self.default_vars:
            self.parse_request_var( var_name, post_vars=post_vars, get_vars=get_vars )
        request = current.request
        self.next_c = request.vars.next_c
        self.next_f = request.vars.next_f
        self.next_args = request.vars.next_args or []
        self.next_vars = request.vars.next_vars or {}



    def get_user_query_data( self ):
        return QueryData()


    def get_query_data( self, orderby=None ):
        #        term.printDebug( 'orderby: %s' % ( repr( orderby ) ),
        #                         print_trace=True )
        #         term.printLog( 'query_vars: %s' % repr( self.query_vars ) )
        qd = self.get_user_query_data()
        lim = self.query_vars.get( KQV_LIMIT )
        qd.limit = int( lim or 100 )

        ofs = self.query_vars.get( KQV_OFFSET )
        qd.offset = int( ofs or 0 )
        #        term.printDebug( 'qd.offset: %s' % repr( qd.offset ) )
        if orderby is None:
            orderby = self.query_vars[ KQV_ORDER ]

        if not orderby:
            orderby = self.get_orderby()
        #        term.printDebug( 'orderby: %s' % repr( orderby ) )
        try:
            n_order = int( orderby )
            qd.order = str( abs( n_order ) )
            if n_order < 0:
                qd.order += ' desc'
        except:
            qd.order = orderby
            pass

        #         term.printDebug( repr( qd ) )
        return qd


    def get_alias( self ):
        return [ ]


    def get_query_select( self ):
        return 'select *'


    def get_query_from( self ):
        #         return 'from %(table_name)s' % { 'table_name': self.table_model.table_name }
        return 'from %(table_name)s' % { 'table_name': self.get_table_name() }


    def get_query_group_by( self ):
        return None


    def get_record_list( self,
                         qd=None,
                         alias=None,
                         print_query=None,
                         force_refresh=False ):
        #        term.printLog( 'qd: %s' % ( repr( qd ) ) )
        #        term.printLog( 'print_query: %s' % ( repr( print_query ) ) )
        if self.list_rows is None or force_refresh:
            if print_query is None:
                print_query = self.print_query
            if alias is None:
                alias = self.get_alias()
            query = '%s %s' % (self.get_query_select(), self.get_query_from())
            group = self.get_query_group_by()
            args = { }
            if qd:
                if qd.where:
                    q = replace_alias( qd.where, alias )
                    query += ' where (' + q + ')'
                if group:
                    query += ' group by ' + group
                if qd.order:
                    query += ' order by ' + qd.order
                if qd.limit:
                    query += ' limit %d ' % (qd.limit)
                if qd.offset is not None:
                    query += ' offset %d ' % (qd.offset)
                if qd.args:
                    args = qd.args
            #         term.printLog( 'query: %s\nargs: %s' % ( query, repr( args ) ) )
            if print_query:
                term.printLog( 'sql: ' + query % args )
                # term.printDebug( 'sql: ' + query % args )
            rows = self.db.executesql( query, placeholders=args, as_dict=True )
            self.list_rows = [ ]
            for r in rows:
                self.list_rows.append( Storage( r ) )
        return self.list_rows


    def get_record_count( self,
                          qd=None,
                          alias=None,
                          print_query=None,
                          force_refresh=False ):
        term.printDebug( 'self.row_count: %s' % repr( self.row_count ) )
        if self.row_count is None \
          or force_refresh \
          or str( self.prev_query_data ) != str( qd ):
            if print_query is None:
                print_query = self.print_query
            if alias is None:
                alias = self.get_alias()
            query = 'select count( * ) %s' % (self.get_query_from())
            group = self.get_query_group_by()
            args = { }
            if qd:
                if qd.where:
                    q = replace_alias( qd.where, alias )
                    query += ' where (' + q + ')'
                    # term.printDebug( 'query: %s' % ( query ) )
                if qd.args:
                    args = qd.args
                if group:
                    query += ' group by ' + group
            if print_query:
                term.printLog( 'query: %s\nargs: %s' % (query, repr( args )) )
            res = self.db.executesql( query, placeholders=args )
            if group:
                self.row_count = len( res )
            else:
                self.row_count = res[ 0 ][ 0 ]
        #             term.printLog( 'sql: ' + db._lastsql )

        return self.row_count


    def register_tdef( self, tdef ):
        self.tdef = storagize( tdef )


    def register_qdata( self, qdata ):
        self.qdata = storagize( qdata )


    def get_table_view_dict( self ):
        self.tdef = {}
        return self.tdef


    def get_table_qdata_dict( self, extra_buttons={} ):
        q_data = {}
        return q_data


    def get_orderby( self ):
        # term.printDebug( 'query_vars: %s' % repr( self.query_vars ) )
        orderby_expr = None
        if self.tdef.get( KTF_SORTABLE_COLS ):
            dv_order = self.default_vars.get( KQV_ORDER )
            if dv_order:
                if self.default_vars[ KQV_ORDER ].fld_type == KDT_INT:
                    qv_order = int( self.query_vars.get( KQV_ORDER ) or 1 )
                    if qv_order == 0:
                        qv_order = 1
                    idx = abs( qv_order ) - 1
                    # s_idx = self.get_sort_col_index_by_name( self.tdef[ KTF_COL_ORDER ][ idx ] )
                    orderby_expr = self.tdef[ KTF_COL_ORDER ][ idx ]
                    if qv_order < 0:
                        orderby_expr += ' desc'

                elif self.default_vars[ KQV_ORDER ].fld_type == KDT_CHAR:
                    orderby_expr = self.query_vars[ KQV_ORDER ]
            # else:

            # if self.default_vars[ KQV_ORDER ].fld_type == KDT_INT:
            #     qv_order = int( self.query_vars.get( KQV_ORDER ) or 1 )
            #     if qv_order == 0:
            #         qv_order = 1
            #     idx = abs( qv_order ) - 1
            #     # s_idx = self.get_sort_col_index_by_name( self.tdef[ KTF_COL_ORDER ][ idx ] )
            #     orderby_expr = self.tdef[ KTF_COL_ORDER ][ idx ]
            #     if qv_order < 0:
            #         orderby_expr += ' desc'
            #
            # elif self.default_vars[ KQV_ORDER ].fld_type == KDT_CHAR:
            #     orderby_expr = self.query_vars[ KQV_ORDER ]

        #        term.printDebug( 'orderby_expr: %s' % repr( orderby_expr ) )
        return orderby_expr


    # def get_orderby( self ):
    #     if self.query_vars[ KQV_ORDER ] and self.order_type == KDT_INT:
    #         n_order = int( self.query_vars[ KQV_ORDER ] )
    #         if n_order < 0:
    #             return '%d %s' % (abs( int( self.query_vars[ KQV_ORDER ] ) ), ' desc')
    #         else:
    #             return self.query_vars[ KQV_ORDER ]
    #     return self.query_vars[ KQV_ORDER ]
    #
    #
    def init_default_buttons( self ):
        T = current.T
        # submit
        # icon = I( _class='glyphicon glyphicon-refresh glyphicon-white',
        #           _style='padding-right: 0.5em;' )
        self.inhibit_actions = self.get_inhibit_actions()
        if not ACT_SUBMIT in self.inhibit_actions:
            self.ui_buttons[ ACT_SUBMIT ] = UiButton( text=T( 'Requery' ),
                                                      ui_icon=UiIcon( 'refresh' ),
                                                      tip=T( 'Apply parameters to query' ),
                                                      action=UiAction( action_name=ACT_SUBMIT ),
                                                      input_id=BT_SUBMIT_ID,
                                                      button_style=BTN_SUBMIT,
                                                      css_class='btn-lg')
        if not ACT_NEW_RECORD in self.inhibit_actions:
            self.ui_buttons[ ACT_NEW_RECORD ] = self.get_new_record_button()

        if not ACT_CLEAR in self.inhibit_actions:
            self.ui_buttons[ ACT_CLEAR ] = UiButton( text=T( 'Clear' ),
                                                     ui_icon=UiIcon( 'unchecked' ),
                                                     tip=T( 'Reset parameters' ),
                                                     input_id=BT_CLEAR_ID,
                                                     button_style=BTN_WARNING,
                                                     button_size=BT_SIZE_XSMALL,
                                                     action=UiAction(action_name=ACT_CLEAR) )


    #----------------------------------------------------------------------
    def get_totalizers( self ):
        return self.totalizers

    #----------------------------------------------------------------------
    def get_selections( self ):
        return []

    #----------------------------------------------------------------------
    def get_moving_rows( self ):
        return []

    #----------------------------------------------------------------------
    def get_table_id( self ):
        return self.table_id


    #----------------------------------------------------------------------
    def get_form_id( self ):
        return self.form_id


    #----------------------------------------------------------------------
    def get_content_div_id( self ):
        return self.content_div_id

    #----------------------------------------------------------------------
    def get_view_dict( self, reload=False ):
        #------------------------------------------------------------------
        def exclude_columns( tdef, column_list=[] ):
            src_cols = tdef.get( KTF_COL_ORDER )
            if src_cols:
                col_order = []
                for col in tdef[ KTF_COL_ORDER ]:
                    if not col in column_list:
                        col_order.append( col )
                tdef[ KTF_COL_ORDER ] = col_order
            src_cols = tdef.get( KTF_SORTABLE_COLS )
            if src_cols:
                sortable_cols = []
                for col in tdef[ KTF_SORTABLE_COLS ]:
                    if not col in column_list:
                        sortable_cols.append( col )
                tdef[ KTF_SORTABLE_COLS ] = sortable_cols
        #------------------------------------------------------------------
        # term.printDebug( 'self.tdef.col_order: %s' % repr( self.tdef ),
        #                  print_trace=True)
        # term.printDebug( 'self.hide_columns: %s' % repr( self.hide_columns ) )
        # term.printDebug( 'self.tdef: %s' % repr( self.tdef ) )
        if not self.tdef or reload:
            tdef = copy.deepcopy( self.get_table_view_dict() )
            exclude_columns( tdef, self.hide_columns )
            self.tdef = storagize( tdef )
        # term.printDebug( 'self.tdef: %s' % repr( self.tdef ) )
        # term.printDebug( 'self.tdef.col_order: %s' % repr( self.tdef ) )
        return self.tdef


    #----------------------------------------------------------------------
    def get_qdata_dict( self, extra_buttons={}, reload=False ):
        if not self.qdata or reload:
            self.qdata = storagize( self.get_table_qdata_dict( extra_buttons=extra_buttons ) )
        return self.qdata

    #------------------------------------------------------------------
    def get_url_vars(self):
        qvars = Storage()
        qv_dict = self.get_opvars()
        for k in qv_dict:
            if qv_dict[k] and k not in self.exclude_from_url:
                qvars[k] = qv_dict[k]
        return qvars


    # def get_sort_col_index_by_name( self, column_name ):
    #     return self.tdef[ KTF_COL_ORDER ].index( column_name )


    #------------------------------------------------------------------
    def get_plastic_table( self, reload=False ):

#         term.printDebug( 'self.tdef: %s' % repr( self.tdef ) )
        if not self._plastic_table or reload:
#             term.printDebug( 'self.qdata: %s' % repr( self.qdata ) )
            self.init_default_buttons()
            self.get_view_dict( reload=reload )
            self.get_qdata_dict( reload=reload )
            self._plastic_table = PlasticTable( self )
        return self._plastic_table


    def get_filter_panel( self ):
        return ''


    def get_nav_options( self,
                         rec_count,
                         opvars=Storage(),
                         offset=0,
                         limit=100,
                         width=None,
                         function_name='index',
                         title_css_class=None,
                         cell_css_class=None,
                         table_id=None,
                         extra_rows=None,
                         extra_rows_style=None,
                         show_options=True,
                         is_header=True ):
#         term.printDebug( 'limit: %s; offset: %s; rec_count: %s; w: %d' %
#                          (limit, offset, rec_count, width) )
        if not table_id:
            table_id = self.get_table_id()
        if not extra_rows:
            extra_rows=self.get_extra_rows()
        if not extra_rows_style:
            extra_rows_style=self.get_extra_rows_style()
        if not width:
            width = self.nav.width
#         term.printDebug( 'width: %s' % repr( width ) )
#         term.printDebug( 'self.nav.width: %s' % repr( self.nav.width ) )
        return self.get_plastic_table().get_nav_options( rec_count,
                                                         opvars=opvars,
                                                         offset=offset,
                                                         limit=limit,
                                                         width=width,
                                                         function_name=function_name,
                                                         title_css_class=title_css_class,
                                                         cell_css_class=cell_css_class,
                                                         table_id=table_id,
                                                         extra_rows=extra_rows,
                                                         show_options=show_options,
                                                         extra_rows_style=extra_rows_style,
                                                         is_header=is_header )

    #------------------------------------------------------------------
    def get_opvars( self ):
        # term.printDebug( 'opvars: %s' % repr( self.query_vars ) )
        return self.query_vars

    #------------------------------------------------------------------
    def get_table_panel( self,
                         rows,
                         controller=None,
                         function_name='index',
                         order=None,
                         query_vars=None,
                         table_id=None ):
        if table_id is None:
            table_id = self.get_table_id()
#         term.printDebug( 'self.tdef: %s' % repr( self.tdef ) )
        pt = self.get_plastic_table( reload=True )
#         term.printDebug( 'self.tdef: %s' % repr( self.tdef ) )
#         term.printDebug( 'order: %s' % repr( order ) )
#         term.printDebug( 'query_vars: %s' % repr( self.query_vars ) )
        return pt.get_table( self.list_rows,
                             transport_text=self.transport_text,
                             totals_text=self.totals_text,
                             totalizers=self.get_totalizers(),
                             controller=controller,
                             function_name=function_name,
                             order=order,
                             selections=self.get_selections(),
                             moving_rows=self.get_moving_rows(),
                             highlight_row_class=self.highlight_row_class,
                             query_vars=query_vars,
                             table_id=table_id )


    def get_table( self ):
        if not self.get_table_name():
            return (None, 0, [])

        # term.printDebug( 'table_name: %s' % self.get_table_name() )

        order = self.get_orderby()
        qd = self.get_query_data( order )
        # term.printDebug( 'query_vars: %s' % repr( self.query_vars ),
        #                  prompt_continue=True )
        rec_count = self.get_record_count( qd )
#         term.printLog( 'rec_count: %s \nqd: %s' % (repr(rec_count), repr( qd )) )
        if qd.offset >= rec_count or self.query_vars[ KQV_OFFSET ] >= rec_count:
            qd.offset = 0
            self.query_vars[ KQV_OFFSET ] = 0
#        term.printLog( 'print_query: %s' % ( repr( self.print_query ) ) )
#        term.printLog( 'qd: %s' % ( str( qd ) ) )
        rows = self.get_record_list( qd )
#         term.printDebug( 'self.query_vars.qv_order: %s' % repr( self.query_vars.qv_order ) )
        table = self.get_table_panel( rows,
                                      function_name=self.function_name,
                                      order=order,
                                      query_vars=self.query_vars )
#         term.printDebug( 'rec_count: %s' % repr( rec_count ) )
        return table, rec_count, rows


    def get_extra_rows( self ):
        return []


    def get_extra_rows_style( self ):
        return None


    def get_table_form( self, table, rec_count, rows ):
        '''
        Args:
            table:
            rec_count:
            rows:

        Returns:
            form ->
                nav_table
                table
        '''
        T = current.T
        if not self.list_title:
            self.list_title = T( 'List of %(table_name)s',
                                 dict( table_name=self.get_table_name() ) )
        opvars = self.get_opvars()
#         term.printDebug( 'opvars: %s' % repr( opvars ) )
        nav_table = self.get_nav_options( rec_count,
                                          opvars=opvars,
                                          offset=self.query_vars[ KQV_OFFSET ],
                                          limit=self.query_vars[ KQV_LIMIT ],
                                          width=self.nav.width,
                                          function_name=self.nav.function_name )
        # term.printDebug( 'nav_table: %s' % nav_table.xml( ) )
        # self.form = FORM( hidden={ KQV_OFFSET: self.query_vars[ KQV_OFFSET ] } )
        hv_set = self.get_hidden_vars()
#         term.printDebug('hv_set: %s' % (repr(hv_set)))
        self.form = FORM( hidden=hv_set )
        if self.form_id:
            self.form[ '_id' ] = self.form_id
        else:
            fid = self.get_form_id()
            if fid:
                self.form[ '_id' ] = fid
        self.form.append( nav_table )
        self.form.append( table )
        nav_footer = self.get_nav_options( rec_count,
                                           offset=self.query_vars[ KQV_OFFSET ],
                                           limit=self.query_vars[ KQV_LIMIT ],
                                           width=self.nav.width,
                                           function_name=self.nav.function_name,
                                           show_options=False,
                                           is_header=False )
        self.form.append( nav_footer )
        # term.printDebug( 'form: %s' % self.form.xml() )
        return self.form


    #------------------------------------------------------------------
    def get_list_title( self ):
        T = current.T
        if not self.list_title:
            self.list_title = T( 'List of %(table_name)s',
                                 dict( table_name=self.get_table_name() ) )
        return self.list_title


    #------------------------------------------------------------------
    def get_list_subtitle( self ):
        return self.list_subtitle


    #------------------------------------------------------------------
    def get_table_div( self, table, rec_count, rows ):
        '''
        Args:
            table:
            rec_count:
            rows:

        Returns:
            div ->
                title (H3)
                subtitle (H4)
                form ->

        '''
        self.form = None
        if self.get_table_name():
            self.form = self.get_table_form( table, rec_count, rows )
            # term.printDebug( 'self.form: %s' % self.form.xml( ) )

        T = current.T
        div = DIV()
        div_id = self.get_content_div_id()
        if div_id:
            div[ '_id' ] = div_id
        s = self.get_list_title()
        if s:
            div.append( H3( s ) )
        s = self.get_list_subtitle()
        if s:
            div.append( H4( s ) )

        if self.form:
            div.append( self.form )
#         term.printDebug( 'div: %s' % div.xml() )
        return div

    #------------------------------------------------------------------
    def get_table_div_element( self ):
#         if not self.tdef:
#             self.tdef = self.get_viewg173_dict()
        table, rec_count, rows = self.get_table()
        div = self.get_table_div( table, rec_count, rows )
        # term.printDebug( 'div: %s' % div.xml() )
        return div

    #------------------------------------------------------------------
    def get_edit_record_function(self):
        return 'edit'


    #------------------------------------------------------------------
    def get_new_record_function(self):
        return 'edit'


    #------------------------------------------------------------------
    def process_new_record_action(self):
        f = self.get_new_record_function()
#         term.printDebug( 'f: %s ' % repr( f ) )
        self.set_result( redirect=URL( c=self.controller_name,
                                       f=f,
                                       args=[ 0 ] ) )


    #------------------------------------------------------------------
    def process_clear_qdata_action(self):
        request = current.request
        term.printDebug( 'request.vars: %s' % repr( request.vars ) )
        term.printDebug( 'request.get_vars: %s' % repr( request.get_vars ) )
        term.printDebug( 'request.post_vars: %s' % repr( request.post_vars ) )
        self.result.redirect = URL( c=self.controller_name,
                                    f=self.function_name,
                                    vars=request.get_vars )


    #------------------------------------------------------------------
    def process_pre_validation_actions( self ):
        term.printDebug( 'self.action: %s ' % repr( self.action ) )
        # term.printDebug( 'self.clear_qdata_action: %s ' % repr( self.clear_qdata_action ) )
        if self.action:
            action_name = get_action_name( self.new_record_action )
            if self.action == action_name:
                self.process_new_record_action()
            elif self.action == self.clear_qdata_action:
                self.process_clear_qdata_action()
            elif self.action in (ACT_NAV_FIRST,
                                 ACT_NAV_PREV,
                                 ACT_NAV_NEXT,
                                 ACT_NAV_LAST):
                self.process_nav()


    def post_process( self, div_content ):
        self.set_result( dict( content=div_content,
                               is_manager=is_in_group( 'manager' ),
                               is_dev=is_in_group( 'dev' ),
                               page_js=self.get_page_js() ) )


    def process_nav( self ):
        qd = self.get_query_data()
        self.row_count = self.get_record_count( qd )
#         term.printDebug( 'self.row_count: %s' % repr( self.row_count ) )
#         term.printDebug( 'limit: %s' % repr( self.query_vars[ KQV_LIMIT ] ) )
        if self.action == ACT_NAV_FIRST:
            self.query_vars[ KQV_OFFSET ] = 0
        elif self.action == ACT_NAV_NEXT:
            if self.query_vars[ KQV_OFFSET ] + self.query_vars[ KQV_LIMIT ] < self.row_count:
                self.query_vars[ KQV_OFFSET ] += self.query_vars[ KQV_LIMIT ]
            else:
                self.query_vars[ KQV_OFFSET ] = self.row_count - self.query_vars[ KQV_LIMIT ]

        elif self.action == ACT_NAV_PREV:
            if self.query_vars[ KQV_OFFSET ] >= self.query_vars[ KQV_LIMIT ]:
                self.query_vars[ KQV_OFFSET ] -= self.query_vars[ KQV_LIMIT ]
            else:
                self.query_vars[ KQV_OFFSET ] = 0

        elif self.action == ACT_NAV_LAST:
            self.query_vars[ KQV_OFFSET ] = self.row_count - self.query_vars[ KQV_LIMIT ]
        if self.query_vars[ KQV_OFFSET ] < 0:
            self.query_vars[ KQV_OFFSET ] = 0
        # q_vars = { k: self.query_vars[ k ]
        #             for k in self.query_vars
        #                 if self.query_vars[ k ] }
        # page = (self.query_vars[ KQV_OFFSET ] / self.query_vars[ KQV_LIMIT ]) + 1
        # term.printDebug( 'ofs: %s; lim: %s; page: %d' %
        #                  ( repr( self.query_vars[ KQV_OFFSET ] ),
        #                    repr( self.query_vars[ KQV_LIMIT ] ),
        #                    page ) )
        # self.set_result( redirect=URL( c=self.controller_name,
        #                                f=self.function_name,
        #                                vars= q_vars ),
        #                  stop_execution=True )


    def process_form_action( self, form ):
        pass


    def process_form( self ):
        response = current.response
        request = current.request
        session = current.session
        T = current.T

        if not self.form:
            return True

        # term.printDebug( 'form: %s' % self.form.xml() )
        accepted = self.form.accepts( request.vars, session, dbio=False )
        if accepted:
            term.printDebug( 'form.vars: ' + repr( self.form.vars ) )
            term.printDebug( 'self.action: %s' % repr( self.action ) )
            self.process_form_action( self.form )
        elif self.form.errors:
            term.printLog( 'form.errors: ' + repr( self.form.errors ) )
            term.printLog( 'form.errors: ' + str( self.form.errors ) )
            response.flash = T( 'Form has errors' )
        self.errors = self.form.errors
        # term.printDebug( 'form: %s' % self.form.xml( ) )
        return accepted


    def do_process( self ):
        request = current.request
        session = current.session

        term.printLog( 'request.args: ' + repr( request.args ) )
        term.printLog( 'request.vars.keys: ' + repr( request.vars.keys() ) )
        if self.show_var_values:
            term.printDebug( 'request.vars: %s' % repr( request.vars ) )

        self.parse_request_args()
        # term.printDebug( 'request.vars: %s' % repr( request.vars ) )
        if self.result.redirect:
            return self.result
#         action = request.post_vars.action
#         term.printDebug( 'query_vars: %s' % repr( self.query_vars ),
#                          prompt_continue=True )

        self.parse_request_vars( request.post_vars, request.get_vars )
        # term.printLog( 'self.action: ' + repr( self.action ) )
        term.printDebug( 'query_vars: %s' % repr( self.query_vars ) )

        if self.result.redirect:
            return self.result

        # term.printDebug( 'self.query_vars: ' + repr( self.query_vars ) )
        # page = 0
        # if request.args:                    # page
        #     page = int( request.args( 0 ) )
        #     self.query_vars.qv_offset = self.query_vars.qv_limit * (page -1)
        # term.printDebug( 'page: %s' % repr( page ) )
        self.process_pre_validation_actions()
        if self.result.redirect:
            return self.result

        self.get_plastic_table()

        div = self.get_table_div_element()
        if self.invoke_process_form:
            self.process_form()
        if self.result.redirect:
            return self.result

        self.post_process( div )
        # term.printDebug( 'result: %s' % ( repr( self.result ) ) )
        return self.result


#------------------------------------------------------------------
def split_chk_var( var_name ):
    parts = var_name.split( '_' )
    prefix = '_'.join( parts[:-1] ) + '_'
    value = int( parts[-1] )
    return prefix, value


