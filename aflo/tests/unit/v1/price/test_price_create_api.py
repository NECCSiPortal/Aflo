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

body01 = {
    "catalog_price": {
        "price": 10000.01,
        "lifetime_start": "2999-12-31T23:59:59.999999",
        "lifetime_end": "9999-12-31T23:59:59.999999",
        "expansions": {
            "expansion_key1": "1",
            "expansion_key2": "2",
            "expansion_key3": "3",
            "expansion_key4": "4",
            "expansion_key5": "5"
        },
        "expansions_text": {
            "expansion_text": "0"
        }
    }
}
body_price_error = {
    "catalog_price": {
        "price": "1000a",
        "lifetime_start": "2015-08-01T00:00:00.999999",
        "lifetime_end": "2015-08-02T00:00:00.999999",
        "expansions": {
            "expansion_key1": "1",
            "expansion_key2": "2",
            "expansion_key3": "3",
            "expansion_key4": "4",
            "expansion_key5": "5"
        },
        "expansions_text": {
            "expansion_text": "0"
        }
    }
}
body_lifetime_start_error = {
    "catalog_price": {
        "price": 10000,
        "lifetime_start": "2015-08-01",
        "lifetime_end": "2015-08-02T00:00:00.999999",
        "expansions": {
            "expansion_key1": "1",
            "expansion_key2": "2",
            "expansion_key3": "3",
            "expansion_key4": "4",
            "expansion_key5": "5"
        },
        "expansions_text": {
            "expansion_text": "0"
        }
    }
}
body_lifetime_end_error = {
    "catalog_price": {
        "price": 10000,
        "lifetime_start": "2015-08-01T00:00:00.999999",
        "lifetime_end": "2015-08-02T00",
        "expansions": {
            "expansion_key1": "1",
            "expansion_key2": "2",
            "expansion_key3": "3",
            "expansion_key4": "4",
            "expansion_key5": "5"
        },
        "expansions_text": {
            "expansion_text": "0"
        }
    }
}
body_expansion_key1_error = {
    "catalog_price": {
        "price": 10000,
        "lifetime_start": "2015-08-01T00:00:00.999999",
        "lifetime_end": "2015-08-02T00:00:00.999999",
        "expansions": {
            "expansion_key1": 'a' * 256,
            "expansion_key2": "2",
            "expansion_key3": "3",
            "expansion_key4": "4",
            "expansion_key5": "5"
        },
        "expansions_text": {
            "expansion_text": "0"
        }
    }
}
body_expansion_key2_error = {
    "catalog_price": {
        "price": 10000,
        "lifetime_start": "2015-08-01T00:00:00.999999",
        "lifetime_end": "2015-08-02T00:00:00.999999",
        "expansions": {
            "expansion_key1": "1",
            "expansion_key2": 'a' * 256,
            "expansion_key3": "3",
            "expansion_key4": "4",
            "expansion_key5": "5"
        },
        "expansions_text": {
            "expansion_text": "0"
        }
    }
}
body_expansion_key3_error = {
    "catalog_price": {
        "price": 10000,
        "lifetime_start": "2015-08-01T00:00:00.999999",
        "lifetime_end": "2015-08-02T00:00:00.999999",
        "expansions": {
            "expansion_key1": "1",
            "expansion_key2": "2",
            "expansion_key3": 'a' * 256,
            "expansion_key4": "4",
            "expansion_key5": "5"
        },
        "expansions_text": {
            "expansion_text": "0"
        }
    }
}
body_expansion_key4_error = {
    "catalog_price": {
        "price": 10000,
        "lifetime_start": "2015-08-01T00:00:00.999999",
        "lifetime_end": "2015-08-02T00:00:00.999999",
        "expansions": {
            "expansion_key1": "1",
            "expansion_key2": "2",
            "expansion_key3": "3",
            "expansion_key4": 'a' * 256,
            "expansion_key5": "5"
        },
        "expansions_text": {
            "expansion_text": "0"
        }
    }
}
body_expansion_key5_error = {
    "catalog_price": {
        "price": 10000,
        "lifetime_start": "2015-08-01T00:00:00.999999",
        "lifetime_end": "2015-08-02T00:00:00.999999",
        "expansions": {
            "expansion_key1": "1",
            "expansion_key2": "2",
            "expansion_key3": "3",
            "expansion_key4": "4",
            "expansion_key5": 'a' * 256
        },
        "expansions_text": {
            "expansion_text": "0"
        }
    }
}
body_expansion_text_error = {
    "catalog_price": {
        "price": 10000,
        "lifetime_start": "2015-08-01T00:00:00.999999",
        "lifetime_end": "2015-08-02T00:00:00.999999",
        "expansions": {
            "expansion_key1": "1",
            "expansion_key2": "2",
            "expansion_key3": "3",
            "expansion_key4": "4",
            "expansion_key5": "5"
        },
        "expansions_text": {
            "expansion_text": 'a' * 4001
        }
    }
}


