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

import fixtures
import mock
from oslo_db.sqlalchemy import migration
import testtools

from aflo.cmd import manage
from aflo.db import migration as db_migration
from aflo.db.sqlalchemy import api as db_api


class TestManageBase(testtools.TestCase):

    def setUp(self):
        super(TestManageBase, self).setUp()

        def clear_conf():
            manage.CONF.reset()
            manage.CONF.unregister_opt(manage.command_opt)
        clear_conf()
        self.addCleanup(clear_conf)

        self.patcher = mock.patch('aflo.db.sqlalchemy.api.get_engine')
        self.patcher.start()
        self.addCleanup(self.patcher.stop)

    def _main_test_helper(self, argv, func_name=None, *exp_args, **exp_kwargs):
        self.useFixture(fixtures.MonkeyPatch('sys.argv', argv))

        def setup(product_name, version='unknown'):
            pass

        self.useFixture(fixtures.MonkeyPatch(
            'oslo_log.setup', setup))
        manage.main()
        func_name.assert_called_once_with(*exp_args, **exp_kwargs)


class TestLegacyManage(TestManageBase):

    @mock.patch.object(migration, 'db_version')
    def test_legacy_db_version(self, db_version):
        self._main_test_helper(['aflo.cmd.manage', 'db_version'],
                               migration.db_version,
                               db_api.get_engine(),
                               db_migration.MIGRATE_REPO_PATH, 0)

    @mock.patch.object(migration, 'db_sync')
    def test_legacy_db_sync(self, db_sync):
        self._main_test_helper(['aflo.cmd.manage', 'db_sync'],
                               migration.db_sync,
                               db_api.get_engine(),
                               db_migration.MIGRATE_REPO_PATH, None)

    @mock.patch.object(migration, 'db_sync')
    def test_legacy_db_upgrade(self, db_sync):
        self._main_test_helper(['aflo.cmd.manage', 'db_upgrade'],
                               migration.db_sync,
                               db_api.get_engine(),
                               db_migration.MIGRATE_REPO_PATH, None)

    @mock.patch.object(migration, 'db_version_control')
    def test_legacy_db_version_control(self, db_version_control):
        self._main_test_helper(['aflo.cmd.manage', 'db_version_control'],
                               migration.db_version_control,
                               db_api.get_engine(),
                               db_migration.MIGRATE_REPO_PATH, None)

    @mock.patch.object(migration, 'db_sync')
    def test_legacy_db_sync_version(self, db_sync):
        self._main_test_helper(['aflo.cmd.manage', 'db_sync', '20'],
                               migration.db_sync,
                               db_api.get_engine(),
                               db_migration.MIGRATE_REPO_PATH, '20')

    @mock.patch.object(migration, 'db_sync')
    def test_legacy_db_upgrade_version(self, db_sync):
        self._main_test_helper(['aflo.cmd.manage', 'db_upgrade', '20'],
                               migration.db_sync,
                               db_api.get_engine(),
                               db_migration.MIGRATE_REPO_PATH, '20')

    @mock.patch.object(migration, 'db_sync')
    def test_legacy_db_downgrade_version(self, db_sync):
        self._main_test_helper(['aflo.cmd.manage', 'db_downgrade', '20'],
                               migration.db_sync,
                               db_api.get_engine(),
                               db_migration.MIGRATE_REPO_PATH, '20')


class TestManage(TestManageBase):

    @mock.patch.object(migration, 'db_version')
    def test_db_version(self, db_version):
        self._main_test_helper(['aflo.cmd.manage', 'db', 'version'],
                               migration.db_version,
                               db_api.get_engine(),
                               db_migration.MIGRATE_REPO_PATH, 0)

    @mock.patch.object(migration, 'db_sync')
    def test_db_sync(self, db_sync):
        self._main_test_helper(['aflo.cmd.manage', 'db', 'sync'],
                               migration.db_sync,
                               db_api.get_engine(),
                               db_migration.MIGRATE_REPO_PATH, None)

    @mock.patch.object(migration, 'db_sync')
    def test_db_upgrade(self, db_sync):
        self._main_test_helper(['aflo.cmd.manage', 'db', 'upgrade'],
                               migration.db_sync,
                               db_api.get_engine(),
                               db_migration.MIGRATE_REPO_PATH, None)

    @mock.patch.object(migration, 'db_version_control')
    def test_db_version_control(self, db_version_control):
        self._main_test_helper(['aflo.cmd.manage', 'db', 'version_control'],
                               migration.db_version_control,
                               db_api.get_engine(),
                               db_migration.MIGRATE_REPO_PATH, None)

    @mock.patch.object(migration, 'db_sync')
    def test_db_sync_version(self, db_sync):
        self._main_test_helper(['aflo.cmd.manage', 'db', 'sync', '20'],
                               migration.db_sync,
                               db_api.get_engine(),
                               db_migration.MIGRATE_REPO_PATH, '20')

    @mock.patch.object(migration, 'db_sync')
    def test_db_upgrade_version(self, db_sync):
        self._main_test_helper(['aflo.cmd.manage', 'db', 'upgrade', '20'],
                               migration.db_sync,
                               db_api.get_engine(),
                               db_migration.MIGRATE_REPO_PATH, '20')

    @mock.patch.object(migration, 'db_sync')
    def test_db_downgrade_version(self, db_sync):
        self._main_test_helper(['aflo.cmd.manage', 'db', 'downgrade', '20'],
                               migration.db_sync,
                               db_api.get_engine(),
                               db_migration.MIGRATE_REPO_PATH, '20')
