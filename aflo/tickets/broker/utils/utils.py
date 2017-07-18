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
import datetime
import functools

from oslo_config import cfg
from oslo_log import log as logging

from cinderclient.v2 import client as cinder_client
from keystoneclient.auth.identity import v3
from keystoneclient import exceptions
from keystoneclient import session as keystone_client_session
from keystoneclient.v2_0 import client as keystone_client
from keystoneclient.v3 import client as keystone_client_v3
from novaclient import client as nova_client

from aflo.common import mail
from aflo.db.sqlalchemy import api as db_api
from aflo import i18n
from aflo.mail import mail_template_contract_error
from aflo.mail import mail_template_contract_registration
from aflo.tickets.broker.utils import INTERNAL_UTC_DATETIME_FORMAT

CONF = cfg.CONF

UNIT_CONVERSION = \
    {'ram': {'KB': float(1 / 1024),
             'MB': 1,
             'GB': 1024,
             'TB': (1024 ** 2)},
     'gigabytes': {'KB': float(1 / (1024 ** 2)),
                   'MB': float(1 / 1024),
                   'GB': 1,
                   'TB': 1024}}

NOVA_QUOTAS = ['cores', 'ram']
CINDER_QUOTAS = ['gigabytes']
NOVA_LIMIT_USED_KEYS = {'cores': 'totalCoresUsed',
                        'ram': 'totalRAMUsed'}
CINDER_LIMIT_USED_KEYS = {'gigabytes': 'totalGigabytesUsed'}

LOG = logging.getLogger(__name__)

_LE = i18n._LE


def keystone_version_validator(func):
    """Keystone version validator"""
    @functools.wraps(func)
    def _func(*args, **kwargs):
        if int(CONF.keystone_client.auth_version) < 3:
            error_message = _LE("Don't support keystone version 2.")
            raise exceptions.UnsupportedVersion(error_message)

        return func(*args, **kwargs)

    return _func


# TODO(matsuda): The future will match the implementation of
# the client to match the other components.
def get_keystone_client():
    if int(CONF.keystone_client.auth_version) < 3:
        return keystone_client.Client(
            username=CONF.keystone_client.username,
            password=CONF.keystone_client.password,
            tenant_name=CONF.keystone_client.tenant_name,
            auth_url=CONF.keystone_client.auth_url)

    return keystone_client_v3.Client(
        username=CONF.keystone_client.username,
        password=CONF.keystone_client.password,
        tenant_name=CONF.keystone_client.tenant_name,
        region_name=CONF.keystone_client.region_name,
        auth_url=CONF.keystone_client.auth_url,
        user_domain_name=CONF.keystone_client.user_domain_id,
        project_domain_name=CONF.keystone_client.project_domain_id)


# TODO(matsuda): The future will match the implementation of
# the client to match the other components.
def get_nova_client():
    if int(CONF.keystone_client.auth_version) < 3:
        return nova_client.Client(
            version=CONF.nova_client.api_version,
            username=CONF.nova_client.username,
            api_key=CONF.nova_client.api_key,
            project_id=CONF.nova_client.project_id,
            auth_url=CONF.keystone_client.auth_url)

    auth = v3.Password(
        auth_url=CONF.keystone_client.auth_url,
        username=CONF.nova_client.username,
        password=CONF.nova_client.api_key,
        project_name=CONF.nova_client.project_id,
        user_domain_name=CONF.nova_client.user_domain_id,
        project_domain_name=CONF.nova_client.project_domain_id)
    session = keystone_client_session.Session(
        auth=auth, verify='/path/to/ca.cert')

    return nova_client.Client(
        version=CONF.nova_client.api_version,
        session=session,
        region_name=CONF.nova_client.region_name,
        endpoint_type=CONF.nova_client.endpoint_type)


# TODO(matsuda): The future will match the implementation of
# the client to match the other components.
def get_cinder_client():
    if int(CONF.keystone_client.auth_version) < 3:
        return cinder_client.Client(
            username=CONF.cinder_client.username,
            api_key=CONF.cinder_client.api_key,
            project_id=CONF.cinder_client.project_id,
            auth_url=CONF.keystone_client.auth_url)

    auth = v3.Password(
        auth_url=CONF.keystone_client.auth_url,
        username=CONF.cinder_client.username,
        password=CONF.cinder_client.api_key,
        project_name=CONF.cinder_client.project_id,
        user_domain_name=CONF.cinder_client.user_domain_id,
        project_domain_name=CONF.cinder_client.project_domain_id)
    session = keystone_client_session.Session(auth=auth,
                                              verify='/path/to/ca.cert')
    return cinder_client.Client(
        session=session,
        region_name=CONF.cinder_client.region_name,
        endpoint_type=CONF.cinder_client.endpoint_type)


