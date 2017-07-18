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

from oslo_serialization import jsonutils
import webob

from aflo.api.middleware import version_negotiation
from aflo.api import versions
from aflo.tests.unit import base


class VersionsTest(base.IsolatedUnitTest):

    """Test the version information returned from the API service."""

    def test_get_version_list(self):
        req = webob.Request.blank('/', base_url='http://127.0.0.1:9293/')
        req.accept = 'application/json'
        self.config(bind_host='127.0.0.1', bind_port=9293)
        res = versions.Controller().index(req)
        self.assertEqual(300, res.status_int)
        self.assertEqual('application/json', res.content_type)
        results = jsonutils.loads(res.body)['versions']
        expected = [
            {
                'id': 'v1.0',
                'status': 'SUPPORTED',
                'links': [{'rel': 'self',
                           'href': 'http://127.0.0.1:9293/v1/'}],
            },
        ]
        self.assertEqual(expected, results)

    def test_get_version_list_public_endpoint(self):
        req = webob.Request.blank('/', base_url='http://127.0.0.1:9293/')
        req.accept = 'application/json'
        self.config(bind_host='127.0.0.1', bind_port=9293,
                    public_endpoint='https://127.0.0.1:9293')
        res = versions.Controller().index(req)
        self.assertEqual(300, res.status_int)
        self.assertEqual('application/json', res.content_type)
        results = jsonutils.loads(res.body)['versions']
        expected = [
            {
                'id': 'v1.0',
                'status': 'SUPPORTED',
                'links': [{'rel': 'self',
                           'href': 'https://127.0.0.1:9293/v1/'}],
            },
        ]
        self.assertEqual(expected, results)


class VersionNegotiationTest(base.IsolatedUnitTest):

    def setUp(self):
        super(VersionNegotiationTest, self).setUp()
        self.middleware = version_negotiation.VersionNegotiationFilter(None)

    def test_request_url_v1(self):
        request = webob.Request.blank('/v1/afloobjs')
        self.middleware.process_request(request)
        self.assertEqual('/v1/afloobjs', request.path_info)

    def test_request_url_v1_0(self):
        request = webob.Request.blank('/v1.0/afloobjs')
        self.middleware.process_request(request)
        self.assertEqual('/v1/afloobjs', request.path_info)

    def test_request_accept_v1(self):
        request = webob.Request.blank('/afloobjs')
        request.headers = {'accept': 'application/vnd.openstack.afloobjs-v1'}
        self.middleware.process_request(request)
        self.assertEqual('/v1/afloobjs', request.path_info)

    def test_request_url_v3_unsupported(self):
        request = webob.Request.blank('/v3/afloobjs')
        resp = self.middleware.process_request(request)
        self.assertIsInstance(resp, versions.Controller)
