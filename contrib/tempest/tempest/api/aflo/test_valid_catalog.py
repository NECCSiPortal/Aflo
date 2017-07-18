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

from tempest.api.aflo import base
from tempest.lib import exceptions


class ValidCatalogAdminTest(base.BaseV1AfloAdminTest):
    """Test class for check valid catalog by admin."""

    @classmethod
    def resource_setup(cls):
        """Setup Resources."""
        super(ValidCatalogAdminTest, cls).resource_setup()

    def test_valid_catalog(self):
        """Test 'List search of valid catalog.'"""

        # To get list of valid catalog,
        # it is necessary to prepare a test data in the following table.
        # - catalog
        # - catalog_scope
        # - price
        field = {'region_id': 'region_id',
                 'catalog_name': 'catalog_name',
                 'lifetime_start': '2015-01-01T00:00:00.000000',
                 'lifetime_end': '2020-10-11T00:00:00.000000'}
        req, body = self.aflo_client.create_catalog(field)
        catalog_id = body['catalog_id']

        self.assertTrue(catalog_id is not None)

        scope = 'Default'
        field = {'price': '123.451',
                 'lifetime_start': '2015-01-01T00:00:00.000000',
                 'lifetime_end': '2020-12-13T00:00:00.000000'}
        req, body = self.aflo_client.create_price(catalog_id, scope, field)
        seq_no = body['seq_no']

        self.assertTrue(seq_no is not None)

        field = {'lifetime_start': '2015-01-01T00:00:00.000000',
                 'lifetime_end': '2018-10-11T00:00:00.000000'}
        req, body = self.aflo_client.create_catalog_scope(catalog_id,
                                                          scope, field)
        catalog_scope_id = body['id']

        self.assertTrue(catalog_scope_id is not None)

        # Get list data.
        url_palams = 'lifetime=2016-01-01T00:00:00.000000&scope=Default'
        resp, body = self.aflo_client.list_valid_catalog(url_palams)

        self.assertTrue(len(body) >= 1)

        result = False
        for valid_info in body:
            if valid_info['catalog_id'] == catalog_id and \
                    valid_info['catalog_scope_id'] == catalog_scope_id and \
                    valid_info['price_seq_no'] == seq_no:
                result = True
                break

        self.assertTrue(result)

        # The test data it will clean up.
        self.aflo_client.delete_catalog(catalog_id)
        self.assertRaises(exceptions.NotFound,
                          self.aflo_client.get_catalog, catalog_id)

        self.aflo_client.delete_price(catalog_id, scope, seq_no)
        self.assertRaises(exceptions.NotFound,
                          self.aflo_client.get_price,
                          catalog_id,
                          scope,
                          seq_no)

        self.aflo_client.delete_catalog_scope(catalog_scope_id)
        self.assertRaises(exceptions.NotFound,
                          self.aflo_client.get_catalog_scope,
                          catalog_scope_id)

    def test_list_valid_catalog_no_result(self):
        """Test 'List search of valid catalog.'
        In this test, get no result
        by filtering the non-existent lifetime and scope.
        """
        # Get list data.
        url_palams = 'lifetime=3019-01-01T00:00:00.000000&scope=Default'
        resp, body = self.aflo_client.list_valid_catalog(url_palams)

        self.assertTrue(len(body) == 0)
