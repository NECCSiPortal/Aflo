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

CATALOG_ID_101 = 'ea0a4146-fd07-414b-aa5e-dedbeef00101'
CATALOG_ID_102 = 'ea0a4146-fd07-414b-aa5e-dedbeef00102'
CATALOG_ID_103 = 'ea0a4146-fd07-414b-aa5e-dedbeef00103'
CATALOG_ID_104 = 'ea0a4146-fd07-414b-aa5e-dedbeef00104'

bo01 = {'catalog':
        {'region_id': 'region_id_101_u',
         'catalog_name': 'catalog_name_101_u',
         'lifetime_start': datetime(2015, 7, 9, 0, 0, 0, 0),
         'lifetime_end': datetime(2015, 8, 9, 0, 0, 0, 0),
         'deleted': True,
         'expansions':
         {'expansion_key1': 'expansion_key1_u',
          'expansion_key2': 'expansion_key2_u',
          'expansion_key3': 'expansion_key3_u',
          'expansion_key4': 'expansion_key4_u',
          'expansion_key5': 'expansion_key5_u'},
         'expansions_text':
         {'expansion_text': 'expansion_text_u'}
         }
        }

bo02 = {'catalog':
        {'region_id': None,
         'catalog_name': None,
         'lifetime_start': None,
         'lifetime_end': None,
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

bo04 = {'catalog': {}}

body_unsupported_field_error = \
    {'catalog':
     {'unsupported_field': None}
     }

body_region_id_error = \
    {'catalog':
     {'region_id': 'a' * 256,
      'catalog_name': None,
      'lifetime_start': None,
      'lifetime_end': None,
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

body_catalog_name_error = \
    {'catalog':
     {'region_id': None,
      'catalog_name': 'a' * 129,
      'lifetime_start': None,
      'lifetime_end': None,
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

body_lifetime_start_error = \
    {'catalog':
     {'region_id': None,
      'catalog_name': None,
      'lifetime_start': 'a',
      'lifetime_end': None,
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

body_lifetime_end_error = \
    {'catalog':
     {'region_id': None,
      'catalog_name': None,
      'lifetime_start': None,
      'lifetime_end': 'a',
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

body_lifetime_period_error = \
    {'catalog':
     {'lifetime_start': datetime(2015, 7, 9, 0, 0, 0, 0),
      'lifetime_end': datetime(2015, 7, 8, 0, 0, 0, 0)
      }
     }

body_expansion_key1_error = \
    {'catalog':
     {'region_id': None,
      'catalog_name': None,
      'lifetime_start': None,
      'lifetime_end': None,
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
    {'catalog':
     {'region_id': None,
      'catalog_name': None,
      'lifetime_start': None,
      'lifetime_end': None,
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
    {'catalog':
     {'region_id': None,
      'catalog_name': None,
      'lifetime_start': None,
      'lifetime_end': None,
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
    {'catalog':
     {'region_id': None,
      'catalog_name': None,
      'lifetime_start': None,
      'lifetime_end': None,
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
    {'catalog':
     {'region_id': None,
      'catalog_name': None,
      'lifetime_start': None,
      'lifetime_end': None,
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
    {'catalog':
     {'region_id': None,
      'catalog_name': None,
      'lifetime_start': None,
      'lifetime_end': None,
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


class TestCatalogUpdateAPI(base.WorkflowUnitTest):
    def setUp(self):
        """Establish a clean test environment"""
        super(TestCatalogUpdateAPI, self).setUp()
        self.mapper = routes.Mapper()
        self.api = test_utils.FakeAuthMiddleware(router.API(self.mapper))

        self.context = aflo.context.RequestContext(is_admin=True)
        db_api.get_engine()
        self.destroy_fixtures()
        self.create_fixtures()
        self.serializer = wsgi.JSONResponseSerializer()

    def tearDown(self):
        """Clear the test environment"""
        super(TestCatalogUpdateAPI, self).tearDown()
        self.destroy_fixtures()

    def create_fixtures(self):
        super(TestCatalogUpdateAPI, self).create_fixtures()
        db_models.Catalog(catalog_id=CATALOG_ID_101,
                          region_id='region_id_101',
                          catalog_name='catalog_name_101',
                          lifetime_start=get_datetime('2015-07-01'),
                          lifetime_end=get_datetime('2015-08-01'),
                          created_at=datetime.utcnow(),
                          expansion_key1='expansion_key1',
                          expansion_key2='expansion_key2',
                          expansion_key3='expansion_key3',
                          expansion_key4='expansion_key4',
                          expansion_key5='expansion_key5',
                          expansion_text='expansion_text'
                          ).save(db_api.get_session())

        db_models.Catalog(catalog_id=CATALOG_ID_102,
                          region_id='region_id_101',
                          catalog_name='catalog_name_102',
                          lifetime_start=get_datetime('2015-07-02'),
                          lifetime_end=get_datetime('2015-08-02'),
                          created_at=datetime.utcnow(),
                          expansion_key1='expansion_key1',
                          expansion_key2='expansion_key2',
                          expansion_key3='expansion_key3',
                          expansion_key4='expansion_key4',
                          expansion_key5='expansion_key5',
                          expansion_text='expansion_text'
                          ).save(db_api.get_session())

        db_models.Catalog(catalog_id=CATALOG_ID_103,
                          region_id='region_id_101',
                          catalog_name='catalog_name_103',
                          lifetime_start=get_datetime('2015-07-03'),
                          lifetime_end=get_datetime('2015-08-03'),
                          created_at=datetime.utcnow(),
                          expansion_key1='expansion_key1',
                          expansion_key2='expansion_key2',
                          expansion_key3='expansion_key3',
                          expansion_key4='expansion_key4',
                          expansion_key5='expansion_key5',
                          expansion_text='expansion_text'
                          ).save(db_api.get_session())

        db_models.Catalog(catalog_id=CATALOG_ID_104,
                          region_id='region_id_104',
                          catalog_name='catalog_name_104',
                          lifetime_start=get_datetime('2015-07-04'),
                          lifetime_end=get_datetime('2015-08-04'),
                          created_at=datetime.utcnow(),
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

    def test_catalog_update_with_no_auth(self):
        path = '/catalog/%s' % CATALOG_ID_101
        req = unit_test_utils.get_fake_request(method='PATCH', path=path)
        headers = {'x-auth-token': 'user:tenant:no_auth'}

        for k, v in headers.iteritems():
            req.headers[k] = v

        req.body = jsonutils.dumps(bo01)

        res = req.get_response(self.api)

        self.assertEqual(res.status_int, 403)

    def test_catalog_update(self):
        path = '/catalog/%s' % CATALOG_ID_101
        req = unit_test_utils.get_fake_request(method='PATCH', path=path)
        headers = {'x-auth-token': 'user:tenant:admin'}

        for k, v in headers.iteritems():
            req.headers[k] = v

        req.body = jsonutils.dumps(bo01)

        res = req.get_response(self.api)
        catalog = jsonutils.loads(res.body)['catalog']

        self.assertEqual(res.status_int, 200)
        self.assertIsNotNone(catalog['catalog_id'])
        self.assertEqual(catalog['region_id'], 'region_id_101_u')
        self.assertEqual(catalog['catalog_name'], 'catalog_name_101_u')
        lifetime_start = datetime.strptime(catalog['lifetime_start'],
                                           '%Y-%m-%dT%H:%M:%S.%f')
        self.assertEqual(lifetime_start, datetime(2015, 7, 9, 0, 0, 0, 0))
        lifetime_end = datetime.strptime(catalog['lifetime_end'],
                                         '%Y-%m-%dT%H:%M:%S.%f')
        self.assertEqual(lifetime_end, datetime(2015, 8, 9, 0, 0, 0, 0))
        self.assertEqual(catalog['expansions']['expansion_key1'],
                         'expansion_key1_u')
        self.assertEqual(catalog['expansions']['expansion_key2'],
                         'expansion_key2_u')
        self.assertEqual(catalog['expansions']['expansion_key3'],
                         'expansion_key3_u')
        self.assertEqual(catalog['expansions']['expansion_key4'],
                         'expansion_key4_u')
        self.assertEqual(catalog['expansions']['expansion_key5'],
                         'expansion_key5_u')
        self.assertEqual(catalog['expansions_text']['expansion_text'],
                         'expansion_text_u')
        self.assertIsNotNone(catalog['created_at'])
        self.assertIsNotNone(catalog['updated_at'])
        self.assertIsNone(catalog['deleted_at'])
        self.assertEqual(catalog['deleted'], False)

    def test_catalog_update_no_keyword(self):
        path = '/catalog/%s' % CATALOG_ID_104
        req = unit_test_utils.get_fake_request(method='PATCH', path=path)
        headers = {'x-auth-token': 'user:tenant:admin'}

        for k, v in headers.iteritems():
            req.headers[k] = v

        req.body = jsonutils.dumps(bo04)

        res = req.get_response(self.api)
        catalog = jsonutils.loads(res.body)['catalog']

        self.assertEqual(res.status_int, 200)
        self.assertIsNotNone(catalog['catalog_id'])
        self.assertEqual(catalog['region_id'], 'region_id_104')
        self.assertEqual(catalog['catalog_name'], 'catalog_name_104')
        lifetime_start = datetime.strptime(catalog['lifetime_start'],
                                           '%Y-%m-%dT%H:%M:%S.%f')
        self.assertEqual(lifetime_start, datetime(2015, 7, 4, 0, 0, 0, 0))
        lifetime_end = datetime.strptime(catalog['lifetime_end'],
                                         '%Y-%m-%dT%H:%M:%S.%f')
        self.assertEqual(lifetime_end, datetime(2015, 8, 4, 0, 0, 0, 0))
        self.assertEqual(catalog['expansions']['expansion_key1'],
                         'expansion_key1')
        self.assertEqual(catalog['expansions']['expansion_key2'],
                         'expansion_key2')
        self.assertEqual(catalog['expansions']['expansion_key3'],
                         'expansion_key3')
        self.assertEqual(catalog['expansions']['expansion_key4'],
                         'expansion_key4')
        self.assertEqual(catalog['expansions']['expansion_key5'],
                         'expansion_key5')
        self.assertEqual(catalog['expansions_text']['expansion_text'],
                         'expansion_text')
        self.assertIsNotNone(catalog['created_at'])
        self.assertIsNotNone(catalog['updated_at'])
        self.assertIsNone(catalog['deleted_at'])
        self.assertEqual(catalog['deleted'], False)

    def test_catalog_update_with_none_value(self):
        path = '/catalog/%s' % CATALOG_ID_102
        req = unit_test_utils.get_fake_request(method='PATCH', path=path)
        headers = {'x-auth-token': 'user:tenant:admin'}

        for k, v in headers.iteritems():
            req.headers[k] = v

        req.body = jsonutils.dumps(bo02)

        res = req.get_response(self.api)
        catalog = jsonutils.loads(res.body)['catalog']

        self.assertEqual(res.status_int, 200)
        self.assertIsNotNone(catalog['catalog_id'])
        self.assertIsNone(catalog['region_id'])
        self.assertIsNone(catalog['catalog_name'])
        self.assertIsNone(catalog['lifetime_start'])
        self.assertIsNone(catalog['lifetime_end'])
        self.assertIsNotNone(catalog['expansions'])
        self.assertIsNone(catalog['expansions']['expansion_key1'])
        self.assertIsNone(catalog['expansions']['expansion_key2'])
        self.assertIsNone(catalog['expansions']['expansion_key3'])
        self.assertIsNone(catalog['expansions']['expansion_key4'])
        self.assertIsNone(catalog['expansions']['expansion_key5'])
        self.assertIsNotNone(catalog['expansions_text'])
        self.assertIsNone(catalog['expansions_text']['expansion_text'])
        self.assertIsNotNone(catalog['created_at'])
        self.assertIsNotNone(catalog['updated_at'])
        self.assertIsNone(catalog['deleted_at'])
        self.assertEqual(catalog['deleted'], False)

    def test_catalog_update_unsuported_field(self):
        path = '/catalog/%s' % CATALOG_ID_103
        req = unit_test_utils.get_fake_request(method='PATCH', path=path)
        headers = {'x-auth-token': 'user:tenant:admin'}

        for k, v in headers.iteritems():
            req.headers[k] = v

        req.body = jsonutils.dumps(body_unsupported_field_error)

        res = req.get_response(self.api)
        self.assertEqual(res.status_int, 400)

    def test_catalog_update_region_id_error(self):
        path = '/catalog/%s' % CATALOG_ID_103
        req = unit_test_utils.get_fake_request(method='PATCH', path=path)
        headers = {'x-auth-token': 'user:tenant:admin'}

        for k, v in headers.iteritems():
            req.headers[k] = v

        req.body = jsonutils.dumps(body_region_id_error)

        res = req.get_response(self.api)
        self.assertEqual(res.status_int, 400)

    def test_catalog_update_catalog_name_error(self):
        path = '/catalog/%s' % CATALOG_ID_103
        req = unit_test_utils.get_fake_request(method='PATCH', path=path)
        headers = {'x-auth-token': 'user:tenant:admin'}

        for k, v in headers.iteritems():
            req.headers[k] = v

        req.body = jsonutils.dumps(body_catalog_name_error)

        res = req.get_response(self.api)
        self.assertEqual(res.status_int, 400)

    def test_catalog_update_lifetime_start_error(self):
        path = '/catalog/%s' % CATALOG_ID_103
        req = unit_test_utils.get_fake_request(method='PATCH', path=path)
        headers = {'x-auth-token': 'user:tenant:admin'}

        for k, v in headers.iteritems():
            req.headers[k] = v

        req.body = jsonutils.dumps(body_lifetime_start_error)

        res = req.get_response(self.api)
        self.assertEqual(res.status_int, 400)

    def test_catalog_update_lifetime_end_error(self):
        path = '/catalog/%s' % CATALOG_ID_103
        req = unit_test_utils.get_fake_request(method='PATCH', path=path)
        headers = {'x-auth-token': 'user:tenant:admin'}

        for k, v in headers.iteritems():
            req.headers[k] = v

        req.body = jsonutils.dumps(body_lifetime_end_error)

        res = req.get_response(self.api)
        self.assertEqual(res.status_int, 400)

    def test_catalog_update_lifetime_period_error(self):
        path = '/catalog/%s' % CATALOG_ID_103
        req = unit_test_utils.get_fake_request(method='PATCH', path=path)
        headers = {'x-auth-token': 'user:tenant:admin'}

        for k, v in headers.iteritems():
            req.headers[k] = v

        req.body = jsonutils.dumps(body_lifetime_period_error)

        res = req.get_response(self.api)
        self.assertEqual(res.status_int, 400)

    def test_catalog_update_expansion_key1_error(self):
        path = '/catalog/%s' % CATALOG_ID_103
        req = unit_test_utils.get_fake_request(method='PATCH', path=path)
        headers = {'x-auth-token': 'user:tenant:admin'}

        for k, v in headers.iteritems():
            req.headers[k] = v

        req.body = jsonutils.dumps(body_expansion_key1_error)

        res = req.get_response(self.api)
        self.assertEqual(res.status_int, 400)

    def test_catalog_update_expansion_key2_error(self):
        """Test update a catalog for expansion_key2 error."""
        path = '/catalog/%s' % CATALOG_ID_103
        req = unit_test_utils.get_fake_request(method='PATCH', path=path)
        headers = {'x-auth-token': 'user:tenant:admin'}

        for k, v in headers.iteritems():
            req.headers[k] = v

        req.body = jsonutils.dumps(body_expansion_key2_error)

        res = req.get_response(self.api)
        self.assertEqual(res.status_int, 400)

    def test_catalog_update_expansion_key3_error(self):
        path = '/catalog/%s' % CATALOG_ID_103
        req = unit_test_utils.get_fake_request(method='PATCH', path=path)
        headers = {'x-auth-token': 'user:tenant:admin'}

        for k, v in headers.iteritems():
            req.headers[k] = v

        req.body = jsonutils.dumps(body_expansion_key3_error)

        res = req.get_response(self.api)
        self.assertEqual(res.status_int, 400)

    def test_catalog_update_expansion_key4_error(self):
        path = '/catalog/%s' % CATALOG_ID_103
        req = unit_test_utils.get_fake_request(method='PATCH', path=path)
        headers = {'x-auth-token': 'user:tenant:admin'}

        for k, v in headers.iteritems():
            req.headers[k] = v

        req.body = jsonutils.dumps(body_expansion_key4_error)

        res = req.get_response(self.api)
        self.assertEqual(res.status_int, 400)

    def test_catalog_update_expansion_key5_error(self):
        path = '/catalog/%s' % CATALOG_ID_103
        req = unit_test_utils.get_fake_request(method='PATCH', path=path)
        headers = {'x-auth-token': 'user:tenant:admin'}

        for k, v in headers.iteritems():
            req.headers[k] = v

        req.body = jsonutils.dumps(body_expansion_key5_error)

        res = req.get_response(self.api)
        self.assertEqual(res.status_int, 400)

    def test_catalog_update_expansion_text_error(self):
        path = '/catalog/%s' % CATALOG_ID_103
        req = unit_test_utils.get_fake_request(method='PATCH', path=path)
        headers = {'x-auth-token': 'user:tenant:admin'}

        for k, v in headers.iteritems():
            req.headers[k] = v

        req.body = jsonutils.dumps(body_expansion_text_error)

        res = req.get_response(self.api)
        self.assertEqual(res.status_int, 400)

    def test_catalog_update_no_catalog_id(self):
        path = '/catalog/%s' % ''
        req = unit_test_utils.get_fake_request(method='PATCH', path=path)
        headers = {'x-auth-token': 'user:tenant:admin'}

        for k, v in headers.iteritems():
            req.headers[k] = v

        req.body = jsonutils.dumps(bo01)

        res = req.get_response(self.api)
        self.assertEqual(res.status_int, 404)

    def test_catalog_update_catalog_id_length(self):
        """Test 'Update of catalog'
        Test of catalog_id is over length.
        """
        path = '/catalog/%s' % ('a' * 65)
        req = unit_test_utils.get_fake_request(method='GET',
                                               path=path)

        headers = {'x-auth-token': 'user:tenant:developer'}
        for k, v in headers.iteritems():
            req.headers[k] = v

        # Send request
        res = req.get_response(self.api)

        # Examination of response
        self.assertEqual(res.status_int, 400)
