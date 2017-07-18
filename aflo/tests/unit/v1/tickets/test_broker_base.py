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

from oslo_config import cfg

from aflo.common import exception
from aflo.db.sqlalchemy import models as db_models
from aflo.tests.unit import base
from aflo.tests.unit import utils as unit_test_utils
from aflo.tests.unit.v1.tickets.broker_stubs.fake_broker import FakeBroker
from aflo.tests.unit.v1.tickets.broker_stubs.stubs \
    import BrokerStubs as broker_stubs
from aflo.tests.unit.v1.tickets.stubs import Ticket_RpcStubs as stubs
from aflo.tests.unit.v1.tickets import utils as tickets_utils

CONF = cfg.CONF


class TestBrokerBase(base.WorkflowUnitTest):
    """Do a test of 'broker_base'"""

    def create_fixtures(self):
        super(TestBrokerBase, self).create_fixtures()

        self.tickets, self.workflows, self.ticket_teamplate = \
            tickets_utils.create_ticket_for_broker_test(db_models, 'tenant', 0)

    def test_broker_executed(self):
        """Do a test of 'broker_base'
        Check that the 'broker' in all of the timing called
        """

        # Create a request data
        path = '/tickets/%s' % self.tickets.id
        req = unit_test_utils.get_fake_request(method='PUT',
                                               path=path)
        headers = {'x-auth-token': 'user:tenant:director',
                   'x-user-name': 'user-name',
                   'x-tenant-name': 'tenant-name'}
        for k, v in headers.iteritems():
            req.headers[k] = v
        req.body = '{"ticket":{"additional_data": ' \
                   '               {"description": "user applied"},' \
                   '           "last_status_code": "%s",' \
                   '           "last_workflow_id": "%s",' \
                   '           "next_status_code": "%s",' \
                   '           "next_workflow_id": "%s"}}' \
                   % ('applied_1st', self.workflows['applied_1st'].id,
                      'applied_2nd', self.workflows['applied_2nd'].id)

        # set stubs
        # "stub_fake_call" is a stub in order to omit the queue transmission
        # When you use the "call_info",
        # you can confirm the call arguments of stub
        stubs.stub_fake_cast(self, 'tickets_update')
        param_check_call_info = \
            broker_stubs.stub_fake_param_check(self)
        before_action_call_info = \
            broker_stubs.stub_fake_before_action(self)
        after_action_call_info = \
            broker_stubs.stub_fake_after_action(self)

        # Send request
        req.get_response(self.api)

        # Compare the updated data
        def assert_req_values(req_values):
            self.assertEqual(req_values['before_status_code'], 'applied_1st')
            self.assertEqual(req_values['after_status_code'], 'applied_2nd')
        assert_req_values(param_check_call_info['req_values'])
        assert_req_values(before_action_call_info['req_values'])
        assert_req_values(after_action_call_info['req_values'])

    def test_general_param_check(self):
        """Do a test of 'broker_base.general_param_check'
        Don't have input parameters.
        """
        input_values = {'ticket_detail': {
            'number_parameter': 9999,
            'string_parameter': ('a' * 512),
            'hidden_parameter': ('a' * 512),
            'date_parameter': '2016-06-27T00:00:00.000000',
            'email_parameter': 'xxxxx@xxxxx.xxxxx',
            'boolean_parameter': True,
            'select_item_parameter': '0',
            'regular_expression_parameter': '99-xxxxx',
        }}

        handler = self._create_handler()
        handler.general_param_check(**input_values)

    def test_general_param_check_no_parameters(self):
        """Do a test of 'broker_base.general_param_check'
        Don't have input parameters.
        """
        template_contents = self.ticket_teamplate.template_contents
        template_contents["create"]["parameters"] = []
        input_values = {'ticket_detail': {}}

        handler = self._create_handler(template_contents)
        handler.general_param_check(**input_values)

    def test_general_param_check_2byte_string(self):
        """Do a test of 'broker_base.general_param_check'
        Inputted string(2byte) value.
        """
        input_values = {'ticket_detail': {
            'number_parameter': 9999,
            'string_parameter': u'\u5099\u8003'}
        }

        handler = self._create_handler()
        handler.general_param_check(**input_values)

    def test_general_param_check_false_boolean(self):
        """Do a test of 'broker_base.general_param_check'
        Inputted boolean(False) parameters.
        """
        input_values = {'ticket_detail': {
            'number_parameter': 9999,
            'boolean_parameter': False,
        }}

        handler = self._create_handler()
        handler.general_param_check(**input_values)

    def test_general_param_check_required_no_set_error(self):
        """Do a test of 'broker_base.general_param_check'
        Required parameter is empty.
        """
        input_values = {'ticket_detail': {}}

        handler = self._create_handler()
        self.assertRaises(exception.InvalidParameterValue,
                          handler.general_param_check,
                          **input_values)

    def test_general_param_check_date_error(self):
        """Do a test of 'broker_base.general_param_check'
        Date parameter is invalid date string.
        """
        input_values = {'ticket_detail': {
            'number_parameter': 9999,
            'date_parameter': 'abc',
        }}

        handler = self._create_handler()
        self.assertRaises(exception.InvalidParameterValue,
                          handler.general_param_check,
                          **input_values)

    def test_general_param_check_invalid_regular_error(self):
        """Do a test of 'broker_base.general_param_check'
        String parameter invalid string.
        """
        input_values = {'ticket_detail': {
            'number_parameter': 9999,
            'regular_expression_parameter': 'ZZZ',
        }}

        handler = self._create_handler()
        self.assertRaises(exception.InvalidParameterValue,
                          handler.general_param_check,
                          **input_values)

    def test_general_param_check_minimum_length_error(self):
        """Do a test of 'broker_base.general_param_check'
        String parameter less minimum length.
        """
        input_values = {'ticket_detail': {
            'number_parameter': 9999,
            'string_parameter': 'a',
        }}

        handler = self._create_handler()
        self.assertRaises(exception.InvalidParameterValue,
                          handler.general_param_check,
                          **input_values)

    def test_general_param_check_maximum_length_error(self):
        """Do a test of 'broker_base.general_param_check'
        String parameter over maximum length.
        """
        input_values = {'ticket_detail': {
            'number_parameter': 9999,
            'string_parameter': ('a' * 513),
        }}

        handler = self._create_handler()
        self.assertRaises(exception.InvalidParameterValue,
                          handler.general_param_check,
                          **input_values)

    def test_general_param_check_minimum_range_error(self):
        """Do a test of 'broker_base.general_param_check'
        Number parameter less minimum range.
        """
        input_values = {'ticket_detail': {
            'number_parameter': 0,
        }}

        handler = self._create_handler()
        self.assertRaises(exception.InvalidParameterValue,
                          handler.general_param_check,
                          **input_values)

    def test_general_param_check_maximum_range_error(self):
        """Do a test of 'broker_base.general_param_check'
        Number parameter over maximum range.
        """
        input_values = {'ticket_detail': {
            'number_parameter': 10000,
        }}

        handler = self._create_handler()
        self.assertRaises(exception.InvalidParameterValue,
                          handler.general_param_check,
                          **input_values)

    def test_general_param_check_invalid_selected_error(self):
        """Do a test of 'broker_base.general_param_check'
        Select parameter selected not exists values.
        """
        input_values = {'ticket_detail': {
            'number_parameter': 9999,
            'select_item_parameter': 'Z',
        }}

        handler = self._create_handler()
        self.assertRaises(exception.InvalidParameterValue,
                          handler.general_param_check,
                          **input_values)

    def test_general_param_check_invalid_email_error(self):
        """Do a test of 'broker_base.general_param_check'
        Mail parameter invalid string.
        """
        input_values = {'ticket_detail': {
            'number_parameter': 9999,
            'email_parameter': 'ZZZ',
        }}

        handler = self._create_handler()
        self.assertRaises(exception.InvalidParameterValue,
                          handler.general_param_check,
                          **input_values)

    def _create_handler(self, contents=None):
        template_contents = self.ticket_teamplate.template_contents \
            if contents is None else contents
        workflow_contents = None
        create_values = {}

        return FakeBroker(None, template_contents, workflow_contents,
                          **create_values)
