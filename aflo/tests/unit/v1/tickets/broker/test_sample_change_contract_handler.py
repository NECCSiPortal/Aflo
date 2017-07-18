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
import six
import uuid

from oslo_config import cfg
from oslo_serialization import jsonutils

from aflo.common import mail
from aflo.db.sqlalchemy import api as db_api
from aflo.db.sqlalchemy import models as db_models
from aflo.mail import mail_template_contract_registration

from aflo.tests.unit import utils as unit_test_utils
from aflo.tests.unit.utils import FakeObject
from aflo.tests.unit.v1.tickets.broker import broker_test_base as base
from aflo.tests.unit.v1.tickets.broker import fixture
from aflo.tests.unit.v1.tickets.stubs import Ticket_RpcStubs as stubs
from aflo.tickets.broker.utils import contract_utils
from aflo.tickets.broker.utils import utils as broker_utils

CONF = cfg.CONF

WFP_UUID1 = str(uuid.uuid4())
WFP_UUID2 = str(uuid.uuid4())
TT_UUID1 = str(uuid.uuid4())
TT_UUID2 = str(uuid.uuid4())
TT_UUID3 = str(uuid.uuid4())
TT_UUID4 = str(uuid.uuid4())
T_UUID1 = str(uuid.uuid4())
T_UUID2 = str(uuid.uuid4())
C_UUID1 = str(uuid.uuid4())
C_UUID2 = str(uuid.uuid4())

VERSION = '20160627'

VCPU = 'vcpu'
RAM = 'ram'
VOLUME_STORAGE = 'volume_storage'

TICKET_DETAIL_FLAT_RATE = {
    VCPU: 1,
    RAM: 4,
    VOLUME_STORAGE: 5,
    'message': 'xxxxx\nxxxxx\nxxxxx'
}
TICKET_DETAIL_PAY_FOR_USE = {
    'message': 'xxxxx\nxxxxx\nxxxxx'
}
METHOD = {
    'POST': 'POST',
    'PUT': 'PUT'
}
ERROR_MESSAGE = {
    'RAISE_DURING_CONTRACT':
        'Could not accept the request, it is under contract',
    'RAISE_NOT_FOUND_GET_CONTRACT_LIST':
        '%s contract does not exist.',
    'RAISE_NOT_FOUND_CREATE_CONTRACT':
        'Failed to register the contract.',
    'RAISE_NOT_FOUND_UPDATE_QUOTAS':
        'Failed to update the quotas.'
}


