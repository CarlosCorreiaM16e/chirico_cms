# -*- coding: utf-8 -*-

import datetime

import m16e.htmlcommon as html
from m16e.db import db_tables
from gluon import current
from gluon.html import TABLE, TR, TH, SPAN, SELECT, OPTION, TD, BUTTON, DIV, A, \
    URL, TBODY, I, BR, THEAD, IMG, TFOOT, XML, B
from gluon.storage import Storage
from m16e import term
from m16e.kommon import KQV_LIMIT, KQV_OFFSET, KQV_ORDER, KQV_COMMON_LIST_VARS, \
    storagize, KDT_BOOLEAN, KDT_SELECT_INT, KDT_SELECT_CHAR, KDT_INT, KDT_RAW, \
    KDT_CHAR, KDT_BLOB_IMG, KDT_XML, is_sequence, KDT_BLOB_MEDIA
from m16e.ktfact import KTF_COL_ORDER, KTF_COLS, KTF_TYPE, KTF_SELECT_INT, \
    KTF_SPAN, KTF_KEY_LIST, KTF_CSS_CLASS, KTF_BUTTON, KTF_EDITABLE, \
    KTF_EDITABLE_CLASS, KTF_COL_NAME, KTF_ROWS, KTF_LINK_C, KTF_LINK_F, KTF_MSG, \
    KTF_TITLE, KTF_TOTALIZE, KTF_ROW_CLASS, K_CHK_ID_PREFIX, KTF_CELL_LINK, \
    KTF_ARGS_V, KTF_VARS_F, KTF_VARS_V, KTF_ARGS_F, KTF_ROW_ID_MASK, KTF_AJAX_TARGET


DT = datetime.datetime
DATE = datetime.date

#------------------------------------------------------------------
def getOrderBy( tdef, order, orderBy=None ):
#    term.printLog( 'order: %s' % repr( order ) )
    if order:
        i = 1
        for t in tdef[ KTF_COL_ORDER ]:
            if not orderBy and i == 1:
                orderBy = t
#            term.printLog( 'i: %d; t: %s' % ( i, repr( t ) ) )
            if i == abs( order ):
                orderBy = t
                if order < 0:
                    orderBy += ' desc'
#                term.printLog( repr( orderBy ) )
                break
            i += 1
    elif not orderBy:
        orderBy = tdef[ KTF_COL_ORDER ][0]
    return orderBy

#------------------------------------------------------------------
def requestToSession(
    qdata, sessionVars = {}, args = [], getVars = {}, postVars = {} ):

#     term.printLog( 'sessionVars: ' + repr( sessionVars ) )
#     term.printLog( 'args: ' + repr( args ) )
#     term.printLog( 'getVars: ' + repr( getVars ) )
#     term.printLog( 'postVars: ' + repr( postVars ) )
    vars = Storage()
    page = 0
    if args:                    # page
        page = int( args[ 0 ] )
#        term.printLog( 'page: %s\n' % ( repr( page ) ) )
        if sessionVars:
            vars[ KQV_LIMIT ] = sessionVars[ KQV_LIMIT ]
            vars[ KQV_OFFSET ] = sessionVars[ KQV_LIMIT ] * page
#    term.printLog( 'vars: %s\n' % ( repr( vars ) ) )
    if getVars and KQV_ORDER in getVars:        # qv_order
        vars[ KQV_ORDER ] = int( getVars[ KQV_ORDER ] )
    if postVars:     # query vars
#        term.printLog( 'postVars: ' + repr( postVars ) )
        pVars = getFormFields( qdata, postVars, True )
        for p in pVars:
            vars[ p ] = pVars[ p ]
            if p in KQV_COMMON_LIST_VARS:
                vars[ KQV_OFFSET ] = 0
#    term.printLog( 'vars: %s\n' % ( repr( vars ) ) )
    if sessionVars:
#        term.printLog( 'sessionVars: ' + repr( sessionVars ) )
        for fieldName in qdata[ KTF_COLS ].keys():
            if sessionVars[ fieldName ] and not fieldName in vars:
                vars[ fieldName ] = sessionVars[ fieldName ]
#        term.printLog( 'vars: %s\n' % ( repr( vars ) ) )
        for fieldName in KQV_COMMON_LIST_VARS:
            if sessionVars[ fieldName ] and not fieldName in vars:
                vars[ fieldName ] = sessionVars[ fieldName ]
#        term.printLog( 'vars: %s\n' % ( repr( vars ) ) )

        for fieldName in sessionVars:
            if not fieldName in qdata[ KTF_COLS ].keys() and \
                 not fieldName in KQV_COMMON_LIST_VARS:
                vars[ fieldName ] = sessionVars[ fieldName ]

    return vars

#------------------------------------------------------------------
#varListMap = {
#    'id': (KDT_INT, 0),
#    'name': (KDT_CHAR, '') }
def getFormFields( qdata, vars, allowNulls = False ):
#    term.printLog( 'vars: %s' % ( repr( vars ) ) )
    upd = Storage()
    qdata = storagize( qdata )
    if vars:
        varList = qdata[ KTF_COLS ].keys()
        varList.sort()
#        term.printLog( 'varList: %s' % ( repr( varList ) ) )
        for fieldName in varList:
            formValue = vars[ fieldName ]
            ftype = qdata[ KTF_COLS ][ fieldName ][ KTF_TYPE ]
#            term.printLog( 'ftype: %s' % ( repr( ftype ) ) )

            if ftype == KDT_BOOLEAN:
                if formValue == 'on':
                    upd[ fieldName ] = True
                else:
                    upd[ fieldName ] = False
            else:
                if ftype == KTF_SELECT_INT:
                    if not formValue:
                        formValue = '0'
