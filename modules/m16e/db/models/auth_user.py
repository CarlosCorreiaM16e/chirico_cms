# -*- coding: utf-8 -*-
# this file is released under GPL Licence v.3
# author: carlos@memoriapersistente.pt
# Created on 26 de Mai de 2013

from m16e.db.database import DbBaseTable

#------------------------------------------------------------------
class AuthUserModel( DbBaseTable ):
    table_name = 'auth_user'
    
    #------------------------------------------------------------------
    def __init__( self, db ):
        super( AuthUserModel, self ).__init__( db )
        
    