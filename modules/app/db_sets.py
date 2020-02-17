# -*- coding: utf-8 -*-

from gluon import current


# mail que status
MQ_STATUS_DEFAULT = ''
MQ_STATUS_ERROR = 'error'
MQ_STATUS_PENDING = 'pending'
MQ_STATUS_SENT = 'sent'
MQ_STATUS_SET = { MQ_STATUS_DEFAULT: current.T( 'queued' ),
                  MQ_STATUS_ERROR: current.T( 'error' ),
                  MQ_STATUS_PENDING: current.T( 'pending' ),
                  MQ_STATUS_SENT: current.T( 'sent' ),
                  }

# markup
MARKUP_SET_DISPLAY_TYPE = [ ('T', current.T( 'Table' )),
                            ('R', current.T( 'Row' )) ]

# MARKUP_SET
MARKUP_MARKMIN = 'M'
# MARKUP_MARKDOWN = 'D'
MARKUP_HTML = 'H'
MARKUP_NONE = 'N'

MARKUP_SET = [ (MARKUP_MARKMIN, 'Markmin'),
               (MARKUP_HTML, 'HTML'),
               # (MARKUP_MARKDOWN, 'Markdown'),
               (MARKUP_NONE, current.T( 'None' )) ]

# block container
BLOCK_CONTAINER_MAIN = 'M'
BLOCK_CONTAINER_ASIDE = 'A'
BLOCK_CONTAINER_SET = [ (BLOCK_CONTAINER_MAIN, current.T( 'Main' )),
                        (BLOCK_CONTAINER_ASIDE, current.T( 'Side' )) ]

# aside position
PANEL_LEFT = 'L'
PANEL_RIGHT = 'R'
PANEL_POSITION_SET = [ (PANEL_LEFT, current.T( 'Left' )),
                       (PANEL_RIGHT, current.T( 'Right')) ]

# image sizes
IMG_SIZE_ORIGINAL = 'original'
IMG_SIZE_MEDIUM = 'medium'
IMG_SIZE_SMALL = 'small'

# block display
# BLOCK_DISPLAY_BODY = 'B'
# BLOCK_DISPLAY_SUMMARY = 'S'
# BLOCK_DISPLAY_DESCRIPTION = 'D'
# BLOCK_DISPLAY_SET = [ (BLOCK_DISPLAY_BODY, current.T( 'Body' )),
#                       (BLOCK_DISPLAY_SUMMARY, current.T( 'Summary' )),
#                       (BLOCK_DISPLAY_DESCRIPTION, current.T( 'Description' )),
#                       ]

# visibility
VIS_TYPE_NONE = 0
VIS_TYPE_SHOW = 1
VIS_TYPE_HIDE = 2
VIS_TYPE_SET = { VIS_TYPE_NONE: '',
                 VIS_TYPE_SHOW: current.T( 'Show' ),
                 VIS_TYPE_HIDE: current.T( 'Hide' ) }

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

# test operators

TEST_OP_EQ = 1
TEST_OP_GT = 2
TEST_OP_LT = 3
TEST_OP_GTEQ = 4
TEST_OP_LTEQ = 5
TEST_OP_DIFF = 6

TEST_OP_LIST = [ ( TEST_OP_EQ, '=' ),
                 # ( TEST_OP_GT, '>' ),
                 # ( TEST_OP_LT, '<' ),
                 # ( TEST_OP_GTEQ, '>=' ),
                 # ( TEST_OP_LTEQ, '<=' ),
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


#----------------------------------------------------------------------
# fixed_position in lists

FIXED_HEADER = -1
FIXED_NONE = 0
FIXED_FOOTER = 1

FIXED_TYPE_SET = [ (FIXED_HEADER, current.T( 'Header' )),
                   (FIXED_NONE, current.T( 'Random' )),
                   (FIXED_FOOTER, current.T( 'Footer' )),
                   ]

# doc_template's status

DT_STATUS_PENDING = 0
DT_STATUS_GENERATED = 1
DT_STATUS_MAIL_SENT = 2

DT_STATUS_SET = { DT_STATUS_PENDING: current.T( 'Pending' ),
                  DT_STATUS_GENERATED: current.T( 'Generated' ),
                  DT_STATUS_MAIL_SENT: current.T( 'Mail sent' ) }

VOTE_SET = [ (1, current.T( 'Up' )),
             (-1, current.T( 'Down' )) ]

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