#                term.printLog( 'vForm[ %s ]: %s' % (fieldName, repr( formValue )) )
                upd[fieldName] = html.parseVal( formValue, ftype, allowNulls )

        if vars[ KQV_LIMIT ]:
            upd[ KQV_LIMIT ] = int( vars[ KQV_LIMIT ] )
        if vars[ KQV_OFFSET ]:
            upd[ KQV_OFFSET ] = int( vars[ KQV_OFFSET ] )
        if vars[ KQV_ORDER ]:
            upd[ KQV_ORDER ] = int( vars[ KQV_ORDER ] )

#    term.printLog( 'upd: %s' % ( repr( upd ) ) )
    return upd

# #------------------------------------------------------------------
# def _getOptionsTable( T,
#                       recCount,
#                       page,
#                       pageCount,
#                       qdata={},
#                       opvars=Storage(),
#                       width=2,
#                       titleCssClass=None,
#                       cellCssClass=None ):
#
# #     term.printDebug( 'opvars: %s' % repr( opvars ) )
#     qdata = storagize( qdata )
# #     term.printDebug( 'qdata: %s' % (repr( qdata ) ) )
#     table = TABLE( _class = 'w100pct small')
#     pct = 100 / (width * 2)
#     if not titleCssClass:
#         titleCssClass = 'small w%dpct' % ( pct )
#     if not cellCssClass:
#         cellCssClass = 'small w%dpct' % ( pct )
#     idx = 0
#     tr = None
#     if qdata.col_order:
#         for varname in qdata.col_order:
# #             term.printDebug( 'varname: %s' % ( repr( varname ) ) )
#             c = qdata.cols[ varname ]
#             if not c:
#                 msg = 'NO DATA FOR OPTION: %s' % ( varname )
#                 term.printLog( msg )
#                 raise Exception( msg )
# #             term.printDebug( 'opvars(%s): %s' % ( varname, repr( opvars ) ) )
#             if not idx:
#                 tr = TR()
#             tr.append( TH( c.title + ':', _class = titleCssClass ) )
#             span = None
#             if c[ KTF_SPAN ]:
#                 span = SPAN( _id = c[ KTF_SPAN ] )
#             if c.type in (KDT_SELECT_INT, KDT_SELECT_CHAR):
#                 if c.callback:
#                     sel = SELECT( _name = varname, _id = varname, _onchange = c.callback )
#                 else:
#                     sel = SELECT( _name = varname, _id = varname )
#     #            sel.append( OPTION( '', _value = '' ) )
# #                term.printDebug(
# #                    'opvars(%s): %s (%s)' %
# #                    ( varname, repr( opvars[ varname ] ), type( opvars[ varname ] ) ) )
#                 for op in c.options:
#                     o = str( op[ 0 ] )
#                     v = str( opvars[ varname ] )
#                     if o == v:
# #                        term.printDebug(
# #                            'o(%s): %s EQUALS v(%s): %s' %
# #                            ( type( o ), repr( o ), type( v ), repr( v ) ) )
#                         sel.append( OPTION( op[1], _value = op[0], _selected = 'selected' ) )
#                     else:
# #                        term.printDebug(
# #                            'o(%s): %s DIFFS v(%s): %s' %
# #                            ( type( o ), repr( o ), type( v ), repr( v ) ) )
#                         sel.append( OPTION( op[1], _value = op[0] ) )
#     #            term.printLog( 'sel: %s' % ( sel.xml() ) )
#                 if span:
#                     span.append( sel )
#                     tr.append( TD( span, _class = cellCssClass ) )
#                 else:
#                     tr.append( TD( sel, _class = cellCssClass ) )
#             else:
#                 colType = 'text'
#                 if c.type == KDT_BOOLEAN:
#                     colType = 'checkbox'
#                 input = html.getInputField( varname,
#                                             value=opvars[ varname ],
#                                             inputType=colType,
#                                             id=varname,
#                                             valueType=c.type,
#                                             readOnly=c.readonly,
#                                             span_wrap=False )
# #                 term.printDebug( 'input: %s' % input.xml() )
#                 if span:
#                     span.append( input )
# #                     term.printDebug( 'span: %s' % span.xml() )
#                     tr.append( TD( span, _class = cellCssClass ) )
#                 else:
#                     tr.append( TD( input, _class = cellCssClass ) )
#
#             idx += 1
#             if idx >= width:
#     #            term.printLog( 'idx: %d' % ( idx ) )
#                 table.append( tr )
#                 idx = 0
#
#     if idx and len( qdata.buttons ) > (width - idx - 2) * 2:
# #        term.printLog( 'idx: %d' % ( idx ) )
#         table.append( tr )
#         tr = TR()
#         idx = 0
#     else:
#         term.printLog( 'BUG??? tr: %s' % (tr.xml() if tr else repr( tr ) ) )
#
#     span = SPAN()
#     if not idx:
#         span.append( SPAN( T( 'Number of records' ) + ': ' + str( recCount or 0 ) ) )
#     else:
#         span.append( SPAN( T( 'Number of records' ) + ': ' + str( recCount or 0 ),
#                            _class = 'margin_buttons' ) )
#     if page:
#         span.append( SPAN( T( 'Page %d of %d' ) % ( page, pageCount ),
#                            _class='margin_buttons' ) )
#         span.append( SPAN( T( 'Records/page' ) + ':',
#                            _style='margin-left: 1em; margin-right: 0.5em;' ) )
#         input = html.getInputField( KQV_LIMIT,
#                                     id=KQV_LIMIT,
#                                     value=opvars.qv_limit or 20,
#                                     valueType=KDT_INT )
#         input[ '_style' ] = 'margin-left: 0.25em; margin-right: 1em; width: 3em;'
#         span.append( input )
#     if len( qdata.buttons ) > 5: # width:
#         tr.append( TD( span, _colspan=(width - idx), _class='text-center' ) )
#         table.append( tr )
#         span = SPAN()
#         tr = TR()
#         idx = 0
#     for bt in qdata.buttons:
#         el = None
#         if bt.img:
#             el = bt.img
#         else:
#             el = bt.title
#         cssClass = 'bt_12 margin_buttons btn'
#         if bt.css_class:
#             cssClass += ' ' + bt.css_class
#         input = BUTTON( el,
#                         _name=bt.name,
#                         _id=bt.id,
#                         _type='submit',
#                         _title=bt.title,
#                         _value=bt.value or 'submit',
#                         _class=cssClass,
#                         _onclick=bt.onclick )
# #         if bt.img:
# #             input.append( bt.img )
# #         if bt.title:
# #             input.append( bt.title )
#
#         span.append( input )
#
#     tr.append( TD( span,
#                    _colspan=(width - idx), # * 2,
#                    _class='text-center' ) )
#     table.append( tr )
# #    term.printLog( 'table: %s' % ( table.xml() ) )
#     return table

