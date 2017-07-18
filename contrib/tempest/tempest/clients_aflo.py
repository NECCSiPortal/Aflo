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

from tempest import clients  # noqa
from tempest.common import credentials_factory as cred_provider  # noqa
from tempest.services.aflo.json import aflo_client


class Manager(clients.Manager):
    def __init__(self, credentials=None, service=None):
        if credentials is None:
            credentials = cred_provider.get_configured_credentials('user')
        super(Manager, self).__init__(credentials, service)
        self.aflo_client = aflo_client.AfloClient(self.auth_provider)


class AdminManager(Manager):
    def __init__(self, service=None):
        super(AdminManager, self).__init__(
            cred_provider.get_configured_credentials('identity_admin'),
            service)
