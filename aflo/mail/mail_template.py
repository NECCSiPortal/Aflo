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

""" Mail Template Aflo"""
from aflo import i18n

_ = i18n._

""" Subject """
SUBJECT = _("[NEC Cloud System] Workflow from ${subject}")

""" Body """
BODY = _("""NEC Cloud System

This message is sent automatically.

Updated By: ${user}
Update Date and Time: ${update_date}

${body}

Login URL: ${url}

===============
NEC Cloud System
URL: http://xxxx.co.jp
===============
""")