#------------------------------------------------------------------
def _get_qdata_col( tr,
                    qdata,
                    opvars=Storage(),
                    varname=None,
                    titleCssClass=None,
                    cellCssClass=None ):
    c = qdata.cols[ varname ]
    if not c:
        msg = 'NO DATA FOR OPTION: %s' % ( varname )
        term.printLog( msg )
        raise Exception( msg )
    if c.get( KTF_CSS_CLASS ) != 'hidden':
        tr.append( TH( c.title + ':', _class = titleCssClass ) )
    span = None
    if c[ KTF_SPAN ]:
        span = SPAN( _id = c[ KTF_SPAN ] )
    if c.get( KTF_CSS_CLASS ):
        if cellCssClass:
            cellCssClass += ' %s' % c.get( KTF_CSS_CLASS )
        else:
            cellCssClass = c.get( KTF_CSS_CLASS )
    if c.type in (KDT_SELECT_INT, KDT_SELECT_CHAR):
        if c.callback:
            sel = SELECT( _name=varname,
                          _id=varname,
                          _onchange=c.callback )
        else:
            sel = SELECT( _name=varname,
                          _id=varname )
#                term.printDebug(
#                    'opvars(%s): %s (%s)' %
#                    ( varname, repr( opvars[ varname ] ), type( opvars[ varname ] ) ) )
        for op in c.options:
            o = str( op[ 0 ] )
            v = str( opvars[ varname ] )
            if o == v:
#                        term.printDebug(
#                            'o(%s): %s EQUALS v(%s): %s' %
#                            ( type( o ), repr( o ), type( v ), repr( v ) ) )
                sel.append( OPTION( op[1], _value = op[0], _selected = 'selected' ) )
            else:
#                        term.printDebug(
#                            'o(%s): %s DIFFS v(%s): %s' %
#                            ( type( o ), repr( o ), type( v ), repr( v ) ) )
                sel.append( OPTION( op[1], _value = op[0] ) )
#            term.printLog( 'sel: %s' % ( sel.xml() ) )
        if span:
            span.append( sel )
            tr.append( TD( span, _class = cellCssClass ) )
        else:
            tr.append( TD( sel, _class = cellCssClass ) )
    else:
        colType = 'text'
        if c.type == KDT_BOOLEAN:
            colType = 'checkbox'
        input = html.getInputField( varname,
                                    value=opvars[ varname ],
                                    inputType=colType,
                                    id=varname,
                                    valueType=c.type,
                                    readOnly=c.readonly,
                                    span_wrap=False )
#                 term.printDebug( 'input: %s' % input.xml() )
        if span:
            span.append( input )
#                     term.printDebug( 'span: %s' % span.xml() )
            tr.append( TD( span, _class = cellCssClass ) )
        else:
            tr.append( TD( input, _class = cellCssClass ) )

#------------------------------------------------------------------

#------------------------------------------------------------------
def _getOptionsTable( T,
                      recCount,
                      page,
                      pageCount,
                      qdata={},
                      opvars=Storage(),
                      width=2,
                      titleCssClass=None,
                      cellCssClass=None,
                      use_select_action=False,
                      table_id=None,
                      extra_rows=[] ):

#     term.printDebug( 'opvars: %s' % repr( opvars ) )
    qdata = storagize( qdata )
#     term.printDebug( 'qdata: %s' % (repr( qdata ) ) )
    bt_action_id = 'bt_action'
    if table_id:
        bt_action_id += '_%s' % table_id
    table = TABLE( _class = 'w100pct small')
    pct = 100 / width   # (width * 2)
    if not titleCssClass:
        titleCssClass = 'small w%dpct' % ( pct )
    if not cellCssClass:
        cellCssClass = 'small w%dpct' % ( pct )
    idx = 0
    tr = TR()
    if qdata.col_order:
        for varname in qdata.col_order:
#             term.printDebug( 'varname: %s' % ( repr( varname ) ) )
#             if not idx:
#                 tr = TR()
            _get_qdata_col( tr,
                            qdata,
                            opvars=opvars,
                            varname=varname,
                            titleCssClass=titleCssClass,
                            cellCssClass=cellCssClass )

            idx += 1
            if idx >= width:
    #            term.printLog( 'idx: %d' % ( idx ) )
                table.append( tr )
                tr = TR()
                idx = 0

    term.printDebug( 'idx: %d' % ( idx ) )
    if idx + 1 >= width or len( qdata.buttons ) > 2:
