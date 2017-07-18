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
#

import uuid

from oslo_config import cfg
from oslo_serialization import jsonutils

from aflo.common import mail
from aflo.db.sqlalchemy import api as db_api
from aflo.db.sqlalchemy import models as db_models
from aflo.mail.common_request import mail_common_request_accepted
from aflo.mail.common_request import mail_common_request_completed
from aflo.mail.common_request import mail_common_request_request
from aflo.mail.user_registration import mail_user_registration_accepted
from aflo.mail.user_registration import mail_user_registration_completed
from aflo.mail.user_registration import mail_user_registration_request
import aflo.tests.unit.utils as unit_test_utils
from aflo.tests.unit.v1.tickets.broker import broker_test_base as base
from aflo.tests.unit.v1.tickets.stubs import Ticket_RpcStubs as stubs
from aflo.tickets.broker.utils import utils as broker_utils

CONF = cfg.CONF

WFP_UUID1 = str(uuid.uuid4())
TT_UUID1 = str(uuid.uuid4())


class Stubs(object):
    @classmethod
    def utils_stubout(cls, target, method):
        """method which method to stub out of
           'aflo.tickets.broker.utils'.
        :param target: Target process.
        :param method: Called function.
        """
        call_info = {}

        def fake_get_email_address(user_id):
            call_info['user_id'] = user_id
            return user_id + '@example.com'

        def fake_error_get_email_address(user_id):
            call_info['user_id'] = user_id
            return None

        def fake_get_email_addresses_from_role(tenant, roles):
            call_info['tenant'] = tenant
            call_info['roles'] = roles
            rtn = []
            for role in roles:
                rtn.append(role + '@example.com')
            return list(set(rtn))

        def fake_error_get_email_addresses_from_role(tenant, roles):
            call_info['tenant'] = tenant
            call_info['roles'] = roles
            rtn = []
            return list(set(rtn))

        fake_managers = \
            {'get_email_address': {'method': 'get_email_address',
                                   'stub': fake_get_email_address},
             'error_get_email_address': {'method': 'get_email_address',
                                         'stub': fake_error_get_email_address},
             'get_email_addresses_from_role':
                {'method': 'get_email_addresses_from_role',
                 'stub': fake_get_email_addresses_from_role},
             'error_get_email_addresses_from_role':
                {'method': 'get_email_addresses_from_role',
                 'stub': fake_error_get_email_addresses_from_role}}
        target.stubs.Set(broker_utils, fake_managers[method]['method'],
                         fake_managers[method]['stub'])

        return call_info

    @classmethod
    def mail_stubout(cls, target, method):
        """method which method to stub out of
           'aflo.tickets.broker.utils'.
        :param target: Target process.
        :param method: Called function.
        """
        call_info = {}

        def fake_sendmail(to_address, template, data,
                          cc_address=None, bcc_address=None,
                          encode=None, from_address=None,
                          smtp_server=None):
            call_info['to_address'] = to_address
            call_info['template'] = template
            call_info['data'] = data

        fake_managers = \
            {'sendmail': fake_sendmail}
        target.stubs.Set(mail, method, fake_managers[method])

        return call_info


