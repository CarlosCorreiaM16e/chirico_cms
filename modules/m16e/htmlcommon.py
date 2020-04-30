# -*- coding: utf-8 -*-

import re
import sys
import traceback
from decimal import Decimal

import m16e.term as term
from gluon import current, DIV, A, LI, xmlescape, TABLE, TR, TD
from gluon.html import SPAN, SELECT, OPTION, SCRIPT, INPUT, BUTTON, TEXTAREA
from gluon.storage import Storage
from gluon.tools import prettydate
from m16e.db import db_tables
from m16e.decorators import deprecated
from m16e.kommon import KDT_DEC, KDT_MONEY, KDT_PERCENT, KDT_BOOLEAN, KDT_DATE, \
    KDT_TIME, KDT_TIMESTAMP, KDT_CHAR, KDT_INT, KDT_SELECT_INT, KDT_SELECT_CHAR, TAB_ROLE, DT, KDT_TIMESTAMP_PRETTY
from m16e.ui import ui_factory

BOOTSTRAP_NONE_SELECTED_TEXT = ''
BOOTSTRAP_SELECTED_AUTO_THRESHOLD = 16

decimalPattern = '%.2f'

#------------------------------------------------------------------
def getFields( formVars, dbTable ):
    upd = Storage()
    for dbFieldName in dbTable.fields:
        if not dbFieldName in formVars:
            term.printLog( 'Field \'%s\' not in form' % dbFieldName )
            continue

        form_value = formVars[ dbFieldName ]
        if form_value is None:
            form_value = dbTable[ dbFieldName ].default
        if dbTable[ dbFieldName ].type == 'boolean':
            if form_value == 'on':
                form_value = True
            else:
                form_value = False
        upd[ dbFieldName ] = form_value

    return upd

#------------------------------------------------------------------
@deprecated( replacement='''htmlcommon.get_changed_fields( form_vars, post_vars, db_table, field_prefix='', get_all=False )''' )
def getChangedFields( formVars,
                      postVars,
                      dbTable,
                      fieldPrefix='',
                      get_all=False ):
#    term.printDebug( 'dbTable: %s' % repr( dbTable ) )
    upd = Storage()
    for fld in dbTable.fields:
        dbFieldName = fieldPrefix + fld
        if not dbFieldName in formVars and not dbFieldName in postVars:
#             term.printLog( 'Field \'%s\' not in form' % dbFieldName )
            continue

        db_value = postVars[ 'org__' + dbFieldName ]
        form_value = postVars[ dbFieldName ]
#        term.printDebug(
#            '>>> (UPD) vDb[%s]: %s: %s; vForm: %s' %
#            (dbFieldName, repr( db_value ),
#             dbTable[ fld ].type, repr( form_value ) ) )
        if db_value is None and form_value == '':
            form_value = None
        if form_value is None:
            form_value = dbTable[ fld ].default
        if dbTable[ fld ].type == 'boolean':
            if form_value == 'on':
                form_value = True
            else:
                form_value = False
        elif form_value is not None \
                and ( dbTable[ fld ].type == 'integer'
              or dbTable[ fld ].type.startswith( 'reference ' ) ):
            form_value = int( form_value )

#            term.printDebug(
#                '>>> (UPD) vDb[%s]: %s; vForm: %s' %
#                (dbFieldName, repr( db_value ), repr( form_value )) )
        if get_all or str( db_value ) != str( form_value ):
#             term.printDebug(
#                 '>>> (UPD) vDb[%s]: %s; vForm: %s' %
#                 (dbFieldName, db_value, form_value) )
            upd[fld] = form_value

#    term.printLog( 'upd: ' + repr( upd ) )
    return upd

#------------------------------------------------------------------
def get_changed_fields( form_vars,
                        post_vars,
                        db_table,
                        field_prefix='',
                        get_all=False ):
