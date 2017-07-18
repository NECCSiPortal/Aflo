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

import datetime
import uuid

from oslo_config import cfg

from aflo.common import exception
from aflo.db.sqlalchemy import api as db_api
from aflo.db.sqlalchemy import models as db_models
from aflo.tests.unit import base
import aflo.tests.unit.utils as unit_test_utils
from aflo.tests.unit.v1.tickets.broker_stubs.stubs import \
    BrokerStubs as broker_stubs
from aflo.tests.unit.v1.tickets.stubs import Ticket_RpcStubs as stubs

CONF = cfg.CONF

WF_UUID1 = str(uuid.uuid4())
TT_UUID1 = str(uuid.uuid4())
TT_UUID2 = str(uuid.uuid4())
TT_UUID3 = str(uuid.uuid4())


wf_pattern_contents = {
    "wf_pattern_code": "Three_approver",
    "wf_pattern_name": {"Default": "Two_approver",
                        "ja_JP": "Two_approver_jp"},
    "status_list": [
        {
            "status_code": "none",
            "status_name": {"Default": "none",
                            "ja_JP": "none_jp"},
            "next_status": [
                {
                    "next_status_code": "applied_1st",
                    "grant_role": "__member__"
                }
            ]
        },
        {
            "status_code": "applied_1st",
            "status_name": {"Default": "applied(1/2)",
                            "ja_JP": "applied(1/2)_jp"},
            "next_status": [
                {
                    "next_status_code": "applied_2nd",
                    "grant_role": "director"
                },
                {
                    "next_status_code": "closed",
                    "grant_role": "__member__"
                }
            ]
        },
        {
            "status_code": "applied_2nd",
            "status_name": {"Default": "applied(2/2)",
                            "ja_JP": "applied(2/2)_jp"},
            "next_status": [
                {
                    "next_status_code": "closed",
                    "grant_role": "__member__"
                }
            ]
        },
        {
            "status_code": "closed",
            "status_name": {"Default": "closed",
                            "ja_JP": "closed_jp"},
            "next_status": [{}]
        }
    ]
}
template_contents = {
    "ticket_template_version": "2016-06-27",
    "ticket_template_name": {
        "Default": "CPU and Memory set L (Quota)",
        "ja_JP": "CPU and Memory set L (Quota)_jp"
    },
    "ticket_type": "goods",
    "target_id": "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx",
    "wf_pattern_code": "Three_approver",
    "param": [
        {
            "name": {"Default": "num",
                     "ja_JP": "num_jp"},
            "type": "integer",
            "max_val": "999",
            "min_val": "1",
            "max_length": "",
            "min_length": "",
            "required": "True"
        },
        {
            "name": {"Default": "description",
                     "ja_JP": "description_jp"},
            "type": "string",
            "max_val": "",
            "min_val": "",
            "max_length": "128",
            "min_length": "0",
            "required": "False"
        }
    ],
    "action": {
        "broker_class":
        "aflo.tests.unit.v1.tickets.broker_stubs.fake_broker.FakeBroker",
        "broker": [
            {
                "status": "applied_1st",
                "timing": "before",
                "validation": "param_check",
                "broker_method": "before_action"
            },
            {
                "status": "applied_1st",
                "timing": "after",
                "broker_method": "after_action"
            },
            {
                "status": "applied_2nd",
                "timing": "before",
                "validation": "param_check",
                "broker_method": "before_action"
            },
            {
                "status": "applied_2nd",
                "timing": "after",
                "broker_method": "after_action"
            },
            {
                "status": "closed",
                "timing": "before",
                "validation": "param_check",
                "broker_method": "before_action"
            },
            {
                "status": "closed",
                "timing": "after",
                "broker_method": "after_action"
            }
        ]
    }
}
template_contents_message_check = {
    "ticket_template_version": "2016-06-27",
    "ticket_template_name": {
        "Default": "CPU and Memory set L (Quota)",
        "ja_JP": "CPU and Memory set L (Quota)_jp"
    },
    "ticket_type": "goods",
    "target_id": "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx",
    "wf_pattern_code": "Three_approver",
    "param": [
        {
            "name": {"Default": "num",
                     "ja_JP": "num_jp"},
            "type": "integer",
            "max_val": "999",
            "min_val": "1",
            "max_length": "",
            "min_length": "",
            "required": "True"
        },
        {
            "name": {"Default": "description",
                     "ja_JP": "description_jp"},
            "type": "string",
            "max_val": "",
            "min_val": "",
            "max_length": "128",
            "min_length": "0",
            "required": "False"
        }
    ],
    "action": {
        "broker_class":
        "aflo.tests.unit.v1.tickets.broker_stubs.fake_broker.FakeBroker",
        "broker": [
            {
                "status": "applied_1st",
                "timing": "before",
                "validation": "param_check",
                "broker_method": "before_action"
            },
            {
                "status": "applied_1st",
                "timing": "after",
                "broker_method": "after_action"
            },
            {
                "status": "applied_2nd",
                "timing": "before",
                "validation": "param_check",
                "broker_method": "before_action"
            },
            {
                "status": "applied_2nd",
                "timing": "after",
                "broker_method": "after_action"
            },
            {
                "status": "closed",
                "timing": "before",
                "validation": "param_check",
                "broker_method": "before_action"
            },
            {
                "status": "closed",
                "timing": "after",
                "broker_method": "after_action"
            }
        ]
    }
}
template_contents_valid_catalog_check = {
    "ticket_template_version": "2016-06-27",
    "ticket_template_name": {
        "Default": "CPU and Memory set L (Quota)",
        "ja_JP": "CPU and Memory set L (Quota)_jp"
    },
    "ticket_type": "goods",
    "target_id": "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx",
    "wf_pattern_code": "Three_approver",
    "param": [
        {
            "name": {"Default": "num",
                     "ja_JP": "num_jp"},
            "type": "integer",
            "max_val": "999",
            "min_val": "1",
            "max_length": "",
            "min_length": "",
            "required": "True"
        },
        {
            "name": {"Default": "description",
                     "ja_JP": "description_jp"},
            "type": "string",
            "max_val": "",
            "min_val": "",
            "max_length": "128",
            "min_length": "0",
            "required": "False"
        }
    ],
    "action": {
        "broker_class":
        "aflo.tests.unit.v1.tickets.broker_stubs.fake_broker.FakeBroker",
        "broker": [
            {
                "status": "applied_1st",
                "timing": "before",
                "validation": "valid_catalog_check",
                "broker_method": "before_action"
            },
            {
                "status": "applied_1st",
                "timing": "after",
                "broker_method": "after_action"
            },
            {
                "status": "applied_2nd",
                "timing": "before",
                "validation": "valid_catalog_check",
                "broker_method": "before_action"
            },
            {
                "status": "applied_2nd",
                "timing": "after",
                "broker_method": "after_action"
            },
            {
                "status": "closed",
                "timing": "before",
                "validation": "valid_catalog_check",
                "broker_method": "before_action"
            },
            {
                "status": "closed",
                "timing": "after",
                "broker_method": "after_action"
            }
        ]
    }
}


