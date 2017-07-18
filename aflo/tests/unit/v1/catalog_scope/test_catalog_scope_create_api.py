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

from oslo_config import cfg
from oslo_serialization import jsonutils
import routes

from aflo.api.v1 import router
from aflo.common import wsgi
from aflo import context
from aflo import db
from aflo.db.sqlalchemy import models as db_models
from aflo.tests.unit import base
import aflo.tests.unit.utils as unit_test_utils
from aflo.tests import utils as test_utils

CONF = cfg.CONF
db_api = db.get_api()

CATALOG_ID_101 = 'ea0a4146-fd07-414b-aa5e-dedbeef00101'
SCOPE_101 = 'bdb8f50f82da4370813e6ea797b1fb101'
SCOPE_DEF = 'Default'

body_normal = {
    "catalog_scope": {
        "lifetime_start": '2015-12-31T23:59:59.999999',
        "lifetime_end": '9999-12-31T23:59:59.999999',
        "expansions": {
            "expansion_key1": 'expansion_key1',
            "expansion_key2": 'expansion_key2',
            "expansion_key3": 'expansion_key3',
            "expansion_key4": 'expansion_key4',
            "expansion_key5": 'expansion_key5'
        },
        "expansions_text": {
            "expansion_text": 'expansion_text'
        }
    }
}

body_no_data = {
    "catalog_scope": {
        "lifetime_start": None,
        "lifetime_end": None,
        "expansions": {
            "expansion_key1": None,
            "expansion_key2": None,
            "expansion_key3": None,
            "expansion_key4": None,
            "expansion_key5": None
        },
        "expansions_text": {
            "expansion_text": None
        }
    }
}

body_lifetime_start_error = {
    "catalog_scope": {
        "lifetime_start": '2015-12-31T23:59:59',
        "lifetime_end": '9999-12-31T23:59:59.999999',
        "expansions": {
            "expansion_key1": 'expansion_key1',
            "expansion_key2": 'expansion_key2',
            "expansion_key3": 'expansion_key3',
            "expansion_key4": 'expansion_key4',
            "expansion_key5": 'expansion_key5'
        },
        "expansions_text": {
            "expansion_text": 'expansion_text'
        }
    }
}

body_lifetime_end_error = {
    "catalog_scope": {
        "lifetime_start": '2015-12-31T23:59:59.999999',
        "lifetime_end": '9999-12-31',
        "expansions": {
            "expansion_key1": 'expansion_key1',
            "expansion_key2": 'expansion_key2',
            "expansion_key3": 'expansion_key3',
            "expansion_key4": 'expansion_key4',
            "expansion_key5": 'expansion_key5'
        },
        "expansions_text": {
            "expansion_text": 'expansion_text'
        }
    }
}

body_lifetime_order_error = {
    "catalog_scope": {
        "lifetime_start": '2020-12-31T23:59:59.999999',
        "lifetime_end": '2019-12-31T23:59:59.999999',
        "expansions": {
            "expansion_key1": 'expansion_key1',
            "expansion_key2": 'expansion_key2',
            "expansion_key3": 'expansion_key3',
            "expansion_key4": 'expansion_key4',
            "expansion_key5": 'expansion_key5'
        },
        "expansions_text": {
            "expansion_text": 'expansion_text'
        }
    }
}

body_expansion_key1_error = {
    "catalog_scope": {
        "lifetime_start": '2015-12-31T23:59:59.999999',
        "lifetime_end": '9999-12-31T23:59:59.999999',
        "expansions": {
            "expansion_key1": 'a' * 256,
            "expansion_key2": 'expansion_key2',
            "expansion_key3": 'expansion_key3',
            "expansion_key4": 'expansion_key4',
            "expansion_key5": 'expansion_key5'
        },
        "expansions_text": {
            "expansion_text": 'expansion_text'
        }
    }
}

