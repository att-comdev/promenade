====================
Promenade API Client
====================


Usage
=====

The Promenade client consists of two components: The Promenade session, which
uses either a Keystone token or credentials to authenticate requests, and the
Promenade client, which communicates with the Promenade API server. Both of
these can be found in the ``promenade_client`` directory.

.. code:: python

    from promenade.promenade_cli import client_helper
    from promenade.promenade_client import client
    from promenade.promenade_client import session

    prom_session = session.PromenadeSession('localhost', port='8000', token='mytoken')
    prom_client = client.PromenadeClient(prom_session)

    prom_health = prom_client.get_health()

Client methods
==============

The following methods are supported for accessing the Promenade API.

get_health
----------

Returns health status of Promenade API.

get_join_scripts
----------------

Provide information about the node (hostname, ip, endpoint containing
configuration documents, labels), returns join scripts for node.

post_validatedesign
-------------------

Provide an endpoint that contains node design documents, returns a response
as to whether or not they are valid.
