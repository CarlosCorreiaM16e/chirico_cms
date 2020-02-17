# -*- coding: utf-8 -*-
from getpass import getpass

from app import db_sets
from gluon import current
from m16e.db.database import table_exists, index_exists, column_exists, constraint_exists, sequence_exists, \
    fetch_record_by_id
from m16e.kommon import DT

db = current.db


def init_app_theme():
    if not table_exists( 'app_theme', db=db ):
        sql = '''
            CREATE TABLE app_theme (
                id SERIAL PRIMARY KEY,
                name character varying(32) NOT NULL,
                title character varying(1024) NOT NULL,
                subtitle character varying(1024) NOT NULL,
                logo_header character varying(1024) NOT NULL,
                login_button_position character varying(512) NOT NULL,
                meta_name character varying(1024),
                stylesheet character varying(1024)
            )
        '''
        db.executesql( sql )


def init_unit_type():
    if not table_exists( 'unit_type', db=db ):
        sql = '''
            CREATE TABLE unit_type (
                id SERIAL PRIMARY KEY,
                name character varying(128) NOT NULL,
                path character varying(512) NOT NULL,
                parent_unit_type_id integer,
                preferred_order integer DEFAULT 1,
                meta_name character varying(128) NOT NULL
            )
        '''
        db.executesql( sql )


def init_company_info():
    if not table_exists( 'company_info', db=db ):
        sql = '''
            CREATE TABLE company_info (
                id SERIAL PRIMARY KEY,
                mail_smtp_server character varying(512),
                mail_account character varying(512),
                mail_user character varying(512),
                mail_password character varying(512),
                mail_default_cc character varying(512),
                mail_default_bcc character varying(512),
                mail_default_sign character varying(512),
                mail_smtp_server_port character varying(8),
                mail_tls boolean,
                company_name character varying(512),
                company_tax_id character varying(32),
                company_address character varying(512),
                company_city character varying(128),
                company_postal_code character varying(32),
                company_country character varying(256),
                company_phone character varying(32),
                company_fax character varying(32),
                company_email character varying(256),
                company_website character varying(512),
                company_country_iso3166 character varying(8)
            )
        '''
        db.executesql( sql )


def init_long_task():
    if not table_exists( 'long_task', db=db ):
        sql = '''
            CREATE TABLE long_task (
                id SERIAL PRIMARY KEY,
                task_name character varying(256),
                force_single_instance boolean DEFAULT true NOT NULL
            )
        '''
        db.executesql( sql )


def init_thread_status():
    if not table_exists( 'thread_status', db=db ):
        sql = '''
            CREATE TABLE thread_status (
                id SERIAL PRIMARY KEY,
                thread_status_name character varying(512) NOT NULL,
                meta_name character varying(512),
                is_closed boolean DEFAULT false NOT NULL,
                preferred_order integer DEFAULT 0 NOT NULL
            )
        '''
        db.executesql( sql )


def init_thread_type():
    if not table_exists( 'thread_type', db=db ):
        sql = '''
            CREATE TABLE thread_type (
                id SERIAL PRIMARY KEY,
                thread_type_name character varying(512) NOT NULL,
                meta_name character varying(512),
                preferred_order integer DEFAULT 0 NOT NULL
            )
        '''
        db.executesql( sql )


def init_mime_type():
    if not table_exists( 'mime_type', db=db ):
        sql = '''
            CREATE TABLE mime_type (
                id SERIAL PRIMARY KEY,
                mt_name character varying(512) NOT NULL,
                description character varying(512),
                edit_command character varying(512),
                view_command character varying(512),
                preferred_order integer DEFAULT 0 NOT NULL
            )
        '''
        db.executesql( sql )


def init_attach_type():
    if not table_exists( 'attach_type', db=db ):
        sql = '''
            CREATE TABLE attach_type (
                id SERIAL PRIMARY KEY,
                name character varying(128) NOT NULL,
                meta_name character varying(80)
            )
        '''
        db.executesql( sql )



def init_mime_type_ext():
    if not table_exists( 'c', db=db ):
        sql = '''
            CREATE TABLE mime_type_ext (
                id SERIAL PRIMARY KEY,
                mime_type_id integer NOT NULL,
                extension character varying(512) NOT NULL
            )
        '''
        db.executesql( sql )
    if not constraint_exists( 'mime_type_ext_2_mime_type', db=db ):
        sql = '''
            ALTER TABLE mime_type_ext
                ADD CONSTRAINT mime_type_ext_2_mime_type 
                FOREIGN KEY (mime_type_id) 
                REFERENCES mime_type( id )
        '''
        db.executesql( sql )


def init_app_config():
    if not table_exists( 'app_config', db=db ):
        sql = '''
            CREATE TABLE app_config (
                id SERIAL PRIMARY KEY,
                qt_decimals integer NOT NULL,
                currency_decimals integer NOT NULL,
                server_timezone character varying(128) DEFAULT 'UTC'::character varying NOT NULL,
                client_timezone character varying(128) DEFAULT 'UTC'::character varying NOT NULL,
                app_theme_id integer DEFAULT 1 NOT NULL,
                flash_msg_delay integer default 3000 not null,
                max_img_page_width integer,
                max_img_block_width integer,
                max_img_thumb_width integer
            )
        '''
        db.executesql( sql )
    if not constraint_exists( 'app_config_2_app_theme', db=db ):
        sql = '''
            ALTER TABLE app_config
                ADD CONSTRAINT app_config_2_app_theme 
                FOREIGN KEY (app_theme_id) 
                REFERENCES app_theme(id)
        '''
        db.executesql( sql )


def init_attach():
    if not table_exists( 'attach', db=db ):
        sql = '''
            CREATE TABLE attach (
                id SERIAL PRIMARY KEY,
                attach_type_id integer NOT NULL,
                attached character varying(512),
                created_on timestamp without time zone DEFAULT now() NOT NULL,
                created_by integer,
                path character varying(512),
                filename character varying(512),
                short_description character varying(512),
                long_description character varying,
                unit_type_id integer,
                mime_type_id integer,
                is_site_image boolean DEFAULT false NOT NULL,
                img_width integer,
                img_height integer,
                attached_file bytea,
                org_attach_id integer
            )
        '''
        db.executesql( sql )
    if not constraint_exists( 'attach_2_attach_type', db=db ):
        sql = '''
            ALTER TABLE attach
                ADD CONSTRAINT attach_2_attach_type 
                FOREIGN KEY (attach_type_id) 
                REFERENCES attach_type(id)
        '''
        db.executesql( sql )
    if not constraint_exists( 'attach_2_unit_type', db=db ):
        sql = '''
            ALTER TABLE attach
                ADD CONSTRAINT attach_2_unit_type 
                FOREIGN KEY (unit_type_id) 
                REFERENCES unit_type(id)
        '''
        db.executesql( sql )
    if not constraint_exists( 'attach_2_mime_type', db=db ):
        sql = '''
            ALTER TABLE attach
                ADD CONSTRAINT attach_2_mime_type 
                FOREIGN KEY (mime_type_id) 
                REFERENCES mime_type(id)
        '''
        db.executesql( sql )


