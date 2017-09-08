Genesis
=======

Specific configuration for the genesis process.  This document is a strict
superset of the :doc:`kubernetes-node`, so only differences are discussed here.


Sample Document
---------------

Here is a complete sample document:

.. code-block:: yaml

    schema: promenade/Genesis/v1
    metadata:
      schema: metadata/Document/v1
      name: genesis
      layeringDefinition:
        abstract: false
        layer: site
    data:
      hostname: n0
      ip: 192.168.77.10
      labels:
        static:
          - calico-etcd=enabled
          - node-role.kubernetes.io/master=
        dynamic:
          - kubernetes-apiserver=enabled
          - kubernetes-controller-manager=enabled
          - kubernetes-etcd=enabled
          - kubernetes-scheduler=enabled
          - promenade-genesis=enabled
          - ucp-control-plane=enabled
      images:
        armada: quay.io/attcomdev/armada:latest
        helm:
          tiller: gcr.io/kubernetes-helm/tiller:v2.5.1
        kubernetes:
          apiserver: gcr.io/google_containers/hyperkube-amd64:v1.8.0
          controller-manager: gcr.io/google_containers/hyperkube-amd64:v1.8.0
          etcd: quay.io/coreos/etcd:v3.0.17
          scheduler: gcr.io/google_containers/hyperkube-amd64:v1.8.0
      additional_files:
        /var/lib/anchor/calico-etcd-bootstrap: ""


Bootstrapping Images
--------------------

Bootstrapping images are specified in the top level key ``images``:

.. code-block:: yaml

    images:
      armada: <Armada image for bootstrapping>
      helm:
        tiller: <Tiller image for bootstrapping>
      kubernetes:
        apiserver: <API server image for bootstrapping>
        controller-manager: <Controller Manager image for bootstrapping>
        etcd: <etcd image for bootstrapping>
        scheduler: <Scheduler image for bootstrapping>


Additional Files
----------------

Arbitrary additional files can be placed on the host via the
``additional_files`` key.  This can be used to indicate to the accompanying
``etcd`` chart that the genesis node should be used for bootstrapping the
cluster.
