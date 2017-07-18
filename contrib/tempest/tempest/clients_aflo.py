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
from tempest import config
from tempest import exceptions
from tempest.services.aflo.json import aflo_client

CONF = config.CONF

DEFAULT_PARAMS = {
    'disable_ssl_certificate_validation':
        CONF.identity.disable_ssl_certificate_validation,
    'ca_certs': CONF.identity.ca_certificates_file,
    'trace_requests': CONF.debug.trace_requests
}


class Manager(clients.Manager):
    def __init__(self, credentials=None, service=None):
        if credentials is None:
            credentials = self._get_configured_demo_credentials()
        super(Manager, self).__init__(credentials, service)
        self.aflo_client = aflo_client.AfloClient(self.auth_provider)

    # Read credentials from configuration, builds a Credentials object
    # based on the specified or configured version
    def _get_configured_demo_credentials(
            self, fill_in=True, identity_version=None):
        identity_version = identity_version or CONF.identity.auth_version

        if identity_version not in ('v2', 'v3'):
            raise exceptions.InvalidConfiguration(
                'Unsupported auth version: %s' % identity_version)

        conf_attributes = ['username', 'password',
                           'project_name']

        if identity_version == 'v3':
            conf_attributes.append('domain_name')
        # Read the parts of credentials from config
        params = DEFAULT_PARAMS.copy()
        for attr in conf_attributes:
            params[attr] = getattr(CONF.aflo, 'demo_' + attr)
        # Build and validate credentials.
        # We are reading configured credentials,
        # so validate them even if fill_in is False.
        credentials = cred_provider.get_credentials(
            fill_in=fill_in, identity_version=identity_version, **params)
        if not fill_in:
            if not credentials.is_valid():
                msg = (
                    "The admin credentials are incorrectly set in the config "
                    "file for identity version %s. Double check that all "
                    "required values are assigned.")
                raise exceptions.InvalidConfiguration(msg % identity_version)
        return credentials


class AdminManager(Manager):
    def __init__(self, service=None):
        super(AdminManager, self).__init__(
            cred_provider.get_configured_admin_credentials(),
            service)
