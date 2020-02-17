'''
Created on 30/05/2014

@author: carlos
'''

from gluon.globals import current
from gluon.html import THEAD, TR, TH, IMG, URL, A, SPAN, TFOOT, TABLE, TD, \
    TBODY, XML, B, BUTTON, DIV, SELECT, OPTION, HR
from gluon.storage import Storage
from m16e import term, htmlcommon, ktfact
from m16e.kommon import KQV_ORDER, is_sequence, KDT_RAW, KDT_INT, \
    KDT_CHAR, KDT_BLOB_IMG, KDT_XML, KDT_BOOLEAN, KQV_LIMIT, KQV_OFFSET, \
    KDT_SELECT_INT, KDT_SELECT_CHAR, KDT_FILE, ACT_SUBMIT, ACT_CLEAR, ACT_NEW_RECORD, KDT_DEC, KDT_MONEY
# from m16e.ktfact import KTF_TITLE, KTF_COLS, KTF_CSS_CLASS, KTF_TOTALIZE, \
#     KTF_ROW_ID_MASK, KTF_ROW_CLASS, KTF_KEY_LIST, KTF_CELL_LINK, KTF_ARGS_F, \
#     KTF_ARGS_V, KTF_VARS_F, KTF_VARS_V, KTF_AJAX_TARGET, KTF_EDITABLE, \
#     KTF_EDITABLE_CLASS, KTF_MV_INSERT_POINT, KTF_MV_LINK_TABLE, KTF_MV_FIELD_ID, \
#     KTF_BUTTON, KTF_MSG, KTF_TYPE, KTF_SELECT_INT, KTF_SPAN, KTF_LINK_C, KTF_LINK_F, \
#     KTF_COL_ORDER, KTF_CELL_IDS, K_CHK_ID_PREFIX, KTF_HIDE_ZEROS, KTF_VALUE, KTF_BUTTONS, KTF_DECIMALS, \
#     KTF_SELECT_LIVE_SEARCH, KTF_FILTER_PANEL
from m16e.ktfact import KTF_COL_ORDER
from m16e.structs import get_non_empty_vars
from m16e.ui import elements
from m16e.ui.actions import UiAction

NAV_DIV_ID = 'nav_div_id'
LIST_DIV_ID = 'list_div_id'



class PlasticTable( object ):


    def __init__( self,
                  plastic_view ):
        '''
        tdef: table defenition
        qdata: query data panel (and navigation)
        '''
        self.plastic_view = plastic_view
        self.nav_span_prev = SPAN()
        self.nav_span_next = SPAN()

        # self.tdef = storagize( tdef )
        # self.qdata = storagize( qdata )
        # self.query_vars = query_vars
        # self.ui_buttons = ui_buttons
#         term.printDebug( 'self.tdef: %s' % repr( self.tdef ) )
#         term.printDebug( 'self.qdata: %s' % repr( self.qdata ) )


    def get_check_box_def( self, cb_prefix ):
        tdef = self.plastic_view.get_view_dict()
#         term.printDebug( 'self.tdef: %s' % repr( self.tdef ) )
        for c in tdef[ ktfact.KTF_COLS ]:
            col = tdef[ ktfact.KTF_COLS ][ c ]
            if col.checkbox:
                if col.checkbox.name == cb_prefix:
                    return col.checkbox, c
        return None


    def get_orderby( self, order=None, orderby=None ):
        #    term.printLog( 'order: %s' % repr( order ) )
        tdef = self.plastic_view.get_view_dict()
        if order:
            i = 1
            for t in tdef[ ktfact.KTF_COL_ORDER ]:
                if not orderby and i == 1:
                    orderby = t
    #            term.printLog( 'i: %d; t: %s' % ( i, repr( t ) ) )
                if i == abs( order ):
                    orderby = t
                    if order < 0:
                        orderby += ' desc'
    #                term.printLog( repr( orderby ) )
                    break
                i += 1
        elif not orderby:
            orderby = tdef[ ktfact.KTF_COL_ORDER ][0]
        return orderby


    def get_nav_last( self, function_name, q_vars, rec_count ):
        T = current.T
        # u_vars = q_vars.copy()
        # u_vars[ KQV_OFFSET ] = rec_count - q_vars[ KQV_LIMIT ]
        # url = URL( f=function_name,
        #            vars=u_vars )
        ui_bt = elements.UiButton( ui_icon=elements.UiIcon( elements.ICON_NAV_END,
                                                            dark_background=False ),
                                   tip=T( 'Go to last page' ),
                                   button_style=elements.BTN_INFO,
                                   button_size=elements.BT_SIZE_XSMALL,
                                   action=UiAction(action_name=ktfact.ACT_NAV_LAST ),
                                   css_class='page_nav_button' )
        return ui_bt.get_html_button( css_style='margin-left: 2em;' )



    def get_nav_next( self, function_name, q_vars, rec_count ):
        T = current.T
        # term.printDebug( 'ofs: %s; lim: %s' % ( repr( q_vars[ KQV_OFFSET ] ),
        #                                         repr( q_vars[ KQV_LIMIT ] ) ) )
        # u_vars = q_vars.copy()
        # if u_vars[ KQV_OFFSET ] + u_vars[ KQV_LIMIT ] < rec_count:
        #     u_vars[ KQV_OFFSET ] += u_vars[ KQV_LIMIT ]
        # else:
        #     u_vars[ KQV_OFFSET ] = rec_count - u_vars[ KQV_LIMIT ]
        # url = URL( f=function_name,
        #            vars=u_vars )
        ui_bt = elements.UiButton( ui_icon=elements.UiIcon( elements.ICON_NAV_NEXT,
                                                            dark_background=False ),
                                   tip=T( 'Go to next page' ),
                                   button_style=elements.BTN_INFO,
                                   button_size=elements.BT_SIZE_XSMALL,
                                   action=UiAction(action_name=ktfact.ACT_NAV_NEXT ),
                                   css_class='page_nav_button' )
        return ui_bt.get_html_button( css_style='margin-left: 2em;' )



    def get_nav_prev( self, function_name, q_vars ):
        T = current.T
        # u_vars = q_vars.copy()
        # if u_vars[ KQV_OFFSET ] >= u_vars[ KQV_LIMIT ]:
        #     u_vars[ KQV_OFFSET ] -= u_vars[ KQV_LIMIT ]
        # else:
        #     u_vars[ KQV_OFFSET ] = 0
        # url = URL( f=function_name,
        #            vars=u_vars )
        ui_bt = elements.UiButton( ui_icon=elements.UiIcon( elements.ICON_NAV_PREV,
                                                            dark_background=False ),
                                   tip=T( 'Go to previous page' ),
                                   button_style=elements.BTN_INFO,
                                   button_size=elements.BT_SIZE_XSMALL,
                                   action=UiAction(action_name=ktfact.ACT_NAV_PREV ),
                                   css_class='page_nav_button' )
        return ui_bt.get_html_button( css_style='margin-left: 2em;' )



    def get_nav_first( self, function_name, q_vars ):
        T = current.T
        # u_vars = q_vars.copy()
        # u_vars[ KQV_OFFSET ] = 0
        # url = URL( f=function_name,
        #            vars=u_vars )
        ui_bt = elements.UiButton( ui_icon=elements.UiIcon( elements.ICON_NAV_START,
                                                            dark_background=False ),
                                   tip=T( 'Go to first page' ),
                                   button_style=elements.BTN_INFO,
                                   button_size=elements.BT_SIZE_XSMALL,
                                   action=UiAction(action_name=ktfact.ACT_NAV_FIRST ),
                                   css_class='page_nav_button' )
        return ui_bt.get_html_button( css_style='margin-left: 2em;' )



    def get_nav_options( self,
                         rec_count,
                         opvars=Storage(),
                         offset=0,
                         limit=100,
                         width=2,
                         function_name='index',
                         title_css_class=None,
                         cell_css_class=None,
                         table_id=None,
                         outer_div_id=NAV_DIV_ID,
                         extra_rows=[],
                         extra_rows_style=None,
                         show_options=True,
                         is_header=True ):

