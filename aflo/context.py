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

from oslo_context import context

from aflo.api import policy


class RequestContext(context.RequestContext):
    """Stores information about the security context.

    Stores how the user accesses the system, as well as additional request
    information.

    """

    def __init__(self, roles=None, service_catalog=None,
                 policy_enforcer=None, user_name=None,
                 tenant_name=None, **kwargs):
        super(RequestContext, self).__init__(**kwargs)
        self.roles = roles or []
        self.service_catalog = service_catalog
        self.policy_enforcer = policy_enforcer or policy.Enforcer()
        self.user_name = user_name
        self.tenant_name = tenant_name
        if not self.is_admin:
            self.is_admin = self.policy_enforcer.check_is_admin(self)

    def to_dict(self):
        d = super(RequestContext, self).to_dict()
        d.update({
            'roles': self.roles,
            'service_catalog': self.service_catalog,
            'user_name': self.user_name,
            'tenant_name': self.tenant_name
        })
        return d

    @classmethod
    def from_dict(cls, values):
        c = super(RequestContext, cls).from_dict(values)
        c.roles = values['roles']
        c.service_catalog = values['service_catalog']
        c.user_name = values['user_name']
        c.tenant_name = values['tenant_name']
        return c

    @property
    def can_see_deleted(self):
        """Admins can see deleted by default"""
        return self.show_deleted or self.is_admin
