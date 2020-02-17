# -*- coding: utf-8 -*-
# this file is released under GPL Licence v.3
# author: carlos@memoriapersistente.pt

#------------------------------------------------------------------
def get_non_null_vars( d_vars={} ):
    nn_vars = {}
    for k in d_vars:
        v = d_vars[ k ]
        if v is not None:
            nn_vars[k] = d_vars[k]
    return nn_vars

#------------------------------------------------------------------
def get_non_empty_vars( d_vars={} ):
    ne_vars = {}
    for k in d_vars:
        v = d_vars[ k ]
        if v:
            ne_vars[k] = d_vars[k]
    return ne_vars

#------------------------------------------------------------------
