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
#

from datetime import datetime
from oslo_config import cfg
from oslo_serialization import jsonutils
import routes

from aflo.api.v1 import router
from aflo.common import wsgi
from aflo import context
from aflo import db
from aflo.db.sqlalchemy import models as db_models
from aflo.db.sqlalchemy.models import CatalogScope
from aflo.tests.unit import base
import aflo.tests.unit.utils as unit_test_utils
from aflo.tests import utils as test_utils

CONF = cfg.CONF
db_api = db.get_api()

ID_101 = 'id0a4146-fd07-414b-aa5e-dedbeef00101'
ID_102 = 'id0a4146-fd07-414b-aa5e-dedbeef00102'
ID_103 = 'id0a4146-fd07-414b-aa5e-dedbeef00103'
ID_104 = 'id0a4146-fd07-414b-aa5e-dedbeef00104'
ID_105 = 'id0a4146-fd07-414b-aa5e-dedbeef00105'

CATALOG_ID_101 = 'ea0a4146-fd07-414b-aa5e-dedbeef00101'
CATALOG_ID_102 = 'ea0a4146-fd07-414b-aa5e-dedbeef00102'

SCOPE_101 = 'bdb8f50f82da4370813e6ea797b1fb101'
SCOPE_102 = 'bdb8f50f82da4370813e6ea797b1fb102'
SCOPE_DEF = 'Default'