#    term.printDebug( 'db_table: %s' % repr( db_table ) )
    upd = Storage()
    for fld in db_table.fields:
        db_field_name = field_prefix + fld
        try:
            if not db_field_name in form_vars and not db_field_name in post_vars:
    #             term.printLog( 'Field \'%s\' not in form' % db_field_name )
                continue

            db_value = post_vars[ 'org__' + db_field_name ]
            # term.printDebug( '>>> db_value[%s]: %s' %
            #                  ( db_field_name, repr( db_value ) ) )
            # term.printDebug( '>>> type: %s' %
            #                  ( repr( db_table[ fld ].type ) ) )
            if db_value == 'None' \
            and ( db_table[ fld ].type == 'integer'
                  or db_table[ fld ].type.startswith( 'reference ' ) ):
                db_value = None
            form_value = post_vars[ db_field_name ]
            # term.printDebug(
            #     '>>> (UPD) db_value[%s]: %s: %s; form_value: %s' %
            #     (db_field_name, repr( db_value ),
            #      db_table[ fld ].type, repr( form_value ) ) )
            if db_value is None and form_value == '':
                form_value = None
            if form_value is None:
                form_value = db_table[ fld ].default

            if db_table[ fld ].type == 'boolean':
                if form_value == 'on':
                    form_value = True
                else:
                    form_value = False
            elif form_value is not None \
            and form_value != '' \
            and ( db_table[ fld ].type == 'integer'
                  or db_table[ fld ].type.startswith( 'reference ' ) ):
                form_value = int( form_value )

            elif db_table[ fld ].type.startswith( 'decimal' ):
                form_value = parse_currency( form_value )
    #            term.printDebug(
    #                '>>> (UPD) vDb[%s]: %s; vForm: %s' %
    #                (db_field_name, repr( db_value ), repr( form_value )) )
            if get_all or str( db_value ) != str( form_value ):
    #             term.printDebug(
    #                 '>>> (UPD) vDb[%s]: %s; vForm: %s' %
    #                 (db_field_name, db_value, form_value) )
                upd[fld] = form_value
        except:
            term.printLog( 'field: %s; value: %s'
                           % ( repr( db_field_name ), repr( form_value ) ) )
            t, v, tb = sys.exc_info()
            traceback.print_exception( t, v, tb )
            raise

#    term.printLog( 'upd: ' + repr( upd ) )
    return upd

#------------------------------------------------------------------
def format_currency( value,
                     currency_mask=None,
                     decimals=2,
                     allow_nulls=False,
                     hide_zeros=False ):
    # term.printDebug( 'currency_mask: %s' % (repr( currency_mask )) )
    # term.printDebug( 'decimals (%s): %s' % (type( decimals ), repr( decimals )) )
    # term.printDebug( 'value (%s): %s' % (type( value ), str( value )),
    #                  print_trace=True )
    # if isinstance( value, basestring ):
    #     value = parse_currency( value )
    #     term.printDebug( 'value (%s): %s' % (type( value ), str( value )) )
    if isinstance( value, Decimal ):
        value = float( value )
    # term.printDebug( 'allow_nulls: %s' % (repr( allow_nulls )) )
    if not value and allow_nulls:
        value = 0.0
    if value == 0.0 and hide_zeros:
        return ''
    if not currency_mask:
        currency_mask = '%.*f ' + current.currency.symbol
    # term.printDebug( 'value (%s): %s' % (type( value ), str( value )) )
    f = currency_mask % ( int( decimals ), value )
    # term.printDebug( 'f (%s): %s' % (type( f ), str( f )) )
    return f


#------------------------------------------------------------------
def format_decimal( value, decimals=None, allow_nulls=False, hide_zeros=False ):
    if not value and allow_nulls:
        value = 0.0
#     term.printDebug( 'hide_zeros: %s' % hide_zeros )
    if not value and hide_zeros:
        return ''

    p = decimalPattern
    if decimals is not None:
        p = '%.' + str( decimals ) + 'f'
    f = p % ( value )
    return f


#------------------------------------------------------------------
@deprecated( 'use format_decimal( value, decimals=None, allow_nulls=False, hide_zeros=False )' )
def formatDecimal( value, decimals=None, allowNulls=False, hide_zeros=False ):
    return format_decimal( value, decimals=decimals, allow_nulls=allowNulls, hide_zeros=hide_zeros )


#------------------------------------------------------------------
def format_percentage( value, decimals=1, allow_nulls=False, hide_zeros=False ):
    if not value and allow_nulls:
        value = 0.0
    p = '%.' + str( decimals ) + 'f'
    f = p % ( value )
    return f + ' %'


#------------------------------------------------------------------
@deprecated( 'use format_percentage( value, decimals=1, allow_nulls=False, hide_zeros=False )' )
def formatPercentage( value, decimals=1, allowNulls=False, hide_zeros=False ):
    return format_percentage( value, decimals=decimals, allow_nulls=allowNulls, hide_zeros=hide_zeros )


#------------------------------------------------------------------
def format_date( value, mask=None, allow_nulls=False ):
    if not mask:
        mask = '%Y-%m-%d'
    if not value and allow_nulls:
        f = ''
    else:
        f = value.strftime( mask )
    return f

