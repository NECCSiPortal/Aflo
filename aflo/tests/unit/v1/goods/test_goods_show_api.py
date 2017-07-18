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

RG_UUID1 = 'ea0a4146-fd07-414b-aa5e-dedbeef01001'
RG_UUID2 = 'ea0a4146-fd07-414b-aa5e-dedbeef01002'
RG_UUID3 = 'ea0a4146-fd07-414b-aa5e-dedbeef01003'
RG_UUID4 = 'ea0a4146-fd07-414b-aa5e-dedbeef01004'
RG_UUID5 = 'ea0a4146-fd07-414b-aa5e-dedbeef01005'


class TestGoodsShowAPI(base.WorkflowUnitTest):
    """Do a test of 'Get the details of the tickettemplates'"""

    def setUp(self):
        """Establish a clean test environment"""
        super(TestGoodsShowAPI, self).setUp()
        self.mapper = routes.Mapper()
        self.api = test_utils.FakeAuthMiddleware(router.API(self.mapper))

        self.context = aflo.context.RequestContext(is_admin=True)
        db_api.get_engine()
        self.destroy_fixtures()
        self.create_fixtures()
        self.serializer = wsgi.JSONResponseSerializer()

    def tearDown(self):
        """Clear the test environment"""
        super(TestGoodsShowAPI, self).tearDown()
        self.destroy_fixtures()

    def create_fixtures(self):
        Goods(goods_id=GD_UUID1,
              region_id=RG_UUID1,
              goods_name='1',
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
        Goods(goods_id=GD_UUID2,
              region_id=RG_UUID2,
              goods_name='2',
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
        Goods(goods_id=GD_UUID3,
              region_id=RG_UUID3,
              goods_name='3',
              created_at=datetime.utcnow(),
              updated_at=None,
              deleted_at=None,
              deleted=True,
              expansion_key1=None,
              expansion_key2=None,
              expansion_key3=None,
              expansion_key4=None,
              expansion_key5=None,
              expansion_text=None
              ).save(db_api.get_session())
        Goods(goods_id=GD_UUID4,
              region_id=RG_UUID4,
              goods_name=',./\;:]@[-^',
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
        path = '/goods/%s' % GD_UUID1
        req = unit_test_utils.get_fake_request(method='GET',
                                               path=path)

        headers = {'x-auth-token': 'user:tenant:developer'}
        for k, v in headers.iteritems():
            req.headers[k] = v

        # Send request
        res = req.get_response(self.api)

        # Examination of response
        self.assertEqual(res.status_int, 200)
        res_objs = jsonutils.loads(res.body)['goods']
        self.assertEqual(res_objs['goods_id'], GD_UUID1)
        self.assertEqual(res_objs['region_id'], RG_UUID1)
        self.assertEqual(res_objs['expansions']['expansion_key1'], '1')

    def test_show_response_empty_irregular(self):
        """Test 'Get of goods'
        Test if the retrieved result is of 0.
        """
        path = '/goods/%s' % GD_UUID5
        req = unit_test_utils.get_fake_request(method='GET',
                                               path=path)

        headers = {'x-auth-token': 'user:tenant:developer'}
        for k, v in headers.iteritems():
            req.headers[k] = v

        # Send request
        res = req.get_response(self.api)

        # Examination of response
        self.assertEqual(res.status_int, 404)

    def test_show_api_no_authority(self):
        """Test 'Get of goods'
        Test cases run unauthorized.
        """
        path = '/goods/%s' % GD_UUID1
        req = unit_test_utils.get_fake_request(method='GET',
                                               path=path)

        headers = {'x-auth-token': 'user:tenant:no_authority'}
        for k, v in headers.iteritems():
            req.headers[k] = v

        # Send request
        res = req.get_response(self.api)

        # Examination of response
        self.assertEqual(res.status_int, 403)

    def test_show_api_symbol(self):
        """Test 'Get of goods'
        Test the operation of symbol.
        """
        path = '/goods/%s' % GD_UUID4
        req = unit_test_utils.get_fake_request(method='GET',
                                               path=path)

        headers = {'x-auth-token': 'user:tenant:developer'}
        for k, v in headers.iteritems():
            req.headers[k] = v

        # Send request
        res = req.get_response(self.api)

        # Examination of response
        self.assertEqual(res.status_int, 200)
        res_objs = jsonutils.loads(res.body)['goods']
        self.assertEqual(res_objs['goods_id'], GD_UUID4)
        self.assertEqual(res_objs['region_id'], RG_UUID4)
        self.assertEqual(res_objs['goods_name'], ',./\;:]@[-^')
        self.assertEqual(res_objs['expansions']['expansion_key1'],
                         '!"#$%&()=~|`{+*}<>?_')

    def test_show_api_response_all_expansions(self):
        """Test 'Get of goods'
        Test if the retrieved result is all expansions.
        """
        path = '/goods/%s' % GD_UUID1
        req = unit_test_utils.get_fake_request(method='GET',
                                               path=path)

        headers = {'x-auth-token': 'user:tenant:developer'}
        for k, v in headers.iteritems():
            req.headers[k] = v

        # Send request
        res = req.get_response(self.api)

        # Examination of response
        self.assertEqual(res.status_int, 200)
        res_objs = jsonutils.loads(res.body)['goods']
        self.assertEqual(res_objs['goods_id'], GD_UUID1)
        self.assertEqual(res_objs['expansions']['expansion_key1'], '1')
        self.assertEqual(res_objs['expansions']['expansion_key2'], '2')
        self.assertEqual(res_objs['expansions']['expansion_key3'], '3')
        self.assertEqual(res_objs['expansions']['expansion_key4'], '4')
        self.assertEqual(res_objs['expansions']['expansion_key5'], '5')
        self.assertEqual(res_objs['expansions_text']['expansion_text'], '0')

    def test_show_api_response_one_expansions(self):
        """Test 'Get of goods'
        Test if the retrieved result is one expansion_key.
        """
        path = '/goods/%s' % GD_UUID2
        req = unit_test_utils.get_fake_request(method='GET',
                                               path=path)

        headers = {'x-auth-token': 'user:tenant:developer'}
        for k, v in headers.iteritems():
            req.headers[k] = v

        # Send request
        res = req.get_response(self.api)

        # Examination of response
        self.assertEqual(res.status_int, 200)
        res_objs = jsonutils.loads(res.body)['goods']
        self.assertEqual(res_objs['goods_id'], GD_UUID2)
        self.assertEqual(res_objs['expansions']['expansion_key1'], '1')
        self.assertIsNone(res_objs['expansions']['expansion_key2'])
        self.assertIsNone(res_objs['expansions']['expansion_key3'])
        self.assertIsNone(res_objs['expansions']['expansion_key4'])
        self.assertIsNone(res_objs['expansions']['expansion_key5'])
        self.assertIsNone(res_objs['expansions_text']['expansion_text'])

    def test_show_api_response_none_expansions(self):
        """Test 'Get of goods'
        Test if the retrieved result is no expansion_key.
        """
        path = '/goods/%s' % GD_UUID3
        req = unit_test_utils.get_fake_request(method='GET',
                                               path=path)

        headers = {'x-auth-token': 'user:tenant:developer'}
        for k, v in headers.iteritems():
            req.headers[k] = v

        # Send request
        res = req.get_response(self.api)

        # Examination of response
        self.assertEqual(res.status_int, 200)
        res_objs = jsonutils.loads(res.body)['goods']
        self.assertEqual(res_objs['goods_id'], GD_UUID3)
        self.assertIsNone(res_objs['expansions']['expansion_key1'])
        self.assertIsNone(res_objs['expansions']['expansion_key2'])
        self.assertIsNone(res_objs['expansions']['expansion_key3'])
        self.assertIsNone(res_objs['expansions']['expansion_key4'])
        self.assertIsNone(res_objs['expansions']['expansion_key5'])
        self.assertIsNone(res_objs['expansions_text']['expansion_text'])

    def test_show_goods_id_length_over(self):
        """Test 'Get of catalog price'
        Test the operation with goods_id where is over length.
        """
        path = '/goods/%s' % ('a' * 65)
        req = unit_test_utils.get_fake_request(method='GET',
                                               path=path)

        headers = {'x-auth-token': 'user:tenant:developer'}
        for k, v in headers.iteritems():
            req.headers[k] = v

        # Send request
        res = req.get_response(self.api)

        # Examination of response
        self.assertEqual(res.status_int, 400)
