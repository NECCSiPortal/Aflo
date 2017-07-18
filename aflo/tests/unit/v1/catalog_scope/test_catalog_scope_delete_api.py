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

from datetime import datetime
from oslo_config import cfg
import routes

from aflo.api.v1 import router
from aflo.common import wsgi
from aflo import context
from aflo import db
from aflo.db.sqlalchemy import models as db_models
from aflo.db.sqlalchemy.models import CatalogScope
from aflo.tests.unit import base
import aflo.tests.unit.utils as unit_test_utils
from aflo.tests import utils as test_utils

CONF = cfg.CONF
db_api = db.get_api()

ID_101 = 'id0a4146-fd07-414b-aa5e-dedbeef00101'
ID_102 = 'id0a4146-fd07-414b-aa5e-dedbeef00102'
ID_103 = 'id0a4146-fd07-414b-aa5e-dedbeef00103'
ID_104 = 'id0a4146-fd07-414b-aa5e-dedbeef00104'
ID_105 = 'id0a4146-fd07-414b-aa5e-dedbeef00105'

CATALOG_ID_101 = 'ea0a4146-fd07-414b-aa5e-dedbeef00101'
CATALOG_ID_102 = 'ea0a4146-fd07-414b-aa5e-dedbeef00102'

SCOPE_101 = 'bdb8f50f82da4370813e6ea797b1fb101'
SCOPE_102 = 'bdb8f50f82da4370813e6ea797b1fb102'
SCOPE_DEF = 'Default'