#------------------------------------------------------------------
@deprecated( 'use format_date( value, mask=None, allow_nulls=False )' )
def formatDate( value, mask=None, allowNulls=False ):
    return format_date( value, mask=mask, allow_nulls=allowNulls )


#------------------------------------------------------------------
def format_timestamp( value, mask=None, allow_nulls=False ):
    if not mask:
        mask = '%Y-%m-%d %H:%M:%S'
    if not value and allow_nulls:
        f = ''
    else:
        f = value.strftime( mask )
    return f


#------------------------------------------------------------------
@deprecated( 'use format_timestamp( value, mask=None, allow_nulls=False )' )
def formatTimestamp( value, mask=None, allowNulls=False ):
    return format_timestamp( value, mask=mask, allow_nulls=allowNulls )


#------------------------------------------------------------------
def format_time( value, mask=None, allow_nulls=False ):
    if not mask:
        mask = '%H:%M'
    if not value and allow_nulls:
        f = ''
    else:
        f = value.strftime( mask )
    return f


#------------------------------------------------------------------
@deprecated( 'use format_time( value, mask=None, allow_nulls=False )' )
def formatTime( value, mask=None, allowNulls=False ):
    return format_timestamp( value, mask=mask, allow_nulls=allowNulls )

#------------------------------------------------------------------
def format( colType,
            value,
            decimals=None,
            allowNulls=False,
            maxLength=None,
            mask=None ):

    return format_value( col_type=colType,
                         value=value,
                         decimals=decimals,
                         allow_nulls=allowNulls,
                         max_length=maxLength,
                         mask=mask )

#------------------------------------------------------------------
def format_value( col_type=KDT_CHAR,
                  value=None,
                  decimals=None,
                  allow_nulls=False,
                  max_length=None,
                  mask=None,
                  hide_zeros=False ):

    if col_type == KDT_DEC:
        return format_decimal( value, decimals or 0, allow_nulls, hide_zeros=hide_zeros )

    if col_type == KDT_MONEY:
        return format_currency( value, currency_mask=mask, decimals=decimals or 2, allow_nulls=allow_nulls, hide_zeros=hide_zeros )

    if col_type == KDT_PERCENT:
        return format_percentage( value, decimals or 1, allow_nulls, hide_zeros=hide_zeros )

    if col_type == KDT_BOOLEAN:
        if value:
            value = 'X'
        else:
            value = ''
    if value is None:
        value = ''

    elif col_type == KDT_DATE:
        return format_date( value, mask=mask, allow_nulls=allow_nulls )

    elif col_type == KDT_TIME:
        return format_time( value, mask=mask, allow_nulls=allow_nulls )

    elif col_type == KDT_TIMESTAMP:
        return format_timestamp( value, mask=mask, allow_nulls=allow_nulls )

    elif col_type == KDT_TIMESTAMP_PRETTY:
        T = current.T
        # term.printDebug( 'type: %s' % type( value ))
        return prettydate( value.replace( tzinfo=None), T )

    elif col_type == KDT_INT:
        return str( int( value ) )

    return str( value )

#------------------------------------------------------------------
def parse_currency( value, currency_symbol=None ):
    # term.printDebug( 'value (%s): %s' % (type( value ), str( value )) )
    if not currency_symbol:
        currency_symbol = current.currency.symbol
    if type( value ) == type( '' ):
        v = value.replace( currency_symbol, '' )
        v = v.replace( '\xe2\x82\xac', '' )
#    term.printLog( 'v: %s' % (v) )
    else:
        v = value
    return parse_decimal( v )

#------------------------------------------------------------------
def parse_percentage( value ):
    v = str( value ).split( ' ' )[0]
    if v.endswith( '%' ):
        v = v[:-1]
    return Decimal( v )

#------------------------------------------------------------------
@deprecated( 'use parse_percentage( value )' )
def parsePercentage( value ):
    return parse_percentage( value )


#------------------------------------------------------------------
def parse_decimal( value ):
    # term.printDebug( 'value (%s): %s' % (type( value ), str( value )) )
    if type( value ) == type( '' ):
        v = value.replace( ',', '.' )
        v = v.replace( ' ', '' )
#         term.printDebug( 'v: ' + repr( v ) )
        decimal_rule = re.compile( r'[^-?\d.]+' )
#        decimal_rule = re.compile( r'^-?[0-9]+$' )
        v = decimal_rule.sub( '', v )
    else:
#        term.printLog( 'type: ' + repr( type( value ) ) )
        v = value
