# Copyright 2012 OpenStack Foundation
# All Rights Reserved.
#
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

import webob

from aflo.common import config
from aflo.tests import utils as test_utils


class SimpleIterator(object):
    def __init__(self, file_object, chunk_size):
        self.file_object = file_object
        self.chunk_size = chunk_size

    def __iter__(self):
        def read_chunk():
            return self.fobj.read(self.chunk_size)

        chunk = read_chunk()
        while chunk:
            yield chunk
            chunk = read_chunk()
        else:
            raise StopIteration()


class TestMalformedRequest(test_utils.BaseTestCase):
    def setUp(self):
        """Establish a clean test environment"""
        super(TestMalformedRequest, self).setUp()
        self.config(flavor='',
                    group='paste_deploy',
                    config_file='etc/aflo-api-paste.ini')
        self.api = config.load_paste_app('aflo-api')

    def test_redirect_incomplete_url(self):
        """Test ApiApp redirects /v# to /v#/ with correct Location header"""
        req = webob.Request.blank('/v1.0')
        res = req.get_response(self.api)
        self.assertEqual(webob.exc.HTTPFound.code, res.status_int)
        self.assertEqual('http://localhost/v1/', res.location)