class TestUserEntryRequestHandler(base.BrokerTestBase):
    """Do a test of 'Request User Entry'"""

    def setUp(self):
        """Establish a clean test environment"""
        super(TestUserEntryRequestHandler, self).setUp()

        self.config(encode='utf-8', group='mail')
        self.config(from_address='user@example.com', group='mail')
        self.config(smtp_server='mail.example.com', group='mail')
        self.config(user='user', group='mail')
        self.config(password='xxxx', group='mail')

    def create_fixtures(self):
        super(TestUserEntryRequestHandler, self).create_fixtures()

        self.wf_pattern_contents = self._get_dict_contents(
            'wf_pattern_RequestUserEntry')
        self._create_workflow_pattern(db_models, WFP_UUID1,
                                      **self.wf_pattern_contents)

        self.template_contents = self._get_dict_contents(
            'template_contents_RequestUserEntry', '20160627')
        self._create_ticket_template(db_models, TT_UUID1, WFP_UUID1,
                                     **self.template_contents)

    def _make_inquiring(self):
        """Testing of the new application """
        # Create a request data
        path = '/tickets'
        req = unit_test_utils.get_fake_request(method='POST',
                                               path=path)
        headers = {'x-auth-token': 'user:tenant:_member_',
                   'x-user-name': 'user-name',
                   'x-tenant-name': 'tenant-name'}
        for k, v in headers.iteritems():
            req.headers[k] = v

        ticket_detail = {'User Name': 'user',
                         'Email': 'user@example.com',
                         'Role': ['wf_apply',
                                  'wf_check',
                                  '_member_'],
                         'Message': 'Please add the user.\n'
                                    'test line 2\n'
                                    'test line 3'}
        body = {'ticket':
                {'ticket_template_id': TT_UUID1,
                 'ticket_detail': self.serializer.to_json(ticket_detail),
                 'status_code': self.template_contents['first_status_code']}}
        req.body = self.serializer.to_json(body)

        # set stubs
        # "stub_fake_call" is a stub in order to omit the queue transmission
        # When you use the "call_info",
        # you can confirm the call arguments of stub
        stubs.stub_fake_cast(self, 'tickets_create')

        Stubs.utils_stubout(self, 'get_email_address')
        Stubs.utils_stubout(self, 'get_email_addresses_from_role')
        call_info = Stubs.mail_stubout(self, 'sendmail')

        # Send request
        res = req.get_response(self.api)

        # Examination of response
        self.assertEqual(res.status_int, 200)
        ticket = jsonutils.loads(res.body)['ticket']

        to_address = call_info['to_address']
        self.assertTrue('wf_request_support@example.com' in to_address)
        self.assertTrue('_member_@example.com' in to_address)
        self.assertEqual(call_info['template'].SUBJECT,
                         mail_user_registration_request.SUBJECT)

        return ticket

    def _update_to_working(self, ticket_id):
        """Test to be approved to 'working' """
        # Create a request data
        path = '/tickets/%s' % ticket_id
        req = unit_test_utils.get_fake_request(method='PUT',
                                               path=path)
        headers = {'x-auth-token': 'support1:tenant:wf_request_support',
                   'x-user-name': 'support1-name',
                   'x-tenant-name': 'tenant-name'}
        for k, v in headers.iteritems():
            req.headers[k] = v

        session = db_api.get_session()
        last_wf = session.query(db_models.Workflow).\
            filter_by(ticket_id=ticket_id).\
            filter_by(status_code='inquiring').one().id
        next_wf = session.query(db_models.Workflow).\
            filter_by(ticket_id=ticket_id).\
            filter_by(status_code='working').one().id
        additional_data = {'Message': 'reception completed'}
        body = {'ticket': {'additional_data':
                           self.serializer.to_json(additional_data),
                           'last_status_code': 'inquiring',
                           'last_workflow_id': last_wf,
                           'next_status_code': 'working',
                           'next_workflow_id': next_wf}}
        req.body = self.serializer.to_json(body)

        # set stubs
        # "stub_fake_call" is a stub in order to omit the queue transmission
        # When you use the "call_info",
        # you can confirm the call arguments of stub
        self.stubs.UnsetAll()
        stubs.stub_fake_cast(self, 'tickets_update')
        Stubs.utils_stubout(self, 'get_email_address')
        call_info = Stubs.mail_stubout(self, 'sendmail')

        # Send request
        res = req.get_response(self.api)

        # Examination of response
        self.assertEqual(res.status_int, 200)

        self.assertEqual(', '.join(call_info['to_address']),
                         'user@example.com')
        self.assertEqual(call_info['template'].SUBJECT,
                         mail_user_registration_accepted.SUBJECT)

    def _update_to_done(self, ticket_id):
        """Test to be approved to 'done' """
        # Create a request data
        path = '/tickets/%s' % ticket_id
        req = unit_test_utils.get_fake_request(method='PUT',
                                               path=path)
        headers = {'x-auth-token': 'support2:tenant:wf_request_support',
                   'x-user-name': 'support2-name',
                   'x-tenant-name': 'tenant-name'}
        for k, v in headers.iteritems():
            req.headers[k] = v

        session = db_api.get_session()
        last_wf = session.query(db_models.Workflow).\
            filter_by(ticket_id=ticket_id).\
            filter_by(status_code='working').one().id
        next_wf = session.query(db_models.Workflow).\
            filter_by(ticket_id=ticket_id).\
            filter_by(status_code='done').one().id
        additional_data = {'Message': 'reception completed'}
        body = {'ticket': {'additional_data':
                           self.serializer.to_json(additional_data),
                           'last_status_code': 'working',
                           'last_workflow_id': last_wf,
                           'next_status_code': 'done',
                           'next_workflow_id': next_wf}}
        req.body = self.serializer.to_json(body)

        # set stubs
        # "stub_fake_call" is a stub in order to omit the queue transmission
        # When you use the "call_info",
        # you can confirm the call arguments of stub
        self.stubs.UnsetAll()
        stubs.stub_fake_cast(self, 'tickets_update')
        Stubs.utils_stubout(self, 'get_email_address')
        call_info = Stubs.mail_stubout(self, 'sendmail')

        # Send request
        res = req.get_response(self.api)

        # Examination of response
        self.assertEqual(res.status_int, 200)

        self.assertEqual(', '.join(call_info['to_address']),
                         'user@example.com')
        self.assertEqual(call_info['template'].SUBJECT,
                         mail_user_registration_completed.SUBJECT)

    def _update_to_closed(self, ticket_id):
        """Test to be approved to 'closed' """
        # Create a request data
        path = '/tickets/%s' % ticket_id
        req = unit_test_utils.get_fake_request(method='PUT',
                                               path=path)
        headers = {'x-auth-token': 'user:tenant:_member_',
                   'x-user-name': 'user-name',
                   'x-tenant-name': 'tenant-name'}
        for k, v in headers.iteritems():
            req.headers[k] = v

        session = db_api.get_session()
        last_wf = session.query(db_models.Workflow).\
            filter_by(ticket_id=ticket_id).\
            filter_by(status_code='done').one().id
        next_wf = session.query(db_models.Workflow).\
            filter_by(ticket_id=ticket_id).\
            filter_by(status_code='closed').one().id
        additional_data = {'Message': 'closed'}
        body = {'ticket': {'additional_data':
                           self.serializer.to_json(additional_data),
                           'last_status_code': 'done',
                           'last_workflow_id': last_wf,
                           'next_status_code': 'closed',
                           'next_workflow_id': next_wf}}
        req.body = self.serializer.to_json(body)

        # set stubs
        # "stub_fake_call" is a stub in order to omit the queue transmission
        # When you use the "call_info",
        # you can confirm the call arguments of stub
        self.stubs.UnsetAll()
        stubs.stub_fake_cast(self, 'tickets_update')

        # Send request
        res = req.get_response(self.api)

        # Examination of response
        self.assertEqual(res.status_int, 200)

    def test_inquiring_to_closed(self):
        """Test from a new application (inquiring)
        until final approval (closed)
        """
        self.config(smtp_server='mail.example.com', group='mail')

        ticket = self._make_inquiring()
        ticket_id = ticket['id']

        self._update_to_working(ticket_id)
        self._update_to_done(ticket_id)
        self._update_to_closed(ticket_id)

    def test_message_check_irregular(self):
        """Test of input check handler (message_check) """
        self.config(smtp_server='mail.example.com', group='mail')

        ticket = self._make_inquiring()
        ticket_id = ticket['id']

        # Create a request data
        path = '/tickets/%s' % ticket_id
        req = unit_test_utils.get_fake_request(method='PUT',
                                               path=path)
        headers = {'x-auth-token': 'support1:tenant:wf_request_support',
                   'x-user-name': 'support1-name',
                   'x-tenant-name': 'tenant-name'}
        for k, v in headers.iteritems():
            req.headers[k] = v

        session = db_api.get_session()
        last_wf = session.query(db_models.Workflow).\
            filter_by(ticket_id=ticket_id).\
            filter_by(status_code='inquiring').one().id
        next_wf = session.query(db_models.Workflow).\
            filter_by(ticket_id=ticket_id).\
            filter_by(status_code='working').one().id
        additional_data = {'Message': 'A' * 513}
        body = {'ticket': {'additional_data':
                           self.serializer.to_json(additional_data),
                           'last_status_code': 'inquiring',
                           'last_workflow_id': last_wf,
                           'next_status_code': 'working',
                           'next_workflow_id': next_wf}}
        req.body = self.serializer.to_json(body)

        # set stubs
        # "stub_fake_call" is a stub in order to omit the queue transmission
        # When you use the "call_info",
        # you can confirm the call arguments of stub
        self.stubs.UnsetAll()
        stubs.stub_fake_cast(self, 'tickets_update')

        # Send request
        res = req.get_response(self.api)

        # Examination of response
        self.assertEqual(res.status_int, 400)


