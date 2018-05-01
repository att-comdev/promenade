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
import kubernetes

LOG = logging.getLogger(__name__)


def load_configuration():
    try:
        kubernetes.config.load_incluster_config()
        LOG.info('Loaded in-cluster Kubernetes configuration.')
    except kubernetes.config.config_exception.ConfigException:
        LOG.debug('Failed to load in-cluster configuration')
        kubernetes.config.load_kube_config()
        LOG.info('Loaded out-of-cluster Kubernetes configuration.')
