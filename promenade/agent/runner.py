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

from . import engine, event_source, kube_util, service_manager, status_manager
from promenade import logging
import time

LOG = logging.getLogger(__name__)

DELAY_PERIOD = 10


class AgentRunner:
    def __init__(self, *, engine, event_source):
        self.engine = engine
        self.event_source = event_source

    @classmethod
    def with_defaults(cls, *, hostname):
        kube_wrapper = kube_util.KubernetesWrapper()
        svc_mgr = service_manager.SystemdServiceManager()
        stat_mgr = status_manager.KubernetesStatusManager(
            hostname=hostname, kube_wrapper=kube_wrapper)
        e = engine.AgentEngine(
            service_manager=svc_mgr, status_manager=stat_mgr)
        es = event_source.KubernetesEventSource(
            hostname=hostname, kube_wrapper=kube_wrapper)
        return cls(engine=e, event_source=es)

    def run(self):
        LOG.info('Starting agent')
        self.engine.report_state()

        while True:
            self.handle_stream()

            LOG.info('Event stream ended, sleeping before restart')
            time.sleep(DELAY_PERIOD)

    def handle_stream(self):
        for document in self.event_source.stream_events():
            LOG.info('Got event: %s', document)
            self.engine.apply(document)
