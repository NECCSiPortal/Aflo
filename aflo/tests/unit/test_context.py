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

import os.path

import aflo.api.policy
import aflo.context
from aflo.tests.unit import base


class TestContext(base.IsolatedUnitTest):

    def test_context_admin_policy_admin(self):
        user = 'test_user_id'
        tenant = 'test_tenant_id'
        user_name = 'test_user'
        tenant_name = 'test_tenant'

        self.config(policy_file=os.path.join(self.test_dir, 'gobble.gobble'),
                    group='oslo_policy')

        rules = {'context_is_admin': 'role:test_admin'}
        self.set_policy_rules(rules)

        enforcer = aflo.api.policy.Enforcer()

        context = aflo.context.RequestContext(roles=['test_admin'],
                                              is_admin=True,
                                              policy_enforcer=enforcer,
                                              user=user,
                                              tenant=tenant,
                                              user_name=user_name,
                                              tenant_name=tenant_name)

        ctx_dict = context.to_dict()
        self.assertEqual(user, ctx_dict['user'])
        self.assertEqual(tenant, ctx_dict['tenant'])
        self.assertEqual(user_name, ctx_dict['user_name'])
        self.assertEqual(tenant_name, ctx_dict['tenant_name'])

        ctx_cls = aflo.context.RequestContext.from_dict(ctx_dict)
        self.assertEqual(user, ctx_cls.user)
        self.assertEqual(tenant, ctx_cls.tenant)
        self.assertEqual(user_name, ctx_cls.user_name)
        self.assertEqual(tenant_name, ctx_cls.tenant_name)
