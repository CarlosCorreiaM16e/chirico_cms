# -*- coding: utf-8 -*-
from gluon.storage import Storage
from m16e import term
from m16e.db.database import table_exists, index_exists, column_exists, constraint_exists, sequence_exists, \
    fetch_record_by_id

if 0:
    import gluon
    import gluon.languages.translator as T

    global auth; auth = gluon.tools.Auth()
    global cache; cache = gluon.cache.Cache()
    global crud; crud = gluon.tools.Crud()
    global db; db = gluon.sql.DAL()
    global request; request = gluon.globals.Request()
    global response; response = gluon.globals.Response()
    global service; service = gluon.tools.Service()
    global session; session = gluon.globals.Session()


def upd_request_priority():
    if not table_exists( 'request_priority' ):
        sql = '''
            CREATE TABLE request_priority (
                id serial primary key,
                priority_name character varying(128) NOT NULL,
                preferred_order integer DEFAULT 0 NOT NULL
                );
                '''
        db.executesql( sql )
        data = ( ('Pode esperar', 0),
                 ('Assim que possível', 30),
                 ('Importante', 60),
                 ('Urgente', 80),
                 ('Dramático', 100),
                 )
        sql = '''insert into request_priority( priority_name, preferred_order ) values( '%s', %d )'''
        for d in data:
            db.executesql( sql % d )

_tmp_data = Storage()

def upd_uom_type():
    if not table_exists( 'uom_type' ):
        global _tmp_data
        sql = '''
            CREATE TABLE uom_type (
                id serial primary key,
                name character varying(64) not null unique,
                mnemonic varchar(16) not null unique,
                is_date boolean not null default false,
                is_time boolean not null default false,
                is_weight boolean not null default false,
                is_length boolean not null default false,
                is_volume boolean not null default false
            );
            '''
        db.executesql( sql )
        data = ( ('Unidade', 'unit', 'false', 'false', 'false', 'false', 'false'),
                 ('Data', 'date', 'true', 'false', 'false', 'false', 'false'),
                 ('Hora', 'time', 'false', 'true', 'false', 'false', 'false'),
                 ('Peso', 'weight', 'false', 'false', 'true', 'false', 'false'),
                 ('Comprimento', 'length', 'false', 'false', 'false', 'true', 'false'),
                 ('Volume', 'volume', 'false', 'false', 'false', 'false', 'true') )
        sql = '''
            insert into uom_type (name, mnemonic, is_date, is_time, is_weight, is_length, is_volume)
            values( '%s', '%s', %s, %s, %s, %s, %s ) returning id
        '''
        _tmp_data.uom_type = Storage()
        for d in data:
            _tmp_data.uom_type[ d[1] ] = db.executesql( sql % d )[0][0]


def upd_uom():
    if not table_exists( 'uom' ):
        global _tmp_data
        sql = '''
            CREATE TABLE uom (
                id serial primary key,
                name character varying(64) not null unique,
                mnemonic character varying(64) not null unique,
                uom_type_id integer not null,
                preferred_order integer DEFAULT 0 NOT NULL
            );
            '''
        db.executesql( sql )
        data = (('Unidade', 'unit', _tmp_data.uom_type.unit, 0),
                ('Dia', 'day', _tmp_data.uom_type.date, 12),
                ('Mês', 'month', _tmp_data.uom_type.date, 13),
                ('Ano', 'year', _tmp_data.uom_type.date, 14),
                ('Hora', 'hour', _tmp_data.uom_type.time, 10),
                ('Minuto', 'minute', _tmp_data.uom_type.time, 11) )
        sql = '''
            insert into uom (name, mnemonic, uom_type_id, preferred_order)
            values( '%s', '%s', %d, %d ) returning id
        '''
        _tmp_data.uom = Storage()
        for d in data:
            _tmp_data.uom[ d[ 1 ] ] = db.executesql( sql % d )[0][0]
    if not constraint_exists( 'uom_2_uom_type' ):
        sql = '''
            alter table uom
                add constraint uom_2_uom_type
                foreign key ( uom_type_id )
                references uom_type ( id )
        '''
        db.executesql( sql )


def upd_period():
    if not table_exists( 'period' ):
        global _tmp_data
        sql = '''
            CREATE TABLE period (
                id serial primary key,
                uom_id integer NOT NULL,
                units integer NOT NULL,
                name character varying(128) NOT NULL,
                preferred_order integer DEFAULT 0 NOT NULL
            );
            '''
        db.executesql( sql )
        data = ( (_tmp_data.uom.month, 1, 'Mês', 5),
                 (_tmp_data.uom.month, 3, 'Trimestre', 6),
                 (_tmp_data.uom.month, 6, 'Semestre', 7),
                 (_tmp_data.uom.year, 1, 'Ano', 10) )
        sql = '''
            insert into period (uom_id, units, name, preferred_order)
            values( %d, %d, '%s', %d ) 
        '''
        for d in data:
            db.executesql( sql % d )
    if not constraint_exists( 'period_2_uom' ):
        sql = '''
            alter table period
                add constraint period_2_uom
                foreign key ( uom_id )
                references uom ( id )
        '''
        db.executesql( sql )


