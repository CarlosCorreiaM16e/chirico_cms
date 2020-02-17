# -*- coding: utf-8 -*-
from gluon import current
from m16e import term
from m16e.kommon import KDT_CHAR
from m16e.ktfact import KTF_COLS, KTF_CELL_LINK, KTF_VARS_V
from m16e.views.gallery.choose_image import GalleryChooseImageView


class GalleryChooseSiteImageView( GalleryChooseImageView ):
    controller_name = 'gallery'
    function_name = 'choose_site_image'


    def __init__( self, db ):
        super( GalleryChooseSiteImageView, self ).__init__( db )

    # def parse_request_args( self ):
    #     super( GalleryChooseSiteImageView, self ).parse_request_args()
    #     request = current.request
    #
    #
    # def get_table_view_dict( self ):
    #     super( GalleryChooseSiteImageView, self ).get_table_view_dict()
    #     # self.tdef[ KTF_COLS ][ 'attached' ][ KTF_CELL_LINK ][ KTF_VARS_V ][ 'target' ] = self.target_field
    #     # term.printDebug( 'link: %s' % repr( self.tdef[ KTF_COLS ][ 'attached' ][ KTF_CELL_LINK ] ) )
    #     return self.tdef

