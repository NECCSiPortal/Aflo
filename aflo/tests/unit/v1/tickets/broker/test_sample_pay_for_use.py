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
#

import datetime
import six
import uuid

from oslo_serialization import jsonutils

from aflo.common.exception import NotFound
from aflo.common import mail
from aflo.db.sqlalchemy import api as db_api
from aflo.db.sqlalchemy import models as db_models

from aflo.tests.unit import utils as unit_test_utils
from aflo.tests.unit.utils import FakeObject
from aflo.tests.unit.v1.tickets.broker import broker_test_base as base
from aflo.tests.unit.v1.tickets.broker import fixture
from aflo.tests.unit.v1.tickets.stubs import Ticket_RpcStubs as stubs
from aflo.tickets.broker.utils import utils as broker_utils

WFP_UUID1 = str(uuid.uuid4())
WFP_UUID2 = str(uuid.uuid4())
TT_UUID1 = str(uuid.uuid4())
TT_UUID2 = str(uuid.uuid4())
TKT_UUID1 = str(uuid.uuid4())
CONT_UUID1 = str(uuid.uuid4())

CONTRACT_TICKET_DETAIL = {
    'message': 'xxxxx\nxxxxx\nxxxxx'
}
CANCELLATION_TICKET_DETAIL = {
    'contract_id': CONT_UUID1,
    'message': 'xxxxx\nxxxxx\nxxxxx'
}
VCPU = 'vcpu'
RAM = 'ram'
VOLUME_STORAGE = 'volume_storage'
ERROR_MESSAGE = {
    'RAISE_NOT_FOUND_EXCEPTION':
        'An object with the specified identifier was not found.',
    'RAISE_CANCELLATION_NG_STATE':
        'Could not accept the request, it is in resource use.',
    'RAISE_NOT_FOUND_CONTRACT_GET': 'Unable to retrieve contract data. %s',
    'RAISE_CONFLICT_CONTRACT':
        'This contract has already terminated.'
}
EXCEPTION_MESSAGE = 'Exception message.'
LIFETIME_END = datetime.datetime(2016, 1, 1, 0, 0, 0, 0)


