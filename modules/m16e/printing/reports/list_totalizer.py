# coding=utf-8
from gluon.storage import Storage
from m16e import term
from m16e.kommon import DECIMAL_0


class ListTotalizer:
    def __init__( self, cols ):
        self.cols = cols
        self.totalizers = Storage( { c: DECIMAL_0 for c in self.cols } )
        # self.reset_totalizers()
        # term.printDebug( 'cols: %s\ntotalizers: %s' % (repr( cols), repr( self.totalizers ) ) )
        # self.reset_totalizers()


    # def reset_totalizers( self ):
    #     self.totalizers = Storage( header={ c: DECIMAL_0 for c in self.cols },
    #                                footer={ c: DECIMAL_0 for c in self.cols } )


    # def totalize_row( self, row ):
    #     for c in self.cols:
    #         self.totalizers.footer[ c ] += row[ c ]


    def totalize_rows( self,
                       row_no,
                       row_list,
                       include_last=True ):
        self.totalizers = Storage( { c: DECIMAL_0 for c in self.cols } )
        term.printDebug( 'row_no: %d; include_last: %s' % (row_no, str( include_last)) )
        if row_no > 0:
            for idx, row in enumerate( row_list ):
                # if not include_last and idx >= row_no - 1:
                #     break
                for c in self.cols:
                    self.totalizers[ c ] +=  row[ c ]
                if idx >= row_no - 1:
                    break
        term.printDebug( 'cols: %s\ntotalizers: %s' % (repr( self.cols ), repr( self.totalizers ) ) )
        return self.totalizers


    # def totalize_header( self, first_row ):
    #     self.reset_totalizers()
    #     for idx, row in enumerate( self.data ):
    #         if idx == first_row:
    #             break
    #         for c in self.cols:
    #             self.totalizers.header[ c ] +=  row[ c ]
    #     term.printDebug( 'cols: %s\ntotalizers: %s' % (repr( self.cols ), repr( self.totalizers ) ) )
    #     return self.totalizers.header
    #
    #
    # def totalize_footer( self, last_row ):
    #     self.reset_totalizers()
    #     for idx, row in enumerate( self.data ):
    #         if idx == last_row:
    #             break
    #         for c in self.cols:
    #             self.totalizers.footer[ c ] += row[ c ]
    #     term.printDebug( 'cols: %s\ntotalizers: %s' % (repr( self.cols ), repr( self.totalizers ) ) )
    #     return self.totalizers.footer
    #
    #