#         term.printDebug( 'opvars: %s' % repr( opvars ) )
#         term.printDebug( 'limit: %s; offset: %s; rec_count: %s' %
#                          (limit, offset, rec_count) )
        request = current.request
        T = current.T
        div = DIV()
        if outer_div_id:
            div[ '_id' ] = outer_div_id

        table = TABLE( _class='w100pct inner_table table_border' )
        page = 1
        page_count = 0
        tr = TR()
        q_vars = {}
        preserve_vars = [KQV_LIMIT, KQV_OFFSET]
        if KQV_ORDER not in self.plastic_view.qdata[ KTF_COL_ORDER ]:
            preserve_vars.append( KQV_ORDER )
        for qv in self.plastic_view.query_vars:
            val = self.plastic_view.query_vars[ qv ]
            if qv not in preserve_vars:
                if not val:
                    continue
                # if self.plastic_view.default_vars[ qv ][ 'fld_type' ] == KDT_BOOLEAN \
                #  and not bool( val ) ):
                # continue
            q_vars[ qv ] = self.plastic_view.query_vars[qv]
        # term.printDebug( 'q_vars: %s' % repr( q_vars ) )
        if limit > 0:
            page = (offset / limit) + 1
            page_count = (rec_count / limit) + 1

            nav_span = SPAN()
            # term.printDebug( 'offset: %d; limit: %d' % (offset, limit) )
            if offset > 0:
                if is_header:
                    nav_span.append( self.get_nav_first( function_name,
                                                         q_vars ) )
                    nav_span.append( self.get_nav_prev( function_name,
                                                        q_vars ) )
                else:
                    nav_span.append( self.get_nav_prev( function_name,
                                                        q_vars ) )
                    nav_span.append( self.get_nav_first( function_name,
                                                         q_vars ) )
            tr.append( TD( nav_span,
                           _class='w5pct inner_table',
                           _style='vertical-align: bottom;' ) )
        if show_options:
            it = self.get_options_table( rec_count,
                                         page,
                                         page_count,
                                         opvars,
                                         width,
                                         title_css_class,
                                         cell_css_class,
                                         table_id=table_id,
                                         extra_rows=extra_rows,
                                         extra_rows_style=extra_rows_style )
        else:
            it = ''
        tr.append( TD( it,
                       _class='w90pct inner_table' ) )

        # term.printDebug( 'ofs: %s; lim: %s' % (repr( q_vars[ KQV_OFFSET ] ),
        #                                        repr( q_vars[ KQV_LIMIT ] )) )

        if limit > 0:
            nav_span = SPAN()
            if offset + limit < rec_count:
                if is_header:
                    nav_span.append( self.get_nav_last( function_name, q_vars, rec_count ) )
                    nav_span.append( self.get_nav_next( function_name, q_vars, rec_count ) )
                else:
                    nav_span.append( self.get_nav_next( function_name, q_vars, rec_count ) )
                    nav_span.append( self.get_nav_last( function_name, q_vars, rec_count ) )

            tr.append( TD( nav_span,
                           _class='w5pct inner_table',
                           _style='vertical-align: bottom;' ) )
        table.append( tr )
        div.append( table )
        return div


    def get_table_header( self,
                          transport_text=None,
                          totalizers=Storage(),
                          controller=None,
                          function_name='index',
                          order=None,
                          moving_rows={},
                          query_vars={} ):

        #    term.printLog( 'totalizers: %s' % ( repr( totalizers ) ) )
        tdef = self.plastic_view.get_view_dict()
        cell_class = tdef.cell_class
        thead = THEAD()
        if tdef.header_groups:
            tr = TR( _class = 'table_header' )
            for hg in tdef.header_groups:
                tr.append( TH( hg[ ktfact.KTF_TITLE ],
                               _colspan=len( hg[ ktfact.KTF_COLS ] ),
                               _class='table_border text-center' ) )
            if not moving_rows and tdef.checkboxes:
                tr.append( TH( '',
                               _colspan=len( tdef.checkboxes ),
                               _class='table_border' ) )
                thead.append( tr )

        tr = TR( _class = 'table_header' )
        i = 0
        for c in tdef.col_order:
            i += 1
            col = tdef.cols[ c ]
            if not col:
                term.printLog( 'no col found: %s' % ( repr( c ) ) )
    #        term.printLog( 'col: %s' % ( repr( col ) ) )
            cell_class = col.cell_class or tdef.cell_class
            if col.get( ktfact.KTF_CSS_CLASS ):
                css_class = col.get( ktfact.KTF_CSS_CLASS )
                if not css_class in cell_class:
                    cell_class += ' ' + css_class

            style = htmlcommon.getAlign( col.type,
                                         [ 'text-left',
                                           'text-center',
                                           'text-right' ] ) + ' ' + cell_class
            if tdef.sortable_cols and c in tdef.sortable_cols:
#                 term.printDebug( 'order: %s (%s)' % (repr( order ), type( order ) ) )
                if isinstance( order, basestring ):
                    if 'desc' in order:
                        parts = order.split( ' ' )
                        try:
                            n_order = -int( parts[0] )
                        except ValueError:
#                             n_order = -int( tdef.sortable_cols.index( parts[0] ) + 1 )
                            n_order = -int( tdef.col_order.index( parts[0] ) + 1 )
                    elif order in tdef.sortable_cols:
#                         n_order = int( tdef.sortable_cols.index( order ) + 1 )
                        n_order = int( tdef.col_order.index( order ) + 1 )
                    else:
                        n_order = 0
                else:
                    n_order = int( order or 0 )
#                 term.printDebug( 'n_order: %s' % repr( n_order ) )
                q_vars = get_non_empty_vars( query_vars )
                if n_order and i == abs( n_order ):
                    l_order = n_order * (-1)
#                     term.printDebug( 'l_order: %s' % repr( l_order ) )
                    q_vars[ KQV_ORDER ] = l_order
                    # term.printDebug( 'n_order: %s' % repr( n_order ) )
                    # term.printDebug( 'order: %s' % repr( order ) )
                    if n_order > 0:
                        icon = elements.get_bootstrap_icon( 'chevron-up', dark_background=False )
                        # img = IMG( _src=URL( 'static', 'images/order_asc.png' ) )
                    else:
                        icon = elements.get_bootstrap_icon( 'chevron-down', dark_background=False )
                        # img = IMG( _src=URL( 'static', 'images/order_desc.png' ) )
