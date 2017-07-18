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
from aflo.db.sqlalchemy import models as db_models
from aflo.db.sqlalchemy.models import Price
from aflo.tests.unit import base
import aflo.tests.unit.utils as unit_test_utils
from aflo.tests import utils as test_utils

CONF = cfg.CONF

CT_UUID1 = 'ea0a4146-fd07-414b-aa5e-dedbeef00001'
CT_UUID2 = 'ea0a4146-fd07-414b-aa5e-dedbeef00002'
CT_UUID3 = 'ea0a4146-fd07-414b-aa5e-dedbeef00003'
CT_UUID4 = 'ea0a4146-fd07-414b-aa5e-dedbeef00004'
CT_UUID5 = 'ea0a4146-fd07-414b-aa5e-dedbeef00005'

SCOPE1 = 'ea0a4146-fd07-414b-aa5e-dedbeef01001'
SCOPE2 = 'ea0a4146-fd07-414b-aa5e-dedbeef01002'
SCOPE3 = 'ea0a4146-fd07-414b-aa5e-dedbeef01003'
SCOPE4 = 'ea0a4146-fd07-414b-aa5e-dedbeef01004'
SCOPE5 = 'ea0a4146-fd07-414b-aa5e-dedbeef01005'

SEQ_NO1 = '101'
SEQ_NO2 = '102'
SEQ_NO3 = '103'
SEQ_NO4 = '104'
SEQ_NO5 = '105'