def get_email_address(user_id):
    try:
        user = get_keystone_client().users.get(user_id)
    except keystone_client.exceptions.NotFound:
        # If target user was deleted, exception will occur.
        return None

    return getattr(user, 'email', None)


def get_email_addresses_from_role(tenant, roles):
    addresses = []
    keystone = get_keystone_client()
    users = _get_project_users_list(keystone, tenant)
    for user in users:
        user_roles = _get_role_users_list(keystone, tenant, user)
        for role in user_roles:
            try:
                if role.name in roles and user.email:
                    addresses.append(user.email)
                    break
            except AttributeError:
                # User object don't have a email attribute.
                continue
    return list(set(addresses))


def _get_project_users_list(keystone, tenant):
    keystone = get_keystone_client()
    if int(CONF.keystone_client.auth_version) < 3:
        return keystone.tenants.list_users(tenant)
    else:
        return keystone.users.list(project=tenant)


def _get_role_users_list(keystone, tenant, user):
    if int(CONF.keystone_client.auth_version) < 3:
        return keystone.roles.roles_for_user(user, tenant)
    else:
        return keystone.roles.list(user=user, project=tenant)


@keystone_version_validator
def add_roles(roles, user_id, project_id, keystone=None):
    """Add roles to project
    :param roles: add roles
    :param user_id: target user
    :param project_id: target project
    :param keystone: optional, keystoneclient
    """
    if not keystone:
        keystone = get_keystone_client()

    for role in get_roles(roles, keystone):
        keystone.roles.grant(role=role, user=user_id,
                             project=project_id)


@keystone_version_validator
def revoke_roles(roles, project_id, keystone=None):
    """Revoke roles from user and group
    :param roles: add roles
    :param project_id: target project
    :param keystone: optional, keystone keystoneclient
    """
    if not keystone:
        keystone = get_keystone_client()

    manager = keystone.roles
    project = get_project(project_id)
    users = get_user_list(project, keystone)
    groups = get_group_list(project, keystone)

    for role in get_roles(roles, keystone):
        for user in users:
            if user.name in CONF.ost_contract.disinherited_user:
                continue
            try:
                manager.check(role=role, user=user, project=project)
                manager.revoke(role=role, user=user, project=project)
            except keystone_client.exceptions.NotFound:
                # If target user don't have the role
                error_message = _LE(
                    "The user doesn't have role. the role=%(role)s, "
                    "user=%(user)s, project=%(project)s") % {
                        'role': role.name,
                        'user': user.name,
                        'project': project_id, }
                LOG.info(error_message)

        for group in groups:
            try:
                manager.check(role=role, group=group, project=project)
                manager.revoke(role=role, group=group, project=project)
            except keystone_client.exceptions.NotFound:
                # If target group don't have the role
                error_message = _LE(
                    "The group doesn't have role. the role=%(role)s, "
                    "group=%(group)s, project=%(project)s") % {
                        'role': role.name,
                        'group': group.name,
                        'project': project_id, }
                LOG.info(error_message)


def get_next_roles(invoker_self):
    # Get a can change next status of an AFTER status.
    # A before status is current change process.
    next_status_list = _get_can_change_status_list(invoker_self)
    next_role = []

    if len(next_status_list) == 0 or \
            next_status_list[0].get('next_status_code', None) is None:
        return next_role

    next_status = filter(
        lambda next_status:
        next_status['next_status_code'] == invoker_self.after_status_code,
        next_status_list)

    for next_status in next_status_list:
        grant_role = next_status.get('grant_role', [])
        if not isinstance(grant_role, list):
            grant_role = [grant_role]
        for role in grant_role:
            next_role.append(role)

    return next_role


def _get_can_change_status_list(invoker_self):
    all_wf_status_list = invoker_self.wf_pattern['status_list']
    after_wf_status = filter(
        lambda wf_status:
        wf_status['status_code'] == invoker_self.after_status_code,
        all_wf_status_list)[0]
    return after_wf_status['next_status']


