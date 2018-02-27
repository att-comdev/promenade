# Copyright 2018 AT&T Intellectual Property.  All other rights reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
from promenade import logging
from . import action

LOG = logging.getLogger(__name__)


class CheckHealth(action.CliAction):  # pylint: disable=too-few-public-methods
    def __init__(self, api_client):
        super().__init__(api_client)
        LOG.debug("Checking Promenade API health")

    def invoke(self):
        return self.api_client.get_health()


class JoinScripts(action.CliAction):  # pylint: disable=too-few-public-methods
    def __init__(self, api_client, hostname, ip, design_ref, dynamic_labels,
                 static_labels):
        super().__init__(api_client)
        LOG.debug("Creating join scripts")
        self.hostname = hostname
        self.ip = ip
        self.design_ref = design_ref
        self.dynamic_labels = dynamic_labels
        self.static_labels = static_labels

    def invoke(self):
        return self.api_client.get_join_scripts(
            hostname=self.hostname,
            ip=self.ip,
            design_ref=self.design_ref,
            dynamic_labels=self.dynamic_labels,
            static_labels=self.static_labels)


class ValidateDesign(action.CliAction):  # pylint: disable=too-few-public-methods
    def __init__(self, api_client, href):
        super().__init__(api_client)
        LOG.debug("Validating design")
        self.href = href

    def invoke(self):
        return self.api_client.post_validatedesign(href=self.href)