body_expansion_key2_error = {
    "catalog_scope": {
        "lifetime_start": '2015-12-31T23:59:59.999999',
        "lifetime_end": '9999-12-31T23:59:59.999999',
        "expansions": {
            "expansion_key1": 'expansion_key1',
            "expansion_key2": 'a' * 256,
            "expansion_key3": 'expansion_key3',
            "expansion_key4": 'expansion_key4',
            "expansion_key5": 'expansion_key5'
        },
        "expansions_text": {
            "expansion_text": 'expansion_text'
        }
    }
}

body_expansion_key3_error = {
    "catalog_scope": {
        "lifetime_start": '2015-12-31T23:59:59.999999',
        "lifetime_end": '9999-12-31T23:59:59.999999',
        "expansions": {
            "expansion_key1": 'expansion_key1',
            "expansion_key2": 'expansion_key2',
            "expansion_key3": 'a' * 256,
            "expansion_key4": 'expansion_key4',
            "expansion_key5": 'expansion_key5'
        },
        "expansions_text": {
            "expansion_text": 'expansion_text'
        }
    }
}

body_expansion_key4_error = {
    "catalog_scope": {
        "lifetime_start": '2015-12-31T23:59:59.999999',
        "lifetime_end": '9999-12-31T23:59:59.999999',
        "expansions": {
            "expansion_key1": 'expansion_key1',
            "expansion_key2": 'expansion_key2',
            "expansion_key3": 'expansion_key3',
            "expansion_key4": 'a' * 256,
            "expansion_key5": 'expansion_key5'
        },
        "expansions_text": {
            "expansion_text": 'expansion_text'
        }
    }
}

body_expansion_key5_error = {
    "catalog_scope": {
        "lifetime_start": '2015-12-31T23:59:59.999999',
        "lifetime_end": '9999-12-31T23:59:59.999999',
        "expansions": {
            "expansion_key1": 'expansion_key1',
            "expansion_key2": 'expansion_key2',
            "expansion_key3": 'expansion_key3',
            "expansion_key4": 'expansion_key4',
            "expansion_key5": 'a' * 256
        },
        "expansions_text": {
            "expansion_text": 'expansion_text'
        }
    }
}

body_expansion_text_error = {
    "catalog_scope": {
        "lifetime_start": '2015-12-31T23:59:59.999999',
        "lifetime_end": '9999-12-31T23:59:59.999999',
        "expansions": {
            "expansion_key1": 'expansion_key1',
            "expansion_key2": 'expansion_key2',
            "expansion_key3": 'expansion_key3',
            "expansion_key4": 'expansion_key4',
            "expansion_key5": 'expansion_key5'
        },
        "expansions_text": {
            "expansion_text": 'a' * 4001
        }
    }
}


