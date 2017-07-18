#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.
import sys

from oslo_config import cfg
import six

import aflo.cmd.api
import aflo.common.config
from aflo.common import exception as exc
import aflo.common.wsgi
from aflo.tests import utils as test_utils


CONF = cfg.CONF


class TestApiAppCmd(test_utils.BaseTestCase):

    __argv_backup = None

    def _do_nothing(self, *args, **kwargs):
        pass

    def _raise(self, exc):
        def fake(*args, **kwargs):
            raise exc
        return fake

    def setUp(self):
        super(TestApiAppCmd, self).setUp()
        self.__argv_backup = sys.argv
        sys.argv = ['aflo-api']
        self.stderr = six.StringIO()
        sys.stderr = self.stderr

        self.stubs.Set(aflo.common.config, 'load_paste_app',
                       self._do_nothing)
        self.stubs.Set(aflo.common.wsgi.Server, 'start',
                       self._do_nothing)
        self.stubs.Set(aflo.common.wsgi.Server, 'wait',
                       self._do_nothing)

    def tearDown(self):
        sys.stderr = sys.__stderr__
        sys.argv = self.__argv_backup
        super(TestApiAppCmd, self).tearDown()

    def test_worker_creation_failure(self):
        failure = exc.WorkerCreationFailure(reason='test')
        self.stubs.Set(aflo.common.wsgi.Server, 'start',
                       self._raise(failure))
        exit = self.assertRaises(SystemExit, aflo.cmd.api.main)
        self.assertEqual(2, exit.code)
