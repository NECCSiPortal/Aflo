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
    DateTime, String, Integer, TextContract, Boolean, create_tables, drop_tables)  # noqa
from sqlalchemy.schema import (Column, MetaData, Table)


def define_contract_table(meta):
    contractobjs = \
        Table('contract',
              meta,
              Column('contract_id', String(64), primary_key=True),
              Column('region_id', String(255)),
              Column('project_id', String(64)),
              Column('project_name', String(64)),
              Column('catalog_id', String(64)),
              Column('catalog_name', String(128)),
              Column('num', Integer()),
              Column('parent_ticket_template_id', String(64)),
              Column('ticket_template_id', String(64)),
              Column('parent_ticket_template_name', TextContract()),
              Column('ticket_template_name', TextContract()),
              Column('parent_application_kinds_name', TextContract()),
              Column('application_kinds_name', TextContract()),
              Column('cancel_application_id', String(64)),
              Column('application_id', String(64)),
              Column('application_name', String(64)),
              Column('application_date', DateTime()),
              Column('parent_contract_id', String(64)),
              Column('lifetime_start', DateTime()),
              Column('lifetime_end', DateTime()),

              Column('created_at', DateTime(), nullable=False),
              Column('updated_at', DateTime()),
              Column('deleted',
                     Boolean(),
                     nullable=False,
                     default=False,
                     index=True),
              Column('deleted_at', DateTime()),

              Column('expansion_key1', String(255)),
              Column('expansion_key2', String(255)),
              Column('expansion_key3', String(255)),
              Column('expansion_key4', String(255)),
              Column('expansion_key5', String(255)),

              Column('expansion_text', TextContract()),

              mysql_engine='InnoDB',
              extend_existing=True)

    return contractobjs


def upgrade(migrate_engine):
    meta = MetaData()
    meta.bind = migrate_engine
    tables = [define_contract_table(meta)]
    create_tables(tables)


def downgrade(migrate_engine):
    meta = MetaData()
    meta.bind = migrate_engine
    tables = [define_contract_table(meta)]
    drop_tables(tables)
