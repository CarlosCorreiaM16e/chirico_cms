# -*- coding: utf-8 -*-

from gluon.globals import current


#----------------------------------------------------------------------
def get_zip_validator_widget( l10n=None ):
    if not l10n:
        l10n = current.app.l10n
    if l10n == 'pt_pt':
        from m16e.i18n.pt_pt.widgets.zip_validator import is_valid_zip
        return is_valid_zip()
    return None

#----------------------------------------------------------------------
# def get_zip_validator_widget( l10n=None ):
#     if not l10n:
#         l10n = current.app.l10n
#     location = '%s/widgets' % l10n
# #     mod_name = 'm16e.i18n.%s.widgets.zip_validator' % l10n
#     mod_name = '%s.widgets.zip_validator' % l10n
#     fp, pathname, description = imp.find_module( mod_name, [ location ] )
#     m = None
#     try:
#         m = imp.load_module( mod_name, fp, pathname, description )
#     except:
#         t, v, tb = sys.exc_info()
#         traceback.print_exception( t, v, tb )
#         raise
#     finally:
#         if fp:
#             fp.close()
#     return m

#----------------------------------------------------------------------
