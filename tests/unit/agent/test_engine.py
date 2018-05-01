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
from promenade.agent.status_manager import IStatusManager
from unittest import mock
import pytest


@pytest.fixture
def stat_mgr():
    return mock.MagicMock(IStatusManager)


TEST_STATUS = {
    'errors': [],
    'state': 'TESTING',
}


@pytest.fixture
def svc_mgr():
    svc_mgr = mock.MagicMock(IServiceManager)
    svc_mgr.get_status.return_value = TEST_STATUS
    return svc_mgr


@pytest.fixture
def eng(stat_mgr, svc_mgr):
    return engine.AgentEngine(service_manager=svc_mgr, status_manager=stat_mgr)


def _report_state_test_helper(eng,
                              stat_mgr,
                              svc_mgr,
                              services=['docker', 'kubelet']):
    assert svc_mgr.get_status.call_count == len(services)
    for service in services:
        svc_mgr.get_status.assert_any_call(service)

    stat_mgr.set_service_statuses.assert_called_once_with(
        {service: TEST_STATUS
         for service in services})


def test_report_state_default_services(eng, stat_mgr, svc_mgr):
    eng.report_state()

    _report_state_test_helper(eng, stat_mgr, svc_mgr)


def test_report_state_specific_services(stat_mgr, svc_mgr):
    eng = engine.AgentEngine(
        service_manager=svc_mgr,
        status_manager=stat_mgr,
        expected_services=['foo', 'bar'])

    eng.report_state()

    _report_state_test_helper(eng, stat_mgr, svc_mgr, services=['foo', 'bar'])


def test_apply_enable_services(eng, stat_mgr, svc_mgr):
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

    assert svc_mgr.set_up.call_count == 2
    svc_mgr.set_up.assert_any_call('docker')
    svc_mgr.set_up.assert_any_call('kubernetes')

    svc_mgr.set_down.assert_not_called()
    _report_state_test_helper(eng, stat_mgr, svc_mgr)


def test_apply_disable_services(eng, stat_mgr, svc_mgr):
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

    svc_mgr.set_up.assert_not_called()

    assert svc_mgr.set_down.call_count == 2
    svc_mgr.set_down.assert_any_call('docker')
    svc_mgr.set_down.assert_any_call('kubernetes')

    _report_state_test_helper(eng, stat_mgr, svc_mgr)


def test_apply_enable_split(eng, stat_mgr, svc_mgr):
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

    assert svc_mgr.set_up.call_count == 1
    svc_mgr.set_up.assert_any_call('docker')

    assert svc_mgr.set_down.call_count == 1
    svc_mgr.set_down.assert_any_call('kubernetes')

    _report_state_test_helper(eng, stat_mgr, svc_mgr)


def test_apply_ignore_unspecified(eng, stat_mgr, svc_mgr):
    event = {
        'services': {
            'kubernetes': {
                'enabled': False,
            },
        },
    }

    eng.apply(event)

    svc_mgr.set_up.assert_not_called()

    assert svc_mgr.set_down.call_count == 1
    svc_mgr.set_down.assert_any_call('kubernetes')

    _report_state_test_helper(eng, stat_mgr, svc_mgr)
