#!/usr/bin/env python

# Copyright 2011 OpenStack Foundation
# All Rights Reserved.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

"""
Routines for configur
"""

import logging
import logging.config
import logging.handlers
import os
import tempfile

from oslo_concurrency import lockutils
from oslo_config import cfg
from oslo_policy import policy
from paste import deploy

from aflo.common import rpc
from aflo import i18n
from aflo.version import version_info as version

_ = i18n._

paste_deploy_opts = [
    cfg.StrOpt('flavor',
               help=_('Partial name of a pipeline in your paste configuration '
                      'file with the service name removed. For example, if '
                      'your paste section name is '
                      '[pipeline:aflo-api-keystone] use the value '
                      '"keystone"')),
    cfg.StrOpt('config_file',
               help=_('Name of the paste configuration file.')),
]
common_opts = [
    cfg.StrOpt('data_api', default='aflo.db.sqlalchemy.api',
               help=_('Python module path of data access API')),
    cfg.IntOpt('limit_param_default', default=25,
               help=_('Default value for the number of items returned by a '
                      'request if not specified explicitly in the request')),
    cfg.IntOpt('api_limit_max', default=1000,
               help=_('Maximum permissible number of items that could be '
                      'returned by a request')),
    cfg.BoolOpt('enable_v1_api', default=True,
                help=_("Deploy the v1 OpenStack API.")),
    cfg.StrOpt('pydev_worker_debug_host',
               help=_('The hostname/IP of the pydev process listening for '
                      'debug connections')),
    cfg.IntOpt('pydev_worker_debug_port', default=5678,
               help=_('The port on which a pydev process is listening for '
                      'connections.')),
    cfg.StrOpt('digest_algorithm', default='sha1',
               help=_('Digest algorithm which will be used for digital '
                      'signature; the default is sha1 the default in Kilo '
                      'for a smooth upgrade process, and it will be updated '
                      'with sha256 in next release(L). Use the command '
                      '"openssl list-message-digest-algorithms" to get the '
                      'available algorithms supported by the version of '
                      'OpenSSL on the platform. Examples are "sha1", '
                      '"sha256", "sha512", etc.')),
]
debug_opts = [
    cfg.BoolOpt('verbose', default=False,
                help=_('Show more verbose log output '
                       '(sets INFO log level output)')),
    cfg.BoolOpt('debug', default=False,
                help=_('Show debugging output in logs '
                       '(sets DEBUG log level output)')),
]
log_opts = [
    cfg.StrOpt('logging_context_format_string',
               default='%(asctime)s.%(msecs)03d %(process)d %(levelname)s '
                       '%(name)s [%(request_id)s %(user_identity)s] '
                       '%(instance)s%(message)s',
               help='Format string to use for log messages with context.'),
    # TODO(matsuda): 'xxx' will be corrected to proper value
    # when the verification is done by Tempest.
    cfg.StrOpt('logging_default_format_string_xxx',
               default='%(asctime)s.%(msecs)03d %(process)d %(levelname)s '
                       '%(name)s [-] %(instance)s%(message)s',
               help='Format string to use for log messages without context.'),
    cfg.StrOpt('logging_debug_format_suffix_xxx',
               default='%(funcName)s %(pathname)s:%(lineno)d',
               help='Data to append to log format when level is DEBUG.'),
    cfg.StrOpt('logging_exception_prefix_xxx',
               default='%(asctime)s.%(msecs)03d %(process)d TRACE %(name)s '
               '%(instance)s',
               help='Prefix each line of exception output with this format.'),
    cfg.StrOpt('instance_format',
               default='[instance: %(uuid)s] ',
               help='The format for an instance that is passed with the log '
                    'message.'),
    cfg.StrOpt('instance_uuid_format',
               default='[instance: %(uuid)s] ',
               help='The format for an instance UUID that is passed with the '
                    'log message.'),
]

aflo_expansion_filter_opts = [
    cfg.StrOpt(
        'ticket_template_expansion_filters',
        default='aflo.tickettemplates.expansion_filters.'
        'valid_catalog_expansion_filter.ValidCatalogExpansionFilter,'
        'aflo.tickettemplates.expansion_filters.'
        'valid_role_expansion_filter.ValidRoleExpansionFilter',
        help='If you would like to use ticket template expansion filtering.'
        'It is necessary for the filtering class to extend '
        '"TicketTemplateExpansionFilterBase".'),
    cfg.StrOpt(
        'target_ticket_type',
        default='New Contract',
        help='It will specify the ticket type to be expansion filter.'),
]

