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


class CatalogScopeAdminTest(base.BaseV1AfloAdminTest):
    """Test class for check catalog scope by admin."""

    @classmethod
    def resource_setup(cls):
        """Setup Resources."""
        super(CatalogScopeAdminTest, cls).resource_setup()

    def test_catalog_scope(self):
        """Test to manipulate the catalog scope data.
        Check process of create, get, update and delete.
        """

        # Create data.
        catalog_id = 'catalog0-111-222-333-0000001'
        scope = '5d19ec09dfb04e83b8385a2365c217e0'

        field = {'lifetime_start': '2015-01-01T00:00:00.000000',
                 'lifetime_end': '2015-10-11T00:00:00.000000'}
        req, body = self.aflo_client.create_catalog_scope(catalog_id,
                                                          scope, field)

        catalog_scope_id = body['id']

        self.assertTrue(catalog_scope_id is not None)

        try:
            # Get record.
            resp, body = self.aflo_client.get_catalog_scope(catalog_scope_id)

            self.assertEqual(body['id'], catalog_scope_id)
            self.assertEqual(body['catalog_id'], catalog_id)
            self.assertEqual(body['scope'], scope)
            self.assertEqual(body['lifetime_start'], field['lifetime_start'])
            self.assertEqual(body['lifetime_end'], field['lifetime_end'])

            # Update record.
            field = {'lifetime_start': '2017-03-03T00:00:00.000000',
                     'lifetime_end': '2020-11-12T00:00:00.000000'}
            req, body = self.aflo_client.update_catalog_scope(catalog_scope_id,
                                                              field)

            self.assertEqual(body['id'], catalog_scope_id)
            self.assertEqual(body['lifetime_start'], field['lifetime_start'])
            self.assertEqual(body['lifetime_end'], field['lifetime_end'])

            # Get record.
            resp, body = self.aflo_client.get_catalog_scope(catalog_scope_id)

            self.assertEqual(body['id'], catalog_scope_id)
            self.assertEqual(body['catalog_id'], catalog_id)
            self.assertEqual(body['scope'], scope)
            self.assertEqual(body['lifetime_start'], field['lifetime_start'])
            self.assertEqual(body['lifetime_end'], field['lifetime_end'])

        except Exception:
            if catalog_scope_id:
                self.aflo_client.delete_catalog_scope(catalog_scope_id)
        else:
            # Delete record.
            self.aflo_client.delete_catalog_scope(catalog_scope_id)
            self.assertRaises(exceptions.NotFound,
                              self.aflo_client.get_catalog_scope,
                              catalog_scope_id)

    def test_get_catalog_scope_no_result(self):
        """Test 'List search of catalog scope.'
        In this test, get no result
        by filtering the non-existent catalog_id.
        """
        resp, body = self.aflo_client.list_catalog_scope(
            "catalog_id=catalog0-1111-2222-3333-000000000006")

        self.assertTrue(len(body) == 0)
