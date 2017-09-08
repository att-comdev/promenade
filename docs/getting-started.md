# Getting Started

## Development

### Deployment using Vagrant

#### Initial Setup

Deployment using Vagrant uses KVM instead of Virtualbox due to better
performance of disk and networking, which both have significant impact on the
stability of the etcd clusters.

Make sure you have [Vagrant](https://vagrantup.com) installed, then
run `./tools/full-vagrant-setup.sh`, which will do the following:

* Install Vagrant libvirt plugin and its dependencies
* Install NFS dependencies for Vagrant volume sharing
* Install [packer](https://packer.io) and build a KVM image for Ubuntu 16.04

#### Deployment

A complete set of configuration that works with the `Vagrantfile` in the
top-level directory is provided in the `example` directory.

To exercise that example, first combine the configuration into usable parts:

```bash
./tools/build-example.sh
```

Start the VMs:

```bash
vagrant up --parallel
```

Then bring up the genesis node:

```bash
vagrant ssh n0 -c 'sudo bash /vagrant/example/scripts/genesis.sh'
```

Join additional master nodes:

```bash
vagrant ssh n1 -c 'sudo bash /vagrant/example/scripts/join-n1.sh'
vagrant ssh n2 -c 'sudo bash /vagrant/example/scripts/join-n2.sh'
```

Re-provision the genesis node as a normal master:

```bash
vagrant ssh n0 -c 'sudo genesis-teardown'
vagrant destroy -f n0
vagrant up n0
vagrant ssh n0 -c 'sudo bash /vagrant/example/scripts/join-n0.sh'
```

Join the remaining worker

```bash
vagrant ssh n3 -c 'sudo bash /vagrant/example/scripts/join-n3.sh'
```

## Using Promenade Behind a Proxy

To use Promenade from behind a proxy, use the proxy settings described in the
[configuration docs](configuration.md).