def upd_request_status():
    if not table_exists( 'request_status' ):
        sql = '''
            CREATE TABLE request_status (
                id serial primary key,
                request_status_name character varying(512) NOT NULL,
                tags character varying(512),
                is_closed boolean DEFAULT false NOT NULL,
                preferred_order integer DEFAULT 0 NOT NULL
            );
            '''
        db.executesql( sql )
        data = ( ('Novo', 'new', 'f', 1),
                 ('Em Análise', 'analyzing', 'f', 2),
                 ('Confirmado', 'confirmed', 'f', 4),
                 ('Reaberto', 'reopened', 'f', 90),
                 ('Inválido', 'invalid', 't', 98),
                 ('Sem solução', 'no-solution', 't', 99),
                 ('Resolvido', 'solved', 't', 100),
                 )
        sql = '''insert into request_status( request_status_name, tags, is_closed, preferred_order ) values( '%s', '%s', '%s', %d )'''
        for d in data:
            db.executesql( sql % d )


def upd_request_type():
    if not table_exists( 'request_type' ):
        sql = '''
            CREATE TABLE request_type (
                id serial primary key,
                request_type_name character varying(512) NOT NULL,
                tags character varying(512),
                preferred_order integer DEFAULT 0 NOT NULL
            );
            '''
        db.executesql( sql )
        data = ( ('Erro', 'error', 1),
                 ('Dúvida', 'doubt', 2),
                 ('Sugestão', 'suggestion', 3),
                 ('Pedido', 'request', 4),
                 )
        sql = '''insert into request_type( request_type_name, tags, preferred_order ) values( '%s', '%s', %d )'''
        for d in data:
            db.executesql( sql % d )


def upd_support_request():
    if not table_exists( 'support_request' ):
        sql = '''
            CREATE TABLE support_request (
                id serial primary key,
                comm_time timestamp without time zone default CURRENT_TIMESTAMP NOT NULL,
                short_description character varying(512) NOT NULL,
                request_status_id integer DEFAULT 1 NOT NULL,
                request_type_id integer DEFAULT 1 NOT NULL,
                closed_time timestamp without time zone,
                priority_id integer DEFAULT 1 NOT NULL,
                assigned_to integer,
                private_request boolean DEFAULT false NOT NULL,
                is_waiting_reply boolean DEFAULT false NOT NULL,
                auth_user_id integer,
                ticket character varying(512)
            );
            '''
        db.executesql( sql )
    db.executesql( 'alter table support_request alter column comm_time set default CURRENT_TIMESTAMP')
    if not constraint_exists( 'support_request_2_request_priority', db=db ):
        sql = '''
            alter table support_request
                add constraint support_request_2_request_priority
                foreign key ( priority_id )
                references request_priority ( id )
        '''
        db.executesql( sql )
    if not constraint_exists( 'support_request_assigned_to_2_auth_user', db=db ):
        sql = '''
            alter table support_request
                add constraint support_request_assigned_to_2_auth_user
                foreign key ( assigned_to )
                references auth_user ( id )
        '''
        db.executesql( sql )
    if not constraint_exists( 'support_request_2_auth_user', db=db ):
        sql = '''
            alter table support_request
                add constraint support_request_2_auth_user
                foreign key ( auth_user_id )
                references auth_user ( id )
        '''
        db.executesql( sql )
    if not constraint_exists( 'support_request_2_request_status', db=db ):
        sql = '''
            alter table support_request
                add constraint support_request_2_request_status
                foreign key ( request_status_id )
                references request_status ( id )
        '''
        db.executesql( sql )
    if not constraint_exists( 'support_request_2_request_type', db=db ):
        sql = '''
            alter table support_request
                add constraint support_request_2_request_type
                foreign key ( request_type_id )
                references request_type ( id )
        '''
        db.executesql( sql )


def upd_request_dup():
    if not table_exists( 'request_dup' ):
        sql = '''
            CREATE TABLE request_dup (
                id serial primary key,
                request_id integer NOT NULL,
                dup_request_id integer NOT NULL
            );
            '''
        db.executesql( sql )
    if not constraint_exists( 'request_dup_2_support_request', db=db ):
        sql = '''
            alter table request_dup
                add constraint request_dup_2_support_request
                foreign key ( request_id )
                references support_request ( id )
        '''
        db.executesql( sql )
    if not constraint_exists( 'request_dup_dup_2_support_request', db=db ):
        sql = '''
            alter table request_dup
                add constraint request_dup_dup_2_support_request
                foreign key ( dup_request_id )
                references support_request ( id )
        '''
        db.executesql( sql )


