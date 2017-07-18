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

import testtools  # noqa

from tempest.api.aflo import base
from tempest import config_aflo as config  # noqa
from tempest.lib import exceptions

CONF = config.CONF


class ContractAdminTest(base.BaseV1AfloAdminTest):
    """Aflo Test Class by admin."""

    @classmethod
    def resource_setup(cls):
        """Setup Resources."""
        super(ContractAdminTest, cls).resource_setup()

    def test_contract(self):
        """Test of "Data Between Created to Deleted"."""

        # create data
        field = {'region_id': 'region_id',
                 'project_id': '5d19ec09dfb04e83b8385a2365c217e0',
                 'project_name': 'demo',
                 'catalog_id': 'catalog_id',
                 'catalog_name': 'catalog_name',
                 'num': 123,
                 'parent_ticket_template_id': 'parent_ticket_template_id',
                 'ticket_template_id': 'ticket_template_id',
                 'parent_ticket_template_name': 'parent_ticket_template_name',
                 'ticket_template_name': 'ticket_template_name',
                 'parent_application_kinds_name':
                 'parent_application_kinds_name',
                 'application_kinds_name': 'application_kinds_name',
                 'cancel_application_id': 'cancel_application_id',
                 'application_id': 'application_id',
                 'application_name': 'application_name',
                 'application_date': '2015-05-13T00:00:00.000000',
                 'parent_contract_id': 'parent_contract_id',
                 'lifetime_start': '2015-01-13T00:00:00.000000',
                 'lifetime_end': '2015-12-13T00:00:00.000000'}
        req, body = self.aflo_client.create_contract(field)

        contract_id = body['contract_id']

        self.assertTrue(contract_id is not None)

        try:

            # Get record
            resp, body = self.aflo_client.get_contract(contract_id)

            self.assertEqual(body['contract_id'], contract_id)
            self.assertEqual(body['region_id'], field['region_id'])
            self.assertEqual(body['project_id'], field['project_id'])
            self.assertEqual(body['project_name'], field['project_name'])
            self.assertEqual(body['catalog_id'], field['catalog_id'])
            self.assertEqual(body['catalog_name'], field['catalog_name'])
            self.assertEqual(body['num'], field['num'])
            self.assertEqual(body['parent_ticket_template_id'],
                             field['parent_ticket_template_id'])
            self.assertEqual(body['ticket_template_id'],
                             field['ticket_template_id'])
            self.assertEqual(body['parent_ticket_template_name'],
                             field['parent_ticket_template_name'])
            self.assertEqual(body['ticket_template_name'],
                             field['ticket_template_name'])
            self.assertEqual(body['parent_application_kinds_name'],
                             field['parent_application_kinds_name'])
            self.assertEqual(body['application_kinds_name'],
                             field['application_kinds_name'])
            self.assertEqual(body['cancel_application_id'],
                             field['cancel_application_id'])
            self.assertEqual(body['application_id'], field['application_id'])
            self.assertEqual(body['application_name'],
                             field['application_name'])
            self.assertEqual(body['application_date'],
                             field['application_date'])
            self.assertEqual(body['parent_contract_id'],
                             field['parent_contract_id'])
            self.assertEqual(body['lifetime_start'], field['lifetime_start'])
            self.assertEqual(body['lifetime_end'], field['lifetime_end'])

            # Update record
            field = {'region_id': 'region_id_test',
                     'project_id': '5d19ec09dfb04e83b8385a2365c217e0',
                     'project_name': 'demo',
                     'catalog_id': 'catalog_id_test',
                     'catalog_name': 'catalog_name_test',
                     'num': 456,
                     'parent_ticket_template_id':
                     'parent_ticket_template_id_test',
                     'ticket_template_id': 'ticket_template_id_test',
                     'parent_ticket_template_name':
                     'parent_ticket_template_name_test',
                     'ticket_template_name': 'ticket_template_name_test',
                     'parent_application_kinds_name':
                     'parent_application_kinds_name_test',
                     'application_kinds_name': 'application_kinds_name_test',
                     'cancel_application_id': 'cancel_application_id_test',
                     'application_id': 'application_id_test',
                     'application_name': 'application_name_test',
                     'application_date': '2015-06-06T00:00:00.000000',
                     'parent_contract_id': 'parent_contract_id_test',
                     'lifetime_start': '2015-02-02T00:00:00.000000',
                     'lifetime_end': '2015-12-18T00:00:00.000000'}
            req, body = self.aflo_client.update_contract(contract_id, field)

            self.assertEqual(body['contract_id'], contract_id)
            self.assertEqual(body['region_id'], field['region_id'])
            self.assertEqual(body['project_id'], field['project_id'])
            self.assertEqual(body['project_name'], field['project_name'])
            self.assertEqual(body['catalog_id'], field['catalog_id'])
            self.assertEqual(body['catalog_name'], field['catalog_name'])
            self.assertEqual(body['num'], field['num'])
            self.assertEqual(body['parent_ticket_template_id'],
                             field['parent_ticket_template_id'])
            self.assertEqual(body['ticket_template_id'],
                             field['ticket_template_id'])
            self.assertEqual(body['parent_ticket_template_name'],
                             field['parent_ticket_template_name'])
            self.assertEqual(body['ticket_template_name'],
                             field['ticket_template_name'])
            self.assertEqual(body['parent_application_kinds_name'],
                             field['parent_application_kinds_name'])
            self.assertEqual(body['application_kinds_name'],
                             field['application_kinds_name'])
            self.assertEqual(body['cancel_application_id'],
                             field['cancel_application_id'])
            self.assertEqual(body['application_id'], field['application_id'])
            self.assertEqual(body['application_name'],
                             field['application_name'])
            self.assertEqual(body['application_date'],
                             field['application_date'])
            self.assertEqual(body['parent_contract_id'],
                             field['parent_contract_id'])
            self.assertEqual(body['lifetime_start'], field['lifetime_start'])
            self.assertEqual(body['lifetime_end'], field['lifetime_end'])

            # Get record
            resp, body = self.aflo_client.get_contract(contract_id)

            self.assertEqual(body['contract_id'], contract_id)
            self.assertEqual(body['region_id'], field['region_id'])
            self.assertEqual(body['project_id'], field['project_id'])
            self.assertEqual(body['project_name'], field['project_name'])
            self.assertEqual(body['catalog_id'], field['catalog_id'])
            self.assertEqual(body['catalog_name'], field['catalog_name'])
            self.assertEqual(body['num'], field['num'])
            self.assertEqual(body['parent_ticket_template_id'],
                             field['parent_ticket_template_id'])
            self.assertEqual(body['ticket_template_id'],
                             field['ticket_template_id'])
            self.assertEqual(body['parent_ticket_template_name'],
                             field['parent_ticket_template_name'])
            self.assertEqual(body['ticket_template_name'],
                             field['ticket_template_name'])
            self.assertEqual(body['parent_application_kinds_name'],
                             field['parent_application_kinds_name'])
            self.assertEqual(body['application_kinds_name'],
                             field['application_kinds_name'])
            self.assertEqual(body['cancel_application_id'],
                             field['cancel_application_id'])
            self.assertEqual(body['application_id'], field['application_id'])
            self.assertEqual(body['application_name'],
                             field['application_name'])
            self.assertEqual(body['application_date'],
                             field['application_date'])
            self.assertEqual(body['parent_contract_id'],
                             field['parent_contract_id'])
            self.assertEqual(body['lifetime_start'], field['lifetime_start'])
            self.assertEqual(body['lifetime_end'], field['lifetime_end'])

        except Exception:
            if contract_id:
                self.aflo_client.delete_contract(contract_id)

        else:
            # Delete record
            self.aflo_client.delete_contract(contract_id)
            self.assertRaises(exceptions.NotFound,
                              self.aflo_client.get_contract, contract_id)

    def test_get_contract_no_result(self):
        """Test 'List search of contract.'
        Test of if you filtering lifetime with no result.
        """
        resp, body = self.aflo_client.list_price("lifetime=2016-01-01")

        self.assertTrue(len(body) == 0)
