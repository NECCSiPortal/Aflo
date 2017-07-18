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

import datetime
import uuid

from oslo_config import cfg
from oslo_serialization import jsonutils

from aflo.common import mail
from aflo.db.sqlalchemy import api as db_api
from aflo.db.sqlalchemy import models as db_models
import aflo.tests.unit.utils as unit_test_utils
from aflo.tests.unit.v1.tickets.broker import broker_test_base as base
from aflo.tests.unit.v1.tickets.broker import fixture
from aflo.tests.unit.v1.tickets.stubs import Ticket_RpcStubs as stubs
from aflo.tickets.broker.utils import utils as broker_utils

CONF = cfg.CONF

WFP_UUID1 = str(uuid.uuid4())
# TT_UUID1 = str(uuid.uuid4())
TT_UUID2 = str(uuid.uuid4())
TKT_UUID1 = str(uuid.uuid4())
# CONT_UUID1 = str(uuid.uuid4())
TT_UUID1 = str('ticket_template_999')
CONT_UUID1 = str('contract_999')


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

        def fake_get_email_addresses_from_role(tenant, roles):
            call_info['tenant'] = tenant
            call_info['roles'] = roles
            rtn = []
            for role in roles:
                rtn.append(role + '@example.com')
            return list(set(rtn))

        def fake_get_nova_client():
            class Client(object):
                def __init__(self, username=None, api_key=None,
                             project_id=None, auth_url=None):
                    self.limits = LimitsManager()
                    self.quotas = QuotaSetManager()

            class QuotaSet(object):
                info = {"cores": 20,
                        "ram": 51200}

                def to_dict(self):
                    return self.info

            class Limits(object):
                info = {"absolute": {"totalCoresUsed": 2,
                                     "totalRAMUsed": 0}}

                def to_dict(self):
                    return self.info

            class QuotaSetManager(object):
                def get(self, tenant_id, user_id=None):
                    return QuotaSet()

                def update(self, tenant_id, **update_val):
                    pass

            class LimitsManager(object):
                def get(self, reserved=False, tenant_id=None):
                    return Limits()

            return Client()

        def fake_get_nova_client_for_integrity_check_error():
            class Client(object):
                def __init__(self, username=None, api_key=None,
                             project_id=None, auth_url=None):
                    self.limits = LimitsManager()
                    self.quotas = QuotaSetManager()

            class QuotaSet(object):
                info = {"cores": 20,
                        "ram": 51200}

                def to_dict(self):
                    return self.info

            class Limits(object):
                info = {"absolute": {"totalCoresUsed": 20,
                                     "totalRAMUsed": 51200}}

                def to_dict(self):
                    return self.info

            class QuotaSetManager(object):
                def get(self, tenant_id, user_id=None):
                    return QuotaSet()

                def update(self, tenant_id, **update_val):
                    pass

            class LimitsManager(object):
                def get(self, reserved=False, tenant_id=None):
                    return Limits()

            return Client()

        def fake_get_cinder_client():
            class Client(object):
                def __init__(self, username=None, api_key=None,
                             project_id=None, auth_url=None):
                    self.quotas = QuotaSetManager()

            class QuotaSet(object):
                gigabytes = 1000

            class QuotaSetUsage(object):
                gigabytes = {u'limit': 1000, u'reserved': 0, u'in_use': 150}

            class QuotaSetManager(object):
                def get(self, tenant_id, user_id=None, usage=None):
                    if not usage:
                        return QuotaSet()
                    else:
                        return QuotaSetUsage()

                def update(self, tenant_id, **update_val):
                    pass

            return Client()

        fake_managers = \
            {'get_email_address':
             {'method': 'get_email_address',
              'stub': fake_get_email_address},

             'get_email_addresses_from_role':
             {'method': 'get_email_addresses_from_role',
              'stub': fake_get_email_addresses_from_role},

             'get_nova_client':
             {'method': 'get_nova_client',
              'stub': fake_get_nova_client},

             'get_nova_client_for_integrity_check_error':
             {'method': 'get_nova_client',
              'stub': fake_get_nova_client_for_integrity_check_error},

             'get_cinder_client':
             {'method': 'get_cinder_client',
              'stub': fake_get_cinder_client}}

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

        fake_managers = {'sendmail': fake_sendmail}
        target.stubs.Set(mail, method, fake_managers[method])

        return call_info


