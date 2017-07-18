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

from aflo.common import exception
from aflo.common import utils
from aflo.tests import utils as test_utils


class ApiAppExceptionTestCase(test_utils.BaseTestCase):

    def test_default_error_msg(self):
        class FakeApiAppException(exception.ApiAppException):
            message = "default message"

        exc = FakeApiAppException()
        self.assertEqual('default message', utils.exception_to_str(exc))

    def test_specified_error_msg(self):
        msg = exception.ApiAppException('test')
        self.assertIn('test', utils.exception_to_str(msg))

    def test_default_error_msg_with_kwargs(self):
        class FakeApiAppException(exception.ApiAppException):
            message = "default message: %(code)s"

        exc = FakeApiAppException(code=500)
        self.assertEqual("default message: 500", utils.exception_to_str(exc))

    def test_specified_error_msg_with_kwargs(self):
        msg = exception.ApiAppException('test: %(code)s', code=500)
        self.assertIn('test: 500', utils.exception_to_str(msg))

    def test_non_unicode_error_msg(self):
        exc = exception.ApiAppException(str('test'))
        self.assertIsInstance(utils.exception_to_str(exc), str)
