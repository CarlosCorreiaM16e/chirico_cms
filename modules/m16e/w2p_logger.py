'''
Created on 02/06/2014

@author: carlos
'''
import logging
import os

from gluon.globals import current

#------------------------------------------------------------------
def get_logger():
    '''
    from
    web2py[:] - http://www.web2pyslices.com/slice/show/1416/logging
    '''
    request = current.request
    log_name = 'web2py.app.' + request.application
    logger = logging.getLogger( log_name )
    if len( logger.handlers ) == 0:
#         formatter = '%(asctime)s %(levelname)s %(process)s %(thread)s %(funcName)s():%(lineno)d %(message)s'
        formatter = '%(asctime)s %(levelname)s %(funcName)s():%(lineno)d %(message)s'
        handler = logging.handlers.RotatingFileHandler( os.path.join(request.folder,'private/app.log'),
                                                        maxBytes=1024*1024*16,
                                                        backupCount=2 )
        handler.setFormatter( logging.Formatter( formatter, 
                                                 datefmt='%Y-%m-%d %H:%M' ) )
        handler.setLevel(logging.DEBUG)
        
        logger.addHandler(handler)
        logger.setLevel(logging.DEBUG)

#         # Test entry:
#         logger.debug( log_name + ' logger created')
#     else:
#         # Test entry:
#         logger.debug( log_name + ' already exists')

    return logger
    
        