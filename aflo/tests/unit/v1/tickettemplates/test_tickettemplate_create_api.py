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
import uuid

from oslo_config import cfg
from oslo_serialization import jsonutils

from aflo.db.sqlalchemy import models as db_models
from aflo.tests.unit import base
from aflo.tests.unit import utils as unit_test_utils
from aflo.tests.unit.v1.tickettemplates import utils

CONF = cfg.CONF

WF_UUID = str(uuid.uuid4())

WORKFLOW_PATTERN_DIR = utils.WORKFLOW_PATTERN_DIR
TICKET_TEMPLATE_DIR = utils.TICKET_TEMPLATE_DIR


class TestTickettemplatesCreateAPI(base.WorkflowUnitTest):
    """Test 'Create a new ticket template'"""

    def setUp(self):
        """Establish a clean test environment"""
        super(TestTickettemplatesCreateAPI, self).setUp()

    def create_fixtures(self):
        super(TestTickettemplatesCreateAPI, self).create_fixtures()

        wf_pattern_contents = utils.get_dict_contents(
            WORKFLOW_PATTERN_DIR, 'workflow_pattern_contents')

        w_pattern = db_models.WorkflowPattern()
        w_pattern.id = WF_UUID
        w_pattern.code = wf_pattern_contents['wf_pattern_code']
        w_pattern.wf_pattern_contents = wf_pattern_contents
        w_pattern.save()

    def test_create(self):
        """Test 'Create ticket template'"""
        # Create a request data
        path = '/tickettemplates'
        req = unit_test_utils.get_fake_request(method='POST',
                                               path=path)
        headers = {'x-auth-token': 'user:tenant:admin',
                   'x-user-name': 'user-name',
                   'x-tenant-name': 'tenant-name'}

        for k, v in headers.iteritems():
            req.headers[k] = v

        template_contents = utils.get_dict_contents(
            TICKET_TEMPLATE_DIR, 'template_contents', '20160627')

        body = {'tickettemplate': {'template_contents': template_contents}}
        req.body = self.serializer.to_json(body)

        # Send request.
        res = req.get_response(self.api)

        # Examination of response.
        self.assertEqual(res.status_int, 200)
        tickettemplate = jsonutils.loads(res.body)['tickettemplate']

        self.assertIsNotNone(tickettemplate['id'])

        self.assertEqual(tickettemplate['ticket_type'],
                         template_contents['ticket_type'])
        self.assertEqual(tickettemplate['template_contents'],
                         template_contents)
        self.assertEqual(tickettemplate['workflow_pattern_id'],
                         WF_UUID)

        self.assertIsNotNone(tickettemplate['created_at'])
        self.assertIsNotNone(tickettemplate['updated_at'])
        self.assertEqual(tickettemplate['deleted'], False)

    def test_create_contents_no_data_irregular(self):
        """Test 'Create ticket template'
        Test the operation of the parameter without.
        """
        template_contents = ''

        self._test_contents_irregular(template_contents)

    def test_create_contents_max_length_over_irregular(self):
        """Test 'Create ticket template'
        Test the operation of the limit over parameter string.
        """
        template_contents = "".zfill((1024 * 64 + 1))

        self._test_contents_irregular(template_contents)

    def test_create_contents_not_exists_key_irregular(self):
        """Test 'Create ticket template'
        Test the operation of the not exists necessary key.
        """
        change_keys = ['ticket_template_name',
                       'application_kinds_name',
                       'wf_pattern_code',
                       'ticket_type',
                       'first_status_code',
                       'create',
                       'update',
                       'action']

        source_template_contents = utils.get_dict_contents(
            TICKET_TEMPLATE_DIR, 'template_contents', '20160627')

        for change_key in change_keys:
            template_contents = copy.deepcopy(source_template_contents)
            del template_contents[change_key]

            self._test_contents_irregular(template_contents)

    def test_create_contents_not_exists_value_irregular(self):
        """Test 'Create ticket template'
        Test the operation of the not exists necessary key.
        """
        change_keys = ['ticket_template_name',
                       'application_kinds_name',
                       'wf_pattern_code',
                       'ticket_type',
                       'first_status_code',
                       'create',
                       'update',
                       'action']

        source_template_contents = utils.get_dict_contents(
            TICKET_TEMPLATE_DIR, 'template_contents', '20160627')

        for change_key in change_keys:
            template_contents = copy.deepcopy(source_template_contents)
            template_contents[change_key] = None

            self._test_contents_irregular(template_contents)

    def test_create_contents_value_type_error_str_irregular(self):
        """Test 'Create ticket template'
        Test the operation of the invalid value type[str].
        """
        change_keys = ['wf_pattern_code',
                       'first_status_code']

        source_template_contents = utils.get_dict_contents(
            TICKET_TEMPLATE_DIR, 'template_contents', '20160627')

        for change_key in change_keys:
            template_contents = copy.deepcopy(source_template_contents)
            template_contents[change_key] = {'test': 'test'}

            self._test_contents_irregular(template_contents)

    def test_create_contents_value_type_error_name_irregular(self):
        """Test 'Create ticket template'
        Test the operation of the invalid value type[name].
        """
        change_keys = ['ticket_template_name',
                       'application_kinds_name']

        source_template_contents = utils.get_dict_contents(
            TICKET_TEMPLATE_DIR, 'template_contents', '20160627')

        for change_key in change_keys:
            template_contents = copy.deepcopy(source_template_contents)
            del template_contents[change_key]['Default']

            self._test_contents_irregular(template_contents)

    def test_create_contents_value_type_param_empty(self):
        """Test 'Create ticket template'
        Test the operation of the empty param.
        """
        # Create a request data
        path = '/tickettemplates'
        req = unit_test_utils.get_fake_request(method='POST',
                                               path=path)
        headers = {'x-auth-token': 'user:tenant:admin',
                   'x-user-name': 'user-name',
                   'x-tenant-name': 'tenant-name'}

        for k, v in headers.iteritems():
            req.headers[k] = v

        template_contents = utils.get_dict_contents(
            TICKET_TEMPLATE_DIR, 'template_contents', '20160627')
        template_contents['param'] = []

        body = {'tickettemplate': {'template_contents': template_contents}}
        req.body = self.serializer.to_json(body)

        # Send request.
        res = req.get_response(self.api)

        # Examination of response.
        self.assertEqual(res.status_int, 200)

    def test_create_contents_value_type_error_ticket_type_over_irregular(
            self):
        """Test 'Create ticket template'
        Test the operation of the length over ticket type.
        """
        template_contents = utils.get_dict_contents(
            TICKET_TEMPLATE_DIR, 'template_contents', '20160627')
        template_contents['ticket_type'] = "".zfill(64 + 1)

        self._test_contents_irregular(template_contents)

    def test_create_contents_value_type_error_create_param_irregular(self):
        """Test 'Create ticket template'
        Test the operation of the invalid value type[create/parameters].
        """
        template_contents = utils.get_dict_contents(
            TICKET_TEMPLATE_DIR, 'template_contents', '20160627')
        del template_contents['create']['parameters'][0]['label']['Default']

        self._test_contents_irregular(template_contents)

    def test_create_contents_value_type_error_update_param_irregular(self):
        """Test 'Create ticket template'
        Test the operation of the invalid value type[update/parameters].
        """
        template_contents = utils.get_dict_contents(
            TICKET_TEMPLATE_DIR, 'template_contents', '20160627')
        del template_contents['update']['parameters'][0]['label']['Default']

        self._test_contents_irregular(template_contents)

    def test_create_contents_value_type_error_action_class_empty_irregular(
            self):
        """Test 'Create ticket template'
        Test the operation of the empty action handler class.
        """
        template_contents = utils.get_dict_contents(
            TICKET_TEMPLATE_DIR, 'template_contents', '20160627')
        del template_contents['action']['broker_class']

        self._test_contents_irregular(template_contents)

    def test_create_contents_value_type_action_status_empty(self):
        """Test 'Create ticket template'
        Test the operation of the empty action-status.
        """
        # Create a request data
        path = '/tickettemplates'
        req = unit_test_utils.get_fake_request(method='POST',
                                               path=path)
        headers = {'x-auth-token': 'user:tenant:admin',
                   'x-user-name': 'user-name',
                   'x-tenant-name': 'tenant-name'}

        for k, v in headers.iteritems():
            req.headers[k] = v

        template_contents = utils.get_dict_contents(
            TICKET_TEMPLATE_DIR, 'template_contents', '20160627')
        template_contents['action']['broker'] = []

        body = {'tickettemplate': {'template_contents': template_contents}}
        req.body = self.serializer.to_json(body)

        # Send request.
        res = req.get_response(self.api)

        # Examination of response.
        self.assertEqual(res.status_int, 200)

    def test_create_contents_value_type_error_action_status_irregular(self):
        """Test 'Create ticket template'
        Test the operation of the invalid status of action.
        """
        change_keys = ['status',
                       'timing',
                       'validation',
                       'broker_method']

        source_template_contents = utils.get_dict_contents(
            TICKET_TEMPLATE_DIR, 'template_contents', '20160627')

        for change_key in change_keys:
            template_contents = copy.deepcopy(source_template_contents)
            del template_contents['action']['broker'][0][change_key]

            self._test_contents_irregular(template_contents)

    def test_create_contents_value_type_error_action_timing_irregular(self):
        """Test 'Create ticket template'
        Test the operation of the invalid status of action.
        """
        template_contents = utils.get_dict_contents(
            TICKET_TEMPLATE_DIR, 'template_contents', '20160627')
        template_contents['action']['broker'][0]['timing'] = 'aaa'

        self._test_contents_irregular(template_contents)

    def test_create_member_authority_irregular(self):
        """Test 'Create a new ticket template'
        Test when it is executed by a user other than the administrator.
        """
        # Create a request data
        path = '/tickettemplates'
        req = unit_test_utils.get_fake_request(method='POST',
                                               path=path)
        headers = {'x-auth-token': 'user:tenant:no_auth',
                   'x-user-name': 'user-name',
                   'x-tenant-name': 'tenant-name'}
        for k, v in headers.iteritems():
            req.headers[k] = v

        template_contents = utils.get_dict_contents(
            TICKET_TEMPLATE_DIR, 'template_contents', '20160627')
        body = {'tickettemplate': {'template_contents': template_contents}}
        req.body = self.serializer.to_json(body)

        # Send request.
        res = req.get_response(self.api)

        # Examination of response.
        self.assertEqual(res.status_int, 403)

    def _test_contents_irregular(self, template_contents):
        """Test 'Create ticket template'
        :param template_contents: Template contents.
        """
        # Create a request data
        path = '/tickettemplates'
        req = unit_test_utils.get_fake_request(method='POST',
                                               path=path)
        headers = {'x-auth-token': 'user:tenant:admin',
                   'x-user-name': 'user-name',
                   'x-tenant-name': 'tenant-name'}

        for k, v in headers.iteritems():
            req.headers[k] = v

        body = {'tickettemplate': {'template_contents': template_contents}}
        req.body = self.serializer.to_json(body)

        # Send request.
        res = req.get_response(self.api)

        # Examination of response.
        self.assertEqual(res.status_int, 400)

    def test_create_not_exists_workflow_pattern_irregular(self):
        """Test 'Create ticket template'
        Test the operation of the not exists workflow pattern.
        """
        # Create a request data
        path = '/tickettemplates'
        req = unit_test_utils.get_fake_request(method='POST',
                                               path=path)
        headers = {'x-auth-token': 'user:tenant:admin',
                   'x-user-name': 'user-name',
                   'x-tenant-name': 'tenant-name'}

        for k, v in headers.iteritems():
            req.headers[k] = v

        template_contents = utils.get_dict_contents(
            TICKET_TEMPLATE_DIR, 'template_contents', '20160627')
        template_contents['wf_pattern_code'] = 'xxxx'

        body = {'tickettemplate': {'template_contents': template_contents}}
        req.body = self.serializer.to_json(body)

        # Send request.
        res = req.get_response(self.api)

        # Examination of response.
        self.assertEqual(res.status_int, 404)