class TestBroker(base.BrokerTestBase):
    """Do a test of 'Request User Entry'"""

    def setUp(self):
        """Establish a clean test environment"""
        super(TestBroker, self).setUp()

        self.config(encode='utf-8', group='mail')
        self.config(from_address='user@example.com', group='mail')
        self.config(smtp_server='mail.example.com', group='mail')
        self.config(user='user', group='mail')
        self.config(password='xxxx', group='mail')

        self.config(username='admin', group='keystone_client')
        self.config(password='xxxx', group='keystone_client')
        self.config(tenant_name='admin', group='keystone_client')
        self.config(auth_url='http://127.0.0.1:5000/v2.0',
                    group='keystone_client')

        self.config(username='admin', group='nova_client')
        self.config(api_key='xxxx', group='nova_client')
        self.config(project_id='admin', group='nova_client')
        self.config(auth_url='http://127.0.0.1:5000/v2.0',
                    group='keystone_client')

        self.config(username='admin', group='cinder_client')
        self.config(api_key='xxxx', group='cinder_client')
        self.config(project_id='admin', group='cinder_client')
        self.config(auth_url='http://127.0.0.1:5000/v2.0',
                    group='keystone_client')

    def create_fixtures(self):
        super(TestBroker, self).create_fixtures()

        catalog_ids = []
        catalog_ids.append(fixture.make_catalog_only(
            'VCPU x 10 CORE(S)', 1, 10, 'cores', None))
        catalog_ids.append(fixture.make_catalog_only(
            'RAM 20 GB', 4, 20, 'ram', 'GB'))
        catalog_ids.append(fixture.make_catalog_only(
            'Volume Storage 50 GB', 5, 50, 'gigabytes', 'GB'))

        # make template
        self.wf_pattern_contents = self._get_dict_contents(
            'wf_pattern_SampleSetCatalogMonthly_cancellation')
        self._create_workflow_pattern(db_models, WFP_UUID1,
                                      **self.wf_pattern_contents)

        self.template_contents = self._get_dict_contents(
            'template_contents_SampleSetCatalogMonthly_cancellation',
            '20160627')
        self.template_contents['target_id'] = catalog_ids

        self._create_ticket_template(db_models, TT_UUID1, WFP_UUID1,
                                     **self.template_contents)

        # make old contract
        self.template_contents_old = self._get_dict_contents(
            'template_contents_SampleSetCatalogMonthly',
            '20160627')
        self.template_contents_old['target_id'] = catalog_ids
        self._create_ticket_template(db_models, TT_UUID2, WFP_UUID1,
                                     **self.template_contents_old)
        ticket = db_models.Ticket(id=TKT_UUID1)
        ticket.ticket_template_id = TT_UUID2
        ticket.ticket_type = 'ticket_type'
        ticket.target_id = self.serializer.to_json(catalog_ids)
        ticket.tenant_id = 'tenant'
        ticket.save()
        contract = db_models.Contract(contract_id=CONT_UUID1)
        contract.application_id = ticket.id
        expansion_text = {'contract_info':
                          {'ticket_detail':
                           {'vcpu': 1,
                            'ram': 2,
                            'volume_storage': 1,
                            'message': 'text'}}}
        contract.expansion_text = self.serializer.to_json(expansion_text)
        contract.lifetime_start = \
            datetime.datetime(2015, 1, 1, 0, 0, 0, 0)
        contract.lifetime_end = \
            datetime.datetime(2999, 12, 31, 23, 59, 59, 999999)
        contract.save()

    def _make_awaiting_approval(self):
        """Testing of the new application """
        # Create a request data
        path = '/tickets'
        req = unit_test_utils.get_fake_request(method='POST',
                                               path=path)
        headers = {'x-auth-token': 'user:tenant:wf_apply',
                   'x-user-name': 'user-name',
                   'x-tenant-name': 'tenant-name'}
        for k, v in headers.iteritems():
            req.headers[k] = v

        ticket_detail = {'contract_id': CONT_UUID1,
                         'vcpu': 1,
                         'ram': 2,
                         'volume_storage': 1,
                         'Message': 'We will apply for cancellation.\n'
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
        self.stubs.UnsetAll()
        stubs.stub_fake_cast(self, 'tickets_create')
        Stubs.utils_stubout(self, 'get_nova_client')
        Stubs.utils_stubout(self, 'get_cinder_client')

        # Send request
        res = req.get_response(self.api)

        # Examination of response
        self.assertEqual(res.status_int, 200)
        ticket = jsonutils.loads(res.body)['ticket']

        return ticket

    def _update_skip(self, ticket_id, user, role,
                     last_status_code, next_status_code):
        """Test to be approved to 'next_status' """
        # Create a request data
        path = '/tickets/%s' % ticket_id
        req = unit_test_utils.get_fake_request(method='PUT',
                                               path=path)
        headers = {'x-auth-token': '%s:tenant:%s' % (user, role),
                   'x-user-name': '%s-name' % user,
                   'x-tenant-name': 'tenant-name'}
        for k, v in headers.iteritems():
            req.headers[k] = v

        session = db_api.get_session()
        last_wf = session.query(db_models.Workflow).\
            filter_by(ticket_id=ticket_id).\
            filter_by(status_code=last_status_code).one().id
        next_wf = session.query(db_models.Workflow).\
            filter_by(ticket_id=ticket_id).\
            filter_by(status_code=next_status_code).one().id
        additional_data = {'Message': 'OK'}
        body = {'ticket': {'additional_data':
                           self.serializer.to_json(additional_data),
                           'last_status_code': last_status_code,
                           'last_workflow_id': last_wf,
                           'next_status_code': next_status_code,
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

    def _update_to_approval(self, ticket_id):
        """Test to be approved to 'approval' """
        # Create a request data
        path = '/tickets/%s' % ticket_id
        req = unit_test_utils.get_fake_request(method='PUT',
                                               path=path)
        headers = {'x-auth-token': 'admin:admin:wf_approval,admin',
                   'x-user-name': 'admin-name',
                   'x-tenant-name': 'admin-tenant-name'}
        for k, v in headers.iteritems():
            req.headers[k] = v
        session = db_api.get_session()
        last_wf = session.query(db_models.Workflow).\
            filter_by(ticket_id=ticket_id).\
            filter_by(status_code='check').one().id
        next_wf = session.query(db_models.Workflow).\
            filter_by(ticket_id=ticket_id).\
            filter_by(status_code='approval').one().id
        additional_data = {'Message': 'OK'}
        body = {'ticket': {'additional_data':
                           self.serializer.to_json(additional_data),
                           'last_status_code': 'check',
                           'last_workflow_id': last_wf,
                           'next_status_code': 'approval',
                           'next_workflow_id': next_wf}}
        req.body = self.serializer.to_json(body)

        # set stubs
        # "stub_fake_call" is a stub in order to omit the queue transmission
        # When you use the "call_info",
        # you can confirm the call arguments of stub
        self.stubs.UnsetAll()
        stubs.stub_fake_cast(self, 'tickets_update')
        Stubs.utils_stubout(self, 'get_nova_client')
        Stubs.utils_stubout(self, 'get_cinder_client')
        Stubs.utils_stubout(self, 'get_email_address')
        Stubs.mail_stubout(self, 'sendmail')

        # Send request
        res = req.get_response(self.api)

        # Examination of response
        self.assertEqual(res.status_int, 200)

        contract = db_api.contract_get(self.context, CONT_UUID1)
        self.assertNotEqual(contract['lifetime_end'],
                            datetime.datetime(2999, 12, 31, 23,
                                              59, 59, 999999))

    def test_awaiting_approval_to_approval(self):
        """Test from a new application (awaiting approval)
        until final approval (approval)
        """
        self.config(smtp_server='mail.example.com', group='mail')

        ticket = self._make_awaiting_approval()
        ticket_id = ticket['id']
        self._update_skip(ticket_id, 'userA', 'wf_check',
                          'awaiting approval', 'check')
        self._update_to_approval(ticket_id)

    def test_quota_conflict_by_awaiting_approval_irregular(self):
        """Test of integrity check error at the time of application """
        # Create a request data
        path = '/tickets'
        req = unit_test_utils.get_fake_request(method='POST',
                                               path=path)
        headers = {'x-auth-token': 'user:tenant:wf_apply',
                   'x-user-name': 'user-name',
                   'x-tenant-name': 'tenant-name'}
        for k, v in headers.iteritems():
            req.headers[k] = v

        ticket_detail = {'contract_id': CONT_UUID1,
                         'vcpu': 1,
                         'ram': 2,
                         'volume_storage': 1,
                         'Message': 'We will apply for cancellation.\n'
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
        self.stubs.UnsetAll()
        stubs.stub_fake_cast(self, 'tickets_create')
        Stubs.utils_stubout(self, 'get_nova_client_for_integrity_check_error')
        Stubs.utils_stubout(self, 'get_cinder_client')

        # Send request
        res = req.get_response(self.api)

        # Examination of response
        self.assertEqual(res.status_int, 409)

    def test_quota_conflict_by_approval_irregular(self):
        """Test of integrity check error at the time of final approval """
        self.config(smtp_server='mail.example.com', group='mail')

        ticket = self._make_awaiting_approval()
        ticket_id = ticket['id']
        self._update_skip(ticket_id, 'userA', 'wf_check',
                          'awaiting approval', 'check')

        # Create a request data
        path = '/tickets/%s' % ticket_id
        req = unit_test_utils.get_fake_request(method='PUT',
                                               path=path)
        headers = {'x-auth-token': 'admin:admin:wf_approval,admin',
                   'x-user-name': 'admin-name',
                   'x-tenant-name': 'admin-tenant-name'}
        for k, v in headers.iteritems():
            req.headers[k] = v
        session = db_api.get_session()
        last_wf = session.query(db_models.Workflow).\
            filter_by(ticket_id=ticket_id).\
            filter_by(status_code='check').one().id
        next_wf = session.query(db_models.Workflow).\
            filter_by(ticket_id=ticket_id).\
            filter_by(status_code='approval').one().id
        additional_data = {'message': 'OK'}
        body = {'ticket': {'additional_data':
                           self.serializer.to_json(additional_data),
                           'last_status_code': 'check',
                           'last_workflow_id': last_wf,
                           'next_status_code': 'approval',
                           'next_workflow_id': next_wf}}
        req.body = self.serializer.to_json(body)

        # set stubs
        # "stub_fake_call" is a stub in order to omit the queue transmission
        # When you use the "call_info",
        # you can confirm the call arguments of stub
        self.stubs.UnsetAll()
        stubs.stub_fake_cast(self, 'tickets_update')
        Stubs.utils_stubout(self, 'get_nova_client_for_integrity_check_error')
        Stubs.utils_stubout(self, 'get_cinder_client')
        Stubs.utils_stubout(self, 'get_email_address')
        Stubs.mail_stubout(self, 'sendmail')

        # Send request
        res = req.get_response(self.api)

        # Examination of response
        self.assertEqual(res.status_int, 409)