#                         q_vars[ KQV_ORDER ] = q_vars[ KQV_ORDER ] + ' desc'
#                     term.printDebug( 'q_vars: %s' % repr( q_vars ) )
                    url = URL( c=controller, f=function_name, vars=q_vars )
                    link = A( icon, tdef.cols[ c ][ 'title' ],
                              _href=url )
                    th = TH( link,
                             _class = style )
                else:
                    q_vars[ KQV_ORDER ] = i
#                     term.printDebug( 'q_vars: %s' % repr( q_vars ) )
                    url = URL( c=controller,
                               f=function_name,
                               vars=q_vars )
                    a = A( col.title,
                           _href=url )
                    th = TH( a,
                             _class=style )
#                 term.printDebug( 'th: %s' % th.xml() )
                tr.append( th )
            else:
                tr.append( TH( col.title,
                               _class=style ) )
        if tdef.checkboxes:
            for cb in tdef.checkboxes:
                tr.append( TH( cb.title, _class = cell_class ) )

        thead.append( tr )
        totalize = False
        tot_col_span = -1
        for c in tdef.col_order:
            tot_col_span += 1
            col = tdef.cols[ c ]
            if col[ ktfact.KTF_TOTALIZE ]:
                totalize = True
                break
    #     term.printDebug( 'totalize: %s' % ( repr( totalize ) ) )

        if totalize:
            i = 0
            tr = TR( _class = 'table_totals' )
            val = transport_text + ':'
            tr.append( TH( val,
                           _colspan=tot_col_span,
                           _class='text-right ' + cell_class ) )
            for c in tdef.col_order:
                col = tdef.cols[ c ]
                style = htmlcommon.getAlign( col.type,
                                             [ 'text-left',
                                               'text-center',
                                               'text-right' ] ) + ' ' + cell_class
                if col[ ktfact.KTF_TOTALIZE ]:
                    decimals = col.get(ktfact.KTF_DECIMALS)
                    if not decimals:
                        if col.type in (KDT_DEC, KDT_MONEY ):
                            decimals = 2
                    val = htmlcommon.format_value( col.type,
                                                   totalizers[ c ] or 0.0,
                                                   decimals=decimals )
                    tr.append( TH( val, _class = style ) )
                elif i >= tot_col_span:
                    tr.append( TH( '', _class = style ) )
                i += 1
            if tdef.checkboxes:
                tr.append( TH( '', _class=cell_class ) )

            thead.append( tr )

    #    term.printLog( 'thead: %s' % ( thead.xml() ) )
    #    term.printLog( 'totalizers: %s' % ( repr( totalizers ) ) )
        return thead


    def get_table_footer( self,
                          totalizers=Storage(),
                          totals_text=None ):
        tdef = self.plastic_view.get_view_dict()
        cell_class = tdef.cell_class
        tfoot = TFOOT()
        totalize = False
        tot_col_span = -1
        for c in tdef.col_order:
            tot_col_span += 1
            col = tdef.cols[ c ]
            if col.has_key( ktfact.KTF_TOTALIZE ):
                totalize = True
                break
    #    term.printLog( 'totalize: %s' % ( repr( totalize ) ) )
        if totalize:
            i = 0
            tr = TR( _class = 'table_totals' )
            val = totals_text + ':'
            tr.append( TH( val, _colspan = tot_col_span, _class = 'text-right ' + cell_class ) )
            for c in tdef.col_order:
                col = tdef.cols[ c ]
                style = htmlcommon.getAlign( col.type,
                                             [ 'text-left',
                                               'text-center',
                                               'text-right' ] ) + ' ' + cell_class
                if col[ ktfact.KTF_TOTALIZE ]:
                    # term.printDebug( 'totalizers[ %s ]: %s' % ( c, repr( totalizers[ c ] ) ) )
                    decimals = col.get(ktfact.KTF_DECIMALS)
                    if not decimals:
                        if col.type in (KDT_DEC, KDT_MONEY ):
                            decimals = 2
                    val = htmlcommon.format_value( col.type,
                                                   totalizers[ c ] or 0.0,
                                                   decimals=decimals )
                    # term.printDebug( 'val: %s' % ( repr( val ) ) )
                    tr.append( TH( val, _class = style ) )
                elif i >= tot_col_span:
                    tr.append( TH( '', _class = style ) )
                i += 1

            if tdef.checkboxes:
                tr.append( TH( '', _class=cell_class ) )
            tfoot.append( tr )
        return tfoot


    def get_table_body( self,
                        rows,
                        selections=[],
                        moving_rows=Storage(),
                        highlight_row_class=None ):
        '''
        get_table_body( tdef,               # table def (dict)
                      rows,               # list of rows
                      selections=[],      # selected items (dict)
                                          # { <fld_name>: { css_class: <class>, key_list: [ <id>, ...] } }
                      moving_rows={},     # { col_name: <fld_name>, rows: [ <id>, ...], (link) }
                      highlight_row_class=None ):
        '''
        T = current.T

        tdef = self.plastic_view.get_view_dict()
        tbody = TBODY()
        if moving_rows:
            term.printLog( 'moving_rows: %s' % repr( moving_rows ) )
        cell_class = ''
        if rows:
            for idx, row in enumerate( rows ):
        #         term.printDebug( 'row: %s' % ( repr( row ) ) )
                if not isinstance( row, Storage ):
                    row = Storage( row )
                tr = self._get_tr( row,
                                   highlight_row_class=highlight_row_class,
                                   selections=selections )
                for col_name in tdef.col_order:
        #             term.printDebug( 'val (%s): %s (%s)' % (c, repr( row[c] ), type( row[c] ) ) )
                    val = None
                    col = tdef.cols[ col_name ]
                    cell_class = col.cell_class and col.cell_class or tdef.cell_class
        #             term.printLog( 'tdef.cols[ %s ] - class: %s' % ( col_name, repr( cell_class ) ) )
        #            term.printLog( 'tdef.cols[ %s ]: %s' % ( col_name, repr( col ) ) )
                    if col.type == ktfact.KTF_BUTTON:
                        inp = self._get_button( row, col )
                        tr.append( TD( inp, _class = cell_class + ' text-center' ) )
                    elif col.type == KDT_XML:
                        val = XML( row[ col_name ] )
                        tr.append( TD( val,
                                       _class=cell_class ) )
                    else:
                        # values from DB
                        val = ''
                        if col_name in row:
                            if col.type == KDT_BLOB_IMG:
                                val = self._get_blob_img( row, col_name )
                            else:
                                val = self._get_row_cell_val( row,
                                                              col_name )
                        if col[ ktfact.KTF_CELL_LINK ] and val:
                            val = self._get_cell_link_val( row,
                                                           col_name,
                                                           val )
        #                     term.printDebug( 'val (%s): %s (%s)' % (col_name, repr( val ), type( val ) ) )
        #                    term.printLog( 'val: %s' % ( val.xml() ) )
                        elif col[ ktfact.KTF_EDITABLE ] and row[ col[ ktfact.KTF_EDITABLE ] ]:
                            val = self._get_editable_cell( row,
                                                           col_name,
                                                           val )
        #                 term.printDebug( 'val (%s): %s (%s)' % (c, repr( val ), type( val ) ) )
        #                 term.printDebug( 'str: %s' % str( val ) )
                        style = htmlcommon.getAlign( col.type,
                                                     [ 'text-left',
                                                       'text-center',
                                                       'text-right' ] )
                        if cell_class:
                            style += ' ' + cell_class

                        if tdef.groupby and col_name in tdef.groupby:
                            if idx > 0 and rows[ idx - 1 ][ col_name ] == row[ col_name ]:
                                val = ''
    #    collapse
    #                         if idx + 1 < len( rows ) \
    #                         and rows[ idx + 1 ][ col_name ] == row[ col_name ]:
    #                             r_value = val
    #                             val = SPAN( r_value )
    #                             sp_collapse = SPAN( T( 'Collapse' ) )
    #                             g_rows = []
    #                             i = idx
    #                             while i + 1 < len( rows ):
    #                                 if rows[ i + 1 ][ col_name ] != row[ col_name ]:
    #                                     break
    #                                 i += 1


                        checkbox_css_class = None
                        if col.checkbox \
                        and idx > 0 \
                        and rows[ idx - 1 ][ col_name ] == row[ col_name ]:
                            val = ''
                        if moving_rows:
                            if col.get( ktfact.KTF_MV_INSERT_POINT ) \
                            and not self._is_idx_in_mv_rows( rows, idx, moving_rows ):
                                if col_name == moving_rows.col_name:
    #                                 term.printDebug( 'col_name: %s; mv.col_name: %s; fld_id: %s' %
    #                                                  ( col_name,
    #                                                    repr( moving_rows.col_name ),
    #                                                    repr( moving_rows.fld_id ) ) )
                                    val = self._apply_insertion_link( rows,
                                                                      idx,
                                                                      col_name,
                                                                      val,
                                                                      moving_rows )
                                    checkbox_css_class = 'hidden'
                        elif col.checkbox \
                        and ( idx == 0 or rows[ idx - 1 ][ col_name ] != row[ col_name ] ):
                            val = self._get_sel_checkbox( row,
                                                          col_name,
                                                          val,
                                                          checkbox_css_class=checkbox_css_class )
                        cell_ids = tdef.get( ktfact.KTF_CELL_IDS )
    #                     term.printDebug( 'cell_ids: %s' % ( repr( cell_ids ) ) )
                        if cell_ids:
                            td_id = 'td_%s_%d' % (col_name, row[ cell_ids ] )
    #                         term.printDebug( 'td_id: %s' % ( repr( td_id ) ) )
                            tr.append( TD( val,
                                           _id=td_id,
                                           _class=style ) )
                        else:
                            tr.append( TD( val, _class=style ) )
                        if row.row__id:
                            tr[ '_id' ] = row.row__id

                if tdef.checkboxes:
                    for cb in tdef.checkboxes:
    #                     term.printDebug( 'cb: %s' % repr( cb ) )
    #                     term.printDebug( 'row[ cb.checkbox_id ]: %s' % repr( row[ cb.checkbox_id ] ) )
                        r_cb = row[ cb.checkbox_id ]
                        if r_cb:
                            cb_name = cb.name % ( r_cb )
                            onclick = None
                            if cb.onclick:
                                if cb.onclick.startswith( 'ajax_call:' ):
                                    parts = cb.onclick.split( ':' )
                                    url = URL( c=parts[1],
                                               f=parts[2],
                                               args=[ r_cb ] )
                                    onclick = '''
                                        ajax( '%(url)s', [ '%(fld)s' ], ':eval' );
                                    ''' % { 'url': url,
                                            'fld': cb_name }
                                else:
                                    onclick = cb.onclick
                            inp = htmlcommon.get_input_field( cb_name,
                                                              input_type='checkbox',
                                                              input_id=cb_name,
                                                              on_change=onclick )
                        else:
                            inp = ''
                        td = TD( inp, _class = 'text-center ' + cell_class )
                        tr.append( td )
                tbody.append( tr )
                if row.validationResult:
                    tbody.append( TR( TD( elements.get_bootstrap_icon( 'arrow-up',
                                                                       dark_background=False ),
                                          row.validationResult[ ktfact.KTF_MSG ],
                                          _colspan=len( tdef.col_order ),
                                          _class=row.validationResult[ ktfact.KTF_CSS_CLASS ] ) ) )
    #    term.printLog( 'totalizers: %s' % ( repr( totalizers ) ) )
    #    term.printLog( 'tbody: %s' % ( repr( tbody.xml() ) ) )
        return tbody


    def get_table( self,
                   rows,
                   transport_text=None,
                   totals_text=None,
                   totalizers=Storage(),
                   controller=None,
                   function_name='index',
                   order=None,
                   selections=[],
                   moving_rows=Storage(),
                   highlight_row_class='highlight_row',
                   query_vars={},
                   table_id=None,
                   outer_div_id=LIST_DIV_ID ):

    #     term.printDebug( 'function_name: %s' % repr( function_name ) )
        thead = self.get_table_header( transport_text,
                                       totalizers=totalizers.header,
                                       controller=controller,
                                       function_name=function_name,
                                       order=order,
                                       moving_rows=moving_rows,
                                       query_vars=query_vars )
    #    term.printLog( 'totalizers: %s' % ( repr( totalizers ) ) )
        tbody = self.get_table_body( rows, selections, moving_rows, highlight_row_class )
        # term.printLog( 'totalizers: %s' % ( repr( totalizers ) ) )

        tfoot = self.get_table_footer( totalizers.footer, totals_text )

        table = TABLE( _id=table_id,
                       _class='w100pct plastic_table' )
        table.append( thead )
        table.append( tbody )
        table.append( tfoot )
    #    term.printLog( 'table: %s' % ( repr( table.xml() ) ) )
        div = DIV( table )
        if outer_div_id:
            div[ '_id' ] = outer_div_id
        return div


    # def _get_qdata_col( self,
    #                     tr,
    #                     opvars=Storage(),
    #                     varname=None,
    #                     title_css_class=None,
    #                     cell_css_class=None,
    #                     width=None ):
    def _get_qdata_col( self,
                        tr,
                        width,
                        opvars=Storage(),
                        varname=None,
                        title_css_class=None,
                        cell_css_class=None ):