rpc_opts = [
    cfg.IntOpt('rpc_workers',
               default='1',
               help='The number of child process workers that will be'
                    'created to RPCservices. The default is 1.'),
]

mail = [
    cfg.StrOpt('encode',
               default='utf-8',
               help='Send mail option.'),
    cfg.StrOpt('from_address',
               help='From e-mail address.'),
    cfg.StrOpt('smtp_server',
               help='SMTP Server IP or hostname.'),
    cfg.StrOpt('user',
               help='SMTP Server user.'),
    cfg.StrOpt('password',
               help='SMTP Server password of user'),
]

keystone_client = [
    cfg.StrOpt('username',
               default=None,
               help='Username for authentication'),
    cfg.StrOpt('password',
               default=None,
               help='Password for authentication'),
    cfg.StrOpt('tenant_id',
               default=None,
               help='Tenant id'),
    cfg.StrOpt('tenant_name',
               default=None,
               help='Tenant name'),
    cfg.StrOpt('region_name',
               default=None,
               help='Region name'),
    cfg.StrOpt('auth_url',
               default=None,
               help='Keystone service endpoint for authorization'),
    cfg.StrOpt('auth_version',
               default=3,
               help='It specifies the version of Keystone.'),
    cfg.StrOpt('user_domain_id',
               default=None,
               help='User domain id'),
    cfg.StrOpt('project_domain_id',
               default=None,
               help='Project domain id'),
]

nova_client = [
    cfg.StrOpt('username',
               default=None,
               help='Username for authentication'),
    cfg.StrOpt('api_key',
               default=None,
               help='Password for authentication'),
    cfg.StrOpt('project_id',
               default=None,
               help='Tenant name'),
    cfg.StrOpt('region_name',
               default=None,
               help='Region name'),
    cfg.StrOpt('user_domain_id',
               default=None,
               help='User domain id'),
    cfg.StrOpt('project_domain_id',
               default=None,
               help='Project domain id'),
    cfg.StrOpt('api_version',
               default=2,
               help='Nova API version.'),
    cfg.StrOpt('endpoint_type',
               default='internalURL',
               help='endpoint type. example) publicURL'),
]

cinder_client = [
    cfg.StrOpt('username',
               default=None,
               help='Username for authentication'),
    cfg.StrOpt('api_key',
               default=None,
               help='Password for authentication'),
    cfg.StrOpt('project_id',
               default=None,
               help='Tenant name'),
    cfg.StrOpt('region_name',
               default=None,
               help='Region name'),
    cfg.StrOpt('user_domain_id',
               default=None,
               help='User domain id'),
    cfg.StrOpt('project_domain_id',
               default=None,
               help='Project domain id'),
    cfg.StrOpt('endpoint_type',
               default='internalURL',
               help='endpoint type. example) publicURL'),
]

announcement = [
    cfg.StrOpt('announcement_url',
               help='Announcement url'),
    cfg.StrOpt('login_url',
               help='Login url'),
    cfg.StrOpt('create_contents_url',
               help='Create contents url'),
    cfg.StrOpt('logout_url',
               help='Logout url'),
    cfg.StrOpt('get_taxonomy_vocabulary_url',
               help='Get taxonomy vocabulary url'),
    cfg.StrOpt('get_taxonomy_term_url',
               help='Get taxonomy term url'),
    cfg.StrOpt('username',
               help='Username for authentication'),
    cfg.StrOpt('password',
               help='Password for authentication'),
    cfg.StrOpt('content_type',
               default='application/json',
               help='Content type'),
    cfg.BoolOpt('ssl_verify',
                default=True,
                help='SSL authentication occurs when to True.'),
]

quotas = [
    cfg.DictOpt('pay_for_use_contract_quota_value',
                default={'cores': -1, 'ram': -1, 'gigabytes': -1},
                help=_('Pay-for-use contract at the time of '
                       'the quota limit. ')),
]

