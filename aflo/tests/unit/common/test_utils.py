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

import os
import tempfile
import uuid

import webob

from aflo.common import utils
from aflo.tests import utils as test_utils


class TestUtils(test_utils.BaseTestCase):
    """Test routines in aflo.utils"""

    def test_mutating(self):
        class FakeContext(object):
            def __init__(self):
                self.read_only = False

        class Fake(object):
            def __init__(self):
                self.context = FakeContext()

        def fake_function(req, context):
            return 'test passed'

        req = webob.Request.blank('/some_request')
        result = utils.mutating(fake_function)
        self.assertEqual("test passed", result(req, Fake()))

    def test_validate_key_cert_key(self):
        self.config(digest_algorithm='sha256')
        var_dir = os.path.abspath(os.path.join(os.path.dirname(__file__),
                                               '../../', 'var'))
        keyfile = os.path.join(var_dir, 'privatekey.key')
        certfile = os.path.join(var_dir, 'certificate.crt')
        utils.validate_key_cert(keyfile, certfile)

    def test_validate_key_cert_no_private_key(self):
        with tempfile.NamedTemporaryFile('w+') as tmpf:
            self.assertRaises(RuntimeError,
                              utils.validate_key_cert,
                              "/not/a/file", tmpf.name)

    def test_validate_key_cert_cert_cant_read(self):
        with tempfile.NamedTemporaryFile('w+') as keyf:
            with tempfile.NamedTemporaryFile('w+') as certf:
                os.chmod(certf.name, 0)
                self.assertRaises(RuntimeError,
                                  utils.validate_key_cert,
                                  keyf.name, certf.name)

    def test_validate_key_cert_key_cant_read(self):
        with tempfile.NamedTemporaryFile('w+') as keyf:
            with tempfile.NamedTemporaryFile('w+') as keyf:
                os.chmod(keyf.name, 0)
                self.assertRaises(RuntimeError,
                                  utils.validate_key_cert,
                                  keyf.name, keyf.name)

    def test_invalid_digest_algorithm(self):
        self.config(digest_algorithm='fake_algorithm')
        var_dir = os.path.abspath(os.path.join(os.path.dirname(__file__),
                                               '../../', 'var'))
        keyfile = os.path.join(var_dir, 'privatekey.key')
        certfile = os.path.join(var_dir, 'certificate.crt')
        self.assertRaises(ValueError,
                          utils.validate_key_cert,
                          keyfile, certfile)

    def test_valid_hostname(self):
        valid_inputs = ['localhost',
                        'aflo04-a'
                        'G',
                        '528491']

        for input_str in valid_inputs:
            self.assertTrue(utils.is_valid_hostname(input_str))

    def test_valid_hostname_fail(self):
        invalid_inputs = ['localhost.localdomain',
                          '127.0.0.1',
                          u'\u2603',
                          'aflo02.stack42.local']

        for input_str in invalid_inputs:
            self.assertFalse(utils.is_valid_hostname(input_str))

    def test_valid_fqdn(self):
        valid_inputs = ['localhost.localdomain',
                        'aflo02.stack42.local'
                        'aflo04-a.stack47.local',
                        'img83.aflo.xn--penstack-r74e.org']

        for input_str in valid_inputs:
            self.assertTrue(utils.is_valid_fqdn(input_str))

    def test_valid_fqdn_fail(self):
        invalid_inputs = ['localhost',
                          '127.0.0.1',
                          '999.999.999.999',
                          u'\u2603.local',
                          'aflo02.stack42']

        for input_str in invalid_inputs:
            self.assertFalse(utils.is_valid_fqdn(input_str))

    def test_valid_host_port_string(self):
        valid_pairs = ['127.0.0.1:80',
                       '127.0.0.1:65535',
                       '[fe80::a:b:c:d]:9990',
                       'localhost:9990',
                       'localhost.localdomain:9990',
                       'aflo02.stack42.local:1234',
                       'aflo04-a.stack47.local:1234',
                       'img83.aflo.xn--penstack-r74e.org:13080']

        for pair_str in valid_pairs:
            host, port = utils.parse_valid_host_port(pair_str)

            escaped = pair_str.startswith('[')
            expected_host = '%s%s%s' % ('[' if escaped else '', host,
                                        ']' if escaped else '')

            self.assertTrue(pair_str.startswith(expected_host))
            self.assertTrue(port > 0)

            expected_pair = '%s:%d' % (expected_host, port)
            self.assertEqual(expected_pair, pair_str)

    def test_valid_host_port_string_fail(self):
        invalid_pairs = ['',
                         '127.0.0.1',
                         '127.0.0.1:99999',
                         '999.999.999.999:5673',
                         'absurd inputs happen',
                         u'\u2601',
                         u'\u2603:8080',
                         'fe80::1',
                         '[fe80::2]',
                         '<fe80::3>:5673',
                         '[fe80::a:b:c:d]9990',
                         'fe80:a:b:c:d:e:f:1:2:3:4',
                         'fe80:a:b:c:d:e:f:g',
                         'fe80::1:8080',
                         '[fe80:a:b:c:d:e:f:g]:9090',
                         '[a:b:s:u:r:d]:fe80']

        for pair in invalid_pairs:
            self.assertRaises(ValueError,
                              utils.parse_valid_host_port,
                              pair)

    def test_exception_to_str(self):
        class FakeException(Exception):
            def __str__(self):
                raise UnicodeError()

        ret = utils.exception_to_str(Exception('error message'))
        self.assertEqual('error message', ret)

        ret = utils.exception_to_str(Exception('\xa5 error message'))
        self.assertEqual(' error message', ret)

        ret = utils.exception_to_str(FakeException('\xa5 error message'))
        self.assertEqual("Caught '%(exception)s' exception." %
                         {'exception': 'FakeException'}, ret)


class UUIDTestCase(test_utils.BaseTestCase):

    def test_is_uuid_like(self):
        self.assertTrue(utils.is_uuid_like(str(uuid.uuid4())))

    def test_id_is_uuid_like(self):
        self.assertFalse(utils.is_uuid_like(1234567))

    def test_name_is_uuid_like(self):
        self.assertFalse(utils.is_uuid_like('zhongyueluo'))


class DateTestCase(test_utils.BaseTestCase):

    def test_is_date_like(self):
        self.assertTrue(utils.is_date_like('2015-01-20'))

    def test_datetime_is_date_like(self):
        self.assertFalse(utils.is_date_like('2015-01-30T22:50:40+00:00'))

    def test_isnt_date_is_date_like(self):
        self.assertFalse(utils.is_uuid_like('2015-02-29'))
