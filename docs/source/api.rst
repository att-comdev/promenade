Promenade API
=============


/v1.0/healthcheck/{node_id}
---------------------------

Checks status of the node specified by `node_id`.

GET /v1.0/healthcheck/{node_id}

Returns the status of the specified node.

Responses
- 200 OK: Returns status of node
- 404 Not Found: The node with that id was not found


/v1.0/configmap/{node_id}
-------------------------

Checks information about the relevant documentation for the node specified by `node_id`.

GET /v1.0/configmap/{node_id}

Returns the location of the ``join.sh`` script and configuration maps for the specified node.

Responses
- 200 OK: Returns the location of the documents
- 404 Not Found: The node with that id was not found


PUT /v1.0/configmap/{node_id}

Updates (or creates, if it does not already exist) ``join.sh`` script and configuration maps for the specified node.

Parameters
- Accepts the location of the document to be created or updated on the node

Responses
- 200 OK: Returns location where documents have been created
- 404 Not Found: The node with that id was not found


/v1.0/documentation
-------------------

Validated documents for environment creation.

GET /v1.0/documentation

Retrieves and validates documentation.

Parameters
- Accepts the location of the document to be validated
- Accepts the type of document to be validated

Responses:
- 200 OK: Returns whether the document was able to be validated and if there were any errors during validation
- 404 Not Found: The document (of that type) was not found at the specified location
