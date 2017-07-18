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

import mock
from oslo_config import cfg

import aflo.context
import aflo.db
import aflo.tests.utils as test_utils

CONF = cfg.CONF


@mock.patch('oslo_utils.importutils.import_module')
class TestDbUtilities(test_utils.BaseTestCase):
    def setUp(self):
        super(TestDbUtilities, self).setUp()
        self.config(data_api='silly pants')
        self.api = mock.Mock()

    def test_get_api_calls_configure_if_present(self, import_module):
        import_module.return_value = self.api
        self.assertEqual(aflo.db.get_api(), self.api)
        import_module.assert_called_once_with('silly pants')
        self.api.configure.assert_called_once_with()

    def test_get_api_skips_configure_if_missing(self, import_module):
        import_module.return_value = self.api
        del self.api.configure
        self.assertEqual(aflo.db.get_api(), self.api)
        import_module.assert_called_once_with('silly pants')
        self.assertFalse(hasattr(self.api, 'configure'))
