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

from aflo.contracts.manager import ContractManager
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

        def fake_contract_create(self, ctxt, method, **kwargs):  # noap
            """Contract craete face function.
            :param ctxt: Request context.
            :param method: Call function.
            :param kwargs: Input parametar from form.
            """
            call_info['req_ctxt'] = ctxt
            call_info['req_method'] = method
            call_info['req_kwargs'] = kwargs
            return ContractManager().contract_create(ctxt, **kwargs)

        fake_managers = {'contract_create': fake_contract_create}
        target.stubs.Set(rpc_client._CallContext, 'cast',
                         fake_managers[method])

        return call_info
