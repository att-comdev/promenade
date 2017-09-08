Images
======

Specifies docker images used throughout the site, but directly by nodes rather
than by charts.


Sample Document
---------------

.. code-block:: yaml

    schema: promenade/Images/v1
    metadata:
      schema: metadata/Document/v1
      name: images
      layeringDefinition:
        abstract: false
        layer: site
    data:
      coredns: coredns/coredns:011
      helm:
        helm: lachlanevenson/k8s-helm:v2.5.1
      kubernetes:
        kubectl: gcr.io/google_containers/hyperkube-amd64:v1.8.0
        kubelet: gcr.io/google_containers/hyperkube-amd64:v1.8.0


Core Images
-----------

These images are used for essential functionality:

``coredns``
    coredns_ is configured and used for Kubernetes API discovery during
    bootstrapping.

``kubectl``
    Used for label application and validation tasks during bootstrapping.

``kubelet``
    Used for process management over the lifetime of the node.


Convenience Images
------------------

The ``helm`` image is available for convenience.


.. _coredns: https://github.com/coredns/coredns
