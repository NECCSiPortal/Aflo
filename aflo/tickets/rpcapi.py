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
import oslo_messaging as messaging

from aflo.common import rpc

CONF = cfg.CONF


class TicketRpcAPI(object):
    """Client side of the cert rpc API.
    """

    def __init__(self):
        super(TicketRpcAPI, self).__init__()
        target = messaging.Target(topic='aflo_topic', version='1.0')
        self.client = rpc.get_client(target, version_cap=None)

    def tickets_create(self, ctxt, **values):
        cctxt = self.client.prepare(version='1.0')
        cctxt.cast(ctxt, 'tickets_create', **values)

    def tickets_update(self, ctxt, ticket_id, **values):
        cctxt = self.client.prepare(version='1.0')
        cctxt.cast(ctxt, 'tickets_update', ticket_id=ticket_id, **values)

    def tickets_delete(self, ctxt, ticket_id):
        cctxt = self.client.prepare(version='1.0')
        cctxt.cast(ctxt, 'tickets_delete', ticket_id=ticket_id)
