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
import abc

LOG = logging.getLogger(__name__)


class IEventSource(metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def stream_events(self):
        pass


class KubernetesEventSource(IEventSource):
    GROUP = 'promenade.ucp.att.com'
    VERSION = 'v1'
    PLURAL = 'node-configurations'

    def __init__(self, *, kube_wrapper):
        self.kube_wrapper = kube_wrapper

    def stream_events(self):
        self.kube_wrapper.wait_for_crds(
            [self.GROUP + '/' + self.VERSION + ':' + self.PLURAL])

        LOG.info('Monitoring events')
        for event in self.kube_wrapper.stream_custom_objects(
                self.GROUP, self.VERSION, self.PLURAL):
            yield event
