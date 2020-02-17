# -*- coding: utf-8 -*-
from gluon import current


class ConditionExpression( object ):
    def __init__( self,
                  condition_field,
                  value=None,
                  l_par=0,
                  r_par=0,
                  test_op=None,
                  next_op=None,
                  db=None ):
        """

        Args:
            value:
            test_op:
            condition_field: ConditionField instance
            l_par: (
            r_par: )
            test_op: '=' | '!=' (for simple types, '>', '<', ...)
            next_op: 'AND' | 'OR'
            db:
        """
        if not db:
            db = current.db
        self.db = db
        self.condition_field = condition_field
        self.l_par= l_par
        self.r_par= r_par
        self.test_op = test_op
        self.next_op = next_op
        self.value = value