class Stubs(object):
    @classmethod
    def contract_utils_stubout(cls, target, method):
        """method which method to stub out of
        'aflo.tickets.broker.utils.contract_utils'.
        :param target: Target process.
        :param method: Called function.
        """
        call_info = {}

        def fake_error_create_contract_raise_exception(
                ctxt, template, ticket, project_id, project_name,
                application_name, contract_key, lifetime_start):
            raise Exception()

        def fake_error_is_during_contract(
                ctxt, contract_keys, project_id):
            _make_call_info(ctxt, contract_keys, project_id)
            return True

        def fake_error_is_not_during_contract(
                ctxt, contract_keys, project_id):
            _make_call_info(ctxt, contract_keys, project_id)
            return False

        def _make_call_info(ctxt, contract_keys, project_id):
            call_info['ctxt'] = ctxt
            call_info['contract_keys'] = contract_keys
            call_info['project_id'] = project_id

        fake_managers = {
            'error_create_contract_raise_exception':
                {'method': 'create_contract',
                 'stub': fake_error_create_contract_raise_exception},
            'error_is_during_contract':
                {'method': 'is_during_contract',
                 'stub': fake_error_is_during_contract},
            'error_is_not_during_contract':
                {'method': 'is_during_contract',
                 'stub': fake_error_is_not_during_contract}
        }
        target.stubs.Set(contract_utils, fake_managers[method]['method'],
                         fake_managers[method]['stub'])

        return call_info

    @classmethod
    def utils_stubout(cls, target, method):
        """method which method to stub out of 'aflo.tickets.broker.utils'.
        :param target: Target process.
        :param method: Called function.
        """
        call_info = {}

        def fake_get_email_address(user_id):
            call_info['user_id'] = user_id
            return user_id + '@example.com'

        def fake_get_nova_client():
            class Client(object):
                def __init__(self, username=None, api_key=None,
                             project_id=None, auth_url=None):
                    self.limits = LimitsManager()
                    self.quotas = QuotaSetManager()

            class QuotaSet(object):
                info = {"cores": 20, "ram": 51200}

                def to_dict(self):
                    return self.info

            class Limits(object):
                info = {
                    "absolute": {
                        "totalCoresUsed": 0,
                        "totalRAMUsed": 0
                    }
                }

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
                gigabytes = {u'limit': 1000, u'reserved': 0, u'in_use': 0}

            class QuotaSetManager(object):
                def get(self, tenant_id, user_id=None, usage=None):
                    if not usage:
                        return QuotaSet()
                    else:
                        return QuotaSetUsage()

                def update(self, tenant_id, **update_val):
                    pass

            return Client()

        def fake_get_user(user_id):
            call_info['user_id'] = user_id
            user = FakeObject()
            user.setattr('name', 'xxxxx')
            return user

        def fake_get_project(project_id):
            call_info['project_id'] = project_id
            project = FakeObject()
            project.setattr('name', 'xxxxx')
            return project

        def fake_error_update_quotas_raise_exception(user_id):
            raise Exception()

        fake_managers = {
            'get_email_address':
                {'method': 'get_email_address',
                 'stub': fake_get_email_address},
            'get_nova_client':
                {'method': 'get_nova_client',
                 'stub': fake_get_nova_client},
            'get_cinder_client':
                {'method': 'get_cinder_client',
                 'stub': fake_get_cinder_client},
            'get_user':
                {'method': 'get_user',
                 'stub': fake_get_user},
            'get_project':
                {'method': 'get_project',
                 'stub': fake_get_project},
            'error_update_quotas_raise_exception':
                {'method': 'update_quotas',
                 'stub': fake_error_update_quotas_raise_exception}
        }
        target.stubs.Set(broker_utils, fake_managers[method]['method'],
                         fake_managers[method]['stub'])

        return call_info

    @classmethod
    def mail_stubout(cls, target, method):
        """method which method to stub out of 'aflo.tickets.broker.utils'.
        :param target: Target process.
        :param method: Called function.
        """
        call_info = {}

        def fake_sendmail(
            to_address, template, data, cc_address=None, bcc_address=None,
                encode=None, from_address=None, smtp_server=None):
            call_info['to_address'] = to_address
            call_info['template'] = template
            call_info['data'] = data

        fake_managers = {'sendmail': fake_sendmail}
        target.stubs.Set(mail, method, fake_managers[method])

        return call_info

    @classmethod
    def api_stubout(cls, target, method):
        """method which method to stub out of 'aflo.db.sqlalchemy.api'.
        :param target: Target process.
        :param method: Called function.
        """
        call_info = {}

        def fake_contract_list(ctxt, project_id):
            call_info['context'] = ctxt
            call_info['project_id'] = project_id

            contract = FakeObject()
            contract.setattr('name', 'xxxxxxxxxx')
            return [contract]

        def fake_error_get_not_found_contract_list(ctxt, project_id):
            call_info['context'] = ctxt
            call_info['project_id'] = project_id

            return []

        fake_managers = {
            'contract_list':
                {'method': 'contract_list',
                 'stub': fake_contract_list},
            'error_get_not_found_contract_list':
                {'method': 'contract_list',
                 'stub': fake_error_get_not_found_contract_list}
        }
        target.stubs.Set(db_api, fake_managers[method]['method'],
                         fake_managers[method]['stub'])

        return call_info