def init_auth():
    # auth_cas
    if not table_exists( 'auth_cas' ):
        sql = '''
            CREATE TABLE auth_cas (
                id SERIAL PRIMARY KEY,
                user_id integer,
                created_on timestamp without time zone,
                service character varying(512),
                ticket character varying(512),
                renew character(1)
            )
        '''
        db.executesql( sql )

    # auth_event
    if not table_exists( 'auth_event' ):
        sql = '''
            CREATE TABLE auth_event (
                id SERIAL PRIMARY KEY,
                time_stamp timestamp without time zone,
                client_ip character varying(512),
                user_id integer,
                origin character varying(512),
                description character varying
            )
        '''
        db.executesql( sql )

    # auth_group
    if not table_exists( 'auth_group' ):
        sql = '''
            CREATE TABLE auth_group (
                id SERIAL PRIMARY KEY,
                role character varying(512) NOT NULL,
                description character varying
            )
        '''
        db.executesql( sql )
    if not index_exists( 'auth_group', 'auth_group_role_ukey' ):
        sql = '''
            create unique index auth_group_role_ukey
                on auth_group ( role )
        '''
        db.executesql( sql )

    # auth_user
    if not table_exists( 'auth_user' ):
        sql = '''
            CREATE TABLE auth_user (
                id SERIAL PRIMARY KEY,
                first_name character varying(128) NOT NULL,
                last_name character varying(128) NOT NULL DEFAULT '',
                email character varying(512) NOT NULL,
                password character varying(512),
                registration_key character varying(512),
                reset_password_key character varying(512),
                registration_id character varying(512),
                user_timezone character varying(128),
                ctime timestamp with time zone
            );
        '''
        db.executesql( sql )
    if not index_exists( 'auth_user', 'auth_user_name_ukey' ):
        sql = '''
            create unique index auth_group_name_ukey
                on auth_user ( first_name, last_name )
        '''
        db.executesql( sql )
    if not index_exists( 'auth_user', 'auth_user_email_ukey' ):
        sql = '''
            create unique index auth_group_email_ukey
                on auth_user ( email )
        '''
        db.executesql( sql )

    # auth_membership
    if not table_exists( 'auth_membership' ):
        sql = '''
            CREATE TABLE auth_membership (
                id SERIAL PRIMARY KEY,
                user_id integer,
                group_id integer
            )
        '''
        db.executesql( sql )
    if not index_exists( 'auth_membership', 'auth_membership_user_group_ukey' ):
        sql = '''
            create unique index auth_membership_user_group_ukey
                on auth_membership ( user_id, group_id )
        '''
        db.executesql( sql )
    if not constraint_exists( 'auth_membership_2_auth_user', db=db ):
        sql = '''
            ALTER TABLE auth_membership
                ADD CONSTRAINT auth_membership_2_auth_user 
                FOREIGN KEY (user_id) 
                REFERENCES auth_user(id)
        '''
        db.executesql( sql )
    if not constraint_exists( 'auth_membership_2_auth_group', db=db ):
        sql = '''
            ALTER TABLE auth_membership
                ADD CONSTRAINT auth_membership_2_auth_group 
                FOREIGN KEY (group_id) 
                REFERENCES auth_group(id)
        '''
        db.executesql( sql )

    # auth_permission
    if not table_exists( 'auth_permission' ):
        sql = '''
            CREATE TABLE auth_permission (
                id SERIAL PRIMARY KEY,
                group_id integer,
                name character varying(512),
                table_name character varying(512),
                record_id integer
            )
        '''
        db.executesql( sql )
    if not constraint_exists( 'auth_permission_2_auth_group', db=db ):
        sql = '''
            ALTER TABLE auth_permission
                ADD CONSTRAINT auth_permission_2_auth_group 
                FOREIGN KEY (group_id) 
                REFERENCES auth_group(id)
        '''
        db.executesql( sql )


def init_page():
    if not table_exists( 'page', db=db ):
        sql = '''
            CREATE TABLE page (
                id SERIAL PRIMARY KEY,
                parent_page_id integer,
                tagname character varying(512),
                title character varying(1024) NOT NULL,
                title_en character varying(1024),
                aside_title character varying(512),
                aside_title_en character varying(512),
                aside_position character(1),
                url_c character varying(512),
                url_f character varying(512),
                url_args character varying(1024),
                colspan integer DEFAULT 1 NOT NULL,
                rowspan integer DEFAULT 1 NOT NULL,
                menu_order integer,
                last_modified_by integer NOT NULL,
                is_news boolean DEFAULT false NOT NULL,
                page_timestamp timestamp without time zone,
                name character varying(512) NOT NULL,
                main_panel_cols integer,
                aside_panel_cols integer,
                hide boolean DEFAULT false
            )
        '''
        db.executesql( sql )
    if not constraint_exists( 'page_2_parent_page', db=db ):
        sql = '''
            ALTER TABLE page
                ADD CONSTRAINT page_2_parent_page 
                FOREIGN KEY (parent_page_id) 
                REFERENCES page(id)
        '''
        db.executesql( sql )


def init_block():
    if not table_exists( 'block', db=db ):
        sql = '''
            CREATE TABLE block (
                id SERIAL PRIMARY KEY,
                name character varying(512),
                description character varying(1024),
                page_id integer,
                container character(1) DEFAULT 'M'::bpchar,
                blk_order integer DEFAULT 1,
                body character varying NOT NULL,
                body_en character varying,
                body_markup character(1) DEFAULT 'M'::bpchar NOT NULL,
                created_on timestamp without time zone DEFAULT now() NOT NULL,
                created_by integer NOT NULL,
                last_modified_by integer NOT NULL,
                last_modified_on timestamp with time zone DEFAULT now(),
                colspan integer DEFAULT 1 NOT NULL,
                rowspan integer DEFAULT 1 NOT NULL,
                css_class character varying(512),
                css_style character varying(512),
                html_element_id character varying(512)
            )
        '''
        db.executesql( sql )
        db.executesql( "COMMENT ON COLUMN block.container IS 'M: main; A: aside';" )
    if not constraint_exists( 'block_2_page', db=db ):
        sql = '''
            ALTER TABLE block
                ADD CONSTRAINT block_2_page 
                FOREIGN KEY (page_id) 
                REFERENCES page(id)
        '''
        db.executesql( sql )


def init_block_attach():
    if not table_exists( 'block_attach', db=db ):
        sql = '''
            CREATE TABLE block_attach (
                id SERIAL PRIMARY KEY,
                block_id integer,
                attach_id integer
            )
        '''
        db.executesql( sql )
    if not constraint_exists( 'block_attach_2_attach', db=db ):
        sql = '''
            ALTER TABLE block_attach
                ADD CONSTRAINT block_attach_2_attach 
                FOREIGN KEY (attach_id) 
                REFERENCES attach(id)
        '''
        db.executesql( sql )
    if not constraint_exists( 'block_attach_2_block', db=db ):
        sql = '''
            ALTER TABLE block_attach
                ADD CONSTRAINT block_attach_2_block 
                FOREIGN KEY (block_id) 
                REFERENCES block(id)
        '''
        db.executesql( sql )