class TestAPI(base.IsolatedUnitTest):
    def setUp(self):
        """Establish a clean test environment"""
        super(TestAPI, self).setUp()
        self.mapper = routes.Mapper()
        self.api = test_utils.FakeAuthMiddleware(router.API(self.mapper))

        self.context = context.RequestContext(is_admin=True)
        db_api.get_engine()
        self.destroy_fixtures()
        self.create_fixtures()
        self.serializer = wsgi.JSONResponseSerializer()

    def tearDown(self):
        """Clear the test environment"""
        super(TestAPI, self).tearDown()
        self.destroy_fixtures()

    def create_fixtures(self):
        CatalogScope(id=ID_101,
                     catalog_id=CATALOG_ID_101,
                     scope=SCOPE_101,
                     lifetime_start=datetime(2015, 12, 31, 23, 59, 59, 999999),
                     lifetime_end=datetime(9999, 12, 31, 23, 59, 59, 999999),
                     created_at=datetime.utcnow(),
                     updated_at=datetime.utcnow(),
                     deleted_at=None,
                     deleted=False,
                     expansion_key1='expansion_key1',
                     expansion_key2='expansion_key2',
                     expansion_key3='expansion_key3',
                     expansion_key4='expansion_key4',
                     expansion_key5='expansion_key5',
                     expansion_text='expansion_text'
                     ).save(db_api.get_session())

        CatalogScope(id=ID_102,
                     catalog_id=CATALOG_ID_101,
                     scope=SCOPE_102,
                     lifetime_start=datetime(2015, 12, 31, 23, 59, 59, 999999),
                     lifetime_end=datetime(9999, 12, 31, 23, 59, 59, 999999),
                     created_at=datetime.utcnow(),
                     updated_at=datetime.utcnow(),
                     deleted_at=None,
                     deleted=False,
                     expansion_key1='expansion_key1',
                     expansion_key2=None,
                     expansion_key3=None,
                     expansion_key4=None,
                     expansion_key5=None,
                     expansion_text='expansion_text'
                     ).save(db_api.get_session())

        CatalogScope(id=ID_103,
                     catalog_id=CATALOG_ID_101,
                     scope=SCOPE_DEF,
                     lifetime_start=datetime(2015, 12, 31, 23, 59, 59, 999999),
                     lifetime_end=datetime(9999, 12, 31, 23, 59, 59, 999999),
                     created_at=datetime.utcnow(),
                     updated_at=datetime.utcnow(),
                     deleted_at=None,
                     deleted=False,
                     expansion_key1=None,
                     expansion_key2=None,
                     expansion_key3=None,
                     expansion_key4=None,
                     expansion_key5=None,
                     expansion_text=None
                     ).save(db_api.get_session())

        CatalogScope(id=ID_104,
                     catalog_id=CATALOG_ID_101,
                     scope=SCOPE_DEF,
                     lifetime_start=datetime(2015, 12, 31, 23, 59, 59, 999999),
                     lifetime_end=datetime(9999, 12, 31, 23, 59, 59, 999999),
                     created_at=datetime.utcnow(),
                     updated_at=datetime.utcnow(),
                     deleted_at=None,
                     deleted=False,
                     expansion_key1='!"#$%&()=~|`{+*}<>?_',
                     expansion_key2='!"#$%&()=~|`{+*}<>?_',
                     expansion_key3='!"#$%&()=~|`{+*}<>?_',
                     expansion_key4='!"#$%&()=~|`{+*}<>?_',
                     expansion_key5='!"#$%&()=~|`{+*}<>?_',
                     expansion_text=',./\;:]@[\^-'
                     ).save(db_api.get_session())

    def destroy_fixtures(self):
        db_models.unregister_models(db_api.get_engine())
        db_models.register_models(db_api.get_engine())

    def test_delete(self):
        """Test 'Delete a catalog scope'
        Test the operation of default.
        """
        path = '/catalogs/scope/%s' % ID_101
        req = unit_test_utils.get_fake_request(method='DELETE',
                                               path=path)

        headers = {'x-auth-token': 'user:tenant:admin'}
        for k, v in headers.iteritems():
            req.headers[k] = v

        res = req.get_response(self.api)
        self.assertEqual(res.status_int, 200)

        se = db_api.get_session()
        catalog_scope = se.query(db_models.CatalogScope)\
            .filter_by(id=ID_101).first()
        self.assertIsNone(catalog_scope)

    def test_delete_api_no_authority_irregular(self):
        """Test 'Delete a catalog scope'
        Test cases run unauthorized.
        """
        path = '/catalogs/scope/%s' % ID_101
        req = unit_test_utils.get_fake_request(method='DELETE',
                                               path=path)

        headers = {'x-auth-token': 'user:tenant:__member__'}
        for k, v in headers.iteritems():
            req.headers[k] = v

        res = req.get_response(self.api)
        self.assertEqual(res.status_int, 403)

    def test_delete_api_no_exist_irregular(self):
        """Test 'Delete a catalog scope'
        Test when the specified 'id' does not exist.
        """
        path = '/catalogs/scope/%s' % ID_105
        req = unit_test_utils.get_fake_request(method='DELETE',
                                               path=path)

        headers = {'x-auth-token': 'user:tenant:admin'}
        for k, v in headers.iteritems():
            req.headers[k] = v

        res = req.get_response(self.api)
        self.assertEqual(res.status_int, 404)

    def test_delete_id_length_irregular(self):
        """Test 'Delete a catalog scope'
        Test when the length of the ID is invalid.
        """
        path = '/catalogs/scope/%s' % ('a' * 65)
        req = unit_test_utils.get_fake_request(method='DELETE',
                                               path=path)

        headers = {'x-auth-token': 'user:tenant:admin'}
        for k, v in headers.iteritems():
            req.headers[k] = v

        res = req.get_response(self.api)
        self.assertEqual(res.status_int, 400)

    def test_delete_api_error_uri_irregular(self):
        """Test 'Delete a catalog scope'
        Test when the required parameter without.
        """
        path = '/catalogs/scope/%s' % ''
        req = unit_test_utils.get_fake_request(method='DELETE',
                                               path=path)

        headers = {'x-auth-token': 'user:tenant:admin'}
        for k, v in headers.iteritems():
            req.headers[k] = v

        res = req.get_response(self.api)
        self.assertEqual(res.status_int, 404)
