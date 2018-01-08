Genesis Troubleshooting
=======================

genesis.sh
----------

1. Stuck in connect loop to k8s API

.. code-block:: bash

    .The connection to the server apiserver.kubernetes.promenade:6443 was refused - did you specify the right host or port?

Check that the hostname in your Genesis.yaml matches the hostname of the machine you are trying to install onto. If they do not match, change one to match the other. If you change Genesis.yaml, then re-generate the Promonade payloads.

If the hostnames match, check the container logs under /var/log/pods for the kubernetes API to see why the container did not start.
