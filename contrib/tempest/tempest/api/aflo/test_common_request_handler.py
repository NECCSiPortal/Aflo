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

from tempest.api.aflo import base
from tempest import config_aflo as config
from tempest.lib import exceptions

from tempest.api.aflo import test_ticket
from tempest.api.aflo import test_tickettemplate
from tempest.api.aflo import test_workflowpattern

CONF = config.CONF

_RETRY_COUNT = 10


class TicketAdminTest(base.BaseV1AfloAdminTest):
    """AFLO Test Class by admin."""

    @classmethod
    def resource_setup(cls):
        """Setup Resources."""
        super(TicketAdminTest, cls).resource_setup()

    def _create_ticket(self, ticket_template_id):
        """Create ticket data.
        :param ticket_template_id: Ticket template id.
        """
        ticket_detail = {'Message': 'mes'}
        field = {'ticket_template_id': ticket_template_id,
                 'status_code': 'inquiring',
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
        """Update ticket data.
        :param ticket_id: ticket id.
        :param next_status: next status code.
        """
        # Get records for update.
        req, body = self.aflo_client.get_ticket(ticket_id)
        workflows = body['workflow']

        last = filter(lambda row:
                      row["status"] == 1,
                      workflows)[0]
        next = filter(lambda row:
                      row["status_code"] == next_status,
                      workflows)[0]

        # Update data
        ticket_detail = {'Message': 'mes_%s' % next_status}
        field = {'last_workflow_id': last["id"],
                 'next_workflow_id': next["id"],
                 'last_status_code': last["status_code"],
                 'next_status_code': next["status_code"],
                 'additional_data': json.dumps(ticket_detail)}
        self.aflo_client.update_ticket(ticket_id, field)

        # Check Updated status
        for c in range(0, _RETRY_COUNT):
            req, body = self.aflo_client.get_ticket(ticket_id)
            workflow = body['workflow']
            now_status = filter(lambda row:
                                row["status_code"] == next_status,
                                workflow)
            # DB Entry is asynchronous process.
            # Wait for a seconds.
            if now_status[0]["status"] != 1:
                if c < _RETRY_COUNT - 1:
                    time.sleep(10)
                else:
                    raise exceptions.TimeoutException(str(body))
            else:
                break

    def test_handler(self):
        """Tests from the application to close """
        # Create data.
        workflow_pattern_id = \
            test_workflowpattern.create_workflow_pattern(
                self,
                ["workflow_pattern_contents_send_inquiry.json"])
        ticket_template_id = \
            test_tickettemplate.create_ticket_template(
                self,
                ["ticket_template_contents_send_inquiry"], '20160627')

        ticket_id = self._create_ticket(ticket_template_id[0])
        self._update_ticket(ticket_id, 'working')
        self._update_ticket(ticket_id, 'close request')
        self._update_ticket(ticket_id, 'close')
        test_ticket.delete_ticket(self, ticket_id)

        # Delete data.
        test_tickettemplate.delete_ticket_template(
            self, ticket_template_id)
        test_workflowpattern.delete_workflow_pattern(
            self, workflow_pattern_id)
