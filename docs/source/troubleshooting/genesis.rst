Genesis Troubleshooting
=======================

genesis.sh
----------

Stuck in connect loop to k8s API
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: bash

    .The connection to the server apiserver.kubernetes.promenade:6443 was
    refused - did you specify the right host or port?

Check that the hostname in your Genesis.yaml matches the hostname of the
machine you are trying to install onto. If they do not match, change one to
match the other. If you change Genesis.yaml, then re-generate the Promenade
payloads.

If the hostnames match, check the container logs to see the reason for the
reason for provisioning failure. E.g.:

.. code-block:: bash

    sudo kubectl logs kubernetes-apiserver-genesis --namespace=kube-system

Armada failures
^^^^^^^^^^^^^^^

When executing genesis.sh, you may encounter failures from Armada in the
provisioning of other containers. For example:

.. code-block:: bash

    CRITICAL armada [-] Unhandled error: armada.exceptions.tiller_exceptions.ReleaseException: Failed to Install release: barbican

Use ``kubectl logs`` on the failed container to determine the reason for the
failure.

Other errors may point to configuration errors. For example:

.. code-block:: bash

    CRITICAL armada [-] Unhandled error: armada.exceptions.source_exceptions.GitLocationException: master is not a valid git repository.

In this case, the git branch name was inadvertently substituted for the git URL
in one of the chart definitions in ``bootstrap-armada.yaml``.
