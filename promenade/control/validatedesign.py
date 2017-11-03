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
import logging
from urllib3 import exceptions as url_ex

import jsonschema
import falcon

from promenade.config import Configuration
from promenade.control import base

LOG = logging.getLogger(__name__)


class ValidateDesignResource(base.BaseResource):
    def on_post(self, req, resp):
        href = req.get_param('href', required=True)
        try:
            config = Configuration.from_design_ref(href)
            self._validate_file(config)
        except (url_ex.URLError, url_ex.HTTPError,
                jsonschema.ValidationError) as e:
            msg = "Promenade validations failed"
            self.return_error(resp, falcon.HTTP_400, message=msg)
            raise falcon.HTTP_400(title=e, description=msg)

    def _validate_file(config):
        required_docs = [
            'Docker.yaml', 'HostSystem.yaml', 'KubernetesNetwork.yaml'
        ]
        if all(docs not in config.documents for docs in required_docs):
            raise jsonschema.ValidationError