#         term.printDebug( 'varname: %s' % repr( varname ) )
#         term.printDebug( 'opvars: %s' % repr( opvars ) )
#         term.printDebug( 'self.qdata: %s' % repr( self.qdata ) )
#         css_pct = 'w%dpct' % (100 / (width * 2 ))
        qdata = self.plastic_view.qdata
        c = qdata.cols[ varname ]
        if not c:
            msg = 'NO DATA FOR OPTION: %s' % ( varname )
            term.printLog( msg )
            raise Exception( msg )
        # css_style = None
        # if width:
        #     css_style = 'width: %s%%;' % str( width )
        if c.get( ktfact.KTF_CSS_CLASS ) != 'hidden':
            th = TH( c.title, ':',
                     _class=title_css_class )
            # if css_style:
            #     th[ '_style' ] = css_style
            tr.append( th )
        span = None
        if c[ ktfact.KTF_SPAN ]:
            span = SPAN( _id = c[ ktfact.KTF_SPAN ] )
        if c.get( ktfact.KTF_CSS_CLASS ):
            if cell_css_class:
                cell_css_class += ' %s' % c.get( ktfact.KTF_CSS_CLASS )
            else:
                cell_css_class = c.get( ktfact.KTF_CSS_CLASS )
        if c.type in (KDT_SELECT_INT, KDT_SELECT_CHAR):
            use_live_search = c.get( ktfact.KTF_SELECT_LIVE_SEARCH )
            if c.callback:
                sel = htmlcommon.get_selection_field( varname,
                                                      input_id=varname,
                                                      options=c.options,
                                                      selected=opvars[ varname ],
                                                      on_change=c.callback,
                                                      use_bootstrap_live_search=use_live_search )
            else:
                sel = htmlcommon.get_selection_field( varname,
                                                      input_id=varname,
                                                      options=c.options,
                                                      selected=opvars[ varname ],
                                                      use_bootstrap_live_search=use_live_search )

            if span:
                span.append( sel )
                tr.append( TD( span,
                               _class=cell_css_class ) )
            else:
                tr.append( TD( sel,
                               _class=cell_css_class ) )
        else:
            if c.type == KDT_FILE:
                colType = 'file'
            else:
                colType = 'text'
            if c.type == KDT_BOOLEAN:
                colType = 'checkbox'
            # term.printDebug( 'opvars[%s]: %s' % ( varname, repr( opvars[ varname ] ) ) )
            input = htmlcommon.get_input_field( varname,
                                                value=opvars[ varname ],
                                                input_type=colType,
                                                input_id=varname,
                                                value_type=c.type,
                                                read_only=c.readonly,
                                                span_wrap=False )