def init_mail_queue():
    if not table_exists( 'mail_queue', db=db ):
        sql = '''
            CREATE TABLE mail_queue (
                id SERIAL PRIMARY KEY,
                subject character varying(512) NOT NULL,
                text_body character varying,
                html_body character varying,
                when_to_send timestamp without time zone DEFAULT now() NOT NULL,
                sent timestamp without time zone,
                status character varying(4096) NOT NULL,
                mail_cc character varying(512),
                mail_bcc character varying(512),
                auth_user_id integer NOT NULL,
                percent_done integer DEFAULT 0 NOT NULL,
                progress_message character varying(2048)
            )
        '''
        db.executesql( sql )
        db.executesql( "COMMENT ON COLUMN mail_queue.status IS 'error, pending, sent or empty (for queued)'")
    if not constraint_exists( 'mail_queue_2_auth_user', db=db ):
        sql = '''
            ALTER TABLE mail_queue
                ADD CONSTRAINT mail_queue_2_auth_user 
                FOREIGN KEY (auth_user_id) 
                REFERENCES auth_user(id)
        '''
        db.executesql( sql )


def init_mail_recipient():
    if not table_exists( 'mail_recipient', db=db ):
        sql = '''
            CREATE TABLE mail_recipient (
                id SERIAL PRIMARY KEY,
                mail_queue_id integer NOT NULL,
                email character varying(512) NOT NULL,
                sent timestamp without time zone,
                status character varying(4096) DEFAULT 'pending'::character varying NOT NULL,
                retries integer DEFAULT 0 NOT NULL
            );
        '''
        db.executesql( sql )
    if not constraint_exists( 'mail_recipient_2_mail_queue', db=db ):
        sql = '''
            ALTER TABLE mail_recipient
                ADD CONSTRAINT mail_recipient_2_mail_queue 
                FOREIGN KEY (mail_queue_id) 
                REFERENCES mail_queue(id)
        '''
        db.executesql( sql )


def init_page_log():
    if not table_exists( 'page_log', db=db ):
        sql = '''
            CREATE TABLE page_log (
                id SERIAL PRIMARY KEY,
                path_info character varying(512) NOT NULL,
                ts timestamp without time zone NOT NULL,
                client_ip character varying(16),
                auth_user_id integer
            );
        '''
        db.executesql( sql )
    if not constraint_exists( 'page_log_2_auth_user', db=db ):
        sql = '''
            ALTER TABLE page_log
                ADD CONSTRAINT page_log_2_auth_user 
                FOREIGN KEY (auth_user_id) 
                REFERENCES auth_user(id)
        '''
        db.executesql( sql )


def init_shared_run():
    if not table_exists( 'shared_run', db=db ):
        sql = '''
            CREATE TABLE shared_run (
                id SERIAL PRIMARY KEY,
                long_task_id integer NOT NULL,
                task_parameters character varying(4096),
                progress_message character varying(4096),
                requested_by integer,
                requested_when timestamp with time zone DEFAULT now() NOT NULL,
                start_at timestamp with time zone DEFAULT now() NOT NULL,
                running_since timestamp with time zone,
                finished_when timestamp with time zone,
                finished_status character varying(1024),
                percent_done integer DEFAULT 0 NOT NULL,
                notify_user boolean DEFAULT true NOT NULL,
                user_notified_when timestamp with time zone,
                progress_msg_id integer,
                priority integer DEFAULT 100 NOT NULL
            )
        '''
        db.executesql( sql )
    if not constraint_exists( 'shared_run_2_long_task', db=db ):
        sql = '''
            ALTER TABLE shared_run
                ADD CONSTRAINT shared_run_2_long_task 
                FOREIGN KEY (long_task_id) 
                REFERENCES long_task(id)
        '''
        db.executesql( sql )
    if not constraint_exists( 'shared_run_2_auth_user', db=db ):
        sql = '''
            ALTER TABLE shared_run
                ADD CONSTRAINT shared_run_2_auth_user 
                FOREIGN KEY (requested_by) 
                REFERENCES auth_user(id)
        '''
        db.executesql( sql )


def init_thread():
    if not table_exists( 'thread', db=db ):
        sql = '''
            CREATE TABLE thread (
                id SERIAL PRIMARY KEY,
                created_on timestamp without time zone NOT NULL,
                created_by integer NOT NULL,
                thread_title character varying(512) NOT NULL,
                thread_msg character varying(65535),
                thread_status_id integer DEFAULT 1 NOT NULL,
                thread_type_id integer DEFAULT 1 NOT NULL,
                closed_time timestamp without time zone,
                markup character(1) DEFAULT 'M'::bpchar
            );
        '''
        db.executesql( sql )
        db.executesql( "COMMENT ON COLUMN thread.markup IS 'M: MARKMIN; H: HTML'")
    if not constraint_exists( 'thread_2_auth_user', db=db ):
        sql = '''
            ALTER TABLE thread
                ADD CONSTRAINT thread_2_auth_user 
                FOREIGN KEY (created_by) 
                REFERENCES auth_user(id)
        '''
        db.executesql( sql )
    if not constraint_exists( 'thread_2_thread_status', db=db ):
        sql = '''
            ALTER TABLE thread
                ADD CONSTRAINT thread_2_thread_status 
                FOREIGN KEY (thread_status_id) 
                REFERENCES thread_status(id)
        '''
        db.executesql( sql )
    if not constraint_exists( 'thread_2_thread_type', db=db ):
        sql = '''
            ALTER TABLE thread
                ADD CONSTRAINT thread_2_thread_type 
                FOREIGN KEY (thread_type_id) 
                REFERENCES thread_type(id)
        '''
        db.executesql( sql )


def init_thread_attach():
    if not table_exists( 'thread_attach', db=db ):
        sql = '''
            CREATE TABLE thread_attach (
                id SERIAL PRIMARY KEY,
                attach_id integer,
                thread_id integer
            );
        '''
        db.executesql( sql )
    if not constraint_exists( 'thread_attach_2_attach', db=db ):
        sql = '''
            ALTER TABLE thread_attach
                ADD CONSTRAINT thread_attach_2_attach 
                FOREIGN KEY (attach_id) 
                REFERENCES attach(id)
        '''
        db.executesql( sql )
    if not constraint_exists( 'thread_attach_2_thread', db=db ):
        sql = '''
            ALTER TABLE thread_attach
                ADD CONSTRAINT thread_attach_2_thread 
                FOREIGN KEY (thread_id) 
                REFERENCES thread(id)
        '''
        db.executesql( sql )


def init_thread_msg():
    if not table_exists( 'thread_msg', db=db ):
        sql = '''
            CREATE TABLE thread_msg (
                id SERIAL PRIMARY KEY,
                thread_id integer NOT NULL,
                parent_thread_msg_id integer,
                auth_user_id integer NOT NULL,
                msg_text character varying NOT NULL,
                msg_ts timestamp without time zone NOT NULL
            );
        '''
        db.executesql( sql )
    if not constraint_exists( 'thread_msg_2_thread', db=db ):
        sql = '''
            ALTER TABLE thread_msg
                ADD CONSTRAINT thread_msg_2_thread 
                FOREIGN KEY (thread_id) 
                REFERENCES thread(id)
        '''
        db.executesql( sql )
    if not constraint_exists( 'thread_msg_2_auth_user', db=db ):
        sql = '''
            ALTER TABLE thread_msg
                ADD CONSTRAINT thread_msg_2_auth_user 
                FOREIGN KEY (auth_user_id) 
                REFERENCES auth_user(id)
        '''
        db.executesql( sql )