class Stubs(object):
    @classmethod
    def utils_stubout(cls, target, method):
        call_info = {}

        def fake_get_project(project_id):
            call_info['project_id'] = project_id
            project = FakeObject()
            project.setattr('name', 'xxx')
            return project

        def fake_get_user(user_id):
            call_info['user_id'] = user_id
            user = FakeObject()
            user.setattr('name', 'xxx')
            return user

        def fake_update_quotas(tenant_id, **quotas):
            call_info['tenant_id'] = tenant_id
            call_info['quotas'] = quotas
            return None

        def fake_get_email_address(user_id):
            call_info['user_id'] = user_id
            return user_id + '@example.com'

        def fake_get_email_addresses_from_role(project, roles):
            call_info['tenant'] = project
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
                info = {"absolute": {"totalCoresUsed": 0,
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

        def fake_error_get_email_address_raise_not_found(owner_id):
            raise NotFound()

        fake_managers = \
            {'get_project':
             {'method': 'get_project',
              'stub': fake_get_project},
             'get_user':
             {'method': 'get_user',
              'stub': fake_get_user},
             'update_quotas':
             {'method': 'update_quotas',
              'stub': fake_update_quotas},
             'get_email_address':
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
              'stub': fake_get_cinder_client},
             'error_get_email_address_not_found':
             {'method': 'get_email_address',
              'stub': fake_error_get_email_address_raise_not_found}}

        target.stubs.Set(broker_utils, fake_managers[method]['method'],
                         fake_managers[method]['stub'])

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

        def fake_error_get_catalog_list(ctxt, refine_flg, filters):
            call_info['context'] = ctxt
            call_info['refine_flg'] = refine_flg
            call_info['filters'] = filters
            return None

        def fake_error_get_ticket_raise_not_found(ctxt, contract_id):
            raise NotFound()

        def fake_error_get_contract_raise_exception(ctxt, contract_id):
            raise Exception(EXCEPTION_MESSAGE)

        def fake_error_contract_get(ctxt, contract_id):
            call_info['context'] = ctxt
            call_info['contract_id'] = contract_id
            contract = {}
            contract['lifetime_end'] = LIFETIME_END
            return contract

        fake_managers = {
            'error_get_catalog_list':
            {'method': 'valid_catalog_list',
             'stub': fake_error_get_catalog_list},
            'error_get_ticket_raise_not_found':
            {'method': 'tickets_get',
             'stub': fake_error_get_ticket_raise_not_found},
            'error_get_contract_raise_exception':
            {'method': 'contract_get',
             'stub': fake_error_get_contract_raise_exception},
            'error_contract_get_raise_conflict':
            {'method': 'contract_get',
             'stub': fake_error_contract_get}}

        target.stubs.Set(db_api, fake_managers[method]['method'],
                         fake_managers[method]['stub'])

        return call_info


class TestPayForUseContractHandler(base.BrokerTestBase):
    """Do a test of 'Pay-For-Use Contract'"""

    def setUp(self):
        """Establish a clean test environment."""
        super(TestPayForUseContractHandler, self).setUp()

        _set_config(self)

    def create_fixtures(self):
        super(TestPayForUseContractHandler, self).create_fixtures()

        lifetime_start = datetime.datetime.strptime(
            '2015/01/01', "%Y/%m/%d")
        lifetime_end = datetime.datetime.strptime(
            '2999/12/31', "%Y/%m/%d")

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
            db_models, WFP_UUID1, **self.wf_pattern_contents)
        self.template_contents = self._get_dict_contents(
            'template_contents_PayForUse_registration', '20160627')
        self.template_contents['target_id'] = catalog_ids
        self._create_ticket_template(
            db_models, TT_UUID1, WFP_UUID1, **self.template_contents)

    def _make_pre_approval(self):
        """Testing of the new application"""
        _set_stubs(self, 'tickets_create')
        res = _normal_system_test(self, 'user:admin:wf_apply',
                                  CONTRACT_TICKET_DETAIL)
        ticket = jsonutils.loads(res.body)['ticket']
        return ticket

    def _update_to_final_approval(self, ticket_id):
        """Test to be approved to 'accepted'"""
        # Create a request data.
        path = '/tickets/%s' % ticket_id
        req = unit_test_utils.get_fake_request(method='PUT', path=path)
        additional_data = {'message': 'xxxxx\nxxxxx\nxxxxx'}
        req.body = _create_request_data(self, ticket_id, req,
                                        'pre-approval', 'final approval',
                                        additional_data)
        _set_stubs(self, 'tickets_update')
        action_names = ['get_project', 'get_user',
                        'update_quotas', 'get_email_address']
        _set_utils_stubs(self, action_names)
        Stubs.mail_stubout(self, 'sendmail')
        _normal_system_check(self, req)

    def test_pre_approval_to_final_approval(self):
        """Test to approval from the new application."""
        ticket = self._make_pre_approval()
        ticket_id = ticket['id']
        self._update_to_final_approval(ticket_id)

    def test_error_get_catalog_not_found_exception(self):
        """Test of Not found"""
        _set_stubs(self, 'tickets_create')
        _set_api_stubs(self, ['error_get_catalog_list'])
        _error_system_test(self, 'user:admin:admin', CONTRACT_TICKET_DETAIL,
                           ERROR_MESSAGE['RAISE_NOT_FOUND_EXCEPTION'])


