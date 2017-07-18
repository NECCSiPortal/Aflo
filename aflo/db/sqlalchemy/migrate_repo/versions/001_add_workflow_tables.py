#  Licensed under the Apache License, Version 2.0 (the "License"); you may
#  not use this file except in compliance with the License. You may obtain
#  a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#  WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#  License for the specific language governing permissions and limitations
#  under the License.

from aflo.db.sqlalchemy.migrate_repo.schema import (
    Boolean, DateTime, String, Integer, create_tables, drop_tables)  # noqa
from aflo.db.sqlalchemy import models
from sqlalchemy.schema import (
    Column, ForeignKey, MetaData, Table)


def define_workflow_pattern_table(meta):
    table = Table('workflow_pattern',
                  meta,
                  Column('id',
                         String(36),
                         primary_key=True,
                         nullable=False),
                  Column('code',
                         String(255),
                         nullable=False,
                         index=True),
                  Column('wf_pattern_contents',
                         models.JSONEncodedDict,
                         default={}),
                  Column('created_at', DateTime(), nullable=False),
                  Column('updated_at', DateTime()),
                  Column('deleted_at', DateTime()),
                  Column('deleted',
                         Boolean(),
                         nullable=False,
                         default=False,
                         index=True),
                  mysql_engine='InnoDB',
                  extend_existing=True)

    return table


def define_ticket_template_table(meta):
    table = Table('ticket_template',
                  meta,
                  Column('id',
                         String(36),
                         primary_key=True,
                         nullable=False),
                  Column('ticket_type',
                         String(64),
                         nullable=False),
                  Column('template_contents',
                         models.JSONEncodedDict,
                         default={}),
                  Column('workflow_pattern_id',
                         String(36),
                         ForeignKey('workflow_pattern.id'),
                         nullable=False),
                  Column('created_at', DateTime(), nullable=False),
                  Column('updated_at', DateTime()),
                  Column('deleted_at', DateTime()),
                  Column('deleted',
                         Boolean(),
                         nullable=False,
                         default=False,
                         index=True),
                  mysql_engine='InnoDB',
                  extend_existing=True)

    return table


def define_ticket_table(meta):
    table = Table('ticket',
                  meta,
                  Column('id',
                         String(36),
                         primary_key=True),
                  Column('ticket_template_id',
                         String(36),
                         ForeignKey('ticket_template.id'),
                         nullable=False),
                  Column('ticket_type',
                         String(64),
                         nullable=False),
                  Column('target_id',
                         models.JSONEncodedDict(),
                         default={}),
                  Column('tenant_id', String(36),
                         nullable=False),
                  Column('tenant_name', String(255)),
                  Column('owner_id', String(255)),
                  Column('owner_name', String(255)),
                  Column('owner_at', DateTime()),
                  Column('ticket_detail',
                         models.JSONEncodedDict(),
                         default={}),
                  Column('action_detail',
                         models.JSONEncodedDict(),
                         default={}),
                  Column('created_at', DateTime(), nullable=False),
                  Column('updated_at', DateTime()),
                  Column('deleted_at', DateTime()),
                  Column('deleted',
                         Boolean(),
                         nullable=False,
                         default=False,
                         index=True),
                  mysql_engine='InnoDB',
                  extend_existing=True)

    return table


def define_workflow_table(meta):
    table = Table('workflow',
                  meta,
                  Column('id',
                         String(36),
                         primary_key=True),
                  Column('ticket_id',
                         String(36),
                         ForeignKey('ticket.id'),
                         nullable=False),
                  Column('status',
                         Integer(),
                         nullable=False),
                  Column('status_code',
                         String(64),
                         nullable=False),
                  Column('status_detail',
                         models.JSONEncodedDict(),
                         default={}),
                  Column('target_role', String(512)),
                  Column('confirmer_id', String(255)),
                  Column('confirmer_name', String(255)),
                  Column('confirmed_at', DateTime()),
                  Column('additional_data',
                         models.JSONEncodedDict(),
                         default={}),
                  Column('created_at', DateTime(), nullable=False),
                  Column('updated_at', DateTime()),
                  Column('deleted_at', DateTime()),
                  Column('deleted',
                         Boolean(),
                         nullable=False,
                         default=False,
                         index=True),
                  mysql_engine='InnoDB',
                  extend_existing=True)

    return table


def upgrade(migrate_engine):
    meta = MetaData()
    meta.bind = migrate_engine
    tables = [define_workflow_pattern_table(meta),
              define_ticket_template_table(meta),
              define_ticket_table(meta),
              define_workflow_table(meta)]
    create_tables(tables)


def downgrade(migrate_engine):
    meta = MetaData()
    meta.bind = migrate_engine
    tables = [define_workflow_pattern_table(meta),
              define_ticket_template_table(meta),
              define_ticket_table(meta),
              define_workflow_table(meta)]
    drop_tables(tables)