#     term.printDebug( 'v: ' + repr( v ) )
    if not v:
        v = 0.0
    d = Decimal( v )
#     term.printDebug( 'd: ' + repr( d ) )
    return d


#------------------------------------------------------------------
@deprecated( 'use parse_decimal( value )' )
def parseDecimal( value ):
    return parse_decimal( value )


#------------------------------------------------------------------
def parse_date( value ):
    d = None
    if value:
        d = DT.strptime( value, '%Y-%m-%d' ).date()
    return d

#------------------------------------------------------------------
@deprecated( 'use parse_date( value )' )
def parseDate( value ):
    return parse_date( value )


#------------------------------------------------------------------
def parse_time( value, mask=None ):
    d = None
    if value:
        masks = []
        if mask:
            masks = [ mask ]
        else:
            masks = [ '%H:%M:%S.%f',
                      '%H:%M:%S',
                      '%H:%M' ]
        for mask in masks:
            try:
                d = DT.strptime( value, mask ).time()
                break
            except ValueError:
                pass
    return d


#------------------------------------------------------------------
@deprecated( 'use parse_time( value, mask=None )' )
def parseTime( value, mask=None ):
    return parse_time( value, mask=mask )


#------------------------------------------------------------------
def parse_timestamp( value, mask=None, allow_dates=True ):
    d = None
    if value:
        if mask:
            masks = [ mask ]
        else:
            masks = [ '%Y-%m-%d %H:%M:%S.%f',
                      '%Y-%m-%d %H:%M:%S',
                      '%Y-%m-%d %H:%M' ]
            if allow_dates:
                masks.append( '%Y-%m-%d' )
        for mask in masks:
            try:
                d = DT.strptime( value, mask )
                break
            except ValueError:
                pass
    return d


#------------------------------------------------------------------
@deprecated( 'use parse_timestamp( value, mask=None )' )
def parseTimestamp( value, mask=None ):
    return parse_timestamp( value, mask=mask )


#------------------------------------------------------------------
def parse_val( value, val_type, allow_nulls=False, mask=None ):
#    term.printLog( 'value: %s; type: %s; pyType: %s ' % (repr( value ), valType, type( value ) ) )
    objValue = None
    if value is not None:
        if isinstance( value, str ):
            if val_type == KDT_CHAR:
                objValue = value
            elif val_type == KDT_INT:
                if not value and allow_nulls:
                    value = '0'
                objValue = int( value )
            elif val_type == KDT_DEC:
                if not value and allow_nulls:
                    value = '0'
                objValue = Decimal( value )
            elif val_type == KDT_MONEY:
                if not value and allow_nulls:
                    value = '0'
                objValue = parse_currency( value )
            elif val_type == KDT_PERCENT:
                if not value and allow_nulls:
                    value = '0'
                objValue = parsePercentage( value )
            elif val_type == KDT_DATE:
                objValue = parseDate( value )
            elif val_type == KDT_TIMESTAMP:
                objValue = parseTimestamp( value, mask=mask )
            elif val_type in (KDT_SELECT_INT, KDT_SELECT_CHAR):
                if not value and allow_nulls:
                    value = '0'
                if val_type == KDT_SELECT_INT:
                    objValue = int( value )
                else:
                    objValue = value
            elif val_type == KDT_SELECT_CHAR:
                term.printLog(
                    'value: %s; type: %s; pyType: %s ' %
                    ( repr( value ), val_type, type( value ) ) )
                raise Exception( 'Unknown type: %s' % ( repr( val_type ) ) )
        else:
            if val_type == KDT_INT and isinstance( value, int ):
                objValue = value
            elif val_type == KDT_DEC and isinstance( value, Decimal ):
                objValue = value
            elif val_type == KDT_MONEY and isinstance( value, Decimal ):
#                term.printLog( 'value: %s; type: %s ' % (value, valType) )
                objValue = value
            elif val_type == KDT_PERCENT and isinstance( value, Decimal ):
                objValue = parsePercentage( value )
#    term.printLog( 'objValue: %s; type: %s ' % (objValue, valType) )
    return objValue

#------------------------------------------------------------------
@deprecated( 'use parse_val( value, val_type, allow_nulls=False, mask=None )' )
def parseVal( value, valType, allowNulls=False, mask=None ):
    return parse_val( value, val_type=valType, allow_nulls=allowNulls, mask=mask )