def upd_request_msg():
    if not table_exists( 'request_msg' ):
        sql = '''
            CREATE TABLE request_msg (
                id serial primary key,
                request_id integer,
                parent_request_msg_id integer,
                msg_title character varying(512),
                msg_text character varying NOT NULL,
                msg_ts timestamp without time zone NOT NULL,
                user_id integer,
                time_consumed integer DEFAULT 0 NOT NULL,
                time_consumed_period_id integer DEFAULT 1 NOT NULL,
                private_msg boolean DEFAULT false
            );
            '''
        db.executesql( sql )
    if not constraint_exists( 'request_msg_2_support_request', db=db ):
        sql = '''
            alter table request_msg
                add constraint request_msg_2_support_request
                foreign key ( request_id )
                references support_request ( id )
        '''
        db.executesql( sql )
    if not constraint_exists( 'request_msg_2_auth_user', db=db ):
        sql = '''
            alter table request_msg
                add constraint request_msg_2_auth_user
                foreign key ( user_id )
                references auth_user ( id )
        '''
        db.executesql( sql )
    if not constraint_exists( 'request_msg_2_period', db=db ):
        sql = '''
            alter table request_msg
                add constraint request_msg_2_period
                foreign key ( time_consumed_period_id )
                references period ( id )
        '''
        db.executesql( sql )


def upd_request_subscribers():
    if not table_exists( 'request_subscribers' ):
        sql = '''
            CREATE TABLE request_subscribers (
                id serial primary key,
                request_id integer NOT NULL,
                user_id integer NOT NULL
            );
            
            '''
        db.executesql( sql )
    if not index_exists( 'request_subscribers', 'request_subscribers_req_user_ukey' ):
        sql = '''
            create unique index request_subscribers_req_user_ukey
                on request_subscribers ( request_id, user_id )
        '''
        db.executesql( sql )

    if not constraint_exists( 'request_subscribers_2_support_request', db=db ):
        sql = '''
            alter table request_subscribers
                add constraint request_subscribers_2_support_request
                foreign key ( request_id )
                references support_request ( id )
        '''
        db.executesql( sql )
    if not constraint_exists( 'request_msg_2_auth_user', db=db ):
        sql = '''
            alter table request_subscribers
                add constraint request_subscribers_2_auth_user
                foreign key ( user_id )
                references auth_user ( id )
        '''
        db.executesql( sql )


def upd_request_vote():
    if not table_exists( 'request_vote' ):
        sql = '''
            CREATE TABLE request_vote (
                id serial primary key,
                request_id integer NOT NULL,
                auth_user_id integer NOT NULL
            );
            '''
        db.executesql( sql )
    if not constraint_exists( 'request_vote_2_support_request', db=db ):
        sql = '''
            alter table request_vote
                add constraint request_vote_2_support_request
                foreign key ( request_id )
                references support_request ( id )
        '''
        db.executesql( sql )
    if not constraint_exists( 'request_vote_2_auth_user', db=db ):
        sql = '''
            alter table request_vote
                add constraint request_vote_2_auth_user
                foreign key ( auth_user_id )
                references auth_user ( id )
        '''
        db.executesql( sql )


def upd_request_msg_attach():
    if not table_exists( 'request_msg_attach' ):
        sql = '''
            CREATE TABLE request_msg_attach (
                id serial primary key,
                attach_id integer,
                request_msg_id integer
            );
        '''
        db.executesql( sql )
    if not constraint_exists( 'request_msg_attach_2_attach', db=db ):
        sql = '''
            alter table request_msg_attach
                add constraint request_msg_attach_2_attach
                foreign key ( attach_id )
                references attach ( id )
        '''
        db.executesql( sql )
    if not constraint_exists( 'request_msg_attach_2_request_msg', db=db ):
        sql = '''
            alter table request_msg_attach
                add constraint request_msg_attach_2_request_msg
                foreign key ( request_msg_id )
                references request_msg ( id )
        '''
        db.executesql( sql )


def upd_thread():
    if not table_exists( 'thread' ):
        sql = '''
            CREATE TABLE thread (
                id serial primary key,
                created_on timestamp without time zone NOT NULL,
                created_by integer NOT NULL,
                thread_title character varying(512) NOT NULL,
                thread_msg character varying(65535),
                thread_status_id integer DEFAULT 1 NOT NULL,
                thread_type_id integer DEFAULT 1 NOT NULL,
                closed_time timestamp without time zone
            );
            '''
        db.executesql( sql )
    if not column_exists( 'thread', 'markup' ):
        sql = "alter table thread add column markup char(1) default 'M'"
        db.executesql( sql )
    if not constraint_exists( 'thread_2_auth_user', db=db ):
        sql = '''
            alter table thread
                add constraint thread_2_auth_user
                foreign key ( created_by )
                references auth_user ( id )
        '''
        db.executesql( sql )
    if not constraint_exists( 'thread_2_thread_status', db=db ):
        sql = '''
            alter table thread
                add constraint thread_2_thread_status
                foreign key ( thread_status_id )
                references thread_status ( id )
        '''
        db.executesql( sql )
    if not constraint_exists( 'thread_2_thread_type', db=db ):
        sql = '''
            alter table thread
                add constraint thread_2_thread_type
                foreign key ( thread_type_id )
                references thread_type ( id )
        '''
        db.executesql( sql )


