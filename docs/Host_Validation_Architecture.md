# Host Validation and Testing

__Date:__  7/6/2017

__Objective:__ To determine the best strategy to validate hosts have joined the Kubernetes cluster successfully and are ready to schedule workloads

## Problem Statement

The Promenade project is a simple and efficient tool for orchestrating the deployment of Kubernetes clusters.  However, Promenade currently lacks the ability to validate that clusters have been deployed successfully and are actually ready to schedule workloads.   I would like to propose a series of tests and validations that can be included with Promenade which will ensure the Kubernetes clusters are working as intended at the time of deployment, and can be executed at any point in time  after the cluster has been deployed to ensure it is continuing to function as intended for Day 2 operations. This tool should be able to identify potential problems with the Kubernetes cluster and provide the user with a comprehensive debugging output which highlights the identified issues.

## Identified Tests

I have identified the following tests which I believe to be a good base-line for basic Kubernetes smoke testing at the time of cluster deployment and during cluster life-cycle management:

1. __Generate SHA256 hashes of all Promenade Generated configuration files and certificates:__ This process will run during the initial deployment of all the Kubernetes hosts in the cluster. Promenade will write a file to `/var/log/promenade/promenade_file_hash.log` with the path to the file as well as the SHA256 hash of that file when it was originally generated. Subsequent runs of the host validation script will re-calculate the SHA256 hashes of the files as they are presently, and compare them with the values written in the log file at the time of deployment. If the file hashes differ, the host validation script will log a failure and provide the user with a list of files that have potentially been modified.

2. __Issue a REST Post Request to the Kubernetes API:__ This test will trigger a simple POST request to the internernal and external Kubernetes API and validate that it gets a `200` response. This check wil also query the `kube-system` namespace to ensure all pods are in a `RUNNING` state. This will ensure that the K8's API and system pods are running and responding as expected. 

3. __Kubelet and Docker Validation__ : The goal of this test will be to ensure the Kubelet and Docker are present on the host and running without error.

4. __Test Workloads__:  This will be the final test which is run against the Kubernetes cluster. If the other tests identified above pass without error, Promenade will issue a test deployment of pods on the cluster and ensure they come up in the `RUNNING` state with the correct IPs and networking provided by the CNI.  Once the workload has come up successfully, Promenade will destroy the deployment and ensure the pods are terminated cleanly.  This final test will determine if the Kubernetes cluster nodes can successfully schedule workloads.

## Other Concerns

1. __Monitoring Tools vs. Promenade:__ A lot of the identified tests blur the lines between what the monitoring tools such as Prometheus are designed to do.  We don't want two tools performing re-work, so we will need to clearly define the boundaries in the scope of Promenade versus other monitoring tools.

2. __Configuration Management Tools vs. Promenade:__  Much of what Promenade does today is template and place configuration files using Python and Jinja2 templates. Purpose-built configuration management tools such as Ansible, Chef, and Puppet can do all of these things, on top of validations to ensure the files are in the desired state.  Instead of re-inventing the wheel, would it make more sense to leverage a configuration management tool and build a wrapper around it for things such as validating configuration files and ensuring services are running?  Should we create a separate project which Promenade can leverage that is built for configuration management using one of the already existing platforms? This conversation again goes back to cleanly defining the scope of Promenade vs other tools that we plan on using going forward.
