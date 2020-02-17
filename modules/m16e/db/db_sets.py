# -*- coding: utf-8 -*-

from gluon import current

#----------------------------------------------------------------------
# shared_run.finished_status codes:

SR_OK = 0
SR_ERROR = 100

#----------------------------------------------------------------------
# doc_line types

K_DOC_LINE_TYPE_PROD = 0
K_DOC_LINE_TYPE_DOC = 1
K_DOC_LINE_TYPE_SEP = 2

K_DOC_LINE_TYPE_SET = { K_DOC_LINE_TYPE_PROD: current.T( 'Product line' ),
                        K_DOC_LINE_TYPE_DOC:  current.T( 'Document line' ),
                        K_DOC_LINE_TYPE_SEP:  current.T( 'Separator line' ) }

#----------------------------------------------------------------------
# ent_doc_type series

KEDT_SERIES_ALL = -1
KEDT_SERIES_MAIN = 0
KEDT_SERIES_AUX = 1
KEDT_SERIES_LEGACY = 90
KEDT_SERIES_EXTERNAL = 91

KEDT_SERIES_SET = { KEDT_SERIES_MAIN: current.T( 'Main series' ),
                    KEDT_SERIES_AUX: current.T( 'Auxiliary' ),
                    KEDT_SERIES_LEGACY: current.T( 'Legacy' ),
                    KEDT_SERIES_EXTERNAL: current.T( 'External app.' ) }

KEDT_SERIES_LIST = [ (KEDT_SERIES_MAIN, current.T( 'Main series' )),
                     (KEDT_SERIES_AUX, current.T( 'Auxiliary' )),
                     (KEDT_SERIES_LEGACY, current.T( 'Legacy' )),
                     (KEDT_SERIES_EXTERNAL, current.T( 'External app.' ))
                     ]

#----------------------------------------------------------------------
# test operators

TEST_OP_EQ = 1
TEST_OP_GT = 2
TEST_OP_LT = 3
TEST_OP_GTEQ = 4
TEST_OP_LTEQ = 5
TEST_OP_DIFF = 6

TEST_OP_LIST = [ ( TEST_OP_EQ, '=' ),
                 ( TEST_OP_GT, '>' ),
                 ( TEST_OP_LT, '<' ),
                 ( TEST_OP_GTEQ, '>=' ),
                 ( TEST_OP_LTEQ, '<=' ),
                 ( TEST_OP_DIFF, '!=' ),
                ]

def get_test_op( test_op_id ):
    for t in TEST_OP_LIST:
        if t[0] == test_op_id:
            return t[1]
    return ''

#------------------------------------------------------------------
TEST_BOOL_AND = 1
TEST_BOOL_OR = 2

TEST_BOOL_LIST = [ ( TEST_BOOL_AND, current.T( 'AND' ) ),
                   ( TEST_BOOL_OR, current.T( 'OR' ) ),
                  ]

def get_test_bool( test_bool_id ):
    if test_bool_id == TEST_BOOL_AND:
        return 'and'
    if test_bool_id == TEST_BOOL_OR:
        return 'or'
    return ''


#------------------------------------------------------------------
# doc_template's status

DT_STATUS_PENDING = 0
DT_STATUS_GENERATED = 1
DT_STATUS_MAIL_SENT = 2

DT_STATUS_SET = { DT_STATUS_PENDING: current.T( 'Pending' ),
                  DT_STATUS_GENERATED: current.T( 'Generated' ),
                  DT_STATUS_MAIL_SENT: current.T( 'Mail sent' ) }

#------------------------------------------------------------------
# L10N - PORTUGAL

L10N_PT_SAFT_TAX_COUNTRY_REGION_PT = 'PT'
L10N_PT_SAFT_TAX_COUNTRY_REGION_PT_MA = 'PT-MA'
L10N_PT_SAFT_TAX_COUNTRY_REGION_PT_AZ = 'PT-AC'

L10N_PT_SAFT_TAX_COUNTRY_REGION_SET = ( (L10N_PT_SAFT_TAX_COUNTRY_REGION_PT, 'PT (continente)'),
                                        (L10N_PT_SAFT_TAX_COUNTRY_REGION_PT_MA, 'PT-MA (Madeira)'),
                                        (L10N_PT_SAFT_TAX_COUNTRY_REGION_PT_AZ, 'PT-AC (Açores)')
                                        )

# SAF-T doc types
SAFT_DOC_TYPE_NOT_SIGNED = 0
SAFT_DOC_TYPE_SALES_INVOICES = 1
SAFT_DOC_TYPE_MOVEMENTS_OF_GOODS = 2
SAFT_DOC_TYPE_WORKING_DOCUMENTS = 3
SAFT_DOC_TYPE_PAYMENTS = 4

SAFT_DOC_TYPE_SET = ( (SAFT_DOC_TYPE_NOT_SIGNED, '(não assinado)'),
                      (SAFT_DOC_TYPE_SALES_INVOICES, 'SalesInvoices'),
                      (SAFT_DOC_TYPE_MOVEMENTS_OF_GOODS, 'MovementOfGoods'),
                      (SAFT_DOC_TYPE_WORKING_DOCUMENTS, 'WorkingDocuments' ),
                      (SAFT_DOC_TYPE_PAYMENTS, 'Payments' ),
                      )