class TestAPI(base.WorkflowUnitTest):
    """Test 'Create a new catalog scope"""

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
        super(TestAPI, self).create_fixtures()

    def destroy_fixtures(self):
        # Easiest to just drop the models and re-create them...
        db_models.unregister_models(db_api.get_engine())
        db_models.register_models(db_api.get_engine())

    def test_create(self):
        """Test 'Create a new catalog scope'
        Test the operation of default.
        """

        path = '/catalogs/%s/scope/%s' % (CATALOG_ID_101, SCOPE_101)
        req = unit_test_utils.get_fake_request(method='POST',
                                               path=path)
        headers = {'x-auth-token': 'user:tenant:admin',
                   'x-user-name': 'user-name',
                   'x-tenant-name': 'tenant-name'}
        for k, v in headers.iteritems():
            req.headers[k] = v

        req.body = jsonutils.dumps(body_normal)

        # Send request
        res = req.get_response(self.api)

        self.assertEqual(res.status_int, 200)

        catalog_scope = jsonutils.loads(res.body)['catalog_scope']

        self.assertIsNotNone(catalog_scope['id'])
        self.assertEqual(catalog_scope['catalog_id'], CATALOG_ID_101)
        self.assertEqual(catalog_scope['scope'], SCOPE_101)
        self.assertEqual(catalog_scope['lifetime_start'],
                         '2015-12-31T23:59:59.999999')
        self.assertEqual(catalog_scope['lifetime_end'],
                         '9999-12-31T23:59:59.999999')
        self.assertEqual(catalog_scope['expansions']['expansion_key1'],
                         'expansion_key1')
        self.assertEqual(catalog_scope['expansions']['expansion_key2'],
                         'expansion_key2')
        self.assertEqual(catalog_scope['expansions']['expansion_key3'],
                         'expansion_key3')
        self.assertEqual(catalog_scope['expansions']['expansion_key4'],
                         'expansion_key4')
        self.assertEqual(catalog_scope['expansions']['expansion_key5'],
                         'expansion_key5')
        self.assertEqual(catalog_scope['expansions_text']['expansion_text'],
                         'expansion_text')
        self.assertIsNotNone(catalog_scope['created_at'])
        self.assertIsNotNone(catalog_scope['updated_at'])
        self.assertIsNone(catalog_scope['deleted_at'])
        self.assertEqual(catalog_scope['deleted'], False)

    def test_create_with_none_value(self):
        """Test 'Create a new catalog scope'
        Test the operation of the body parameter without.
        """

        path = '/catalogs/%s/scope/%s' % (CATALOG_ID_101, SCOPE_101)
        req = unit_test_utils.get_fake_request(method='POST',
                                               path=path)
        headers = {'x-auth-token': 'user:tenant:admin',
                   'x-user-name': 'user-name',
                   'x-tenant-name': 'tenant-name'}
        for k, v in headers.iteritems():
            req.headers[k] = v

        req.body = jsonutils.dumps(body_no_data)

        # Send request
        res = req.get_response(self.api)

        self.assertEqual(res.status_int, 200)

        catalog_scope = jsonutils.loads(res.body)['catalog_scope']

        self.assertIsNotNone(catalog_scope['id'])
        self.assertEqual(catalog_scope['catalog_id'], CATALOG_ID_101)
        self.assertEqual(catalog_scope['scope'], SCOPE_101)
        self.assertIsNone(catalog_scope['lifetime_start'])
        self.assertIsNone(catalog_scope['lifetime_end'])
        self.assertIsNone(catalog_scope['expansions']['expansion_key1'])
        self.assertIsNone(catalog_scope['expansions']['expansion_key2'])
        self.assertIsNone(catalog_scope['expansions']['expansion_key3'])
        self.assertIsNone(catalog_scope['expansions']['expansion_key4'])
        self.assertIsNone(catalog_scope['expansions']['expansion_key5'])
        self.assertIsNone(catalog_scope['expansions_text']['expansion_text'])
        self.assertIsNotNone(catalog_scope['created_at'])
        self.assertIsNotNone(catalog_scope['updated_at'])
        self.assertIsNone(catalog_scope['deleted_at'])
        self.assertEqual(catalog_scope['deleted'], False)

    def test_create_member_authority_irregular(self):
        """Test 'Create a new catalog scope'
        Test cases run unauthorized.
        """

        path = '/catalogs/%s/scope/%s' % (CATALOG_ID_101, SCOPE_101)
        req = unit_test_utils.get_fake_request(method='POST',
                                               path=path)
        headers = {'x-auth-token': 'user:tenant:__member__',
                   'x-user-name': 'user-name',
                   'x-tenant-name': 'tenant-name'}
        for k, v in headers.iteritems():
            req.headers[k] = v

        req.body = jsonutils.dumps(body_normal)

        # Send request
        res = req.get_response(self.api)

        self.assertEqual(res.status_int, 403)

    def test_create_catalog_id_length_irregular(self):
        """Test 'Create a new catalog scope'
        Test when the length of the catalog id is invalid.
        """

        path = '/catalogs/%s/scope/%s' % ('a' * 65, SCOPE_101)
        req = unit_test_utils.get_fake_request(method='POST',
                                               path=path)
        headers = {'x-auth-token': 'user:tenant:admin',
                   'x-user-name': 'user-name',
                   'x-tenant-name': 'tenant-name'}
        for k, v in headers.iteritems():
            req.headers[k] = v

        req.body = jsonutils.dumps(body_normal)

        # Send request
        res = req.get_response(self.api)

        self.assertEqual(res.status_int, 400)

    def test_create_scope_length_irregular(self):
        """Test 'Create a new catalog scope'
        Test when the length of the scope is invalid.
        """

        path = '/catalogs/%s/scope/%s' % (CATALOG_ID_101, 'a' * 65)
        req = unit_test_utils.get_fake_request(method='POST',
                                               path=path)
        headers = {'x-auth-token': 'user:tenant:admin',
                   'x-user-name': 'user-name',
                   'x-tenant-name': 'tenant-name'}
        for k, v in headers.iteritems():
            req.headers[k] = v

        req.body = jsonutils.dumps(body_normal)

        # Send request
        res = req.get_response(self.api)

        self.assertEqual(res.status_int, 400)

    def test_create_lifetime_start_datetime_irregular(self):
        """Test 'Create a new catalog scope'
        Test when the lifetime_start is not datetime.
        """

        path = '/catalogs/%s/scope/%s' % (CATALOG_ID_101, SCOPE_101)
        req = unit_test_utils.get_fake_request(method='POST',
                                               path=path)
        headers = {'x-auth-token': 'user:tenant:admin',
                   'x-user-name': 'user-name',
                   'x-tenant-name': 'tenant-name'}
        for k, v in headers.iteritems():
            req.headers[k] = v

        req.body = jsonutils.dumps(body_lifetime_start_error)

        # Send request
        res = req.get_response(self.api)

        self.assertEqual(res.status_int, 400)

    def test_create_lifetime_end_datetime_irregular(self):
        """Test 'Create a new catalog scope'
        Test when the lifetime_end is not datetime.
        """

        path = '/catalogs/%s/scope/%s' % (CATALOG_ID_101, SCOPE_101)
        req = unit_test_utils.get_fake_request(method='POST',
                                               path=path)
        headers = {'x-auth-token': 'user:tenant:admin',
                   'x-user-name': 'user-name',
                   'x-tenant-name': 'tenant-name'}
        for k, v in headers.iteritems():
            req.headers[k] = v

        req.body = jsonutils.dumps(body_lifetime_end_error)

        # Send request
        res = req.get_response(self.api)

        self.assertEqual(res.status_int, 400)

    def test_create_lifetime_order_irregular(self):
        """Test 'Create a new catalog scope'
        Test when after lifetime_start is day than lifetime_end.
        """

        path = '/catalogs/%s/scope/%s' % (CATALOG_ID_101, SCOPE_101)
        req = unit_test_utils.get_fake_request(method='POST',
                                               path=path)
        headers = {'x-auth-token': 'user:tenant:admin',
                   'x-user-name': 'user-name',
                   'x-tenant-name': 'tenant-name'}
        for k, v in headers.iteritems():
            req.headers[k] = v

        req.body = jsonutils.dumps(body_lifetime_order_error)

        # Send request
        res = req.get_response(self.api)

        self.assertEqual(res.status_int, 400)

    def test_create_expansion_key1_length_irregular(self):
        """Test 'Create a new catalog scope'
        Test when the length of the expansion_key1 is invalid.
        """

        path = '/catalogs/%s/scope/%s' % (CATALOG_ID_101, SCOPE_101)
        req = unit_test_utils.get_fake_request(method='POST',
                                               path=path)
        headers = {'x-auth-token': 'user:tenant:admin',
                   'x-user-name': 'user-name',
                   'x-tenant-name': 'tenant-name'}
        for k, v in headers.iteritems():
            req.headers[k] = v

        req.body = jsonutils.dumps(body_expansion_key1_error)

        # Send request
        res = req.get_response(self.api)

        self.assertEqual(res.status_int, 400)

    def test_create_expansion_key2_length_irregular(self):
        """Test 'Create a new catalog scope'
        Test when the length of the expansion_key2 is invalid.
        """

        path = '/catalogs/%s/scope/%s' % (CATALOG_ID_101, SCOPE_101)
        req = unit_test_utils.get_fake_request(method='POST',
                                               path=path)
        headers = {'x-auth-token': 'user:tenant:admin',
                   'x-user-name': 'user-name',
                   'x-tenant-name': 'tenant-name'}
        for k, v in headers.iteritems():
            req.headers[k] = v

        req.body = jsonutils.dumps(body_expansion_key2_error)

        # Send request
        res = req.get_response(self.api)

        self.assertEqual(res.status_int, 400)

    def test_create_expansion_key3_length_irregular(self):
        """Test 'Create a new catalog scope'
        Test when the length of the expansion_key3 is invalid.
        """

        path = '/catalogs/%s/scope/%s' % (CATALOG_ID_101, SCOPE_101)
        req = unit_test_utils.get_fake_request(method='POST',
                                               path=path)
        headers = {'x-auth-token': 'user:tenant:admin',
                   'x-user-name': 'user-name',
                   'x-tenant-name': 'tenant-name'}
        for k, v in headers.iteritems():
            req.headers[k] = v

        req.body = jsonutils.dumps(body_expansion_key3_error)

        # Send request
        res = req.get_response(self.api)

        self.assertEqual(res.status_int, 400)

    def test_create_expansion_key4_length_irregular(self):
        """Test 'Create a new catalog scope'
        Test when the length of the expansion_key4 is invalid.
        """

        path = '/catalogs/%s/scope/%s' % (CATALOG_ID_101, SCOPE_101)
        req = unit_test_utils.get_fake_request(method='POST',
                                               path=path)
        headers = {'x-auth-token': 'user:tenant:admin',
                   'x-user-name': 'user-name',
                   'x-tenant-name': 'tenant-name'}
        for k, v in headers.iteritems():
            req.headers[k] = v

        req.body = jsonutils.dumps(body_expansion_key4_error)

        # Send request
        res = req.get_response(self.api)

        self.assertEqual(res.status_int, 400)

    def test_create_expansion_key5_length_irregular(self):
        """Test 'Create a new catalog scope'
        Test when the length of the expansion_key5 is invalid.
        """

        path = '/catalogs/%s/scope/%s' % (CATALOG_ID_101, SCOPE_101)
        req = unit_test_utils.get_fake_request(method='POST',
                                               path=path)
        headers = {'x-auth-token': 'user:tenant:admin',
                   'x-user-name': 'user-name',
                   'x-tenant-name': 'tenant-name'}
        for k, v in headers.iteritems():
            req.headers[k] = v

        req.body = jsonutils.dumps(body_expansion_key5_error)

        # Send request
        res = req.get_response(self.api)

        self.assertEqual(res.status_int, 400)

    def test_create_expansion_text_length_irregular(self):
        """Test 'Create a new catalog scope'
        Test when the length of the expansion_text is invalid.
        """

        path = '/catalogs/%s/scope/%s' % (CATALOG_ID_101, SCOPE_101)
        req = unit_test_utils.get_fake_request(method='POST',
                                               path=path)
        headers = {'x-auth-token': 'user:tenant:admin',
                   'x-user-name': 'user-name',
                   'x-tenant-name': 'tenant-name'}
        for k, v in headers.iteritems():
            req.headers[k] = v

        req.body = jsonutils.dumps(body_expansion_text_error)

        # Send request
        res = req.get_response(self.api)

        self.assertEqual(res.status_int, 400)

    def test_create_uri_irregular(self):
        """Test 'Create a new catalog scope'
        Test when the required parameter without.
        """

        path = '/catalogs/%s/scope/%s' % (CATALOG_ID_101, '')
        req = unit_test_utils.get_fake_request(method='POST',
                                               path=path)
        headers = {'x-auth-token': 'user:tenant:admin',
                   'x-user-name': 'user-name',
                   'x-tenant-name': 'tenant-name'}
        for k, v in headers.iteritems():
            req.headers[k] = v

        req.body = jsonutils.dumps(body_normal)

        # Send request
        res = req.get_response(self.api)

        self.assertEqual(res.status_int, 404)