#------------------------------------------------------------------
@deprecated( ' use get_align( colType, styles=None )' )
def getAlignment( colType ):
    align = 'text-left'
    if colType in [KDT_INT, KDT_DEC, KDT_MONEY, KDT_PERCENT]:
        align = 'text-right'
    elif colType in [KDT_DATE, KDT_TIME, KDT_TIMESTAMP, KDT_TIMESTAMP_PRETTY ]:
        align = 'text-center'
    return align

#------------------------------------------------------------------
def get_align( col_type, styles=None ):
    if not styles:
        styles = [ 'text-left', 'text-center', 'text-right' ]
    if col_type == KDT_DATE or \
         col_type == KDT_TIME or \
         col_type == KDT_TIMESTAMP or \
         col_type == KDT_TIMESTAMP_PRETTY or \
         col_type == KDT_BOOLEAN:
        return styles[1]

    if col_type == KDT_INT or \
         col_type == KDT_DEC or \
         col_type == KDT_MONEY or \
         col_type == KDT_PERCENT:
        return styles[2]

    return styles[0]

#------------------------------------------------------------------
def getAlign( colType, styles ):
    # styles = [ left, center, right ]
    if colType == KDT_DATE or \
         colType == KDT_TIME or \
         colType == KDT_TIMESTAMP or \
         colType == KDT_TIMESTAMP_PRETTY or \
         colType == KDT_BOOLEAN:
        return styles[1]
    if colType == KDT_INT or \
         colType == KDT_DEC or \
         colType == KDT_MONEY or \
         colType == KDT_PERCENT:
        return styles[2]
    return styles[0]

#------------------------------------------------------------------
@deprecated( 'use get_slider_field( name, ... )' )
def getSliderField(
    name, id=None, idPrefix=None,
    value=None, minValue=0, maxValue=10, stepIncr=1,
    cssClass=None, readOnly=False,
    valueType=None ):
    return get_slider_field( name,
                             input_id=id,
                             id_prefix=idPrefix,
                             value=value,
                             min_value=minValue,
                             max_value=maxValue,
                             step_incr=stepIncr,
                             css_class=cssClass,
                             read_only=readOnly,
                             value_type=valueType )
    # span = SPAN()
    # select = SELECT( _name=name, _id=id, _style='display: none;' )
    # for i in range( minValue, maxValue + stepIncr, stepIncr ):
    #     if i == value:
    #         select.append( OPTION( '%d' % i, _value='%d' % i, _selected='selected' ) )
    #     else:
    #         select.append( OPTION( '%d' % i, _value='%d' % i ) )
    # span.append( select )
    # js = SCRIPT( '''jQuery(function() { jQuery( '#%(id)s' ).selectToUISlider(); } );''' % { 'id': id } )
    # span.append( js )
    # return span


#------------------------------------------------------------------
def get_slider_field( name,
                      input_id=None,
                      id_prefix=None,
                      value=None,
                      min_value=0,
                      min_value_label='',
                      max_value=10,
                      max_value_label='',
                      step_incr=1,
                      css_class=None,
                      read_only=False,
                      value_type=None ):
    if not input_id:
        if id_prefix:
            input_id = id_prefix + name
            if not name.startswith( id_prefix ):
                name = id_prefix + name
        else:
            input_id = name

    # term.printDebug( 'value: %s; min_value: %s; max_value: %s; step_incr: %s' %
    #                  ( repr( value ), repr( min_value ),
    #                    repr( max_value ), repr( step_incr ) ),
    #                  print_trace=True )
    w_div = DIV()
    inp_val = get_input_field( name=name,
                               value=value,
                               input_id=input_id,
                               hide=True )
    w_div.append( inp_val )

    if not value:
        value = min_value
    div = DIV()
    div_slider = DIV( _id=input_id + '_slider' )
    if min_value_label:
        div.append( TABLE( TR( TD( min_value_label, _class='text-left' ),
                               TD( max_value_label, _class='text-right' ) ),
                           _class='w100pct' ) )
    if css_class:
        div_slider[ '_class' ] = css_class
    js = '''
        jQuery( function() {
            jQuery( '#%(id)s' ).labeledslider(
                {
                    min: %(min)s,
                    max: %(max)s,
                    tickInterval: %(step)s,
                    step: %(step)s,
                    value: %(value)s,
                    change: function( event, ui ) {
                        $('#%(target_id)s').val( ui.value );
                    }
                } );
        } );
    ''' % { 'id': input_id + '_slider',
            'target_id': input_id,
            'value': value,
            'min': min_value,
            'max': max_value,
            'step': step_incr }
    div_slider.append( SCRIPT( js ) )
    div.append( div_slider )
    w_div.append( div )
    return w_div
    #
    # select = SELECT( _name=name, _id=id, _style='display: none;' )
    # for i in range( minValue, maxValue + stepIncr, stepIncr ):
    #     if i == value:
    #         select.append( OPTION( '%d' % i, _value='%d' % i, _selected='selected' ) )
    #     else:
    #         select.append( OPTION( '%d' % i, _value='%d' % i ) )
    # span.append( select )
    # js = SCRIPT( '''jQuery(function() { jQuery( '#%(id)s' ).selectToUISlider(); } );''' % { 'id': id } )
    # span.append( js )
    # return span


