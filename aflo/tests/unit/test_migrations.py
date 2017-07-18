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

"""
Tests for database migrations. This test case reads the configuration
file /tests/unit/test_migrations.conf for database connection settings
to use in the tests. For each connection found in the config file,
the test case runs a series of test cases to ensure that migrations work
properly both upgrading and downgrading, and that no data loss occurs
if possible.
"""

from __future__ import print_function

from oslo_config import cfg
from oslo_db.sqlalchemy import test_base
from oslo_db.sqlalchemy import test_migrations
# NOTE(jokke): simplified transition to py3, behaves like py2 xrange
import sqlalchemy

from aflo.db import migration
from aflo.db.sqlalchemy import models

from aflo import i18n

_ = i18n._

CONF = cfg.CONF


def index_exist(index, table, engine):
    inspector = sqlalchemy.inspect(engine)
    return index in [i['name'] for i in inspector.get_indexes(table)]


def unique_constraint_exist(constraint, table, engine):
    inspector = sqlalchemy.inspect(engine)
    return constraint in [c['name'] for c in
                          inspector.get_unique_constraints(table)]


class TestMysqlMigrations(test_base.MySQLOpportunisticTestCase):

    def test_mysql_innodb_tables(self):
        migration.db_sync(engine=self.migrate_engine)

        total = self.migrate_engine.execute(
            "SELECT COUNT(*) "
            "FROM information_schema.TABLES "
            "WHERE TABLE_SCHEMA='%s'"
            % self.migrate_engine.url.database)
        self.assertTrue(total.scalar() > 0, "No tables found. Wrong schema?")

        noninnodb = self.migrate_engine.execute(
            "SELECT count(*) "
            "FROM information_schema.TABLES "
            "WHERE TABLE_SCHEMA='%s' "
            "AND ENGINE!='InnoDB' "
            "AND TABLE_NAME!='migrate_version'"
            % self.migrate_engine.url.database)
        count = noninnodb.scalar()
        self.assertEqual(count, 0, "%d non InnoDB tables created" % count)


class TestPostgresqlMigrations(test_base.PostgreSQLOpportunisticTestCase):
    pass


class TestSqliteMigrations(test_base.DbTestCase):
    pass


class ModelsMigrationSyncMixin(object):

    def get_metadata(self):
        return models.BASE.metadata

    def get_engine(self):
        return self.engine

    def db_sync(self, engine):
        migration.db_sync(engine=engine)

    def include_object(self, object_, name, type_, reflected, compare_to):
        if name in ['migrate_version'] and type_ == 'table':
            return False
        return True


class ModelsMigrationsSyncMysql(ModelsMigrationSyncMixin,
                                test_migrations.ModelsMigrationsSync,
                                test_base.MySQLOpportunisticTestCase):
    pass


class ModelsMigrationsSyncPostgres(ModelsMigrationSyncMixin,
                                   test_migrations.ModelsMigrationsSync,
                                   test_base.PostgreSQLOpportunisticTestCase):
    pass


class ModelsMigrationsSyncSQLite(ModelsMigrationSyncMixin,
                                 test_migrations.ModelsMigrationsSync,
                                 test_base.DbTestCase):
    pass
