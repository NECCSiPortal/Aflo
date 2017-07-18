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

import copy
import datetime
import six
import uuid

from oslo_config import cfg
from oslo_serialization import jsonutils

from aflo.common import mail
from aflo.db.sqlalchemy import api as db_api
from aflo.db.sqlalchemy import models as db_models
from aflo.mail.project_contract import \
    mail_cancel_project_contract_final_approval
from aflo.mail.project_contract import mail_project_contract_accept

from aflo.tests.unit import utils as unit_test_utils
from aflo.tests.unit.utils import FakeObject
from aflo.tests.unit.v1.tickets.broker import broker_test_base as base
from aflo.tests.unit.v1.tickets.stubs import Ticket_RpcStubs as stubs
from aflo.tickets.broker.utils import contract_utils
from aflo.tickets.broker.utils import utils as broker_utils

CONF = cfg.CONF

WFP_UUID1 = str(uuid.uuid4())
WFP_UUID2 = str(uuid.uuid4())
TT_UUID1 = str(uuid.uuid4())
TT_UUID2 = str(uuid.uuid4())
T_UUID1 = str(uuid.uuid4())
W_UUID1 = str(uuid.uuid4())

INPUT_DATA = 'xxxxxxxxxx'
TICKET_DETAIL = {
    'user_name': INPUT_DATA,
    'email': 'xxxxx@xxxxx.xxxxx',
    'project_name': INPUT_DATA,
    'preferred_date': '2016-06-27T00:00:00.000000',
    'message': 'xxxxx\nxxxxx\nxxxxx'
}
UUID_INPUT_DATA = 'xxxxxx-xxxxx-xxxxxx-xxxxx-xxxxxx'
CANCEL_TICKET_DETAIL = {
    'contract_id': UUID_INPUT_DATA,
    'preferred_date': '2016-06-27T00:00:00.000000',
    'message': 'xxxxx\nxxxxx\nxxxxx'
}
DONE_ADDITIONAL_DATA = {
    'project_id': UUID_INPUT_DATA,
    'user_id': UUID_INPUT_DATA,
    'join_date': '2016-06-27T00:00:00.000000',
    'message': 'xxxxx\nxxxxx\nxxxxx'
}
FINAL_APPROVAL_ADDITIONAL_DATA = {
    'withdrawal_date': '2016-06-27T00:00:00.000000',
    'message': 'xxxxx\nxxxxx\nxxxxx'
}
LIFETIME_START = datetime.datetime(2016, 1, 1, 0, 0, 0, 0)
LIFETIME_END_NOT_CANCEL = datetime.datetime(9999, 12, 31, 23, 59, 59, 999999)
ERROR_MESSAGE = {
    'RAISE_NOT_FOUND_GET_EMAIL_ADDRESS_FROM_ROLE':
        'Unable to retrieve email address. %s',
    'RAISE_NOT_FOUND_NONE_EMAIL_ADDRESS':
        'E-mail address has not been set in the contract manager.',
    'RAISE_NOT_FOUND_GET_USER_LIST': 'Unable to retrieve user list. %s',
    'RAISE_CONFLICT_GET_USER_LIST': 'User name %s is already used.',
    'RAISE_NOT_FOUND_GET_PROJECT_LIST': 'Unable to retrieve project list. %s',
    'RAISE_CONFLICT_GET_PROJECT_LIST': 'Project name %s is already used.',
    'RAISE_NOT_FOUND_GET_USER': 'Unable to retrieve user data. %s',
    'RAISE_INVALID_GET_USER': '%s of the user ID does not exist.',
    'RAISE_NOT_FOUND_GET_PROJECT': 'Unable to retrieve project data. %s',
    'RAISE_INVALID_GET_PROJECT': '%s of the project ID does not exist.',
    'RAISE_NOT_FOUND_CREATE_CONTRACT':
        'Failed to register the project contract. %s',
    'RAISE_NOT_FOUND_GET_CHILD_PROJECT_LIST':
        'Unable to retrieve project data. %s',
    'RAISE_CONFLICT_GET_CHILD_PROJECT_LIST': 'Child project exists.',
    'RAISE_NOT_FOUND_GET_WORKFLOW_LIST': 'Unable to retrieve workflow data.',
    'RAISE_CONFLICT_GET_CONTRACT': 'It is canceled of contract.',
    'RAISE_NOT_FOUND_GET_CONTRACT': 'Unable to retrieve contract data. %s',
    'RAISE_NOT_FOUND_UPDATE_CONTRACT':
        'Failed to register the project contract. %s'
}
EXCEPTION_MESSAGE = 'Exception message.'