def get_user_list(project_id=None, keystone=None):
    """Get user list
    :param project_id: optional, target project
    :param keystone: optional, keystoneclient
    """
    if not keystone:
        keystone = get_keystone_client()
    if int(CONF.keystone_client.auth_version) < 3:
        return keystone.tenants.list_users()
    else:
        if project_id:
            return keystone.users.list(project=project_id)
        else:
            return keystone.users.list()


def get_project_list():
    keystone = get_keystone_client()
    if int(CONF.keystone_client.auth_version) < 3:
        return keystone.tenants.list()
    else:
        return keystone.projects.list()


@keystone_version_validator
def get_group_list(project_id=None, keystone=None):
    """Get group list of project
    :param project_id: optional, target project
    :param keystone: optional, keystoneclient
    """
    if not keystone:
        keystone = get_keystone_client()

    return keystone.groups.list(project=project_id)


def get_child_project_list(project_id):
    keystone = get_keystone_client()
    if int(CONF.keystone_client.auth_version) < 3:
        return None
    else:
        kwargs = {"parent_id": project_id}
        return keystone.projects.list(**kwargs)


def get_user(user_id):
    return get_keystone_client().users.get(user_id)


def get_project(project_id):
    keystone = get_keystone_client()
    if int(CONF.keystone_client.auth_version) < 3:
        return keystone.tenants.get(project_id)
    else:
        return keystone.projects.get(project_id)


@keystone_version_validator
def get_roles(role_names, keystone=None):
    """Get roles by role name
    :param role_names: list object of role names
    :param keystone: optional, keystoneclient
    """
    if not keystone:
        keystone = get_keystone_client()

    role_list = keystone.roles.list()

    return [role for role in role_list if role.name in role_names]


def update_quotas(tenant_id, **values):
    update_val_nova = {}
    update_val_cinder = {}

    for key, val in values.iteritems():
        if key in NOVA_QUOTAS:
            update_val_nova[key] = val
        elif key in CINDER_QUOTAS:
            update_val_cinder[key] = val

    get_nova_client().quotas.update(tenant_id, **update_val_nova)
    get_cinder_client().quotas.update(tenant_id, **update_val_cinder)


def get_catalog_contents_data(ctxt, catalog_id):
    catalog_contents = db_api.catalog_contents_list(ctxt, catalog_id)

    rtn_vals = {}

    for content in catalog_contents:
        val = long(content['goods_num'])
        key = content['expansions']['expansion_key2']
        unit = content['expansions']['expansion_key3']

        if unit in UNIT_CONVERSION.get(key, []):
            val = val * UNIT_CONVERSION[key][unit]

        rtn_vals[key] = val

    return rtn_vals


def get_display_name(name):
    return name.get('default', name.get('Default', ''))


def sendmail_for_contract_registration(self, to_address, **values):
    if not to_address:
        return

    data = {'id': values['id'],
            'user': values["confirmer_name"],
            'update_date': values['confirmed_at'],
            'message': values['additional_data'].get(
                'Message', values['additional_data'].get('message', '')),
            'status': get_status_name(self,
                                      values['after_status_code'])
            }

    if CONF.mail.smtp_server:
        mail.sendmail(to_address,
                      mail_template_contract_registration,
                      data)


def sendmail_for_contract_error(self, to_address, location,
                                cause, **values):
    if not to_address:
        return

    data = {'subject': 'Change status [%s] from %s' %
            (self.after_status_code, values["confirmer_name"]),
            'user': values['confirmer_name'],
            'date': values['confirmed_at'],
            'location': location,
            'cause': cause}

    if CONF.mail.smtp_server:
        mail.sendmail(to_address,
                      mail_template_contract_error,
                      data)


def get_status_name(self, status_code):
    status_name = ''
    if self.wf_pattern and self.wf_pattern['status_list']:
        # Get status list.
        status_list = self.wf_pattern['status_list']

        # Find status data from contents.
        status = filter(lambda status:
                        status["status_code"] == status_code,
                        status_list)

        if status and 0 < len(status):
            status_name = get_display_name(status[0]["status_name"])

    return status_name


def get_now_string():
    """Get utc now string"""
    return datetime.datetime.utcnow().strftime(INTERNAL_UTC_DATETIME_FORMAT)