def upd_thread_visibility():
    if not table_exists( 'thread_visibility' ):
        sql = '''
            CREATE TABLE thread_visibility (
                id serial primary key,
                thread_id integer NOT NULL,
                group_id integer NOT NULL
            );
            '''
        db.executesql( sql )
    if not constraint_exists( 'thread_visibility_2_auth_group', db=db ):
        sql = '''
            alter table thread_visibility
                add constraint thread_visibility_2_auth_group
                foreign key ( group_id )
                references auth_group ( id )
        '''
        db.executesql( sql )
    if not constraint_exists( 'thread_visibility_2_thread', db=db ):
        sql = '''
            alter table thread_visibility
                add constraint thread_visibility_2_thread
                foreign key ( thread_id )
                references thread ( id )
        '''
        db.executesql( sql )


def upd_thread_status():
    if not table_exists( 'thread_status' ):
        sql = '''
            CREATE TABLE thread_status (
                id serial primary key,
                thread_status_name character varying(512) NOT NULL,
                meta_name character varying(512),
                is_closed boolean DEFAULT false NOT NULL,
                preferred_order integer DEFAULT 0 NOT NULL
            );
            '''
        db.executesql( sql )
        data = ( ('Aberto', 'open', 'f', 1),
                 ('Suspenso', 'suspended', 'f', 2),
                 ('Fechado', 'closed', 't', 100),
                 )
        sql = '''insert into thread_status( thread_status_name, meta_name, is_closed, preferred_order ) values( '%s', '%s', '%s', %d )'''
        for d in data:
            db.executesql( sql % d )


def upd_thread_type():
    if not table_exists( 'thread_type' ):
        sql = '''
            CREATE TABLE thread_type (
                id serial primary key,
                thread_type_name character varying(512) NOT NULL,
                meta_name character varying(512),
                preferred_order integer DEFAULT 0 NOT NULL
            );
            '''
        db.executesql( sql )
        data = ( ('Discussão aberta', 'open-discussion', 1),
                 ('Discussão restrita', 'restricted', 4),
                 )
        sql = '''insert into thread_type( thread_type_name, meta_name, preferred_order ) values( '%s', '%s', %d )'''
        for d in data:
            db.executesql( sql % d )


def upd_thread_msg():
    if not table_exists( 'thread_msg' ):
        sql = '''
            CREATE TABLE thread_msg (
                id serial primary key,
                thread_id integer NOT NULL,
                parent_thread_msg_id integer,
                auth_user_id integer NOT NULL,
                msg_text character varying NOT NULL,
                msg_ts timestamp without time zone NOT NULL
            );
            '''
        db.executesql( sql )
    if not column_exists( 'thread_msg', 'markup' ):
        sql = "alter table thread_msg add column markup char(1) default 'M'"
        db.executesql( sql )
    if not constraint_exists( 'thread_msg_2_thread', db=db ):
        sql = '''
            alter table thread_msg
                add constraint thread_msg_2_thread
                foreign key ( thread_id )
                references thread ( id )
        '''
        db.executesql( sql )
    if not constraint_exists( 'thread_msg_2_auth_user', db=db ):
        sql = '''
            alter table thread_msg
                add constraint thread_msg_2_auth_user
                foreign key ( auth_user_id )
                references auth_user ( id )
        '''
        db.executesql( sql )


def upd_thread_subscriber():
    if not table_exists( 'thread_subscriber' ):
        sql = '''
            CREATE TABLE thread_subscriber (
                id serial primary key,
                thread_id integer NOT NULL,
                auth_user_id integer NOT NULL
            );

            '''
        db.executesql( sql )
    if not index_exists( 'thread_subscriber', 'thread_subscriber_user_thread_msg_ukey' ):
        sql = '''
            create unique index thread_subscriber_user_thread_msg_ukey
                on thread_subscriber ( thread_id, auth_user_id )
        '''
        db.executesql( sql )
    if not constraint_exists( 'thread_subscriber_2_thread', db=db ):
        sql = '''
            alter table thread_subscriber
                add constraint thread_subscriber_2_thread
                foreign key ( thread_id )
                references thread ( id )
        '''
        db.executesql( sql )
    if not constraint_exists( 'thread_msg_2_auth_user', db=db ):
        sql = '''
            alter table thread_subscriber
                add constraint thread_subscriber_2_auth_user
                foreign key ( user_id )
                references auth_user ( id )
        '''
        db.executesql( sql )
    if not column_exists( 'thread_subscriber', 'unsubscribed' ):
        sql = 'alter table thread_subscriber add column unsubscribed timestamp without time zone'
        db.executesql( sql )