class TestChangeToFlatRateContractHandler(base.BrokerTestBase):
    """Do a test of 'Change To FlatRate Contract'"""

    def setUp(self):
        """Establish a clean test environment"""
        super(TestChangeToFlatRateContractHandler, self).setUp()

        _set_config(self)

    def create_fixtures(self):
        super(TestChangeToFlatRateContractHandler, self).create_fixtures()

        _create_registration_data(
            self, WFP_UUID1, TT_UUID1, TT_UUID2, T_UUID1, C_UUID1,
            'contract-pay-for-use',
            'template_contents_SampleChangeContract_flat_rate',
            'template_contents_PayForUse_registration', VERSION)

    def test_pre_approval_to_final_approval(self):
        """Test from a new application (pre-approval)
        until final approval.
        """
        ticket = _make_pre_approval(self, TT_UUID1, TICKET_DETAIL_FLAT_RATE)
        ticket_id = ticket['id']

        _update_to_final_approval(self, ticket_id)

    def test_error_raise_during_contract_by_is_during_contract(self):
        """Test of during contract"""
        _tickets_create_error(
            self, TT_UUID1, TICKET_DETAIL_FLAT_RATE,
            'error_is_during_contract', ERROR_MESSAGE['RAISE_DURING_CONTRACT'],
            True)

    def test_error_raise_not_found_by_is_not_during_contract(self):
        """Test of not found"""
        _tickets_create_error(
            self, TT_UUID1, TICKET_DETAIL_FLAT_RATE,
            'error_is_not_during_contract',
            ERROR_MESSAGE['RAISE_NOT_FOUND_GET_CONTRACT_LIST'] % 'Pay-for-use',
            True)

    def test_error_raise_not_found_by_create_contract(self):
        """Test of not found"""
        _tickets_update_error(
            self, TT_UUID1, TICKET_DETAIL_FLAT_RATE,
            'error_create_contract_raise_exception',
            ERROR_MESSAGE['RAISE_NOT_FOUND_CREATE_CONTRACT'], 'contract')

    def test_error_raise_not_found_by_update_quotas(self):
        """Test of not found"""
        _tickets_update_error(
            self, TT_UUID1, TICKET_DETAIL_FLAT_RATE,
            'error_update_quotas_raise_exception',
            ERROR_MESSAGE['RAISE_NOT_FOUND_UPDATE_QUOTAS'], 'base')


class TestChangeToPayForUseContractHandler(base.BrokerTestBase):
    """Do a test of 'Change To PayForUse Contract'"""

    def setUp(self):
        """Establish a clean test environment"""
        super(TestChangeToPayForUseContractHandler, self).setUp()

        _set_config(self)

    def create_fixtures(self):
        super(TestChangeToPayForUseContractHandler, self).create_fixtures()

        _create_registration_data(
            self, WFP_UUID2, TT_UUID3, TT_UUID4, T_UUID2, C_UUID2,
            'contract-flat-rate',
            'template_contents_SampleChangeContract_pay_for_use',
            'template_contents_SampleSetCatalogMonthly_registration', VERSION)

    def test_pre_approval_to_final_approval(self):
        """Test from a new application (pre-approval)
        until final approval.
        """
        ticket = _make_pre_approval(self, TT_UUID3, TICKET_DETAIL_PAY_FOR_USE)
        ticket_id = ticket['id']

        _update_to_final_approval(self, ticket_id, True)

    def test_error_raise_during_contract_by_is_during_contract(self):
        """Test of during contract"""
        _tickets_create_error(
            self, TT_UUID3, TICKET_DETAIL_PAY_FOR_USE,
            'error_is_during_contract', ERROR_MESSAGE['RAISE_DURING_CONTRACT'],
            True)

    def test_error_raise_during_contract_by_is_not_during_contract(self):
        """Test of during contract"""
        _tickets_create_error(
            self, TT_UUID3, TICKET_DETAIL_PAY_FOR_USE,
            'error_is_not_during_contract',
            ERROR_MESSAGE['RAISE_NOT_FOUND_GET_CONTRACT_LIST'] % 'Flat-rate',
            True)

    def test_error_raise_not_found_by_create_contract(self):
        """Test of not found"""
        _tickets_update_error(
            self, TT_UUID3, TICKET_DETAIL_PAY_FOR_USE,
            'error_create_contract_raise_exception',
            ERROR_MESSAGE['RAISE_NOT_FOUND_CREATE_CONTRACT'], 'contract', True)

    def test_error_raise_not_found_by_update_quotas(self):
        """Test of not found"""
        _tickets_update_error(
            self, TT_UUID3, TICKET_DETAIL_PAY_FOR_USE,
            'error_update_quotas_raise_exception',
            ERROR_MESSAGE['RAISE_NOT_FOUND_UPDATE_QUOTAS'], 'base', True)


