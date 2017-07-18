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

from datetime import datetime
from oslo_config import cfg
from oslo_serialization import jsonutils
import routes

from aflo.api.v1 import router
from aflo.common import wsgi
import aflo.context
from aflo.db.sqlalchemy import api as db_api
from aflo.db.sqlalchemy.models import Price
from aflo.tests.unit import base
import aflo.tests.unit.utils as unit_test_utils
from aflo.tests import utils as test_utils

CONF = cfg.CONF

CT_UUID1 = 'ea0a4146-fd07-414b-aa5e-dedbeef00001'
CT_UUID2 = 'ea0a4146-fd07-414b-aa5e-dedbeef00002'
CT_UUID3 = 'ea0a4146-fd07-414b-aa5e-dedbeef00003'
CT_UUID4 = 'ea0a4146-fd07-414b-aa5e-dedbeef00004'

SCOPE1 = 'ea0a4146-fd07-414b-aa5e-dedbeef01001'
SCOPE2 = 'ea0a4146-fd07-414b-aa5e-dedbeef01002'
SCOPE3 = 'ea0a4146-fd07-414b-aa5e-dedbeef01003'
SCOPE4 = 'ea0a4146-fd07-414b-aa5e-dedbeef01004'

body01 = {
    "catalog_price": {
        "price": 10000.01,
        'deleted': True,
        "lifetime_start": datetime(2015, 8, 1, 0, 0, 0, 0),
        "lifetime_end": datetime(2015, 8, 2, 0, 0, 0, 0),
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
body02 = {
    "catalog_price": {
        "price": 10000.00
    }
}
body03 = {
    "catalog_price": {}
}
body04 = {
    "catalog_price": {
        "price": None,
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
body_price_error = {
    "catalog_price": {
        "price": "1000a",
        "lifetime_start": "2015-08-01T00:00:00",
        "lifetime_end": "2015-08-02T00:00:00",
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
        "lifetime_end": "2015-08-02T00:00:00",
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
        "lifetime_start": "2015-08-01T00:00:00",
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
        "lifetime_start": "2015-08-01T00:00:00",
        "lifetime_end": "2015-08-02T00:00:00",
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
        "lifetime_start": "2015-08-01T00:00:00",
        "lifetime_end": "2015-08-02T00:00:00",
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
        "lifetime_start": "2015-08-01T00:00:00",
        "lifetime_end": "2015-08-02T00:00:00",
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
        "lifetime_start": "2015-08-01T00:00:00",
        "lifetime_end": "2015-08-02T00:00:00",
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
        "lifetime_start": "2015-08-01T00:00:00",
        "lifetime_end": "2015-08-02T00:00:00",
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
        "lifetime_start": "2015-08-01T00:00:00",
        "lifetime_end": "2015-08-02T00:00:00",
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


class TestPriceShowAPI(base.WorkflowUnitTest):
    """Test 'Get the details of the Price'"""

    def setUp(self):
        """Establish a clean test environment"""
        super(TestPriceShowAPI, self).setUp()
        self.mapper = routes.Mapper()
        self.api = test_utils.FakeAuthMiddleware(router.API(self.mapper))

        self.context = aflo.context.RequestContext(is_admin=True)
        db_api.get_engine()
        self.destroy_fixtures()
        self.create_fixtures()
        self.serializer = wsgi.JSONResponseSerializer()

    def tearDown(self):
        """Clear the test environment"""
        super(TestPriceShowAPI, self).tearDown()
        self.destroy_fixtures()

    def create_fixtures(self):
        Price(catalog_id=CT_UUID1,
              scope=SCOPE1,
              seq_no='1',
              price=100,
              lifetime_start=datetime(2015, 7, 5, 0, 0, 0, 0),
              lifetime_end=datetime(2015, 7, 6, 0, 0, 0, 0),
              created_at=datetime.utcnow(),
              updated_at=None,
              deleted_at=None,
              deleted=False,
              expansion_key1='expansion_key1',
              expansion_key2='expansion_key2',
              expansion_key3='expansion_key3',
              expansion_key4='expansion_key4',
              expansion_key5='expansion_key5',
              expansion_text='expansion_text'
              ).save(db_api.get_session())
        Price(catalog_id=CT_UUID1,
              scope=SCOPE2,
              seq_no='1',
              price=100.0,
              lifetime_start=datetime(2015, 7, 5, 0, 0, 0, 0),
              lifetime_end=datetime(2015, 7, 6, 0, 0, 0, 0),
              created_at=datetime.utcnow(),
              updated_at=None,
              deleted_at=None,
              deleted=False,
              expansion_key1='expansion_key1',
              expansion_key2='expansion_key2',
              expansion_key3='expansion_key3',
              expansion_key4='expansion_key4',
              expansion_key5='expansion_key5',
              expansion_text='expansion_text'
              ).save(db_api.get_session())
        Price(catalog_id=CT_UUID1,
              scope=SCOPE1,
              seq_no='2',
              price=100.1,
              lifetime_start=datetime(2015, 7, 5, 0, 0, 0, 0),
              lifetime_end=datetime(2015, 7, 6, 0, 0, 0, 0),
              created_at=datetime.utcnow(),
              updated_at=None,
              deleted_at=None,
              deleted=False,
              expansion_key1='expansion_key1',
              expansion_key2='expansion_key2',
              expansion_key3='expansion_key3',
              expansion_key4='expansion_key4',
              expansion_key5='expansion_key5',
              expansion_text='expansion_text'
              ).save(db_api.get_session())
        Price(catalog_id=CT_UUID2,
              scope=SCOPE1,
              seq_no='1',
              price=100.01,
              lifetime_start=datetime(2015, 7, 5, 0, 0, 0, 0),
              lifetime_end=datetime(2015, 7, 6, 0, 0, 0, 0),
              created_at=datetime.utcnow(),
              updated_at=None,
              deleted_at=None,
              deleted=False,
              expansion_key1='expansion_key1',
              expansion_key2='expansion_key2',
              expansion_key3='expansion_key3',
              expansion_key4='expansion_key4',
              expansion_key5='expansion_key5',
              expansion_text='expansion_text'
              ).save(db_api.get_session())
        Price(catalog_id=CT_UUID2,
              scope=SCOPE2,
              seq_no='2',
              price=100.001,
              lifetime_start=datetime(2015, 7, 5, 0, 0, 0, 0),
              lifetime_end=datetime(2015, 7, 6, 0, 0, 0, 0),
              created_at=datetime.utcnow(),
              updated_at=None,
              deleted_at=None,
              deleted=True,
              expansion_key1='expansion_key1',
              expansion_key2='expansion_key2',
              expansion_key3='expansion_key3',
              expansion_key4='expansion_key4',
              expansion_key5='expansion_key5',
              expansion_text='expansion_text'
              ).save(db_api.get_session())

    def test_price_update_api(self):
        """Test 'Update of price'
        Test with all parameters.
        """
        # Create a request data
        path = '/catalog/%s/price/%s/seq/%s' \
               % (CT_UUID1, SCOPE1, '1')
        req = unit_test_utils.get_fake_request(method='PATCH',
                                               path=path)
        headers = {'x-auth-token': 'user:tenant:admin'}
        for k, v in headers.iteritems():
            req.headers[k] = v

        req.body = jsonutils.dumps(body01)

        # Send request
        res = req.get_response(self.api)

        # Examination of response
        self.assertEqual(res.status_int, 200)

        price = jsonutils.loads(res.body)['catalog_price']
        self.assertEqual(price['catalog_id'], CT_UUID1)
        self.assertEqual(price['scope'], SCOPE1)
        self.assertEqual(price['seq_no'], '1')
        self.assertEqual(price['price'], '10000.01')
        lifetime_start = datetime.strptime(price['lifetime_start'],
                                           '%Y-%m-%dT%H:%M:%S.%f')
        self.assertEqual(lifetime_start, datetime(2015, 8, 1, 0, 0, 0, 0))
        lifetime_end = datetime.strptime(price['lifetime_end'],
                                         '%Y-%m-%dT%H:%M:%S.%f')
        self.assertEqual(lifetime_end, datetime(2015, 8, 2, 0, 0, 0, 0))
        self.assertEqual(price['expansions']['expansion_key1'], '1')
        self.assertEqual(price['expansions']['expansion_key2'], '2')
        self.assertEqual(price['expansions']['expansion_key3'], '3')
        self.assertEqual(price['expansions']['expansion_key4'], '4')
        self.assertEqual(price['expansions']['expansion_key5'], '5')
        self.assertEqual(price['expansions_text']['expansion_text'], '0')
        self.assertIsNotNone(price['created_at'])
        self.assertIsNotNone(price['updated_at'])
        self.assertIsNone(price['deleted_at'])
        self.assertEqual(price['deleted'], False)

    def test_price_update_no_auth_irregular(self):
        """Test 'Update of price'
        Test cases run unauthorized.
        """
        # Create a request data
        path = '/catalog/%s/price/%s/seq/%s' \
               % (CT_UUID1, SCOPE1, '1')
        req = unit_test_utils.get_fake_request(method='PATCH',
                                               path=path)
        headers = {'x-auth-token': 'user:tenant:no_auth'}
        for k, v in headers.iteritems():
            req.headers[k] = v

        req.body = jsonutils.dumps(body02)

        # Send request
        res = req.get_response(self.api)

        # Examination of response
        self.assertEqual(res.status_int, 403)

    def test_price_update_no_keyword(self):
        """Test 'Update of price'
        Test the operation of all keyword without.
        """
        # Create a request data
        path = '/catalog/%s/price/%s/seq/%s' \
               % (CT_UUID1, SCOPE1, '1')
        req = unit_test_utils.get_fake_request(method='PATCH',
                                               path=path)
        headers = {'x-auth-token': 'user:tenant:admin'}
        for k, v in headers.iteritems():
            req.headers[k] = v

        req.body = jsonutils.dumps(body03)

        # Send request
        res = req.get_response(self.api)

        # Examination of response
        self.assertEqual(res.status_int, 200)

        price = jsonutils.loads(res.body)['catalog_price']
        self.assertEqual(price['catalog_id'], CT_UUID1)
        self.assertEqual(price['scope'], SCOPE1)
        self.assertEqual(price['seq_no'], '1')
        self.assertEqual(price['price'], '100.000')
        lifetime_start = datetime.strptime(price['lifetime_start'],
                                           '%Y-%m-%dT%H:%M:%S.%f')
        self.assertEqual(lifetime_start, datetime(2015, 7, 5, 0, 0, 0, 0))
        lifetime_end = datetime.strptime(price['lifetime_end'],
                                         '%Y-%m-%dT%H:%M:%S.%f')
        self.assertEqual(lifetime_end, datetime(2015, 7, 6, 0, 0, 0, 0))
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

    def test_price_update_none_value(self):
        """Test 'Update of price'
        Test the operation of the parameter value without.
        """
        # Create a request data
        path = '/catalog/%s/price/%s/seq/%s' \
               % (CT_UUID1, SCOPE1, '1')
        req = unit_test_utils.get_fake_request(method='PATCH',
                                               path=path)
        headers = {'x-auth-token': 'user:tenant:admin'}
        for k, v in headers.iteritems():
            req.headers[k] = v

        req.body = jsonutils.dumps(body04)

        # Send request
        res = req.get_response(self.api)

        # Examination of response
        self.assertEqual(res.status_int, 400)

    def test_price_update_catalog_id_error(self):
        """Test 'Update of price'
        Test with catalog_id is over length.
        """
        # Create a request data
        path = '/catalog/%s/price/%s/seq/%s' \
               % ('a' * 65, SCOPE1, '1')
        req = unit_test_utils.get_fake_request(method='PATCH',
                                               path=path)
        headers = {'x-auth-token': 'user:tenant:admin'}
        for k, v in headers.iteritems():
            req.headers[k] = v

        req.body = jsonutils.dumps(body01)

        # Send request
        res = req.get_response(self.api)

        # Examination of response
        self.assertEqual(res.status_int, 400)

    def test_price_update_scope_error(self):
        """Test 'Update of price'
        Test with scope is over length.
        """
        # Create a request data
        path = '/catalog/%s/price/%s/seq/%s' \
               % (CT_UUID1, 'a' * 65, '1')
        req = unit_test_utils.get_fake_request(method='PATCH',
                                               path=path)
        headers = {'x-auth-token': 'user:tenant:admin'}
        for k, v in headers.iteritems():
            req.headers[k] = v

        req.body = jsonutils.dumps(body01)

        # Send request
        res = req.get_response(self.api)

        # Examination of response
        self.assertEqual(res.status_int, 400)

    def test_price_update_seq_no_error(self):
        """Test 'Update of price'
        Test with seq_no is over length.
        """
        # Create a request data
        path = '/catalog/%s/price/%s/seq/%s' \
               % (CT_UUID1, SCOPE1, 'a' * 65)
        req = unit_test_utils.get_fake_request(method='PATCH',
                                               path=path)
        headers = {'x-auth-token': 'user:tenant:admin'}
        for k, v in headers.iteritems():
            req.headers[k] = v

        req.body = jsonutils.dumps(body01)

        # Send request
        res = req.get_response(self.api)

        # Examination of response
        self.assertEqual(res.status_int, 400)

    def test_price_update_price_error(self):
        """Test 'Update of price'
        Test of price parameter is error.
        """
        # Create a request data
        path = '/catalog/%s/price/%s/seq/%s' \
               % (CT_UUID1, SCOPE1, '1')
        req = unit_test_utils.get_fake_request(method='PATCH',
                                               path=path)
        headers = {'x-auth-token': 'user:tenant:admin'}
        for k, v in headers.iteritems():
            req.headers[k] = v

        req.body = jsonutils.dumps(body_price_error)

        # Send request
        res = req.get_response(self.api)

        # Examination of response
        self.assertEqual(res.status_int, 400)

    def test_price_update_lifetime_start_error(self):
        """Test 'Update of price'
        Test of lifetime_start parameter is error.
        """
        # Create a request data
        path = '/catalog/%s/price/%s/seq/%s' \
               % (CT_UUID1, SCOPE1, '1')
        req = unit_test_utils.get_fake_request(method='PATCH',
                                               path=path)
        headers = {'x-auth-token': 'user:tenant:admin'}
        for k, v in headers.iteritems():
            req.headers[k] = v

        req.body = jsonutils.dumps(body_lifetime_start_error)

        # Send request
        res = req.get_response(self.api)

        # Examination of response
        self.assertEqual(res.status_int, 400)

    def test_price_update_lifetime_end_error(self):
        """Test 'Update of price'
        Test of lifetime_end parameter is error.
        """
        # Create a request data
        path = '/catalog/%s/price/%s/seq/%s' \
               % (CT_UUID1, SCOPE1, '1')
        req = unit_test_utils.get_fake_request(method='PATCH',
                                               path=path)
        headers = {'x-auth-token': 'user:tenant:admin'}
        for k, v in headers.iteritems():
            req.headers[k] = v

        req.body = jsonutils.dumps(body_lifetime_end_error)

        # Send request
        res = req.get_response(self.api)

        # Examination of response
        self.assertEqual(res.status_int, 400)

    def test_price_update_expansion_key1_error(self):
        """Test 'Update of price'
        Test of expansion_key1 parameter is error.
        """
        # Create a request data
        path = '/catalog/%s/price/%s/seq/%s' \
               % (CT_UUID1, SCOPE1, '1')
        req = unit_test_utils.get_fake_request(method='PATCH',
                                               path=path)
        headers = {'x-auth-token': 'user:tenant:admin'}
        for k, v in headers.iteritems():
            req.headers[k] = v

        req.body = jsonutils.dumps(body_expansion_key1_error)

        # Send request
        res = req.get_response(self.api)

        # Examination of response
        self.assertEqual(res.status_int, 400)

    def test_price_update_expansion_key2_error(self):
        """Test 'Update of price'
        Test of expansion_key2 parameter is error.
        """
        # Create a request data
        path = '/catalog/%s/price/%s/seq/%s' \
               % (CT_UUID1, SCOPE1, '1')
        req = unit_test_utils.get_fake_request(method='PATCH',
                                               path=path)
        headers = {'x-auth-token': 'user:tenant:admin'}
        for k, v in headers.iteritems():
            req.headers[k] = v

        req.body = jsonutils.dumps(body_expansion_key2_error)

        # Send request
        res = req.get_response(self.api)

        # Examination of response
        self.assertEqual(res.status_int, 400)

    def test_price_update_expansion_key3_error(self):
        """Test 'Update of price'
        Test of expansion_key3 parameter is error.
        """
        # Create a request data
        path = '/catalog/%s/price/%s/seq/%s' \
               % (CT_UUID1, SCOPE1, '1')
        req = unit_test_utils.get_fake_request(method='PATCH',
                                               path=path)
        headers = {'x-auth-token': 'user:tenant:admin'}
        for k, v in headers.iteritems():
            req.headers[k] = v

        req.body = jsonutils.dumps(body_expansion_key3_error)

        # Send request
        res = req.get_response(self.api)

        # Examination of response
        self.assertEqual(res.status_int, 400)

    def test_price_update_expansion_key4_error(self):
        """Test 'Update of price'
        Test of expansion_key4 parameter is error.
        """
        # Create a request data
        path = '/catalog/%s/price/%s/seq/%s' \
               % (CT_UUID1, SCOPE1, '1')
        req = unit_test_utils.get_fake_request(method='PATCH',
                                               path=path)
        headers = {'x-auth-token': 'user:tenant:admin'}
        for k, v in headers.iteritems():
            req.headers[k] = v

        req.body = jsonutils.dumps(body_expansion_key4_error)

        # Send request
        res = req.get_response(self.api)

        # Examination of response
        self.assertEqual(res.status_int, 400)

    def test_price_update_expansion_key5_error(self):
        """Test 'Update of price'
        Test of expansion_key5 parameter is error.
        """
        # Create a request data
        path = '/catalog/%s/price/%s/seq/%s' \
               % (CT_UUID1, SCOPE1, '1')
        req = unit_test_utils.get_fake_request(method='PATCH',
                                               path=path)
        headers = {'x-auth-token': 'user:tenant:admin'}
        for k, v in headers.iteritems():
            req.headers[k] = v

        req.body = jsonutils.dumps(body_expansion_key5_error)

        # Send request
        res = req.get_response(self.api)

        # Examination of response
        self.assertEqual(res.status_int, 400)

    def test_price_update_expansion_text_error(self):
        """Test 'Update of price'
        Test of expansion_text parameter is error.
        """
        # Create a request data
        path = '/catalog/%s/price/%s/seq/%s' \
               % (CT_UUID1, SCOPE1, '1')
        req = unit_test_utils.get_fake_request(method='PATCH',
                                               path=path)
        headers = {'x-auth-token': 'user:tenant:admin'}
        for k, v in headers.iteritems():
            req.headers[k] = v

        req.body = jsonutils.dumps(body_expansion_text_error)

        # Send request
        res = req.get_response(self.api)

        # Examination of response
        self.assertEqual(res.status_int, 400)

    def test_update_api_nodata_irregular(self):
        """Test 'Update of price'
        Test of nonexistent data update.
        """
        # Create a request data
        path = '/catalog/%s/price/%s/seq/%s' \
               % (CT_UUID3, SCOPE1, '1')
        req = unit_test_utils.get_fake_request(method='PATCH',
                                               path=path)
        headers = {'x-auth-token': 'user:tenant:admin'}
        for k, v in headers.iteritems():
            req.headers[k] = v

        req.body = jsonutils.dumps(body01)

        # Send request
        res = req.get_response(self.api)

        # Examination of response
        self.assertEqual(res.status_int, 404)
