====================
Promenade API Client
====================


Usage
=====

The Promenade client consists of two components: The Promenade session, which
uses credentials to authenticate requests, and the Promenade client, which
communicates with the Promenade API server. Both of these can be found in the
``promenade_client`` directory.


Client methods
==============

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
