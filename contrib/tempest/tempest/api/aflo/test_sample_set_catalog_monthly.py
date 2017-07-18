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

from tempest.api.aflo.fixture import sample_set_catalog_monthly as fixture
from tempest.api.aflo import test_ticket
from tempest.api.aflo import test_tickettemplate
from tempest.api.aflo import test_workflowpattern

CONF = config.CONF

_RETRY_COUNT = 10

REGISTRATION_NUM = [1, 2, 3]


class TicketAdminTest(base.BaseV1AfloAdminTest):
    """AFLO Test Class by admin."""

    @classmethod
    def resource_setup(cls):
        """Setup Resources."""
        super(TicketAdminTest, cls).resource_setup()
        cls.tenant_id = cls.os.credentials.tenant_id

    def _create_registration_ticket(self, ticket_template_id):
        """Create ticket data."""
        ticket_detail = \
            {'vcpu': REGISTRATION_NUM[0],
             'ram': REGISTRATION_NUM[1],
             'volume_storage': REGISTRATION_NUM[2],
             'Message': 'text'}
        field = {'ticket_template_id': ticket_template_id,
                 'status_code': 'awaiting approval',
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

    def _create_cancellation_ticket(self, contract_id, ticket_template_id):
        """Create ticket data."""
        ticket_detail = {'contract_id': contract_id,
                         'vcpu': REGISTRATION_NUM[0],
                         'ram': REGISTRATION_NUM[1],
                         'volume_storage': REGISTRATION_NUM[2],
                         'Message': 'mes'}
        field = {'ticket_template_id': ticket_template_id,
                 'status_code': 'awaiting approval',
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

    def _update_cores(self, tenant_id, cores):
        self.os.quotas_client.update_quota_set(tenant_id, cores=cores)
        # Wait for a quota of update
        for c in range(0, _RETRY_COUNT):
            body = self.os.quotas_client.show_quota_set(self.tenant_id)
            new_cores = body['quota_set']['cores']

            # DB Entry is asynchronous process.
            # Wait for a seconds.
            if cores != new_cores:
                if c < _RETRY_COUNT - 1:
                    time.sleep(10)
                else:
                    raise exceptions.TimeoutException(str(body))
            else:
                break

    def _update_gigabytes(self, tenant_id, gigabytes):
        self.os.volume_quotas_client.update_quota_set(tenant_id,
                                                      gigabytes=gigabytes)
        # Wait for a quota of update
        for c in range(0, _RETRY_COUNT):
            body = self.os.volume_quotas_client.show_quota_set(self.tenant_id)
            new_gigabytes = body['quota_set']['gigabytes']

            # DB Entry is asynchronous process.
            # Wait for a seconds.
            if gigabytes != new_gigabytes:
                if c < _RETRY_COUNT - 1:
                    time.sleep(10)
                else:
                    raise exceptions.TimeoutException(str(body))
            else:
                break

    def test_handler(self):
        """Tests from the contract to cancellation """
        # Get contract info ids.
        goods_ids, catalog_ids, contents_ids, catalog_scope_ids, price_ids = \
            test_tickettemplate.get_contract_info_ids(self)

        workflow_pattern_id = \
            test_workflowpattern.create_workflow_pattern(
                self,
                ["workflow_pattern_contents_monthly.json"])
        ticket_template_id = \
            test_tickettemplate.create_ticket_template(
                self,
                ["ticket_template_contents_monthly_registration",
                 "ticket_template_contents_monthly_cancelling"],
                '20160627', catalog_ids)

        # Refrain from the value of the quota
        body = self.os.quotas_client.show_quota_set(self.tenant_id)
        old_cores = body['quota_set']['cores']
        old_ram = body['quota_set']['ram']
        body = self.os.volume_quotas_client.show_quota_set(self.tenant_id)
        old_gigabytes = body['quota_set']['gigabytes']

        # Purchase contract
        registration_ticket_id = self._create_registration_ticket(
            ticket_template_id[0])
        self._update_ticket(registration_ticket_id, 'check')
        self._update_ticket(registration_ticket_id, 'approval')

        # Wait for a quota of update
        for c in range(0, _RETRY_COUNT):
            body = self.os.quotas_client.show_quota_set(self.tenant_id)
            new_cores = body['quota_set']['cores']
            new_ram = body['quota_set']['ram']
            body = self.os.volume_quotas_client.show_quota_set(self.tenant_id)
            new_gigabytes = body['quota_set']['gigabytes']

            # DB Entry is asynchronous process.
            # Wait for a seconds.
            if old_cores == new_cores or old_gigabytes == new_gigabytes:
                if c < _RETRY_COUNT - 1:
                    time.sleep(10)
                else:
                    raise exceptions.TimeoutException(str(body))
            else:
                break
        # Comparison of the quota
        contents = fixture.CATALOG_CONTENTS_DATA_LIST
        core_num = \
            (contents[0].get('goods_num') * REGISTRATION_NUM[0])
        self.assertEqual(old_cores + core_num, new_cores)
        ram_num = \
            (contents[1].get('goods_num') * REGISTRATION_NUM[1] * 1024)
        self.assertEqual(old_ram + ram_num, new_ram)
        gigabytes_num = \
            (contents[2].get('goods_num') * REGISTRATION_NUM[2])
        self.assertEqual(old_gigabytes + gigabytes_num, new_gigabytes)

        # cancellation
        body = self.os.limits_client.show_limits()
        total_cores_used = body['limits']['absolute']['totalCoresUsed']
        error_cores = \
            total_cores_used + core_num - 1

        body = self.os.volume_quotas_client.show_quota_usage(self.tenant_id)
        total_gigabytes_used = body['quota_set']['gigabytes']['in_use']
        error_gigabytes = \
            total_gigabytes_used + gigabytes_num - 1

        req, body = \
            self.aflo_client.list_contract(
                'application_id=%s' % registration_ticket_id)
        contract_id = body[0]['contract_id']

        # NOTE: Error lack the number of CPU
        self._update_cores(self.tenant_id, error_cores)
        try:
            self._create_cancellation_ticket(contract_id,
                                             ticket_template_id[1])
        except exceptions.Conflict:
            pass
        # NOTE: The normal system
        self._update_cores(self.tenant_id, new_cores)

        # NOTE: Error lack the number of Volume Storage
        self._update_gigabytes(self.tenant_id, error_gigabytes)
        try:
            self._create_cancellation_ticket(contract_id,
                                             ticket_template_id[1])
        except exceptions.Conflict:
            pass
        # NOTE: The normal system
        self._update_gigabytes(self.tenant_id, new_gigabytes)

        cancellation_ticket_id = self._create_cancellation_ticket(
            contract_id, ticket_template_id[1])

        self._update_ticket(cancellation_ticket_id, 'check')

        # NOTE: Error lack the number of CPU
        self._update_cores(self.tenant_id, error_cores)
        try:
            self._update_ticket(cancellation_ticket_id, 'approval')
        except exceptions.Conflict:
            pass
        # NOTE: The normal system
        self._update_cores(self.tenant_id, new_cores)

        # NOTE: Error lack the number of Volume Storage
        self._update_gigabytes(self.tenant_id, error_gigabytes)
        try:
            self._update_ticket(cancellation_ticket_id, 'approval')
        except exceptions.Conflict:
            pass
        # NOTE: The normal system
        self._update_gigabytes(self.tenant_id, new_gigabytes)

        self._update_ticket(cancellation_ticket_id, 'approval')

        # Wait for a quota of update
        for c in range(0, _RETRY_COUNT):
            body = self.os.quotas_client.show_quota_set(self.tenant_id)
            new_cores = body['quota_set']['cores']
            new_ram = body['quota_set']['ram']
            body = self.os.volume_quotas_client.show_quota_set(self.tenant_id)
            new_gigabytes = body['quota_set']['gigabytes']

            # DB Entry is asynchronous process.
            # Wait for a seconds.
            if old_cores != new_cores or old_gigabytes != new_gigabytes:
                if c < _RETRY_COUNT - 1:
                    time.sleep(10)
                else:
                    raise exceptions.TimeoutException(str(body))
            else:
                break
        # Comparison of the quota
        self.assertEqual(old_cores, new_cores)
        self.assertEqual(old_ram, new_ram)
        self.assertEqual(old_gigabytes, new_gigabytes)

        test_ticket.delete_ticket(self, registration_ticket_id)
        test_ticket.delete_ticket(self, cancellation_ticket_id)

        # Delete data.
        test_tickettemplate.delete_ticket_template(
            self, ticket_template_id)
        test_workflowpattern.delete_workflow_pattern(
            self, workflow_pattern_id)

        test_tickettemplate.delete_contract_info_data(
            self,
            contract_id,
            goods_ids,
            catalog_ids,
            contents_ids,
            catalog_scope_ids,
            price_ids)