#------------------------------------------------------------------
def append_class( src_css, append_css ):
    if src_css:
        if not append_css in src_css:
            if src_css:
                src_css += ' '
            src_css += append_css
    else:
        src_css = append_css
    return src_css


#------------------------------------------------------------------
def get_selection_field( name,
                         input_id=None,
                         options=[],
                         selected=None,
                         on_change=None,
                         span_wrap=False,
                         css_class=None,
                         css_style=None,
                         use_bootstrap_select=None,
                         use_bootstrap_live_search=None,
                         width=None,
                         max_width=None ):
    '''

    Args:
        name:
        input_id:
        options:
        selected:
        on_change:
        span_wrap:
        css_class:
        css_style:
        use_bootstrap_select:
        use_bootstrap_live_search:
        max_width: attib string (200px, 50%, etc)

    Returns:

    '''
    if use_bootstrap_select is None:
        use_bootstrap_select = ui_factory.use_bootstrap_select()

    if use_bootstrap_select:
        css_class = append_class( css_class, 'selectpicker' )
        # if use_bootstrap_live_search is None:
        #     use_bootstrap_live_search = False
    sel = SELECT( _name=name,
                  _id=input_id,
                  _onchange=on_change,
                  _class=css_class,
                  _style=css_style )

    if use_bootstrap_select:
        sel[ '_data-none-selected-text' ] = BOOTSTRAP_NONE_SELECTED_TEXT
        if use_bootstrap_live_search is None and len( options ) > BOOTSTRAP_SELECTED_AUTO_THRESHOLD:
            use_bootstrap_live_search = True
        if use_bootstrap_live_search:
            sel[ '_data-live-search' ] = 'true'
    for o in options:
        op = OPTION( o[1], _value=o[0] )
        # op = OPTION( xmlescape( o[1] ), _value=xmlescape( o[0] ) )
        if len( o ) > 2 and o[2]:
            op[ '_class' ] = o[2]
        if len( o ) > 3 and o[3]:
            op[ '_style' ] = o[3]
        if str( o[0] ) == str( selected ):
            op[ '_selected' ] = 'selected'
        sel.append( op )
    if span_wrap or max_width or width:
        if max_width or width:
            if width:
                sel[ '_style' ] = 'width: %s;' % width
            else:
                sel[ '_style' ] = 'max-width: %s;' % max_width
        fld = SPAN( sel,
                    _id=(input_id or name) +'_span' )
        if max_width or width:
            # if width:
            #     fld[ '_style' ] = 'width: %s;' % width
            # else:
            #     fld[ '_style' ] = 'max-width: %s;' % max_width
            if span_wrap:
                fld[ '_class' ] = 'input_wrap'
            else:
                fld[ '_class' ] = 'input_wrap_inline'
    else:
        fld = sel

    return fld