def upd_thread_vote():
    if table_exists( 'thread_vote' ):
        db.executesql( 'drop table thread_vote' )
    if not table_exists( 'thread_vote' ):
        sql = '''
            CREATE TABLE thread_vote (
                id serial primary key,
                thread_id integer NOT NULL,
                thread_msg_id integer,
                auth_user_id integer NOT NULL,
                vote_ts timestamp without time zone NOT NULL,
                vote integer not null check ( vote = 1 or vote = -1)
            );
            '''
        db.executesql( sql )
    if not index_exists( 'thread_vote', 'thread_vote_user_thread_msg_ukey' ):
        sql = '''
            create unique index thread_vote_user_thread_msg_ukey
                on thread_vote ( thread_msg_id, auth_user_id )
                where thread_msg_id is not null
        '''
        db.executesql( sql )
    if not constraint_exists( 'thread_vote_2_thread', db=db ):
        sql = '''
            alter table thread_vote
                add constraint thread_vote_2_thread
                foreign key ( thread_id )
                references thread ( id )
        '''
        db.executesql( sql )
    if not constraint_exists( 'thread_vote_2_thread_msg', db=db ):
        sql = '''
            alter table thread_vote
                add constraint thread_vote_2_thread_msg
                foreign key ( thread_msg_id )
                references thread_msg ( id )
        '''
        db.executesql( sql )
    if not constraint_exists( 'thread_vote_2_auth_user', db=db ):
        sql = '''
            alter table thread_vote
                add constraint thread_vote_2_auth_user
                foreign key ( auth_user_id )
                references auth_user ( id )
        '''
        db.executesql( sql )


def upd_thread_attach():
    if not table_exists( 'thread_attach' ):
        sql = '''
            CREATE TABLE thread_attach (
                id serial primary key,
                attach_id integer,
                thread_id integer
            );
        '''
        db.executesql( sql )
    if not constraint_exists( 'thread_attach_2_attach', db=db ):
        sql = '''
            alter table thread_attach
                add constraint thread_attach_2_attach
                foreign key ( attach_id )
                references attach ( id )
        '''
        db.executesql( sql )
    if not constraint_exists( 'thread_attach_2_thread', db=db ):
        sql = '''
            alter table thread_attach
                add constraint thread_attach_2_thread
                foreign key ( thread_id )
                references thread ( id )
        '''
        db.executesql( sql )


def upd_thread_msg_attach():
    if not table_exists( 'thread_msg_attach' ):
        sql = '''
            CREATE TABLE thread_msg_attach (
                id serial primary key,
                attach_id integer,
                thread_msg_id integer
            );
        '''
        db.executesql( sql )
    if not constraint_exists( 'thread_msg_attach_2_attach', db=db ):
        sql = '''
            alter table thread_msg_attach
                add constraint thread_msg_attach_2_attach
                foreign key ( attach_id )
                references attach ( id )
        '''
        db.executesql( sql )
    if not constraint_exists( 'thread_msg_attach_2_thread_msg', db=db ):
        sql = '''
            alter table thread_msg_attach
                add constraint thread_msg_attach_2_thread_msg
                foreign key ( thread_msg_id )
                references thread_msg ( id )
        '''
        db.executesql( sql )


def upd_auth_user():
    if not index_exists( 'auth_user', 'auth_user_name_ukey' ):
        sql = '''create unique index auth_user_name_ukey
                on auth_user ( first_name )
                '''
        db.executesql( sql )
    db.executesql( 'delete from auth_membership where group_id = 6' )
    db.executesql( 'delete from auth_group where id = 6' )


def upd_block():
    if column_exists( 'block', 'order_in_page' ):
        sql = 'alter table block drop column order_in_page'
        db.executesql( sql )
    needs_update = False
    if not column_exists( 'block', 'page_id' ):
        sql = 'alter table block add column page_id integer'
        db.executesql( sql )
        needs_update = True
    if not column_exists( 'block', 'container' ):
        sql_list = [ "alter table block add column container char(1) default 'M'",
                     "comment on column block.container is 'M: main; A: aside'" ]
        for sql in sql_list:
            db.executesql( sql )
    if not column_exists( 'block', 'blk_order' ):
        sql = 'alter table block add column blk_order integer default 1'
        db.executesql( sql )
    if not column_exists( 'block', 'colspan' ):
        sql = 'alter table block add column colspan integer default 1'
        db.executesql( sql )
    if not column_exists( 'block', 'rowspan' ):
        sql = 'alter table block add column rowspan integer default 1'
        db.executesql( sql )
    if needs_update:
        upd_sql = '''
            update block set
                page_id = %(page_id)s,
                container = '%(container)s',
                blk_order = %(blk_order)s,
                colspan = %(colspan)s,
                rowspan = %(rowspan)s
            where
                id = %(block_id)s
        '''
        sql = 'select * from page_block'
        rows = db.executesql( sql, as_dict=True )
        for row in rows:
            db.executesql( upd_sql % row )
    if not constraint_exists( 'block_2_page' ):
        sql = '''
            alter table block
                add constraint block_2_page
                foreign key ( page_id )
                references page ( id )
        '''
        db.executesql( sql )
    upd_page_block()
    for c in ('title', 'title_en' ):
        if column_exists( 'block', c ):
            sql = 'alter table block drop column %s' % c
            db.executesql( sql )
    if not index_exists( 'block', 'block_page_container_order_ukey' ):
        sql = '''
            create unique index block_page_container_order_ukey
                on block ( page_id, container, blk_order )
        '''
        db.executesql( sql )
    db.executesql( 'alter table block alter column last_modified_on type timestamp without time zone' )