def init_thread_msg_attach():
    if not table_exists( 'thread_msg_attach', db=db ):
        sql = '''
            CREATE TABLE thread_msg_attach (
                id SERIAL PRIMARY KEY,
                attach_id integer,
                thread_msg_id integer
            );
        '''
        db.executesql( sql )
    if not constraint_exists( 'thread_msg_attach_2_attach', db=db ):
        sql = '''
            ALTER TABLE thread_msg_attach
                ADD CONSTRAINT thread_msg_attach_2_attach 
                FOREIGN KEY (attach_id) 
                REFERENCES attach(id)
        '''
        db.executesql( sql )
    if not constraint_exists( 'thread_msg_attach_2_thread_msg', db=db ):
        sql = '''
            ALTER TABLE thread_msg_attach
                ADD CONSTRAINT thread_attach_msg_2_thread_msg 
                FOREIGN KEY (thread_msg_id) 
                REFERENCES thread_msg(id)
        '''
        db.executesql( sql )


def init_thread_subscriber():
    if not table_exists( 'thread_subscriber', db=db ):
        sql = '''
            CREATE TABLE thread_subscriber (
                id SERIAL PRIMARY KEY,
                thread_id integer NOT NULL,
                auth_user_id integer NOT NULL,
                unsubscribed timestamp without time zone
            );
        '''
        db.executesql( sql )
    if not constraint_exists( 'thread_subscriber_2_auth_user', db=db ):
        sql = '''
            ALTER TABLE thread_subscriber
                ADD CONSTRAINT thread_subscriber_2_auth_user 
                FOREIGN KEY (auth_user_id) 
                REFERENCES auth_user(id)
        '''
        db.executesql( sql )
    if not constraint_exists( 'thread_subscriber_2_thread', db=db ):
        sql = '''
            ALTER TABLE thread_subscriber
                ADD CONSTRAINT thread_subscriber_2_thread 
                FOREIGN KEY (thread_id) 
                REFERENCES thread(id)
        '''
        db.executesql( sql )


def init_thread_vote():
    if not table_exists( 'thread_vote', db=db ):
        sql = '''
            CREATE TABLE thread_vote (
                id SERIAL PRIMARY KEY,
                thread_id integer NOT NULL,
                thread_msg_id integer,
                auth_user_id integer NOT NULL,
                vote_ts timestamp without time zone NOT NULL,
                vote integer NOT NULL,
                CONSTRAINT thread_vote_vote_check CHECK (((vote = 1) OR (vote = '-1'::integer)))
            )
        '''
        db.executesql( sql )
    if not constraint_exists( 'thread_vote_2_auth_user', db=db ):
        sql = '''
            ALTER TABLE thread_vote
                ADD CONSTRAINT thread_vote_2_auth_user 
                FOREIGN KEY (auth_user_id) 
                REFERENCES auth_user(id)
        '''
        db.executesql( sql )
    if not constraint_exists( 'thread_vote_2_thread', db=db ):
        sql = '''
            ALTER TABLE thread_vote
                ADD CONSTRAINT thread_vote_2_thread 
                FOREIGN KEY (thread_id) 
                REFERENCES thread(id)
        '''
        db.executesql( sql )
    if not constraint_exists( 'thread_vote_2_thread_msg', db=db ):
        sql = '''
            ALTER TABLE thread_vote
                ADD CONSTRAINT thread_vote_2_thread_msg
                FOREIGN KEY (thread_msg_id) 
                REFERENCES thread_msg(id)
        '''
        db.executesql( sql )


def init_user_message():
    if not table_exists( 'user_message', db=db ):
        sql = '''
            CREATE TABLE user_message (
                id SERIAL PRIMARY KEY,
                notify_user_id integer NOT NULL,
                msg_org integer,
                msg_title character varying(512) NOT NULL,
                msg_text character varying(4096) NOT NULL,
                times_viewed integer NOT NULL,
                period_start timestamp with time zone DEFAULT now() NOT NULL,
                period_stop timestamp with time zone,
                ack_when timestamp without time zone,
                answer character varying(4096),
                delete_if_past boolean DEFAULT false NOT NULL,
                msg_type character varying(16)
            )
        '''
        db.executesql( sql )
    if not constraint_exists( 'user_message_2_auth_user', db=db ):
        sql = '''
            ALTER TABLE user_message
                ADD CONSTRAINT user_message_2_auth_user 
                FOREIGN KEY (notify_user_id) 
                REFERENCES auth_user(id)
        '''
        db.executesql( sql )


from gluon import CRYPT
from m16e import kommon, user_factory, term


def populate_users():
    T = current.T
    # admin user
    print( '''
        Please fill the main user (administrator) data below.
    ''')
    request = current.request
    cfg_file = request.env.web2py_path + '/applications/%(app)s/resources/config/init/cfg_%(app)s.py' % dict( app=current.app_name )
    term.printDebug( 'cfg_file: ' + cfg_file )
    from m16e.files import fileutils
    if fileutils.file_exists( cfg_file ):
        data = fileutils.read_data_file( cfg_file )
        first_name = data[ 'full_name']
        email = data[ 'email']
        password = data[ 'password']
    else:
        first_name = raw_input( T( 'Full name' ) + ': ' )
        email = raw_input( T( 'E-mail' ) + ': ' )
        password = getpass( T( 'Password' ) + ': ' )
    user_id = db.auth_user.insert( first_name=first_name,
                                   last_name='',
                                   email=email,
                                   password=db.auth_user.password.requires( password )[0] )
    for g in (user_factory._group_hierarchy_list ):
        g_id = db.auth_group.insert( role=g )
        db.auth_membership.insert( user_id=user_id, group_id=g_id )
    # dummy user (robot)
    db.auth_user.insert( first_name='(dummy)',
                         email=user_factory.DUMMY_USER,
                         registration_key='dummy' ) # prevent login


def populate_types():
    T = current.T
    from m16e.db import db_tables
    # attach_type
    at_model = db_tables.get_table_model( 'attach_type' )
    values = [ dict( name='Logo', meta_name='company-logo' ),
               dict( name='Fotos', meta_name='images' ),
               dict( name='Webshop', meta_name='webshop' ) ]
    for v in values:
        at_model.insert( v )
    # long_task
    lt_model = db_tables.get_table_model( 'long_task' )
    values = [ dict( task_name='send_mails', force_single_instance=True ) ]
    for v in values:
        lt_model.insert( v )
    # thread_type
    tt_model = db_tables.get_table_model( 'thread_type' )
    values = [ dict( thread_type_name=T( 'Open discussion' ), meta_name='open-discussion', preferred_order=1 ),
               dict( thread_type_name=T( 'Private discussion' ), meta_name='restricted', preferred_order=10 ),]
    for v in values:
        tt_model.insert( v )
    # app_theme
    appt_model = db_tables.get_table_model( 'app_theme' )
    values = [ dict( name='Chirico',
                     title='Chirico CMS',
                     subtitle='A free content management system',
                     logo_header='logo-64x64.png',
                     login_button_position='menu',
                     meta_name='chirico',
                     stylesheet='chirico' )
               ]
    for v in values:
        at_id = appt_model.insert( v )
    # app_config
    ac_model = db_tables.get_table_model( 'app_config' )
    values = [ dict( qt_decimals=0,
                     currency_decimals=0,
                     server_timezone='UTC',
                     client_timezone='UTC',
                     app_theme_id=at_id,
                     max_img_page_width=2048,
                     max_img_block_width=800,
                     max_img_thumb_width=160 )
               ]
    for v in values:
        ac_model.insert( v )


