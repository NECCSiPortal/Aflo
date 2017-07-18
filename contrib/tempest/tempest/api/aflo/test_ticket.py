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

import json
import testtools  # noqa
import time
import uuid

from tempest.api.aflo import base
from tempest import config_aflo as config  # noqa
from tempest.lib import exceptions

from tempest.api.aflo import test_tickettemplate
from tempest.api.aflo import test_workflowpattern

CONF = config.CONF

_RETRY_COUNT = 20


class TicketAdminTest(base.BaseV1AfloAdminTest):
    """AFLO Test Class by admin."""

    @classmethod
    def resource_setup(cls):
        """Setup Resources."""
        super(TicketAdminTest, cls).resource_setup()

    def test_ticket(self):
        """Test 'Data Between Created to Deleted'"""
        # Create data.
        workflow_pattern_id = \
            test_workflowpattern.create_workflow_pattern(
                self,
                ["workflow_pattern_contents_009.json"])
        ticket_template_id = \
            test_tickettemplate.create_ticket_template(
                self,
                ["ticket_template_contents_009"], '20160627')

        # Test ticket operations.
        ticket_id = self._create_ticket(ticket_template_id[0])
        self._list_ticket(ticket_id)
        self._update_ticket(ticket_id)
        delete_ticket(self, ticket_id)

        # Delete data.
        test_tickettemplate.delete_ticket_template(
            self, ticket_template_id)
        test_workflowpattern.delete_workflow_pattern(
            self, workflow_pattern_id)

    def test_create_validation_error(self):
        """Test of "Data Create".
        Test of input check error.
        """
        # Create data.
        workflow_pattern_id = \
            test_workflowpattern.create_workflow_pattern(
                self,
                ["workflow_pattern_contents_004.json"])
        ticket_template_id = \
            test_tickettemplate.create_ticket_template(
                self,
                ["ticket_template_contents_004"], '20160627')

        # Test ticket operations.
        ticket_detail = {'key': 'json'}
        field = {'ticket_template_id': ticket_template_id[0],
                 'status_code': 'applied',
                 'ticket_detail': json.dumps(ticket_detail)}
        self.assertRaises(exceptions.BadRequest,
                          self.aflo_client.create_ticket,
                          field)

        # Delete data.
        test_tickettemplate.delete_ticket_template(
            self, ticket_template_id)
        test_workflowpattern.delete_workflow_pattern(
            self, workflow_pattern_id)

    def test_create_broker_error(self):
        """Test of "Data Create".
        Test of broker error.
        """
        # Create data.
        workflow_pattern_id = \
            test_workflowpattern.create_workflow_pattern(
                self,
                ["workflow_pattern_contents_005.json"])
        ticket_template_id = \
            test_tickettemplate.create_ticket_template(
                self,
                ["ticket_template_contents_005"], '20160627')

        # Test ticket operations.
        ticket_detail = {'key': 'json'}
        field = {'ticket_template_id': ticket_template_id[0],
                 'status_code': 'applied',
                 'ticket_detail': json.dumps(ticket_detail)}
        req, body = self.aflo_client.create_ticket(field)
        ticket = body['ticket']

        # Check Updated status
        for c in range(0, _RETRY_COUNT):
            try:
                req, body = self.aflo_client.get_ticket(ticket['id'])
            except Exception:
                if c < _RETRY_COUNT - 1:
                    time.sleep(10)
                else:
                    raise exceptions.TimeoutException(str(body))
                continue

        workflow = body['workflow']
        now_status = filter(lambda row:
                            row["status_code"] == 'error',
                            workflow)
        self.assertNotEmpty(now_status)

        delete_ticket(self, ticket['id'])

        # Delete data.
        test_tickettemplate.delete_ticket_template(
            self, ticket_template_id)
        test_workflowpattern.delete_workflow_pattern(
            self, workflow_pattern_id)

    def test_create_ticket_irregular_no_workflow_role(self):
        """Test of "Data Create".
        Test the operation of the workflow role without.
        """
        # Create data.
        workflow_pattern_id = \
            test_workflowpattern.create_workflow_pattern(
                self,
                ["workflow_pattern_contents_003.json"])
        ticket_template_id = \
            test_tickettemplate.create_ticket_template(
                self,
                ["ticket_template_contents_003"], '20160627')

        # Test ticket operations.
        field = {'ticket_template_id': ticket_template_id[0],
                 'status_code': 'applied',
                 'ticket_detail': '{"num": "0"}'}
        self.assertRaises(exceptions.Forbidden,
                          self.aflo_client.create_ticket,
                          field)

        # Delete data.
        test_tickettemplate.delete_ticket_template(
            self, ticket_template_id)
        test_workflowpattern.delete_workflow_pattern(
            self, workflow_pattern_id)

    def _create_ticket(self, ticket_template_id):
        """Create a ticket data.
        :param ticket_template_id: A ticket template id.
        """
        ticket_detail = {'num': '0'}
        field = {'ticket_template_id': ticket_template_id,
                 'status_code': 'applied',
                 'ticket_detail': json.dumps(ticket_detail)}

        req, body = self.aflo_client.create_ticket(field)
        ticket = body['ticket']

        self.assertTrue(ticket['id'] is not None)
        self.assertEqual(ticket['ticket_template_id'],
                         ticket_template_id)

        return ticket['id']

    def _list_ticket(self, ticket_id):
        """List ticket data."""
        for c in range(0, _RETRY_COUNT):
            req, body = self.aflo_client.list_ticket()

            # DB Entry is asynchronous process.
            # Wait for a seconds.
            if self._get_count(body, [ticket_id]) < 1:
                if c < _RETRY_COUNT - 1:
                    time.sleep(10)
                else:
                    raise exceptions.TimeoutException(str(body))
            else:
                break

        self._list_ticket_ticket_type_filter(ticket_id)
        self._list_ticket_irregular_ticket_type_filter(ticket_id)

        self._list_ticket_template_contents_filter(ticket_id)
        self._list_ticket_irregular_template_contents_filter(ticket_id)

    def _list_ticket_ticket_type_filter(self, ticket_id):
        """Test 'List Search'
        Test of if you filtering ticket type.
        """
        params = ['ticket_type=New+Contract',
                  'ticket_type=New+Contract,request']

        for url_param in params:
            req, body = self.aflo_client.list_ticket(url_param)

            self.assertEqual(self._get_count(body, [ticket_id]),
                             1)

    def _list_ticket_multi_ticket_type_filter(self,
                                              ticket_id):
        """Test 'List Search'
        Test of if you filtering multi ticket type.
        """
        url_params = \
            'ticket_type=New+Contract&ticket_type=New+Contract,request'

        req, body = self.aflo_client.list_ticket(url_params)

        self.assertEqual(self._get_count(body, [ticket_id]),
                         1)

    def _list_ticket_irregular_ticket_type_filter(self,
                                                  ticket_id):
        """Test 'List Search'
        Test of if you filtering not exists value of
        ticket type.
        """
        req, body = self.aflo_client.list_ticket('ticket_type=aaaaa')

        self.assertEqual(self._get_count(body, [ticket_id]),
                         0)

    def _list_ticket_template_contents_filter(self,
                                              ticket_id):
        """Test 'List Search'
        Test of if you filtering ticket template contents.
        """
        params = ['ticket_template_name=' +
                  "flat-rate-1(ja)%20*root:three",
                  'application_kinds_name=application_kinds_2(ja)']

        for url_param in params:
            req, body = self.aflo_client.list_ticket(url_param)

        self.assertEqual(self._get_count(body, [ticket_id]),
                         1)

    def _list_ticket_irregular_template_contents_filter(self,
                                                        ticket_id):
        """Test 'List Search'
        Test of if you filtering not exists value of
        ticket template contents.
        """
        params = ['ticket_template_name=aaaaa',
                  'application_kinds_name=aaaaa']

        for url_param in params:
            req, body = self.aflo_client.list_ticket(url_param)

        self.assertEqual(self._get_count(body, [ticket_id]),
                         0)

    def _get_count(self, body, ids):
        count = 0
        for id in ids:
            for row in body:
                if id == row['id']:
                    count = count + 1
        return count

    def _update_ticket(self, ticket_id):
        """Update ticket data.
        :param ticket_id: ticket id.
        """
        # Get records for update.
        req, body = self.aflo_client.get_ticket(ticket_id)
        workflows = body['workflow']

        last = filter(lambda row:
                      row["status"] == 1,
                      workflows)[0]
        next = filter(lambda row:
                      row["status_code"] == "withdrew",
                      workflows)[0]

        # Update data
        field = {'last_workflow_id': last["id"],
                 'next_workflow_id': next["id"],
                 'last_status_code': 'applied',
                 'next_status_code': 'withdrew'}
        self.aflo_client.update_ticket(ticket_id, field)

        # Check Updated status
        for c in range(0, _RETRY_COUNT):
            req, body = self.aflo_client.get_ticket(ticket_id)
            workflow = body['workflow']
            now_status = filter(lambda row:
                                row["status_code"] == 'withdrew',
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

    def test_update_validation_error(self):
        """Test of "Data Update".
        Test of input check error.
        """
        # Create data.
        workflow_pattern_id = \
            test_workflowpattern.create_workflow_pattern(
                self,
                ["workflow_pattern_contents_006.json"])
        ticket_template_id = \
            test_tickettemplate.create_ticket_template(
                self,
                ["ticket_template_contents_006"], '20160627')

        # Test ticket operations.
        ticket_detail = {'key': 'json'}
        field = {'ticket_template_id': ticket_template_id[0],
                 'status_code': 'applied',
                 'ticket_detail': json.dumps(ticket_detail)}
        req, body = self.aflo_client.create_ticket(field)
        ticket = body['ticket']
        ticket_id = ticket['id']

        for c in range(0, _RETRY_COUNT):
            try:
                req, body = self.aflo_client.get_ticket(ticket_id)
            except Exception:
                if c < _RETRY_COUNT - 1:
                    time.sleep(10)
                else:
                    raise exceptions.TimeoutException(str(body))
                continue
        workflows = body['workflow']
        last = filter(lambda row:
                      row["status"] == 1,
                      workflows)[0]
        next = filter(lambda row:
                      row["status_code"] == "inspectioned",
                      workflows)[0]

        field = {'last_workflow_id': last["id"],
                 'next_workflow_id': next["id"],
                 'last_status_code': 'applied',
                 'next_status_code': 'inspectioned'}
        self.assertRaises(exceptions.BadRequest,
                          self.aflo_client.update_ticket,
                          ticket_id,
                          field)

        delete_ticket(self, ticket_id)

        # Delete data.
        test_tickettemplate.delete_ticket_template(
            self, ticket_template_id)
        test_workflowpattern.delete_workflow_pattern(
            self, workflow_pattern_id)

    def test_update_broker_error(self):
        """Test of "Data Update".
        Test of broker error.
        """
        # Create data.
        workflow_pattern_id = \
            test_workflowpattern.create_workflow_pattern(
                self,
                ["workflow_pattern_contents_007.json"])
        ticket_template_id = \
            test_tickettemplate.create_ticket_template(
                self,
                ["ticket_template_contents_007"], '20160627')

        # Test ticket operations.
        ticket_detail = {'num': '0'}
        field = {'ticket_template_id': ticket_template_id[0],
                 'status_code': 'applied',
                 'ticket_detail': json.dumps(ticket_detail)}
        req, body = self.aflo_client.create_ticket(field)
        ticket = body['ticket']
        ticket_id = ticket['id']

        for c in range(0, _RETRY_COUNT):
            try:
                req, body = self.aflo_client.get_ticket(ticket_id)
            except Exception:
                if c < _RETRY_COUNT - 1:
                    time.sleep(10)
                    continue
                else:
                    raise exceptions.TimeoutException(str(body))
            break

        workflows = body['workflow']
        last = filter(lambda row:
                      row["status"] == 1,
                      workflows)[0]
        next = filter(lambda row:
                      row["status_code"] == "inspectioned",
                      workflows)[0]

        field = {'last_workflow_id': last["id"],
                 'next_workflow_id': next["id"],
                 'last_status_code': 'applied',
                 'next_status_code': 'inspectioned'}
        req, body = self.aflo_client.update_ticket(ticket_id, field)

        # Check Updated status
        for c in range(0, _RETRY_COUNT):
            req, body = self.aflo_client.get_ticket(ticket_id)
            workflow = body['workflow']
            now_status = filter(lambda row:
                                row["status_code"] == 'error',
                                workflow)
            # DB Entry is asynchronous process.
            # Wait for a seconds.
            if 0 == len(now_status):
                if c < _RETRY_COUNT - 1:
                    time.sleep(10)
                else:
                    raise exceptions.TimeoutException(str(body))
            else:
                break

        delete_ticket(self, ticket_id)

        # Delete data.
        test_tickettemplate.delete_ticket_template(
            self, ticket_template_id)
        test_workflowpattern.delete_workflow_pattern(
            self, workflow_pattern_id)

    def test_update_integrity_error(self):
        """Test of "Data Update".
        Update of the updated status.
        """
        # Create data.
        workflow_pattern_id = \
            test_workflowpattern.create_workflow_pattern(
                self,
                ["workflow_pattern_contents_008.json"])
        ticket_template_id = \
            test_tickettemplate.create_ticket_template(
                self,
                ["ticket_template_contents_008"], '20160627')

        # Test ticket operations.
        ticket_detail = {'num': '0'}
        field = {'ticket_template_id': ticket_template_id[0],
                 'status_code': 'applied',
                 'ticket_detail': json.dumps(ticket_detail)}
        req, body = self.aflo_client.create_ticket(field)
        ticket = body['ticket']
        ticket_id = ticket['id']

        for c in range(0, _RETRY_COUNT):
            try:
                req, body = self.aflo_client.get_ticket(ticket_id)
            except Exception:
                if c < _RETRY_COUNT - 1:
                    time.sleep(10)
                    continue
                else:
                    raise exceptions.TimeoutException(str(body))
            break

        workflows = body['workflow']
        last = filter(lambda row:
                      row["status"] == 1,
                      workflows)[0]
        next = filter(lambda row:
                      row["status_code"] == "withdrew",
                      workflows)[0]

        field = {'last_workflow_id': last["id"],
                 'next_workflow_id': next["id"],
                 'last_status_code': 'applied',
                 'next_status_code': 'withdrew'}
        req, body = self.aflo_client.update_ticket(ticket_id, field)

        # Check Updated status
        for c in range(0, _RETRY_COUNT):
            req, body = self.aflo_client.get_ticket(ticket_id)
            workflow = body['workflow']
            now_status = filter(lambda row:
                                row["status_code"] == 'withdrew',
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

        self.assertRaises(exceptions.Conflict,
                          self.aflo_client.update_ticket,
                          ticket_id,
                          field)

        delete_ticket(self, ticket_id)

        # Delete data.
        test_tickettemplate.delete_ticket_template(
            self, ticket_template_id)
        test_workflowpattern.delete_workflow_pattern(
            self, workflow_pattern_id)

    def test_ticket_invalid_delete_irregular_no_data(self):
        """Do a test of 'Ticket commands'
        Test the operation of the Delete command(Not exist ticket id).
        """
        id = str(uuid.uuid4())

        # This test case is not raise exception,
        # delete method is async.
        self.aflo_client.delete_ticket(id)


class TicketTest(base.BaseV1AfloTest):
    """AFLO Test Class."""

    @classmethod
    def resource_setup(cls):
        """Setup Resources."""
        super(TicketTest, cls).resource_setup()

    def test_ticket_invalid_get_irregular_no_data(self):
        """Do a test of 'Ticket Get'
        Test the operation of the Get API(Not exist ticket id).
        """
        id = str(uuid.uuid4())

        self.assertRaises(exceptions.NotFound,
                          self.aflo_client.get_ticket,
                          id)

    def test_ticket_list_irregular_params(self):
        """Do a test of 'Ticket List'
        Test the operation of the List API(Ignore parameters).
        """
        params = ['sort_key=a',
                  'sort_dir=a',
                  'limit=a',
                  'force_show_deleted=a']

        for url_param in params:
            # List data.
            self.assertRaises(exceptions.BadRequest,
                              self.aflo_client.list_ticket,
                              url_param)

    def test_ticket_invalid_update_irregular_workflow(self):
        """Do a test of 'Ticket Update'
        Test the operation of the Update API(Not exist ticket id).
        """
        id = str(uuid.uuid4())
        field = {'last_workflow_id': 'a',
                 'next_workflow_id': 'b',
                 'last_status_code': 'applied',
                 'next_status_code': 'withdrew'}

        self.assertRaises(exceptions.BadRequest,
                          self.aflo_client.update_ticket,
                          id,
                          field)

    def test_ticket_invalid_delete_irregular_no_authority(self):
        """Do a test of 'Ticket Delete'
        Test the operation of the Delete API(Not exist authority).
        """
        id = str(uuid.uuid4())

        self.assertRaises(exceptions.Forbidden,
                          self.aflo_client.delete_ticket,
                          id)


def delete_ticket(self, ticket_id):
    """Delete the ticket.
    :param ticket_id: Target ticket id.
    """
    self.aflo_client.delete_ticket(ticket_id)

    for c in range(0, _RETRY_COUNT):
        try:
            req, body = self.aflo_client.get_ticket(ticket_id)

            if c < _RETRY_COUNT - 1:
                time.sleep(10)
            else:
                raise exceptions.TimeoutException(str(body))

        except exceptions.NotFound:
            break
