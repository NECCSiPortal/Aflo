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

body_region_id_error = \
    {'goods':
     {'region_id': 'a' * 256,
      'goods_name': None,
      'expansions':
      {'expansion_key1': None,
       'expansion_key2': None,
       'expansion_key3': None,
       'expansion_key4': None,
       'expansion_key5': None},
      'expansions_text':
      {'expansion_text': None}
      }
     }

body_goods_name_error = \
    {'goods':
     {'region_id': None,
      'goods_name': 'a' * 129,
      'expansions':
      {'expansion_key1': None,
       'expansion_key2': None,
       'expansion_key3': None,
       'expansion_key4': None,
       'expansion_key5': None},
      'expansions_text':
      {'expansion_text': None}
      }
     }

body_expansion_key1_error = \
    {'goods':
     {'region_id': None,
      'goods_name': None,
      'expansions':
      {'expansion_key1': 'a' * 256,
       'expansion_key2': None,
       'expansion_key3': None,
       'expansion_key4': None,
       'expansion_key5': None},
      'expansions_text':
      {'expansion_text': None}
      }
     }

body_expansion_key2_error = \
    {'goods':
     {'region_id': None,
      'goods_name': None,
      'expansions':
      {'expansion_key1': None,
       'expansion_key2': 'a' * 256,
       'expansion_key3': None,
       'expansion_key4': None,
       'expansion_key5': None},
      'expansions_text':
      {'expansion_text': None}
      }
     }

body_expansion_key3_error = \
    {'goods':
     {'region_id': None,
      'goods_name': None,
      'expansions':
      {'expansion_key1': None,
       'expansion_key2': None,
       'expansion_key3': 'a' * 256,
       'expansion_key4': None,
       'expansion_key5': None},
      'expansions_text':
      {'expansion_text': None}
      }
     }

body_expansion_key4_error = \
    {'goods':
     {'region_id': None,
      'goods_name': None,
      'expansions':
      {'expansion_key1': None,
       'expansion_key2': None,
       'expansion_key3': None,
       'expansion_key4': 'a' * 256,
       'expansion_key5': None},
      'expansions_text':
      {'expansion_text': None}
      }
     }

body_expansion_key5_error = \
    {'goods':
     {'region_id': None,
      'goods_name': None,
      'expansions':
      {'expansion_key1': None,
       'expansion_key2': None,
       'expansion_key3': None,
       'expansion_key4': None,
       'expansion_key5': 'a' * 256},
      'expansions_text':
      {'expansion_text': None}
      }
     }

body_expansion_text_error = \
    {'goods':
     {'region_id': None,
      'goods_name': None,
      'expansions':
      {'expansion_key1': None,
       'expansion_key2': None,
       'expansion_key3': None,
       'expansion_key4': None,
       'expansion_key5': None},
      'expansions_text':
      {'expansion_text': 'a' * 4001}
      }
     }