#             term.printDebug( 'input: %s' % input.xml() )
#             if span:
#                 span.append( input )
#                 tr.append( TD( span, _class=cell_css_class, _style=css_style ) )
#             else:
#                 tr.append( TD( input, _class=cell_css_class, _style=css_style ) )
            if span:
                span.append( input )
                tr.append( TD( span,
                               _class=cell_css_class ) )
            else:
                tr.append( TD( input,
                               _class=cell_css_class ) )


    def get_nav_page_sel_limits( self,
                                 rec_count,
                                 page,
                                 page_count,
                                 opvars=Storage() ):
        T = current.T
        div_sel_limits = DIV( _class='nav_page_sel_limits' )
        div_sel_limits.append( SPAN( T( 'Number of records' ) + ': ' + str( rec_count or 0 ) ) )
        if page is None:
            page = 1
        if page_count:
            div_sel_limits.append( SPAN( T( 'Page %d of %d' ) % ( page, page_count ),
                               _class='margin_buttons' ) )
        else:
            div_sel_limits.append( SPAN( T( 'Page 1 of 1' ),
                               _class='margin_buttons' ) )
        if page_count:
            div_sel_limits.append( SPAN( T( 'Records/page' ) + ':',
                               _style='margin-left: 1em; margin-right: 0.5em;' ) )
            inp = htmlcommon.get_input_field( KQV_LIMIT,
                                              value=opvars.qv_limit or 20,
                                              input_id=KQV_LIMIT,
                                              value_type=KDT_INT,
                                              css_style='margin-left: 0.25em; margin-right: 1em; width: 5em;' )
            div_sel_limits.append( inp )

        return div_sel_limits


    def get_nav_actions_select( self ):
        T = current.T
        qdata = self.plastic_view.qdata
#         term.printDebug( 'qdata: %s' % repr( qdata ) )
        sel_div = DIV( _id='nav_buttons_select_div',
                       _class='nowrap nav_buttons_select' )
        if not qdata.actions:
            return sel_div

        # colors: tuple of ( bg_color, fg_color )
        opt_colors = { 'sel_bt': ('#0181D0', '#FFFFFF'),
                       'submit_bt': ('#F2F2F2', '#000000'),
                       'nav_bt': ('#008080', '#FFFFFF'),
                       'del_bt': ('#D00000', '#FFFFFF'),
                       }
        bt_action_id = 'bt_action'

        sel_div.append( B( T( 'Action' ) + ': ' ) )
        on_change = ''
        for bt in qdata.actions:
            opt_color = opt_colors[ 'submit_bt' ]
            if bt.css_class:
                opt_color = opt_colors[ bt.css_class ]
            on_change += '''
                if( $(this ).val() == '%(bt_value)s' ) {
                    $( '#%(bt_action)s' ).css( 'background-color','%(bg)s' );
                    $( '#%(bt_action)s' ).css( 'color','%(fg)s' );
                } ''' % { 'bt_value': bt.value,
                          'bt_action': bt_action_id,
                          'bg': opt_color[0],
                          'fg': opt_color[1] }
        # options = [(a.value, a.title, '', '') for a in qdata.actions ]
        # sel = htmlcommon.get_selection_field( 'action',
        #                                       input_id=bt_action_id,
        #                                       options=options,
        #                                       on_change=on_change )
        sel = SELECT( _name='action',
                      _id=bt_action_id,
                      _onchange=on_change )
        for bt in qdata.actions:
            opt_color = opt_colors[ 'submit_bt' ]
            if bt.css_class:
                opt_color = opt_colors[ bt.css_class ]
            sel.append( OPTION( bt.title,
                                _value=bt.value,
                                _style='background-color: %s; color: %s' %
                                (opt_color[0], opt_color[1]) ) )
        sel_div.append( sel )
        bt = BUTTON( T( 'Execute action' ),
                        _id='bt_submit_sel',
                        _type='submit',
                        _title=T( 'Execute selected action' ),
                        _value='act_submit_sel',
                        _class='submit_bt' )
        sel_div.append( bt )
        return sel_div


    def get_nav_buttons_array( self ):
        qdata = self.plastic_view.qdata
#         term.printDebug( 'qdata: %s' % repr( qdata ) )
        T = current.T
        # term.printDebug( 'qdata[ ktfact.KTF_BUTTONS ]: %s' % repr( qdata[ ktfact.KTF_BUTTONS ] ) )
        q_bt_names = [ bt[ ktfact.KTF_VALUE ] for bt in qdata[ ktfact.KTF_BUTTONS ] ]
        # term.printDebug( 'q_bt_names: %s' % repr( q_bt_names ) )
        bt_array = []
        if self.plastic_view.ui_buttons:
            for bt_action in (ACT_SUBMIT, ACT_CLEAR):
                ui_bt = self.plastic_view.ui_buttons.get( bt_action )
                if ui_bt:
                    bt_array.append( ui_bt.get_html_button() )

        qdata = self.plastic_view.qdata
        for bt in qdata.get( ktfact.KTF_BUTTONS ):
            el = None
            if bt.img:
                el = bt.img
            elif bt.icon:
                el = (elements.get_bootstrap_icon( bt.icon ), ' ', bt.title)
            else:
                el = bt.title
            css_class = 'btn btn-submit'
            if bt.css_class:
                css_class = bt.css_class
            title = bt.title
            if is_sequence( bt.title ):
                title = bt.title[1]
            inp = BUTTON( el,
                          _name=bt.name,
                          _id=bt.id,
                          _type=bt.type or 'submit',
                          _title=title,
                          _value=bt.value or 'submit',
                          _class=css_class,
                          _onclick=bt.onclick )
            bt_array.append( inp )
            # term.printDebug( 'bt_array: %s' % repr( bt_array ) )
        if self.plastic_view.ui_buttons:
            ui_bt = self.plastic_view.ui_buttons.get( ACT_NEW_RECORD )
            if ui_bt:
                bt_array.append( ui_bt.get_html_button( css_style='margin-left: 2em;' ) )
                # term.printDebug( 'bt_array: %s' % repr( bt_array ) )
        return bt_array


    def get_options_table( self,
                           rec_count,
                           page,
                           page_count,
                           opvars=Storage(),
                           width=2,
                           title_css_class=None,
                           cell_css_class=None,
                           table_id=None,
                           extra_rows=[],
                           extra_rows_style=None ):
        T = current.T
        qdata = self.plastic_view.qdata
