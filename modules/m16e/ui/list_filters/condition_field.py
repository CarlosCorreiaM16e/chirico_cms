# -*- coding: utf-8 -*-
from gluon import current
from m16e.kommon import KDT_CHAR


class ConditionField( object ):
    def __init__( self,
                  fld_name,
                  fld_type=KDT_CHAR,
                  fld_options=None,
                  db=None ):
        """

        Args:
            fld_name: field name
            fld_type: field type
            fld_options: field options (for selects), format [(id, label)]
            db:
        """
        if not db:
            db = current.db
        self.db = db
        self.fld_name = fld_name
        self.fld_type= fld_type
        self.fld_options = fld_options



