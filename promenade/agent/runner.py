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

from . import engine, event_source, service_manager
from promenade import exceptions, logging
import time

LOG = logging.getLogger(__name__)

DELAY_PERIOD = 10


class AgentRunner:
    def __init__(self, *, engine, event_source, hostname):
        self.engine = engine
        self.event_source = event_source
        self.hostname = hostname

    @classmethod
    def with_defaults(cls, **kwargs):
        sm = service_manager.SystemdServiceManager()
        e = engine.AgentEngine(service_manager=sm)
        es = event_source.KubernetesEventSource()
        return cls(engine=e, event_source=es, **kwargs)

    def run(self):
        LOG.info('Starting agent for hostname=%s', self.hostname)
        self.engine.log_state()

        while True:
            self.handle_stream()

            LOG.info('Event stream ended, sleeping before restart')
            time.sleep(DELAY_PERIOD)

    def handle_stream(self):
        for event in self.event_source.stream_events():
            if self._is_local(event):
                self.handle_event(event)
            else:
                LOG.debug('Got unrelated event: %s (%s)',
                          event.get('object', {}).get('metadata', {}).get('name'),
                          event.get('type', ''))

    def _is_local(self, event):
        return event['object'].get('metadata', {}).get('name') == self.hostname

    def handle_event(self, event):
        LOG.info('Got host event: %s', event)
        type_ = event.get('type', '').upper()
        if type_ in {'ADDED', 'MODIFIED'}:
            LOG.info('Got %s event for node.', type_)
            self.engine.apply(event['object'])
        elif type_ == 'DELETED':
            LOG.warn('Got delete event for node: %s', event)
        elif type_ == 'ERROR':
            LOG.error('Got an error event from the Kubernetes API: %s', event)
            raise exceptions.KubernetesErrorEvent()
        else:
            LOG.error('Got unexpected event from Kubernets API: %s', event)
            raise exceptions.KubernetesUnexpectedEvent()
