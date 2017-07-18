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
from aflo import db
from aflo.db.sqlalchemy import models as db_models
from aflo.tests.unit import base
import aflo.tests.unit.utils as unit_test_utils
from aflo.tests import utils as test_utils

CONF = cfg.CONF
db_api = db.get_api()

GOODS_ID_101 = 'ea0a4146-fd07-414b-aa5e-dedbeef00101'
GOODS_ID_102 = 'ea0a4146-fd07-414b-aa5e-dedbeef00102'
GOODS_ID_103 = 'ea0a4146-fd07-414b-aa5e-dedbeef00103'
GOODS_ID_104 = 'ea0a4146-fd07-414b-aa5e-dedbeef00104'

bo01 = {'goods':
        {'region_id': 'region_id_101_u',
         'goods_name': 'goods_name_101_u',
         'deleted': True,
         'expansions':
         {'expansion_key1': 'expansion_key1_u',
          'expansion_key2': 'expansion_key2_u_\"_\\_$_/_',
          'expansion_key3': 'expansion_key3_u',
          'expansion_key4': 'expansion_key4_u',
          'expansion_key5': 'expansion_key5_u'},
         'expansions_text':
         {'expansion_text': 'expansion_text_u'}
         }
        }

bo02 = {'goods':
        {'region_id': None,
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

bo04 = {'goods': {}}

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


def get_datetime(str_date):
    """Get datetime.
        :param str_date: String of date.
    """
    return datetime.strptime(str_date + 'T00:00:00.000000',
                             '%Y-%m-%dT%H:%M:%S.%f')


class TestGoodsUpdateAPI(base.WorkflowUnitTest):
    def setUp(self):
        """Establish a clean test environment"""
        super(TestGoodsUpdateAPI, self).setUp()
        self.mapper = routes.Mapper()
        self.api = test_utils.FakeAuthMiddleware(router.API(self.mapper))

        self.context = aflo.context.RequestContext(is_admin=True)
        db_api.get_engine()
        self.destroy_fixtures()
        self.create_fixtures()
        self.serializer = wsgi.JSONResponseSerializer()

    def tearDown(self):
        """Clear the test environment"""
        super(TestGoodsUpdateAPI, self).tearDown()
        self.destroy_fixtures()

    def create_fixtures(self):
        super(TestGoodsUpdateAPI, self).create_fixtures()
        db_models.Goods(goods_id=GOODS_ID_101,
                        region_id='region_id_101',
                        goods_name='goods_name_101',
                        created_at=datetime.utcnow(),
                        deleted=False,
                        expansion_key1='expansion_key1',
                        expansion_key2='expansion_key2',
                        expansion_key3='expansion_key3',
                        expansion_key4='expansion_key4',
                        expansion_key5='expansion_key5',
                        expansion_text='expansion_text'
                        ).save(db_api.get_session())

        db_models.Goods(goods_id=GOODS_ID_102,
                        region_id='region_id_101',
                        goods_name='goods_name_102',
                        created_at=datetime.utcnow(),
                        deleted=False,
                        expansion_key1='expansion_key1',
                        expansion_key2='expansion_key2',
                        expansion_key3='expansion_key3',
                        expansion_key4='expansion_key4',
                        expansion_key5='expansion_key5',
                        expansion_text='expansion_text'
                        ).save(db_api.get_session())

        db_models.Goods(goods_id=GOODS_ID_103,
                        region_id='region_id_101',
                        goods_name='goods_name_103',
                        created_at=datetime.utcnow(),
                        deleted=False,
                        expansion_key1='expansion_key1',
                        expansion_key2='expansion_key2',
                        expansion_key3='expansion_key3',
                        expansion_key4='expansion_key4',
                        expansion_key5='expansion_key5',
                        expansion_text='expansion_text'
                        ).save(db_api.get_session())

        db_models.Goods(goods_id=GOODS_ID_104,
                        region_id='region_id_104',
                        goods_name='goods_name_104',
                        created_at=datetime.utcnow(),
                        deleted=False,
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

    def test_goods_update_with_no_auth(self):
        path = '/goods/%s' % GOODS_ID_101
        req = unit_test_utils.get_fake_request(method='PATCH', path=path)
        headers = {'x-auth-token': 'user:tenant:no_auth'}

        for k, v in headers.iteritems():
            req.headers[k] = v

        req.body = jsonutils.dumps(bo01)

        res = req.get_response(self.api)

        self.assertEqual(res.status_int, 403)

    def test_goods_update(self):
        path = '/goods/%s' % GOODS_ID_101
        req = unit_test_utils.get_fake_request(method='PATCH', path=path)
        headers = {'x-auth-token': 'user:tenant:admin'}

        for k, v in headers.iteritems():
            req.headers[k] = v

        req.body = jsonutils.dumps(bo01)

        res = req.get_response(self.api)
        goods = jsonutils.loads(res.body)['goods']

        self.assertEqual(res.status_int, 200)
        self.assertIsNotNone(goods['goods_id'])
        self.assertEqual(goods['region_id'], 'region_id_101_u')
        self.assertEqual(goods['goods_name'], 'goods_name_101_u')
        self.assertEqual(goods['expansions']['expansion_key1'],
                         'expansion_key1_u')
        self.assertEqual(goods['expansions']['expansion_key2'],
                         'expansion_key2_u_\"_\\_$_/_')
        self.assertEqual(goods['expansions']['expansion_key3'],
                         'expansion_key3_u')
        self.assertEqual(goods['expansions']['expansion_key4'],
                         'expansion_key4_u')
        self.assertEqual(goods['expansions']['expansion_key5'],
                         'expansion_key5_u')
        self.assertEqual(goods['expansions_text']['expansion_text'],
                         'expansion_text_u')
        self.assertIsNotNone(goods['created_at'])
        self.assertIsNotNone(goods['updated_at'])
        self.assertIsNone(goods['deleted_at'])
        self.assertEqual(goods['deleted'], False)

    def test_goods_update_with_no_keyword(self):
        path = '/goods/%s' % GOODS_ID_104
        req = unit_test_utils.get_fake_request(method='PATCH', path=path)
        headers = {'x-auth-token': 'user:tenant:admin'}

        for k, v in headers.iteritems():
            req.headers[k] = v

        req.body = jsonutils.dumps(bo04)

        res = req.get_response(self.api)
        goods = jsonutils.loads(res.body)['goods']

        self.assertEqual(res.status_int, 200)
        self.assertIsNotNone(goods['goods_id'])
        self.assertEqual(goods['region_id'], 'region_id_104')
        self.assertEqual(goods['goods_name'], 'goods_name_104')
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

    def test_goods_update_with_none_value(self):
        path = '/goods/%s' % GOODS_ID_102
        req = unit_test_utils.get_fake_request(method='PATCH', path=path)
        headers = {'x-auth-token': 'user:tenant:admin'}

        for k, v in headers.iteritems():
            req.headers[k] = v

        req.body = jsonutils.dumps(bo02)

        res = req.get_response(self.api)
        goods = jsonutils.loads(res.body)['goods']

        self.assertEqual(res.status_int, 200)
        self.assertIsNotNone(goods['goods_id'])
        self.assertIsNone(goods['region_id'])
        self.assertIsNone(goods['goods_name'])
        self.assertIsNotNone(goods['expansions'])
        self.assertIsNone(goods['expansions']['expansion_key1'])
        self.assertIsNone(goods['expansions']['expansion_key2'])
        self.assertIsNone(goods['expansions']['expansion_key3'])
        self.assertIsNone(goods['expansions']['expansion_key4'])
        self.assertIsNone(goods['expansions']['expansion_key5'])
        self.assertIsNotNone(goods['expansions_text'])
        self.assertIsNone(goods['expansions_text']['expansion_text'])
        self.assertIsNotNone(goods['created_at'])
        self.assertIsNotNone(goods['updated_at'])
        self.assertIsNone(goods['deleted_at'])
        self.assertEqual(goods['deleted'], False)

    def test_goods_update_goods_id_max_len_over(self):
        path = '/goods/%s' % ('a' * 65)
        req = unit_test_utils.get_fake_request(method='PATCH', path=path)
        headers = {'x-auth-token': 'user:tenant:admin'}

        for k, v in headers.iteritems():
            req.headers[k] = v

        req.body = jsonutils.dumps(bo01)

        res = req.get_response(self.api)
        self.assertEqual(res.status_int, 400)

    def test_goods_update_region_id_max_len_over(self):
        path = '/goods/%s' % GOODS_ID_103
        req = unit_test_utils.get_fake_request(method='PATCH', path=path)
        headers = {'x-auth-token': 'user:tenant:admin'}

        for k, v in headers.iteritems():
            req.headers[k] = v

        req.body = jsonutils.dumps(body_region_id_error)

        res = req.get_response(self.api)
        self.assertEqual(res.status_int, 400)

    def test_goods_update_goods_name_max_len_over(self):
        path = '/goods/%s' % GOODS_ID_103
        req = unit_test_utils.get_fake_request(method='PATCH', path=path)
        headers = {'x-auth-token': 'user:tenant:admin'}

        for k, v in headers.iteritems():
            req.headers[k] = v

        req.body = jsonutils.dumps(body_goods_name_error)

        res = req.get_response(self.api)
        self.assertEqual(res.status_int, 400)

    def test_goods_update_expansion_key1_max_len_over(self):
        path = '/goods/%s' % GOODS_ID_103
        req = unit_test_utils.get_fake_request(method='PATCH', path=path)
        headers = {'x-auth-token': 'user:tenant:admin'}

        for k, v in headers.iteritems():
            req.headers[k] = v

        req.body = jsonutils.dumps(body_expansion_key1_error)

        res = req.get_response(self.api)
        self.assertEqual(res.status_int, 400)

    def test_goods_update_expansion_key2_max_len_over(self):
        path = '/goods/%s' % GOODS_ID_103
        req = unit_test_utils.get_fake_request(method='PATCH', path=path)
        headers = {'x-auth-token': 'user:tenant:admin'}

        for k, v in headers.iteritems():
            req.headers[k] = v

        req.body = jsonutils.dumps(body_expansion_key2_error)

        res = req.get_response(self.api)
        self.assertEqual(res.status_int, 400)

    def test_goods_update_expansion_key3_max_len_over(self):
        path = '/goods/%s' % GOODS_ID_103
        req = unit_test_utils.get_fake_request(method='PATCH', path=path)
        headers = {'x-auth-token': 'user:tenant:admin'}

        for k, v in headers.iteritems():
            req.headers[k] = v

        req.body = jsonutils.dumps(body_expansion_key3_error)

        res = req.get_response(self.api)
        self.assertEqual(res.status_int, 400)

    def test_goods_update_expansion_key4_max_len_over(self):
        path = '/goods/%s' % GOODS_ID_103
        req = unit_test_utils.get_fake_request(method='PATCH', path=path)
        headers = {'x-auth-token': 'user:tenant:admin'}

        for k, v in headers.iteritems():
            req.headers[k] = v

        req.body = jsonutils.dumps(body_expansion_key4_error)

        res = req.get_response(self.api)
        self.assertEqual(res.status_int, 400)

    def test_goods_update_expansion_key5_max_len_over(self):
        path = '/goods/%s' % GOODS_ID_103
        req = unit_test_utils.get_fake_request(method='PATCH', path=path)
        headers = {'x-auth-token': 'user:tenant:admin'}

        for k, v in headers.iteritems():
            req.headers[k] = v

        req.body = jsonutils.dumps(body_expansion_key5_error)

        res = req.get_response(self.api)
        self.assertEqual(res.status_int, 400)

    def test_goods_update_expansion_text_max_len_over(self):
        path = '/goods/%s' % GOODS_ID_103
        req = unit_test_utils.get_fake_request(method='PATCH', path=path)
        headers = {'x-auth-token': 'user:tenant:admin'}

        for k, v in headers.iteritems():
            req.headers[k] = v

        req.body = jsonutils.dumps(body_expansion_text_error)

        res = req.get_response(self.api)
        self.assertEqual(res.status_int, 400)

    def test_goods_update_no_goods_id(self):
        path = '/goods/%s' % ''
        req = unit_test_utils.get_fake_request(method='PATCH', path=path)
        headers = {'x-auth-token': 'user:tenant:admin'}

        for k, v in headers.iteritems():
            req.headers[k] = v

        req.body = jsonutils.dumps(bo04)

        res = req.get_response(self.api)
        self.assertEqual(res.status_int, 404)