#------------------------------------------------------------------
def get_input_field( name,
                     value=None,
                     input_type=None,
                     input_id=None,
                     id_prefix=None,
                     css_class=None,
                     css_style=None,
                     read_only=False,
                     on_blur=None,
                     on_change=None,
                     on_keyup=None,
                     requires=None,
                     placeholder=None,
                     value_type=None,
                     span_wrap=None,
                     autocomplete=True,
                     title=None,
                     decimals=2,
                     mask=None,
                     hide=False,
                     min_value=None,
                     max_value=None ):
    '''

    Args:
        name:
        value:
        input_type: 'text' | checkbox | ...
        input_id:
        id_prefix:
        css_class:
        css_style:
        read_only:
        on_blur:
        on_change:
        on_keyup:
        requires:
        placeholder:
        value_type: one of kommon.KDT_*
        span_wrap:
        autocomplete:
        title:
        decimals:
        mask:
        hide:

    Returns:

    '''
    if value_type == 'hidden':
        hide = True
    if hide:
        value_type = 'hidden'
        if not css_class:
            css_class = 'hidden'
        elif not 'hidden' in css_class:
            if len( css_class ) > 0:
                css_class += ' '
            css_class += 'hidden'
        span_wrap = False
    if not input_id:
        if id_prefix:
            input_id = id_prefix + name
            if not name.startswith( id_prefix ):
                name = id_prefix + name
        else:
            input_id = name
    if not input_type:
        if value_type == KDT_BOOLEAN:
            input_type = 'checkbox'
        else:
            input_type = 'text'
    # if span_wrap is None:
    #     span_wrap = (input_type != 'checkbox')

    data = dict( _name=name,
                 _id=input_id,
                 _type=input_type,
                 requires=requires )
    if not value and input_type == 'radio':
        data[ '_value' ] = False
    input = INPUT( **data )
    # term.printDebug( 'input: %s' % ( str( input ) ) )
    if value is not None:
        # term.printLog( 'value: %s' % ( repr( value ) ) )
        if input_type in [ 'checkbox', 'radio' ]:
            if value:
                input[ '_checked' ] = 'checked'
        else:
            input['_value'] = format_value( col_type=value_type,
                                            value=value,
                                            decimals=decimals,
                                            mask=mask )

    if min_value:
        input[ '_min' ] = min_value
    if max_value:
        input[ '_max' ] = max_value
    css = []
    if css_class:
        css = css_class.split( ' ' )
    if value_type == KDT_DATE and not 'date' in css:
        css.append( 'date' )
    elif value_type == KDT_TIMESTAMP and not 'datetime' in css:
        css.append( 'datetime' )
    elif value_type in [ KDT_INT, KDT_DEC, KDT_MONEY, KDT_PERCENT ] \
    and not 'text-right' in css:
        css.append( 'text-right double' )

    if css:
        input['_class'] = ' '.join( css )
    if css_style:
        input['_style'] = css_style
    if read_only:
        if input_type in [ 'checkbox', 'radio' ]:
            input['_disabled'] = 'disabled'
        else:
            input['_readonly'] = 'readonly'
    if on_change:
        if input_type in [ 'checkbox', 'radio' ]:
            input['_onclick'] = on_change
        else:
            input['_onchange'] = on_change
            input[ '_autocomplete' ] = 'off'
    if on_blur:
        input['_autocomplete'] = 'off'
        input['_onblur'] = on_blur
    if on_keyup:
        input['_autocomplete'] = 'off'
        input['_onkeyup'] = on_keyup
    if not autocomplete and input_type not in [ 'checkbox', 'radio' ]:
        input[ '_autocomplete' ] = 'off'
    if title:
        input[ '_title' ] = title
    if placeholder:
        input[ '_placeholder' ] = placeholder
    fld = input
    if span_wrap:
        fld = SPAN( input, _class='input_wrap' )
    # term.printDebug( 'fld: %s' % ( fld.xml() ) )

    return fld

#------------------------------------------------------------------
def get_checkbox( name,
                  value=None,
                  input_id=None,
                  id_prefix=None,
                  css_class=None,
                  css_style=None,
                  read_only=False,
                  on_blur=None,
                  on_change=None,
                  on_keyup=None,
                  span_wrap=None,
                  title=None,
                  hide=False ):
    return get_input_field( name,
                            value=value,
                            input_type='checkbox',
                            input_id=input_id,
                            id_prefix=id_prefix,
                            css_class=css_class,
                            css_style=css_style,
                            read_only=read_only,
                            on_blur=on_blur,
                            on_change=on_change,
                            on_keyup=on_keyup,
                            value_type=KDT_BOOLEAN,
                            span_wrap=span_wrap,
                            title=title,
                            hide=hide )

