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

from oslo_config import cfg
from oslo_serialization import jsonutils
import routes

from aflo.api.v1 import router
from aflo.common import wsgi
import aflo.context
from aflo.db.sqlalchemy import api as db_api
from aflo.db.sqlalchemy import models as db_models
from aflo.tests.unit import base
import aflo.tests.unit.utils as unit_test_utils
from aflo.tests import utils as test_utils

CONF = cfg.CONF

body_goods_id_error = {
    "catalog_contents": {
        "goods_id": 'a' * 65,
        "goods_num": None,
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

body_goods_num_error = {
    "catalog_contents": {
        "goods_id": None,
        "goods_num": 10000,
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

body_goods_num_error_not_int = {
    "catalog_contents": {
        "goods_id": None,
        "goods_num": 'a',
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

body_expansion_key1_error = {
    "catalog_contents": {
        "goods_id": None,
        "goods_num": None,
        "expansions": {
            "expansion_key1": 'a' * 256,
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

body_expansion_key2_error = {
    "catalog_contents": {
        "goods_id": None,
        "goods_num": None,
        "expansions": {
            "expansion_key1": None,
            "expansion_key2": 'a' * 256,
            "expansion_key3": None,
            "expansion_key4": None,
            "expansion_key5": None
        },
        "expansions_text": {
            "expansion_text": None
        }
    }
}

body_expansion_key3_error = {
    "catalog_contents": {
        "goods_id": None,
        "goods_num": None,
        "expansions": {
            "expansion_key1": None,
            "expansion_key2": None,
            "expansion_key3": 'a' * 256,
            "expansion_key4": None,
            "expansion_key5": None
        },
        "expansions_text": {
            "expansion_text": None
        }
    }
}

body_expansion_key4_error = {
    "catalog_contents": {
        "goods_id": None,
        "goods_num": None,
        "expansions": {
            "expansion_key1": None,
            "expansion_key2": None,
            "expansion_key3": None,
            "expansion_key4": 'a' * 256,
            "expansion_key5": None
        },
        "expansions_text": {
            "expansion_text": None
        }
    }
}

body_expansion_key5_error = {
    "catalog_contents": {
        "goods_id": None,
        "goods_num": None,
        "expansions": {
            "expansion_key1": None,
            "expansion_key2": None,
            "expansion_key3": None,
            "expansion_key4": None,
            "expansion_key5": 'a' * 256
        },
        "expansions_text": {
            "expansion_text": None
        }
    }
}

body_expansion_text_error = {
    "catalog_contents": {
        "goods_id": None,
        "goods_num": None,
        "expansions": {
            "expansion_key1": None,
            "expansion_key2": None,
            "expansion_key3": None,
            "expansion_key4": None,
            "expansion_key5": None
        },
        "expansions_text": {
            "expansion_text": 'a' * 4001
        }
    }
}


class TestCatalogContentsCreateAPI(base.WorkflowUnitTest):
    """Do a test of 'Create a new catalog contents'"""

    def setUp(self):
        """Establish a clean test environment"""
        super(TestCatalogContentsCreateAPI, self).setUp()
        self.mapper = routes.Mapper()
        self.api = test_utils.FakeAuthMiddleware(router.API(self.mapper))

        self.context = aflo.context.RequestContext(is_admin=True)
        db_api.get_engine()
        self.destroy_fixtures()
        self.create_fixtures()
        self.serializer = wsgi.JSONResponseSerializer()

    def tearDown(self):
        """Clear the test environment"""
        super(TestCatalogContentsCreateAPI, self).tearDown()
        self.destroy_fixtures()

    def create_fixtures(self):
        super(TestCatalogContentsCreateAPI, self).create_fixtures()

    def destroy_fixtures(self):
        # Easiest to just drop the models and re-create them...
        db_models.unregister_models(db_api.get_engine())
        db_models.register_models(db_api.get_engine())

    def test_create(self):
        """Do a test of 'Create a new catalog contents'
        """

        # Create a request data
        path = '/catalog/1/contents'
        req = unit_test_utils.get_fake_request(method='POST',
                                               path=path)
        headers = {'x-auth-token': 'user:tenant:admin',
                   'x-user-name': 'user-name',
                   'x-tenant-name': 'tenant-name'}
        for k, v in headers.iteritems():
            req.headers[k] = v

        req.body = '{"catalog_contents":{ ' \
                   '          "goods_id": "goods_id_101", ' \
                   '          "goods_num": 1, ' \
                   '          "deleted": "True", ' \
                   '          "expansions": { ' \
                   '              "expansion_key1": "expansion_key1", ' \
                   '              "expansion_key2": "expansion_key2", ' \
                   '              "expansion_key3": "expansion_key3", ' \
                   '              "expansion_key4": "expansion_key4", ' \
                   '              "expansion_key5": "expansion_key5" ' \
                   '           }, ' \
                   '           "expansions_text": ' \
                   '               {"expansion_text": "expansion_text"} }}'

        # Send request
        res = req.get_response(self.api)

        # Examination of response
        self.assertEqual(res.status_int, 200)

        catalog_contents = jsonutils.loads(res.body)['catalog_contents']

        self.assertIsNotNone(catalog_contents['seq_no'])
        self.assertEqual(catalog_contents['goods_id'], 'goods_id_101')
        self.assertEqual(catalog_contents['goods_num'], 1)
        self.assertEqual(catalog_contents['expansions']['expansion_key1'],
                         'expansion_key1')
        self.assertEqual(catalog_contents['expansions']['expansion_key2'],
                         'expansion_key2')
        self.assertEqual(catalog_contents['expansions']['expansion_key3'],
                         'expansion_key3')
        self.assertEqual(catalog_contents['expansions']['expansion_key4'],
                         'expansion_key4')
        self.assertEqual(catalog_contents['expansions']['expansion_key5'],
                         'expansion_key5')
        self.assertEqual(catalog_contents['expansions_text']['expansion_text'],
                         'expansion_text')
        self.assertIsNotNone(catalog_contents['created_at'])
        self.assertIsNotNone(catalog_contents['updated_at'])
        self.assertIsNone(catalog_contents['deleted_at'])
        self.assertEqual(catalog_contents['deleted'], False)

    def test_create_catalog_id_error(self):
        """Test create a new catalog contents for catalog_id error."""

        # Create a request data
        path = '/catalog/%s/contents' % ('a' * 65)
        req = unit_test_utils.get_fake_request(method='POST',
                                               path=path)
        headers = {'x-auth-token': 'user:tenant:admin',
                   'x-user-name': 'user-name',
                   'x-tenant-name': 'tenant-name'}
        for k, v in headers.iteritems():
            req.headers[k] = v

        req.body = '{"catalog_contents":{ ' \
                   '          "goods_id": "goods_id_101", ' \
                   '          "goods_num": 1, ' \
                   '          "deleted": "True", ' \
                   '          "expansions": { ' \
                   '              "expansion_key1": "expansion_key1", ' \
                   '              "expansion_key2": "expansion_key2", ' \
                   '              "expansion_key3": "expansion_key3", ' \
                   '              "expansion_key4": "expansion_key4", ' \
                   '              "expansion_key5": "expansion_key5" ' \
                   '           }, ' \
                   '           "expansions_text": ' \
                   '               {"expansion_text": "expansion_text"} }}'

        res = req.get_response(self.api)
        self.assertEqual(res.status_int, 400)

    def test_create_goods_id_error(self):
        """Test create a new catalog contents for goods_id error."""

        # Create a request data
        path = '/catalog/1/contents'
        req = unit_test_utils.get_fake_request(method='POST',
                                               path=path)
        headers = {'x-auth-token': 'user:tenant:admin',
                   'x-user-name': 'user-name',
                   'x-tenant-name': 'tenant-name'}
        for k, v in headers.iteritems():
            req.headers[k] = v

        req.body = jsonutils.dumps(body_goods_id_error)

        res = req.get_response(self.api)
        self.assertEqual(res.status_int, 400)

    def test_create_goods_num_error(self):
        """Test create a new catalog contents for goods_num error."""

        # Create a request data
        path = '/catalog/1/contents'
        req = unit_test_utils.get_fake_request(method='POST',
                                               path=path)
        headers = {'x-auth-token': 'user:tenant:admin',
                   'x-user-name': 'user-name',
                   'x-tenant-name': 'tenant-name'}
        for k, v in headers.iteritems():
            req.headers[k] = v

        req.body = jsonutils.dumps(body_goods_num_error)

        res = req.get_response(self.api)
        self.assertEqual(res.status_int, 400)

    def test_create_goods_num_error_not_int(self):
        """Test create a new catalog contents for goods_num error."""

        # Create a request data
        path = '/catalog/1/contents'
        req = unit_test_utils.get_fake_request(method='POST',
                                               path=path)
        headers = {'x-auth-token': 'user:tenant:admin',
                   'x-user-name': 'user-name',
                   'x-tenant-name': 'tenant-name'}
        for k, v in headers.iteritems():
            req.headers[k] = v

        req.body = jsonutils.dumps(body_goods_num_error_not_int)

        res = req.get_response(self.api)
        self.assertEqual(res.status_int, 400)

    def test_create_expansion_key1_error(self):
        """Test create a new catalog contents for expansion_key1 error."""

        # Create a request data
        path = '/catalog/1/contents'
        req = unit_test_utils.get_fake_request(method='POST',
                                               path=path)
        headers = {'x-auth-token': 'user:tenant:admin',
                   'x-user-name': 'user-name',
                   'x-tenant-name': 'tenant-name'}
        for k, v in headers.iteritems():
            req.headers[k] = v

        req.body = jsonutils.dumps(body_expansion_key1_error)

        res = req.get_response(self.api)
        self.assertEqual(res.status_int, 400)

    def test_create_expansion_key2_error(self):
        """Test create a new catalog contents for expansion_key2 error."""

        # Create a request data
        path = '/catalog/1/contents'
        req = unit_test_utils.get_fake_request(method='POST',
                                               path=path)
        headers = {'x-auth-token': 'user:tenant:admin',
                   'x-user-name': 'user-name',
                   'x-tenant-name': 'tenant-name'}
        for k, v in headers.iteritems():
            req.headers[k] = v

        req.body = jsonutils.dumps(body_expansion_key2_error)

        res = req.get_response(self.api)
        self.assertEqual(res.status_int, 400)

    def test_create_expansion_key3_error(self):
        """Test create a new catalog contents for expansion_key3 error."""

        # Create a request data
        path = '/catalog/1/contents'
        req = unit_test_utils.get_fake_request(method='POST',
                                               path=path)
        headers = {'x-auth-token': 'user:tenant:admin',
                   'x-user-name': 'user-name',
                   'x-tenant-name': 'tenant-name'}
        for k, v in headers.iteritems():
            req.headers[k] = v

        req.body = jsonutils.dumps(body_expansion_key3_error)

        res = req.get_response(self.api)
        self.assertEqual(res.status_int, 400)

    def test_create_expansion_key4_error(self):
        """Test create a new catalog contents for expansion_key4 error."""

        # Create a request data
        path = '/catalog/1/contents'
        req = unit_test_utils.get_fake_request(method='POST',
                                               path=path)
        headers = {'x-auth-token': 'user:tenant:admin',
                   'x-user-name': 'user-name',
                   'x-tenant-name': 'tenant-name'}
        for k, v in headers.iteritems():
            req.headers[k] = v

        req.body = jsonutils.dumps(body_expansion_key4_error)

        res = req.get_response(self.api)
        self.assertEqual(res.status_int, 400)

    def test_create_expansion_key5_error(self):
        """Test create a new catalog contents for expansion_key5 error."""

        # Create a request data
        path = '/catalog/1/contents'
        req = unit_test_utils.get_fake_request(method='POST',
                                               path=path)
        headers = {'x-auth-token': 'user:tenant:admin',
                   'x-user-name': 'user-name',
                   'x-tenant-name': 'tenant-name'}
        for k, v in headers.iteritems():
            req.headers[k] = v

        req.body = jsonutils.dumps(body_expansion_key5_error)

        res = req.get_response(self.api)
        self.assertEqual(res.status_int, 400)

    def test_create_expansion_text_error(self):
        """Test create a new catalog contents for expansion_text error."""

        # Create a request data
        path = '/catalog/1/contents'
        req = unit_test_utils.get_fake_request(method='POST',
                                               path=path)
        headers = {'x-auth-token': 'user:tenant:admin',
                   'x-user-name': 'user-name',
                   'x-tenant-name': 'tenant-name'}
        for k, v in headers.iteritems():
            req.headers[k] = v

        req.body = jsonutils.dumps(body_expansion_text_error)

        res = req.get_response(self.api)
        self.assertEqual(res.status_int, 400)
