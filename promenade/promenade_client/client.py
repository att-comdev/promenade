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

from promenade import exceptions, logging

LOG = logging.getLogger(__name__)


class PromenadeClient(object):
    def __init__(self, session):
        self.session = session

    def get_join_scripts(self, **kwargs):
        endpoint = 'v1.0/join-scripts'
        resp = self.session.get(
            endpoint,
            query={
                'hostname': kwargs['hostname'],
                'ip': kwargs['ip'],
                'design_ref': kwargs['design_ref'],
                'labels.dynamic': kwargs['dynamic_labels'],
                'labels.static': kwargs['static_labels']
            })
        self._check_response(resp)
        return resp.json()

    def get_health(self):
        endpoint = 'v1.0/health'
        resp = self.session.get(endpoint)
        str_resp = "<Response [204]>"
        if str(resp) == str_resp:
            return "Promeande API is healthy."

    def post_validatedesign(self, href):
        endpoint = 'v1.0/validatedesign'
        body = {'href': href}
        resp = self.session.post(endpoint, data=body)
        self._check_response(resp)
        return resp.json()

    def _check_response(self, resp):
        if resp.status_code == 401:
            raise exceptions.ApiError(
                title="Unauthenticated",
                status=resp.status_code,
                description="Credentials are not established",
                retry=False)
        elif resp.status_code == 403:
            raise exceptions.ApiError(
                title="Forbidden",
                status=resp.status_code,
                description="Credentials do not permit access",
                retry=False)
        elif not resp.ok:
            raise exceptions.ApiError(
                title="Unknown error",
                status=resp.status_code,
                description="Error description: %s" % str(resp.text),
                retry=False)
