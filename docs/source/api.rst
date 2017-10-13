Promenade API
=============


/v1.0/health
------------

Allows other components to validate Promenade's health status.

GET /v1.0/health

Returns the health status.

Responses
- 200 OK


/v1.0/join-scripts
------------------

Generates join scripts and for Drydock.

GET /v1.0/join-scripts

Generates script to be consumed by Drydock.

Query parameters
- Hostname: Name of the node
- IP: IP address of the node
- Docs ref: Deckhand endpoint containing configuration documents
- Dynamic labels: Used to set configuration options in the generated script

Responses
- 200 OK: Scripts generated successfully
- 400 Bad Request: One or more query parameters is missing or misspelled
- 404 Not Found: Hostname or IP address could not be found


/v1.0/validatedesign
--------------------

Performs validations against specified documents.

POST /v1.0/validatedesign

Performs validation against specified documents.

Parameters
- Accepts the location of the document to be validated
- Accepts the type of document to be validated

Responses:
- 200 OK: Documents were successfully validated
- 400 Bad Request: Documents were not successfully validated
- 404 Not Found: The document (of that type) was not found at the specified location
