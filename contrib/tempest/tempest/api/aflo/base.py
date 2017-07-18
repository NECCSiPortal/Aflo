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

from oslo_log import log  # noqa

from tempest import clients_aflo as clients
from tempest import config_aflo as config
from tempest import exceptions  # noqa
from tempest import test  # noqa

CONF = config.CONF
LOG = log.getLogger(__name__)


class BaseAfloTest(test.BaseTestCase):
    """Base test class for AFLO API tests."""

    credentials = ['admin', 'primary']

    @classmethod
    def skip_checks(cls):
        """Skip conditions of run tests.
        """
        super(BaseAfloTest, cls).skip_checks()
        if not CONF.service_available.aflo:
            skip_msg = ("%s skipped as aflo is not available" % cls.__name__)
            raise cls.skipException(skip_msg)

    @classmethod
    def verify_nonempty(cls, *args):
        """Check credentilas data.
        Necessary values check.
        """
        if not all(args):
            msg = "Missing API credentials in configuration."
            raise cls.skipException(msg)

    @classmethod
    def resource_setup(cls):
        """Setup resources of Testing.
        """
        super(BaseAfloTest, cls).resource_setup()

        cls.username = CONF.aflo.demo_username
        cls.password = CONF.aflo.demo_password
        cls.project_name = CONF.aflo.demo_project_name
        cls.verify_nonempty(cls.username, cls.password, cls.project_name)
        cls.os = clients.Manager()
        cls.aflo_client = cls.os.aflo_client

        cls.os.credentials.project_id = CONF.aflo.demo_project_id


class BaseV1AfloTest(BaseAfloTest):
    """V1 Interface Test Class.
    """

    @classmethod
    def setup_clients(cls):
        """Setup client.
        """
        super(BaseV1AfloTest, cls).setup_clients()


class BaseV1AfloAdminTest(BaseAfloTest):
    """V1 Interface Test Calss by admin user.
    """

    @classmethod
    def resource_setup(cls):
        super(BaseV1AfloAdminTest, cls).resource_setup()

        cls.username = CONF.aflo.admin_username
        cls.password = CONF.aflo.admin_password
        cls.project_name = CONF.aflo.admin_project_name
        cls.verify_nonempty(cls.username, cls.password, cls.project_name)
        cls.os = clients.AdminManager()
        cls.aflo_client = cls.os.aflo_client

        cls.os.credentials.project_id = CONF.aflo.admin_project_id