class TestPayForUseCancellationHandler(base.BrokerTestBase):
    """Do a test of 'Pay-For-Use Cancellation'"""

    def setUp(self):
        """Establish a clean test environment."""
        super(TestPayForUseCancellationHandler, self).setUp()

        _set_config(self)

    def create_fixtures(self):
        super(TestPayForUseCancellationHandler, self).create_fixtures()

        catalog_ids = []
        catalog_ids.append(fixture.make_catalog_only(
            VCPU, 1, 10, 'cores', None))
        catalog_ids.append(fixture.make_catalog_only(
            RAM, 4, 20, 'ram', 'GB'))
        catalog_ids.append(fixture.make_catalog_only(
            VOLUME_STORAGE, 5, 50, 'gigabytes', 'GB'))

        # make template
        self.wf_pattern_contents = self._get_dict_contents(
            'wf_pattern_PayForUseContract')
        self._create_workflow_pattern(db_models, WFP_UUID1,
                                      **self.wf_pattern_contents)

        self.template_contents = self._get_dict_contents(
            'template_contents_PayForUse_cancellation',
            '20160627')
        self.template_contents['target_id'] = catalog_ids

        self._create_ticket_template(db_models, TT_UUID1, WFP_UUID1,
                                     **self.template_contents)

        # make old contract
        self.template_contents_old = self._get_dict_contents(
            'template_contents_PayForUse_registration',
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
                           {'message': 'text'}}}
        contract.expansion_text = self.serializer.to_json(expansion_text)
        contract.lifetime_start = \
            datetime.datetime(2015, 1, 1, 0, 0, 0, 0)
        contract.lifetime_end = \
            datetime.datetime(2999, 12, 31, 23, 59, 59, 999999)
        contract.save()

    def _make_pre_approval(self):
        """Testing of the new application"""
        _set_stubs(self, 'tickets_create')
        action_names = ['get_nova_client', 'get_cinder_client']
        _set_utils_stubs(self, action_names)

        # Send request.
        res = _normal_system_test(self, 'user:admin:wf_apply',
                                  CANCELLATION_TICKET_DETAIL)
        ticket = jsonutils.loads(res.body)['ticket']

        return ticket

    def _update_to_final_approval(self, ticket_id):
        """Test to be approved to 'accepted'"""
        # Create a request data.
        path = '/tickets/%s' % ticket_id
        req = unit_test_utils.get_fake_request(method='PUT', path=path)
        additional_data = {'message': 'xxxxx\nxxxxx\nxxxxx'}
        req.body = _create_request_data(self, ticket_id, req,
                                        'pre-approval', 'final approval',
                                        additional_data)
        _set_stubs(self, 'tickets_update')
        action_names = ['get_nova_client', 'get_cinder_client', 'get_project',
                        'get_user', 'update_quotas', 'get_email_address']
        _set_utils_stubs(self, action_names)
        Stubs.mail_stubout(self, 'sendmail')
        _normal_system_check(self, req)

    def test_pre_approval_to_final_approval(self):
        """Test to approval from the new application."""
        ticket = self._make_pre_approval()
        ticket_id = ticket['id']
        self._update_to_final_approval(ticket_id)

    def test_error_get_contract_not_found(self):
        """Test of Not Found"""
        _set_stubs(self, 'tickets_create')
        _set_api_stubs(self, ['error_get_contract_raise_exception'])
        _error_system_test(self, 'user:admin:wf_apply',
                           CANCELLATION_TICKET_DETAIL,
                           ERROR_MESSAGE['RAISE_NOT_FOUND_CONTRACT_GET'] %
                           EXCEPTION_MESSAGE)

    def test_error_get_contract_conflict(self):
        """Test of Conflict"""
        _set_stubs(self, 'tickets_create')
        Stubs.api_stubout(self, 'error_contract_get_raise_conflict')
        _error_system_test(self, 'user:admin:wf_apply',
                           CANCELLATION_TICKET_DETAIL,
                           ERROR_MESSAGE['RAISE_CONFLICT_CONTRACT'])

    def test_get_ticket_not_found_exception(self):
        """Test of Not Found"""
        _set_stubs(self, 'tickets_create')
        Stubs.api_stubout(self, 'error_get_ticket_raise_not_found')
        action_names = ['get_nova_client', 'get_cinder_client']
        _set_utils_stubs(self, action_names)
        _normal_system_test(self, 'user:admin:wf_apply',
                            CANCELLATION_TICKET_DETAIL)

    def test_get_nova_limit_used_keys_not_found(self):
        """Test of Limit used"""
        nova_limit_used_keys = broker_utils.NOVA_LIMIT_USED_KEYS
        broker_utils.NOVA_LIMIT_USED_KEYS = {'test': 'test'}

        _set_stubs(self, 'tickets_create')
        action_names = ['get_nova_client', 'get_cinder_client']
        _set_utils_stubs(self, action_names)
        _normal_system_test(self, 'user:admin:wf_apply',
                            CANCELLATION_TICKET_DETAIL)

        broker_utils.NOVA_LIMIT_USED_KEYS = nova_limit_used_keys

    def test_error_quota_use_size_check(self):
        """Test of Used resources"""
        _set_stubs(self, 'tickets_create')
        action_names = ['get_nova_client_for_integrity_check_error',
                        'get_cinder_client']
        _set_utils_stubs(self, action_names)
        _error_system_test(self, 'user:admin:wf_apply',
                           CANCELLATION_TICKET_DETAIL,
                           ERROR_MESSAGE['RAISE_CANCELLATION_NG_STATE'])

    def test_error_get_email_address_not_found(self):
        """Test to approval from the new application."""
        ticket = self._make_pre_approval()
        ticket_id = ticket['id']
        # Create a request data.
        path = '/tickets/%s' % ticket_id
        req = unit_test_utils.get_fake_request(method='PUT', path=path)
        additional_data = {'message': 'xxxxx\nxxxxx\nxxxxx'}
        req.body = _create_request_data(self, ticket_id, req,
                                        'pre-approval', 'final approval',
                                        additional_data)
        _set_stubs(self, 'tickets_update')
        action_names = ['get_nova_client', 'get_cinder_client',
                        'get_project', 'get_user', 'update_quotas',
                        'error_get_email_address_not_found']
        _set_utils_stubs(self, action_names)
        _error_system_check(self, req,
                            ERROR_MESSAGE['RAISE_NOT_FOUND_EXCEPTION'])


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


