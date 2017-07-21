# Bootstrap Validation

The purpose of this validation is to ensure the genesis process was successful
and that the host is ready to instantiate the rest of the site.  That means not
only that Kubernetes is functioning as expected, including CNI and PVC
functionality, but also that other necessary services (e.g.
[Drydock](https://github.com/att-comdev/drydock)) are up.

While some validations can be performed directly by Promenade, validations of
other services need to be abstracted since different sites may deploy different
services.  This document describes the validations to be performed by Promenade
and pattern for other services to follow to provide their own validations.

## Direct Validation

Promenade will be responsible for either directly validating or delegating the
validation of the host, Kubernetes functionality, and etcd cluster health.

### Pre-Genesis, Pre-Join Validation

Before beginning the genesis or join processes, some validations can be applied
to the host machine to avoid surprising issues.

* Host DNS Validation
  * Ensure DNS is configured on the correct interface (e.g. not lo)

### Post-Genesis Validation

After the genesis process is executed, additional validations can be performed.

* Kubernetes cluster validation
  * Cluster DNS works as expected
    * Pod using CNI-managed network can resolve the Kubernetes service to the
      correct IP.
    * Pod in the host network namespace with
      `dnsPolicy: ClusterFirstWithHostNet` can resolve the Kubernetes service
      to the correct IP.
  * Pod logging is working (start a pod with known output & try to retrieve its logs)
* Host level DNS validation
  * Process outside of POD can resolve
    * Kubernetes service to expected IPs
    * A configurable list of names (e.g. repository names)
* Etcd cluster health validation
  * Membership is as expected
  * Logs do not indicate load issues

## Externally-Owned Validation

To keep services decoupled, Promenade will not check the status of services
directly, rather it will query Prometheus and check the status of a
configurable set of alerts.
