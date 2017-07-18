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

from datetime import datetime
from oslo_config import cfg
from oslo_serialization import jsonutils
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

    def test_show(self):
        """Test 'Get of catalog scope'
        Test the operation of default.
        """
        path = '/catalogs/scope/%s' % ID_101
        req = unit_test_utils.get_fake_request(method='GET',
                                               path=path)

        headers = {'x-auth-token': 'user:tenant:developer'}
        for k, v in headers.iteritems():
            req.headers[k] = v

        # Send request
        res = req.get_response(self.api)

        # Examination of response
        self.assertEqual(res.status_int, 200)
        res_objs = jsonutils.loads(res.body)['catalog_scope']
        self.assertEqual(res_objs['id'], ID_101)
        self.assertEqual(res_objs['catalog_id'], CATALOG_ID_101)
        self.assertEqual(res_objs['scope'], SCOPE_101)
        self.assertEqual(res_objs['lifetime_start'],
                         '2015-12-31T23:59:59.999999')
        self.assertEqual(res_objs['lifetime_end'],
                         '9999-12-31T23:59:59.999999')
        self.assertEqual(res_objs['expansions']['expansion_key1'],
                         'expansion_key1')
        self.assertEqual(res_objs['expansions']['expansion_key2'],
                         'expansion_key2')
        self.assertEqual(res_objs['expansions']['expansion_key3'],
                         'expansion_key3')
        self.assertEqual(res_objs['expansions']['expansion_key4'],
                         'expansion_key4')
        self.assertEqual(res_objs['expansions']['expansion_key5'],
                         'expansion_key5')
        self.assertEqual(res_objs['expansions_text']['expansion_text'],
                         'expansion_text')
        self.assertIsNotNone(res_objs['created_at'])
        self.assertIsNotNone(res_objs['updated_at'])
        self.assertIsNone(res_objs['deleted_at'])
        self.assertEqual(res_objs['deleted'], False)

    def test_show_response_empty_id_irregular(self):
        """Test 'Get of catalog scope'
        Test when the specified 'id' does not exist.
        """
        path = '/catalogs/scope/%s' % ID_105
        req = unit_test_utils.get_fake_request(method='GET',
                                               path=path)

        headers = {'x-auth-token': 'user:tenant:developer'}
        for k, v in headers.iteritems():
            req.headers[k] = v

        # Send request
        res = req.get_response(self.api)

        # Examination of response
        self.assertEqual(res.status_int, 404)

    def test_show_api_no_authority_irregular(self):
        """Test 'Get of catalog scope'
        Test cases run unauthorized.
        """
        path = '/catalogs/scope/%s' % ID_105
        req = unit_test_utils.get_fake_request(method='GET',
                                               path=path)

        headers = {'x-auth-token': 'user:tenant:no_autority'}
        for k, v in headers.iteritems():
            req.headers[k] = v

        # Send request
        res = req.get_response(self.api)

        # Examination of response
        self.assertEqual(res.status_int, 403)

    def test_show_api_symbol(self):
        """Test 'Get of catalog scope'
        Test when the acquired parameters include a symbol.
        """
        path = '/catalogs/scope/%s' % ID_104
        req = unit_test_utils.get_fake_request(method='GET',
                                               path=path)

        headers = {'x-auth-token': 'user:tenant:developer'}
        for k, v in headers.iteritems():
            req.headers[k] = v

        # Send request
        res = req.get_response(self.api)

        # Examination of response
        self.assertEqual(res.status_int, 200)
        res_objs = jsonutils.loads(res.body)['catalog_scope']
        self.assertEqual(res_objs['id'], ID_104)
        self.assertEqual(res_objs['expansions']['expansion_key5'],
                         '!"#$%&()=~|`{+*}<>?_')
        self.assertEqual(res_objs['expansions_text']['expansion_text'],
                         ',./\;:]@[\^-')

    def test_show_api_response_one_expansions(self):
        """Test 'Get of catalog scope'
        Test if the retrieved result is one expansion_key.
        """
        path = '/catalogs/scope/%s' % ID_102
        req = unit_test_utils.get_fake_request(method='GET',
                                               path=path)

        headers = {'x-auth-token': 'user:tenant:developer'}
        for k, v in headers.iteritems():
            req.headers[k] = v

        # Send request
        res = req.get_response(self.api)

        # Examination of response
        self.assertEqual(res.status_int, 200)
        res_objs = jsonutils.loads(res.body)['catalog_scope']
        self.assertEqual(res_objs['id'], ID_102)
        self.assertEqual(res_objs['expansions']['expansion_key1'],
                         'expansion_key1')
        self.assertIsNone(res_objs['expansions']['expansion_key2'])
        self.assertIsNone(res_objs['expansions']['expansion_key3'])
        self.assertIsNone(res_objs['expansions']['expansion_key4'])
        self.assertIsNone(res_objs['expansions']['expansion_key5'])

    def test_show_api_response_none_expansions(self):
        """Test 'Get of catalog scope'
        Test if the retrieved result is non expansion_key.
        """
        path = '/catalogs/scope/%s' % ID_103
        req = unit_test_utils.get_fake_request(method='GET',
                                               path=path)

        headers = {'x-auth-token': 'user:tenant:developer'}
        for k, v in headers.iteritems():
            req.headers[k] = v

        # Send request
        res = req.get_response(self.api)

        # Examination of response
        self.assertEqual(res.status_int, 200)
        res_objs = jsonutils.loads(res.body)['catalog_scope']
        self.assertEqual(res_objs['id'], ID_103)
        self.assertIsNone(res_objs['expansions']['expansion_key1'])
        self.assertIsNone(res_objs['expansions']['expansion_key2'])
        self.assertIsNone(res_objs['expansions']['expansion_key3'])
        self.assertIsNone(res_objs['expansions']['expansion_key4'])
        self.assertIsNone(res_objs['expansions']['expansion_key5'])
        self.assertIsNone(res_objs['expansions_text']['expansion_text'])

    def test_show_id_length_irregular(self):
        """Test 'Get of catalog scope'
        Test when the length of the ID is invalid.
        """
        path = '/catalogs/scope/%s' % ('a' * 65)
        req = unit_test_utils.get_fake_request(method='GET',
                                               path=path)

        headers = {'x-auth-token': 'user:tenant:developer'}
        for k, v in headers.iteritems():
            req.headers[k] = v

        # Send request
        res = req.get_response(self.api)

        # Examination of response
        self.assertEqual(res.status_int, 400)

    def test_show_id_error_uri_irregular(self):
        """Test 'Get of catalog scope'
        Test when the required parameter without.
        """
        path = '/catalogs/scope/%s' % ''
        req = unit_test_utils.get_fake_request(method='GET',
                                               path=path)

        headers = {'x-auth-token': 'user:tenant:developer'}
        for k, v in headers.iteritems():
            req.headers[k] = v

        # Send request
        res = req.get_response(self.api)

        # Examination of response
        self.assertEqual(res.status_int, 404)