class TestCatalogPriceShowAPI(base.WorkflowUnitTest):
    """Do a test of 'Get the details of the Catalog'"""

    def setUp(self):
        """Establish a clean test environment"""
        super(TestCatalogPriceShowAPI, self).setUp()
        self.mapper = routes.Mapper()
        self.api = test_utils.FakeAuthMiddleware(router.API(self.mapper))

        self.context = aflo.context.RequestContext(is_admin=True)
        db_api.get_engine()
        self.destroy_fixtures()
        self.create_fixtures()
        self.serializer = wsgi.JSONResponseSerializer()

    def tearDown(self):
        """Clear the test environment"""
        super(TestCatalogPriceShowAPI, self).tearDown()
        self.destroy_fixtures()

    def create_fixtures(self):
        Price(catalog_id=CT_UUID1,
              scope=SCOPE1,
              seq_no=SEQ_NO1,
              price=100,
              lifetime_start=datetime(2015, 1, 10),
              lifetime_end=datetime(2015, 1, 20),
              created_at=datetime.utcnow(),
              updated_at=None,
              deleted_at=None,
              deleted=False,
              expansion_key1='1',
              expansion_key2='1',
              expansion_key3='1',
              expansion_key4='1',
              expansion_key5='1',
              expansion_text='expansion_text'
              ).save(db_api.get_session())
        Price(catalog_id=CT_UUID1,
              scope=SCOPE1,
              seq_no=SEQ_NO2,
              price=100,
              lifetime_start=datetime(2015, 1, 10),
              lifetime_end=datetime(2015, 1, 20),
              created_at=datetime.utcnow(),
              updated_at=None,
              deleted_at=None,
              deleted=False,
              expansion_key1='1',
              expansion_key2='1',
              expansion_key3='1',
              expansion_key4='1',
              expansion_key5='1',
              expansion_text='expansion_text'
              ).save(db_api.get_session())
        Price(catalog_id=CT_UUID1,
              scope=SCOPE2,
              seq_no=SEQ_NO1,
              price=100,
              lifetime_start=datetime(2015, 1, 10),
              lifetime_end=datetime(2015, 1, 20),
              created_at=datetime.utcnow(),
              updated_at=None,
              deleted_at=None,
              deleted=False,
              expansion_key1='1',
              expansion_key2='2',
              expansion_key3='3',
              expansion_key4='4',
              expansion_key5='5',
              expansion_text='expansion_text'
              ).save(db_api.get_session())
        Price(catalog_id=CT_UUID1,
              scope=SCOPE2,
              seq_no=SEQ_NO2,
              price=100,
              lifetime_start=datetime(2015, 1, 10),
              lifetime_end=datetime(2015, 1, 20),
              created_at=datetime.utcnow(),
              updated_at=None,
              deleted_at=None,
              deleted=False,
              expansion_key1='1',
              expansion_key2=None,
              expansion_key3=None,
              expansion_key4=None,
              expansion_key5=None,
              expansion_text='expansion_text'
              ).save(db_api.get_session())
        Price(catalog_id=CT_UUID2,
              scope=SCOPE1,
              seq_no=SEQ_NO1,
              price=100,
              lifetime_start=datetime(2015, 1, 10),
              lifetime_end=datetime(2015, 1, 20),
              created_at=datetime.utcnow(),
              updated_at=None,
              deleted_at=None,
              deleted=False,
              expansion_key1=None,
              expansion_key2=None,
              expansion_key3=None,
              expansion_key4=None,
              expansion_key5=None,
              expansion_text=None
              ).save(db_api.get_session())
        Price(catalog_id=CT_UUID2,
              scope=SCOPE1,
              seq_no=SEQ_NO2,
              price=100,
              lifetime_start=datetime(2015, 1, 10),
              lifetime_end=datetime(2015, 1, 20),
              created_at=datetime.utcnow(),
              updated_at=None,
              deleted_at=None,
              deleted=False,
              expansion_key1='1',
              expansion_key2='1',
              expansion_key3='1',
              expansion_key4='1',
              expansion_key5='1',
              expansion_text='expansion_text'
              ).save(db_api.get_session())
        Price(catalog_id=CT_UUID3,
              scope=SCOPE3,
              seq_no=SEQ_NO3,
              price=100,
              lifetime_start=datetime(2015, 1, 10),
              lifetime_end=datetime(2015, 1, 20),
              created_at=datetime.utcnow(),
              updated_at=None,
              deleted_at=None,
              deleted=False,
              expansion_key1='!"#$%&()=~|`{+*}<>?_',
              expansion_key2='!"#$%&()=~|`{+*}<>?_',
              expansion_key3='!"#$%&()=~|`{+*}<>?_',
              expansion_key4='!"#$%&()=~|`{+*}<>?_',
              expansion_key5='!"#$%&()=~|`{+*}<>?_',
              expansion_text='!"#$%&()=~|`{+*}<>?_'
              ).save(db_api.get_session())

    def destroy_fixtures(self):
        # Easiest to just drop the models and re-create them...
        db_models.unregister_models(db_api.get_engine())
        db_models.register_models(db_api.get_engine())

    def test_show(self):
        """Test 'Get of catalog price'
        Test the operation of default.
        """
        path = '/catalog/%s/price/%s/seq/%s' % (CT_UUID1, SCOPE1, SEQ_NO1)
        req = unit_test_utils.get_fake_request(method='GET',
                                               path=path)

        headers = {'x-auth-token': 'user:tenant:admin'}
        for k, v in headers.iteritems():
            req.headers[k] = v

        # Send request
        res = req.get_response(self.api)

        # Examination of response
        self.assertEqual(res.status_int, 200)
        res_objs = jsonutils.loads(res.body)['catalog_price']
        self.assertEqual(res_objs['catalog_id'], CT_UUID1)
        self.assertEqual(res_objs['scope'], SCOPE1)
        self.assertEqual(res_objs['seq_no'], SEQ_NO1)
        self.assertEqual(res_objs['expansions']['expansion_key1'], '1')

    def test_show_response_empty_catalogid_irregular(self):
        """Test 'Get of catalog price'
        Test if the retrieved result is of 0.
        """
        path = '/catalog/%s/price/%s/seq/%s' % (CT_UUID3, SCOPE1, SEQ_NO1)
        req = unit_test_utils.get_fake_request(method='GET',
                                               path=path)

        headers = {'x-auth-token': 'user:tenant:admin'}
        for k, v in headers.iteritems():
            req.headers[k] = v

        # Send request
        res = req.get_response(self.api)

        # Examination of response
        self.assertEqual(res.status_int, 404)

    def test_show_response_empty_scope_irregular(self):
        """Test 'Get of catalog price'
        Test if the retrieved result is of 0.
        """
        path = '/catalog/%s/price/%s/seq/%s' % (CT_UUID1, SCOPE3, SEQ_NO1)
        req = unit_test_utils.get_fake_request(method='GET',
                                               path=path)

        headers = {'x-auth-token': 'user:tenant:admin'}
        for k, v in headers.iteritems():
            req.headers[k] = v

        # Send request
        res = req.get_response(self.api)

        # Examination of response
        self.assertEqual(res.status_int, 404)

    def test_show_response_empty_seqno_irregular(self):
        """Test 'Get of catalog price'
        Test if the retrieved result is of 0.
        """
        path = '/catalog/%s/price/%s/seq/%s' % (CT_UUID1, SCOPE1, SEQ_NO3)
        req = unit_test_utils.get_fake_request(method='GET',
                                               path=path)

        headers = {'x-auth-token': 'user:tenant:admin'}
        for k, v in headers.iteritems():
            req.headers[k] = v

        # Send request
        res = req.get_response(self.api)

        # Examination of response
        self.assertEqual(res.status_int, 404)

    def test_show_api_no_authority_irregular(self):
        """Test 'Get of catalog price'
        Test cases run unauthorized.
        """
        path = '/catalog/%s/price/%s/seq/%s' % (CT_UUID1, SCOPE1, SEQ_NO1)
        req = unit_test_utils.get_fake_request(method='GET',
                                               path=path)

        headers = {'x-auth-token': 'user:tenant:no_auth'}
        for k, v in headers.iteritems():
            req.headers[k] = v

        # Send request
        res = req.get_response(self.api)

        # Examination of response
        self.assertEqual(res.status_int, 403)

    def test_show_api_member_authority(self):
        """Test 'Get of catalog price'
        Test cases run member authority.
        """
        path = '/catalog/%s/price/%s/seq/%s' % (CT_UUID1, SCOPE2, SEQ_NO1)
        req = unit_test_utils.get_fake_request(method='GET',
                                               path=path)

        headers = {'x-auth-token': 'user:%s:__member__' % SCOPE2}
        for k, v in headers.iteritems():
            req.headers[k] = v

        # Send request
        res = req.get_response(self.api)

        # Examination of response
        self.assertEqual(res.status_int, 200)
        res_objs = jsonutils.loads(res.body)['catalog_price']
        self.assertEqual(res_objs['catalog_id'], CT_UUID1)
        self.assertEqual(res_objs['scope'], SCOPE2)
        self.assertEqual(res_objs['seq_no'], SEQ_NO1)
        self.assertEqual(res_objs['expansions']['expansion_key1'], '1')

    def test_show_api_member_authority_irregular(self):
        """Test 'Get of catalog price'
        Test cases run member unauthorized.
        """
        path = '/catalog/%s/price/%s/seq/%s' % (CT_UUID1, SCOPE2, SEQ_NO1)
        req = unit_test_utils.get_fake_request(method='GET',
                                               path=path)

        headers = {'x-auth-token': 'user:%s:__member__' % SCOPE1}
        for k, v in headers.iteritems():
            req.headers[k] = v

        # Send request
        res = req.get_response(self.api)

        # Examination of response
        self.assertEqual(res.status_int, 404)

    def test_show_api_symbol(self):
        """Test 'Get of catalog price'
        Test the operation of symbol.
        """
        path = '/catalog/%s/price/%s/seq/%s' % (CT_UUID3, SCOPE3, SEQ_NO3)
        req = unit_test_utils.get_fake_request(method='GET',
                                               path=path)

        headers = {'x-auth-token': 'user:tenant:admin'}
        for k, v in headers.iteritems():
            req.headers[k] = v

        # Send request
        res = req.get_response(self.api)

        # Examination of response
        self.assertEqual(res.status_int, 200)
        res_objs = jsonutils.loads(res.body)['catalog_price']
        self.assertEqual(res_objs['catalog_id'], CT_UUID3)
        self.assertEqual(res_objs['scope'], SCOPE3)
        self.assertEqual(res_objs['seq_no'], SEQ_NO3)
        self.assertEqual(res_objs['expansions']['expansion_key1'],
                         '!"#$%&()=~|`{+*}<>?_')

    def test_show_api_response_all_expansions(self):
        """Test 'Get of catalog price'
        Test if the retrieved result is all expansions.
        """
        path = '/catalog/%s/price/%s/seq/%s' % (CT_UUID1, SCOPE2, SEQ_NO1)
        req = unit_test_utils.get_fake_request(method='GET',
                                               path=path)

        headers = {'x-auth-token': 'user:tenant:admin'}
        for k, v in headers.iteritems():
            req.headers[k] = v

        # Send request
        res = req.get_response(self.api)

        # Examination of response
        self.assertEqual(res.status_int, 200)
        res_objs = jsonutils.loads(res.body)['catalog_price']
        self.assertEqual(res_objs['catalog_id'], CT_UUID1)
        self.assertEqual(res_objs['scope'], SCOPE2)
        self.assertEqual(res_objs['seq_no'], SEQ_NO1)
        self.assertEqual(res_objs['expansions']['expansion_key1'], '1')
        self.assertEqual(res_objs['expansions']['expansion_key2'], '2')
        self.assertEqual(res_objs['expansions']['expansion_key3'], '3')
        self.assertEqual(res_objs['expansions']['expansion_key4'], '4')
        self.assertEqual(res_objs['expansions']['expansion_key5'], '5')

    def test_show_api_response_one_expansions(self):
        """Test 'Get of catalog price'
        Test if the retrieved result is one expansions.
        """
        path = '/catalog/%s/price/%s/seq/%s' % (CT_UUID1, SCOPE2, SEQ_NO2)
        req = unit_test_utils.get_fake_request(method='GET',
                                               path=path)

        headers = {'x-auth-token': 'user:tenant:admin'}
        for k, v in headers.iteritems():
            req.headers[k] = v

        # Send request
        res = req.get_response(self.api)

        # Examination of response
        self.assertEqual(res.status_int, 200)
        res_objs = jsonutils.loads(res.body)['catalog_price']
        self.assertEqual(res_objs['catalog_id'], CT_UUID1)
        self.assertEqual(res_objs['scope'], SCOPE2)
        self.assertEqual(res_objs['seq_no'], SEQ_NO2)
        self.assertEqual(res_objs['expansions']['expansion_key1'], '1')
        self.assertIsNone(res_objs['expansions']['expansion_key2'])
        self.assertIsNone(res_objs['expansions']['expansion_key3'])
        self.assertIsNone(res_objs['expansions']['expansion_key4'])
        self.assertIsNone(res_objs['expansions']['expansion_key5'])

    def test_show_api_response_none_expansions(self):
        """Test 'Get of catalog price'
        Test if the retrieved result is none expansions.
        """
        path = '/catalog/%s/price/%s/seq/%s' % (CT_UUID2, SCOPE1, SEQ_NO1)
        req = unit_test_utils.get_fake_request(method='GET',
                                               path=path)

        headers = {'x-auth-token': 'user:tenant:admin'}
        for k, v in headers.iteritems():
            req.headers[k] = v

        # Send request
        res = req.get_response(self.api)

        # Examination of response
        self.assertEqual(res.status_int, 200)
        res_objs = jsonutils.loads(res.body)['catalog_price']
        self.assertEqual(res_objs['catalog_id'], CT_UUID2)
        self.assertEqual(res_objs['scope'], SCOPE1)
        self.assertEqual(res_objs['seq_no'], SEQ_NO1)
        self.assertIsNone(res_objs['expansions']['expansion_key1'])
        self.assertIsNone(res_objs['expansions']['expansion_key2'])
        self.assertIsNone(res_objs['expansions']['expansion_key3'])
        self.assertIsNone(res_objs['expansions']['expansion_key4'])
        self.assertIsNone(res_objs['expansions']['expansion_key5'])

    def test_show_catalog_id_error(self):
        """Test 'Get of catalog price'
        Test with catalog_id is over length.
        """
        path = '/catalog/%s/price/%s/seq/%s' % ('a' * 65, SCOPE1, SEQ_NO1)
        req = unit_test_utils.get_fake_request(method='GET',
                                               path=path)

        headers = {'x-auth-token': 'user:tenant:admin'}
        for k, v in headers.iteritems():
            req.headers[k] = v

        # Send request
        res = req.get_response(self.api)

        # Examination of response
        self.assertEqual(res.status_int, 400)

    def test_show_scope_error(self):
        """Test 'Get of catalog price'
        Test with scope is over length.
        """
        path = '/catalog/%s/price/%s/seq/%s' % (CT_UUID1, 'a' * 65, SEQ_NO1)
        req = unit_test_utils.get_fake_request(method='GET',
                                               path=path)

        headers = {'x-auth-token': 'user:tenant:admin'}
        for k, v in headers.iteritems():
            req.headers[k] = v

        # Send request
        res = req.get_response(self.api)

        # Examination of response
        self.assertEqual(res.status_int, 400)

    def test_show_seq_no_error(self):
        """Test 'Get of catalog price'
        Test with seq_no is over length.
        """
        path = '/catalog/%s/price/%s/seq/%s' % (CT_UUID1, SCOPE1, 'a' * 65)
        req = unit_test_utils.get_fake_request(method='GET',
                                               path=path)

        headers = {'x-auth-token': 'user:tenant:admin'}
        for k, v in headers.iteritems():
            req.headers[k] = v

        # Send request
        res = req.get_response(self.api)

        # Examination of response
        self.assertEqual(res.status_int, 400)
