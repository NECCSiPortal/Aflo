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

"""Stubouts, mocks and fixtures for the test suite"""

from aflo.tickets.manager import TicketsManager
from oslo_messaging.rpc import client as rpc_client


class Ticket_RpcStubs(object):
    @classmethod
    def stub_fake_cast(cls, target, method):  # noap
        """RPC Process Stub.
        This stub is calling actual rpc called function.
        :param target: Target rpc process.
        :param method: Called rpc function.
        """
        call_info = {}

        def fake_tickets_create(self, ctxt, method, **kwargs):
            """Ticket craete fake function.
            :param ctxt: Request context.
            :param method: Call function.
            :param kwargs: Input parametar from form.
            """
            call_info['req_ctxt'] = ctxt
            call_info['req_method'] = method
            call_info['req_kwargs'] = kwargs
            return TicketsManager().tickets_create(ctxt.to_dict(), **kwargs)

        def fake_tickets_update(self, ctxt, method, **kwargs):
            """Ticket update fake function.
            :param ctxt: Request context.
            :param method: Call function.
            :param kwargs: Input parametar from form.
            """
            call_info['req_ctxt'] = ctxt
            call_info['req_method'] = method
            call_info['req_kwargs'] = kwargs
            return TicketsManager().tickets_update(ctxt.to_dict(), **kwargs)

        def fake_tickets_delete(self, ctxt, method, **kwargs):
            """Ticket delete fake function.
            :param ctxt: Request context.
            :param method: Call function.
            :param kwargs: Input parametar from form.
            """
            call_info['req_ctxt'] = ctxt
            call_info['req_method'] = method
            call_info['req_kwargs'] = kwargs
            return TicketsManager().tickets_delete(ctxt.to_dict(), **kwargs)

        fake_managers = {'tickets_create': fake_tickets_create,
                         'tickets_update': fake_tickets_update,
                         'tickets_delete': fake_tickets_delete}
        target.stubs.Set(rpc_client._CallContext, 'cast',
                         fake_managers[method])

        return call_info
