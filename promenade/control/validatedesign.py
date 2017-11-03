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
import os
from urllib3 import request, error
import yaml

import falcon

from promenade.control import base

LOG = logging.getLogger(__name__)


class ValidateDesignResource(base.BaseResource):
    def on_post(self, req, resp, href, doc_type):
        if os.path.isfile(href):
            self._validate_file(href, True)
        else:
            try:
                service, url = href.split("+")
                self._validate_file(url)
            except ValueError as e:
                msg = "File location improperly formatted"
                LOG.error(msg)
                raise falcon.HTTPNotFound(title=e, description=msg)

    def _validate_file(file_location, local=False):
        if not local:
            try:
                request.urlopen(file_location)
            except (error.HTTPError, error.URLError) as e:
                msg = "Could not reach specified URL"
                LOG.error(msg)
                raise falcon.HTTPNotFound(title=e, description=msg)
        # validate file
        try:
            with open(file_location) as f:
                yaml.safe_load(f)
        except yaml.scanner.ScannerError as e:
            msg = "YAML file is improperly formatted"
            LOG.error(msg)
            raise falcon.HTTP_400(title=e, description=msg)