class TestTicketsUpdateAPI(base.WorkflowUnitTest):
    """Do a test of 'Update ticket'"""

    def setUp(self):
        """Establish a clean test environment"""
        super(TestTicketsUpdateAPI, self).setUp()

    def create_fixtures(self):
        super(TestTicketsUpdateAPI, self).create_fixtures()

        w_pattern = db_models.WorkflowPattern()
        w_pattern.id = WF_UUID1
        w_pattern.code = 'wfp_01'
        w_pattern.wf_pattern_contents = wf_pattern_contents
        w_pattern.save()

        t_template = db_models.TicketTemplate()
        t_template.id = TT_UUID1
        t_template.ticket_type = template_contents['ticket_type']
        t_template.workflow_pattern_id = w_pattern.id
        t_template.template_contents = template_contents
        t_template.save()

        t_template = db_models.TicketTemplate()
        t_template.id = TT_UUID2
        t_template.ticket_type = \
            template_contents_message_check['ticket_type']
        t_template.workflow_pattern_id = w_pattern.id
        t_template.template_contents = template_contents_message_check
        t_template.save()

        t_template = db_models.TicketTemplate()
        t_template.id = TT_UUID3
        t_template.ticket_type = \
            template_contents_valid_catalog_check['ticket_type']
        t_template.workflow_pattern_id = w_pattern.id
        t_template.template_contents = template_contents_valid_catalog_check
        t_template.save()

        # for test_raise_brokererror_irregular
        self.tickets0, self.t0_workflows = \
            self._create_ticket_for_update(TT_UUID1)
        # for test_update_api_1st_approval
        self.tickets1, self.t1_workflows = \
            self._create_ticket_for_update(TT_UUID1)
        # for test_update_api_final_approval
        self.tickets2, self.t2_workflows = \
            self._create_ticket_for_update(TT_UUID1)
        self.t2_workflow1 = self.t2_workflows['applied_1st']
        self.t2_workflow1.status = 2
        self.t2_workflow1.confirmer_id = 'dummy_confirmer_id'
        self.t2_workflow1.confirmer_name = 'dummy_confirmer_name'
        self.t2_workflow1.confirmed_at = datetime.date(2015, 1, 1)
        self.t2_workflow1.save()
        self.t2_workflow2 = self.t2_workflows['applied_2nd']
        self.t2_workflow2.status = 1
        self.t2_workflow2.confirmer_id = 'dummy_confirmer_id'
        self.t2_workflow2.confirmer_name = 'dummy_confirmer_name'
        self.t2_workflow2.confirmed_at = datetime.date(2015, 1, 2)
        self.t2_workflow2.save()
        # for test_update_api_closed_data_update_irregular
        #     test_update_api_already_updated_irregular
        self.tickets3, self.t3_workflows = \
            self._create_ticket_for_update(TT_UUID1)
        self.t3_workflow1 = self.t3_workflows['applied_1st']
        self.t3_workflow1.status = 2
        self.t3_workflow1.confirmer_id = 'dummy_confirmer_id'
        self.t3_workflow1.confirmer_name = 'dummy_confirmer_name'
        self.t3_workflow1.confirmed_at = datetime.date(2015, 1, 1)
        self.t3_workflow1.save()
        self.t3_workflow2 = self.t3_workflows['applied_2nd']
        self.t3_workflow2.status = 2
        self.t3_workflow2.confirmer_id = 'dummy_confirmer_id'
        self.t3_workflow2.confirmer_name = 'dummy_confirmer_name'
        self.t3_workflow2.confirmed_at = datetime.date(2015, 1, 2)
        self.t3_workflow2.save()
        self.t3_workflow3 = self.t3_workflows['closed']
        self.t3_workflow3.status = 1
        self.t3_workflow3.confirmer_id = 'dummy_confirmer_id'
        self.t3_workflow3.confirmer_name = 'dummy_confirmer_name'
        self.t3_workflow3.confirmed_at = datetime.date(2015, 1, 2)
        self.t3_workflow3.save()
        # for test_update_api_can_not_update_other_tenant
        self.tickets4, self.t4_workflows = \
            self._create_ticket_for_update(TT_UUID1)
        self.t4_workflow1 = self.t4_workflows['applied_1st']
        self.t4_workflow1.status = 2
        self.t4_workflow1.confirmer_id = 'dummy_confirmer_id'
        self.t4_workflow1.confirmer_name = 'dummy_confirmer_name'
        self.t4_workflow1.confirmed_at = datetime.date(2015, 1, 1)
        self.t4_workflow1.save()
        self.t4_workflow2 = self.t4_workflows['applied_2nd']
        self.t4_workflow2.status = 1
        self.t4_workflow2.confirmer_id = 'dummy_confirmer_id'
        self.t4_workflow2.confirmer_name = 'dummy_confirmer_name'
        self.t4_workflow2.confirmed_at = datetime.date(2015, 1, 2)
        self.t4_workflow2.save()
        # for test_raise_validation_error_irregular_message_check
        self.tickets5, self.t5_workflows = \
            self._create_ticket_for_update(TT_UUID2)
        # for test_update_api_1st_approval_message_check
        self.tickets6, self.t6_workflows = \
            self._create_ticket_for_update(TT_UUID2)
        # for test_update_api_final_approval_message_check
        self.tickets7, self.t7_workflows = \
            self._create_ticket_for_update(TT_UUID2)
        self.t7_workflow1 = self.t7_workflows['applied_1st']
        self.t7_workflow1.status = 2
        self.t7_workflow1.confirmer_id = 'dummy_confirmer_id'
        self.t7_workflow1.confirmer_name = 'dummy_confirmer_name'
        self.t7_workflow1.confirmed_at = datetime.date(2015, 1, 1)
        self.t7_workflow1.save()
        self.t7_workflow2 = self.t7_workflows['applied_2nd']
        self.t7_workflow2.status = 1
        self.t7_workflow2.confirmer_id = 'dummy_confirmer_id'
        self.t7_workflow2.confirmer_name = 'dummy_confirmer_name'
        self.t7_workflow2.confirmed_at = datetime.date(2015, 1, 2)
        self.t7_workflow2.save()
        # for test_raise_validation_error_irregular_valid_catalog_check
        self.tickets8, self.t8_workflows = self._create_ticket_for_update(
            TT_UUID3)
        # for test_update_api_1st_approval_valid_catalog_check
        self.tickets9, self.t9_workflows = self._create_ticket_for_update(
            TT_UUID3)
        # for test_update_api_final_approval_valid_catalog_check
        self.tickets10, self.t10_workflows = self._create_ticket_for_update(
            TT_UUID3)
        self.t10_workflow1 = self.t10_workflows['applied_1st']
        self.t10_workflow1.status = 2
        self.t10_workflow1.confirmer_id = 'dummy_confirmer_id'
        self.t10_workflow1.confirmer_name = 'dummy_confirmer_name'
        self.t10_workflow1.confirmed_at = datetime.date(2015, 1, 1)
        self.t10_workflow1.save()
        self.t10_workflow2 = self.t10_workflows['applied_2nd']
        self.t10_workflow2.status = 1
        self.t10_workflow2.confirmer_id = 'dummy_confirmer_id'
        self.t10_workflow2.confirmer_name = 'dummy_confirmer_name'
        self.t10_workflow2.confirmed_at = datetime.date(2015, 1, 2)
        self.t10_workflow2.save()

    def _create_ticket_for_update(self, ticket_template_id):
        """Create ticket and workflows"""
        t_uuid = str(uuid.uuid4())

        ticket = db_models.Ticket(id=t_uuid,
                                  ticket_template_id=ticket_template_id,
                                  target_id='dummy',
                                  ticket_type='goods',
                                  tenant_id='tenant',
                                  owner_id='dummy_owner_id',
                                  owner_name='dummy_owner_name',
                                  owner_at=datetime.date(2015, 1, 1),
                                  ticket_detail={'description': 'ticket'},
                                  action_detail=template_contents['action'])
        ticket.save()

        workflows = {}
        for status_detail in wf_pattern_contents['status_list']:
            if 'none' == status_detail['status_code']:
                continue
            elif 'applied_1st' == status_detail['status_code']:
                status = 1
                confirmer_id = 'dummy_confirmer_id'
                confirmer_name = 'dummy_confirmer_name'
                confirmed_at = datetime.date(2015, 1, 1)
            else:
                status = 0
                confirmer_id = None
                confirmer_name = None
                confirmed_at = None

            workflow = \
                db_models.Workflow(id=str(uuid.uuid4()),
                                   ticket_id=t_uuid,
                                   status=status,
                                   status_code=status_detail['status_code'],
                                   status_detail=status_detail,
                                   target_role='none',
                                   confirmer_id=confirmer_id,
                                   confirmer_name=confirmer_name,
                                   confirmed_at=confirmed_at,
                                   additional_data={})
            workflow.save()
            workflows[status_detail['status_code']] = workflow

        return ticket, workflows

    def test_raise_before_brokererror_irregular(self):
        """Test if an error has occurred in the before_broker"""
        # Create a request data
        path = '/tickets/%s' % self.tickets0.id
        req = unit_test_utils.get_fake_request(method='PUT',
                                               path=path)
        headers = {'x-auth-token': 'user:tenant:director',
                   'x-user-name': 'user-name',
                   'x-tenant-name': 'tenant-name'}
        for k, v in headers.iteritems():
            req.headers[k] = v

        workflows = self.t0_workflows
        body = {'ticket': {'additional_data': {'description': 'user applied'},
                           'last_status_code': 'applied_1st',
                           'last_workflow_id': workflows['applied_1st'].id,
                           'next_status_code': 'applied_2nd',
                           'next_workflow_id': workflows['applied_2nd'].id}}
        req.body = self.serializer.to_json(body)

        # set stubs
        # "stub_fake_call" is a stub in order to omit the queue transmission
        # When you use the "call_info",
        # you can confirm the call arguments of stub
        stubs.stub_fake_cast(self, 'tickets_update')
        broker_stubs.stub_fake_param_check(self)
        broker_stubs.stub_fake_exception_before_action(self)
        broker_stubs.stub_fake_after_action(self)

        # Send request
        self.assertRaises(exception.BrokerError,
                          req.get_response,
                          self.api)

        # Examination of response
        session = db_api.get_session()
        objs = session.query(db_models.Workflow).\
            filter_by(ticket_id=self.tickets0.id).all()
        error_row = objs[3]
        self.assertEqual(error_row['status'], 1)
        self.assertEqual(error_row['status_code'], 'error')
        self.assertEqual(error_row['confirmer_name'], 'user-name')

    def test_raise_after_brokererror_irregular(self):
        """Test if an error has occurred in the after_broker"""
        # Create a request data
        path = '/tickets/%s' % self.tickets0.id
        req = unit_test_utils.get_fake_request(method='PUT',
                                               path=path)
        headers = {'x-auth-token': 'user:tenant:director',
                   'x-user-name': 'user-name',
                   'x-tenant-name': 'tenant-name'}
        for k, v in headers.iteritems():
            req.headers[k] = v

        workflows = self.t0_workflows
        body = {'ticket': {'additional_data': {'description': 'user applied'},
                           'last_status_code': 'applied_1st',
                           'last_workflow_id': workflows['applied_1st'].id,
                           'next_status_code': 'applied_2nd',
                           'next_workflow_id': workflows['applied_2nd'].id}}
        req.body = self.serializer.to_json(body)

        # set stubs
        # "stub_fake_call" is a stub in order to omit the queue transmission
        # When you use the "call_info",
        # you can confirm the call arguments of stub
        stubs.stub_fake_cast(self, 'tickets_update')
        broker_stubs.stub_fake_param_check(self)
        broker_stubs.stub_fake_before_action(self)
        broker_stubs.stub_fake_exception_after_action(self)

        # Send request
        self.assertRaises(exception.BrokerError,
                          req.get_response,
                          self.api)

        # Examination of response
        session = db_api.get_session()
        objs = session.query(db_models.Workflow).\
            filter_by(ticket_id=self.tickets0.id).all()
        error_row = objs[1]
        self.assertEqual(error_row['status'], 2)
        self.assertEqual(error_row['status_code'], 'applied_2nd')
        self.assertEqual(error_row['confirmer_name'], 'user-name')
        error_row = objs[3]
        self.assertEqual(error_row['status'], 1)
        self.assertEqual(error_row['status_code'], 'error')
        self.assertEqual(error_row['confirmer_name'], 'user-name')

    def test_raise_validation_error_irregular(self):
        """Test of validation error"""
        # Create a request data
        path = '/tickets/%s' % self.tickets0.id
        req = unit_test_utils.get_fake_request(method='PUT',
                                               path=path)
        headers = {'x-auth-token': 'user:tenant:director',
                   'x-user-name': 'user-name',
                   'x-tenant-name': 'tenant-name'}
        for k, v in headers.iteritems():
            req.headers[k] = v

        workflows = self.t0_workflows
        body = {'ticket': {'additional_data': {'description': 'user applied'},
                           'last_status_code': 'applied_1st',
                           'last_workflow_id': workflows['applied_1st'].id,
                           'next_status_code': 'applied_2nd',
                           'next_workflow_id': workflows['applied_2nd'].id}}
        req.body = self.serializer.to_json(body)

        # set stubs
        # "stub_fake_call" is a stub in order to omit the queue transmission
        # When you use the "call_info",
        # you can confirm the call arguments of stub
        broker_stubs.stub_fake_exception_param_check(self)

        # Send request
        res = req.get_response(self.api)

        # Examination of response
        self.assertEqual(res.status_int, 400)

    def test_raise_validation_error_irregular_message_check(self):
        """Test of validation error(message check)"""
        # Create a request data
        path = '/tickets/%s' % self.tickets5.id
        req = unit_test_utils.get_fake_request(method='PUT',
                                               path=path)
        headers = {'x-auth-token': 'user:tenant:director',
                   'x-user-name': 'user-name',
                   'x-tenant-name': 'tenant-name'}
        for k, v in headers.iteritems():
            req.headers[k] = v

        workflows = self.t5_workflows
        body = {'ticket': {'additional_data': {'description': 'user applied'},
                           'last_status_code': 'applied_1st',
                           'last_workflow_id': workflows['applied_1st'].id,
                           'next_status_code': 'applied_2nd',
                           'next_workflow_id': workflows['applied_2nd'].id}}
        req.body = self.serializer.to_json(body)

        # set stubs
        # "stub_fake_call" is a stub in order to omit the queue transmission
        # When you use the "call_info",
        # you can confirm the call arguments of stub
        broker_stubs.stub_fake_exception_message_check(self)

        # Send request
        res = req.get_response(self.api)

        # Examination of response
        self.assertEqual(res.status_int, 400)

    def test_raise_validation_error_irregular_valid_catalog_check(self):
        """Test of validation error(valid catalog check)"""
        # Create a request data
        path = '/tickets/%s' % self.tickets8.id
        req = unit_test_utils.get_fake_request(method='PUT',
                                               path=path)
        headers = {'x-auth-token': 'user:tenant:director',
                   'x-user-name': 'user-name',
                   'x-tenant-name': 'tenant-name'}
        for k, v in headers.iteritems():
            req.headers[k] = v

        workflows = self.t8_workflows
        body = {'ticket': {'additional_data': {'description': 'user applied'},
                           'last_status_code': 'applied_1st',
                           'last_workflow_id': workflows['applied_1st'].id,
                           'next_status_code': 'applied_2nd',
                           'next_workflow_id': workflows['applied_2nd'].id}}
        req.body = self.serializer.to_json(body)

        # set stubs
        # "stub_fake_call" is a stub in order to omit the queue transmission
        # When you use the "call_info",
        # you can confirm the call arguments of stub
        broker_stubs.stub_fake_exception_valid_catalog_check(self)

        # Send request
        self.assertRaises(exception.NotFound,
                          req.get_response,
                          self.api)

    def test_raise_role_erroer_irregular(self):
        """Test of authority error"""
        # Create a request data
        path = '/tickets/%s' % self.tickets0.id
        req = unit_test_utils.get_fake_request(method='PUT',
                                               path=path)
        headers = {'x-auth-token': 'user:tenant:XXXXX',
                   'x-user-name': 'user-name',
                   'x-tenant-name': 'tenant-name'}
        for k, v in headers.iteritems():
            req.headers[k] = v

        workflows = self.t0_workflows
        body = {'ticket': {'additional_data': {'description': 'user applied'},
                           'last_status_code': 'applied_1st',
                           'last_workflow_id': workflows['applied_1st'].id,
                           'next_status_code': 'applied_2nd',
                           'next_workflow_id': workflows['applied_2nd'].id}}
        req.body = self.serializer.to_json(body)

        # set stubs
        # "stub_fake_call" is a stub in order to omit the queue transmission
        # When you use the "call_info",
        # you can confirm the call arguments of stub
        broker_stubs.stub_fake_param_check(self)

        # Send request
        res = req.get_response(self.api)

        # Examination of response
        self.assertEqual(res.status_int, 403)

    def test_update_api_1st_approval(self):
        """Do a test of 'Update ticket'
        The test for the first approval
        """
        # Create a request data
        path = '/tickets/%s' % self.tickets1.id
        req = unit_test_utils.get_fake_request(method='PUT',
                                               path=path)
        headers = {'x-auth-token': 'user:tenant:director',
                   'x-user-name': 'user-name',
                   'x-tenant-name': 'tenant-name'}
        for k, v in headers.iteritems():
            req.headers[k] = v
        workflows = self.t1_workflows
        body = {'ticket': {'additional_data': {'description': 'user applied'},
                           'last_status_code': 'applied_1st',
                           'last_workflow_id': workflows['applied_1st'].id,
                           'next_status_code': 'applied_2nd',
                           'next_workflow_id': workflows['applied_2nd'].id}}
        req.body = self.serializer.to_json(body)

        # set stubs
        # "stub_fake_call" is a stub in order to omit the queue transmission
        # When you use the "call_info",
        # you can confirm the call arguments of stub
        stubs.stub_fake_cast(self, 'tickets_update')
        param_check_call_info = broker_stubs.stub_fake_param_check(self)
        before_action_call_info = broker_stubs.stub_fake_before_action(self)
        after_action_call_info = broker_stubs.stub_fake_after_action(self)

        # Send request
        req.get_response(self.api)

        # Compare the updated data
        session = db_api.get_session()
        workflows = session.query(db_models.Workflow).\
            filter_by(ticket_id=self.tickets1.id).all()
        for wf in workflows:
            if wf.id == self.t1_workflows['applied_1st'].id:
                self.assertEqual(wf.status, 2)
                self.assertEqual(wf.confirmer_id, 'dummy_confirmer_id')
                self.assertEqual(wf.confirmer_name, 'dummy_confirmer_name')
                self.assertIsNotNone(wf.confirmed_at)
            elif wf.id == self.t1_workflows['applied_2nd'].id:
                self.assertEqual(wf.status, 1)
                self.assertEqual(wf.confirmer_id, 'user')
                self.assertEqual(wf.confirmer_name, 'user-name')
                self.assertIsNotNone(wf.confirmed_at)
            else:
                self.assertEqual(wf.status, 0)
                self.assertIsNone(wf.confirmer_id)
                self.assertIsNone(wf.confirmer_name)
                self.assertIsNone(wf.confirmed_at)

        def _assert_call_info(call_info):
            values = call_info['req_values']
            self.assertEqual(values['confirmer_id'], 'user')
            self.assertEqual(values['confirmer_name'], 'user-name')
            self.assertEqual(values['tenant_id'], 'tenant')
            self.assertEqual(values['tenant_name'], 'tenant-name')
            self.assertEqual(values['roles'][0], 'director')
            self.assertEqual(values['last_status_code'], 'applied_1st')
            self.assertEqual(values['next_status_code'], 'applied_2nd')
            self.assertEqual(values['additional_data']['description'],
                             'user applied')

        _assert_call_info(param_check_call_info)
        _assert_call_info(before_action_call_info)
        _assert_call_info(after_action_call_info)

    def test_update_api_1st_approval_message_check(self):
        """Do a test of 'Update ticket'
        The test for the first approval(message check)
        """
        # Create a request data
        path = '/tickets/%s' % self.tickets6.id
        req = unit_test_utils.get_fake_request(method='PUT',
                                               path=path)
        headers = {'x-auth-token': 'user:tenant:director',
                   'x-user-name': 'user-name',
                   'x-tenant-name': 'tenant-name'}
        for k, v in headers.iteritems():
            req.headers[k] = v
        workflows = self.t6_workflows
        body = {'ticket': {'additional_data': {'description': 'user applied'},
                           'last_status_code': 'applied_1st',
                           'last_workflow_id': workflows['applied_1st'].id,
                           'next_status_code': 'applied_2nd',
                           'next_workflow_id': workflows['applied_2nd'].id}}
        req.body = self.serializer.to_json(body)

        # set stubs
        # "stub_fake_call" is a stub in order to omit the queue transmission
        # When you use the "call_info",
        # you can confirm the call arguments of stub
        stubs.stub_fake_cast(self, 'tickets_update')
        message_check_call_info = broker_stubs.stub_fake_param_check(self)
        before_action_call_info = broker_stubs.stub_fake_before_action(self)
        after_action_call_info = broker_stubs.stub_fake_after_action(self)

        # Send request
        req.get_response(self.api)

        # Compare the updated data
        session = db_api.get_session()
        workflows = session.query(db_models.Workflow).\
            filter_by(ticket_id=self.tickets6.id).all()
        for wf in workflows:
            if wf.id == self.t6_workflows['applied_1st'].id:
                self.assertEqual(wf.status, 2)
                self.assertEqual(wf.confirmer_id, 'dummy_confirmer_id')
                self.assertEqual(wf.confirmer_name, 'dummy_confirmer_name')
                self.assertIsNotNone(wf.confirmed_at)
            elif wf.id == self.t6_workflows['applied_2nd'].id:
                self.assertEqual(wf.status, 1)
                self.assertEqual(wf.confirmer_id, 'user')
                self.assertEqual(wf.confirmer_name, 'user-name')
                self.assertIsNotNone(wf.confirmed_at)
            else:
                self.assertEqual(wf.status, 0)
                self.assertIsNone(wf.confirmer_id)
                self.assertIsNone(wf.confirmer_name)
                self.assertIsNone(wf.confirmed_at)

        def _assert_call_info(call_info):
            values = call_info['req_values']
            self.assertEqual(values['confirmer_id'], 'user')
            self.assertEqual(values['confirmer_name'], 'user-name')
            self.assertEqual(values['tenant_id'], 'tenant')
            self.assertEqual(values['tenant_name'], 'tenant-name')
            self.assertEqual(values['roles'][0], 'director')
            self.assertEqual(values['last_status_code'], 'applied_1st')
            self.assertEqual(values['next_status_code'], 'applied_2nd')
            self.assertEqual(values['additional_data']['description'],
                             'user applied')

        _assert_call_info(message_check_call_info)
        _assert_call_info(before_action_call_info)
        _assert_call_info(after_action_call_info)

    def test_update_api_1st_approval_valid_catalog_check(self):
        """Do a test of 'Update ticket'
        The test for the first approval(valid catalog check)
        """
        # Create a request data
        path = '/tickets/%s' % self.tickets9.id
        req = unit_test_utils.get_fake_request(method='PUT',
                                               path=path)
        headers = {'x-auth-token': 'user:tenant:director',
                   'x-user-name': 'user-name',
                   'x-tenant-name': 'tenant-name'}
        for k, v in headers.iteritems():
            req.headers[k] = v
        workflows = self.t9_workflows
        body = {'ticket': {'additional_data': {'description': 'user applied'},
                           'last_status_code': 'applied_1st',
                           'last_workflow_id': workflows['applied_1st'].id,
                           'next_status_code': 'applied_2nd',
                           'next_workflow_id': workflows['applied_2nd'].id}}
        req.body = self.serializer.to_json(body)

        # set stubs
        # "stub_fake_call" is a stub in order to omit the queue transmission
        # When you use the "call_info",
        # you can confirm the call arguments of stub
        stubs.stub_fake_cast(self, 'tickets_update')
        valid_catalog_check_call_info = \
            broker_stubs.stub_fake_valid_catalog_check(self)
        before_action_call_info = broker_stubs.stub_fake_before_action(self)
        after_action_call_info = broker_stubs.stub_fake_after_action(self)

        # Send request
        req.get_response(self.api)

        # Compare the updated data
        session = db_api.get_session()
        workflows = session.query(
            db_models.Workflow).filter_by(ticket_id=self.tickets9.id).all()
        for wf in workflows:
            if wf.id == self.t9_workflows['applied_1st'].id:
                self.assertEqual(wf.status, 2)
                self.assertEqual(wf.confirmer_id, 'dummy_confirmer_id')
                self.assertEqual(wf.confirmer_name, 'dummy_confirmer_name')
                self.assertIsNotNone(wf.confirmed_at)
            elif wf.id == self.t9_workflows['applied_2nd'].id:
                self.assertEqual(wf.status, 1)
                self.assertEqual(wf.confirmer_id, 'user')
                self.assertEqual(wf.confirmer_name, 'user-name')
                self.assertIsNotNone(wf.confirmed_at)
            else:
                self.assertEqual(wf.status, 0)
                self.assertIsNone(wf.confirmer_id)
                self.assertIsNone(wf.confirmer_name)
                self.assertIsNone(wf.confirmed_at)

        def _assert_call_info(call_info):
            values = call_info['req_values']
            self.assertEqual(values['confirmer_id'], 'user')
            self.assertEqual(values['confirmer_name'], 'user-name')
            self.assertEqual(values['tenant_id'], 'tenant')
            self.assertEqual(values['tenant_name'], 'tenant-name')
            self.assertEqual(values['roles'][0], 'director')
            self.assertEqual(values['last_status_code'], 'applied_1st')
            self.assertEqual(values['next_status_code'], 'applied_2nd')
            self.assertEqual(values['additional_data']['description'],
                             'user applied')

        _assert_call_info(valid_catalog_check_call_info)
        _assert_call_info(before_action_call_info)
        _assert_call_info(after_action_call_info)

    def test_update_api_final_approval(self):
        """Do a test of 'Update ticket'
        Test of final approval
        """
        # Create a request data
        path = '/tickets/%s' % self.tickets2.id
        req = unit_test_utils.get_fake_request(method='PUT',
                                               path=path)
        headers = {'x-auth-token': 'user:tenant:__member__',
                   'x-user-name': 'user-name',
                   'x-tenant-name': 'tenant-name'}
        for k, v in headers.iteritems():
            req.headers[k] = v
        workflows = self.t2_workflows
        body = {'ticket': {'additional_data': {'description': 'user applied'},
                           'last_status_code': 'applied_2nd',
                           'last_workflow_id': workflows['applied_2nd'].id,
                           'next_status_code': 'closed',
                           'next_workflow_id': workflows['closed'].id}}
        req.body = self.serializer.to_json(body)

        # set stubs
        # "stub_fake_call" is a stub in order to omit the queue transmission
        # When you use the "call_info",
        # you can confirm the call arguments of stub
        stubs.stub_fake_cast(self, 'tickets_update')
        param_check_call_info = broker_stubs.stub_fake_param_check(self)
        before_action_call_info = broker_stubs.stub_fake_before_action(self)
        after_action_call_info = broker_stubs.stub_fake_after_action(self)

        # Send request
        req.get_response(self.api)

        # Compare the updated data
        session = db_api.get_session()
        workflows = session.query(db_models.Workflow).\
            filter_by(ticket_id=self.tickets2.id).all()
        for wf in workflows:
            if wf.id == self.t2_workflows['applied_1st'].id or \
                    wf.id == self.t2_workflows['applied_2nd'].id:
                self.assertEqual(wf.status, 2)
                self.assertEqual(wf.confirmer_id, 'dummy_confirmer_id')
                self.assertEqual(wf.confirmer_name, 'dummy_confirmer_name')
                self.assertIsNotNone(wf.confirmed_at)
            elif wf.id == self.t2_workflows['closed'].id:
                self.assertEqual(wf.status, 1)
                self.assertEqual(wf.confirmer_id, 'user')
                self.assertEqual(wf.confirmer_name, 'user-name')
                self.assertIsNotNone(wf.confirmed_at)
            else:
                self.assertEqual(wf.status, 0)
                self.assertIsNone(wf.confirmer_id)
                self.assertIsNone(wf.confirmer_name)
                self.assertIsNone(wf.confirmed_at)

        def _assert_call_info(call_info):
            values = call_info['req_values']
            self.assertEqual(values['confirmer_id'], 'user')
            self.assertEqual(values['confirmer_name'], 'user-name')
            self.assertEqual(values['tenant_id'], 'tenant')
            self.assertEqual(values['tenant_name'], 'tenant-name')
            self.assertEqual(values['roles'][0], '__member__')
            self.assertEqual(values['last_status_code'], 'applied_2nd')
            self.assertEqual(values['next_status_code'], 'closed')
            self.assertEqual(values['additional_data']['description'],
                             'user applied')

        _assert_call_info(param_check_call_info)
        _assert_call_info(before_action_call_info)
        _assert_call_info(after_action_call_info)

    def test_update_api_final_approval_message_check(self):
        """Do a test of 'Update ticket'
        Test of final approval(message check)
        """
        # Create a request data
        path = '/tickets/%s' % self.tickets7.id
        req = unit_test_utils.get_fake_request(method='PUT',
                                               path=path)
        headers = {'x-auth-token': 'user:tenant:__member__',
                   'x-user-name': 'user-name',
                   'x-tenant-name': 'tenant-name'}
        for k, v in headers.iteritems():
            req.headers[k] = v
        workflows = self.t7_workflows
        body = {'ticket': {'additional_data': {'description': 'user applied'},
                           'last_status_code': 'applied_2nd',
                           'last_workflow_id': workflows['applied_2nd'].id,
                           'next_status_code': 'closed',
                           'next_workflow_id': workflows['closed'].id}}
        req.body = self.serializer.to_json(body)

        # set stubs
        # "stub_fake_call" is a stub in order to omit the queue transmission
        # When you use the "call_info",
        # you can confirm the call arguments of stub
        stubs.stub_fake_cast(self, 'tickets_update')
        message_check_call_info = broker_stubs.stub_fake_param_check(self)
        before_action_call_info = broker_stubs.stub_fake_before_action(self)
        after_action_call_info = broker_stubs.stub_fake_after_action(self)

        # Send request
        req.get_response(self.api)

        # Compare the updated data
        session = db_api.get_session()
        workflows = session.query(db_models.Workflow).\
            filter_by(ticket_id=self.tickets7.id).all()
        for wf in workflows:
            if wf.id == self.t7_workflows['applied_1st'].id or \
                    wf.id == self.t7_workflows['applied_2nd'].id:
                self.assertEqual(wf.status, 2)
                self.assertEqual(wf.confirmer_id, 'dummy_confirmer_id')
                self.assertEqual(wf.confirmer_name, 'dummy_confirmer_name')
                self.assertIsNotNone(wf.confirmed_at)
            elif wf.id == self.t7_workflows['closed'].id:
                self.assertEqual(wf.status, 1)
                self.assertEqual(wf.confirmer_id, 'user')
                self.assertEqual(wf.confirmer_name, 'user-name')
                self.assertIsNotNone(wf.confirmed_at)
            else:
                self.assertEqual(wf.status, 0)
                self.assertIsNone(wf.confirmer_id)
                self.assertIsNone(wf.confirmer_name)
                self.assertIsNone(wf.confirmed_at)

        def _assert_call_info(call_info):
            values = call_info['req_values']
            self.assertEqual(values['confirmer_id'], 'user')
            self.assertEqual(values['confirmer_name'], 'user-name')
            self.assertEqual(values['tenant_id'], 'tenant')
            self.assertEqual(values['tenant_name'], 'tenant-name')
            self.assertEqual(values['roles'][0], '__member__')
            self.assertEqual(values['last_status_code'], 'applied_2nd')
            self.assertEqual(values['next_status_code'], 'closed')
            self.assertEqual(values['additional_data']['description'],
                             'user applied')

        _assert_call_info(message_check_call_info)
        _assert_call_info(before_action_call_info)
        _assert_call_info(after_action_call_info)

    def test_update_api_final_approval_valid_catalog_check(self):
        """Do a test of 'Update ticket'
        Test of final approval(valid catalog check)
        """
        # Create a request data
        path = '/tickets/%s' % self.tickets10.id
        req = unit_test_utils.get_fake_request(method='PUT',
                                               path=path)
        headers = {'x-auth-token': 'user:tenant:__member__',
                   'x-user-name': 'user-name',
                   'x-tenant-name': 'tenant-name'}
        for k, v in headers.iteritems():
            req.headers[k] = v
        workflows = self.t10_workflows
        body = {'ticket': {'additional_data': {'description': 'user applied'},
                           'last_status_code': 'applied_2nd',
                           'last_workflow_id': workflows['applied_2nd'].id,
                           'next_status_code': 'closed',
                           'next_workflow_id': workflows['closed'].id}}
        req.body = self.serializer.to_json(body)

        # set stubs
        # "stub_fake_call" is a stub in order to omit the queue transmission
        # When you use the "call_info",
        # you can confirm the call arguments of stub
        stubs.stub_fake_cast(self, 'tickets_update')
        valid_catalog_check_call_info = \
            broker_stubs.stub_fake_valid_catalog_check(self)
        before_action_call_info = broker_stubs.stub_fake_before_action(self)
        after_action_call_info = broker_stubs.stub_fake_after_action(self)

        # Send request
        req.get_response(self.api)

        # Compare the updated data
        session = db_api.get_session()
        workflows = session.query(
            db_models.Workflow).filter_by(ticket_id=self.tickets10.id).all()
        for wf in workflows:
            if wf.id == self.t10_workflows['applied_1st'].id or \
                    wf.id == self.t10_workflows['applied_2nd'].id:
                self.assertEqual(wf.status, 2)
                self.assertEqual(wf.confirmer_id, 'dummy_confirmer_id')
                self.assertEqual(wf.confirmer_name, 'dummy_confirmer_name')
                self.assertIsNotNone(wf.confirmed_at)
            elif wf.id == self.t10_workflows['closed'].id:
                self.assertEqual(wf.status, 1)
                self.assertEqual(wf.confirmer_id, 'user')
                self.assertEqual(wf.confirmer_name, 'user-name')
                self.assertIsNotNone(wf.confirmed_at)
            else:
                self.assertEqual(wf.status, 0)
                self.assertIsNone(wf.confirmer_id)
                self.assertIsNone(wf.confirmer_name)
                self.assertIsNone(wf.confirmed_at)

        def _assert_call_info(call_info):
            values = call_info['req_values']
            self.assertEqual(values['confirmer_id'], 'user')
            self.assertEqual(values['confirmer_name'], 'user-name')
            self.assertEqual(values['tenant_id'], 'tenant')
            self.assertEqual(values['tenant_name'], 'tenant-name')
            self.assertEqual(values['roles'][0], '__member__')
            self.assertEqual(values['last_status_code'], 'applied_2nd')
            self.assertEqual(values['next_status_code'], 'closed')
            self.assertEqual(values['additional_data']['description'],
                             'user applied')

        _assert_call_info(valid_catalog_check_call_info)
        _assert_call_info(before_action_call_info)
        _assert_call_info(after_action_call_info)

    def test_update_api_closed_data_update_irregular(self):
        """Do a test of 'Update ticket'
        Update test of closed data.
        *In other words, status updates in a non-existent route.
        """
        # Create a request data
        path = '/tickets/%s' % self.tickets3.id
        req = unit_test_utils.get_fake_request(method='PUT',
                                               path=path)
        headers = {'x-auth-token': 'user:tenant:__member__',
                   'x-user-name': 'user-name',
                   'x-tenant-name': 'tenant-name'}
        for k, v in headers.iteritems():
            req.headers[k] = v
        workflows = self.t2_workflows
        body = {'ticket': {'additional_data': {'description': 'user applied'},
                           'last_status_code': 'closed',
                           'last_workflow_id': workflows['closed'].id,
                           'next_status_code': 'applied_1st',
                           'next_workflow_id': workflows['applied_1st'].id}}
        req.body = self.serializer.to_json(body)

        # set stubs
        # "stub_fake_call" is a stub in order to omit the queue transmission
        # When you use the "call_info",
        # you can confirm the call arguments of stub
        stubs.stub_fake_cast(self, 'tickets_update')
        broker_stubs.stub_fake_param_check(self)

        # Send request
        res = req.get_response(self.api)

        # Examination of response
        self.assertEqual(res.status_int, 409)

    def test_update_api_already_updated_irregular(self):
        """Do a test of 'Update ticket'
        Testing If you have already been updated.
        """
        # Create a request data
        path = '/tickets/%s' % self.tickets3.id
        req = unit_test_utils.get_fake_request(method='PUT',
                                               path=path)
        headers = {'x-auth-token': 'user:tenant:__member__',
                   'x-user-name': 'user-name',
                   'x-tenant-name': 'tenant-name'}
        for k, v in headers.iteritems():
            req.headers[k] = v
        workflows = self.t2_workflows
        body = {'ticket': {'additional_data': {'description': 'user applied'},
                           'last_status_code': 'applied_2nd',
                           'last_workflow_id': workflows['applied_2nd'].id,
                           'next_status_code': 'closed',
                           'next_workflow_id': workflows['closed'].id}}
        req.body = self.serializer.to_json(body)

        # set stubs
        # "stub_fake_call" is a stub in order to omit the queue transmission
        # When you use the "call_info",
        # you can confirm the call arguments of stub
        stubs.stub_fake_cast(self, 'tickets_update')
        broker_stubs.stub_fake_param_check(self)

        # Send request
        res = req.get_response(self.api)

        # Examination of response
        self.assertEqual(res.status_int, 409)

    def test_update_api_nodata_irregular(self):
        """Do a test of 'Update ticket'
        Test cases run unauthorized.
        """
        # Create a request data
        path = '/tickets/%s' % 'xxxxxx-xxxxxxx'
        req = unit_test_utils.get_fake_request(method='PUT',
                                               path=path)
        headers = {'x-auth-token': 'user:tenant:__member__',
                   'x-user-name': 'user-name',
                   'x-tenant-name': 'tenant-name'}
        for k, v in headers.iteritems():
            req.headers[k] = v
        workflows = self.t2_workflows
        body = {'ticket': {'additional_data': {'description': 'user applied'},
                           'last_status_code': 'applied_2nd',
                           'last_workflow_id': workflows['applied_2nd'].id,
                           'next_status_code': 'closed',
                           'next_workflow_id': workflows['closed'].id}}
        req.body = self.serializer.to_json(body)

        # set stubs
        # "stub_fake_call" is a stub in order to omit the queue transmission
        # When you use the "call_info",
        # you can confirm the call arguments of stub
        stubs.stub_fake_cast(self, 'tickets_update')
        broker_stubs.stub_fake_param_check(self)

        # Send request
        res = req.get_response(self.api)

        # Examination of response
        self.assertEqual(res.status_int, 404)

    def test_update_api_can_not_update_other_tenant(self):
        """Do a test of 'Update ticket'
        Data of other tenants can not be updated.
        """
        # Create a request data
        path = '/tickets/%s' % self.tickets4.id
        req = unit_test_utils.get_fake_request(method='PUT',
                                               path=path)
        headers = {'x-auth-token': 'user:tenant_XXX:__member__',
                   'x-user-name': 'user-name',
                   'x-tenant-name': 'tenant-name'}
        for k, v in headers.iteritems():
            req.headers[k] = v
        workflows = self.t4_workflows
        body = {'ticket': {'additional_data': {'description': 'user applied'},
                           'last_status_code': 'applied_1st',
                           'last_workflow_id': workflows['applied_1st'].id,
                           'next_status_code': 'applied_2nd',
                           'next_workflow_id': workflows['applied_2nd'].id}}
        req.body = self.serializer.to_json(body)

        # set stubs
        # "stub_fake_call" is a stub in order to omit the queue transmission
        # When you use the "call_info",
        # you can confirm the call arguments of stub
        stubs.stub_fake_cast(self, 'tickets_update')
        broker_stubs.stub_fake_param_check(self)

        # Send request
        res = req.get_response(self.api)

        # Examination of response
        self.assertEqual(res.status_int, 404)
