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

from aflo.common.broker_base import BrokerBase
from aflo.common.exception import BrokerError
from aflo.common.exception import InvalidParameterValue


class FunctionalTestBroker(BrokerBase):
    """FunctionalTest broker.
    """
    def __init__(self,
                 ctxt,
                 template_contents,
                 wf_pattern_contents,
                 **values):
        """Load template contents and workflow pattern contents from json string.
        :param ctxt: Request context.
        :param template_contents: Ticket template contents json string.
        :param wf_pattern_contents: Workflow Pattern contents json string.
        :param values: Input data from form.
        """
        BrokerBase.__init__(self,
                            ctxt,
                            template_contents,
                            wf_pattern_contents,
                            **values)

    def param_check(self, ctxt, **values):
        pass

    def param_check_raise_exception(self, ctxt, **values):
        mes_param = {'value': None,
                     'param': 'test',
                     'extra_msg': 'is None but is required'}
        raise InvalidParameterValue(**mes_param)

    def action(self, session, *args, **values):
        pass

    def action_raise_exception(self, session, *args, **values):
        mes = {'location': 'location_001', 'cause': 'cause_001'}
        raise BrokerError(**mes)
