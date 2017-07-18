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

from oslo_config import cfg
from oslo_log import log as logging

from aflo.common import wsgi
from aflo import i18n

CONF = cfg.CONF

LOG = logging.getLogger(__name__)
_ = i18n._

decorat = _("\n"
            "**********************************************************\n"
            "%s\n"
            "**********************************************************\n")


class AccessLogFilter(wsgi.Middleware):

    def __init__(self, app):
        super(AccessLogFilter, self).__init__(app)

    def process_request(self, req):
        msg = _("It has been accessed to aflo request: %(method)s %(path)s"
                " Accept: %(accept)s")
        args = {'method': req.method, 'path': req.path,
                'accept': req.accept}
        LOG.info(msg % args)

        LOG.debug(decorat % req)

        return None

    def process_response(self, response):
        req = response.request
        msg = _("Treatment of aflo has been terminated: %(method)s %(path)s"
                " Accept: %(accept)s")
        args = {'method': req.method, 'path': req.path,
                'accept': req.accept}
        LOG.info(msg % args)

        LOG.debug(decorat % response)

        return response