body_normal = {
    "catalog_scope": {
        "lifetime_start": '2020-01-01T00:00:00.000000',
        "lifetime_end": '2024-12-31T23:59:59.999999',
        "expansions": {
            "expansion_key1": 'expansion_key1_update',
            "expansion_key2": 'expansion_key2_update',
            "expansion_key3": 'expansion_key3_update',
            "expansion_key4": 'expansion_key4_update',
            "expansion_key5": 'expansion_key5_update'
        },
        "expansions_text": {
            "expansion_text": 'expansion_text_update'
        }
    }
}
body_no_data = {
    "catalog_scope": {
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
body_no_keyword = {
    "catalog_scope": {}
}
body_lifetime_start_error = {
    "catalog_scope": {
        "lifetime_start": '2015-12-31T23:59:59',
        "lifetime_end": '9999-12-31T23:59:59.999999',
        "expansions": {
            "expansion_key1": 'expansion_key1',
            "expansion_key2": 'expansion_key2',
            "expansion_key3": 'expansion_key3',
            "expansion_key4": 'expansion_key4',
            "expansion_key5": 'expansion_key5'
        },
        "expansions_text": {
            "expansion_text": 'expansion_text'
        }
    }
}
body_lifetime_end_error = {
    "catalog_scope": {
        "lifetime_start": '2015-12-31T23:59:59.999999',
        "lifetime_end": '9999-12-31',
        "expansions": {
            "expansion_key1": 'expansion_key1',
            "expansion_key2": 'expansion_key2',
            "expansion_key3": 'expansion_key3',
            "expansion_key4": 'expansion_key4',
            "expansion_key5": 'expansion_key5'
        },
        "expansions_text": {
            "expansion_text": 'expansion_text'
        }
    }
}
body_lifetime_order_error = {
    "catalog_scope": {
        "lifetime_start": '2020-12-31T23:59:59.999999',
        "lifetime_end": '2019-12-31T23:59:59.999999',
        "expansions": {
            "expansion_key1": 'expansion_key1',
            "expansion_key2": 'expansion_key2',
            "expansion_key3": 'expansion_key3',
            "expansion_key4": 'expansion_key4',
            "expansion_key5": 'expansion_key5'
        },
        "expansions_text": {
            "expansion_text": 'expansion_text'
        }
    }
}
body_expansion_key1_error = {
    "catalog_scope": {
        "lifetime_start": '2015-12-31T23:59:59.999999',
        "lifetime_end": '9999-12-31T23:59:59.999999',
        "expansions": {
            "expansion_key1": 'a' * 256,
            "expansion_key2": 'expansion_key2',
            "expansion_key3": 'expansion_key3',
            "expansion_key4": 'expansion_key4',
            "expansion_key5": 'expansion_key5'
        },
        "expansions_text": {
            "expansion_text": 'expansion_text'
        }
    }
}
body_expansion_key2_error = {
    "catalog_scope": {
        "lifetime_start": '2015-12-31T23:59:59.999999',
        "lifetime_end": '9999-12-31T23:59:59.999999',
        "expansions": {
            "expansion_key1": 'expansion_key1',
            "expansion_key2": 'a' * 256,
            "expansion_key3": 'expansion_key3',
            "expansion_key4": 'expansion_key4',
            "expansion_key5": 'expansion_key5'
        },
        "expansions_text": {
            "expansion_text": 'expansion_text'
        }
    }
}
body_expansion_key3_error = {
    "catalog_scope": {
        "lifetime_start": '2015-12-31T23:59:59.999999',
        "lifetime_end": '9999-12-31T23:59:59.999999',
        "expansions": {
            "expansion_key1": 'expansion_key1',
            "expansion_key2": 'expansion_key2',
            "expansion_key3": 'a' * 256,
            "expansion_key4": 'expansion_key4',
            "expansion_key5": 'expansion_key5'
        },
        "expansions_text": {
            "expansion_text": 'expansion_text'
        }
    }
}
body_expansion_key4_error = {
    "catalog_scope": {
        "lifetime_start": '2015-12-31T23:59:59.999999',
        "lifetime_end": '9999-12-31T23:59:59.999999',
        "expansions": {
            "expansion_key1": 'expansion_key1',
            "expansion_key2": 'expansion_key2',
            "expansion_key3": 'expansion_key3',
            "expansion_key4": 'a' * 256,
            "expansion_key5": 'expansion_key5'
        },
        "expansions_text": {
            "expansion_text": 'expansion_text'
        }
    }
}
body_expansion_key5_error = {
    "catalog_scope": {
        "lifetime_start": '2015-12-31T23:59:59.999999',
        "lifetime_end": '9999-12-31T23:59:59.999999',
        "expansions": {
            "expansion_key1": 'expansion_key1',
            "expansion_key2": 'expansion_key2',
            "expansion_key3": 'expansion_key3',
            "expansion_key4": 'expansion_key4',
            "expansion_key5": 'a' * 256
        },
        "expansions_text": {
            "expansion_text": 'expansion_text'
        }
    }
}
body_expansion_text_error = {
    "catalog_scope": {
        "lifetime_start": '2015-12-31T23:59:59.999999',
        "lifetime_end": '9999-12-31T23:59:59.999999',
        "expansions": {
            "expansion_key1": 'expansion_key1',
            "expansion_key2": 'expansion_key2',
            "expansion_key3": 'expansion_key3',
            "expansion_key4": 'expansion_key4',
            "expansion_key5": 'expansion_key5'
        },
        "expansions_text": {
            "expansion_text": 'a' * 4001
        }
    }
}
body_catalog_id_scope = {
    "catalog_scope": {
        "catalog_id": CATALOG_ID_102,
        "scope": SCOPE_102,
        "lifetime_start": '2020-01-01T00:00:00.000000',
        "lifetime_end": '2024-12-31T23:59:59.999999',
        "expansions": {
            "expansion_key1": 'expansion_key1_update',
            "expansion_key2": 'expansion_key2_update',
            "expansion_key3": 'expansion_key3_update',
            "expansion_key4": 'expansion_key4_update',
            "expansion_key5": 'expansion_key5_update'
        },
        "expansions_text": {
            "expansion_text": 'expansion_text_update'
        }
    }
}


class TestAPI(base.WorkflowUnitTest):
    """Test 'Update a catalog scope"""

    def setUp(self):
        """Establish a clean test environment"""
        super(TestAPI, self).setUp()
        self.mapper = routes.Mapper()
        self.api = test_utils.FakeAuthMiddleware(router.API(self.mapper))

        self.context = context.RequestContext(is_admin=True)
        db_api.get_engine()
        self.destroy_fixtures()
        self.create_fixtures()
        self.serializer = wsgi.JSONResponseSerializer()

    def tearDown(self):
        """Clear the test environment"""
        super(TestAPI, self).tearDown()
        self.destroy_fixtures()

    def create_fixtures(self):
        CatalogScope(id=ID_101,
                     catalog_id=CATALOG_ID_101,
                     scope=SCOPE_101,
                     lifetime_start=datetime(2015, 12, 31, 23, 59, 59, 999999),
                     lifetime_end=datetime(9999, 12, 31, 23, 59, 59, 999999),
                     created_at=datetime.utcnow(),
                     updated_at=datetime.utcnow(),
                     deleted_at=None,
                     deleted=False,
                     expansion_key1='expansion_key1',
                     expansion_key2='expansion_key2',
                     expansion_key3='expansion_key3',
                     expansion_key4='expansion_key4',
                     expansion_key5='expansion_key5',
                     expansion_text='expansion_text'
                     ).save(db_api.get_session())

        CatalogScope(id=ID_102,
                     catalog_id=CATALOG_ID_101,
                     scope=SCOPE_102,
                     lifetime_start=datetime(2015, 12, 31, 23, 59, 59, 999999),
                     lifetime_end=datetime(9999, 12, 31, 23, 59, 59, 999999),
                     created_at=datetime.utcnow(),
                     updated_at=datetime.utcnow(),
                     deleted_at=None,
                     deleted=False,
                     expansion_key1='expansion_key1',
                     expansion_key2=None,
                     expansion_key3=None,
                     expansion_key4=None,
                     expansion_key5=None,
                     expansion_text='expansion_text'
                     ).save(db_api.get_session())

        CatalogScope(id=ID_103,
                     catalog_id=CATALOG_ID_101,
                     scope=SCOPE_DEF,
                     lifetime_start=datetime(2015, 12, 31, 23, 59, 59, 999999),
                     lifetime_end=datetime(9999, 12, 31, 23, 59, 59, 999999),
                     created_at=datetime.utcnow(),
                     updated_at=datetime.utcnow(),
                     deleted_at=None,
                     deleted=False,
                     expansion_key1=None,
                     expansion_key2=None,
                     expansion_key3=None,
                     expansion_key4=None,
                     expansion_key5=None,
                     expansion_text=None
                     ).save(db_api.get_session())

        CatalogScope(id=ID_104,
                     catalog_id=CATALOG_ID_101,
                     scope=SCOPE_DEF,
                     lifetime_start=datetime(2015, 12, 31, 23, 59, 59, 999999),
                     lifetime_end=datetime(9999, 12, 31, 23, 59, 59, 999999),
                     created_at=datetime.utcnow(),
                     updated_at=datetime.utcnow(),
                     deleted_at=None,
                     deleted=False,
                     expansion_key1='!"#$%&()=~|`{+*}<>?_',
                     expansion_key2='!"#$%&()=~|`{+*}<>?_',
                     expansion_key3='!"#$%&()=~|`{+*}<>?_',
                     expansion_key4='!"#$%&()=~|`{+*}<>?_',
                     expansion_key5='!"#$%&()=~|`{+*}<>?_',
                     expansion_text=',./\;:]@[\^-'
                     ).save(db_api.get_session())

    def destroy_fixtures(self):
        db_models.unregister_models(db_api.get_engine())
        db_models.register_models(db_api.get_engine())

    def test_catalog_scope_update_api(self):
        """Test 'Update a catalog scope'
        Test the operation of default.
        """

        path = '/catalogs/scope/%s' % ID_101
        req = unit_test_utils.get_fake_request(method='PATCH',
                                               path=path)
        headers = {'x-auth-token': 'user:tenant:admin'}
        for k, v in headers.iteritems():
            req.headers[k] = v

        req.body = jsonutils.dumps(body_normal)

        # Send request
        res = req.get_response(self.api)

        self.assertEqual(res.status_int, 200)

        catalog_scope = jsonutils.loads(res.body)['catalog_scope']

        self.assertEqual(catalog_scope['id'], ID_101)
        self.assertEqual(catalog_scope['catalog_id'], CATALOG_ID_101)
        self.assertEqual(catalog_scope['scope'], SCOPE_101)
        self.assertEqual(catalog_scope['lifetime_start'],
                         '2020-01-01T00:00:00.000000')
        self.assertEqual(catalog_scope['lifetime_end'],
                         '2024-12-31T23:59:59.999999')
        self.assertEqual(catalog_scope['expansions']['expansion_key1'],
                         'expansion_key1_update')
        self.assertEqual(catalog_scope['expansions']['expansion_key2'],
                         'expansion_key2_update')
        self.assertEqual(catalog_scope['expansions']['expansion_key3'],
                         'expansion_key3_update')
        self.assertEqual(catalog_scope['expansions']['expansion_key4'],
                         'expansion_key4_update')
        self.assertEqual(catalog_scope['expansions']['expansion_key5'],
                         'expansion_key5_update')
        self.assertEqual(catalog_scope['expansions_text']['expansion_text'],
                         'expansion_text_update')
        self.assertIsNotNone(catalog_scope['created_at'])
        self.assertIsNotNone(catalog_scope['updated_at'])
        self.assertIsNone(catalog_scope['deleted_at'])
        self.assertEqual(catalog_scope['deleted'], False)

    def test_catalog_scope_update_no_auth_irregular(self):
        """Test 'Update a catalog scope'
        Test cases run unauthorized.
        """

        path = '/catalogs/scope/%s' % ID_101
        req = unit_test_utils.get_fake_request(method='PATCH',
                                               path=path)
        headers = {'x-auth-token': 'user:tenant:__member__'}
        for k, v in headers.iteritems():
            req.headers[k] = v

        req.body = jsonutils.dumps(body_normal)

        # Send request
        res = req.get_response(self.api)

        self.assertEqual(res.status_int, 403)

    def test_catalog_scope_update_no_keyword(self):
        """Test 'Update a catalog scope'
        Test the operation with no parameters of the keyword.
        """

        path = '/catalogs/scope/%s' % ID_101
        req = unit_test_utils.get_fake_request(method='PATCH',
                                               path=path)
        headers = {'x-auth-token': 'user:tenant:admin'}
        for k, v in headers.iteritems():
            req.headers[k] = v

        req.body = jsonutils.dumps(body_no_keyword)

        # Send request
        res = req.get_response(self.api)

        self.assertEqual(res.status_int, 200)

        catalog_scope = jsonutils.loads(res.body)['catalog_scope']

        self.assertIsNotNone(catalog_scope['id'])
        self.assertEqual(catalog_scope['catalog_id'], CATALOG_ID_101)
        self.assertEqual(catalog_scope['scope'], SCOPE_101)
        self.assertEqual(catalog_scope['lifetime_start'],
                         '2015-12-31T23:59:59.999999')
        self.assertEqual(catalog_scope['lifetime_end'],
                         '9999-12-31T23:59:59.999999')
        self.assertEqual(catalog_scope['expansions']['expansion_key1'],
                         'expansion_key1')
        self.assertEqual(catalog_scope['expansions']['expansion_key2'],
                         'expansion_key2')
        self.assertEqual(catalog_scope['expansions']['expansion_key3'],
                         'expansion_key3')
        self.assertEqual(catalog_scope['expansions']['expansion_key4'],
                         'expansion_key4')
        self.assertEqual(catalog_scope['expansions']['expansion_key5'],
                         'expansion_key5')
        self.assertEqual(catalog_scope['expansions_text']['expansion_text'],
                         'expansion_text')
        self.assertIsNotNone(catalog_scope['created_at'])
        self.assertIsNotNone(catalog_scope['updated_at'])
        self.assertIsNone(catalog_scope['deleted_at'])
        self.assertEqual(catalog_scope['deleted'], False)

    def test_catalog_scope_update_none_value(self):
        """Test 'Update a catalog scope'
        Test the operation of the parameter is None.
        """

        path = '/catalogs/scope/%s' % ID_101
        req = unit_test_utils.get_fake_request(method='PATCH',
                                               path=path)
        headers = {'x-auth-token': 'user:tenant:admin'}
        for k, v in headers.iteritems():
            req.headers[k] = v

        req.body = jsonutils.dumps(body_no_data)

        # Send request
        res = req.get_response(self.api)

        self.assertEqual(res.status_int, 200)

        catalog_scope = jsonutils.loads(res.body)['catalog_scope']

        self.assertIsNotNone(catalog_scope['id'])
        self.assertEqual(catalog_scope['catalog_id'], CATALOG_ID_101)
        self.assertEqual(catalog_scope['scope'], SCOPE_101)
        self.assertIsNone(catalog_scope['lifetime_start'])
        self.assertIsNone(catalog_scope['lifetime_end'])
        self.assertIsNone(catalog_scope['expansions']['expansion_key1'])
        self.assertIsNone(catalog_scope['expansions']['expansion_key2'])
        self.assertIsNone(catalog_scope['expansions']['expansion_key3'])
        self.assertIsNone(catalog_scope['expansions']['expansion_key4'])
        self.assertIsNone(catalog_scope['expansions']['expansion_key5'])
        self.assertIsNone(catalog_scope['expansions_text']['expansion_text'])
        self.assertIsNotNone(catalog_scope['created_at'])
        self.assertIsNotNone(catalog_scope['updated_at'])
        self.assertIsNone(catalog_scope['deleted_at'])
        self.assertEqual(catalog_scope['deleted'], False)

    def test_catalog_scope_update_id_length_irregular(self):
        """Test 'Update a catalog scope'
        Test when the length of the id is invalid.
        """

        path = '/catalogs/scope/%s' % ('a' * 65)
        req = unit_test_utils.get_fake_request(method='PATCH',
                                               path=path)
        headers = {'x-auth-token': 'user:tenant:admin'}
        for k, v in headers.iteritems():
            req.headers[k] = v

        req.body = jsonutils.dumps(body_normal)

        # Send request
        res = req.get_response(self.api)

        self.assertEqual(res.status_int, 400)

    def test_catalog_scope_update_lifetime_start_datetime_irregular(self):
        """Test 'Update a catalog scope'
        Test when the lifetime_start is not datetime.
        """

        path = '/catalogs/scope/%s' % ID_101
        req = unit_test_utils.get_fake_request(method='PATCH',
                                               path=path)
        headers = {'x-auth-token': 'user:tenant:admin'}
        for k, v in headers.iteritems():
            req.headers[k] = v

        req.body = jsonutils.dumps(body_lifetime_start_error)

        # Send request
        res = req.get_response(self.api)

        self.assertEqual(res.status_int, 400)

    def test_catalog_scope_update_lifetime_end_datetime_irregular(self):
        """Test 'Update a catalog scope'
        Test when the lifetime_end is not datetime.
        """

        path = '/catalogs/scope/%s' % ID_101
        req = unit_test_utils.get_fake_request(method='PATCH',
                                               path=path)
        headers = {'x-auth-token': 'user:tenant:admin'}
        for k, v in headers.iteritems():
            req.headers[k] = v

        req.body = jsonutils.dumps(body_lifetime_end_error)

        # Send request
        res = req.get_response(self.api)

        self.assertEqual(res.status_int, 400)

    def test_catalog_scope_update_lifetime_order_irregular(self):
        """Test 'Update a catalog scope'
        Test when after lifetime_start is day than lifetime_end.
        """

        path = '/catalogs/scope/%s' % ID_101
        req = unit_test_utils.get_fake_request(method='PATCH',
                                               path=path)
        headers = {'x-auth-token': 'user:tenant:admin'}
        for k, v in headers.iteritems():
            req.headers[k] = v

        req.body = jsonutils.dumps(body_lifetime_order_error)

        # Send request
        res = req.get_response(self.api)

        self.assertEqual(res.status_int, 400)

    def test_catalog_scope_update_expansion_key1_length_irregular(self):
        """Test 'Update a catalog scope'
        Test when the length of the expansion_key1 is invalid.
        """

        path = '/catalogs/scope/%s' % ID_101
        req = unit_test_utils.get_fake_request(method='PATCH',
                                               path=path)
        headers = {'x-auth-token': 'user:tenant:admin'}
        for k, v in headers.iteritems():
            req.headers[k] = v

        req.body = jsonutils.dumps(body_expansion_key1_error)

        # Send request
        res = req.get_response(self.api)

        self.assertEqual(res.status_int, 400)

    def test_catalog_scope_update_expansion_key2_length_irregular(self):
        """Test 'Update a catalog scope'
        Test when the length of the expansion_key2 is invalid.
        """

        path = '/catalogs/scope/%s' % ID_101
        req = unit_test_utils.get_fake_request(method='PATCH',
                                               path=path)
        headers = {'x-auth-token': 'user:tenant:admin'}
        for k, v in headers.iteritems():
            req.headers[k] = v

        req.body = jsonutils.dumps(body_expansion_key2_error)

        # Send request
        res = req.get_response(self.api)

        self.assertEqual(res.status_int, 400)

    def test_catalog_scope_update_expansion_key3_length_irregular(self):
        """Test 'Update a catalog scope'
        Test when the length of the expansion_key3 is invalid.
        """

        path = '/catalogs/scope/%s' % ID_101
        req = unit_test_utils.get_fake_request(method='PATCH',
                                               path=path)
        headers = {'x-auth-token': 'user:tenant:admin'}
        for k, v in headers.iteritems():
            req.headers[k] = v

        req.body = jsonutils.dumps(body_expansion_key3_error)

        # Send request
        res = req.get_response(self.api)

        self.assertEqual(res.status_int, 400)

    def test_catalog_scope_update_expansion_key4_length_irregular(self):
        """Test 'Update a catalog scope'
        Test when the length of the expansion_key4 is invalid.
        """

        path = '/catalogs/scope/%s' % ID_101
        req = unit_test_utils.get_fake_request(method='PATCH',
                                               path=path)
        headers = {'x-auth-token': 'user:tenant:admin'}
        for k, v in headers.iteritems():
            req.headers[k] = v

        req.body = jsonutils.dumps(body_expansion_key4_error)

        # Send request
        res = req.get_response(self.api)

        self.assertEqual(res.status_int, 400)

    def test_catalog_scope_update_expansion_key5_length_irregular(self):
        """Test 'Update a catalog scope'
        Test when the length of the expansion_key5 is invalid.
        """

        path = '/catalogs/scope/%s' % ID_101
        req = unit_test_utils.get_fake_request(method='PATCH',
                                               path=path)
        headers = {'x-auth-token': 'user:tenant:admin'}
        for k, v in headers.iteritems():
            req.headers[k] = v

        req.body = jsonutils.dumps(body_expansion_key5_error)

        # Send request
        res = req.get_response(self.api)

        self.assertEqual(res.status_int, 400)

    def test_catalog_scope_update_expansion_text_length_irregular(self):
        """Test 'Update a catalog scope'
        Test when the length of the expansion_text is invalid.
        """

        path = '/catalogs/scope/%s' % ID_101
        req = unit_test_utils.get_fake_request(method='PATCH',
                                               path=path)
        headers = {'x-auth-token': 'user:tenant:admin'}
        for k, v in headers.iteritems():
            req.headers[k] = v

        req.body = jsonutils.dumps(body_expansion_text_error)

        # Send request
        res = req.get_response(self.api)

        self.assertEqual(res.status_int, 400)

    def test_catalog_scope_update_catalog_id_scope_update(self):
        """Test 'Update a catalog scope'
        Test when catalog_id and scope update.
        """

        path = '/catalogs/scope/%s' % ID_101
        req = unit_test_utils.get_fake_request(method='PATCH',
                                               path=path)
        headers = {'x-auth-token': 'user:tenant:admin'}
        for k, v in headers.iteritems():
            req.headers[k] = v

        req.body = jsonutils.dumps(body_catalog_id_scope)

        # Send request
        res = req.get_response(self.api)

        self.assertEqual(res.status_int, 200)

        catalog_scope = jsonutils.loads(res.body)['catalog_scope']

        self.assertEqual(catalog_scope['id'], ID_101)
        self.assertEqual(catalog_scope['catalog_id'], CATALOG_ID_101)
        self.assertEqual(catalog_scope['scope'], SCOPE_101)
        self.assertEqual(catalog_scope['lifetime_start'],
                         '2020-01-01T00:00:00.000000')
        self.assertEqual(catalog_scope['lifetime_end'],
                         '2024-12-31T23:59:59.999999')
        self.assertEqual(catalog_scope['expansions']['expansion_key1'],
                         'expansion_key1_update')
        self.assertEqual(catalog_scope['expansions']['expansion_key2'],
                         'expansion_key2_update')
        self.assertEqual(catalog_scope['expansions']['expansion_key3'],
                         'expansion_key3_update')
        self.assertEqual(catalog_scope['expansions']['expansion_key4'],
                         'expansion_key4_update')
        self.assertEqual(catalog_scope['expansions']['expansion_key5'],
                         'expansion_key5_update')
        self.assertEqual(catalog_scope['expansions_text']['expansion_text'],
                         'expansion_text_update')
        self.assertIsNotNone(catalog_scope['created_at'])
        self.assertIsNotNone(catalog_scope['updated_at'])
        self.assertIsNone(catalog_scope['deleted_at'])
        self.assertEqual(catalog_scope['deleted'], False)

    def test_catalog_scope_update_nodata_irregular(self):
        """Test 'Update a catalog scope'
        Test when the specified id does not exist.
        """

        path = '/catalogs/scope/%s' % ID_105
        req = unit_test_utils.get_fake_request(method='PATCH',
                                               path=path)
        headers = {'x-auth-token': 'user:tenant:admin'}
        for k, v in headers.iteritems():
            req.headers[k] = v

        req.body = jsonutils.dumps(body_normal)

        # Send request
        res = req.get_response(self.api)

        self.assertEqual(res.status_int, 404)

    def test_catalog_scope_update_uri_irregular(self):
        """Test 'Update a catalog scope'
        Test when the required parameter without.
        """

        path = '/catalogs/scope/%s' % ''
        req = unit_test_utils.get_fake_request(method='PATCH',
                                               path=path)
        headers = {'x-auth-token': 'user:tenant:admin'}
        for k, v in headers.iteritems():
            req.headers[k] = v

        req.body = jsonutils.dumps(body_normal)

        # Send request
        res = req.get_response(self.api)

        self.assertEqual(res.status_int, 404)
