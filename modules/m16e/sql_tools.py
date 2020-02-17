# -*- coding: utf-8 -*-


def spaces_to_wildcards( value, add_to_beginning=True, add_to_end=True ):
    '''
    Converts spaces to SQL wildcards (%)
    Args:
        value: value to convert
        add_to_beginning: add wildcard to beginning
        add_to_end: add wildcard to end

    Returns:
        converted value
    '''
    w_value = value.replace( ' ', '%%' )
    if add_to_beginning:
        w_value = '%%' + w_value
    if add_to_end:
        w_value = w_value + '%%'
    return w_value