def upd_block_log():
    if not table_exists( 'block_log' ):
        sql = '''
            CREATE TABLE block_log (
                id SERIAL PRIMARY KEY,
                block_id INTEGER NOT NULL,
                auth_user_id INTEGER NOT NULL,
                ts TIMESTAMP WITHOUT TIME ZONE NOT NULL,
                old_body VARCHAR NOT NULL,
                old_body_en VARCHAR NOT NULL,
                diff_body VARCHAR NOT NULL,
                diff_body_en VARCHAR NOT NULL 
                );
                '''
        db.executesql( sql )
    if not constraint_exists( 'block_log_2_block', db=db ):
        sql = '''
            alter table block_log
                add constraint block_log_2_block
                foreign key ( block_id )
                references block ( id )
        '''
        db.executesql( sql )
    if not constraint_exists( 'block_log_2_auth_user', db=db ):
        sql = '''
            alter table block_log
                add constraint block_log_2_auth_user
                foreign key ( auth_user_id )
                references auth_user ( id )
        '''
        db.executesql( sql )


def upd_page_block():
    if table_exists( 'page_block' ):
        sql = 'drop table page_block cascade'
        db.executesql( sql )


def upd_mail_recipient():
    db.executesql( 'update mail_recipient set status = \'pending\' where status is null' )
    db.executesql( 'alter table mail_recipient alter column status set default \'pending\'' )
    db.executesql( 'alter table mail_recipient alter column status set not null' )
    if not column_exists( 'mail_recipient', 'retries' ):
        sql_list = [ 'alter table mail_recipient add column retries integer default 0',
                     'update mail_recipient set retries = 0',
                     'alter table mail_recipient alter column retries set not null' ]
        for sql in sql_list:
            db.executesql( sql )


def upd_page():
    sql = 'alter table page alter column name set not null'
    db.executesql( sql )
    if not index_exists( 'page', 'page_name_ukey' ):
        sql = '''
            create unique index page_name_ukey
                on page ( name )
        '''
        db.executesql( sql )


def upd_user_message():
    if not constraint_exists( 'user_message_2_auth_user', db=db ):
        sql = '''
            alter table user_message
                add constraint user_message_2_auth_user
                foreign key ( notify_user_id )
                references auth_user ( id )
        '''
        db.executesql( sql )


def upd_page_counter():
    if not table_exists( 'page_counter' ):
        sql = '''
            CREATE TABLE page_counter (
                id SERIAL PRIMARY KEY,
                path_info CHARACTER VARYING(512) NOT NULL,
                year INTEGER NOT NULL,
                month INTEGER NOT NULL,
                day INTEGER NOT NULL,
                hour INTEGER NOT NULL,
                views INTEGER DEFAULT 1 NOT NULL
                );
                '''
        db.executesql( sql )
    if not index_exists( 'page_counter', 'page_counter_pymdh_ukey' ):
        sql = '''
            create unique index page_counter_pymdh_ukey
                on page_counter ( path_info, year, month, day, hour )
        '''
        db.executesql( sql )


