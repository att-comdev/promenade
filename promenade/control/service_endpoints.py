# Copyright 2017 AT&T Intellectual Property.  All other rights reserved.
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
"""
Module to encapsulate thet endpoint lookup for the services used
by Shipyard
"""

import enum

import falcon

from promenade.exceptions import ApiError
from promenade import logging

LOG = logging.getLogger(__name__)


class Endpoints(enum.Enum):
    """
    Enumeration of the endpoints that are served by this endpoint manager
    """
    PROMENADE = 'promenade'
    DECKHAND = 'deckhand'


def _get_service_type(endpoint):
    """
    Because these values should not be used until after initialization,
    they cannot be directly associated with the enum. Thie method takes
    the enum value and retrieves the values when accessed the first time.
    :param Endpoints endpoint: The endpoint to look up
    :returns: The service type value for the named endpoint
    :rtype: str
    :raises ValidationError: if not provided a valid Endpoints enumeration value
    """
    if isinstance(endpoint, Endpoints):
        endpoint_values = {
            Endpoints.PROMENADE: CONF.promenade.service_type,
            Endpoints.DECKHAND: CONF.deckhand.service_type,
        }
        return endpoint_values.get(endpoint)
    raise ApiError(
        title='Endpoint is not known',
        description=(
            'Shipyard is trying to reach an unknown endpoint: {}'.format(
                endpoint.name
            )
        ),
        status=falcon.HTTP_500,
        retry=False
    )


def get_endpoint(endpoint):
    """
    Wraps calls to keystone for lookup of an endpoint by service type
    :param Endpoints endpoint: The endpoint to look up
    :returns: The url string of the endpoint
    :rtype: str
    :raises ApiError: if the endpoint cannot be resolved
    """
    service_type = _get_service_type(endpoint)
    try:
        return _get_ks_session().get_endpoint(
            interface='internal',
            service_type=service_type)
    except EndpointNotFound:
        LOG.error('Could not find a public interface for %s',
                  endpoint.name)
        raise ApiError(
            title='Can not access service endpoint',
            description=(
                'Keystone catalog has no internal endpoint for service type: '
                '{}'.format(service_type)
            ),
            status=falcon.HTTP_500,
            retry=False)