class Stubs(object):
    @classmethod
    def contract_utils_stubout(cls, target, method):
        """method which method to stub out of
        'aflo.tickets.broker.contract_utils'.
        :param target: Target process.
        :param method: Called function.
        """

        def fake_error_create_contract_raise_exception(
                ctxt, template, ticket, project_id, project_name,
                application_name, contract_key, lifetime_start=None):
            raise Exception(EXCEPTION_MESSAGE)

        fake_managers = {
            'error_create_contract_raise_exception':
                {'method': 'create_contract',
                 'stub': fake_error_create_contract_raise_exception},
        }
        target.stubs.Set(contract_utils, fake_managers[method]['method'],
                         fake_managers[method]['stub'])

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

        def fake_get_email_addresses_from_role(project, roles):
            call_info['tenant'] = project
            call_info['roles'] = roles
            rtn = []
            for role in roles:
                rtn.append(role + '@example.com')
            return list(set(rtn))

        def fake_error_get_email_addresses_from_role_raise_exception(
                project, roles):
            raise Exception(EXCEPTION_MESSAGE)

        def fake_error_get_not_found_email_addresses_from_role(
                project, roles):
            call_info['tenant'] = project
            call_info['roles'] = roles
            return None

        def fake_get_user_list():
            user = FakeObject()
            user.setattr('name', 'xxx')
            return [user]

        def fake_error_get_user_list_raise_exception():
            raise Exception(EXCEPTION_MESSAGE)

        def fake_error_get_conflict_user_list():
            user = FakeObject()
            user.setattr('name', INPUT_DATA)
            return [user]

        def fake_get_project_list():
            project = FakeObject()
            project.setattr('name', 'xxx')
            return [project]

        def fake_error_get_project_list_raise_exception():
            raise Exception(EXCEPTION_MESSAGE)

        def fake_error_get_conflict_project_list():
            project = FakeObject()
            project.setattr('name', INPUT_DATA)
            return [project]

        def fake_get_user(user_id):
            call_info['user_id'] = user_id
            user = FakeObject()
            user.setattr('name', 'xxx')
            return user

        def fake_error_get_not_found_user(user_id):
            call_info['user_id'] = user_id
            user = FakeObject()
            user.setattr('name', 'xxx')
            return user

        def fake_error_get_invalid_user(user_id):
            call_info['user_id'] = user_id
            return None

        def fake_get_project(project_id):
            call_info['project_id'] = project_id
            project = FakeObject()
            project.setattr('name', 'xxx')
            return project

        def fake_error_get_project_raise_exception(user_id):
            raise Exception(EXCEPTION_MESSAGE)

        def fake_error_get_invalid_project(project_id):
            call_info['project_id'] = project_id
            return None

        def fake_get_child_project_list(project_id):
            call_info['project_id'] = project_id
            return None

        def fake_error_get_child_project_list_raise_exception(project_id):
            raise Exception(EXCEPTION_MESSAGE)

        def fake_error_get_conflict_child_project_list(project_id):
            call_info['project_id'] = project_id
            project = FakeObject()
            project.setattr('name', 'xxx')
            return project

        fake_managers = {
            'get_email_address':
                {'method': 'get_email_address',
                 'stub': fake_get_email_address},
            'get_email_addresses_from_role':
                {'method': 'get_email_addresses_from_role',
                 'stub': fake_get_email_addresses_from_role},
            'error_get_email_addresses_from_role_raise_exception':
                {'method': 'get_email_addresses_from_role',
                 'stub':
                    fake_error_get_email_addresses_from_role_raise_exception},
            'error_get_not_found_email_addresses_from_role':
                {'method': 'get_email_addresses_from_role',
                 'stub':
                    fake_error_get_not_found_email_addresses_from_role},
            'get_user_list':
                {'method': 'get_user_list',
                 'stub': fake_get_user_list},
            'error_get_user_list_raise_exception':
                {'method': 'get_user_list',
                 'stub': fake_error_get_user_list_raise_exception},
            'error_get_conflict_user_list':
                {'method': 'get_user_list',
                 'stub': fake_error_get_conflict_user_list},
            'get_project_list':
                {'method': 'get_project_list',
                 'stub': fake_get_project_list},
            'error_get_project_list_raise_exception':
                {'method': 'get_project_list',
                 'stub': fake_error_get_project_list_raise_exception},
            'error_get_conflict_project_list':
                {'method': 'get_project_list',
                 'stub': fake_error_get_conflict_project_list},
            'get_user':
                {'method': 'get_user',
                 'stub': fake_get_user},
            'error_get_not_found_user':
                {'method': 'get_user',
                 'stub': fake_error_get_not_found_user},
            'error_get_invalid_user':
                {'method': 'get_user',
                 'stub': fake_error_get_invalid_user},
            'get_project':
                {'method': 'get_project',
                 'stub': fake_get_project},
            'error_get_project_raise_exception':
                {'method': 'get_project',
                 'stub': fake_error_get_project_raise_exception},
            'error_get_invalid_project':
                {'method': 'get_project',
                 'stub': fake_error_get_invalid_project},
            'get_child_project_list':
                {'method': 'get_child_project_list',
                 'stub': fake_get_child_project_list},
            'error_get_child_project_list_raise_exception':
                {'method': 'get_child_project_list',
                 'stub': fake_error_get_child_project_list_raise_exception},
            'error_get_conflict_child_project_list':
                {'method': 'get_child_project_list',
                 'stub': fake_error_get_conflict_child_project_list}
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

        def fake_error_get_not_found_contract(ctxt, contract_id):
            return _create_contract(ctxt, contract_id, None, None)

        def fake_error_get_conflict_contract(ctxt, contract_id):
            return _create_contract(ctxt, contract_id, T_UUID1, LIFETIME_START)

        def _create_contract(ctxt, contract_id, ticket_id, lifetime_end):
            call_info['context'] = ctxt
            call_info['contract_id'] = contract_id

            contract = {}
            contract['application_id'] = ticket_id
            contract['lifetime_end'] = lifetime_end
            return contract

        def fake_error_get_contract_raise_exception(ctxt, contract_id):
            raise Exception(EXCEPTION_MESSAGE)

        def fake_error_update_contract_raise_exception(
                ctxt, contract_id, **contract_update_values):
            raise Exception(EXCEPTION_MESSAGE)

        fake_managers = {
            'error_get_not_found_contract':
                {'method': 'contract_get',
                 'stub': fake_error_get_not_found_contract},
            'error_get_conflict_contract':
                {'method': 'contract_get',
                 'stub': fake_error_get_conflict_contract},
            'error_get_contract_raise_exception':
                {'method': 'contract_get',
                 'stub': fake_error_get_contract_raise_exception},
            'error_update_contract_raise_exception':
                {'method': 'contract_update',
                 'stub': fake_error_update_contract_raise_exception}
        }
        target.stubs.Set(db_api, fake_managers[method]['method'],
                         fake_managers[method]['stub'])

        return call_info


class TestNewProjectContractHandler(base.BrokerTestBase):
    """Do a test of 'New Project Contract'"""

    def setUp(self):
        """Establish a clean test environment."""
        super(TestNewProjectContractHandler, self).setUp()

        _set_config(self)

    def create_fixtures(self):
        super(TestNewProjectContractHandler, self).create_fixtures()

        self.wf_pattern_contents = self._get_dict_contents(
            'wf_pattern_ProjectContract_registration')
        self._create_workflow_pattern(
            db_models, WFP_UUID1, **self.wf_pattern_contents)

        self.template_contents = self._get_dict_contents(
            'template_contents_ProjectContract_registration', '20160627')
        self._create_ticket_template(
            db_models, TT_UUID1, WFP_UUID1, **self.template_contents)

    def _make_accepted_before(self):
        """Testing of the new application"""
        # Create a request data.
        req = _create_request_headers()
        req.body = _create_request_body(self, TICKET_DETAIL)

        _set_stubs(self, 'tickets_create')
        Stubs.utils_stubout(self, 'get_user_list')
        Stubs.utils_stubout(self, 'get_project_list')
        Stubs.utils_stubout(self, 'get_email_address')
        Stubs.utils_stubout(self, 'get_email_addresses_from_role')
        call_info = Stubs.mail_stubout(self, 'sendmail')

        # Send request.
        res = req.get_response(self.api)

        # Examination of response.
        self.assertEqual(res.status_int, 200)
        ticket = jsonutils.loads(res.body)['ticket']

        to_address = call_info['to_address']

        self.assertTrue('O__DC1__ContractManager@example.com' in to_address)
        self.assertEqual(call_info['template'].SUBJECT,
                         mail_project_contract_accept.SUBJECT)

        return ticket

    def _update_to_accepted(self, ticket_id):
        """Test to be approved to 'accepted'"""
        # Create a request data.
        path = '/tickets/%s' % ticket_id
        req = unit_test_utils.get_fake_request(method='PUT', path=path)
        additional_data = {'message': 'xxxxx\nxxxxx\nxxxxx'}
        req.body = _create_request_data(self, ticket_id, req,
                                        'accepted before', 'accepted',
                                        additional_data)

        _set_stubs(self, 'tickets_update')
        Stubs.utils_stubout(self, 'get_user_list')
        Stubs.utils_stubout(self, 'get_project_list')

        # Send request.
        res = req.get_response(self.api)

        # Examination of response.
        self.assertEqual(res.status_int, 200)

    def _update_to_working(self, ticket_id):
        """Test to be approved to 'working'"""
        # Create a request data.
        path = '/tickets/%s' % ticket_id
        req = unit_test_utils.get_fake_request(method='PUT', path=path)
        additional_data = {'message': 'xxxxx\nxxxxx\nxxxxx'}
        req.body = _create_request_data(self, ticket_id, req, 'accepted',
                                        'working', additional_data)

        _set_stubs(self, 'tickets_update')
        Stubs.utils_stubout(self, 'get_user_list')
        Stubs.utils_stubout(self, 'get_project_list')

        # Send request.
        res = req.get_response(self.api)

        # Examination of response.
        self.assertEqual(res.status_int, 200)

    def _update_to_done(self, ticket_id):
        """Test to be approved to 'done'"""
        # Create a request data.
        path = '/tickets/%s' % ticket_id
        req = unit_test_utils.get_fake_request(method='PUT', path=path)
        additional_data = DONE_ADDITIONAL_DATA
        req.body = _create_request_data(self, ticket_id, req, 'working',
                                        'done', additional_data)

        _set_stubs(self, 'tickets_update')
        Stubs.utils_stubout(self, 'get_user')
        Stubs.utils_stubout(self, 'get_project')

        # Send request.
        res = req.get_response(self.api)

        # Examination of response.
        self.assertEqual(res.status_int, 200)

    def test_accepted_before_to_done(self):
        """Test from a new application (accepted before)
        until done.
        """
        ticket = self._make_accepted_before()
        ticket_id = ticket['id']

        self._update_to_accepted(ticket_id)
        self._update_to_working(ticket_id)
        self._update_to_done(ticket_id)

    def test_error_raise_not_found_by_get_email_addresses_from_role(self):
        """Test of not found"""
        self._tickets_create_error(
            'error_get_email_addresses_from_role_raise_exception',
            ERROR_MESSAGE['RAISE_NOT_FOUND_GET_EMAIL_ADDRESS_FROM_ROLE'] %
            EXCEPTION_MESSAGE)

    def test_error_raise_not_found_by_none_email_address(self):
        """Test of not found"""
        self._tickets_create_error(
            'error_get_not_found_email_addresses_from_role',
            ERROR_MESSAGE['RAISE_NOT_FOUND_NONE_EMAIL_ADDRESS'])

    def test_error_raise_not_found_by_get_user_list(self):
        """Test of not found"""
        self._tickets_create_error(
            'error_get_user_list_raise_exception',
            ERROR_MESSAGE['RAISE_NOT_FOUND_GET_USER_LIST'] % EXCEPTION_MESSAGE)

    def test_error_raise_conflict_by_get_user_list(self):
        """Test of conflict"""
        self._tickets_create_error(
            'error_get_conflict_user_list',
            ERROR_MESSAGE['RAISE_CONFLICT_GET_USER_LIST'] % INPUT_DATA)

    def test_error_raise_not_found_by_get_project_list(self):
        """Test of not found"""
        self._tickets_create_error(
            'error_get_project_list_raise_exception',
            ERROR_MESSAGE['RAISE_NOT_FOUND_GET_PROJECT_LIST'] %
            EXCEPTION_MESSAGE)

    def test_error_raise_conflict_by_get_project_list(self):
        """Test of conflict"""
        self._tickets_create_error(
            'error_get_conflict_project_list',
            ERROR_MESSAGE['RAISE_CONFLICT_GET_PROJECT_LIST'] % INPUT_DATA)

    def test_error_raise_not_found_by_get_user(self):
        """Test of not found"""
        self._tickets_update_to_done_error(
            'error_get_not_found_user', 'get_project',
            ERROR_MESSAGE['RAISE_NOT_FOUND_GET_USER'] % EXCEPTION_MESSAGE)

    def test_error_raise_invalid_by_get_user(self):
        """Test of invalid"""
        self._tickets_update_to_done_error(
            'error_get_invalid_user', 'get_project',
            ERROR_MESSAGE['RAISE_INVALID_GET_USER'] % UUID_INPUT_DATA)

    def test_error_raise_not_found_by_get_project(self):
        """Test of not found"""
        self._tickets_update_to_done_error(
            'get_user', 'error_get_project_raise_exception',
            ERROR_MESSAGE['RAISE_NOT_FOUND_GET_PROJECT'] % EXCEPTION_MESSAGE)

    def test_error_raise_invalid_by_get_project(self):
        """Test of invalid"""
        self._tickets_update_to_done_error(
            'get_user', 'error_get_invalid_project',
            ERROR_MESSAGE['RAISE_INVALID_GET_PROJECT'] % UUID_INPUT_DATA)

    def test_error_raise_not_found_by_create_contract(self):
        """Test of not found"""
        self._tickets_update_to_done_error(
            'get_user', 'get_project',
            ERROR_MESSAGE['RAISE_NOT_FOUND_CREATE_CONTRACT'] %
            EXCEPTION_MESSAGE, True)

    def _tickets_update_to_done_error(
            self, fake_user_stub_name, fake_project_stub_name, error_message,
            raise_flag=False):
        """Test to be approved error to 'done'"""
        ticket = self._make_accepted_before()
        ticket_id = ticket['id']

        self._update_to_accepted(ticket_id)
        self._update_to_working(ticket_id)

        # Create a request data.
        path = '/tickets/%s' % ticket_id
        req = unit_test_utils.get_fake_request(method='PUT', path=path)
        additional_data = DONE_ADDITIONAL_DATA
        req.body = _create_request_data(self, ticket_id, req, 'working',
                                        'done', additional_data)

        _set_stubs(self, 'tickets_update')
        Stubs.utils_stubout(self, fake_user_stub_name)
        Stubs.utils_stubout(self, fake_project_stub_name)
        if raise_flag:
            Stubs.contract_utils_stubout(
                self, 'error_create_contract_raise_exception')
        try:
            # Send request.
            req.get_response(self.api)
        except Exception as e:
            # Examination of response.
            self.assertEqual(e.args[0], error_message)

    def _tickets_create_error(self, fake_stub_name, error_message):
        # Create a request data.
        req = _create_request_headers()
        req.body = _create_request_body(self, TICKET_DETAIL)

        _set_stubs(self, 'tickets_create')
        Stubs.utils_stubout(self, 'get_user_list')
        Stubs.utils_stubout(self, 'get_project_list')
        Stubs.utils_stubout(self, fake_stub_name)

        try:
            # Send request.
            req.get_response(self.api)
        except Exception as e:
            # Examination of response.
            self.assertEqual(e.args[0], error_message)


class TestCancelProjectContractHandler(base.BrokerTestBase):
    """Do a test of 'Cancel Project Contract'"""

    def setUp(self):
        """Establish a clean test environment."""
        super(TestCancelProjectContractHandler, self).setUp()

        _set_config(self)

    def create_fixtures(self):
        super(TestCancelProjectContractHandler, self).create_fixtures()

        self.wf_pattern_contents = self._get_dict_contents(
            'wf_pattern_ProjectContract_cancellation')
        self._create_workflow_pattern(
            db_models, WFP_UUID1, **self.wf_pattern_contents)

        self.template_contents = self._get_dict_contents(
            'template_contents_ProjectContract_cancellation', '20160627')
        self._create_ticket_template(
            db_models, TT_UUID1, WFP_UUID1, **self.template_contents)

        # make old contract
        self.template_contents_old = self._get_dict_contents(
            'template_contents_ProjectContract_registration',
            '20160627')
        self._create_ticket_template(db_models, TT_UUID2, WFP_UUID2,
                                     **self.template_contents_old)
        ticket = db_models.Ticket(id=T_UUID1)
        ticket.ticket_template_id = TT_UUID2
        ticket.ticket_type = 'ticket_type'
        ticket.tenant_id = UUID_INPUT_DATA
        ticket.save()

        workflow = db_models.Workflow(id=W_UUID1)
        workflow.ticket_id = T_UUID1
        workflow.status_code = 'done'
        workflow.status = 1
        workflow.additional_data = self.serializer.to_json(
            {'project_id': INPUT_DATA})
        workflow.save()

        contract = db_models.Contract(contract_id=UUID_INPUT_DATA)
        contract.application_id = ticket.id
        expansion_text = {
            'contract_info': {
                'ticket_detail': {
                    'project_id': UUID_INPUT_DATA,
                    'user_id': UUID_INPUT_DATA,
                    'join_date': '2016-06-27T00:00:00.000000',
                    'message': 'xxxxx\nxxxxx\nxxxxx'
                }
            }
        }
        contract.expansion_text = self.serializer.to_json(expansion_text)
        contract.lifetime_start = LIFETIME_START
        contract.lifetime_end = LIFETIME_END_NOT_CANCEL
        contract.save()

    def _make_pre_approval(self):
        """Testing of the new application"""
        # Create a request data.
        req = _create_request_headers()
        req.body = _create_request_body(self, CANCEL_TICKET_DETAIL)

        _set_stubs(self, 'tickets_create')
        Stubs.utils_stubout(self, 'get_child_project_list')

        # Send request.
        res = req.get_response(self.api)

        # Examination of response.
        self.assertEqual(res.status_int, 200)
        ticket = jsonutils.loads(res.body)['ticket']

        return ticket

    def _update_to_final_approval(self, ticket_id):
        """Test to be approved to 'final approval'"""
        # Create a request data.
        path = '/tickets/%s' % ticket_id
        req = unit_test_utils.get_fake_request(method='PUT', path=path)
        additional_data = copy.deepcopy(FINAL_APPROVAL_ADDITIONAL_DATA)
        req.body = _create_request_data(self, ticket_id, req, 'pre-approval',
                                        'final approval', additional_data)

        _set_stubs(self, 'tickets_update')
        Stubs.utils_stubout(self, 'get_child_project_list')
        Stubs.utils_stubout(self, 'get_email_address')
        call_info = Stubs.mail_stubout(self, 'sendmail')

        # Send request
        res = req.get_response(self.api)

        # Examination of response
        self.assertEqual(res.status_int, 200)
        self.assertEqual(call_info['template'].SUBJECT,
                         mail_cancel_project_contract_final_approval.SUBJECT)
        contract = db_api.contract_get(self.context, UUID_INPUT_DATA)
        self.assertNotEqual(contract['lifetime_end'], LIFETIME_END_NOT_CANCEL)

    def test_pre_approval_to_final_approval(self):
        """Test from a new application (pre-approval)
        until final approval.
        """
        ticket = self._make_pre_approval()
        ticket_id = ticket['id']

        self._update_to_final_approval(ticket_id)

    def test_error_raise_not_found_by_get_child_project_list(self):
        """Test of not found"""
        self._tickets_update_error(
            'PUT', 'error_get_child_project_list_raise_exception',
            ERROR_MESSAGE['RAISE_NOT_FOUND_GET_CHILD_PROJECT_LIST'] %
            EXCEPTION_MESSAGE)

    def test_error_raise_conflict_by_get_child_project_list(self):
        """Test of conflict"""
        self._tickets_update_error(
            'PUT', 'error_get_conflict_child_project_list',
            ERROR_MESSAGE['RAISE_CONFLICT_GET_CHILD_PROJECT_LIST'])

    def test_error_raise_not_found_by_get_workflow_list(self):
        """Test of not found"""
        self._tickets_update_error(
            'PUT', 'error_get_not_found_contract',
            ERROR_MESSAGE['RAISE_NOT_FOUND_GET_WORKFLOW_LIST'], False)

    def test_error_raise_conflict_by_contract_get(self):
        """Test of conflict"""
        self._tickets_update_error(
            'PUT', 'error_get_conflict_contract',
            ERROR_MESSAGE['RAISE_CONFLICT_GET_CONTRACT'], False)

    def test_error_raise_not_found_by_contract_get(self):
        """Test of not found"""
        self._tickets_update_error(
            'PUT', 'error_get_contract_raise_exception',
            ERROR_MESSAGE['RAISE_NOT_FOUND_GET_CONTRACT'] %
            EXCEPTION_MESSAGE, False)

    def test_error_raise_not_found_by_contract_update(self):
        """Test of not found"""
        self._tickets_update_error(
            'PUT', 'error_update_contract_raise_exception',
            ERROR_MESSAGE['RAISE_NOT_FOUND_UPDATE_CONTRACT'] %
            EXCEPTION_MESSAGE, False)

    def _tickets_update_error(
            self, method, fake_stub_name, error_message, utils_flag=True):
        req, req.body = self._get_make_pre_approval_request(method)

        _set_stubs(self, 'tickets_update')
        if utils_flag:
            Stubs.utils_stubout(self, fake_stub_name)
        else:
            Stubs.utils_stubout(self, 'get_child_project_list')
            Stubs.api_stubout(self, fake_stub_name)
        try:
            # Send request.
            req.get_response(self.api)
        except Exception as e:
            # Examination of response.
            self.assertEqual(e.args[0], error_message)

    def _get_make_pre_approval_request(self, method):
        ticket = self._make_pre_approval()
        ticket_id = ticket['id']

        # Create a request data.
        path = '/tickets/%s' % ticket_id
        req = unit_test_utils.get_fake_request(method=method, path=path)
        additional_data = copy.deepcopy(FINAL_APPROVAL_ADDITIONAL_DATA)
        return req, _create_request_data(self, ticket_id, req, 'pre-approval',
                                         'final approval', additional_data)


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


def _create_request_headers():
    path = '/tickets'
    req = unit_test_utils.get_fake_request(method='POST', path=path)
    headers = {'x-auth-token': 'user:tenant:admin',
               'x-user-name': 'user-name',
               'x-tenant-name': 'tenant-name'}
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
    headers = {'x-auth-token': 'admin:admin:O__DC1__ContractManager,admin',
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


def _set_stubs(self, action_name):
    # Set stubs.
    # "stub_fake_call" is a stub in order to omit the queue transmission.
    # When you use the "call_info",
    # you can confirm the call arguments of stub.
    self.stubs.UnsetAll()
    stubs.stub_fake_cast(self, action_name)