def populate_mime_types():
    from m16e.db import db_tables
    mt_model = db_tables.get_table_model( 'mime_type' )
    values = [ dict( mt_name='application/msword', description='', edit_command='', view_command='', preferred_order=1 ),
               dict( mt_name='application/octet-stream', description='', edit_command='', view_command='', preferred_order=1 ),
               dict( mt_name='application/ogg', description='', edit_command='', view_command='', preferred_order=1 ),
               dict( mt_name='application/pdf', description='', edit_command='', view_command='', preferred_order=1 ),
               dict( mt_name='application/pgp-keys', description='', edit_command='', view_command='', preferred_order=1 ),
               dict( mt_name='application/pgp-signature', description='', edit_command='', view_command='', preferred_order=1 ),
               dict( mt_name='application/postscript', description='', edit_command='', view_command='', preferred_order=1 ),
               dict( mt_name='application/rar', description='', edit_command='', view_command='', preferred_order=1 ),
               dict( mt_name='application/rdf+xml', description='', edit_command='', view_command='', preferred_order=1 ),
               dict( mt_name='application/rss+xml', description='', edit_command='', view_command='', preferred_order=1 ),
               dict( mt_name='application/vnd.ms-excel', description='', edit_command='', view_command='', preferred_order=1 ),
               dict( mt_name='application/vnd.ms-powerpoint', description='', edit_command='', view_command='', preferred_order=1 ),
               dict( mt_name='application/vnd.oasis.opendocument.chart', description='', edit_command='', view_command='', preferred_order=1 ),
               dict( mt_name='application/vnd.oasis.opendocument.database', description='', edit_command='', view_command='', preferred_order=1 ),
               dict( mt_name='application/vnd.oasis.opendocument.formula', description='', edit_command='', view_command='', preferred_order=1 ),
               dict( mt_name='application/vnd.oasis.opendocument.graphics', description='', edit_command='', view_command='', preferred_order=1 ),
               dict( mt_name='application/vnd.oasis.opendocument.graphics-template', description='', edit_command='', view_command='', preferred_order=1 ),
               dict( mt_name='application/vnd.oasis.opendocument.image', description='', edit_command='', view_command='', preferred_order=1 ),
               dict( mt_name='application/vnd.oasis.opendocument.presentation', description='', edit_command='', view_command='', preferred_order=1 ),
               dict( mt_name='application/vnd.oasis.opendocument.presentation-template', description='', edit_command='', view_command='', preferred_order=1 ),
               dict( mt_name='application/vnd.oasis.opendocument.spreadsheet', description='', edit_command='', view_command='', preferred_order=1 ),
               dict( mt_name='application/vnd.oasis.opendocument.spreadsheet-template', description='', edit_command='', view_command='', preferred_order=1 ),
               dict( mt_name='application/vnd.oasis.opendocument.text', description='', edit_command='', view_command='', preferred_order=1 ),
               dict( mt_name='application/vnd.oasis.opendocument.text-master', description='', edit_command='', view_command='', preferred_order=1 ),
               dict( mt_name='application/vnd.oasis.opendocument.text-template', description='', edit_command='', view_command='', preferred_order=1 ),
               dict( mt_name='application/vnd.oasis.opendocument.text-web', description='', edit_command='', view_command='', preferred_order=1 ),
               dict( mt_name='application/vnd.stardivision.calc', description='', edit_command='', view_command='', preferred_order=1 ),
               dict( mt_name='application/vnd.stardivision.draw', description='', edit_command='', view_command='', preferred_order=1 ),
               dict( mt_name='application/vnd.stardivision.impress', description='', edit_command='', view_command='', preferred_order=1 ),
               dict( mt_name='application/vnd.stardivision.math', description='', edit_command='', view_command='', preferred_order=1 ),
               dict( mt_name='application/vnd.stardivision.writer', description='', edit_command='', view_command='', preferred_order=1 ),
               dict( mt_name='application/vnd.stardivision.writer-global', description='', edit_command='', view_command='', preferred_order=1 ),
               dict( mt_name='application/vnd.sun.xml.calc', description='', edit_command='', view_command='', preferred_order=1 ),
               dict( mt_name='application/vnd.sun.xml.calc.template', description='', edit_command='', view_command='', preferred_order=1 ),
               dict( mt_name='application/vnd.sun.xml.draw', description='', edit_command='', view_command='', preferred_order=1 ),
               dict( mt_name='application/vnd.sun.xml.draw.template', description='', edit_command='', view_command='', preferred_order=1 ),
               dict( mt_name='application/vnd.sun.xml.impress', description='', edit_command='', view_command='', preferred_order=1 ),
               dict( mt_name='application/vnd.sun.xml.impress.template', description='', edit_command='', view_command='', preferred_order=1 ),
               dict( mt_name='application/vnd.sun.xml.math', description='', edit_command='', view_command='', preferred_order=1 ),
               dict( mt_name='application/vnd.sun.xml.writer', description='', edit_command='', view_command='', preferred_order=1 ),
               dict( mt_name='application/vnd.sun.xml.writer.global', description='', edit_command='', view_command='', preferred_order=1 ),
               dict( mt_name='application/vnd.sun.xml.writer.template', description='', edit_command='', view_command='', preferred_order=1 ),
               dict( mt_name='application/x-dvi', description='', edit_command='', view_command='', preferred_order=1 ),
               dict( mt_name='application/x-flac', description='', edit_command='', view_command='', preferred_order=1 ),
               dict( mt_name='application/x-font', description='', edit_command='', view_command='', preferred_order=1 ),
               dict( mt_name='application/x-freemind', description='', edit_command='', view_command='', preferred_order=1 ),
               dict( mt_name='application/x-gnumeric', description='', edit_command='', view_command='', preferred_order=1 ),
               dict( mt_name='application/x-gtar', description='', edit_command='', view_command='', preferred_order=1 ),
               dict( mt_name='application/x-java-jnlp-file', description='', edit_command='', view_command='', preferred_order=1 ),
               dict( mt_name='application/x-kpresenter', description='', edit_command='', view_command='', preferred_order=1 ),
               dict( mt_name='application/x-kspread', description='', edit_command='', view_command='', preferred_order=1 ),
               dict( mt_name='application/x-kword', description='', edit_command='', view_command='', preferred_order=1 ),
               dict( mt_name='application/xml', description='', edit_command='', view_command='', preferred_order=1 ),
               dict( mt_name='application/x-shockwave-flash', description='', edit_command='', view_command='', preferred_order=1 ),
               dict( mt_name='application/x-tar', description='', edit_command='', view_command='', preferred_order=1 ),
               dict( mt_name='application/zip', description='', edit_command='', view_command='', preferred_order=1 ),
               dict( mt_name='audio/basic', description='', edit_command='', view_command='', preferred_order=1 ),
               dict( mt_name='audio/midi', description='', edit_command='', view_command='', preferred_order=1 ),
               dict( mt_name='audio/mpeg', description='', edit_command='', view_command='', preferred_order=1 ),
               dict( mt_name='audio/mpegurl', description='', edit_command='', view_command='', preferred_order=1 ),
               dict( mt_name='audio/x-aiff', description='', edit_command='', view_command='', preferred_order=1 ),
               dict( mt_name='audio/x-mpegurl', description='', edit_command='', view_command='', preferred_order=1 ),
               dict( mt_name='audio/x-ms-wma', description='', edit_command='', view_command='', preferred_order=1 ),
               dict( mt_name='audio/x-pn-realaudio', description='', edit_command='', view_command='', preferred_order=1 ),
               dict( mt_name='audio/x-realaudio', description='', edit_command='', view_command='', preferred_order=1 ),
               dict( mt_name='audio/x-wav', description='', edit_command='', view_command='', preferred_order=1 ),
               dict( mt_name='(desconhecido)', description='(tipo deconhecido)', edit_command='', view_command='', preferred_order=1 ),
               dict( mt_name='image/gif', description='', edit_command='', view_command='', preferred_order=1 ),
               dict( mt_name='image/jpeg', description='', edit_command='', view_command='', preferred_order=1 ),
               dict( mt_name='image/png', description='', edit_command='', view_command='', preferred_order=1 ),
               dict( mt_name='image/svg+xml', description='', edit_command='', view_command='', preferred_order=1 ),
               dict( mt_name='image/tiff', description='', edit_command='', view_command='', preferred_order=1 ),
               dict( mt_name='image/vnd.djvu', description='', edit_command='', view_command='', preferred_order=1 ),
               dict( mt_name='image/x-coreldraw', description='', edit_command='', view_command='', preferred_order=1 ),
               dict( mt_name='image/x-coreldrawpattern', description='', edit_command='', view_command='', preferred_order=1 ),
               dict( mt_name='image/x-coreldrawtemplate', description='', edit_command='', view_command='', preferred_order=1 ),
               dict( mt_name='image/x-corelphotopaint', description='', edit_command='', view_command='', preferred_order=1 ),
               dict( mt_name='image/x-icon', description='', edit_command='', view_command='', preferred_order=1 ),
               dict( mt_name='image/x-ms-bmp', description='', edit_command='', view_command='', preferred_order=1 ),
               dict( mt_name='image/x-photoshop', description='', edit_command='', view_command='', preferred_order=1 ),
               dict( mt_name='image/x-portable-anymap', description='', edit_command='', view_command='', preferred_order=1 ),
               dict( mt_name='image/x-portable-bitmap', description='', edit_command='', view_command='', preferred_order=1 ),
               dict( mt_name='image/x-portable-graymap', description='', edit_command='', view_command='', preferred_order=1 ),
               dict( mt_name='image/x-portable-pixmap', description='', edit_command='', view_command='', preferred_order=1 ),
               dict( mt_name='image/x-rgb', description='', edit_command='', view_command='', preferred_order=1 ),
               dict( mt_name='image/x-xbitmap', description='', edit_command='', view_command='', preferred_order=1 ),
               dict( mt_name='image/x-xpixmap', description='', edit_command='', view_command='', preferred_order=1 ),
               dict( mt_name='image/x-xwindowdump', description='', edit_command='', view_command='', preferred_order=1 ),
               dict( mt_name='text/html', description='', edit_command='', view_command='', preferred_order=1 ),
               dict( mt_name='text/plain', description='', edit_command='', view_command='', preferred_order=1 ),
               dict( mt_name='text/richtext', description='', edit_command='', view_command='', preferred_order=1 ),
               dict( mt_name='text/rtf', description='', edit_command='', view_command='', preferred_order=1 ),
               dict( mt_name='video/mp4', description='', edit_command='', view_command='', preferred_order=1 ),
               dict( mt_name='video/mpeg', description='', edit_command='', view_command='', preferred_order=1 ),
               dict( mt_name='video/quicktime', description='', edit_command='', view_command='', preferred_order=1 ),
               dict( mt_name='video/x-ms-wmv', description='', edit_command='', view_command='', preferred_order=1 ),
               dict( mt_name='video/x-sgi-movie', description='', edit_command='', view_command='', preferred_order=1 ),
    ]
    for v in values:
        mt_model.insert( v )

    mte_model = db_tables.get_table_model( 'mime_type_ext' )
    # mime_type_ext
    values = [ dict( mime_type_name='application/postscript', extension='ai' ),
               dict( mime_type_name='audio/x-aiff', extension='aif' ),
               dict( mime_type_name='audio/x-aiff', extension='aifc' ),
               dict( mime_type_name='audio/x-aiff', extension='aiff' ),
               dict( mime_type_name='text/plain', extension='asc' ),
               dict( mime_type_name='audio/basic', extension='au' ),
               dict( mime_type_name='application/octet-stream', extension='bin' ),
               dict( mime_type_name='image/x-ms-bmp', extension='bmp' ),
               dict( mime_type_name='image/x-coreldraw', extension='cdr' ),
               dict( mime_type_name='image/x-coreldrawtemplate', extension='cdt' ),
               dict( mime_type_name='image/x-corelphotopaint', extension='cpt' ),
               dict( mime_type_name='text/plain', extension='csv' ),
               dict( mime_type_name='text/plain', extension='diff' ),
               dict( mime_type_name='image/vnd.djvu', extension='djv' ),
               dict( mime_type_name='image/vnd.djvu', extension='djvu' ),
               dict( mime_type_name='application/msword', extension='doc' ),
               dict( mime_type_name='application/msword', extension='docx' ),
               dict( mime_type_name='application/msword', extension='dot' ),
               dict( mime_type_name='application/x-dvi', extension='dvi' ),
               dict( mime_type_name='application/postscript', extension='eps' ),
               dict( mime_type_name='application/x-flac', extension='flac' ),
               dict( mime_type_name='image/gif', extension='gif' ),
               dict( mime_type_name='application/x-gnumeric', extension='gnumeric' ),
               dict( mime_type_name='application/x-font', extension='gsf' ),
               dict( mime_type_name='application/x-gtar', extension='gtar' ),
               dict( mime_type_name='text/html', extension='htm' ),
               dict( mime_type_name='text/html', extension='html' ),
               dict( mime_type_name='image/x-icon', extension='ico' ),
               dict( mime_type_name='application/x-java-jnlp-file', extension='jnlp' ),
               dict( mime_type_name='image/jpeg', extension='jpe' ),
               dict( mime_type_name='image/jpeg', extension='jpeg' ),
               dict( mime_type_name='image/jpeg', extension='jpg' ),
               dict( mime_type_name='audio/midi', extension='kar' ),
               dict( mime_type_name='application/pgp-keys', extension='key' ),
               dict( mime_type_name='application/x-kpresenter', extension='kpr' ),
               dict( mime_type_name='application/x-kpresenter', extension='kpt' ),
               dict( mime_type_name='application/x-kspread', extension='ksp' ),
               dict( mime_type_name='application/x-kword', extension='kwd' ),
               dict( mime_type_name='application/x-kword', extension='kwt' ),
               dict( mime_type_name='audio/x-mpegurl', extension='m3u' ),
               dict( mime_type_name='audio/mpeg', extension='m4a' ),
               dict( mime_type_name='audio/midi', extension='mid' ),
               dict( mime_type_name='audio/midi', extension='midi' ),
               dict( mime_type_name='application/x-freemind', extension='mm' ),
               dict( mime_type_name='video/quicktime', extension='mov' ),
               dict( mime_type_name='video/x-sgi-movie', extension='movie' ),
               dict( mime_type_name='audio/mpeg', extension='mp2' ),
               dict( mime_type_name='audio/mpeg', extension='mp3' ),
               dict( mime_type_name='video/mp4', extension='mp4' ),
               dict( mime_type_name='video/mpeg', extension='mpe' ),
               dict( mime_type_name='video/mpeg', extension='mpeg' ),
               dict( mime_type_name='audio/mpeg', extension='mpega' ),
               dict( mime_type_name='video/mpeg', extension='mpg' ),
               dict( mime_type_name='audio/mpeg', extension='mpga' ),
               dict( mime_type_name='application/vnd.oasis.opendocument.database', extension='odb' ),
               dict( mime_type_name='application/vnd.oasis.opendocument.chart', extension='odc' ),
               dict( mime_type_name='application/vnd.oasis.opendocument.formula', extension='odf' ),
               dict( mime_type_name='application/vnd.oasis.opendocument.graphics', extension='odg' ),
               dict( mime_type_name='application/vnd.oasis.opendocument.image', extension='odi' ),
               dict( mime_type_name='application/vnd.oasis.opendocument.text-master', extension='odm' ),
               dict( mime_type_name='application/vnd.oasis.opendocument.presentation', extension='odp' ),
               dict( mime_type_name='application/vnd.oasis.opendocument.spreadsheet', extension='ods' ),
               dict( mime_type_name='application/vnd.oasis.opendocument.text', extension='odt' ),
               dict( mime_type_name='application/ogg', extension='ogg' ),
               dict( mime_type_name='application/vnd.oasis.opendocument.graphics-template', extension='otg' ),
               dict( mime_type_name='application/vnd.oasis.opendocument.text-web', extension='oth' ),
               dict( mime_type_name='application/vnd.oasis.opendocument.presentation-template', extension='otp' ),
               dict( mime_type_name='application/vnd.oasis.opendocument.spreadsheet-template', extension='ots' ),
               dict( mime_type_name='application/vnd.oasis.opendocument.text-template', extension='ott' ),
               dict( mime_type_name='image/x-coreldrawpattern', extension='pat' ),
               dict( mime_type_name='image/x-portable-bitmap', extension='pbm' ),
               dict( mime_type_name='application/x-font', extension='pcf' ),
               dict( mime_type_name='application/x-font', extension='pcf.Z' ),
               dict( mime_type_name='application/pdf', extension='pdf' ),
               dict( mime_type_name='application/x-font', extension='pfa' ),
               dict( mime_type_name='application/x-font', extension='pfb' ),
               dict( mime_type_name='image/x-portable-graymap', extension='pgm' ),
               dict( mime_type_name='application/pgp-signature', extension='pgp' ),
               dict( mime_type_name='image/png', extension='png' ),
               dict( mime_type_name='image/x-portable-anymap', extension='pnm' ),
               dict( mime_type_name='text/plain', extension='pot' ),
               dict( mime_type_name='image/x-portable-pixmap', extension='ppm' ),
               dict( mime_type_name='application/vnd.ms-powerpoint', extension='pps' ),
               dict( mime_type_name='application/vnd.ms-powerpoint', extension='ppt' ),
               dict( mime_type_name='application/postscript', extension='ps' ),
               dict( mime_type_name='image/x-photoshop', extension='psd' ),
               dict( mime_type_name='video/quicktime', extension='qt' ),
               dict( mime_type_name='audio/x-pn-realaudio', extension='ra' ),
               dict( mime_type_name='audio/x-pn-realaudio', extension='ram' ),
               dict( mime_type_name='application/rar', extension='rar' ),
               dict( mime_type_name='application/rdf+xml', extension='rdf' ),
               dict( mime_type_name='image/x-rgb', extension='rgb' ),
               dict( mime_type_name='audio/x-pn-realaudio', extension='rm' ),
               dict( mime_type_name='application/rss+xml', extension='rss' ),
               dict( mime_type_name='text/rtf', extension='rtf' ),
               dict( mime_type_name='text/richtext', extension='rtx' ),
               dict( mime_type_name='application/vnd.stardivision.draw', extension='sda' ),
               dict( mime_type_name='application/vnd.stardivision.calc', extension='sdc' ),
               dict( mime_type_name='application/vnd.stardivision.impress', extension='sdd' ),
               dict( mime_type_name='application/vnd.stardivision.impress', extension='sdp' ),
               dict( mime_type_name='application/vnd.stardivision.writer', extension='sdw' ),
               dict( mime_type_name='application/vnd.stardivision.writer-global', extension='sgl' ),
               dict( mime_type_name='text/html', extension='shtml' ),
               dict( mime_type_name='application/vnd.stardivision.math', extension='smf' ),
               dict( mime_type_name='audio/basic', extension='snd' ),
               dict( mime_type_name='application/vnd.sun.xml.calc.template', extension='stc' ),
               dict( mime_type_name='application/vnd.sun.xml.draw.template', extension='std' ),
               dict( mime_type_name='application/vnd.sun.xml.impress.template', extension='sti' ),
               dict( mime_type_name='application/vnd.sun.xml.writer.template', extension='stw' ),
               dict( mime_type_name='image/svg+xml', extension='svg' ),
               dict( mime_type_name='image/svg+xml', extension='svgz' ),
               dict( mime_type_name='application/x-shockwave-flash', extension='swf' ),
               dict( mime_type_name='application/x-shockwave-flash', extension='swfl' ),
               dict( mime_type_name='application/vnd.sun.xml.calc', extension='sxc' ),
               dict( mime_type_name='application/vnd.sun.xml.draw', extension='sxd' ),
               dict( mime_type_name='application/vnd.sun.xml.writer.global', extension='sxg' ),
               dict( mime_type_name='application/vnd.sun.xml.impress', extension='sxi' ),
               dict( mime_type_name='application/vnd.sun.xml.math', extension='sxm' ),
               dict( mime_type_name='application/vnd.sun.xml.writer', extension='sxw' ),
               dict( mime_type_name='application/x-tar', extension='tar' ),
               dict( mime_type_name='application/x-gtar', extension='taz' ),
               dict( mime_type_name='text/plain', extension='text' ),
               dict( mime_type_name='application/x-gtar', extension='tgz' ),
               dict( mime_type_name='image/tiff', extension='tif' ),
               dict( mime_type_name='image/tiff', extension='tiff' ),
               dict( mime_type_name='text/plain', extension='txt' ),
               dict( mime_type_name='application/vnd.stardivision.writer', extension='vor' ),
               dict( mime_type_name='audio/x-wav', extension='wav' ),
               dict( mime_type_name='audio/x-ms-wma', extension='wma' ),
               dict( mime_type_name='video/x-ms-wmv', extension='wmv' ),
               dict( mime_type_name='image/x-xbitmap', extension='xbm' ),
               dict( mime_type_name='application/vnd.ms-excel', extension='xlb' ),
               dict( mime_type_name='application/vnd.ms-excel', extension='xls' ),
               dict( mime_type_name='application/vnd.ms-excel', extension='xlsx' ),
               dict( mime_type_name='application/vnd.ms-excel', extension='xlt' ),
               dict( mime_type_name='application/xml', extension='xml' ),
               dict( mime_type_name='image/x-xpixmap', extension='xpm' ),
               dict( mime_type_name='application/xml', extension='xsl' ),
               dict( mime_type_name='image/x-xwindowdump', extension='xwd' ),
               dict( mime_type_name='application/zip', extension='zip' ),
    ]
    for v in values:
        q_sql = (db.mime_type.mt_name == v[ 'mime_type_name' ])
        mt = mt_model.select( q_sql ).first()
        mte_model.insert( dict( mime_type_id=mt.id, extension=v[ 'extension' ] ) )