#        term.printLog( 'idx: %d' % ( idx ) )
        if tr:
            table.append( tr )
        tr = TR()
        idx = 0
    else:
        term.printLog( 'BUG??? tr: %s' % (tr.xml() if tr else '(none)' ) )
#     else:
#         term.printLog( 'BUG??? tr: %s' % (tr.xml() if tr else repr( tr ) ) )

    if extra_rows:
        if tr:
            table.append( tr )
        idx = 0
        t_inner = TABLE( _class='margin_0' )
        for r in extra_rows:
            t_inner.append( r )
        table.append( TR( TD( t_inner,
                              _colspan=width * 2 ) ) )
        tr = TR()

    span = SPAN()
    if not idx:
        span.append( SPAN( T( 'Number of records' ) + ': ' + str( recCount or 0 ) ) )
    else:
        span.append( SPAN( T( 'Number of records' ) + ': ' + str( recCount or 0 ),
                           _class = 'margin_buttons' ) )
    if page:
        span.append( SPAN( T( 'Page %d of %d' ) % ( page, pageCount ),
                           _class='margin_buttons' ) )
        span.append( SPAN( T( 'Records/page' ) + ':',
                           _style='margin-left: 1em; margin-right: 0.5em;' ) )
        input = html.getInputField( KQV_LIMIT,
                                    id=KQV_LIMIT,
                                    value=opvars.qv_limit or 20,
                                    valueType=KDT_INT )
        input[ '_style' ] = 'margin-left: 0.25em; margin-right: 1em; width: 5em;'
        span.append( input )
    if use_select_action:
        if idx + 2 > width: # width:
            tr.append( TD( span, _colspan=(width - idx) * 2, _class='text-center' ) )
            table.append( tr )
            span = SPAN()
            tr = TR()
            idx = 0
        sel_span = SPAN( _class='nowrap' )
        # colors: tuple of ( bg_color, fg_color )
        opt_colors = { 'sel_bt': ('#0181D0', '#FFFFFF'),
                       'submit_bt': ('#F2F2F2', '#FFFFFF'),
                       'nav_bt': ('#008080', '#FFFFFF'),
                       'del_bt': ('#D00000', '#FFFFFF'),
                       }
        sel_span.append( B( T( 'Action' ) + ': ' ) )
        onchange = ''
        js_buttons = []
        for bt in qdata.buttons:
            if bt.onclick:
                js_buttons.append( bt )
                continue

            opt_color = opt_colors[ 'submit_bt' ]
            if bt.css_class:
                opt_color = opt_colors[ bt.css_class ]
            onchange += '''
                if( $(this ).val() == '%(bt_value)s' ) {
                    $( '#%(bt_action)s' ).css( 'background-color','%(bg)s' );
                    $( '#%(bt_action)s' ).css( 'color','%(fg)s' );
                } ''' % { 'bt_value': bt.value,
                          'bt_action': bt_action_id,
                          'bg': opt_color[0],
                          'fg': opt_color[1] }
        sel = SELECT( _name='action',
                      _id=bt_action_id,
                      _onchange=onchange )
        for bt in qdata.buttons:
            if bt in js_buttons:
                continue

            opt_color = opt_colors[ 'submit_bt' ]
            if bt.css_class:
                opt_color = opt_colors[ bt.css_class ]
            sel.append( OPTION( bt.title,
                                _value=bt.value,
                                _style='background-color: %s; color: %s' %
                                (opt_color[0], opt_color[1]) ) )
        sel_span.append( sel )
        bt = BUTTON( T( 'Execute' ),
                        _id='bt_submit',
                        _type='submit',
                        _title=T( 'Execute selected action' ),
                        _value='submit',
                        _class='submit_bt' )
        sel_span.append( bt )

        for bt in js_buttons:
            cssClass = 'btn btn-submit'
            if bt.css_class:
                cssClass += ' ' + bt.css_class
            jsbt = BUTTON( bt.title,
                           _name=bt.name,
                           _id=bt.id,
                           _type='submit',
                           _title=bt.title,
                           _value=bt.value or 'submit',
                           _class=cssClass,
                           _onclick=bt.onclick )
            span.append( jsbt )

        span.append( sel_span )

    else:
        if len( qdata.buttons ) > width: # width:
            tr.append( TD( span, _colspan=(width - idx) * 2, _class='text-center' ) )
            table.append( tr )
            span = SPAN()
            tr = TR()
            idx = 0
        for bt in qdata.buttons:
            el = None
            if bt.img:
                el = bt.img
            else:
                el = bt.title
            cssClass = 'btn btn-submit'
            if bt.css_class:
                cssClass += ' ' + bt.css_class
            input = BUTTON( el,
                            _name=bt.name,
                            _id=bt.id,
                            _type='submit',
                            _title=bt.title,
                            _value=bt.value or 'submit',
                            _class=cssClass,
                            _onclick=bt.onclick )
            span.append( input )

    tr.append( TD( span,
                   _colspan=(width - idx) * 2, # * 2,
                   _class='text-center' ) )
    table.append( tr )
#    term.printLog( 'table: %s' % ( table.xml() ) )
    return table

#------------------------------------------------------------------
def getNavOptions( T,
                   recCount,
                   qdata=Storage(),
                   opvars=Storage(),
                   offset=0,
                   limit=20,
                   width=2,
                   functionName='index',
                   titleCssClass=None,
                   cellCssClass=None,
                   use_select_action=False,
                   table_id=None,
                   extra_rows=[] ):

