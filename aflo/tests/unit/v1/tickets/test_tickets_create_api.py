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
from oslo_serialization import jsonutils

from aflo.common import exception
from aflo.db.sqlalchemy import api as db_api
from aflo.db.sqlalchemy import models as db_models

from aflo.tests.unit import base
from aflo.tests.unit import utils as unit_test_utils
from aflo.tests.unit.v1.tickets.broker_stubs.stubs import \
    BrokerStubs as broker_stubs
from aflo.tests.unit.v1.tickets.stubs import Ticket_RpcStubs as stubs
from aflo.tests.unit.v1.tickets import utils as tickets_utils

CONF = cfg.CONF

WF_UUID1 = str(uuid.uuid4())
TT_UUID1 = str(uuid.uuid4())


class TestTicketsCreateAPI(base.WorkflowUnitTest):
    """Do a test of 'Create a new ticket'"""

    def setUp(self):
        """Establish a clean test environment"""
        super(TestTicketsCreateAPI, self).setUp()

    def create_fixtures(self):
        super(TestTicketsCreateAPI, self).create_fixtures()

        w_pattern = db_models.WorkflowPattern()
        w_pattern.id = WF_UUID1
        w_pattern.code = 'wfp_01'
        w_pattern.wf_pattern_contents = tickets_utils.get_dict_contents(
            'wf_pattern_contents_001')
        w_pattern.save()

        t_template = db_models.TicketTemplate()
        t_template.id = TT_UUID1
        t_template.workflow_pattern_id = w_pattern.id
        t_template.template_contents = tickets_utils.get_dict_contents(
            'template_contents_001', '20160627')
        t_template.ticket_type = t_template.template_contents['ticket_type']
        t_template.save()

    def test_create(self):
        """Test of the normal system"""
        # Create a request data
        path = '/tickets'
        req = unit_test_utils.get_fake_request(method='POST',
                                               path=path)
        headers = {'x-auth-token': 'user:tenant:__member__',
                   'x-user-name': 'user-name',
                   'x-tenant-name': 'tenant-name'}
        for k, v in headers.iteritems():
            req.headers[k] = v
        body = {'ticket': {'ticket_template_id': TT_UUID1,
                           'ticket_detail': {'num': 2,
                                             'description': 'test01'},
                           'status_code': 'applied_1st'}}
        req.body = self.serializer.to_json(body)

        # set stubs
        # "stub_fake_call" is a stub in order to omit the queue transmission
        # When you use the "call_info",
        # you can confirm the call arguments of stub
        stubs.stub_fake_cast(self, 'tickets_create')
        param_check_call_info = broker_stubs.stub_fake_param_check(self)
        before_action_call_info = broker_stubs.stub_fake_before_action(self)
        after_action_call_info = broker_stubs.stub_fake_after_action(self)

        # Send request
        res = req.get_response(self.api)

        # Examination of response
        self.assertEqual(res.status_int, 200)
        session = db_api.get_session()
        res_obj = jsonutils.loads(res.body)['ticket']
        objs = session.query(db_models.Workflow).\
            filter_by(ticket_id=res_obj['id']).all()
        self.assertEqual(len(objs), 2)
        self.assertEqual(objs[0]['status'], 1)
        self.assertEqual(objs[0]['status_code'], 'applied_1st')
        self.assertEqual(objs[0]['confirmer_name'], 'user-name')
        self.assertEqual(objs[1]['status'], 0)
        self.assertEqual(objs[1]['status_code'], 'applied_2nd')
        self.assertIsNone(objs[1]['confirmer_name'])

        def _assert_call_info(call_info):
            values = call_info['req_values']
            self.assertEqual(values['owner_id'], 'user')
            self.assertEqual(values['owner_name'], 'user-name')
            self.assertEqual(values['tenant_id'], 'tenant')
            self.assertEqual(values['tenant_name'], 'tenant-name')
            self.assertEqual(values['roles'][0], '__member__')
            self.assertEqual(values['status_code'], 'applied_1st')
            self.assertEqual(values['ticket_detail']['description'], 'test01')
            self.assertEqual(values['ticket_detail']['num'], 2)

        _assert_call_info(param_check_call_info)
        _assert_call_info(before_action_call_info)
        _assert_call_info(after_action_call_info)

    def test_raise_before_brokererror_irregular(self):
        """Test if an error has occurred in the before_broker"""
        # Create a request data
        path = '/tickets'
        req = unit_test_utils.get_fake_request(method='POST',
                                               path=path)
        headers = {'x-auth-token': 'user:tenant:__member__',
                   'x-user-name': 'user-name',
                   'x-tenant-name': 'tenant-name'}
        for k, v in headers.iteritems():
            req.headers[k] = v
        body = {'ticket': {'ticket_template_id': TT_UUID1,
                           'ticket_detail': {},
                           'status_code': 'applied_1st'}}
        req.body = self.serializer.to_json(body)

        # set stubs
        # "stub_fake_call" is a stub in order to omit the queue transmission
        # When you use the "call_info",
        # you can confirm the call arguments of stub
        stubs.stub_fake_cast(self, 'tickets_create')
        broker_stubs.stub_fake_param_check(self)
        broker_stubs.stub_fake_exception_before_action(self)
        broker_stubs.stub_fake_after_action(self)

        # Send request
        self.assertRaises(exception.BrokerError,
                          req.get_response,
                          self.api)

        # Examination of response
        session = db_api.get_session()
        tickets = session.query(db_models.Ticket).\
            order_by(db_models.Ticket.created_at).all()
        objs = session.query(db_models.Workflow).\
            filter_by(ticket_id=tickets[0].id).all()
        error_row = objs[2]

        self.assertEqual(error_row['status'], 1)
        self.assertEqual(error_row['status_code'], 'error')
        self.assertEqual(error_row['confirmer_name'], 'user-name')

    def test_raise_after_brokererror_irregular(self):
        """Test if an error has occurred in the after_broker"""
        # Create a request data
        path = '/tickets'
        req = unit_test_utils.get_fake_request(method='POST',
                                               path=path)
        headers = {'x-auth-token': 'user:tenant:__member__',
                   'x-user-name': 'user-name',
                   'x-tenant-name': 'tenant-name'}
        for k, v in headers.iteritems():
            req.headers[k] = v
        body = {'ticket': {'ticket_template_id': TT_UUID1,
                           'ticket_detail': {},
                           'status_code': 'applied_1st'}}
        req.body = self.serializer.to_json(body)

        # set stubs
        # "stub_fake_call" is a stub in order to omit the queue transmission
        # When you use the "call_info",
        # you can confirm the call arguments of stub
        stubs.stub_fake_cast(self, 'tickets_create')
        broker_stubs.stub_fake_param_check(self)
        broker_stubs.stub_fake_before_action(self)
        broker_stubs.stub_fake_exception_after_action(self)

        # Send request
        self.assertRaises(exception.BrokerError,
                          req.get_response,
                          self.api)

        # Examination of response
        session = db_api.get_session()
        tickets = session.query(db_models.Ticket).\
            order_by(db_models.Ticket.created_at).all()
        objs = session.query(db_models.Workflow).\
            filter_by(ticket_id=tickets[0].id).all()
        error_row = objs[2]

        self.assertEqual(error_row['status'], 1)
        self.assertEqual(error_row['status_code'], 'error')
        self.assertEqual(error_row['confirmer_name'], 'user-name')

    def test_raise_validation_error_irregular(self):
        """Test of validation error"""
        # Create a request data
        path = '/tickets'
        req = unit_test_utils.get_fake_request(method='POST',
                                               path=path)
        headers = {'x-auth-token': 'user:tenant:__member__',
                   'x-user-name': 'user-name',
                   'x-tenant-name': 'tenant-name'}
        for k, v in headers.iteritems():
            req.headers[k] = v
        body = {'ticket': {'ticket_template_id': TT_UUID1,
                           'ticket_detail': {},
                           'status_code': 'applied_1st'}}
        req.body = self.serializer.to_json(body)

        # Send request
        res = req.get_response(self.api)

        # Examination of response
        self.assertEqual(res.status_int, 400)

    def test_raise_role_erroer_irregular(self):
        """Test of authority error"""
        # Create a request data
        path = '/tickets'
        req = unit_test_utils.get_fake_request(method='POST',
                                               path=path)
        headers = {'x-auth-token': 'user:tenant:XXXXX',
                   'x-user-name': 'user-name',
                   'x-tenant-name': 'tenant-name'}
        for k, v in headers.iteritems():
            req.headers[k] = v
        body = {'ticket': {'ticket_template_id': TT_UUID1,
                           'ticket_detail': {},
                           'status_code': 'applied_1st'}}
        req.body = self.serializer.to_json(body)

        # Send request
        res = req.get_response(self.api)

        # Examination of response
        self.assertEqual(res.status_int, 403)
