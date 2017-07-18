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

import copy
import json
import os
import uuid

from oslo_config import cfg
from oslo_serialization import jsonutils

from aflo.db.sqlalchemy import models as db_models

from aflo.tests.unit import base
from aflo.tests.unit import utils as unit_test_utils

CONF = cfg.CONF

WF_UUID = str(uuid.uuid4())

WORKFLOW_PATTERN_DIR = 'aflo/tests/unit/v1/workflow_patterns/' \
    'operation_definition_files'
TICKET_TEMPLATE_DIR = 'aflo/tests/unit/v1/tickettemplates/' \
    'operation_definition_files'


class TestWorkflowpatternsCreateAPI(base.WorkflowUnitTest):
    """Test 'Create a new workflow pattern'"""

    def _get_dict_contents(self, folder, file_name):
        obj = open(os.path.join(folder, file_name)).read()
        return json.loads(obj)

    def setUp(self):
        """Establish a clean test environment"""
        super(TestWorkflowpatternsCreateAPI, self).setUp()

    def create_fixtures(self):
        super(TestWorkflowpatternsCreateAPI, self).create_fixtures()

        wf_pattern_contents = self._get_dict_contents(
            WORKFLOW_PATTERN_DIR, 'workflow_pattern_contents.json')

        w_pattern = db_models.WorkflowPattern()
        w_pattern.id = WF_UUID
        w_pattern.code = 'exists_wf_pattern_code'
        w_pattern.wf_pattern_contents = wf_pattern_contents
        w_pattern.save()

    def test_create(self):
        """Test 'Create a workflow pattern'"""
        # Create a request data
        path = '/workflowpatterns'
        req = unit_test_utils.get_fake_request(method='POST',
                                               path=path)
        headers = {'x-auth-token': 'user:tenant:admin',
                   'x-user-name': 'user-name',
                   'x-tenant-name': 'tenant-name'}

        for k, v in headers.iteritems():
            req.headers[k] = v

        wf_pattern_contents = self._get_dict_contents(
            WORKFLOW_PATTERN_DIR, 'workflow_pattern_contents.json')

        body = {'workflowpattern':
                {'wf_pattern_contents': wf_pattern_contents}}
        req.body = self.serializer.to_json(body)

        # Send request.
        res = req.get_response(self.api)

        # Examination of response.
        self.assertEqual(res.status_int, 200)
        wofkflowpattern = jsonutils.loads(res.body)['workflowpattern']

        self.assertIsNotNone(wofkflowpattern['id'])

        self.assertEqual(wofkflowpattern['code'],
                         wf_pattern_contents['wf_pattern_code'])
        self.assertEqual(wofkflowpattern['wf_pattern_contents'],
                         wf_pattern_contents)

        self.assertIsNotNone(wofkflowpattern['created_at'])
        self.assertIsNotNone(wofkflowpattern['updated_at'])
        self.assertEqual(wofkflowpattern['deleted'], False)

    def test_create_contents_no_data_irregular(self):
        """Test 'Create a workflow pattern'
        Test the operation of the parameter without.
        """
        wf_pattern_contents = ''

        self._test_contents_irregular(wf_pattern_contents)

    def test_create_contents_max_length_over_irregular(self):
        """Test 'Create a workflow pattern'
        Test the operation of the limit over parameter string.
        """
        wf_pattern_contents = "".zfill((1024 * 64 + 1))

        self._test_contents_irregular(wf_pattern_contents)

    def test_create_contents_not_exists_key_irregular(self):
        """Test 'Create a workflow pattern'
        Test the operation of the not exists necessary key.
        """
        change_keys = ['wf_pattern_code',
                       'status_list']

        source_wf_pattern_contents = self._get_dict_contents(
            WORKFLOW_PATTERN_DIR, 'workflow_pattern_contents.json')

        for change_key in change_keys:
            wf_pattern_contents = copy.deepcopy(source_wf_pattern_contents)
            del wf_pattern_contents[change_key]

            self._test_contents_irregular(wf_pattern_contents)

    def test_create_contents_not_exists_value_irregular(self):
        """Test 'Create a workflow pattern'
        Test the operation of the not exists necessary key.
        """
        change_keys = ['wf_pattern_code',
                       'status_list']

        source_wf_pattern_contents = self._get_dict_contents(
            WORKFLOW_PATTERN_DIR, 'workflow_pattern_contents.json')

        for change_key in change_keys:
            wf_pattern_contents = copy.deepcopy(source_wf_pattern_contents)
            wf_pattern_contents[change_key] = None

            self._test_contents_irregular(wf_pattern_contents)

    def test_create_contents_error_wf_pattern_code_over_irregular(
            self):
        """Test 'Create a workflow pattern'
        Test the operation of the length over workflow pattern code.
        """
        wf_pattern_contents = self._get_dict_contents(
            WORKFLOW_PATTERN_DIR, 'workflow_pattern_contents.json')
        wf_pattern_contents['wf_pattern_code'] = "".zfill(64 + 1)

        self._test_contents_irregular(wf_pattern_contents)

    def test_create_contents_error_status_list_no_data_irregular(self):
        """Test 'Create a workflow pattern'
        Test the operation of the no data type[status_list].
        """
        wf_pattern_contents = self._get_dict_contents(
            WORKFLOW_PATTERN_DIR, 'workflow_pattern_contents.json')
        wf_pattern_contents['status_list'] = []

        self._test_contents_irregular(wf_pattern_contents)

    def test_create_contents_error_status_list_irregular(self):
        """Test 'Create a workflow pattern'
        Test the operation of the invalid key of status.
        """
        change_keys = ['status_code',
                       'status_name',
                       'next_status']

        source_wf_pattern_contents = self._get_dict_contents(
            WORKFLOW_PATTERN_DIR, 'workflow_pattern_contents.json')

        for change_key in change_keys:
            wf_pattern_contents = copy.deepcopy(source_wf_pattern_contents)
            del wf_pattern_contents['status_list'][0][change_key]

            self._test_contents_irregular(wf_pattern_contents)

    def test_create_contents_error_status_name_no_default_irregular(self):
        """Test 'Create a workflow pattern'
        Test the operation of the no data type[status_list].
        """
        wf_pattern_contents = self._get_dict_contents(
            WORKFLOW_PATTERN_DIR, 'workflow_pattern_contents.json')
        del wf_pattern_contents['status_list'][0]['status_name']['Default']

        self._test_contents_irregular(wf_pattern_contents)

    def test_create_exists_workflow_pattern_irregular(self):
        """Test 'Create a workflow pattern'
        Test the operation of the exists workflow pattern.
        """
        # Create a request data
        path = '/workflowpatterns'
        req = unit_test_utils.get_fake_request(method='POST',
                                               path=path)
        headers = {'x-auth-token': 'user:tenant:no_auth',
                   'x-user-name': 'user-name',
                   'x-tenant-name': 'tenant-name'}
        for k, v in headers.iteritems():
            req.headers[k] = v

        wf_pattern_contents = self._get_dict_contents(
            WORKFLOW_PATTERN_DIR, 'workflow_pattern_contents.json')
        wf_pattern_contents['wf_pattern_code'] = 'exists_wf_pattern_code'

        body = {'workflowpattern':
                {'wf_pattern_contents': wf_pattern_contents}}
        req.body = self.serializer.to_json(body)

        # Send request.
        res = req.get_response(self.api)

        # Examination of response.
        self.assertEqual(res.status_int, 403)

    def test_create_member_authority_irregular(self):
        """Test 'Create a new workflow pattern'
        Test when it is executed by a user other than the administrator.
        """
        # Create a request data
        path = '/workflowpatterns'
        req = unit_test_utils.get_fake_request(method='POST',
                                               path=path)
        headers = {'x-auth-token': 'user:tenant:no_auth',
                   'x-user-name': 'user-name',
                   'x-tenant-name': 'tenant-name'}
        for k, v in headers.iteritems():
            req.headers[k] = v

        wf_pattern_contents = self._get_dict_contents(
            WORKFLOW_PATTERN_DIR, 'workflow_pattern_contents.json')
        body = {'workflowpattern':
                {'wf_pattern_contents': wf_pattern_contents}}
        req.body = self.serializer.to_json(body)

        # Send request.
        res = req.get_response(self.api)

        # Examination of response.
        self.assertEqual(res.status_int, 403)

    def _test_contents_irregular(self, wf_pattern_contents):
        """Test 'Create a workflow pattern'
        :param wf_pattern_contents: Workflow pattern contents.
        """
        # Create a request data
        path = '/workflowpatterns'
        req = unit_test_utils.get_fake_request(method='POST',
                                               path=path)
        headers = {'x-auth-token': 'user:tenant:admin',
                   'x-user-name': 'user-name',
                   'x-tenant-name': 'tenant-name'}

        for k, v in headers.iteritems():
            req.headers[k] = v

        body = {'workflowpattern':
                {'wf_pattern_contents': wf_pattern_contents}}
        req.body = self.serializer.to_json(body)

        # Send request.
        res = req.get_response(self.api)

        # Examination of response.
        self.assertEqual(res.status_int, 400)
