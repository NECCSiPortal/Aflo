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

import uuid

from oslo_config import cfg

from aflo.db.sqlalchemy import models as db_models

from aflo.tests.unit import base
from aflo.tests.unit import utils as unit_test_utils
from aflo.tests.unit.v1.tickettemplates import utils as data_util

CONF = cfg.CONF

WF_UUID1 = str(uuid.uuid4())
WF_UUID2 = str(uuid.uuid4())

TT_UUID1 = str(uuid.uuid4())
TT_UUID2 = str(uuid.uuid4())

TK_UUID = str(uuid.uuid4())
WK_UUID = str(uuid.uuid4())


class TestTickettemplatesDeleteAPI(base.WorkflowUnitTest):
    """Test 'Delete a ticket template'"""

    def setUp(self):
        """Establish a clean test environment"""
        super(TestTickettemplatesDeleteAPI, self).setUp()

    def create_fixtures(self):
        super(TestTickettemplatesDeleteAPI, self).create_fixtures()

        # Create delete data
        data_util.create_testdata(db_models, TT_UUID1, WF_UUID1, 0)

        # Create exists data
        data_util.create_testdata(db_models, TT_UUID2, WF_UUID2, 1)
        data_util.create_ticket(db_models, TK_UUID, TT_UUID2)
        data_util.create_workflow(db_models, WK_UUID, TK_UUID)

    def test_delete(self):
        """Test 'Delete ticket template'"""
        # Create a request data
        path = '/tickettemplates/' + TT_UUID1
        req = unit_test_utils.get_fake_request(method='DELETE',
                                               path=path)
        headers = {'x-auth-token': 'user:tenant:admin',
                   'x-user-name': 'user-name',
                   'x-tenant-name': 'tenant-name'}

        for k, v in headers.iteritems():
            req.headers[k] = v

        # Send request.
        res = req.get_response(self.api)

        # Examination of response.
        self.assertEqual(res.status_int, 200)

    def test_delete_no_data_irregular(self):
        """Test 'Delete ticket template'
        Test the operation of the parameter without.
        """
        # Create a request data
        path = '/tickettemplates/'
        req = unit_test_utils.get_fake_request(method='DELETE',
                                               path=path)
        headers = {'x-auth-token': 'user:tenant:admin',
                   'x-user-name': 'user-name',
                   'x-tenant-name': 'tenant-name'}

        for k, v in headers.iteritems():
            req.headers[k] = v

        # Send request.
        res = req.get_response(self.api)

        # Examination of response.
        self.assertEqual(res.status_int, 404)

    def test_delete_not_exists_target_irregular(self):
        """Test 'Delete ticket template'
        Test the operation of not exists ticket template.
        """
        # Create a request data
        path = '/tickettemplates/' + str(uuid.uuid4())
        req = unit_test_utils.get_fake_request(method='DELETE',
                                               path=path)
        headers = {'x-auth-token': 'user:tenant:admin',
                   'x-user-name': 'user-name',
                   'x-tenant-name': 'tenant-name'}

        for k, v in headers.iteritems():
            req.headers[k] = v

        # Send request.
        res = req.get_response(self.api)

        # Examination of response.
        self.assertEqual(res.status_int, 404)

    def test_delete_used_irregular(self):
        """Test 'Delete ticket template'
        Test the operation of the used data in ticket.
        """
        # Create a request data
        path = '/tickettemplates/' + TT_UUID2
        req = unit_test_utils.get_fake_request(method='DELETE',
                                               path=path)
        headers = {'x-auth-token': 'user:tenant:admin',
                   'x-user-name': 'user-name',
                   'x-tenant-name': 'tenant-name'}

        for k, v in headers.iteritems():
            req.headers[k] = v

        # Send request.
        res = req.get_response(self.api)

        # Examination of response.
        self.assertEqual(res.status_int, 403)

    def test_delete_authority_irregular(self):
        """Test 'Delete ticket template'
        Test when it is executed by a user other than the administrator.
        """
        # Create a request data
        path = '/tickettemplates/' + TT_UUID1
        req = unit_test_utils.get_fake_request(method='DELETE',
                                               path=path)
        headers = {'x-auth-token': 'user:tenant:no_auth',
                   'x-user-name': 'user-name',
                   'x-tenant-name': 'tenant-name'}

        for k, v in headers.iteritems():
            req.headers[k] = v

        # Send request.
        res = req.get_response(self.api)

        # Examination of response.
        self.assertEqual(res.status_int, 403)
