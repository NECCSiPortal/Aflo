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

from __future__ import print_function

from oslo_config import cfg

from tempest import config  # noqa


service_available_group = cfg.OptGroup(name="service_available",
                                       title="Available OpenStack Services")

ServiceAvailableGroup = [
    cfg.BoolOpt("aflo",
                default=True,
                help="Whether or not aflo is expected to be available"),
]

aflo_group = cfg.OptGroup(name="aflo", title="Aflo Service Options")

AfloGroup = [
    cfg.StrOpt("aflo_feature_enabled",
               default="v1",
               help="Use aflo version."),
    cfg.StrOpt("region",
               default="",
               help="The aflo region name to use. If empty, the value "
                    "of identity.region is used instead. If no such region "
                    "is found in the service catalog, the first found one is "
                    "used."),
    cfg.StrOpt("catalog_type",
               default="ticket",
               help="Catalog type of the Aflo service."),
    cfg.StrOpt('endpoint_type',
               default='publicURL',
               choices=['public', 'admin', 'internal',
                        'publicURL', 'adminURL', 'internalURL'],
               help="The endpoint type to use for the aflo service."),
    cfg.StrOpt("demo_project_id",
               help="Demo project id."),
    cfg.StrOpt("demo_project_name",
               help="Demo project name."),
    cfg.StrOpt("demo_user_id",
               help="Demo user id."),
    cfg.StrOpt("demo_username",
               help="Demo user name."),
    cfg.ListOpt('ost_roles',
                default=["SwiftOperator"],
                help='Object Storage role of use.Set approve multi roles.'
                     'example) T__DC1__ObjectStore,Other_Role'),
]


class TempestConfigProxyAflo(object):
    """Wrapper over standard Tempest config that sets Aflo opts."""

    def __init__(self):
        self._config = config.CONF
        config.register_opt_group(
            cfg.CONF, service_available_group, ServiceAvailableGroup)
        config.register_opt_group(cfg.CONF, aflo_group, AfloGroup)
        self._config.aflo = cfg.CONF.aflo

    def __getattr__(self, attr):
        return getattr(self._config, attr)


CONF = TempestConfigProxyAflo()