#     term.printDebug( 'limit: %s; offset: %s; recCount: %s' %
#                      (limit, offset, recCount) )
    request = current.request
    qdata = storagize( qdata )
    div = DIV()
    table = TABLE( _class = 'w100pct inner_table table_border' )
    page = 0
    pageCount = 0
    tr = TR()
    qvars = Storage()
    for k in opvars:
        if opvars[k] and k != KQV_OFFSET:
            qvars[k] = opvars[k]
    if limit > 0:
        a = ''
        if offset - limit >= 0:
            ofs = offset - limit
    #        session.querydata = qd
            prevPage = ofs / limit
#             term.printDebug( 'prevPage: %s' % prevPage )
#             if functionName.startswith( 'ajax_' ):
#                 onclick = '''
#                     ajax( '%(url)s', [], '%(target)s' );
#                 ''' % { 'url': URL( f=functionName, args=prevPage, vars=qvars ),
#                         'target': ajax_target }
#                 a = A( '<<',
#                        _href=URL( f=functionName, args=prevPage, vars=qvars ),
#                        _class='bt_12 margin_buttons button' )
#             else:
            if request.cid:
                a = A( '<<',
                       _href=URL( f=functionName, args=prevPage, vars=qvars ),
                       _class='btn btn-submit',
                       cid=request.cid )
            else:
                a = A( '<<',
                       _href=URL( f=functionName, args=prevPage, vars=qvars ),
                       _class='btn btn-submit' )

        tr.append( TD( a,
                       _class='w5pct inner_table',
                       _style='vertical-align: bottom;' ) )
        page = (offset / limit) + 1
        pageCount = (recCount / limit) + 1
    it = _getOptionsTable( T,
                           recCount,
                           page,
                           pageCount,
                           qdata,
                           opvars,
                           width,
                           titleCssClass,
                           cellCssClass,
                           use_select_action=use_select_action,
                           table_id=table_id,
                           extra_rows=extra_rows )

    tr.append( TD( it, _class = 'w90pct inner_table' ) )
    if limit > 0:
        a = ''
        if offset + limit < recCount:
            ofs = offset + limit
            nextPage = ofs / limit
#             term.printDebug( 'nextPage: %s' % nextPage )
            if request.cid:
                a = A( '>>',
                       _href=URL( f=functionName,
                                  args=nextPage,
                                  vars=qvars ),
                       _class='btn btn-submit',
                       cid=request.cid )
            else:
                a = A( '>>',
                       _href=URL( f=functionName,
                                  args=nextPage,
                                  vars=qvars ),
                       _class='btn btn-submit' )

        tr.append( TD( a,
                       _class='w5pct inner_table',
                       _style='vertical-align: bottom;' ) )
    table.append( tr )
    div.append( table )
    return div

#------------------------------------------------------------------
def get_link_args_and_vars( col, row ):
#     term.printDebug( 'col: %s' % ( repr( col ) ) )
#     term.printDebug( 'row: %s' % ( repr( row ) ) )
#     term.printDebug( 'col[ KTF_CELL_LINK ][ KTF_ARGS_F ]: %s' % ( repr( col[ KTF_CELL_LINK ][ KTF_ARGS_F ] ) ) )
#     term.printDebug( 'col[ KTF_CELL_LINK ][ KTF_ARGS_V ]: %s' % ( repr( col[ KTF_CELL_LINK ][ KTF_ARGS_V ] ) ) )
#     term.printDebug( 'col[ KTF_CELL_LINK ][ KTF_VARS_F ]: %s' % ( repr( col[ KTF_CELL_LINK ][ KTF_VARS_F ] ) ) )
#     term.printDebug( 'col[ KTF_CELL_LINK ][ KTF_VARS_V ]: %s' % ( repr( col[ KTF_CELL_LINK ][ KTF_VARS_V ] ) ) )
    arg_list = []
    # by field name
    if col[ KTF_CELL_LINK ][ KTF_ARGS_F ]:
        for arg in col[ KTF_CELL_LINK ][ KTF_ARGS_F ]:
            if arg in row:
                arg_list.append( row[ arg ] )
    # by value
    if col[ KTF_CELL_LINK ][ KTF_ARGS_V ]:
        args_v = col[ KTF_CELL_LINK ][ KTF_ARGS_V ]
        if is_sequence( args_v ):
            for arg in col[ KTF_CELL_LINK ][ KTF_ARGS_V ]:
                arg_list.append( arg )
        else:
            arg_list.append( args_v )

    var_dict = {}
    # by field name
    if col[ KTF_CELL_LINK ][ KTF_VARS_F ]:
        for arg in col[ KTF_CELL_LINK ][ KTF_VARS_F ]:
            if col[ KTF_CELL_LINK ][ KTF_VARS_F ][ arg ] in row:
                var_dict[ arg ] = row[ col[ KTF_CELL_LINK ][ KTF_VARS_F ][ arg ] ]
#             if arg == KQV_RETURN_NAME:
#                 c_name = col[ KTF_CELL_LINK ][ KTF_VARS_F ][ arg ]
#                 var_dict[ c_name ] = row
    if col[ KTF_CELL_LINK ][ KTF_VARS_V ]:
        for arg in col[ KTF_CELL_LINK ][ KTF_VARS_V ]:
            var_dict[ arg ] = col[ KTF_CELL_LINK ][ KTF_VARS_V ][ arg ]
#     term.printDebug( 'arg_list: %s' % ( repr( arg_list ) ) )
#     term.printDebug( 'var_dict: %s' % ( repr( var_dict ) ) )
    return (arg_list, var_dict)