ost_contract = [
    cfg.ListOpt('ost_roles',
                default=["SwiftOperator"],
                help='Roles for operating Object Storage Service.'
                     'example) T__DC1__ObjectStore,Other_Role'),
    cfg.ListOpt('disinherited_user',
                default=['aflo', 'admin', 'cinder', 'ceilometer',
                         'swift', 'nova', 'glance', 'neutron',
                         'heat', 'keystone', 'aodh', 'gnocchi'],
                help="Specify users who should not be stripped roles"
                     "to operate Object Storage Service"
                     "when a contract is cancelled."
                     "Basically, it's assumed operators like"
                     "system administrator, or service users"
                     "like nova, cinder."),
]

CONF = cfg.CONF
CONF.register_opts(paste_deploy_opts, group='paste_deploy')
CONF.register_opts(common_opts)
CONF.register_opts(log_opts)
CONF.register_opts(aflo_expansion_filter_opts)
CONF.register_opts(rpc_opts)
CONF.register_opts(mail, group='mail')
CONF.register_opts(keystone_client, group='keystone_client')
CONF.register_opts(nova_client, group='nova_client')
CONF.register_opts(cinder_client, group='cinder_client')
CONF.register_opts(announcement, group='announcement')
CONF.register_opts(quotas, group='quotas')
CONF.register_opts(ost_contract, group='ost_contract')
# CONF.register_opts(debug_opts)


policy.Enforcer(CONF)


def parse_args(args=None, usage=None, default_config_files=None):
    if "OSLO_LOCK_PATH" not in os.environ:
        lockutils.set_defaults(tempfile.gettempdir())

    CONF(args=args,
         project='aflo',
         version=version.cached_version_string(),
         usage=usage,
         default_config_files=default_config_files)

    rpc.init(CONF)


def _get_deployment_flavor(flavor=None):
    """
    Retrieve the paste_deploy.flavor config item, formatted appropriately
    for appending to the application name.

    :param flavor: if specified, use this setting rather than the
                   paste_deploy.flavor configuration setting
    """
    if not flavor:
        flavor = CONF.paste_deploy.flavor
    return '' if not flavor else ('-' + flavor)


def _get_paste_config_path():
    paste_suffix = '-paste.ini'
    conf_suffix = '.conf'
    if CONF.config_file:
        # Assume paste config is in a paste.ini file corresponding
        # to the last config file
        path = CONF.config_file[-1].replace(conf_suffix, paste_suffix)
    else:
        path = CONF.prog + paste_suffix
    return CONF.find_file(os.path.basename(path))


def _get_deployment_config_file():
    """
    Retrieve the deployment_config_file config item, formatted as an
    absolute pathname.
    """
    path = CONF.paste_deploy.config_file
    if not path:
        path = _get_paste_config_path()
    if not path:
        msg = _("Unable to locate paste config file for %s.") % CONF.prog
        raise RuntimeError(msg)
    return os.path.abspath(path)


def load_paste_app(app_name, flavor=None, conf_file=None):
    """
    Builds and returns a WSGI app from a paste config file.

    We assume the last config file specified in the supplied ConfigOpts
    object is the paste config file, if conf_file is None.

    :param app_name: name of the application to load
    :param flavor: name of the variant of the application to load
    :param conf_file: path to the paste config file

    :raises RuntimeError when config file cannot be located or application
            cannot be loaded from config file
    """
    # append the deployment flavor to the application name,
    # in order to identify the appropriate paste pipeline
    app_name += _get_deployment_flavor(flavor)

    if not conf_file:
        conf_file = _get_deployment_config_file()

    try:
        logger = logging.getLogger(__name__)
        logger.debug("Loading %(app_name)s from %(conf_file)s",
                     {'conf_file': conf_file, 'app_name': app_name})

        app = deploy.loadapp("config:%s" % conf_file, name=app_name)

        # Log the options used when starting if we're in debug mode...
        if CONF.debug:
            CONF.log_opt_values(logger, logging.DEBUG)

        return app
    except (LookupError, ImportError) as e:
        msg = (_("Unable to load %(app_name)s from "
                 "configuration file %(conf_file)s."
                 "\nGot: %(e)r") % {'app_name': app_name,
                                    'conf_file': conf_file,
                                    'e': e})
        logger.error(msg)
        raise RuntimeError(msg)
