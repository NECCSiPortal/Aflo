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


class PriceAdminTest(base.BaseV1AfloAdminTest):
    """Aflo Test Class by admin."""

    @classmethod
    def resource_setup(cls):
        """Setup Resources."""
        super(PriceAdminTest, cls).resource_setup()

    def test_price(self):
        """Test of "Data Between Created to Deleted"."""

        catalog_id = 'catalog_id'
        scope = 'Default'

        # create data
        field = {'price': '123.451',
                 'lifetime_start': '2015-01-01T00:00:00.000000',
                 'lifetime_end': '2015-12-13T00:00:00.000000'}
        req, body = self.aflo_client.create_price(catalog_id, scope, field)

        seq_no = body['seq_no']

        self.assertTrue(seq_no is not None)

        try:

            # Get record
            resp, body = self.aflo_client.get_price(catalog_id, scope, seq_no)

            self.assertEqual(body['catalog_id'], catalog_id)
            self.assertEqual(body['scope'], scope)
            self.assertEqual(body['seq_no'], seq_no)
            self.assertEqual(body['price'], field['price'])
            self.assertEqual(body['lifetime_start'], field['lifetime_start'])
            self.assertEqual(body['lifetime_end'], field['lifetime_end'])

            # Update record
            field = {'price': '678.091',
                     'lifetime_start': '2015-02-02T00:00:00.000000',
                     'lifetime_end': '2015-12-13T00:00:00.000000'}
            req, body = self.aflo_client.update_price(catalog_id,
                                                      scope,
                                                      seq_no,
                                                      field)

            self.assertEqual(body['price'], field['price'])
            self.assertEqual(body['lifetime_start'], field['lifetime_start'])
            self.assertEqual(body['lifetime_end'], field['lifetime_end'])

            # Get record
            resp, body = self.aflo_client.get_price(catalog_id, scope, seq_no)

            self.assertEqual(body['price'], field['price'])
            self.assertEqual(body['lifetime_start'], field['lifetime_start'])
            self.assertEqual(body['lifetime_end'], field['lifetime_end'])

        except Exception:
            if catalog_id and scope and seq_no:
                self.aflo_client.delete_price(catalog_id, scope, seq_no)

        else:
            # Delete record
            self.aflo_client.delete_price(catalog_id, scope, seq_no)
            self.assertRaises(exceptions.NotFound,
                              self.aflo_client.get_price,
                              catalog_id,
                              scope,
                              seq_no)

    def test_get_price_no_result(self):
        """Test 'List search of price.'
        Test of if you filtering catalog_id with no result.
        """
        catalog_id = "catalog0-1111-2222-3333-000000000001"
        resp, body = self.aflo_client.list_price(
            catalog_id,
            "scope=no_scope")

        self.assertTrue(len(body) == 0)
