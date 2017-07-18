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

"""Stubouts, mocks and fixtures for the test suite"""

from aflo.common.exception import BrokerError
from aflo.common.exception import InvalidParameterValue
from aflo.common.exception import NotFound
from aflo.tests.unit.v1.tickets.broker_stubs import fake_broker


class BrokerStubs(object):

    @classmethod
    def stub_fake_param_check(cls, target):
        """FakeBroker.param_check Stub.
        :param target: test process self.
        """
        call_info = {}

        def fake_function(self, *args, **values):
            call_info['req_args'] = args
            call_info['req_values'] = values

        target.stubs.Set(fake_broker.FakeBroker, 'param_check',
                         fake_function)

        return call_info

    @classmethod
    def stub_fake_valid_catalog_check(cls, target):
        """FakeBroker.valid_catalog_check Stub.
        :param target: test process self.
        """
        call_info = {}

        def fake_function(self, *args, **values):
            call_info['req_args'] = args
            call_info['req_values'] = values

        target.stubs.Set(fake_broker.FakeBroker, 'valid_catalog_check',
                         fake_function)

        return call_info

    @classmethod
    def stub_fake_exception_param_check(cls, target):
        """FakeBroker.param_check Stub.
        :param target: test process self.
        """
        call_info = {}

        def fake_function(self, *args, **values):
            call_info['req_args'] = args
            call_info['req_values'] = values
            mes_param = {'value': None,
                         'param': 'test',
                         'extra_msg': 'is None but is required'}
            raise InvalidParameterValue(**mes_param)

        target.stubs.Set(fake_broker.FakeBroker, 'param_check',
                         fake_function)

        return call_info

    @classmethod
    def stub_fake_exception_message_check(cls, target):
        """FakeBroker.message_check Stub.
        :param target: test process self.
        """
        call_info = {}

        def fake_function(self, *args, **values):
            call_info['req_args'] = args
            call_info['req_values'] = values
            mes_param = {'value': None,
                         'param': 'test',
                         'extra_msg': 'is None but is required'}
            raise InvalidParameterValue(**mes_param)

        target.stubs.Set(fake_broker.FakeBroker, 'param_check',
                         fake_function)

        return call_info

    @classmethod
    def stub_fake_exception_valid_catalog_check(cls, target):
        """FakeBroker.valid_catalog_check Stub.
        :param target: test process self.
        """
        call_info = {}

        def fake_function(self, *args, **values):
            call_info['req_args'] = args
            call_info['req_values'] = values
            raise NotFound()

        target.stubs.Set(fake_broker.FakeBroker, 'valid_catalog_check',
                         fake_function)

        return call_info

    @classmethod
    def stub_fake_before_action(cls, target):
        """FakeBroker.before_action Stub.
        :param target: test process self.
        """
        call_info = {}

        def fake_function(self, session, *args, **values):
            call_info['req_args'] = args
            call_info['req_values'] = values

        target.stubs.Set(fake_broker.FakeBroker, 'before_action',
                         fake_function)

        return call_info

    @classmethod
    def stub_fake_exception_before_action(cls, target):
        """FakeBroker.after_action Stub.
        :param target: test process self.
        """
        call_info = {}

        def fake_function(self, session, *args, **values):
            call_info['req_args'] = args
            call_info['req_values'] = values
            mes = {'location': 'location_001', 'cause': 'cause_001'}
            raise BrokerError(**mes)

        target.stubs.Set(fake_broker.FakeBroker, 'before_action',
                         fake_function)

        return call_info

    @classmethod
    def stub_fake_after_action(cls, target):
        """FakeBroker.after_action Stub.
        :param target: test process self.
        """
        call_info = {}

        def fake_function(self, session, *args, **values):
            call_info['req_args'] = args
            call_info['req_values'] = values

        target.stubs.Set(fake_broker.FakeBroker, 'after_action',
                         fake_function)

        return call_info

    @classmethod
    def stub_fake_exception_after_action(cls, target):
        """FakeBroker.after_action Stub.
        :param target: test process self.
        """
        call_info = {}

        def fake_function(self, session, *args, **values):
            call_info['req_args'] = args
            call_info['req_values'] = values
            mes = {'location': 'location_001', 'cause': 'cause_001'}
            raise BrokerError(**mes)

        target.stubs.Set(fake_broker.FakeBroker, 'after_action',
                         fake_function)

        return call_info
