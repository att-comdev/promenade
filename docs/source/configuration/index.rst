Configuration
=============

Promenade is configured using a set of Deckhand_ compatible configuration
documents and a bootstrapping Armada_ manifest that is responsible for
deploying core components into the cluster.

The provided Armada_ manifest ``armada-resources.yaml`` will be applied on the 
genesis node as soon as it is healthy.

Details about Promenade-specific documents can be found here:

.. toctree::
    :maxdepth: 2
    :caption: Documents

    docker
    genesis
    host-system
    kubelet
    kubernetes-network
    kubernetes-node
    layering-policy

.. _Armada: https://github.com/att-comdev/armada
.. _Deckhand: https://github.com/att-comdev/deckhand