def _create_request_headers(auth_token):
    path = '/tickets'
    headers = {'x-auth-token': auth_token,
               'x-user-name': 'user-name',
               'x-tenant-name': 'tenant-name'}
    req = unit_test_utils.get_fake_request(method='POST', path=path)
    for (k, v) in six.iteritems(headers):
        req.headers[k] = v
    return req


def _create_request_body(self, ticket_detail):
    body = {'ticket': {
        'ticket_template_id': TT_UUID1,
        'ticket_detail': self.serializer.to_json(ticket_detail),
        'status_code': self.template_contents['first_status_code']}}
    return self.serializer.to_json(body)


def _create_request_data(self, ticket_id, req, last_status_code,
                         next_status_code, additional_data):
    headers = {'x-auth-token': 'admin:admin:_member_',
               'x-user-name': 'admin-name',
               'x-tenant-name': 'admin-tenant-name'}
    for k, v in headers.iteritems():
        req.headers[k] = v
    session = db_api.get_session()
    last_wf = session.query(
        db_models.Workflow).filter_by(ticket_id=ticket_id).filter_by(
            status_code=last_status_code).one().id
    next_wf = session.query(db_models.Workflow).filter_by(
        ticket_id=ticket_id).filter_by(
            status_code=next_status_code).one().id
    body = {'ticket': {
        'additional_data': self.serializer.to_json(additional_data),
        'last_status_code': last_status_code,
        'last_workflow_id': last_wf,
        'next_status_code': next_status_code,
        'next_workflow_id': next_wf}}
    return self.serializer.to_json(body)


def _normal_system_check(self, req):
    # Send request.
    res = req.get_response(self.api)
    # Examination of response.
    self.assertEqual(res.status_int, 200)
    return res


def _normal_system_test(self, auth_token, ticket_detail):
    req = _create_request_headers(auth_token)
    req.body = _create_request_body(self, ticket_detail)
    res = _normal_system_check(self, req)
    return res


def _error_system_check(self, req, error_message):
    try:
        # Send request.
        req.get_response(self.api)
    except Exception as e:
        # Examination of response.
        self.assertEqual(e.args[0], error_message)


def _error_system_test(self, auth_token, ticket_detail, error_message):
    req = _create_request_headers(auth_token)
    req.body = _create_request_body(self, ticket_detail)
    _error_system_check(self, req, error_message)


def _set_utils_stubs(self, action_names):
    # utils stubs set
    for action_name in action_names:
        Stubs.utils_stubout(self, action_name)


def _set_api_stubs(self, action_names):
    # api stubs set
    for action_name in action_names:
        Stubs.api_stubout(self, action_name)


def _set_stubs(self, action_name):
    # Set stubs.
    self.stubs.UnsetAll()
    stubs.stub_fake_cast(self, action_name)