#------------------------------------------------------------------
#selections = {
#    colId: { 'cssClass': 'class', 'selList': [] }
#}
#
#moving_rows = {
#    'col_name': 'id',
#    'rows': [],
#    'link_c': 'question_list',
#    'link_f': 'paste_rows'
#}
def getTableBody( tdef,
                  rows,
                  selections=[],
                  movingRows={},
                  highlight_row_class=None ):

    tdef = storagize( tdef )
    cellClass = tdef.cell_class

    row_id_mask = tdef.get( KTF_ROW_ID_MASK )
    tbody = TBODY()
    for idx, row in enumerate( rows ):
#         term.printDebug( 'row: %s' % ( repr( row ) ) )
        if not isinstance( row, Storage ):
            row = Storage( row )
        if row_id_mask:
            tr = TR( _id=row_id_mask % row )
        else:
            tr = TR()
        if highlight_row_class:
            tr[ '_onmouseover' ] = '''jQuery( this ).addClass( '%s' );''' % highlight_row_class
            tr[ '_onmouseout' ] = '''jQuery( this ).removeClass( '%s' );''' % highlight_row_class
#        term.printDebug( 'row: %s' % repr( row ) )
        if row.has_key( KTF_ROW_CLASS ):
            tr[ '_class' ] = row[ KTF_ROW_CLASS ]
        for c in tdef.col_order:
#             term.printDebug( 'val (%s): %s (%s)' % (c, repr( row[c] ), type( row[c] ) ) )
            val = None
            col = tdef.cols[ c ]
            rowClass = ''
            for colName in selections:
                v = row[ colName ]
                if v in selections[ colName ][ KTF_KEY_LIST ]:
                    rowClass = selections[ colName ][ KTF_CSS_CLASS ]
                    if tr[ '_class' ]:
                        if not rowClass in tr[ '_class' ]:
                            tr[ '_class' ] = tr[ '_class' ] + ' ' + rowClass
                    else:
                        tr[ '_class' ] = rowClass
                    break

            cellClass = col.cell_class and col.cell_class or tdef.cell_class
#             term.printLog( 'tdef.cols[ %s ] - class: %s' % ( c, repr( cellClass ) ) )
#            term.printLog( 'tdef.cols[ %s ]: %s' % ( c, repr( col ) ) )
            if col.type == KTF_BUTTON:
                arg_list, var_dict = get_link_args_and_vars( col, row )
                url = URL(
                    c=col[ KTF_CELL_LINK ].link_c,
                    f=col[ KTF_CELL_LINK ].link_f,
                    args=arg_list,
                    vars=var_dict )
                cssClass = 'btn btn-submit'
                if col.css_class:
                    cssClass = col.css_class
                input = A( col.title,
                           _href=url,
                           _class=cssClass )
#                 BUTTON(
#                     col.title, _name = 'action', _type = 'submit',
#                     _value = row[ c ], _class = cssClass )
                tr.append( TD( input, _class = cellClass + ' text-center' ) )
            elif col.type == KDT_BLOB_IMG:
                url = URL( c='default',
                           f='download', args=[ 'db', row[ c ] ] )
#                 term.printDebug( 'url: %s' % ( repr( url ) ) )
                val = IMG( _src=url )
                if col.width:
                    val[ '_width' ] = col.width
                tr.append( TD( val ) )
            elif col.type == KDT_BLOB_MEDIA:
                url = URL( c='default',
                           f='download', args=[ 'db', row[ c ] ] )
                #                 term.printDebug( 'url: %s' % ( repr( url ) ) )
                from gluon.contrib.autolinks import expand_one
                val = XML( expand_one( url, row ) )
                if col.width:
                    val[ '_width' ] = col.width
                tr.append( TD( val ) )
            elif col.type == KDT_XML:
                val = XML( row[ c ] )
                tr.append( TD( val, _class = cellClass ) )
            else:
                if c in row:
                    if col.type == KDT_RAW:
                        val = row[ c ]
#                         term.printDebug( 'val (%s): %s (%s)' % (c, repr( val ), type( val ) ) )
                    else:
                        val = html.format( col.type,
                                           row[ c ],
                                           allowNulls=True,
                                           mask=col.mask )
                        if col.max_length and len( val ) > col.max_length:
                            val = val[ : col.max_length ].rsplit( ' ', 1 )[0] + ' (...)'
#                         term.printDebug( 'val (%s): %s (%s)' % (c, repr( val ), type( val ) ) )
                else:
#                    val = col.title
                    val = ''
                if col[ KTF_CELL_LINK ] and val:
#                    term.printLog( 'val: %s' % ( repr( val ) ) )
                    if not val and \
                         (col[ KTF_CELL_LINK ].use_icon or \
                            ( col[ KTF_CELL_LINK ].use_icon is None and col.type == KDT_INT ) ):
                        val = col.title
#                     term.printDebug( 'val: %s' % ( repr( val ) ) )
                    arg_list, var_dict = get_link_args_and_vars( col, row )
                    url = URL( c=col[ KTF_CELL_LINK ].link_c,
                               f=col[ KTF_CELL_LINK ].link_f,
                               args=arg_list,
                               vars=var_dict )
