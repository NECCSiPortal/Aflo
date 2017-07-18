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
#

from aflo.db.sqlalchemy.migrate_repo.schema import (
    Boolean, DateTime, String, Text, create_tables, drop_tables)  # noqa
from sqlalchemy.schema import (
    Column, MetaData, Table)


def define_catalog_scope_table(meta):
    table = Table('catalog_scope',
                  meta,
                  Column('id', String(64), primary_key=True),
                  Column('catalog_id', String(64), primary_key=True),
                  Column('scope', String(64), primary_key=True),
                  Column('lifetime_start', DateTime()),
                  Column('lifetime_end', DateTime()),
                  Column('expansion_key1', String(255)),
                  Column('expansion_key2', String(255)),
                  Column('expansion_key3', String(255)),
                  Column('expansion_key4', String(255)),
                  Column('expansion_key5', String(255)),
                  Column('expansion_text', Text(4000)),
                  Column('created_at', DateTime(), nullable=False),
                  Column('updated_at', DateTime()),
                  Column('deleted_at', DateTime()),
                  Column('deleted', Boolean(), nullable=False,
                         default=False, index=True),
                  mysql_engine='InnoDB',
                  extend_existing=True)

    return table


def upgrade(migrate_engine):
    meta = MetaData()
    meta.bind = migrate_engine
    tables = [define_catalog_scope_table(meta)]
    create_tables(tables)


def downgrade(migrate_engine):
    meta = MetaData()
    meta.bind = migrate_engine
    tables = [define_catalog_scope_table(meta)]
    drop_tables(tables)
