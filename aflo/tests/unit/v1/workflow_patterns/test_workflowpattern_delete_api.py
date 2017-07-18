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
from aflo.tests.unit.v1.workflow_patterns import utils as data_util

CONF = cfg.CONF

WF_UUID1 = str(uuid.uuid4())
WF_UUID2 = str(uuid.uuid4())

TT_UUID = str(uuid.uuid4())


class TestWorkflowPatternDeleteAPI(base.WorkflowUnitTest):
    """Test 'Delete a workflow pattern'"""

    def setUp(self):
        """Establish a clean test environment"""
        super(TestWorkflowPatternDeleteAPI, self).setUp()

    def create_fixtures(self):
        super(TestWorkflowPatternDeleteAPI, self).create_fixtures()

        # Create delete data
        data_util.create_workflow_pattern(db_models, WF_UUID1, 'code1')

        # Create exists data
        data_util.create_workflow_pattern(db_models, WF_UUID2, 'code2')
        data_util.create_ticket_template(db_models, TT_UUID, WF_UUID2)

    def test_delete(self):
        """Test 'Delete a workflow pattern'"""
        # Create a request data
        path = '/workflowpatterns/' + WF_UUID1
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
        """Test 'Delete a workflow pattern'
        Test the operation of the parameter without.
        """
        # Create a request data
        path = '/workflowpatterns/'
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
        """Test 'Delete a workflow pattern'
        Test the operation of not exists workflow pattern.
        """
        # Create a request data
        path = '/workflowpatterns/' + str(uuid.uuid4())
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
        """Test 'Delete a workflow pattern'
        Test the operation of the used data in ticket template.
        """
        # Create a request data
        path = '/workflowpatterns/' + WF_UUID2
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
        """Test 'Delete a workflow pattern'
        Test when it is executed by a user other than the administrator.
        """
        # Create a request data
        path = '/workflowpatterns/' + WF_UUID1
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