#                     term.printDebug( 'url: %s' % str( url ) )
                    if col[ KTF_CELL_LINK ].use_icon or \
                         ( col[ KTF_CELL_LINK ].use_icon is None and col.type == KDT_INT ):

                        if col.type == KDT_CHAR:
                            span = SPAN()
                            aStyle = 'margin-right: 0.5em;'
                        else:
                            span = SPAN( val )
                            aStyle = 'margin-left: 0.5em;'
                        i = I( _class='glyphicon glyphicon-circle-arrow-right glyphicon-white' )
                        ajax_target = col[ KTF_CELL_LINK ].get( KTF_AJAX_TARGET )
                        if ajax_target:
                            if ajax_target:
                                ajax_target = ':eval'
                            onclick = '''
                                ajax( '%(url)s', [], '%(target)s' );
                            ''' % { 'url': url, 'target': ajax_target }
                            a = A( i,
                                   _class='dark_bg',
                                   _style=aStyle,
                                   _href='#',
                                   _onclick=onclick )
                        else:
                            a = A( i,
                                   _class='dark_bg',
                                   _style=aStyle,
                                   _href=url )

                        if col[ KTF_CELL_LINK ].title:
                            a[ '_title' ] = col[ KTF_CELL_LINK ].title
                        span.append( a )
                        if col.type == KDT_CHAR:
                            span.append( val )
                        val = span
                    else:
                        val = A( val, _href = url )
#                     term.printDebug( 'val (%s): %s (%s)' % (c, repr( val ), type( val ) ) )
#                    term.printLog( 'val: %s' % ( val.xml() ) )
                elif col[ KTF_EDITABLE ] and row[ col[ KTF_EDITABLE ] ]:
                    cellId = 'row__%s__%d' % ( c, row[ col[ KTF_EDITABLE ] ] )
                    val = html.getInputField(
                        cellId, value = val, id = cellId, valueType = col.type )
                    if col[ KTF_EDITABLE_CLASS ]:
                        val[ '_class' ] += ' ' + col[ KTF_EDITABLE_CLASS ]
#                 term.printDebug( 'val (%s): %s (%s)' % (c, repr( val ), type( val ) ) )
#                 term.printDebug( 'str: %s' % str( val ) )
                style = html.get_align( col.type )
                if cellClass:
                    style += ' ' + cellClass
#                 if movingRows and c in groupby:


                tr.append( TD( val, _class = style ) )
                if row.row__id:
                    tr[ '_id' ] = row.row__id
#                    tr[ '_class' ] = 'highlight'
        if tdef.checkboxes:
            for cb in tdef.checkboxes:
                cbName = cb.name % ( row[ cb.checkbox_id ] )
                input = html.getInputField( cbName, inputType = 'checkbox', id = cbName )
                td = TD( input, _class = 'text-center ' + cellClass )
                tr.append( td )
        if movingRows:
            id = row[ movingRows[ KTF_COL_NAME ] ]
            if not id in movingRows[ KTF_ROWS ]:
                div = DIV( _class = 'row_insertion_icons' )
                url = URL(
                    c = movingRows[ KTF_LINK_C ],
                    f = movingRows[ KTF_LINK_F ],
                    args = [ 'before', id ] )
                i = I( _class = 'glyphicon glyphicon-circle-arrow-up glyphicon-white' )
                a = A(
                    i,
                    _class = 'dark_bg',
                    _href = url )
                div.append( a )

#                 if row == rows[ -1 ]:
                div.append( BR() )
                url = URL(
                    c = movingRows[ KTF_LINK_C ],
                    f = movingRows[ KTF_LINK_F ],
                    args = [ 'after', id ] )
                i = I( _class = 'glyphicon glyphicon-circle-arrow-down glyphicon-white' )
                a = A(
                    i,
                    _class = 'dark_bg_down',
                    _href = url )
                div.append( a )
                tr.append( TD( div, _class = 'row_insertion_icons' ) )
        tbody.append( tr )
        if row.validationResult:
            tbody.append(
                TR(
                    TD(
                        I(_class = 'glyphicon glyphicon-arrow-up' ),
                        row.validationResult[ KTF_MSG ],
                        _colspan = len( tdef.col_order ),
                        _class = row.validationResult[ KTF_CSS_CLASS ] ) ) )
#         if movingRows:
#             for g in groupby:
#                 last_groups[ g ] = row[ g ]

#    term.printLog( 'totalizers: %s' % ( repr( totalizers ) ) )
#    term.printLog( 'tbody: %s' % ( repr( tbody.xml() ) ) )
    return tbody

#------------------------------------------------------------------
def getTableHeader(
    tdef,
    transportText=None,
    totalizers=Storage(),
    controller=None,
    function='index',
    order=None,
    query_vars={} ):

#    term.printLog( 'totalizers: %s' % ( repr( totalizers ) ) )

#    term.printLog( 'tdef: %s' % ( repr( tdef ) ) )
    tdef = storagize( tdef )
#    term.printLog( 'order: %s' % ( repr( order ) ) )
    cellClass = tdef.cell_class
    thead = THEAD()
    if tdef.header_groups:
        tr = TR( _class = 'table_header' )
        for hg in tdef.header_groups:
            tr.append(
                TH(
                    hg[ KTF_TITLE ],
                    _colspan = len( hg[ KTF_COLS ] ),
                    _class = 'table_border text-center' ) )
        if tdef.checkboxes:
            tr.append(
                TH( '', _colspan = len( tdef.checkboxes ), _class = 'table_border' ) )
            thead.append( tr )

    tr = TR( _class = 'table_header' )
    i = 0
#    term.printLog( 'tdef.sortable_cols: %s' % ( repr( tdef.sortable_cols ) ) )
    for c in tdef.col_order:
        i += 1
        col = tdef.cols[ c ]
        if not col:
            term.printLog( 'no col found: %s' % ( repr( c ) ) )
#        term.printLog( 'col: %s' % ( repr( col ) ) )
        cellClass = col.cell_class or tdef.cell_class
        if col.get( KTF_CSS_CLASS ):
            css_class = col.get( KTF_CSS_CLASS )
            if not css_class in cellClass:
                cellClass += ' ' + css_class
#         term.printLog( 'tdef.cols[ %s ] - class: %s' % ( c, repr( cellClass ) ) )

        style = html.get_align( col.type ) + ' ' + cellClass
