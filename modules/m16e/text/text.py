#! /usr/bin/python

#----------------------------------------------------------------------
def underscore2CamelCase( text ):
  a = text.split( '_' )
  cc = ''
  for w in a:
    cc += w.capitalize()
  return cc


def trim_field( value, max_len ):
    if not value:
        return ''
    if len( value ) > max_len:
        return value[ :max_len ]
    return value


def get_padded_str( s, pad_len, pad_left=True ):
    padded_str = '%'
    if pad_left:
        padded_str += '-'
    padded_str += '%d.%d' % (pad_len, pad_len)
    padded_str += 's'
    return padded_str % s


def list_strings( s_list, length=22, cols=4 ):
    menu = ''
    c = 1
    for s in s_list:
        menu += get_padded_str( s, length )
        if c % cols == 0:
            menu += '\n'
            c = 1
    return menu


if __name__ == "__main__":
  print underscore2CamelCase( 'asd_def_iut_iuh' );