def _set_config(self):
    self.config(encode='utf-8', group='mail')
    self.config(from_address='user@example.com', group='mail')
    self.config(smtp_server='mail.example.com', group='mail')
    self.config(user='user', group='mail')
    self.config(password='xxxx', group='mail')

    self.config(username='admin', group='keystone_client')
    self.config(password='xxxx', group='keystone_client')
    self.config(tenant_name='admin', group='keystone_client')
    self.config(region_name='RegionOne', group='keystone_client')
    self.config(auth_url='http://127.0.0.1:5000/v3',
                group='keystone_client')
    self.config(auth_version='3', group='keystone_client')
    self.config(user_domain_id='default', group='keystone_client')
    self.config(project_domain_id='default', group='keystone_client')


def _create_registration_data(
        self, workflow_pattern_id, ticket_template_id,
        contract_ticket_template_id, ticket_id, contract_id, expansion_key,
        template_contents_file_prefix, contract_template_contents_file_prefix,
        version):
    # Make catalog.
    lifetime_start = datetime.datetime(2016, 1, 1, 0, 0, 0, 0)
    lifetime_end = datetime.datetime(9999, 12, 31, 23, 59, 59, 999999)

    catalog_ids = []
    catalog_ids.append(fixture.make_catalog(
        VCPU, 1, 10, 'cores', None, lifetime_start, lifetime_end))
    catalog_ids.append(fixture.make_catalog(
        RAM, 4, 20, 'ram', 'GB', lifetime_start, lifetime_end))
    catalog_ids.append(fixture.make_catalog(
        VOLUME_STORAGE, 5, 50, 'gigabytes', 'GB',
        lifetime_start, lifetime_end))

    self.wf_pattern_contents = self._get_dict_contents(
        'wf_pattern_PayForUseContract')
    self._create_workflow_pattern(
        db_models, workflow_pattern_id, **self.wf_pattern_contents)
    self.template_contents = self._get_dict_contents(
        template_contents_file_prefix, version)
    self.template_contents['target_id'] = catalog_ids
    self._create_ticket_template(
        db_models, ticket_template_id, workflow_pattern_id,
        **self.template_contents)

    self.template_contents = self._get_dict_contents(
        contract_template_contents_file_prefix, version)
    self.template_contents['target_id'] = catalog_ids
    self._create_ticket_template(
        db_models, contract_ticket_template_id, workflow_pattern_id,
        **self.template_contents)

    ticket = db_models.Ticket(id=ticket_id)
    ticket.ticket_template_id = contract_ticket_template_id
    ticket.ticket_type = 'ticket_type'
    ticket.target_id = self.serializer.to_json(catalog_ids)
    ticket.tenant_id = 'admin'
    ticket.save()
    contract = db_models.Contract(contract_id=contract_id)
    contract.application_id = ticket.id
    contract.project_id = 'admin'
    expansion_text = {
        'contract_info': {
            'ticket_detail': {
                'message': 'text'
            }
        }
    }
    contract.expansion_text = self.serializer.to_json(expansion_text)
    contract.lifetime_start = lifetime_start
    contract.lifetime_end = lifetime_end
    contract.expansion_key1 = expansion_key
    contract.save()


def _create_request_headers():
    path = '/tickets'
    req = unit_test_utils.get_fake_request(
        method=METHOD['POST'], path=path)
    headers = {
        'x-auth-token': 'user:admin:wf_apply',
        'x-user-name': 'user-name',
        'x-tenant-name': 'tenant-name'
    }
    for (k, v) in six.iteritems(headers):
        req.headers[k] = v
    return req


def _create_request_body(self, ticket_template_id, ticket_detail):
    body = {
        'ticket': {
            'ticket_template_id': ticket_template_id,
            'ticket_detail': self.serializer.to_json(ticket_detail),
            'status_code': self.template_contents['first_status_code']
        }
    }
    return self.serializer.to_json(body)


def _create_request_data(self, ticket_id, req):
    headers = {
        'x-auth-token': 'admin:admin:_member_',
        'x-user-name': 'admin-name',
        'x-tenant-name': 'admin-tenant-name'
    }
    for k, v in headers.iteritems():
        req.headers[k] = v
    last_status_code = 'pre-approval'
    next_status_code = 'final approval'
    session = db_api.get_session()
    last_wf = session.query(
        db_models.Workflow).filter_by(ticket_id=ticket_id).filter_by(
            status_code=last_status_code).one().id
    next_wf = session.query(db_models.Workflow).filter_by(
        ticket_id=ticket_id).filter_by(
            status_code=next_status_code).one().id
    body = {
        'ticket': {
            'additional_data':
                self.serializer.to_json({'message': 'xxxxx\nxxxxx\nxxxxx'}),
            'last_status_code': last_status_code,
            'last_workflow_id': last_wf,
            'next_status_code': next_status_code,
            'next_workflow_id': next_wf
        }
    }
    return self.serializer.to_json(body)


