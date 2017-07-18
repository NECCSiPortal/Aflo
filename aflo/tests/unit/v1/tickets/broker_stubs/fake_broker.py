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
#

from aflo.common.broker_base import BrokerBase


class FakeBroker(BrokerBase):
    def __init__(self, ctxt, template_contents,
                 wf_pattern_contents, **values):
        BrokerBase.__init__(self, ctxt,
                            template_contents,
                            wf_pattern_contents,
                            **values)

    def param_check(self, **values):
        self.general_param_check(**values)

    def before_action(self, session, *args, **values):
        pass

    def after_action(self, session, *args, **values):
        pass

    def valid_catalog_check(self, ctxt, **values):
        pass
