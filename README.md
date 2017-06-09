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

Start the VMs and save a snapshot for quicker iteration:

```bash
vagrant up
vagrant snapshot save clean
```

Start the genesis node:

```bash
vagrant ssh n0
docker run --rm -v /vagrant/example/config:/etc/promenade -v /:/target promenade:experimental genesis
exit
```

Join additional nodes (as masters):

```bash
for i in 1 2 3; do
vagrant ssh n$i
docker run --rm -v /vagrant/example/config:/etc/promenade -v /:/target promenade:experimental join master
exit
```

To test changes, you can safely reset single or multiple nodes:

```bash
vagrant snapshot resotre n2 clean --no-provision
vagrant snapshot restore clean --no-provision
```
