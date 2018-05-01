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

from promenade.agent import engine
from promenade.agent.service_manager import IServiceManager
from unittest import mock
import pytest


@pytest.fixture
def sm():
    return mock.MagicMock(IServiceManager)


@pytest.fixture
def eng(sm):
    return engine.AgentEngine(service_manager=sm)


def test_log_state_default_services(eng, sm):
    eng.log_state()

    assert sm.get_status.call_count == 2
    sm.get_status.assert_any_call('docker')
    sm.get_status.assert_any_call('kubelet')


def test_log_state_specific_services(sm):
    eng = engine.AgentEngine(service_manager=sm, expected_services=['foo', 'bar'])

    eng.log_state()

    assert sm.get_status.call_count == 2
    sm.get_status.assert_any_call('foo')
    sm.get_status.assert_any_call('bar')


def test_apply_enable_services(eng, sm):
    event = {
        'services': {
            'docker': {
                'enabled': True,
            },
            'kubernetes': {
                'enabled': True,
            },
        },
    }

    eng.apply(event)

    assert sm.set_up.call_count == 2
    sm.set_up.assert_any_call('docker')
    sm.set_up.assert_any_call('kubernetes')

    sm.set_down.assert_not_called()


def test_apply_disable_services(eng, sm):
    event = {
        'services': {
            'docker': {
                'enabled': False,
            },
            'kubernetes': {
                'enabled': False,
            },
        },
    }

    eng.apply(event)

    sm.set_up.assert_not_called()

    assert sm.set_down.call_count == 2
    sm.set_down.assert_any_call('docker')
    sm.set_down.assert_any_call('kubernetes')


def test_apply_enable_split(eng, sm):
    event = {
        'services': {
            'docker': {
                'enabled': True,
            },
            'kubernetes': {
                'enabled': False,
            },
        },
    }

    eng.apply(event)

    assert sm.set_up.call_count == 1
    sm.set_up.assert_any_call('docker')

    assert sm.set_down.call_count == 1
    sm.set_down.assert_any_call('kubernetes')


def test_apply_ignore_unspecified(eng, sm):
    event = {
        'services': {
            'kubernetes': {
                'enabled': False,
            },
        },
    }

    eng.apply(event)

    sm.set_up.assert_not_called()

    assert sm.set_down.call_count == 1
    sm.set_down.assert_any_call('kubernetes')