class TestPriceCreateAPI(base.WorkflowUnitTest):
    """Do a test of 'Create a new price'"""

    def setUp(self):
        """Establish a clean test environment"""
        super(TestPriceCreateAPI, self).setUp()
        self.mapper = routes.Mapper()
        self.api = test_utils.FakeAuthMiddleware(router.API(self.mapper))

        self.context = aflo.context.RequestContext(is_admin=True)
        db_api.get_engine()
        self.destroy_fixtures()
        self.create_fixtures()
        self.serializer = wsgi.JSONResponseSerializer()

    def tearDown(self):
        """Clear the test environment"""
        super(TestPriceCreateAPI, self).tearDown()
        self.destroy_fixtures()

    def create_fixtures(self):
        super(TestPriceCreateAPI, self).create_fixtures()

    def destroy_fixtures(self):
        # Easiest to just drop the models and re-create them...
        db_models.unregister_models(db_api.get_engine())
        db_models.register_models(db_api.get_engine())

    def test_create(self):
        """Test 'Create a new price'
        """

        # Create a request data
        path = '/catalog/1/price/1'
        req = unit_test_utils.get_fake_request(method='POST',
                                               path=path)
        headers = {'x-auth-token': 'user:tenant:admin',
                   'x-user-name': 'user-name',
                   'x-tenant-name': 'tenant-name'}
        for k, v in headers.iteritems():
            req.headers[k] = v

        req.body = '{"catalog_price": { ' \
                   '    "price": "123456789.123", ' \
                   '    "lifetime_start": "2999-12-31T23:59:59.999999", ' \
                   '    "lifetime_end": "9999-12-31T23:59:59.999999", ' \
                   '    "deleted": "True", ' \
                   '    "expansions": { ' \
                   '        "expansion_key1": "expansion_key1", ' \
                   '        "expansion_key2": "expansion_key2", ' \
                   '        "expansion_key3": "expansion_key3", ' \
                   '        "expansion_key4": "expansion_key4", ' \
                   '        "expansion_key5": "expansion_key5" ' \
                   '    }, ' \
                   '    "expansions_text": ' \
                   '        {"expansion_text": "expansion_text"} ' \
                   '    } ' \
                   '} '

        # Send request
        res = req.get_response(self.api)

        # Examination of response
        self.assertEqual(res.status_int, 200)

        price = jsonutils.loads(res.body)['catalog_price']

        self.assertEqual(price['catalog_id'], '1')
        self.assertEqual(price['scope'], '1')
        self.assertIsNotNone(price['seq_no'])
        self.assertEqual(price['price'], '123456789.123')
        self.assertEqual(price['expansions']['expansion_key1'],
                         'expansion_key1')
        self.assertEqual(price['expansions']['expansion_key2'],
                         'expansion_key2')
        self.assertEqual(price['expansions']['expansion_key3'],
                         'expansion_key3')
        self.assertEqual(price['expansions']['expansion_key4'],
                         'expansion_key4')
        self.assertEqual(price['expansions']['expansion_key5'],
                         'expansion_key5')
        self.assertEqual(price['expansions_text']['expansion_text'],
                         'expansion_text')
        self.assertIsNotNone(price['created_at'])
        self.assertIsNotNone(price['updated_at'])
        self.assertIsNone(price['deleted_at'])
        self.assertEqual(price['deleted'], False)

    def test_create_no_expansion(self):
        """Test Create a new price with no expansion.
        """

        # Create a request data
        path = '/catalog/1/price/1'
        req = unit_test_utils.get_fake_request(method='POST',
                                               path=path)
        headers = {'x-auth-token': 'user:tenant:admin',
                   'x-user-name': 'user-name',
                   'x-tenant-name': 'tenant-name'}
        for k, v in headers.iteritems():
            req.headers[k] = v

        req.body = '{"catalog_price": { ' \
                   '          "price": "10000" ' \
                   '           } ' \
                   ' } '

        # Send request
        res = req.get_response(self.api)

        # Examination of response
        self.assertEqual(res.status_int, 200)

        price = jsonutils.loads(res.body)['catalog_price']

        self.assertEqual(price['catalog_id'], '1')
        self.assertEqual(price['scope'], '1')
        self.assertIsNotNone(price['seq_no'])
        self.assertEqual(price['price'], '10000')
        self.assertIsNotNone(price['expansions'])
        self.assertIsNone(price['expansions']['expansion_key1'])
        self.assertIsNone(price['expansions']['expansion_key2'])
        self.assertIsNone(price['expansions']['expansion_key3'])
        self.assertIsNone(price['expansions']['expansion_key4'])
        self.assertIsNone(price['expansions']['expansion_key5'])
        self.assertIsNotNone(price['expansions_text'])
        self.assertIsNone(price['expansions_text']['expansion_text'])
        self.assertIsNotNone(price['created_at'])
        self.assertIsNotNone(price['updated_at'])
        self.assertIsNone(price['deleted_at'])
        self.assertEqual(price['deleted'], False)

    def test_create_member_authority_irregular(self):
        """Test 'Create a new price'
        Test when it is executed by a user other than the administrator.
        """

        # Create a request data
        path = '/catalog/1/price/1'
        req = unit_test_utils.get_fake_request(method='POST',
                                               path=path)
        headers = {'x-auth-token': 'user:tenant:__member__',
                   'x-user-name': 'user-name',
                   'x-tenant-name': 'tenant-name'}
        for k, v in headers.iteritems():
            req.headers[k] = v

        req.body = '{"catalog_price": { ' \
                   '          "price": "10000", ' \
                   '          "expansions": { ' \
                   '              "expansion_key1": "expansion_key1", ' \
                   '              "expansion_key2": "expansion_key2", ' \
                   '              "expansion_key3": "expansion_key3", ' \
                   '              "expansion_key4": "expansion_key4", ' \
                   '              "expansion_key5": "expansion_key5" ' \
                   '           }, ' \
                   '           "expansions_text": ' \
                   '               {"expansion_text": "expansion_text"} ' \
                   '           } ' \
                   ' } '

        # Send request
        res = req.get_response(self.api)

        # Examination of response
        self.assertEqual(res.status_int, 403)

    def test_create_catalog_id_error(self):
        """Test 'Create a new price'
        Test with catalog_id is over length.
        """

        # Create a request data
        path = '/catalog/%s/price/1' % ('a' * 65)
        req = unit_test_utils.get_fake_request(method='POST',
                                               path=path)
        headers = {'x-auth-token': 'user:tenant:admin',
                   'x-user-name': 'user-name',
                   'x-tenant-name': 'tenant-name'}
        for k, v in headers.iteritems():
            req.headers[k] = v

        req.body = jsonutils.dumps(body01)

        # Send request
        res = req.get_response(self.api)

        # Examination of response
        self.assertEqual(res.status_int, 400)

    def test_create_scope_error(self):
        """Test 'Create a new price'
        Test with scope is over length.
        """

        # Create a request data
        path = '/catalog/1/price/%s' % ('a' * 65)
        req = unit_test_utils.get_fake_request(method='POST',
                                               path=path)
        headers = {'x-auth-token': 'user:tenant:admin',
                   'x-user-name': 'user-name',
                   'x-tenant-name': 'tenant-name'}
        for k, v in headers.iteritems():
            req.headers[k] = v

        req.body = jsonutils.dumps(body01)

        # Send request
        res = req.get_response(self.api)

        # Examination of response
        self.assertEqual(res.status_int, 400)

    def test_create_price_error(self):
        """Test 'Create a new price'
        Test with price is not int.
        """

        # Create a request data
        path = '/catalog/1/price/1'
        req = unit_test_utils.get_fake_request(method='POST',
                                               path=path)
        headers = {'x-auth-token': 'user:tenant:admin',
                   'x-user-name': 'user-name',
                   'x-tenant-name': 'tenant-name'}
        for k, v in headers.iteritems():
            req.headers[k] = v

        req.body = jsonutils.dumps(body_price_error)

        # Send request
        res = req.get_response(self.api)

        # Examination of response
        self.assertEqual(res.status_int, 400)

    def test_create_lifetime_start_error(self):
        """Test 'Create a new price'
        Test with lifetime_start is over length.
        """

        # Create a request data
        path = '/catalog/1/price/1'
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

        # Examination of response
        self.assertEqual(res.status_int, 400)

    def test_create_lifetime_end_error(self):
        """Test 'Create a new price'
        Test with lifetime_end is over length.
        """

        # Create a request data
        path = '/catalog/1/price/1'
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

        # Examination of response
        self.assertEqual(res.status_int, 400)

    def test_create_expansion_key1_error(self):
        """Test 'Create a new price'
        Test with expansion_key1 is over length.
        """

        # Create a request data
        path = '/catalog/1/price/1'
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

        # Examination of response
        self.assertEqual(res.status_int, 400)

    def test_create_expansion_key2_error(self):
        """Test 'Create a new price'
        Test with expansion_key2 is over length.
        """

        # Create a request data
        path = '/catalog/1/price/1'
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

        # Examination of response
        self.assertEqual(res.status_int, 400)

    def test_create_expansion_key3_error(self):
        """Test 'Create a new price'
        Test with expansion_key3 is over length.
        """

        # Create a request data
        path = '/catalog/1/price/1'
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

        # Examination of response
        self.assertEqual(res.status_int, 400)

    def test_create_expansion_key4_error(self):
        """Test 'Create a new price'
        Test with expansion_key4 is over length.
        """

        # Create a request data
        path = '/catalog/1/price/1'
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

        # Examination of response
        self.assertEqual(res.status_int, 400)

    def test_create_expansion_key5_error(self):
        """Test 'Create a new price'
        Test with expansion_key5 is over length.
        """

        # Create a request data
        path = '/catalog/1/price/1'
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

        # Examination of response
        self.assertEqual(res.status_int, 400)

    def test_create_expansion_text_error(self):
        """Test 'Create a new price'
        Test with expansion_text is over length.
        """

        # Create a request data
        path = '/catalog/1/price/1'
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

        # Examination of response
        self.assertEqual(res.status_int, 400)