# #------------------------------------------------------------------
# @deprecated( 'use get_input_field( name, ... )' )
# def getInputField( name,
#                    value=None,
#                    inputType=None,
#                    id=None,
#                    idPrefix=None,
#                    cssClass=None,
#                    cssStyle=None,
#                    readOnly=False,
#                    onBlur=None,
#                    onChange=None,
#                    onKeyup=None,
#                    requires=None,
#                    valueType=None,
#                    span_wrap=True,
#                    autocomplete=True,
#                    title=None,
#                    decimals=2,
#                    mask=None ):
#     return get_input_field( name,
#                             value=value,
#                             input_type=inputType,
#                             input_id=id,
#                             id_prefix=idPrefix,
#                             css_class=cssClass,
#                             css_style=cssStyle,
#                             read_only=readOnly,
#                             on_blur=onBlur,
#                             on_change=onChange,
#                             on_keyup=onKeyup,
#                             requires=requires,
#                             value_type=valueType,
#                             span_wrap=span_wrap,
#                             autocomplete=autocomplete,
#                             title=title,
#                             decimals=decimals,
#                             mask=mask )
#
#------------------------------------------------------------------
def get_textarea( name,
                  value='',
                  input_id=None,
                  rows=None,
                  cols=80,
                  requires=None,
                  read_only=False,
                  on_blur=None,
                  css_class=None ):
    inp = TEXTAREA( _name=name,
                    value=value,
                    requires=requires,
                    _id=input_id )
    if rows:
        inp[ '_rows' ] = rows
    if cols:
        inp[ '_cols' ] = cols
    if read_only:
        inp[ '_readonly' ] = read_only
    if on_blur:
        inp[ '_onblur' ] = on_blur
    if css_class:
        inp[ '_class' ] = css_class
    return inp

#------------------------------------------------------------------
def getSubmitButton( title,
                     name,
                     value,
                     id=None,
                     cssClass=None,
                     onClick=None ):
    if not id:
        id = name
    input = INPUT(
        _name=name, _id=id, _type='button', _value=title )
    if cssClass:
        input['_class'] = cssClass
    if onClick:
        input['_onclick'] = onClick
    return input

#------------------------------------------------------------------
def get_button( bt_text,
                name='action',
                value=None,
                icon=None,
                tip=None,
                input_id=None,
                button_type='submit',
                css_class=None,
                css_style=None,
                on_click=None,
                bt_link=None,
                disabled=None,
                confirm_action=False ):
    T = current.T
    if icon:
        bt_icon = icon
        if isinstance( icon, basestring ):
            if not icon.startswith( '<' ):
                from m16e.ui import elements
                bt_icon = elements.get_bootstrap_icon( icon )
        bt_text = (bt_icon, ' ' + bt_text)
    if bt_link:
        bt = A( bt_text,
                _href=bt_link,
                _class=css_class )
    else:
        bt = BUTTON( bt_text,
                     _id=input_id,
                     _name=name,
                     _type=button_type,
                     _value=value )
    if css_class:
        bt['_class'] = css_class
    if css_style:
        bt['_style'] = css_style
    if on_click:
        bt['_onclick'] = on_click
    if tip:
        bt[ '_title' ] = tip
    if disabled:
        bt['_disabled'] = 'disabled'
    if confirm_action:
        bt[ '_onclick' ] = '''return alert( '%s' );''' % T( 'Are you sure?' )
    return bt

#------------------------------------------------------------------
def get_tab_panel_header_link( name, href ):
    a = A( name,
           _href=href,
           _role=TAB_ROLE )
    a[ '_data-toggle' ] = 'tab'
    return a


#------------------------------------------------------------------
def get_tab_panel_header_li( name, href, active=False ):
    a = get_tab_panel_header_link( name, href )
    li = LI( a )
    if active:
        li[ '_class' ] = 'active'
    return li


#------------------------------------------------------------------
class is_currency( object ):
    def __init__( self,
                  format='0.00',
                  error_message='must be a valid currency format (ex.: 1234.56 €, 1234.56)',
                  currency_mask=None ):
        self.format = format
        self.error_message = error_message
    def __call__( self, value ):
        try:
            value = parse_currency( value )
            return ( value, None )
        except:
            return ( value, self.error_message )
    def formatter( self, value ):
        return format_currency( value )

#------------------------------------------------------------------
class is_decimal( object ):
    def __init__( self, format='0.00', error_message='must be a valid currency format (ex.: 1234.56 €, 1234.56)' ):
        self.format = format
        self.error_message = error_message
        self.decimals = len( format.split( '.' )[1] )
    def __call__( self, value ):
        try:
            value = parseVal( value, KDT_DEC )
            return ( value, None )
        except:
            return ( value, self.error_message )
    def formatter( self, value ):
        return formatDecimal( value, self.decimals )

#------------------------------------------------------------------
class is_percentage( object ):
    def __init__( self, format='0.00', error_message='must be a valid currency format (ex.: 1234.56 €, 1234.56)' ):
        self.format = format
        self.error_message = error_message
        self.decimals = len( format.split( '.' )[1] )
    def __call__( self, value ):
        try:
            value = parsePercentage( value )
            return ( value, None )
        except:
            return ( value, self.error_message )
    def formatter( self, value ):
        return formatPercentage( value, self.decimals )


