# -*- coding: utf-8 -*-

from m16e import htmlcommon, term
from m16e.kommon import KDT_DEC, KDT_MONEY


#----------------------------------------------------------------------
def get_decimal_widget( field, value, decimals=2, allow_nulls=True, hide_zeros=False ):
    value = htmlcommon.format_decimal( value,
                                       decimals=decimals,
                                       allow_nulls=allow_nulls,
                                       hide_zeros=hide_zeros )
    inp = htmlcommon.get_input_field( field.name,
                                      value=value,
                                      input_id='%s_%s' % (field._tablename, field.name),
                                      value_type=KDT_DEC,
                                      css_class=field.type,
                                      requires=field.requires )
    return inp


#----------------------------------------------------------------------
def get_money_widget( field, value, currency_mask=None, decimals=2, allow_nulls=True, hide_zeros=False ):
    term.printDebug( 'value (%s): %s' % (type( value ), str( value )) )
    term.printDebug( 'decimals (%s): %s' % (type( decimals ), str( decimals )) )
    term.printDebug( 'allow_nulls: %s' % (repr( allow_nulls )),
                     print_trace=True )
    if  isinstance( value, basestring ):
        value = htmlcommon.parse_currency( value )
    term.printDebug( 'value (%s): %s' % (type( value ), str( value )) )
    # if value:
    #     value = htmlcommon.format_currency( value,
    #                                         currency_mask=currency_mask,
    #                                         decimals=decimals,
    #                                         allow_nulls=allow_nulls,
    #                                         hide_zeros=hide_zeros )
    inp = htmlcommon.get_input_field( field.name,
                                      value=value,
                                      input_id='%s_%s' % (field._tablename, field.name),
                                      value_type=KDT_MONEY,
                                      requires=field.requires,
                                      decimals=decimals )
    return inp


#----------------------------------------------------------------------