def populate_home_page():
    T = current.T
    from m16e.db import db_tables
    p_model = db_tables.get_table_model( 'page' )
    ts = DT.now()
    p_id = p_model.insert( dict( name='Home',
                                 tagname='home',
                                 title=T( 'Welcome to ChiricoCMS' ),
                                 url_c='default',
                                 url_f='index',
                                 aside_position=db_sets.PANEL_RIGHT,
                                 aside_title=T( 'News' ),
                                 aside_title_en='News',
                                 colspan=3,
                                 rowspan=1,
                                 last_modified_by=1,
                                 page_timestamp=ts,
                                 main_panel_cols=2,
                                 aside_panel_cols=1 ) )
    b_model = db_tables.get_table_model( 'block' )
    txt = '''# %(h1)s

%(p)s

    '''
    h1 = 'Welcome to ChiricoCMS'
    p = 'Once authenticated, click on the top left icon of this panel to edit content.'
    b_model.insert( dict( name='Home main panel',
                          description='Home main panel',
                          page_id=p_id,
                          container=db_sets.BLOCK_CONTAINER_MAIN,
                          blk_order=1,
                          body=txt % dict( h1=T( h1 ), p=T( p ) ),
                          body_en=txt % dict( h1=h1, p=p ),
                          created_on=ts,
                          created_by=1,
                          last_modified_by=1,
                          colspan=2,
                          rowspan=1 ) )
    h1 = 'ChiricoCMS is up'
    p = 'Our site is up and running.\n[+[timestamp]+]'
    b_model.insert( dict( name='News panel',
                          description='News panel',
                          page_id=p_id,
                          container=db_sets.BLOCK_CONTAINER_ASIDE,
                          blk_order=1,
                          body=txt % dict( h1=T( h1 ), p=T( p ) ),
                          body_en=txt % dict( h1=h1, p=p ),
                          created_on=ts,
                          created_by=1,
                          last_modified_by=1,
                          colspan=2,
                          rowspan=1 ) )


