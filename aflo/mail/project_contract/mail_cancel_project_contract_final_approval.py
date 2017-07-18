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
#

""" Mail Template Aflo"""
from aflo import i18n

_ = i18n._

""" Subject """
SUBJECT = _("[NEC Cloud System] Request of contract(${status})")

""" Body """
BODY = _("""NEC Cloud System

This message is sent automatically.

Change status to ${status}.

Contract Overview
    Request ID: ${id}
    Request Type: Request of contract
    Updated By: ${user}
    Update Date and Time: ${update_date}
    Withdrawal Date and Time: ${withdrawal_date}

===============
Message:
${message}

===============
NEC Cloud System
URL: http://xxxx.co.jp
===============
""")
