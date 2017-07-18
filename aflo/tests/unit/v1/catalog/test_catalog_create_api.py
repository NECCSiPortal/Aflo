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

bo01 = {'catalog':
        {'region_id': 'region_id_101_u',
         'catalog_name': 'catalog_name_101_u',
         'lifetime_start': None,
         'lifetime_end': None,
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


class TestCatalogCreateAPI(base.WorkflowUnitTest):
    """Do a test of 'Create a new catalog'"""

    def setUp(self):
        """Establish a clean test environment"""
        super(TestCatalogCreateAPI, self).setUp()
        self.mapper = routes.Mapper()
        self.api = test_utils.FakeAuthMiddleware(router.API(self.mapper))

        self.context = aflo.context.RequestContext(is_admin=True)
        db_api.get_engine()
        self.destroy_fixtures()
        self.create_fixtures()
        self.serializer = wsgi.JSONResponseSerializer()

    def tearDown(self):
        """Clear the test environment"""
        super(TestCatalogCreateAPI, self).tearDown()
        self.destroy_fixtures()

    def create_fixtures(self):
        super(TestCatalogCreateAPI, self).create_fixtures()

    def destroy_fixtures(self):
        # Easiest to just drop the models and re-create them...
        db_models.unregister_models(db_api.get_engine())
        db_models.register_models(db_api.get_engine())

    def test_create(self):
        """Do a test of 'Create a new catalog'
        """

        # Create a request data
        path = '/catalog'
        req = unit_test_utils.get_fake_request(method='POST',
                                               path=path)
        headers = {'x-auth-token': 'user:tenant:admin',
                   'x-user-name': 'user-name',
                   'x-tenant-name': 'tenant-name'}
        for k, v in headers.iteritems():
            req.headers[k] = v

        req.body = '{"catalog": { ' \
                   '    "region_id": "region_id_101", ' \
                   '    "catalog_name": "test_catalog", ' \
                   '    "lifetime_start": "2999-12-31T23:59:59.999999", ' \
                   '    "lifetime_end": "9999-12-31T23:59:59.999999", ' \
                   '    "deleted": "True", ' \
                   '    "expansions": { ' \
                   '        "expansion_key1": "expansion_key1", ' \
                   '        "expansion_key2": "expansion_key2", ' \
                   '        "expansion_key3": "expansion_key3", ' \
                   '        "expansion_key4": "expansion_key4", ' \
                   '        "expansion_key5": "expansion_key5" ' \
                   '     }, ' \
                   '     "expansions_text": ' \
                   '         {"expansion_text": "expansion_text"} }}'

        # Send request
        res = req.get_response(self.api)

        # Examination of response
        self.assertEqual(res.status_int, 200)

        catalog = jsonutils.loads(res.body)['catalog']

        self.assertIsNotNone(catalog['catalog_id'])
        self.assertEqual(catalog['region_id'], 'region_id_101')
        self.assertEqual(catalog['catalog_name'], 'test_catalog')
        self.assertEqual(catalog['lifetime_start'],
                         '2999-12-31T23:59:59.999999')
        self.assertEqual(catalog['lifetime_end'], '9999-12-31T23:59:59.999999')
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

    def test_create_region_id_error(self):
        """Test of 'Create a new catalog'
        Test with region_id is over length.
        """

        # Create a request data
        path = '/catalog'
        req = unit_test_utils.get_fake_request(method='POST',
                                               path=path)
        headers = {'x-auth-token': 'user:tenant:admin',
                   'x-user-name': 'user-name',
                   'x-tenant-name': 'tenant-name'}
        for k, v in headers.iteritems():
            req.headers[k] = v

        req.body = jsonutils.dumps(body_region_id_error)

        # Send request
        res = req.get_response(self.api)

        # Examination of response
        self.assertEqual(res.status_int, 400)

    def test_create_catalog_name_error(self):
        """Test of 'Create a new catalog'
        Test with catalog_name is over length.
        """

        # Create a request data
        path = '/catalog'
        req = unit_test_utils.get_fake_request(method='POST',
                                               path=path)
        headers = {'x-auth-token': 'user:tenant:admin',
                   'x-user-name': 'user-name',
                   'x-tenant-name': 'tenant-name'}
        for k, v in headers.iteritems():
            req.headers[k] = v

        req.body = jsonutils.dumps(body_catalog_name_error)

        # Send request
        res = req.get_response(self.api)

        # Examination of response
        self.assertEqual(res.status_int, 400)

    def test_create_lifetime_start_error(self):
        """Test of 'Create a new catalog'
        Test with lifetime_start is not datetime.
        """

        # Create a request data
        path = '/catalog'
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
        """Test of 'Create a new catalog'
        Test with lifetime_end is not datetime.
        """

        # Create a request data
        path = '/catalog'
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
        """Test of 'Create a new catalog'
        Test with expansion_key1 is over length.
        """

        # Create a request data
        path = '/catalog'
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
        """Test of 'Create a new catalog'
        Test with expansion_key2 is over length.
        """

        # Create a request data
        path = '/catalog'
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
        """Test of 'Create a new catalog'
        Test with expansion_key3 is over length.
        """

        # Create a request data
        path = '/catalog'
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
        """Test of 'Create a new catalog'
        Test with expansion_key4 is over length.
        """

        # Create a request data
        path = '/catalog'
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
        """Test of 'Create a new catalog'
        Test with expansion_key5 is over length.
        """

        # Create a request data
        path = '/catalog'
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
        """Test of 'Create a new catalog'
        Test with expansion_text is over length.
        """

        # Create a request data
        path = '/catalog'
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
