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

import webob

from aflo.api.middleware import context
import aflo.context
from aflo.tests.unit import base


class TestContextMiddleware(base.IsolatedUnitTest):
    def _build_request(self, roles=None, identity_status='Confirmed',
                       service_catalog=None):
        req = webob.Request.blank('/')
        req.headers['x-auth-token'] = 'token1'
        req.headers['x-identity-status'] = identity_status
        req.headers['x-user-id'] = 'user1'
        req.headers['x-tenant-id'] = 'tenant1'
        _roles = roles or ['role1', 'role2']
        req.headers['x-roles'] = ','.join(_roles)
        if service_catalog:
            req.headers['x-service-catalog'] = service_catalog
        req.headers['x-user-name'] = 'user1_name'
        req.headers['x-tenant-name'] = 'tenant1_name'

        return req

    def _build_middleware(self):
        return context.ContextMiddleware(None)

    def test_header_parsing(self):
        req = self._build_request()
        self._build_middleware().process_request(req)
        self.assertEqual('token1', req.context.auth_token)
        self.assertEqual('user1', req.context.user)
        self.assertEqual('tenant1', req.context.tenant)
        self.assertEqual(['role1', 'role2'], req.context.roles)
        self.assertEqual('user1_name', req.context.user_name)
        self.assertEqual('tenant1_name', req.context.tenant_name)

    def test_is_admin_flag(self):
        # is_admin check should look for 'admin' role by default
        req = self._build_request(roles=['admin', 'role2'])
        self._build_middleware().process_request(req)
        self.assertTrue(req.context.is_admin)

        # without the 'admin' role, is_admin should be False
        req = self._build_request()
        self._build_middleware().process_request(req)
        self.assertFalse(req.context.is_admin)

        # if we change the admin_role attribute, we should be able to use it
        req = self._build_request()
        self.config(admin_role='role1')
        self._build_middleware().process_request(req)
        self.assertTrue(req.context.is_admin)

    def test_roles_case_insensitive(self):
        # accept role from request
        req = self._build_request(roles=['Admin', 'role2'])
        self._build_middleware().process_request(req)
        self.assertTrue(req.context.is_admin)

        # accept role from config
        req = self._build_request(roles=['role1'])
        self.config(admin_role='role1')
        self._build_middleware().process_request(req)
        self.assertTrue(req.context.is_admin)

    def test_roles_stripping(self):
        # stripping extra spaces in request
        req = self._build_request(roles=['\trole1'])
        self.config(admin_role='role1')
        self._build_middleware().process_request(req)
        self.assertTrue(req.context.is_admin)

        # stripping extra spaces in config
        req = self._build_request(roles=['\trole1\n'])
        self.config(admin_role=' role1\t')
        self._build_middleware().process_request(req)
        self.assertTrue(req.context.is_admin)

    def test_anonymous_access_defaults_to_disabled(self):
        req = self._build_request(identity_status='Nope')
        middleware = self._build_middleware()
        self.assertRaises(webob.exc.HTTPUnauthorized,
                          middleware.process_request, req)

    def test_service_catalog(self):
        catalog_json = "[{}]"
        req = self._build_request(service_catalog=catalog_json)
        self._build_middleware().process_request(req)
        self.assertEqual([{}], req.context.service_catalog)

    def test_invalid_service_catalog(self):
        catalog_json = "bad json"
        req = self._build_request(service_catalog=catalog_json)
        middleware = self._build_middleware()
        self.assertRaises(webob.exc.HTTPInternalServerError,
                          middleware.process_request, req)


class TestUnauthenticatedContextMiddleware(base.IsolatedUnitTest):
    def test_request(self):
        middleware = context.UnauthenticatedContextMiddleware(None)
        req = webob.Request.blank('/')
        middleware.process_request(req)
        self.assertIsNone(req.context.auth_token)
        self.assertIsNone(req.context.user)
        self.assertIsNone(req.context.tenant)
        self.assertEqual([], req.context.roles)
        self.assertTrue(req.context.is_admin)
        self.assertIsNone(req.context.user_name)
        self.assertIsNone(req.context.tenant_name)

    def test_response(self):
        middleware = context.UnauthenticatedContextMiddleware(None)
        req = webob.Request.blank('/')
        req.context = aflo.context.RequestContext()
        request_id = req.context.request_id

        resp = webob.Response()
        resp.request = req
        middleware.process_response(resp)
        self.assertEqual(resp.headers['x-openstack-request-id'],
                         'req-%s' % request_id)
