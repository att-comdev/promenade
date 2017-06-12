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
vagrant ssh n0 -c 'sudo PROMENADE_CONFIG_DIR=/vagrant/example/config/n0-genesis /vagrant/setup.sh genesis'
```

Join additional nodes (as masters):

```bash
for i in 1 2; do
    vagrant ssh n$i -c 'sudo PROMENADE_CONFIG_DIR=/vagrant/example/config/n$i /vagrant/setup.sh join'
done
```

Tear down the genesis node:

```bash
...
```

Re-provision the genesis node as a normal node:

```bash
vagrant ssh n0 -c 'sudo PROMENADE_CONFIG_DIR=/vagrant/example/config/n0-master /vagrant/setup.sh join'
```
