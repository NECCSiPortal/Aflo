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

import datetime
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
from aflo.tests.unit.v1.price\
    import utils as price_utils
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


class TestPriceShowAPI(base.WorkflowUnitTest):
    """Do a test of 'Get the details of the Price'"""

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
        price_utils.create_testdata(
            db_models,
            catalog_id=CT_UUID1,
            scope=SCOPE1,
            seq_no='1',
            price=100,
            lifetime_start=datetime.date(2015, 1, 1),
            lifetime_end=datetime.date(2015, 12, 31),
            date=datetime.date(2015, 1, 11),
            seq=1,
            deleted=0)
        price_utils.create_testdata(
            db_models,
            catalog_id=CT_UUID1,
            scope="Default",
            seq_no='2',
            price=5000,
            lifetime_start=datetime.date(2016, 1, 2),
            lifetime_end=datetime.date(2016, 12, 31),
            date=datetime.date(2015, 1, 11),
            seq=2,
            deleted=0)
        price_utils.create_testdata(
            db_models,
            catalog_id=CT_UUID1,
            scope=SCOPE2,
            seq_no='3',
            price=2000,
            lifetime_start=datetime.date(2015, 1, 3),
            lifetime_end=datetime.date(2015, 12, 31),
            date=datetime.date(2015, 1, 11),
            seq=3,
            deleted=0)
        price_utils.create_testdata(
            db_models,
            catalog_id=CT_UUID1,
            scope=SCOPE2,
            seq_no='4',
            price=3000,
            lifetime_start=datetime.date(2016, 1, 4),
            lifetime_end=datetime.date(2016, 12, 31),
            date=datetime.date(2015, 1, 11),
            seq=4,
            deleted=0)
        price_utils.create_testdata(
            db_models,
            catalog_id=CT_UUID1,
            scope=SCOPE2,
            seq_no='5',
            price=4000,
            lifetime_start=datetime.date(2015, 1, 5),
            lifetime_end=datetime.datetime(2015, 12, 31, 10, 00, 00),
            date=datetime.date(2015, 1, 11),
            seq=5,
            deleted=0)
        price_utils.create_testdata(
            db_models,
            catalog_id=CT_UUID1,
            scope=SCOPE2,
            seq_no='6',
            price=5000,
            lifetime_start=datetime.date(2016, 1, 6),
            lifetime_end=datetime.date(2016, 12, 31),
            date=datetime.date(2015, 1, 11),
            seq=6,
            deleted=0)
        price_utils.create_testdata(
            db_models,
            catalog_id=CT_UUID2,
            scope=SCOPE1,
            seq_no='7',
            price=100,
            lifetime_start=datetime.date(2015, 1, 7),
            lifetime_end=datetime.date(2015, 12, 31),
            date=datetime.date(2015, 1, 11),
            seq=7,
            deleted=0)
        price_utils.create_testdata(
            db_models,
            catalog_id=CT_UUID2,
            scope=SCOPE2,
            seq_no='8',
            price=100,
            lifetime_start=datetime.date(2016, 1, 8),
            lifetime_end=datetime.date(2016, 12, 31),
            date=datetime.date(2015, 1, 11),
            seq=8,
            deleted=0)
        price_utils.create_testdata(
            db_models,
            catalog_id=CT_UUID2,
            scope=SCOPE2,
            seq_no='9',
            price=100,
            lifetime_start=datetime.date(2016, 1, 9),
            lifetime_end=datetime.date(2016, 12, 31),
            date=datetime.date(2015, 1, 11),
            seq=9,
            deleted=1)

    def destroy_fixtures(self):
        # Easiest to just drop the models and re-create them...
        db_models.unregister_models(db_api.get_engine())
        db_models.register_models(db_api.get_engine())

    def test_index_api_non_params(self):
        """Do a test of 'List Search of price'
        Test the operation of the parameter without.
        """

        # Create a request data
        path = '/catalog/%s/price' % CT_UUID2
        req = unit_test_utils.get_fake_request(method='GET', path=path)
        headers = {'x-auth-token': 'user:tenant:admin'}
        for k, v in headers.iteritems():
            req.headers[k] = v

        # Send request
        res = req.get_response(self.api)

        # Examination of response
        self.assertEqual(res.status_int, 200)
        res_objs = jsonutils.loads(res.body)['catalog_price']
        self.assertEqual(len(res_objs), 2)
        self.assertEqual(res_objs[0]['catalog_id'], CT_UUID2)
        self.assertEqual(res_objs[0]['scope'], SCOPE1)
        self.assertEqual(res_objs[0]['seq_no'], '7')
        self.assertEqual(res_objs[1]['catalog_id'], CT_UUID2)
        self.assertEqual(res_objs[1]['scope'], SCOPE2)
        self.assertEqual(res_objs[1]['seq_no'], '8')

    def test_index_api_paginate_params(self):
        """Do a test of 'List Search of price'
        Test with paginate parameters.
        """

        # Create a request data
        path = '/catalog/%s/price?marker=%s&limit=%d'\
            '&sort_key=%s&sort_dir=%s&force_show_deleted=%s&scope=%s' \
            % (CT_UUID1, '3',
               2, 'price', 'asc', 'True', SCOPE2)
        req = unit_test_utils.get_fake_request(method='GET', path=path)
        headers = {'x-auth-token': 'user:tenant:admin'}
        for k, v in headers.iteritems():
            req.headers[k] = v

        # Send request
        res = req.get_response(self.api)

        # Examination of response
        self.assertEqual(res.status_int, 200)
        res_objs = jsonutils.loads(res.body)['catalog_price']
        self.assertEqual(len(res_objs), 2)
        self.assertEqual(res_objs[0]['catalog_id'], CT_UUID1)
        self.assertEqual(res_objs[0]['scope'], SCOPE2)
        self.assertEqual(res_objs[0]['seq_no'], '4')
        self.assertEqual(res_objs[1]['catalog_id'], CT_UUID1)
        self.assertEqual(res_objs[1]['scope'], SCOPE2)
        self.assertEqual(res_objs[1]['seq_no'], '5')

    def test_index_api_lifetime_param(self):
        """Do a test of 'List Search of price'
        Test with lifetime parameter.
        """

        # Create a request data
        path = '/catalog/%s/price?lifetime=%s' \
               % (CT_UUID1, "2015-7-1T00:00:00.000")
        req = unit_test_utils.get_fake_request(method='GET', path=path)
        headers = {'x-auth-token': 'user:tenant:admin'}
        for k, v in headers.iteritems():
            req.headers[k] = v

        # Send request
        res = req.get_response(self.api)

        # Examination of response
        self.assertEqual(res.status_int, 200)
        res_objs = jsonutils.loads(res.body)['catalog_price']
        self.assertEqual(len(res_objs), 3)
        self.assertEqual(res_objs[0]['catalog_id'], CT_UUID1)
        self.assertEqual(res_objs[0]['scope'], SCOPE1)
        self.assertEqual(res_objs[0]['seq_no'], '1')
        self.assertEqual(res_objs[1]['catalog_id'], CT_UUID1)
        self.assertEqual(res_objs[1]['scope'], SCOPE2)
        self.assertEqual(res_objs[1]['seq_no'], '3')

    def test_index_api_lifetime_start_today(self):
        """Do a test of 'List Search of price'
        Test with lifetime parameter.
        """

        # Create a request data
        path = '/catalog/%s/price?lifetime=%s' \
               % (CT_UUID1, "2015-1-1T23:00:00.000")
        req = unit_test_utils.get_fake_request(method='GET', path=path)
        headers = {'x-auth-token': 'user:tenant:admin'}
        for k, v in headers.iteritems():
            req.headers[k] = v

        # Send request
        res = req.get_response(self.api)

        # Examination of response
        self.assertEqual(res.status_int, 200)
        res_objs = jsonutils.loads(res.body)['catalog_price']
        self.assertEqual(len(res_objs), 1)
        self.assertEqual(res_objs[0]['catalog_id'], CT_UUID1)
        self.assertEqual(res_objs[0]['scope'], SCOPE1)
        self.assertEqual(res_objs[0]['seq_no'], '1')

    def test_index_api_lifetime_end_today(self):
        """Do a test of 'List Search of price'
        Test with lifetime parameter.
        """

        # Create a request data
        path = '/catalog/%s/price?lifetime=%s' \
               % (CT_UUID1, "2015-12-31T00:00:00.000")
        req = unit_test_utils.get_fake_request(method='GET', path=path)
        headers = {'x-auth-token': 'user:tenant:admin'}
        for k, v in headers.iteritems():
            req.headers[k] = v

        # Send request
        res = req.get_response(self.api)

        # Examination of response
        self.assertEqual(res.status_int, 200)
        res_objs = jsonutils.loads(res.body)['catalog_price']
        self.assertEqual(len(res_objs), 3)
        self.assertEqual(res_objs[0]['seq_no'], '1')
        self.assertEqual(res_objs[1]['seq_no'], '3')
        self.assertEqual(res_objs[2]['seq_no'], '5')

    def test_index_api_response_empty_irregular(self):
        """Do a test of 'List Search of price'
        Test if the retrieved result is of 0.
        """

        # Create a request data
        path = '/catalog/%s/price?marker=%s' \
               % (CT_UUID1, '1')
        req = unit_test_utils.get_fake_request(method='GET', path=path)
        headers = {'x-auth-token': 'user:tenant:admin'}
        for k, v in headers.iteritems():
            req.headers[k] = v

        # Send request
        res = req.get_response(self.api)

        # Examination of response
        self.assertEqual(res.status_int, 200)
        res_objs = jsonutils.loads(res.body)['catalog_price']
        self.assertEqual(len(res_objs), 0)

    def test_index_api_many_sort_key(self):
        """Do a test of 'List Search of price'
        Test of if you specify multiple 'sort_key'.
        """

        # Create a request data
        path = '/catalog/%s/price?sort_key=%s&sort_key=%s' \
               '&sort_dir=%s&sort_dir=%s' \
               % (CT_UUID1, 'price', 'lifetime_start', 'asc', 'desc')
        req = unit_test_utils.get_fake_request(method='GET', path=path)
        headers = {'x-auth-token': 'user:tenant:admin'}
        for k, v in headers.iteritems():
            req.headers[k] = v

        # Send request
        res = req.get_response(self.api)

        # Examination of response
        self.assertEqual(res.status_int, 200)
        res_objs = jsonutils.loads(res.body)['catalog_price']
        self.assertEqual(len(res_objs), 6)
        self.assertEqual(res_objs[0]['catalog_id'], CT_UUID1)
        self.assertEqual(res_objs[0]['scope'], SCOPE1)
        self.assertEqual(res_objs[0]['seq_no'], '1')
        self.assertEqual(res_objs[1]['catalog_id'], CT_UUID1)
        self.assertEqual(res_objs[1]['scope'], SCOPE2)
        self.assertEqual(res_objs[1]['seq_no'], '3')
        self.assertEqual(res_objs[2]['catalog_id'], CT_UUID1)
        self.assertEqual(res_objs[2]['scope'], SCOPE2)
        self.assertEqual(res_objs[2]['seq_no'], '4')
        self.assertEqual(res_objs[3]['catalog_id'], CT_UUID1)
        self.assertEqual(res_objs[3]['scope'], SCOPE2)
        self.assertEqual(res_objs[3]['seq_no'], '5')
        self.assertEqual(res_objs[4]['catalog_id'], CT_UUID1)
        self.assertEqual(res_objs[4]['scope'], SCOPE2)
        self.assertEqual(res_objs[4]['seq_no'], '6')
        self.assertEqual(res_objs[5]['catalog_id'], CT_UUID1)
        self.assertEqual(res_objs[5]['scope'], 'Default')
        self.assertEqual(res_objs[5]['seq_no'], '2')

    def test_index_api_sort_dir_not_enough_irregular(self):
        """Do a test of 'List Search of price'
        Test of if you specify multiple 'sort_key'.
        Pattern the number of 'sort_dir' is not enough.
        """

        # Create a request data
        path = '/catalog/%s/price?sort_key=%s&sort_key=%s&sort_key=%s'\
            '&sort_dir=%s&sort_dir=%s' \
            % (CT_UUID1, 'price', 'lifetime_start', 'lifetime_end',
               'desc', 'asc')
        req = unit_test_utils.get_fake_request(method='GET', path=path)
        headers = {'x-auth-token': 'user:tenant:admin'}
        for k, v in headers.iteritems():
            req.headers[k] = v

        # Send request
        res = req.get_response(self.api)

        # Examination of response
        self.assertEqual(res.status_int, 400)

    def test_index_api_sort_key_not_enough_irregular(self):
        """Do a test of 'List Search of price'
        Test of if you specify multiple 'sort_key'.
        Pattern the number of 'sort_key' is not enough.
        """

        # Create a request data
        path = '/catalog/%s/price?sort_key=%s'\
            '&sort_dir=%s&sort_dir=%s' \
            % (CT_UUID1, 'price', 'asc', 'desc')
        req = unit_test_utils.get_fake_request(method='GET', path=path)
        headers = {'x-auth-token': 'user:tenant:admin'}
        for k, v in headers.iteritems():
            req.headers[k] = v

        # Send request
        res = req.get_response(self.api)

        # Examination of response
        self.assertEqual(res.status_int, 400)

    def test_index_api_default_limit(self):
        """Do a test of 'List Search of price'
        Or testing the default value of 'limit' is used.
        """

        # Create a request data
        bk_limit_param_default = CONF.limit_param_default
        self.config(limit_param_default=2)

        # Create a request data
        path = '/catalog/%s/price' % CT_UUID1
        req = unit_test_utils.get_fake_request(method='GET', path=path)
        headers = {'x-auth-token': 'user:tenant:admin'}
        for k, v in headers.iteritems():
            req.headers[k] = v

        # Send request
        res = req.get_response(self.api)

        self.config(limit_param_default=bk_limit_param_default)

        # Examination of response
        self.assertEqual(res.status_int, 200)
        res_objs = jsonutils.loads(res.body)['catalog_price']
        self.assertEqual(len(res_objs), 2)
        self.assertEqual(res_objs[0]['catalog_id'], CT_UUID1)
        self.assertEqual(res_objs[0]['scope'], SCOPE1)
        self.assertEqual(res_objs[0]['seq_no'], '1')
        self.assertEqual(res_objs[1]['catalog_id'], CT_UUID1)
        self.assertEqual(res_objs[1]['scope'], 'Default')
        self.assertEqual(res_objs[1]['seq_no'], '2')

    def test_index_api_max_limit(self):
        """Do a test of 'List Search of price'
        Test of whether the upper limit of 'limit' is used.
        """

        # Create a request data
        bk_api_limit_max = CONF.api_limit_max
        self.config(api_limit_max=2)

        # Create a request data
        path = '/catalog/%s/price' % CT_UUID1
        req = unit_test_utils.get_fake_request(method='GET', path=path)
        headers = {'x-auth-token': 'user:tenant:admin'}
        for k, v in headers.iteritems():
            req.headers[k] = v

        # Send request
        res = req.get_response(self.api)

        self.config(api_limit_max=bk_api_limit_max)

        # Examination of response
        self.assertEqual(res.status_int, 200)
        res_objs = jsonutils.loads(res.body)['catalog_price']
        self.assertEqual(len(res_objs), 2)
        self.assertEqual(res_objs[0]['catalog_id'], CT_UUID1)
        self.assertEqual(res_objs[0]['scope'], SCOPE1)
        self.assertEqual(res_objs[0]['seq_no'], '1')
        self.assertEqual(res_objs[1]['catalog_id'], CT_UUID1)
        self.assertEqual(res_objs[1]['scope'], 'Default')
        self.assertEqual(res_objs[1]['seq_no'], '2')

    def test_index_api_force_show_deleted_param(self):
        """Do a test of 'List Search of price'
        Test with force_show_deleted parameter.
        """

        # Create a request data
        path = '/catalog/%s/price?force_show_deleted=%s' \
               % (CT_UUID2, True)
        req = unit_test_utils.get_fake_request(method='GET', path=path)
        headers = {'x-auth-token': 'user:tenant:admin'}
        for k, v in headers.iteritems():
            req.headers[k] = v

        # Send request
        res = req.get_response(self.api)

        # Examination of response
        self.assertEqual(res.status_int, 200)
        res_objs = jsonutils.loads(res.body)['catalog_price']
        self.assertEqual(len(res_objs), 3)
        self.assertEqual(res_objs[0]['catalog_id'], CT_UUID2)
        self.assertEqual(res_objs[0]['scope'], SCOPE1)
        self.assertEqual(res_objs[0]['seq_no'], '7')
        self.assertEqual(res_objs[1]['catalog_id'], CT_UUID2)
        self.assertEqual(res_objs[1]['scope'], SCOPE2)
        self.assertEqual(res_objs[1]['seq_no'], '8')
        self.assertEqual(res_objs[2]['catalog_id'], CT_UUID2)
        self.assertEqual(res_objs[2]['scope'], SCOPE2)
        self.assertEqual(res_objs[2]['seq_no'], '9')

    def test_index_api_member_authority(self):
        """Do a test of 'List Search of price'
        Test when it is executed by a user other than the administrator.
        """

        # Create a request data
        path = '/catalog/%s/price' % CT_UUID1
        req = unit_test_utils.get_fake_request(method='GET', path=path)
        headers = {'x-auth-token': 'user:%s:__member__' % SCOPE1}
        for k, v in headers.iteritems():
            req.headers[k] = v

        # Send request
        res = req.get_response(self.api)

        # Examination of response
        self.assertEqual(res.status_int, 200)
        res_objs = jsonutils.loads(res.body)['catalog_price']
        self.assertEqual(len(res_objs), 2)
        self.assertEqual(res_objs[0]['catalog_id'], CT_UUID1)
        self.assertEqual(res_objs[0]['scope'], SCOPE1)
        self.assertEqual(res_objs[0]['seq_no'], '1')
        self.assertEqual(res_objs[1]['catalog_id'], CT_UUID1)
        self.assertEqual(res_objs[1]['scope'], 'Default')
        self.assertEqual(res_objs[1]['seq_no'], '2')

    def test_index_api_no_authority_irregular(self):
        """Do a test of 'List Search of price'
        Test cases run unauthorized.
        """

        # Create a request data
        path = '/catalog/%s/price' % CT_UUID1
        req = unit_test_utils.get_fake_request(method='GET', path=path)
        headers = {'x-auth-token': 'user:tenant:no_authority'}
        for k, v in headers.iteritems():
            req.headers[k] = v

        # Send request
        res = req.get_response(self.api)

        # Examination of response
        self.assertEqual(res.status_int, 403)

    def test_index_api_with_catalog_id_length(self):
        """Test of 'List Search of price'
        Test with catalog_id where is over length.
        """

        # Create a request data
        path = '/catalog/%s/price' \
               % ('a' * 65)
        req = unit_test_utils.get_fake_request(method='GET', path=path)
        headers = {'x-auth-token': 'user:tenant:admin'}
        for k, v in headers.iteritems():
            req.headers[k] = v

        # Send request
        res = req.get_response(self.api)

        # Examination of response
        self.assertEqual(res.status_int, 400)

    def test_index_api_with_limit_not_int(self):
        """Test of 'List Search of price'
        Test with limit where is not int.
        """

        # Create a request data
        path = '/catalog/%s/price?limit=%s' \
               % (CT_UUID1, 'a')
        req = unit_test_utils.get_fake_request(method='GET', path=path)
        headers = {'x-auth-token': 'user:tenant:admin'}
        for k, v in headers.iteritems():
            req.headers[k] = v

        # Send request
        res = req.get_response(self.api)

        # Examination of response
        self.assertEqual(res.status_int, 400)

    def test_index_api_with_marker_length(self):
        """Test of 'List Search of price'
        Test with marker where is over length.
        """

        # Create a request data
        path = '/catalog/%s/price?marker=%s' \
               % (CT_UUID1, 'a' * 65)
        req = unit_test_utils.get_fake_request(method='GET', path=path)
        headers = {'x-auth-token': 'user:tenant:admin'}
        for k, v in headers.iteritems():
            req.headers[k] = v

        # Send request
        res = req.get_response(self.api)

        # Examination of response
        self.assertEqual(res.status_int, 400)

    def test_index_api_with_sort_key_not_supported(self):
        """Test of 'List Search of price'
        Test with sort_key where is not supported.
        """

        # Create a request data
        path = '/catalog/%s/price?sort_key=%s' \
               % (CT_UUID1, 'expansion_key1')
        req = unit_test_utils.get_fake_request(method='GET', path=path)
        headers = {'x-auth-token': 'user:tenant:admin'}
        for k, v in headers.iteritems():
            req.headers[k] = v

        # Send request
        res = req.get_response(self.api)

        # Examination of response
        self.assertEqual(res.status_int, 400)

    def test_index_api_with_sort_dir_not_supported(self):
        """Test of 'List Search of price'
        Test with sort_dir where is not supported.
        """

        # Create a request data
        path = '/catalog/%s/price?sort_dir=%s' \
               % (CT_UUID1, 'dasc')
        req = unit_test_utils.get_fake_request(method='GET', path=path)
        headers = {'x-auth-token': 'user:tenant:admin'}
        for k, v in headers.iteritems():
            req.headers[k] = v

        # Send request
        res = req.get_response(self.api)

        # Examination of response
        self.assertEqual(res.status_int, 400)

    def test_index_api_with_force_show_deleted_not_supported(self):
        """Test of 'List Search of price'
        Test with force_show_deleted where is not supported.
        """

        # Create a request data
        path = '/catalog/%s/price?force_show_deleted=%s' \
               % (CT_UUID1, 'tree')
        req = unit_test_utils.get_fake_request(method='GET', path=path)
        headers = {'x-auth-token': 'user:tenant:admin'}
        for k, v in headers.iteritems():
            req.headers[k] = v

        # Send request
        res = req.get_response(self.api)

        # Examination of response
        self.assertEqual(res.status_int, 400)

    def test_index_api_with_lifetime_not_datetime(self):
        """Test of 'List Search of price'
        Test with lifetime where is not datetime.
        """

        # Create a request data
        path = '/catalog/%s/price?lifetime=%s' \
               % (CT_UUID1, '2015-01')
        req = unit_test_utils.get_fake_request(method='GET', path=path)
        headers = {'x-auth-token': 'user:tenant:admin'}
        for k, v in headers.iteritems():
            req.headers[k] = v

        # Send request
        res = req.get_response(self.api)

        # Examination of response
        self.assertEqual(res.status_int, 400)
