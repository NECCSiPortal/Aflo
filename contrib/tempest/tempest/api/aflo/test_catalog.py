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


class CatalogAdminTest(base.BaseV1AfloAdminTest):
    """Aflo Test Class by admin."""

    @classmethod
    def resource_setup(cls):
        """Setup Resources."""
        super(CatalogAdminTest, cls).resource_setup()

    def test_catalog(self):
        """Test of "Data Between Created to Deleted"."""

        # create data
        field = {'region_id': 'region_id',
                 'catalog_name': 'catalog_name',
                 'lifetime_start': '2015-01-01T00:00:00.000000',
                 'lifetime_end': '2015-10-11T00:00:00.000000'}
        req, body = self.aflo_client.create_catalog(field)

        catalog_id = body['catalog_id']

        self.assertTrue(catalog_id is not None)

        try:
            # Get record
            resp, body = self.aflo_client.get_catalog(catalog_id)

            self.assertEqual(body['catalog_id'], catalog_id)
            self.assertEqual(body['region_id'], field['region_id'])
            self.assertEqual(body['catalog_name'], field['catalog_name'])
            self.assertEqual(body['lifetime_start'],
                             field['lifetime_start'])
            self.assertEqual(body['lifetime_end'], field['lifetime_end'])

            # Update record
            field = {'region_id': 'region_id_test',
                     'catalog_name': 'catalog_name_test',
                     'lifetime_start': '2015-03-03T00:00:00.000000',
                     'lifetime_end': '2015-11-12T00:00:00.000000'}
            req, body = self.aflo_client.update_catalog(catalog_id, field)

            self.assertEqual(body['region_id'], field['region_id'])
            self.assertEqual(body['catalog_name'], field['catalog_name'])
            self.assertEqual(body['lifetime_start'], field['lifetime_start'])
            self.assertEqual(body['lifetime_end'], field['lifetime_end'])

            # Get record
            resp, body = self.aflo_client.get_catalog(catalog_id)

            self.assertEqual(body['region_id'], field['region_id'])
            self.assertEqual(body['catalog_name'], field['catalog_name'])
            self.assertEqual(body['lifetime_start'], field['lifetime_start'])
            self.assertEqual(body['lifetime_end'], field['lifetime_end'])

        except Exception:
            if catalog_id:
                self.aflo_client.delete_catalog(catalog_id)
        else:
            # Delete record
            self.aflo_client.delete_catalog(catalog_id)
            self.assertRaises(exceptions.NotFound,
                              self.aflo_client.get_catalog, catalog_id)

    def test_get_catalog_no_result(self):
        """Test 'List search of catalog.'
        Test of if you filtering catalog_id with no result.
        """
        resp, body = self.aflo_client.list_catalog(
            "catalog_id=catalog0-1111-2222-3333-000000000006")

        self.assertTrue(len(body) == 0)
