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

from control import api
import policy


def start_promenade():
    # Setup root logger
    base_console_handler = logging.StreamHandler()

    logging.basicConfig(level=logging.INFO,
                        format='%(asctime)s - %(levelname)s - %(message)s',
                        handlers=[base_console_handler])
    logging.getLogger().info("Setting logging level to: %s",
                             logging.getLevelName(10))

    logging.basicConfig(level=10,
                        format='%(asctime)s - %(levelname)s - %(message)s',
                        handlers=[base_console_handler])

    # Specalized format for API logging
    logger = logging.getLogger('promenade.control')
    logger.propagate = False
    formatter = logging.Formatter(
        ('%(asctime)s - %(levelname)s - %(message)s'))

    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    # Start the API
    return api.start_api()


# Initialization compatible with PasteDeploy
def paste_start_promenade(global_conf, **kwargs):
    return promenade


promenade = start_promenade()