#         term.printDebug( 'rec_count: %s; w: %d' % (rec_count, width) )

#         term.printDebug( 'qdata: %s' % repr( qdata ) )
#         bt_action_id = 'bt_action'
#         if table_id:
#             bt_action_id += '_%s' % table_id
        table = TABLE( _class = 'w100pct')
        if extra_rows:
            if extra_rows_style:
                t_inner = TABLE( _class='margin_0 w100pct', _style=extra_rows_style )
            else:
                t_inner = TABLE( _class='margin_0 w100pct' )
            for r in extra_rows:
                t_inner.append( r )
            table.append( TR( TD( t_inner,
                                  _colspan=width * 2 ) ) )
            # tr = TR()

        # pct = 100 / (width * 2)
        if not title_css_class:
            title_css_class = 'text-right'
        if not cell_css_class:
            cell_css_class = ''
        idx = 0
        tr = None
        if qdata.get( ktfact.KTF_FILTER_PANEL ):
            table.append( TR( TD( self.plastic_view.get_filter_panel(),
                                  _colspan=width * 2 ) ) )

        elif qdata.col_order:
            for varname in qdata.col_order:
#                 term.printDebug( 'varname: %s' % ( repr( varname ) ) )
                if not idx or not tr:
                    tr = TR()
                self._get_qdata_col( tr,
                                     width,
                                     opvars=opvars,
                                     varname=varname,
                                     title_css_class=title_css_class,
                                     cell_css_class=cell_css_class )
#                 term.printDebug( 'w: %d; idx: %d; tr: \n%s' %
#                                  ( width,
#                                    idx,
#                                    '\n'.join( [ '%s: %s' % (e.tag, str( e.components ) )
#                                                 for e in tr.elements() ] ) ) )

                idx += 1
                if idx >= width:
#                     term.printDebug( 'idx: %d' % ( idx ) )
                    table.append( tr )
                    tr = None
                    idx = 0

#         term.printDebug( 'idx: %d' % ( idx ) )
        if tr:
            table.append( tr )
        tr = TR()
        idx = 0

        div_sel_limits = self.get_nav_page_sel_limits( rec_count,
                                                       page,
                                                       page_count,
                                                       opvars )
        idx += 1
        tr.append( TD( div_sel_limits,
                       _colspan=width * 2,
                       _class='text-center' ) )

        nav_actions_select = self.get_nav_actions_select()
#         term.printDebug( 'nav_actions_select: %s' % ( nav_actions_select.xml() ) )
        if nav_actions_select:
            if idx + 2 > width: # width:
                tr.append( TD( nav_actions_select,
                               _colspan=2,
                               _class='text-center' ) )
                idx += 2

        if idx + 2 > width:
            table.append( tr )
            tr = TR()
            idx = 0

        nav_buttons_array = self.get_nav_buttons_array()

        if nav_buttons_array:
            table.append( tr )
            tr = TR()
            bt_div = DIV( _class='nav_buttons_array' )
            for bt in nav_buttons_array:
                # term.printDebug( 'bt: %s' % ( bt.xml() ) )
                bt_div.append( bt )
            tr.append( TD( bt_div,
                           _colspan=width * 2,
                           _class='text-center' ) )
        if tr:
            table.append( tr )
    #    term.printLog( 'table: %s' % ( table.xml() ) )
        return table


    def _get_tr( self,
                row,
                highlight_row_class=None,
                selections=[] ):
        tdef = self.plastic_view.get_view_dict()
        row_id_mask = tdef.get( ktfact.KTF_ROW_ID_MASK )

        rid = None
        if row_id_mask:
            rid = row_id_mask % row
#            term.printDebug( 'rid: %s' % repr( rid ) )
        if tdef.row_data:
            rdata = {}
            for c in tdef.row_data:
                rdata[ '_data-' + c ] = row[ c ]
            tr = TR( _id=rid,
                     **rdata )
#             tr = TR( _id=rid,
#                      data=rdata )
        else:
            tr = TR( _id=rid )
#         term.printDebug( 'tr: %s' % tr.xml() )
        if highlight_row_class:
            tr[ '_onmouseover' ] = '''jQuery( this ).addClass( '%s' );''' % highlight_row_class
            tr[ '_onmouseout' ] = '''jQuery( this ).removeClass( '%s' );''' % highlight_row_class
#         if row_id_mask:
#             tr = TR( _id=row_id_mask % row )
#         else:
#             tr = TR()
#             if highlight_row_class:
#                 tr[ '_onmouseover' ] = '''jQuery( this ).addClass( '%s' );''' % highlight_row_class
#                 tr[ '_onmouseout' ] = '''jQuery( this ).removeClass( '%s' );''' % highlight_row_class
        if row.has_key( ktfact.KTF_ROW_CLASS ):
            tr[ '_class' ] = row[ ktfact.KTF_ROW_CLASS ]
        for col_name in selections:
            v = row[ col_name ]
