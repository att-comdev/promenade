# -*- mode: ruby -*-
# vi: set ft=ruby :

Vagrant.configure("2") do |config|
  config.vm.box = "ubuntu/xenial64"
  config.vm.box_check_update = false

  config.vm.provision :shell, privileged: true, inline:<<EOS
set -ex

echo === Installing Docker ===
apt-get update -qq
apt-get install -y -qq --no-install-recommends docker.io

if [ -f /vagrant/promenade.tar ]; then
  echo === Loading updated promenade image ===
  docker load -i /vagrant/promenade.tar
fi

echo === Done ===
EOS

  config.hostmanager.enabled = true
  config.hostmanager.manage_guest = true

  config.vm.provider "virtualbox" do |vb|
    vb.cpus = 2
    vb.memory = "2048"
  end

  config.vm.define "n0" do |c|
      c.vm.hostname = "n0"
      c.vm.network "private_network", ip: "192.168.77.10"
  end

  config.vm.define "n1" do |c|
      c.vm.hostname = "n1"
      c.vm.network "private_network", ip: "192.168.77.11"
  end

  config.vm.define "n2" do |c|
      c.vm.hostname = "n2"
      c.vm.network "private_network", ip: "192.168.77.12"
  end

  config.vm.define "n2" do |c|
      c.vm.hostname = "n2"
      c.vm.network "private_network", ip: "192.168.77.13"
  end

end
