# Overview

Promenade is tool for deploying self-hosted, highly resilient Kubernetes clusters.

## Quickstart using Vagrant

Make sure you have [Vagrant](https://vagrantup.com) and
[VirtualBox](https://www.virtualbox.org/wiki/Downloads) installed.  Then
install the `vagrant-hostmanager` plugin.

```bash
vagrant plugin install vagrant-hostmanager
```

Build the genesis and join images and save them to disk for quick loading into
the Vagrant VMs.

```bash
docker build -t promenade:experimental .
```

Start the VMs:

```bash
vagrant up
```

Start the genesis node:

```bash
vagrant ssh n0 -c 'sudo /vagrant/setup.sh /vagrant/example/vagrant-config.yaml'
```