#         term.printLog( 'style: %s' % ( style ) )
#        term.printLog( 'c: %s' % ( repr( c ) ) )
        if tdef.sortable_cols and c in tdef.sortable_cols:
#            term.printLog( 'i: %s; order: %s' % ( repr( i ), repr( order ) ) )
            if order and i == abs( order ):
                lOrder = order * (-1)
#                term.printLog( 'lOrder: %s' % ( repr( lOrder ) ) )
                if order > 0:
                    img = IMG( _src = URL( 'static', 'images/order_asc.png' ) )
                else:
                    img = IMG( _src = URL( 'static', 'images/order_desc.png' ) )
                query_vars[ KQV_ORDER ] = lOrder
                url = URL( c=controller, f=function, vars=query_vars )
                link = A( tdef.cols[ c ][ 'title' ], _href = url )
                tr.append( TH( SPAN( img, link,
                                     _style = 'white-space:nowrap;' ),
                               _class = style ) )
            else:
                query_vars[ KQV_ORDER ] = i
                url = URL( c=controller, f=function, vars=query_vars )
                a = A( col.title, _href = url )
                tr.append( TH( a, _class = style ) )
        else:
            tr.append( TH( col.title, _class = style ) )
    if tdef.checkboxes:
        for cb in tdef.checkboxes:
            tr.append( TH( cb.title, _class = cellClass ) )

    thead.append( tr )
    totalize = False
    totColSpan = -1
    for c in tdef.col_order:
        totColSpan += 1
        col = tdef.cols[ c ]
#         term.printDebug( 'col: %s' % ( repr( col ) ) )
        if col[ KTF_TOTALIZE ]:
            totalize = True
            break
#     term.printDebug( 'totalize: %s' % ( repr( totalize ) ) )

    if totalize:
        i = 0
        tr = TR( _class = 'table_totals' )
        val = transportText + ':'
        tr.append( TH( val, _colspan = totColSpan, _class = 'text-right ' + cellClass ) )
        for c in tdef.col_order:
#            term.printLog( 'c: %s' % ( repr( c ) ) )
            col = tdef.cols[ c ]
#            term.printLog( 'col: %s' % ( repr( col ) ) )
            style = html.get_align( col.type ) + ' ' + cellClass
            if col[ KTF_TOTALIZE ]:
                val = html.format( col.type, totalizers[ c ] or 0.0 )
                tr.append( TH( val, _class = style ) )
            elif i >= totColSpan:
                tr.append( TH( '', _class = style ) )
            i += 1

        thead.append( tr )

#    term.printLog( 'thead: %s' % ( thead.xml() ) )
#    term.printLog( 'totalizers: %s' % ( repr( totalizers ) ) )
    return thead

#------------------------------------------------------------------
def getTableFooter( tdef, totalizers=Storage(), totalsText=None ):
    tdef = storagize( tdef )
    cellClass = tdef.cell_class
    tfoot = TFOOT()
    totalize = False
    totColSpan = -1
    for c in tdef.col_order:
        totColSpan += 1
        col = tdef.cols[ c ]
        if col.has_key( KTF_TOTALIZE ):
            totalize = True
            break
#    term.printLog( 'totalize: %s' % ( repr( totalize ) ) )
    if totalize:
        i = 0
        tr = TR( _class = 'table_totals' )
        val = totalsText + ':'
        tr.append( TH( val, _colspan = totColSpan, _class = 'text-right ' + cellClass ) )
        for c in tdef.col_order:
            col = tdef.cols[ c ]
            style = html.get_align( col.type ) + ' ' + cellClass
            if col[ KTF_TOTALIZE ]:
                val = html.format( col.type, totalizers[ c ] or 0.0 )
                tr.append( TH( val, _class = style ) )
            elif i >= totColSpan:
                tr.append( TH( '', _class = style ) )
            i += 1

        tfoot.append( tr )
    return tfoot

#------------------------------------------------------------------
def getTable(
    tdef,
    rows,
    transportText=None,
    totalsText=None,
    totalizers=Storage(),
    controller=None,
    function='index',
    order=None,
    selections=[],
    movingRows={},
    highlight_row_class='highlight_row',
    query_vars={},
    table_id=None ):

#     term.printDebug( 'function: %s' % repr( function ) )
#    term.printLog( 'totalizers: %s' % ( repr( totalizers ) ) )

#    term.printLog( 'rows: %d' % ( len( rows ) ) )
#    term.printLog(
#        'transportText: %s\ntotalsText: %s' %
#        ( repr( transportText ), repr( totalsText ) ) )
    tdef = storagize( tdef )
    thead = getTableHeader( tdef,
                            transportText,
                            totalizers=totalizers.header,
                            controller=controller,
                            function=function,
                            order=order,
                            query_vars=query_vars )
#    term.printLog( 'totalizers: %s' % ( repr( totalizers ) ) )
    tbody = getTableBody( tdef, rows, selections, movingRows, highlight_row_class )
#    term.printLog( 'totalizers: %s' % ( repr( totalizers ) ) )

    tfoot = getTableFooter( tdef, totalizers.footer, totalsText )

    table = TABLE( _id=table_id,
                   _class='w100pct' )
    table.append( thead )
    table.append( tbody )
    table.append( tfoot )
#    term.printLog( 'table: %s' % ( repr( table.xml() ) ) )
    return table

#------------------------------------------------------------------
def extract_ids_from_vars( request_vars ):
    ids = []
    for v in request_vars:
        if v.startswith( K_CHK_ID_PREFIX ):
            ids.append( int( v[ len( K_CHK_ID_PREFIX ) : ] ) )
    return ids