class TestGoodsCreateAPI(base.WorkflowUnitTest):
    """Do a test of 'Create a new goods'"""

    def setUp(self):
        """Establish a clean test environment"""
        super(TestGoodsCreateAPI, self).setUp()
        self.mapper = routes.Mapper()
        self.api = test_utils.FakeAuthMiddleware(router.API(self.mapper))

        self.context = aflo.context.RequestContext(is_admin=True)
        db_api.get_engine()
        self.destroy_fixtures()
        self.create_fixtures()
        self.serializer = wsgi.JSONResponseSerializer()

    def tearDown(self):
        """Clear the test environment"""
        super(TestGoodsCreateAPI, self).tearDown()
        self.destroy_fixtures()

    def create_fixtures(self):
        super(TestGoodsCreateAPI, self).create_fixtures()

    def destroy_fixtures(self):
        # Easiest to just drop the models and re-create them...
        db_models.unregister_models(db_api.get_engine())
        db_models.register_models(db_api.get_engine())

    def test_create(self):
        """Do a test of 'Create a new goods'
        """

        # Create a request data
        path = '/goods'
        req = unit_test_utils.get_fake_request(method='POST',
                                               path=path)
        headers = {'x-auth-token': 'user:tenant:admin',
                   'x-user-name': 'user-name',
                   'x-tenant-name': 'tenant-name'}
        for k, v in headers.iteritems():
            req.headers[k] = v

        req.body = '{"goods":{"region_id": "region_id_101", ' \
                   '          "goods_name": "test_goods", ' \
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

        goods = jsonutils.loads(res.body)['goods']

        self.assertIsNotNone(goods['goods_id'])
        self.assertEqual(goods['region_id'], 'region_id_101')
        self.assertEqual(goods['goods_name'], 'test_goods')
        self.assertEqual(goods['expansions']['expansion_key1'],
                         'expansion_key1')
        self.assertEqual(goods['expansions']['expansion_key2'],
                         'expansion_key2')
        self.assertEqual(goods['expansions']['expansion_key3'],
                         'expansion_key3')
        self.assertEqual(goods['expansions']['expansion_key4'],
                         'expansion_key4')
        self.assertEqual(goods['expansions']['expansion_key5'],
                         'expansion_key5')
        self.assertEqual(goods['expansions_text']['expansion_text'],
                         'expansion_text')
        self.assertIsNotNone(goods['created_at'])
        self.assertIsNotNone(goods['updated_at'])
        self.assertIsNone(goods['deleted_at'])
        self.assertEqual(goods['deleted'], False)

    def test_goods_create_region_id_max_len_over(self):
        path = '/goods'
        req = unit_test_utils.get_fake_request(method='POST', path=path)
        headers = {'x-auth-token': 'user:tenant:admin'}

        for k, v in headers.iteritems():
            req.headers[k] = v

        req.body = jsonutils.dumps(body_region_id_error)

        res = req.get_response(self.api)
        self.assertEqual(res.status_int, 400)

    def test_goods_create_goods_name_max_len_over(self):
        path = '/goods'
        req = unit_test_utils.get_fake_request(method='POST', path=path)
        headers = {'x-auth-token': 'user:tenant:admin'}

        for k, v in headers.iteritems():
            req.headers[k] = v

        req.body = jsonutils.dumps(body_goods_name_error)

        res = req.get_response(self.api)
        self.assertEqual(res.status_int, 400)

    def test_goods_create_expansion_key1_max_len_over(self):
        path = '/goods'
        req = unit_test_utils.get_fake_request(method='POST', path=path)
        headers = {'x-auth-token': 'user:tenant:admin'}

        for k, v in headers.iteritems():
            req.headers[k] = v

        req.body = jsonutils.dumps(body_expansion_key1_error)

        res = req.get_response(self.api)
        self.assertEqual(res.status_int, 400)

    def test_goods_create_expansion_key2_max_len_over(self):
        path = '/goods'
        req = unit_test_utils.get_fake_request(method='POST', path=path)
        headers = {'x-auth-token': 'user:tenant:admin'}

        for k, v in headers.iteritems():
            req.headers[k] = v

        req.body = jsonutils.dumps(body_expansion_key2_error)

        res = req.get_response(self.api)
        self.assertEqual(res.status_int, 400)

    def test_goods_create_expansion_key3_max_len_over(self):
        path = '/goods'
        req = unit_test_utils.get_fake_request(method='POST', path=path)
        headers = {'x-auth-token': 'user:tenant:admin'}

        for k, v in headers.iteritems():
            req.headers[k] = v

        req.body = jsonutils.dumps(body_expansion_key3_error)

        res = req.get_response(self.api)
        self.assertEqual(res.status_int, 400)

    def test_goods_create_expansion_key4_max_len_over(self):
        path = '/goods'
        req = unit_test_utils.get_fake_request(method='POST', path=path)
        headers = {'x-auth-token': 'user:tenant:admin'}

        for k, v in headers.iteritems():
            req.headers[k] = v

        req.body = jsonutils.dumps(body_expansion_key4_error)

        res = req.get_response(self.api)
        self.assertEqual(res.status_int, 400)

    def test_goods_create_expansion_key5_max_len_over(self):
        path = '/goods'
        req = unit_test_utils.get_fake_request(method='POST', path=path)
        headers = {'x-auth-token': 'user:tenant:admin'}

        for k, v in headers.iteritems():
            req.headers[k] = v

        req.body = jsonutils.dumps(body_expansion_key5_error)

        res = req.get_response(self.api)
        self.assertEqual(res.status_int, 400)

    def test_goods_create_expansion_text_max_len_over(self):
        path = '/goods'
        req = unit_test_utils.get_fake_request(method='POST', path=path)
        headers = {'x-auth-token': 'user:tenant:admin'}

        for k, v in headers.iteritems():
            req.headers[k] = v

        req.body = jsonutils.dumps(body_expansion_text_error)

        res = req.get_response(self.api)
        self.assertEqual(res.status_int, 400)