def _make_pre_approval(self, ticket_template_id, ticket_detail):
    """Testing of the new application"""
    # Create a request data.
    req = _create_request_headers()
    req.body = _create_request_body(
        self, ticket_template_id, ticket_detail)

    _set_stubs(self, 'tickets_create')
    Stubs.utils_stubout(self, 'get_nova_client')
    Stubs.utils_stubout(self, 'get_cinder_client')

    # Send request.
    res = req.get_response(self.api)

    # Examination of response.
    self.assertEqual(res.status_int, 200)

    return jsonutils.loads(res.body)['ticket']


def _update_to_final_approval(self, ticket_id, add_fake_stubs_flag=False):
    """Test to be approved to 'final approval'"""
    # Create a request data.
    path = '/tickets/%s' % ticket_id
    req = unit_test_utils.get_fake_request(method=METHOD['PUT'], path=path)
    req.body = _create_request_data(self, ticket_id, req)

    _set_stubs(self, 'tickets_update')
    if add_fake_stubs_flag:
        Stubs.utils_stubout(self, 'get_project')
        Stubs.utils_stubout(self, 'get_user')
    Stubs.utils_stubout(self, 'get_nova_client')
    Stubs.utils_stubout(self, 'get_cinder_client')
    Stubs.utils_stubout(self, 'get_email_address')
    call_info = Stubs.mail_stubout(self, 'sendmail')

    # Send request.
    res = req.get_response(self.api)

    # Examination of response.
    self.assertEqual(res.status_int, 200)
    self.assertTrue('user@example.com' in call_info['to_address'])
    self.assertEqual(call_info['template'].SUBJECT,
                     mail_template_contract_registration.SUBJECT)


def _tickets_create_error(
        self, ticket_template_id, ticket_detail, fake_stub_name,
        error_message, raise_flag=False):
    # Create a request data.
    req = _create_request_headers()
    req.body = _create_request_body(self, ticket_template_id, ticket_detail)

    _set_stubs(self, 'tickets_create')
    if raise_flag:
        Stubs.utils_stubout(self, 'get_nova_client')
        Stubs.utils_stubout(self, 'get_cinder_client')
        Stubs.contract_utils_stubout(self, fake_stub_name)
    else:
        Stubs.api_stubout(self, fake_stub_name)

    try:
        # Send request.
        req.get_response(self.api)
    except Exception as e:
        # Examination of response.
        self.assertEqual(e.args[0], error_message)


def _tickets_update_error(
        self, ticket_template_id, ticket_detail, fake_stub_name,
        error_message, use_stubs, add_fake_stubs_flag=False):
    """Test to be approved error"""
    ticket = _make_pre_approval(self, ticket_template_id, ticket_detail)
    ticket_id = ticket['id']

    # Create a request data.
    path = '/tickets/%s' % ticket_id
    req = unit_test_utils.get_fake_request(method=METHOD['PUT'], path=path)
    req.body = _create_request_data(self, ticket_id, req)

    _set_stubs(self, 'tickets_update')
    if add_fake_stubs_flag:
        Stubs.utils_stubout(self, 'get_project')
        Stubs.utils_stubout(self, 'get_user')
    Stubs.utils_stubout(self, 'get_nova_client')
    Stubs.utils_stubout(self, 'get_cinder_client')
    if 'contract' == use_stubs:
        Stubs.contract_utils_stubout(self, fake_stub_name)
    elif 'base' == use_stubs:
        Stubs.utils_stubout(self, fake_stub_name)
    try:
        # Send request.
        req.get_response(self.api)
    except Exception as e:
        # Examination of response.
        self.assertEqual(e.args[0], error_message)


def _set_stubs(self, action_name):
    # Set stubs.
    # "stub_fake_call" is a stub in order to omit the queue transmission.
    # When you use the "call_info",
    # you can confirm the call arguments of stub.
    self.stubs.UnsetAll()
    stubs.stub_fake_cast(self, action_name)