#             term.printDebug( 'v: %s' % repr( v ) )
#             term.printDebug( 'selections[ %s ]: %s' % (col_name, repr( selections[ col_name ] ) ) )
            if v in selections[ col_name ][ ktfact.KTF_KEY_LIST ]:
                row_class = selections[ col_name ][ ktfact.KTF_CSS_CLASS ]
                if tr[ '_class' ]:
                    if not row_class in tr[ '_class' ]:
                        tr[ '_class' ] = tr[ '_class' ] + ' ' + row_class
                else:
                    tr[ '_class' ] = row_class
                break

        return tr


    def _get_link_args_and_vars( self,
                                col,
                                row ):
        arg_list = []
        # by field name
        if col[ ktfact.KTF_CELL_LINK ][ ktfact.KTF_ARGS_F ]:
            for arg in col[ ktfact.KTF_CELL_LINK ][ ktfact.KTF_ARGS_F ]:
                if arg in row:
                    arg_list.append( row[ arg ] )
        # by value
        if col[ ktfact.KTF_CELL_LINK ][ ktfact.KTF_ARGS_V ]:
            args_v = col[ ktfact.KTF_CELL_LINK ][ ktfact.KTF_ARGS_V ]
            if is_sequence( args_v ):
                for arg in col[ ktfact.KTF_CELL_LINK ][ ktfact.KTF_ARGS_V ]:
                    arg_list.append( arg )
            else:
                arg_list.append( args_v )

        var_dict = {}
        # by field name
        if col[ ktfact.KTF_CELL_LINK ][ ktfact.KTF_VARS_F ]:
            for arg in col[ ktfact.KTF_CELL_LINK ][ ktfact.KTF_VARS_F ]:
                # term.printDebug( 'arg: %s (%s)' % (repr( arg ), type( arg )) )
                if col[ ktfact.KTF_CELL_LINK ][ ktfact.KTF_VARS_F ][ arg ] in row:
                    var_dict[ arg ] = row[ col[ ktfact.KTF_CELL_LINK ][ ktfact.KTF_VARS_F ][ arg ] ]
    #             if arg == KQV_RETURN_NAME:
    #                 c_name = col[ ktfact.KTF_CELL_LINK ][ ktfact.KTF_VARS_F ][ arg ]
    #                 var_dict[ c_name ] = row
    #     term.printDebug( 'col[ ktfact.KTF_CELL_LINK ]: %s' % (repr( col[ ktfact.KTF_CELL_LINK ] )) )
        if col[ ktfact.KTF_CELL_LINK ][ ktfact.KTF_VARS_V ]:
            for arg in col[ ktfact.KTF_CELL_LINK ][ ktfact.KTF_VARS_V ]:
                # term.printDebug( 'arg: %s (%s)' % (repr( arg ), type( arg )) )
                var_dict[ arg ] = col[ ktfact.KTF_CELL_LINK ][ ktfact.KTF_VARS_V ][ arg ]
        # term.printDebug( 'arg_list: %s' % ( repr( arg_list ) ) )
        # term.printDebug( 'var_dict: %s' % ( repr( var_dict ) ) )
        return (arg_list, var_dict)


    def _get_button( self,
                    row,
                    col ):
        arg_list, var_dict = self._get_link_args_and_vars( col, row )
#        term.printDebug( 'arg_list: %s' % repr( arg_list ) )
        url = URL( c=col[ ktfact.KTF_CELL_LINK ].link_c,
                   f=col[ ktfact.KTF_CELL_LINK ].link_f,
                   args=arg_list,
                   vars=var_dict )
        css_class = 'btn btn-info'
        if col.css_class:
            css_class = col.css_class
        inp = A( col.title,
                 _href=url,
                 _class=css_class )
        return inp


    def _get_blob_img( self,
                       row,
                       col_name ):
        tdef = self.plastic_view.get_view_dict()
        col = tdef.cols[ col_name ]
        url = URL( c='default',
                   f='download',
                   args=row[ col_name ] )
    #                 term.printDebug( 'url: %s' % ( repr( url ) ) )
        img = IMG( _src=url )
        if col.width:
            img[ '_width' ] = col.width
#         term.printDebug( 'img: %s' % ( img.xml() ) )
        return img


    def _get_row_cell_val( self,
                          row,
                          col_name ):
        tdef = self.plastic_view.get_view_dict()
        col = tdef.cols[ col_name ]
        if col.type == KDT_RAW:
            val = row[ col_name ]
    #                         term.printDebug( 'val (%s): %s (%s)' % (col_name, repr( val ), type( val ) ) )
        else:
            decimals = col.get( ktfact.KTF_DECIMALS )
            if not decimals:
                if col.type in (KDT_DEC, KDT_MONEY):
                    decimals = 2
            val = htmlcommon.format_value( col.type,
                                           row[ col_name ],
                                           decimals=decimals,
                                           allow_nulls=True,
                                           mask=col.mask,
                                           hide_zeros=col.get( ktfact.KTF_HIDE_ZEROS ) )
            if col.max_length and len( val ) > col.max_length:
                val = val[ : col.max_length ].rsplit( ' ', 1 )[0] + ' (...)'
    #                         term.printDebug( 'val (%s): %s (%s)' % (c, repr( val ), type( val ) ) )
        return val


    def _get_cell_link_val( self,
                            row,
                            col_name,
                            val ):
        tdef = self.plastic_view.get_view_dict()
        col = tdef.cols[ col_name ]
        if not val \
        and ( col[ ktfact.KTF_CELL_LINK ].use_icon
              or ( col[ ktfact.KTF_CELL_LINK ].use_icon is None
                   and col.type == KDT_INT ) ):
            val = col.title
    #                     term.printDebug( 'val: %s' % ( repr( val ) ) )
        arg_list, var_dict = self._get_link_args_and_vars( col, row )
        url = URL( c=col[ ktfact.KTF_CELL_LINK ].link_c,
                   f=col[ ktfact.KTF_CELL_LINK ].link_f,
                   args=arg_list,
                   vars=var_dict )
    #                     term.printDebug( 'url: %s' % str( url ) )
        if col[ ktfact.KTF_CELL_LINK ].use_icon \
        or ( col[ ktfact.KTF_CELL_LINK ].use_icon is None
             and col.type == KDT_INT ):

            if col.type == KDT_CHAR:
                span = SPAN()
                a_style = 'margin-right: 0.5em;'
            else:
                span = SPAN( val )
                a_style = 'margin-left: 0.5em;'
            i = elements.get_bootstrap_icon( 'circle-arrow-right' )
            ajax_target = col[ ktfact.KTF_CELL_LINK ].get( ktfact.KTF_AJAX_TARGET )
            if ajax_target:
                if ajax_target:
                    ajax_target = ':eval'
                onclick = '''
                    ajax( '%(url)s', [], '%(target)s' );
                ''' % { 'url': url, 'target': ajax_target }
                a = A( i,
                       _class='dark_bg',
                       _href='#',
                       _style=a_style,
                       _onclick=onclick )
            else:
                a = A( i,
                       _class='dark_bg',
                       _style=a_style,
                       _href=url )

            if col[ ktfact.KTF_CELL_LINK ].title:
                a[ '_title' ] = col[ ktfact.KTF_CELL_LINK ].title
            span.append( a )
            if col.type == KDT_CHAR:
                span.append( val )
            val = span
        else:
            val = A( val, _href=url )
            if col[ ktfact.KTF_CELL_LINK ].title:
                val[ '_title' ] = col[ ktfact.KTF_CELL_LINK ].title
    #                     term.printDebug( 'val (%s): %s (%s)' % (c, repr( val ), type( val ) ) )
    #                    term.printLog( 'val: %s' % ( val.xml() ) )
        return val


    def _get_editable_cell( self,
                           row,
                           col_name,
                           val ):
        tdef = self.plastic_view.get_view_dict()
        col = tdef.cols[ col_name ]
        cell_id = 'row__%s__%d' % ( col_name, row[ col[ ktfact.KTF_EDITABLE ] ] )
        val = htmlcommon.get_input_field( cell_id,
                                          value=val,
                                          input_id=cell_id,
                                          value_type=col.type )
        # val = htmlcommon.getInputField(
        #     cell_id, value = val, id = cell_id, valueType = col.type )
        if col[ ktfact.KTF_EDITABLE_CLASS ]:
            val[ '_class' ] += ' ' + col[ ktfact.KTF_EDITABLE_CLASS ]
        return val


    def _get_paste_rows_link( self,
                             moving_rows,
                             row_id,
                             position='before',
                             table='question',
                             title=None ):
        T = current.T
        if not row_id:
            term.printLog( 'position: %s\nrow_id: %s\nrows: %s' %
                           (position, repr( row_id ), repr( moving_rows )) )
            return ''

        url = URL( c=moving_rows[ ktfact.KTF_LINK_C ],
                   f=moving_rows[ ktfact.KTF_LINK_F ],
                   args=[ position, table, row_id ] )
        i = None
        if position in [ 'before', 'start' ]:
            i = elements.get_bootstrap_icon( 'chevron-up' )
            css_class = 'dark_bg_up'
            if not title:
                if position == 'before':
                    title = T( 'Insert before' )
                else:
                    title = T( 'Insert at start' )
        elif row_id and position in [ 'after', 'end' ]:
            i = elements.get_bootstrap_icon( 'chevron-down' )
            css_class = 'dark_bg_down'
            if not title:
                if position == 'after':
                    title = T( 'Insert after' )
                else:
                    title = T( 'Insert at end' )
        else:
            term.printLog( 'url: %s\ntitle: %s\nposition: %s\nrow_id: %s\nrows: %s' %
                           (url, title, position, repr( row_id ), repr( moving_rows )) )
        a = A( i, _class=css_class, _href=url, _title=title )
        return a


    def _apply_insertion_link( self,
                               rows,
                               idx,
                               col_name,
                               val,
                               moving_rows ):
        T = current.T
        tdef = self.plastic_view.get_view_dict()
        col = tdef.cols[ col_name ]
        u_pos, d_pos = None, None
        ins_p = col[ ktfact.KTF_MV_INSERT_POINT ]