def upd_page_log():
    if not table_exists( 'page_log' ):
        sql = '''
            CREATE TABLE page_log (
                id SERIAL PRIMARY KEY,
                path_info CHARACTER VARYING(512) NOT NULL,
                ts TIMESTAMP WITHOUT TIME ZONE NOT NULL,
                client_ip VARCHAR( 16 ),
                auth_user_id INTEGER,
                is_tablet boolean default false,
                is_mobile boolean default false,
                os_name character varying(64),
                browser_name character varying(64),
                browser_version character varying(64)
                );
                '''
        db.executesql( sql )
    sql = '''
        update page_log
        set path_info = substring( path_info, 1, 4 )
        where path_info like( '/www/%' )
    '''
    db.executesql( sql )
    sql = '''
        update page_log
        set path_info = '/'
        where path_info = '/www'
    '''
    db.executesql( sql )
    skip_list = [ '/auth_event_viewer',
                  '/defualt',
                  '/set_session_',
                  '/lang/',
                  '/default/bang/',
                  '/default/download',
                  '/default/set_session_anon/',
                  '/default/user/',
                  '/download/',
                  '/block/',
                  '/user_admin',
                  '/page/',
                  '/page_stats/',
                  '/cronjobs/',
                  '/default/error/'
                  ]
    sql1 = "delete from page_log where path_info like( '%s%%' )"
    sql2 = "delete from page_log where path_info = '%s'"
    for s in skip_list:
        db.executesql( sql1 % s )
        db.executesql( sql2 % s[ : -1 ] )
    sql = '''
        update page_log set path_info = '/' where path_info = '/default/index'
    '''
    db.executesql( sql )
    sql = "delete from page_log where ts < '2020-01-27'"
    db.executesql( sql )
    if not column_exists( 'page_log', 'is_tablet' ):
        sql = 'alter table page_log add column is_tablet boolean default false'
        db.executesql( sql )
    if not column_exists( 'page_log', 'is_mobile' ):
        sql = 'alter table page_log add column is_mobile boolean default false'
        db.executesql( sql )
    if not column_exists( 'page_log', 'os_name' ):
        sql = 'alter table page_log add column os_name varchar( 64 )'
        db.executesql( sql )
    if not column_exists( 'page_log', 'browser_name' ):
        sql = 'alter table page_log add column browser_name varchar( 64 )'
        db.executesql( sql )
    if not column_exists( 'page_log', 'browser_version' ):
        sql = 'alter table page_log add column browser_version varchar( 64 )'
        db.executesql( sql )
    sql = '''
        update page_log
        set path_info = '/register/mia2020'
        where path_info = '/arquivo/ver/31'
    '''
    db.executesql( sql )


def upd_participant():
    if table_exists( 'participant' ):
        sql = 'DROP TABLE participant CASCADE'
        db.executesql( sql )


def upd_artist():
    if not table_exists( 'artist' ):
        sql = '''
            CREATE TABLE artist (
                id SERIAL PRIMARY KEY,
                user_data_id INTEGER NOT NULL,
                artistic_name VARCHAR( 128 ),
                birthday DATE NOT NULL,
                instrument VARCHAR( 512 ),
                obs VARCHAR( 4096 )                
                );
                '''
        db.executesql( sql )
    if not constraint_exists( 'artist_2_user_data', db=db ):
        sql = '''
            alter table artist
                add constraint artist_2_user_data
                foreign key ( user_data_id )
                references user_data ( id )
        '''
        db.executesql( sql )


def upd_instrument():
    if not table_exists( 'instrument' ):
        sql = '''
            CREATE TABLE instrument (
                id SERIAL PRIMARY KEY,
                name VARCHAR( 256 )
                );
                '''
        db.executesql( sql )
    if not index_exists( 'instrument', 'instrument_name_ukey' ):
        sql = '''
            create unique index instrument_name_ukey
                on instrument ( name )
        '''
        db.executesql( sql )


def upd_artist_instrument():
    if not table_exists( 'artist_instrument' ):
        sql = '''
            CREATE TABLE artist_instrument (
                id SERIAL PRIMARY KEY,
                artist_id INTEGER NOT NULL,
                instrument_id INTEGER NOT NULL
                );
                '''
        db.executesql( sql )
    if not constraint_exists( 'artist_instrument_2_artist', db=db ):
        sql = '''
            alter table artist_instrument
                add constraint artist_instrument_2_artist
                foreign key ( artist_id )
                references artist ( id )
        '''
        db.executesql( sql )
    if not constraint_exists( 'artist_instrument_2_instrument', db=db ):
        sql = '''
            alter table artist_instrument
                add constraint artist_instrument_2_instrument
                foreign key ( instrument_id )
                references instrument ( id )
        '''
        db.executesql( sql )


def upd_event():
    if not table_exists( 'event' ):
        sql = '''
            CREATE TABLE event (
                id SERIAL PRIMARY KEY,
                name VARCHAR( 256 ) NOT NULL,
                start_day date NOT NULL,
                end_day date NOT NULL
                );
                '''
        db.executesql( sql )
    if not index_exists( 'event', 'event_name_ukey' ):
        sql = '''
            create unique index event_name_ukey
                on event ( name )
        '''
        db.executesql( sql )


def upd_event_participant():
    if not table_exists( 'event_participant' ):
        sql = '''
            CREATE TABLE event_participant (
                id SERIAL PRIMARY KEY,
                event_id INTEGER NOT NULL,
                artist_id INTEGER NOT NULL,
                obs VARCHAR( 8192),
                attach_id INTEGER NOT NULL,
                description VARCHAR( 2048 )
                )
                '''
        db.executesql( sql )
    if not index_exists( 'event_participant', 'event_participant_artist_ukey' ):
        sql = '''
            create unique index event_participant_artist_ukey
                on event_participant ( event_id, artist_id )
        '''
        db.executesql( sql )
    if not constraint_exists( 'event_participant_2_event', db=db ):
        sql = '''
            alter table event_participant
                add constraint event_participant_2_event
                foreign key ( event_id )
                references event ( id )
        '''
        db.executesql( sql )
    if not constraint_exists( 'event_participant_2_artist', db=db ):
        sql = '''
            alter table event_participant
                add constraint event_participant_2_artist
                foreign key ( artist_id )
                references artist ( id )
        '''
        db.executesql( sql )
    if not constraint_exists( 'event_participant_2_attach', db=db ):
        sql = '''
            alter table event_participant
                add constraint event_participant_2_attach
                foreign key ( attach_id )
                references attach ( id )
        '''
        db.executesql( sql )