class TestCommonRequestHandler(base.BrokerTestBase):
    """Do a test of 'Request User Entry'"""

    def setUp(self):
        """Establish a clean test environment"""
        super(TestCommonRequestHandler, self).setUp()

    def create_fixtures(self):
        super(TestCommonRequestHandler, self).create_fixtures()

        self.wf_pattern_contents = self._get_dict_contents(
            'wf_pattern_RequestUserEntry')
        self._create_workflow_pattern(db_models, WFP_UUID1,
                                      **self.wf_pattern_contents)

        self.template_contents = self._get_dict_contents(
            'template_contents_Request', '20160627')
        self._create_ticket_template(db_models, TT_UUID1, WFP_UUID1,
                                     **self.template_contents)

    def _make_inquiring(self):
        """Testing of the new application """
        # Create a request data
        path = '/tickets'
        req = unit_test_utils.get_fake_request(method='POST',
                                               path=path)
        headers = {'x-auth-token': 'user:tenant:_member_',
                   'x-user-name': 'user-name',
                   'x-tenant-name': 'tenant-name'}
        for k, v in headers.iteritems():
            req.headers[k] = v

        ticket_detail = {'Message': 'Please add the user.\n'
                                    'test line 2\n'
                                    'test line 3'}
        body = {'ticket':
                {'ticket_template_id': TT_UUID1,
                 'ticket_detail': self.serializer.to_json(ticket_detail),
                 'status_code': self.template_contents['first_status_code']}}
        req.body = self.serializer.to_json(body)

        # set stubs
        # "stub_fake_call" is a stub in order to omit the queue transmission
        # When you use the "call_info",
        # you can confirm the call arguments of stub
        stubs.stub_fake_cast(self, 'tickets_create')

        Stubs.utils_stubout(self, 'get_email_address')
        Stubs.utils_stubout(self, 'get_email_addresses_from_role')
        call_info = Stubs.mail_stubout(self, 'sendmail')

        # Send request
        res = req.get_response(self.api)

        # Examination of response
        self.assertEqual(res.status_int, 200)
        ticket = jsonutils.loads(res.body)['ticket']

        to_address = call_info['to_address']
        self.assertTrue('wf_request_support@example.com' in to_address)
        self.assertTrue('_member_@example.com' in to_address)
        self.assertEqual(call_info['template'].SUBJECT,
                         mail_common_request_request.SUBJECT)

        return ticket

    def _update_to_working(self, ticket_id):
        """Test to be approved to 'working' """
        # Create a request data
        path = '/tickets/%s' % ticket_id
        req = unit_test_utils.get_fake_request(method='PUT',
                                               path=path)
        headers = {'x-auth-token': 'support1:tenant:wf_request_support',
                   'x-user-name': 'support1-name',
                   'x-tenant-name': 'tenant-name'}
        for k, v in headers.iteritems():
            req.headers[k] = v

        session = db_api.get_session()
        last_wf = session.query(db_models.Workflow).\
            filter_by(ticket_id=ticket_id).\
            filter_by(status_code='inquiring').one().id
        next_wf = session.query(db_models.Workflow).\
            filter_by(ticket_id=ticket_id).\
            filter_by(status_code='working').one().id
        additional_data = {'Message': 'reception completed'}
        body = {'ticket': {'additional_data':
                           self.serializer.to_json(additional_data),
                           'last_status_code': 'inquiring',
                           'last_workflow_id': last_wf,
                           'next_status_code': 'working',
                           'next_workflow_id': next_wf}}
        req.body = self.serializer.to_json(body)

        # set stubs
        # "stub_fake_call" is a stub in order to omit the queue transmission
        # When you use the "call_info",
        # you can confirm the call arguments of stub
        self.stubs.UnsetAll()
        stubs.stub_fake_cast(self, 'tickets_update')
        Stubs.utils_stubout(self, 'get_email_address')
        call_info = Stubs.mail_stubout(self, 'sendmail')

        # Send request
        res = req.get_response(self.api)

        # Examination of response
        self.assertEqual(res.status_int, 200)

        self.assertEqual(', '.join(call_info['to_address']),
                         'user@example.com')
        self.assertEqual(call_info['template'].SUBJECT,
                         mail_common_request_accepted.SUBJECT)

    def _update_to_done(self, ticket_id):
        """Test to be approved to 'done' """
        # Create a request data
        path = '/tickets/%s' % ticket_id
        req = unit_test_utils.get_fake_request(method='PUT',
                                               path=path)
        headers = {'x-auth-token': 'support2:tenant:wf_request_support',
                   'x-user-name': 'support2-name',
                   'x-tenant-name': 'tenant-name'}
        for k, v in headers.iteritems():
            req.headers[k] = v

        session = db_api.get_session()
        last_wf = session.query(db_models.Workflow).\
            filter_by(ticket_id=ticket_id).\
            filter_by(status_code='working').one().id
        next_wf = session.query(db_models.Workflow).\
            filter_by(ticket_id=ticket_id).\
            filter_by(status_code='done').one().id
        additional_data = {'Message': 'reception completed'}
        body = {'ticket': {'additional_data':
                           self.serializer.to_json(additional_data),
                           'last_status_code': 'working',
                           'last_workflow_id': last_wf,
                           'next_status_code': 'done',
                           'next_workflow_id': next_wf}}
        req.body = self.serializer.to_json(body)

        # set stubs
        # "stub_fake_call" is a stub in order to omit the queue transmission
        # When you use the "call_info",
        # you can confirm the call arguments of stub
        self.stubs.UnsetAll()
        stubs.stub_fake_cast(self, 'tickets_update')
        Stubs.utils_stubout(self, 'get_email_address')
        call_info = Stubs.mail_stubout(self, 'sendmail')

        # Send request
        res = req.get_response(self.api)

        # Examination of response
        self.assertEqual(res.status_int, 200)

        self.assertEqual(', '.join(call_info['to_address']),
                         'user@example.com')
        self.assertEqual(call_info['template'].SUBJECT,
                         mail_common_request_completed.SUBJECT)

    def _update_to_closed(self, ticket_id):
        """Test to be approved to 'closed' """
        # Create a request data
        path = '/tickets/%s' % ticket_id
        req = unit_test_utils.get_fake_request(method='PUT',
                                               path=path)
        headers = {'x-auth-token': 'user:tenant:_member_',
                   'x-user-name': 'user-name',
                   'x-tenant-name': 'tenant-name'}
        for k, v in headers.iteritems():
            req.headers[k] = v

        session = db_api.get_session()
        last_wf = session.query(db_models.Workflow).\
            filter_by(ticket_id=ticket_id).\
            filter_by(status_code='done').one().id
        next_wf = session.query(db_models.Workflow).\
            filter_by(ticket_id=ticket_id).\
            filter_by(status_code='closed').one().id
        additional_data = {'Message': 'closed'}
        body = {'ticket': {'additional_data':
                           self.serializer.to_json(additional_data),
                           'last_status_code': 'done',
                           'last_workflow_id': last_wf,
                           'next_status_code': 'closed',
                           'next_workflow_id': next_wf}}
        req.body = self.serializer.to_json(body)

        # set stubs
        # "stub_fake_call" is a stub in order to omit the queue transmission
        # When you use the "call_info",
        # you can confirm the call arguments of stub
        self.stubs.UnsetAll()
        stubs.stub_fake_cast(self, 'tickets_update')

        # Send request
        res = req.get_response(self.api)

        # Examination of response
        self.assertEqual(res.status_int, 200)

    def test_inquiring_to_closed(self):
        """Test from a new application (inquiring)
        until final approval (closed)
        """
        self.config(smtp_server='mail.example.com', group='mail')

        ticket = self._make_inquiring()
        ticket_id = ticket['id']

        self._update_to_working(ticket_id)
        self._update_to_done(ticket_id)
        self._update_to_closed(ticket_id)

    def test_message_check_irregular(self):
        """Test of input check handler (message_check) """
        self.config(smtp_server='mail.example.com', group='mail')

        ticket = self._make_inquiring()
        ticket_id = ticket['id']

        # Create a request data
        path = '/tickets/%s' % ticket_id
        req = unit_test_utils.get_fake_request(method='PUT',
                                               path=path)
        headers = {'x-auth-token': 'support1:tenant:wf_request_support',
                   'x-user-name': 'support1-name',
                   'x-tenant-name': 'tenant-name'}
        for k, v in headers.iteritems():
            req.headers[k] = v

        session = db_api.get_session()
        last_wf = session.query(db_models.Workflow).\
            filter_by(ticket_id=ticket_id).\
            filter_by(status_code='inquiring').one().id
        next_wf = session.query(db_models.Workflow).\
            filter_by(ticket_id=ticket_id).\
            filter_by(status_code='working').one().id
        additional_data = {'Message': 'A' * 513}
        body = {'ticket': {'additional_data':
                           self.serializer.to_json(additional_data),
                           'last_status_code': 'inquiring',
                           'last_workflow_id': last_wf,
                           'next_status_code': 'working',
                           'next_workflow_id': next_wf}}
        req.body = self.serializer.to_json(body)

        # set stubs
        self.stubs.UnsetAll()
        stubs.stub_fake_cast(self, 'tickets_update')

        # Send request
        res = req.get_response(self.api)

        # Examination of response
        self.assertEqual(res.status_int, 400)
