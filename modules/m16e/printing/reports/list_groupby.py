# coding=utf-8
from gluon.storage import Storage
from m16e import term
from m16e.kommon import storagize, DECIMAL_0


class ListGroupBy( object ):
    def __init__( self,
                  field_order=None, # (field_name, label)
                  groups_per_line=2,
                  totalizers=None,
                  font_size=None,
                  font_style=None,
                  totals_label='Totals' ):
        # self.groups = storagize( data )
        self.field_order = [ f[0] for f in field_order ]
        self.labels = Storage()
        for f in field_order:
            self.labels[ f[0] ] = f[1]
        self.current_group = None
        self.groups_per_line = groups_per_line
        self.font_size = font_size
        self.font_style = font_style
        self.totals_label = totals_label
        self.totalizers = Storage()
        if totalizers:
            for t in totalizers:
                self.totalizers[t] = DECIMAL_0


    def reset_totalizers( self ):
        if self.totalizers:
            for t in self.totalizers:
                self.totalizers[ t ] = DECIMAL_0


    def totalize_groups( self, row ):
        for f in self.totalizers:
            # term.printDebug( 'f: %s, totalizers(%s): %s; row(%s): %s' %
            #                  (repr( f ),
            #                   type( self.totalizers[f] ),
            #                   repr( self.totalizers[ f ] ),
            #                   type( row[f] ),
            #                   repr( row[f] )) )
            self.totalizers[f] += row[f]


    def set_current_group( self, row ):
        self.current_group = Storage()
        for f in self.field_order:
            self.current_group[f] = row[f]
        # term.printDebug( 'current_group: %s' % repr( self.current_group ), prompt_continue=True )


    def is_row_in_group( self, row ):
        for f in self.current_group:
            if self.current_group[f] != row[f]:
                return False
        return True

