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


class CatalogContentsAdminTest(base.BaseV1AfloAdminTest):
    """Aflo Test Class by admin."""

    @classmethod
    def resource_setup(cls):
        """Setup Resources."""
        super(CatalogContentsAdminTest, cls).resource_setup()

    def test_catalog_contents(self):
        """Test of "Data Between Created to Deleted"."""

        catalog_id = 'catalog_id'

        # create data
        field = {'goods_id': 'goods_id',
                 'goods_num': 123}
        req, body = self.aflo_client.create_catalog_contents(catalog_id, field)

        seq_no = body['seq_no']

        self.assertTrue(seq_no is not None)

        try:

            # Get record
            resp, body = self.aflo_client.get_catalog_contents(catalog_id,
                                                               seq_no)

            self.assertEqual(body['catalog_id'], catalog_id)
            self.assertEqual(body['seq_no'], seq_no)
            self.assertEqual(body['goods_id'], field['goods_id'])
            self.assertEqual(body['goods_num'], field['goods_num'])

            # Update record
            field = {'goods_id': 'goods_id_test',
                     'goods_num': 456}
            req, body = self.aflo_client.update_catalog_contents(catalog_id,
                                                                 seq_no,
                                                                 field)

            self.assertEqual(body['goods_id'], field['goods_id'])
            self.assertEqual(body['goods_num'], field['goods_num'])

            # Get record
            resp, body = self.aflo_client.get_catalog_contents(catalog_id,
                                                               seq_no)

            self.assertEqual(body['goods_id'], field['goods_id'])
            self.assertEqual(body['goods_num'], field['goods_num'])

        except Exception:
            if catalog_id and seq_no:
                self.aflo_client.delete_catalog_contents(catalog_id, seq_no)

        else:

            # Delete record
            self.aflo_client.delete_catalog_contents(catalog_id, seq_no)
            self.assertRaises(exceptions.NotFound,
                              self.aflo_client.delete_catalog_contents,
                              catalog_id,
                              seq_no)

    def test_get_catalog_contents_no_result(self):
        """Test 'List search of catalog_contents.'
        Test of if you filtering catalog_id with no result.
        """
        catalog_id = "catalog0-1111-2222-3333-000000000006"
        resp, body = self.aflo_client.list_catalog_contents(catalog_id)

        self.assertTrue(len(body) == 0)
