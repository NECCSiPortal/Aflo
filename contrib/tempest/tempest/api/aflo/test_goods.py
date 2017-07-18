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

from tempest.api.aflo import base
from tempest import config_aflo as config  # noqa
from tempest.lib import exceptions

CONF = config.CONF


class GoodsAdminTest(base.BaseV1AfloAdminTest):
    """Aflo Test Class by admin."""

    @classmethod
    def resource_setup(cls):
        """Setup Resources."""
        super(GoodsAdminTest, cls).resource_setup()

    def test_goods(self):
        """Test of "Data Between Created to Deleted"."""

        # create data
        field = {'goods_name': 'test_goods'}
        req, body = self.aflo_client.create_goods(field)

        goods_id = body['goods_id']

        self.assertTrue(goods_id is not None)

        try:

            # Get record
            resp, body = self.aflo_client.get_goods(goods_id)

            self.assertEqual(body['goods_id'], goods_id)
            self.assertEqual(body['goods_name'], 'test_goods')

            # Update record
            field = {'goods_name': 'test_goods_test'}
            req, body = self.aflo_client.update_goods(goods_id, field)

            print(body)
            self.assertEqual(body['goods_name'], 'test_goods_test')

            # Get record
            resp, body = self.aflo_client.get_goods(goods_id)
            self.assertEqual(body['goods_name'], 'test_goods_test')

        except Exception:
            if goods_id:
                self.aflo_client.delete_goods(goods_id)

        else:
            # Delete record
            self.aflo_client.delete_goods(goods_id)
            self.assertRaises(exceptions.NotFound,
                              self.aflo_client.get_goods, goods_id)

    def test_get_goods_no_result(self):
        """Test 'List search of goods.'
        Test of if you filtering irregular ticket type.
        """
        resp, body = self.aflo_client.list_goods(
            "region_id=samplexx-3e13-4284-a2f7-05b1b71ef40a")

        self.assertTrue(len(body) == 0)