def upd_artist_attach():
    if not table_exists( 'artist_attach' ):
        sql = '''
            CREATE TABLE artist_attach (
                id SERIAL PRIMARY KEY,
                artist_id INTEGER NOT NULL,
                attach_id INTEGER NOT NULL,
                description VARCHAR( 2048 )
                )
                '''
        db.executesql( sql )
    if not constraint_exists( 'artist_attach_2_artist', db=db ):
        sql = '''
            alter table artist_attach
                add constraint artist_attach_2_artist
                foreign key ( artist_id )
                references artist ( id )
        '''
        db.executesql( sql )
    if not constraint_exists( 'artist_attach_2_attach', db=db ):
        sql = '''
            alter table artist_attach
                add constraint artist_attach_2_attach
                foreign key ( attach_id )
                references attach ( id )
        '''
        db.executesql( sql )


def upd_app_theme():
    sql_list = [ 'update app_config set app_theme_id = 1',
                 'delete from app_theme where id > 1',
                 '''update app_theme set name='Chirico', 
                    title='Chirico CMS', 
                    subtitle='A free content management system',
                    logo_header='logo-64x64.png',
                    login_button_position='menu',
                    meta_name='chirico',
                    stylesheet='chirico'
                    ''' ]
    for sql in sql_list:
        db.executesql( sql )


def upd_user_data():
    if not table_exists( 'user_data', db=db ):
        sql = '''
            CREATE TABLE user_data (
                id serial primary key,
                auth_user_id integer not null,
                address_1 character varying(128),
                address_2 character varying(128),
                zip_code character varying(64),
                city character varying(128),
                country_id integer,
                phone_1 character varying(32),
                url character varying(256),
                obs character varying(2048)
                );
                '''
        db.executesql( sql )
    if not constraint_exists( 'user_data_2_auth_user', db=db ):
        sql = '''
            alter table user_data
                add constraint user_data_2_auth_user
                foreign key ( auth_user_id )
                references auth_user ( id )
        '''
        db.executesql( sql )
    if not constraint_exists( 'user_data_2_country', db=db ):
        sql = '''
            alter table user_data
                add constraint user_data_2_country
                foreign key ( country_id )
                references country ( id )
        '''
        db.executesql( sql )


def drop_tables():
    sql = 'drop table if exists artist, artist_instrument, event,' \
          'artist_attach, event_participant cascade'
    db.executesql( sql )


def upd_data():
    from m16e.db import db_tables
    at_model = db_tables.get_table_model( 'attach_type', db=db )
    q_sql = (db.attach_type.meta_name == 'portfolio')
    at = at_model.select( q_sql ).first()
    if not at:
        at_model.insert( dict( name='Portfolio', meta_name='portfolio' ) )
    ut_model = db_tables.get_table_model( 'unit_type', db=db )
    q_sql = (db.unit_type.meta_name == 'portfolio')
    ut = ut_model.select( q_sql ).first()
    if not ut:
        ut_model.insert( dict( name='Portfolio', path='portfolios',
                               preferred_order=90, meta_name='portfolio' ) )


def upd_attach():
    if not constraint_exists( 'attach_2_attach_org', db=db ):
        sql = '''
            alter table attach
                add constraint attach_2_attach_org
                foreign key ( org_attach_id )
                references attach ( id )
        '''
        db.executesql( sql )


def update():
    T.lazy = False

    drop_tables()
    upd_data()

    upd_uom_type()
    upd_uom()
    upd_period()
    upd_attach()

    upd_page()
    upd_mail_recipient()
    upd_auth_user()
    upd_request_priority()
    upd_request_status()
    upd_request_type()
    upd_support_request()
    upd_request_dup()
    upd_request_msg()
    upd_request_msg_attach()
    upd_request_subscribers()
    upd_request_vote()

    upd_thread_status()
    upd_thread_type()
    upd_thread()
    upd_thread_visibility()
    upd_thread_msg()
    upd_thread_subscriber()
    upd_thread_vote()
    upd_thread_attach()
    upd_thread_msg_attach()

    upd_page_counter()
    upd_page_log()
    upd_user_message()
    upd_user_data()
    upd_event()

    upd_block()
    upd_block_log()
    upd_app_theme()

    db.commit()

    T.lazy = True


update()