def populate_aux_pages():
    T = current.T
    from m16e.db import db_tables
    p_model = db_tables.get_table_model( 'page' )
    ts = DT.now()
    # /about
    p_id = p_model.insert( dict( name='About',
                                 tagname='about',
                                 title=T( 'About us' ),
                                 url_c='about',
                                 url_f='index',
                                 colspan=1,
                                 rowspan=1,
                                 last_modified_by=1,
                                 page_timestamp=ts,
                                 main_panel_cols=1,
                                 aside_panel_cols=1 ) )
    b_model = db_tables.get_table_model( 'block' )
    txt = '''# %(h1)s

%(p)s

    '''
    h1 = 'About us'
    p = 'This is some text describing who we are'
    b_model.insert( dict( name='About panel',
                          description='About panel',
                          page_id=p_id,
                          container=db_sets.BLOCK_CONTAINER_MAIN,
                          blk_order=1,
                          body=txt % dict( h1=T( h1 ), p=T( p ) ),
                          body_en=txt % dict( h1=h1, p=p ),
                          created_on=ts,
                          created_by=1,
                          last_modified_by=1,
                          colspan=2,
                          rowspan=1 ) )
    # /contacts
    p_id = p_model.insert( dict( name='Contacts',
                                 tagname='contacts',
                                 title=T( 'Contacts' ),
                                 url_c='contacts',
                                 url_f='index',
                                 colspan=1,
                                 rowspan=1,
                                 last_modified_by=1,
                                 page_timestamp=ts,
                                 main_panel_cols=1,
                                 aside_panel_cols=1 ) )
    h1 = 'Contacts'
    p = '- E-mail: mail@example.com\n- Address: \n'
    b_model.insert( dict( name='Contacts',
                          description='Contacts panel',
                          page_id=p_id,
                          container=db_sets.BLOCK_CONTAINER_MAIN,
                          blk_order=1,
                          body=txt % dict( h1=T( h1 ), p=T( p ) ),
                          body_en=txt % dict( h1=h1, p=p ),
                          created_on=ts,
                          created_by=1,
                          last_modified_by=1,
                          colspan=1,
                          rowspan=1 ) )
    # /terms_of_use
    p_id = p_model.insert( dict( name='Terms of use',
                                 tagname='terms_of_use',
                                 title=T( 'Terms of use' ),
                                 url_c='about',
                                 url_f='terms_of_use',
                                 colspan=1,
                                 rowspan=1,
                                 last_modified_by=1,
                                 page_timestamp=ts,
                                 main_panel_cols=1,
                                 aside_panel_cols=1 ) )
    h1 = 'Terms of use'
    p = 'In order to use this site you must agree with theese terms.\n'
    b_model.insert( dict( name='Terms of use',
                          description='Terms of use panel',
                          page_id=p_id,
                          container=db_sets.BLOCK_CONTAINER_MAIN,
                          blk_order=1,
                          body=txt % dict( h1=T( h1 ), p=T( p ) ),
                          body_en=txt % dict( h1=h1, p=p ),
                          created_on=ts,
                          created_by=1,
                          last_modified_by=1,
                          colspan=1,
                          rowspan=1 ) )


def populate_pages():
    populate_home_page()
    populate_aux_pages()


def populate():
    from m16e.db import db_tables
    import m16e.db.list_of_tables
    import chirico.db.list_of_tables
    import forum_threads.db.list_of_tables
    db_tables.register_table_list( db, table_list=m16e.db.list_of_tables.TABLE_LIST )
    db_tables.register_table_list( db, table_list=chirico.db.list_of_tables.TABLE_LIST )
    db_tables.register_table_list( db, table_list=forum_threads.db.list_of_tables.TABLE_LIST )

    populate_users()
    populate_mime_types()
    populate_types()
    populate_pages()


def initdb():
    init_auth()
    init_company_info()
    init_app_theme()
    init_attach_type()
    init_mime_type()
    init_unit_type()
    init_mime_type()
    init_long_task()
    init_thread_status()
    init_thread_type()

    init_page()
    init_mime_type_ext()
    init_attach()
    init_app_config()
    init_block()
    init_block_attach()
    init_mail_queue()
    init_mail_recipient()
    init_page_log()
    init_shared_run()
    init_thread()
    init_thread_attach()
    init_thread_msg()
    init_thread_msg_attach()
    init_thread_subscriber()
    init_thread_vote()
    init_user_message()

    populate()


