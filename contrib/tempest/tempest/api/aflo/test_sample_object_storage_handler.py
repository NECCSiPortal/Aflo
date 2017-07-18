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

import copy
import json
import time

from tempest.api.aflo import base
from tempest.api.aflo import test_ticket
from tempest.api.aflo import test_tickettemplate
from tempest.api.aflo import test_workflowpattern
from tempest import config_aflo as config
from tempest.lib import exceptions

CONF = config.CONF

_RETRY_COUNT = 10

OST_ROLES = CONF.aflo.ost_roles
OST_ROLES_SET = set(OST_ROLES)

DEMO_USER_ID = CONF.aflo.demo_user_id

TICKET_DETAIL = {
    'message': 'xxxxx\nxxxxx\nxxxxx'
}
CANCEL_TICKET_DETAIL = {
    'contract_id': 'xxxxx',
    'message': 'xxxxx\nxxxxx\nxxxxx'
}
ADDITIONAL_DATA = {
    'message': 'xxxxx\nxxxxx\nxxxxx'
}


class TicketAdminTest(base.BaseV1AfloAdminTest):
    """AFLO Test Class by admin"""

    @classmethod
    def resource_setup(cls):
        """Setup Resources"""
        super(TicketAdminTest, cls).resource_setup()
        cls.user_id = cls.os.credentials.user_id
        cls.tenant_id = cls.os.credentials.tenant_id

    def _create_registration_ticket(self, ticket_template_id, ticket_detail):
        # Create ticket data.
        field = {'ticket_template_id': ticket_template_id,
                 'status_code': 'pre-approval',
                 'ticket_detail': json.dumps(ticket_detail)}

        req, body = self.aflo_client.create_ticket(field)
        ticket = body['ticket']

        self.assertTrue(ticket['id'] is not None)

        for c in range(0, _RETRY_COUNT):
            try:
                req, body = self.aflo_client.get_ticket(ticket['id'])
            except Exception:
                if c < _RETRY_COUNT - 1:
                    time.sleep(10)
                else:
                    raise exceptions.TimeoutException(str(body))
                continue

        return ticket['id']

    def _create_cancellation_ticket(
            self, contract_id, ticket_template_id, ticket_detail):
        # Create ticket data.
        ticket_detail = CANCEL_TICKET_DETAIL
        ticket_detail['contract_id'] = contract_id
        field = {'ticket_template_id': ticket_template_id,
                 'status_code': 'pre-approval',
                 'ticket_detail': json.dumps(ticket_detail)}

        req, body = self.aflo_client.create_ticket(field)
        ticket = body['ticket']

        self.assertTrue(ticket['id'] is not None)

        for c in range(0, _RETRY_COUNT):
            try:
                req, body = self.aflo_client.get_ticket(ticket['id'])
            except Exception:
                if c < _RETRY_COUNT - 1:
                    time.sleep(10)
                else:
                    raise exceptions.TimeoutException(str(body))
                continue

        return ticket['id']

    def _update_ticket(self, ticket_id, next_status, additional_data):
        # Update ticket data.
        req, body = self.aflo_client.get_ticket(ticket_id)
        workflows = body['workflow']

        last = filter(lambda row:
                      row['status'] == 1,
                      workflows)[0]
        next = filter(lambda row:
                      row['status_code'] == next_status,
                      workflows)[0]

        field = {'last_workflow_id': last['id'],
                 'next_workflow_id': next['id'],
                 'last_status_code': last['status_code'],
                 'next_status_code': next['status_code'],
                 'additional_data': json.dumps(additional_data)}
        self.aflo_client.update_ticket(ticket_id, field)

        # Check Updated status.
        for c in range(0, _RETRY_COUNT):
            req, body = self.aflo_client.get_ticket(ticket_id)
            workflow = body['workflow']
            now_status = filter(lambda row:
                                row['status_code'] == next_status,
                                workflow)
            # DB Entry is asynchronous process.
            # Wait for a seconds.
            if now_status[0]['status'] != 1:
                if c < _RETRY_COUNT - 1:
                    time.sleep(10)
                else:
                    raise exceptions.TimeoutException(str(body))
            else:
                break

    def test_handler(self):
        """Tests from the contract to cancellation"""
        # Get catalog info ids.
        goods_ids, catalog_ids, contents_ids, catalog_scope_ids, price_ids = \
            test_tickettemplate.get_contract_info_ids(self)

        # Create data.
        workflow_pattern_ids = test_workflowpattern.create_workflow_pattern(
            self, ['workflow_pattern_contents_object_storage.json'])
        cancellation_template_id = test_tickettemplate.create_ticket_template(
            self,
            ['ticket_template_contents_cancel_object_storage'], '20160627',
            catalog_ids, None)

        registration_template_id = test_tickettemplate.create_ticket_template(
            self,
            ['ticket_template_contents_registration_object_storage'],
            '20160627',
            catalog_ids, cancellation_template_id[0])

        registration_ticket_id = self._create_registration_ticket(
            registration_template_id[0], copy.deepcopy(TICKET_DETAIL))

        self._update_ticket(registration_ticket_id, 'final approval',
                            ADDITIONAL_DATA)

        # Wait for a grant roles
        for c in range(0, _RETRY_COUNT):
            try:
                req, body = self.aflo_client.list_contract(
                    'application_id=%s' % registration_ticket_id)
                contract_id = body[0]['contract_id']
            except IndexError:
                if c < _RETRY_COUNT - 1:
                    time.sleep(10)
                else:
                    raise exceptions.TimeoutException(str(body))
                continue

        # Create role to demo user
        self._create_dummy_role()

        cancellation_ticket_id = self._create_cancellation_ticket(
            contract_id, cancellation_template_id[0], CANCEL_TICKET_DETAIL)
        self._update_ticket(cancellation_ticket_id, 'final approval',
                            ADDITIONAL_DATA)

        # Wait for a rovoke roles
        for c in range(0, _RETRY_COUNT):
            body = self.os.roles_v3_client.list_user_roles_on_project(
                user_id=DEMO_USER_ID, project_id=self.tenant_id)
            role_ids = set(map(lambda role: role['name'], body['roles']))

            # DB Entry is asynchronous process.
            # Wait for a seconds.
            if len(OST_ROLES_SET & role_ids) != 0:
                if c < _RETRY_COUNT - 1:
                    time.sleep(10)
                else:
                    raise exceptions.TimeoutException(str(body))
            else:
                break

        # Delete data.
        test_ticket.delete_ticket(self, registration_ticket_id)
        test_ticket.delete_ticket(self, cancellation_ticket_id)
        test_tickettemplate.delete_ticket_template(
            self, registration_template_id)
        test_tickettemplate.delete_ticket_template(
            self, cancellation_template_id)
        test_workflowpattern.delete_workflow_pattern(
            self, workflow_pattern_ids)

        test_tickettemplate.delete_contract_info_data(
            self,
            contract_id,
            goods_ids,
            catalog_ids,
            contents_ids,
            catalog_scope_ids,
            price_ids)

    def _create_dummy_role(self):
        """When tempest run user(Admin) deleted one's role in a handler,
        a session is cut as tempest test.
        Therefore carry out a test as 'Admin' user and evade the problem
        in the thing inspecting by the 'Dummy' user.
        """
        roles_body = self.os.roles_v3_client.list_roles()
        role_id = filter(lambda role:
                         role['name'] == OST_ROLES[0],
                         roles_body['roles'])[0]['id']
        self.os.roles_v3_client.create_user_role_on_project(
            project_id=self.tenant_id,
            user_id=DEMO_USER_ID,
            role_id=role_id)
        # Check assigned role
        for c in range(0, _RETRY_COUNT):
            body = self.os.roles_v3_client.list_user_roles_on_project(
                user_id=DEMO_USER_ID, project_id=self.tenant_id)
            role_ids = set(map(lambda role: role['name'], body['roles']))

            # DB Entry is asynchronous process.
            # Wait for a seconds.
            if len(OST_ROLES_SET & role_ids) != len(OST_ROLES):
                if c < _RETRY_COUNT - 1:
                    time.sleep(10)
                else:
                    raise exceptions.TimeoutException(str(body))
            else:
                break