#         term.printDebug( 'col[%s]: %s\n' % ( col_name, repr( col ) ) )
        lnk_table = ins_p[ ktfact.KTF_MV_LINK_TABLE ]
        fld_id = ins_p[ ktfact.KTF_MV_FIELD_ID ]
        titles = ins_p[ ktfact.KTF_TITLE ]
        row = rows[ idx ]
        if idx == 0 \
        or (idx > 0 and rows[ idx - 1 ][ col_name ] != row[ col_name ]):
            u_pos = 'start'
        if idx == len( rows ) - 1 \
        or (idx < len( rows ) - 1 and rows[ idx + 1 ][ col_name ] != row[ col_name ]):
            d_pos = 'end'
#         term.printDebug( 'u_pos: %s; d_pos: %s' %
#                          (repr( u_pos ), repr( d_pos )) )
#         term.printDebug( 'idx: %s; len( rows ): %s; name: %s\n' %
#                          ( repr( idx ), repr( len( rows ) ), row[ 'q_name' ] ) )
        if u_pos or d_pos:
            i_table = TABLE( _class='margin_0', _style='width: 100%;' )
            i_tr = TR()
            i_tr.append( TD( val, _class='margin_0' ) )
            if u_pos:
                title = titles[0]
                i_tr.append( TD( self._get_paste_rows_link( moving_rows,
                                                            row[ fld_id ],
                                                            position=u_pos,
                                                            table=lnk_table,
                                                            title=title ),
                                 _class='text-right margin_0' ) )
            else:
                i_tr.append( TD() )
            i_table.append( i_tr )
            i_tr = TR( TD() )
            if d_pos:
#                 term.printDebug( 'd_pos: %s' %
#                                  (repr( d_pos ) ) )
                title = titles[1]
                i_tr.append( TD( self._get_paste_rows_link( moving_rows,
                                                            row[ fld_id ],
                                                            position=d_pos,
                                                            table=lnk_table,
                                                            title=title ),
                                 _class='text-right margin_0',
                                 _style='vertical-align: bottom' ) )
#                 term.printDebug( 'i_tr: %s' % i_tr.xml() )
            else:
                i_tr.append( TD() )
            i_table.append( i_tr )
            val = i_table
#             term.printDebug( 'val: %s' % val.xml() )
        return val


    def _get_sel_checkbox( self,
                           row,
                           col_name,
                           val,
                           checkbox_css_class=None ):
        tdef = self.plastic_view.get_view_dict()
        col = tdef.cols[ col_name ]
        if not row[ col.checkbox.checkbox_id ]:
            return ''
        i_table = TABLE( _class='margin_0', _style='width: 100%;' )
        i_tr = TR()
        i_tr.append( TD( val, _class='margin_0' ) )

        cb_name = '%s%d' % (col.checkbox.name, row[ col.checkbox.checkbox_id])
        on_change = '''
            window.console && console.log( '%(id)s' );
            jQuery( 'input:not( [id^="%(id)s"] )' ).prop( 'checked', false );
        ''' % { 'id': col.checkbox.name }
        checkbox = htmlcommon.get_input_field( cb_name,
                                               input_type='checkbox',
                                               input_id=cb_name,
                                               on_change=on_change,
                                               title=col.checkbox.title )
        if checkbox_css_class:
            checkbox_css_class += ' text-right margin_0'
        else:
            checkbox_css_class = 'text-right margin_0'
        i_tr.append( TD( checkbox,
                         _class=checkbox_css_class ) )
        i_table.append( i_tr )
        return i_table


    def _get_form_fields( self,
                         vars,
                         allow_nulls=False ):
    #    term.printLog( 'vars: %s' % ( repr( vars ) ) )
        qdata = self.plastic_view.qdata
        upd = Storage()
        if vars:
            varList = qdata[ ktfact.KTF_COLS ].keys()
            varList.sort()
    #        term.printLog( 'varList: %s' % ( repr( varList ) ) )
            for field_name in varList:
                formValue = vars[ field_name ]
                ftype = qdata[ ktfact.KTF_COLS ][ field_name ][ ktfact.KTF_TYPE ]
    #            term.printLog( 'ftype: %s' % ( repr( ftype ) ) )

                if ftype == KDT_BOOLEAN:
                    if formValue == 'on':
                        upd[ field_name ] = True
                    else:
                        upd[ field_name ] = False
                else:
                    if ftype == ktfact.KTF_SELECT_INT:
                        if not formValue:
                            formValue = '0'
    #                term.printLog( 'vForm[ %s ]: %s' % (field_name, repr( formValue )) )
                    upd[field_name] = htmlcommon.parseVal( formValue, ftype, allow_nulls )

            if vars[ KQV_LIMIT ]:
                upd[ KQV_LIMIT ] = int( vars[ KQV_LIMIT ] )
            if vars[ KQV_OFFSET ]:
                upd[ KQV_OFFSET ] = int( vars[ KQV_OFFSET ] )
            if vars[ KQV_ORDER ]:
                upd[ KQV_ORDER ] = int( vars[ KQV_ORDER ] )

    #    term.printLog( 'upd: %s' % ( repr( upd ) ) )
        return upd


    def _is_idx_in_mv_rows( self,
                            rows,
                            idx,
                            moving_rows ):
        fld_id = moving_rows.fld_id
        row_id = rows[ idx ][ fld_id ]
        return row_id in moving_rows.rows




def extract_ids_from_vars( request_vars, prefix=ktfact.K_CHK_ID_PREFIX ):
    ids = []
    for v in request_vars:
        if v.startswith( prefix ):
            ids.append( int( v[ len( prefix ) : ] ) )
    return ids
