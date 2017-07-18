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
from aflo.db.sqlalchemy.models import Goods
from aflo.tests.unit import base
import aflo.tests.unit.utils as unit_test_utils
from aflo.tests import utils as test_utils

CONF = cfg.CONF

GD_UUID1 = 'ea0a4146-fd07-414b-aa5e-dedbeef00001'
GD_UUID2 = 'ea0a4146-fd07-414b-aa5e-dedbeef00002'
GD_UUID3 = 'ea0a4146-fd07-414b-aa5e-dedbeef00003'
GD_UUID4 = 'ea0a4146-fd07-414b-aa5e-dedbeef00004'
GD_UUID5 = 'ea0a4146-fd07-414b-aa5e-dedbeef00005'
GD_UUID6 = 'ea0a4146-fd07-414b-aa5e-dedbeef00006'
GD_UUID7 = 'ea0a4146-fd07-414b-aa5e-dedbeef00007'
GD_UUID8 = 'ea0a4146-fd07-414b-aa5e-dedbeef00008'

REGION1 = 'ea0a4146-fd07-414b-aa5e-dedbeef01001'
REGION2 = 'ea0a4146-fd07-414b-aa5e-dedbeef01002'


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
        Goods(goods_id=GD_UUID1,
              region_id=REGION1,
              goods_name='1',
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
        Goods(goods_id=GD_UUID2,
              region_id=REGION2,
              goods_name='2',
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
        Goods(goods_id=GD_UUID3,
              region_id=REGION1,
              goods_name=',./\;:]@[\^-',
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
        Goods(goods_id=GD_UUID4,
              region_id=REGION2,
              goods_name='4',
              created_at=datetime.utcnow(),
              updated_at=None,
              deleted_at=None,
              deleted=False,
              expansion_key1='1',
              expansion_key2='2',
              expansion_key3='3',
              expansion_key4='4',
              expansion_key5='5',
              expansion_text='0'
              ).save(db_api.get_session())
        Goods(goods_id=GD_UUID5,
              region_id=REGION1,
              goods_name='5',
              created_at=datetime.utcnow(),
              updated_at=None,
              deleted_at=None,
              deleted=False,
              expansion_key1='1',
              expansion_key2=None,
              expansion_key3=None,
              expansion_key4=None,
              expansion_key5=None,
              expansion_text=None
              ).save(db_api.get_session())
        Goods(goods_id=GD_UUID6,
              region_id=REGION2,
              goods_name='6',
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
        Goods(goods_id=GD_UUID7,
              region_id=REGION1,
              goods_name='7',
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
        Goods(goods_id=GD_UUID8,
              region_id=REGION2,
              goods_name='8',
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

    def destroy_fixtures(self):
        # Easiest to just drop the models and re-create them...
        db_models.unregister_models(db_api.get_engine())
        db_models.register_models(db_api.get_engine())

    def test_index_api_non_params(self):
        """Test 'List Search of goods'
        Test the operation of the parameter without.
        """
        # Create a request data
        path = '/goods'
        req = unit_test_utils.get_fake_request(method='GET', path=path)
        headers = {'x-auth-token': 'user:tenant:admin'}
        for k, v in headers.iteritems():
            req.headers[k] = v

        # Send request
        res = req.get_response(self.api)

        # Examination of response
        self.assertEqual(res.status_int, 200)
        res_objs = jsonutils.loads(res.body)['goods']
        self.assertEqual(len(res_objs), 6)
        self.assertEqual(res_objs[0]['goods_id'], GD_UUID6)
        self.assertEqual(res_objs[1]['goods_id'], GD_UUID5)

    def test_index_api_paginate_params(self):
        """Test 'List Search of goods'
        Test with paginate parameters.
        """
        # Create a request data
        path = '/goods?marker=%s&limit=%s'\
            '&sort_key=%s&sort_dir=%s&force_show_deleted=%s&region_id=%s' \
            % (GD_UUID1, 2, 'goods_id', 'asc', 'True', REGION1)
        req = unit_test_utils.get_fake_request(method='GET', path=path)
        headers = {'x-auth-token': 'user:tenant:admin'}
        for k, v in headers.iteritems():
            req.headers[k] = v

        # Send request
        res = req.get_response(self.api)

        # Examination of response
        self.assertEqual(res.status_int, 200)
        res_objs = jsonutils.loads(res.body)['goods']
        self.assertEqual(len(res_objs), 2)
        self.assertEqual(res_objs[0]['goods_id'], GD_UUID3)
        self.assertEqual(res_objs[1]['goods_id'], GD_UUID5)

    def test_index_api_response_empty_irregular(self):
        """Test 'List Search of goods'
        Test if the retrieved result is of 0.
        """
        # Create a request data
        path = '/goods?marker=%s&sort_key=%s&sort_dir=%s' \
            % (GD_UUID6, 'goods_id', 'asc')
        req = unit_test_utils.get_fake_request(method='GET', path=path)
        headers = {'x-auth-token': 'user:tenant:admin'}
        for k, v in headers.iteritems():
            req.headers[k] = v

        # Send request
        res = req.get_response(self.api)

        # Examination of response
        self.assertEqual(res.status_int, 200)
        res_objs = jsonutils.loads(res.body)['goods']
        self.assertEqual(len(res_objs), 0)

    def test_index_api_many_sort_key(self):
        """Test 'List Search of goods'
        Test of if you specify multiple 'sort_key'.
        """
        # Create a request data
        path = '/goods?sort_key=%s&sort_dir=%s'\
            '&sort_key=%s&sort_dir=%s' \
            % ('region_id', 'desc', 'goods_id', 'asc')
        req = unit_test_utils.get_fake_request(method='GET', path=path)
        headers = {'x-auth-token': 'user:tenant:admin'}
        for k, v in headers.iteritems():
            req.headers[k] = v

        # Send request
        res = req.get_response(self.api)

        # Examination of response
        self.assertEqual(res.status_int, 200)
        res_objs = jsonutils.loads(res.body)['goods']
        self.assertEqual(len(res_objs), 6)
        self.assertEqual(res_objs[0]['goods_id'], GD_UUID2)
        self.assertEqual(res_objs[1]['goods_id'], GD_UUID4)

    def test_index_api_sort_dir_not_enough_irregular(self):
        """Test 'List Search of goods'
        Test of if you specify multiple 'sort_key'.
        Pattern the number of 'sort_dir' is not enough.
        """
        # Create a request data
        path = '/goods?sort_key=%s&sort_dir=%s'\
            '&sort_key=%s&sort_dir=%s&sort_key=%s' \
            % ('region_id', 'desc', 'goods_id', 'asc', 'created_at')
        req = unit_test_utils.get_fake_request(method='GET', path=path)
        headers = {'x-auth-token': 'user:tenant:admin'}
        for k, v in headers.iteritems():
            req.headers[k] = v

        # Send request
        res = req.get_response(self.api)

        # Examination of response
        self.assertEqual(res.status_int, 400)

    def test_index_api_sort_key_not_enough_irregular(self):
        """Test 'List Search of goods'
        Test of if you specify multiple 'sort_key'.
        Pattern the number of 'sort_key' is not enough.
        """
        # Create a request data
        path = '/goods?sort_key=%s&sort_dir=%s'\
            '&sort_key=%s&sort_dir=%s&sort_dir=%s' \
            % ('region_id', 'desc', 'goods_id', 'asc', 'asc')
        req = unit_test_utils.get_fake_request(method='GET', path=path)
        headers = {'x-auth-token': 'user:tenant:admin'}
        for k, v in headers.iteritems():
            req.headers[k] = v

        # Send request
        res = req.get_response(self.api)

        # Examination of response
        self.assertEqual(res.status_int, 400)

    def test_index_api_many_sort_key_one_sort_dir(self):
        """Test 'List Search of goods'
        Test of if you specify multiple 'sort_key'.
        Pattern the number of 'sort_dir' is one.
        """
        # Create a request data
        path = '/goods?sort_key=%s&sort_dir=%s'\
            '&sort_key=%s' \
            % ('region_id', 'desc', 'goods_id')
        req = unit_test_utils.get_fake_request(method='GET', path=path)
        headers = {'x-auth-token': 'user:tenant:admin'}
        for k, v in headers.iteritems():
            req.headers[k] = v

        # Send request
        res = req.get_response(self.api)

        # Examination of response
        self.assertEqual(res.status_int, 200)
        res_objs = jsonutils.loads(res.body)['goods']
        self.assertEqual(len(res_objs), 6)
        self.assertEqual(res_objs[0]['goods_id'], GD_UUID6)
        self.assertEqual(res_objs[1]['goods_id'], GD_UUID4)
        self.assertEqual(res_objs[2]['goods_id'], GD_UUID2)
        self.assertEqual(res_objs[3]['goods_id'], GD_UUID5)
        self.assertEqual(res_objs[4]['goods_id'], GD_UUID3)
        self.assertEqual(res_objs[5]['goods_id'], GD_UUID1)

    def test_index_api_limit_not_num(self):
        """Test 'List Search of goods'
        Test with limit in not integer.
        """
        # Create a request data
        path = '/goods?limit=%s' % "1a"
        req = unit_test_utils.get_fake_request(method='GET', path=path)
        headers = {'x-auth-token': 'user:tenant:admin'}
        for k, v in headers.iteritems():
            req.headers[k] = v

        # Send request
        res = req.get_response(self.api)

        # Examination of response
        self.assertEqual(res.status_int, 400)

    def test_index_api_default_limit(self):
        """Test 'List Search of goods'
        Or testing the default value of 'limit' is used.
        """
        # Create a request data
        bk_limit_param_default = CONF.limit_param_default
        self.config(limit_param_default=2)

        # Create a request data
        path = '/goods'
        req = unit_test_utils.get_fake_request(method='GET', path=path)
        headers = {'x-auth-token': 'user:tenant:admin'}
        for k, v in headers.iteritems():
            req.headers[k] = v

        # Send request
        res = req.get_response(self.api)

        self.config(limit_param_default=bk_limit_param_default)

        # Examination of response
        self.assertEqual(res.status_int, 200)
        res_objs = jsonutils.loads(res.body)['goods']
        self.assertEqual(len(res_objs), 2)
        self.assertEqual(res_objs[0]['goods_id'], GD_UUID6)
        self.assertEqual(res_objs[1]['goods_id'], GD_UUID5)

    def test_index_api_max_limit(self):
        """Test 'List Search of goods'
        Test of whether the upper limit of 'limit' is used.
        """
        # Create a request data
        bk_api_limit_max = CONF.api_limit_max
        self.config(api_limit_max=2)

        # Create a request data
        path = '/goods'
        req = unit_test_utils.get_fake_request(method='GET', path=path)
        headers = {'x-auth-token': 'user:tenant:admin'}
        for k, v in headers.iteritems():
            req.headers[k] = v

        # Send request
        res = req.get_response(self.api)

        self.config(api_limit_max=bk_api_limit_max)

        # Examination of response
        self.assertEqual(res.status_int, 200)
        res_objs = jsonutils.loads(res.body)['goods']
        self.assertEqual(len(res_objs), 2)
        self.assertEqual(res_objs[0]['goods_id'], GD_UUID6)
        self.assertEqual(res_objs[1]['goods_id'], GD_UUID5)

    def test_index_api_no_authority_irregular(self):
        """Test 'List Search of goods'
        Test cases run unauthorized.
        """
        # Create a request data
        path = '/goods'
        req = unit_test_utils.get_fake_request(method='GET', path=path)
        headers = {'x-auth-token': 'user:tenant:no_auth'}
        for k, v in headers.iteritems():
            req.headers[k] = v

        # Send request
        res = req.get_response(self.api)

        # Examination of response
        self.assertEqual(res.status_int, 403)

    def test_index_api_symbol(self):
        """Test 'List Search of goods'
        Test the operation of symbol.
        """
        # Create a request data
        path = '/goods'
        req = unit_test_utils.get_fake_request(method='GET', path=path)
        headers = {'x-auth-token': 'user:tenant:admin'}
        for k, v in headers.iteritems():
            req.headers[k] = v

        # Send request
        res = req.get_response(self.api)

        # Examination of response
        self.assertEqual(res.status_int, 200)
        res_objs = jsonutils.loads(res.body)['goods']
        self.assertEqual(len(res_objs), 6)
        self.assertEqual(res_objs[3]['goods_id'], GD_UUID3)
        self.assertEqual(res_objs[3]['goods_name'], ',./\;:]@[\^-')
        self.assertEqual(res_objs[3]['expansions']['expansion_key1'],
                         '!"#$%&()=~|`{+*}<>?_')

    def test_index_api_response_all_expansions(self):
        """Test 'List Search of goods'
        Test if the retrieved result is all expansions.
        """
        # Create a request data
        path = '/goods'
        req = unit_test_utils.get_fake_request(method='GET', path=path)
        headers = {'x-auth-token': 'user:tenant:admin'}
        for k, v in headers.iteritems():
            req.headers[k] = v

        # Send request
        res = req.get_response(self.api)

        # Examination of response
        self.assertEqual(res.status_int, 200)
        res_objs = jsonutils.loads(res.body)['goods']
        self.assertEqual(len(res_objs), 6)
        self.assertEqual(res_objs[2]['goods_id'], GD_UUID4)
        self.assertEqual(res_objs[2]['expansions']['expansion_key1'], '1')
        self.assertEqual(res_objs[2]['expansions']['expansion_key2'], '2')
        self.assertEqual(res_objs[2]['expansions']['expansion_key3'], '3')
        self.assertEqual(res_objs[2]['expansions']['expansion_key4'], '4')
        self.assertEqual(res_objs[2]['expansions']['expansion_key5'], '5')
        self.assertEqual(res_objs[2]['expansions_text']['expansion_text'], '0')

    def test_index_api_response_one_expansions(self):
        """Test 'List Search of goods'
        Test if the retrieved result is one expansions.
        """
        # Create a request data
        path = '/goods'
        req = unit_test_utils.get_fake_request(method='GET', path=path)
        headers = {'x-auth-token': 'user:tenant:admin'}
        for k, v in headers.iteritems():
            req.headers[k] = v

        # Send request
        res = req.get_response(self.api)

        # Examination of response
        self.assertEqual(res.status_int, 200)
        res_objs = jsonutils.loads(res.body)['goods']
        self.assertEqual(len(res_objs), 6)
        self.assertEqual(res_objs[1]['goods_id'], GD_UUID5)
        self.assertEqual(res_objs[1]['expansions']['expansion_key1'], '1')
        self.assertIsNone(res_objs[1]['expansions']['expansion_key2'])
        self.assertIsNone(res_objs[1]['expansions']['expansion_key3'])
        self.assertIsNone(res_objs[1]['expansions']['expansion_key4'])
        self.assertIsNone(res_objs[1]['expansions']['expansion_key5'])

    def test_show_api_response_none_expansions(self):
        """Test 'List Search of goods'
        Test if the retrieved result is none expansions.
        """
        # Create a request data
        path = '/goods'
        req = unit_test_utils.get_fake_request(method='GET', path=path)
        headers = {'x-auth-token': 'user:tenant:admin'}
        for k, v in headers.iteritems():
            req.headers[k] = v

        # Send request
        res = req.get_response(self.api)

        # Examination of response
        self.assertEqual(res.status_int, 200)
        res_objs = jsonutils.loads(res.body)['goods']
        self.assertEqual(len(res_objs), 6)
        self.assertEqual(res_objs[0]['goods_id'], GD_UUID6)
        self.assertIsNone(res_objs[0]['expansions']['expansion_key1'])
        self.assertIsNone(res_objs[0]['expansions']['expansion_key2'])
        self.assertIsNone(res_objs[0]['expansions']['expansion_key3'])
        self.assertIsNone(res_objs[0]['expansions']['expansion_key4'])
        self.assertIsNone(res_objs[0]['expansions']['expansion_key5'])
        self.assertIsNone(res_objs[0]['expansions_text']['expansion_text'])

    def test_index_api_member_auth_deleted_data(self):
        """Test 'List Search of goods'
        Be ignored 'force_show_deleted' for no authority.
        """
        # Create a request data
        path = '/goods?force_show_deleted=%s' % True
        req = unit_test_utils.get_fake_request(method='GET', path=path)
        headers = {'x-auth-token': 'user:tenant:__member__'}
        for k, v in headers.iteritems():
            req.headers[k] = v

        # Send request
        res = req.get_response(self.api)

        # Examination of response
        self.assertEqual(res.status_int, 200)
        res_objs = jsonutils.loads(res.body)['goods']
        self.assertEqual(len(res_objs), 6)
        self.assertEqual(res_objs[0]['goods_id'], GD_UUID6)
        self.assertEqual(res_objs[1]['goods_id'], GD_UUID5)

    def test_index_api_sort_key_error(self):
        """Test 'List Search of goods'
        Test with sort_key where is not supported.
        """
        # Create a request data
        path = '/goods?sort_key=%s' % "expansion_key1"
        req = unit_test_utils.get_fake_request(method='GET', path=path)
        headers = {'x-auth-token': 'user:tenant:admin'}
        for k, v in headers.iteritems():
            req.headers[k] = v

        # Send request
        res = req.get_response(self.api)

        # Examination of response
        self.assertEqual(res.status_int, 400)

    def test_index_api_sort_dir_error(self):
        """Test 'List Search of goods'
        Test with sort_dir where is not supported.
        """
        # Create a request data
        path = '/goods?sort_dir=%s' % "dasc"
        req = unit_test_utils.get_fake_request(method='GET', path=path)
        headers = {'x-auth-token': 'user:tenant:admin'}
        for k, v in headers.iteritems():
            req.headers[k] = v

        # Send request
        res = req.get_response(self.api)

        # Examination of response
        self.assertEqual(res.status_int, 400)

    def test_index_api_marker_error(self):
        """Test 'List Search of goods'
        Test with marker where is over length.
        """
        # Create a request data
        path = '/goods?marker=%s' % "a" * 65
        req = unit_test_utils.get_fake_request(method='GET', path=path)
        headers = {'x-auth-token': 'user:tenant:admin'}
        for k, v in headers.iteritems():
            req.headers[k] = v

        # Send request
        res = req.get_response(self.api)

        # Examination of response
        self.assertEqual(res.status_int, 400)

    def test_index_api_force_show_deleted_error(self):
        """Test 'List Search of goods'
        Test with force_show_deleted where is over length.
        """
        # Create a request data
        path = '/goods?force_show_deleted=%s' % 'ture'
        req = unit_test_utils.get_fake_request(method='GET', path=path)
        headers = {'x-auth-token': 'user:tenant:admin'}
        for k, v in headers.iteritems():
            req.headers[k] = v

        # Send request
        res = req.get_response(self.api)

        # Examination of response
        self.assertEqual(res.status_int, 400)
