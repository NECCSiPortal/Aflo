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

import json
import time

from tempest.lib import exceptions

from tempest.api.aflo import base
from tempest.api.aflo import test_ticket
from tempest.api.aflo import test_tickettemplate
from tempest.api.aflo import test_workflowpattern

_RETRY_COUNT = 10

VERSION = '20160627'

TICKET_DETAIL_FLAT_RATE = {
    'vcpu': 1,
    'ram': 4,
    'volume_storage': 5,
    'message': 'xxxxx\nxxxxx\nxxxxx'
}
TICKET_DETAIL = {
    'message': 'xxxxx\nxxxxx\nxxxxx'
}


class TicketAdminTest(base.BaseV1AfloAdminTest):
    """AFLO Test Class by admin"""

    @classmethod
    def resource_setup(cls):
        """Setup Resources"""
        super(TicketAdminTest, cls).resource_setup()

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

    def _update_ticket(self, ticket_id, next_status):
        # Update ticket data.
        req, body = self.aflo_client.get_ticket(ticket_id)
        workflows = body['workflow']

        last = filter(lambda row:
                      row['status'] == 1,
                      workflows)[0]
        next = filter(lambda row:
                      row['status_code'] == next_status,
                      workflows)[0]

        field = {
            'last_workflow_id': last['id'],
            'next_workflow_id': next['id'],
            'last_status_code': last['status_code'],
            'next_status_code': next['status_code'],
            'additional_data': json.dumps({'message': 'xxxxx\nxxxxx\nxxxxx'})
        }
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

    def _create_contract(
            self, ticket_template_id, ticket_detail, ticket_ids, contract_ids):
        registration_ticket_id = self._create_registration_ticket(
            ticket_template_id, ticket_detail)
        ticket_ids.append(registration_ticket_id)

        self._update_ticket(registration_ticket_id, 'final approval')

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
        contract_ids.append(contract_id)

    def test_handler(self):
        """Tests from the change of contract"""
        # Get catalog info ids.
        goods_ids, catalog_ids, contents_ids, catalog_scope_ids, price_ids = \
            test_tickettemplate.get_contract_info_ids(self)

        # Create data.
        workflow_pattern_ids = []
        ticket_template_ids = []
        ticket_ids = []
        contract_ids = []

        # Flat-rate ticket template.
        workflow_pattern_id = test_workflowpattern.create_workflow_pattern(
            self, ["workflow_pattern_contents_monthly.json"])
        workflow_pattern_ids.append(workflow_pattern_id)

        flat_rate_cancellation_template_id = \
            test_tickettemplate.create_ticket_template(
                self, ['ticket_template_contents_monthly_cancelling'],
                VERSION, catalog_ids)
        ticket_template_ids.append(flat_rate_cancellation_template_id)
        flat_rate_registration_template_id = \
            test_tickettemplate.create_ticket_template(
                self, ['ticket_template_contents_monthly_registration'],
                VERSION, catalog_ids,
                flat_rate_cancellation_template_id[0])
        ticket_template_ids.append(flat_rate_registration_template_id)

        # Pay-for-use ticket template.
        workflow_pattern_id = test_workflowpattern.create_workflow_pattern(
            self, ["workflow_pattern_contents_pay_for_use_contract.json"])
        workflow_pattern_ids.append(workflow_pattern_id)

        pay_for_use_cancellation_template_id = \
            test_tickettemplate.create_ticket_template(
                self, ['ticket_template_contents_cancellation_pay_for_use'],
                VERSION, catalog_ids)
        ticket_template_ids.append(pay_for_use_cancellation_template_id)
        pay_for_use_registration_template_id = \
            test_tickettemplate.create_ticket_template(
                self, ['ticket_template_contents_registration_pay_for_use'],
                VERSION, catalog_ids,
                pay_for_use_cancellation_template_id[0])
        ticket_template_ids.append(pay_for_use_registration_template_id)

        # Change to flat-rate ticket template.
        workflow_pattern_id = test_workflowpattern.create_workflow_pattern(
            self, ["workflow_pattern_contents_change_contract.json"])
        workflow_pattern_ids.append(workflow_pattern_id)

        flat_rate_change_template_id = \
            test_tickettemplate.create_ticket_template(
                self, ['ticket_template_contents_change_contract_flat_rate'],
                VERSION, catalog_ids,
                flat_rate_cancellation_template_id[0])
        ticket_template_ids.append(flat_rate_change_template_id)

        # Change to pay-for-use ticket template.
        pay_for_use_change_template_id = \
            test_tickettemplate.create_ticket_template(
                self, ['ticket_template_contents_change_contract_pay_for_use'],
                VERSION, catalog_ids,
                pay_for_use_cancellation_template_id[0])
        ticket_template_ids.append(pay_for_use_change_template_id)

        try:
            # Pay-for-use contract does not exist.
            self._create_registration_ticket(
                flat_rate_change_template_id[0], TICKET_DETAIL_FLAT_RATE)
        except exceptions.ServerFault:
            pass
        try:
            # Flat-rate contract does not exist.
            self._create_registration_ticket(
                pay_for_use_change_template_id[0], TICKET_DETAIL)
        except exceptions.ServerFault:
            pass

        # Create pay-for-use contract.
        self._create_contract(
            pay_for_use_registration_template_id[0], TICKET_DETAIL,
            ticket_ids, contract_ids)

        # Create change to flat-rate contract.
        self._create_contract(
            flat_rate_change_template_id[0], TICKET_DETAIL_FLAT_RATE,
            ticket_ids, contract_ids)
        try:
            # Could not accept the request, it is under contract.
            self._create_contract(
                flat_rate_change_template_id[0], TICKET_DETAIL_FLAT_RATE,
                ticket_ids, contract_ids)
        except exceptions.ServerFault:
            pass

        # Create change to pay-for-use contract.
        self._create_contract(
            pay_for_use_change_template_id[0], TICKET_DETAIL,
            ticket_ids, contract_ids)
        try:
            # Could not accept the request, it is under contract.
            self._create_contract(
                pay_for_use_change_template_id[0], TICKET_DETAIL,
                ticket_ids, contract_ids)
        except exceptions.ServerFault:
            pass

        # Delete data.
        for ticket_id in ticket_ids:
            test_ticket.delete_ticket(self, ticket_id)
        for ticket_template_id in ticket_template_ids:
            test_tickettemplate.delete_ticket_template(
                self, ticket_template_id)
        for workflow_pattern_id in workflow_pattern_ids:
            test_workflowpattern.delete_workflow_pattern(
                self, workflow_pattern_id)
        for contract_id in contract_ids:
            self.aflo_client.delete_contract(contract_id)

        test_tickettemplate.delete_contract_info_data(
            self, None, goods_ids, catalog_ids, contents_ids,
            catalog_scope_ids, price_ids)
